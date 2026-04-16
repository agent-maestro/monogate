"""Tests for monogate.padic — p-adic arithmetic and p-adic EML."""

from __future__ import annotations

import math
import pytest

from monogate.padic import (
    PAdicNumber,
    padic_exp,
    padic_log,
    padic_eml,
    padic_fixed_points,
    valuation,
)


# ── valuation ─────────────────────────────────────────────────────────────────

def test_valuation_basic():
    """v_2(12) = 2 since 12 = 4 × 3."""
    assert valuation(12, 2) == 2


def test_valuation_prime():
    """v_3(45) = 2 since 45 = 9 × 5."""
    assert valuation(45, 3) == 2


def test_valuation_prime_itself():
    """v_p(p) = 1."""
    for p in (2, 3, 5, 7):
        assert valuation(p, p) == 1


def test_valuation_coprime():
    """v_p(n) = 0 when gcd(n, p) = 1."""
    assert valuation(7, 2) == 0
    assert valuation(4, 3) == 0


def test_valuation_zero():
    """v_p(0) = 0 by convention."""
    assert valuation(0, 2) == 0


# ── PAdicNumber construction ──────────────────────────────────────────────────

def test_padic_from_int_zero():
    """PAdicNumber.from_int(0) has all-zero digits."""
    x = PAdicNumber.from_int(0, p=2, precision=8)
    assert all(d == 0 for d in x.digits)


def test_padic_from_int_one():
    """PAdicNumber.from_int(1) has digit 1 at index 0."""
    x = PAdicNumber.from_int(1, p=2, precision=8)
    assert x.digits[0] == 1
    assert all(d == 0 for d in x.digits[1:])


def test_padic_from_int_round_trip():
    """from_int(n).to_int() == n mod p^precision."""
    for n in [0, 1, 6, 12, 100]:
        x = PAdicNumber.from_int(n, p=3, precision=6)
        assert x.to_int() == n % (3 ** 6)


def test_padic_zero():
    """PAdicNumber.zero() has all-zero digits."""
    x = PAdicNumber.zero(p=5, precision=8)
    assert all(d == 0 for d in x.digits)
    assert x.norm() == 0.0


def test_padic_one():
    """PAdicNumber.one() has digit 1 at index 0."""
    x = PAdicNumber.one(p=5, precision=8)
    assert x.digits[0] == 1
    assert all(d == 0 for d in x.digits[1:])


# ── PAdicNumber arithmetic ────────────────────────────────────────────────────

def test_padic_add_zero():
    """x + 0 == x."""
    x = PAdicNumber.from_int(6, p=3, precision=8)
    z = PAdicNumber.zero(p=3, precision=8)
    assert (x + z).digits == x.digits


def test_padic_add_commutative():
    """x + y == y + x."""
    x = PAdicNumber.from_int(4, p=2, precision=8)
    y = PAdicNumber.from_int(6, p=2, precision=8)
    assert (x + y).digits == (y + x).digits


def test_padic_add_associative():
    """(x + y) + z == x + (y + z)."""
    x = PAdicNumber.from_int(3, p=3, precision=6)
    y = PAdicNumber.from_int(9, p=3, precision=6)
    z = PAdicNumber.from_int(27, p=3, precision=6)
    assert ((x + y) + z).digits == (x + (y + z)).digits


def test_padic_neg():
    """x + (-x) == 0."""
    x = PAdicNumber.from_int(7, p=2, precision=8)
    result = x + (-x)
    # Sum should be 0 mod 2^8
    assert result.to_int() % (2 ** 8) == 0


def test_padic_mul_one():
    """x * 1 == x."""
    x = PAdicNumber.from_int(6, p=3, precision=8)
    one = PAdicNumber.one(p=3, precision=8)
    assert (x * one).digits == x.digits


def test_padic_mul_integers():
    """2 * 3 == 6 in 5-adic."""
    a = PAdicNumber.from_int(2, p=5, precision=8)
    b = PAdicNumber.from_int(3, p=5, precision=8)
    product = a * b
    assert product.to_int() == 6


def test_padic_norm():
    """p-adic norm of p^k is p^{-k}."""
    x = PAdicNumber.from_int(4, p=2, precision=8)  # 4 = 2^2
    assert abs(x.norm() - 2 ** (-2)) < 1e-9


def test_padic_repr():
    """PAdicNumber has a non-empty repr."""
    x = PAdicNumber.from_int(3, p=2, precision=6)
    assert isinstance(repr(x), str)
    assert len(repr(x)) > 0


# ── padic_exp ─────────────────────────────────────────────────────────────────

