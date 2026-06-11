"""Tests for FEF-P68 assignment/phi reference-runtime gate."""

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

from scripts.fef_p68_assignment_phi_reference_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    reference_runtime,
    validate_payload,
    validate_row,
)


def test_fef_p68_records_reference_runtime_gate_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P68_ASSIGNMENT_PHI_REFERENCE_RUNTIME_GATE_PASS"
    assert payload["decision"] == "assignment_phi_reference_runtime_gate_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_branch_assignment_merge_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0


def test_fef_p68_reference_rows_match_runtime_and_expected_values():
    payload = build_payload()
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
        assert row["observed"] == reference_runtime(row["inputs"]["x"], row["inputs"]["y"])
        assert row["observed"] == row["expected"]
        assert row["assignmentTaken"] == (row["inputs"]["x"] > 0.0)
        assert row["referenceRuntimeOnly"] is True
        assert row["sourceOrGeneratedCodeExecuted"] is False


def test_fef_p68_runtime_scope_is_reference_only():
    payload = build_payload()
    runtime = payload["runtimeComparison"]
    assert runtime["comparisonKind"] == "local_python_reference_runtime_against_assignment_phi_expected_samples"
    assert runtime["originalSourceExecuted"] is False
    assert runtime["generatedTargetExecuted"] is False
    assert runtime["reingestedTargetExecuted"] is False
    assert payload["summary"]["sourceOrGeneratedCodeExecuted"] is False


def test_fef_p68_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["assignment_phi_reference_runtime_gate"] == "recorded"
    assert gates["original_c_assignment_phi_runtime_execution"] == "not_performed"
    assert gates["generated_target_runtime_execution"] == "not_performed"
    assert gates["assignment_phi_lowering"] == "blocked"
    assert "Generated assignment/phi target code was executed." in payload["blockedStatements"]
    assert summary["assignmentPhiSourceExecutionClaim"] is False
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


def test_fef_p68_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P68")


def test_fef_p68_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p68_assignment_phi_reference_runtime_gate.py",
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
    assert "FEF_P68_ASSIGNMENT_PHI_REFERENCE_RUNTIME_GATE_OK" in proc.stdout
