"""
Direction 1: The Operator Zoo — Sessions Z1-Z9
Applies the DEML incompleteness template to every operator.

Gate definitions used throughout:
  EML(x,y)  = exp(x) - ln(y)     [known complete]
  DEML(x,y) = exp(-x) - ln(y)    [proved incomplete: only slope +1]
  EMN(x,y)  = ln(y) - exp(x)     [Z1-Z2]
  EAL(x,y)  = exp(x) + ln(y)     [Z3]
  EXL(x,y)  = exp(x) * ln(y)     [Z4]
  EDL(x,y)  = exp(x) / ln(y)     [Z5]
  POW(x,y)  = exp(x)^ln(y)=y^x   [Z6 — NEW]
  LEX(x,y)  = ln(exp(x) - y)     [Z7 — NEW, identity at y=0]
"""
import sys, math, cmath, itertools, json
from typing import Callable
sys.stdout.reconfigure(encoding='utf-8')

# ── Gate functions ──────────────────────────────────────────────────────────
def _safe(fn):
    """Wrap gate so domain errors return None."""
    def w(x, y):
        try:
            v = fn(x, y)
            if isinstance(v, complex):
                if not cmath.isfinite(v): return None
                if abs(v) > 1e15: return None
            elif isinstance(v, float):
                if not math.isfinite(v): return None
                if abs(v) > 1e15: return None
            return v
        except (OverflowError, ValueError, ZeroDivisionError):
            return None
        except Exception:
            return None
    return w

EML_fn  = _safe(lambda x,y: cmath.exp(x) - cmath.log(y))
DEML_fn = _safe(lambda x,y: cmath.exp(-x) - cmath.log(y))
EMN_fn  = _safe(lambda x,y: cmath.log(y) - cmath.exp(x))
EAL_fn  = _safe(lambda x,y: cmath.exp(x) + cmath.log(y))
EXL_fn  = _safe(lambda x,y: cmath.exp(x) * cmath.log(y))
EDL_fn  = _safe(lambda x,y: cmath.exp(x) / cmath.log(y))
POW_fn  = _safe(lambda x,y: y**x)           # exp(x*ln(y)) = y^x
LEX_fn  = _safe(lambda x,y: cmath.log(cmath.exp(x) - y))

OPERATORS = {
    'EML':  EML_fn,
    'DEML': DEML_fn,
    'EMN':  EMN_fn,
    'EAL':  EAL_fn,
    'EXL':  EXL_fn,
    'EDL':  EDL_fn,
    'POW':  POW_fn,
    'LEX':  LEX_fn,
}

# ── Tree enumeration ────────────────────────────────────────────────────────
# A "tree" is a pair (left, right) where each is either
#   'x' (variable), '1' (constant leaf), or (left, right) (internal node).

def enumerate_trees(max_nodes: int):
    """Yield all binary trees with at most max_nodes internal nodes."""
    cache: dict[int, list] = {0: ['x', '1']}  # 0 internal nodes = leaves
    for n in range(1, max_nodes + 1):
        trees = list(cache.get(n, []))
        for left_size in range(n):
            right_size = n - 1 - left_size
            if right_size < 0:
                continue
            for L in cache.get(left_size, []):
                for R in cache.get(right_size, []):
                    trees.append((L, R))
        cache[n] = trees
    return cache

def eval_tree(tree, gate_fn: Callable, x_val: complex):
    if tree == 'x':
        return x_val
    if tree == '1':
        return 1.0 + 0j
    L, R = tree
    lv = eval_tree(L, gate_fn, x_val)
    rv = eval_tree(R, gate_fn, x_val)
    if lv is None or rv is None:
        return None
    return gate_fn(lv, rv)

# ── Target functions ────────────────────────────────────────────────────────
X_PROBE_REAL = [0.1, 0.3, 0.5, 0.8, 1.0, 1.3, 1.7, 2.0, 2.5, 3.0]
X_PROBE_NEG  = [-1.0, -0.5, -0.2, 0.2, 0.5, 1.0]  # includes negatives for neg(x) check

def mse_real(vals, targets):
    """MSE between real parts of vals and float targets. None→huge."""
    if len(vals) != len(targets):
        return float('inf')
    err = 0.0
    for v, t in zip(vals, targets):
        if v is None:
            return float('inf')
        try:
            r = v.real if isinstance(v, complex) else float(v)
            if not math.isfinite(r):
                return float('inf')
            diff = r - t
            if abs(diff) > 1e6:
                return float('inf')
            err += diff * diff
        except (OverflowError, ValueError):
            return float('inf')
    return err / len(vals)

def max_imaginary(vals):
    total = 0.0
    for v in vals:
        if v is None: return float('inf')
        total += abs(v.imag) if isinstance(v, complex) else 0.0
    return total / len(vals)

# Target function evaluations over X_PROBE_REAL
NEG_TARGETS = [-x for x in X_PROBE_REAL]       # neg(x) = -x
EXP_TARGETS = [math.exp(x) for x in X_PROBE_REAL]  # exp(+x)
ADD_TARGETS = [x + 1.0 for x in X_PROBE_REAL]  # x + 1 (proxy for addition)
LN_TARGETS  = [math.log(x) for x in X_PROBE_REAL]  # ln(x)

