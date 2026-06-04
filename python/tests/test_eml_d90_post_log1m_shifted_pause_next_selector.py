"""Tests for EML-D90 post log1m-shifted pause next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d90_post_log1m_shifted_pause_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d90_consumes_d89_and_selects_next_bounded_identity_branch():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D90_POST_LOG1M_SHIFTED_PAUSE_NEXT_SELECTOR_PASS"
    assert payload["sourceFreezePacket"] == "eml-d89-log1m-shifted-branch-pause-freeze-packet"
    assert summary["selectedOptionId"] == "next_bounded_identity_branch_selector"
    assert summary["selectedNextArtifact"] == "EML-D91 bounded identity branch candidate selector"
    assert summary["nextActionSelected"] is True
    assert summary["nextBoundedIdentityBranchSelected"] is True


def test_d90_observes_act_a16_private_handoff_without_acceptance():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert payload["sourceActHandoff"] == "act-a16-reviewer-promotion-hold-final-handoff"
    assert summary["actHandoffChainRange"] == "ACT-A13-A15"
    assert summary["actHandoffReady"] is True
    assert summary["actPrivateHandoffObserved"] is True
    assert summary["actReviewerDecisionRecorded"] is False
    assert summary["actPromotionAllowed"] is False
    assert summary["actPublicReady"] is False


def test_d90_preserves_d89_log1m_shifted_freeze_boundary():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["branchPauseStarted"] is True
    assert summary["checkedWitnessCopyFrozen"] is True
    assert summary["privateFreezePacket"] is True
    assert summary["duplicateLog1pBlockPreserved"] is True
    assert summary["frozenWitnessName"] == "MachLib.Real.log1m_shifted_boundary_coordinate_witness"
    assert summary["frozenCheckedStatement"] == "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x"
    assert summary["frozenGuardCount"] == 1
    assert summary["frozenGuards"] == ["0 < 1 - x"]
    assert summary["frozenCaveatCount"] == 10
    assert summary["frozenBlockedPhraseCount"] == 13
    assert summary["sourceNegativeControlCount"] == 4
    assert summary["sourceBlockerCount"] == 4


def test_d90_options_keep_later_paths_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == "selected_next"
    assert option_by_id(payload, "private_reviewer_response_intake")["selectionStatus"] == (
        "candidate_later_requires_real_response"
    )
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_human_approval"
    )
    assert payload["selectedOption"]["optionId"] == "next_bounded_identity_branch_selector"


def test_d90_keeps_public_reviewer_proof_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
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


def test_d90_runtime_guard_public_hold_and_duplicate_block_preserved():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert summary["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert summary["guardBoundaryStatus"] == "shifted_positive_domain_boundary_required"
    assert summary["publicAtlasStatus"] == "held_private"
    assert summary["duplicateLog1pBlockPreserved"] is True


def test_d90_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in ["next_action_selected", "next_bounded_identity_branch_selected", "act_private_handoff_observed"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "next_bounded_identity_branch_selected", "act_private_handoff_observed"}:
            assert value is False


def test_d90_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D90")


def test_d90_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d90_post_log1m_shifted_pause_next_selector.py",
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
    assert "EML_D90_POST_LOG1M_SHIFTED_PAUSE_NEXT_SELECTOR_OK" in proc.stdout
