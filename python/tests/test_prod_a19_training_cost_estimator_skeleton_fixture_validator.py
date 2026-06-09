"""Tests for PROD-A19 private skeleton fixture validator."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

from monogate.training_cost_estimator_skeleton import build_hold_packet
from monogate.training_cost_estimator_skeleton_validator import validate_skeleton_hold_packet
from scripts.prod_a18_training_cost_estimator_non_executing_skeleton_implementation import SAMPLE_ACCEPTED_INPUT
from scripts.prod_a19_training_cost_estimator_skeleton_fixture_validator import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_skeleton_validator_accepts_clean_hold_packet():
    packet = build_hold_packet(SAMPLE_ACCEPTED_INPUT)
    result = validate_skeleton_hold_packet(packet)
    assert result.disposition == "accept"
    assert result.errors == ()
    assert result.accepted is True


def test_skeleton_validator_rejects_populated_cost_view():
    packet = build_hold_packet(SAMPLE_ACCEPTED_INPUT)
    packet["graph_cost_profile"] = {"estimate": 123}
    result = validate_skeleton_hold_packet(packet)
    assert result.disposition == "reject"
    assert "graph_cost_profile must remain null" in result.errors


def test_skeleton_validator_rejects_true_claim_flag():
    packet = build_hold_packet(SAMPLE_ACCEPTED_INPUT)
    packet["claim_flags"]["training_savings_claim"] = True
    result = validate_skeleton_hold_packet(packet)
    assert result.disposition == "reject"
    assert "training_savings_claim must be false" in result.errors


def test_skeleton_validator_rejects_missing_hold_reason_and_wrong_disposition():
    packet = build_hold_packet(SAMPLE_ACCEPTED_INPUT)
    mutated = copy.deepcopy(packet)
    mutated.pop("hold_reason")
    mutated["disposition"] = "estimate_ready"
    result = validate_skeleton_hold_packet(mutated)
    assert result.disposition == "reject"
    assert "hold_reason must be present" in result.errors
    assert "disposition must be hold_no_estimate" in result.errors


def test_prod_a19_consumes_a18_and_executes_skeleton_fixture_validator():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A19_TRAINING_COST_ESTIMATOR_SKELETON_FIXTURE_VALIDATOR_PASS"
    assert payload["sourceArtifact"] == "prod-a18-training-cost-estimator-non-executing-skeleton-implementation"
    assert summary["acceptedSkeletonFixtureCount"] == 1
    assert summary["rejectionSkeletonFixtureCount"] == 4
    assert summary["fixtureValidationResultCount"] == 5
    assert summary["matchedExpectationCount"] == 5
    assert summary["allFixtureExpectationsMatched"] is True


def test_prod_a19_records_accepted_and_rejection_results():
    payload = build_payload()
    assert all(row["actualDisposition"] == "accept" for row in payload["acceptedSkeletonFixtureResults"])
    assert all(row["actualDisposition"] == "reject" for row in payload["rejectionSkeletonFixtureResults"])
    assert all(row["errors"] for row in payload["rejectionSkeletonFixtureResults"])


def test_prod_a19_blocks_estimator_execution_public_runtime_and_accuracy_claims():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "estimateValuesProduced",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        assert summary[key] is False


def test_prod_a19_claim_flags_are_validator_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a19_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A19")
    assert "Accepted Skeleton Fixture Results" in report
    assert "Rejection Skeleton Fixture Results" in report


def test_prod_a19_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a19_training_cost_estimator_skeleton_fixture_validator.py",
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
    assert "PROD_A19_TRAINING_COST_ESTIMATOR_SKELETON_FIXTURE_VALIDATOR_OK" in proc.stdout
