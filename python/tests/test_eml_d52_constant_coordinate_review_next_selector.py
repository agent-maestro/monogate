"""Tests for EML-D52 constant-coordinate review next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d52_constant_coordinate_review_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d52_consumes_d51_copy_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D52_CONSTANT_COORDINATE_REVIEW_NEXT_SELECTOR_PASS"
    assert payload["sourceReview"] == "eml-d51-constant-coordinate-delta-copy-review-packet"
    assert payload["summary"]["d51CopyReviewStarted"] is True
    assert payload["summary"]["d51PrivateCopyReviewOnly"] is True
    assert payload["summary"]["d51DeltaCopyReviewOnly"] is True


def test_d52_preserves_constant_coordinate_copy_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert payload["summary"]["sourceSelectedCandidateId"] == "zero_coordinate_exp_two_boundary"
    assert payload["summary"]["sourceSelectedFamily"] == "constant_coordinate_refresh"
    assert payload["summary"]["sourceProposedStatement"] == "eml 0 (exp 2) = -1"
    assert payload["summary"]["checkedLeanStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["localSpellingUsesOnePlusOne"] is True
    assert payload["summary"]["duplicatesExistingConstantWitness"] is False
    assert payload["summary"]["guardCount"] == 0


def test_d52_selects_constant_coordinate_pause_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "constant_coordinate_branch_pause_freeze_packet")
    assert payload["decision"] == "select_constant_coordinate_branch_pause_freeze_packet"
    assert payload["summary"]["selectedOptionId"] == "constant_coordinate_branch_pause_freeze_packet"
    assert payload["summary"]["selectedNextArtifact"] == (
        "EML-D53 constant-coordinate branch pause and checked-witness delta freeze packet"
    )
    assert payload["summary"]["pauseFreezeSelected"] is True
    assert payload["summary"]["checkedWitnessDeltaFreezePlanned"] is True
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_pause_freeze_lane"


def test_d52_parks_future_branch_trig_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == "candidate_later_requires_human_approval"
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d52_preserves_d51_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["d51WitnessRowCount"] == 1
    assert payload["summary"]["d51RequiredCaveatCount"] == 8
    assert payload["summary"]["d51BlockedGlobalPhraseCount"] == 10


def test_d52_starts_no_pause_public_copy_or_implementation():
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
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d52_keeps_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicHoldPreserved"] is True
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_and_arithmetic_remain_runtime_controls"
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d52_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in ["next_action_selected", "pause_freeze_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "pause_freeze_selected"}:
            assert value is False
    for option in payload["decisionOptions"]:
        for key, value in option["claimFlags"].items():
            if key not in {"next_action_selected", "pause_freeze_selected"}:
                assert value is False


def test_d52_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D52")


def test_d52_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d52_constant_coordinate_review_next_selector.py",
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
    assert "EML_D52_CONSTANT_COORDINATE_REVIEW_NEXT_SELECTOR_OK" in proc.stdout
