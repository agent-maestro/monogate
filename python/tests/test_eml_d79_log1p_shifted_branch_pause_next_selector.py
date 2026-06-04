"""Tests for EML-D79 log1p-shifted branch pause next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d79_log1p_shifted_branch_pause_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d79_consumes_d78_copy_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D79_LOG1P_SHIFTED_BRANCH_PAUSE_NEXT_SELECTOR_PASS"
    assert payload["sourceReview"] == "eml-d78-log1p-shifted-checked-witness-copy-review-packet"
    assert payload["summary"]["sourceSelectedOptionId"] == "log1p_shifted_checked_witness_copy_review_packet"
    assert payload["summary"]["d78CopyReviewStarted"] is True
    assert payload["summary"]["d78PrivateCopyReviewOnly"] is True
    assert payload["summary"]["d78CheckedWitnessCopyReviewOnly"] is True


def test_d79_preserves_log1p_shifted_copy_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.log1p_shifted_boundary_coordinate_witness"
    assert payload["summary"]["sourceSelectedCandidateId"] == "log1p_shifted_boundary_coordinate"
    assert payload["summary"]["sourceSelectedFamily"] == "guarded_log1p_shifted_coordinate"
    assert payload["summary"]["checkedStatement"] == "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"


def test_d79_selects_log1p_shifted_pause_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "log1p_shifted_branch_pause_freeze_packet")
    assert payload["decision"] == "select_log1p_shifted_branch_pause_freeze_packet"
    assert payload["summary"]["selectedOptionId"] == "log1p_shifted_branch_pause_freeze_packet"
    assert payload["summary"]["selectedNextArtifact"] == (
        "EML-D80 log1p-shifted branch pause and checked-witness copy freeze packet"
    )
    assert payload["summary"]["nextActionSelected"] is True
    assert payload["summary"]["branchPauseFreezeSelected"] is True
    assert payload["summary"]["checkedWitnessCopyFreezePlanned"] is True
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_pause_freeze_lane"


def test_d79_parks_future_branch_trig_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == "candidate_later_requires_human_approval"
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d79_preserves_d78_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert payload["summary"]["d76SurfaceRowCount"] == 5
    assert payload["summary"]["d78WitnessRowCount"] == 1
    assert payload["summary"]["d78RequiredCaveatCount"] == 9
    assert payload["summary"]["d78BlockedGlobalPhraseCount"] == 12
    assert payload["summary"]["d78RowRequiredCaveatCount"] == 6
    assert payload["summary"]["d78RowBlockedPhraseCount"] == 10


def test_d79_starts_no_pause_public_copy_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["pauseStarted"] is False
    assert payload["summary"]["freezePacketStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
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


def test_d79_keeps_runtime_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d79_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in ["next_action_selected", "branch_pause_freeze_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "branch_pause_freeze_selected"}:
            assert value is False
    for option in payload["decisionOptions"]:
        for key, value in option["claimFlags"].items():
            if key not in {"next_action_selected", "branch_pause_freeze_selected"}:
                assert value is False


def test_d79_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D79")


def test_d79_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d79_log1p_shifted_branch_pause_next_selector.py",
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
    assert "EML_D79_LOG1P_SHIFTED_BRANCH_PAUSE_NEXT_SELECTOR_OK" in proc.stdout
