"""Tests for ATLAS-A8 private sqrt boundary candidate value selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a8_private_sqrt_candidate_value_selector import (
    CLAIM_FLAGS,
    ROOT,
    SELECTED_OPTION_ID,
    SOURCE_ENTRY_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a8_consumes_a7_and_selects_abs_normalized_candidate_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A8_PRIVATE_SQRT_CANDIDATE_VALUE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a7-private-sqrt-boundary-reference-feasibility-packet"
    assert summary["sourceReviewedEntryId"] == SOURCE_ENTRY_ID
    assert summary["sourceAbsNormalizationCaveatRecorded"] is True
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedCandidateShape"] == "abs_normalized_then_guarded"
    assert summary["nextRecommendedArtifact"] == "ATLAS-A9 private abs-normalized sqrt boundary candidate packet"


def test_atlas_a8_recommends_packet_but_creates_no_candidate_or_validity_claim():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["candidateValueSelectorCreated"] is True
    assert summary["sqrtReferenceValueReviewed"] is True
    assert summary["absNormalizedShapeSelected"] is True
    assert summary["candidatePacketRecommended"] is True
    assert summary["candidatePacketCreated"] is False
    assert summary["sqrtCandidatePacketSelected"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["proofAttemptStarted"] is False


def test_atlas_a8_rejects_simple_guarded_shape_for_now_and_keeps_pause_available():
    payload = build_payload(ATLAS_GATE)
    options = {item["optionId"]: item for item in payload["options"]}
    assert options["create_abs_normalized_sqrt_candidate_packet"]["selectionStatus"] == "selected_next"
    assert options["create_simple_guarded_sqrt_candidate_packet"]["selectionStatus"] == (
        "rejected_for_now_due_abs_caveat"
    )
    assert options["pause_for_atlas_v0_reference_document"]["selectionStatus"] == (
        "available_if_human_prefers_consolidation"
    )
    assert options["park_sqrt_entry"]["selectionStatus"] == "not_selected"


def test_atlas_a8_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a8_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "candidate_packet_created",
        "sqrt_candidate_packet_selected",
        "simple_guarded_shape_selected",
        "atlas_v0_doc_pause_selected",
        "sqrt_entry_parked",
        "shortlist_entries_are_checked_witnesses",
        "candidate_validity_claim",
        "new_identity_candidate_selected",
        "next_bounded_identity_branch_selected",
        "proof_attempt_started",
        "candidate_proved",
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


def test_atlas_a8_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A8 Private Sqrt Boundary Candidate Value Selector")
    assert "## Options" in report


def test_atlas_a8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a8_private_sqrt_candidate_value_selector.py",
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
    assert "ATLAS_A8_PRIVATE_SQRT_CANDIDATE_VALUE_SELECTOR_OK" in proc.stdout