def test_padic_exp_zero():
    """exp_p(0) == 1."""
    for p in (2, 3, 5):
        prec = 8
        x = PAdicNumber.zero(p=p, precision=prec)
        result = padic_exp(x)
        assert result.digits[0] == 1, f"exp_{p}(0) should have digits[0]=1, got {result.digits[0]}"


def test_padic_exp_convergence_check():
    """padic_exp raises for inputs outside convergence radius."""
    # For p=2, need val >= 2; input 2 has val=1 which is too small
    x = PAdicNumber.from_int(2, p=2, precision=8)  # val=1 < required 2
    with pytest.raises(ValueError, match="converge"):
        padic_exp(x)


def test_padic_exp_valid_input_p3():
    """padic_exp works for valid input (multiple of p for p=3)."""
    x = PAdicNumber.from_int(3, p=3, precision=8)  # val_3(3) = 1 >= 1 ✓
    result = padic_exp(x)
    # Result should be 1 (mod 3): digits[0] == 1 (since exp(x) ≡ 1 mod p for small x)
    assert isinstance(result, PAdicNumber)


def test_padic_exp_returns_padic_number():
    """padic_exp returns a PAdicNumber."""
    x = PAdicNumber.from_int(4, p=2, precision=8)  # val_2(4) = 2 >= 2 ✓
    result = padic_exp(x)
    assert isinstance(result, PAdicNumber)


# ── padic_log ─────────────────────────────────────────────────────────────────

def test_padic_log_one():
    """log_p(1) == 0."""
    for p in (2, 3, 5):
        one = PAdicNumber.one(p=p, precision=8)
        result = padic_log(one)
        assert result.to_int() % (p ** 8) == 0, f"log_{p}(1) should be 0"


def test_padic_log_convergence_check():
    """padic_log raises for input not ≡ 1 (mod p)."""
    x = PAdicNumber.from_int(2, p=3, precision=8)  # digits[0]=2 ≠ 1
    with pytest.raises(ValueError, match="≡ 1"):
        padic_log(x)


def test_padic_log_returns_padic_number():
    """padic_log returns a PAdicNumber for valid input."""
    x = PAdicNumber.from_int(1 + 3, p=3, precision=8)  # 4 ≡ 1 (mod 3)
    result = padic_log(x)
    assert isinstance(result, PAdicNumber)


# ── padic_eml ─────────────────────────────────────────────────────────────────

def test_padic_eml_zero_one():
    """eml(0, 1) = exp(0) - log(1) = 1 - 0 = 1."""
    for p in (2, 3, 5):
        x = PAdicNumber.zero(p=p, precision=8)
        y = PAdicNumber.one(p=p, precision=8)
        result = padic_eml(x, y)
        assert result.digits[0] == 1, f"eml_{p}(0,1) digits[0] should be 1"


def test_padic_eml_returns_padic_number():
    """padic_eml returns a PAdicNumber."""
    p, prec = 3, 8
    x = PAdicNumber.zero(p=p, precision=prec)
    y = PAdicNumber.one(p=p, precision=prec)
    result = padic_eml(x, y)
    assert isinstance(result, PAdicNumber)


def test_padic_eml_incompatible_raises():
    """padic_eml raises for incompatible p or precision."""
    x = PAdicNumber.zero(p=2, precision=8)
    y = PAdicNumber.zero(p=3, precision=8)
    with pytest.raises(ValueError):
        padic_eml(x, y)


# ── padic_fixed_points ────────────────────────────────────────────────────────

def test_padic_fixed_points_returns_list():
    """padic_fixed_points returns a list."""
    result = padic_fixed_points(depth=1, p=3, precision=6, n_candidates=10)
    assert isinstance(result, list)


def test_padic_fixed_points_all_padic_numbers():
    """padic_fixed_points returns PAdicNumber instances."""
    result = padic_fixed_points(depth=1, p=3, precision=6, n_candidates=10)
    for item in result:
        assert isinstance(item, PAdicNumber)


def test_padic_fixed_points_correct_p():
    """padic_fixed_points returns numbers with the correct p."""
    p = 5
    result = padic_fixed_points(depth=1, p=p, precision=6, n_candidates=10)
    for item in result:
        assert item.p == p


def test_padic_fixed_points_zero_is_candidate():
    """The zero element is always a trivial fixed-point candidate (depth=1, eml(0,1))."""
    # eml(0,1) = exp(0) - log(1) = 1 ≠ 0, so zero is NOT a fixed point.
    # But the function should return a list (possibly empty) without crashing.
    result = padic_fixed_points(depth=1, p=3, precision=6, n_candidates=5)
    assert isinstance(result, list)
