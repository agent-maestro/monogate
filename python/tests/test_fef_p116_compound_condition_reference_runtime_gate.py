"""Tests for FEF-P116 compound-condition reference-runtime gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p116_compound_condition_reference_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    modeled_reference_runtime,
    validate_payload,
    validate_row,
)


def test_fef_p116_records_reference_runtime_gate_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P116_COMPOUND_CONDITION_REFERENCE_RUNTIME_GATE_PASS"
    assert payload["decision"] == "compound_condition_reference_runtime_gate_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_and_guard_return_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0


def test_fef_p116_reference_rows_match_modeled_runtime_and_expected_values():
    payload = build_payload()
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
        runtime = modeled_reference_runtime(row)
        assert row["observed"] == runtime["observed"]
        assert row["observed"] == row["expected"]
        assert row["referenceRuntimeOnly"] is True
        assert row["originalSourceExecuted"] is False
        assert row["generatedTargetExecuted"] is False
        assert row["reingestedTargetExecuted"] is False


def test_fef_p116_preserves_short_circuit_event_paths():
    payload = build_payload()
    rows = payload["runtimeComparison"]["rows"]
    assert sum(1 for row in rows if row["rightPredicateEvaluated"]) == 4
    assert sum(1 for row in rows if not row["rightPredicateEvaluated"]) == 3
    short_circuit_rows = [row for row in rows if not row["rightPredicateEvaluated"]]
    assert all("short_circuit_skip_right_predicate" in row["orderedEvents"] for row in short_circuit_rows)
    assert all(row["rightPredicateValue"] is None for row in short_circuit_rows)


def test_fef_p116_runtime_scope_is_reference_only():
    payload = build_payload()
    runtime = payload["runtimeComparison"]
    assert runtime["comparisonKind"] == "local_modeled_python_reference_runtime_against_compound_condition_expected_samples_under_p115_policy"
    assert runtime["originalSourceExecuted"] is False
    assert runtime["generatedTargetExecuted"] is False
    assert runtime["reingestedTargetExecuted"] is False
    assert payload["summary"]["allP115PolicyUsedAsPrecondition"] is True
    assert payload["summary"]["originalSourceExecuted"] is False


def test_fef_p116_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["compound_condition_reference_runtime_gate"] == "recorded"
    assert gates["original_c_compound_condition_runtime_execution"] == "not_performed"
    assert gates["generated_target_runtime_execution"] == "not_performed"
    assert gates["compound_condition_reingest_execution"] == "not_performed"
    assert gates["compound_condition_lowering"] == "blocked"
    assert "Generated compound-condition target code was executed." in payload["blockedStatements"]
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["shortCircuitPolicyImplemented"] is False
    assert summary["booleanNormalizationPolicyImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p116_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P116")


def test_fef_p116_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p116_compound_condition_reference_runtime_gate.py",
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
    assert "FEF_P116_COMPOUND_CONDITION_REFERENCE_RUNTIME_GATE_OK" in proc.stdout
