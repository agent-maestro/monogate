"""Tests for EML-A11.3 builder/export feedback."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from scripts.eml_a11_3_builder_export_feedback import DEFAULT_DRAFTS, build_feedback, validate_payload


def build_tmp(tmp_path):
    return build_feedback(
        list(DEFAULT_DRAFTS),
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def test_builder_export_feedback_cites_a11_2_for_protected_lowerings(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A11_3_BUILDER_EXPORT_FEEDBACK_PASS"
    assert payload["summary"]["protectedLoweringDraftCount"] >= 2
    assert payload["summary"]["allProtectedLoweringsCiteA11_2"] is True
    validate_payload(payload)


def test_feedback_packets_include_specific_case_ids(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    case_ids = {
        evidence["caseId"]
        for packet in payload["validationPackets"]
        for evidence in packet["supportingEvidenceArtifacts"]
    }
    assert {"expm1_near_zero", "logsumexp_edge_grid"}.issubset(case_ids)


def test_feedback_keeps_claims_false(tmp_path):
    summary = build_tmp(tmp_path)["payload"]["summary"]
    assert summary["compilerBehaviorChanged"] is False
    assert summary["compilerImplementationClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["productionReady"] is False
    assert summary["claimFlagsAllFalse"] is True


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a11_3_builder_export_feedback.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
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
    assert "EML_A11_3_BUILDER_EXPORT_FEEDBACK_OK" in proc.stdout


def test_default_drafts_exist():
    assert all(Path(path).exists() for path in DEFAULT_DRAFTS)
