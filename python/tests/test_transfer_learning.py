"""Tests for monogate.frontiers.transfer_learning."""
import pytest


def test_single_pair_runs():
    """Smoke test: run_transfer_experiment returns required structure."""
    from monogate.frontiers.transfer_learning import run_transfer_experiment

    result = run_transfer_experiment(
        "trig", "hyperbolic",
        n_runs=1,
        max_train=3,
        max_test=3,
    )

    assert result["train_category"] == "trig"
    assert result["test_category"] == "hyperbolic"
    assert len(result["runs"]) == 1

    agg = result["aggregate"]
    for key in ("baseline_mean", "transfer_mean", "transfer_benefit", "transfer_helps"):
        assert key in agg, f"Missing aggregate key: {key}"

    assert agg["transfer_benefit"] > 0.0


def test_diagonal_is_one():
    """compute_transfer_matrix diagonal entries must be 1.0."""
    from monogate.frontiers.transfer_learning import compute_transfer_matrix

    result = compute_transfer_matrix(n_runs=1, max_train=2, max_test=2)
    matrix = result["matrix"]
    cats = result["categories"]

    for cat in cats:
        assert matrix[cat][cat] == 1.0, (
            f"Diagonal [{cat}][{cat}] = {matrix[cat][cat]}, expected 1.0"
        )
