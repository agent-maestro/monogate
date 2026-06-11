"""Tests for PROD-A6 training cost estimator fixture packet."""

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

from scripts.prod_a6_training_cost_estimator_fixture_packet import (
    CLAIM_FLAGS,
    REQUIRED_BLOCKED_CLAIMS,
    REQUIRED_CAVEATS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def fixture_by_id(fixtures, fixture_id: str):
    return next(item for item in fixtures if item["fixtureId"] == fixture_id)


def test_prod_a6_consumes_prod_a5_and_creates_static_fixtures():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A6_TRAINING_COST_ESTIMATOR_FIXTURE_PACKET_PASS"
    assert payload["sourceArtifact"] == "prod-a5-training-cost-estimator-fixture-next-selector"
    assert summary["prodA5SelectedOptionId"] == "static_fixture_packet"
    assert summary["prodA5SelectedNextArtifact"] == "PROD-A6 training cost estimator validator contract fixture packet"
    assert summary["fixturePacketCreated"] is True
    assert summary["acceptedFixturesCreated"] is True
    assert summary["rejectionFixturesCreated"] is True


def test_prod_a6_records_two_accepted_fixtures_with_required_caveats_and_blocked_claims():
    payload = build_payload()
    assert payload["summary"]["acceptedFixtureCount"] == 2
    static = fixture_by_id(payload["acceptedFixtures"], "accepted_static_expression_cost_shape")["packet"]
    budget = fixture_by_id(payload["acceptedFixtures"], "accepted_training_budget_context_shape")["packet"]
    assert static["calibration_caveats"] == REQUIRED_CAVEATS
    assert static["blocked_claims"] == REQUIRED_BLOCKED_CLAIMS
    assert static["static_expression_cost"] is not None
    assert budget["training_budget_context"] is not None
    assert all(value is False for value in static["claim_flags"].values())
    assert all(value is False for value in budget["claim_flags"].values())


def test_prod_a6_records_five_rejection_fixtures_from_a4_contract():
    payload = build_payload()
    assert payload["summary"]["rejectionFixtureCount"] == 5
    assert "blocked_claims" not in fixture_by_id(payload["rejectionFixtures"], "missing_blocked_claims")["packet"]
    assert "calibration_caveats" not in fixture_by_id(payload["rejectionFixtures"], "missing_calibration_caveats")["packet"]
    all_null = fixture_by_id(payload["rejectionFixtures"], "all_cost_views_null")["packet"]
    assert all_null["static_expression_cost"] is None
    assert all_null["graph_cost_profile"] is None
    assert all_null["training_budget_context"] is None
    assert fixture_by_id(payload["rejectionFixtures"], "training_savings_true")["packet"]["claim_flags"][
        "training_savings_claim"
    ] is True
    assert fixture_by_id(payload["rejectionFixtures"], "public_product_ready_true")["packet"]["claim_flags"][
        "public_product_ready"
    ] is True


def test_prod_a6_selects_shared_toolkit_as_next_artifact():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["sharedToolkitNextSelected"] is True
    assert summary["nextRecommendedArtifact"] == "EA-A1 shared evidence artifact toolkit seed"


def test_prod_a6_does_not_implement_validator_or_estimator():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "schemaValidatorImplemented",
        "schemaValidatorExecuted",
        "executableValidatorTestsCreated",
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
    ]:
        assert summary[key] is False


def test_prod_a6_blocks_public_training_runtime_and_compiler_claims():
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


def test_prod_a6_respects_d109_hold_and_does_not_consume_review():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["d109HoldRespected"] is True
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert payload["claimFlags"]["d109_hold_respected"] is True
    assert payload["claimFlags"]["d110_started"] is False
    assert payload["claimFlags"]["reviewer_response_consumed"] is False


def test_prod_a6_claim_flags_are_fixture_packet_only():
    payload = build_payload()
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a6_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# PROD-A6")


def test_prod_a6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a6_training_cost_estimator_fixture_packet.py",
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
    assert "PROD_A6_TRAINING_COST_ESTIMATOR_FIXTURE_PACKET_OK" in proc.stdout
