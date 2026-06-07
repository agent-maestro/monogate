"""Tests for ATLAS-A19 private corrected-scope sqrt proof-attempt gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    CORRECTED_ALLOWED_FILE,
    GATE_ID,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a19_consumes_a18_and_creates_corrected_scope_gate():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A19_PRIVATE_CORRECTED_SCOPE_SQRT_PROOF_ATTEMPT_GATE_PASS"
    assert payload["sourceArtifact"] == "atlas-a18-private-sqrt-attempt-scope-correction-selector"
    assert summary["sourceSelectedOptionId"] == "approve_one_off_scope_correction_for_future_attempt"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["gateId"] == GATE_ID
    assert summary["correctedScopeGateCreated"] is True
    assert summary["nextRecommendedArtifact"] == "ATLAS-A20 private corrected-scope sqrt attempt readiness selector"


def test_atlas_a19_records_corrected_scope_budget_route_and_checkpoints():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    gate = payload["correctedScopeGate"]
    assert summary["allowedFiles"] == [CORRECTED_ALLOWED_FILE]
    assert gate["allowedScope"]["allowedFiles"] == [CORRECTED_ALLOWED_FILE]
    assert summary["futureAttemptWallClockLimitMinutes"] == 30
    assert summary["futureLeanRunLimit"] == 1
    assert summary["requiredRouteStepIds"] == [
        "abs_normalization",
        "guard_reduction",
        "eml_boundary_alignment",
    ]
    assert summary["abortConditionCount"] == 6
    assert summary["reviewCheckpointCount"] == 6


def test_atlas_a19_creates_gate_but_no_readiness_selector_or_attempt():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["correctedScopeGateCreated"] is True
    assert summary["readinessSelectorRecommended"] is True
    assert summary["proofAttemptReadinessSelectorCreated"] is False
    assert summary["actualProofAttemptBlocked"] is True
    assert summary["machlibEditBlocked"] is True
    assert summary["leanTypecheckBlocked"] is True
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["leanTypecheckPassed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False


def test_atlas_a19_preserves_runtime_public_product_and_target_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
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


def test_atlas_a19_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
        assert payload["correctedScopeGate"]["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "proof_attempt_readiness_selector_created",
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


def test_atlas_a19_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A19 Private Corrected-Scope Sqrt Proof-Attempt Gate")
    assert "## Corrected Allowed Scope And Budget" in report
    assert "## Required Starting Route" in report
    assert "## Abort Conditions" in report
    assert "## Review Checkpoints" in report


def test_atlas_a19_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate.py",
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
    assert "ATLAS_A19_PRIVATE_CORRECTED_SCOPE_SQRT_PROOF_ATTEMPT_GATE_OK" in proc.stdout
