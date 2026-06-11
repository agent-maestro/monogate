"""Tests for FEF-P92 loop boundedness policy."""

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

from scripts.fef_p92_loop_boundedness_policy import (
    CLAIM_FLAGS,
    MAX_EFFECTIVE_ITERATIONS,
    build_outputs,
    build_payload,
    effective_iteration_count,
    validate_payload,
    validate_policy_row,
)


def test_fef_p92_records_policy_without_executing_loops():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P92_LOOP_BOUNDEDNESS_POLICY_PASS"
    assert payload["decision"] == "loop_boundedness_policy_recorded_execution_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["policyRecorded"] is True
    assert summary["policyAppliedToRuntime"] is False
    assert summary["runtimeExecutionPerformed"] is False
    assert summary["loopBackedgeSupportClaim"] is False


def test_fef_p92_policy_shape_is_selected_and_bounded():
    payload = build_payload()
    policy = payload["boundednessPolicy"]
    assert policy["policyId"] == "selected_c_while_accumulate_boundedness_policy_v0"
    assert policy["scope"] == "selected_c_while_accumulate_v0_expected_samples_only"
    assert policy["maxEffectiveIterationCount"] == MAX_EFFECTIVE_ITERATIONS
    assert len(policy["requiredAcceptedSurface"]) == 4
    assert len(policy["requiredRejectedSurface"]) == 5
    assert policy["policyAppliedToRuntime"] is False
    assert policy["runtimeExecutionPerformed"] is False


def test_fef_p92_sample_policy_rows_make_all_p91_samples_eligible_for_future_gate():
    payload = build_payload()
    rows = payload["samplePolicyRows"]
    assert len(rows) == 7
    assert all(row["policyEligibleForFutureExecution"] is True for row in rows)
    assert all(row["runtimeExecutionPerformed"] is False for row in rows)
    assert all(row["boundednessPolicyAppliedToRuntime"] is False for row in rows)
    for row in rows:
        validate_policy_row(row)
        assert row["effectiveIterationCount"] == effective_iteration_count(row["inputN"])
        assert row["effectiveIterationCount"] <= MAX_EFFECTIVE_ITERATIONS


def test_fef_p92_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["loop_boundedness_policy"] == "recorded_execution_blocked"
    assert gates["loop_policy_sample_eligibility"] == "recorded"
    assert gates["loop_runtime_execution"] == "not_performed"
    assert gates["loop_reference_runtime_gate"] == "blocked_until_next_phase"
    assert gates["loop_backedge_support"] == "blocked"
    assert gates["p89_private_reviewer_hold"] == "preserved"
    assert "Loop fixtures were executed." in payload["blockedStatements"]
    assert summary["loopExecutionAllowedClaim"] is False
    assert summary["loopRuntimeExecutionClaim"] is False
    assert summary["loopReferenceRuntimeClaim"] is False
    assert summary["loopLoweringClaim"] is False
    assert summary["loopBoundednessPolicyClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p92_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P92")


def test_fef_p92_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p92_loop_boundedness_policy.py",
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
    assert "FEF_P92_LOOP_BOUNDEDNESS_POLICY_OK" in proc.stdout
