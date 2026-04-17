"""
spatial_eml.py — Sessions 42-43: EML Symbolic Regression for Spatial Functions

Session 42: Radial/axis reduction — project 2D targets to 1D and run existing
           MCTS to discover compact formulas. EML-SIREN vs sin-SIREN benchmark.

Session 43: Bivariate EML grammar — extend MCTS leaf set to {x, y, constants},
           run true 2D symbolic regression without any dimensionality reduction.
           Also: symbolic distillation of trained EML-SIREN models.

Reference: EML Weierstrass Theorem guarantees density in C([a,b]^n) for all n,
so any smooth 2D field has an EML approximation discoverable by bivariate MCTS.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

import random
from dataclasses import dataclass as _dc_import  # avoid name clash

from monogate.search.mcts import mcts_search, MCTSResult
from monogate.search.mcts import beam_search, BeamResult, _eval_tree
from monogate.search.mcts import (
    _leaf, _eml, _placeholder, _copy,
    _is_complete, _depth, _formula,
    _first_placeholder_path, _set_at_path,
    _MCTSNode, Node,
)
from monogate.frontiers.eml_complexity import classify_function


# ── Spatial targets ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SpatialTarget:
    """A 2D benchmark function with metadata."""

    name: str
    fn: Callable[[float, float], float]
    domain: tuple[float, float]           # symmetric domain [-d, d]^2
    reduction: str                         # "radial", "axis", "diagonal"
    description: str
    exact_formula: str | None = None       # ground-truth EML if known
    eml_complexity: str | None = None      # known EML-k class if known


def _circle_sdf(x: float, y: float, r: float = 1.0) -> float:
    return math.sqrt(x * x + y * y) - r


def _ellipse_sdf(x: float, y: float, a: float = 1.5, b: float = 0.8) -> float:
    return math.sqrt((x / a) ** 2 + (y / b) ** 2) - 1.0


def _gaussian_2d(x: float, y: float, sigma: float = 0.8) -> float:
    return math.exp(-(x * x + y * y) / (2 * sigma * sigma))


def _ring_sdf(x: float, y: float, r: float = 1.0, w: float = 0.3) -> float:
    return abs(math.sqrt(x * x + y * y) - r) - w


def _inverse_sq(x: float, y: float, eps: float = 0.1) -> float:
    return 1.0 / (x * x + y * y + eps)


def _axis_wave(x: float, _y: float) -> float:
    return math.exp(x) - math.log(abs(x) + 1.0)


# Pre-built benchmark targets
CIRCLE_SDF = SpatialTarget(
    name="circle_sdf",
    fn=lambda x, y: _circle_sdf(x, y, r=1.0),
    domain=2.0,
    reduction="radial",
    description="Signed distance field of unit circle: sqrt(x²+y²) - 1",
    exact_formula="r - 1.0",
    eml_complexity="EML-1 (via r = sqrt(x²+y²), then EML-1 shift)",
)

ELLIPSE_SDF = SpatialTarget(
    name="ellipse_sdf",
    fn=lambda x, y: _ellipse_sdf(x, y, a=1.5, b=0.8),
    domain=2.0,
    reduction="radial",
    description="Scaled radial SDF of ellipse: sqrt((x/1.5)² + (y/0.8)²) - 1",
    exact_formula=None,
    eml_complexity="EML-1 (radial after scaling)",
)

GAUSSIAN_2D = SpatialTarget(
    name="gaussian_2d",
    fn=lambda x, y: _gaussian_2d(x, y, sigma=0.8),
    domain=2.5,
    reduction="radial",
    description="Isotropic Gaussian: exp(-(x²+y²) / 2σ²)",
    exact_formula="exp(-r² / 2σ²)",
    eml_complexity="EML-1 (exp of radial argument)",
)

RING_SDF = SpatialTarget(
    name="ring_sdf",
    fn=lambda x, y: _ring_sdf(x, y, r=1.0, w=0.3),
    domain=2.0,
    reduction="radial",
    description="Ring SDF: |sqrt(x²+y²) - 1| - 0.3",
    exact_formula=None,
    eml_complexity="EML-≥2 (requires absolute value via EML composition)",
)

INVERSE_SQ = SpatialTarget(
    name="inverse_sq",
    fn=lambda x, y: _inverse_sq(x, y, eps=0.1),
    domain=2.0,
    reduction="radial",
    description="Regularized inverse-square: 1 / (x²+y²+0.1)",
    exact_formula="1 / (r²+0.1)",
    eml_complexity="EML-1 (rational form via EML)",
)

AXIS_WAVE = SpatialTarget(
    name="axis_wave",
    fn=_axis_wave,
    domain=2.0,
    reduction="axis",
    description="EML wave along x-axis: exp(x) - ln(|x|+1)",
    exact_formula="eml(x, |x|+1)",
    eml_complexity="EML-1 (exact EML expression)",
)

ALL_TARGETS: list[SpatialTarget] = [
    CIRCLE_SDF, ELLIPSE_SDF, GAUSSIAN_2D, RING_SDF, INVERSE_SQ, AXIS_WAVE,
]


# ── Reduction strategies ──────────────────────────────────────────────────────

def radial_reduce(fn_2d: Callable[[float, float], float], r_min: float = 0.0, r_max: float = 2.0) -> Callable[[float], float]:
    """Project a 2D function to 1D via f_1d(r) = f(r, 0).

    Valid when f is rotationally symmetric: f(x,y) depends only on sqrt(x²+y²).
    Reconstruction: f_approx(x,y) = f_1d(sqrt(x²+y²)).
    """
    def f_1d(r: float) -> float:
        return fn_2d(r, 0.0)
    return f_1d


def axis_reduce(fn_2d: Callable[[float, float], float], axis: int = 0) -> Callable[[float], float]:
    """Project a 2D function to 1D along a coordinate axis.

    axis=0: f_1d(x) = f(x, 0)
    axis=1: f_1d(y) = f(0, y)
    """
    if axis == 0:
        return lambda x: fn_2d(x, 0.0)
    else:
        return lambda y: fn_2d(0.0, y)


def pca_reduce(
    fn_2d: Callable[[float, float], float],
    domain: float = 2.0,
    n_grid: int = 30,
) -> tuple[Callable[[float], float], np.ndarray]:
    """Project 2D function to dominant PCA direction.

    Samples fn_2d on a grid, finds the principal variation direction via SVD,
    returns a 1D slice along that direction.  For non-symmetric functions.

    Returns:
        (f_1d, direction_vec) where direction_vec is the 2D unit vector.
    """
    xs = np.linspace(-domain, domain, n_grid)
    ys = np.linspace(-domain, domain, n_grid)
    Z = np.zeros((n_grid, n_grid))
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            try:
                Z[i, j] = fn_2d(float(x), float(y))
            except Exception:
                Z[i, j] = 0.0

    # SVD to find principal variation direction in the grid
    U, S, Vt = np.linalg.svd(Z - Z.mean(), full_matrices=False)
    direction = np.array([1.0, Vt[0, n_grid // 2]])
    direction /= np.linalg.norm(direction)

    def f_1d(t: float) -> float:
        px = float(t * direction[0])
        py = float(t * direction[1])
        try:
            return fn_2d(px, py)
        except Exception:
            return 0.0

    return f_1d, direction


# ── 2D reconstruction ─────────────────────────────────────────────────────────

def reconstruct_radial(f_1d: Callable[[float], float]) -> Callable[[float, float], float]:
    """Lift a 1D radial formula back to 2D: f_2d(x,y) = f_1d(sqrt(x²+y²))."""
    def f_2d(x: float, y: float) -> float:
        r = math.sqrt(x * x + y * y)
        try:
            return f_1d(r)
        except Exception:
            return float("nan")
    return f_2d


def reconstruct_axis(f_1d: Callable[[float], float], axis: int = 0) -> Callable[[float, float], float]:
    """Lift a 1D axis formula back to 2D."""
    if axis == 0:
        return lambda x, y: f_1d(x)
    else:
        return lambda x, y: f_1d(y)


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class SpatialSRResult:
    """Result of EML symbolic regression on a 2D target."""

    target_name: str
    reduction_mode: str
    formula_1d: str                    # EML formula in 1D variable
    formula_2d: str                    # formula with reduction substituted
    fn_1d: Callable[[float], float] | None  # callable from best_tree
    mse_1d: float                      # MSE of 1D fit
    mse_2d: float                      # MSE on 2D test grid
    l_inf_2d: float                    # L∞ error on 2D test grid
    eml_k_class: str                   # e.g. "EML-1", "EML-≥2"
    n_simulations: int
    elapsed_s: float
    grid_size: int
    domain: float
    probe_points: list[float]
    search_method: str                 # "mcts" or "beam"
    raw_result: MCTSResult | BeamResult | None = None
    error: str | None = None


# ── Core search API ───────────────────────────────────────────────────────────

def fit_spatial_eml(
    target: SpatialTarget,
    n_simulations: int = 2000,
    depth: int = 5,
    grid_size: int = 64,
    search: str = "mcts",
    seed: int = 42,
    verbose: bool = True,
) -> SpatialSRResult:
    """Fit a compact EML expression to a 2D spatial target.

    Pipeline:
      1. Reduce fn_2d → fn_1d using target.reduction strategy
      2. Run MCTS/beam search on fn_1d to find best EML formula
      3. Reconstruct fn_2d from best formula
      4. Evaluate on 2D grid: MSE, L∞
      5. Classify the 1D formula for EML-k complexity

    Args:
        target:         A SpatialTarget defining the benchmark function.
        n_simulations:  MCTS simulations (or beam width for beam search).
        depth:          Maximum EML tree depth.
        grid_size:      Evaluation grid resolution (grid_size × grid_size).
        search:         "mcts" or "beam".
        seed:           Random seed for MCTS.
        verbose:        Print progress.

    Returns:
        SpatialSRResult with formula, errors, and EML-k classification.
    """
    if verbose:
        print(f"[spatial_eml] Fitting: {target.name}  ({target.description})")
        print(f"  reduction={target.reduction}  search={search}  "
              f"n_sim={n_simulations}  depth={depth}")

    domain = target.domain if isinstance(target.domain, float) else float(target.domain)

    # ── Step 1: reduce to 1D ──────────────────────────────────────────────────
    if target.reduction == "radial":
        f_1d = radial_reduce(target.fn, r_min=0.0, r_max=domain)
        probe_pts = [domain * i / 49 for i in range(50)]  # r in [0, domain]
        reconstruct_fn = reconstruct_radial
        formula_2d_template = "f_1d(sqrt(x²+y²))"
    elif target.reduction in ("axis", "diagonal"):
        ax = 0
        f_1d = axis_reduce(target.fn, axis=ax)
        probe_pts = [-domain + 2 * domain * i / 49 for i in range(50)]
        reconstruct_fn = lambda f: reconstruct_axis(f, axis=ax)
        formula_2d_template = "f_1d(x)"
    else:
        f_1d, _ = pca_reduce(target.fn, domain=domain)
        probe_pts = [-domain + 2 * domain * i / 49 for i in range(50)]
        reconstruct_fn = reconstruct_axis  # fallback: treat as x-axis
        formula_2d_template = "f_1d(t)"

    # ── Step 2: MCTS / beam search ────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        if search == "beam":
            raw = beam_search(
                target_fn=f_1d,
                probe_points=probe_pts,
                depth=depth,
                width=n_simulations,
                objective="mse",
            )
        else:
            raw = mcts_search(
                target_fn=f_1d,
                probe_points=probe_pts,
                depth=depth,
                n_simulations=n_simulations,
                seed=seed,
                objective="mse",
            )
        formula_1d = raw.best_formula
        mse_1d = float(raw.best_mse)
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return SpatialSRResult(
            target_name=target.name,
            reduction_mode=target.reduction,
            formula_1d="(search failed)",
            formula_2d="(search failed)",
            fn_1d=None,
            mse_1d=float("inf"),
            mse_2d=float("inf"),
            l_inf_2d=float("inf"),
            eml_k_class="unknown",
            n_simulations=n_simulations,
            elapsed_s=elapsed,
            grid_size=grid_size,
            domain=domain,
            probe_points=probe_pts,
            search_method=search,
            raw_result=None,
            error=str(e),
        )
    elapsed = time.perf_counter() - t0

    if verbose:
        print(f"  1D formula: {formula_1d}  (MSE={mse_1d:.3e}, t={elapsed:.1f}s)")

    # ── Step 3: build callable from best_tree ─────────────────────────────────
    best_tree = raw.best_tree

    def f_1d_formula(x: float) -> float:
        try:
            return _eval_tree(best_tree, x)
        except Exception:
            return float("nan")

    # ── Step 4: reconstruct 2D and evaluate on grid ───────────────────────────
    xs = np.linspace(-domain, domain, grid_size)
    ys = np.linspace(-domain, domain, grid_size)

    errors: list[float] = []
    for xi in xs:
        for yi in ys:
            try:
                true_val = target.fn(float(xi), float(yi))
            except Exception:
                continue

            if f_1d_formula is not None:
                try:
                    if target.reduction == "radial":
                        r = math.sqrt(float(xi) ** 2 + float(yi) ** 2)
                        pred_val = f_1d_formula(r)
                    else:
                        pred_val = f_1d_formula(float(xi))
                except Exception:
                    pred_val = float("nan")
            else:
                # fallback: use 1D MSE as proxy
                pred_val = float("nan")

            if math.isfinite(pred_val) and math.isfinite(true_val):
                errors.append((pred_val - true_val) ** 2)

    mse_2d = float(np.mean(errors)) if errors else float("inf")
    l_inf_2d = float(np.sqrt(max(errors))) if errors else float("inf")

    # ── Step 5: EML-k classification ─────────────────────────────────────────
    eml_k = "unknown"
    try:
        cls = classify_function(f_1d_formula, domain=(0.05, domain - 0.05))
        eml_k = cls.get("complexity_class", "unknown")
    except Exception:
        eml_k = "unknown"

    # Build 2D formula string
    if target.reduction == "radial":
        formula_2d = formula_1d.replace("x", "sqrt(x²+y²)")
    else:
        formula_2d = formula_1d

    if verbose:
        print(f"  2D MSE: {mse_2d:.3e}  L∞: {l_inf_2d:.3e}  EML-k: {eml_k}")

    return SpatialSRResult(
        target_name=target.name,
        reduction_mode=target.reduction,
        formula_1d=formula_1d,
        formula_2d=formula_2d,
        fn_1d=f_1d_formula,
        mse_1d=mse_1d,
        mse_2d=mse_2d,
        l_inf_2d=l_inf_2d,
        eml_k_class=eml_k,
        n_simulations=n_simulations,
        elapsed_s=elapsed,
        grid_size=grid_size,
        domain=domain,
        probe_points=probe_pts,
        search_method=search,
        raw_result=raw,
        error=None,
    )


# ── Grid evaluation helpers ───────────────────────────────────────────────────

def eval_on_grid(
    fn_2d: Callable[[float, float], float],
    domain: float = 2.0,
    grid_size: int = 64,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate a 2D function on a uniform grid.

    Returns:
        (X, Y, Z) meshgrids — suitable for plt.contourf or plt.imshow.
    """
    xs = np.linspace(-domain, domain, grid_size)
    ys = np.linspace(-domain, domain, grid_size)
    X, Y = np.meshgrid(xs, ys)
    Z = np.zeros_like(X)
    for i in range(grid_size):
        for j in range(grid_size):
            try:
                Z[i, j] = fn_2d(float(X[i, j]), float(Y[i, j]))
            except Exception:
                Z[i, j] = float("nan")
    return X, Y, Z


