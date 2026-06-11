"""Tests for FEF-P102 loop parsed-EML Python comparison."""

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

from scripts.fef_p102_loop_parsed_eml_python_comparison import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    evaluate_p101_parsed_eml_shape,
    validate_payload,
)


def test_fef_p102_records_parsed_eml_python_comparison():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P102_LOOP_PARSED_EML_PYTHON_COMPARISON_PASS"
    assert payload["decision"] == "selected_loop_parsed_eml_python_comparison_recorded_installed_support_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["p101ReingestParseSucceeded"] is True
    assert summary["parsedEmlPythonComparisonPerformed"] is True
    assert summary["rowCount"] == 7
    assert summary["passCount"] == 7
    assert summary["maxAbsError"] == 0.0


def test_fef_p102_evaluates_p101_parsed_loop_shape():
    assert evaluate_p101_parsed_eml_shape(2.0, 0.0)["observed"] == 0.0
    assert evaluate_p101_parsed_eml_shape(2.0, 3.0)["observed"] == 6.0
    assert evaluate_p101_parsed_eml_shape(-1.5, 4.0)["observed"] == -6.0
    assert evaluate_p101_parsed_eml_shape(3.0, -2.0)["observed"] == 0.0


def test_fef_p102_rows_match_p98_generated_runtime_rows():
    payload = build_payload()
    rows = payload["comparisonResult"]["rows"]
    assert [row["sampleId"] for row in rows] == [f"sample_0{index}" for index in range(7)]
    assert [row["effectiveIterationCount"] for row in rows] == [0, 1, 3, 4, 5, 0, 8]
    assert all(row["pass"] is True for row in rows)
    assert all(row["absError"] == 0.0 for row in rows)
    assert rows[5]["parsedEmlPythonObserved"] == 0.0
    assert rows[6]["parsedEmlPythonObserved"] == 2.0


def test_fef_p102_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_parsed_eml_python_comparison"] == "recorded"
    assert gates["recompiled_python_target_execution"] == "not_performed"
    assert gates["loop_helper_adapter_installation"] == "not_performed"
    assert gates["loop_backedge_support"] == "blocked"
    assert "A Forge-recompiled Python target was executed." in payload["blockedStatements"]
    assert summary["recompiledPythonTargetExecuted"] is False
    assert summary["loopReingestSupported"] is False
    assert summary["selectedLoopHelperAdapterInstalled"] is False
    assert summary["compilerBehaviorChanged"] is False
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p102_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P102")


def test_fef_p102_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p102_loop_parsed_eml_python_comparison.py",
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
    assert "FEF_P102_LOOP_PARSED_EML_PYTHON_COMPARISON_OK" in proc.stdout
