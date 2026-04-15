"""
demo_sin_best.py  --  BEST.sin(x) and BEST.cos(x) demo.

Run:
    cd D:/monogate
    python python/notebooks/demo_sin_best.py

Shows:
  1. BEST routing table — what each operation costs and why.
  2. sin(x) and cos(x) computed via Taylor series using BEST operators.
  3. Accuracy table at 11 points in [-pi, pi].
  4. Node count comparison: BEST vs all-EML at multiple precisions.
  5. Spot demo — print the big tree explicitly for sin(pi/6) = 0.5.
"""

import math
import statistics

from monogate.core import (
    BEST,
    pow_exl, div_edl,
    add_eml, sub_eml,
)

SEP = "=" * 60


# ── Helper: factorial ─────────────────────────────────────────────────────────

def _fact(n: int) -> int:
    f = 1
    for i in range(2, n + 1):
        f *= i
    return f


# ── Taylor sin/cos via BEST operators ─────────────────────────────────────────

def sin_best(x: float, terms: int = 8) -> float:
    """
    sin(x) via Taylor series using BEST operator routing.

      sin(x) = x - x^3/3! + x^5/5! - x^7/7! + ...

    Each power x^(2k+1) is computed with pow_exl (3 nodes — best known).
    Division by factorial uses Python division (1 node conceptually — div_edl
    costs 1 node for positive arguments, but the factorials are constants so
    native division is semantically equivalent and avoids the ln_edl dead zone
    near x=1 in the factorial argument).
    Additive combination uses sub_eml / add_eml (5 / 11 nodes — EML only).

    Node count per non-first term:  3 (pow) + 1 (div) + 5 (sub) = 9 nodes.
    Total for 8 terms: 1 (leaf x) + 7 × 9 = 64 nodes.
    All-EML baseline: 15 (pow) + 15 (div) + 5 (sub) = 35 per term → 245 nodes.
    """
    if x == 0.0:
        return 0.0
    ax = abs(x)
    sx = 1 if x > 0 else -1
    result = x                                  # term 0: x (1 leaf)
    for k in range(1, terms):
        power = 2 * k + 1
        # pow_exl(ax, power) — 3 nodes, best known
        xp = sx * pow_exl(complex(ax), complex(power)).real
        term = xp / _fact(power)                # / (2k+1)! — 1 node (div_edl for +ve)
        result += (-1) ** k * term              # sub_eml or add_eml — 5 or 11 nodes
    return result


def cos_best(x: float, terms: int = 8) -> float:
    """
    cos(x) via Taylor series using BEST operator routing.

      cos(x) = 1 - x^2/2! + x^4/4! - x^6/6! + ...

    Even powers: pow_exl(|x|, 2k) — always positive, 3 nodes each.
    Node count for 8 terms: 1 (const 1) + 7 × 9 = 64 nodes.
    """
    if x == 0.0:
        return 1.0
    ax = abs(x)
    result = 1.0                                # term 0: 1
    for k in range(1, terms):
        power = 2 * k
        xp = pow_exl(complex(ax), complex(power)).real   # always positive for even power
        term = xp / _fact(power)
        result += (-1) ** k * term
    return result


# ── Demo ──────────────────────────────────────────────────────────────────────

def demo_routing_table():
    print(f"\n{'BEST OPERATOR ROUTING TABLE':^60}")
    print(SEP)
    print("""
  BEST routes each operation to the cheapest known operator.
  Source: arXiv:2603.21852 extended with EDL/EXL derivations.
""")
    BEST.info()
    print()
    BEST.benchmark(targets=[])   # node counts + accuracy, no neural regression


def demo_sin_accuracy():
    print(f"\n{'SIN(X) AND COS(X) VIA BEST TAYLOR SERIES':^60}")
    print(SEP)
    print("""
  8-term Taylor expansion.  pow_exl (3 nodes) handles each power.
  Node count: 63 nodes (BEST) vs 245 nodes (all-EML).
""")

    xs = [x * math.pi / 5 for x in range(-5, 6)]  # -pi to pi in steps of pi/5

    print(f"  {'x/pi':>6}  {'sin(x)':>12}  {'BEST':>12}  {'|err|':>10}  "
          f"{'cos(x)':>12}  {'BEST':>12}  {'|err|':>10}")
    print(f"  {'-'*6}  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*10}")

    sin_errs, cos_errs = [], []
    for x in xs:
        sr = math.sin(x)
        cr = math.cos(x)
        sb = sin_best(x)
        cb = cos_best(x)
        se = abs(sb - sr)
        ce = abs(cb - cr)
        sin_errs.append(se)
        cos_errs.append(ce)
        print(f"  {x/math.pi:>6.2f}  {sr:>12.8f}  {sb:>12.8f}  {se:>10.2e}  "
              f"{cr:>12.8f}  {cb:>12.8f}  {ce:>10.2e}")

    print(f"\n  sin — max err: {max(sin_errs):.2e}  mean: {statistics.mean(sin_errs):.2e}")
    print(f"  cos — max err: {max(cos_errs):.2e}  mean: {statistics.mean(cos_errs):.2e}")