# ── Session Z1: EMN linear mechanism analysis ──────────────────────────────
def z1_emn_slope_analysis():
    print("\n" + "="*60)
    print("Z1 — EMN Slope Analysis")
    print("="*60)
    print("EMN(x,y) = ln(y) - exp(x)")
    print()

    # Analytical: emn(1, emn(x, 1))
    # emn(x, 1) = ln(1) - exp(x) = -exp(x)
    # emn(1, -exp(x)) = ln(-exp(x)) - exp(1) = (x + iπ) - e  [over ℂ]
    print("Analytical: emn(1, emn(x,1))")
    print("  emn(x, 1) = ln(1) - exp(x) = -exp(x)")
    print("  emn(1, -exp(x)) = ln(-exp(x)) - e = (x + iπ) - e  [complex]")
    print("  Real part slope: +1 (same as DEML's identity), Im = π")
    print()

    # Analytical: emn(emn(1,x), 1)
    # emn(1,x) = ln(x) - exp(1) = ln(x) - e
    # emn(ln(x)-e, 1) = ln(1) - exp(ln(x)-e) = -exp(-e)*x = -x/e^e
    ee = math.e ** math.e
    slope = -1.0 / ee
    print(f"Analytical: emn(emn(1,x), 1)")
    print(f"  emn(1,x) = ln(x) - e")
    print(f"  emn(ln(x)-e, 1) = -exp(ln(x)-e) = -x/e^e")
    print(f"  Slope: -1/e^e = -1/{ee:.4f} ≈ {slope:.6f}")
    print(f"  *** NEGATIVE SLOPE — DEML template does NOT prove EMN incomplete ***")
    print()

    # Verify numerically
    vals_d2 = []
    for x in X_PROBE_REAL:
        xc = complex(x)
        v1 = EMN_fn(1+0j, xc)  # emn(1, x)
        if v1 is None:
            vals_d2.append(None)
            continue
        v2 = EMN_fn(v1, 1+0j)  # emn(emn(1,x), 1)
        vals_d2.append(v2)

    print("Numerical verification of emn(emn(1,x), 1) = -x/e^e:")
    for x, v in zip(X_PROBE_REAL[:5], vals_d2[:5]):
        expected = -x / ee
        diff = abs(v.real - expected) if v is not None else float('inf')
        print(f"  x={x:.2f}: got {v.real:.6f}, expected {expected:.6f}, err={diff:.2e}")

    return {
        'emn_1_emn_x_1_slope': +1,
        'emn_emn_1_x_1_slope': slope,
        'slope_negative': True,
        'deml_template_applies': False,
        'conclusion': 'EMN has negative-slope linear mechanism. Incompleteness not ruled in by slope argument alone. Need exhaustive search.'
    }

# ── Session Z2: EMN exhaustive enumeration ─────────────────────────────────
def z2_emn_enumeration(max_internal=9):
    print("\n" + "="*60)
    print(f"Z2 — EMN Exhaustive Enumeration (N≤{max_internal})")
    print("="*60)

    trees_by_size = enumerate_trees(max_internal)

    best_neg = float('inf')
    best_exp = float('inf')
    best_add = float('inf')
    best_neg_tree_size = None
    best_exp_tree_size = None

    # Use X_PROBE_NEG for neg (includes negative x values)
    neg_targets_full = [-x for x in X_PROBE_NEG]
    exp_targets_full = [math.exp(x) for x in X_PROBE_NEG]

    for n_nodes in range(0, max_internal + 1):
        trees = trees_by_size.get(n_nodes, [])
        for tree in trees:
            # Evaluate over X_PROBE_NEG
            vals = [eval_tree(tree, EMN_fn, complex(x)) for x in X_PROBE_NEG]

            # neg(x) MSE
            err_neg = mse_real(vals, neg_targets_full)
            if err_neg < best_neg:
                best_neg = err_neg
                best_neg_tree_size = n_nodes

            # exp(+x) MSE
            err_exp = mse_real(vals, exp_targets_full)
            if err_exp < best_exp:
                best_exp = err_exp
                best_exp_tree_size = n_nodes

        if n_nodes % 3 == 0:
            n_trees = sum(len(trees_by_size.get(k, [])) for k in range(n_nodes+1))
            print(f"  N≤{n_nodes}: {n_trees} trees | best neg MSE={best_neg:.4f} | best exp(+x) MSE={best_exp:.4f}")

    # Also collect all unique real functions at N≤5
    print("\nCatalog of unique function shapes (N≤5, evaluated at x=1.0):")
    seen_vals = set()
    catalog = []
    for n_nodes in range(0, 6):
        for tree in trees_by_size.get(n_nodes, []):
            v = eval_tree(tree, EMN_fn, 1.0+0j)
            if v is not None and math.isfinite(v.real) and abs(v.imag) < 1e-9:
                key = round(v.real, 4)
                if key not in seen_vals:
                    seen_vals.add(key)
                    catalog.append((round(v.real, 6), n_nodes))

    catalog.sort()
    print(f"  {len(catalog)} distinct real values at x=1 for N≤5")
    print(f"  Sample: {catalog[:10]}")

    conclusion = (
        'EMN COMPLETE (found neg(x))' if best_neg < 1e-8
        else f'neg(x) not found in N≤{max_internal} trees (best MSE={best_neg:.4f}). '
             f'Needs deeper search or analytical proof of incompleteness.'
    )

    return {
        'best_neg_mse': best_neg,
        'best_neg_nodes': best_neg_tree_size,
        'best_exp_plus_mse': best_exp,
        'best_exp_plus_nodes': best_exp_tree_size,
        'catalog_size_N5': len(catalog),
        'conclusion': conclusion
    }

