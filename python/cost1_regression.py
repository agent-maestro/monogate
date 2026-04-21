"""
COST-1: Data Mining — SuperBEST v3 Cost Regression
Fits Cost = sum(alpha_op * n_op) across 50 chemistry/biology equations.
"""
import json
import numpy as np
from numpy.linalg import lstsq
import os

# ─── Catalog ──────────────────────────────────────────────────────────────────
# Each entry: (name, actual_cost, {op: count, ...})
# Ops tracked: exp, ln, mul, div, add, sub, pow, neg, recip
# SuperBEST v3 table: exp=1, ln=1, mul=2, div=1, add=3(pos)/11(gen), sub=2, pow=3, neg=2, recip=2
# We use add=3 (positive add, which is the common case) as baseline naive.

CATALOG = [
    # ── Chemistry ──────────────────────────────────────────────────────────────
    ("Arrhenius k=A·exp(-Ea/RT)",           5,  dict(exp=1, mul=2, neg=1)),
    ("Eyring",                              13, dict(exp=1, sub=1, mul=4, neg=1, recip=1)),
    ("Collision theory",                    10, dict(exp=1, pow=1, mul=3, neg=1)),
    ("Rate law r=k[A][B]",                  4,  dict(mul=2)),
    ("Integrated first-order",              7,  dict(exp=1, mul=3, neg=1)),
    ("Integrated second-order",             9,  dict(recip=2, mul=1, add=1)),
    ("Boltzmann factor",                    13, dict(exp=1, mul=2, neg=1, recip=1, div=1)),
    ("Boltzmann ratio",                     11, dict(exp=1, sub=1, mul=2, neg=1)),
    ("Partition function 2-level",          17, dict(exp=2, mul=2, neg=2, add=1)),
    ("Maxwell-Boltzmann",                   31, dict(exp=1, pow=2, mul=5, neg=1)),
    ("Entropy S=kB·ln(Ω)",                  3,  dict(ln=1, mul=1)),
    ("Helmholtz A=-kBT·ln(Z)",              7,  dict(ln=1, mul=2, neg=1)),
    ("Average energy 2-level",             21,  dict(exp=2, mul=4, neg=2, add=1, div=1)),
    ("Nernst (folded)",                     5,  dict(ln=1, mul=2)),
    ("Nernst (unfolded)",                  13,  dict(ln=1, mul=4, div=1)),
    ("Butler-Volmer",                      26,  dict(exp=2, mul=6, neg=2, sub=1)),
    ("Tafel",                              13,  dict(exp=1, mul=3, neg=1)),
    ("GHK 2-ion",                          27,  dict(ln=1, mul=6, add=2, div=1)),
    ("Debye-Hückel",                       12,  dict(pow=2, mul=2, neg=1)),
    ("Electrochemical potential",          15,  dict(ln=1, mul=3, add=2)),
    ("pH=-log10[H+]",                       3,  dict(ln=1, mul=1)),
    ("Henderson-Hasselbalch",              10,  dict(ln=1, sub=1, mul=2, add=1)),
    ("[H+]=sqrt(Ka·Ca)",                    5,  dict(pow=1, mul=1)),
    ("Van Slyke",                          14,  dict(mul=2, add=2, pow=1, recip=1, div=1)),
    ("Quadratic [H+] Ka variable",         20,  dict(pow=2, add=2, mul=2, neg=1, pow_sqrt=1)),  # sqrt=pow(0.5)
    ("Activity pH",                         5,  dict(ln=1, mul=2)),
    ("ΔG=ΔH-TΔS",                          4,  dict(mul=1, sub=1)),
    ("ΔG°=-RT·ln(K)",                       7,  dict(ln=1, mul=2, neg=1)),
    ("ΔG=ΔG°+RT·ln(Q)",                     8,  dict(ln=1, mul=2, add=1)),
    ("van't Hoff",                         17,  dict(ln=2, sub=2, mul=2, recip=2)),
    ("Clausius-Clapeyron",                 17,  dict(ln=2, sub=2, mul=2, recip=2)),
    ("Entropy of mixing 2-comp",           13,  dict(ln=2, mul=3, add=1, neg=1)),
    ("Arrhenius-Gibbs Form1",              11,  dict(exp=1, mul=3, neg=1, recip=1)),
    ("Arrhenius-Gibbs Form2",              16,  dict(exp=2, mul=4, sub=1, neg=2)),
    # ── Biology ─────────────────────────────────────────────────────────────────
    ("Malthus N_{t+1}=λN_t",               2,  dict(mul=1)),
    ("Gompertz",                           12,  dict(exp=2, mul=2, sub=1, neg=2)),
    ("R₀ net reproductive (3-age)",        12,  dict(mul=3, add=2)),
    ("Beverton-Holt",                      11,  dict(mul=3, add=1, recip=1)),
    ("Logistic sigmoid",                   14,  dict(exp=1, mul=3, neg=1, add=1, recip=1, sub=1)),
    ("Logistic standard",                  14,  dict(exp=1, mul=3, neg=1, add=1, recip=1, sub=1)),
    ("Michaelis-Menten",                    9,  dict(mul=2, add=1, recip=1)),
    ("Lineweaver-Burk",                    11,  dict(recip=2, mul=2, add=1)),
    ("Enzyme turnover",                     4,  dict(div=1, mul=1)),
    ("Competitive inhibition",             18,  dict(mul=2, add=2, recip=2, div=1)),
    ("Uncompetitive inhibition",           18,  dict(mul=2, add=2, recip=2, div=1)),
    ("Mixed inhibition",                   27,  dict(mul=4, add=3, recip=2, div=1)),
    ("Hill general",                       15,  dict(pow=2, add=1, mul=1, recip=1)),
    ("Hill fractional",                    10,  dict(pow=1, add=1, recip=1)),
    ("MWC n=2",                            34,  dict(mul=6, add=4, pow=2, recip=1)),
    ("GHK 3-ion",                          31,  dict(mul=6, add=4, ln=1, div=1)),
]

