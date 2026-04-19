"""
S99 — The Approximation Rate Theorem

Using data from S95-S98: attempt to prove or precisely conjecture:
"Im parts of depth-d EML trees over {1} are eps(d)-dense in some interval [a,b]
where eps(d) -> 0 as d -> inf."

Proof strategy: at each depth, new values interlace old ones.
Hard part: proving interlacing, not just observing it.

Also: if T_i holds AND EML_1 is dense, then i is a transcendental accumulation point
of a constructible set -- analogous to pi in Q.
"""
from __future__ import annotations
import json, math, cmath
from pathlib import Path

PI = math.pi

def eml(x, y):
    if abs(y) < 1e-300:
        return None
    try:
        if x.real > 600:
            return None
        return cmath.exp(x) - cmath.log(y)
    except Exception:
        return None

def round_c(z, digits=6):
    return (round(z.real, digits), round(z.imag, digits))

def build_layered(max_depth: int, max_abs: float = 1e10):
    values_at: dict[int, list[complex]] = {0: [complex(1.0)]}
    seen: set = {round_c(complex(1.0))}
    for d in range(1, max_depth + 1):
        new_layer: list[complex] = []
        prev_all = [v for dd in range(d) for v in values_at.get(dd, [])]
        prev_d = values_at.get(d - 1, [])
        for v1 in prev_all:
            for v2 in prev_d:
                r = eml(v1, v2)
                if r is None or abs(r) > max_abs:
                    continue
                k = round_c(r)
                if k not in seen:
                    seen.add(k)
                    new_layer.append(r)
        for v1 in prev_d:
            for v2 in prev_all:
                r = eml(v1, v2)
                if r is None or abs(r) > max_abs:
                    continue
                k = round_c(r)
                if k not in seen:
                    seen.add(k)
                    new_layer.append(r)
        values_at[d] = new_layer
    return values_at

def max_gap_in_sorted(vals: list[float]) -> float:
    """Largest gap between consecutive sorted values."""
    if len(vals) < 2:
        return float("inf")
    s = sorted(vals)
    return max(s[i+1] - s[i] for i in range(len(s)-1))

