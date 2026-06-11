"""Tests for FEF-P45 C/Rust selected roundtrip attachment gate."""

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

from scripts.fef_p45_c_rust_roundtrip_attachment_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p45_attaches_selected_c_rust_generated_target_roundtrip():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P45_C_RUST_ROUNDTRIP_ATTACHMENT_GATE_PASS"
    assert (
        payload["decision"]
        == "selected_c_rust_generated_target_roundtrip_attached_publication_blocked"
    )
    assert summary["attachedTargets"] == ["c", "rust"]
    assert summary["attachmentPacketCount"] == 10
    assert summary["attachmentPassCount"] == 10
    assert summary["attachmentSampleCount"] == 34
    assert summary["cSelectedGeneratedTargetRoundtripAttached"] is True
    assert summary["rustSelectedGeneratedTargetRoundtripAttached"] is True


def test_fef_p45_attachment_rows_keep_scope_precise():
    payload = build_payload()
    rows = {row["target"]: row for row in payload["attachmentRows"]}
    assert set(rows) == {"c", "rust"}
    for row in rows.values():
        assert row["attachmentStatus"] == "pass_selected_generated_target_reingest"
        assert row["attachedEvidenceKind"] == "selected_generated_target_reingest_to_python"
        assert row["packetCount"] == 5
        assert row["passCount"] == 5
        assert row["sourceLanguages"] == ["c", "javascript", "python", "rust"]
        assert "full arbitrary source roundtrip" in row["blockedClaims"]
        assert "selected Forge-generated" in row["allowedClaim"]


def test_fef_p45_keeps_full_roundtrip_and_public_claims_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_c_generated_target_roundtrip_attached"] == "pass"
    assert gates["selected_rust_generated_target_roundtrip_attached"] == "pass"
    assert gates["full_c_roundtrip_claim"] == "blocked"
    assert gates["full_rust_roundtrip_claim"] == "blocked"
    assert gates["public_package_published"] == "blocked"
    assert summary["fullCRoundtripClaim"] is False
    assert summary["fullRustRoundtripClaim"] is False
    assert summary["allFreeTargetsRoundtripClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p45_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P45")


def test_fef_p45_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p45_c_rust_roundtrip_attachment_gate.py",
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
    assert "FEF_P45_C_RUST_ROUNDTRIP_ATTACHMENT_GATE_OK" in proc.stdout