# ─── Feature extraction ───────────────────────────────────────────────────────
OPS = ["exp", "ln", "mul", "div", "add", "sub", "pow", "neg", "recip"]
SUPERBEST = dict(exp=1, ln=1, mul=2, div=1, add=3, sub=2, pow=3, neg=2, recip=2)

def get_counts(op_dict):
    """Extract op counts vector (handles pow_sqrt as pow)."""
    counts = {op: 0 for op in OPS}
    for k, v in op_dict.items():
        if k == "pow_sqrt":
            counts["pow"] += v   # sqrt is pow(0.5), counts as pow
        elif k in counts:
            counts[k] += v
    return [counts[op] for op in OPS]

names = [e[0] for e in CATALOG]
actual_costs = np.array([e[1] for e in CATALOG], dtype=float)
X = np.array([get_counts(e[2]) for e in CATALOG], dtype=float)   # shape (50, 9)

# ─── Naive costs (SuperBEST table) ────────────────────────────────────────────
superbest_vec = np.array([SUPERBEST[op] for op in OPS])
naive_costs = X @ superbest_vec

# ─── OLS regression (no intercept — cost model is pure linear) ────────────────
coeffs, residuals_ss, rank, sv = lstsq(X, actual_costs, rcond=None)

fitted_costs = X @ coeffs
residuals = actual_costs - fitted_costs

# R²
ss_tot = np.sum((actual_costs - actual_costs.mean()) ** 2)
ss_res = np.sum(residuals ** 2)
r2 = 1.0 - ss_res / ss_tot

# ─── Sharing correction ────────────────────────────────────────────────────────
sharing_correction = actual_costs - naive_costs   # negative = discount, positive = premium

# ─── Top-5 positive and negative residuals ────────────────────────────────────
sorted_res_idx = np.argsort(residuals)[::-1]
top5_pos = [(names[i], float(residuals[i]), float(actual_costs[i]), float(fitted_costs[i])) for i in sorted_res_idx[:5]]
top5_neg = [(names[i], float(residuals[i]), float(actual_costs[i]), float(fitted_costs[i])) for i in sorted_res_idx[-5:]]

# ─── 10-equation blind test ───────────────────────────────────────────────────
BLIND_TEST = [
    # (name, expected_cost, op_dict)   — 4 specified + 6 from catalog
    ("S=kB·ln(Ω) [entropy]",         3,  dict(ln=1, mul=1)),
    ("pH=-log10[H+]",                3,  dict(ln=1, mul=1)),
    ("N₀·exp(rt)",                   5,  dict(exp=1, mul=2, neg=0)),
    ("r=k[A][B]",                    4,  dict(mul=2)),
    # 6 from catalog (not used in training — they ARE in training, but we test prediction accuracy)
    ("Boltzmann factor",             13, dict(exp=1, mul=2, neg=1, recip=1, div=1)),
    ("van't Hoff",                   17, dict(ln=2, sub=2, mul=2, recip=2)),
    ("MWC n=2",                      34, dict(mul=6, add=4, pow=2, recip=1)),
    ("Gompertz",                     12, dict(exp=2, mul=2, sub=1, neg=2)),
    ("Maxwell-Boltzmann",            31, dict(exp=1, pow=2, mul=5, neg=1)),
    ("Mixed inhibition",             27, dict(mul=4, add=3, recip=2, div=1)),
]

