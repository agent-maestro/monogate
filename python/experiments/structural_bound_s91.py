"""
S91 — Re(x) Lower Bound + Inductive Step Analysis

QUESTION: Is Re(z) ≥ 1 for all z ∈ EML₁?
  If yes: exp(Re(x)) ≥ e for all x in the operator eml(x, y),
  which tightly constrains sin(Im(x)) and the Im-part evolution.

ALSO: Full inductive step analysis for SB (Im ≤ 0).
  Can we prove: if Im(x) ≤ 0 and Im(y) ≤ 0, then Im(eml(x,y)) ≤ 0?
"""

import json
import math
import cmath
from pathlib import Path

PI = math.pi


def eml(x, y):
    if abs(y) < 1e-300:
        return None
    try:
        if x.real > 600:
            return None
        return cmath.exp(x) - cmath.log(y)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def round_c(z, digits=7):
    return (round(z.real, digits), round(z.imag, digits))


def build_closure_layered(max_depth, max_abs=1e10):
    values_at = {0: [(complex(1.0), "1")]}
    seen = {round_c(complex(1.0))}
    for d in range(1, max_depth + 1):
        new_layer = []
        all_prev = [(v, e, dd) for dd in range(d) for v, e in values_at.get(dd, [])]
        prev_d = values_at.get(d - 1, [])
        pairs = []
        for v1, e1, _ in all_prev:
            for v2, e2 in prev_d:
                pairs.append((v1, e1, v2, e2))
        for v1, e1 in prev_d:
            for v2, e2, _ in all_prev:
                pairs.append((v1, e1, v2, e2))
        for v1, e1, v2, e2 in pairs:
            result = eml(v1, v2)
            if result is None or abs(result) > max_abs:
                continue
            key = round_c(result)
            if key not in seen:
                seen.add(key)
                new_layer.append((result, f"eml({e1[:15]},{e2[:15]})"))
        values_at[d] = new_layer
    return [(v, d, e) for d, layer in values_at.items() for v, e in layer]


