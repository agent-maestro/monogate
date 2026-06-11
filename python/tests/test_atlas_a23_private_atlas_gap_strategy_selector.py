"""Tests for ATLAS-A23 private Atlas gap strategy selector."""

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

from scripts.atlas_a23_private_atlas_gap_strategy_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_OPTION_ID,
    SOURCE_CANDIDATE_ID,
    STRATEGY_CRITERIA,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a23_consumes_a22_and_selects_gap_pool_refresh():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A23_PRIVATE_ATLAS_GAP_STRATEGY_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a22-private-sqrt-candidate-reframe-or-park-selector"
    assert summary["sourceSelectedOptionId"] == "park_eml_sqrt_candidate_preserve_pure_sqrt_abs_reframe"
    assert summary["sourceCandidateId"] == SOURCE_CANDIDATE_ID
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedDecision"] == "refresh_reference_value_gap_pool_before_more_candidate_packets"
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a23_reviews_parked_sqrt_and_deferred_reciprocal_context():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    carried = payload["carriedContext"]
    assert summary["sourceSqrtCandidateParked"] is True
    assert summary["sourcePureSqrtAbsPreserved"] is True
    assert summary["sqrtParkDecisionReviewed"] is True
    assert summary["reciprocalDeferContextRecorded"] is True
    assert carried["parkedSqrtCandidateId"] == SOURCE_CANDIDATE_ID
    assert carried["preservedPureSqrtAbsCandidateId"] == "sqrt_square_abs_normalized_pure_boundary_candidate"
    assert "ATLAS-A6 deferred reciprocal promotion" in carried["deferredReciprocalContext"]


def test_atlas_a23_records_strategy_criteria_without_creating_pool_or_packet():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["strategyCriteriaRecorded"] is True
    assert summary["strategyCriteriaCount"] == len(STRATEGY_CRITERIA) == 5
    assert payload["strategyCriteria"] == STRATEGY_CRITERIA
    assert summary["gapPoolRefreshRecommended"] is True
    assert summary["newCandidatePoolCreated"] is False
    assert summary["newCandidatePacketCreated"] is False


def test_atlas_a23_options_keep_reopen_paths_available_but_not_selected():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    options = {item["optionId"]: item for item in payload["options"]}
    assert set(options) == {
        SELECTED_OPTION_ID,
        "reopen_pure_sqrt_abs_feasibility",
        "reopen_reciprocal_candidate_path",
        "pause_for_atlas_v0_reference_document",
    }
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert (
        options["reopen_pure_sqrt_abs_feasibility"]["selectionStatus"]
        == "available_if_human_explicitly_wants_sqrt_path"
    )
    assert (
        options["reopen_reciprocal_candidate_path"]["selectionStatus"]
        == "available_if_human_prefers_simpler_algebraic_candidate"
    )
    assert options["pause_for_atlas_v0_reference_document"]["selectionStatus"] == "available_if_human_prefers_consolidation"


def test_atlas_a23_blocks_proof_edit_lean_theorem_public_runtime_and_product_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateRejected"] is False
    assert summary["candidateDisproved"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False
    assert summary["machlibEditBlocked"] is True
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckBlocked"] is True
    assert summary["leanTypecheckPerformed"] is False
    assert summary["leanTypecheckPassed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["runtimeReciprocalReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a23_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a23_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "new_candidate_pool_created",
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
        "runtime_sqrt_replacement_claim",
        "runtime_reciprocal_replacement_claim",
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


def test_atlas_a23_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A23 Private Atlas Gap Strategy Selector")
    assert "## Strategy Criteria" in report
    assert "## Selected Rationale" in report
    assert "## Selected Constraints" in report
    assert "## Options" in report


def test_atlas_a23_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a23_private_atlas_gap_strategy_selector.py",
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
    assert "ATLAS_A23_PRIVATE_ATLAS_GAP_STRATEGY_SELECTOR_OK" in proc.stdout
