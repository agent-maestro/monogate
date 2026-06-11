"""Tests for FEF-P85 compound-condition guarded-div source primitive execution."""

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

from scripts.fef_p85_compound_condition_guarded_div_source_primitive_execution import (
    CLAIM_FLAGS,
    build_execution_result,
    build_outputs,
    build_payload,
    evaluate_guarded_div_source_primitive,
    guarded_div,
    read_json,
    validate_payload,
    P84_RESULT,
)


def test_fef_p85_executes_all_rows_with_guarded_div_source_primitive():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P85_COMPOUND_CONDITION_GUARDED_DIV_SOURCE_PRIMITIVE_EXECUTION_PASS"
    assert payload["decision"] == "selected_guarded_div_source_primitive_executes_all_rows_installation_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["executedRowCount"] == 7
    assert summary["p84PreviouslyBlockedRowCount"] == 2
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0
    assert summary["fullP77GuardedPrimitiveComparisonPerformed"] is True


def test_fef_p85_represents_p84_blocked_zero_denominator_rows_without_division():
    payload = build_payload()
    execution = payload["executionResult"]
    assert execution["executedSampleIds"] == [
        "sample_00",
        "sample_01",
        "sample_02",
        "sample_03",
        "sample_04",
        "sample_05",
        "sample_06",
    ]
    assert execution["previouslyBlockedSampleIds"] == ["sample_01", "sample_03"]
    blocked = [row for row in execution["rows"] if row["wasBlockedInP84"]]
    assert len(blocked) == 2
    assert all(row["zeroDenominator"] is True for row in blocked)
    assert all(row["intermediates"]["divisionEvaluated"] is False for row in blocked)
    assert all(row["intermediates"]["defaultUsed"] is True for row in blocked)
    assert all(row["observed"] == 0.0 for row in blocked)


def test_fef_p85_guarded_div_primitive_semantics():
    guarded = guarded_div(2.0, 4.0, 0.0, 1.0)
    assert guarded["value"] == 0.5
    assert guarded["divisionEvaluated"] is True
    skipped = guarded_div(2.0, 0.0, 0.0, 0.0)
    assert skipped["value"] == 0.0
    assert skipped["divisionEvaluated"] is False
    values = evaluate_guarded_div_source_primitive(2.0, 4.0)
    assert values["lhs"] == 1.0
    assert values["rhs"] == 1.0
    assert values["guardedDivValue"] == 0.5
    assert values["observed"] == 0.5
    zero_denominator = evaluate_guarded_div_source_primitive(2.0, 0.0)
    assert zero_denominator["rhs"] == 0.0
    assert zero_denominator["divisionEvaluated"] is False
    assert zero_denominator["observed"] == 0.0
    left_false = evaluate_guarded_div_source_primitive(-1.0, 0.0)
    assert left_false["rhsEvaluated"] is False
    assert left_false["divisionEvaluated"] is False
    assert left_false["observed"] == 0.0


def test_fef_p85_execution_result_sources_p84_rows():
    p84_payload = read_json(P84_RESULT)
    result = build_execution_result(p84_payload)
    assert result["rowCount"] == 7
    assert result["executedRowCount"] == 7
    assert result["p84PreviouslyBlockedRowCount"] == 2
    assert result["zeroDenominatorRowsWithDivisionSkipped"] == 2
    assert result["zeroDenominatorDivisionEvaluated"] is False
    assert result["allRowsPass"] is True


def test_fef_p85_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_guarded_div_source_primitive_execution"] == "executed_all_selected_rows"
    assert gates["zero_denominator_non_evaluation_boundary"] == "preserved_by_source_primitive"
    assert gates["source_primitive_installation"] == "not_performed"
    assert "The selected guarded-div source primitive is installed in eFrog or Forge." in payload["blockedStatements"]
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["sourcePrimitiveInstalled"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p85_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P85")


def test_fef_p85_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p85_compound_condition_guarded_div_source_primitive_execution.py",
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
    assert "FEF_P85_COMPOUND_CONDITION_GUARDED_DIV_SOURCE_PRIMITIVE_EXECUTION_OK" in proc.stdout
