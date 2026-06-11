"""Tests for FEF-P75 compound-condition lowering rule packet."""

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

from scripts.fef_p75_compound_condition_lowering_rule_packet import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
    validate_row,
    validate_rule,
)


def test_fef_p75_records_selected_rule_without_compiler_change():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P75_COMPOUND_CONDITION_LOWERING_RULE_PACKET_PASS"
    assert payload["decision"] == "selected_compound_condition_lowering_rule_recorded_runtime_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["loweringRuleStatus"] == "candidate_rule_recorded_runtime_blocked"
    assert summary["loweringRuleScope"] == "selected_fixture_only"
    assert summary["compilerBehaviorChanged"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["compoundConditionLoweringImplemented"] is False


def test_fef_p75_rule_declares_required_helpers_and_semantics():
    payload = build_payload()
    rule = payload["loweringRule"]
    validate_rule(rule)
    assert rule["requiredHelpers"] == ["step01", "nonzero01", "guarded_div"]
    assert rule["valueLowering"]["selectedValue"] == "guarded_div(x, y, default=0.0, guard=rhs_y_nonzero)"
    assert "division is not evaluated unless y != 0.0" in rule["semanticRequirements"]
    assert rule["generatedTargetRuntimeStatusAfterRule"] == "blocked_until_helpers_and_codegen_exist"
    assert rule["supportClaimAllowed"] is False


def test_fef_p75_rule_validation_matches_existing_samples():
    payload = build_payload()
    rows = payload["ruleValidationRows"]
    assert len(rows) == 7
    for row in rows:
        validate_row(row)
        assert row["loweredRuleValue"] == row["expected"]
        assert row["absError"] == 0.0
        assert row["pass"] is True
    assert payload["summary"]["ruleValidationPassCount"] == 7
    assert payload["summary"]["ruleValidationFailCount"] == 0
    assert payload["summary"]["ruleValidationMaxAbsError"] == 0.0


def test_fef_p75_short_circuit_and_guard_behavior_are_visible():
    payload = build_payload()
    rows = {row["sampleId"]: row for row in payload["ruleValidationRows"]}
    left_false = [row for row in rows.values() if row["path"] == "left_false_short_circuit"]
    right_guard = [row for row in rows.values() if row["path"] == "right_false_zero_denominator_guard"]
    assert len(left_false) == 3
    assert all(row["rhsEvaluated"] is False for row in left_false)
    assert len(right_guard) == 1
    assert right_guard[0]["divisionProtected"] is True
    assert right_guard[0]["loweredRuleValue"] == 0.0


def test_fef_p75_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_compound_condition_lowering_rule"] == "recorded_runtime_blocked"
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert gates["compound_condition_support"] == "blocked"
    assert "Compound-condition lowering is implemented in Forge or eFrog." in payload["blockedStatements"]
    assert summary["compoundConditionGeneratedTargetExecuted"] is False
    assert summary["compoundConditionReingestExecuted"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["guardedDivisionRuntimeHelperImplemented"] is False
    assert summary["nonzeroPredicateRuntimeHelperImplemented"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p75_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P75")


def test_fef_p75_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p75_compound_condition_lowering_rule_packet.py",
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
    assert "FEF_P75_COMPOUND_CONDITION_LOWERING_RULE_PACKET_OK" in proc.stdout
