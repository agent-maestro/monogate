"""Tests for the SuperBEST expression frontier exploration."""

from __future__ import annotations

import json
import subprocess
import sys

from scripts.superbest_expression_frontier import FRONTIER_CASES, run_frontier


def test_frontier_covers_target_families():
    payload = run_frontier()
    assert payload["case_count"] == len(FRONTIER_CASES)
    assert set(payload["families"]) == {
        "polynomial_basis_reuse",
        "rational_shared_denominator",
        "sigmoid_logistic",
        "softmax_attention",
    }


def test_softmax_attention_is_top_frontier_in_current_suite():
    payload = run_frontier()
    assert payload["best_case_id"] == "attention_three_logits_three_outputs"
    assert payload["max_extra_superbest_savings_nodes"] == 26
    assert payload["family_summary"]["softmax_attention"]["max_extra_superbest_savings_nodes"] == 26


def test_logistic_and_rational_frontiers_have_positive_savings():
    payload = run_frontier()
    families = payload["family_summary"]
    assert families["sigmoid_logistic"]["max_extra_superbest_savings_nodes"] >= 10
    assert families["rational_shared_denominator"]["max_extra_superbest_savings_nodes"] >= 6
    assert families["polynomial_basis_reuse"]["max_extra_superbest_savings_nodes"] >= 4


def test_frontier_preserves_boundary_flags():
    payload = run_frontier()
    assert payload["boundary"]["expression_level_only"] is True
    assert payload["boundary"]["canonical_row_table_changed"] is False
    assert payload["boundary"]["new_row_optimality_claim"] is False
    assert payload["boundary"]["public_theorem_claim"] is False
    assert payload["boundary"]["open_problem_solved_claim"] is False
    assert payload["boundary"]["compiler_integration_implemented"] is False


def test_frontier_cli_writes_json(tmp_path):
    out_json = tmp_path / "frontier.json"
    out_report = tmp_path / "frontier.md"
    subprocess.run(
        [
            sys.executable,
            "python/scripts/superbest_expression_frontier.py",
            "--out-json",
            str(out_json),
            "--out-report",
            str(out_report),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(out_json.read_text())
    assert payload["status"] == "SUPERBEST_EXPRESSION_FRONTIER_COMPLETE"
    assert out_report.exists()
