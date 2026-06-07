"""Tests for ATLAS-A17 private bounded sqrt proof-attempt artifact."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a17_private_bounded_sqrt_proof_attempt_artifact import (
    BLOCKER_ID,
    CANDIDATE_ID,
    CLAIM_FLAGS,
    EXPECTED_ALLOWED_FILE,
    OBSERVED_WITNESS_FILE,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a17_consumes_a16_and_records_blocked_attempt_artifact():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A17_PRIVATE_BOUNDED_SQRT_PROOF_ATTEMPT_ARTIFACT_BLOCKED"
    assert payload["sourceArtifact"] == "atlas-a16-private-sqrt-proof-attempt-open-selector"
    assert summary["sourceSelectedOptionId"] == "recommend_future_bounded_sqrt_proof_attempt_artifact"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["boundedProofAttemptArtifactCreated"] is True
    assert summary["attemptStatus"] == "blocked_before_edit_due_allowed_file_missing"
    assert summary["blockerId"] == BLOCKER_ID
    assert summary["nextRecommendedArtifact"] == "ATLAS-A18 private sqrt attempt scope correction selector"


def test_atlas_a17_preflights_allowed_file_and_records_mismatch():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    preflight = payload["attemptPreflight"]
    assert summary["allowedFilePreflightPerformed"] is True
    assert summary["allowedFiles"] == [EXPECTED_ALLOWED_FILE]
    assert summary["allowedFilesExist"] is False
    assert preflight["checkedAllowedFiles"][0]["allowedFile"] == EXPECTED_ALLOWED_FILE
    assert preflight["checkedAllowedFiles"][0]["exists"] is False
    assert summary["observedLikelyWitnessFile"] == OBSERVED_WITNESS_FILE
    assert summary["observedLikelyWitnessFileExists"] is True


def test_atlas_a17_aborts_before_edit_and_does_not_correct_scope():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["attemptAbortedBeforeEdit"] is True
    assert summary["scopeCorrectedThisPhase"] is False
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


def test_atlas_a17_preserves_runtime_public_and_product_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a17_preserves_target_gap():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a17_claim_flags_stay_bounded():
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
        "scope_corrected_this_phase",
        "runtime_lowering_changed",
        "runtime_sqrt_replacement_claim",
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


def test_atlas_a17_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A17 Private Bounded Sqrt Proof-Attempt Artifact")
    assert "## Allowed-File Preflight" in report
    assert "## Precise Blocker" in report
    assert "## Why This Aborts Instead Of Correcting Scope" in report


def test_atlas_a17_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a17_private_bounded_sqrt_proof_attempt_artifact.py",
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
    assert "ATLAS_A17_PRIVATE_BOUNDED_SQRT_PROOF_ATTEMPT_ARTIFACT_OK" in proc.stdout
