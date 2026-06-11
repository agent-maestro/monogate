"""Tests for EML-D31 checked-witness review next decision."""

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

from scripts.eml_d31_checked_witness_review_next_decision import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d31_consumes_d30_copy_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D31_CHECKED_WITNESS_REVIEW_NEXT_DECISION_PASS"
    assert payload["sourceReview"] == "eml-d30-checked-witness-copy-review-packet"
    assert payload["summary"]["d30CopyReviewStarted"] is True
    assert payload["summary"]["d30PrivateCopyReviewOnly"] is True
    assert payload["summary"]["d30WitnessRowCount"] == 6


def test_d31_selects_family_pause_and_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "select_pause_subtraction_family_deepening"
    assert payload["summary"]["selectedOptionId"] == "pause_subtraction_family_deepening"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D32 subtraction-family pause and checked-witness index freeze packet"
    selected = option_by_id(payload, "pause_subtraction_family_deepening")
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_pause_freeze_lane"
    assert payload["summary"]["familyDeepeningPauseSelected"] is True
    assert payload["summary"]["checkedWitnessIndexFreezePlanned"] is True


def test_d31_parks_public_copy_gate_and_new_branch():
    payload = build_payload(ATLAS_GATE)
    public_gate = option_by_id(payload, "human_approved_public_copy_gate")
    new_branch = option_by_id(payload, "new_bounded_identity_branch_selector")
    assert public_gate["selectionStatus"] == "candidate_later_requires_human_approval"
    assert new_branch["selectionStatus"] == "candidate_later_after_pause"
    assert payload["summary"]["humanApprovedPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["newBoundedBranchSelected"] is False


def test_d31_preserves_d30_caveat_and_blocker_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["d30RequiredCaveatCount"] == 5
    assert payload["summary"]["d30BlockedGlobalPhraseCount"] == 8
    assert payload["summary"]["optionCount"] == 3


def test_d31_starts_no_public_copy_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStartedInD31"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["publicReady"] is False


def test_d31_keeps_broad_family_and_runtime_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["advantageLabCaseAdded"] is False


def test_d31_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for option in payload["decisionOptions"]:
        assert all(value is False for value in option["claimFlags"].values())


def test_d31_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D31")


def test_d31_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d31_checked_witness_review_next_decision.py",
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
    assert "EML_D31_CHECKED_WITNESS_REVIEW_NEXT_DECISION_OK" in proc.stdout
