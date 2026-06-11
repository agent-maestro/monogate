"""Tests for FEF-P112 side-effect private reviewer handoff hold gate."""

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

from scripts.fef_p112_side_effect_private_reviewer_handoff_hold_gate import (
    CLAIM_FLAGS,
    build_bundle_evidence,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p112_records_reviewer_handoff_hold():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P112_SIDE_EFFECT_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"
    assert payload["decision"] == "side_effect_private_reviewer_handoff_ready_response_not_recorded_implementation_held"
    assert summary["selectedFixtureId"] == "c_global_state_update_v0"
    assert summary["reviewerHandoffReady"] is True
    assert summary["reviewerDecisionStatus"] == "not_recorded"
    assert summary["implementationHeldPendingReview"] is True


def test_fef_p112_bundle_evidence_covers_p105_p111_in_order():
    payload = build_payload()
    phases = [item["phase"] for item in payload["bundleEvidence"]]
    assert phases == ["P105", "P106", "P107", "P108", "P109", "P110", "P111"]
    assert build_bundle_evidence() == payload["bundleEvidence"]
    assert payload["reviewerHandoffPacket"]["bundleRange"] == "P105-P111"
    assert payload["summary"]["bundleEvidenceEntryCount"] == 7


def test_fef_p112_handoff_checklist_and_allowed_outcomes_are_complete():
    payload = build_payload()
    checklist = [item["id"] for item in payload["handoffChecklist"]]
    assert checklist == [
        "p105_fixture_inventory_reviewed",
        "p106_expected_samples_reviewed",
        "p107_policy_gate_reviewed",
        "p108_reference_runtime_reviewed",
        "p109_original_c_stubbed_runtime_reviewed",
        "p110_generated_target_blocker_reviewed",
        "p111_proposal_and_rollback_gates_reviewed",
    ]
    assert len(payload["reviewerHandoffPacket"]["allowedPrivateOutcomes"]) == 6
    assert "request_generated_fixture_text_before_approval" in payload["reviewerHandoffPacket"]["allowedPrivateOutcomes"]
    assert "request_stronger_alias_external_call_policy" in payload["reviewerHandoffPacket"]["allowedPrivateOutcomes"]


def test_fef_p112_holds_proposal_without_diff_generated_text_or_execution():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["proposalId"] == "selected_global_state_update_lowering_codegen_proposal_v0"
    assert summary["proposalStatus"] == "proposal_recorded_not_applied"
    assert summary["proposalHeld"] is True
    assert summary["implementationApproved"] is False
    assert summary["implementationApplied"] is False
    assert summary["implementationDiffProduced"] is False
    assert summary["generatedFixtureTextProduced"] is False
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["p111ReviewCheckCount"] == 12
    assert summary["p111ReviewCheckPassCount"] == 12
    assert summary["p111ReviewCheckFailCount"] == 0


def test_fef_p112_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["side_effect_private_reviewer_handoff"] == "ready"
    assert gates["reviewer_decision"] == "not_recorded"
    assert gates["implementation_change"] == "held"
    assert gates["implementation_diff"] == "not_produced"
    assert gates["generated_fixture_text"] == "not_produced"
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert gates["side_effect_reingest_execution"] == "not_performed"
    assert gates["side_effect_lowering"] == "blocked"
    assert gates["compiler_correctness"] == "blocked"
    assert "A reviewer has approved the P111 side-effect lowering/codegen proposal." in payload["blockedStatements"]
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["sideEffectCodegenPolicyImplemented"] is False
    assert summary["sideEffectReingestPolicyImplemented"] is False
    assert summary["sideEffectMemorySupportClaim"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p112_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P112")


def test_fef_p112_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p112_side_effect_private_reviewer_handoff_hold_gate.py",
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
    assert "FEF_P112_SIDE_EFFECT_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK" in proc.stdout
