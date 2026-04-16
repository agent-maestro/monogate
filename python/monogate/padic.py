"""
monogate.padic — p-adic arithmetic and p-adic EML.

Implements finite-precision p-adic numbers as truncated power series
sum_{i=0}^{precision-1} a_i * p^i, where each a_i ∈ {0, ..., p-1}.

p-adic exp and log are defined via Mahler/Newton power series within their
convergence radii:
  - p-adic exp: converges for |x|_p < p^(-1/(p-1))
  - p-adic log: converges for |x-1|_p < 1

The EML operator extends naturally: padic_eml(x, y) = padic_exp(x) - padic_log(y)

Public API
----------
PAdicNumber            — p-adic number as truncated digit series
padic_exp              — p-adic exponential (Mahler series)
padic_log              — p-adic logarithm (Newton series)
padic_eml              — EML operator in p-adic arithmetic
padic_fixed_points     — find p-adic attractors of EML trees
valuation              — p-adic valuation v_p(n)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional, Tuple

__all__ = [
    "PAdicNumber",
    "padic_exp",
    "padic_log",
    "padic_eml",
    "padic_fixed_points",
    "valuation",
]

# ── p-adic valuation ──────────────────────────────────────────────────────────

def valuation(n: int, p: int) -> int:
    """Return the p-adic valuation v_p(n): largest k s.t. p^k divides n.

    Args:
        n: Integer (non-zero).
        p: Prime base.

    Returns:
        v_p(n) as a non-negative integer, or 0 for n=0 (by convention).

    Example::

        >>> valuation(12, 2)   # 12 = 4 × 3, v_2(12) = 2
        2
        >>> valuation(45, 3)   # 45 = 9 × 5, v_3(45) = 2
        2
    """
    if n == 0:
        return 0
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


# ── PAdicNumber ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PAdicNumber:
    """p-adic number as a truncated digit expansion.

    Represents x = sum_{i=0}^{precision-1} digits[i] * p^i, where each
    digit is in {0, ..., p-1}.  The valuation v_p(x) is the index of the
    first non-zero digit.

    Attributes:
        p:         Prime base (2, 3, 5, 7, ...).
        precision: Number of p-adic digits (truncation depth).
        digits:    Tuple of digits a_0, a_1, ..., a_{precision-1}.
        val:       p-adic valuation (index of leading non-zero digit).

    Example::

        >>> from monogate.padic import PAdicNumber
        >>> x = PAdicNumber.from_int(6, p=2, precision=8)
        >>> x.to_float()   # 6.0
        6.0
        >>> x.val          # v_2(6) = 1 (6 = 2^1 * 3)
        1
    """

    p: int
    precision: int
    digits: Tuple[int, ...]
    val: int = field(default=0)

    # ── Constructors ──────────────────────────────────────────────────────────

    @staticmethod
    def from_int(n: int, p: int, precision: int = 10) -> "PAdicNumber":
        """Construct from a non-negative integer.

        Args:
            n:         Non-negative integer.
            p:         Prime base.
            precision: Number of digits.

        Returns:
            PAdicNumber representing n mod p^precision.
        """
        if n < 0:
            # Represent negative via p-adic complement: -n = p^precision - n mod p^prec
            n = p ** precision + n
        digits: List[int] = []
        remainder = n % (p ** precision)
        for _ in range(precision):
            digits.append(remainder % p)
            remainder //= p
        v = valuation(n, p) if n != 0 else precision
        return PAdicNumber(p=p, precision=precision, digits=tuple(digits), val=v)

    @staticmethod
    def zero(p: int, precision: int = 10) -> "PAdicNumber":
        """Return the p-adic zero."""
        return PAdicNumber(p=p, precision=precision, digits=tuple([0] * precision), val=precision)

    @staticmethod
    def one(p: int, precision: int = 10) -> "PAdicNumber":
        """Return the p-adic one."""
        digits = [0] * precision
        digits[0] = 1
        return PAdicNumber(p=p, precision=precision, digits=tuple(digits), val=0)

    # ── Conversion ────────────────────────────────────────────────────────────

    def to_int(self) -> int:
        """Convert to integer (canonical representative in [0, p^precision))."""
        result = 0
        pk = 1
        for d in self.digits:
            result += d * pk
            pk *= self.p
        return result

    def to_float(self) -> float:
        """Convert to float by summing digit * p^i terms."""
        result = 0.0
        pk = 1.0
        for d in self.digits:
            result += d * pk
            pk *= self.p
        return result

    def norm(self) -> float:
        """p-adic norm |x|_p = p^(-v_p(x)).  Returns 0.0 for the zero element."""
        if all(d == 0 for d in self.digits):
            return 0.0
        return self.p ** (-self.val)

    # ── Arithmetic ────────────────────────────────────────────────────────────

    def _coerce(self, other: "int | PAdicNumber") -> "PAdicNumber":
        if isinstance(other, int):
            return PAdicNumber.from_int(other, self.p, self.precision)
        if other.p != self.p or other.precision != self.precision:
            raise ValueError(
                f"Incompatible p-adic numbers: p={self.p}/{other.p}, "
                f"precision={self.precision}/{other.precision}"
            )
        return other

    def __add__(self, other: "int | PAdicNumber") -> "PAdicNumber":
        other = self._coerce(other)
        digits: List[int] = []
        carry = 0
        for a, b in zip(self.digits, other.digits):
            s = a + b + carry
            digits.append(s % self.p)
            carry = s // self.p
        result = PAdicNumber(p=self.p, precision=self.precision, digits=tuple(digits))
        return _recompute_val(result)

    def __radd__(self, other: int) -> "PAdicNumber":
        return self.__add__(other)

    def __neg__(self) -> "PAdicNumber":
        # -x via p-adic complement: negate all digits and add 1
        digits = [self.p - 1 - d for d in self.digits]
        result = PAdicNumber(p=self.p, precision=self.precision, digits=tuple(digits))
        return result + 1

    def __sub__(self, other: "int | PAdicNumber") -> "PAdicNumber":
        other = self._coerce(other)
        return self.__add__(-other)

    def __rsub__(self, other: int) -> "PAdicNumber":
        return self._coerce(other).__sub__(self)

    def __mul__(self, other: "int | PAdicNumber") -> "PAdicNumber":
        other = self._coerce(other)
        # Standard schoolbook multiplication mod p^precision
        p, prec = self.p, self.precision
        result = [0] * prec
        for i, a in enumerate(self.digits):
            for j, b in enumerate(other.digits):
                if i + j < prec:
                    result[i + j] += a * b
        # Carry propagation
        carry = 0
        digits: List[int] = []
        for s in result:
            s += carry
            digits.append(s % p)
            carry = s // p
        out = PAdicNumber(p=p, precision=prec, digits=tuple(digits))
        return _recompute_val(out)

    def __rmul__(self, other: int) -> "PAdicNumber":
        return self.__mul__(other)

    def __truediv__(self, other: "int | PAdicNumber") -> "PAdicNumber":
        other = self._coerce(other)
        inv = _padic_inverse(other)
        return self * inv

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PAdicNumber):
            return NotImplemented
        return self.p == other.p and self.digits == other.digits

    def __repr__(self) -> str:
        # Display as ...d_{k-1} ... d_1 d_0 (p-adic convention, LSD first)
        digs = "".join(str(d) for d in reversed(self.digits))
        return f"PAdicNumber({digs}|p={self.p})"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _recompute_val(x: PAdicNumber) -> PAdicNumber:
    """Return x with .val recomputed from digits."""
    v = x.precision
    for i, d in enumerate(x.digits):
        if d != 0:
            v = i
            break
    return PAdicNumber(p=x.p, precision=x.precision, digits=x.digits, val=v)


def _padic_inverse(x: PAdicNumber) -> PAdicNumber:
    """Compute the p-adic multiplicative inverse of x (requires val=0).

    Uses Newton's method: y_{n+1} = y_n * (2 - x * y_n) mod p^precision.
    Requires x.digits[0] != 0 (i.e., x is a p-adic unit).
    """
    if x.digits[0] == 0:
        raise ValueError(f"Cannot invert p-adic number with val > 0: {x}")

    p, prec = x.p, x.precision
    # Start with modular inverse of a_0 mod p
    a0 = x.digits[0]
    # Find y0 such that a0 * y0 ≡ 1 (mod p)
    y0_int = pow(int(a0), -1, p)
    y = PAdicNumber.from_int(y0_int, p, prec)

    # Newton iterations: each iteration doubles the number of correct digits
    two = PAdicNumber.from_int(2, p, prec)
    for _ in range(math.ceil(math.log2(prec + 1)) + 2):
        y = y * (two - x * y)

    return y


def _factorial_padic(n: int, p: int, precision: int) -> PAdicNumber:
    """Return n! as a PAdicNumber (for series coefficients)."""
    result = PAdicNumber.one(p, precision)
    for k in range(2, n + 1):
        result = result * PAdicNumber.from_int(k, p, precision)
    return result


def _padic_right_shift(x: PAdicNumber, v: int) -> PAdicNumber:
    """Divide x by p^v (right-shift digits, assumes v_p(x) >= v).

    Args:
        x: PAdicNumber with val >= v.
        v: Number of digit positions to shift right.

    Returns:
        PAdicNumber representing x / p^v.
    """
    if v <= 0:
        return x
    prec = x.precision
    if v >= prec:
        # Entirely shifted out — result is 0 (mod p^precision)
        return PAdicNumber.zero(x.p, prec)
    new_digits = x.digits[v:] + (0,) * v
    return _recompute_val(PAdicNumber(p=x.p, precision=prec, digits=new_digits))


def _padic_divide_by_int(x: PAdicNumber, n: int) -> PAdicNumber:
    """Divide PAdicNumber x by Python integer n in p-adic arithmetic.

    Works even when p | n, as long as v_p(x) >= v_p(n).
    Factors out p^v from n, right-shifts x by v, then divides by the unit part.

    Args:
        x: Numerator (PAdicNumber).
        n: Positive integer denominator.

    Returns:
        PAdicNumber x / n.

    Raises:
        ValueError: If v_p(n) > v_p(x) (result would not be a p-adic integer).
    """
    p, prec = x.p, x.precision
    v = valuation(n, p)
    if v > 0:
        if x.val < v:
            raise ValueError(
                f"Cannot divide: v_p(numerator)={x.val} < v_p(denominator)={v}"
            )
        x = _padic_right_shift(x, v)
        n = n // (p ** v)
    # Now n is a p-adic unit; divide via _padic_inverse
    unit = PAdicNumber.from_int(n % (p ** prec), p, prec)
    return x * _padic_inverse(unit)


# ── p-adic exp ────────────────────────────────────────────────────────────────

def padic_exp(x: PAdicNumber, terms: int = 12) -> PAdicNumber:
    """p-adic exponential: exp_p(x) = sum_{n=0}^{terms} x^n / n!

    Converges for |x|_p < p^(-1/(p-1)).  For p=2: |x|_2 < 1/2 (v_2(x) >= 2).

    Args:
        x:     p-adic number in the convergence disk.
        terms: Number of series terms (default: 12).

    Returns:
        PAdicNumber approximation of exp_p(x).

    Raises:
        ValueError: If x is likely outside the convergence radius.
    """
    p, prec = x.p, x.precision
    # Check convergence: for p=2 need val >= 2; for p odd need val >= 1
    min_val = 2 if p == 2 else 1
    if x.val < min_val and not all(d == 0 for d in x.digits):
        raise ValueError(
            f"padic_exp may not converge: |x|_p = {x.norm():.4f}, "
            f"p={p}, required |x|_p < p^(-1/(p-1)) = {p**(-1/(p-1)):.4f}. "
            f"Ensure v_p(x) >= {min_val}."
        )

    result = PAdicNumber.one(p, prec)
    x_power = PAdicNumber.one(p, prec)
    factorial_int = 1

    for n in range(1, terms + 1):
        x_power = x_power * x
        factorial_int *= n
        try:
            term = _padic_divide_by_int(x_power, factorial_int)
        except (ValueError, ZeroDivisionError):
            break
        result = result + term

    return result


# ── p-adic log ────────────────────────────────────────────────────────────────

def padic_log(x: PAdicNumber, terms: int = 15) -> PAdicNumber:
    """p-adic logarithm: log_p(x) = sum_{n=1}^{terms} (-1)^{n+1} (x-1)^n / n

    Converges for |x - 1|_p < 1.

    Args:
        x:     p-adic number with |x-1|_p < 1 (i.e., x ≡ 1 mod p).
        terms: Number of series terms (default: 15).

    Returns:
        PAdicNumber approximation of log_p(x).

    Raises:
        ValueError: If x is likely outside the convergence domain.
    """
    p, prec = x.p, x.precision
    one = PAdicNumber.one(p, prec)

    # Check: x must have digits[0] == 1 (x ≡ 1 mod p) for convergence
    if x.digits[0] != 1:
        raise ValueError(
            f"padic_log requires x ≡ 1 (mod p), but x.digits[0] = {x.digits[0]}. "
            f"Ensure |x - 1|_p < 1."
        )

    u = x - one  # u = x - 1; need |u|_p < 1
    result = PAdicNumber.zero(p, prec)
    u_power = PAdicNumber.one(p, prec)

    for n in range(1, terms + 1):
        u_power = u_power * u
        try:
            term = _padic_divide_by_int(u_power, n)
        except (ValueError, ZeroDivisionError):
            break
        if n % 2 == 1:
            result = result + term
        else:
            result = result - term

    return result


# ── p-adic EML ────────────────────────────────────────────────────────────────

def padic_eml(x: PAdicNumber, y: PAdicNumber) -> PAdicNumber:
    """p-adic EML operator: exp_p(x) - log_p(y).

    Requires:
      - x in convergence disk of padic_exp (|x|_p < p^(-1/(p-1)))
      - y ≡ 1 (mod p)  (so padic_log converges)

    Args:
        x: Left argument (exponent input).
        y: Right argument (logarithm input, must satisfy |y-1|_p < 1).

    Returns:
        PAdicNumber: padic_exp(x) - padic_log(y).

    Example::

        >>> from monogate.padic import PAdicNumber, padic_eml
        >>> p, prec = 3, 10
        >>> # Use x=0 (exp_3(0)=1), y=1 (log_3(1)=0) → eml(0,1) = 1 - 0 = 1
        >>> x = PAdicNumber.zero(p, prec)
        >>> y = PAdicNumber.one(p, prec)
        >>> r = padic_eml(x, y)
        >>> r.digits[0]   # should be 1
        1
    """
    if x.p != y.p or x.precision != y.precision:
        raise ValueError("padic_eml: x and y must have the same p and precision")
    return padic_exp(x) - padic_log(y)


# ── p-adic fixed points ────────────────────────────────────────────────────────

def padic_fixed_points(
    depth: int,
    p: int,
    precision: int = 8,
    n_candidates: int = 20,
) -> List[PAdicNumber]:
    """Find p-adic attractors of depth-k EML trees.

    Sweeps over candidate p-adic inputs x (where eml tree maps x→x),
    and returns those where |f(x) - x|_p < p^{-precision/2}.

    Specifically, tests the identity tree f(x) = padic_eml(x, x) for depth=1,
    and f(x) = padic_eml(padic_eml(x, x), padic_eml(x, x)) for depth=2, etc.

    Args:
        depth:        EML tree depth (1, 2, or 3).
        p:            Prime base.
        precision:    p-adic precision (number of digits).
        n_candidates: Number of integer candidates to sweep.

    Returns:
        List of PAdicNumber fixed points found.
    """
    fixed: List[PAdicNumber] = []
    seen: set = set()

    for n in range(n_candidates):
        # Build candidates as integers that satisfy convergence requirements:
        # For p=2: need val_2(x) >= 2, so multiples of 4
        # For p odd: need val_p(x) >= 1, so multiples of p
        if p == 2:
            x_int = n * 4
        else:
            x_int = n * p

        if x_int >= p ** precision:
            break

        try:
            x = PAdicNumber.from_int(x_int, p, precision)
            # y must satisfy |y-1|_p < 1, use one for testing
            y = PAdicNumber.one(p, precision)

            # Build depth-level EML tree evaluation
            result = _eval_padic_tree(x, y, depth)

            # Check fixed point: |f(x) - x|_p ≈ 0
            diff = result - x
            if diff.norm() < p ** (-(precision // 2)):
                key = tuple(x.digits)
                if key not in seen:
                    seen.add(key)
                    fixed.append(x)
        except (ValueError, ZeroDivisionError):
            continue

    return fixed


def _eval_padic_tree(
    x: PAdicNumber,
    y: PAdicNumber,
    depth: int,
) -> PAdicNumber:
    """Evaluate a depth-k EML tree on p-adic inputs x, y.

    depth=1: eml(x, y)
    depth=2: eml(eml(x, y), eml(x, y))
    depth=3: eml(eml(eml(x,y), eml(x,y)), eml(eml(x,y), eml(x,y)))
    """
    if depth <= 0:
        return x
    if depth == 1:
        return padic_eml(x, y)
    sub = _eval_padic_tree(x, y, depth - 1)
    return padic_eml(sub, sub)