def formula_to_2d(formula_1d: str, reduction: str = "radial") -> Callable[[float, float], float]:
    """Convert a 1D EML formula string to a 2D function.

    For radial reduction: substitutes x → sqrt(x²+y²).
    For axis reduction: uses x directly, ignores y.
    """
    safe = {"exp": math.exp, "log": math.log, "sqrt": math.sqrt,
            "abs": abs, "pi": math.pi, "e": math.e}
    try:
        f_1d = eval(f"lambda x: {formula_1d}", safe)  # noqa: S307
    except Exception as e:
        raise ValueError(f"Cannot parse formula {formula_1d!r}: {e}") from e

    if reduction == "radial":
        def f_2d(x: float, y: float) -> float:
            r = math.sqrt(x * x + y * y)
            try:
                return float(f_1d(r))
            except Exception:
                return float("nan")
    else:
        def f_2d(x: float, y: float) -> float:
            try:
                return float(f_1d(x))
            except Exception:
                return float("nan")

    return f_2d


# ── Pareto analysis ───────────────────────────────────────────────────────────

@dataclass
class ParetoPoint:
    name: str
    mse_2d: float
    n_nodes: int       # effective node count
    eml_k: str


def pareto_analysis(results: list[SpatialSRResult]) -> list[ParetoPoint]:
    """Extract Pareto-efficient (MSE, node_count) points from a set of results."""
    points = []
    for r in results:
        # Approximate node count from formula complexity
        n_nodes = r.formula_1d.count("exp") + r.formula_1d.count("log") + 1
        points.append(ParetoPoint(
            name=r.target_name,
            mse_2d=r.mse_2d,
            n_nodes=n_nodes,
            eml_k=r.eml_k_class,
        ))

    # Pareto filter: keep points not dominated on (mse, n_nodes)
    pareto = []
    for p in points:
        dominated = any(
            q.mse_2d <= p.mse_2d and q.n_nodes <= p.n_nodes and q != p
            for q in points
        )
        if not dominated:
            pareto.append(p)
    return sorted(pareto, key=lambda p: p.mse_2d)