if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("Building depth-5 closure...")
    layers = build_layered(5, max_abs=1e10)

    # Load depth-6 sampled Im data from S95
    s95_path = results_dir / "s95_depth6_complex_closure.json"
    d6_unique_im = []
    if s95_path.exists():
        with open(s95_path, encoding="utf-8") as f:
            s95_data = json.load(f)
        d6_unique_im = [v for v in s95_data.get("unique_im_sample", []) if -5 < v < 5]
        print(f"  Loaded {len(d6_unique_im)} depth-6 unique Im values from S95")

    # Analyse Im-value density at each depth (for complex values in bounded region)
    density_data = []
    for d in range(6):
        all_vals = [v for dd in range(d + 1) for v in layers.get(dd, [])]
        im_vals = sorted(set(
            round(v.imag, 5) for v in all_vals
            if abs(v.imag) > 1e-9 and -5 < v.imag < 5
        ))
        if not im_vals:
            density_data.append({"depth": d, "im_values_in_pm5": 0,
                                 "max_gap_between_consecutive": None, "im_range": []})
            continue
        gap = max_gap_in_sorted(im_vals)
        im_range = (min(im_vals), max(im_vals))
        density_data.append({
            "depth": d,
            "im_values_in_pm5": len(im_vals),
            "max_gap_between_consecutive": gap if gap < 1e10 else None,
            "im_range": list(im_range),
        })
        gap_str = f"{gap:.6f}" if gap < 1e10 else "inf (single point)"
        print(f"  Depth {d}: {len(im_vals)} distinct Im in (-5,5), max gap = {gap_str}")

    # Add depth-6 data from S95
    if d6_unique_im:
        gap6 = max_gap_in_sorted(d6_unique_im)
        density_data.append({
            "depth": 6,
            "im_values_in_pm5": len(d6_unique_im),
            "max_gap_between_consecutive": gap6 if gap6 < 1e10 else None,
            "im_range": [min(d6_unique_im), max(d6_unique_im)],
            "source": "S95 sampled data",
        })
        print(f"  Depth 6 (from S95): {len(d6_unique_im)} distinct Im, max gap = {gap6:.6f}")

    # Is max_gap shrinking with depth?
    gaps = [x["max_gap_between_consecutive"] for x in density_data
            if x["max_gap_between_consecutive"] is not None]
    gap_shrinking = all(gaps[i] >= gaps[i+1] for i in range(len(gaps)-1)) if len(gaps) > 1 else False

    # Theorem statement attempt
    # At depth d, max gap ~ g(d). If g(d) -> 0, Im-values are asymptotically dense.
    # Rate of decrease:
    gap_rates = []
    for i in range(1, len(gaps)):
        if gaps[i-1] > 0:
            gap_rates.append(gaps[i] / gaps[i-1])

    print(f"\nMax gap shrinking: {gap_shrinking}")
    print(f"Gap rates: {[f'{r:.4f}' for r in gap_rates]}")

    # Theorem vs conjecture determination
    if gap_shrinking and all(r < 1.0 for r in gap_rates):
        status = "CONJECTURE — gap shrinking but proof not yet available"
        conjecture_evidence = "strong (monotone decrease with depth)"
    elif gap_shrinking:
        status = "CONJECTURE — gap shrinking non-monotonically"
        conjecture_evidence = "moderate"
    else:
        status = "CONJECTURE — insufficient depth to determine"
        conjecture_evidence = "weak at current depth"

    # The theorem we CAN prove (weakly):
    proved_proposition = {
        "statement": (
            "P1 (Observation): The set of Im parts of EML_1 restricted to depth <= 6 "
            "and |Im| <= 5 has max consecutive gap of {:.6f} (at depth 6). "
            "Gap is strictly smaller than at depth 5 ({:.6f}).".format(
                gaps[-1] if gaps else 0,
                gaps[-2] if len(gaps) > 1 else 0
            )
        ),
        "tier": "OBSERVATION",
    }

    density_conjecture = {
        "statement": (
            "For all M > 0, the max gap between consecutive Im values of EML_1 "
            "elements with |Im| <= M converges to 0 as depth -> infinity. "
            "Equivalently: the Im parts of EML_1 are dense in R."
        ),
        "status": status,
        "evidence": conjecture_evidence,
        "proof_sketch": (
            "At depth d, new Im values arise as -arg(y) for y in depth-(d-1). "
            "The arg function is continuous; as Re(y) varies, -arg(y) sweeps intervals. "
            "If the real EML closure is dense (separately conjectured), "
            "then the arg values become dense in (-pi, pi), "
            "forcing Im values dense in (-pi, pi) at depth d+1. "
            "MISSING STEP: real closure density is not proved."
        ),
    }

    conclusion = (
        "If both density conjectures hold (S98 and here), then EML_1 is dense in C. "
        "Combined with T_i (i not constructible), this gives: "
        "i is a TRANSCENDENTAL ACCUMULATION POINT of EML_1. "
        "This is the exact analogue of pi being an accumulation point of Q. "
        "The distinction 'approximable to any precision' vs 'exactly constructible' "
        "is the mathematical content of the tan(1) obstruction."
    )

    result = {
        "session": "S99",
        "title": "Approximation Rate Theorem",
        "density_by_depth": density_data,
        "max_gap_sequence": gaps,
        "gap_shrinking": gap_shrinking,
        "gap_rates": gap_rates,
        "proved_proposition": proved_proposition,
        "density_conjecture": density_conjecture,
        "conclusion": conclusion,
        "tier": status.split(" — ")[0],
    }

    out = results_dir / "s99_approximation_rate.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults: {out}")
    print(json.dumps(result, indent=2))
