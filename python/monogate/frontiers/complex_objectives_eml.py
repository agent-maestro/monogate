"""Session 28 — Objective Functions for Complex EML Search.

Defines R², MAE, phase-aware loss, and analytic continuation score
for complex-valued symbolic regression targets.
"""

import cmath
import math
from typing import Callable, Dict, List, Tuple

__all__ = ["run_session28"]


def ceml(z1: complex, z2: complex) -> complex:
    return cmath.exp(z1) - cmath.log(z2)


# ---------------------------------------------------------------------------
# Objective functions
# ---------------------------------------------------------------------------

def r2_real(pred: List[float], true: List[float]) -> float:
    mean_t = sum(true) / len(true)
    ss_tot = sum((t - mean_t)**2 for t in true)
    ss_res = sum((p - t)**2 for p, t in zip(pred, true))
    return 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else (1.0 if ss_res < 1e-12 else 0.0)


def r2_complex(pred: List[complex], true: List[complex]) -> float:
    mean_t = sum(true) / len(true)
    ss_tot = sum(abs(t - mean_t)**2 for t in true)
    ss_res = sum(abs(p - t)**2 for p, t in zip(pred, true))
    return 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else (1.0 if ss_res < 1e-12 else 0.0)


def mae_real(pred: List[float], true: List[float]) -> float:
    return sum(abs(p - t) for p, t in zip(pred, true)) / len(pred)


def mae_complex(pred: List[complex], true: List[complex]) -> float:
    return sum(abs(p - t) for p, t in zip(pred, true)) / len(pred)


def phase_loss(pred: List[complex], true: List[complex]) -> float:
    """Phase-aware loss: penalizes both magnitude and phase errors."""
    mag_loss = sum((abs(p) - abs(t))**2 for p, t in zip(pred, true))
    phase_loss_val = sum(abs(cmath.phase(p) - cmath.phase(t))**2
                         for p, t in zip(pred, true)
                         if abs(p) > 1e-10 and abs(t) > 1e-10)
    return (mag_loss + phase_loss_val) / len(pred)


def modulus_r2(pred: List[complex], true: List[complex]) -> float:
    """R² on |·| only — for matching modulus."""
    pred_abs = [abs(p) for p in pred]
    true_abs = [abs(t) for t in true]
    return r2_real(pred_abs, true_abs)


def real_imag_r2(pred: List[complex], true: List[complex]) -> Tuple[float, float]:
    """Separate R² for real and imaginary parts."""
    pred_re = [p.real for p in pred]
    pred_im = [p.imag for p in pred]
    true_re = [t.real for t in true]
    true_im = [t.imag for t in true]
    return r2_real(pred_re, true_re), r2_real(pred_im, true_im)


def analytic_continuation_score(
    fn: Callable[[complex], complex],
    real_pts: List[float],
    eps: float = 1e-6,
) -> float:
    """Check if fn satisfies Cauchy-Riemann numerically — returns score 0-1."""
    scores = []
    for xv in real_pts:
        x = complex(xv)
        try:
            # Numerical partial derivatives
            f0 = fn(x)
            fdx = fn(x + eps)
            fdy = fn(x + 1j*eps)
            du_dx = (fdx.real - f0.real) / eps
            dv_dx = (fdx.imag - f0.imag) / eps
            du_dy = (fdy.real - f0.real) / eps
            dv_dy = (fdy.imag - f0.imag) / eps
            # CR: du/dx = dv/dy and du/dy = -dv/dx
            cr1 = abs(du_dx - dv_dy)
            cr2 = abs(du_dy + dv_dx)
            cr_err = (cr1 + cr2) / 2
            scores.append(1.0 / (1.0 + cr_err))
        except Exception:
            scores.append(0.0)
    return sum(scores) / len(scores) if scores else 0.0


# ---------------------------------------------------------------------------
# Benchmark all objectives
# ---------------------------------------------------------------------------

