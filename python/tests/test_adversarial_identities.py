"""Tests for monogate.frontiers.adversarial_identities."""
import pytest


def test_expand_trig_changes_string():
    """expand_trig should transform sin(2*x) into something different."""
    pytest.importorskip("sympy", reason="sympy required for adversarial tests")

    from monogate.frontiers.adversarial_identities import AdversarialGenerator

    gen = AdversarialGenerator()
    original = "sin(2*x) == 2*sin(x)*cos(x)"
    result = gen.expand_trig(original)

    # sympy is present — transformation should produce different string
    assert result != original, (
        f"expand_trig returned unchanged string: {result!r}"
    )


def test_measure_gap_runs():
    """measure_gap executes without error on a trivially true identity."""
    from monogate.prover import EMLProverV2
    from monogate.frontiers.adversarial_identities import measure_gap

    prover = EMLProverV2(enable_learning=False)
    result = measure_gap(prover, "exp(x)", "exp(x)")

    assert "gap_ratio" in result
    assert "original_elapsed_s" in result
    assert "adversarial_elapsed_s" in result
    assert result["gap_ratio"] > 0.0
    # Same expression — gap ratio should be very close to 1.0
    assert 0.1 < result["gap_ratio"] < 10.0
