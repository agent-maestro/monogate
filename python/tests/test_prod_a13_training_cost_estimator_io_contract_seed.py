"""Tests for PROD-A13 private training-cost estimator I/O contract seed."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a13_training_cost_estimator_io_contract_seed import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def fixture_by_id(payload, fixture_id: str):
    return next(fixture for fixture in payload["contractFixtures"] if fixture["fixtureId"] == fixture_id)


def test_prod_a13_consumes_prod_a12_and_creates_io_contract():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A13_TRAINING_COST_ESTIMATOR_IO_CONTRACT_SEED_PASS"
    assert payload["sourceArtifact"] == "prod-a12-training-cost-validator-contract-review-selector"
    assert summary["sourceSelectedActionId"] == "private_estimator_io_contract_seed"
    assert summary["estimatorIoContractCreated"] is True


def test_prod_a13_records_four_input_contracts_from_private_spec():
    payload = build_payload()
    assert payload["summary"]["inputContractCount"] == 4
    input_ids = {item["inputId"] for item in payload["inputContracts"]}
    assert input_ids == {
        "sympy_expression_or_expression_list",
        "torch_fx_graph_summary",
        "training_loop_metadata",
        "manual_operation_count_packet",
    }
    assert all(item["requiredFields"] for item in payload["inputContracts"])


def test_prod_a13_output_contract_forces_caveats_blocked_claims_and_false_flags():
    payload = build_payload()
    output = payload["outputContract"]
    assert payload["summary"]["outputRequiredFieldCount"] == 8
    assert payload["summary"]["requiredCaveatCount"] == 5
    assert "calibration_caveats" in output["requiredFields"]
    assert "blocked_claims" in output["requiredFields"]
    assert "training_savings_claim" in output["requiredFalseClaimFlags"]
    assert "estimator_accuracy_claim" in output["requiredFalseClaimFlags"]
    assert "At least one" in output["costViewRule"]


def test_prod_a13_records_accepted_and_rejection_contract_fixtures():
    payload = build_payload()
    assert payload["summary"]["contractFixtureCount"] == 6
    assert payload["summary"]["acceptedContractFixtureCount"] == 2
    assert payload["summary"]["rejectionContractFixtureCount"] == 4
    assert fixture_by_id(payload, "accepted_static_expression_input_output_shape")[
        "expectedDisposition"
    ] == "accept_contract_shape"
    assert fixture_by_id(payload, "reject_true_accuracy_or_savings_flag")[
        "expectedDisposition"
    ] == "reject_contract_shape"


def test_prod_a13_blocks_estimator_execution_public_and_performance_claims():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "schemaValidatorChanged",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        assert summary[key] is False


def test_prod_a13_selects_a14_fixture_validator_or_hold_selector():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert payload["summary"]["nextRecommendedArtifact"].startswith("PROD-A14")


def test_prod_a13_claim_flags_are_contract_seed_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a13_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A13")
    assert "Input Contracts" in report
    assert "Contract Fixtures" in report


def test_prod_a13_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a13_training_cost_estimator_io_contract_seed.py",
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
    assert "PROD_A13_TRAINING_COST_ESTIMATOR_IO_CONTRACT_SEED_OK" in proc.stdout
