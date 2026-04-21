"""
Exhaustive 1- and 2-node F16 circuit search for multiplication x*y.
Confirms SB(mul, general) >= 3: no 2-node F16 circuit computes x*y for all reals.

CONJ_MUL_GEN_TIGHT attack — Step 1.
"""
import math
import itertools
import json

# ── helpers ──────────────────────────────────────────────────────────────────

def safe(fn, *args):
    try:
        r = fn(*args)
        if r is None or not math.isfinite(r):
            return None
        return r
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return None

TOL = 1e-9

def approx_eq(a, b):
    return a is not None and b is not None and abs(a - b) < TOL

# ── F16 operators ─────────────────────────────────────────────────────────────
# Defined over the natural domain; returns None if undefined at (x,y).

def F1(x, y):   return safe(lambda: math.exp(x) - math.log(y) if y > 0 else None)
def F2(x, y):   return safe(lambda: math.exp(x) - math.log(-y) if y < 0 else None)
def F3(x, y):   return safe(lambda: math.exp(-x) - math.log(y) if y > 0 else None)
def F4(x, y):   return safe(lambda: math.exp(-x) - math.log(-y) if y < 0 else None)
def F5(x, y):   return safe(lambda: math.exp(y) - math.log(x) if x > 0 else None)
def F6(x, y):   return safe(lambda: math.exp(-y) - math.log(x) if x > 0 else None)
def F7(x, y):   return safe(lambda: math.exp(y) - math.log(-x) if x < 0 else None)
def F8(x, y):   return safe(lambda: math.exp(-y) - math.log(-x) if x < 0 else None)
def F9(x, y):   return safe(lambda: x - math.log(y) if y > 0 else None)
def F10(x, y):  return safe(lambda: x - math.log(-y) if y < 0 else None)
def F11(x, y):  return safe(lambda: math.log(math.exp(x) + y) if math.exp(x) + y > 0 else None)
def F12(x, y):  return safe(lambda: math.log(math.exp(x) - y) if math.exp(x) - y > 0 else None)
def F13(x, y):  return safe(lambda: math.exp(x * math.log(y)) if y > 0 else None)
def F14(x, y):  return safe(lambda: math.exp(x + math.log(y)) if y > 0 else None)
def F15(x, y):  return safe(lambda: math.exp(x + math.log(-y)) if y < 0 else None)
def F16(x, y):  return safe(lambda: math.exp(math.log(x) + math.log(y)) if x > 0 and y > 0 else None)

OPS = [F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16]
OP_NAMES = [f"F{i}" for i in range(1, 17)]

# ── test points ───────────────────────────────────────────────────────────────
# Diverse (x, y) pairs: positive, negative, mixed, small, large
TEST_PTS = [
    (2.0,  3.0),   # x*y = 6
    (0.5,  4.0),   # x*y = 2
    (3.0,  5.0),   # x*y = 15
    (0.1,  10.0),  # x*y = 1
    (4.0,  0.25),  # x*y = 1
    (-1.0, 2.0),   # x*y = -2
    (1.0, -3.0),   # x*y = -3
    (2.0, -2.0),   # x*y = -4
    (-3.0, -4.0),  # x*y = 12
    (0.5, -0.5),   # x*y = -0.25
    (1.5,  2.0),   # x*y = 3
    (7.0,  0.5),   # x*y = 3.5
]

# ── 1-node check ──────────────────────────────────────────────────────────────
def check_1node():
    results = {}
    for name, op in zip(OP_NAMES, OPS):
        witness = None
        match = True
        for x, y in TEST_PTS:
            val = op(x, y)
            tgt = x * y
            if val is None or not approx_eq(val, tgt):
                witness = (x, y, val, tgt)
                match = False
                break
        results[name] = {
            "match": match,
            "witness": witness,
        }
    matches = [n for n, r in results.items() if r["match"]]
    return results, matches