# ── Summary printer ───────────────────────────────────────────────────────────

def print_results_table(results: list[SpatialSRResult]) -> None:
    """Print a formatted comparison table."""
    header = f"{'Target':<20} {'Reduction':<10} {'MSE-2D':<12} {'L-inf':<12} {'EML-k':<12} {'Formula (1D)'}"
    print()
    print("=" * 90)
    print("  EML Spatial Symbolic Regression — Session 42")
    print("=" * 90)
    print(f"  {header}")
    print("  " + "-" * 86)
    for r in results:
        mse_str = f"{r.mse_2d:.3e}" if math.isfinite(r.mse_2d) else "FAILED"
        linf_str = f"{r.l_inf_2d:.3e}" if math.isfinite(r.l_inf_2d) else "FAILED"
        formula_trunc = r.formula_1d[:38] + "..." if len(r.formula_1d) > 40 else r.formula_1d
        print(f"  {r.target_name:<20} {r.reduction_mode:<10} {mse_str:<12} {linf_str:<12} {r.eml_k_class:<12} {formula_trunc}")
    print("=" * 90)


# ═══════════════════════════════════════════════════════════════════════════════
#  Session 43 — Bivariate EML Grammar
# ═══════════════════════════════════════════════════════════════════════════════

# Leaf set extended with "y" — true 2D search, no projection needed.
_TERMINALS_2D: list = [1.0, "x", "y", 2.0, -1.0, 0.5]


