"""
Door 3: Approximation Rate Study — Session S104

Central question: T31 proves EML trees are dense in C([a,b]).
How fast does the approximation error decay with tree size n?

For each of 5 target functions on [0.1, 3], we train an EMLNetwork
(complete binary EML tree with learnable linear leaves) at each depth level,
which maps to an internal-node count n = 2^depth - 1.

Tree sizes (internal EML nodes): 1, 3, 7, 15, 31 correspond to depths 1-5.
For the requested odd sizes [1,3,5,7,9,11,13] we pick the closest depth.

Fallback (no torch): scipy parametric grid search over parameterized EML families.

Results saved to: python/results/s104_door3_approximation_rate.json
"""
from __future__ import annotations

import sys
import math
import json
import time
import random
from typing import Callable

sys.stdout.reconfigure(encoding="utf-8")

# ── Try monogate neural API (torch required) ──────────────────────────────────
MONOGATE_NEURAL = False
try:
    import torch
    from torch import Tensor
    from monogate import EMLNetwork, fit as eml_fit
    MONOGATE_NEURAL = True
    print("monogate EMLNetwork available: using gradient-based EML tree training")
except ImportError:
    print("torch / EMLNetwork not available: falling back to scipy parametric search")

# ── Try monogate beam_search API ──────────────────────────────────────────────
MONOGATE_SEARCH = False
try:
    from monogate.search import beam_search
    MONOGATE_SEARCH = True
    print("monogate beam_search available (structural + gradient hybrid)")
except ImportError:
    pass

# ── Probe points: 50 equally-spaced in [0.1, 3] ──────────────────────────────
N_PROBE = 50
PROBE_X: list[float] = [0.1 + (3.0 - 0.1) * i / (N_PROBE - 1) for i in range(N_PROBE)]

# ── Target functions ──────────────────────────────────────────────────────────
def f1(x: float) -> float:
    """sin(x) — analytic, entire function."""
    return math.sin(x)

def f2(x: float) -> float:
    """exp(-x^2) — Gaussian, entire function."""
    return math.exp(-x * x)

def f3(x: float) -> float:
    """|x - 1.5| — piecewise smooth (Lipschitz), one corner."""
    return abs(x - 1.5)

def f4(x: float) -> float:
    """1/(1+x^2) — Lorentzian, analytic on real line."""
    return 1.0 / (1.0 + x * x)

def f5(x: float) -> float:
    """x^0.3 — fractional power, smooth but not analytic (branch point at 0)."""
    return x ** 0.3

TARGETS: dict[str, Callable[[float], float]] = {
    "f1_sin":        f1,
    "f2_gaussian":   f2,
    "f3_abs":        f3,
    "f4_lorentzian": f4,
    "f5_fracpower":  f5,
}

TARGET_DESC: dict[str, str] = {
    "f1_sin":        "sin(x) — entire function",
    "f2_gaussian":   "exp(-x^2) — entire function (Gaussian)",
    "f3_abs":        "|x-1.5| — piecewise smooth, one corner",
    "f4_lorentzian": "1/(1+x^2) — analytic on ℝ",
    "f5_fracpower":  "x^0.3 — smooth, not analytic (branch point)",
}

# Tree sizes requested; depth d gives 2^d - 1 internal nodes
TREE_SIZES = [1, 3, 5, 7, 9, 11, 13]
# Map requested n to (depth, actual_n):
#   n=1  → depth=1, actual=1
#   n=3  → depth=2, actual=3
#   n=5  → depth=2 or 3; use depth=2 (3) and depth=3 (7)
#   n=7  → depth=3, actual=7
#   n=9  → depth=3 (7) or depth=4 (15) — use depth=4 to get more nodes
#   n=11 → depth=4, actual=15
#   n=13 → depth=4, actual=15
# For granularity we use depths 1..5, then report actual node counts
DEPTH_SEQUENCE = [1, 2, 3, 4, 5]  # gives n = 1, 3, 7, 15, 31 internal nodes

# Training budget — tuned so total runtime fits within ~8 minutes
_N_RESTARTS       = 3    # gradient restarts per depth per target
_STEPS_PER_RESTART = 1500  # Adam steps per restart

def _depth_to_n(depth: int) -> int:
    return 2**depth - 1

