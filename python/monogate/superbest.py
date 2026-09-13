"""
SuperBEST Router — per-operation node counts for arithmetic primitives
The fewest-node construction we know for each arithmetic primitive, and routing by those counts.

Author: Monogate Research
Version: v5.3 table, recounted in F16 (2026-09-13)

Headlines (monogate.org/superbest renders the same figures):
  - Positive domain (10 ops: exp, ln, neg, add, sub, mul, div, recip, pow, sqrt):
        15n / 79.5% savings vs 73n naive, counted in F16
  - General domain (6 ops: exp, mul, div, neg, add, sub):
        18n / 66.7% savings vs 54n naive, counted in F16
  - The same ten positive-domain ops with ln x = EXL(0, x) counted as ONE node:
        14n / 80.8% (SUPERBEST_V53_POS_TOTAL). EXL, exp(x)*ln(y), is a census operator outside
        F16. monogate-lean's ModelAudit.lean states this sum (superbest_v53_positive_total).

"F16" means the sixteen binary operators on monogate.org/framework, F1..F16 of monogate-lean's
MonogateEML/AddLowerBound.lean:
  F1  EML        exp(x) - ln(y)          F9   LEdiv   x - ln(y)
  F2  EMLn       exp(x) - ln(-y)         F10  LEdivn  x - ln(-y)
  F3  DEML       exp(-x) - ln(y)         F11  LEAd    ln(exp(x) + y)
  F4  DEMLn      exp(-x) - ln(-y)        F12  LEAdn   ln(exp(x) - y)
  F5  EMLswap    exp(y) - ln(x)          F13          exp(x * ln(y)) = y^x
  F6  EMLnswap   exp(-y) - ln(x)         F14          exp(x + ln(y)) = y * e^x
  F7  EMLswapn   exp(y) - ln(-x)         F15          exp(x + ln(-y))
  F8  EMLnswapn  exp(-y) - ln(-x)        F16fn        exp(ln(x) + ln(y)) = x * y
A tree is defined at a point only where every log argument is positive (the negated argument for
F2, F4, F7, F8, F10 and F15) and both F16fn arguments are positive.

F16 recount, 2026-09-13 (v5.3 counts in brackets):
  - ln positive      2n [1n]  LEdiv(0, F13(-1, x)). The 1n was EXL(0, x), a census operator.
  - neg, recip, div positive: same counts, now written in F16 (LEdiv(0, EML(x, 1));
                              F13(-1, x); F16fn(x, F13(-1, y))).
  - mul general      3n [3n]  now one tree, LEdiv(0, F13(y, DEML(x, 1))), for all real x, y.
                              The old 3n was a sign-dispatch case split, one circuit per quadrant.
  - div general      8n [3n]  one tree for all x and y != 0 (F16_CONSTRUCTIONS). The old 3n was a
                              sign-dispatch case split, not a tree.
  - recip general    7n [1n]  one tree for x != 0 (row-level; not in the general basket).
  - abs              dropped  no real F16 tree computes |x| over all reals: a tree is real-analytic
                              wherever it is defined, and |x| is not analytic at 0. The old 2n
                              route, sqrt(x^2) through EPL, is defined only for x > 0.
  - ln, sqrt, pow general: no all-reals entry (GENERAL_DOMAIN_GAPS); ln left the general basket.
  - headlines: positive 14n / 80.8% -> 15n / 79.5%; general 16n / 74.2% (8 ops) -> 18n / 66.7% (6 ops).

What backs the figures:
  - python/tests/test_superbest_f16_constructions.py evaluates every construction in
    F16_CONSTRUCTIONS at 30 digits on random points of its domain and checks its node count. These
    are upper bounds.
  - python/benchmarks/superbest_f16/search.py enumerates F16 trees with constant leaves
    0, 1, -1, 2, 1/2 at sample points. It finds no tree with fewer nodes than listed for ln, neg and
    positive div (none with 1), mul general (none with 2), recip general (none with 6) and div
    general (none with 7). That is numerical evidence, not a proof.
  - Lean (monogate-lean) has lower bounds for add, sub, mul and div over all reals (each at least 2
    nodes), and witnesses for exp, mul, pow, recip and sqrt in one node and div in two, on the
    positive domain. No Lean theorem states the F16 totals.
  - NAIVE_COSTS are the library's pure-EML figures, carried unchanged; the recount did not re-derive
    them or check their domains.
"""
from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Headline totals
# ---------------------------------------------------------------------------

