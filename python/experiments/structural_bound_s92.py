"""
S92 — Arg Distribution: Why SB Holds Despite Analytical Failure

S91 showed:
  - Re(z) is NOT bounded below by 1 (goes to -15 at depth 5).
  - Induction step fails analytically: eml(real, y_complex) can give Im > 0.
  - But SB still holds empirically at depth ≤ 5.

KEY QUESTION: What is the arg distribution of EML₁ elements?
  Specifically: all complex elements at depth ≤ 5 have Im < 0 and large |arg|.
  If arg(z) is always close to -π for complex z ∈ EML₁, then:
    Im(eml(x, z)) = exp(Re(x))·sin(Im(x)) − arg(z) ≈ exp(Re(x))·sin(Im(x)) + π
    This could be positive only if exp(Re(x))·|sin(Im(x))| < π.

Goal: catalog arg(z) for all complex z ∈ EML₁ at depth ≤ 5 and find the
minimum |arg(z)|.  If min |arg| = π (i.e., all complex elements have arg = -π),
then SB is trivially preserved!

ALSO: Track the Im-part distribution more carefully. From S90:
  min_im = -π, max_im = 0. The minimum is EXACTLY -π.
  This suggests: Im(z) ∈ {0, -π} for z ∈ EML₁ at depth ≤ 5? Check this.
"""

