"""Tests for PROD-A16 private training-cost estimator implementation gate selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a16_training_cost_estimator_implementation_gate_or_hold_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def action_by_id(payload, action_id: str):
    return next(action for action in payload["candidateActions"] if action["actionId"] == action_id)


def test_prod_a16_consumes_prod_a15_and_selects_skeleton_contract_path():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A16_TRAINING_COST_ESTIMATOR_IMPLEMENTATION_GATE_OR_HOLD_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "prod-a15-training-cost-io-contract-fixture-validator-implementation"
    assert summary["sourceMatchedExpectationCount"] == 6
    assert summary["sourceAllFixtureExpectationsMatched"] is True
    assert summary["selectedActionId"] == "private_estimator_skeleton_contract_seed"
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_prod_a16_records_gate_criteria():
    payload = build_payload()
    statuses = {item["criterionId"]: item["status"] for item in payload["gateCriteria"]}
    assert statuses == {
        "contract_fixture_validator_executed": "pass",
        "fixture_expectations_matched": "pass",
        "semantic_scope_limited": "bounded",
        "skeleton_before_execution": "required",
    }


def test_prod_a16_blocks_executing_estimator_and_public_docs():
    payload = build_payload()
    assert action_by_id(payload, "executing_estimator_implementation")["decision"] == "blocked"
    assert action_by_id(payload, "public_product_or_docs")["decision"] == "blocked"
    summary = payload["summary"]
    assert summary["executingEstimatorImplementationBlocked"] is True
    for key in [
        "estimatorSkeletonContractCreated",
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        assert summary[key] is False


def test_prod_a16_claim_flags_are_gate_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a16_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A16")
    assert "Gate Criteria" in report
    assert "Candidate Actions" in report


def test_prod_a16_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a16_training_cost_estimator_implementation_gate_or_hold_selector.py",
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
    assert "PROD_A16_TRAINING_COST_ESTIMATOR_IMPLEMENTATION_GATE_OR_HOLD_SELECTOR_OK" in proc.stdout
