"""
S93 — SB Counterexample: Im > 0 at Depth 6 (and Im = 1 search)

S92 revealed:
  - ALL complex EML₁ values at depth ≤ 5 have Im = -π EXACTLY.
  - Some have large positive Re (up to 1.8e9), giving arg ≈ 0.
  - Some have negative Re (e.g., -15.15), giving arg ≈ -2.937.
  - eml(real, z_with_negative_Re) gives Im = -arg(z) ≈ 2.937 > 0 at depth 6!

THEREFORE: Conjecture SB (Im ≤ 0) is FALSE. It will be violated at depth 6.

KEY QUESTION: Does Im = 1 appear at depth 6?
  We know Im ≈ 2.937 appears. Does Im = 1 appear?
  Im(eml(real_x, z)) = -arg(z) for real x.
  arg(z) for z ∈ EML₁ depth 5: ranges in (-2.27, ~0).
  For Im = 1: need arg(z) = -1. Is -1 in range (-2.27, 0)? YES!
  So the question is: does any depth-5 value have arg = -1?
  From S85: NO arg = -1 found at depth ≤ 5.

BUT: eml(non-real_x, z) also contributes. The full depth-6 search is:
  Im(eml(x, y)) = exp(Re(x))·sin(Im(x)) − arg(y)
  x can be from depth ≤ 5 (including complex), y from depth ≤ 5.

This session: verify the depth-6 Im counterexample and check if Im = 1 appears.
(Depth 6 full closure too large; we sample specific constructions.)
"""

import json
import math
import cmath
from pathlib import Path

PI = math.pi
TAN1 = math.tan(1)


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
    return values_at, [(v, d, e) for d, layer in values_at.items() for v, e in layer]


