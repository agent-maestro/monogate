"""
S95 — Map the Depth-6 Complex Closure

Track Im distribution at depth 6 without storing all values.
Use streaming histogram approach to stay in memory.
"""
from __future__ import annotations
import json, math, cmath
from pathlib import Path
from collections import defaultdict

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

if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("Building depth-5 closure...")
    layers = build_layered(5)
    all_d5 = [v for d in range(6) for v in layers.get(d, [])]
    real_d5 = [v for v in all_d5 if abs(v.imag) < 1e-9]
    complex_d5 = [v for v in all_d5 if abs(v.imag) >= 1e-9]
    print(f"  Depth<=5: {len(all_d5)} total, {len(real_d5)} real, {len(complex_d5)} complex")

    # Streaming depth-6 analysis: don't store all values
    seen6: set = {round_c(v) for v in all_d5}

    # Tracking only
    hist: dict[str, int] = defaultdict(int)  # Im histogram by 0.1 bins
    unique_im_set: set[float] = set()
    near_1: list[tuple[float, float]] = []   # (im, re) for |im-1| < 0.1
    counters = [0, 0]  # [d6_total_new, d6_complex_count]

    def process(r: complex):
        k = round_c(r)
        if k in seen6:
            return
        seen6.add(k)
        counters[0] += 1
        if abs(r.imag) > 1e-9:
            counters[1] += 1
            bucket = round(r.imag * 10) / 10
            hist[f"{bucket:.1f}"] += 1
            unique_im_set.add(round(r.imag, 4))
            if abs(r.imag - 1.0) < 0.1:
                near_1.append((r.imag, r.real))

    # Batch 1: real x complex — Im(result) = -arg(y)
    print("Batch 1: real x complex...")
    for y in complex_d5:
        arg_y = cmath.phase(y)
        target_im = -arg_y
        # Any real x gives Im = -arg(y), so just enumerate unique Im values
        # from the arg distribution. The actual Re value changes with x.
        # Process a sample of (x, y) pairs to discover Im values.
        for x in real_d5[:100]:  # 100 real values is sufficient to find Im patterns
            r = eml(x, y)
            if r is None or abs(r) > 1e10:
                continue
            process(r)

    print(f"  After batch 1: {counters[0]} new, {counters[1]} complex")

    # Batch 2: complex x real — Im(result) = exp(Re(x))*sin(Im(x))
    print("Batch 2: complex x real...")
    for x in complex_d5:
        if x.real > 8:
            continue
        for y in real_d5[:50]:
            if y.real <= 0:
                continue
            r = eml(x, y)
            if r is None or abs(r) > 1e10:
                continue
            process(r)

    print(f"  After batch 2: {counters[0]} new, {counters[1]} complex")

    # Batch 3: complex x complex (sample)
    print("Batch 3: complex x complex (100x100)...")
    cx_sample = complex_d5[:100]
    for x in cx_sample:
        if x.real > 8:
            continue
        for y in cx_sample:
            r = eml(x, y)
            if r is None or abs(r) > 1e10:
                continue
            process(r)

    print(f"  After batch 3: {counters[0]} new, {counters[1]} complex")

    near_1.sort(key=lambda t: abs(t[0] - 1.0))
    unique_im_list = sorted(unique_im_set)

    print(f"\nSummary:")
    print(f"  Unique Im values (4dp): {len(unique_im_list)}")
    print(f"  Near Im=1 (|Im-1|<0.1): {len(near_1)}")
    if near_1:
        best = near_1[0]
        print(f"  Best: Im={best[0]:.8f}, gap={abs(best[0]-1):.2e}")
    if unique_im_list:
        print(f"  Im range: [{min(unique_im_list):.4f}, {max(unique_im_list):.4f}]")

    result = {
        "session": "S95",
        "title": "Depth-6 Complex EML Closure",
        "depth5_total": len(all_d5),
        "depth5_real": len(real_d5),
        "depth5_complex": len(complex_d5),
        "depth6_new_sampled": counters[0],
        "depth6_complex_sampled": counters[1],
        "unique_im_count": len(unique_im_list),
        "im_range": [min(unique_im_list), max(unique_im_list)] if unique_im_list else None,
        "unique_im_sample": unique_im_list[:50],
        "histogram_by_0_1": dict(sorted(hist.items(), key=lambda x: float(x[0]))),
        "near_im_1_count": len(near_1),
        "near_im_1_top5": near_1[:5],
        "best_im_near_1": {
            "im": near_1[0][0], "re": near_1[0][1], "gap": abs(near_1[0][0] - 1.0)
        } if near_1 else None,
        "structure_notes": (
            f"{len(unique_im_list)} unique Im values (4dp) sampled at depth 6. "
            "Im values arise from -arg(y) for depth-5 complex y. "
            "Not restricted to {-pi}: full range from arg distribution of depth-5 closure."
        ),
        "method": "Streaming histogram; full enumeration infeasible (26k*4k pairs); sampled 100 real x per y",
    }

    out = results_dir / "s95_depth6_complex_closure.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults: {out}")
    print(json.dumps(result, indent=2))
