"""
S90 — Structural Bound Conjecture: Im(EML₁) ⊆ (−π, 0]

Formal statement, base case verification, and depth-by-depth census
of imaginary parts.

CONJECTURE SB (Structural Bound):
  For all z ∈ EML₁ = EML({1}, extended), Im(z) ≤ 0.
  More precisely: Im(z) ∈ {0} ∪ (−π, 0) for all z ∈ EML₁.

  If SB holds: Im(z) = 1 > 0 is immediately impossible, so i ∉ EML₁.
  Combined with T19: T_i follows from SB alone, without Schanuel.

WHY SB MIGHT HOLD:
  Propagation: Im(eml(x,y)) = exp(Re(x))·sin(Im(x)) − arg(y)
  Base: Im(1) = 0.
  If Im(x) ≤ 0 and Im(y) ≤ 0 (and hence arg(y) ≤ 0):
    - sin(Im(x)): for Im(x) ∈ (−π, 0), sin(Im(x)) ∈ (−1, 0). So exp(Re(x))·sin(Im(x)) < 0.
    - −arg(y): arg(y) ≤ 0 so −arg(y) ≥ 0.
    - Im(eml) = negative + non-negative. SIGN AMBIGUOUS.

  BUT: if Im(y) < 0 and Re(y) > 0, then arg(y) = arctan(Im(y)/Re(y)) ∈ (−π/2, 0).
  So −arg(y) ∈ (0, π/2).
  And exp(Re(x))·sin(Im(x)) ∈ (−exp(Re(x)), 0).
  For Im(eml) ≤ 0: need exp(Re(x))·sin(Im(x)) ≤ arg(y) ≤ 0.
  This requires sin(Im(x)) ≤ 0 (already true) and |exp(Re(x))·sin(Im(x))| ≥ |arg(y)|.

  Not obviously true! The bound could fail if |arg(y)| is large relative to exp(Re(x))|sin(Im(x))|.

COMPUTATIONAL VERIFICATION:
  This session: compute Im(z) for all z ∈ EML₁ at depth ≤ 6,
  verify Im ≤ 0 for all, record the maximum Im observed.
"""

import json
import math
import cmath
from pathlib import Path

TAN1 = math.tan(1)
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

    all_vals = [(v, d, e) for d, layer in values_at.items() for v, e in layer]
    return all_vals


if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("S90 — Structural Bound: Im(EML₁) ⊆ (−π, 0]?")
    print("=" * 60)
    print()

    MAX_DEPTH = 5
    print(f"Computing EML₁ closure to depth {MAX_DEPTH}...")
    vals = build_closure_layered(MAX_DEPTH)
    print(f"Total values: {len(vals)}")
    print()

    # Analyze Im parts
    im_pos = [(v, d, e) for v, d, e in vals if v.imag > 1e-10]
    im_neg = [(v, d, e) for v, d, e in vals if v.imag < -1e-10]
    im_zero = [(v, d, e) for v, d, e in vals if abs(v.imag) <= 1e-10]

    max_im = max((v.imag for v, d, e in vals), default=0.0)
    min_im = min((v.imag for v, d, e in vals), default=0.0)

    print(f"Im = 0:   {len(im_zero)} values")
    print(f"Im < 0:   {len(im_neg)} values")
    print(f"Im > 0:   {len(im_pos)} values")
    print()
    print(f"Max Im observed: {max_im:.10f}")
    print(f"Min Im observed: {min_im:.10f}")
    print(f"Min Im / pi:     {min_im / PI:.10f}")
    print()

    sb_holds = len(im_pos) == 0
    print(f"Structural Bound Im <= 0 holds at depth <= {MAX_DEPTH}: {sb_holds}")
    print()

    if im_pos:
        print("VIOLATION FOUND! First few positive-Im values:")
        for v, d, e in im_pos[:5]:
            print(f"  depth {d}: Im={v.imag:.10f}, Re={v.real:.6f}, {e[:50]}")
    else:
        print("All Im parts are <= 0 at depth <=", MAX_DEPTH)
        print(f"Minimum Im: {min_im:.10f}  (ratio to -pi: {min_im / (-PI):.6f})")

    # Depth-by-depth Im stats
    print()
    print("Depth | total | Im<0 | Im=0 | max_Im  | min_Im")
    for d in range(MAX_DEPTH + 1):
        layer = [(v, d_, e) for v, d_, e in vals if d_ == d]
        n_neg = sum(1 for v, _, _ in layer if v.imag < -1e-10)
        n_zero = sum(1 for v, _, _ in layer if abs(v.imag) <= 1e-10)
        n_pos = sum(1 for v, _, _ in layer if v.imag > 1e-10)
        mx = max((v.imag for v, _, _ in layer), default=0.0)
        mn = min((v.imag for v, _, _ in layer), default=0.0)
        print(f"  {d}   | {len(layer):5d} | {n_neg:4d} | {n_zero:4d} | {mx:8.5f} | {mn:8.5f}")

    RESULT = {
        "session": "S90",
        "title": "Structural Bound Im(EML₁) ⊆ (-pi, 0] — Conjecture",
        "conjecture": "SB: For all z in EML_1, Im(z) <= 0",
        "max_depth_checked": MAX_DEPTH,
        "total_values": len(vals),
        "im_positive_count": len(im_pos),
        "im_negative_count": len(im_neg),
        "im_zero_count": len(im_zero),
        "max_im_observed": max_im,
        "min_im_observed": min_im,
        "sb_holds_at_depth": MAX_DEPTH if sb_holds else None,
        "sb_violated": not sb_holds,
        "conclusion": (
            f"SB holds at depth <= {MAX_DEPTH}. "
            "All Im parts are 0 or negative. "
            "If SB holds for all depths, T_i follows without Schanuel."
            if sb_holds else
            "SB VIOLATED! Positive Im found. T_i cannot be proved via this route."
        ),
    }

    out_path = results_dir / "s90_structural_bound.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(RESULT, f, indent=2)
    print(f"\nResults: {out_path}")
