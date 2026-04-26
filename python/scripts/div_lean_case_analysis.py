"""
Analyze all 3072 F1-F12-outer 2-node F16 circuits at (x,y)=(6,3) with Lean semantics.
Lean semantics: Real.log(x) = 0 for x <= 0 (not undefined).
Identifies near-2 cases that need custom Lean proofs.
"""
import math
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Lean-compatible log
def L(x):
    return math.log(x) if x > 0 else 0.0

def E(x):
    try:
        return math.exp(x)
    except OverflowError:
        return float('inf')

# 16 F16 operators, Lean semantics
OPS = {
    'F1':  lambda a, b: E(a) - L(b),
    'F2':  lambda a, b: E(a) - L(-b),
    'F3':  lambda a, b: E(-a) - L(b),
    'F4':  lambda a, b: E(-a) - L(-b),
    'F5':  lambda a, b: E(b) - L(a),
    'F6':  lambda a, b: E(-b) - L(a),
    'F7':  lambda a, b: E(b) - L(-a),
    'F8':  lambda a, b: E(-b) - L(-a),
    'F9':  lambda a, b: a - L(b),
    'F10': lambda a, b: a - L(-b),
    'F11': lambda a, b: L(E(a) + b),
    'F12': lambda a, b: L(E(a) - b),
    'F13': lambda a, b: E(a * L(b)),
    'F14': lambda a, b: E(a + L(b)),
    'F15': lambda a, b: E(a + L(-b)),
    'F16': lambda a, b: E(L(a) + L(b)),
}

X, Y = 6.0, 3.0
TARGET = X / Y  # 2.0

# F1-F12 are the outer ops we need to prove
F12_OUTERS = ['F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12']

# Inner values at (6,3) for all 64 combinations
print("=== Inner values at (6,3) ===")
inner_vals = {}
for name, fn in OPS.items():
    for a_s in ['x', 'y']:
        for b_s in ['x', 'y']:
            a = X if a_s == 'x' else Y
            b = X if b_s == 'x' else Y
            v = fn(a, b)
            key = (name, a_s, b_s)
            inner_vals[key] = v

# Print inner val categories
print("\nInner value ranges:")
for key, v in sorted(inner_vals.items(), key=lambda x: x[1]):
    print(f"  {key[0]}({key[1]},{key[2]}) = {v:.4f}")

# Compute all outer circuits
print("\n=== Circuit analysis at (6,3) ===")
all_circuits = []
for outer_name in F12_OUTERS:
    outer_fn = OPS[outer_name]
    for (inner_name, a_s, b_s), iv in inner_vals.items():
        for c_s in ['x', 'y']:
            c = X if c_s == 'x' else Y
            for shape in ['A', 'B']:
                try:
                    result = outer_fn(iv, c) if shape == 'A' else outer_fn(c, iv)
                    if not math.isfinite(result):
                        result = 1e18  # effectively infinity
                except (OverflowError, ValueError):
                    result = 1e18
                diff = abs(result - TARGET)
                all_circuits.append({
                    'outer': outer_name, 'inner': inner_name,
                    'a': a_s, 'b': b_s, 'c': c_s, 'shape': shape,
                    'inner_val': iv, 'result': result, 'diff': diff
                })

total = len(all_circuits)
print(f"Total F1-F12 outer circuits: {total}")

# Check any matches
matches = [c for c in all_circuits if c['diff'] < 1e-9]
print(f"Exact matches (result = 2): {len(matches)}")

# Categorize by difficulty
near1 = [c for c in all_circuits if c['diff'] < 1.0]
near05 = [c for c in all_circuits if c['diff'] < 0.5]
near01 = [c for c in all_circuits if c['diff'] < 0.1]

print(f"Within 1 of target: {len(near1)}")
print(f"Within 0.5 of target: {len(near05)}")
print(f"Within 0.1 of target: {len(near01)}")

print("\n=== Near-2 cases (diff < 0.5, sorted by closeness) ===")
for c in sorted(near05, key=lambda x: x['diff']):
    iv_str = f"{c['inner']}({c['a']},{c['b']})"
    if c['shape'] == 'A':
        expr = f"{c['outer']}({iv_str}, {c['c']})"
    else:
        expr = f"{c['outer']}({c['c']}, {iv_str})"
    print(f"  {expr}: inner={c['inner_val']:.5f}, result={c['result']:.6f}, diff={c['diff']:.6f}")

# Summary by outer op
print("\n=== By outer op: how many near-2 cases (diff < 0.5)? ===")
for outer_name in F12_OUTERS:
    near = [c for c in all_circuits if c['outer'] == outer_name and c['diff'] < 0.5]
    far_pos = [c for c in all_circuits if c['outer'] == outer_name and c['result'] > 2.5]
    far_neg = [c for c in all_circuits if c['outer'] == outer_name and c['result'] < 1.5]
    print(f"  {outer_name}: near-2={len(near)}, far-positive={len(far_pos)}, far-negative={len(far_neg)}")

# For each "near-2" case, show the exact mathematical form
print("\n=== Exact forms of near-2 cases (for Lean proof) ===")
for c in sorted(near05, key=lambda x: x['diff']):
    outer = c['outer']
    inner = c['inner']
    a_val = X if c['a'] == 'x' else Y  # 6 or 3
    b_val = X if c['b'] == 'x' else Y
    c_val = X if c['c'] == 'x' else Y
    shape = c['shape']

    # Express the circuit symbolically
    if shape == 'A':
        print(f"  D_{outer}(D_{inner}({a_val:.0f},{b_val:.0f}), {c_val:.0f})")
        print(f"    = D_{outer}({c['inner_val']:.5f}, {c_val:.0f})")
        print(f"    = {c['result']:.6f}  [target: 2.0, diff: {c['diff']:.6f}]")
    else:
        print(f"  D_{outer}({c_val:.0f}, D_{inner}({a_val:.0f},{b_val:.0f}))")
        print(f"    = D_{outer}({c_val:.0f}, {c['inner_val']:.5f})")
        print(f"    = {c['result']:.6f}  [target: 2.0, diff: {c['diff']:.6f}]")

    # Show what the proof condition reduces to
    if outer == 'F9':
        # F9(v,c) = v - log(c). For = 2: v = 2 + log(c).
        if shape == 'A':
            # v = inner_val, c = c_val
            print(f"    Proof: inner_val ≠ 2 + log({c_val:.0f})")
            target_inner = 2 + L(c_val)
            print(f"    inner_val={c['inner_val']:.5f} vs 2+log({c_val:.0f})={target_inner:.5f}")
        else:
            # F9(c, inner_val) = c - log(inner_val). For = 2: log(inner_val) = c - 2.
            print(f"    Proof: log(inner_val) ≠ {c_val:.0f} - 2 = {c_val-2:.0f}")
    print()

print("Done.")
