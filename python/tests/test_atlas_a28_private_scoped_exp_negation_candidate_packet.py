"""Tests for ATLAS-A28 private scoped exp-negation candidate packet."""

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

from scripts.atlas_a28_private_scoped_exp_negation_candidate_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_SCOPE_ID,
    SOURCE_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a28_consumes_a27_and_creates_scoped_candidate_packet():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A28_PRIVATE_SCOPED_EXP_NEGATION_CANDIDATE_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a27-private-exp-negation-candidate-packet-selector"
    assert summary["sourceReviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["sourceSelectedDecision"] == "recommend_scoped_candidate_packet_without_creating_it"
    assert summary["candidatePacketCreated"] is True
    assert summary["selectedScopeId"] == SELECTED_SCOPE_ID
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a28_records_guard_and_statement_shapes():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    candidate = payload["candidatePacket"]
    assert summary["guard"] == "all real x"
    assert summary["allRealGuardRecorded"] is True
    assert summary["pureCandidateStatementRecorded"] is True
    assert summary["pureCandidateStatement"] == "forall x : Real, Real.exp x * Real.exp (-x) = 1"
    assert summary["pureCandidateValidityStatus"] == "not_checked_not_proved_not_selected_for_proof"
    assert summary["emlCompanionHintRecorded"] is True
    assert summary["emlCompanionHint"] == "eml (x + (-x)) 1 = 1"
    assert summary["emlCompanionValidityStatus"] == "not_checked_not_proved_not_formal_equivalence_claim"
    assert candidate["statements"]["pureExpStatement"]["sourceHint"] == "exp x * exp (-x) = 1"
    assert candidate["statements"]["emlCompanionHint"]["sourceHint"] == "eml (x + (-x)) 1 = 1"


def test_atlas_a28_records_review_value_and_blockers():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    candidate = payload["candidatePacket"]
    assert len(candidate["reviewValue"]) == 3
    assert len(candidate["blockersBeforeProofSelection"]) == 4
    assert "perform theorem lookup before naming any Lean theorem dependency" in candidate["blockersBeforeProofSelection"]
    assert "check exact local notation and import surface before any MachLib edit" in candidate[
        "blockersBeforeProofSelection"
    ]


def test_atlas_a28_creates_no_proof_or_validity_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateRejected"] is False
    assert summary["candidateDisproved"] is False
    assert summary["candidateProved"] is False
    assert summary["proofScopeFeasibilityPerformed"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False
    assert summary["checkedWitnessClaim"] is False


def test_atlas_a28_blocks_edit_lean_theorem_public_runtime_and_product_claims():
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


def test_atlas_a28_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a28_claim_flags_stay_bounded():
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
        "proof_scope_feasibility_performed",
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
        "checked_witness_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "formal_equivalence_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a28_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A28 Private Scoped Exp-Negation Candidate Packet")
    assert "## Candidate Statements" in report
    assert "## Review Value" in report
    assert "## Blockers Before Proof Selection" in report


def test_atlas_a28_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a28_private_scoped_exp_negation_candidate_packet.py",
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
    assert "ATLAS_A28_PRIVATE_SCOPED_EXP_NEGATION_CANDIDATE_PACKET_OK" in proc.stdout
