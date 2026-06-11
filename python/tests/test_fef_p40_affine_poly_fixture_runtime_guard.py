"""Tests for FEF-P40 affine polynomial fixture runtime guard."""

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

from scripts.fef_p40_affine_poly_fixture_runtime_guard import (
    ATOL,
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p40_affine_poly_emits_validates_and_executes():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P40_AFFINE_POLY_FIXTURE_RUNTIME_GUARD_PASS"
    assert payload["sourceFixture"] == "generated/affine_poly_mix.eml"
    assert summary["freeTargetCount"] == 13
    assert summary["emissionPassCount"] == 13
    assert summary["validationPassCount"] == 13
    assert summary["runtimeTargets"] == ["c", "cpp", "rust", "python", "javascript", "java"]
    assert summary["runtimeTargetCount"] == 6
    assert summary["sampleCountPerTarget"] == 6
    assert summary["totalSampleExecutions"] == 36
    assert summary["runtimePassCount"] == 6
    assert summary["agreementPassCount"] == 6
    assert summary["maxAbsError"] <= ATOL


def test_fef_p40_sample_grid_and_reference_values_are_explicit():
    payload = build_payload()
    samples = [sample["args"] for sample in payload["sampleGrid"]]
    assert samples == [
        [0.0, 0.0],
        [1.0, 2.0],
        [-1.5, 0.25],
        [3.0, -4.0],
        [0.125, 10.0],
        [-10.0, -2.5],
    ]
    assert payload["reference"]["function"] == "x*x + 2*y + 1"
    assert payload["reference"]["values"] == [1.0, 6.0, 3.75, 2.0, 21.015625, 96.0]


def test_fef_p40_target_rows_cover_all_free_targets():
    payload = build_payload()
    rows = {row["target"]: row for row in payload["targetRows"]}
    assert set(rows) == {
        "c",
        "cpp",
        "rust",
        "python",
        "go",
        "java",
        "kotlin",
        "csharp",
        "javascript",
        "wasm",
        "matlab",
        "lean",
        "zkproof",
    }
    for row in rows.values():
        assert row["emissionStatus"] == "pass"
        assert row["validationStatus"] == "pass"
        assert row["artifactBytes"] > 0


def test_fef_p40_runtime_rows_have_passing_frames():
    payload = build_payload()
    for row in payload["runtimeRows"]:
        assert row["emissionStatus"] == "pass"
        assert row["runtimeStatus"] == "pass"
        assert row["agreementStatus"] == "pass"
        assert row["sampleCount"] == 6
        assert row["maxAbsError"] <= ATOL
        assert len(row["frames"]) == 6


def test_fef_p40_keeps_broad_claims_false():
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


def test_fef_p40_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P40")


def test_fef_p40_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p40_affine_poly_fixture_runtime_guard.py",
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
    assert "FEF_P40_AFFINE_POLY_FIXTURE_RUNTIME_GUARD_OK" in proc.stdout
