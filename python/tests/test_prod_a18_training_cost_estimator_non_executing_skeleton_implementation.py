"""Tests for PROD-A18 private non-executing training-cost estimator skeleton."""

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

from monogate.training_cost_estimator_skeleton import (
    NULL_COST_VIEW_FIELDS,
    REQUIRED_FALSE_CLAIM_FLAGS,
    TrainingCostEstimatorSkeleton,
    build_hold_packet,
    validate_input_shape,
)
from scripts.prod_a18_training_cost_estimator_non_executing_skeleton_implementation import (
    CLAIM_FLAGS,
    SAMPLE_ACCEPTED_INPUT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_skeleton_validates_input_shape_without_estimate_semantics():
    accepted = validate_input_shape(SAMPLE_ACCEPTED_INPUT)
    rejected = validate_input_shape({"workload_id": "only-one-field"})
    assert accepted.disposition == "accept_input_shape"
    assert accepted.missing_fields == ()
    assert rejected.disposition == "reject_input_shape"
    assert "expression_ref" in rejected.missing_fields


def test_skeleton_hold_packet_nulls_every_cost_view_and_keeps_flags_false():
    packet = build_hold_packet(SAMPLE_ACCEPTED_INPUT)
    assert packet["disposition"] == "hold_no_estimate"
    assert packet["hold_reason"]
    for field in NULL_COST_VIEW_FIELDS:
        assert packet[field] is None
    assert set(packet["claim_flags"]) == set(REQUIRED_FALSE_CLAIM_FLAGS)
    assert all(value is False for value in packet["claim_flags"].values())
    assert "estimate" not in json.dumps(
        {
            field: packet[field]
            for field in NULL_COST_VIEW_FIELDS
        }
    )


def test_skeleton_class_has_no_estimate_producing_api():
    skeleton = TrainingCostEstimatorSkeleton()
    public_names = {name for name in dir(skeleton) if not name.startswith("_")}
    assert "hold_packet" in public_names
    assert "estimate" not in public_names
    assert "predict" not in public_names
    assert "benchmark" not in public_names
    assert skeleton.hold_packet(SAMPLE_ACCEPTED_INPUT)["disposition"] == "hold_no_estimate"


def test_prod_a18_consumes_a17_and_records_private_skeleton_implementation():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A18_TRAINING_COST_ESTIMATOR_NON_EXECUTING_SKELETON_IMPLEMENTATION_PASS"
    assert payload["sourceArtifact"] == "prod-a17-training-cost-estimator-skeleton-contract-seed"
    assert summary["sourceModulePath"] == "python/monogate/training_cost_estimator_skeleton.py"
    assert summary["implementedModulePath"] == summary["sourceModulePath"]
    assert summary["estimatorSkeletonImplemented"] is True
    assert summary["nonExecutingHoldPacketImplemented"] is True
    assert summary["inputShapeValidationImplemented"] is True


def test_prod_a18_smoke_rows_are_non_executing_and_value_free():
    payload = build_payload()
    assert payload["summary"]["smokeFixtureCount"] == 4
    assert payload["summary"]["holdPacketSmokeExecuted"] is True
    assert payload["summary"]["blockedImportsAbsent"] is True
    assert payload["moduleImportScan"]["blockedImportsObserved"] == []
    for row in payload["skeletonSmokeRows"]:
        assert row["estimateValuesProduced"] is False
        if row["fixtureId"].startswith("hold_packet"):
            assert row["disposition"] == "hold_no_estimate"
            assert row["nullCostViewFields"] == list(NULL_COST_VIEW_FIELDS)
            assert set(row["falseClaimFlags"]) == set(REQUIRED_FALSE_CLAIM_FLAGS)


def test_prod_a18_blocks_estimator_execution_public_runtime_and_accuracy_claims():
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


def test_prod_a18_claim_flags_are_skeleton_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a18_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A18")
    assert "Smoke Rows" in report
    assert "Blocked Imports" in report


def test_prod_a18_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a18_training_cost_estimator_non_executing_skeleton_implementation.py",
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
    assert "PROD_A18_TRAINING_COST_ESTIMATOR_NON_EXECUTING_SKELETON_IMPLEMENTATION_OK" in proc.stdout
