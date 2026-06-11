"""Tests for FEF-P89 compound-condition private reviewer handoff hold gate."""

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

from scripts.fef_p89_compound_condition_private_reviewer_handoff_hold_gate import (
    CLAIM_FLAGS,
    build_bundle_evidence,
    build_outputs,
    build_payload,
    build_reviewer_handoff_packet,
    validate_payload,
)


def test_fef_p89_records_private_handoff_without_reviewer_decision():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P89_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"
    assert payload["decision"] == "private_reviewer_handoff_ready_response_not_recorded_implementation_held"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["reviewerHandoffReady"] is True
    assert summary["reviewerDecisionRecorded"] is False
    assert payload["reviewerHandoffPacket"]["reviewerDecisionStatus"] == "not_recorded"


def test_fef_p89_bundle_evidence_spans_p47_p88():
    evidence = build_bundle_evidence()
    phases = [row["phase"] for row in evidence]
    assert phases[0] == "P47-P48"
    assert "P59-P61" in phases
    assert "P83-P85" in phases
    assert "P88" in phases
    assert phases[-1] == "P89"
    assert len(evidence) == 11


def test_fef_p89_holds_implementation_pending_reviewer():
    payload = build_payload()
    handoff = build_reviewer_handoff_packet()
    assert handoff["implementationStatus"] == "held_pending_reviewer_response"
    assert "approve_separate_implementation_phase" in handoff["allowedReviewerOutcomes"]
    summary = payload["summary"]
    assert summary["implementationHeldPendingReview"] is True
    assert summary["implementationChangeApproved"] is False
    assert summary["implementationChangeApplied"] is False
    assert summary["implementationDiffProduced"] is False


def test_fef_p89_release_gates_block_implementation_and_public_claims():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["private_reviewer_handoff"] == "ready"
    assert gates["private_reviewer_decision"] == "not_recorded"
    assert gates["implementation_change_approval"] == "blocked_pending_reviewer"
    assert gates["implementation_diff"] == "not_produced"
    assert gates["actual_reingest_execution"] == "blocked_not_performed"
    assert gates["compound_condition_support"] == "blocked"
    assert gates["compiler_correctness"] == "blocked"


def test_fef_p89_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert "A reviewer has approved the P88 proposal." in payload["blockedStatements"]
    assert "A reviewer has rejected the P88 proposal." in payload["blockedStatements"]
    assert summary["actualReingestExecutionPerformed"] is False
    assert summary["sourcePrimitiveInstalled"] is False
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["publicReady"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p89_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P89")


def test_fef_p89_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p89_compound_condition_private_reviewer_handoff_hold_gate.py",
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
    assert "FEF_P89_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK" in proc.stdout
