"""Tests for EH-A10 private command-center readability queue item selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eh_a10_private_command_center_readability_queue_item_selector import (
    CLAIM_FLAGS,
    SELECTION_INPUT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def door_by_id(payload, candidate_id: str):
    return next(d for d in payload["candidateDoors"] if d["candidateId"] == candidate_id)


def test_eh_a10_consumes_eh_a9_and_selects_pub_r0_and_pub_r1():
    payload = build_payload()
    validate_payload(payload)
    assert (
        payload["status"]
        == "EH_A10_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_ITEM_SELECTOR_PASS"
    )
    assert payload["sourceArtifact"] == "eh-a9-private-command-center-readability-queue-contract"
    assert payload["summary"]["sourceContainerId"] == "EH-A9"
    assert set(payload["summary"]["selectedItemIds"]) == {"PUB-R0", "PUB-R1"}
    assert payload["summary"]["selectionInput"] == SELECTION_INPUT


def test_eh_a10_records_build_order_and_pub_r1_gate():
    payload = build_payload()
    pub_r0 = door_by_id(payload, "PUB-R0")
    pub_r1 = door_by_id(payload, "PUB-R1")
    assert pub_r0["decision"] == "selected"
    assert pub_r1["decision"] == "selected"
    assert pub_r0["buildOrder"] == 1
    assert pub_r1["buildOrder"] == 2
    assert pub_r0["buildGate"] == "ready_to_build"
    assert "build_gated_on_pub_r0_ship" in pub_r1["buildGate"]
    assert "deploy_authorization" in pub_r1["buildGate"]
    assert payload["summary"]["pubR1BuildGatedOnPubR0Ship"] is True


def test_eh_a10_does_not_implement_or_deploy():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["queueItemImplementationStarted"] is False
    assert summary["pubR0Built"] is False
    assert summary["pubR1Built"] is False
    assert summary["deployAuthorizationGranted"] is False
    assert summary["liveDeployExecuted"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["laptopOwnedRepoTouched"] is False


def test_eh_a10_blocks_lane_reopens_and_substance_claims():
    payload = build_payload()
    for key in [
        "queue_item_implementation_started",
        "pub_r0_built",
        "pub_r1_built",
        "ledger_generated",
        "drift_guard_implemented",
        "deploy_authorization_granted",
        "live_deploy_executed",
        "dashboard_ui_created",
        "all_feeds_scanned",
        "public_surface_updated",
        "public_readiness_claim",
        "public_copy_approved",
        "training_cost_estimator_reopened",
        "product_roadmap_reopened",
        "atlas_public_promotion",
        "public_math_promotion",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
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


def test_eh_a10_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a10_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds"
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# EH-A10")
    assert "Candidate Doors" in report
    assert "Selection Input" in report
    assert "PUB-R0" in report and "PUB-R1" in report
    assert "build_gated_on_pub_r0_ship" in report


def test_eh_a10_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a10_private_command_center_readability_queue_item_selector.py",
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
    assert "EH_A10_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_ITEM_SELECTOR_OK" in proc.stdout
