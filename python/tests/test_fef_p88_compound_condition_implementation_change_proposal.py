"""Tests for FEF-P88 compound-condition implementation-change proposal."""

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

from scripts.fef_p88_compound_condition_implementation_change_proposal import (
    CLAIM_FLAGS,
    build_change_proposal,
    build_outputs,
    build_payload,
    build_review_checks,
    read_json,
    validate_payload,
    P87_RESULT,
)


def test_fef_p88_records_proposal_without_applying_it():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P88_COMPOUND_CONDITION_IMPLEMENTATION_CHANGE_PROPOSAL_PASS"
    assert payload["decision"] == "selected_guarded_div_implementation_change_proposal_recorded_not_applied"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["proposalStatus"] == "proposal_recorded_not_applied"
    assert summary["implementationChangeProposalRecorded"] is True
    assert summary["proposalApplied"] is False
    assert summary["implementationDiffProduced"] is False
    assert summary["actualReingestExecutionPerformed"] is False


def test_fef_p88_proposal_has_scoped_change_items_gates_and_rollback():
    p87_payload = read_json(P87_RESULT)
    proposal = build_change_proposal(p87_payload)
    assert proposal["proposalId"] == "selected_guarded_div_adapter_installation_change_proposal_v0"
    assert proposal["scope"] == "selected_c_and_short_circuit_guard_v0_only"
    assert [change["changeId"] for change in proposal["proposedChangeSet"]] == [
        "install_selected_nonzero01_mapping",
        "install_selected_guarded_div_mapping",
        "add_selected_non_evaluation_assertions",
    ]
    assert len(proposal["requiredApprovalGates"]) == 5
    assert len(proposal["rollbackCriteria"]) == 5
    assert proposal["proposalApplied"] is False


def test_fef_p88_review_checks_pass_from_p87_boundary():
    p87_payload = read_json(P87_RESULT)
    checks = build_review_checks(build_change_proposal(p87_payload), p87_payload)
    assert len(checks) == 9
    assert all(check["passed"] is True for check in checks)
    assert {check["status"] for check in checks} == {"pass"}


def test_fef_p88_release_gates_require_review_and_separate_implementation():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["implementation_change_proposal"] == "recorded_not_applied"
    assert gates["private_reviewer_approval"] == "required_not_recorded"
    assert gates["implementation_diff"] == "not_produced"
    assert gates["actual_reingest_execution"] == "blocked_not_performed"


def test_fef_p88_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert "The implementation change has been applied." in payload["blockedStatements"]
    assert summary["implementationChangeApplied"] is False
    assert summary["sourcePrimitiveInstalled"] is False
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p88_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P88")


def test_fef_p88_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p88_compound_condition_implementation_change_proposal.py",
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
    assert "FEF_P88_COMPOUND_CONDITION_IMPLEMENTATION_CHANGE_PROPOSAL_OK" in proc.stdout
