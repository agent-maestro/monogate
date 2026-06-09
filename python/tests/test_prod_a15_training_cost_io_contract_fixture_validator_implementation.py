"""Tests for PROD-A15 private training-cost I/O contract fixture validator."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from monogate.training_cost_io_contract_validator import validate_io_contract_fixture
from scripts.prod_a13_training_cost_estimator_io_contract_seed import build_payload as build_a13_payload
from scripts.prod_a15_training_cost_io_contract_fixture_validator_implementation import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def fixture_by_id(payload, fixture_id: str):
    return next(fixture for fixture in payload["contractFixtures"] if fixture["fixtureId"] == fixture_id)


def test_io_contract_validator_accepts_private_accepted_fixture_shape():
    contract = build_a13_payload()["outputContract"]
    fixture = fixture_by_id(build_a13_payload(), "accepted_static_expression_input_output_shape")
    result = validate_io_contract_fixture(fixture, contract)
    assert result.disposition == "accept"
    assert result.errors == ()
    assert result.accepted is True


def test_io_contract_validator_rejects_rejection_fixture_shape():
    contract = build_a13_payload()["outputContract"]
    fixture = fixture_by_id(build_a13_payload(), "reject_output_without_caveats")
    result = validate_io_contract_fixture(fixture, contract)
    assert result.disposition == "reject"
    assert result.errors == ("rejection fixture carries blocked mutation",)


def test_io_contract_validator_rejects_accepted_fixture_without_boundary():
    contract = build_a13_payload()["outputContract"]
    fixture = {**fixture_by_id(build_a13_payload(), "accepted_training_budget_input_output_shape")}
    fixture.pop("requiredBoundary")
    result = validate_io_contract_fixture(fixture, contract)
    assert result.disposition == "reject"
    assert "accepted fixture must carry requiredBoundary" in result.errors


def test_prod_a15_consumes_a14_and_a13_and_executes_contract_fixtures():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A15_TRAINING_COST_IO_CONTRACT_FIXTURE_VALIDATOR_IMPLEMENTATION_PASS"
    assert payload["sourceSelectorArtifact"] == "prod-a14-training-cost-contract-fixture-validator-or-hold-selector"
    assert payload["sourceContractArtifact"] == "prod-a13-training-cost-estimator-io-contract-seed"
    assert summary["fixtureValidationResultCount"] == 6
    assert summary["matchedExpectationCount"] == 6
    assert summary["allFixtureExpectationsMatched"] is True


def test_prod_a15_records_accepted_and_rejection_results():
    payload = build_payload()
    assert payload["summary"]["acceptedContractFixtureCount"] == 2
    assert payload["summary"]["rejectionContractFixtureCount"] == 4
    assert all(row["actualDisposition"] == "accept" for row in payload["acceptedContractFixtureResults"])
    assert all(row["actualDisposition"] == "reject" for row in payload["rejectionContractFixtureResults"])
    assert all(row["errors"] for row in payload["rejectionContractFixtureResults"])


def test_prod_a15_blocks_estimator_public_runtime_and_accuracy_claims():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
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


def test_prod_a15_claim_flags_are_validator_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a15_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A15")
    assert "Accepted Contract Fixture Results" in report
    assert "Rejection Contract Fixture Results" in report


def test_prod_a15_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a15_training_cost_io_contract_fixture_validator_implementation.py",
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
    assert "PROD_A15_TRAINING_COST_IO_CONTRACT_FIXTURE_VALIDATOR_IMPLEMENTATION_OK" in proc.stdout
