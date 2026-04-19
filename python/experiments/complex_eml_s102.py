"""
S102 — The EML Closure Monoid: Growth Rate

EML_1 is a magma (closed under eml, not necessarily associative).
Study growth rate of |EML_d({1})| as a function of depth d.
Is it exponential? Doubly exponential?
Growth rate connects to how fast closure approaches density.
"""
from __future__ import annotations
import json, math, cmath
from pathlib import Path

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

def build_layered_counted(max_depth: int, max_abs: float = 1e10):
    values_at: dict[int, list[complex]] = {0: [complex(1.0)]}
    seen: set = {round_c(complex(1.0))}
    cumulative = [1]
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
        cumulative.append(cumulative[-1] + len(new_layer))
    return values_at, cumulative

if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("Building depth-5 closure with growth tracking...")
    layers, cumulative = build_layered_counted(5, max_abs=1e10)

    layer_sizes = []
    for d in range(6):
        layer = layers.get(d, [])
        real_count = sum(1 for v in layer if abs(v.imag) < 1e-9)
        complex_count = sum(1 for v in layer if abs(v.imag) >= 1e-9)
        layer_sizes.append({
            "depth": d,
            "new_in_layer": len(layer),
            "real": real_count,
            "complex": complex_count,
            "cumulative_total": cumulative[d] if d < len(cumulative) else None,
        })
        print(f"  Depth {d}: +{len(layer)} new, cumulative = {cumulative[d] if d < len(cumulative) else '?'}")

    # Growth rate analysis
    totals = [x["cumulative_total"] for x in layer_sizes if x["cumulative_total"] is not None]
    growth_ratios = []
    for i in range(1, len(totals)):
        if totals[i-1] > 0:
            growth_ratios.append(totals[i] / totals[i-1])

    # Log-log fit: if log(N(d)) ~ alpha * d, growth is exponential base exp(alpha)
    import math as _math
    log_totals = [_math.log(t) for t in totals if t > 0]
    depths = list(range(len(log_totals)))
    # Linear fit log(N) = a*d + b
    n = len(depths)
    mean_d = sum(depths) / n
    mean_l = sum(log_totals) / n
    ss_dx = sum((d - mean_d)**2 for d in depths)
    ss_dl = sum((d - mean_d) * (l - mean_l) for d, l in zip(depths, log_totals))
    slope = ss_dl / ss_dx if ss_dx > 0 else 0
    intercept = mean_l - slope * mean_d
    r_squared = (ss_dl ** 2) / (ss_dx * sum((l - mean_l)**2 for l in log_totals)) if ss_dx > 0 else 0

    print(f"\nGrowth ratios N(d)/N(d-1): {[f'{r:.3f}' for r in growth_ratios]}")
    print(f"Log-linear fit: log(N) = {slope:.4f}*d + {intercept:.4f}, R^2 = {r_squared:.4f}")
    print(f"Implied exponential base: {_math.exp(slope):.4f}")

    # Is growth doubly exponential? Check if log(log(N)) ~ linear
    log_log_totals = [_math.log(l) for l in log_totals[1:] if l > 0]
    dl_depths = depths[1:len(log_log_totals)+1]
    if len(dl_depths) > 2:
        mean_d2 = sum(dl_depths) / len(dl_depths)
        mean_ll = sum(log_log_totals) / len(log_log_totals)
        ss2 = sum((d - mean_d2)**2 for d in dl_depths)
        ss_dl2 = sum((d - mean_d2) * (l - mean_ll) for d, l in zip(dl_depths, log_log_totals))
        slope2 = ss_dl2 / ss2 if ss2 > 0 else 0
        r2_sq = (ss_dl2**2) / (ss2 * sum((l - mean_ll)**2 for l in log_log_totals)) if ss2 > 0 else 0
        print(f"Log-log-linear fit: log(log(N)) ~ {slope2:.4f}*d, R^2 = {r2_sq:.4f}")
        doubly_exp = r2_sq > r_squared
    else:
        slope2, r2_sq, doubly_exp = 0, 0, False

    growth_model = "doubly_exponential" if doubly_exp else "exponential"

    # Algebraic structure note
    algebraic_structure = {
        "type": "magma",
        "operation": "eml(x,y) = exp(x) - Log(y)",
        "identity": None,
        "associativity": False,
        "commutativity": False,
        "note": (
            "EML_1 is a magma under eml: closed but neither associative nor commutative. "
            "It is finitely generated (from {1}). "
            "The growth rate of the generated magma is the key quantity."
        ),
    }

    result = {
        "session": "S102",
        "title": "EML Closure Monoid — Growth Rate",
        "layer_sizes": layer_sizes,
        "cumulative_totals": totals,
        "growth_ratios": growth_ratios,
        "growth_fit": {
            "log_linear_slope": slope,
            "log_linear_intercept": intercept,
            "r_squared": r_squared,
            "implied_exponential_base": math.exp(slope),
            "log_log_slope": slope2,
            "log_log_r_squared": r2_sq,
        },
        "growth_model": growth_model,
        "algebraic_structure": algebraic_structure,
        "connection_to_density": (
            f"Growth model: {growth_model}. "
            "If growth is exponential, the magma expands rapidly but not 'infinitely fast'. "
            "Density conjecture requires that new values increasingly fill gaps. "
            "An exponential growth count is consistent with density if values spread uniformly."
        ),
    }

    out = results_dir / "s102_closure_monoid.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults: {out}")
    print(json.dumps(result, indent=2))
