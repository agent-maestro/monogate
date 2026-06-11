"""Tests for ATLAS-A4 private two-gap feasibility selector."""

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

from scripts.atlas_a4_private_two_gap_feasibility_selector import (
    CLAIM_FLAGS,
    PARKED_ENTRY_ID,
    ROOT,
    SELECTED_ENTRY_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a4_consumes_a3_and_recommends_reciprocal_feasibility_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A4_PRIVATE_TWO_GAP_FEASIBILITY_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a3-private-two-gap-candidate-shortlist"
    assert summary["sourceStatus"] == "ATLAS_A3_PRIVATE_TWO_GAP_CANDIDATE_SHORTLIST_PASS"
    assert summary["selectedEntryId"] == SELECTED_ENTRY_ID
    assert summary["nextRecommendedArtifact"] == "ATLAS-A5 private reciprocal boundary feasibility packet"
    assert payload["selectedDecision"]["selectionStatus"] == "recommended_for_next_feasibility_packet"


def test_atlas_a4_parks_sqrt_without_rejection_or_disproof():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    parked = payload["parkedDecision"]
    assert summary["parkedEntryId"] == PARKED_ENTRY_ID
    assert summary["sqrtEntryParked"] is True
    assert parked["selectionStatus"] == "parked_for_later_feasibility_review"
    assert "not rejected" in parked["blockers"]
    assert "not disproved" in parked["blockers"]


def test_atlas_a4_preserves_target_gap_and_shortlist_count():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["shortlistEntryCount"] == 2
    assert len(payload["shortlistEntries"]) == 2
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a4_recommends_one_packet_but_creates_none():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["privateFeasibilitySelectorCreated"] is True
    assert summary["shortlistEntriesReviewed"] is True
    assert summary["oneFeasibilityPacketRecommended"] is True
    assert summary["feasibilityPacketCreated"] is False
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["newIdentityCandidateSelected"] is False
    assert summary["nextBoundedIdentityBranchSelected"] is False
    assert summary["proofAttemptStarted"] is False


def test_atlas_a4_blocks_public_product_runtime_reviewer_and_validity_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "feasibility_packet_created",
        "shortlist_entries_are_checked_witnesses",
        "candidate_validity_claim",
        "new_identity_candidate_selected",
        "next_bounded_identity_branch_selected",
        "proof_attempt_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "runtime_lowering_changed",
        "public_atlas_promotion",
        "public_copy_approved",
        "public_surface_updated",
        "sdk_compiler_docs_created",
        "course_material_created",
        "claim_topology_ui_created",
        "product_implementation_started",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "catalog_completeness_claim",
        "target_lower_bound_reached_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["reviewerResponseConsumed"] is False


def test_atlas_a4_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# ATLAS-A4 Private Two-Gap Feasibility Selector")
    assert "## Feasibility Decisions" in report


def test_atlas_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a4_private_two_gap_feasibility_selector.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
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
    assert "ATLAS_A4_PRIVATE_TWO_GAP_FEASIBILITY_SELECTOR_OK" in proc.stdout
