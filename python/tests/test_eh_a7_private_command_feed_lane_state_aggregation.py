"""Tests for EH-A7 private command-feed lane-state aggregation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eh_a7_private_command_feed_lane_state_aggregation import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    SOURCE_FEEDS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def row_by_id(payload, lane_id: str):
    return next(item for item in payload["laneStateRows"] if item["laneId"] == lane_id)


def test_eh_a7_consumes_selected_feeds_only():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A7_PRIVATE_COMMAND_FEED_LANE_STATE_AGGREGATION_PASS"
    assert payload["summary"]["digestVisibility"] == "private"
    assert payload["summary"]["sourceFeedCount"] == len(SOURCE_FEEDS)
    assert payload["summary"]["laneStateRowCount"] == len(SOURCE_FEEDS)
    assert payload["summary"]["allFeedsScanned"] is False
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_eh_a7_records_held_paused_and_pending_lane_states():
    payload = build_payload()
    assert payload["summary"]["heldOrPausedRowCount"] >= 5
    assert row_by_id(payload, "training-cost-estimator")["laneStatus"] == "held_by_prod_a21"
    assert (
        row_by_id(payload, "private-atlas-v0")["laneStatus"]
        == "held_pending_reviewer_response_or_explicit_redirect"
    )
    assert row_by_id(payload, "public-math-review")["laneStatus"] == "held_pending_actual_reviewer_response"
    assert row_by_id(payload, "product-roadmap")["laneStatus"] == "paused_by_product_roadmap_pause_digest"
    assert row_by_id(payload, "electronics-inbox")["laneStatus"] == "pending_no_artifact"


def test_eh_a7_keeps_private_only_boundaries():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["dashboardUiCreated"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["trainingCostEstimatorReopened"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["d110Started"] is False
    assert summary["laptopOwnedRepoTouched"] is False


def test_eh_a7_lane_rows_block_public_runtime_compiler_and_laptop_touch():
    payload = build_payload()
    for row in payload["laneStateRows"]:
        assert row["publicSurfaceUpdated"] is False
        assert row["laptopOwnedRepoTouched"] is False
        assert row["runtimePerformanceClaim"] is False
        assert row["compilerCorrectnessClaim"] is False
        assert row["blockedClaimCount"] >= 1


def test_eh_a7_blocks_dashboard_public_product_and_advantage_claims():
    payload = build_payload()
    for key in [
        "all_feeds_scanned",
        "dashboard_ui_created",
        "public_dashboard_created",
        "public_surface_updated",
        "renderer_correctness_claim",
        "visualization_quality_claim",
        "health_report_completeness_claim",
        "external_source_checked",
        "training_cost_estimator_reopened",
        "training_cost_estimator_implemented",
        "estimate_values_produced",
        "training_savings_claim",
        "estimator_accuracy_claim",
        "product_implementation_started",
        "public_readiness_claim",
        "public_copy_approved",
        "sdk_compiler_docs_created",
        "course_material_created",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "d110_started",
        "atlas_public_promotion",
        "atlas_catalog_completeness_claim",
        "public_math_promotion",
        "laptop_artifact_consumed",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_eh_a7_claim_flags_are_aggregation_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a7_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# EH-A7")
    assert "Lane State Rows" in report
    assert "training-cost-estimator" in report
    assert "selected local command feeds only" in report


def test_eh_a7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a7_private_command_feed_lane_state_aggregation.py",
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
    assert "EH_A7_PRIVATE_COMMAND_FEED_LANE_STATE_AGGREGATION_OK" in proc.stdout
