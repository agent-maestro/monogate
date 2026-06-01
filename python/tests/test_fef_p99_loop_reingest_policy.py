"""Tests for FEF-P99 loop re-ingest policy."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p99_loop_reingest_policy import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    policy_validation_rows,
    selected_policy,
    validate_payload,
    validate_policy,
    validate_row,
)


def test_fef_p99_records_selected_loop_reingest_policy_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P99_LOOP_REINGEST_POLICY_PASS"
    assert payload["decision"] == "selected_loop_reingest_policy_recorded_execution_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["policyStatus"] == "policy_recorded_execution_blocked"
    assert summary["policyScope"] == "selected_generated_c_loop_fixture_only"
    assert summary["reingestPolicyRecorded"] is True
    assert summary["reingestExecuted"] is False


def test_fef_p99_policy_accepts_only_selected_generated_loop_surface():
    payload = build_payload()
    policy = payload["reingestPolicy"]
    validate_policy(policy)
    accepted_ids = [item["surfaceId"] for item in policy["requiredAcceptedSurface"]]
    rejected_ids = [item["surfaceId"] for item in policy["requiredRejectedSurface"]]
    assert accepted_ids == [
        "static_helper_loop_effective_iterations",
        "selected_generated_loop_function",
        "selected_effective_iteration_binding",
        "selected_closed_form_loop_return",
    ]
    assert rejected_ids == [
        "arbitrary_while_loop",
        "arbitrary_for_loop",
        "side_effect_loop_body",
        "unbounded_or_data_dependent_backedge",
        "helper_runtime_import",
    ]


def test_fef_p99_policy_validation_rows_match_codegen_tokens():
    payload = build_payload()
    rows = payload["policyValidationRows"]
    assert len(rows) == 9
    for row in rows:
        validate_row(row)
        assert row["reingestExecuted"] is False
    assert payload["summary"]["policyValidationPassCount"] == 9
    assert payload["summary"]["policyValidationFailCount"] == 0


def test_fef_p99_required_comparison_rows_are_pending_reingest():
    payload = build_payload()
    comparisons = payload["reingestPolicy"]["requiredComparisonRows"]
    assert len(comparisons) == 7
    assert all(row["comparisonStatus"] == "pending_reingest_execution" for row in comparisons)
    assert all(row["reingestExecuted"] is False for row in comparisons)
    assert [row["sampleId"] for row in comparisons] == [f"sample_0{i}" for i in range(7)]
    assert [row["effectiveIterationCount"] for row in comparisons] == [0, 1, 3, 4, 5, 0, 8]


def test_fef_p99_policy_builder_is_deterministic_from_p98_payload():
    payload = build_payload()
    policy = selected_policy({"summary": payload["summary"], "runtimeComparison": {"rows": payload["reingestPolicy"]["requiredComparisonRows"]}})
    rows = policy_validation_rows(payload["reingestPolicy"], payload)
    assert policy["selectedFixtureId"] == "c_while_accumulate_v0"
    assert len(rows) == 9


def test_fef_p99_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_loop_reingest_policy"] == "recorded_execution_blocked"
    assert gates["selected_loop_reingest_execution"] == "not_performed"
    assert gates["loop_backedge_support"] == "blocked"
    assert "Re-ingested loop code was executed." in payload["blockedStatements"]
    assert summary["loopReingestSupported"] is False
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["loopBackedgeSemanticsImplemented"] is False
    assert summary["selectedCodegenFixtureInstalled"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p99_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P99")


def test_fef_p99_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p99_loop_reingest_policy.py",
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
    assert "FEF_P99_LOOP_REINGEST_POLICY_OK" in proc.stdout