# F16 recount (2026-09-13): the headline. Positive domain, 10 ops.
SUPERBEST_F16_POS_OPS = (
    "exp", "ln", "neg", "add", "sub", "mul", "div", "recip", "pow", "sqrt",
)
SUPERBEST_F16_POS_TOTAL = 15
SUPERBEST_F16_POS_NAIVE = 73
SUPERBEST_F16_POS_SAVINGS_PCT = 79.5

# General domain: every op whose F16 tree is valid for all real inputs where the op is defined
# (div needs y != 0). abs and ln left the basket on 2026-09-13; see GENERAL_DOMAIN_GAPS.
SUPERBEST_F16_GEN_OPS = (
    "exp", "mul", "div", "neg", "add", "sub",
)
SUPERBEST_F16_GEN_TOTAL = 18
SUPERBEST_F16_GEN_NAIVE = 54
SUPERBEST_F16_GEN_SAVINGS_PCT = 66.7

# Census count: the ten positive-domain ops with ln x = EXL(0, x) as ONE node (EXL is a census
# operator, not one of the sixteen). ModelAudit.lean states this sum, 1+1+1+1+1+2+2+2+2+1 = 14
# (superbest_v53_positive_total), with its ln witness taken through EXL (ln_is_one_node_via_exl).
SUPERBEST_V53_POS_TOTAL = 14
SUPERBEST_V53_POS_NAIVE = 73
SUPERBEST_V53_POS_SAVINGS_PCT = 80.8
SUPERBEST_V52_POS_TOTAL = SUPERBEST_V53_POS_TOTAL
SUPERBEST_V52_POS_NAIVE = SUPERBEST_V53_POS_NAIVE
SUPERBEST_V52_POS_SAVINGS_PCT = SUPERBEST_V53_POS_SAVINGS_PCT
SUPERBEST_V52_POS_OPS = (
    "exp", "ln", "neg", "add", "sub", "mul", "div", "recip", "pow", "sqrt",
)

# Withdrawn 2026-09-13: the census general basket, 16n vs 62n naive over exp, ln, mul, div, neg,
# add, sub and abs. It counted abs at 2n, which no real tree achieves, ln on x > 0 only, and mul
# and div at 3n from sign-dispatch case splits. The old names now point at the F16 basket.
SUPERBEST_V52_GEN_TOTAL = SUPERBEST_F16_GEN_TOTAL
SUPERBEST_V52_GEN_NAIVE = SUPERBEST_F16_GEN_NAIVE
SUPERBEST_V52_GEN_SAVINGS_PCT = SUPERBEST_F16_GEN_SAVINGS_PCT
SUPERBEST_V52_GEN_OPS = SUPERBEST_F16_GEN_OPS


# ---------------------------------------------------------------------------
# Per-op node costs
# ---------------------------------------------------------------------------

# Naive pure-EML tree costs (no routing), carried unchanged from v5.2:
#   sum over SUPERBEST_F16_POS_OPS = 73
#   sum over SUPERBEST_F16_GEN_OPS = 54
NAIVE_COSTS: dict[str, int] = {
    "exp": 1,
    "ln": 3,
    "mul": 13,
    "div": 15,
    "add": 11,
    "sub": 5,
    "neg": 9,
    "recip": 5,
    "sqrt": 8,
    "pow": 3,
    "abs": 5,
    "sin": 13,
    "cos": 13,
}

# Positive domain, counted in F16. Sum over SUPERBEST_F16_POS_OPS = 15.
SUPERBEST_COSTS_POS: dict[str, int] = {
    "exp": 1,
    "ln": 2,
    "neg": 2,
    "add": 2,
    "sub": 2,
    "mul": 1,
    "div": 2,
    "recip": 1,
    "pow": 1,
    "sqrt": 1,
    "sin": 1,   # complex path Im(eml(ix, 1)); not a real F16 tree
    "cos": 1,   # complex path Re(eml(ix, 1)); not a real F16 tree
}

