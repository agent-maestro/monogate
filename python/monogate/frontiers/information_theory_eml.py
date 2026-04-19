"""Session 53 — Information Theory and EML.

Shannon entropy, KL divergence, mutual information as ceml expressions.
All involve log — depth 1 ceml via ceml(0,p) = 1-log(p).
"""
import cmath, math
from typing import Dict, List
__all__ = ["run_session53"]

def ceml_log(p: float) -> float:
    """Log(p) = 1 - ceml(0, p)."""
    return 1.0 - (math.exp(0) - math.log(p))   # = log(p)

def shannon_entropy(probs: List[float]) -> float:
    """H(P) = -Σ p·log(p). Each log is depth-1 ceml(0,p)."""
    return -sum(p * ceml_log(p) for p in probs if p > 1e-15)

def kl_divergence(p: List[float], q: List[float]) -> float:
    """KL(P‖Q) = Σ p·log(p/q). Depth-1 ceml via log(p/q) = log(p)-log(q)."""
    return sum(pi * (ceml_log(pi) - ceml_log(qi))
               for pi, qi in zip(p, q) if pi > 1e-15 and qi > 1e-15)

def mutual_information(joint: List[List[float]]) -> float:
    """I(X;Y) = Σ p(x,y)·log(p(x,y)/(p(x)p(y))). Depth-1 ceml."""
    n = len(joint); m = len(joint[0])
    px = [sum(joint[i][j] for j in range(m)) for i in range(n)]
    py = [sum(joint[i][j] for i in range(n)) for j in range(m)]
    return sum(
        joint[i][j] * (ceml_log(joint[i][j]) - ceml_log(px[i]) - ceml_log(py[j]))
        for i in range(n) for j in range(m)
        if joint[i][j] > 1e-15 and px[i] > 1e-15 and py[j] > 1e-15
    )

INFO_THEORY_DEPTH = [
    {"quantity": "H(P) = -Σ p log p",        "ceml_depth": 1, "formula": "ceml(0,p)=1-log(p)"},
    {"quantity": "KL(P‖Q) = Σ p log(p/q)",   "ceml_depth": 1, "formula": "log(p/q)=log(p)-log(q)"},
    {"quantity": "I(X;Y) = H(X)-H(X|Y)",     "ceml_depth": 1, "formula": "two log calls, depth 1 each"},
    {"quantity": "H(X|Y) = -Σ p(x,y)log p(x|y)", "ceml_depth": 1, "formula": "depth 1 per term"},
    {"quantity": "Channel capacity C = max I(X;Y)", "ceml_depth": "EML-∞", "formula": "optimization over distributions"},
    {"quantity": "AEP: -1/n log P(X^n) → H", "ceml_depth": 1, "formula": "LLN + log = depth 1"},
    {"quantity": "Rate-distortion R(D)",       "ceml_depth": "EML-∞", "formula": "variational, no finite ceml"},
]

def verify_info_quantities() -> Dict:
    # Uniform binary
    p_uniform = [0.5, 0.5]
    h_uniform = shannon_entropy(p_uniform)

    # Biased
    p_biased = [0.9, 0.1]
    h_biased = shannon_entropy(p_biased)

    # KL: P=[0.4,0.6], Q=[0.5,0.5]
    P = [0.4, 0.6]; Q = [0.5, 0.5]
    kl = kl_divergence(P, Q)
    kl_ref = sum(P[i]*math.log(P[i]/Q[i]) for i in range(2))

    # MI: XOR channel
    joint = [[0.25, 0.25], [0.25, 0.25]]  # independent → MI = 0
    mi_indep = mutual_information(joint)

    joint_dep = [[0.5, 0.0], [0.0, 0.5]]  # perfectly correlated → MI = 1 bit
    mi_dep = mutual_information(joint_dep)

    return {
        "H_uniform": {"val": h_uniform, "expected": math.log(2), "ok": abs(h_uniform - math.log(2)) < 1e-10},
        "H_biased_less": h_biased < h_uniform,
        "KL_PQ": {"ceml": kl, "ref": kl_ref, "ok": abs(kl - kl_ref) < 1e-10},
        "MI_indep": {"val": mi_indep, "ok": abs(mi_indep) < 1e-10},
        "MI_dep": {"val": mi_dep, "expected": math.log(2), "ok": abs(mi_dep - math.log(2)) < 1e-10},
    }

def run_session53() -> Dict:
    checks = verify_info_quantities()
    all_ok = all(v["ok"] for v in checks.values() if isinstance(v, dict) and "ok" in v) and checks["H_biased_less"]
    theorems = [
        "CEML-T103: Shannon entropy H(P) is depth-1 ceml: each -p·log(p) = p·(ceml(0,p)-1)",
        "CEML-T104: KL divergence is depth-1 ceml: log(p/q) = ceml(0,q) - ceml(0,p)",
        "CEML-T105: Mutual information I(X;Y) is depth-1 ceml (all terms are logs)",
        "CEML-T106: All additive information measures are EML-1; variational measures (R(D), C) are EML-∞",
    ]
    return {
        "session": 53, "title": "Information Theory and EML",
        "depth_table": INFO_THEORY_DEPTH,
        "verifications": checks,
        "theorems": theorems,
        "status": "PASS" if all_ok else "FAIL",
    }
