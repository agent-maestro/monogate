"""Tests for monogate.equality — bounded-depth F16 equality decision.

Covers the demo cases from exploration/blind-sessions/tools/eq_d_decide.py
plus edge cases (malformed parse, unequal with close values, high-depth
identities, named constants).
"""

from __future__ import annotations

import pytest
from mpmath import mpf

from monogate.equality import (
    DecisionResult,
    F16Tree,
    decide,
    parse,
)


# ─── Parser ──────────────────────────────────────────────────────────

class TestParser:
    def test_leaf_integer(self):
        t = parse("1")
        assert t.op == "LEAF"
        assert t.value == mpf(1)

    def test_leaf_fraction(self):
        t = parse("3/4")
        assert t.op == "LEAF"
        assert abs(t.value - mpf("0.75")) < 1e-40

    def test_leaf_named_constant_e(self):
        t = parse("e")
        assert t.op == "LEAF"
        # e is approximately 2.718
        assert abs(float(t.value) - 2.718281828459045) < 1e-12

    def test_leaf_named_constant_pi(self):
        t = parse("pi")
        assert t.op == "LEAF"
        assert abs(float(t.value) - 3.141592653589793) < 1e-12

    def test_leaf_named_constant_ln2(self):
        t = parse("ln2")
        assert t.op == "LEAF"
        assert abs(float(t.value) - 0.6931471805599453) < 1e-12

    def test_unary_minus(self):
        t = parse("-1")
        assert t.op == "NEG"
        assert t.args[0].value == mpf(1)

    def test_binary_op(self):
        t = parse("EML(1, 1)")
        assert t.op == "EML"
        assert len(t.args) == 2
        assert t.depth() == 1
        assert t.size() == 3

    def test_nested(self):
        t = parse("EML(EXL(0, e), 1)")
        assert t.op == "EML"
        assert t.args[0].op == "EXL"
        assert t.depth() == 2

    def test_unknown_token_raises(self):
        with pytest.raises(ValueError):
            parse("@")

    def test_trailing_tokens_raises(self):
        with pytest.raises(ValueError):
            parse("1 2")


# ─── F16Tree metadata ────────────────────────────────────────────────

class TestTreeMetadata:
    def test_leaf_depth_zero(self):
        assert parse("1").depth() == 0

    def test_leaf_size_one(self):
        assert parse("1").size() == 1

    def test_depth_1_tree(self):
        assert parse("EML(1, 1)").depth() == 1

    def test_depth_2_tree(self):
        assert parse("EML(EML(1, 1), 1)").depth() == 2

    def test_size_nested(self):
        # EML(EML(1,1),1): 1 + size(EML(1,1)) + size(1) = 1 + 3 + 1 = 5
        assert parse("EML(EML(1, 1), 1)").size() == 5


# ─── Decision: known equalities ─────────────────────────────────────

class TestKnownEqualities:
    """Well-known identities. The decision procedure must return EQUAL."""

    def test_e_equals_EML_1_1(self):
        # EML(1, 1) = exp(1) - ln(1) = e - 0 = e
        r = decide(parse("e"), parse("EML(1, 1)"))
        assert r.verdict == "EQUAL"

    def test_one_equals_EXL_0_e(self):
        # EXL(0, e) = exp(0) * ln(e) = 1 * 1 = 1
        r = decide(parse("1"), parse("EXL(0, e)"))
        assert r.verdict == "EQUAL"

    def test_zero_equals_EML_0_e(self):
        # EML(0, e) = exp(0) - ln(e) = 1 - 1 = 0
        r = decide(parse("0"), parse("EML(0, e)"))
        assert r.verdict == "EQUAL"

    def test_e_minus_one_equals_EML_1_e(self):
        # EML(1, e) = exp(1) - ln(e) = e - 1
        r = decide(parse("EML(1, e)"), parse("SUB(e, 1)"))
        assert r.verdict == "EQUAL"

    def test_sinh_ln2_equals_three_quarters(self):
        # sinh(ln 2) = (e^{ln 2} - e^{-ln 2}) / 2 = (2 - 1/2)/2 = 3/4
        expr = "DIV(SUB(EXP(ln2), DIV(1, EXP(ln2))), 2)"
        r = decide(parse(expr), parse("3/4"))
        assert r.verdict == "EQUAL"

    def test_cosh_ln2_equals_five_quarters(self):
        # cosh(ln 2) = (2 + 1/2)/2 = 5/4
        expr = "DIV(ADD(EXP(ln2), DIV(1, EXP(ln2))), 2)"
        r = decide(parse(expr), parse("5/4"))
        assert r.verdict == "EQUAL"

    def test_exp_zero_equals_one(self):
        r = decide(parse("EXP(0)"), parse("1"))
        assert r.verdict == "EQUAL"

    def test_log_e_equals_one(self):
        r = decide(parse("LOG(e)"), parse("1"))
        assert r.verdict == "EQUAL"

    def test_self_equality(self):
        r = decide(parse("EML(1, 1)"), parse("EML(1, 1)"))
        assert r.verdict == "EQUAL"


# ─── Decision: known inequalities ───────────────────────────────────

class TestKnownInequalities:
    def test_e_not_equal_pi(self):
        r = decide(parse("e"), parse("pi"))
        assert r.verdict == "UNEQUAL"

    def test_one_not_equal_two(self):
        r = decide(parse("1"), parse("2"))
        assert r.verdict == "UNEQUAL"

    def test_EML_unequal_different_args(self):
        r = decide(parse("EML(1, 1)"), parse("EML(1, e)"))
        assert r.verdict == "UNEQUAL"


# ─── DecisionResult metadata ─────────────────────────────────────────

class TestDecisionResultMetadata:
    def test_verdict_is_string(self):
        r = decide(parse("1"), parse("1"))
        assert isinstance(r.verdict, str)

    def test_frozen_dataclass(self):
        r = decide(parse("1"), parse("1"))
        with pytest.raises((AttributeError, Exception)):
            r.verdict = "UNEQUAL"  # type: ignore[misc]

    def test_precision_is_positive(self):
        r = decide(parse("e"), parse("pi"))
        assert r.precision_used > 0

    def test_max_depth_computed(self):
        r = decide(parse("EML(EML(1, 1), 1)"), parse("1"))
        assert r.max_depth == 2

    def test_max_size_computed(self):
        r = decide(parse("EML(1, 1)"), parse("EML(1, 1)"))
        # each tree size 3, sum = 6
        assert r.max_size == 6


# ─── Subtle-near-equality (non-standard identity) ───────────────────

class TestSubtleCases:
    def test_ln_e_plus_one_equals_two(self):
        # ln(e) + 1 = 1 + 1 = 2
        r = decide(parse("ADD(LOG(e), 1)"), parse("2"))
        assert r.verdict == "EQUAL"

    def test_exp_log_e_equals_e(self):
        # exp(log(e)) = exp(1) = e
        r = decide(parse("EXP(LOG(e))"), parse("e"))
        assert r.verdict == "EQUAL"

    def test_negation_double(self):
        # NEG(NEG(5)) = 5
        r = decide(parse("NEG(NEG(5))"), parse("5"))
        assert r.verdict == "EQUAL"
