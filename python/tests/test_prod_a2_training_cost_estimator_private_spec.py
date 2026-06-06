"""Tests for PROD-A2 training cost estimator private spec."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a2_training_cost_estimator_private_spec import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def item_by_id(items, key: str, value: str):
    return next(item for item in items if item[key] == value)


def test_prod_a2_consumes_prod_a1_and_selects_training_cost_estimator():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "PROD_A2_TRAINING_COST_ESTIMATOR_PRIVATE_SPEC_PASS"
    assert payload["sourceArtifact"] == "prod-a1-private-product-evidence-surface-seed"
    assert payload["selectedLane"] == "training_cost_estimator"
    assert summary["prodA1NextRecommendedArtifact"] == "PROD-A2 training cost estimator private spec"
    assert summary["nextRecommendedArtifact"] == "PROD-A3 training cost estimator schema validator or example packet selector"


def test_prod_a2_records_supported_inputs_output_schema_and_caveats():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["supportedInputCount"] == 4
    assert summary["outputFieldCount"] == 8
    assert summary["calibrationCaveatCount"] == 5
    assert item_by_id(payload["supportedInputs"], "inputId", "sympy_expression_or_expression_list")[
        "status"
    ] == "supported_for_static_cost_shape_spec"
    assert item_by_id(payload["outputSchemaFields"], "field", "blocked_claims")["type"] == "array[string]"
    assert item_by_id(payload["calibrationCaveats"], "caveatId", "not_wall_clock_runtime")["text"]


def test_prod_a2_records_example_boundaries_and_reviewer_next_steps():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["exampleBoundaryCount"] == 3
    assert summary["reviewerNextStepCount"] == 3
    mnist = item_by_id(payload["exampleBoundaries"], "exampleId", "mnist_mlp_budget_shape")
    assert "public claim" in mnist["blockedUse"]
    select = item_by_id(payload["reviewerNextSteps"], "stepId", "select_a3_path")
    assert select["status"] == "open_private_review"


def test_prod_a2_blocks_estimator_runtime_public_and_training_claims():
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
        "modelQualityClaim",
        "scientificCorrectnessClaim",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "hardwareReadinessClaim",
        "siliconReadinessClaim",
        "broadEmlAdvantageClaim",
    ]:
        assert summary[key] is False
    assert "training cost savings" in payload["blockedClaims"]
    assert "wall-clock runtime performance" in payload["blockedClaims"]


def test_prod_a2_respects_d109_hold_and_does_not_consume_review():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["d109HoldRespected"] is True
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert payload["claimFlags"]["d109_hold_respected"] is True
    assert payload["claimFlags"]["d110_started"] is False
    assert payload["claimFlags"]["reviewer_response_consumed"] is False


def test_prod_a2_claim_flags_are_private_spec_only():
    payload = build_payload()
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# PROD-A2")


def test_prod_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a2_training_cost_estimator_private_spec.py",
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
    assert "PROD_A2_TRAINING_COST_ESTIMATOR_PRIVATE_SPEC_OK" in proc.stdout
