"""Tests for FEF-P103 loop helper adapter installation candidate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p103_loop_helper_adapter_installation_candidate import (
    CLAIM_FLAGS,
    build_installation_candidate,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p103_records_candidate_without_applying_it():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P103_LOOP_HELPER_ADAPTER_INSTALLATION_CANDIDATE_PASS"
    assert payload["decision"] == "selected_loop_helper_adapter_installation_candidate_recorded_not_applied"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["installationCandidateRecorded"] is True
    assert summary["candidateApplied"] is False
    assert summary["implementationDiffProduced"] is False
    assert summary["loopHelperAdapterInstalled"] is False


def test_fef_p103_candidate_has_scoped_hooks_and_gates():
    payload = build_payload()
    candidate = payload["installationCandidate"]
    assert candidate["scope"] == "selected_c_while_accumulate_v0_generated_c_fixture_only"
    assert candidate["status"] == "candidate_recorded_not_applied"
    assert [hook["hookId"] for hook in candidate["intendedPipelineHooks"]] == [
        "match_selected_loop_effective_iteration_helper_definition",
        "inline_selected_loop_effective_iteration_call",
        "preserve_selected_p92_boundedness_contract",
    ]
    assert len(candidate["requiredApprovalGates"]) == 5
    assert len(candidate["rollbackCriteria"]) == 5
    assert candidate["installedInEfrog"] is False
    assert candidate["installedInForge"] is False


def test_fef_p103_review_checks_bind_to_p102_prerequisites():
    payload = build_payload()
    summary = payload["summary"]
    checks = {check["checkId"]: check for check in payload["reviewChecks"]}
    assert summary["p102RowCount"] == 7
    assert summary["p102PassCount"] == 7
    assert summary["p102FailCount"] == 0
    assert summary["p102MaxAbsError"] == 0.0
    assert summary["p101ReingestParseSucceeded"] is True
    assert summary["p101PreviousBlockerCleared"] is True
    assert summary["reviewCheckCount"] == 11
    assert summary["reviewCheckFailCount"] == 0
    assert checks["p102_all_rows_pass"]["passed"] is True
    assert checks["candidate_not_applied"]["passed"] is True


def test_fef_p103_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_loop_helper_adapter_installation_candidate"] == "recorded_not_applied"
    assert gates["implementation_diff"] == "not_produced"
    assert gates["actual_reingest_execution"] == "blocked_not_performed"
    assert gates["loop_backedge_support"] == "blocked"
    assert "The selected loop helper adapter has been installed." in payload["blockedStatements"]
    assert summary["actualReingestExecutionPerformed"] is False
    assert summary["loopReingestSupported"] is False
    assert summary["compilerBehaviorChanged"] is False
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p103_candidate_builder_uses_selected_fixture_id():
    p102_payload = build_payload()
    candidate = build_installation_candidate(p102_payload)
    assert candidate["candidateId"] == "selected_loop_helper_inline_adapter_installation_candidate_v0"
    assert candidate["sourceAdapterId"] == "c_while_accumulate_v0_helper_inline_adapter"


def test_fef_p103_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P103")


def test_fef_p103_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p103_loop_helper_adapter_installation_candidate.py",
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
    assert "FEF_P103_LOOP_HELPER_ADAPTER_INSTALLATION_CANDIDATE_OK" in proc.stdout
