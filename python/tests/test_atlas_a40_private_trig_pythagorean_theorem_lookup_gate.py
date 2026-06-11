"""Tests for ATLAS-A40 private trig pythagorean theorem-lookup gate."""

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

from scripts.atlas_a40_private_trig_pythagorean_theorem_lookup_gate import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    PRIMARY_OBSERVED_IDENTIFIER,
    ROOT,
    SOURCE_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a40_consumes_a39_and_records_lookup_gate():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A40_PRIVATE_TRIG_PYTHAGOREAN_THEOREM_LOOKUP_GATE_PASS"
    assert payload["sourceArtifact"] == "atlas-a39-private-trig-pythagorean-proof-scope-feasibility-packet"
    assert summary["sourceReviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["theoremLookupGateCreated"] is True
    assert summary["boundedLookupPerformed"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a40_scopes_lookup_to_pure_trig_and_keeps_eml_deferred():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    review = payload["theoremLookupReview"]
    assert summary["lookupScopeStatement"] == (
        "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1"
    )
    assert summary["lookupScopeGuard"] == "all real x"
    assert summary["pureTrigStatementLookupScoped"] is True
    assert summary["emlCompanionKeptDeferred"] is True
    assert summary["deferredCompanionStatement"] == "deferred_no_eml_shape_selected"
    assert review["lookupScope"]["scopeStatus"] == "pure_trig_statement_only_eml_companion_deferred"


def test_atlas_a40_records_observed_identifier_candidates():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    review = payload["theoremLookupReview"]
    identifiers = [item["identifier"] for item in review["observedIdentifierCandidates"]]
    assert summary["observedIdentifierCandidatesRecorded"] is True
    assert summary["observedIdentifierCandidateCount"] == 3
    assert summary["primaryObservedIdentifierRecorded"] is True
    assert summary["primaryObservedIdentifier"] == PRIMARY_OBSERVED_IDENTIFIER
    assert identifiers == [
        "MachLib.Real.sin_sq_add_cos_sq",
        "MachLib.Real.pythagorean",
        "MachLib.Real.sin_cos_pythagorean_checked",
    ]
    assert review["primaryObservedIdentifier"]["matchStatus"] == (
        "primary_shape_match_observed_not_typechecked_this_phase"
    )


def test_atlas_a40_records_lookup_method_and_blockers():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    review = payload["theoremLookupReview"]
    assert review["lookupMethod"]["method"] == "bounded_read_only_text_lookup"
    assert review["lookupMethod"]["leanTypecheckPerformed"] is False
    assert review["lookupMethod"]["machlibEdited"] is False
    assert len(review["readinessReasons"]) == 3
    assert len(review["blockersBeforeWitnessAttempt"]) == 5
    assert "run Lean only in a separately gated future phase" in review["blockersBeforeWitnessAttempt"]
    assert "keep the EML companion deferred until a concrete EML boundary shape is selected" in review[
        "blockersBeforeWitnessAttempt"
    ]


def test_atlas_a40_creates_no_dependency_proof_or_validity_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
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


def test_atlas_a40_blocks_edit_lean_public_runtime_and_product_claims():
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


def test_atlas_a40_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 14
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 1
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a40_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
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


def test_atlas_a40_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A40 Private Trig Pythagorean Theorem-Lookup Gate")
    assert "## Observed Identifier Candidates" in report
    assert "## Readiness Reasons" in report
    assert "## Blockers Before Witness Attempt" in report


def test_atlas_a40_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a40_private_trig_pythagorean_theorem_lookup_gate.py",
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
    assert "ATLAS_A40_PRIVATE_TRIG_PYTHAGOREAN_THEOREM_LOOKUP_GATE_OK" in proc.stdout
