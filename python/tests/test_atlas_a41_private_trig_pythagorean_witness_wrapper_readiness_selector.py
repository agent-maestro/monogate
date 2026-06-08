"""Tests for ATLAS-A41 private trig pythagorean witness-wrapper readiness selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a41_private_trig_pythagorean_witness_wrapper_readiness_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_DECISION_ID,
    SOURCE_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a41_consumes_a40_and_recommends_future_gate():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A41_PRIVATE_TRIG_PYTHAGOREAN_WITNESS_WRAPPER_READINESS_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a40-private-trig-pythagorean-theorem-lookup-gate"
    assert summary["sourceReviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["lookupResultConsumed"] is True
    assert summary["witnessWrapperReadinessSelectorCreated"] is True
    assert summary["selectedDecisionId"] == SELECTED_DECISION_ID
    assert summary["wrapperOrAliasFutureGateRecommended"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a41_reviews_observed_identifier_and_scope():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    selected = payload["selectedOption"]
    assert summary["primaryObservedIdentifierReviewed"] is True
    assert summary["primaryObservedIdentifier"] == "MachLib.Real.sin_sq_add_cos_sq"
    assert summary["lookupScopeStatement"] == (
        "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1"
    )
    assert summary["lookupScopeGuard"] == "all real x"
    assert summary["emlCompanionKeptDeferred"] is True
    assert summary["deferredCompanionStatement"] == "deferred_no_eml_shape_selected"
    assert selected["sourceSignals"]["primaryObservedIdentifier"] == "MachLib.Real.sin_sq_add_cos_sq"


def test_atlas_a41_records_options():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    options = {item["optionId"]: item for item in payload["options"]}
    assert set(options) == {
        SELECTED_DECISION_ID,
        "park_trig_pythagorean_after_lookup",
        "request_human_scope_review",
    }
    assert options[SELECTED_DECISION_ID]["selectionStatus"] == "selected_next"
    assert options["park_trig_pythagorean_after_lookup"]["selectionStatus"] == (
        "available_if_reviewer_prefers_atlas_pause"
    )
    assert options["request_human_scope_review"]["selectionStatus"] == (
        "available_if_dependency_claim_wording_needs_review"
    )
    assert len(options[SELECTED_DECISION_ID]["futureGateRequirements"]) == 5


def test_atlas_a41_creates_no_wrapper_dependency_proof_or_validity_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["wrapperAttemptStarted"] is False
    assert summary["wrapperAttemptCompleted"] is False
    assert summary["aliasAttemptStarted"] is False
    assert summary["observedIdentifierClaimedAsDependency"] is False
    assert summary["exactTheoremNamesClaimed"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateRejected"] is False
    assert summary["candidateDisproved"] is False
    assert summary["candidateProved"] is False
    assert summary["proofScopeFinalized"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False
    assert summary["checkedWitnessClaim"] is False


def test_atlas_a41_blocks_edit_lean_public_runtime_and_product_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["machlibEditBlocked"] is True
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckBlocked"] is True
    assert summary["leanTypecheckPerformed"] is False
    assert summary["leanTypecheckPassed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeTrigReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a41_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 14
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 1
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a41_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "wrapper_attempt_started",
        "wrapper_attempt_completed",
        "alias_attempt_started",
        "candidate_selected_for_proof",
        "candidate_validity_claim",
        "candidate_rejected",
        "candidate_disproved",
        "candidate_proved",
        "proof_scope_finalized",
        "proof_attempt_started",
        "proof_attempt_completed",
        "machlib_file_changed",
        "machlib_commit_created",
        "lean_typecheck_performed",
        "lean_typecheck_passed",
        "observed_identifier_claimed_as_dependency",
        "exact_theorem_names_claimed",
        "runtime_lowering_changed",
        "runtime_trig_replacement_claim",
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
        "checked_witness_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "formal_equivalence_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a41_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A41 Private Trig Pythagorean Witness-Wrapper Readiness Selector")
    assert "## Readiness Reasons" in report
    assert "## Future Gate Requirements" in report
    assert "## Options" in report


def test_atlas_a41_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a41_private_trig_pythagorean_witness_wrapper_readiness_selector.py",
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
    assert "ATLAS_A41_PRIVATE_TRIG_PYTHAGOREAN_WITNESS_WRAPPER_READINESS_SELECTOR_OK" in proc.stdout