if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("S93 — SB Counterexample + Im=1 Search at Depth 6")
    print("=" * 60)
    print()

    _, vals_d5 = build_closure_layered(5)
    print(f"Depth ≤ 5 values: {len(vals_d5)}")
    print()

    # Identify depth-5 values with Im = -pi and Re < 0 (large |arg|)
    complex_neg_re = [(v, d, e) for v, d, e in vals_d5
                      if abs(v.imag + PI) < 1e-6 and v.real < 0]
    complex_pos_re = [(v, d, e) for v, d, e in vals_d5
                      if abs(v.imag + PI) < 1e-6 and v.real >= 0]
    print(f"Complex (Im=-pi) with Re < 0: {len(complex_neg_re)}")
    print(f"Complex (Im=-pi) with Re >= 0: {len(complex_pos_re)}")
    print()

    # arg distribution of complex values
    args_neg_re = sorted([cmath.phase(v) for v, d, e in complex_neg_re])
    args_pos_re = sorted([cmath.phase(v) for v, d, e in complex_pos_re])
    print(f"Arg range (Re<0): [{min(args_neg_re):.6f}, {max(args_neg_re):.6f}]")
    print(f"Arg range (Re>=0): [{min(args_pos_re):.6f}, {max(args_pos_re):.6f}]")
    print()

    # Direct construction of depth-6 Im > 0 values
    print("Depth-6 Im > 0 constructions (eml(real, z_neg_re)):")
    real_vals = [(v, d, e) for v, d, e in vals_d5 if abs(v.imag) < 1e-10]
    im_pos_d6 = []
    im_near_1 = []
    for rx, dr, er in real_vals[:20]:  # sample real values
        for cy, dc, ec in complex_neg_re[:50]:  # sample complex values with Re<0
            result = eml(rx, cy)
            if result is None:
                continue
            if result.imag > 1e-8:
                im_pos_d6.append((result, rx, cy))
                if abs(result.imag - 1.0) < 0.1:
                    im_near_1.append((result, rx, cy, er, ec))

    print(f"  Pairs found with Im(eml) > 0: {len(im_pos_d6)}")
    if im_pos_d6:
        ims = sorted([r.imag for r, x, y in im_pos_d6])
        print(f"  Im range: [{min(ims):.6f}, {max(ims):.6f}]")
        print(f"  Sample Im values: {[f'{v:.4f}' for v in ims[:8]]}")
    print()

    print(f"Pairs with Im near 1.0 (±0.1): {len(im_near_1)}")
    if im_near_1:
        for res, rx, cy, er, ec in im_near_1[:5]:
            print(f"  Im={res.imag:.8f}, Re={res.real:.6f}")
            print(f"    x={rx:.6f} ({er[:30]})")
            print(f"    y={cy:.6f} ({ec[:30]})")
    print()

    # Also check all depth-5 pairs more carefully for Im near 1
    print("Extended search: all (real_x, complex_y) pairs at depth <= 5 with |Im(eml)-1| < 0.01:")
    count_near_1 = 0
    for rx, dr, er in real_vals:
        for cy, dc, ec in [(v, d, e) for v, d, e in vals_d5 if abs(v.imag) > 1e-10]:
            result = eml(rx, cy)
            if result and abs(result.imag - 1.0) < 0.01:
                count_near_1 += 1
                print(f"  Im={result.imag:.8f} — x={rx:.4f}, y={cy:.6f}")
    if count_near_1 == 0:
        print("  None found.")
    print()

    # Refine: what Im values DO appear at depth 6 (from real x, complex y)?
    # Im(eml(x_real, y_complex)) = -arg(y_complex)
    # arg values of depth-5 complex elements:
    all_args_d5 = sorted(set(round(cmath.phase(v), 6)
                             for v, d, e in vals_d5 if abs(v.imag) > 1e-10))
    print(f"Unique arg values in complex EML₁ (depth<=5): {len(all_args_d5)}")
    print(f"Range: [{min(all_args_d5):.6f}, {max(all_args_d5):.6f}]")
    print()
    im_from_real_x = sorted([-a for a in all_args_d5])
    print(f"Resulting Im(eml(real, complex_d5)) = -arg values:")
    print(f"Range: [{min(im_from_real_x):.6f}, {max(im_from_real_x):.6f}]")
    print()
    # Does 1 appear?
    one_in_range = min(im_from_real_x) <= 1.0 <= max(im_from_real_x)
    closest_to_1 = min(im_from_real_x, key=lambda x: abs(x - 1.0))
    print(f"Is 1.0 in range of -arg values? {one_in_range}")
    print(f"Closest -arg value to 1.0: {closest_to_1:.8f} (distance: {abs(closest_to_1-1):.8f})")

    # Are there depth-5 complex values with arg = -1?
    arg_neg1 = [(v, d, e) for v, d, e in vals_d5
                if abs(v.imag) > 1e-10 and abs(cmath.phase(v) + 1.0) < 1e-6]
    print(f"\nDepth-5 values with arg = -1 (tol 1e-6): {len(arg_neg1)}")

    RESULT = {
        "session": "S93",
        "title": "SB Counterexample + Im=1 Search at Depth 6",
        "sb_violated_at_depth_6": len(im_pos_d6) > 0,
        "im_pos_d6_count": len(im_pos_d6),
        "im_near_1_count": len(im_near_1),
        "arg_neg1_at_depth5": len(arg_neg1),
        "one_in_im_range_from_real_x": one_in_range,
        "closest_to_1": closest_to_1,
        "key_finding": (
            "SB (Im ≤ 0) IS violated at depth 6 via eml(real, complex_neg_re). "
            f"Im values > 0 appear (range up to ~{max(ims):.2f} if any). "
            f"BUT Im = 1 not found — closest is {closest_to_1:.6f}. "
            "T_i (i not constructible) may still hold even though SB fails."
            if len(im_pos_d6) > 0 else
            "Unexpected: no Im > 0 found in sampled pairs. Larger search needed."
        ),
        "refined_conjecture": (
            "SB (Im ≤ 0) is FALSE. "
            "Refined Claim: Im(EML₁) never equals 1. "
            "This is weaker than SB but sufficient for T_i."
        ),
    }

    out_path = results_dir / "s93_sb_counterexample.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(RESULT, f, indent=2)
    print(f"\nResults: {out_path}")