# ── 2-node check ──────────────────────────────────────────────────────────────
# Two shapes:
#   A: outer(inner(a, b), c)
#   B: outer(c, inner(a, b))
# a, b, c ∈ {x, y}  →  selectors ∈ {0=x, 1=y}

def check_2node():
    results = {}
    matches = []
    total = 0

    for oi, outer_name in enumerate(OP_NAMES):
        outer = OPS[oi]
        for ii, inner_name in enumerate(OP_NAMES):
            inner = OPS[ii]
            for shape in ('A', 'B'):
                for a_sel, b_sel, c_sel in itertools.product((0, 1), repeat=3):
                    total += 1
                    circuit_id = f"{shape}:{outer_name}({inner_name}({'x' if a_sel==0 else 'y'},{'x' if b_sel==0 else 'y'}),{'x' if c_sel==0 else 'y'})"

                    witness = None
                    is_match = True
                    defined_at = 0

                    for x, y in TEST_PTS:
                        a = x if a_sel == 0 else y
                        b = x if b_sel == 0 else y
                        c = x if c_sel == 0 else y
                        inner_val = inner(a, b)
                        if inner_val is None:
                            val = None
                        elif shape == 'A':
                            val = outer(inner_val, c)
                        else:
                            val = outer(c, inner_val)
                        tgt = x * y
                        if val is None or not approx_eq(val, tgt):
                            witness = (x, y, val, tgt)
                            is_match = False
                            break
                        defined_at += 1

                    rec = {
                        "outer": outer_name, "inner": inner_name,
                        "shape": shape,
                        "a": "x" if a_sel == 0 else "y",
                        "b": "x" if b_sel == 0 else "y",
                        "c": "x" if c_sel == 0 else "y",
                        "match": is_match,
                        "defined_at": defined_at,
                        "witness": witness,
                    }
                    results[circuit_id] = rec
                    if is_match:
                        matches.append(circuit_id)

    return results, matches, total

# ── run ───────────────────────────────────────────────────────────────────────
print("=== Step 1: 1-node check ===")
r1, m1 = check_1node()
print(f"  1-node circuits: 16 checked, {len(m1)} matching x*y")
for name, res in r1.items():
    w = res['witness']
    wstr = f"  witness: ({w[0]},{w[1]}) => circuit={w[2]}, target={w[3]}" if w else "  NO WITNESS FOUND"
    status = "MATCH" if res['match'] else "ruled_out"
    print(f"  {name}: {status} {wstr}")

print()
print("=== Step 2: 2-node check ===")
r2, m2, total2 = check_2node()
print(f"  2-node circuits: {total2} checked, {len(m2)} matching x*y at all test points")
if m2:
    print("  MATCHES (unexpected!):")
    for cid in m2:
        print(f"    {cid}")
else:
    print("  No 2-node circuit matches x*y. Confirmed: SB(mul, general) >= 3.")

# ── summary for JSON ──────────────────────────────────────────────────────────
summary = {
    "conclusion": "SB(mul, general) >= 3" if not m2 else "UNEXPECTED MATCH FOUND",
    "method": "exhaustive F16 witness search",
    "date": "2026-04-21",
    "1node": {
        "total_checked": 16,
        "matches": len(m1),
        "ops_ruled_out": [n for n, r in r1.items() if not r["match"]],
    },
    "2node": {
        "total_checked": total2,
        "matches": len(m2),
        "match_ids": m2,
        "test_points": TEST_PTS,
        "shapes": ["A: outer(inner(a,b), c)", "B: outer(c, inner(a,b))"],
        "terminal_choices": "a,b,c ∈ {x, y}",
    },
    "gap_status": {
        "lower_bound_lean": 2,
        "lower_bound_python": 3 if not m2 else 2,
        "upper_bound": 6,
        "open_gap": "[3, 6]" if not m2 else "[2, 6]",
    },
    "next_step": "Prove >=3 in Lean via witness encoding or native_decide. Then check 3-node circuits for >=4.",
}

out_path = "python/results/mul_gen_tight_2node_search.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, default=str)
print(f"\nSummary written to {out_path}")
