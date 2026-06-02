"""Tests for EML-D42 positive log-exp next-action selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d42_positive_log_exp_next_action_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d42_consumes_d41_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D42_POSITIVE_LOG_EXP_NEXT_ACTION_SELECTOR_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d41-positive-log-exp-witness-surface-review"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert payload["summary"]["sourceSelectedCandidateId"] == "positive_log_exp_roundtrip_identity"


def test_d42_selects_positive_log_exp_delta_copy_review():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "select_positive_log_exp_delta_copy_review_packet"
    assert payload["summary"]["selectedOptionId"] == "positive_log_exp_delta_copy_review_packet"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D43 positive log-exp checked-witness delta copy review packet"
    selected = option_by_id(payload, "positive_log_exp_delta_copy_review_packet")
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_copy_review_lane"


def test_d42_parks_other_private_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "constant_coordinate_refresh_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "positive_log_exp_branch_pause")["selectionStatus"] == "candidate_later"


def test_d42_preserves_d41_guard_public_hold_and_runtime_boundary():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True
    assert payload["summary"]["candidateProved"] is True
    assert payload["summary"]["positiveDomainGuardRequired"] is True
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["publicHoldPreserved"] is True
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_remains_runtime_control"


def test_d42_starts_no_copy_review_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStarted"] is False
    assert payload["summary"]["pauseStarted"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d42_keeps_public_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["surfaceUpdated"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d42_claim_flags_are_bounded():
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


def test_d42_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D42")


def test_d42_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d42_positive_log_exp_next_action_selector.py",
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
    assert "EML_D42_POSITIVE_LOG_EXP_NEXT_ACTION_SELECTOR_OK" in proc.stdout
