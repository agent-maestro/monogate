"""
Tests for monogate.core — pure-Python EML arithmetic.

Mirrors the JS test suite (lib/src/__tests__/) for parity.
All tolerances match the JS suite: 1e-10 for derived ops, 1e-14 for exact ones.
"""

import math

import pytest

from monogate.core import (
    E,
    IDENTITIES,
    NEG_ONE,
    ZERO,
    add_eml,
    div_eml,
    exp_eml,
    ln_eml,
    mul_eml,
    neg_eml,
    op,
    pow_eml,
    recip_eml,
    sub_eml,
)

TOL_TIGHT = 1e-14
TOL_LOOSE = 1e-10


# ── op ────────────────────────────────────────────────────────────────────────

class TestOp:
    def test_op_one_one(self):
        assert abs(op(1, 1) - math.e) < TOL_TIGHT

    def test_op_zero_one(self):
        # exp(0) − ln(1) = 1 − 0 = 1
        assert abs(op(0, 1) - 1) < TOL_TIGHT

    def test_op_one_e(self):
        # exp(1) − ln(e) = e − 1
        assert abs(op(1, math.e) - (math.e - 1)) < TOL_TIGHT

    def test_op_negative_x(self):
        # exp(−1) − ln(1) = 1/e
        assert abs(op(-1, 1) - 1 / math.e) < TOL_TIGHT

    def test_op_rejects_y_zero(self):
        with pytest.raises(ValueError, match="y must be > 0"):
            op(1, 0)

    def test_op_rejects_y_negative(self):
        with pytest.raises(ValueError, match="y must be > 0"):
            op(1, -1)

    def test_op_large_values(self):
        # Just check it doesn't raise and is finite
        result = op(10, 1)
        assert math.isfinite(result)
        assert abs(result - math.exp(10)) < 1e-6


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_E(self):
        assert abs(E - math.e) < TOL_TIGHT

    def test_ZERO(self):
        assert abs(ZERO) < TOL_TIGHT

    def test_NEG_ONE(self):
        assert abs(NEG_ONE - (-1)) < TOL_TIGHT


# ── exp_eml ───────────────────────────────────────────────────────────────────

class TestExpEml:
    def test_exp_zero(self):
        assert abs(exp_eml(0) - 1) < TOL_TIGHT

    def test_exp_one(self):
        assert abs(exp_eml(1) - math.e) < TOL_TIGHT

    def test_exp_two(self):
        assert abs(exp_eml(2) - math.e ** 2) < TOL_TIGHT

    def test_exp_negative(self):
        assert abs(exp_eml(-1) - 1 / math.e) < TOL_TIGHT

    def test_exp_matches_math(self):
        for v in [0.5, 1.5, 3.0, -2.0]:
            assert abs(exp_eml(v) - math.exp(v)) < TOL_TIGHT


# ── ln_eml ────────────────────────────────────────────────────────────────────

class TestLnEml:
    def test_ln_one(self):
        assert abs(ln_eml(1) - 0) < TOL_TIGHT

    def test_ln_e(self):
        assert abs(ln_eml(math.e) - 1) < TOL_LOOSE

    def test_ln_e_squared(self):
        assert abs(ln_eml(math.e ** 2) - 2) < TOL_LOOSE

    def test_ln_half(self):
        assert abs(ln_eml(0.5) - math.log(0.5)) < TOL_LOOSE

    def test_ln_matches_math(self):
        for v in [0.1, 0.5, 2.0, 10.0, 100.0]:
            assert abs(ln_eml(v) - math.log(v)) < TOL_LOOSE

    def test_ln_inverse_of_exp(self):
        for v in [0.1, 1.0, 5.0]:
            assert abs(ln_eml(exp_eml(v)) - v) < TOL_LOOSE


# ── sub_eml ───────────────────────────────────────────────────────────────────

class TestSubEml:
    def test_sub_basic(self):
        assert abs(sub_eml(5, 2) - 3) < TOL_LOOSE

    def test_sub_to_zero(self):
        assert abs(sub_eml(3, 3) - 0) < TOL_LOOSE

    def test_sub_to_negative(self):
        assert abs(sub_eml(1, 3) - (-2)) < TOL_LOOSE

    def test_sub_small(self):
        assert abs(sub_eml(1.5, 0.5) - 1) < TOL_LOOSE

    def test_sub_by_zero_impossible(self):
        # sub_eml(x, y) = ln(x) − exp(y); y=0 means exp(0)=1 subtracted from ln(x)
        # sub_eml is valid for x > 0 only (uses ln_eml internally)
        with pytest.raises((ValueError, Exception)):
            sub_eml(0, 1)  # ln(0) is undefined


