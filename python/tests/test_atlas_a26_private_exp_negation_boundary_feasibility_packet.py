"""Tests for ATLAS-A26 private exp-negation boundary feasibility packet."""

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

from scripts.atlas_a26_private_exp_negation_boundary_feasibility_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SOURCE_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a26_consumes_a25_and_creates_feasibility_packet():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A26_PRIVATE_EXP_NEGATION_BOUNDARY_FEASIBILITY_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a25-private-refreshed-gap-candidate-value-selector"
    assert summary["sourceSelectedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["sourceSelectedDecision"] == "recommend_exp_negation_boundary_feasibility_packet"
    assert summary["reviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["feasibilityPacketCreated"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a26_reviews_guard_statement_shape_and_reference_value():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    review = payload["feasibilityReview"]
    assert summary["guardReviewed"] is True
    assert summary["statementShapeReviewed"] is True
    assert summary["referenceValueReviewed"] is True
    assert summary["requiredGuard"] == "all real x"
    assert summary["pureShapeHint"] == "exp x * exp (-x) = 1"
    assert summary["possibleEmlBoundaryHint"] == "eml (x + (-x)) 1 = 1"
    assert review["guardReview"]["guardStatus"] == "clean_all_real_guard_surface"
    assert review["referenceValueReview"]["referenceStatus"] == "moderate_high_reference_value_for_atlas_gap"
    assert len(review["referenceValueReview"]["whyUseful"]) == 3


def test_atlas_a26_records_blockers_before_candidate_packet():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    review = payload["feasibilityReview"]
    assert summary["blockersRecorded"] is True
    assert summary["feasibleForCandidateSelectorRecorded"] is True
    assert summary["feasibilityStatus"] == (
        "feasible_for_later_private_candidate_selector_not_candidate_packet_not_validity_claim"
    )
    assert len(review["blockersBeforeCandidatePacket"]) == 4
    assert "choose pure exp statement" in review["blockersBeforeCandidatePacket"][0]
    assert "must not be conflated" in review["statementShapeReview"]["shapeCaveats"][0]


def test_atlas_a26_creates_no_candidate_packet_or_proof_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["newCandidatePacketCreated"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateRejected"] is False
    assert summary["candidateDisproved"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False


def test_atlas_a26_blocks_edit_lean_theorem_public_runtime_and_product_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["machlibEditBlocked"] is True
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckBlocked"] is True
    assert summary["leanTypecheckPerformed"] is False
    assert summary["leanTypecheckPassed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeExpReplacementClaim"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["runtimeReciprocalReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a26_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a26_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "new_candidate_packet_created",
        "candidate_selected_for_proof",
        "candidate_validity_claim",
        "candidate_rejected",
        "candidate_disproved",
        "candidate_proved",
        "proof_attempt_started",
        "proof_attempt_completed",
        "machlib_file_changed",
        "machlib_commit_created",
        "lean_typecheck_performed",
        "lean_typecheck_passed",
        "theorem_lookup_performed",
        "exact_theorem_names_claimed",
        "runtime_lowering_changed",
        "runtime_exp_replacement_claim",
        "public_atlas_promotion",
        "public_copy_approved",
        "sdk_compiler_docs_created",
        "course_material_created",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "catalog_completeness_claim",
        "target_lower_bound_reached_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a26_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
        MACHLIB_ROOT,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# ATLAS-A26 Private Exp-Negation Boundary Feasibility Packet")
    assert "## Reference Value" in report
    assert "## Statement Shape Caveats" in report
    assert "## Blockers Before Candidate Packet" in report


def test_atlas_a26_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a26_private_exp_negation_boundary_feasibility_packet.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
            "--machlib-root",
            str(MACHLIB_ROOT),
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
    assert "ATLAS_A26_PRIVATE_EXP_NEGATION_BOUNDARY_FEASIBILITY_PACKET_OK" in proc.stdout
