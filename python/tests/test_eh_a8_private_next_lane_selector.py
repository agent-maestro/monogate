"""Tests for EH-A8 private next-lane selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eh_a8_private_next_lane_selector import (
    CLAIM_FLAGS,
    SELECTED_NEXT_ARTIFACT,
    SELECTED_PATH,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def candidate_by_id(payload, candidate_id: str):
    return next(item for item in payload["candidateDoors"] if item["candidateId"] == candidate_id)


def test_eh_a8_consumes_eh_a7_and_selects_readability_contract():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A8_PRIVATE_NEXT_LANE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "eh-a7-private-command-feed-lane-state-aggregation"
    assert payload["summary"]["selectedPath"] == SELECTED_PATH
    assert payload["summary"]["selectedNextArtifact"] == SELECTED_NEXT_ARTIFACT
    assert candidate_by_id(payload, SELECTED_PATH)["decision"] == "selected"


def test_eh_a8_blocks_held_lane_continuations():
    payload = build_payload()
    lanes = {item["laneId"] for item in payload["blockedLaneContinuations"]}
    assert lanes == {
        "training-cost-estimator",
        "private-atlas-v0",
        "public-math-review",
        "product-roadmap",
        "electronics-inbox",
    }
    assert payload["summary"]["blockedContinuationCount"] == 5
    for item in payload["blockedLaneContinuations"]:
        assert item["requiredTrigger"]


def test_eh_a8_keeps_implementation_and_public_boundaries_closed():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["dashboardUiCreated"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["trainingCostEstimatorReopened"] is False
    assert summary["productRoadmapReopened"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["d110Started"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["laptopOwnedRepoTouched"] is False


def test_eh_a8_candidate_doors_block_atlas_public_math_estimator_and_electronics():
    payload = build_payload()
    assert candidate_by_id(payload, "atlas_v0_reference_document_revision")["decision"] == "blocked_for_now"
    assert candidate_by_id(payload, "public_math_witness_promotion")["decision"] == "blocked_for_now"
    assert candidate_by_id(payload, "training_cost_estimator_reopen")["decision"] == "blocked_for_now"
    assert candidate_by_id(payload, "electronics_artifact_intake")["decision"] == "blocked_for_now"


def test_eh_a8_blocks_dashboard_public_runtime_hardware_and_advantage_claims():
    payload = build_payload()
    for key in [
        "dashboard_ui_created",
        "dashboard_implementation_started",
        "all_feeds_scanned",
        "health_report_completeness_claim",
        "renderer_correctness_claim",
        "visualization_quality_claim",
        "public_dashboard_created",
        "public_surface_updated",
        "public_readiness_claim",
        "public_copy_approved",
        "training_cost_estimator_reopened",
        "training_cost_estimator_implemented",
        "estimate_values_produced",
        "training_savings_claim",
        "estimator_accuracy_claim",
        "product_implementation_started",
        "product_roadmap_reopened",
        "atlas_reviewer_response_consumed",
        "atlas_public_promotion",
        "atlas_catalog_completeness_claim",
        "public_math_promotion",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "laptop_artifact_consumed",
        "electronics_inbox_reopened",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "runtime_lowering_changed",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_eh_a8_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a8_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# EH-A8")
    assert "Candidate Doors" in report
    assert SELECTED_PATH in report
    assert "no held-lane reopen" in report


def test_eh_a8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a8_private_next_lane_selector.py",
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
    assert "EH_A8_PRIVATE_NEXT_LANE_SELECTOR_OK" in proc.stdout
