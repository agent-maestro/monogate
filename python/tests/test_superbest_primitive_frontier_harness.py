"""Tests for the bounded SuperBEST primitive frontier harness."""

from __future__ import annotations

import json
import subprocess
import sys

from scripts.superbest_primitive_frontier_harness import evaluate_candidate, run_harness, CANDIDATES


def candidate(candidate_id: str):
    return next(item for item in CANDIDATES if item.candidate_id == candidate_id)


def test_mul_positive_route_confirms_existing_route():
    result = evaluate_candidate(candidate("mul_positive_1n_route"))
    assert result["empirical_pass"] is True
    assert result["classification"] == "CONFIRMED_EXISTING_ROUTE"
    assert result["failure_count"] == 0


def test_mul_general_positive_route_attempt_fails_on_negative_domain():
    result = evaluate_candidate(candidate("mul_general_positive_route_attempt"))
    assert result["empirical_pass"] is False
    assert result["classification"] == "INVALID_OR_DOMAIN_LIMITED"
    assert result["failure_count"] > 0
    assert any(row["inputs"][0] < 0 for row in result["first_failures"])


def test_div_general_positive_route_attempt_fails_on_negative_domain():
    result = evaluate_candidate(candidate("div_general_positive_route_attempt"))
    assert result["empirical_pass"] is False
    assert result["classification"] == "INVALID_OR_DOMAIN_LIMITED"
    assert result["failure_count"] > 0


def test_branched_references_are_not_single_tree_improvements():
    result = evaluate_candidate(candidate("mul_general_sign_branched_reference"))
    assert result["empirical_pass"] is True
    assert result["single_tree"] is False
    assert result["classification"] == "BRANCHED_REFERENCE_ONLY"


def test_add_sub_neg_confirm_existing_routes():
    for candidate_id in ["add_general_2n_route", "sub_general_2n_route", "neg_general_2n_route"]:
        result = evaluate_candidate(candidate(candidate_id))
        assert result["empirical_pass"] is True
        assert result["classification"] == "CONFIRMED_EXISTING_ROUTE"


def test_harness_finds_no_primitive_row_improvements():
    payload = run_harness()
    assert payload["status"] == "SUPERBEST_PRIMITIVE_FRONTIER_HARNESS_COMPLETE"
    assert payload["primitive_improvement_candidate_count"] == 0
    assert payload["row_frontier_notes"]["mul_general"]["status"] == "BLOCKED_BY_SIGN_DOMAIN"
    assert payload["row_frontier_notes"]["div_general"]["status"] == "BLOCKED_BY_NUMERATOR_SIGN_DOMAIN"


def test_harness_preserves_boundaries():
    payload = run_harness()
    assert payload["boundary"]["canonical_row_table_changed"] is False
    assert payload["boundary"]["new_row_optimality_claim"] is False
    assert payload["boundary"]["public_theorem_claim"] is False
    assert payload["boundary"]["open_problem_solved_claim"] is False


def test_harness_cli_writes_json(tmp_path):
    out_json = tmp_path / "primitive.json"
    out_report = tmp_path / "primitive.md"
    subprocess.run(
        [
            sys.executable,
            "python/scripts/superbest_primitive_frontier_harness.py",
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
    assert payload["primitive_improvement_candidate_count"] == 0
    assert out_report.exists()
