"""Tests for FEF-P84 compound-condition row-filtered parsed-EML execution."""

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

from scripts.fef_p84_compound_condition_row_filtered_parsed_eml_execution import (
    CLAIM_FLAGS,
    build_execution_result,
    build_outputs,
    build_payload,
    evaluate_p82_parsed_shape,
    read_json,
    step01,
    validate_payload,
    P83_RESULT,
)


def test_fef_p84_executes_only_policy_allowed_rows():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P84_COMPOUND_CONDITION_ROW_FILTERED_PARSED_EML_EXECUTION_PASS"
    assert payload["decision"] == "selected_row_filtered_parsed_eml_execution_pass_blocked_rows_preserved"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["executedRowCount"] == 5
    assert summary["blockedRowCount"] == 2
    assert summary["passCount"] == 5
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0
    assert summary["fullP77RowComparisonPerformed"] is False


def test_fef_p84_preserves_zero_denominator_blockers():
    payload = build_payload()
    execution = payload["executionResult"]
    assert execution["executedSampleIds"] == ["sample_00", "sample_02", "sample_04", "sample_05", "sample_06"]
    assert execution["blockedSampleIds"] == ["sample_01", "sample_03"]
    blocked = [row for row in execution["rows"] if row["executionStatus"] == "blocked_by_p83_policy"]
    assert len(blocked) == 2
    assert all(row["observed"] is None for row in blocked)
    assert all(row["pass"] is None for row in blocked)


def test_fef_p84_evaluator_matches_selected_formula():
    assert step01(0.0) == 0.0
    assert step01(2.0) == 1.0
    values = evaluate_p82_parsed_shape(2.0, 4.0)
    assert values["lhs"] == 1.0
    assert values["rhsCandidate"] == 1.0
    assert values["rhs"] == 1.0
    assert values["selected"] == 0.5
    assert values["observed"] == 0.5
    left_false = evaluate_p82_parsed_shape(-1.0, -2.0)
    assert left_false["lhs"] == 0.0
    assert left_false["observed"] == 0.0


def test_fef_p84_execution_result_sources_p83_policy():
    p83_payload = read_json(P83_RESULT)
    result = build_execution_result(p83_payload["executionPolicy"])
    assert result["rowCount"] == 7
    assert result["executedRowCount"] == 5
    assert result["blockedRowCount"] == 2
    assert result["allExecutedRowsPass"] is True
    assert result["zeroDenominatorRowsExecuted"] is False


def test_fef_p84_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_row_filtered_parsed_eml_execution"] == "executed_p83_allowed_rows_only"
    assert gates["blocked_zero_denominator_rows"] == "preserved_blocked"
    assert gates["full_p77_row_comparison"] == "blocked_not_performed"
    assert "All P77 rows were executed through parsed EML." in payload["blockedStatements"]
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p84_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P84")


def test_fef_p84_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p84_compound_condition_row_filtered_parsed_eml_execution.py",
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
    assert "FEF_P84_COMPOUND_CONDITION_ROW_FILTERED_PARSED_EML_EXECUTION_OK" in proc.stdout
