"""Tests for PROD-A5 training cost estimator fixture/test next selector."""

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

from scripts.prod_a5_training_cost_estimator_fixture_next_selector import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def option_by_id(payload, option_id: str):
    return next(item for item in payload["nextActionOptions"] if item["optionId"] == option_id)


def test_prod_a5_consumes_prod_a4_and_selects_static_fixture_packet():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A5_TRAINING_COST_ESTIMATOR_FIXTURE_NEXT_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "prod-a4-training-cost-estimator-schema-validator-contract"
    assert summary["prodA4NextRecommendedArtifact"] == (
        "PROD-A5 training cost estimator validator contract fixture packet or executable validator test selector"
    )
    assert summary["selectedOptionId"] == "static_fixture_packet"
    assert summary["selectedNextArtifact"] == "PROD-A6 training cost estimator validator contract fixture packet"


def test_prod_a5_records_options_and_parks_executable_tests():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["optionCount"] == 3
    assert summary["staticFixturePacketSelected"] is True
    assert summary["executableValidatorTestsParked"] is True
    assert option_by_id(payload, "static_fixture_packet")["status"] == "selected"
    assert option_by_id(payload, "executable_validator_tests")["status"] == "parked_until_static_fixtures_exist"
    assert option_by_id(payload, "implementation_hold_gate")["status"] == "blocked_until_fixtures_and_tests_reviewed"


def test_prod_a5_records_selector_criteria_for_static_fixtures():
    payload = build_payload()
    assert payload["summary"]["selectorCriterionCount"] == 4
    assert {item["result"] for item in payload["selectorCriteria"]} == {"static_fixture_packet"}
    assert any(item["criterionId"] == "preserve_rejection_coverage" for item in payload["selectorCriteria"])


def test_prod_a5_does_not_create_fixtures_or_validator_tests():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "fixturePacketCreated",
        "schemaValidatorImplemented",
        "schemaValidatorExecuted",
        "executableValidatorTestsCreated",
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
    ]:
        assert summary[key] is False


def test_prod_a5_blocks_public_training_runtime_and_compiler_claims():
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


def test_prod_a5_respects_d109_hold_and_does_not_consume_review():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["d109HoldRespected"] is True
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert payload["claimFlags"]["d109_hold_respected"] is True
    assert payload["claimFlags"]["d110_started"] is False
    assert payload["claimFlags"]["reviewer_response_consumed"] is False


def test_prod_a5_claim_flags_are_selector_only():
    payload = build_payload()
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a5_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# PROD-A5")


def test_prod_a5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a5_training_cost_estimator_fixture_next_selector.py",
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
    assert "PROD_A5_TRAINING_COST_ESTIMATOR_FIXTURE_NEXT_SELECTOR_OK" in proc.stdout
