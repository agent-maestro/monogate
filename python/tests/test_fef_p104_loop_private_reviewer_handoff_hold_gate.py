"""Tests for FEF-P104 loop private reviewer handoff hold gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p104_loop_private_reviewer_handoff_hold_gate import (
    CLAIM_FLAGS,
    build_bundle_evidence,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p104_records_private_handoff_without_decision():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P104_LOOP_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"
    assert payload["decision"] == "loop_private_reviewer_handoff_ready_response_not_recorded_implementation_held"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["reviewerHandoffReady"] is True
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["implementationHeldPendingReview"] is True


def test_fef_p104_bundle_evidence_covers_loop_ladder():
    payload = build_payload()
    phases = [item["phase"] for item in payload["bundleEvidence"]]
    assert phases == ["P90-P92", "P93-P94", "P95-P98", "P99-P100", "P101-P102", "P103"]
    assert build_bundle_evidence() == payload["bundleEvidence"]
    assert payload["reviewerHandoffPacket"]["bundleRange"] == "P90-P103"
    assert len(payload["reviewerHandoffPacket"]["reviewerQuestions"]) == 5
    assert len(payload["reviewerHandoffPacket"]["allowedReviewerOutcomes"]) == 5


def test_fef_p104_checklist_keeps_human_decision_pending():
    payload = build_payload()
    checklist = {item["id"]: item for item in payload["handoffChecklist"]}
    assert checklist["send_p90_p103_bundle"]["status"] == "ready"
    assert checklist["inspect_p103_candidate"]["status"] == "ready"
    assert checklist["collect_reviewer_decision"]["status"] == "pending_human"
    assert checklist["keep_implementation_held"]["status"] == "required"
    assert checklist["preserve_claim_boundary"]["status"] == "required"


def test_fef_p104_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["private_reviewer_handoff"] == "ready"
    assert gates["private_reviewer_decision"] == "not_recorded"
    assert gates["implementation_change_approval"] == "blocked_pending_reviewer"
    assert gates["actual_reingest_execution"] == "blocked_not_performed"
    assert gates["loop_backedge_support"] == "blocked"
    assert "A reviewer has approved the P103 candidate." in payload["blockedStatements"]
    assert summary["implementationChangeApproved"] is False
    assert summary["implementationChangeApplied"] is False
    assert summary["actualReingestExecutionPerformed"] is False
    assert summary["loopHelperAdapterInstalled"] is False
    assert summary["loopReingestSupported"] is False
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p104_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P104")


def test_fef_p104_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p104_loop_private_reviewer_handoff_hold_gate.py",
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
    assert "FEF_P104_LOOP_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK" in proc.stdout