def _eval_tree_2d(node: Node, x: float, y: float) -> float:
    """Evaluate a bivariate EML tree at (x, y).

    Extends the 1D evaluator: leaf "y" returns the y-coordinate.
    All other ops are identical to the univariate case.
    """
    op = node["op"]
    if op == "leaf":
        val = node["val"]
        if val == "x":
            return x
        if val == "y":
            return y
        return float(val)
    if op == "?":
        raise ValueError("Incomplete tree")
    a = _eval_tree_2d(node["left"],  x, y)
    b = _eval_tree_2d(node["right"], x, y)
    if b <= 0.0:
        raise ValueError(f"ln domain error: b={b}")
    return math.exp(a) - math.log(b)


def _score_2d(
    node: Node,
    probe_xy: list[tuple[float, float]],
    probe_z:  list[float],
) -> float:
    """MSE of bivariate tree against probe points.  Returns inf on any error."""
    if not _is_complete(node):
        return float("inf")
    sq_sum = 0.0
    n_ok = 0
    for (px, py), pz in zip(probe_xy, probe_z):
        try:
            pred = _eval_tree_2d(node, px, py)
            if math.isfinite(pred):
                sq_sum += (pred - pz) ** 2
                n_ok += 1
        except Exception:
            pass
    return sq_sum / n_ok if n_ok > 0 else float("inf")