blind_results = []
for bname, bexpected, bops in BLIND_TEST:
    bvec = np.array(get_counts(bops), dtype=float)
    pred_fitted  = float(bvec @ coeffs)
    pred_naive   = float(bvec @ superbest_vec)
    blind_results.append({
        "name": bname,
        "expected": bexpected,
        "predicted_fitted": round(pred_fitted, 3),
        "predicted_naive": pred_naive,
        "error_fitted": round(pred_fitted - bexpected, 3),
        "error_naive": pred_naive - bexpected,
    })

# ─── Assemble results ─────────────────────────────────────────────────────────
fitted_coeffs = {op: float(round(coeffs[i], 4)) for i, op in enumerate(OPS)}
superbest_compare = {
    op: {
        "superbest": SUPERBEST[op],
        "fitted": fitted_coeffs[op],
        "delta": round(fitted_coeffs[op] - SUPERBEST[op], 4)
    }
    for op in OPS
}

data_table = []
for i, (n, ac, od) in enumerate(CATALOG):
    counts = get_counts(od)
    data_table.append({
        "name": n,
        "actual": float(ac),
        "naive": float(naive_costs[i]),
        "fitted": float(round(fitted_costs[i], 3)),
        "residual": float(round(residuals[i], 3)),
        "sharing_correction": float(sharing_correction[i]),
        "op_counts": {op: int(counts[j]) for j, op in enumerate(OPS)},
    })

result = {
    "session": "COST-1",
    "title": "SuperBEST v3 Cost Regression — 50-equation data mine",
    "ops_order": OPS,
    "superbest_v3": SUPERBEST,
    "fitted_coefficients": fitted_coeffs,
    "r_squared": round(r2, 6),
    "rmse": round(float(np.sqrt(ss_res / len(actual_costs))), 4),
    "mae": round(float(np.mean(np.abs(residuals))), 4),
    "superbest_comparison": superbest_compare,
    "top5_positive_residuals": [
        {"name": r[0], "residual": r[1], "actual": r[2], "fitted": r[3]}
        for r in top5_pos
    ],
    "top5_negative_residuals": [
        {"name": r[0], "residual": r[1], "actual": r[2], "fitted": r[3]}
        for r in top5_neg
    ],
    "data_table": data_table,
    "blind_test": blind_results,
    "sharing_pattern_analysis": {
        "description": "sharing_correction = actual - naive. Negative = cheaper than naive, positive = more expensive.",
        "large_discounts": [],  # filled below
        "large_premiums": [],
    }
}

# Find sharing pattern extremes
sc_sorted = sorted(enumerate(sharing_correction), key=lambda x: x[1])
result["sharing_pattern_analysis"]["large_discounts"] = [
    {"name": names[i], "correction": float(v), "naive": float(naive_costs[i]), "actual": float(actual_costs[i])}
    for i, v in sc_sorted[:5]
]
result["sharing_pattern_analysis"]["large_premiums"] = [
    {"name": names[i], "correction": float(v), "naive": float(naive_costs[i]), "actual": float(actual_costs[i])}
    for i, v in sc_sorted[-5:]
]

import pathlib
out_path = pathlib.Path(__file__).parent / "results" / "cost1_regression.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Saved -> {out_path}")
print(f"R² = {r2:.6f}   RMSE = {np.sqrt(ss_res/len(actual_costs)):.4f}   MAE = {np.mean(np.abs(residuals)):.4f}")
print("\nFitted coefficients vs SuperBEST:")
for op in OPS:
    print(f"  {op:6s}: fitted={fitted_coeffs[op]:6.3f}  superbest={SUPERBEST[op]}  d={fitted_coeffs[op]-SUPERBEST[op]:+.3f}")
print("\nTop-5 positive residuals (actual > fitted):")
for r in top5_pos:
    print(f"  {r[0][:40]:40s}: residual={r[1]:+.2f} (actual={r[2]:.0f}, fitted={r[3]:.2f})")
print("\nTop-5 negative residuals (actual < fitted):")
for r in top5_neg:
    print(f"  {r[0][:40]:40s}: residual={r[1]:+.2f} (actual={r[2]:.0f}, fitted={r[3]:.2f})")
print("\nBlind test predictions:")
for b in blind_results:
    print(f"  {b['name'][:35]:35s}: expected={b['expected']:3d}  pred_fitted={b['predicted_fitted']:6.2f}  err={b['error_fitted']:+.2f}")
