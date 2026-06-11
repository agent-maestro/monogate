"""Tests for ATLAS-A5 private reciprocal boundary feasibility packet."""

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

from scripts.atlas_a5_private_reciprocal_boundary_feasibility_packet import (
    CLAIM_FLAGS,
    ROOT,
    SOURCE_ENTRY_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a5_consumes_a4_and_reviews_reciprocal_entry():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A5_PRIVATE_RECIPROCAL_BOUNDARY_FEASIBILITY_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a4-private-two-gap-feasibility-selector"
    assert summary["sourceStatus"] == "ATLAS_A4_PRIVATE_TWO_GAP_FEASIBILITY_SELECTOR_PASS"
    assert summary["sourceSelectedEntryId"] == SOURCE_ENTRY_ID
    assert summary["reviewedEntryId"] == SOURCE_ENTRY_ID
    assert summary["sourceParkedEntryId"] == "sqrt_square_nonnegative_roundtrip_candidate"


def test_atlas_a5_records_guard_statement_caveats_and_next_selector():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    review = payload["feasibilityReview"]
    assert summary["guardHint"] == "0 < x"
    assert summary["statementShapeHint"] == "0 < x -> eml (x * (1 / x)) 1 = 1"
    assert review["guardReview"]["requiredGuard"] == "0 < x"
    assert review["statementShapeReview"]["candidateStatementHint"] == (
        "0 < x -> eml (x * (1 / x)) 1 = 1"
    )
    assert len(review["reviewCaveats"]) == 3
    assert summary["nextRecommendedArtifact"] == "ATLAS-A6 private reciprocal boundary candidate selector"


def test_atlas_a5_marks_feasible_for_selector_not_validity_or_proof():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    review = payload["feasibilityReview"]
    assert summary["feasibilityPacketCreated"] is True
    assert summary["feasibleForCandidateSelectorRecorded"] is True
    assert review["feasibilityStatus"] == "feasible_for_later_private_candidate_selector_not_validity_claim"
    assert summary["candidateValidityClaim"] is False
    assert summary["newIdentityCandidateSelected"] is False
    assert summary["nextBoundedIdentityBranchSelected"] is False
    assert summary["proofAttemptStarted"] is False
    assert "not a candidate validity claim" in review["blockedClaims"]
    assert "no Lean typecheck" in review["blockedClaims"]


def test_atlas_a5_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a5_blocks_public_product_runtime_reviewer_and_validity_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
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


def test_atlas_a5_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A5 Private Reciprocal Boundary Feasibility Packet")
    assert "## Review Caveats" in report
    assert "## Blocked Claims" in report


def test_atlas_a5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a5_private_reciprocal_boundary_feasibility_packet.py",
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
    assert "ATLAS_A5_PRIVATE_RECIPROCAL_BOUNDARY_FEASIBILITY_PACKET_OK" in proc.stdout