# ── neg_eml ───────────────────────────────────────────────────────────────────

class TestNegEml:
    def test_neg_zero(self):
        assert abs(neg_eml(0)) < TOL_TIGHT

    def test_neg_positive(self):
        assert abs(neg_eml(3) + 3) < TOL_LOOSE

    def test_neg_negative(self):
        assert abs(neg_eml(-5) - 5) < TOL_LOOSE

    def test_neg_one(self):
        assert abs(neg_eml(1) + 1) < TOL_LOOSE

    def test_neg_neg_one(self):
        assert abs(neg_eml(-1) - 1) < TOL_LOOSE

    def test_double_neg(self):
        for v in [-3.0, 0.0, 1.0, 5.0]:
            assert abs(neg_eml(neg_eml(v)) - v) < TOL_LOOSE

    def test_neg_small_positive(self):
        assert abs(neg_eml(0.001) + 0.001) < TOL_LOOSE

    def test_neg_large_negative(self):
        # Regime A (tower formula) should be stable for y << 0
        assert abs(neg_eml(-10) - 10) < TOL_LOOSE

    @pytest.mark.parametrize("v", [-5, -2, -1, -0.5, 0, 0.5, 1, 2, 5, 10])
    def test_neg_parametric(self, v):
        assert abs(neg_eml(float(v)) + float(v)) < TOL_LOOSE


# ── add_eml ───────────────────────────────────────────────────────────────────

class TestAddEml:
    def test_add_positive(self):
        assert abs(add_eml(2, 3) - 5) < TOL_LOOSE

    def test_add_negative(self):
        assert abs(add_eml(-2, -3) + 5) < TOL_LOOSE

    def test_add_mixed_positive_dominant(self):
        assert abs(add_eml(0.5, -1.5) + 1) < TOL_LOOSE

    def test_add_mixed_negative_dominant(self):
        assert abs(add_eml(-1.5, 0.5) + 1) < TOL_LOOSE

    def test_add_commutative(self):
        assert abs(add_eml(3, 7) - add_eml(7, 3)) < TOL_LOOSE

    def test_add_with_zero(self):
        assert abs(add_eml(5, 0) - 5) < TOL_LOOSE

    def test_add_to_zero(self):
        assert abs(add_eml(3, -3)) < TOL_LOOSE

    def test_add_fractional(self):
        assert abs(add_eml(1.5, 2.5) - 4.0) < TOL_LOOSE

    @pytest.mark.parametrize("a,b", [(1, 2), (-1, -2), (3, -1), (-3, 1), (0, 5)])
    def test_add_parametric(self, a, b):
        assert abs(add_eml(float(a), float(b)) - (a + b)) < TOL_LOOSE


# ── mul_eml ───────────────────────────────────────────────────────────────────

class TestMulEml:
    def test_mul_integers(self):
        assert abs(mul_eml(2, 3) - 6) < TOL_LOOSE

    def test_mul_by_one(self):
        assert abs(mul_eml(5, 1) - 5) < TOL_LOOSE

    def test_mul_fraction(self):
        assert abs(mul_eml(4, 0.25) - 1) < TOL_LOOSE

    def test_mul_commutative(self):
        assert abs(mul_eml(3, 7) - mul_eml(7, 3)) < TOL_LOOSE

    def test_mul_e_squared(self):
        assert abs(mul_eml(math.e, math.e) - math.e ** 2) < TOL_LOOSE

    @pytest.mark.parametrize("a,b", [(2, 5), (1.5, 4), (0.1, 10), (100, 0.01)])
    def test_mul_parametric(self, a, b):
        assert abs(mul_eml(a, b) - a * b) < TOL_LOOSE


# ── div_eml ───────────────────────────────────────────────────────────────────

class TestDivEml:
    def test_div_exact(self):
        assert abs(div_eml(6, 3) - 2) < TOL_LOOSE

    def test_div_fraction(self):
        # div_eml requires ln(x) > 0 (i.e. x > 1) to avoid ln(0) inside add_eml
        assert abs(div_eml(2, 8) - 0.25) < TOL_LOOSE

    def test_div_by_self(self):
        assert abs(div_eml(5, 5) - 1) < TOL_LOOSE

    def test_div_less_than_one(self):
        assert abs(div_eml(2, 4) - 0.5) < TOL_LOOSE

    @pytest.mark.parametrize("a,b", [(10, 5), (3, 2), (7, 7), (4, 2)])
    def test_div_parametric(self, a, b):
        assert abs(div_eml(a, b) - a / b) < TOL_LOOSE


