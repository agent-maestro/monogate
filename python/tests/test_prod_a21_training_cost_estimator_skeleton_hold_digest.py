"""Tests for PROD-A21 private training-cost estimator skeleton hold digest."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a21_training_cost_estimator_skeleton_hold_digest import (
    BLOCKED_CLAIMS,
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_prod_a21_consumes_a20_and_holds_training_cost_lane():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A21_TRAINING_COST_ESTIMATOR_SKELETON_HOLD_DIGEST_PASS"
    assert payload["sourceArtifact"] == "prod-a20-training-cost-estimator-skeleton-review-or-hold-selector"
    assert summary["sourceSelectedActionId"] == "private_skeleton_hold_digest"
    assert summary["trainingCostEstimatorLaneHeld"] is True
    assert summary["skeletonHoldDigestCreated"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_prod_a21_lane_state_rows_record_skeleton_and_blocked_estimator():
    payload = build_payload()
    states = {row["rowId"]: row["state"] for row in payload["laneStateRows"]}
    assert states == {
        "skeleton_module": "implemented_private_non_executing",
        "skeleton_validator": "implemented_and_executed_private_structural",
        "review_selector": "hold_selected",
        "estimator_behavior": "blocked",
    }
    assert payload["summary"]["laneStateRowCount"] == 4


def test_prod_a21_blocked_actions_and_reopen_conditions_are_bounded():
    payload = build_payload()
    action_statuses = {action["actionId"]: action["status"] for action in payload["blockedActions"]}
    assert action_statuses["open_estimator_implementation_gate"] == "blocked"
    assert action_statuses["execute_estimator"] == "blocked"
    assert action_statuses["publish_product_or_docs"] == "blocked"
    assert action_statuses["continue_fixture_expansion"] == "parked"
    condition_statuses = {condition["conditionId"]: condition["status"] for condition in payload["reopenConditions"]}
    assert condition_statuses == {
        "explicit_bounded_user_request": "allowed_reopen_trigger",
        "actual_private_reviewer_approval": "allowed_reopen_trigger",
        "estimate_value_contract_and_calibration_plan": "required_before_estimator_gate",
        "public_launch_impulse": "blocked_reopen_trigger",
    }


def test_prod_a21_blocked_claims_are_recorded():
    payload = build_payload()
    assert payload["summary"]["blockedClaimCount"] == len(BLOCKED_CLAIMS)
    assert set(payload["blockedClaims"]) == set(BLOCKED_CLAIMS)
    assert "estimator accuracy" in payload["blockedClaims"]
    assert "broad EML advantage" in payload["blockedClaims"]


def test_prod_a21_blocks_estimator_execution_public_runtime_and_accuracy_claims():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "estimatorImplementationGateOpened",
        "estimatorImplemented",
        "estimatorExecuted",
        "estimateValuesProduced",
        "estimateValuesValidated",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        assert summary[key] is False


def test_prod_a21_claim_flags_are_digest_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a21_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A21")
    assert "Lane State Rows" in report
    assert "Blocked Actions" in report
    assert "Reopen Conditions" in report
    assert "Blocked Claims" in report


def test_prod_a21_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a21_training_cost_estimator_skeleton_hold_digest.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--command-feed-dir",
            str(tmp_path / "feeds"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "PROD_A21_TRAINING_COST_ESTIMATOR_SKELETON_HOLD_DIGEST_OK" in proc.stdout
