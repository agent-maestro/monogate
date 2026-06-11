"""Tests for EML-D89 log1m-shifted branch pause freeze packet."""

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

from scripts.eml_d89_log1m_shifted_branch_pause_freeze_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def parked_by_id(payload, option_id: str):
    return next(item for item in payload["parkedOptions"] if item["optionId"] == option_id)


def test_d89_consumes_d88_selected_pause_freeze_option():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D89_LOG1M_SHIFTED_BRANCH_PAUSE_FREEZE_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d88-log1m-shifted-post-copy-review-next-selector"
    assert payload["summary"]["selectedOptionId"] == "log1m_shifted_branch_pause_freeze_packet"


def test_d89_freezes_log1m_shifted_checked_witness_copy():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["branchPauseStarted"] is True
    assert payload["summary"]["checkedWitnessCopyFrozen"] is True
    assert payload["summary"]["privateFreezePacket"] is True
    assert row["freezeStatus"] == "private_checked_witness_copy_frozen"
    assert row["machlibName"] == "MachLib.Real.log1m_shifted_boundary_coordinate_witness"
    assert row["checkedStatement"] == "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x"
    assert row["guards"] == ["0 < 1 - x"]


def test_d89_preserves_log1m_shifted_guard_duplicate_block_and_boundary_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceSelectedCandidateId"] == "log1m_shifted_boundary_coordinate"
    assert payload["summary"]["sourceSelectedFamily"] == "guarded_log1m_shifted_coordinate"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert payload["summary"]["d85SurfaceRowCount"] == 5
    assert payload["summary"]["guardBoundaryStatus"] == "shifted_positive_domain_boundary_required"
    assert payload["summary"]["duplicateLog1pBlockPreserved"] is True


def test_d89_preserves_d87_caveats_blockers_and_runtime_control():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["frozenCaveatCount"] == 10
    assert payload["summary"]["frozenBlockedPhraseCount"] == 13
    assert payload["summary"]["sourceD87RequiredCaveatCount"] == 10
    assert payload["summary"]["sourceD87BlockedGlobalPhraseCount"] == 13
    assert payload["summary"]["sourceD87RowRequiredCaveatCount"] == 7
    assert payload["summary"]["sourceD87RowBlockedPhraseCount"] == 12
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert row["runtimeControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert "shifted positive-domain guard" in " ".join(row["frozenCaveats"])
    assert "duplicate-log1p block" in " ".join(row["frozenCaveats"])
    assert "log1p replacement" in row["frozenBlockedPhrases"]


def test_d89_parks_future_branches_reviewer_intake_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert parked_by_id(payload, "next_bounded_identity_branch_selector")["status"] == "parked_after_log1m_shifted_pause"
    assert parked_by_id(payload, "private_reviewer_response_intake")["status"] == "parked_requires_actual_reviewer_response"
    assert parked_by_id(payload, "bounded_trig_identity_feasibility_selector")["status"] == "parked_after_log1m_shifted_pause"
    assert parked_by_id(payload, "human_approved_public_copy_gate")["status"] == "parked_requires_explicit_human_approval"
    assert payload["summary"]["parkedNextBoundedIdentityBranchSelector"] is True
    assert payload["summary"]["parkedPrivateReviewerResponseIntake"] is True
    assert payload["summary"]["parkedBoundedTrigFeasibility"] is True
    assert payload["summary"]["parkedHumanApprovedPublicCopyGate"] is True
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["privateReviewerResponseIntakeSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanApprovedPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d89_starts_no_public_copy_reviewer_decision_or_implementation():
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


def test_d89_keeps_runtime_log_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d89_claim_flags_are_freeze_only_with_duplicate_block():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "branch_pause_started",
        "checked_witness_copy_frozen",
        "private_freeze_packet",
        "duplicate_log1p_block_preserved",
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


def test_d89_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D89")


def test_d89_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d89_log1m_shifted_branch_pause_freeze_packet.py",
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
    assert "EML_D89_LOG1M_SHIFTED_BRANCH_PAUSE_FREEZE_PACKET_OK" in proc.stdout