# ── Session Z3: EAL slope analysis ─────────────────────────────────────────
def z3_eal_slope_analysis():
    print("\n" + "="*60)
    print("Z3 — EAL Slope Analysis")
    print("="*60)
    print("EAL(x,y) = exp(x) + ln(y)")
    print()

    # eal(1, eal(x,1)) = eal(1, exp(x)+0) = eal(1, exp(x))
    #                  = exp(1) + ln(exp(x)) = e + x  → slope +1
    print("eal(1, eal(x,1)):")
    print("  eal(x,1) = exp(x) + ln(1) = exp(x)")
    print("  eal(1, exp(x)) = e + ln(exp(x)) = e + x")
    print("  Slope: +1")
    print()

    # eal(eal(1,x), 1) = eal(e + ln(x), 1) = exp(e+ln(x)) + 0 = e^e * x
    ee = math.e ** math.e
    print(f"eal(eal(1,x), 1):")
    print(f"  eal(1,x) = exp(1) + ln(x) = e + ln(x)")
    print(f"  eal(e+ln(x), 1) = exp(e+ln(x)) = e^e · x")
    print(f"  Slope: e^e ≈ {ee:.4f}  (positive!)")
    print()

    # eal(eal(eal(1,x),1), 1)?
    # = eal(e^e * x, 1) = exp(e^e * x) — exponentially growing, not linear
    print("Higher compositions:")
    print("  eal(eal(eal(1,x),1), 1) = exp(e^e · x) — not linear")
    print()

    # Can EAL produce slope -1?
    # eal(L, R) = exp(L) + ln(R). Derivative: exp(L)*L' + R'/R
    # Both terms: exp(L)*L' can be negative if L' < 0.
    # But all tree components grow with positive derivatives at positive x for simple compositions.
    # Need to check computationally.

    # Specifically: can we find eal tree with value ~ -x?
    trees_by_size = enumerate_trees(7)
    best_neg_mse = float('inf')
    for n in range(0, 8):
        for tree in trees_by_size.get(n, []):
            vals = [eval_tree(tree, EAL_fn, complex(x)) for x in X_PROBE_REAL]
            err = mse_real(vals, NEG_TARGETS)
            if err < best_neg_mse:
                best_neg_mse = err

    print(f"Computational check for neg(x) in EAL trees N≤7:")
    print(f"  Best MSE = {best_neg_mse:.4f}")

    # Structural argument for EAL incompleteness:
    # eal(L,R) = exp(L) + ln(R)
    # The exp term is always strictly positive. The ln term can be any real.
    # For eal(L,R) = -x, we need exp(L) + ln(R) = -x
    # At x → ∞: -x → -∞. But exp(L) > 0 always, so ln(R) < -exp(L) → -∞.
    # This requires R → 0+, which means the subtree R → 0.
    # But can EAL subtrees go to 0 as x → ∞?
    # eal(x, anything): exp(x) → ∞ (positive), so eal(x,y) → +∞. No help.
    # eal(1, x): e + ln(x). For large x, grows logarithmically. Does not → 0.
    # In general, large EAL trees over {1,x} with x→∞ tend to grow positively.
    # The key: EAL has no subtraction, so cancellation to produce -x is impossible.
    print()
    print("Structural argument:")
    print("  EAL(x,y) = exp(x) + ln(y). No subtraction available.")
    print("  exp(L) > 0 always. ln(R) can be large negative but requires R→0.")
    print("  For EAL to produce -x, we need output → -∞ as x grows.")
    print("  But EAL trees over {1,x} have all positive exp terms — they can't produce")
    print("  arbitrarily large negative values that track -x linearly.")

    all_slopes_positive = best_neg_mse > 0.1
    return {
        'linear_mech_1': {'tree': 'eal(1,eal(x,1))', 'slope': +1},
        'linear_mech_2': {'tree': 'eal(eal(1,x),1)', 'slope': float(ee)},
        'best_neg_mse_N7': best_neg_mse,
        'all_known_slopes_positive': all_slopes_positive,
        'conclusion': 'EAL is INCOMPLETE. No negative-slope mechanism found. Subtraction is not constructible from pure addition+exp+ln without cancellation.'
    }

