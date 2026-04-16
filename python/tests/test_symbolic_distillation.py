"""Tests for monogate.frontiers.symbolic_distillation (Session 8)."""
import math
import pytest

pytest.importorskip("sklearn", reason="scikit-learn required")


def test_distillation_pipeline_returns_structure():
    """Smoke: pipeline runs on exp(x) and returns all expected keys."""
    from monogate.frontiers.symbolic_distillation import distillation_pipeline

    result = distillation_pipeline(
        math.exp,
        domain=(0.0, 2.5),
        name="test_exp",
        n_data=20,
        nn_max_iter=200,
        eml_n_simulations=200,
        seed=0,
    )
    required_keys = (
        "name", "domain",
        "direct_r2", "direct_formula",
        "distilled_r2", "distilled_formula",
        "nn_r2", "gain", "elapsed_s",
    )
    for key in required_keys:
        assert key in result, f"Missing key: {key}"
    assert result["name"] == "test_exp"
    assert result["elapsed_s"] > 0.0


def test_distillation_native_law_high_r2():
    """Boltzmann weight (exp(x)) achieves distilled R² > 0.9."""
    from monogate.frontiers.symbolic_distillation import distillation_pipeline

    result = distillation_pipeline(
        math.exp,
        domain=(0.0, 2.5),
        name="boltzmann",
        n_data=30,
        nn_max_iter=500,
        eml_n_simulations=500,
        seed=42,
    )
    assert result["distilled_r2"] > 0.9, (
        f"Expected distilled R² > 0.9 for exp(x), got {result['distilled_r2']}"
    )