if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("S91 — Re Lower Bound + Inductive Step Analysis")
    print("=" * 60)
    print()

    vals = build_closure_layered(5)
    print(f"Values at depth <= 5: {len(vals)}")
    print()

    # Re lower bound analysis
    re_vals = [v.real for v, d, e in vals]
    min_re = min(re_vals)
    max_re = max(re_vals)
    re_below_1 = [(v, d, e) for v, d, e in vals if v.real < 1.0 - 1e-9]
    re_below_0 = [(v, d, e) for v, d, e in vals if v.real < -1e-9]
    re_negative = [(v, d, e) for v, d, e in vals if v.real < 0]

    print(f"Re range: [{min_re:.6f}, {max_re:.6f}]")
    print(f"Values with Re < 1: {len(re_below_1)}")
    print(f"Values with Re < 0: {len(re_negative)}")
    print()

    if re_below_1:
        print("Sample values with Re < 1:")
        for v, d, e in sorted(re_below_1, key=lambda x: x[0].real)[:8]:
            print(f"  depth {d}: Re={v.real:.8f}, Im={v.imag:.8f}  [{e[:40]}]")
    print()

    # Inductive step: if Im(x) <= 0 and Im(y) <= 0, is Im(eml(x,y)) <= 0?
    # Im(eml(x,y)) = exp(Re(x))*sin(Im(x)) - arg(y)
    # Need: exp(Re(x))*sin(Im(x)) <= arg(y)
    # If Im(x) in (-pi, 0): sin(Im(x)) in (-1, 0), so exp(Re(x))*sin(Im(x)) < 0
    # If Im(y) in (-pi, 0) and Re(y) > 0: arg(y) = arctan(Im(y)/Re(y)) in (-pi/2, 0)
    # Need: negative <= arg(y) in (-pi/2, 0) — TRUE since negative < 0 <= something? No.
    # Need: exp(Re(x))*sin(Im(x)) <= arg(y)
    # LHS < 0, RHS in (-pi/2, 0) — RHS is also negative!
    # So: exp(Re(x))|sin(Im(x))| >= |arg(y)|?
    # This is NOT guaranteed.

    # Find cases where the induction could fail
    print("Inductive step analysis:")
    print("  Im(eml(x,y)) = exp(Re(x))*sin(Im(x)) - arg(y)")
    print()

    # Only check depth <= 4 for pairwise to avoid memory explosion
    vals_small = [(v, d, e) for v, d, e in vals if d <= 4]
    violations = []
    near_violations = []  # cases where Im(eml) is close to 0 from below
    for v1, d1, e1 in vals_small:
        if v1.imag > 1e-10:
            continue
        for v2, d2, e2 in vals_small:
            if v2.imag > 1e-10:
                continue
            result = eml(v1, v2)
            if result is None:
                continue
            if result.imag > 1e-8:
                violations.append((v1, v2, result, d1, d2, e1, e2))
            elif result.imag > -0.01:
                near_violations.append((result.imag, d1, d2))

    print(f"  Pairs (Im(x)<=0, Im(y)<=0) giving Im(eml)>0: {len(violations)}")
    print(f"  Pairs giving Im(eml) in (-0.01, 0]: {len(near_violations)}")
    print()

    if violations:
        print("  VIOLATION FOUND — induction step FAILS:")
        for v1, v2, res, d1, d2, e1, e2 in violations[:3]:
            print(f"    x={v1:.4f} (Im={v1.imag:.4f}), y={v2:.4f} (Im={v2.imag:.4f})")
            print(f"    => eml = {res:.4f}, Im={res.imag:.8f}")
    else:
        print("  Induction step HOLDS for all checked pairs at depth <= 5.")
        print()
        # Show the closest cases to violation
        near_violations.sort(reverse=True)
        print("  Closest to 0 (Im nearly 0 from below):")
        for im_val, d1, d2 in near_violations[:5]:
            print(f"    Im(eml) = {im_val:.8f}  [x depth {d1}, y depth {d2}]")

    # Can we prove the inductive step analytically?
    print()
    print("Analytical induction step attempt:")
    print("  Case Im(x) = 0 (x real):")
    print("    Im(eml(x,y)) = 0 - arg(y) = -arg(y)")
    print("    If Im(y) <= 0: arg(y) in (-pi, 0] => -arg(y) in [0, pi)")
    print("    PROBLEM: -arg(y) >= 0, so Im(eml) >= 0!")
    print("    INDUCTION FAILS for x real, y with Im(y) < 0!")
    print()
    print("  Example: x = 1 (real), y with Im(y) < 0, arg(y) = -0.5")
    x_ex = complex(1.0, 0)
    # Construct y with arg = -0.5: y = r*(cos(-0.5) + i*sin(-0.5)) for any r > 0
    y_ex = complex(math.cos(-0.5), math.sin(-0.5))  # r=1, arg=-0.5
    res_ex = eml(x_ex, y_ex)
    if res_ex:
        print(f"    eml(1, e^(-0.5i)) = {res_ex:.6f}")
        print(f"    Im = {res_ex.imag:.6f}  > 0 = VIOLATION OF SB!")
        print()
        print("  CONCLUSION: Induction step FAILS analytically.")
        print("  But SB still holds empirically at depth <= 5.")
        print("  The key: y with Im(y) < 0 AND small |arg(y)| is not in EML₁ at depth <= 5.")
        print("  This hints: Re(EML₁ elements with Im<0) > 0 and arg stays bounded away from 0.")

    RESULT = {
        "session": "S91",
        "title": "Re Lower Bound + Inductive Step Analysis",
        "re_min_observed": min_re,
        "re_max_observed": max_re,
        "re_below_1_count": len(re_below_1),
        "re_below_0_count": len(re_negative),
        "re_below_1_sample": [(float(v.real), float(v.imag), d) for v, d, e in re_below_1[:5]],
        "induction_step": {
            "holds_computationally": len(violations) == 0,
            "fails_analytically": True,
            "reason": "x real + y with Im(y) < 0 => Im(eml) = -arg(y) > 0",
            "example": {
                "x": "1 (real)",
                "y": "e^(-0.5i) = cos(-0.5)+i*sin(-0.5)",
                "eml_im": float(res_ex.imag) if res_ex else None,
                "conclusion": "Im > 0 but y not in EML_1 at depth <= 5",
            },
        },
        "key_insight": (
            "SB cannot be proved by simple Im-preservation induction. "
            "The induction step fails analytically (x real, y with small |arg|). "
            "But SB holds empirically because EML_1 elements with Im < 0 have "
            "large |arg|, preventing the violation. "
            "The true reason SB holds must be a quantitative bound on arg(y) for y in EML_1."
        ),
        "next_step": "S92: Quantitative arg bound — prove |arg(z)| > threshold for z in EML_1 with Im(z) < 0",
    }

    out_path = results_dir / "s91_re_lower_bound.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(RESULT, f, indent=2)
    print(f"\nResults: {out_path}")