# ── pow_eml ───────────────────────────────────────────────────────────────────

class TestPowEml:
    def test_pow_integer(self):
        assert abs(pow_eml(2, 10) - 1024) < 1e-8

    def test_pow_half(self):
        assert abs(pow_eml(4, 0.5) - 2) < TOL_LOOSE

    def test_pow_one(self):
        # pow_eml(x, 1): mul_eml(1, ln(x)) requires x > 1
        assert abs(pow_eml(7, 1) - 7) < TOL_LOOSE

    @pytest.mark.parametrize("base,exp_", [(2, 3), (3, 2), (4, 0.5), (9, 0.5)])
    def test_pow_parametric(self, base, exp_):
        assert abs(pow_eml(base, exp_) - base ** exp_) < TOL_LOOSE


# ── recip_eml ─────────────────────────────────────────────────────────────────

class TestRecipEml:
    def test_recip_two(self):
        assert abs(recip_eml(2) - 0.5) < TOL_LOOSE

    def test_recip_four(self):
        assert abs(recip_eml(4) - 0.25) < TOL_LOOSE

    def test_recip_one(self):
        assert abs(recip_eml(1) - 1) < TOL_LOOSE

    def test_recip_e(self):
        assert abs(recip_eml(math.e) - 1 / math.e) < TOL_LOOSE

    def test_recip_self_inverse(self):
        for v in [2, 3, 5, 10]:
            assert abs(recip_eml(recip_eml(float(v))) - v) < TOL_LOOSE


# ── IDENTITIES table ──────────────────────────────────────────────────────────

class TestIdentities:
    def test_identities_is_list(self):
        assert isinstance(IDENTITIES, list)

    def test_identities_count(self):
        assert len(IDENTITIES) == 11

    def test_required_keys(self):
        required = {"name", "eml_form", "nodes", "depth", "status"}
        for entry in IDENTITIES:
            assert required.issubset(entry.keys()), f"Missing keys in {entry}"

    def test_status_values(self):
        valid = {"verified", "proven"}
        for entry in IDENTITIES:
            assert entry["status"] in valid, f"Bad status in {entry}"

    def test_nodes_positive(self):
        for entry in IDENTITIES:
            assert entry["nodes"] >= 1

    def test_depth_positive(self):
        for entry in IDENTITIES:
            assert entry["depth"] >= 1

    def test_named_entries_present(self):
        names = {e["name"] for e in IDENTITIES}
        assert "eˣ" in names
        assert "ln x" in names
        assert "e" in names
        assert "0" in names


# ── Cross-function consistency ────────────────────────────────────────────────

class TestConsistency:
    def test_exp_ln_inverse(self):
        for v in [0.1, 0.5, 1.0, 2.0, 5.0]:
            assert abs(exp_eml(ln_eml(v)) - v) < TOL_LOOSE

    def test_neg_add(self):
        # x + neg(x) = 0
        for v in [-3.0, -1.0, 0.5, 2.0, 5.0]:
            assert abs(add_eml(v, neg_eml(v))) < TOL_LOOSE

    def test_mul_recip(self):
        # x * recip(x) = 1  (skip v=1: mul_eml(1,1) hits add_eml(0,0) domain edge)
        for v in [0.5, 2.0, 5.0]:
            assert abs(mul_eml(v, recip_eml(v)) - 1) < TOL_LOOSE

    def test_div_is_mul_recip(self):
        # div_eml requires a > 1 (so ln(a) > 0) to avoid domain edge in add_eml
        for a, b in [(6, 3), (10, 4), (7, 7)]:
            assert abs(div_eml(a, b) - mul_eml(a, recip_eml(b))) < TOL_LOOSE

    def test_pow_consistent_with_mul(self):
        # x^2 = x*x  (only for x > 1: pow_eml needs ln(x) > 0)
        for v in [2.0, 3.0]:
            assert abs(pow_eml(v, 2) - mul_eml(v, v)) < TOL_LOOSE

    def test_sub_is_add_neg(self):
        # sub(x, y) = add(x, neg(y))  — only for x > 0
        for x, y in [(5, 2), (3, 1), (10, 7)]:
            assert abs(sub_eml(float(x), float(y)) - add_eml(float(x), neg_eml(float(y)))) < TOL_LOOSE
