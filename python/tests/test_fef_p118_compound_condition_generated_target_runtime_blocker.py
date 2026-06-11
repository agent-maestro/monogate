"""Tests for FEF-P118 compound-condition generated-target runtime blocker."""

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

from scripts.fef_p118_compound_condition_generated_target_runtime_blocker import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    generated_target_gate,
    validate_payload,
)


def test_fef_p118_records_generated_target_runtime_blocker():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P118_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_BLOCKER_PASS"
    assert payload["decision"] == "compound_condition_generated_target_runtime_gate_blocked"
    assert summary["selectedFixtureId"] == "c_and_guard_return_v0"
    assert summary["generatedTargetGateStatus"] == "blocked_not_run"
    assert summary["generatedTargetGateBlocked"] is True
    assert summary["requiredBeforeRunCount"] == 5


def test_fef_p118_gate_inherits_p117_original_runtime_evidence():
    payload = build_payload()
    inherited = payload["generatedTargetRuntimeGate"]["inheritedOriginalRuntimeEvidence"]
    assert inherited["phase"] == "P117"
    assert inherited["comparisonCount"] == 7
    assert inherited["passCount"] == 7
    assert inherited["maxAbsError"] == 0.0
    assert inherited["rightPredicateEvaluatedCount"] == 4
    assert inherited["shortCircuitCount"] == 3
    assert inherited["originalCSourceExecuted"] is True


def test_fef_p118_required_before_run_names_compound_condition_policy_gaps():
    payload = build_payload()
    required = payload["generatedTargetRuntimeGate"]["requiredBeforeRun"]
    assert required == [
        "selected_compound_condition_lowering_rule",
        "generated_compound_condition_codegen_fixture",
        "generated_target_short_circuit_policy",
        "generated_target_runtime_comparison_harness",
        "compound_condition_reingest_policy_for_generated_targets",
    ]


def test_fef_p118_gate_helper_remains_fail_closed():
    p117_payload = {
        "summary": {
            "selectedFixtureId": "c_and_guard_return_v0",
            "comparisonCount": 7,
            "passCount": 7,
            "maxAbsError": 0.0,
            "rightPredicateEvaluatedCount": 4,
            "shortCircuitCount": 3,
            "allOriginalCSourceExecuted": True,
        }
    }
    gate = generated_target_gate(p117_payload)
    assert gate["status"] == "blocked_not_run"
    assert gate["blockedBy"] == "compound_condition_lowering_codegen_and_reingest_policy_missing"
    assert gate["generatedTargetExecuted"] is False
    assert gate["reingestedTargetExecuted"] is False
    assert gate["supportClaimAllowed"] is False


def test_fef_p118_blocks_execution_lowering_codegen_reingest_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["compoundConditionGeneratedTargetExecutionClaim"] is False
    assert summary["compoundConditionReingestExecutionClaim"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["shortCircuitPolicyImplemented"] is False
    assert summary["booleanNormalizationPolicyImplemented"] is False
    assert summary["predicateOrderPolicyImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p118_release_gates_remain_fail_closed():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["original_c_compound_condition_runtime_execution"] == "recorded_by_p117"
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert gates["compound_condition_reingest_execution"] == "not_performed"
    assert gates["compound_condition_lowering"] == "blocked"
    assert gates["generated_target_short_circuit_policy"] == "blocked"
    assert "Generated compound-condition target code was executed." in payload["blockedStatements"]


def test_fef_p118_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P118")


def test_fef_p118_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p118_compound_condition_generated_target_runtime_blocker.py",
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
    assert "FEF_P118_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_BLOCKER_OK" in proc.stdout
