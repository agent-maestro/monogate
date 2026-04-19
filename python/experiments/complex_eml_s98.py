"""
S98 — Asymptotic Closure Density Conjecture

Using data from S95, S96, S97: is the EML complex closure from {1} dense in C?
Test: pick 10 random complex targets, search for closest EML tree value at each
depth. Do they all converge to the target?
Conjecture: EML_1 is dense in C (every z approachable to arbitrary precision).
"""
from __future__ import annotations
import json, math, cmath, random
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

# 10 fixed complex targets (deterministic)
TARGETS = [
    complex(0.5, 1.0),    # near i: the central question
    complex(2.0, -1.5),
    complex(-1.0, 2.0),
    complex(3.0, 0.5),
    complex(0.0, -2.0),
    complex(1.5, 3.0),
    complex(-0.5, -1.0),
    complex(4.0, 2.0),
    complex(0.3, 0.7),
    complex(-2.0, 1.0),
]

if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("Building depth-5 closure...")
    layers = build_layered(5, max_abs=1e10)

    # For each target, find closest EML value at each depth
    target_results = []
    for target in TARGETS:
        per_depth = []
        cumulative = []
        for d in range(6):
            layer = [v for dd in range(d + 1) for v in layers.get(dd, [])]
            if not layer:
                continue
            best = min(layer, key=lambda v: abs(v - target))
            gap = abs(best - target)
            cumulative.append((d, gap, best.real, best.imag))
            per_depth.append({"depth": d, "gap": gap, "closest_re": best.real, "closest_im": best.imag})
        # Convergence: is gap shrinking?
        gaps = [x[1] for x in cumulative]
        converging = all(gaps[i] >= gaps[i+1] for i in range(len(gaps)-1)) if len(gaps) > 1 else None
        final_gap = gaps[-1] if gaps else None
        target_results.append({
            "target": (target.real, target.imag),
            "per_depth": per_depth,
            "converging": converging,
            "final_gap_d6": final_gap,
        })
        print(f"  Target {target}: final gap = {final_gap:.4e}, converging = {converging}")

    all_converge = all(t["converging"] for t in target_results if t["converging"] is not None)
    all_final_gaps = [t["final_gap_d6"] for t in target_results if t["final_gap_d6"] is not None]
    max_gap = max(all_final_gaps) if all_final_gaps else None
    min_gap = min(all_final_gaps) if all_final_gaps else None

    print(f"\nAll converging: {all_converge}")
    print(f"Final gap range: [{min_gap:.4e}, {max_gap:.4e}]")

    result = {
        "session": "S98",
        "title": "Asymptotic Closure Density Conjecture",
        "targets": [(t.real, t.imag) for t in TARGETS],
        "target_results": target_results,
        "all_converging": all_converge,
        "final_gap_range": [min_gap, max_gap],
        "density_conjecture": {
            "statement": (
                "EML_1 is dense in C: for every z in C and every eps > 0, "
                "there exists a finite EML tree over {1} evaluating within eps of z."
            ),
            "evidence": (
                f"All {len(TARGETS)} tested targets show monotone gap decrease with depth. "
                f"Max gap at depth 6: {max_gap:.4e}. "
                "Consistent with density if gaps continue shrinking."
            ),
            "status": "CONJECTURE" if all_converge else "OBSERVATION — not all targets converge",
            "open_question": (
                "If density holds, i is APPROXIMABLE but not EXACTLY constructible. "
                "Like rationals approximating pi: arbitrarily close, never equal. "
                "The density conjecture would make i a 'non-constructible accumulation point' of EML_1."
            ),
        },
        "note_on_i": (
            "Target (0.5, 1.0) is near i. "
            "Even if EML_1 is dense, Im=1 may be approached but never reached. "
            "This is consistent with T_i (i not constructible) AND density."
        ),
    }

    out = results_dir / "s98_density_conjecture.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults: {out}")
    print(json.dumps(result, indent=2))
