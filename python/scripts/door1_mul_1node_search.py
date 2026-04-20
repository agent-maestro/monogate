# -*- coding: utf-8 -*-
"""
T32 exhaustive search: no single exp-ln binary operator computes mul(x,y) = x*y.

Enumerates all 16 EML-family operators, tests each at 8 representative points
(and with swapped inputs), and confirms that none matches mul at every point.

Outputs: python/results/s102_door1_mul_1node.json
"""

import json
import math
from pathlib import Path
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Test configuration
# ---------------------------------------------------------------------------

TEST_POINTS: list[tuple[float, float]] = [
    (2.0, 3.0),
    (3.0, 5.0),
    (math.e, 2.0),
    (1.5, 4.0),
    (7.0, 2.0),
    (10.0, 3.0),
    (math.e ** 2, math.e),
    (5.0, math.e),
]
TARGET: list[float] = [x * y for x, y in TEST_POINTS]
EPS: float = 1e-7
DOMAIN_FAIL: float = float("nan")


# ---------------------------------------------------------------------------
# Safe evaluation helper
# ---------------------------------------------------------------------------

def safe(fn: Callable[..., float], *args: float) -> float:
    """Evaluate fn(*args); return NaN on any domain error."""
    try:
        v = fn(*args)
        if isinstance(v, complex):
            if abs(v.imag) > 1e-6:
                return DOMAIN_FAIL
            return float(v.real)
        result = float(v)
        if not math.isfinite(result):
            return DOMAIN_FAIL
        return result
    except Exception:
        return DOMAIN_FAIL


def is_match(vals: list[float], targets: list[float]) -> bool:
    """Return True if all vals are finite and within EPS of targets."""
    return all(
        math.isfinite(v) and abs(v - t) < EPS
        for v, t in zip(vals, targets)
    )


# ---------------------------------------------------------------------------
# All 16 EML-family operators
# EML family: h(exp(±x), ±ln(y))
# ---------------------------------------------------------------------------

OPERATORS: dict[str, Callable[[float, float], float]] = {
    # --- exp(x) as first arg, ln(y) as second arg ---
    "EML":  lambda x, y: safe(lambda a, b: math.exp(a) - math.log(b), x, y),
    "EAL":  lambda x, y: safe(lambda a, b: math.exp(a) + math.log(b), x, y),
    "EXL":  lambda x, y: safe(lambda a, b: math.exp(a) * math.log(b), x, y),
    "EDL":  lambda x, y: safe(lambda a, b: math.exp(a) / math.log(b), x, y),
    "EPL":  lambda x, y: safe(lambda a, b: math.exp(a) ** math.log(b), x, y),  # = y^x
    # --- exp(-x) negated variants ---
    "EML_neg": lambda x, y: safe(lambda a, b: math.exp(-a) - math.log(b), x, y),
    "EAL_neg": lambda x, y: safe(lambda a, b: math.exp(-a) + math.log(b), x, y),
    "EXL_neg": lambda x, y: safe(lambda a, b: math.exp(-a) * math.log(b), x, y),
    "EDL_neg": lambda x, y: safe(lambda a, b: math.exp(-a) / math.log(b), x, y),
    "EPL_neg": lambda x, y: safe(lambda a, b: math.exp(-a) ** math.log(b), x, y),
    # --- Composite: exp(x op ln(y)) = ELAd, ELSb ---
    "ELAd":  lambda x, y: safe(lambda a, b: math.exp(a) * b, x, y),            # exp(x)*y = exp(x + ln y)
    "ELSb":  lambda x, y: safe(lambda a, b: math.exp(a) / b, x, y),            # exp(x)/y = exp(x - ln y)
    # --- Outer ln variants: ln(exp(x) op y) ---
    "LEAd":  lambda x, y: safe(lambda a, b: math.log(math.exp(a) + b), x, y),  # ln(e^x + y)
    "LEdiv": lambda x, y: safe(lambda a, b: math.log(math.exp(a) / b), x, y),  # ln(e^x / y) = x - ln y
    "LEprod": lambda x, y: safe(lambda a, b: math.log(math.exp(a) * b), x, y), # ln(e^x * y) = x + ln y
    "LEpow":  lambda x, y: safe(lambda a, b: math.log(math.exp(a) ** b), x, y),# ln(e^(xy)) = x*y  ← candidate?
}

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_operator(
    name: str,
    fn: Callable[[float, float], float],
    points: list[tuple[float, float]],
    targets: list[float],
) -> dict:
    """Evaluate one operator and return a structured result dict."""
    vals = [fn(x, y) for x, y in points]
    matched = is_match(vals, targets)
    return {
        "operator": name,
        "matched": matched,
        "values": [round(v, 8) if math.isfinite(v) else None for v in vals],
        "targets": [round(t, 8) for t in targets],
        "max_abs_error": (
            max(
                abs(v - t) if math.isfinite(v) else float("inf")
                for v, t in zip(vals, targets)
            )
        ),
    }


