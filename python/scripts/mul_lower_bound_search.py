"""
Exhaustive search: minimum node count for mul(x,y) = x*y
over mixed EML-family operators.

Checks all 1-node and 2-node trees with the 6 implemented operators
{EML, EDL, EXL, EAL, EMN, DEML} plus the 10 theoretical operators
{EPL, LEAd, ELAd, ELSb, DEAL, DEXL, DEDL, DEPL, DEMN, LEX}.

Outputs: python/results/s100_mul_lower_bound.json
"""
# -*- coding: utf-8 -*-
import sys, json, math, cmath, itertools
from pathlib import Path

# ── Test points -----------------------------------------------------------
TEST_POINTS = [
    (2.0, 3.0), (0.5, 4.0), (1.0, 5.0), (3.0, 2.0),
    (1.5, 1.5), (0.25, 8.0), (math.e, 2.0), (2.0, math.e),
]
TARGET = [(x * y) for x, y in TEST_POINTS]
EPS = 1e-7
DOMAIN_FAIL = float('nan')

def safe(fn, *args):
    try:
        v = fn(*args)
        if isinstance(v, complex):
            if abs(v.imag) > 1e-6:
                return DOMAIN_FAIL
            return v.real
        return float(v)
    except Exception:
        return DOMAIN_FAIL

def is_match(vals):
    return all(
        t is not DOMAIN_FAIL and not math.isnan(t) and abs(t - ref) < EPS
        for t, ref in zip(vals, TARGET)
    )

# ── 6 implemented operators -----------------------------------------------
def eml(a, b): return safe(lambda a,b: math.exp(a) - math.log(b), a, b)
def edl(a, b): return safe(lambda a,b: math.exp(a) / math.log(b), a, b)
def exl(a, b): return safe(lambda a,b: math.exp(a) * math.log(b), a, b)
def eal(a, b): return safe(lambda a,b: math.exp(a) + math.log(b), a, b)
def emn(a, b): return safe(lambda a,b: math.log(b) - math.exp(a), a, b)
def deml(a, b): return safe(lambda a,b: math.exp(-a) - math.log(b), a, b)

# ── 10 theoretical operators (T24-T28 census) ----------------------------
def epl(a, b): return safe(lambda a,b: math.exp(a) ** math.log(b), a, b)
def lead(a, b): return safe(lambda a,b: math.log(math.exp(a) + b), a, b)  # ln(exp(x)+y)
def elad(a, b): return safe(lambda a,b: math.exp(a) * b, a, b)            # exp(x)*y = exp(x+ln(y))
def elsb(a, b): return safe(lambda a,b: math.exp(a) / b, a, b)            # exp(x)/y = exp(x-ln(y))
def deal(a, b): return safe(lambda a,b: math.exp(-a) + math.log(b), a, b) # exp(-x)+ln(y)
def dexl(a, b): return safe(lambda a,b: math.exp(-a) * math.log(b), a, b) # exp(-x)*ln(y)
def dedl(a, b): return safe(lambda a,b: math.exp(-a) / math.log(b), a, b) # exp(-x)/ln(y)
def depl(a, b): return safe(lambda a,b: math.exp(-a) ** math.log(b), a, b)# exp(-x)^ln(y)
def demn(a, b): return safe(lambda a,b: math.log(b) - math.exp(-a), a, b) # ln(y)-exp(-x)
def lex(a, b): return safe(lambda a,b: math.log(math.exp(a) - b), a, b)   # ln(exp(x)-y)

SIX_OPS = {
    "EML": eml, "EDL": edl, "EXL": exl,
    "EAL": eal, "EMN": emn, "DEML": deml,
}

ALL16_OPS = {
    **SIX_OPS,
    "EPL": epl, "LEAd": lead, "ELAd": elad, "ELSb": elsb,
    "DEAL": deal, "DEXL": dexl, "DEDL": dedl,
    "DEPL": depl, "DEMN": demn, "LEX": lex,
}

# ── Terminals (0 and 1 are free constants per superbest.py) ---------------
def get_terminals(x, y):
    return {"x": x, "y": y, "0": 0.0, "1": 1.0}