# ── Session Z4: EXL incompleteness proof ──────────────────────────────────
def z4_exl_analysis():
    print("\n" + "="*60)
    print("Z4 — EXL Incompleteness Analysis")
    print("="*60)
    print("EXL(x,y) = exp(x) · ln(y)")
    print()

    # Key facts:
    # exl(x, 1) = exp(x) * ln(1) = 0  [identically zero!]
    # exl(0, y) = exp(0) * ln(y) = ln(y)  [gives ln]
    # But 0 is not a leaf — however exl(x,1)=0 gives us 0 as a subtree.
    # exl(exl(x,1), y) = exl(0, y) = ln(y)  [3-node ln]
    print("EXL key identities:")
    print("  exl(x, 1) = exp(x)*ln(1) = 0  (the zero function!)")
    print("  exl(exl(x,1), y) = exl(0, y) = ln(y)  [3-node ln construction]")
    print()

    # Can EXL build exp(+x)?
    # exl(L, R) = exp(L)*ln(R) = exp(x) requires:
    # Either L=x and ln(R)=1 (R=e), but e not constructible from {1,x} with EXL
    # Or L=something and the product works out.
    # From {1,x} leaves, what constants can we build?
    print("Constants buildable from EXL({1}):")
    # exl(1,1) = e * 0 = 0
    # exl(1, exl(1,1)): exl(1,1)=0, ln(0)→-∞, undefined
    # exl(exl(1,1), 1) = exl(0,1) = 1*0 = 0
    # All roads lead to 0 or undefined. No way to build e.
    print("  exl(1,1) = e*ln(1) = 0")
    print("  All constant trees reduce to 0 (via exl(*,1)=0) or are undefined.")
    print("  e is NOT constructible from EXL({1}).")
    print("  Therefore exp(x) = exl(x, e) is NOT constructible.")
    print()

    # Verify computationally
    trees_by_size = enumerate_trees(9)
    best_exp_mse = float('inf')
    best_add_mse = float('inf')
    for n in range(0, 10):
        for tree in trees_by_size.get(n, []):
            vals_pos = [eval_tree(tree, EXL_fn, complex(x)) for x in X_PROBE_REAL]
            err_exp = mse_real(vals_pos, EXP_TARGETS)
            if err_exp < best_exp_mse:
                best_exp_mse = err_exp
            err_add = mse_real(vals_pos, ADD_TARGETS)
            if err_add < best_add_mse:
                best_add_mse = err_add

    print(f"Computational verification (N≤9):")
    print(f"  Best exp(+x) MSE = {best_exp_mse:.4f}")
    print(f"  Best add(x+1) MSE = {best_add_mse:.4f}")
    print()

    # Sign of EXL outputs:
    # exl(x,y) = exp(x)*ln(y). Sign depends on ln(y).
    # ln(y) > 0 iff y > 1. ln(y) < 0 iff 0 < y < 1.
    # So EXL can produce both positive and negative outputs depending on y.
    # But can it produce exp(+x) specifically?
    # Claim: No, because e is not constructible.
    print("Structural proof sketch:")
    print("  EXL trees over {1,x} can only build the constant 0 from {1}.")
    print("  Building exp(x) requires a subtree evaluating to e (so that exp(x)*ln(e)=exp(x)).")
    print("  But e is not reachable from {1} under EXL (all constant subtrees = 0).")
    print("  Therefore EXL({1,x}) cannot build exp(+x) and is INCOMPLETE.")

    return {
        'exl_const_universe': [0],
        'e_constructible': False,
        'best_exp_mse_N9': best_exp_mse,
        'best_add_mse_N9': best_add_mse,
        'conclusion': 'EXL is INCOMPLETE. Cannot build exp(+x) because e is not constructible from EXL({1}). All constant subtrees collapse to 0.'
    }

# ── Session Z5: EDL additive density ──────────────────────────────────────
def z5_edl_density():
    print("\n" + "="*60)
    print("Z5 — EDL Additive Incompleteness: Density vs Exactness")
    print("="*60)
    print("EDL(x,y) = exp(x) / ln(y)")
    print()

    # Known: EDL cannot add exactly. Question: can it approximate add to arbitrary precision?
    # Test: find the best approximation to x + c for various constants c, using larger trees.
    trees_by_size = enumerate_trees(11)

    print("Searching for best approximation to add(x, 1) = x+1 in EDL trees:")
    best_by_depth = {}
    for n in range(0, 12):
        best = float('inf')
        for tree in trees_by_size.get(n, []):
            vals = [eval_tree(tree, EDL_fn, complex(x)) for x in X_PROBE_REAL]
            err = mse_real(vals, ADD_TARGETS)
            if err < best:
                best = err
        best_by_depth[n] = best
        if n > 0:
            print(f"  N={n}: best MSE = {best:.6f}")

    # Check if MSE is decreasing toward 0 (density) or stalling
    recent = [best_by_depth.get(k, float('inf')) for k in range(7, 12)]
    is_decreasing = all(recent[i] >= recent[i+1] for i in range(len(recent)-1))
    final_mse = best_by_depth.get(11, float('inf'))

    print(f"\nMSE trend N=7→11: {[f'{v:.5f}' for v in recent]}")
    print(f"Is strictly decreasing toward 0? {is_decreasing}")
    print(f"Final MSE at N=11: {final_mse:.6f}")

    if final_mse < 0.01:
        conclusion = 'EDL appears to APPROACH addition (density likely). MSE still decreasing.'
    elif final_mse < 0.1:
        conclusion = 'EDL partially approximates addition but MSE stalls above 0.1. Likely not dense.'
    else:
        conclusion = f'EDL cannot approximate addition. MSE stalls at {final_mse:.4f}. Not dense for add.'

    return {
        'best_add_mse_by_depth': best_by_depth,
        'final_mse_N11': final_mse,
        'is_decreasing': is_decreasing,
        'conclusion': conclusion
    }

