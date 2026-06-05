"""Tests for EML-D98 log1p affine-scaled branch pause freeze packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d98_log1p_affine_scaled_branch_pause_freeze_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def parked_by_id(payload, option_id: str):
    return next(item for item in payload["parkedOptions"] if item["optionId"] == option_id)


def test_d98_consumes_d97_selected_pause_freeze_option():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D98_LOG1P_AFFINE_SCALED_BRANCH_PAUSE_FREEZE_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d97-log1p-affine-scaled-post-copy-review-next-selector"
    assert payload["summary"]["selectedOptionId"] == "log1p_affine_scaled_branch_pause_freeze_packet"


def test_d98_freezes_log1p_affine_scaled_checked_witness_copy():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["branchPauseStarted"] is True
    assert payload["summary"]["checkedWitnessCopyFrozen"] is True
    assert payload["summary"]["privateFreezePacket"] is True
    assert row["freezeStatus"] == "private_checked_witness_copy_frozen"
    assert row["machlibName"] == "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness"
    assert row["checkedStatement"] == "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"
    assert row["guards"] == ["0 < 1 + a * x"]


def test_d98_preserves_affine_guard_duplicate_blocks_and_boundary_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceSelectedCandidateId"] == "log1p_affine_scaled_boundary_coordinate"
    assert payload["summary"]["sourceSelectedFamily"] == "guarded_log1p_affine_scaled_coordinate"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["sourceNegativeControlCount"] == 5
    assert payload["summary"]["sourceBlockerCount"] == 5
    assert payload["summary"]["d94SurfaceRowCount"] == 5
    assert payload["summary"]["guardBoundaryStatus"] == "affine_scaled_positive_domain_boundary_required"
    assert payload["summary"]["duplicateShiftedBlocksPreserved"] is True


def test_d98_preserves_d96_caveats_blockers_and_runtime_control():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["frozenCaveatCount"] == 10
    assert payload["summary"]["frozenBlockedPhraseCount"] == 16
    assert payload["summary"]["sourceD96RequiredCaveatCount"] == 10
    assert payload["summary"]["sourceD96BlockedGlobalPhraseCount"] == 14
    assert payload["summary"]["sourceD96RowRequiredCaveatCount"] == 7
    assert payload["summary"]["sourceD96RowBlockedPhraseCount"] == 13
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert row["runtimeControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert "affine positive-domain guard" in " ".join(row["frozenCaveats"])
    assert "duplicate shifted-coordinate blocks" in " ".join(row["frozenCaveats"])
    assert "log1p replacement" in row["frozenBlockedPhrases"]


def test_d98_parks_future_selectors_reviewer_intake_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert parked_by_id(payload, "post_log1p_affine_scaled_pause_next_selector")["status"] == (
        "parked_after_log1p_affine_scaled_pause"
    )
    assert parked_by_id(payload, "next_bounded_identity_branch_selector")["status"] == (
        "parked_after_log1p_affine_scaled_pause"
    )
    assert parked_by_id(payload, "private_reviewer_response_intake")["status"] == (
        "parked_requires_actual_reviewer_response"
    )
    assert parked_by_id(payload, "bounded_trig_identity_feasibility_selector")["status"] == (
        "parked_after_log1p_affine_scaled_pause"
    )
    assert parked_by_id(payload, "human_approved_public_copy_gate")["status"] == (
        "parked_requires_explicit_human_approval"
    )
    assert payload["summary"]["parkedPostPauseNextSelector"] is True
    assert payload["summary"]["parkedNextBoundedIdentityBranchSelector"] is True
    assert payload["summary"]["parkedPrivateReviewerResponseIntake"] is True
    assert payload["summary"]["parkedBoundedTrigFeasibility"] is True
    assert payload["summary"]["parkedHumanApprovedPublicCopyGate"] is True
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["privateReviewerResponseIntakeSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanApprovedPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d98_starts_no_public_copy_reviewer_decision_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["reviewerDecisionRecorded"] is False
    assert payload["summary"]["reviewerApprovalRecorded"] is False
    assert payload["summary"]["reviewerRejectionRecorded"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["freezeRows"][0]["publicPromotionAllowed"] is False


def test_d98_keeps_runtime_log_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d98_claim_flags_are_freeze_only_with_duplicate_blocks():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "branch_pause_started",
        "checked_witness_copy_frozen",
        "private_freeze_packet",
        "duplicate_shifted_blocks_preserved",
    }
    assert payload["summary"]["claimFlagsFrozenOnly"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False
    for row in payload["freezeRows"]:
        for key, value in row["claimFlags"].items():
            if key not in allowed_true:
                assert value is False


def test_d98_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D98")


def test_d98_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d98_log1p_affine_scaled_branch_pause_freeze_packet.py",
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
    assert "EML_D98_LOG1P_AFFINE_SCALED_BRANCH_PAUSE_FREEZE_PACKET_OK" in proc.stdout
