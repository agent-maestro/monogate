"""Tests for FEF-P128 source-preserving private reviewer handoff hold gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p128_source_preserving_private_reviewer_handoff_hold_gate import (
    CLAIM_FLAGS,
    build_bundle_evidence,
    build_outputs,
    build_payload,
    build_reviewer_handoff_packet,
    validate_payload,
)


def test_fef_p128_records_private_reviewer_handoff_without_decision():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P128_SOURCE_PRESERVING_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"
    assert payload["decision"] == "source_preserving_private_reviewer_handoff_ready_response_not_recorded_implementation_held"
    assert summary["bundleRange"] == "P121-P127"
    assert summary["reviewerHandoffReady"] is True
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["reviewerDecisionStatus"] == "not_recorded"


def test_fef_p128_bundle_evidence_covers_p121_through_p127():
    bundle = build_bundle_evidence()
    assert [item["phase"] for item in bundle] == ["P121", "P122", "P123", "P124", "P125", "P126", "P127"]
    assert len(bundle) == 7
    assert all(item["decision"] for item in bundle)
    assert all(item["reviewFocus"] for item in bundle)


def test_fef_p128_handoff_packet_defines_pivot_criteria():
    handoff = build_reviewer_handoff_packet()
    assert handoff["handoffStatus"] == "ready_for_private_review"
    assert handoff["reviewerDecisionStatus"] == "not_recorded"
    assert handoff["implementationStatus"] == "held_pending_reviewer_response"
    assert handoff["bundleRange"] == "P121-P127"
    assert len(handoff["allowedPrivateOutcomes"]) == 7
    assert len(handoff["reviewerMustInspect"]) == 7
    assert len(handoff["pivotCriteria"]) == 4
    assert "A real reviewer response is recorded before any implementation posture changes." in handoff["pivotCriteria"]


def test_fef_p128_summary_records_source_preserving_totals():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["sourcePreservingFixtureCount"] == 4
    assert summary["checkerFixtureCount"] == 4
    assert summary["totalExpectedRowsAcrossCheckerFixtures"] == 30
    assert summary["totalCheckerPassesAcrossCheckerFixtures"] == 30
    assert summary["totalNegativeControlsAcrossCheckerFixtures"] == 13
    assert summary["totalExpectedFailedRowsAcrossNegativeControls"] == 37
    assert summary["p127CheckerPassCount"] == 8
    assert summary["p127NegativeControlExpectedFailureCount"] == 9


def test_fef_p128_blocks_parser_reemitter_oracle_fidelity_support_and_release():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["implementationApproved"] is False
    assert summary["implementationApplied"] is False
    assert summary["implementationDiffProduced"] is False
    assert summary["sourceParserExecuted"] is False
    assert summary["sourceReemitterExecuted"] is False
    assert summary["preservationOracleExecuted"] is False
    assert summary["sourceFidelityValidated"] is False
    assert summary["runtimeExecutionPerformed"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["sourcePreservingRoundtripSupportClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["publicReady"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p128_release_gates_hold_pivot_point():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["source_preserving_private_reviewer_handoff"] == "ready"
    assert gates["reviewer_decision"] == "not_recorded"
    assert gates["implementation_change"] == "held"
    assert gates["source_parser_execution"] == "not_performed"
    assert gates["source_reemitter_execution"] == "not_performed"
    assert gates["preservation_oracle_execution"] == "not_run"
    assert gates["source_fidelity_validation"] == "not_performed"
    assert gates["source_preserving_roundtrip_support"] == "blocked"
    assert "A reviewer has approved source-preserving roundtrip implementation." in payload["blockedStatements"]


def test_fef_p128_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P128")


def test_fef_p128_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p128_source_preserving_private_reviewer_handoff_hold_gate.py",
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
    assert "FEF_P128_SOURCE_PRESERVING_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK" in proc.stdout