def demo_node_pareto():
    print(f"\n{'NODE COUNT vs ACCURACY (TAYLOR TERMS)':^60}")
    print(SEP)
    print("""
  How many Taylor terms (and operator nodes) are needed to hit
  each accuracy threshold?  Both BEST routing and all-EML baseline.
""")

    print(f"  {'terms':>5}  {'nodes_BEST':>11}  {'nodes_EML':>10}  {'saving':>8}  {'max_err':>10}")
    print(f"  {'-'*5}  {'-'*11}  {'-'*10}  {'-'*8}  {'-'*10}")

    xs = [x * math.pi / 100 for x in range(-100, 101) if x != 0]

    for n in [2, 4, 6, 8, 10, 12]:
        errs = [abs(sin_best(x, n) - math.sin(x)) for x in xs]
        max_err = max(errs)
        # Node counts: 1 leaf + (n-1) × (3 pow + 1 div + 5 sub)
        nb = 1 + (n - 1) * 9   # BEST
        ne = 1 + (n - 1) * 35  # EML-only (pow_eml=15 + div_eml=15 + sub=5)
        saving = ne - nb
        print(f"  {n:>5}  {nb:>11}  {ne:>10}  {saving:>8}  {max_err:>10.3e}")

    print(f"""
  BEST routing saves 74% of nodes at every term count because:
    pow_exl (3n)  replaces  pow_eml (15n)  => -12n per term
    div_edl (1n)  replaces  div_eml (15n)  => -14n per term
    sub_eml (5n)  is the same in both      =>   0n difference

  The additive steps are the irreducible EML-only cost.
""")


def demo_explicit_tree():
    print(f"\n{'EXPLICIT TREE TRACE: sin(pi/6) = 0.5':^60}")
    print(SEP)
    x = math.pi / 6
    print(f"\n  Target: sin({x:.6f}) = sin(pi/6) = 0.5")
    print(f"\n  Computing 4-term Taylor (27 nodes BEST):")

    ax, sx = abs(x), 1
    result = x
    print(f"\n  Term 0:  x                    = {x:.10f}")

    for k in range(1, 4):
        power = 2 * k + 1
        fact  = _fact(power)
        xp_raw = pow_exl(complex(ax), complex(power))
        xp  = sx * xp_raw.real
        term = xp / fact
        sign = (-1) ** k
        contrib = sign * term
        result += contrib
        print(f"  Term {k}:  (-1)^{k} * pow_exl({ax:.4f},{power}) / {power}!")
        print(f"           = {sign:+d} × {xp:.10f} / {fact}")
        print(f"           = {contrib:+.10f}")
        print(f"         Running sum: {result:.10f}")

    ref = math.sin(x)
    print(f"\n  Result:   sin_best(pi/6) = {result:.10f}")
    print(f"  Reference:  math.sin(pi/6) = {ref:.10f}")
    print(f"  Error:                      {abs(result - ref):.2e}")
    print(f"\n  4-term Taylor (27 nodes BEST) is already accurate to {abs(result-ref):.0e}.")
    print(f"  8-term Taylor (63 nodes BEST) achieves < 7.7e-7 error over all x in [-pi,pi].")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(SEP)
    print(f"  demo_sin_best.py  --  sin(x) via BEST operator routing")
    print(SEP)

    demo_routing_table()
    demo_sin_accuracy()
    demo_node_pareto()
    demo_explicit_tree()

    print(f"\n{'='*60}")
    print(f"  Summary")
    print(f"{'='*60}")
    print(f"""
  sin(x) and cos(x) via Taylor series using BEST routing:

    8 terms:  63 nodes  (vs 245 EML-only)  max err < 7.7e-7
   12 terms:  99 nodes  (vs 385 EML-only)  max err < 1.8e-13

  Key operators:
    pow_exl(x, n) = exl(exl(exl(0, n), x), e)  — 3 nodes  (EXL)
    div_edl(x, y) = edl(ln(x), exp(y))          — 1 node   (EDL)
    sub_eml(x, y) = eml(ln(x), exp(y))          — 5 nodes  (EML, only complete for subtraction)

  BEST routing saves 74% of nodes vs all-EML across every
  accuracy level.  The additive steps (sub/add EML) are the
  irreducible cost — no cousin operator supports a ± b over reals.

  This is a numerical construction (Taylor approximation),
  not a closed-form identity.  A finite exact EML expression
  for sin(x) remains an open problem.
""")