def _expand_options_2d(node: Node, max_depth: int) -> list[Node]:
    """Bivariate grammar expansions — same as 1D but uses _TERMINALS_2D."""
    path = _first_placeholder_path(node)
    if path is None:
        return []
    options: list[Node] = []
    for t in _TERMINALS_2D:
        options.append(_set_at_path(node, path, _leaf(t)))
    if _depth(node) + 1 < max_depth:
        options.append(_set_at_path(node, path, _eml(_placeholder(), _placeholder())))
    return options


def _random_complete_2d(partial: Node, depth_budget: int, rng: random.Random) -> Node:
    """Randomly complete a bivariate partial tree."""
    node = _copy(partial)
    for _ in range(300):
        path = _first_placeholder_path(node)
        if path is None:
            break
        if _depth(node) >= depth_budget - 1:
            replacement = _leaf(rng.choice(_TERMINALS_2D))
        else:
            replacement = (
                _leaf(rng.choice(_TERMINALS_2D))
                if rng.random() < 0.6
                else _eml(_placeholder(), _placeholder())
            )
        node = _set_at_path(node, path, replacement)
    for _ in range(200):
        path = _first_placeholder_path(node)
        if path is None:
            break
        node = _set_at_path(node, path, _leaf(rng.choice(_TERMINALS_2D)))
    return node


@dataclass
class BivariateMCTSResult:
    """Result of bivariate EML MCTS search."""
    best_tree:    Node
    best_mse:     float
    best_formula: str
    n_simulations: int
    elapsed_s:    float
    history:      list[tuple[int, float]] = field(default_factory=list)

    def eval(self, x: float, y: float) -> float:
        try:
            return _eval_tree_2d(self.best_tree, x, y)
        except Exception:
            return float("nan")


