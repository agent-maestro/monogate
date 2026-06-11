"""Tests for FEF-P49 non-generated C/Rust fixture gate."""

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

from scripts.fef_p49_non_generated_c_rust_fixture_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p49_attaches_non_generated_c_rust_semantic_evidence():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P49_NON_GENERATED_C_RUST_FIXTURE_GATE_PASS"
    assert payload["decision"] == (
        "selected_non_generated_c_rust_semantic_evidence_attached_roundtrip_blocked"
    )
    assert summary["nonGeneratedCRustSemanticEvidenceAttached"] is True
    assert summary["sourceEvidenceValidationPass"] is True
    assert summary["sourceEvidenceClaimFlagsAllFalse"] is True
    assert summary["p48IntakeReady"] is True


def test_fef_p49_preserves_hero_lane_and_source_fixture_scope():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["heroTargets"] == ["rust", "c", "python"]
    assert summary["selectedGeneratedRoundtripAttachmentTargets"] == ["c", "rust"]
    assert summary["selectedGeneratedRoundtripAttachmentPackets"] == 10
    assert summary["selectedGeneratedRoundtripAttachmentSamples"] == 34
    assert summary["nonGeneratedSourceCaseCount"] == 5
    assert summary["nonGeneratedSourcePassCount"] == 5
    assert summary["nonGeneratedSourceSampleCount"] == 23
    assert summary["nonGeneratedSourceLanguages"] == ["c", "rust"]
    assert summary["nonGeneratedTargetLanguages"] == ["python", "javascript"]


def test_fef_p49_attachment_row_is_semantic_not_roundtrip():
    payload = build_payload()
    rows = payload["attachmentRows"]
    assert len(rows) == 1
    row = rows[0]
    assert row["status"] == "pass_attached"
    assert row["evidenceKind"] == "selected_original_runtime_semantic_comparison"
    assert row["caseCount"] == 5
    assert row["sampleCount"] == 23
    assert "non-generated source roundtrip" in row["blockedClaims"]
    assert "full arbitrary C/Rust source roundtrip" in row["blockedClaims"]


def test_fef_p49_claim_flags_and_release_gates_remain_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_non_generated_c_rust_semantic_evidence_attached"] == "pass"
    assert gates["non_generated_source_roundtrip_claim"] == "blocked"
    assert gates["full_c_rust_roundtrip_claim"] == "blocked"
    assert gates["private_reviewer_decision"] == "not_recorded"
    assert summary["nonGeneratedSourceRoundtripClaim"] is False
    assert summary["fullCRustRoundtripClaim"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["packagePublished"] is False
    assert summary["checkoutEnabled"] is False
    assert summary["publicReady"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["allFreeTargetsRuntimeExecutionClaim"] is False
    assert summary["allFreeTargetsRoundtripClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p49_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P49")


def test_fef_p49_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p49_non_generated_c_rust_fixture_gate.py",
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
    assert "FEF_P49_NON_GENERATED_C_RUST_FIXTURE_GATE_OK" in proc.stdout
