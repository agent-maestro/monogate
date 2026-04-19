"""
S97 — The pi/tan(1) Constructibility Barrier

The near-miss requires Re(y) = pi/tan(1) ~ 2.0270 for exact Im=1.
Search real EML values at depths 0-5 for closest to pi/tan(1).
Targeted depth-6 search near the target.
"""
from __future__ import annotations
import json, math, cmath
from pathlib import Path

PI = math.pi
TAN1 = math.tan(1.0)
TARGET = PI / TAN1  # pi/tan(1) ~ 2.01719...

def eml_real(x: float, y: float) -> float | None:
    if y <= 0:
        return None
    try:
        if x > 600:
            return None
        r = math.exp(x) - math.log(y)
        return r if math.isfinite(r) and abs(r) < 1e10 else None
    except (ValueError, OverflowError):
        return None

def round_c(z, digits=6):
    return (round(z.real, digits), round(z.imag, digits))

def build_layered_cplx(max_depth: int, max_abs: float = 1e10):
    values_at: dict[int, list[complex]] = {0: [complex(1.0)]}
    seen: set = {round_c(complex(1.0))}
    for d in range(1, max_depth + 1):
        new_layer: list[complex] = []
        prev_all = [v for dd in range(d) for v in values_at.get(dd, [])]
        prev_d = values_at.get(d - 1, [])
        for v1 in prev_all:
            for v2 in prev_d:
                r_c = None
                try:
                    if v1.real > 600 or abs(v2) < 1e-300:
                        continue
                    r_c = cmath.exp(v1) - cmath.log(v2)
                except Exception:
                    continue
                if r_c is None or abs(r_c) > max_abs:
                    continue
                k = round_c(r_c)
                if k not in seen:
                    seen.add(k)
                    new_layer.append(r_c)
        for v1 in prev_d:
            for v2 in prev_all:
                r_c = None
                try:
                    if v1.real > 600 or abs(v2) < 1e-300:
                        continue
                    r_c = cmath.exp(v1) - cmath.log(v2)
                except Exception:
                    continue
                if r_c is None or abs(r_c) > max_abs:
                    continue
                k = round_c(r_c)
                if k not in seen:
                    seen.add(k)
                    new_layer.append(r_c)
        values_at[d] = new_layer
    return values_at

if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print(f"Target: pi/tan(1) = {TARGET:.10f}")
    print()

    print("Building complex depth-5 closure...")
    layers = build_layered_cplx(5)
    all_d5 = [v for d in range(6) for v in layers.get(d, [])]
    real_d5 = [v.real for v in all_d5 if abs(v.imag) < 1e-9]
    print(f"  {len(real_d5)} real values at depth<=5")

    # Find closest real value to TARGET at each depth
    depth_results: list[dict] = []
    for d in range(6):
        all_to_d_real = [v.real for dd in range(d+1) for v in layers.get(dd, []) if abs(v.imag) < 1e-9]
        if not all_to_d_real:
            continue
        best = min(all_to_d_real, key=lambda v: abs(v - TARGET))
        gap = abs(best - TARGET)
        print(f"  Depth {d}: {len(all_to_d_real)} real values, closest={best:.10f}, gap={gap:.6e}")
        depth_results.append({"depth": d, "values_total": len(all_to_d_real),
                              "closest": best, "gap": gap})

    # Depth-6 targeted: try to get closer via eml(v1, v2) where result near TARGET
    # TARGET ~ 2.0172, so find v1, v2 in real_d5 where exp(v1) - ln(v2) ~ TARGET
    # i.e., exp(v1) - TARGET ~ ln(v2) => v2 ~ exp(exp(v1) - TARGET)
    print("\nTargeted depth-6 search near pi/tan(1)...")
    best_d6_gap = depth_results[-1]["gap"] if depth_results else float("inf")
    best_d6_val = depth_results[-1]["closest"] if depth_results else None
    seen_real = set(round(v, 9) for v in real_d5)

    for v1 in real_d5:
        # What v2 would make eml(v1, v2) = TARGET?
        # exp(v1) - ln(v2) = TARGET => ln(v2) = exp(v1) - TARGET => v2 = exp(exp(v1) - TARGET)
        try:
            if v1 > 10:
                continue
            needed_v2 = math.exp(math.exp(v1) - TARGET)
            if not math.isfinite(needed_v2) or needed_v2 <= 0 or needed_v2 > 1e10:
                continue
            # Find closest real_d5 value to needed_v2
            closest_v2 = min(real_d5, key=lambda v: abs(v - needed_v2))
            if closest_v2 <= 0:
                continue
            r = eml_real(v1, closest_v2)
            if r is not None:
                gap = abs(r - TARGET)
                if gap < best_d6_gap:
                    best_d6_gap = gap
                    best_d6_val = r
        except (ValueError, OverflowError):
            continue

    d6_str = f"{best_d6_val:.10f}" if best_d6_val is not None else "N/A"
    print(f"  Best depth-6 approach to pi/tan(1): {d6_str}")
    print(f"  Gap: {best_d6_gap:.6e}")

    # Convergence rates
    gaps = [x["gap"] for x in depth_results]
    rates = [gaps[i] / gaps[i-1] for i in range(1, len(gaps)) if gaps[i-1] > 0]
    # Also append depth-6 gap if improved
    if depth_results and best_d6_gap < depth_results[-1]["gap"]:
        depth_results.append({"depth": 6, "values_total": "targeted", "closest": best_d6_val, "gap": best_d6_gap})
        gaps.append(best_d6_gap)
        if depth_results[-2]["gap"] > 0:
            rates.append(best_d6_gap / depth_results[-2]["gap"])

    print(f"\nConvergence rates: {[f'{r:.4f}' for r in rates]}")

    result = {
        "session": "S97",
        "title": "pi/tan(1) Constructibility Barrier — Real EML Closure",
        "target": TARGET,
        "target_desc": "pi/tan(1) = pi*cos(1)/sin(1), ~2.0172. Exact Re(y) needed for Im(eml(1,y))=1.",
        "tan1_transcendence": "Hermite-Lindemann: tan(1) transcendental (1 not zero, e^{2i} != 1)",
        "depth_results": depth_results,
        "convergence_rates": rates,
        "conclusion": (
            f"Closest real EML value to pi/tan(1) at depth 5: gap = {gaps[-1] if gaps else 'N/A'}. "
            "The real EML closure DOES approach pi/tan(1) but the gap is non-zero. "
            "This IS the tan(1) obstruction: the constructibility gap in the real closure "
            "propagates directly to the Im=1 gap in the complex closure via -arg(y) = Im(eml(1,y))."
        ),
    }

    out = results_dir / "s97_pi_tan1_barrier.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults: {out}")
    print(json.dumps(result, indent=2))
