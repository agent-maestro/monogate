"""Tests for FEF-P96 loop lowering rule packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p96_loop_lowering_rule_packet import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
    validate_row,
    validate_rule,
)


def test_fef_p96_records_selected_rule_without_compiler_change():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P96_LOOP_LOWERING_RULE_PACKET_PASS"
    assert payload["decision"] == "selected_loop_lowering_rule_recorded_runtime_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["loweringRuleStatus"] == "candidate_rule_recorded_runtime_blocked"
    assert summary["loweringRuleScope"] == "selected_fixture_only_under_p92_policy"
    assert summary["compilerBehaviorChanged"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["loopLoweringImplemented"] is False


def test_fef_p96_rule_declares_bounded_accumulator_lowering():
    payload = build_payload()
    rule = payload["loweringRule"]
    validate_rule(rule)
    assert rule["candidateLowering"]["effectiveIterationBinding"] == "k = max(0, int(n))"
    assert rule["candidateLowering"]["loweredValue"] == "x * k"
    assert rule["boundednessPrecondition"]["policyId"] == "selected_c_while_accumulate_boundedness_policy_v0"
    assert rule["boundednessPrecondition"]["maxEffectiveIterationCount"] == 16
    assert "side_effecting_loop_body" in rule["rejectedSurfaces"]
    assert rule["generatedTargetRuntimeStatusAfterRule"] == "blocked_until_codegen_fixture_exists"
    assert rule["supportClaimAllowed"] is False


def test_fef_p96_rule_validation_matches_existing_samples():
    payload = build_payload()
    rows = payload["ruleValidationRows"]
    assert len(rows) == 7
    for row in rows:
        validate_row(row)
        assert row["loweredRuleValue"] == row["expected"]
        assert row["absError"] == 0.0
        assert row["pass"] is True
        assert row["generatedTargetExecuted"] is False
        assert row["reingestedTargetExecuted"] is False
    assert payload["summary"]["ruleValidationPassCount"] == 7
    assert payload["summary"]["ruleValidationFailCount"] == 0
    assert payload["summary"]["ruleValidationMaxAbsError"] == 0.0


def test_fef_p96_iteration_distribution_remains_visible():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["zeroIterationCount"] == 2
    assert summary["singleIterationCount"] == 1
    assert summary["multiIterationCount"] == 4
    assert summary["maxEffectiveIterationCount"] == 8


def test_fef_p96_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_loop_lowering_rule"] == "recorded_runtime_blocked"
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert gates["loop_backedge_support"] == "blocked"
    assert "Loop lowering is implemented in Forge or eFrog." in payload["blockedStatements"]
    assert summary["loopGeneratedTargetExecuted"] is False
    assert summary["loopReingestExecuted"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["loopBackedgeSemanticsImplemented"] is False
    assert summary["loopBoundednessPolicyGeneralClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p96_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P96")


def test_fef_p96_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p96_loop_lowering_rule_packet.py",
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
    assert "FEF_P96_LOOP_LOWERING_RULE_PACKET_OK" in proc.stdout