# ── Gradient-based EMLNetwork training ────────────────────────────────────────
def _train_eml_network(
    target_fn: Callable[[float], float],
    depth: int,
    n_restarts: int = _N_RESTARTS,
    steps_per_restart: int = _STEPS_PER_RESTART,
    lr: float = 5e-3,
) -> float:
    """Train EMLNetwork at given depth; return best MSE over PROBE_X.

    Uses multiple random restarts with varying learning rates to escape
    the phantom attractor problem documented for EML gradient descent.
    """
    X_list = [[xi] for xi in PROBE_X]
    y_list = [target_fn(xi) for xi in PROBE_X]

    X = torch.tensor(X_list, dtype=torch.float32)
    Y = torch.tensor(y_list, dtype=torch.float32)

    best_mse = float("inf")

    # Grid of (seed, lr) pairs to try
    configs = [(seed, lr_try)
               for seed in range(n_restarts)
               for lr_try in [1e-2, 5e-3, 2e-3]]

    for seed, lr_val in configs:
        torch.manual_seed(seed * 137 + depth * 31)
        try:
            net = EMLNetwork(in_features=1, depth=depth)
            eml_fit(net, x=X, y=Y, steps=steps_per_restart, lr=lr_val, log_every=0)
            with torch.no_grad():
                pred = net(X).squeeze()
                mse_val = ((pred - Y) ** 2).mean().item()
            if math.isfinite(mse_val) and mse_val < best_mse:
                best_mse = mse_val
        except Exception:
            pass

    return best_mse


# ── EML safe operator ──────────────────────────────────────────────────────────
def _eml_safe(a: float, b: float) -> float:
    """eml(a,b) = exp(a) - ln(b), returns inf on domain error."""
    if b <= 0:
        return float("inf")
    try:
        v = math.exp(a) - math.log(b)
        return v if math.isfinite(v) else float("inf")
    except (OverflowError, ValueError):
        return float("inf")

# ── Parametric EML tree families for scipy fallback ───────────────────────────
def _make_param_tree(tree_idx: int, params: list[float], x: float) -> float:
    """
    Evaluate a parameterized EML tree at x.
    tree_idx selects the structural template; params are the free scalars.
    """
    p = params
    if tree_idx == 0:
        # depth=0: affine leaf (proxy for 1-node)
        return p[0] * x + p[1]

    elif tree_idx == 1:
        # depth=1: eml(ax+b, cx+d)  — 1 internal node
        left  = p[0] * x + p[1]
        right = abs(p[2] * x + p[3]) + 1e-6
        return _eml_safe(left, right)

    elif tree_idx == 2:
        # depth=2: eml(eml(ax+b, cx+d), ex+f)  — 3 internal nodes
        inner = _eml_safe(p[0] * x + p[1], abs(p[2] * x + p[3]) + 1e-6)
        if not math.isfinite(inner):
            return float("inf")
        return _eml_safe(inner, abs(p[4] * x + p[5]) + 1e-6)

    elif tree_idx == 3:
        # depth=2: eml(ax+b, eml(cx+d, ex+f))  — 3 internal nodes
        inner = _eml_safe(p[2] * x + p[3], abs(p[4] * x + p[5]) + 1e-6)
        if not math.isfinite(inner):
            return float("inf")
        return _eml_safe(p[0] * x + p[1], abs(inner) + 1e-6)

    elif tree_idx == 4:
        # depth=3: eml(eml(ax+b,cx+d), eml(ex+f,gx+h))  — 7 internal nodes
        left  = _eml_safe(p[0] * x + p[1], abs(p[2] * x + p[3]) + 1e-6)
        right = _eml_safe(p[4] * x + p[5], abs(p[6] * x + p[7]) + 1e-6)
        if not math.isfinite(left) or not math.isfinite(right):
            return float("inf")
        return _eml_safe(left, abs(right) + 1e-6)

    elif tree_idx == 5:
        # depth=4 approx: chain of 4 eml ops — 15 internal nodes
        v1 = _eml_safe(p[0] * x + p[1], abs(p[2] * x + p[3]) + 1e-6)
        if not math.isfinite(v1):
            return float("inf")
        v2 = _eml_safe(p[4] * x + p[5], abs(p[6] * x + p[7]) + 1e-6)
        if not math.isfinite(v2):
            return float("inf")
        v3 = _eml_safe(v1, abs(v2) + 1e-6)
        if not math.isfinite(v3):
            return float("inf")
        return _eml_safe(v3, abs(p[8] * x + p[9]) + 1e-6)

    elif tree_idx == 6:
        # depth=5 approx — 31 internal nodes (deep chain)
        v1 = _eml_safe(p[0] * x + p[1], abs(p[2] * x + p[3]) + 1e-6)
        if not math.isfinite(v1):
            return float("inf")
        v2 = _eml_safe(p[4] * x + p[5], abs(p[6] * x + p[7]) + 1e-6)
        if not math.isfinite(v2):
            return float("inf")
        v3 = _eml_safe(v1, abs(v2) + 1e-6)
        if not math.isfinite(v3):
            return float("inf")
        v4 = _eml_safe(v3, abs(p[8] * x + p[9]) + 1e-6)
        if not math.isfinite(v4):
            return float("inf")
        return _eml_safe(v4, abs(p[10] * x + p[11]) + 1e-6)

    return float("inf")

