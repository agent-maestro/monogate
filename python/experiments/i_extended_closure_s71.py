"""
S71 — Extended Grammar Closure: What's in EML({1}, extended)?

Extended grammar: ln defined on ℂ \ {0} via principal branch.
Starting terminal: {1}.

Computes the actual set of reachable values at N=1..7.
Tracks: real values, negative reals (loophole precursors), complex values, Im/pi census.

KEY RESULTS from this computation:
  N=1: {e}
  N=2: {exp(e), e−1}
  N=3: {exp(exp(e)), exp(e−1), exp(e)−1, 0, e−ln(e−1)}
  N=4: first negative real — e − exp(e) ≈ −12.44 (from eml(1, exp(exp(e))))
         Wait: eml(1, exp(e)) = e - ln(exp(e)) = e - e = 0 (at N=3)
         eml(1, exp(exp(e))) = e - ln(exp(exp(e))) = e - exp(e) ≈ -12.44 (at N=4)
  N=5: first complex values (Im = −π, from ln of negative real)
"""

import cmath
import math
import json
from pathlib import Path
from fractions import Fraction


_CLAMP = 600.0


def eml_ext(x, y):
    """Extended grammar: ln(y) for all y != 0 via principal branch."""
    if y == 0:
        return None
    try:
        xc = complex(x)
        yc = complex(y)
        ex = cmath.exp(complex(min(xc.real, _CLAMP), xc.imag))
        ly = cmath.log(yc)
        result = ex - ly
        if not cmath.isfinite(result):
            return None
        return result
    except (ValueError, OverflowError, ZeroDivisionError):
        return None


def round_c(z, digits=6):
    """Round complex to detect equality."""
    if abs(z.imag) < 1e-9:
        return round(z.real, digits)
    return complex(round(z.real, digits), round(z.imag, digits))


def build_closure(max_n):
    """Build all reachable values at each N."""
    values_at_n = {0: [1.0]}
    all_vals_set = {round_c(complex(1.0))}

    for n in range(1, max_n + 1):
        new_raw = []
        for k in range(n):
            lefts = values_at_n.get(k, [])
            rights = values_at_n.get(n - 1 - k, [])
            for lv in lefts:
                for rv in rights:
                    result = eml_ext(lv, rv)
                    if result is None:
                        continue
                    rc = round_c(result)
                    if rc not in all_vals_set and abs(result) < 1e8:
                        all_vals_set.add(rc)
                        new_raw.append(result)
        values_at_n[n] = new_raw

    return values_at_n


def analyze_set(values_at_n, max_n):
    analysis = {}
    for n in range(max_n + 1):
        vals = values_at_n.get(n, [])
        real_pos = [v for v in vals if isinstance(v, float) and v > 0]
        real_neg = [v for v in vals if isinstance(v, float) and v < 0]
        real_zero = [v for v in vals if isinstance(v, float) and v == 0]
        complex_vals = [v for v in vals if isinstance(v, complex)]

        im_over_pi = []
        for v in complex_vals:
            ratio = v.imag / math.pi
            im_over_pi.append(round(ratio, 4))

        analysis[n] = {
            "count": len(vals),
            "real_pos": len(real_pos),
            "real_neg": len(real_neg),
            "real_zero": len(real_zero),
            "complex": len(complex_vals),
            "sample_real_pos": sorted(real_pos)[:5],
            "sample_real_neg": sorted(real_neg)[:5],
            "sample_complex": [str(round_c(v, 4)) for v in complex_vals[:5]],
            "im_over_pi_sample": im_over_pi[:10],
            "first_complex": len(complex_vals) > 0,
        }

    return analysis


if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    MAX_N = 7
    print(f"Building EML closure from {{1}} under extended grammar (N=1..{MAX_N})...")
    values_at_n = build_closure(MAX_N)
    analysis = analyze_set(values_at_n, MAX_N)

    # Find first N with complex values
    first_complex_n = None
    for n in range(MAX_N + 1):
        if analysis[n]["complex"] > 0:
            first_complex_n = n
            break

    # Check if i is in the set
    i_target = complex(0, 1)
    i_found = False
    for n in range(MAX_N + 1):
        for v in values_at_n.get(n, []):
            if abs(complex(v) - i_target) < 1e-4:
                i_found = True
                break

    # All unique Im/pi values across all N
    all_im_pi = set()
    for n in range(MAX_N + 1):
        for v in values_at_n.get(n, []):
            vc = complex(v)
            if abs(vc.imag) > 1e-8:
                ratio = round(vc.imag / math.pi, 4)
                all_im_pi.add(ratio)

    output = {
        "grammar": "extended (principal branch)",
        "terminal": "{1}",
        "max_n": MAX_N,
        "analysis_by_n": analysis,
        "first_complex_n": first_complex_n,
        "i_found": i_found,
        "all_im_over_pi_values": sorted(list(all_im_pi)),
        "total_values": sum(len(v) for v in values_at_n.values()),
    }

    out_path = results_dir / "s71_extended_closure.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("=" * 60)
    print("S71 — Extended Grammar Closure: EML({1}, extended)")
    print("=" * 60)
    print()
    for n in range(MAX_N + 1):
        a = analysis[n]
        flag = " ← FIRST COMPLEX" if n == first_complex_n else ""
        print(f"  N={n}: {a['count']:4d} new values  "
              f"[real+:{a['real_pos']} real-:{a['real_neg']} zero:{a['real_zero']} complex:{a['complex']}]{flag}")
        if a["sample_real_neg"]:
            print(f"       real negative: {[round(x, 4) for x in a['sample_real_neg'][:3]]}")
        if a["sample_complex"]:
            print(f"       complex: {a['sample_complex'][:3]}")
        if a["im_over_pi_sample"]:
            print(f"       Im/pi: {a['im_over_pi_sample'][:5]}")
    print()
    print(f"First complex appearance: N={first_complex_n}")
    print(f"i found (N<=7): {i_found}")
    print(f"All Im/pi values seen: {sorted(list(all_im_pi))[:15]}")
    print()
    print("KEY: Im/pi = -1 means Im = -pi (the loophole). Im/pi = 1/pi would mean Im = 1.")
    print(f"     1/pi = {1/math.pi:.6f} — NOT in set: {round(1/math.pi, 4) not in all_im_pi}")
    print()
    print(f"Total values computed: {output['total_values']}")
    print(f"Results: {out_path}")
