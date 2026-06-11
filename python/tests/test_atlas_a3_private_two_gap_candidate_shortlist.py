"""Tests for ATLAS-A3 private two-gap candidate shortlist."""

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

from scripts.atlas_a3_private_two_gap_candidate_shortlist import (
    CLAIM_FLAGS,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def entry_by_id(payload, entry_id: str):
    return next(item for item in payload["shortlistEntries"] if item["entryId"] == entry_id)


def test_atlas_a3_consumes_a2_and_creates_private_shortlist():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A3_PRIVATE_TWO_GAP_CANDIDATE_SHORTLIST_PASS"
    assert payload["sourceArtifact"] == "atlas-a2-private-gap-review-pause-selector"
    assert summary["sourceStatus"] == "ATLAS_A2_PRIVATE_GAP_REVIEW_PAUSE_SELECTOR_PASS"
    assert summary["sourceSelectedOptionId"] == "prepare_two_gap_candidate_shortlist"
    assert summary["privateShortlistCreated"] is True
    assert summary["nextRecommendedArtifact"] == "ATLAS-A4 private two-gap feasibility selector"


def test_atlas_a3_preserves_target_gap_and_source_slots():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["gapSlotCount"] == 2
    assert len(payload["sourceGapSlots"]) == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a3_records_exactly_two_materially_distinct_entries():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    entries = payload["shortlistEntries"]
    assert summary["shortlistEntryCount"] == 2
    assert summary["twoGapEntriesRecorded"] is True
    assert {entry["entryId"] for entry in entries} == {
        "reciprocal_positive_boundary_candidate",
        "sqrt_square_nonnegative_roundtrip_candidate",
    }
    reciprocal = entry_by_id(payload, "reciprocal_positive_boundary_candidate")
    sqrt_entry = entry_by_id(payload, "sqrt_square_nonnegative_roundtrip_candidate")
    assert reciprocal["familyHint"] == "reciprocal_boundary"
    assert reciprocal["guardHint"] == "0 < x"
    assert sqrt_entry["familyHint"] == "sqrt_boundary"
    assert sqrt_entry["guardHint"] == "0 <= x"
    assert "non-log and non-subtraction family" in reciprocal["whyMateriallyDistinct"]
    assert "non-log and non-subtraction family" in sqrt_entry["whyMateriallyDistinct"]


def test_atlas_a3_entries_are_not_checked_or_selected_for_proof():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["shortlistEntriesAreCheckedWitnesses"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["newIdentityCandidateSelected"] is False
    assert summary["nextBoundedIdentityBranchSelected"] is False
    assert summary["feasibilityPacketCreated"] is False
    assert summary["proofAttemptStarted"] is False
    for entry in payload["shortlistEntries"]:
        assert entry["status"] == "private_shortlist_entry_not_checked_not_selected_for_proof"
        assert "not a checked witness" in entry["blockedClaims"]
        assert "not selected as a proof branch" in entry["blockedClaims"]
        assert "no candidate validity claim" in entry["blockedClaims"]


def test_atlas_a3_blocks_public_product_runtime_reviewer_and_lower_bound_claims():
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


def test_atlas_a3_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A3 Private Two-Gap Candidate Shortlist")
    assert "## Shortlist Entries" in report


def test_atlas_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a3_private_two_gap_candidate_shortlist.py",
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
    assert "ATLAS_A3_PRIVATE_TWO_GAP_CANDIDATE_SHORTLIST_OK" in proc.stdout
