"""Tests for FEF-P58 branch gap private-review addendum."""

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

from scripts.fef_p58_branch_gap_private_review_addendum import (
    CLAIM_FLAGS,
    GAP_ROWS,
    SOURCE_PACKETS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p58_links_private_review_and_branch_closure_sources():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P58_BRANCH_GAP_PRIVATE_REVIEW_ADDENDUM_PASS"
    assert payload["decision"] == "private_review_addendum_ready_general_branch_gap_blocked"
    assert set(payload["sourcePackets"]) == set(SOURCE_PACKETS)
    assert summary["sourcePacketCount"] == 6
    assert summary["allSourcePacketsValidationPass"] is True
    assert summary["allSourcePacketClaimFlagsFalse"] is True
    assert summary["privateReviewBundleReady"] is True
    assert summary["privateReviewerIntakeReady"] is True
    assert summary["reviewerDecisionRecorded"] is False


def test_fef_p58_preserves_selected_evidence_totals():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["nonGeneratedSemanticSourceCaseCount"] == 5
    assert summary["nonGeneratedSemanticSourceSampleCount"] == 23
    assert summary["sourceDerivedReingestPacketCount"] == 10
    assert summary["sourceDerivedReingestSampleCount"] == 46
    assert summary["selectedBranchCaseCount"] == 5
    assert summary["selectedBranchClosureCount"] == 5
    assert summary["selectedBranchReingestPacketCount"] == 10
    assert summary["selectedBranchPacketSampleComparisons"] == 58
    assert summary["p51SelectedBlockedCount"] == 0


def test_fef_p58_gap_rows_are_explicit_and_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gaps = {row["id"]: row for row in payload["gapRows"]}
    assert summary["gapCount"] == len(GAP_ROWS) == 6
    assert summary["blockedGapCount"] == 6
    assert set(gaps) == {row["id"] for row in GAP_ROWS}
    assert gaps["grammar_surface_breadth"]["status"] == "blocked"
    assert gaps["control_flow_normalization"]["nextValidator"] == "control_flow_ir_inventory"
    assert gaps["source_roundtrip_semantics"]["nextValidator"] == "non_generated_branch_roundtrip_gate"
    assert gaps["release_readiness_surface"]["nextValidator"] == "private_reviewer_response_packet"
    for row in payload["gapRows"]:
        assert row["status"] == "blocked"
        assert row["missingEvidence"]
        assert row["nextValidator"]


def test_fef_p58_statement_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["private_reviewer_addendum"] == "ready"
    assert gates["selected_branch_closure_matrix"] == "pass"
    assert gates["general_branch_control_flow_support"] == "blocked"
    assert "P47-P58 are ready to send as a private-review packet set." in (
        payload["allowedPrivateReviewerStatements"]
    )
    assert "General C/Rust branch/control-flow support is established." in payload["blockedStatements"]
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert summary["fullCRustRoundtripClaim"] is False
    assert summary["arbitrarySourceFamilyClaim"] is False
    assert summary["packagePublished"] is False
    assert summary["checkoutEnabled"] is False
    assert summary["publicReady"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p58_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P58")


def test_fef_p58_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p58_branch_gap_private_review_addendum.py",
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
    assert "FEF_P58_BRANCH_GAP_PRIVATE_REVIEW_ADDENDUM_OK" in proc.stdout