# The census count: ln x = EXL(0, x) as one node. Sum over the ten ops = 14.
SUPERBEST_COSTS_POS_WITH_EXL: dict[str, int] = {**SUPERBEST_COSTS_POS, "ln": 1}

# General domain, counted in F16. Sum over SUPERBEST_F16_GEN_OPS = 18.
SUPERBEST_COSTS_GEN: dict[str, int] = {
    "exp": 1,
    "neg": 2,
    "add": 2,
    "sub": 2,
    "mul": 3,
    "div": 8,
    "recip": 7,  # row-level; not in the general basket
    "sin": 1,
    "cos": 1,
}

# Ops with no general-domain F16 entry, and why. superbest_cost(..., positive_domain=False) raises.
GENERAL_DOMAIN_GAPS: dict[str, str] = {
    "abs": "no real F16 tree computes |x| over all reals: a tree is real-analytic wherever it is "
           "defined, and |x| is not analytic at 0",
    "ln": "ln(x) has no real value for x <= 0; the positive-domain entry is the only one",
    "sqrt": "sqrt(x) has no real value for x < 0, and no F16 tree equals it on [0, inf): a tree "
            "defined at 0 is analytic there, and sqrt is not",
    "pow": "x^n has no real value for x < 0 unless n is an integer; F13(n, x) covers x > 0",
}

# Legacy unified table (pre-v5.2 callers) — points at positive-domain costs.
SUPERBEST_COSTS_V5: dict[str, int] = dict(SUPERBEST_COSTS_POS)


# ---------------------------------------------------------------------------
# F16 constructions: (tree, domain). Leaves are x, y, n and numeric constants.
# python/tests/test_superbest_f16_constructions.py evaluates each one and checks its node count.
# ---------------------------------------------------------------------------

_P_X = "F13(-1, LEdiv(0, F13(x, DEML(x, 1))))"   # 1/x^2 for x != 0 (4 nodes)
_P_Y = "F13(-1, LEdiv(0, F13(y, DEML(y, 1))))"   # 1/y^2 for y != 0 (4 nodes)

F16_CONSTRUCTIONS: dict[str, dict[str, tuple[str, str]]] = {
    "positive": {
        "exp": ("EML(x, 1)", "all x"),
        "ln": ("LEdiv(0, F13(-1, x))", "x > 0"),
        "neg": ("LEdiv(0, EML(x, 1))", "all x"),
        "add": ("LEdiv(x, DEML(y, 1))", "all x, y"),
        "sub": ("LEdiv(x, EML(y, 1))", "all x, y"),
        "mul": ("F16fn(x, y)", "x, y > 0"),
        "div": ("F16fn(x, F13(-1, y))", "x, y > 0"),
        "recip": ("F13(-1, x)", "x > 0"),
        "pow": ("F13(n, x)", "x > 0"),
        "sqrt": ("F13(1/2, x)", "x > 0"),
    },
    "general": {
        "exp": ("EML(x, 1)", "all x"),
        "neg": ("LEdiv(0, EML(x, 1))", "all x"),
        "add": ("LEdiv(x, DEML(y, 1))", "all x, y"),
        "sub": ("LEdiv(x, EML(y, 1))", "all x, y"),
        # -ln(exp(-x*y)) = x*y
        "mul": ("LEdiv(0, F13(y, DEML(x, 1)))", "all x, y"),
        # -ln(exp(-x/x^2)) = 1/x
        "recip": (f"LEdiv(0, F13({_P_X}, DEML(x, 1)))", "x != 0"),
        # -ln(exp(-x * y/y^2)) = x/y
        "div": (f"LEdiv(0, F13(x, F13({_P_Y}, DEML(y, 1))))", "all x, y != 0"),
    },
}

_OPERATORS = {
    "exp": "EML (F1)", "ln": "LEdiv+F13", "neg": "LEdiv+EML", "add": "LEdiv+DEML",
    "sub": "LEdiv+EML", "mul": "F16fn", "div": "F16fn+F13", "recip": "F13", "pow": "F13",
    "sqrt": "F13",
}

