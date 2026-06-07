"""Tests for ATLAS-A21 private corrected-scope bounded sqrt attempt artifact."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact import (
    BLOCKER_ID,
    CANDIDATE_ID,
    CLAIM_FLAGS,
    CORRECTED_ALLOWED_FILE,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a21_consumes_a20_and_records_blocked_attempt_artifact():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A21_PRIVATE_CORRECTED_SCOPE_BOUNDED_SQRT_ATTEMPT_ARTIFACT_BLOCKED"
    assert payload["sourceArtifact"] == "atlas-a20-private-corrected-scope-sqrt-attempt-readiness-selector"
    assert summary["sourceSelectedOptionId"] == "recommend_future_corrected_scope_bounded_attempt_artifact"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["boundedAttemptArtifactCreated"] is True
    assert summary["attemptStatus"] == "blocked_before_patch_due_eml_definition_alignment"
    assert summary["blockerId"] == BLOCKER_ID
    assert summary["nextRecommendedArtifact"] == "ATLAS-A22 private sqrt candidate reframe-or-park selector"


def test_atlas_a21_preflights_corrected_file_and_reviews_target_statements():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    review = payload["attemptReview"]
    assert summary["correctedAllowedFilePreflightPerformed"] is True
    assert summary["allowedFiles"] == [CORRECTED_ALLOWED_FILE]
    assert summary["allowedFileExists"] is True
    assert summary["targetStatementAlignmentReviewed"] is True
    assert [item["statementId"] for item in review["targetStatementsReviewed"]] == [
        "abs_normalization",
        "guard_reduction",
        "eml_boundary_alignment",
    ]
    assert review["targetStatementsReviewed"][2]["status"] == "blocked_before_patch"


def test_atlas_a21_records_eml_definition_alignment_blocker():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    review = payload["attemptReview"]
    assert summary["emlDefinitionAlignmentBlockerRecorded"] is True
    assert review["blocker"]["blockerId"] == BLOCKER_ID
    assert review["blocker"]["status"] == "blocks_patch_before_machlib_edit"
    assert "eml a b := exp a - log b" in review["targetStatementsReviewed"][2]["note"]
    assert len(review["futureSafeOptions"]) == 3


def test_atlas_a21_aborts_before_edit_lean_and_theorem_lookup():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["attemptAbortedBeforeEdit"] is True
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
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


def test_atlas_a21_preserves_runtime_public_product_target_and_reframe_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["sqrtCandidateParked"] is False
    assert summary["sqrtCandidateReframed"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a21_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "candidate_selected_for_proof",
        "candidate_validity_claim",
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
        "sqrt_candidate_parked",
        "sqrt_candidate_reframed",
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


def test_atlas_a21_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A21 Private Corrected-Scope Bounded Sqrt Attempt Artifact")
    assert "## Target Statement Review" in report
    assert "## Precise Blocker" in report
    assert "## Future Safe Options" in report


def test_atlas_a21_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact.py",
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
    assert "ATLAS_A21_PRIVATE_CORRECTED_SCOPE_BOUNDED_SQRT_ATTEMPT_ARTIFACT_OK" in proc.stdout
