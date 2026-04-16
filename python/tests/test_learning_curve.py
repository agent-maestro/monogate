"""Tests for monogate.frontiers.learning_curve."""
import pytest


def test_run_returns_structure():
    """Smoke test: result has required structure."""
    from monogate.frontiers.learning_curve import run_learning_curve

    result = run_learning_curve(n_identities=5, n_runs=1, seed=0, enable_learning=False)

    assert result["learning_enabled"] is False
    assert result["n_identities"] == 5
    assert result["n_runs"] == 1
    assert len(result["runs"]) == 1

    run = result["runs"][0]
    assert "run_idx" in run
    assert "proofs" in run
    assert len(run["proofs"]) == 5

    proof = run["proofs"][0]
    for key in ("pos", "name", "elapsed_s", "proved"):
        assert key in proof, f"Missing key: {key}"


def test_analyze_keys_present():
    """analyze_learning_curve returns all required keys."""
    from monogate.frontiers.learning_curve import run_learning_curve, analyze_learning_curve

    result = run_learning_curve(n_identities=8, n_runs=2, seed=1, enable_learning=False)
    analysis = analyze_learning_curve(result)

    required = {
        "mean_by_position",
        "std_by_position",
        "first_quarter_mean",
        "last_quarter_mean",
        "improvement_ratio",
        "rolling_mean",
        "prove_rate",
        "window",
    }
    missing = required - set(analysis.keys())
    assert not missing, f"Missing keys: {missing}"

    assert len(analysis["mean_by_position"]) == 8
    assert len(analysis["std_by_position"]) == 8


def test_improvement_ratio_is_positive():
    """improvement_ratio must always be > 0."""
    from monogate.frontiers.learning_curve import run_learning_curve, analyze_learning_curve

    result = run_learning_curve(n_identities=10, n_runs=1, seed=7, enable_learning=False)
    analysis = analyze_learning_curve(result)

    assert analysis["improvement_ratio"] > 0.0, (
        f"improvement_ratio is {analysis['improvement_ratio']}"
    )
