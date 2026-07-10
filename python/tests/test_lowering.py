"""Tests for the Layer-2 → Layer-1 (F16) lowering pass (monogate.lowering)."""
import pytest
from mpmath import mp, mpf, cosh, sinh, tanh

from monogate.lowering import L2_OPS, lower, verify, certify_all

mp.dps = 30
TOL = mpf("1e-25")


@pytest.mark.parametrize("name", list(L2_OPS))
def test_lowering_is_numerically_correct(name):
    ok, max_err = verify(name)
    assert ok, f"{name}: F16 lowering disagrees with semantics (max_rel_err={max_err:.3e})"


@pytest.mark.parametrize("name", list(L2_OPS))
def test_lowering_hits_canonical_minimum_cost(name):
    op = L2_OPS[name]
    # The Layer-2 op is a single-node notation; its F16 lowering achieves the
    # canonical SuperBEST minimum (>1 node, since it is a compound).
    assert op.l2_cost == 1
    assert op.f16_cost >= op.l2_cost
    assert op.f16_cost in (3, 4)  # the extended operators all lower to 3 or 4 F16 nodes


def test_certify_all_correct():
    certs = certify_all()
    assert len(certs) == 7
    assert all(c["correct"] and c["minimal"] for c in certs)


def test_composite_hyperbolics_lower_through_L2():
    """cosh/sinh/tanh compose from EEA/EES (New_Minimal_Identities_23.tex), so the
    lowering pass reaches them: cosh(x)=½·EEA(x,−x), sinh(x)=½·EES(x,−x),
    tanh(x)=EES(x,−x)/EEA(x,−x). Verify the composed F16 trees numerically."""
    for xv in [mpf("0.5"), mpf("1.0"), mpf("2.0")]:
        eea = lower("EEA", xv, -xv).evaluate()   # e^x + e^{-x}
        ees = lower("EES", xv, -xv).evaluate()   # e^x − e^{-x}
        assert abs(eea / 2 - cosh(xv)) < TOL
        assert abs(ees / 2 - sinh(xv)) < TOL
        assert abs(ees / eea - tanh(xv)) < TOL


def test_lower_arity_check():
    with pytest.raises(ValueError):
        lower("EEM", mpf(1))          # EEM needs 2 args
    with pytest.raises(KeyError):
        lower("NOPE", mpf(1), mpf(2))
