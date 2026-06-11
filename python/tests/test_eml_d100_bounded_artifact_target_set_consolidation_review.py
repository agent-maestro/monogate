"""Tests for EML-D100 bounded artifact target-set consolidation review."""

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

from scripts.eml_d100_bounded_artifact_target_set_consolidation_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["nextStepOptions"] if item["optionId"] == option_id)


def witness_by_id(payload, witness_id: str):
    return next(item for item in payload["checkedWitnessRows"] if item["witnessId"] == witness_id)


def test_d100_consumes_d99_and_creates_private_consolidation_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D100_BOUNDED_ARTIFACT_TARGET_SET_CONSOLIDATION_REVIEW_PASS"
    assert payload["sourceSelector"] == "eml-d99-post-log1p-affine-scaled-pause-next-selector"
    assert summary["sourceSelectedOptionId"] == "bounded_artifact_target_set_consolidation_review"
    assert summary["sourceSelectedNextArtifact"] == "EML-D100 bounded artifact target-set consolidation review"
    assert summary["consolidationReviewCreated"] is True
    assert summary["privateReviewOnly"] is True


def test_d100_counts_checked_witness_core_against_target_range():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["checkedWitnessCoreCount"] == 13
    assert len(payload["checkedWitnessRows"]) == 13
    assert summary["targetLowerBoundReached"] is False
    assert summary["targetUpperBoundExceeded"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["remainingSlotsBeforeUpperBound"] == 12
    assert summary["selectorOnlyPacketsCountedAsFinalArtifacts"] is False


def test_d100_preserves_d98_affine_log1p_freeze_boundary():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    row = witness_by_id(payload, "log1p_affine_scaled_boundary_coordinate")
    assert summary["d99ConsolidationReviewSelected"] is True
    assert summary["d98BranchPauseStarted"] is True
    assert summary["d98CheckedWitnessCopyFrozen"] is True
    assert summary["d98DuplicateShiftedBlocksPreserved"] is True
    assert summary["d98FrozenWitnessName"] == "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness"
    assert summary["d98FrozenCheckedStatement"] == "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"
    assert summary["d98FrozenGuardCount"] == 1
    assert summary["d98FrozenCaveatCount"] == 10
    assert summary["d98FrozenBlockedPhraseCount"] == 16
    assert row["guardSummary"] == "0 < 1 + a * x"
    assert row["consolidationStatus"] == "core_checked_candidate_frozen_after_d98"


def test_d100_includes_expected_checked_witness_families():
    payload = build_payload(ATLAS_GATE)
    ids = {row["witnessId"] for row in payload["checkedWitnessRows"]}
    assert "constants_zero_one_e_boundary" in ids
    assert "subtraction_boundary_three_stage_chain" in ids
    assert "positive_log_exp_roundtrip" in ids
    assert "expm1_boundary_identity" in ids
    assert "probability_logit_boundary_coordinate" in ids
    assert "log1p_shifted_boundary_coordinate" in ids
    assert "log1m_shifted_boundary_coordinate" in ids
    assert "log1p_affine_scaled_boundary_coordinate" in ids
    assert witness_by_id(payload, "expm1_boundary_identity")["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert witness_by_id(payload, "probability_logit_boundary_coordinate")["guardSummary"] == "0 < p and p < 1"


def test_d100_recommends_private_public_witness_candidate_selector():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["recommendedNextOptionId"] == "private_public_witness_candidate_selector"
    assert summary["recommendedNextArtifact"] == "EML-D101 private public-witness candidate selector"
    assert summary["nextPrivateConsolidationStepRecommended"] is True
    assert summary["nextStepOptionCount"] == 4
    assert option_by_id(payload, "private_public_witness_candidate_selector")["selectionStatus"] == "recommended_next"
    assert option_by_id(payload, "private_claim_topology_surface_mvp")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "sdk_compiler_guard_note_excerpt")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "next_materially_distinct_bounded_branch_selector")["selectionStatus"] == (
        "candidate_later_if_gap_remains"
    )


def test_d100_keeps_public_branch_proof_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["newIdentityCandidateSelected"] is False
    assert summary["nextBoundedIdentityBranchSelected"] is False
    assert summary["boundedTrigFeasibilitySelected"] is False
    assert summary["privateReviewerResponseIntakeSelected"] is False
    assert summary["humanPublicCopyGateSelected"] is False
    assert summary["humanApprovalRecorded"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicPromotionPerformed"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["advantageLabCaseAdded"] is False
    assert summary["implementationStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["catalogCompletenessClaim"] is False
    assert summary["electronicsRepoTouched"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False
    assert all(row["publicPromotionAllowed"] is False for row in payload["checkedWitnessRows"])


def test_d100_claim_flags_are_review_only():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "consolidation_review_created",
        "private_review_only",
        "checked_witness_core_counted",
        "affine_log1p_branch_frozen_observed",
        "next_private_consolidation_step_recommended",
    }
    assert payload["summary"]["claimFlagsReviewOnly"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False


def test_d100_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D100")


def test_d100_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d100_bounded_artifact_target_set_consolidation_review.py",
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
    assert "EML_D100_BOUNDED_ARTIFACT_TARGET_SET_CONSOLIDATION_REVIEW_OK" in proc.stdout
