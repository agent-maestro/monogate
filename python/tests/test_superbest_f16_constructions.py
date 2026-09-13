"""The F16 constructions behind monogate.superbest's node counts, evaluated at 30 digits.

Each entry of ``superbest.F16_CONSTRUCTIONS`` is parsed, its node count is compared with the cost
table it backs, and its value is compared with the target at random points of its stated domain.
Semantics are the natural real ones: a tree is defined at a point only where every log argument is
positive (the negated argument for F2, F4, F7, F8, F10 and F15) and both F16fn arguments are
positive. A construction that is undefined anywhere on its domain fails.

This checks upper bounds only. Whether smaller trees exist is a separate, numerical question:
python/benchmarks/superbest_f16/search.py.
"""
from __future__ import annotations

import random
import re

import pytest

mp = pytest.importorskip("mpmath")

from monogate import superbest as sb

mp.mp.dps = 30
REL = mp.mpf(10) ** -20


def _op(name, a, b):
    e, lg = mp.exp, mp.log
    table = {
        "EML": (lambda: b > 0, lambda: e(a) - lg(b)),
        "EMLn": (lambda: b < 0, lambda: e(a) - lg(-b)),
        "DEML": (lambda: b > 0, lambda: e(-a) - lg(b)),
        "DEMLn": (lambda: b < 0, lambda: e(-a) - lg(-b)),
        "EMLswap": (lambda: a > 0, lambda: e(b) - lg(a)),
        "EMLnswap": (lambda: a > 0, lambda: e(-b) - lg(a)),
        "EMLswapn": (lambda: a < 0, lambda: e(b) - lg(-a)),
        "EMLnswapn": (lambda: a < 0, lambda: e(-b) - lg(-a)),
        "LEdiv": (lambda: b > 0, lambda: a - lg(b)),
        "LEdivn": (lambda: b < 0, lambda: a - lg(-b)),
        "LEAd": (lambda: e(a) + b > 0, lambda: lg(e(a) + b)),
        "LEAdn": (lambda: e(a) - b > 0, lambda: lg(e(a) - b)),
        "F13": (lambda: b > 0, lambda: e(a * lg(b))),
        "F14": (lambda: b > 0, lambda: e(a + lg(b))),
        "F15": (lambda: b < 0, lambda: e(a + lg(-b))),
        "F16fn": (lambda: a > 0 and b > 0, lambda: e(lg(a) + lg(b))),
    }
    defined, value = table[name]
    return value() if defined() else None


def _parse(text):
    s = text.replace(" ", "")
    pos = 0

    def expr():
        nonlocal pos
        m = re.match(r"[A-Za-z][A-Za-z0-9]*\(", s[pos:])
        if m:
            name = m.group(0)[:-1]
            pos += len(m.group(0))
            left = expr()
            assert s[pos] == ","
            pos += 1
            right = expr()
            assert s[pos] == ")"
            pos += 1
            return (name, left, right)
        m = re.match(r"-?[0-9]+(/[0-9]+)?|[a-z]", s[pos:])
        assert m, f"cannot parse {s[pos:]!r}"
        pos += len(m.group(0))
        return m.group(0)

    tree = expr()
    assert pos == len(s), f"trailing text in {text!r}"
    return tree


def _nodes(tree):
    return 0 if isinstance(tree, str) else 1 + _nodes(tree[1]) + _nodes(tree[2])


def _eval(tree, env):
    if isinstance(tree, str):
        if tree in env:
            return env[tree]
        if "/" in tree:
            p, q = tree.split("/")
            return mp.mpf(p) / mp.mpf(q)
        return mp.mpf(tree)
    a = _eval(tree[1], env)
    b = _eval(tree[2], env)
    if a is None or b is None:
        return None
    return _op(tree[0], a, b)


TARGETS = {
    "exp": lambda v: mp.exp(v["x"]),
    "ln": lambda v: mp.log(v["x"]),
    "neg": lambda v: -v["x"],
    "add": lambda v: v["x"] + v["y"],
    "sub": lambda v: v["x"] - v["y"],
    "mul": lambda v: v["x"] * v["y"],
    "div": lambda v: v["x"] / v["y"],
    "recip": lambda v: 1 / v["x"],
    "pow": lambda v: v["x"] ** v["n"],
    "sqrt": lambda v: mp.sqrt(v["x"]),
}

_MAGNITUDES = ["1e-3", "0.05", "0.4", "1", "3", "9"]