# Display metadata; the counts live in the cost dicts above.
SUPERBEST_TABLE: dict[str, dict] = {}
for _op, (_expr, _dom) in F16_CONSTRUCTIONS["positive"].items():
    _entry = {"operator": _OPERATORS[_op], "nodes": SUPERBEST_COSTS_POS[_op], "domain": _dom,
              "construction": _expr}
    _gen = F16_CONSTRUCTIONS["general"].get(_op)
    if _gen is not None and _gen[0] != _expr:
        _entry.update(nodes_gen=SUPERBEST_COSTS_GEN[_op], domain_gen=_gen[1], construction_gen=_gen[0])
    SUPERBEST_TABLE[_op] = _entry
SUPERBEST_TABLE["ln"]["construction_with_exl"] = "EXL(0, x): 1 node, with a census operator outside F16"
SUPERBEST_TABLE["sin"] = {"operator": "EML (complex)", "nodes": 1, "domain": "all x",
                          "construction": "Im(eml(i*x, 1))"}
SUPERBEST_TABLE["cos"] = {"operator": "EML (complex)", "nodes": 1, "domain": "all x",
                          "construction": "Re(eml(i*x, 1))"}
del _op, _expr, _dom, _entry, _gen


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def superbest_cost(op: str, positive_domain: bool = True, count_exl: bool = False) -> int:
    """Return the node count for an operation.

    Args:
        op: Operation name.
        positive_domain: True for the positive-domain table, False for the all-reals table.
        count_exl: Positive domain only. Count ln x = EXL(0, x) as one node (the census count).

    Raises:
        ValueError: ``positive_domain`` is False and ``op`` has no general-domain F16 entry.
    """
    if positive_domain:
        table = SUPERBEST_COSTS_POS_WITH_EXL if count_exl else SUPERBEST_COSTS_POS
    else:
        if op in GENERAL_DOMAIN_GAPS:
            raise ValueError(f"{op}: no general-domain F16 entry ({GENERAL_DOMAIN_GAPS[op]})")
        table = SUPERBEST_COSTS_GEN
    return table.get(op, NAIVE_COSTS.get(op, 99))


def predict_cost(op: str, positive_domain: bool = False) -> int:
    """Return the predicted SuperBEST node cost (general domain by default).

    Args:
        op: Operation name.
        positive_domain: If True, use positive-domain costs. Default: False (general).

    Returns:
        Node count under the selected domain.
    """
    return superbest_cost(op, positive_domain=positive_domain)


def superbest_operator(op: str) -> str:
    if op in SUPERBEST_TABLE:
        return SUPERBEST_TABLE[op]["operator"]
    return "unknown"


def superbest_construction(op: str, positive_domain: bool = True) -> str:
    entry = SUPERBEST_TABLE.get(op)
    if not positive_domain and op in GENERAL_DOMAIN_GAPS:
        return f"none over all reals: {GENERAL_DOMAIN_GAPS[op]}"
    if entry is None:
        return "unknown"
    if not positive_domain and "construction_gen" in entry:
        return entry["construction_gen"]
    return entry["construction"]


def savings_vs_naive(op: str, positive_domain: bool = True) -> int:
    return NAIVE_COSTS.get(op, 0) - superbest_cost(op, positive_domain=positive_domain)


def route_expression(ops: list[str], positive_domain: bool = False) -> dict:
    """Route a list of arithmetic operations using the F16 SuperBEST costs.

    Args:
        ops: List of operation names, e.g. ["mul", "add", "exp"].
        positive_domain: If True, use positive-domain costs.

    Returns:
        dict mapping op -> routing info, plus a "__totals__" entry.

    Raises:
        ValueError: general domain and an op in GENERAL_DOMAIN_GAPS.
    """
    result: dict = {}
    total_superbest = 0
    total_naive = 0
    for op in ops:
        sb = predict_cost(op, positive_domain=positive_domain)
        naive = NAIVE_COSTS.get(op, 99)
        total_superbest += sb
        total_naive += naive
        result[op] = {
            "operator": superbest_operator(op),
            "nodes": sb,
            "naive_nodes": naive,
            "savings": naive - sb,
            "construction": superbest_construction(op, positive_domain=positive_domain),
            "domain": "positive" if positive_domain else "general",
        }
    result["__totals__"] = {
        "superbest_nodes": total_superbest,
        "naive_nodes": total_naive,
        "total_savings": total_naive - total_superbest,
        "savings_pct": round((1 - total_superbest / max(total_naive, 1)) * 100, 1),
        "domain_assumption": "positive (x > 0)" if positive_domain else "general (all reals)",
    }
    return result


