"""Tests for FEF-P69 assignment/phi original C runtime gate."""

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

from scripts.fef_p69_assignment_phi_original_c_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    c_harness_source,
    parse_runtime_output,
    validate_payload,
    validate_row,
)


def test_fef_p69_records_original_c_runtime_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P69_ASSIGNMENT_PHI_ORIGINAL_C_RUNTIME_GATE_PASS"
    assert payload["decision"] == "assignment_phi_original_c_runtime_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_branch_assignment_merge_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0
    assert summary["selectedOriginalCRuntimeEvidenceRecorded"] is True


def test_fef_p69_rows_match_original_c_outputs_and_expected_values():
    payload = build_payload()
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
        assert row["observed"] == row["expected"]
        assert row["originalCSourceExecuted"] is True
        assert row["generatedTargetExecuted"] is False
        assert row["reingestedTargetExecuted"] is False


def test_fef_p69_runtime_scope_is_original_c_only():
    payload = build_payload()
    runtime = payload["runtimeComparison"]
    assert runtime["comparisonKind"] == "local_original_c_source_runtime_against_assignment_phi_expected_samples"
    assert runtime["sourceLanguage"] == "c"
    assert runtime["originalSourceExecuted"] is True
    assert runtime["generatedTargetExecuted"] is False
    assert runtime["reingestedTargetExecuted"] is False
    assert payload["summary"]["allOriginalCSourceExecuted"] is True
    assert payload["summary"]["generatedTargetExecuted"] is False
    assert payload["summary"]["reingestedTargetExecuted"] is False


def test_fef_p69_c_harness_contains_selected_assignment_phi_source():
    source = c_harness_source([{"sampleId": "sample_00", "inputs": {"x": 2.0, "y": 5.0}}])
    assert "static double selected_assignment_phi(double x, double y)" in source
    assert "double z = x;" in source
    assert "if (x > 0.0)" in source
    assert "z = y;" in source
    assert "return z;" in source


def test_fef_p69_runtime_output_parser():
    observed = parse_runtime_output("sample_00 5\nsample_01 -2\n")
    assert observed == {"sample_00": 5.0, "sample_01": -2.0}


def test_fef_p69_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["original_c_assignment_phi_runtime_execution"] == "recorded"
    assert gates["generated_target_runtime_execution"] == "not_performed"
    assert gates["assignment_phi_reingest_execution"] == "not_performed"
    assert gates["assignment_phi_lowering"] == "blocked"
    assert "Generated assignment/phi target code was executed." in payload["blockedStatements"]
    assert summary["assignmentPhiGeneratedTargetExecutionClaim"] is False
    assert summary["assignmentPhiReingestExecutionClaim"] is False
    assert summary["assignmentPhiLoweringClaim"] is False
    assert summary["assignmentPhiSupportClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p69_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P69")


def test_fef_p69_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p69_assignment_phi_original_c_runtime_gate.py",
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
    assert "FEF_P69_ASSIGNMENT_PHI_ORIGINAL_C_RUNTIME_GATE_OK" in proc.stdout
