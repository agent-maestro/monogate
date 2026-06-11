"""Tests for EH-A6 private health digest post-training-cost-hold refresh."""

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

from scripts.eh_a6_private_health_digest_post_training_cost_hold_refresh import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def lane_by_id(payload, lane_id: str):
    return next(item for item in payload["refreshedLaneRows"] if item["laneId"] == lane_id)


def test_eh_a6_consumes_eh_a5_and_prod_a21():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A6_PRIVATE_HEALTH_DIGEST_POST_TRAINING_COST_HOLD_REFRESH_PASS"
    assert payload["sourceHealthArtifact"] == "eh-a5-private-health-digest-post-atlas-hold-refresh"
    assert payload["sourceTrainingCostArtifact"] == "prod-a21-training-cost-estimator-skeleton-hold-digest"
    assert payload["summary"]["postTrainingCostHoldDigestCreated"] is True
    assert payload["summary"]["digestVisibility"] == "private"
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_eh_a6_records_training_cost_hold_and_existing_held_lanes():
    payload = build_payload()
    assert payload["summary"]["laneRowCount"] == 6
    assert payload["summary"]["heldLaneCount"] >= 4
    assert payload["summary"]["atlasHeld"] is True
    assert payload["summary"]["publicMathHeld"] is True
    assert payload["summary"]["trainingCostEstimatorHeld"] is True
    assert payload["summary"]["productRoadmapPaused"] is True
    assert lane_by_id(payload, "private-atlas-v0")["status"] == "held_pending_reviewer_response_or_explicit_redirect"
    assert lane_by_id(payload, "training-cost-estimator")["status"] == "held_by_prod_a21"
    assert lane_by_id(payload, "product-roadmap")["status"] == "paused_with_training_cost_held"


def test_eh_a6_private_only_and_no_training_cost_reopen():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["privateOnlyRefresh"] is True
    assert summary["reviewerResponseConsumed"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["d110Started"] is False
    assert summary["trainingCostEstimatorReopened"] is False
    assert summary["laptopOwnedRepoTouched"] is False
    assert summary["publicSurfaceUpdated"] is False


def test_eh_a6_blocks_public_dashboard_runtime_hardware_and_advantage_claims():
    payload = build_payload()
    for key in [
        "dashboard_ui_created",
        "public_dashboard_created",
        "public_readiness_claim",
        "public_copy_approved",
        "public_surface_updated",
        "renderer_correctness_claim",
        "visualization_quality_claim",
        "compiler_correctness_claim",
        "runtime_performance_claim",
        "training_savings_claim",
        "estimator_accuracy_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "atlas_public_promotion",
        "atlas_catalog_completeness_claim",
        "public_math_promotion",
        "sdk_compiler_docs_created",
        "course_material_created",
        "product_implementation_started",
        "training_cost_estimator_reopened",
        "training_cost_estimator_implemented",
        "estimate_values_produced",
        "health_report_completeness_claim",
        "external_source_checked",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_eh_a6_claim_flags_are_refresh_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a6_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# EH-A6")
    assert "training-cost-estimator" in report
    assert "Blocked Follow-Ups" in report


def test_eh_a6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a6_private_health_digest_post_training_cost_hold_refresh.py",
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
    assert "EH_A6_PRIVATE_HEALTH_DIGEST_POST_TRAINING_COST_HOLD_REFRESH_OK" in proc.stdout
