"""Tests for FEF-P93 loop reference-runtime gate."""

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

from scripts.fef_p93_loop_reference_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    reference_runtime,
    validate_payload,
    validate_row,
)


def test_fef_p93_records_reference_runtime_gate_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P93_LOOP_REFERENCE_RUNTIME_GATE_PASS"
    assert payload["decision"] == "loop_reference_runtime_gate_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0


def test_fef_p93_reference_rows_match_runtime_and_expected_values():
    payload = build_payload()
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
        runtime = reference_runtime(row["inputs"]["x"], int(row["inputs"]["n"]))
        assert row["observed"] == runtime["observed"]
        assert row["observed"] == row["expected"]
        assert row["iterationCount"] == runtime["iterationCount"]
        assert row["backEdgeTakenCount"] == runtime["backEdgeTakenCount"]
        assert row["referenceRuntimeOnly"] is True
        assert row["originalSourceExecuted"] is False
        assert row["generatedTargetExecuted"] is False
        assert row["reingestedTargetExecuted"] is False


def test_fef_p93_runtime_scope_is_reference_only_under_p92_policy():
    payload = build_payload()
    runtime = payload["runtimeComparison"]
    assert runtime["comparisonKind"] == "local_python_reference_runtime_against_loop_expected_samples_under_p92_policy"
    assert runtime["policyAppliedAsPrecondition"] is True
    assert runtime["originalSourceExecuted"] is False
    assert runtime["generatedTargetExecuted"] is False
    assert runtime["reingestedTargetExecuted"] is False
    assert payload["summary"]["allPolicyEligible"] is True
    assert payload["summary"]["allReferenceRuntimeOnly"] is True


def test_fef_p93_comparison_paths_preserve_iteration_distribution():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["zeroIterationCount"] == 2
    assert summary["singleIterationCount"] == 1
    assert summary["multiIterationCount"] == 4
    assert summary["maxIterationCount"] == 8
    assert summary["totalBackEdgeTakenCount"] == 21


def test_fef_p93_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["loop_reference_runtime_gate"] == "recorded"
    assert gates["original_c_loop_runtime_execution"] == "not_performed"
    assert gates["generated_target_runtime_execution"] == "not_performed"
    assert gates["loop_reingest_execution"] == "not_performed"
    assert gates["loop_lowering"] == "blocked"
    assert gates["loop_backedge_support"] == "blocked"
    assert "The original C loop source was executed." in payload["blockedStatements"]
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


def test_fef_p93_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P93")


def test_fef_p93_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p93_loop_reference_runtime_gate.py",
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
    assert "FEF_P93_LOOP_REFERENCE_RUNTIME_GATE_OK" in proc.stdout