def rewrite_python_expr(expr: str) -> str:
    """Annotate a Python expression with SuperBEST constructions (demo only)."""
    annotations = []
    if re.search(r"\*(?!\*)", expr):
        annotations.append(f"mul -> {superbest_construction('mul')} (1n pos)")
    if "+" in expr:
        annotations.append(f"add -> {superbest_construction('add')} (2n, all reals)")
    if "-" in expr and "exp" not in expr:
        annotations.append(f"sub -> {superbest_construction('sub')} (2n)")
    if "exp(" in expr or "math.exp" in expr:
        annotations.append(f"exp -> {superbest_construction('exp')} (1n)")
    if "log(" in expr or "math.log" in expr:
        annotations.append(f"ln -> {superbest_construction('ln')} (2n)")
    if "/" in expr:
        annotations.append(f"div -> {superbest_construction('div')} (2n pos)")
    return expr + "  # SuperBEST: " + "; ".join(annotations)


def superbest_summary(positive_domain: bool = False) -> str:
    """Return a human-readable routing table summary, counted in F16.

    Args:
        positive_domain: If True, show the 10-op positive table (15n / 79.5%).
                         If False (default), show the 6-op general table (18n / 66.7%).
    """
    if positive_domain:
        domain_label = "Positive-Domain (x > 0)"
        costs = SUPERBEST_COSTS_POS
        ops = SUPERBEST_F16_POS_OPS
        total_sb = SUPERBEST_F16_POS_TOTAL
        total_naive = SUPERBEST_F16_POS_NAIVE
        savings_pct = SUPERBEST_F16_POS_SAVINGS_PCT
    else:
        domain_label = "General-Domain (all reals)"
        costs = SUPERBEST_COSTS_GEN
        ops = SUPERBEST_F16_GEN_OPS
        total_sb = SUPERBEST_F16_GEN_TOTAL
        total_naive = SUPERBEST_F16_GEN_NAIVE
        savings_pct = SUPERBEST_F16_GEN_SAVINGS_PCT

    headline = f"{total_sb}n / {savings_pct}% savings"
    lines = [
        f"SuperBEST v5.3 Routing Table, counted in F16 - {domain_label}",
        f"Headline: {headline} vs naive {total_naive}n baseline ({len(ops)} ops)",
    ]
    if positive_domain:
        lines.append(
            "Counting ln x = EXL(0, x) as one node (EXL is a census operator, not in F16): "
            f"{SUPERBEST_V53_POS_TOTAL} nodes, {SUPERBEST_V53_POS_SAVINGS_PCT} percent"
        )
    else:
        lines.append("Not in the general basket: " + ", ".join(sorted(GENERAL_DOMAIN_GAPS)) + " (see GENERAL_DOMAIN_GAPS)")
    lines += [
        "=" * 72,
        f"  {'Op':8} {'Nodes':6} {'Naive':6} {'Savings':8} {'Construction':40}",
        "-" * 72,
    ]

    computed_sb = 0
    computed_naive = 0
    for op in ops:
        sb = costs.get(op, 99)
        naive = NAIVE_COSTS.get(op, 0)
        computed_sb += sb
        computed_naive += naive
        constr = superbest_construction(op, positive_domain=positive_domain)
        savings_n = naive - sb
        lines.append(f"  {op:8} {sb:6} {naive:6} {savings_n:+8d} {constr:40}")

    lines.append("-" * 72)
    lines.append(f"  {'TOTAL':8} {computed_sb:6} {computed_naive:6} {computed_naive - computed_sb:+8d}")
    lines.append(
        f"  Savings: {(1 - computed_sb / max(computed_naive, 1)) * 100:.1f}% "
        f"vs naive {computed_naive}n baseline"
    )

    if computed_sb != total_sb or computed_naive != total_naive:
        lines.append(
            f"  WARNING: per-op sum ({computed_sb}n / {computed_naive}n) disagrees with "
            f"declared headline ({total_sb}n / {total_naive}n). "
            "Fix the per-op entries or the headline constants."
        )

    return "\n".join(lines)