def _points(domain, n=150, seed=20260913):
    rng = random.Random(seed)

    def real(positive):
        v = mp.mpf(rng.choice(_MAGNITUDES)) * mp.mpf(rng.uniform(0.5, 2.0))
        return v if positive or rng.random() < 0.5 else -v

    zero = mp.mpf(0)
    points = []
    for i in range(n):
        if domain == "all x":
            points.append({"x": zero if i == 0 else real(False)})
        elif domain == "x > 0":
            points.append({"x": real(True), "n": mp.mpf(rng.uniform(-4, 4))})
        elif domain == "x != 0":
            points.append({"x": real(False)})
        elif domain == "all x, y":
            points.append({"x": zero if i % 7 == 0 else real(False), "y": zero if i % 5 == 0 else real(False)})
        elif domain == "x, y > 0":
            points.append({"x": real(True), "y": real(True)})
        elif domain == "all x, y != 0":
            points.append({"x": zero if i % 7 == 0 else real(False), "y": real(False)})
        else:
            raise ValueError(f"unknown domain {domain!r}")
    return points


CASES = [
    (table, op, expr, where)
    for table in ("positive", "general")
    for op, (expr, where) in sb.F16_CONSTRUCTIONS[table].items()
]


@pytest.mark.parametrize("table,op,expr,where", CASES, ids=[f"{t}-{o}" for t, o, _, _ in CASES])
def test_construction_equals_target_on_its_domain_and_matches_the_cost(table, op, expr, where):
    tree = _parse(expr)
    costs = sb.SUPERBEST_COSTS_POS if table == "positive" else sb.SUPERBEST_COSTS_GEN
    assert _nodes(tree) == costs[op], f"{expr} has {_nodes(tree)} nodes, table says {costs[op]}"
    for p in _points(where):
        val = _eval(tree, p)
        assert val is not None, f"{expr} is undefined at {p}"
        ref = TARGETS[op](p)
        assert abs(val - ref) <= REL * max(1, abs(ref)), (expr, p, val, ref)


@pytest.mark.parametrize(
    "expr,where",
    [
        ("F16fn(x, y)", "all x, y"),
        ("F16fn(x, F13(-1, y))", "all x, y != 0"),
        ("F13(-1, x)", "x != 0"),
        ("LEdiv(0, F13(-1, x))", "all x"),
    ],
)
def test_positive_domain_trees_are_undefined_somewhere_on_signed_domains(expr, where):
    # The evaluator must reject a sign-restricted tree; otherwise the test above proves nothing.
    tree = _parse(expr)
    assert any(_eval(tree, p) is None for p in _points(where))


def test_every_basket_op_has_a_construction_and_no_gap_op_has_a_general_cost():
    assert set(sb.SUPERBEST_F16_POS_OPS) <= set(sb.F16_CONSTRUCTIONS["positive"])
    assert set(sb.SUPERBEST_F16_GEN_OPS) <= set(sb.F16_CONSTRUCTIONS["general"])
    for op in sb.GENERAL_DOMAIN_GAPS:
        assert op not in sb.SUPERBEST_COSTS_GEN
        assert op not in sb.SUPERBEST_F16_GEN_OPS
        with pytest.raises(ValueError):
            sb.superbest_cost(op, positive_domain=False)


def _pct(total, naive):
    return round(100 * (1 - total / naive), 1)


def test_headline_totals_follow_from_the_cost_tables():
    pos = sum(sb.SUPERBEST_COSTS_POS[op] for op in sb.SUPERBEST_F16_POS_OPS)
    pos_naive = sum(sb.NAIVE_COSTS[op] for op in sb.SUPERBEST_F16_POS_OPS)
    assert (pos, pos_naive) == (sb.SUPERBEST_F16_POS_TOTAL, sb.SUPERBEST_F16_POS_NAIVE) == (15, 73)
    assert _pct(pos, pos_naive) == sb.SUPERBEST_F16_POS_SAVINGS_PCT == 79.5

    gen = sum(sb.SUPERBEST_COSTS_GEN[op] for op in sb.SUPERBEST_F16_GEN_OPS)
    gen_naive = sum(sb.NAIVE_COSTS[op] for op in sb.SUPERBEST_F16_GEN_OPS)
    assert (gen, gen_naive) == (sb.SUPERBEST_F16_GEN_TOTAL, sb.SUPERBEST_F16_GEN_NAIVE) == (18, 54)
    assert _pct(gen, gen_naive) == sb.SUPERBEST_F16_GEN_SAVINGS_PCT == 66.7

    # The census count: ln x = EXL(0, x) as one node. ModelAudit.lean states 1+1+1+1+1+2+2+2+2+1 = 14.
    assert sb.SUPERBEST_V52_POS_OPS == sb.SUPERBEST_F16_POS_OPS
    exl = sum(sb.SUPERBEST_COSTS_POS_WITH_EXL[op] for op in sb.SUPERBEST_V52_POS_OPS)
    assert exl == sb.SUPERBEST_V53_POS_TOTAL == 14
    assert _pct(exl, sb.SUPERBEST_V53_POS_NAIVE) == sb.SUPERBEST_V53_POS_SAVINGS_PCT == 80.8
