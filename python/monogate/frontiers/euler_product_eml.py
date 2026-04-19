"""Session 58 — Euler Products, L-functions & EML Depth.

Each Euler factor (1-p^{-s})^{-1} = 1/(1-exp(-s·log(p))) is depth-1 ceml.
Partial Euler products approximate ζ(s) and Dirichlet L-functions at depth 1.
"""
import cmath, math
from typing import Dict, List
__all__ = ["run_session58"]

PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

def euler_factor(p: int, s: complex) -> complex:
    return 1.0 / (1.0 - cmath.exp(-s * math.log(p)))

def zeta_euler(s: complex, primes=PRIMES) -> complex:
    r = complex(1)
    for p in primes: r *= euler_factor(p, s)
    return r

def zeta_series(s: complex, N: int = 2000) -> complex:
    return sum(cmath.exp(-s * math.log(n)) for n in range(1, N+1))

DEPTH_TABLE = [
    {"quantity": "p^{-s}",                    "depth": 1},
    {"quantity": "Euler factor (1-p^{-s})^{-1}", "depth": 1},
    {"quantity": "Partial Euler product",      "depth": 1},
    {"quantity": "ζ(s) exact",                 "depth": "EML-∞"},
    {"quantity": "q^n = exp(2πinτ)",           "depth": 1},
    {"quantity": "Modular form Σ a_n q^n [partial]", "depth": 1},
    {"quantity": "Zeros of ζ",                 "depth": "EML-∞"},
]

def verify(s_vals: List[complex]) -> Dict:
    results = []
    for s in s_vals:
        ep = zeta_euler(s, PRIMES)
        ds = zeta_series(s, N=1000)
        rel = abs(ep - ds) / abs(ds) if abs(ds) > 0 else 999
        results.append({"s": str(s), "rel_err": rel, "ok": rel < 0.02})
    z2 = zeta_series(complex(2), 10000)
    z4 = zeta_series(complex(4), 3000)
    return {
        "euler_vs_series": results, "all_ok": all(r["ok"] for r in results),
        "zeta2": abs(z2.real - math.pi**2/6) < 0.01,
        "zeta4": abs(z4.real - math.pi**4/90) < 0.01,
    }

def run_session58() -> Dict:
    v = verify([complex(2), complex(3), complex(4)])
    theorems = [
        "CEML-T126: p^{-s} = exp(-s·log(p)) = ceml(-s·log(p),1) — depth 1",
        "CEML-T127: Euler factors and partial Euler products are depth-1 ceml",
        "CEML-T128: ζ(s) exact is EML-∞ (infinite product over all primes)",
        "CEML-T129: Modular form q-expansions (q^n) are depth-1 ceml per harmonic",
        "CEML-T130: Zeros of ζ are EML-∞: no finite ceml expression known",
    ]
    ok = v["all_ok"] and v["zeta2"] and v["zeta4"]
    return {
        "session": 58, "title": "Euler Products, L-functions & EML Depth",
        "depth_table": DEPTH_TABLE, "verification": v, "theorems": theorems,
        "status": "PASS" if ok else "FAIL",
    }
