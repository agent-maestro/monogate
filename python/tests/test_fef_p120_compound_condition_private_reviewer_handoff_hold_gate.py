"""Tests for FEF-P120 compound-condition private reviewer handoff hold gate."""

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

from scripts.fef_p120_compound_condition_private_reviewer_handoff_hold_gate import (
    CLAIM_FLAGS,
    build_bundle_evidence,
    build_outputs,
    build_payload,
    build_reviewer_handoff_packet,
    validate_payload,
)


def test_fef_p120_records_private_reviewer_handoff_without_decision():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P120_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"
    assert payload["decision"] == "compound_condition_private_reviewer_handoff_ready_response_not_recorded_implementation_held"
    assert summary["selectedFixtureId"] == "c_and_guard_return_v0"
    assert summary["bundleRange"] == "P113-P119"
    assert summary["reviewerHandoffReady"] is True
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["reviewerDecisionStatus"] == "not_recorded"


def test_fef_p120_bundle_evidence_covers_p113_through_p119():
    bundle = build_bundle_evidence()
    assert [item["phase"] for item in bundle] == ["P113", "P114", "P115", "P116", "P117", "P118", "P119"]
    assert len(bundle) == 7
    assert all(item["decision"] for item in bundle)
    assert all(item["reviewFocus"] for item in bundle)


def test_fef_p120_handoff_packet_holds_p119_proposal():
    payload = build_payload()
    handoff = payload["reviewerHandoffPacket"]
    assert handoff["handoffStatus"] == "ready_for_private_review"
    assert handoff["reviewerDecisionStatus"] == "not_recorded"
    assert handoff["implementationStatus"] == "held_pending_reviewer_response"
    assert handoff["heldProposalId"] == "selected_and_guard_return_lowering_codegen_proposal_v0"
    assert len(handoff["allowedPrivateOutcomes"]) == 6
    assert len(handoff["reviewerMustInspect"]) == 7


def test_fef_p120_handoff_helper_uses_p119_proposal_identity():
    p119_payload = {
        "loweringCodegenProposal": {
            "proposalId": "selected_and_guard_return_lowering_codegen_proposal_v0",
            "status": "proposal_recorded_not_applied",
        }
    }
    handoff = build_reviewer_handoff_packet(p119_payload)
    assert handoff["heldProposalId"] == "selected_and_guard_return_lowering_codegen_proposal_v0"
    assert handoff["heldProposalStatus"] == "proposal_recorded_not_applied"


def test_fef_p120_blocks_implementation_execution_lowering_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["implementationApproved"] is False
    assert summary["implementationApplied"] is False
    assert summary["implementationDiffProduced"] is False
    assert summary["generatedFixtureTextProduced"] is False
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionCodegenPolicyImplemented"] is False
    assert summary["compoundConditionReingestPolicyImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p120_release_gates_hold_implementation():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["compound_condition_private_reviewer_handoff"] == "ready"
    assert gates["reviewer_decision"] == "not_recorded"
    assert gates["implementation_change"] == "held"
    assert gates["generated_fixture_text"] == "not_produced"
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert "A reviewer has approved the P119 compound-condition lowering/codegen proposal." in payload["blockedStatements"]


def test_fef_p120_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P120")


def test_fef_p120_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p120_compound_condition_private_reviewer_handoff_hold_gate.py",
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
    assert "FEF_P120_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK" in proc.stdout
