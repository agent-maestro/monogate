"""Tests for ATLAS-A24 private reference-value gap pool refresh."""

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

from scripts.atlas_a24_private_reference_value_gap_pool_refresh import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    POOL_ID,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a24_consumes_a23_and_creates_pool_refresh():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A24_PRIVATE_REFERENCE_VALUE_GAP_POOL_REFRESH_PASS"
    assert payload["sourceArtifact"] == "atlas-a23-private-atlas-gap-strategy-selector"
    assert summary["sourceSelectedOptionId"] == "refresh_non_sqrt_non_reciprocal_gap_pool"
    assert summary["sourceSelectedDecision"] == "refresh_reference_value_gap_pool_before_more_candidate_packets"
    assert summary["poolId"] == POOL_ID
    assert summary["gapPoolRefreshCreated"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a24_records_excluded_paths_without_rejection_or_disproof():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    excluded = {item["pathId"]: item for item in payload["excludedPaths"]}
    assert summary["excludedPathsRecorded"] is True
    assert summary["excludedPathCount"] == 2
    assert excluded["blocked_eml_sqrt_boundary_path"]["status"] == "excluded_from_a24_pool_unless_new_precise_statement"
    assert excluded["deferred_reciprocal_positive_boundary_path"]["status"] == "deferred_not_rejected"
    assert summary["candidateRejected"] is False
    assert summary["candidateDisproved"] is False


def test_atlas_a24_records_candidate_directions_and_scores():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    directions = {item["entryId"]: item for item in payload["candidateDirections"]}
    assert summary["candidateDirectionsRecorded"] is True
    assert summary["candidateDirectionScoresRecorded"] is True
    assert summary["candidateDirectionCount"] == 4
    assert set(directions) == {
        "trig_pythagorean_unit_identity_direction",
        "exp_negation_multiplicative_identity_direction",
        "square_nonnegative_guard_direction",
        "logistic_symmetry_boundary_direction",
    }
    assert directions["trig_pythagorean_unit_identity_direction"]["familyHint"] == "trig_boundary"
    assert directions["exp_negation_multiplicative_identity_direction"]["guardHint"] == "all real x"
    assert directions["square_nonnegative_guard_direction"]["shapeHint"] == "0 <= x * x"
    assert directions["logistic_symmetry_boundary_direction"]["referenceStatus"].endswith("not_validity_claim")
    assert summary["highestReferenceValueEntryId"] in directions


def test_atlas_a24_creates_no_candidate_packet_and_selects_no_proof_target():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["candidateSelectedForPacket"] is False
    assert summary["newCandidatePacketCreated"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False


def test_atlas_a24_blocks_edit_lean_theorem_public_runtime_and_product_claims():
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
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["runtimeReciprocalReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a24_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a24_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "candidate_selected_for_packet",
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


def test_atlas_a24_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A24 Private Reference-Value Gap Pool Refresh")
    assert "## Excluded Paths" in report
    assert "## Candidate Directions" in report


def test_atlas_a24_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a24_private_reference_value_gap_pool_refresh.py",
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
    assert "ATLAS_A24_PRIVATE_REFERENCE_VALUE_GAP_POOL_REFRESH_OK" in proc.stdout
