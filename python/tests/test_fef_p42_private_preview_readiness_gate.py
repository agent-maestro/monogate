"""Tests for FEF-P42 private preview readiness gate."""

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

from scripts.fef_p42_private_preview_readiness_gate import (
    CLAIM_FLAGS,
    PRIVATE_PREVIEW_COPY,
    build_outputs,
    build_payload,
    scan_private_copy,
    validate_payload,
)


def test_fef_p42_reviews_selected_private_evidence_and_blocks_publication():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P42_PRIVATE_PREVIEW_READINESS_GATE_PASS"
    assert payload["decision"] == "selected_private_preview_evidence_reviewed_publication_blocked"
    assert summary["privateCopyReviewPassed"] is True
    assert summary["evidenceInputsValid"] is True
    assert summary["evidenceClaimFlagsAllFalse"] is True
    assert summary["packagePublished"] is False
    assert summary["publicReady"] is False
    assert summary["safeToPublishPublicly"] is False
    assert summary["checkoutEnabled"] is False


def test_fef_p42_selected_capability_snapshot_is_explicit():
    payload = build_payload()
    snapshot = payload["selectedCapabilitySnapshot"]
    assert snapshot["fixtureCount"] == 4
    assert snapshot["freeTargetCount"] == 13
    assert snapshot["matrixCellCount"] == 52
    assert snapshot["runtimeOverlayCellCount"] == 24
    assert snapshot["runtimeOverlaySampleExecutions"] == 144
    assert snapshot["runtimeOverlayMaxAbsError"] <= 1.0e-12


def test_fef_p42_evidence_inputs_include_late_fef_chain():
    payload = build_payload()
    assert set(payload["evidenceInputs"]) == {
        "fefP31",
        "fefP32",
        "fefP34",
        "fefP35",
        "fefP37",
        "fefP38",
        "fefP40",
        "fefP41",
    }
    assert payload["evidenceInputs"]["fefP41"]["reviewDecision"] == "selected_four_fixture_capability_matrix_refreshed"
    assert payload["evidenceInputs"]["fefP41"]["summary"]["matrixCellCount"] == 52


def test_fef_p42_private_copy_scan_requires_boundaries():
    assert scan_private_copy(PRIVATE_PREVIEW_COPY)["status"] == "pass"
    bad = scan_private_copy("Private preview evidence only. public package available. checkout enabled.")
    assert bad["status"] == "fail"
    assert "public package available" in bad["forbiddenHits"]
    assert "checkout enabled" in bad["forbiddenHits"]


def test_fef_p42_release_gates_are_bounded():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_four_fixture_matrix_recorded"] == "pass"
    assert gates["selected_runtime_overlays_recorded"] == "pass"
    assert gates["private_preview_copy_boundary_review_passed"] == "pass"
    assert gates["public_package_published"] == "blocked"
    assert gates["checkout_remains_disabled"] == "required"
    assert gates["public_readiness"] == "blocked"
    assert gates["compiler_correctness_proved"] == "blocked"


def test_fef_p42_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    assert any("does not publish a package" in item for item in payload["nonClaims"])


def test_fef_p42_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P42")


def test_fef_p42_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p42_private_preview_readiness_gate.py",
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
    assert "FEF_P42_PRIVATE_PREVIEW_READINESS_GATE_OK" in proc.stdout