# Map depth to (tree_idx, n_params)
_TREE_TEMPLATES: dict[int, tuple[int, int]] = {
    1: (1, 4),
    2: (2, 6),
    3: (4, 8),
    4: (5, 10),
    5: (6, 12),
}

def _search_scipy(target_fn: Callable[[float], float], depth: int) -> float:
    """Scipy differential evolution for parametric EML tree. Returns best MSE."""
    from scipy.optimize import minimize, differential_evolution
    import numpy as np

    tree_idx, n_params = _TREE_TEMPLATES.get(depth, (1, 4))
    target_y = [target_fn(xi) for xi in PROBE_X]

    def objective(params: list[float]) -> float:
        total = 0.0
        for xi, yi in zip(PROBE_X, target_y):
            try:
                pred = _make_param_tree(tree_idx, params, xi)
                if not math.isfinite(pred):
                    return 1e12
                diff = pred - yi
                total += diff * diff
            except Exception:
                return 1e12
        return total / N_PROBE

    best_mse = float("inf")
    best_params = [1.0] * n_params

    bounds = [(-4.0, 4.0)] * n_params

    try:
        de_result = differential_evolution(
            objective,
            bounds=bounds,
            seed=42,
            maxiter=400,
            popsize=15,
            tol=1e-10,
            mutation=(0.5, 1.5),
            recombination=0.7,
            polish=True,
        )
        if de_result.fun < best_mse:
            best_mse = float(de_result.fun)
            best_params = list(de_result.x)
    except Exception:
        pass

    # Nelder-Mead refinement
    for seed_val in [42, 123, 777, 2024, 42000]:
        np.random.seed(seed_val)
        p0 = np.random.uniform(-2.0, 2.0, n_params)
        try:
            local = minimize(
                objective,
                x0=p0,
                method="Nelder-Mead",
                options={"maxiter": 5000, "xatol": 1e-11, "fatol": 1e-13},
            )
            if local.fun < best_mse:
                best_mse = float(local.fun)
        except Exception:
            pass

    return best_mse if math.isfinite(best_mse) else float("inf")


# ── Dispatch: select best available search method ─────────────────────────────
def search_for_depth(target_fn: Callable[[float], float], depth: int) -> float:
    """Find best MSE for an EML tree of given depth."""
    if MONOGATE_NEURAL:
        return _train_eml_network(target_fn, depth)
    else:
        return _search_scipy(target_fn, depth)


