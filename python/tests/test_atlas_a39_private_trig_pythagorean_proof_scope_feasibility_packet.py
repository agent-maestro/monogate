"""Tests for ATLAS-A39 private trig pythagorean proof-scope feasibility packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_PROOF_SCOPE_ID,
    SOURCE_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a39_consumes_a38_and_recommends_theorem_lookup_gate():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A39_PRIVATE_TRIG_PYTHAGOREAN_PROOF_SCOPE_FEASIBILITY_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a38-private-scoped-trig-pythagorean-candidate-packet"
    assert summary["sourceReviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["proofScopeFeasibilityPacketCreated"] is True
    assert summary["candidateScopeReviewed"] is True
    assert summary["selectedProofScopeId"] == SELECTED_PROOF_SCOPE_ID
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a39_recommends_pure_trig_and_defers_eml_companion():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    review = payload["proofScopeFeasibilityReview"]
    assert summary["pureTrigScopeRecommended"] is True
    assert summary["recommendedFutureProofScopeStatement"] == (
        "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1"
    )
    assert summary["recommendedFutureProofScopeGuard"] == "all real x"
    assert summary["emlCompanionDeferred"] is True
    assert summary["deferredCompanionStatement"] == "deferred_no_eml_shape_selected"
    assert summary["deferredCompanionStatus"] == "deferred_context_only_not_rejected_not_disproved_not_equivalence_claim"
    assert review["scopeDecision"] == "prefer_pure_real_trig_statement_for_future_theorem_lookup_gate"


def test_atlas_a39_records_reasons_and_blockers():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    review = payload["proofScopeFeasibilityReview"]
    assert len(review["feasibilityReasons"]) == 3
    assert len(review["blockersBeforeProofSelection"]) == 5
    assert "perform a bounded theorem-lookup gate before naming dependencies" in review[
        "blockersBeforeProofSelection"
    ]
    assert "confirm whether the local import surface exposes the needed sin/cos identity facts" in review[
        "blockersBeforeProofSelection"
    ]
    assert "decide whether future proof notation should remain repeated multiplication or use square notation" in review[
        "blockersBeforeProofSelection"
    ]


def test_atlas_a39_creates_no_lookup_proof_or_validity_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["theoremLookupBlocked"] is True
    assert summary["theoremLookupPerformed"] is False
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


def test_atlas_a39_blocks_edit_lean_public_runtime_and_product_claims():
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


def test_atlas_a39_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 14
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 1
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a39_claim_flags_stay_bounded():
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
        "theorem_lookup_performed",
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


def test_atlas_a39_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A39 Private Trig Pythagorean Proof-Scope Feasibility Packet")
    assert "## Scope Feasibility" in report
    assert "## Feasibility Reasons" in report
    assert "## Blockers Before Proof Selection" in report


def test_atlas_a39_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet.py",
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
    assert "ATLAS_A39_PRIVATE_TRIG_PYTHAGOREAN_PROOF_SCOPE_FEASIBILITY_PACKET_OK" in proc.stdout
