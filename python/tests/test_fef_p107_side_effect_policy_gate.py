"""Tests for FEF-P107 side-effect policy gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p107_side_effect_policy_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    policy_rows,
    runtime_eligibility_checks,
    validate_payload,
)


def test_fef_p107_records_policy_gate_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P107_SIDE_EFFECT_POLICY_GATE_PASS"
    assert payload["decision"] == "side_effect_policy_specified_not_applied_reference_runtime_eligible_next"
    assert summary["selectedFixtureId"] == "c_global_state_update_v0"
    assert summary["p106SampleCount"] == 7
    assert summary["policyRuleCount"] == 4
    assert summary["allP106SamplesStillNotExecuted"] is True


def test_fef_p107_policy_rows_cover_required_families():
    rows = policy_rows()
    assert {row["policyFamily"] for row in rows} == {
        "effect_order",
        "external_call",
        "memory_alias",
        "no_effect_path",
    }
    assert all(row["status"] == "specified_not_applied" for row in rows)
    assert all(row["implementationApplied"] is False for row in rows)
    assert rows[0]["requiredOrder"] == [
        "evaluate_guard",
        "perform_modeled_call_if_guard_true",
        "write_modeled_state_if_call_occurs",
        "return_final_state",
    ]


def test_fef_p107_runtime_eligibility_is_next_gate_only():
    payload = build_payload()
    checks = {check["id"]: check["status"] for check in runtime_eligibility_checks()}
    assert checks["expected_samples_exist"] == "satisfied_by_p106"
    assert checks["reference_runtime_may_be_next"] == "eligible_next_gate_only"
    assert payload["summary"]["eligibleForReferenceRuntimeNextGate"] is True
    assert payload["summary"]["referenceRuntimeComparisonClaim"] is False


def test_fef_p107_blocks_execution_policies_lowering_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["effectOrderPolicyImplemented"] is False
    assert summary["externalCallPolicyImplemented"] is False
    assert summary["memoryAliasPolicyImplemented"] is False
    assert summary["sideEffectRuntimeExecutionClaim"] is False
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["sideEffectMemorySupportClaim"] is False
    assert summary["allExternalCallsStillNotPerformed"] is True
    assert summary["allMemoryWritesStillNotPerformed"] is True


def test_fef_p107_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["side_effect_policy_gate"] == "recorded"
    assert gates["effect_order_policy"] == "specified_not_applied"
    assert gates["external_call_policy"] == "specified_not_applied"
    assert gates["memory_alias_policy"] == "specified_not_applied"
    assert gates["reference_runtime_comparison"] == "eligible_next_gate_only"
    assert gates["side_effect_runtime_execution"] == "not_performed"
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p107_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P107")


def test_fef_p107_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p107_side_effect_policy_gate.py",
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
    assert "FEF_P107_SIDE_EFFECT_POLICY_GATE_OK" in proc.stdout
