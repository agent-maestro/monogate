"""Tests for PROD-A11 private training-cost estimator fixture validator implementation."""

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

from monogate.training_cost_validator import validate_training_cost_fixture_packet
from scripts.prod_a11_training_cost_estimator_fixture_validator_implementation import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)
from scripts.prod_a6_training_cost_estimator_fixture_packet import accepted_fixtures


def test_validator_accepts_prod_a6_static_fixture_shape():
    result = validate_training_cost_fixture_packet(accepted_fixtures()[0]["packet"])
    assert result.disposition == "accept"
    assert result.errors == ()
    assert result.accepted is True


def test_validator_rejects_missing_blocked_claims():
    packet = {key: value for key, value in accepted_fixtures()[0]["packet"].items() if key != "blocked_claims"}
    result = validate_training_cost_fixture_packet(packet)
    assert result.disposition == "reject"
    assert "missing blocked_claims" in result.errors
    assert "blocked_claims mismatch" in result.errors


def test_validator_rejects_all_cost_views_null_and_true_claim():
    packet = {
        **accepted_fixtures()[0]["packet"],
        "static_expression_cost": None,
        "graph_cost_profile": None,
        "training_budget_context": None,
        "claim_flags": {
            **accepted_fixtures()[0]["packet"]["claim_flags"],
            "training_savings_claim": True,
        },
    }
    result = validate_training_cost_fixture_packet(packet)
    assert result.disposition == "reject"
    assert "at least one cost view must be present" in result.errors
    assert "training_savings_claim must be false" in result.errors


def test_prod_a11_consumes_prod_a6_and_prod_a10():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PROD_A11_TRAINING_COST_ESTIMATOR_FIXTURE_VALIDATOR_IMPLEMENTATION_PASS"
    assert payload["sourceFixtureArtifact"] == "prod-a6-training-cost-estimator-fixture-packet"
    assert payload["sourcePauseArtifact"] == "prod-a10-private-product-roadmap-pause-digest"
    assert payload["summary"]["explicitProductRedirectConsumed"] is True


def test_prod_a11_executes_all_fixture_expectations():
    payload = build_payload()
    assert payload["summary"]["acceptedFixtureCount"] == 2
    assert payload["summary"]["rejectionFixtureCount"] == 5
    assert payload["summary"]["fixtureValidationResultCount"] == 7
    assert payload["summary"]["matchedExpectationCount"] == 7
    assert payload["summary"]["allFixtureExpectationsMatched"] is True
    assert all(row["actualDisposition"] == "accept" for row in payload["acceptedFixtureResults"])
    assert all(row["actualDisposition"] == "reject" for row in payload["rejectionFixtureResults"])
    assert all(row["errors"] for row in payload["rejectionFixtureResults"])


def test_prod_a11_blocks_estimator_public_runtime_and_accuracy_claims():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        assert summary[key] is False


def test_prod_a11_claim_flags_are_validator_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a11_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A11")
    assert "Accepted Fixture Results" in report
    assert "Rejection Fixture Results" in report


def test_prod_a11_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a11_training_cost_estimator_fixture_validator_implementation.py",
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
    assert "PROD_A11_TRAINING_COST_ESTIMATOR_FIXTURE_VALIDATOR_IMPLEMENTATION_OK" in proc.stdout
