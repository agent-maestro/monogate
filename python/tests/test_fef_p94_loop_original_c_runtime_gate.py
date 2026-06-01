"""Tests for FEF-P94 loop original C runtime gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts import fef_p93_loop_reference_runtime_gate as p93
from scripts.fef_p94_loop_original_c_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
    validate_row,
)


def test_fef_p94_records_original_c_runtime_gate_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P94_LOOP_ORIGINAL_C_RUNTIME_GATE_PASS"
    assert payload["decision"] == "loop_original_c_runtime_gate_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0


def test_fef_p94_original_c_rows_match_reference_and_expected_values():
    payload = build_payload()
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
        runtime = p93.reference_runtime(row["inputs"]["x"], int(row["inputs"]["n"]))
        assert row["referenceObserved"] == runtime["observed"]
        assert row["observed"] == row["expected"]
        assert row["iterationCount"] == runtime["iterationCount"]
        assert row["backEdgeTakenCount"] == runtime["backEdgeTakenCount"]
        assert row["originalCSourceExecuted"] is True
        assert row["generatedTargetExecuted"] is False
        assert row["reingestedTargetExecuted"] is False


def test_fef_p94_runtime_scope_is_original_c_only_under_p92_policy():
    payload = build_payload()
    runtime = payload["runtimeComparison"]
    assert runtime["comparisonKind"] == "original_c_loop_runtime_against_p93_reference_runtime_under_p92_policy"
    assert runtime["policyAppliedAsPrecondition"] is True
    assert runtime["originalSourceExecuted"] is True
    assert runtime["generatedTargetExecuted"] is False
    assert runtime["reingestedTargetExecuted"] is False
    assert payload["originalCSourceExecution"]["sourceExecuted"] is True
    assert payload["originalCSourceExecution"]["compileReturnCode"] == 0
    assert payload["originalCSourceExecution"]["runReturnCode"] == 0
    assert payload["summary"]["allPolicyEligible"] is True
    assert payload["summary"]["allOriginalCSourceExecuted"] is True


def test_fef_p94_comparison_paths_preserve_iteration_distribution():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["zeroIterationCount"] == 2
    assert summary["singleIterationCount"] == 1
    assert summary["multiIterationCount"] == 4
    assert summary["maxIterationCount"] == 8
    assert summary["totalBackEdgeTakenCount"] == 21


def test_fef_p94_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["loop_original_c_runtime_gate"] == "recorded"
    assert gates["original_c_loop_runtime_execution"] == "recorded"
    assert gates["generated_target_runtime_execution"] == "not_performed"
    assert gates["loop_reingest_execution"] == "not_performed"
    assert gates["loop_lowering"] == "blocked"
    assert gates["loop_backedge_support"] == "blocked"
    assert "Generated loop target code was executed." in payload["blockedStatements"]
    assert summary["selectedOriginalCLoopRuntimeEvidenceRecorded"] is True
    assert summary["originalSourceExecuted"] is True
    assert summary["loopOriginalSourceExecutionClaim"] is False
    assert summary["loopGeneratedTargetExecutionClaim"] is False
    assert summary["loopReingestExecutionClaim"] is False
    assert summary["loopLoweringClaim"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["loopBoundednessPolicyGeneralClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p94_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P94")


def test_fef_p94_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p94_loop_original_c_runtime_gate.py",
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
    assert "FEF_P94_LOOP_ORIGINAL_C_RUNTIME_GATE_OK" in proc.stdout
