"""Tests for ATLAS-A25 private refreshed gap candidate value selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a25_private_refreshed_gap_candidate_value_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_DIRECTION_ID,
    SOURCE_POOL_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a25_consumes_a24_and_selects_exp_negation_future_feasibility():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A25_PRIVATE_REFRESHED_GAP_CANDIDATE_VALUE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a24-private-reference-value-gap-pool-refresh"
    assert summary["sourcePoolId"] == SOURCE_POOL_ID
    assert summary["sourceCandidateDirectionCount"] == 4
    assert summary["selectedDirectionId"] == SELECTED_DIRECTION_ID
    assert summary["selectedDecision"] == "recommend_exp_negation_boundary_feasibility_packet"
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a25_defers_square_despite_higher_raw_score():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    decisions = {item["entryId"]: item for item in payload["valueDecisions"]}
    assert summary["sourceHighestReferenceValueEntryId"] == "square_nonnegative_guard_direction"
    assert summary["higherScoreSquareDirectionDeferred"] is True
    assert decisions["square_nonnegative_guard_direction"]["selectionStatus"] == "deferred_despite_higher_raw_score"
    assert "too elementary" in " ".join(decisions["square_nonnegative_guard_direction"]["valueRationale"])
    assert decisions[SELECTED_DIRECTION_ID]["selectionStatus"] == "selected_for_future_feasibility_packet"


def test_atlas_a25_records_all_value_decisions():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    decisions = {item["entryId"]: item for item in payload["valueDecisions"]}
    assert set(decisions) == {
        SELECTED_DIRECTION_ID,
        "square_nonnegative_guard_direction",
        "trig_pythagorean_unit_identity_direction",
        "logistic_symmetry_boundary_direction",
    }
    assert decisions["trig_pythagorean_unit_identity_direction"]["selectionStatus"] == "deferred_higher_namespace_risk"
    assert decisions["logistic_symmetry_boundary_direction"]["selectionStatus"] == "deferred_definition_risk"
    assert decisions[SELECTED_DIRECTION_ID]["sourceDirection"]["familyHint"] == "exp_algebra_boundary"
    assert decisions[SELECTED_DIRECTION_ID]["nextArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a25_recommends_future_feasibility_but_creates_no_packet_or_proof():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["nextFeasibilityPacketRecommended"] is True
    assert summary["newCandidatePacketCreated"] is False
    assert summary["feasibilityPacketCreated"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False


def test_atlas_a25_blocks_edit_lean_theorem_public_runtime_and_product_claims():
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


def test_atlas_a25_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a25_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "new_candidate_packet_created",
        "feasibility_packet_created",
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


def test_atlas_a25_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A25 Private Refreshed Gap Candidate Value Selector")
    assert "## Selected Rationale" in report
    assert "## Value Decisions" in report


def test_atlas_a25_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a25_private_refreshed_gap_candidate_value_selector.py",
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
    assert "ATLAS_A25_PRIVATE_REFRESHED_GAP_CANDIDATE_VALUE_SELECTOR_OK" in proc.stdout
