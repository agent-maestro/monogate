"""Tests for FEF-P41 four-fixture capability matrix refresh."""

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

from scripts.fef_p41_four_fixture_capability_matrix_refresh import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p41_refreshes_four_fixture_matrix():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P41_FOUR_FIXTURE_CAPABILITY_MATRIX_REFRESH_PASS"
    assert payload["baseMatrixArtifactId"] == "fef-p36-free-target-capability-matrix"
    assert [fixture["id"] for fixture in payload["fixtureRows"]] == [
        "verified_add",
        "runtime_helper_mix",
        "clamp_guard_mix",
        "affine_poly_mix",
    ]
    assert summary["fixtureCount"] == 4
    assert summary["freeTargetCount"] == 13
    assert summary["matrixCellCount"] == 52
    assert summary["emissionPassCount"] == 52
    assert summary["validationPassCount"] == 52
    assert summary["runtimeOverlayFixtureCount"] == 4
    assert summary["runtimeOverlayCellCount"] == 24
    assert summary["runtimeOverlayPassCount"] == 24
    assert summary["runtimeOverlaySampleExecutions"] == 144
    assert summary["runtimeOverlayMaxAbsError"] <= 1.0e-12


def test_fef_p41_runtime_overlay_by_fixture_counts_are_explicit():
    payload = build_payload()
    by_fixture = {row["fixtureId"]: row for row in payload["summary"]["runtimeOverlayByFixture"]}
    assert by_fixture["verified_add"]["sourceFixture"] == "examples/verified_add.eml"
    assert by_fixture["verified_add"]["runtimeSampleExecutions"] == 36
    assert by_fixture["runtime_helper_mix"]["sourceFixture"] == "generated/runtime_helper_mix.eml"
    assert by_fixture["runtime_helper_mix"]["runtimeSampleExecutions"] == 30
    assert by_fixture["clamp_guard_mix"]["sourceFixture"] == "generated/clamp_guard_mix.eml"
    assert by_fixture["clamp_guard_mix"]["runtimeSampleExecutions"] == 42
    assert by_fixture["affine_poly_mix"]["sourceFixture"] == "generated/affine_poly_mix.eml"
    assert by_fixture["affine_poly_mix"]["runtimeSampleExecutions"] == 36
    assert all(row["runtimeCellCount"] == 6 for row in by_fixture.values())
    assert all(row["runtimePassCount"] == 6 for row in by_fixture.values())


def test_fef_p41_runtime_overlay_by_target_marks_installed_runtime_targets():
    payload = build_payload()
    by_target = {row["target"]: row for row in payload["summary"]["runtimeOverlayByTarget"]}
    for target in ["c", "cpp", "rust", "python", "java", "javascript"]:
        assert by_target[target]["fixtureCount"] == 4
        assert by_target[target]["runtimePassCount"] == 4
        assert by_target[target]["runtimeSampleExecutions"] == 24
    for target in ["go", "kotlin", "csharp", "wasm", "matlab", "lean", "zkproof"]:
        assert by_target[target]["fixtureCount"] == 4
        assert by_target[target]["runtimePassCount"] == 0
        assert by_target[target]["runtimeSampleExecutions"] == 0


def test_fef_p41_matrix_rows_have_runtime_only_for_selected_targets():
    payload = build_payload()
    runtime_cells = [row for row in payload["matrixRows"] if row["runtimeStatus"] == "pass"]
    assert len(runtime_cells) == 24
    assert {row["fixtureId"] for row in runtime_cells} == {
        "verified_add",
        "runtime_helper_mix",
        "clamp_guard_mix",
        "affine_poly_mix",
    }
    assert {row["target"] for row in runtime_cells} == {"c", "cpp", "rust", "python", "javascript", "java"}
    sample_counts = {(row["fixtureId"], row["target"]): row["runtimeSampleCount"] for row in runtime_cells}
    for target in ["c", "cpp", "rust", "python", "javascript", "java"]:
        assert sample_counts[("verified_add", target)] == 6
        assert sample_counts[("runtime_helper_mix", target)] == 5
        assert sample_counts[("clamp_guard_mix", target)] == 7
        assert sample_counts[("affine_poly_mix", target)] == 6


def test_fef_p41_keeps_broad_claims_false():
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


def test_fef_p41_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P41")


def test_fef_p41_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p41_four_fixture_capability_matrix_refresh.py",
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
    assert "FEF_P41_FOUR_FIXTURE_CAPABILITY_MATRIX_REFRESH_OK" in proc.stdout
