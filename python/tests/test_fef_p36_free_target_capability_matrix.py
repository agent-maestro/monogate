"""Tests for FEF-P36 selected free-target capability matrix."""

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

from scripts.fef_p36_free_target_capability_matrix import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p36_matrix_covers_three_fixtures_and_all_free_targets():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P36_FREE_TARGET_CAPABILITY_MATRIX_PASS"
    assert [fixture["id"] for fixture in payload["fixtureRows"]] == [
        "verified_add",
        "runtime_helper_mix",
        "clamp_guard_mix",
    ]
    assert summary["fixtureCount"] == 3
    assert summary["freeTargetCount"] == 13
    assert summary["matrixCellCount"] == 39
    assert summary["emissionPassCount"] == 39
    assert summary["validationPassCount"] == 39
    assert summary["allMatrixEmissionPass"] is True
    assert summary["allMatrixValidationPass"] is True


def test_fef_p36_runtime_overlay_is_selected_and_explicit():
    payload = build_payload()
    summary = payload["summary"]
    assert payload["runtimeOverlay"]["sourceFixture"] == "generated/clamp_guard_mix.eml"
    assert payload["runtimeOverlay"]["runtimeTargets"] == ["c", "cpp", "rust", "python", "javascript", "java"]
    assert summary["runtimeOverlayCellCount"] == 6
    assert summary["runtimeOverlayPassCount"] == 6
    assert summary["runtimeOverlayTargets"] == ["c", "cpp", "rust", "python", "java", "javascript"]
    assert summary["runtimeOverlaySampleCount"] == 42
    assert summary["runtimeOverlayMaxAbsError"] == 0.0
    assert summary["allRuntimeOverlayCellsPass"] is True


def test_fef_p36_runtime_overlay_only_on_clamp_guard_cells():
    payload = build_payload()
    runtime_cells = [row for row in payload["matrixRows"] if row["runtimeStatus"] == "pass"]
    assert len(runtime_cells) == 6
    assert {row["fixtureId"] for row in runtime_cells} == {"clamp_guard_mix"}
    assert {row["target"] for row in runtime_cells} == {"c", "cpp", "rust", "python", "javascript", "java"}
    assert all(row["runtimeSampleCount"] == 7 for row in runtime_cells)
    assert all(row["runtimeMaxAbsError"] == 0.0 for row in runtime_cells)


def test_fef_p36_every_target_has_three_passing_fixture_cells():
    payload = build_payload()
    for target_row in payload["summary"]["byTarget"]:
        assert target_row["fixtureCount"] == 3
        assert target_row["emissionPassCount"] == 3
        assert target_row["validationPassCount"] == 3
    by_fixture = {}
    for row in payload["matrixRows"]:
        by_fixture.setdefault(row["fixtureId"], []).append(row)
        assert row["emissionStatus"] == "pass"
        assert row["validationStatus"] == "pass"
    assert set(by_fixture) == {"verified_add", "runtime_helper_mix", "clamp_guard_mix"}
    assert all(len(rows) == 13 for rows in by_fixture.values())


def test_fef_p36_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["allFreeTargetsRuntimeExecutionClaim"] is False
    assert summary["allFreeTargetsPublicReadyClaim"] is False
    assert summary["targetAllReadyClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    assert any("does not execute all 13 free targets" in item for item in payload["nonClaims"])


def test_fef_p36_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P36")


def test_fef_p36_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p36_free_target_capability_matrix.py",
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
    assert "FEF_P36_FREE_TARGET_CAPABILITY_MATRIX_OK" in proc.stdout
