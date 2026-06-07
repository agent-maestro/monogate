"""Tests for ATLAS-A6 private reference-value candidate selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a6_private_reference_value_candidate_selector import (
    CLAIM_FLAGS,
    CRITERIA,
    RECIPROCAL_ENTRY_ID,
    ROOT,
    SELECTED_OPTION_ID,
    SQRT_ENTRY_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def score_by_id(payload, entry_id: str):
    return next(item for item in payload["referenceValueScores"] if item["entryId"] == entry_id)


def test_atlas_a6_consumes_a5_and_creates_reference_value_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A6_PRIVATE_REFERENCE_VALUE_CANDIDATE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a5-private-reciprocal-boundary-feasibility-packet"
    assert summary["sourceStatus"] == "ATLAS_A5_PRIVATE_RECIPROCAL_BOUNDARY_FEASIBILITY_PACKET_PASS"
    assert summary["sourceReviewedEntryId"] == RECIPROCAL_ENTRY_ID
    assert summary["referenceValueSelectorCreated"] is True


def test_atlas_a6_records_practical_reference_criteria():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert payload["referenceCriteria"] == CRITERIA
    assert summary["criteriaCount"] == 5
    assert set(CRITERIA) == {
        "shape_diversity",
        "guard_clarity",
        "future_leverage",
        "proof_effort_value_ratio",
        "public_witness_potential",
    }
    assert summary["practicalReferenceCriteriaRecorded"] is True


def test_atlas_a6_defers_reciprocal_and_selects_sqrt_reference_review():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    reciprocal = score_by_id(payload, RECIPROCAL_ENTRY_ID)
    sqrt_entry = score_by_id(payload, SQRT_ENTRY_ID)
    assert summary["reciprocalTotalScore"] == 17
    assert summary["sqrtTotalScore"] == 21
    assert sqrt_entry["totalScore"] > reciprocal["totalScore"]
    assert reciprocal["referenceValueStatus"] == "feasible_but_deferred_lower_shape_diversity"
    assert sqrt_entry["referenceValueStatus"] == "recommended_for_reference_feasibility_review"
    assert summary["reciprocalPromotionDeferred"] is True
    assert summary["sqrtReferenceReviewRecommended"] is True
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedEntryId"] == SQRT_ENTRY_ID
    assert summary["nextRecommendedArtifact"] == "ATLAS-A7 private sqrt boundary reference-feasibility packet"


def test_atlas_a6_options_do_not_create_candidate_or_feasibility_packet():
    payload = build_payload(ATLAS_GATE)
    options = {item["optionId"]: item for item in payload["options"]}
    summary = payload["summary"]
    assert options["promote_reciprocal_to_candidate_packet"]["selectionStatus"] == "deferred_lower_reference_value"
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert options["pause_gap_candidates_pending_atlas_v0_doc"]["selectionStatus"] == (
        "available_if_human_prefers_consolidation"
    )
    assert summary["reciprocalCandidatePacketSelected"] is False
    assert summary["sqrtCandidatePacketSelected"] is False
    assert summary["feasibilityPacketCreated"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["proofAttemptStarted"] is False


def test_atlas_a6_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a6_blocks_public_product_runtime_reviewer_and_validity_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "reciprocal_candidate_packet_selected",
        "sqrt_candidate_packet_selected",
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


def test_atlas_a6_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A6 Private Reference-Value Candidate Selector")
    assert "## Reference-Value Scores" in report


def test_atlas_a6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a6_private_reference_value_candidate_selector.py",
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
    assert "ATLAS_A6_PRIVATE_REFERENCE_VALUE_CANDIDATE_SELECTOR_OK" in proc.stdout
