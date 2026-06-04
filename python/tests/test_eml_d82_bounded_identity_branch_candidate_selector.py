"""Tests for EML-D82 bounded identity branch candidate selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d82_bounded_identity_branch_candidate_selector import (
    CLAIM_FLAGS,
    ROOT,
    SELECTED_CANDIDATE_ID,
    SELECTED_NEXT_ARTIFACT,
    SELECTED_STATEMENT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def candidate_by_id(payload, candidate_id: str):
    return next(item for item in payload["candidateRows"] if item["candidateId"] == candidate_id)


def test_d82_consumes_d81_bounded_identity_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D82_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"
    assert payload["sourceSelector"] == "eml-d81-post-log1p-shifted-pause-next-selector"
    assert summary["sourceSelectedOptionId"] == "next_bounded_identity_branch_selector"
    assert summary["sourceSelectedNextArtifact"] == "EML-D82 bounded identity branch candidate selector"
    assert summary["sourceD81SelectorObserved"] is True


def test_d82_preserves_d80_log1p_freeze_boundary():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceD80FrozenWitnessName"] == "MachLib.Real.log1p_shifted_boundary_coordinate_witness"
    assert summary["sourceD80FrozenCheckedStatement"] == "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x"
    assert summary["sourceD80FrozenGuards"] == ["0 < 1 + x"]
    assert summary["sourceRuntimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert summary["sourceRuntimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert summary["sourcePublicAtlasStatus"] == "held_private"


def test_d82_observes_act_handoff_without_acceptance():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceActHandoffChainRange"] == "ACT-A13-A15"
    assert summary["sourceActHandoffReady"] is True
    assert summary["sourceActReviewerDecisionRecorded"] is False
    assert summary["sourceActPromotionAllowed"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["reviewerRejectionRecorded"] is False


def test_d82_selects_fresh_log1m_shifted_candidate():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    selected = payload["selectedCandidate"]
    assert summary["selectedCandidateId"] == SELECTED_CANDIDATE_ID
    assert selected["candidateId"] == SELECTED_CANDIDATE_ID
    assert summary["selectedFamily"] == "guarded_log1m_shifted_coordinate"
    assert summary["selectedNextArtifact"] == SELECTED_NEXT_ARTIFACT
    assert summary["selectedProposedStatement"] == SELECTED_STATEMENT
    assert summary["selectedGuardCount"] == 1
    assert summary["selectedGuards"] == ["0 < 1 - x"]
    assert summary["boundedIdentityCandidateSelected"] is True
    assert summary["log1mShiftedBoundaryCandidateSelected"] is True


def test_d82_blocks_duplicate_log1p_candidate():
    payload = build_payload(ATLAS_GATE)
    duplicate = candidate_by_id(payload, "log1p_shifted_boundary_coordinate")
    assert duplicate["selectionStatus"] == "blocked_duplicate_checked_witness"
    assert duplicate["duplicateCheckedWitnesses"] == ["MachLib.Real.log1p_shifted_boundary_coordinate_witness"]
    assert duplicate["freshRelativeToCheckedWitnesses"] is False
    assert payload["summary"]["blockedDuplicateCandidateId"] == "log1p_shifted_boundary_coordinate"
    assert payload["summary"]["blockedDuplicateStatus"] == "blocked_duplicate_checked_witness"
    assert payload["summary"]["log1pShiftedDuplicateReselected"] is False


def test_d82_records_candidates_and_parks_later_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["candidateCount"] == 4
    assert candidate_by_id(payload, SELECTED_CANDIDATE_ID)["selectionStatus"] == "selected_next_feasibility_packet"
    assert candidate_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert candidate_by_id(payload, "private_reviewer_response_intake")["selectionStatus"] == (
        "candidate_later_requires_real_response"
    )


def test_d82_keeps_selected_candidate_non_duplicate_and_runtime_controlled():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    selected = payload["selectedCandidate"]
    assert summary["selectedDuplicateCheckedWitnessCount"] == 0
    assert summary["selectedFreshRelativeToCheckedWitnesses"] is True
    assert summary["freshCandidateNonDuplicateSelected"] is True
    assert selected["duplicateCheckedWitnesses"] == []
    assert selected["runtimeControl"] == "protected_log_and_log1p_remain_runtime_controls"


def test_d82_starts_no_feasibility_proof_runtime_public_or_laptop_work():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["feasibilityPacketStarted"] is False
    assert summary["boundedTrigFeasibilitySelected"] is False
    assert summary["privateReviewerResponseIntakeSelected"] is False
    assert summary["humanPublicCopyGateSelected"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicPromotionPerformed"] is False
    assert summary["publicEducationPromotionPerformed"] is False
    assert summary["publicSurfaceUpdated"] is False
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


def test_d82_claim_flags_are_candidate_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsCandidateSelectorOnly"] is True
    true_keys = {
        "bounded_identity_candidate_selected",
        "log1m_shifted_boundary_candidate_selected",
        "fresh_candidate_non_duplicate_selected",
        "source_d81_selector_observed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_d82_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D82")


def test_d82_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d82_bounded_identity_branch_candidate_selector.py",
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
    assert "EML_D82_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK" in proc.stdout