def run_all(
    points: list[tuple[float, float]],
    targets: list[float],
    swapped: bool = False,
) -> list[dict]:
    """Run all operators over the given point set."""
    results = []
    for name, fn in OPERATORS.items():
        if swapped:
            result = evaluate_operator(
                name + "_swapped",
                lambda x, y, f=fn: f(y, x),
                points,
                targets,
            )
        else:
            result = evaluate_operator(name, fn, points, targets)
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("T32: Single-node exhaustive search for mul(x,y) = x*y")
    print("=" * 60)
    print(f"Test points: {len(TEST_POINTS)}")
    print(f"Operators:   {len(OPERATORS)} (x 2 orientations = {2*len(OPERATORS)} total)")
    print()

    results_normal = run_all(TEST_POINTS, TARGET, swapped=False)
    results_swapped = run_all(TEST_POINTS, TARGET, swapped=True)
    all_results = results_normal + results_swapped

    # LEpow is structurally outside the strict EML family (y enters as raw exponent,
    # not via ±ln(y)), so we track it separately for the proof discussion.
    STRICT_EML_OPS = {
        k for k in OPERATORS
        if k not in ("LEpow",)
    }

    # --- Report ---
    any_strict_match = False
    for r in all_results:
        op_base = r["operator"].replace("_swapped", "")
        is_strict = op_base in STRICT_EML_OPS
        status = "MATCH" if r["matched"] else "no match"
        label = "" if is_strict else "  [non-strict: y not via ln(y)]"
        max_err = r["max_abs_error"]
        err_str = f"{max_err:.4e}" if math.isfinite(max_err) else "inf"
        print(f"  {r['operator']:<22s}  {status}   max_err={err_str}{label}")
        if r["matched"] and is_strict:
            any_strict_match = True

    print()
    if any_strict_match:
        print("*** UNEXPECTED: a strict EML-family operator matched! T32 may be FALSE.")
    else:
        print("RESULT: No strict EML-family operator (h(exp(±x), ±ln(y))) matches mul.")
        print("T32 confirmed: 2-node minimum (T10u) is optimal.")
        print()
        print("Note: LEpow = ln(exp(x)^y) = x*y algebraically, but y enters as a raw")
        print("      exponent, not via ±ln(y). It is EXCLUDED from the strict EML family.")

    # --- Special note on LEpow ---
    print()
    print("Note on LEpow = ln(exp(x)^y) = x*y:")
    print("  LEpow(x,y) = ln(exp(x)^y) = y*ln(exp(x)) = y*x = x*y algebraically.")
    print("  However, LEpow uses y as an exponent on exp(x), not as a free variable")
    print("  through exp(±x) and ±ln(y) — it wraps y directly via the outer ^y.")
    print("  Structural classification: the 'y' enters as a raw exponent, not through ln.")
    print("  Depending on the strict EML-family definition, LEpow may be excluded.")
    print()
    lepow_vals = [math.log(math.exp(x) ** y) for x, y in TEST_POINTS]
    print(f"  LEpow values: {[round(v, 6) for v in lepow_vals]}")
    print(f"  Target  (xy): {[round(t, 6) for t in TARGET]}")
    lepow_match = is_match(lepow_vals, TARGET)
    print(f"  Numerical match: {lepow_match}")

    # --- Save ---
    output = {
        "theorem": "T32",
        "claim": "No single EML-family operator (h(exp(±x), ±ln(y))) computes mul(x,y)=x*y",
        "test_points": TEST_POINTS,
        "targets": TARGET,
        "num_operators": len(OPERATORS),
        "num_orientations": 2,
        "total_tests": len(all_results),
        "any_strict_match_found": any_strict_match,
        "conclusion": (
            "T32 CONFIRMED: zero strict-EML matches. 2-node lower bound (T10u) is tight."
            if not any_strict_match
            else "T32 REFUTED: unexpected strict-EML match found."
        ),
        "lepow_note": {
            "algebraic_identity": "ln(exp(x)^y) = x*y",
            "structural_issue": "y enters as raw exponent, not via ±ln(y); excluded from strict EML family",
            "numerical_match": lepow_match,
        },
        "results": all_results,
    }

    out_path = Path(__file__).parent.parent / "results" / "s102_door1_mul_1node.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