import json
import math
import cmath
from pathlib import Path
from collections import Counter

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
    print("S92 — Arg Distribution Analysis")
    print("=" * 60)
    print()

    vals = build_closure_layered(5)
    complex_vals = [(v, d, e) for v, d, e in vals if abs(v.imag) > 1e-10]
    print(f"Total values: {len(vals)}")
    print(f"Complex values (Im != 0): {len(complex_vals)}")
    print()

    # Im distribution
    im_vals = [v.imag for v, d, e in complex_vals]
    print(f"Im range among complex: [{min(im_vals):.10f}, {max(im_vals):.10f}]")
    print(f"Im/pi range:            [{min(im_vals)/PI:.10f}, {max(im_vals)/PI:.10f}]")
    print()

    # Check: is Im exactly -π for all complex values?
    im_exactly_neg_pi = sum(1 for v in im_vals if abs(v + PI) < 1e-7)
    im_other = sum(1 for v in im_vals if abs(v + PI) >= 1e-7)
    print(f"Complex values with Im = -pi (tol 1e-7): {im_exactly_neg_pi}")
    print(f"Complex values with Im != -pi:           {im_other}")
    print()

    if im_other > 0:
        other_vals = [(v, d, e) for v, d, e in complex_vals if abs(v.imag + PI) >= 1e-7]
        print("Sample non-(-pi) complex values:")
        for v, d, e in sorted(other_vals, key=lambda x: x[0].imag, reverse=True)[:10]:
            print(f"  depth {d}: Im={v.imag:.8f} (Im/pi={v.imag/PI:.8f}), Re={v.real:.6f}")
        print()

    # Arg distribution
    args = [cmath.phase(v) for v, d, e in complex_vals]
    print(f"Arg range: [{min(args):.10f}, {max(args):.10f}]")
    print(f"Arg/pi:    [{min(args)/PI:.10f}, {max(args)/PI:.10f}]")
    print()

    # Check: is arg always = -π?
    arg_exactly_neg_pi = sum(1 for a in args if abs(a + PI) < 1e-7)
    arg_not_neg_pi = sum(1 for a in args if abs(a + PI) >= 1e-7)
    print(f"Complex values with arg(z) = -pi: {arg_exactly_neg_pi}")
    print(f"Complex values with arg(z) != -pi: {arg_not_neg_pi}")
    print()

    if arg_not_neg_pi > 0:
        other_args = [(v, d, e) for v, d, e in complex_vals if abs(cmath.phase(v) + PI) >= 1e-7]
        print("Sample values with arg != -pi:")
        for v, d, e in sorted(other_args, key=lambda x: cmath.phase(x[0]), reverse=True)[:10]:
            a = cmath.phase(v)
            print(f"  depth {d}: arg={a:.8f} (arg/pi={a/PI:.8f}), Re={v.real:.6f}, Im={v.imag:.8f}")
        print()

    # Min |arg| among complex values
    min_abs_arg = min(abs(a) for a in args)
    max_abs_arg = max(abs(a) for a in args)
    print(f"Min |arg| among complex EML₁ values: {min_abs_arg:.10f}")
    print(f"Max |arg|:                            {max_abs_arg:.10f}")
    print(f"Min |arg|/pi:                         {min_abs_arg/PI:.10f}")
    print()

    # KEY: if min |arg| = pi, then all complex values have arg = -pi
    # and Im(eml(real_x, complex_y)) = -arg(y) = pi > 0 — VIOLATION!
    # But wait: we showed Im(z) in EML₁ are all negative. So eml(real, complex_y) with
    # arg(y) = -pi gives Im = pi > 0 — but that value is NOT observed in EML₁.
    # This means: real x combined with complex y (arg=-pi) DOES give Im = pi > 0,
    # but this value is NOT in our closure! Why?
    # Because our closure ONLY starts from 1, builds recursively, and is closed.
    # The value eml(1, y) where Im(y) = -pi gives Im = pi.
    # But Im = pi values ARE reachable if we allow combining real x with those y.

    print("Critical test: eml(real_x, y_with_arg_neg_pi) = ?")
    # Take x = 1 (real), y = first complex element (Im = -pi)
    # From S72: first complex is at depth 5: z = e - exp(e) - i*pi ≈ -15.15 - 3.14i
    first_complex = complex(-15.154262, -3.141593)
    for x_re in [1.0, 0.0, math.e, -1.0]:
        x = complex(x_re, 0)
        result = eml(x, first_complex)
        if result:
            print(f"  eml({x_re}, {first_complex:.4f}) = {result:.6f}  [Im={result.imag:.6f}]")

    print()
    print("CONCLUSION:")
    if arg_not_neg_pi == 0:
        print("  ALL complex EML₁ values have arg = -pi (Im/pi = -1 exactly).")
        print("  Combining real x with these gives Im(eml) = pi > 0.")
        print("  This SHOULD violate SB — but it does in principle!")
        print("  The resolution: eml(real, complex_arg_neg_pi) gives Im = pi,")
        print("  but this pi value is ALSO a multiple of pi. Not 1.")
        print("  SB would then give: Im(EML₁) ⊆ {0, -pi, pi, -2pi, ...}?")
        print("  But we only see {0, -pi} at depth ≤ 5. Depth 6+ might show pi.")
    else:
        print("  Complex EML₁ values have diverse arg values.")
        print("  SB preservation requires |arg(y)| ≥ exp(Re(x))|sin(Im(x))| for all valid pairs.")

    RESULT = {
        "session": "S92",
        "title": "Arg Distribution Analysis",
        "total_values": len(vals),
        "complex_count": len(complex_vals),
        "im_range": [min(im_vals), max(im_vals)],
        "im_all_neg_pi": im_other == 0,
        "im_exactly_neg_pi_count": im_exactly_neg_pi,
        "im_other_count": im_other,
        "arg_range": [min(args), max(args)],
        "arg_all_neg_pi": arg_not_neg_pi == 0,
        "min_abs_arg": min_abs_arg,
        "key_finding": (
            "At depth <= 5: ALL complex EML₁ values have Im = -pi (exactly). "
            "So arg(z) = -pi for all complex z. "
            "eml(real, z_complex) gives Im = pi > 0. "
            "This IS reachable — so Im = pi WILL appear at depth 6+. "
            "SB (Im <= 0) will be VIOLATED at depth 6!"
            if im_other == 0 else
            "Complex values have diverse Im parts."
        ),
        "prediction": "Im = pi will appear at depth 6 via eml(real, complex_arg_neg_pi)",
    }

    out_path = results_dir / "s92_arg_distribution.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(RESULT, f, indent=2)
    print(f"\nResults: {out_path}")
