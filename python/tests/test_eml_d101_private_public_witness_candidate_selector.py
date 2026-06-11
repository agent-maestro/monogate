"""Tests for EML-D101 private public-witness candidate selector."""

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

from scripts.eml_d101_private_public_witness_candidate_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["candidateOptions"] if item["optionId"] == option_id)


def test_d101_consumes_d100_and_preserves_target_set_context():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D101_PRIVATE_PUBLIC_WITNESS_CANDIDATE_SELECTOR_PASS"
    assert payload["sourceReview"] == "eml-d100-bounded-artifact-target-set-consolidation-review"
    assert summary["sourceRecommendedNextOptionId"] == "private_public_witness_candidate_selector"
    assert summary["sourceRecommendedNextArtifact"] == "EML-D101 private public-witness candidate selector"
    assert summary["sourceCheckedWitnessCoreCount"] == 13
    assert summary["sourceTargetMin"] == 15
    assert summary["sourceTargetMax"] == 25
    assert summary["sourceAdditionalArtifactsNeededForLowerBound"] == 2
    assert summary["sourceRemainingSlotsBeforeUpperBound"] == 12
    assert summary["sourceSelectorOnlyPacketsCountedAsFinalArtifacts"] is False
    assert summary["sourceAffineLog1pBranchFrozenObserved"] is True


def test_d101_selects_exactly_one_expm1_candidate():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    selected_options = [
        option for option in payload["candidateOptions"] if option["selectionStatus"] == "selected_next"
    ]
    assert len(selected_options) == 1
    assert summary["candidateOptionCount"] == 4
    assert summary["publicWitnessCandidateSelected"] is True
    assert summary["privateSelectorOnly"] is True
    assert summary["checkedWitnessCoreObserved"] is True
    assert summary["expm1BoundaryCandidateSelected"] is True
    assert summary["publicWitnessCopyPacketRecommended"] is True
    assert summary["selectedOptionId"] == "expm1_boundary_identity_public_witness_candidate"
    assert summary["selectedCandidateId"] == "expm1_boundary_identity"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["selectedFamily"] == "expm1_boundary"
    assert summary["selectedCheckedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["selectedGuardSummary"] == "no extra real-domain guard recorded"
    assert summary["selectedRuntimeControl"] == "protected_expm1_remains_runtime_control"
    assert summary["selectedNextArtifact"] == "EML-D102 expm1 boundary public-witness copy packet"
    assert payload["selectedCandidate"] == selected_options[0]


def test_d101_keeps_alternate_candidates_parked():
    payload = build_payload(ATLAS_GATE)
    assert option_by_id(payload, "expm1_boundary_identity_public_witness_candidate")["selectionStatus"] == (
        "selected_next"
    )
    assert option_by_id(payload, "positive_log_exp_roundtrip_public_witness_candidate")["selectionStatus"] == (
        "candidate_later"
    )
    assert option_by_id(payload, "subtraction_boundary_affine_offset_public_witness_candidate")[
        "selectionStatus"
    ] == "candidate_later"
    assert option_by_id(payload, "log1p_affine_scaled_boundary_public_witness_candidate")[
        "selectionStatus"
    ] == "candidate_later_after_affine_branch_rest"
    assert option_by_id(payload, "log1p_affine_scaled_boundary_public_witness_candidate")[
        "runtimeControl"
    ] == "protected_log_and_log1p_remain_runtime_controls"
    assert all(option["publicPromotionAllowed"] is False for option in payload["candidateOptions"])


def test_d101_blocks_public_proof_runtime_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
        "publicCopyDrafted",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "claimTopologySurfaceCreated",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "boundedTrigFeasibilitySelected",
        "advantageLabCaseAdded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedLogReplacementClaim",
        "protectedLog1pReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "fullEmlSemanticsClaim",
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        assert summary[key] is False


def test_d101_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "public_witness_candidate_selected",
        "private_selector_only",
        "checked_witness_core_observed",
        "expm1_boundary_candidate_selected",
        "public_witness_copy_packet_recommended",
    }
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False


def test_d101_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D101")


def test_d101_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d101_private_public_witness_candidate_selector.py",
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
    assert "EML_D101_PRIVATE_PUBLIC_WITNESS_CANDIDATE_SELECTOR_OK" in proc.stdout
