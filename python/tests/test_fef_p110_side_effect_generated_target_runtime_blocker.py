"""Tests for FEF-P110 side-effect generated-target runtime blocker."""

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

from scripts.fef_p110_side_effect_generated_target_runtime_blocker import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    generated_target_gate,
    validate_payload,
)


def test_fef_p110_records_generated_target_runtime_blocker():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P110_SIDE_EFFECT_GENERATED_TARGET_RUNTIME_BLOCKER_PASS"
    assert payload["decision"] == "side_effect_generated_target_runtime_gate_blocked"
    assert summary["selectedFixtureId"] == "c_global_state_update_v0"
    assert summary["generatedTargetGateStatus"] == "blocked_not_run"
    assert summary["generatedTargetGateBlocked"] is True
    assert summary["requiredBeforeRunCount"] == 6


def test_fef_p110_gate_inherits_p109_stubbed_runtime_evidence():
    payload = build_payload()
    inherited = payload["generatedTargetRuntimeGate"]["inheritedOriginalStubbedRuntimeEvidence"]
    assert inherited["phase"] == "P109"
    assert inherited["comparisonCount"] == 7
    assert inherited["passCount"] == 7
    assert inherited["maxAbsError"] == 0.0
    assert inherited["stubbedCallCount"] == 4
    assert inherited["boundedStateWriteCount"] == 4
    assert inherited["stubbedOriginalCSourceExecuted"] is True


def test_fef_p110_required_before_run_names_side_effect_policy_gaps():
    payload = build_payload()
    required = payload["generatedTargetRuntimeGate"]["requiredBeforeRun"]
    assert required == [
        "selected_side_effect_lowering_rule",
        "generated_side_effect_codegen_fixture",
        "deterministic_external_call_stub_policy_for_generated_targets",
        "bounded_state_capture_model_for_generated_targets",
        "generated_target_runtime_comparison_harness",
        "side_effect_reingest_policy_for_generated_targets",
    ]


def test_fef_p110_gate_helper_remains_fail_closed():
    p109_payload = {
        "summary": {
            "selectedFixtureId": "c_global_state_update_v0",
            "comparisonCount": 7,
            "passCount": 7,
            "maxAbsError": 0.0,
            "stubbedCallCount": 4,
            "boundedStateWriteCount": 4,
            "allStubbedOriginalCSourceExecuted": True,
        }
    }
    gate = generated_target_gate(p109_payload)
    assert gate["status"] == "blocked_not_run"
    assert gate["blockedBy"] == "side_effect_lowering_and_codegen_policy_missing"
    assert gate["generatedTargetExecuted"] is False
    assert gate["reingestedTargetExecuted"] is False
    assert gate["supportClaimAllowed"] is False


def test_fef_p110_blocks_execution_lowering_codegen_reingest_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["liveExternalCallPerformed"] is False
    assert summary["unboundedMemoryMutationPerformed"] is False
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["sideEffectCodegenPolicyClaim"] is False
    assert summary["sideEffectReingestPolicyClaim"] is False
    assert summary["sideEffectMemorySupportClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p110_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P110")


def test_fef_p110_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p110_side_effect_generated_target_runtime_blocker.py",
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
    assert "FEF_P110_SIDE_EFFECT_GENERATED_TARGET_RUNTIME_BLOCKER_OK" in proc.stdout
