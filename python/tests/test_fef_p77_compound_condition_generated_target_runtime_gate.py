"""Tests for FEF-P77 compound-condition generated-target runtime gate."""

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

from scripts.fef_p77_compound_condition_generated_target_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    c_harness_source,
    parse_runtime_output,
    validate_payload,
    validate_row,
)


def test_fef_p77_records_selected_generated_runtime_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P77_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_GATE_PASS"
    assert payload["decision"] == "selected_generated_c_fixture_runtime_recorded_reingest_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0
    assert summary["selectedGeneratedTargetRuntimeEvidenceRecorded"] is True


def test_fef_p77_rows_match_generated_c_outputs_and_expected_values():
    payload = build_payload()
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
        assert row["observed"] == row["expected"]
        assert row["generatedTargetExecuted"] is True
        assert row["reingestedTargetExecuted"] is False


def test_fef_p77_runtime_scope_is_selected_generated_fixture_only():
    payload = build_payload()
    runtime = payload["runtimeComparison"]
    assert runtime["comparisonKind"] == "local_generated_c_fixture_against_compound_condition_expected_samples"
    assert runtime["targetLanguage"] == "c"
    assert runtime["generatedTargetExecuted"] is True
    assert runtime["reingestedTargetExecuted"] is False
    assert runtime["installedInForge"] is False
    assert payload["summary"]["generatedTargetRuntimeExecuted"] is True
    assert payload["summary"]["reingestedTargetExecuted"] is False
    assert payload["summary"]["helperRuntimeInstalled"] is False


def test_fef_p77_c_harness_contains_generated_fixture_source():
    payload = build_payload()
    source = c_harness_source(payload["selectedCodegenFixture"]["source"], payload["runtimeComparison"]["rows"][:1])
    assert "static double mg_step01(double value)" in source
    assert "static double mg_nonzero01(double value)" in source
    assert "static double mg_guarded_div" in source
    assert "c_and_short_circuit_guard_v0_generated_fixture" in source
    assert "int main(void)" in source


def test_fef_p77_runtime_output_parser():
    observed = parse_runtime_output("sample_00 0.5\nsample_01 0\n")
    assert observed == {"sample_00": 0.5, "sample_01": 0.0}


def test_fef_p77_short_circuit_distribution_is_preserved():
    payload = build_payload()
    rows = payload["runtimeComparison"]["rows"]
    left_false = [row for row in rows if row["path"] == "left_false_short_circuit"]
    right_guard = [row for row in rows if row["path"] == "right_false_zero_denominator_guard"]
    assert len(left_false) == 3
    assert all(row["rhsEvaluated"] is False for row in left_false)
    assert len(right_guard) == 1
    assert right_guard[0]["selected"] == 0.0
    assert payload["summary"]["leftFalseShortCircuitCount"] == 3
    assert payload["summary"]["rightFalseGuardCount"] == 1


def test_fef_p77_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_generated_c_fixture_runtime_execution"] == "recorded"
    assert gates["helper_runtime_installation"] == "not_performed"
    assert gates["compound_condition_reingest_execution"] == "not_performed"
    assert gates["compound_condition_support"] == "blocked"
    assert "Re-ingested compound-condition code was executed." in payload["blockedStatements"]
    assert summary["compoundConditionGeneratedTargetRuntimeClaim"] is False
    assert summary["compoundConditionReingestExecuted"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["guardedDivisionRuntimeHelperInstalled"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p77_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P77")


def test_fef_p77_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p77_compound_condition_generated_target_runtime_gate.py",
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
    assert "FEF_P77_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_GATE_OK" in proc.stdout