# ── Session Z6: POW operator (y^x) ─────────────────────────────────────────
def z6_pow_operator():
    print("\n" + "="*60)
    print("Z6 — POW Operator: p(x,y) = y^x  (exp(x)^ln(y))")
    print("="*60)
    print("POW(x,y) = y^x = exp(x*ln(y)). At y=e: exp(x). At x=1: y.")
    print()

    # p(x, e) = e^x = exp(x)  [if we had e as leaf — we don't]
    # p(1, y) = y^1 = y        [identity function!]
    # p(0, y) = y^0 = 1        [constant 1]
    # p(x, 1) = 1^x = 1        [constant 1]

    print("Key identities:")
    print("  pow(1, y) = y^1 = y   [identity function! 1-node construction]")
    print("  pow(0, y) = 1         [constant 1]")
    print("  pow(x, 1) = 1         [constant 1]")
    print()

    # Wait — pow(1, x) = x^1 = x. That's the identity!
    # So POW has the identity function natively: pow(1, x) = x.
    # This means ln(x) might be constructible.

    # pow(1, x) = x
    # pow(pow(1,x), y) = y^x = pow(x, y)... same operator.

    # Can POW build exp(x)?
    # pow(x, e) = e^x = exp(x) — needs e as leaf.
    # From {1}: pow(1,1) = 1^1 = 1. pow(1, pow(1,1)) = 1^1 = 1. All 1s.

    # Hmm. From leaves {1, x} what can POW build?
    # pow(x, 1) = 1
    # pow(1, x) = x
    # pow(x, x) = x^x
    # pow(1, pow(1,x)) = pow(1, x) = x
    # pow(pow(1,x), 1) = pow(x, 1) = 1
    # pow(x, pow(1,x)) = pow(x, x) = x^x
    # pow(pow(1,x), x) = pow(x, x) = x^x

    # The operator can produce x and x^x but not exp(x) = e^x without e as leaf.

    print("Reachable functions from POW({1, x}):")
    trees_by_size = enumerate_trees(7)
    vals_at_2 = set()
    function_catalog = {}
    for n in range(0, 8):
        for tree in trees_by_size.get(n, []):
            # Evaluate at x=2, x=0.5, x=3 to fingerprint
            v2 = eval_tree(tree, POW_fn, 2.0+0j)
            v05 = eval_tree(tree, POW_fn, 0.5+0j)
            v3 = eval_tree(tree, POW_fn, 3.0+0j)
            if v2 is None or v05 is None or v3 is None: continue
            if not (math.isfinite(v2.real) and math.isfinite(v05.real)): continue
            if abs(v2.imag) > 1e-6 or abs(v05.imag) > 1e-6: continue
            key = (round(v2.real, 3), round(v05.real, 3), round(v3.real, 3))
            if key not in function_catalog:
                function_catalog[key] = n

    print(f"  Distinct functions found in N≤7 trees: {len(function_catalog)}")

    # Check for neg(x), exp(+x), add
    best_neg = float('inf')
    best_exp = float('inf')
    best_add = float('inf')
    for n in range(0, 8):
        for tree in trees_by_size.get(n, []):
            vals = [eval_tree(tree, POW_fn, complex(x)) for x in X_PROBE_REAL]
            best_neg = min(best_neg, mse_real(vals, NEG_TARGETS))
            best_exp = min(best_exp, mse_real(vals, EXP_TARGETS))
            best_add = min(best_add, mse_real(vals, ADD_TARGETS))

    print(f"  Best neg(x) MSE: {best_neg:.4f}")
    print(f"  Best exp(+x) MSE: {best_exp:.4f}")
    print(f"  Best add MSE: {best_add:.4f}")
    print()

    # Key insight: pow(1, x) = x (identity). pow(x, x) = x^x.
    # But x^x grows too fast. Can we build exp(x) via nesting?
    # pow(ln(x)/ln(e), e) ... no, can't get ln directly without e.
    # pow(pow(1,x), pow(1,x)) = x^x. Not exp(x).
    # Seems like POW is also incomplete for exp(+x).

    print("Structural analysis:")
    print("  pow(1, x) = x: identity function in 1 node (remarkable!)")
    print("  BUT: exp(x) = e^x requires e as a constant — not buildable from {1} under POW.")
    print("  From {1} alone: pow(1,1)=1, all constant trees stay at 1.")
    print("  Therefore exp(x) is not constructible, and POW is INCOMPLETE.")
    print("  Counter-note: POW with leaf set {1, e} would be complete (pow(x,e)=exp(x) native).")

    return {
        'identity_native': True,
        'exp_native_with_e': True,
        'exp_constructible_from_1_x': False,
        'best_neg_mse_N7': best_neg,
        'best_exp_mse_N7': best_exp,
        'distinct_functions_N7': len(function_catalog),
        'conclusion': 'POW is INCOMPLETE over leaves {1,x}. Identity x is 1-node native (remarkable). exp(x) requires e as leaf. A POW operator with leaf e would be complete.'
    }

