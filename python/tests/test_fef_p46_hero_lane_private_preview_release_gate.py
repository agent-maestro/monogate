"""Tests for FEF-P46 hero-lane private preview release gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p46_hero_lane_private_preview_release_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p46_approves_private_preview_release_action_only():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P46_HERO_LANE_PRIVATE_PREVIEW_RELEASE_GATE_PASS"
    assert (
        payload["decision"]
        == "rust_c_python_private_preview_release_action_approved_publication_blocked"
    )
    assert summary["privatePreviewReleaseActionApproved"] is True
    assert summary["heroTargets"] == ["rust", "c", "python"]
    assert summary["heroRuntimeCellCount"] == 12
    assert summary["heroRuntimeSampleExecutions"] == 72
    assert summary["selectedRoundtripAttachmentTargets"] == ["c", "rust"]
    assert summary["selectedRoundtripAttachmentPackets"] == 10
    assert summary["selectedRoundtripAttachmentSamples"] == 34


def test_fef_p46_private_copy_boundary_passes():
    payload = build_payload()
    copy_review = payload["privateCopyReview"]
    assert copy_review["status"] == "pass"
    assert copy_review["forbiddenHits"] == []
    assert copy_review["requiredBoundaryMissing"] == []
    text = payload["privatePreviewCopy"].lower()
    assert "private preview evidence only" in text
    assert "not a public package release" in text
    assert "not full arbitrary c/rust source roundtrip" in text


def test_fef_p46_release_gates_keep_public_actions_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["private_preview_scope_recorded"] == "pass"
    assert gates["private_preview_copy_boundary_review_passed"] == "pass"
    assert gates["hero_lane_runtime_evidence_attached"] == "pass"
    assert gates["selected_c_rust_roundtrip_attachment_attached"] == "pass"
    assert gates["full_c_rust_roundtrip_claim"] == "blocked"
    assert gates["public_package_published"] == "blocked"
    assert gates["checkout_enabled"] == "blocked"
    assert gates["public_readiness"] == "blocked"
    assert gates["compiler_correctness_proved"] == "blocked"


def test_fef_p46_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["packagePublished"] is False
    assert summary["checkoutEnabled"] is False
    assert summary["publicReady"] is False
    assert summary["safeToPublishPublicly"] is False
    assert summary["fullCRustRoundtripClaim"] is False
    assert summary["allFreeTargetsRuntimeExecutionClaim"] is False
    assert summary["allFreeTargetsRoundtripClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p46_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P46")


def test_fef_p46_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p46_hero_lane_private_preview_release_gate.py",
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
    assert "FEF_P46_HERO_LANE_PRIVATE_PREVIEW_RELEASE_GATE_OK" in proc.stdout
