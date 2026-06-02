"""Tests for EML-D32 subtraction-family pause freeze packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d32_subtraction_family_pause_freeze_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def action_by_id(payload, action_id: str):
    return next(item for item in payload["availableAfterFreeze"] if item["actionId"] == action_id)


def test_d32_consumes_d31_and_d30():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D32_SUBTRACTION_FAMILY_PAUSE_FREEZE_PACKET_PASS"
    assert payload["sourceDecision"] == "eml-d31-checked-witness-review-next-decision"
    assert payload["sourceReview"] == "eml-d30-checked-witness-copy-review-packet"
    assert payload["summary"]["selectedOptionId"] == "pause_subtraction_family_deepening"


def test_d32_pauses_family_deepening_and_freezes_index():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "pause_subtraction_family_deepening_and_freeze_checked_witness_index"
    assert payload["summary"]["familyDeepeningPauseSelected"] is True
    assert payload["summary"]["checkedWitnessIndexFreezePlanned"] is True
    assert payload["summary"]["familyDeepeningPaused"] is True
    assert payload["summary"]["checkedWitnessIndexFrozen"] is True
    assert payload["summary"]["freezeScopeRowCount"] == 4


def test_d32_freezes_six_checked_witnesses():
    payload = build_payload(ATLAS_GATE)
    witness_ids = {row["witnessId"] for row in payload["frozenWitnessRows"]}
    assert payload["summary"]["frozenWitnessCount"] == 6
    assert "constants_zero_one_e_boundary" in witness_ids
    assert "ln_from_eml_boundary" in witness_ids
    assert "subtraction_boundary_affine_offset" in witness_ids
    assert "subtraction_boundary_two_stage_chain" in witness_ids
    assert "subtraction_boundary_affine_nested_chain" in witness_ids
    assert "subtraction_boundary_three_stage_chain" in witness_ids
    assert all(row["freezeStatus"] == "frozen_for_private_handoff" for row in payload["frozenWitnessRows"])


def test_d32_preserves_d30_caveats_and_blockers():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["d30RequiredCaveatCount"] == 5
    assert payload["summary"]["d30BlockedGlobalPhraseCount"] == 8
    assert len(payload["preservedRequiredCaveats"]) == 5
    assert len(payload["preservedBlockedGlobalPhrases"]) == 8
    assert "theorem discovery" in payload["preservedBlockedGlobalPhrases"]
    assert "broad nested subtraction family" in payload["preservedBlockedGlobalPhrases"]


def test_d32_records_available_after_freeze_paths():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["availableActionCount"] == 3
    public_gate = action_by_id(payload, "human_approved_public_copy_gate")
    new_branch = action_by_id(payload, "new_bounded_identity_branch_selector")
    course_ref = action_by_id(payload, "course_scaling_private_reference")
    assert public_gate["availability"] == "available_only_with_explicit_human_approval"
    assert new_branch["availability"] == "available_after_pause_packet"
    assert course_ref["availability"] == "available_as_private_reference_only"


def test_d32_starts_no_public_copy_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["copyReviewStartedInD32"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["publicReady"] is False


def test_d32_keeps_broad_family_and_runtime_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["newBoundedBranchStarted"] is False
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["arbitraryDepthClaim"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["advantageLabCaseAdded"] is False


def test_d32_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["frozenWitnessRows"]:
        assert row["publicPromotionAllowed"] is False
        assert all(value is False for value in row["claimFlags"].values())


def test_d32_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D32")


def test_d32_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d32_subtraction_family_pause_freeze_packet.py",
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
    assert "EML_D32_SUBTRACTION_FAMILY_PAUSE_FREEZE_PACKET_OK" in proc.stdout
