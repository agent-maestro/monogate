"""Tests for FEF-P87 guarded-div re-ingest boundary probe."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p87_compound_condition_guarded_div_reingest_boundary_probe import (
    CLAIM_FLAGS,
    boundary_contract,
    build_boundary_probe,
    build_outputs,
    build_payload,
    read_json,
    validate_payload,
    P86_RESULT,
)


def test_fef_p87_records_fail_closed_boundary_probe():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P87_COMPOUND_CONDITION_GUARDED_DIV_REINGEST_BOUNDARY_PROBE_PASS"
    assert payload["decision"] == "selected_guarded_div_reingest_boundary_probe_pass_execution_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["contractStatus"] == "boundary_probe_pass_reingest_execution_blocked"
    assert summary["boundaryPassCount"] == 7
    assert summary["boundaryFailCount"] == 0
    assert summary["failClosedReingestBoundaryProbePerformed"] is True
    assert summary["actualReingestExecutionPerformed"] is False


def test_fef_p87_boundary_contract_requires_helper_surface_and_blocked_execution():
    p86_payload = read_json(P86_RESULT)
    contract = boundary_contract(p86_payload)
    assert contract["contractId"] == "selected_guarded_div_reingest_boundary_contract_v0"
    assert contract["requiredHelperSurface"] == ["nonzero01", "guarded_div"]
    assert len(contract["requiredBoundaryProperties"]) == 6
    assert contract["actualReingestExecutionPerformed"] is False
    assert contract["installedInEfrog"] is False
    assert contract["installedInForge"] is False


def test_fef_p87_probe_preserves_zero_denominator_and_left_false_non_evaluation():
    payload = build_payload()
    probe = payload["boundaryProbe"]
    assert probe["rowCount"] == 7
    assert probe["zeroDenominatorRowCount"] == 2
    assert probe["zeroDenominatorRowsWithDivisionSkipped"] == 2
    assert probe["leftFalseRowCount"] == 3
    assert probe["leftFalseRowsWithRightSideSkipped"] == 3
    assert probe["nonEvaluationBoundaryPreserved"] is True
    zero_rows = [row for row in probe["rows"] if row["zeroDenominator"]]
    left_false_rows = [row for row in probe["rows"] if row["leftFalse"]]
    assert all(row["divisionEvaluated"] is False for row in zero_rows)
    assert all(row["rhsEvaluated"] is False for row in left_false_rows)


def test_fef_p87_probe_result_sources_p86_rows():
    p86_payload = read_json(P86_RESULT)
    result = build_boundary_probe(boundary_contract(p86_payload), p86_payload)
    assert result["actualReingestExecutionPerformed"] is False
    assert result["recompiledPythonExecuted"] is False
    assert result["candidateInstalled"] is False
    assert result["allCandidateRowsPass"] is True
    assert result["boundaryPassCount"] == 7


def test_fef_p87_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_guarded_div_reingest_boundary_probe"] == "pass_execution_blocked"
    assert gates["actual_reingest_execution"] == "blocked_not_performed"
    assert gates["source_primitive_installation"] == "not_performed"
    assert "Re-ingested compound-condition code executed successfully." in payload["blockedStatements"]
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


def test_fef_p87_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P87")


def test_fef_p87_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p87_compound_condition_guarded_div_reingest_boundary_probe.py",
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
    assert "FEF_P87_COMPOUND_CONDITION_GUARDED_DIV_REINGEST_BOUNDARY_PROBE_OK" in proc.stdout