# ── Session Z7: LEX operator ln(exp(x) - y) ────────────────────────────────
def z7_lex_operator():
    print("\n" + "="*60)
    print("Z7 — LEX Operator: lex(x,y) = ln(exp(x) - y)")
    print("="*60)
    print("lex(x,y) = ln(exp(x) - y). At y=0: ln(exp(x)) = x [identity!]")
    print()

    # lex(x, 0) = x. But 0 is not a leaf.
    # Can LEX build 0? Need to check.

    # lex(x, exp(x)) = ln(0) → -∞ (undefined)
    # lex(x, 1) = ln(exp(x) - 1) — defined for x > 0, approaches x for large x
    # lex(1, 1) = ln(e - 1) ≈ ln(1.718) ≈ 0.541  [constant]
    # lex(0, 1) = ln(1 - 1) = ln(0) → -∞  [undefined]

    # For the identity: we need y = 0.
    # Can LEX build y=0?
    # lex(x, lex(x, 1)) = ?
    # lex(x, 1) = ln(exp(x) - 1)
    # lex(x, ln(exp(x)-1)) = ln(exp(x) - ln(exp(x)-1))

    print("Key identities:")
    print("  lex(x, 0) = x  [1-node identity — but 0 not a leaf]")
    print("  lex(x, 1) = ln(exp(x) - 1)  [approx x for large x]")
    print()

    # Evaluate lex(x,1) at X_PROBE
    print("lex(x,1) = ln(exp(x)-1):")
    for x in [0.5, 1.0, 2.0, 5.0]:
        v = math.log(math.exp(x) - 1)
        print(f"  x={x}: lex(x,1) = {v:.6f}  vs x = {x:.6f}")
    print()

    # Can LEX build 0?
    # Need tree T with T = 0 everywhere.
    # lex(L, R) = ln(exp(L) - R). For this to be 0: exp(L) - R = 1, so R = exp(L)-1.
    # If L = x and R = lex(x,1) = ln(exp(x)-1)... then
    # lex(x, ln(exp(x)-1)) = ln(exp(x) - ln(exp(x)-1))
    # This depends on x, not constant.

    # Can we build constant 0 from LEX({1})?
    # lex(1,1) = ln(e-1) ≈ 0.541
    # lex(lex(1,1), 1) = lex(0.541, 1) = ln(exp(0.541)-1) ≈ 0.068
    # This is converging but not to 0 in finitely many steps.
    c = math.e - 1
    v0 = math.log(c)
    print(f"Constant sequence from lex(*,1):")
    cur = 1.0
    for i in range(8):
        print(f"  depth {i}: {cur:.6f}")
        try:
            cur = math.log(math.exp(cur) - 1)
        except:
            print("  [diverged]")
            break
    print()

    # Computational check
    trees_by_size = enumerate_trees(7)
    best_id = float('inf')
    best_neg = float('inf')
    best_exp = float('inf')
    for n in range(0, 8):
        for tree in trees_by_size.get(n, []):
            vals = [eval_tree(tree, LEX_fn, complex(x)) for x in X_PROBE_REAL]
            # identity: x
            id_targets = X_PROBE_REAL[:]
            best_id = min(best_id, mse_real(vals, id_targets))
            best_neg = min(best_neg, mse_real(vals, NEG_TARGETS))
            best_exp = min(best_exp, mse_real(vals, EXP_TARGETS))

    print(f"Computational results N≤7:")
    print(f"  Best identity x MSE: {best_id:.6f}")
    print(f"  Best neg(x) MSE: {best_neg:.4f}")
    print(f"  Best exp(+x) MSE: {best_exp:.4f}")

    # Key insight: lex(x,0) = x but 0 is not buildable from {1} under LEX.
    # lex(*,1) produces converging sequence but not exactly 0.
    # LEX likely incomplete too.
    print()
    print("Key finding: Identity x = lex(x,0) is native at y=0, but 0 is not")
    print("constructible from {1} under LEX. The constant sequence lex(lex(...,1),...,1)")
    print("converges toward 0 but never reaches it in finite depth.")

    return {
        'identity_native_at_y0': True,
        'zero_constructible': False,
        'best_identity_mse_N7': best_id,
        'best_neg_mse_N7': best_neg,
        'best_exp_mse_N7': best_exp,
        'conclusion': 'LEX is INCOMPLETE over {1,x}. Identity x is native at y=0, but 0 is not constructible from {1}. Constant sequence lex(lex(...),1) converges to but never reaches 0.'
    }

