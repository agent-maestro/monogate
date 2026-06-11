"""Tests for EML-D70 probability logit branch pause next selector."""

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

from scripts.eml_d70_probability_logit_branch_pause_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d70_consumes_d69_copy_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D70_PROBABILITY_LOGIT_BRANCH_PAUSE_NEXT_SELECTOR_PASS"
    assert payload["sourceReview"] == "eml-d69-probability-logit-checked-witness-copy-review-packet"
    assert payload["summary"]["sourceSelectedOptionId"] == "probability_logit_checked_witness_copy_review_packet"
    assert payload["summary"]["d69CopyReviewStarted"] is True
    assert payload["summary"]["d69PrivateCopyReviewOnly"] is True
    assert payload["summary"]["d69CheckedWitnessCopyReviewOnly"] is True


def test_d70_preserves_probability_logit_copy_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"
    assert payload["summary"]["sourceSelectedCandidateId"] == "probability_logit_boundary_coordinate"
    assert payload["summary"]["sourceSelectedFamily"] == "guarded_probability_log_coordinate"
    assert payload["summary"]["checkedStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["guardCount"] == 2
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"


def test_d70_selects_probability_logit_pause_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "probability_logit_branch_pause_freeze_packet")
    assert payload["decision"] == "select_probability_logit_branch_pause_freeze_packet"
    assert payload["summary"]["selectedOptionId"] == "probability_logit_branch_pause_freeze_packet"
    assert payload["summary"]["selectedNextArtifact"] == (
        "EML-D71 probability-logit branch pause and checked-witness copy freeze packet"
    )
    assert payload["summary"]["nextActionSelected"] is True
    assert payload["summary"]["branchPauseFreezeSelected"] is True
    assert payload["summary"]["checkedWitnessCopyFreezePlanned"] is True
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_pause_freeze_lane"


def test_d70_parks_future_branch_trig_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later_after_pause"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == "candidate_later_requires_human_approval"
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d70_preserves_d69_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert payload["summary"]["d67SurfaceRowCount"] == 5
    assert payload["summary"]["d69WitnessRowCount"] == 1
    assert payload["summary"]["d69RequiredCaveatCount"] == 9
    assert payload["summary"]["d69BlockedGlobalPhraseCount"] == 12
    assert payload["summary"]["d69RowRequiredCaveatCount"] == 6
    assert payload["summary"]["d69RowBlockedPhraseCount"] == 10


def test_d70_starts_no_pause_public_copy_or_implementation():
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


def test_d70_keeps_runtime_laptop_and_electronics_claims_blocked():
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


def test_d70_claim_flags_are_bounded():
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


def test_d70_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D70")


def test_d70_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d70_probability_logit_branch_pause_next_selector.py",
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
    assert "EML_D70_PROBABILITY_LOGIT_BRANCH_PAUSE_NEXT_SELECTOR_OK" in proc.stdout
