"""Tests for FEF-P95 loop generated-target runtime blocker."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p95_loop_generated_target_runtime_blocker import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_gate,
    validate_payload,
)


def test_fef_p95_records_blocked_generated_target_gate():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P95_LOOP_GENERATED_TARGET_RUNTIME_BLOCKER_PASS"
    assert payload["decision"] == "loop_generated_target_runtime_gate_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["generatedTargetGateStatus"] == "blocked_not_run"
    assert summary["generatedTargetGateBlocked"] is True


def test_fef_p95_inherits_p94_original_runtime_evidence_without_rerun_claim():
    payload = build_payload()
    gate = payload["generatedTargetRuntimeGate"]
    validate_gate(gate)
    inherited = gate["inheritedOriginalRuntimeEvidence"]
    assert inherited["phase"] == "P94"
    assert inherited["comparisonCount"] == 7
    assert inherited["passCount"] == 7
    assert inherited["maxAbsError"] == 0.0
    assert inherited["originalCSourceExecuted"] is True
    assert payload["summary"]["p94OriginalRuntimeComparisons"] == 7
    assert payload["summary"]["p94OriginalRuntimePassCount"] == 7


def test_fef_p95_required_before_run_items_are_explicit():
    payload = build_payload()
    required = payload["generatedTargetRuntimeGate"]["requiredBeforeRun"]
    assert required == [
        "loop_lowering_rule",
        "loop_header_latch_variant_semantics",
        "generated_target_fixture",
        "runtime_comparison_harness",
        "reingest_policy_for_generated_loop",
    ]
    assert payload["summary"]["requiredBeforeRunCount"] == 5


def test_fef_p95_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert gates["loop_lowering"] == "blocked"
    assert gates["loop_backedge_support"] == "blocked"
    assert gates["loop_reingest_execution"] == "not_performed"
    assert "Generated loop target code was executed." in payload["blockedStatements"]
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["loopGeneratedTargetExecutionClaim"] is False
    assert summary["loopReingestExecutionClaim"] is False
    assert summary["loopLoweringClaim"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["loopBackedgeSemanticsImplemented"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p95_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P95")


def test_fef_p95_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p95_loop_generated_target_runtime_blocker.py",
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
    assert "FEF_P95_LOOP_GENERATED_TARGET_RUNTIME_BLOCKER_OK" in proc.stdout
