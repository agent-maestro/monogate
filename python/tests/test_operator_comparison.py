"""Tests for monogate.frontiers.operator_comparison (Session 7)."""
import pytest


def test_barrier_analysis_runs():
    """Smoke: barrier analysis runs on 2 operators without error."""
    from monogate.frontiers.operator_comparison import barrier_analysis

    result = barrier_analysis(operators=["EML", "EDL"])
    assert "EML" in result
    assert "EDL" in result
    for op in ("EML", "EDL"):
        assert "best_mse" in result[op]
        assert "blocked" in result[op]
        assert result[op]["blocked"] is True
        assert result[op]["best_mse"] >= 0.0


def test_node_count_table_has_physics():
    """Extended node-count table includes exp(-x) row with EML=None (blocked)."""
    from monogate.frontiers.operator_comparison import PHYSICS_NODE_COUNTS

    assert "exp(-x)" in PHYSICS_NODE_COUNTS
    # EML cannot represent exp(-x)
    assert PHYSICS_NODE_COUNTS["exp(-x)"].get("EML") is None
    # EDL also blocked
    assert PHYSICS_NODE_COUNTS["exp(-x)"].get("EDL") is None
    # exp(x) is representable in EML (1 node)
    assert "exp(x)" in PHYSICS_NODE_COUNTS
    assert PHYSICS_NODE_COUNTS["exp(x)"]["EML"] == 1
