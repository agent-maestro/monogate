"""Tests for FEF-P115 compound-condition policy gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p115_compound_condition_policy_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    policy_rows,
    runtime_eligibility_checks,
    validate_payload,
)


def test_fef_p115_records_policy_gate_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P115_COMPOUND_CONDITION_POLICY_GATE_PASS"
    assert payload["decision"] == "compound_condition_policy_specified_not_applied_reference_runtime_eligible_next"
    assert summary["selectedFixtureId"] == "c_and_guard_return_v0"
    assert summary["p114SampleCount"] == 7
    assert summary["policyRuleCount"] == 4
    assert summary["allP114SamplesStillNotExecuted"] is True


def test_fef_p115_policy_rows_cover_required_families():
    rows = policy_rows()
    assert {row["policyFamily"] for row in rows} == {
        "short_circuit",
        "predicate_truth_table",
        "boolean_normalization",
        "return_path",
    }
    assert all(row["status"] == "specified_not_applied" for row in rows)
    assert all(row["implementationApplied"] is False for row in rows)
    assert rows[0]["requiredOrder"] == [
        "evaluate_left_predicate",
        "evaluate_right_predicate_only_if_left_true",
        "select_return_path",
    ]


def test_fef_p115_policy_preserves_and_short_circuit_boundary():
    payload = build_payload()
    rules = {rule["id"]: rule for rule in payload["policyRules"]}
    assert rules["and_left_to_right_short_circuit_v0"]["operator"] == "and"
    assert rules["predicate_truth_table_for_selected_and_v0"]["truePath"] == "left_true_right_true_return_sum"
    assert rules["predicate_truth_table_for_selected_and_v0"]["falsePaths"] == [
        "left_true_right_false_return_zero",
        "left_false_short_circuit_return_zero",
    ]
    assert rules["boolean_normalization_preserve_source_order_v0"]["disallowedNormalization"] == "commute_or_eagerly_evaluate_predicates"
    assert rules["branch_path_return_mapping_v0"]["returnMapping"]["left_false_short_circuit_return_zero"] == "0.0"


def test_fef_p115_runtime_eligibility_is_next_gate_only():
    payload = build_payload()
    checks = {check["id"]: check["status"] for check in runtime_eligibility_checks()}
    assert checks["expected_samples_exist"] == "satisfied_by_p114"
    assert checks["reference_runtime_may_be_next"] == "eligible_next_gate_only"
    assert payload["summary"]["eligibleForReferenceRuntimeNextGate"] is True
    assert payload["summary"]["referenceRuntimeComparisonClaim"] is False


def test_fef_p115_blocks_execution_policies_lowering_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["shortCircuitPolicyImplemented"] is False
    assert summary["booleanNormalizationPolicyImplemented"] is False
    assert summary["predicateOrderPolicyImplemented"] is False
    assert summary["compoundConditionRuntimeExecutionClaim"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["allP114SamplesStillNotLowered"] is True
    assert summary["allP114PoliciesStillNotApplied"] is True


def test_fef_p115_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["compound_condition_policy_gate"] == "recorded"
    assert gates["short_circuit_policy"] == "specified_not_applied"
    assert gates["predicate_truth_policy"] == "specified_not_applied"
    assert gates["boolean_normalization_policy"] == "specified_not_applied"
    assert gates["reference_runtime_comparison"] == "eligible_next_gate_only"
    assert gates["compound_condition_runtime_execution"] == "not_performed"
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p115_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P115")


def test_fef_p115_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p115_compound_condition_policy_gate.py",
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
    assert "FEF_P115_COMPOUND_CONDITION_POLICY_GATE_OK" in proc.stdout
