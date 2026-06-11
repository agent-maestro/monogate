"""Tests for PROD-A17 private training-cost estimator skeleton contract seed."""

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

from scripts.prod_a17_training_cost_estimator_skeleton_contract_seed import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_prod_a17_consumes_a16_and_creates_non_executing_contract():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A17_TRAINING_COST_ESTIMATOR_SKELETON_CONTRACT_SEED_PASS"
    assert payload["sourceArtifact"] == "prod-a16-training-cost-estimator-implementation-gate-or-hold-selector"
    assert summary["sourceSelectedActionId"] == "private_estimator_skeleton_contract_seed"
    assert summary["estimatorSkeletonContractCreated"] is True
    assert summary["holdDisposition"] == "hold_no_estimate"


def test_prod_a17_records_module_and_api_boundaries():
    payload = build_payload()
    assert payload["moduleBoundary"]["modulePath"] == "python/monogate/training_cost_estimator_skeleton.py"
    assert "torch" in payload["moduleBoundary"]["blockedImports"]
    assert payload["summary"]["apiBoundaryCount"] == 3
    api_ids = {item["apiId"] for item in payload["apiBoundaries"]}
    assert api_ids == {"TrainingCostEstimatorSkeleton", "build_hold_packet", "validate_input_shape"}


def test_prod_a17_hold_behavior_blocks_estimate_values():
    payload = build_payload()
    hold = payload["holdBehavior"]
    assert hold["requiredDisposition"] == "hold_no_estimate"
    assert hold["requiredOutputNulls"] == [
        "static_expression_cost",
        "graph_cost_profile",
        "training_budget_context",
    ]
    assert "training_savings_claim" in hold["requiredFalseClaimFlags"]
    assert "estimator_accuracy_claim" in hold["requiredFalseClaimFlags"]


def test_prod_a17_records_skeleton_contract_fixtures():
    payload = build_payload()
    assert payload["summary"]["skeletonContractFixtureCount"] == 4
    assert payload["summary"]["acceptedSkeletonFixtureCount"] == 1
    assert payload["summary"]["rejectionSkeletonFixtureCount"] == 3
    dispositions = {fixture["fixtureId"]: fixture["expectedDisposition"] for fixture in payload["skeletonContractFixtures"]}
    assert dispositions["accepted_hold_packet_shape"] == "accept_skeleton_hold_shape"
    assert dispositions["reject_estimate_values_present"] == "reject_skeleton_shape"


def test_prod_a17_blocks_skeleton_implementation_estimator_execution_and_public_claims():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "estimatorSkeletonImplemented",
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


def test_prod_a17_claim_flags_are_contract_seed_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a17_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A17")
    assert "API Boundaries" in report
    assert "Skeleton Fixtures" in report


def test_prod_a17_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a17_training_cost_estimator_skeleton_contract_seed.py",
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
    assert "PROD_A17_TRAINING_COST_ESTIMATOR_SKELETON_CONTRACT_SEED_OK" in proc.stdout
