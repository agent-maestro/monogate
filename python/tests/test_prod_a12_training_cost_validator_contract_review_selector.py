"""Tests for PROD-A12 private training-cost validator contract review selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a12_training_cost_validator_contract_review_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def action_by_id(payload, action_id: str):
    return next(action for action in payload["candidateActions"] if action["actionId"] == action_id)


def test_prod_a12_consumes_prod_a11_and_reviews_fixture_results():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A12_TRAINING_COST_VALIDATOR_CONTRACT_REVIEW_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "prod-a11-training-cost-estimator-fixture-validator-implementation"
    assert summary["fixtureValidationResultCount"] == 7
    assert summary["matchedExpectationCount"] == 7
    assert summary["allFixtureExpectationsMatched"] is True


def test_prod_a12_accepts_private_validator_boundary_only():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["privateValidatorBoundaryAccepted"] is True
    assert {row["status"] for row in payload["reviewRows"]} == {"pass", "bounded"}
    semantic_scope = next(row for row in payload["reviewRows"] if row["reviewId"] == "semantic_scope")
    assert "structural fixture shape only" in semantic_scope["detail"]


def test_prod_a12_selects_estimator_io_contract_seed():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["selectedActionId"] == "private_estimator_io_contract_seed"
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert action_by_id(payload, "private_estimator_io_contract_seed")["decision"] == "selected"


def test_prod_a12_blocks_immediate_estimator_and_public_docs():
    payload = build_payload()
    assert action_by_id(payload, "immediate_estimator_implementation")["decision"] == "blocked"
    assert action_by_id(payload, "public_product_or_docs")["decision"] == "blocked"
    summary = payload["summary"]
    assert summary["immediateEstimatorImplementationBlocked"] is True
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "estimatorContractCreated",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        assert summary[key] is False


def test_prod_a12_claim_flags_are_review_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a12_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A12")
    assert "Review Rows" in report
    assert "Candidate Actions" in report


def test_prod_a12_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a12_training_cost_validator_contract_review_selector.py",
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
    assert "PROD_A12_TRAINING_COST_VALIDATOR_CONTRACT_REVIEW_SELECTOR_OK" in proc.stdout
