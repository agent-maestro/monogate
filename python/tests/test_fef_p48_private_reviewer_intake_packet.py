"""Tests for FEF-P48 private reviewer intake packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p48_private_reviewer_intake_packet import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p48_prepares_private_reviewer_intake_without_decision():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P48_PRIVATE_REVIEWER_INTAKE_PACKET_PASS"
    assert payload["decision"] == "private_reviewer_intake_ready_no_reviewer_decision_recorded"
    assert summary["intakeReady"] is True
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["sourceBundleValidationPass"] is True
    assert summary["sourceBundleClaimFlagsAllFalse"] is True
    assert summary["sourceBundleEvidenceCount"] == 4


def test_fef_p48_inherits_p47_bundle_scope():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["heroTargets"] == ["rust", "c", "python"]
    assert summary["heroRuntimeCellCount"] == 12
    assert summary["heroRuntimeSampleExecutions"] == 72
    assert summary["selectedRoundtripAttachmentTargets"] == ["c", "rust"]
    assert summary["selectedRoundtripAttachmentPackets"] == 10
    assert summary["selectedRoundtripAttachmentSamples"] == 34
    assert payload["sourceBundle"]["packetPath"] == (
        "reports/evidence_packets/fef_p47_private_reviewer_bundle_index.json"
    )


def test_fef_p48_reviewer_rubric_and_handoff_are_explicit():
    payload = build_payload()
    intake = payload["reviewerIntakePacket"]
    checklist = {item["id"]: item for item in payload["handoffChecklist"]}
    assert intake["intakeStatus"] == "ready_for_private_review"
    assert intake["reviewerDecisionStatus"] == "not_recorded"
    assert "accept_private_scope" in intake["allowedReviewerOutcomes"]
    assert "request_non_generated_c_rust_fixtures" in intake["allowedReviewerOutcomes"]
    assert checklist["send_p47_bundle"]["status"] == "ready"
    assert checklist["send_p48_intake"]["status"] == "ready"
    assert checklist["collect_reviewer_decision"]["status"] == "pending_human"
    assert checklist["preserve_claim_boundary"]["status"] == "required"


def test_fef_p48_statement_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert "A reviewer has approved the bundle." in payload["blockedStatements"]
    assert "Forge/eFrog is public-ready." in payload["blockedStatements"]
    assert any("private reviewer" in item for item in payload["allowedPrivateReviewerStatements"])
    assert summary["packagePublished"] is False
    assert summary["checkoutEnabled"] is False
    assert summary["publicReady"] is False
    assert summary["safeToPublishPublicly"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["fullCRustRoundtripClaim"] is False
    assert summary["allFreeTargetsRuntimeExecutionClaim"] is False
    assert summary["allFreeTargetsRoundtripClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p48_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P48")


def test_fef_p48_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p48_private_reviewer_intake_packet.py",
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
    assert "FEF_P48_PRIVATE_REVIEWER_INTAKE_PACKET_OK" in proc.stdout
