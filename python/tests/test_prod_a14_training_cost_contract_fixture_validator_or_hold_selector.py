"""Tests for PROD-A14 private training-cost contract fixture validator selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a14_training_cost_contract_fixture_validator_or_hold_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def action_by_id(payload, action_id: str):
    return next(action for action in payload["candidateActions"] if action["actionId"] == action_id)


def test_prod_a14_consumes_prod_a13_and_selects_validator_path():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A14_TRAINING_COST_CONTRACT_FIXTURE_VALIDATOR_OR_HOLD_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "prod-a13-training-cost-estimator-io-contract-seed"
    assert summary["sourceContractFixtureCount"] == 6
    assert summary["selectedActionId"] == "implement_private_contract_fixture_validator"
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_prod_a14_records_decision_criteria_from_a13_contract():
    payload = build_payload()
    assert payload["summary"]["decisionCriterionCount"] == 4
    statuses = {item["criterionId"]: item["status"] for item in payload["decisionCriteria"]}
    assert statuses["contract_fixtures_exist"] == "pass"
    assert statuses["accepted_and_rejection_balance"] == "pass"
    assert statuses["output_boundary_carried"] == "pass"
    assert statuses["estimator_still_blocked"] == "bounded"


def test_prod_a14_blocks_immediate_estimator_and_public_docs():
    payload = build_payload()
    assert action_by_id(payload, "immediate_estimator_implementation")["decision"] == "blocked"
    assert action_by_id(payload, "public_product_or_docs")["decision"] == "blocked"
    summary = payload["summary"]
    assert summary["immediateEstimatorImplementationBlocked"] is True
    for key in [
        "contractFixtureValidatorImplemented",
        "contractFixtureValidatorExecuted",
        "estimatorImplemented",
        "estimatorExecuted",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        assert summary[key] is False


def test_prod_a14_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a14_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A14")
    assert "Decision Criteria" in report
    assert "Candidate Actions" in report


def test_prod_a14_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a14_training_cost_contract_fixture_validator_or_hold_selector.py",
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
    assert "PROD_A14_TRAINING_COST_CONTRACT_FIXTURE_VALIDATOR_OR_HOLD_SELECTOR_OK" in proc.stdout
