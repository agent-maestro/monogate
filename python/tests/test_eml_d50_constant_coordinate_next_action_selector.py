"""Tests for EML-D50 constant-coordinate next-action selector."""

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

from scripts.eml_d50_constant_coordinate_next_action_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d50_consumes_d49_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D50_CONSTANT_COORDINATE_NEXT_ACTION_SELECTOR_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d49-constant-coordinate-zero-exp-two-surface-review"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True


def test_d50_preserves_spelling_and_non_duplicate_boundary():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceProposedStatement"] == "eml 0 (exp 2) = -1"
    assert payload["summary"]["checkedLeanStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["localSpellingUsesOnePlusOne"] is True
    assert payload["summary"]["existingConstantWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["duplicatesExistingConstantWitness"] is False
    assert payload["summary"]["guardCount"] == 0


def test_d50_selects_private_delta_copy_review():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "constant_coordinate_delta_copy_review_packet")
    assert payload["decision"] == "select_constant_coordinate_delta_copy_review_packet"
    assert payload["summary"]["selectedOptionId"] == "constant_coordinate_delta_copy_review_packet"
    assert payload["summary"]["selectedNextArtifact"] == (
        "EML-D51 constant-coordinate checked-witness delta copy review packet"
    )
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_copy_review_lane"


def test_d50_parks_future_branch_trig_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == (
        "candidate_later_after_copy_review"
    )
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == (
        "candidate_later_after_copy_review"
    )
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_human_approval"
    )
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d50_starts_no_copy_review_public_work_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d50_keeps_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicHoldPreserved"] is True
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_and_arithmetic_remain_runtime_controls"
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d50_claim_flags_are_selector_only():
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


def test_d50_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D50")


def test_d50_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d50_constant_coordinate_next_action_selector.py",
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
    assert "EML_D50_CONSTANT_COORDINATE_NEXT_ACTION_SELECTOR_OK" in proc.stdout
