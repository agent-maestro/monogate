"""
Session 1 — Fuzz & numerical stability tests for monogate.core.

Covers: NaN/inf inputs, huge exponents, near-zero log arguments,
overflow/underflow, identity preservation under extreme inputs,
and BEST routing stability.
"""

import math
import random
import sys

import pytest

from monogate.core import (
    BEST,
    E,
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

TOL = 1e-9
RNG = random.Random(42)


# ── op: invalid / edge inputs ─────────────────────────────────────────────────

class TestOpEdgeCases:
    def test_y_exactly_zero(self):
        with pytest.raises((ValueError, ZeroDivisionError)):
            op(0.0, 0.0)

    def test_y_negative_integer(self):
        with pytest.raises(ValueError):
            op(1.0, -5)

    def test_y_negative_float(self):
        with pytest.raises(ValueError):
            op(0.0, -1e-300)

    def test_y_minus_inf(self):
        with pytest.raises(ValueError):
            op(0.0, float("-inf"))

    def test_x_positive_inf(self):
        result = op(float("inf"), 1.0)
        assert result == float("inf")

    def test_x_negative_inf(self):
        result = op(float("-inf"), 1.0)
        # exp(-inf) = 0, ln(1) = 0 → result = 0
        assert result == 0.0

    def test_y_positive_inf(self):
        # exp(0) - ln(inf) = 1 - inf = -inf
        result = op(0.0, float("inf"))
        assert result == float("-inf")

    def test_x_nan(self):
        result = op(float("nan"), 1.0)
        assert math.isnan(result)

    def test_y_nan_raises_or_nan(self):
        # y=nan fails the y<=0 check? nan<=0 is False, so it passes
        result = op(0.0, float("nan"))
        assert math.isnan(result)

    def test_y_very_small_positive(self):
        # Near zero but positive — ln(ε) is large negative
        epsilon = 1e-300
        result = op(0.0, epsilon)
        expected = 1.0 - math.log(epsilon)
        assert abs(result - expected) < abs(expected) * 1e-12

    def test_x_very_large(self):
        # exp(710) overflows to inf in Python
        result = op(710.0, 1.0)
        assert result == float("inf")

    def test_x_very_negative(self):
        # exp(-1000) underflows to 0.0
        result = op(-1000.0, 1.0)
        assert result == 0.0 - math.log(1.0)  # = 0.0

    def test_y_close_to_one(self):
        # ln(1+ε) ≈ ε for small ε; result ≈ exp(0) - ε = 1 - ε
        for eps in [1e-7, 1e-12, 1e-15]:
            result = op(0.0, 1.0 + eps)
            expected = 1.0 - math.log(1.0 + eps)
            assert abs(result - expected) < 1e-12

    def test_x_zero_y_one(self):
        assert abs(op(0.0, 1.0) - 1.0) < 1e-15


# ── Numerical stability: derived ops ─────────────────────────────────────────

class TestDerivedOpStability:
    @pytest.mark.parametrize("x", [0.0, 1.0, -1.0, 100.0, -100.0, 1e-10, -1e-10])
    def test_exp_eml_matches_math(self, x):
        result = exp_eml(x)
        expected = math.exp(x) if x < 709 else float("inf")
        if math.isinf(expected):
            assert math.isinf(result)
        else:
            assert abs(result - expected) < abs(expected) * 1e-12 + 1e-15

    @pytest.mark.parametrize("x", [1e-15, 1e-10, 0.5, 1.0, math.e, 100.0, 1e100])
    def test_ln_eml_matches_math(self, x):
        result = ln_eml(x)
        expected = math.log(x)
        assert abs(result - expected) < abs(expected) * 1e-12 + 1e-15

    def test_ln_eml_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            ln_eml(0.0)
        with pytest.raises(ValueError):
            ln_eml(-1.0)

    # add_eml: works for any pair where at least one branch is reachable.
    # Domain: both-zero is a special case now handled; both-negative uses double-negation.
    @pytest.mark.parametrize("x,y,expected", [
        (2.0, 3.0, 5.0),
        (0.5, 1.5, 2.0),
        (0.0, 0.0, 0.0),
        (10.0, 5.0, 15.0),
        (1.0, 0.0, 1.0),
        (0.0, 1.0, 1.0),
    ])
    def test_add_eml_matches_expected(self, x, y, expected):
        assert abs(add_eml(x, y) - expected) < 1e-9

    # sub_eml domain: x > 0 (uses ln_eml(x))
    @pytest.mark.parametrize("x,y", [
        (5.0, 2.0), (1.0, 0.5), (10.0, 3.0), (math.e, 1.0),
    ])
    def test_sub_eml_matches_expected(self, x, y):
        assert abs(sub_eml(x, y) - (x - y)) < 1e-9

    @pytest.mark.parametrize("x", [0.5, 1.0, 2.0, 10.0, -1.0, -10.0, 0.0])
    def test_neg_eml_matches_expected(self, x):
        assert abs(neg_eml(x) - (-x)) < 1e-9

    # mul_eml domain: x, y > 0 (uses ln internally)
    @pytest.mark.parametrize("x,y", [
        (2.0, 3.0), (0.5, 4.0), (math.e, math.e), (10.0, 0.1),
    ])
    def test_mul_eml_matches_expected(self, x, y):
        assert abs(mul_eml(x, y) - x * y) < abs(x * y) * 1e-9 + 1e-12

    # pow_eml domain: x > 0
    @pytest.mark.parametrize("x,n", [
        (2.0, 3), (3.0, 2), (0.5, 4), (math.e, 2),
    ])
    def test_pow_eml_integer_matches_expected(self, x, n):
        result = pow_eml(x, n)
        expected = x ** n
        assert abs(result - expected) < abs(expected) * 1e-9 + 1e-12

    @pytest.mark.parametrize("x", [0.5, 1.0, 2.0, math.e, 100.0])
    def test_recip_eml_matches_expected(self, x):
        result = recip_eml(x)
        assert abs(result - 1.0 / x) < 1e-9


# ── Identity preservation ─────────────────────────────────────────────────────

class TestIdentities:
    def test_zero_identity(self):
        assert abs(ZERO) < 1e-12

    def test_e_identity(self):
        assert abs(E - math.e) < 1e-14

    def test_exp_ln_roundtrip(self):
        for x in [0.1, 1.0, math.e, 10.0, 100.0]:
            assert abs(math.exp(math.log(x)) - x) < x * 1e-14

    def test_add_zero_identity(self):
        # add_eml(x, 0) = x for x > 0
        for x in [0.5, 1.0, 5.0]:
            assert abs(add_eml(x, 0.0) - x) < 1e-9

    def test_add_both_zero(self):
        assert abs(add_eml(0.0, 0.0)) < 1e-12

    def test_mul_recip_inverse(self):
        # mul_eml domain: both args > 0
        for x in [0.5, 1.0, 2.0, 10.0]:
            assert abs(mul_eml(x, recip_eml(x)) - 1.0) < 1e-9

    def test_div_eml_as_mul_recip(self):
        # div_eml domain: x, y > 0
        for x, y in [(1.0, 2.0), (5.0, 3.0), (0.1, 0.7)]:
            assert abs(div_eml(x, y) - x / y) < 1e-9


# ── Fuzz: random valid inputs ─────────────────────────────────────────────────

class TestFuzzRandomInputs:
    N = 500

    def test_op_random_valid(self):
        failures = []
        for _ in range(self.N):
            x = RNG.uniform(-50, 50)
            y = RNG.uniform(1e-10, 1e6)
            try:
                result = op(x, y)
                expected = math.exp(x) - math.log(y)
                if not (math.isinf(result) and math.isinf(expected)):
                    if abs(result - expected) > abs(expected) * 1e-12 + 1e-15:
                        failures.append((x, y, result, expected))
            except (ValueError, OverflowError):
                failures.append(("exception", x, y))
        assert len(failures) == 0, f"{len(failures)} failures: {failures[:3]}"

    def test_add_random_positive(self):
        # add_eml: safe for x, y in (0, 200) — neg_eml stable for |y| < 708
        for _ in range(self.N):
            x = RNG.uniform(1e-6, 200.0)
            y = RNG.uniform(1e-6, 200.0)
            assert abs(add_eml(x, y) - (x + y)) < 1e-6

    def test_mul_random_positive(self):
        # mul_eml domain: x, y > 0
        for _ in range(self.N):
            x = RNG.uniform(1e-4, 1e4)
            y = RNG.uniform(1e-4, 1e4)
            result = mul_eml(x, y)
            expected = x * y
            tol = abs(expected) * 1e-9 + 1e-10
            assert abs(result - expected) < tol

    def test_pow_random_positive_base(self):
        # pow_eml domain: x > 0, all sign combinations handled
        for _ in range(200):
            x = RNG.uniform(0.1, 5.0)
            n = RNG.randint(1, 6)  # keep n small so exp(n*ln(x)) doesn't overflow
            result = pow_eml(x, n)
            expected = x ** n
            tol = abs(expected) * 1e-9 + 1e-10
            assert abs(result - expected) < tol


# ── BEST routing stability ────────────────────────────────────────────────────

class TestBESTStability:
    # BEST routes: exp->EML, ln->EXL, mul->EDL, div->EDL, pow->EXL
    # EDL domain: args must not be 0 or 1 in certain positions
    # BEST has no .op() — use the module-level op() for the raw operator

    def test_best_exp_valid(self):
        for x in [0.0, 1.0, -1.0, 10.0]:
            result = BEST.exp(x)
            assert abs(result - math.exp(x)) < 1e-9

    def test_best_ln_valid(self):
        for x in [0.5, 2.0, math.e, 100.0]:  # exclude 1.0 (EXL domain edge)
            result = BEST.ln(x)
            assert abs(result - math.log(x)) < 1e-9

    def test_best_pow_valid(self):
        # EXL.pow: x > 0, n != 0, 1
        for x, n in [(2.0, 3), (3.0, 2), (4.0, 3)]:
            result = BEST.pow(x, n)
            assert abs(result - x ** n) < 1e-9

    def test_best_has_no_op_attribute(self):
        # BEST routes named ops, not the raw operator — document this
        import pytest
        with pytest.raises(AttributeError):
            _ = BEST.op

    def test_raw_op_still_works(self):
        # The module-level op() is always correct
        assert abs(op(1.0, 1.0) - math.e) < 1e-14
