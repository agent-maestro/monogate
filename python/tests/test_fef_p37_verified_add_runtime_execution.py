"""Tests for FEF-P37 verified_add runtime execution."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p37_verified_add_runtime_execution import (
    ATOL,
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p37_selected_runtime_targets_execute_and_match_reference():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P37_VERIFIED_ADD_RUNTIME_EXECUTION_PASS"
    assert payload["sourceFixture"] == "examples/verified_add.eml"
    assert summary["runtimeTargets"] == ["c", "cpp", "rust", "python", "javascript", "java"]
    assert summary["runtimeTargetCount"] == 6
    assert summary["sampleCountPerTarget"] == 6
    assert summary["totalSampleExecutions"] == 36
    assert summary["emissionPassCount"] == 6
    assert summary["runtimePassCount"] == 6
    assert summary["agreementPassCount"] == 6
    assert summary["allSelectedRuntimeTargetsPass"] is True
    assert summary["allSelectedTargetsAgreeWithReference"] is True
    assert summary["maxAbsError"] <= ATOL


def test_fef_p37_sample_grid_and_reference_values_are_explicit():
    payload = build_payload()
    samples = [sample["args"] for sample in payload["sampleGrid"]]
    assert samples == [
        [0.0, 0.0],
        [1.0, 2.0],
        [0.25, 0.75],
        [10.0, 0.5],
        [123.456, 0.001],
        [1.0e-9, 2.0e-9],
    ]
    assert payload["reference"]["values"] == [0.0, 3.0, 1.0, 10.5, 123.45700000000001, 3.0000000000000004e-09]


def test_fef_p37_rows_have_passing_frames():
    payload = build_payload()
    for row in payload["runtimeRows"]:
        assert row["emissionStatus"] == "pass"
        assert row["runtimeStatus"] == "pass"
        assert row["agreementStatus"] == "pass"
        assert row["sampleCount"] == 6
        assert row["maxAbsError"] <= ATOL
        assert len(row["frames"]) == 6


def test_fef_p37_keeps_broad_claims_false():
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


def test_fef_p37_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P37")


def test_fef_p37_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p37_verified_add_runtime_execution.py",
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
    assert "FEF_P37_VERIFIED_ADD_RUNTIME_EXECUTION_OK" in proc.stdout
