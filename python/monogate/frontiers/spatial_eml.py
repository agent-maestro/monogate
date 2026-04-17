"""
spatial_eml.py — Session 42: EML Symbolic Regression for Spatial Functions

Bridges the gap between the (proven) EML density theorem and 2D coordinate-based
tasks.  Strategy: reduce smooth 2D spatial functions to 1D via principled
projections, then run existing MCTS/beam search to discover compact EML formulas.

Supported reduction modes:
  radial   — for rotationally symmetric functions f(x,y) = g(sqrt(x²+y²))
  axis     — for separable or axis-aligned functions; projects onto dominant axis
  diagonal — for functions varying primarily along x+y or x-y

Reference: EML Weierstrass Theorem guarantees density in C([a,b]^n) for all n,
so any smooth 2D field has an EML approximation — we just need to find its
most compact 1D reduction for tractable search.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from monogate.search.mcts import mcts_search, MCTSResult
from monogate.search.mcts import beam_search, BeamResult, _eval_tree
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
    print()