def mcts_search_2d(
    target_fn:    Callable[[float, float], float],
    probe_points: list[tuple[float, float]] | None = None,
    depth:        int = 5,
    n_simulations: int = 5000,
    seed:         int = 42,
    log_every:    int = 0,
    domain:       float = 2.0,
) -> BivariateMCTSResult:
    """Monte-Carlo Tree Search over the bivariate EML grammar.

    Finds the compact EML expression tree in variables {x, y, constants} that
    minimises MSE against target_fn on probe_points.  No dimensionality
    reduction — true 2D symbolic regression.

    The leaf set {x, y, 1.0, 2.0, -1.0, 0.5} enables the grammar to express:
      circle_sdf    = sqrt(x²+y²) - 1  (via deep trees at depth>=5)
      gaussian_2d   = exp(-(x²+y²)/c)  (via nested eml nodes)
      inverse_sq    = 1/(x²+y²+eps)    (EML-≥1 in radius)

    Args:
        target_fn:     2D target: (x, y) -> z
        probe_points:  List of (x, y) pairs. Default: 7x7 grid + boundary ring.
        depth:         Max tree depth.
        n_simulations: MCTS simulations.
        seed:          Random seed.
        log_every:     Print progress every N sims (0=silent).
        domain:        If probe_points is None, sample on [-domain, domain]^2.

    Returns:
        BivariateMCTSResult with best_tree, best_formula, best_mse.
    """
    if probe_points is None:
        probe_points = _default_probe_2d(domain)

    probe_z = []
    valid_pts: list[tuple[float, float]] = []
    for px, py in probe_points:
        try:
            z = target_fn(float(px), float(py))
            if math.isfinite(z):
                probe_z.append(z)
                valid_pts.append((px, py))
        except Exception:
            pass
    probe_points = valid_pts

    rng = random.Random(seed)
    t0  = time.perf_counter()

    # Bootstrap _MCTSNode with 2D expansions
    class _MCTSNode2D:
        __slots__ = ("partial", "parent", "children", "visits", "total_reward",
                     "untried_expansions", "is_terminal")

        def __init__(self, partial: Node, parent, max_depth: int) -> None:
            self.partial = partial
            self.parent  = parent
            self.children: list[_MCTSNode2D] = []
            self.visits: int = 0
            self.total_reward: float = 0.0
            self.is_terminal: bool = _is_complete(partial)
            self.untried_expansions: list[Node] = (
                [] if self.is_terminal else _expand_options_2d(partial, max_depth)
            )

        def ucb1(self) -> float:
            if self.visits == 0:
                return float("inf")
            parent_v = self.parent.visits if self.parent else self.visits
            return (self.total_reward / self.visits
                    + math.sqrt(2.0) * math.sqrt(math.log(parent_v) / self.visits))

        def is_fully_expanded(self) -> bool:
            return len(self.untried_expansions) == 0

        def best_child(self):
            return max(self.children, key=lambda c: c.ucb1())

    root = _MCTSNode2D(_placeholder(), parent=None, max_depth=depth)
    best_node: Node  = _leaf(1.0)
    best_mse:  float = float("inf")
    history:   list[tuple[int, float]] = []

    for sim in range(1, n_simulations + 1):
        node = root
        while node.is_fully_expanded() and node.children and not node.is_terminal:
            node = node.best_child()

        if not node.is_terminal and node.untried_expansions:
            expansion = node.untried_expansions.pop(rng.randrange(len(node.untried_expansions)))
            child = _MCTSNode2D(expansion, parent=node, max_depth=depth)
            node.children.append(child)
            node = child

        if node.is_terminal:
            completed = node.partial
        else:
            completed = _random_complete_2d(node.partial, depth, rng)

        mse = _score_2d(completed, probe_points, probe_z)
        reward = 1.0 / (1.0 + mse)

        if mse < best_mse:
            best_mse  = mse
            best_node = completed

        n = node
        while n is not None:
            n.visits       += 1
            n.total_reward += reward
            n = n.parent

        if log_every and sim % log_every == 0:
            print(f"  2D sim {sim:>6}/{n_simulations}  best_mse={best_mse:.4e}"
                  f"  formula={_formula(best_node)}")
        if sim % max(1, n_simulations // 20) == 0:
            history.append((sim, best_mse))

    return BivariateMCTSResult(
        best_tree=best_node,
        best_mse=best_mse,
        best_formula=_formula(best_node),
        n_simulations=n_simulations,
        elapsed_s=time.perf_counter() - t0,
        history=history,
    )


def _default_probe_2d(domain: float, n_grid: int = 7) -> list[tuple[float, float]]:
    """Default 2D probe points: regular grid + boundary ring for SDF targets."""
    pts: list[tuple[float, float]] = []
    # 7x7 regular grid
    vals = [-domain + 2 * domain * i / (n_grid - 1) for i in range(n_grid)]
    for x in vals:
        for y in vals:
            pts.append((x, y))
    # Boundary ring at r=1 (important for SDF targets)
    for k in range(12):
        angle = 2 * math.pi * k / 12
        pts.append((math.cos(angle), math.sin(angle)))
    return pts


@dataclass
class Bivariate2DResult:
    """Result of bivariate fit_spatial_eml_2d()."""
    target_name:  str
    formula:      str              # EML formula in x, y
    mse_2d:       float
    l_inf_2d:     float
    eml_k_class:  str
    n_nodes:      int              # internal EML node count
    n_simulations: int
    elapsed_s:    float
    grid_size:    int
    domain:       float
    raw_result:   BivariateMCTSResult | None = None
    error:        str | None = None

    def eval(self, x: float, y: float) -> float:
        if self.raw_result is None:
            return float("nan")
        return self.raw_result.eval(x, y)


def fit_spatial_eml_2d(
    target: SpatialTarget,
    n_simulations: int = 5000,
    depth: int = 5,
    grid_size: int = 64,
    seed: int = 42,
    verbose: bool = True,
) -> Bivariate2DResult:
    """Fit a bivariate EML formula to a 2D spatial target.

    Uses the full {x, y, constants} leaf set — no radial reduction.
    Proves or approximates the target directly in 2D.

    Args:
        target:        SpatialTarget to fit.
        n_simulations: MCTS simulations.
        depth:         Max EML tree depth (5-6 recommended for SDFs).
        grid_size:     Test grid resolution for MSE/L∞ evaluation.
        seed:          Random seed.
        verbose:       Print progress.

    Returns:
        Bivariate2DResult with formula, errors, EML-k class, node count.
    """
    domain = float(target.domain)

    if verbose:
        print(f"[bivariate] Fitting: {target.name}  depth={depth}  n_sim={n_simulations}")

    probe_pts = _default_probe_2d(domain)

    t0 = time.perf_counter()
    try:
        raw = mcts_search_2d(
            target_fn=target.fn,
            probe_points=probe_pts,
            depth=depth,
            n_simulations=n_simulations,
            seed=seed,
            domain=domain,
        )
        formula = raw.best_formula
        mse_raw = raw.best_mse
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return Bivariate2DResult(
            target_name=target.name,
            formula="(failed)",
            mse_2d=float("inf"),
            l_inf_2d=float("inf"),
            eml_k_class="unknown",
            n_nodes=0,
            n_simulations=n_simulations,
            elapsed_s=elapsed,
            grid_size=grid_size,
            domain=domain,
            raw_result=None,
            error=str(e),
        )
    elapsed = time.perf_counter() - t0

    # Evaluate on dense 2D test grid
    xs = np.linspace(-domain, domain, grid_size)
    ys = np.linspace(-domain, domain, grid_size)
    sq_errs: list[float] = []
    for xi in xs:
        for yi in ys:
            try:
                true_v = target.fn(float(xi), float(yi))
                pred_v = raw.eval(float(xi), float(yi))
                if math.isfinite(true_v) and math.isfinite(pred_v):
                    sq_errs.append((pred_v - true_v) ** 2)
            except Exception:
                pass
    mse_2d  = float(np.mean(sq_errs)) if sq_errs else float("inf")
    l_inf_2d = float(np.sqrt(max(sq_errs))) if sq_errs else float("inf")

    # EML-k classification via 1D slice along x-axis (y=0)
    eml_k = "unknown"
    try:
        def _slice_x(x: float) -> float:
            return raw.eval(x, 0.0)
        cls = classify_function(_slice_x, domain=(0.05, domain - 0.05))
        eml_k = cls.get("complexity_class", "unknown")
    except Exception:
        pass

    # Node count from formula string
    n_nodes = formula.count("eml(")

    if verbose:
        print(f"  formula: {formula[:60]}...")
        print(f"  MSE-2D={mse_2d:.3e}  L-inf={l_inf_2d:.3e}  nodes={n_nodes}  [{eml_k}]")

    return Bivariate2DResult(
        target_name=target.name,
        formula=formula,
        mse_2d=mse_2d,
        l_inf_2d=l_inf_2d,
        eml_k_class=eml_k,
        n_nodes=n_nodes,
        n_simulations=n_simulations,
        elapsed_s=elapsed,
        grid_size=grid_size,
        domain=domain,
        raw_result=raw,
        error=None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  Session 43 — Symbolic Distillation of Coordinate Networks
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DistillationResult:
    """Result of distilling a trained neural network into a bivariate EML formula."""
    model_name:       str
    target_name:      str
    formula:          str          # discovered EML formula
    distill_mse:      float        # MSE between formula and network output
    network_mse:      float        # original network MSE vs ground truth
    formula_vs_truth: float        # formula MSE vs ground truth (end-to-end)
    fidelity:         float        # 1 - distill_mse / network_var (how well we captured the net)
    n_nodes:          int
    n_params:         int
    compression_ratio: float       # n_params / n_nodes
    eml_k_class:      str
    n_simulations:    int
    elapsed_s:        float
    raw_result:       BivariateMCTSResult | None = None
    error:            str | None = None


def distill_network(
    model,                              # trained PyTorch nn.Module
    target: SpatialTarget,
    model_name: str = "network",
    n_simulations: int = 5000,
    depth: int = 5,
    grid_size: int = 48,
    seed: int = 42,
    verbose: bool = True,
) -> DistillationResult:
    """Distill a trained 2D coordinate network into a compact bivariate EML formula.

    Pipeline:
      1. Sample the network densely on a 2D grid -> Z_net
      2. Create target_fn_net(x, y) via grid interpolation
      3. Run mcts_search_2d to find best EML formula for Z_net
      4. Evaluate: formula vs network (distillation fidelity)
                   formula vs ground truth (end-to-end quality)
      5. EML-k classify the distilled formula

    Args:
        model:         Trained PyTorch model: input (N, 2) -> output (N, 1)
        target:        SpatialTarget for ground truth comparison
        model_name:    Name for reporting
        n_simulations: MCTS budget for distillation search
        depth:         Max EML tree depth
        grid_size:     Sampling grid for the network
        seed:          Random seed
        verbose:       Print progress

    Returns:
        DistillationResult with formula, fidelity scores, compression ratio.
    """
    try:
        import torch
    except ImportError:
        return DistillationResult(
            model_name=model_name, target_name=target.name,
            formula="(torch not available)", distill_mse=float("inf"),
            network_mse=float("inf"), formula_vs_truth=float("inf"),
            fidelity=0.0, n_nodes=0, n_params=0, compression_ratio=0.0,
            eml_k_class="unknown", n_simulations=n_simulations, elapsed_s=0.0,
            error="torch not installed",
        )

    domain = float(target.domain)
    if verbose:
        print(f"[distill] {model_name} -> EML  target={target.name}  n_sim={n_simulations}")

    # ── Sample the network on a 2D grid ──────────────────────────────────────
    xs = np.linspace(-domain, domain, grid_size)
    ys = np.linspace(-domain, domain, grid_size)
    xy_list, z_net_list, z_true_list = [], [], []

    with torch.no_grad():
        for xi in xs:
            for yi in ys:
                try:
                    z_true = target.fn(float(xi), float(yi))
                    if not math.isfinite(z_true):
                        continue
                    xy_list.append([float(xi), float(yi)])
                    z_true_list.append(z_true)
                except Exception:
                    pass

        if not xy_list:
            return DistillationResult(
                model_name=model_name, target_name=target.name,
                formula="(no valid grid points)", distill_mse=float("inf"),
                network_mse=float("inf"), formula_vs_truth=float("inf"),
                fidelity=0.0, n_nodes=0, n_params=0, compression_ratio=0.0,
                eml_k_class="unknown", n_simulations=n_simulations, elapsed_s=0.0,
                error="no valid grid points",
            )

        xy_t    = torch.tensor(xy_list, dtype=torch.float32)
        z_pred  = model(xy_t).squeeze().numpy()
        z_true  = np.array(z_true_list)

    # Network MSE vs ground truth
    network_mse = float(np.mean((z_pred - z_true) ** 2))

    # ── Build interpolated target_fn for distillation ─────────────────────────
    xy_arr = np.array(xy_list)
    from scipy.interpolate import LinearNDInterpolator
    try:
        interp = LinearNDInterpolator(xy_arr, z_pred, fill_value=float("nan"))
        def target_fn_net(x: float, y: float) -> float:
            val = float(interp([[x, y]])[0])
            if not math.isfinite(val):
                raise ValueError("out of interpolation domain")
            return val
    except ImportError:
        # Fallback: nearest-neighbor via numpy
        def target_fn_net(x: float, y: float) -> float:
            dists = (xy_arr[:, 0] - x)**2 + (xy_arr[:, 1] - y)**2
            idx = int(np.argmin(dists))
            return float(z_pred[idx])

    # ── Run bivariate MCTS on network output ─────────────────────────────────
    probe_pts = _default_probe_2d(domain)
    t0 = time.perf_counter()
    try:
        raw = mcts_search_2d(
            target_fn=target_fn_net,
            probe_points=probe_pts,
            depth=depth,
            n_simulations=n_simulations,
            seed=seed,
            domain=domain,
        )
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return DistillationResult(
            model_name=model_name, target_name=target.name,
            formula="(search failed)", distill_mse=float("inf"),
            network_mse=network_mse, formula_vs_truth=float("inf"),
            fidelity=0.0, n_nodes=0,
            n_params=sum(p.numel() for p in model.parameters()),
            compression_ratio=0.0, eml_k_class="unknown",
            n_simulations=n_simulations, elapsed_s=elapsed, error=str(e),
        )
    elapsed = time.perf_counter() - t0

    # ── Evaluate distillation quality ─────────────────────────────────────────
    formula_vs_net: list[float] = []
    formula_vs_truth_errs: list[float] = []
    for (xi, yi), zn, zt in zip(xy_list, z_pred, z_true):
        try:
            pred = raw.eval(float(xi), float(yi))
            if math.isfinite(pred):
                formula_vs_net.append((pred - zn) ** 2)
                formula_vs_truth_errs.append((pred - zt) ** 2)
        except Exception:
            pass

    distill_mse       = float(np.mean(formula_vs_net)) if formula_vs_net else float("inf")
    formula_vs_truth  = float(np.mean(formula_vs_truth_errs)) if formula_vs_truth_errs else float("inf")
    net_var           = float(np.var(z_pred)) if len(z_pred) > 1 else 1.0
    fidelity          = max(0.0, 1.0 - distill_mse / net_var) if net_var > 0 else 0.0

    # EML-k classify
    eml_k = "unknown"
    try:
        def _slice(x: float) -> float:
            return raw.eval(x, 0.0)
        cls = classify_function(_slice, domain=(0.05, domain - 0.05))
        eml_k = cls.get("complexity_class", "unknown")
    except Exception:
        pass

    n_nodes  = raw.best_formula.count("eml(")
    n_params = sum(p.numel() for p in model.parameters())
    compression = n_params / max(n_nodes, 1)

    if verbose:
        print(f"  formula:         {raw.best_formula[:60]}...")
        print(f"  distill_mse:     {distill_mse:.3e}  (formula vs network)")
        print(f"  formula_vs_truth:{formula_vs_truth:.3e}  (formula vs ground truth)")
        print(f"  network_mse:     {network_mse:.3e}  (network vs ground truth)")
        print(f"  fidelity:        {fidelity:.3f}  compression: {n_params}/{n_nodes} = {compression:.0f}x")
        print(f"  EML-k:           {eml_k}")

    return DistillationResult(
        model_name=model_name,
        target_name=target.name,
        formula=raw.best_formula,
        distill_mse=distill_mse,
        network_mse=network_mse,
        formula_vs_truth=formula_vs_truth,
        fidelity=fidelity,
        n_nodes=n_nodes,
        n_params=n_params,
        compression_ratio=compression,
        eml_k_class=eml_k,
        n_simulations=n_simulations,
        elapsed_s=elapsed,
        raw_result=raw,
    )


def print_bivariate_table(results: list[Bivariate2DResult]) -> None:
    """Print Session 43 bivariate results table."""
    print()
    print("=" * 95)
    print("  Session 43 — Bivariate EML Grammar: True 2D Symbolic Regression")
    print("=" * 95)
    header = f"  {'Target':<20} {'MSE-2D':<12} {'L-inf':<12} {'Nodes':<8} {'EML-k':<12} {'Formula'}"
    print(header)
    print("  " + "-" * 91)
    for r in results:
        mse_s  = f"{r.mse_2d:.3e}" if math.isfinite(r.mse_2d) else "FAILED"
        linf_s = f"{r.l_inf_2d:.3e}" if math.isfinite(r.l_inf_2d) else "FAILED"
        fml    = r.formula[:35] + "..." if len(r.formula) > 37 else r.formula
        print(f"  {r.target_name:<20} {mse_s:<12} {linf_s:<12} {r.n_nodes:<8} {r.eml_k_class:<12} {fml}")
    print("=" * 95)
    print()


def print_distillation_table(results: list[DistillationResult]) -> None:
    """Print symbolic distillation comparison table."""
    print()
    print("=" * 100)
    print("  Session 43 — Symbolic Distillation: EML-SIREN -> Compact Formula")
    print("=" * 100)
    print(f"  {'Target':<18} {'Model':<20} {'Net MSE':<10} {'Formula MSE':<13} {'Fidelity':<10} {'Nodes':<7} {'Compression'}")
    print("  " + "-" * 95)
    for r in results:
        nm  = f"{r.network_mse:.2e}"
        fm  = f"{r.formula_vs_truth:.2e}"
        fid = f"{r.fidelity:.3f}"
        cmp = f"{r.compression_ratio:.0f}x"
        print(f"  {r.target_name:<18} {r.model_name:<20} {nm:<10} {fm:<13} {fid:<10} {r.n_nodes:<7} {cmp}")
    print("=" * 100)
    print()
    print()