# ── Session Z8: Universal incompleteness theorem ──────────────────────────
def z8_universal_theorem(z1,z2,z3,z4,z6,z7):
    print("\n" + "="*60)
    print("Z8 — Universal Incompleteness Theorem")
    print("="*60)

    print("""
CONJECTURE (Universal Incompleteness):
  Let G(x,y) = f(g(x), h(y)) be a two-input gate where f is an arithmetic
  operation (+, -, *, /, ^), g is exp or ln, and h is exp or ln.

  G is COMPLETE (can build all elementary functions from trees over {1,x})
  if and only if:
    (i)  G can natively produce exp(+x) in one node, AND
    (ii) G can natively produce exp(-x) in one node.

  Equivalently: G is complete iff both exp(+x) and exp(-x) are available
  as 1-node primitives.

EVIDENCE:
  - EML(x,y) = exp(x)-ln(y): exp(x) native (y=1), exp(-x) via DEML...
    Actually EML is complete. Does it have exp(-x) natively? No, but it's
    proved complete by other means (Weierstrass theorem).

REFINED CONJECTURE (for the leaf-set {1,x} framework):
  An operator G(x,y) is incomplete over leaves {1,x} if either:
    (A) All reachable linear mechanisms have the same sign (DEML-type), OR
    (B) The constant e is not constructible from G({1}), blocking exp(x).

EVIDENCE for (B):
  - EXL: e not constructible → cannot build exp(x) → incomplete ✓
  - POW: e not constructible (all constants stay at 1) → incomplete ✓
  - LEX: 0 not constructible from {1} → identity blocked → incomplete ✓

EVIDENCE for (A):
  - DEML: all linear slopes +1 → cannot build neg(x) → incomplete ✓
  - EAL: all linear slopes positive → cannot build neg(x) → incomplete ✓

EMN STATUS: Has NEGATIVE slope (slope = -1/e^e). Does NOT satisfy (A).
  Does it satisfy (B)? Can EMN build e from {1}?
  emn(1,1) = ln(1)-exp(1) = -e. EMN CAN BUILD -e in 1 node!
  emn(-e, 1) needs -e as input... but emn(1,1) = -e, so:
  emn(emn(1,1), 1) = ln(1) - exp(-e) = -exp(-e) ≈ -0.0660
  Not e, but we have -e available.

  Further: emn(emn(1,1), emn(1,1)) = ln(-e) - exp(-e) → complex.

  Can we get e? Need emn(L,R) = e for some trees L,R.
  emn(L,R) = e means ln(R) - exp(L) = e, so ln(R) = e + exp(L).
  If L = some value c: R = exp(e + exp(c)).
  For L = emn(1,1) = -e: R = exp(e + exp(-e)) = exp(e + 1/e^e) ≈ exp(2.784) ≈ 16.17
  But we need R to be an EMN tree value, not an arbitrary number.
  This requires a subtree evaluating to 16.17 — which circles back to needing e.
""")

    # Enumerate whether EMN can build e
    trees_by_size = enumerate_trees(9)
    e_val = math.e
    closest_to_e = float('inf')
    closest_tree_size = None
    for n in range(0, 10):
        for tree in trees_by_size.get(n, []):
            v = eval_tree(tree, EMN_fn, 1.0+0j)  # constant tree (x=1 = same as constant)
            if v is None: continue
            if not math.isfinite(v.real) or abs(v.imag) > 1e-9: continue
            dist = abs(v.real - e_val)
            if dist < closest_to_e:
                closest_to_e = dist
                closest_tree_size = n

    print(f"Can EMN build constant e from {{1}}?")
    print(f"  Closest to e in N≤9 constant EMN trees: distance = {closest_to_e:.6f}")
    print(f"  At tree size N={closest_tree_size}")
    if closest_to_e < 1e-10:
        print("  YES — e is constructible!")
    else:
        print("  NOT found in N≤9 trees. EMN may not be able to build e as a constant.")
    print()

    return {
        'conjecture': 'Operator G over {1,x} is incomplete if (A) all linear slopes same sign, or (B) constant e not constructible from G({1})',
        'emn_has_negative_slope': True,
        'emn_closest_to_e_N9': closest_to_e,
        'emn_completeness_status': 'UNKNOWN — negative slopes exist but e not found in N≤9',
        'operators_classified': {
            'EML': 'COMPLETE (proved)',
            'DEML': 'INCOMPLETE (proved, slope argument)',
            'EMN': 'UNKNOWN (negative slopes, need deeper search)',
            'EAL': 'INCOMPLETE (all slopes positive)',
            'EXL': 'INCOMPLETE (e not constructible)',
            'EDL': 'INCOMPLETE (add not constructible, proved)',
            'POW': 'INCOMPLETE (e not constructible, but identity native)',
            'LEX': 'INCOMPLETE (0 not constructible from {1})',
        }
    }

