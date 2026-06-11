"""Tests for FEF-P98 loop generated-target runtime gate."""

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

from scripts.fef_p98_loop_generated_target_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
    validate_row,
)


def test_fef_p98_runs_selected_generated_c_loop_fixture():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P98_LOOP_GENERATED_TARGET_RUNTIME_GATE_PASS"
    assert payload["decision"] == "selected_loop_generated_c_fixture_runtime_recorded_reingest_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["runtimeComparisonKind"] == "local_generated_c_loop_fixture_against_selected_loop_expected_samples"
    assert summary["generatedTargetCompiled"] is True
    assert summary["generatedTargetRuntimeExecuted"] is True
    assert summary["selectedGeneratedTargetRuntimeEvidenceRecorded"] is True


def test_fef_p98_runtime_rows_match_selected_samples():
    payload = build_payload()
    rows = payload["runtimeComparison"]["rows"]
    assert len(rows) == 7
    for row in rows:
        validate_row(row)
        assert row["observed"] == row["expected"]
        assert row["absError"] == 0.0
        assert row["generatedTargetCompiled"] is True
        assert row["generatedTargetExecuted"] is True
        assert row["reingestedTargetExecuted"] is False
    assert payload["summary"]["passCount"] == 7
    assert payload["summary"]["failCount"] == 0
    assert payload["summary"]["maxAbsError"] == 0.0


def test_fef_p98_iteration_distribution_remains_visible():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["zeroIterationCount"] == 2
    assert summary["singleIterationCount"] == 1
    assert summary["multiIterationCount"] == 4
    assert summary["maxEffectiveIterationCount"] == 8


def test_fef_p98_runtime_gate_keeps_support_and_claims_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_loop_generated_c_fixture_runtime_execution"] == "recorded"
    assert gates["loop_reingest_execution"] == "not_performed"
    assert gates["loop_backedge_support"] == "blocked"
    assert "Re-ingested loop code was executed." in payload["blockedStatements"]
    assert summary["reingestedTargetExecuted"] is False
    assert summary["selectedCodegenFixtureInstalled"] is False
    assert summary["compilerBehaviorChanged"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopGeneratedTargetRuntimeClaim"] is False
    assert summary["loopReingestExecuted"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["loopBackedgeSemanticsImplemented"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p98_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P98")


def test_fef_p98_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p98_loop_generated_target_runtime_gate.py",
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
    assert "FEF_P98_LOOP_GENERATED_TARGET_RUNTIME_GATE_OK" in proc.stdout