def benchmark_objectives() -> Dict:
    test_pts_real = [0.3, 0.5, 0.7, 1.0, 1.2, 1.5, 2.0]

    results = {}

    # sin(x): pred = Im(ceml(ix,1)); true = math.sin
    pred_sin = [ceml(1j*complex(xv), 1+0j).imag for xv in test_pts_real]
    true_sin = [math.sin(xv) for xv in test_pts_real]
    results["sin_r2"] = r2_real(pred_sin, true_sin)
    results["sin_mae"] = mae_real(pred_sin, true_sin)

    # exp(ix): complex target
    pred_euler = [ceml(1j*complex(xv), 1+0j) for xv in test_pts_real]
    true_euler = [cmath.exp(1j*complex(xv)) for xv in test_pts_real]
    results["euler_r2_complex"] = r2_complex(pred_euler, true_euler)
    results["euler_modulus_r2"] = modulus_r2(pred_euler, true_euler)
    results["euler_phase_loss"] = phase_loss(pred_euler, true_euler)
    re_r2, im_r2 = real_imag_r2(pred_euler, true_euler)
    results["euler_re_r2"] = re_r2
    results["euler_im_r2"] = im_r2

    # Analytic continuation score for ceml(ix, 1)
    ac_score = analytic_continuation_score(
        lambda x: ceml(1j*x, 1+0j),
        test_pts_real,
    )
    results["euler_analytic_score"] = ac_score

    # Analytic continuation score for sin (NOT analytic as complex function — real-valued)
    ac_sin = analytic_continuation_score(
        lambda x: complex(math.sin(x.real)),
        test_pts_real,
    )
    results["sin_analytic_score"] = ac_sin

    return results


# ---------------------------------------------------------------------------
# Depth-weighted loss
# ---------------------------------------------------------------------------

def depth_weighted_loss(r2: float, depth: int, lambda_: float = 0.1) -> float:
    """Penalize deep trees: loss = (1-R²) + lambda*depth."""
    return (1.0 - r2) + lambda_ * depth


def optimal_depth_tradeoff() -> List[Dict]:
    """Evaluate depth-weighted loss for various depth/R2 combinations."""
    results = []
    for depth in [1, 2, 3, 5]:
        for r2 in [0.95, 0.99, 0.999, 1.0]:
            loss = depth_weighted_loss(r2, depth)
            results.append({"depth": depth, "r2": r2, "depth_weighted_loss": loss})
    return results


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_session28() -> Dict:
    bench = benchmark_objectives()
    tradeoff = optimal_depth_tradeoff()

    key_findings = [
        f"sin(x) R² = {bench['sin_r2']:.6f} (should be 1.0)",
        f"Euler exp(ix) complex R² = {bench['euler_r2_complex']:.6f}",
        f"Euler modulus R² = {bench['euler_modulus_r2']:.6f}",
        f"Euler analytic continuation score = {bench['euler_analytic_score']:.4f} (higher=more analytic)",
        f"sin(x) analytic score = {bench['sin_analytic_score']:.4f} (should be lower - not complex-analytic)",
    ]

    objectives_summary = {
        "for_real_targets": ["r2_real", "mae_real"],
        "for_complex_targets": ["r2_complex", "mae_complex", "modulus_r2", "phase_loss"],
        "for_analyticity": ["analytic_continuation_score"],
        "for_search": ["depth_weighted_loss = (1-R²) + lambda*depth"],
    }

    return {
        "session": 28,
        "title": "Objective Functions for Complex EML Search",
        "benchmark_results": bench,
        "depth_tradeoff": tradeoff,
        "objectives_summary": objectives_summary,
        "key_findings": key_findings,
        "recommendation": (
            "For complex EML search: use r2_complex as primary metric + "
            "depth_weighted_loss(lambda=0.1) to prefer shallow trees. "
            "Use analytic_continuation_score as a bonus reward for holomorphic expressions."
        ),
        "status": "PASS" if bench["sin_r2"] > 0.999 else "PARTIAL",
    }
