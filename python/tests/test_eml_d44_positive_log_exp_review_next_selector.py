"""Tests for EML-D44 positive log-exp review next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d44_positive_log_exp_review_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d44_consumes_d43_delta_copy_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D44_POSITIVE_LOG_EXP_REVIEW_NEXT_SELECTOR_PASS"
    assert payload["sourceReview"] == "eml-d43-positive-log-exp-delta-copy-review-packet"
    assert payload["summary"]["d43CopyReviewStarted"] is True
    assert payload["summary"]["d43PrivateCopyReviewOnly"] is True
    assert payload["summary"]["d43DeltaCopyReviewOnly"] is True


def test_d44_selects_branch_pause_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "select_positive_log_exp_branch_pause_freeze_packet"
    assert payload["summary"]["selectedOptionId"] == "positive_log_exp_branch_pause_freeze_packet"
    assert payload["summary"]["selectedNextArtifact"] == (
        "EML-D45 positive log-exp branch pause and checked-witness delta freeze packet"
    )
    selected = option_by_id(payload, "positive_log_exp_branch_pause_freeze_packet")
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_pause_freeze_lane"


def test_d44_parks_public_gate_and_future_branches():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == "candidate_later_requires_human_approval"
    assert option_by_id(payload, "constant_coordinate_refresh_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert payload["summary"]["humanApprovedPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["newBoundedBranchSelected"] is False


def test_d44_preserves_d43_guard_and_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["positiveDomainGuardRequired"] is True
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["d43WitnessRowCount"] == 1
    assert payload["summary"]["d43RequiredCaveatCount"] == 5
    assert payload["summary"]["d43BlockedGlobalPhraseCount"] == 8


def test_d44_starts_no_pause_public_copy_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["pauseStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d44_keeps_runtime_log_exp_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_remains_runtime_control"
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d44_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    assert CLAIM_FLAGS["next_action_selected"] is True
    assert payload["claimFlags"]["next_action_selected"] is True
    for key, value in payload["claimFlags"].items():
        if key != "next_action_selected":
            assert value is False
    for option in payload["decisionOptions"]:
        assert option["claimFlags"]["next_action_selected"] is True
        for key, value in option["claimFlags"].items():
            if key != "next_action_selected":
                assert value is False


def test_d44_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D44")


def test_d44_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d44_positive_log_exp_review_next_selector.py",
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
    assert "EML_D44_POSITIVE_LOG_EXP_REVIEW_NEXT_SELECTOR_OK" in proc.stdout
