"""Tests for ATLAS-A2 private Atlas gap review or pause selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a2_private_gap_review_pause_selector import (
    CLAIM_FLAGS,
    ROOT,
    SELECTED_OPTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a2_consumes_a1_and_selects_two_gap_shortlist():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A2_PRIVATE_GAP_REVIEW_PAUSE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a1-private-checked-witness-table"
    assert summary["sourceStatus"] == "ATLAS_A1_PRIVATE_CHECKED_WITNESS_TABLE_PASS"
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedNextArtifact"] == "ATLAS-A3 private two-gap candidate shortlist"
    assert payload["selectedOption"]["selectionStatus"] == "selected_next"


def test_atlas_a2_records_target_gap_from_a1():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["familyCount"] == len(payload["familyCounts"])
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["remainingSlotsBeforeUpperBound"] == 12
    assert summary["targetGapRecorded"] is True
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a2_lists_exactly_two_gap_slots_without_candidates():
    payload = build_payload(ATLAS_GATE)
    slots = payload["gapSlots"]
    assert len(slots) == 2
    assert payload["summary"]["twoGapSlotsRequired"] is True
    assert {slot["slotId"] for slot in slots} == {
        "gap_slot_1_non_log_non_subtraction_boundary",
        "gap_slot_2_runtime_control_contrast_boundary",
    }
    assert all(slot["status"] == "slot_required_not_candidate_selected" for slot in slots)
    assert all("no candidate identity selected" in slot["blockedClaims"] for slot in slots[:1])
    assert payload["summary"]["candidateShortlistCreated"] is False
    assert payload["summary"]["newIdentityCandidateSelected"] is False


def test_atlas_a2_options_keep_pause_and_wait_available_but_not_selected():
    payload = build_payload(ATLAS_GATE)
    options = {item["optionId"]: item for item in payload["options"]}
    assert options["prepare_two_gap_candidate_shortlist"]["selectionStatus"] == "selected_next"
    assert options["pause_on_private_atlas_table"]["selectionStatus"] == "available_if_human_prefers_review"
    assert options["wait_for_reviewer_product_or_electronics_input"]["selectionStatus"] == (
        "available_if_external_signal_arrives"
    )
    assert payload["summary"]["pauseSelected"] is False
    assert payload["summary"]["externalInputWaitSelected"] is False


def test_atlas_a2_blocks_public_product_proof_runtime_and_reviewer_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "candidate_shortlist_created",
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
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["reviewerResponseConsumed"] is False


def test_atlas_a2_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A2 Private Atlas Gap Review Or Pause Selector")
    assert "## Gap Slots" in report


def test_atlas_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a2_private_gap_review_pause_selector.py",
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
    assert "ATLAS_A2_PRIVATE_GAP_REVIEW_PAUSE_SELECTOR_OK" in proc.stdout
