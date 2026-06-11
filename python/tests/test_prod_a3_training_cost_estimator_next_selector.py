"""Tests for PROD-A3 training cost estimator next-action selector."""

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

from scripts.prod_a3_training_cost_estimator_next_selector import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def option_by_id(payload, option_id: str):
    return next(item for item in payload["nextActionOptions"] if item["optionId"] == option_id)


def test_prod_a3_consumes_prod_a2_and_selects_schema_validator_path():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A3_TRAINING_COST_ESTIMATOR_NEXT_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "prod-a2-training-cost-estimator-private-spec"
    assert summary["prodA2NextRecommendedArtifact"] == (
        "PROD-A3 training cost estimator schema validator or example packet selector"
    )
    assert summary["selectedOptionId"] == "schema_validator"
    assert summary["selectedNextArtifact"] == "PROD-A4 training cost estimator schema validator contract"


def test_prod_a3_records_three_options_and_parks_later_paths():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["optionCount"] == 3
    assert option_by_id(payload, "schema_validator")["status"] == "selected"
    assert option_by_id(payload, "example_packet")["status"] == "parked_until_schema_contract_exists"
    assert option_by_id(payload, "implementation_hold_gate")["status"] == "blocked_until_schema_and_examples_reviewed"


def test_prod_a3_records_selector_criteria_for_schema_validator():
    payload = build_payload()
    assert payload["summary"]["selectorCriterionCount"] == 4
    assert {item["result"] for item in payload["selectorCriteria"]} == {"schema_validator"}
    assert any(item["criterionId"] == "preserve_caveat_carriage" for item in payload["selectorCriteria"])


def test_prod_a3_does_not_implement_validator_estimator_or_examples():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "schemaValidatorImplemented",
        "examplePacketCreated",
        "implementationHoldGateCreated",
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
    ]:
        assert summary[key] is False


def test_prod_a3_blocks_public_training_runtime_and_compiler_claims():
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


def test_prod_a3_respects_d109_hold_and_does_not_consume_review():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["d109HoldRespected"] is True
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert payload["claimFlags"]["d109_hold_respected"] is True
    assert payload["claimFlags"]["d110_started"] is False
    assert payload["claimFlags"]["reviewer_response_consumed"] is False


def test_prod_a3_claim_flags_are_selector_only():
    payload = build_payload()
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a3_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# PROD-A3")


def test_prod_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a3_training_cost_estimator_next_selector.py",
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
    assert "PROD_A3_TRAINING_COST_ESTIMATOR_NEXT_SELECTOR_OK" in proc.stdout
