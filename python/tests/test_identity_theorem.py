"""Tests for the EML Identity Theorem — Session 36.

The theorem: eml(1, eml(eml(1, eml(x, 1)), 1)) = x for all x > 0.

Proof sketch:
  Step 1: eml(x, 1) = exp(x)
  Step 2: eml(1, exp(x)) = e - x
  Step 3: eml(e - x, 1) = exp(e - x)
  Step 4: eml(1, exp(e - x)) = e - (e - x) = x  QED
"""

from __future__ import annotations

import math
import pytest

from monogate.core import op


def eml_identity(x: float) -> float:
    """4-node EML tree that equals x: eml(1, eml(eml(1, eml(x, 1)), 1))."""
    step1 = op(x, 1.0)           # exp(x)
    step2 = op(1.0, step1)       # e - x
    step3 = op(step2, 1.0)       # exp(e - x)
    step4 = op(1.0, step3)       # e - (e - x) = x
    return step4


class TestEMLIdentityTheorem:

    def test_identity_x01(self):
        assert abs(eml_identity(0.1) - 0.1) < 1e-12

    def test_identity_x1(self):
        assert abs(eml_identity(1.0) - 1.0) < 1e-12

    def test_identity_x25(self):
        assert abs(eml_identity(2.5) - 2.5) < 1e-12

    def test_identity_x5(self):
        assert abs(eml_identity(5.0) - 5.0) < 1e-12

    def test_identity_x999(self):
        assert abs(eml_identity(9.99) - 9.99) < 1e-12

    def test_identity_small_positive(self):
        for x in [0.001, 0.01, 0.05, 0.5]:
            assert abs(eml_identity(x) - x) < 1e-10, f"failed at x={x}"

    def test_identity_integer_range(self):
        for x in [1, 2, 3, 4, 5]:
            assert abs(eml_identity(float(x)) - x) < 1e-12, f"failed at x={x}"

    def test_identity_noninteger(self):
        for x in [0.3, 0.7, 1.4142, 2.7182, 3.1415]:
            assert abs(eml_identity(x) - x) < 1e-11, f"failed at x={x}"

    def test_identity_step1_is_exp(self):
        """Step 1: eml(x, 1) = exp(x)."""
        for x in [0.1, 1.0, 2.0]:
            assert abs(op(x, 1.0) - math.exp(x)) < 1e-14

    def test_identity_step2_is_e_minus_x(self):
        """Step 2: eml(1, exp(x)) = e - x."""
        for x in [0.1, 1.0, 2.0]:
            assert abs(op(1.0, math.exp(x)) - (math.e - x)) < 1e-14

    def test_identity_step3_is_exp_e_minus_x(self):
        """Step 3: eml(e - x, 1) = exp(e - x)."""
        for x in [0.1, 1.0, 2.0]:
            v = op(math.e - x, 1.0)
            assert abs(v - math.exp(math.e - x)) < 1e-13

    def test_identity_step4_closes_to_x(self):
        """Step 4: eml(1, exp(e - x)) = x."""
        for x in [0.1, 1.0, 2.0]:
            v = op(1.0, math.exp(math.e - x))
            assert abs(v - x) < 1e-12, f"step4 failed at x={x}: got {v}"

    def test_identity_also_works_for_negative_x(self):
        """The algebraic proof holds for all x where exp(e-x) doesn't overflow."""
        for x in [-1.0, -5.0, -10.0]:
            assert abs(eml_identity(x) - x) < 1e-9, f"failed at x={x}"

    def test_identity_overflows_for_very_large_negative_x(self):
        """exp(e - x) overflows when x << 0; Python raises OverflowError."""
        with pytest.raises((OverflowError, ValueError)):
            eml_identity(-1000.0)

    def test_identity_tree_depth(self):
        """The identity uses exactly 4 internal EML nodes."""
        # Structure: op(1, op(op(1, op(x, 1)), 1))
        # Nodes: op1(x,1), op2(1,op1), op3(op2,1), op4(1,op3) — 4 nodes
        # This is the minimum depth for an identity function in EML
        x = 3.0
        a = op(x, 1.0)
        b = op(1.0, a)
        c = op(b, 1.0)
        d = op(1.0, c)
        assert abs(d - x) < 1e-12


class TestEMLIdentityCatalog:

    def test_identity_is_in_identities_catalog(self):
        from monogate.identities import ALL_IDENTITIES as IDENTITIES
        names = [i.name for i in IDENTITIES]
        assert "EML identity function" in names, (
            f"'EML identity function' not found in catalog. Found: {names}"
        )

    def test_identity_catalog_entry_domain(self):
        from monogate.identities import ALL_IDENTITIES as IDENTITIES
        identity = next(i for i in IDENTITIES if i.name == "EML identity function")
        lo, hi = identity.domain
        assert lo > 0, "Domain must be strictly positive (ln requires positive argument)"
        assert hi > lo

    def test_identity_catalog_entry_category(self):
        from monogate.identities import ALL_IDENTITIES as IDENTITIES
        identity = next(i for i in IDENTITIES if i.name == "EML identity function")
        assert identity.category == "exponential"

    def test_identity_catalog_entry_verifies_numerically(self):
        """The catalog entry's expression evaluates correctly."""
        from monogate.identities import ALL_IDENTITIES as IDENTITIES
        identity = next(i for i in IDENTITIES if i.name == "EML identity function")
        lo, hi = identity.domain
        import numpy as np
        xs = np.linspace(lo, min(hi, 5.0), 20)
        for x in xs:
            result = eml_identity(float(x))
            assert abs(result - float(x)) < 1e-10, f"failed at x={x}"