TERMINAL_NAMES = ["x", "y", "0", "1"]

# ── 1-node search ---------------------------------------------------------
def search_1node(op_set):
    """Return all 1-node trees that compute mul(x,y)."""
    found = []
    for op_name, op in op_set.items():
        for a_name in TERMINAL_NAMES:
            for b_name in TERMINAL_NAMES:
                vals = []
                for (x, y) in TEST_POINTS:
                    T = get_terminals(x, y)
                    a, b = T[a_name], T[b_name]
                    vals.append(op(a, b))
                if is_match(vals):
                    found.append({
                        "nodes": 1,
                        "tree": f"{op_name}({a_name}, {b_name})",
                        "op": op_name, "a": a_name, "b": b_name,
                    })
    return found

# ── 2-node search ---------------------------------------------------------
def search_2node(op_set):
    """Return all 2-node mixed trees that compute mul(x,y).

    Two shapes:
      Shape A: op2(op1(a, b), c)
      Shape B: op2(c, op1(a, b))
    """
    found = []
    op_items = list(op_set.items())

    for (op1_name, op1), (op2_name, op2) in itertools.product(op_items, repeat=2):
        for a_name, b_name, c_name in itertools.product(TERMINAL_NAMES, repeat=3):
            # Shape A
            vals_A = []
            for (x, y) in TEST_POINTS:
                T = get_terminals(x, y)
                a, b, c = T[a_name], T[b_name], T[c_name]
                v1 = op1(a, b)
                if math.isnan(v1): break
                vals_A.append(op2(v1, c))
            else:
                if is_match(vals_A):
                    found.append({
                        "nodes": 2,
                        "shape": "A",
                        "tree": f"{op2_name}({op1_name}({a_name},{b_name}), {c_name})",
                    })

            # Shape B
            vals_B = []
            for (x, y) in TEST_POINTS:
                T = get_terminals(x, y)
                a, b, c = T[a_name], T[b_name], T[c_name]
                v1 = op1(a, b)
                if math.isnan(v1): break
                vals_B.append(op2(c, v1))
            else:
                if is_match(vals_B):
                    found.append({
                        "nodes": 2,
                        "shape": "B",
                        "tree": f"{op2_name}({c_name}, {op1_name}({a_name},{b_name}))",
                    })
    return found

# ── Main -----------------------------------------------------------------
if __name__ == "__main__":
    out = {}

    print("=== 1-node search (6-operator library) ===")
    r1_6 = search_1node(SIX_OPS)
    print(f"  Found: {len(r1_6)} constructions")
    out["1node_6ops"] = r1_6

    print("=== 2-node search (6-operator library) ===")
    r2_6 = search_2node(SIX_OPS)
    print(f"  Found: {len(r2_6)} constructions")
    out["2node_6ops"] = r2_6

    print("=== 1-node search (16-operator family) ===")
    r1_16 = search_1node(ALL16_OPS)
    print(f"  Found: {len(r1_16)} constructions")
    out["1node_16ops"] = r1_16

    print("=== 2-node search (16-operator family) ===")
    r2_16 = search_2node(ALL16_OPS)
    print(f"  Found: {len(r2_16)} constructions")
    out["2node_16ops"] = r2_16

    if r2_16:
        print("\nNEW 2-node constructions found:")
        for c in r2_16[:10]:
            print(f"  {c['tree']}")
    else:
        print("\nNo 2-node construction found even with 16 operators.")

    # Verify known 3-node construction
    known = "exl(exl(0,x), eml(y,1))"
    vals = []
    for (x, y) in TEST_POINTS:
        v = exl(exl(0.0, x), eml(y, 1.0))
        vals.append(v)
    ok = is_match(vals)
    print(f"\nKnown 3-node construction {known}: {'VALID' if ok else 'INVALID'}")
    out["known_3node_valid"] = ok

    # Save results
    out_path = Path(__file__).parent.parent / "results" / "s100_mul_lower_bound.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to {out_path}")
