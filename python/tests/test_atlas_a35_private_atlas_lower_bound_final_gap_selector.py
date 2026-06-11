"""Tests for ATLAS-A35 private Atlas lower-bound final gap selector."""

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

from scripts.atlas_a35_private_atlas_lower_bound_final_gap_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def decision_by_id(payload, entry_id: str):
    return next(item for item in payload["valueDecisions"] if item["entryId"] == entry_id)


def test_atlas_a35_consumes_a34_and_references_gap_pool():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    assert payload["status"] == "ATLAS_A35_PRIVATE_ATLAS_LOWER_BOUND_FINAL_GAP_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a34-private-exp-negation-checked-wrapper-surface-review"
    assert payload["summary"]["gapPoolArtifact"] == "atlas-a24-private-reference-value-gap-pool-refresh"
    assert payload["summary"]["gapPoolCandidateDirectionCount"] == 4


def test_atlas_a35_selects_trig_for_future_feasibility():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    selected = payload["selectedDecision"]
    assert summary["selectedDirectionId"] == SELECTED_DIRECTION_ID
    assert summary["selectedDecision"] == "recommend_trig_pythagorean_feasibility_packet"
    assert summary["selectedFamilyHint"] == "trig_boundary"
    assert summary["selectedShapeHint"] == "sin x * sin x + cos x * cos x = 1"
    assert summary["selectedGuardHint"] == "all real x"
    assert summary["trigDirectionSelectedForFutureFeasibility"] is True
    assert selected["nextArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a35_records_deferred_alternatives():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    square = decision_by_id(payload, "square_nonnegative_guard_direction")
    exp_negation = decision_by_id(payload, "exp_negation_multiplicative_identity_direction")
    logistic = decision_by_id(payload, "logistic_symmetry_boundary_direction")
    assert square["selectionStatus"] == "deferred_as_too_elementary_for_final_lower_bound_slot"
    assert exp_negation["selectionStatus"] == "already_reviewed_as_a33_a34_private_row_candidate"
    assert logistic["selectionStatus"] == "deferred_definition_risk"
    assert payload["summary"]["squareDirectionDeferredAsTooElementary"] is True
    assert payload["summary"]["expNegationMarkedAlreadyReviewed"] is True
    assert payload["summary"]["logisticDirectionDeferredDefinitionRisk"] is True


def test_atlas_a35_preserves_lower_bound_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["sourceAtlasRowCount"] == 14
    assert summary["atlasRowCount"] == 14
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 1
    assert summary["targetLowerBoundReachedClaim"] is False
    assert summary["catalogCompletenessClaim"] is False


def test_atlas_a35_creates_no_packet_proof_machlib_or_lean_work():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["newCandidatePacketCreated"] is False
    assert summary["feasibilityPacketCreated"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibEditBlocked"] is True
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckBlocked"] is True
    assert summary["leanTypecheckPerformed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False


def test_atlas_a35_keeps_public_runtime_product_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeTrigReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False


def test_atlas_a35_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for decision in payload["valueDecisions"]:
        for key in TRUE_CLAIM_FLAGS:
            assert decision["claimFlags"][key] is True
        for key, value in decision["claimFlags"].items():
            if key not in TRUE_CLAIM_FLAGS:
                assert value is False
    for blocked in [
        "new_candidate_packet_created",
        "feasibility_packet_created",
        "candidate_validity_claim",
        "candidate_proved",
        "proof_attempt_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "theorem_lookup_performed",
        "exact_theorem_names_claimed",
        "runtime_lowering_changed",
        "runtime_trig_replacement_claim",
        "public_atlas_promotion",
        "public_copy_approved",
        "public_surface_updated",
        "sdk_compiler_docs_created",
        "course_material_created",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "target_lower_bound_reached_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "formal_equivalence_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a35_points_to_a36():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a35_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A35 Private Atlas Lower-Bound Final Gap Selector")
    assert "## Value Decisions" in report
    assert "## Blocked Before A36" in report


def test_atlas_a35_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a35_private_atlas_lower_bound_final_gap_selector.py",
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
    assert "ATLAS_A35_PRIVATE_ATLAS_LOWER_BOUND_FINAL_GAP_SELECTOR_OK" in proc.stdout
