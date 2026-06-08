"""Tests for ATLAS-A32 private exp-negation wrapper-or-alias attempt gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a32_private_exp_negation_wrapper_or_alias_attempt_gate import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    PROPOSED_WITNESS_NAME,
    ROOT,
    SELECTED_ATTEMPT_SHAPE_ID,
    SOURCE_DIRECTION_ID,
    TARGET_FILE,
    TARGET_NAMESPACE,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a32_consumes_a31_and_selects_future_attempt_shape():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A32_PRIVATE_EXP_NEGATION_WRAPPER_OR_ALIAS_ATTEMPT_GATE_PASS"
    assert payload["sourceArtifact"] == "atlas-a31-private-exp-negation-witness-wrapper-readiness-selector"
    assert summary["sourceReviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["wrapperOrAliasAttemptGateCreated"] is True
    assert summary["attemptShapeSelected"] is True
    assert summary["selectedAttemptShapeId"] == SELECTED_ATTEMPT_SHAPE_ID
    assert summary["futureWrapperAttemptRecommended"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a32_records_target_shape():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    gate = payload["wrapperOrAliasAttemptGate"]
    assert summary["targetFileRecorded"] is True
    assert summary["targetFile"] == TARGET_FILE
    assert summary["targetNamespaceRecorded"] is True
    assert summary["targetNamespace"] == TARGET_NAMESPACE
    assert summary["proposedWitnessNameRecorded"] is True
    assert summary["proposedWitnessName"] == PROPOSED_WITNESS_NAME
    assert summary["proposedStatement"] == "forall x : Real, Real.exp x * Real.exp (-x) = 1"
    assert gate["target"]["targetStatus"] == "recorded_for_future_attempt_not_edited_not_typechecked"


def test_atlas_a32_records_observed_surface_and_deferred_companion():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    gate = payload["wrapperOrAliasAttemptGate"]
    assert summary["primaryObservedIdentifier"] == "MachLib.Real.exp_mul_exp_neg"
    assert gate["observedSurface"]["dependencyStatus"] == "observed_surface_only_not_claimed_as_dependency"
    assert summary["emlCompanionKeptDeferred"] is True
    assert summary["deferredCompanionStatement"] == "eml (x + (-x)) 1 = 1"


def test_atlas_a32_records_future_plan_and_blocked_alternatives():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    gate = payload["wrapperOrAliasAttemptGate"]
    assert len(gate["futureAttemptPlan"]) == 5
    assert len(gate["blockedAlternatives"]) == 3
    assert "open only foundations/MachLib/EMLAtlasWitness.lean in the future attempt" in gate[
        "futureAttemptPlan"
    ]
    assert "do not include the EML companion hint in the first wrapper attempt" in gate[
        "blockedAlternatives"
    ]


def test_atlas_a32_creates_no_attempt_dependency_proof_or_validity_claims():
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


def test_atlas_a32_blocks_edit_lean_public_runtime_and_product_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["machlibEditBlocked"] is True
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckBlocked"] is True
    assert summary["leanTypecheckPerformed"] is False
    assert summary["leanTypecheckPassed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeExpReplacementClaim"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["runtimeReciprocalReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a32_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a32_claim_flags_stay_bounded():
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
        "checked_witness_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "formal_equivalence_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a32_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A32 Private Exp-Negation Wrapper-Or-Alias Attempt Gate")
    assert "## Target Shape" in report
    assert "## Future Attempt Plan" in report
    assert "## Blocked Alternatives" in report


def test_atlas_a32_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a32_private_exp_negation_wrapper_or_alias_attempt_gate.py",
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
    assert "ATLAS_A32_PRIVATE_EXP_NEGATION_WRAPPER_OR_ALIAS_ATTEMPT_GATE_OK" in proc.stdout