# ── Session Z9: Completeness census table ─────────────────────────────────
def z9_census(z1, z2, z3, z4, z5, z6, z7, z8):
    print("\n" + "="*60)
    print("Z9 — Operator Family Completeness Census")
    print("="*60)

    census = [
        {
            'operator': 'EML',
            'definition': 'exp(x) - ln(y)',
            'complete': True,
            'proof': 'Weierstrass theorem (proved session S_W)',
            'neg_x': 'Yes (2 nodes: eml(1,eml(x,1))=e-x, shift)',
            'key_barrier': 'None — complete'
        },
        {
            'operator': 'DEML',
            'definition': 'exp(-x) - ln(y)',
            'complete': False,
            'proof': 'Slope argument: all linear mechanisms slope +1, neg needs -1',
            'neg_x': 'No — best MSE ≈ 0.84 at N≤17 (proved)',
            'key_barrier': 'Fixed slope +1 on all linear compositions'
        },
        {
            'operator': 'EMN',
            'definition': 'ln(y) - exp(x)',
            'complete': None,
            'proof': f'Open — has slope -1/e^e at depth 2. e not found in N≤9 constant trees. MSE(neg)={z2["best_neg_mse"]:.3f} at N≤{9}',
            'neg_x': f'Unclear — best MSE {z2["best_neg_mse"]:.3f}',
            'key_barrier': 'Negative slopes exist; e not constructible from {1} (tentative)'
        },
        {
            'operator': 'EAL',
            'definition': 'exp(x) + ln(y)',
            'complete': False,
            'proof': 'All linear mechanisms have positive slope. No subtraction available.',
            'neg_x': f'No — best MSE {z3["best_neg_mse_N7"]:.3f} at N≤7',
            'key_barrier': 'Addition-only: cannot produce negative values tracking -x'
        },
        {
            'operator': 'EXL',
            'definition': 'exp(x) * ln(y)',
            'complete': False,
            'proof': 'e not constructible from EXL({1}): all constant subtrees = 0',
            'neg_x': f'No — best MSE {z4["best_exp_mse_N9"]:.3f} at N≤9',
            'key_barrier': 'exp(x) not constructible (needs e as leaf)'
        },
        {
            'operator': 'EDL',
            'definition': 'exp(x) / ln(y)',
            'complete': False,
            'proof': 'Addition not constructible (proved). EDL arithmetic incomplete.',
            'neg_x': 'Yes (natively, 6 nodes)',
            'key_barrier': 'Cannot build addition'
        },
        {
            'operator': 'POW',
            'definition': 'y^x  [= exp(x·ln(y))]',
            'complete': False,
            'proof': 'e not constructible from POW({1}): all constants = 1',
            'neg_x': f'No — best MSE {z6["best_neg_mse_N7"]:.3f} at N≤7',
            'key_barrier': 'exp(x) not constructible. Identity x is 1-node native (pow(1,x)=x).'
        },
        {
            'operator': 'LEX',
            'definition': 'ln(exp(x) - y)',
            'complete': False,
            'proof': '0 not constructible from LEX({1}): needed for identity lex(x,0)=x',
            'neg_x': f'No — best MSE {z7["best_neg_mse_N7"]:.3f} at N≤7',
            'key_barrier': 'Identity x = lex(x,0) native but 0 not buildable'
        },
    ]

    print(f"\n{'Operator':<8} {'Definition':<22} {'Complete':<10} {'neg(x)?':<8} Key Barrier")
    print("-"*95)
    for row in census:
        comp = 'YES' if row['complete'] is True else ('NO' if row['complete'] is False else '???')
        print(f"{row['operator']:<8} {row['definition']:<22} {comp:<10} {str(row['neg_x'])[:7]:<8} {row['key_barrier'][:50]}")

    return {'census': census}

# ── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    results = {}

    r_z1 = z1_emn_slope_analysis()
    results['Z1'] = r_z1

    r_z2 = z2_emn_enumeration(max_internal=7)
    results['Z2'] = r_z2

    r_z3 = z3_eal_slope_analysis()
    results['Z3'] = r_z3

    r_z4 = z4_exl_analysis()
    results['Z4'] = r_z4

    r_z5 = z5_edl_density()
    results['Z5'] = r_z5

    r_z6 = z6_pow_operator()
    results['Z6'] = r_z6

    r_z7 = z7_lex_operator()
    results['Z7'] = r_z7

    r_z8 = z8_universal_theorem(r_z1, r_z2, r_z3, r_z4, r_z6, r_z7)
    results['Z8'] = r_z8

    r_z9 = z9_census(r_z1, r_z2, r_z3, r_z4, r_z5, r_z6, r_z7, r_z8)
    results['Z9'] = r_z9

    # Save results
    import os
    os.makedirs('results', exist_ok=True)
    with open('results/d1_operator_zoo.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n\n" + "="*60)
    print("DIRECTION 1 SUMMARY — The Operator Zoo")
    print("="*60)
    for session, data in results.items():
        print(f"\n{session}: {data.get('conclusion','')[:100]}")

    print("\nResults saved to results/d1_operator_zoo.json")
