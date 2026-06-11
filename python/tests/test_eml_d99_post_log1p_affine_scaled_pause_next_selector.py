"""Tests for EML-D99 post log1p affine-scaled pause next selector."""

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

from scripts.eml_d99_post_log1p_affine_scaled_pause_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d99_consumes_d98_and_selects_consolidation_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D99_POST_LOG1P_AFFINE_SCALED_PAUSE_NEXT_SELECTOR_PASS"
    assert payload["sourceFreezePacket"] == "eml-d98-log1p-affine-scaled-branch-pause-freeze-packet"
    assert summary["selectedOptionId"] == "bounded_artifact_target_set_consolidation_review"
    assert summary["selectedNextArtifact"] == "EML-D100 bounded artifact target-set consolidation review"
    assert summary["nextActionSelected"] is True
    assert summary["consolidationReviewSelected"] is True


def test_d99_preserves_d98_affine_log1p_freeze_boundary():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["branchPauseStarted"] is True
    assert summary["checkedWitnessCopyFrozen"] is True
    assert summary["privateFreezePacket"] is True
    assert summary["duplicateShiftedBlocksPreserved"] is True
    assert summary["frozenWitnessName"] == "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness"
    assert summary["frozenCheckedStatement"] == "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"
    assert summary["frozenGuardCount"] == 1
    assert summary["frozenGuards"] == ["0 < 1 + a * x"]
    assert summary["frozenCaveatCount"] == 10
    assert summary["frozenBlockedPhraseCount"] == 16
    assert summary["sourceNegativeControlCount"] == 5
    assert summary["sourceBlockerCount"] == 5


def test_d99_preserves_d96_copy_counts_and_runtime_boundary():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceD96RequiredCaveatCount"] == 10
    assert summary["sourceD96BlockedGlobalPhraseCount"] == 14
    assert summary["sourceD96RowRequiredCaveatCount"] == 7
    assert summary["sourceD96RowBlockedPhraseCount"] == 13
    assert summary["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert summary["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert summary["guardBoundaryStatus"] == "affine_scaled_positive_domain_boundary_required"
    assert summary["publicAtlasStatus"] == "held_private"


def test_d99_options_keep_later_paths_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 5
    assert option_by_id(payload, "bounded_artifact_target_set_consolidation_review")["selectionStatus"] == "selected_next"
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == (
        "candidate_later_after_consolidation_review"
    )
    assert option_by_id(payload, "private_reviewer_response_intake")["selectionStatus"] == (
        "candidate_later_requires_real_response"
    )
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == (
        "candidate_later_after_consolidation_review"
    )
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_human_approval"
    )
    assert payload["selectedOption"]["optionId"] == "bounded_artifact_target_set_consolidation_review"


def test_d99_keeps_public_reviewer_branch_proof_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["nextBoundedIdentityBranchSelected"] is False
    assert summary["boundedTrigFeasibilitySelected"] is False
    assert summary["privateReviewerResponseIntakeSelected"] is False
    assert summary["humanPublicCopyGateSelected"] is False
    assert summary["humanApprovalRecorded"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["reviewerRejectionRecorded"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicPromotionPerformed"] is False
    assert summary["publicEducationPromotionPerformed"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["advantageLabCaseAdded"] is False
    assert summary["implementationStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["candidateProved"] is False
    assert summary["candidateProvedThisPhase"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["protectedLogReplacementClaim"] is False
    assert summary["protectedLog1pReplacementClaim"] is False
    assert summary["electronicsRepoTouched"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False


def test_d99_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in ["next_action_selected", "consolidation_review_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "consolidation_review_selected"}:
            assert value is False


def test_d99_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D99")


def test_d99_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d99_post_log1p_affine_scaled_pause_next_selector.py",
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
    assert "EML_D99_POST_LOG1P_AFFINE_SCALED_PAUSE_NEXT_SELECTOR_OK" in proc.stdout
