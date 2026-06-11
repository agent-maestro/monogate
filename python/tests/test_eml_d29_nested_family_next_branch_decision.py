"""Tests for EML-D29 nested-family next branch decision."""

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

from scripts.eml_d29_nested_family_next_branch_decision import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d29_consumes_d28_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D29_NESTED_FAMILY_NEXT_BRANCH_DECISION_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d28-subtraction-boundary-three-stage-chain-surface-review"
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True
    assert payload["summary"]["threeStageWitnessRecordedPrivately"] is True


def test_d29_selects_checked_witness_copy_review_packet():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "select_checked_witness_copy_review_packet"
    assert payload["summary"]["selectedOptionId"] == "checked_witness_copy_review_packet"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D30 checked witness copy review packet"
    selected = option_by_id(payload, "checked_witness_copy_review_packet")
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_copy_review_lane"


def test_d29_parks_family_pause_and_new_branch():
    payload = build_payload(ATLAS_GATE)
    pause = option_by_id(payload, "pause_subtraction_family_deepening")
    new_branch = option_by_id(payload, "new_bounded_identity_branch_selector")
    assert pause["selectionStatus"] == "candidate_later"
    assert new_branch["selectionStatus"] == "candidate_later"
    assert payload["summary"]["familyPausePreviouslyParked"] is True
    assert payload["summary"]["copyReviewStarted"] is False


def test_d29_preserves_checked_witness_chain():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["negativeControlBlockedBySelector"] is True
    assert payload["summary"]["twoStageWitnessRecordedPrivately"] is True
    assert payload["summary"]["affineNestedWitnessRecordedPrivately"] is True
    assert payload["summary"]["threeStageWitnessRecordedPrivately"] is True
    assert payload["summary"]["optionCount"] == 3


def test_d29_starts_no_implementation_or_public_copy():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d29_keeps_broad_nested_and_runtime_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"


def test_d29_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for option in payload["decisionOptions"]:
        assert all(value is False for value in option["claimFlags"].values())


def test_d29_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D29")


def test_d29_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d29_nested_family_next_branch_decision.py",
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
    assert "EML_D29_NESTED_FAMILY_NEXT_BRANCH_DECISION_OK" in proc.stdout
