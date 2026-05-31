"""Tests for FEF-P47 private reviewer bundle index."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p47_private_reviewer_bundle_index import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p47_links_private_reviewer_bundle():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P47_PRIVATE_REVIEWER_BUNDLE_INDEX_PASS"
    assert payload["decision"] == "private_reviewer_bundle_index_ready_publication_blocked"
    assert summary["bundleEvidenceCount"] == 4
    assert summary["allEvidenceValidationPass"] is True
    assert summary["allEvidenceClaimFlagsFalse"] is True
    assert summary["heroTargets"] == ["rust", "c", "python"]
    assert summary["heroRuntimeCellCount"] == 12
    assert summary["heroRuntimeSampleExecutions"] == 72
    assert summary["selectedRoundtripAttachmentTargets"] == ["c", "rust"]
    assert summary["selectedRoundtripAttachmentPackets"] == 10
    assert summary["selectedRoundtripAttachmentSamples"] == 34


def test_fef_p47_evidence_order_and_roles_are_explicit():
    payload = build_payload()
    rows = payload["evidenceRows"]
    assert [row["id"] for row in rows] == ["fefP43", "fefP44", "fefP45", "fefP46"]
    assert [row["role"] for row in rows] == [
        "target_level_reality_matrix",
        "hero_lane_runtime_gate",
        "selected_c_rust_roundtrip_attachment",
        "private_preview_release_action_gate",
    ]
    for row in rows:
        assert row["validationStatus"] == "pass"
        assert row["claimFlagsAllFalse"] is True
        assert row["path"].startswith("reports/evidence_packets/")


def test_fef_p47_reviewer_checklist_and_statement_boundaries():
    payload = build_payload()
    checklist = {item["id"]: item for item in payload["reviewerChecklist"]}
    assert checklist["target_reality_matrix_reviewed"]["status"] == "ready"
    assert checklist["hero_runtime_lane_reviewed"]["status"] == "ready"
    assert checklist["selected_c_rust_roundtrip_attachment_reviewed"]["status"] == "ready"
    assert checklist["private_release_boundary_reviewed"]["status"] == "ready"
    assert checklist["public_claims_checked"]["status"] == "required"
    assert any("Rust, C, and Python" in item for item in payload["allowedPrivateReviewerStatements"])
    assert "Forge/eFrog is public-ready." in payload["blockedStatements"]
    assert "Compiler correctness has been proved." in payload["blockedStatements"]


def test_fef_p47_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
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


def test_fef_p47_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P47")


def test_fef_p47_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p47_private_reviewer_bundle_index.py",
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
    assert "FEF_P47_PRIVATE_REVIEWER_BUNDLE_INDEX_OK" in proc.stdout