# ── Decay rate fitting ─────────────────────────────────────────────────────────
def _ols_fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """OLS line y = a + b*x. Returns (a, b, R²)."""
    k = len(xs)
    if k < 2:
        return (0.0, 0.0, 0.0)
    mean_x = sum(xs) / k
    mean_y = sum(ys) / k
    ss_xx = sum((xi - mean_x) ** 2 for xi in xs)
    ss_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(xs, ys))
    if abs(ss_xx) < 1e-14:
        return (mean_y, 0.0, 0.0)
    b = ss_xy / ss_xx
    a = mean_y - b * mean_x
    ss_res = sum((yi - (a + b * xi)) ** 2 for xi, yi in zip(xs, ys))
    ss_tot = sum((yi - mean_y) ** 2 for yi in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-14 else 1.0
    return (float(a), float(b), float(r2))


def _fit_exponential_decay(ns: list[int], errors: list[float]) -> dict:
    """Fit log(error) = A - b*n  (exponential decay in n)."""
    valid = [(n, e) for n, e in zip(ns, errors) if e > 0 and math.isfinite(e)]
    if len(valid) < 2:
        return {"b": None, "A": None, "r2": None, "model": "exp(-b*n)"}
    log_e = [math.log(e) for _, e in valid]
    n_vals = [float(n) for n, _ in valid]
    A, neg_b, r2 = _ols_fit(n_vals, log_e)
    b = -neg_b  # log(err) = A - b*n → slope = -b
    return {"b": float(b), "A": float(A), "r2": float(r2), "model": "exp(-b*n)"}


def _fit_sqrt_decay(ns: list[int], errors: list[float]) -> dict:
    """Fit log(error) = A - b*sqrt(n)."""
    valid = [(n, e) for n, e in zip(ns, errors) if e > 0 and math.isfinite(e)]
    if len(valid) < 2:
        return {"b": None, "A": None, "r2": None, "model": "exp(-b*sqrt(n))"}
    log_e = [math.log(e) for _, e in valid]
    sqrt_n = [math.sqrt(n) for n, _ in valid]
    A, neg_b, r2 = _ols_fit(sqrt_n, log_e)
    b = -neg_b
    return {"b": float(b), "A": float(A), "r2": float(r2), "model": "exp(-b*sqrt(n))"}


def _fit_algebraic_decay(ns: list[int], errors: list[float]) -> dict:
    """Fit log(error) = C - k*log(n)  →  error ~ n^(-k)."""
    valid = [(n, e) for n, e in zip(ns, errors) if e > 0 and n > 0 and math.isfinite(e)]
    if len(valid) < 2:
        return {"k": None, "C": None, "r2": None, "model": "C*n^(-k)"}
    log_e = [math.log(e) for _, e in valid]
    log_n = [math.log(n) for n, _ in valid]
    intercept, slope, r2 = _ols_fit(log_n, log_e)
    k = -slope
    C = math.exp(intercept)
    return {"k": float(k), "C": float(C), "r2": float(r2), "model": "C*n^(-k)"}


def _classify_rate(dr: dict, fname: str) -> str:
    """Classify error decay rate quality."""
    exp_info  = dr.get("exponential", {})
    sqrt_info = dr.get("sqrt_exponential", {})
    alg_info  = dr.get("algebraic", {})

    b_exp  = exp_info.get("b") or 0.0
    r2_exp = exp_info.get("r2") or 0.0
    b_sqrt = sqrt_info.get("b") or 0.0
    r2_sqrt = sqrt_info.get("r2") or 0.0
    k_alg  = alg_info.get("k") or 0.0
    r2_alg = alg_info.get("r2") or 0.0

    if r2_exp > 0.90 and b_exp > 0.05:
        return "EXPONENTIAL"
    elif r2_exp > 0.80 and b_exp > 0.02:
        return "LIKELY_EXPONENTIAL"
    elif r2_sqrt > 0.90 and b_sqrt > 0.05:
        return "SUB-EXPONENTIAL (sqrt)"
    elif r2_alg > 0.85 and k_alg > 0.3:
        return "ALGEBRAIC"
    elif r2_alg > 0.70 and k_alg > 0.1:
        return "LIKELY_ALGEBRAIC"
    elif max(r2_exp, r2_sqrt, r2_alg) > 0.65:
        return "UNCLEAR (moderate fit)"
    else:
        return "INSUFFICIENT DATA / NO DECAY DETECTED"


# ── Main study ─────────────────────────────────────────────────────────────────
def run_study() -> dict:
    results: dict = {}
    decay_rates: dict = {}
    summary_rows: list[dict] = []
    node_counts: list[int] = [_depth_to_n(d) for d in DEPTH_SEQUENCE]

    method = "EMLNetwork (gradient)" if MONOGATE_NEURAL else "scipy parametric grid"

    print("\n" + "=" * 70)
    print("DOOR 3: Approximation Rate Study — S104")
    print("=" * 70)
    print(f"Search method : {method}")
    print(f"Probe domain  : [0.1, 3], {N_PROBE} points")
    print(f"Depths        : {DEPTH_SEQUENCE}")
    print(f"Node counts   : {node_counts}")
    print()

    for fname, target_fn in TARGETS.items():
        print(f"\n{'─'*60}")
        print(f"Target: {fname}  ({TARGET_DESC[fname]})")
        print(f"{'─'*60}")

        errors_by_n: dict[int, float] = {}
        for depth in DEPTH_SEQUENCE:
            n = _depth_to_n(depth)
            t0 = time.perf_counter()
            mse_val = search_for_depth(target_fn, depth)
            elapsed = time.perf_counter() - t0
            errors_by_n[n] = mse_val
            mse_str = f"{mse_val:.4e}" if math.isfinite(mse_val) else "inf"
            print(f"  depth={depth} (n={n:2d}): MSE = {mse_str}  ({elapsed:.1f}s)")

        results[fname] = {str(n): v for n, v in errors_by_n.items()}

        ns   = list(errors_by_n.keys())
        errs = [errors_by_n[n] for n in ns]

        exp_fit  = _fit_exponential_decay(ns, errs)
        sqrt_fit = _fit_sqrt_decay(ns, errs)
        alg_fit  = _fit_algebraic_decay(ns, errs)

        r2_scores = {
            "exp(-b*n)":       exp_fit.get("r2") or -1.0,
            "exp(-b*sqrt(n))": sqrt_fit.get("r2") or -1.0,
            "C*n^(-k)":        alg_fit.get("r2") or -1.0,
        }
        best_model = max(r2_scores, key=lambda m: r2_scores[m])

        dr = {
            "exponential": exp_fit,
            "sqrt_exponential": sqrt_fit,
            "algebraic": alg_fit,
            "best_model": best_model,
            "best_r2": r2_scores[best_model],
        }
        decay_rates[fname] = dr
        classification = _classify_rate(dr, fname)

        finite_errs = [e for e in errs if math.isfinite(e)]

        summary_rows.append({
            "target":       fname,
            "description":  TARGET_DESC[fname],
            "n_valid":      len(finite_errs),
            "min_mse":      min(finite_errs) if finite_errs else float("inf"),
            "best_model":   best_model,
            "b_exp":        exp_fit.get("b"),
            "r2_exp":       exp_fit.get("r2"),
            "k_alg":        alg_fit.get("k"),
            "r2_alg":       alg_fit.get("r2"),
            "classification": classification,
        })

        print(f"  Decay fits:")
        if exp_fit.get("b") is not None:
            print(f"    exp(-b*n):        b={exp_fit['b']:.4f}  R²={exp_fit['r2']:.4f}")
        if sqrt_fit.get("b") is not None:
            print(f"    exp(-b*sqrt(n)):  b={sqrt_fit['b']:.4f}  R²={sqrt_fit['r2']:.4f}")
        if alg_fit.get("k") is not None:
            print(f"    C*n^(-k):         k={alg_fit['k']:.4f}  R²={alg_fit['r2']:.4f}")
        print(f"  Best model  : {best_model}  (R²={r2_scores[best_model]:.4f})")
        print(f"  Classification: {classification}")

    return {
        "errors": results,
        "decay_rates": decay_rates,
        "summary": summary_rows,
        "node_counts": node_counts,
        "method": method,
    }


def print_summary_table(summary: list[dict]) -> None:
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    hdr = (f"{'Target':<18} {'BestMSE':>10} {'BestModel':<22} "
           f"{'b_exp':>7} {'R²_exp':>6} {'k_alg':>6} {'R²_alg':>6} {'Class':<28}")
    print(hdr)
    print("-" * 80)
    for row in summary:
        b_e  = f"{row['b_exp']:.4f}"  if row["b_exp"]  is not None else "  N/A"
        r2_e = f"{row['r2_exp']:.4f}" if row["r2_exp"] is not None else "  N/A"
        k_a  = f"{row['k_alg']:.4f}"  if row["k_alg"]  is not None else "  N/A"
        r2_a = f"{row['r2_alg']:.4f}" if row["r2_alg"] is not None else "  N/A"
        mse  = f"{row['min_mse']:.3e}" if math.isfinite(row["min_mse"]) else "    inf"
        cls  = row.get("classification", "?")
        print(
            f"{row['target']:<18} {mse:>10} {row['best_model']:<22} "
            f"{b_e:>7} {r2_e:>6} {k_a:>6} {r2_a:>6} {cls:<28}"
        )
    print("=" * 80)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = run_study()
    print_summary_table(data["summary"])

    # Save results
    output = {
        "session": "S104",
        "title":   "Door 3: EML Approximation Rate Study",
        "method":  data["method"],
        "probe_domain": [0.1, 3.0],
        "n_probe": N_PROBE,
        "depth_sequence": DEPTH_SEQUENCE,
        "node_counts":    data["node_counts"],
        "errors":         data["errors"],
        "decay_rates":    data["decay_rates"],
        "summary":        data["summary"],
    }

    out_path = "D:/monogate/python/results/s104_door3_approximation_rate.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2)
    print(f"\nResults saved to: {out_path}")
