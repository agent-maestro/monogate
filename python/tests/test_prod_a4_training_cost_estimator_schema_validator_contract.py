"""Tests for PROD-A4 training cost estimator schema validator contract."""

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

from scripts.prod_a4_training_cost_estimator_schema_validator_contract import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def item_by_id(items, key: str, value: str):
    return next(item for item in items if item[key] == value)


def test_prod_a4_consumes_prod_a3_schema_validator_selection():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A4_TRAINING_COST_ESTIMATOR_SCHEMA_VALIDATOR_CONTRACT_PASS"
    assert payload["sourceArtifact"] == "prod-a3-training-cost-estimator-next-selector"
    assert summary["prodA3SelectedOptionId"] == "schema_validator"
    assert summary["prodA3SelectedNextArtifact"] == "PROD-A4 training cost estimator schema validator contract"
    assert summary["schemaValidatorContractCreated"] is True


def test_prod_a4_records_required_fields_and_validation_obligations():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["requiredFieldCount"] == 8
    assert summary["validationObligationCount"] == 6
    assert item_by_id(payload["requiredPacketFields"], "field", "blocked_claims")["required"] is True
    assert item_by_id(payload["validationObligations"], "obligationId", "blocked_claims_required")[
        "severity"
    ] == "reject_if_missing"


def test_prod_a4_records_rejection_fixtures_and_reviewer_questions():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["rejectionFixtureCount"] == 5
    assert summary["reviewerQuestionCount"] == 3
    assert item_by_id(payload["rejectionFixtures"], "fixtureId", "training_savings_true")["reason"]
    assert item_by_id(payload["nextReviewerQuestions"], "questionId", "a5_path")["question"]


def test_prod_a4_does_not_implement_validator_estimator_or_examples():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "schemaValidatorImplemented",
        "schemaValidatorExecuted",
        "examplePacketCreated",
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
    ]:
        assert summary[key] is False


def test_prod_a4_blocks_public_training_runtime_and_compiler_claims():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "hardwareReadinessClaim",
        "siliconReadinessClaim",
        "broadEmlAdvantageClaim",
    ]:
        assert summary[key] is False


def test_prod_a4_respects_d109_hold_and_does_not_consume_review():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["d109HoldRespected"] is True
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert payload["claimFlags"]["d109_hold_respected"] is True
    assert payload["claimFlags"]["d110_started"] is False
    assert payload["claimFlags"]["reviewer_response_consumed"] is False


def test_prod_a4_claim_flags_are_contract_only():
    payload = build_payload()
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a4_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# PROD-A4")


def test_prod_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a4_training_cost_estimator_schema_validator_contract.py",
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
    assert "PROD_A4_TRAINING_COST_ESTIMATOR_SCHEMA_VALIDATOR_CONTRACT_OK" in proc.stdout
