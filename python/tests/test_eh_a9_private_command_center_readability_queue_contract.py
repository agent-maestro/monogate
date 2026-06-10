"""Tests for EH-A9 private command-center readability queue contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eh_a9_private_command_center_readability_queue_contract import (
    CLAIM_FLAGS,
    CONTAINER_ID,
    DEFINED_NOT_SELECTED,
    QUEUE_ITEM_RECORD_FIELDS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def item_by_id(payload, item_id: str):
    return next(item for item in payload["queueItems"] if item["itemId"] == item_id)


def test_eh_a9_consumes_eh_a8_and_defines_queue_contract():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A9_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_CONTRACT_PASS"
    assert payload["sourceArtifact"] == "eh-a8-private-next-lane-selector"
    assert payload["summary"]["containerId"] == CONTAINER_ID
    assert payload["summary"]["queueItemRecordShapeDefined"] is True
    assert payload["queueItemRecordFields"] == list(QUEUE_ITEM_RECORD_FIELDS)


def test_eh_a9_records_pub_r0_and_pub_r1_defined_not_selected():
    payload = build_payload()
    ids = {item["itemId"] for item in payload["queueItems"]}
    assert {"PUB-R0", "PUB-R1"} <= ids
    for item in payload["queueItems"]:
        assert item["status"] == DEFINED_NOT_SELECTED
        assert item["container"] == CONTAINER_ID
        for field in QUEUE_ITEM_RECORD_FIELDS:
            assert field in item
        assert item["entryCriteria"], f"{item['itemId']} missing entry criteria"
        assert item["exitCriteria"], f"{item['itemId']} missing exit criteria"
        assert item["nonGoals"], f"{item['itemId']} missing non-goals"


def test_eh_a9_pub_r1_depends_on_pub_r0():
    payload = build_payload()
    pub_r0 = item_by_id(payload, "PUB-R0")
    pub_r1 = item_by_id(payload, "PUB-R1")
    assert pub_r0["dependencies"] == []
    assert "PUB-R0" in pub_r1["dependencies"]
    assert payload["summary"]["pubR1DependsOnPubR0"] is True


def test_eh_a9_pub_r1_carries_six_entry_criteria_and_no_js_non_goal():
    payload = build_payload()
    pub_r1 = item_by_id(payload, "PUB-R1")
    # r2 spec defines E1..E6
    assert len(pub_r1["entryCriteria"]) == 6
    joined_entry = " ".join(pub_r1["entryCriteria"])
    for tag in ["E1 —", "E2 —", "E3 —", "E4 —", "E5 —", "E6 —"]:
        assert tag in joined_entry, f"missing entry criterion tag {tag}"
    no_js_present = any(
        "JS" in goal or "JavaScript" in goal or "dynamic" in goal for goal in pub_r1["nonGoals"]
    )
    assert no_js_present, "PUB-R1 must carry the no-JS / no-dynamic non-goal"


def test_eh_a9_implements_no_queue_item_and_selects_none():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["selectedItemCount"] == 0
    assert summary["implementedItemCount"] == 0
    assert summary["definedNotSelectedCount"] == summary["queueItemCount"]


def test_eh_a9_keeps_implementation_and_public_boundaries_closed():
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


def test_eh_a9_blocks_implementation_public_runtime_hardware_and_advantage_claims():
    payload = build_payload()
    for key in [
        "queue_item_selected",
        "queue_item_implementation_started",
        "pub_r0_built",
        "pub_r1_built",
        "ledger_generated",
        "drift_guard_implemented",
        "deploy_authorization_granted",
        "dashboard_ui_created",
        "dashboard_implementation_started",
        "all_feeds_scanned",
        "renderer_correctness_claim",
        "visualization_quality_claim",
        "health_report_completeness_claim",
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


def test_eh_a9_claim_flags_are_contract_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a9_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds"
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# EH-A9")
    assert "Queue Items" in report
    assert "Queue Item Record Shape" in report
    assert "PUB-R0" in report
    assert "PUB-R1" in report
    assert "broad delegation from the operator does not constitute selection" in report


def test_eh_a9_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a9_private_command_center_readability_queue_contract.py",
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
    assert "EH_A9_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_CONTRACT_OK" in proc.stdout
