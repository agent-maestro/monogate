"""Tests for ATLAS-A18 private sqrt attempt scope correction selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a18_private_sqrt_attempt_scope_correction_selector import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    CORRECTED_ALLOWED_FILE,
    ROOT,
    SELECTED_OPTION_ID,
    STALE_ALLOWED_FILE,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a18_consumes_a17_and_approves_one_off_scope_correction():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A18_PRIVATE_SQRT_ATTEMPT_SCOPE_CORRECTION_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a17-private-bounded-sqrt-proof-attempt-artifact"
    assert summary["sourceBlockerId"] == "allowed_file_missing_in_machlib_checkout"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedDecision"] == "approve_corrected_future_scope_without_editing_machlib"
    assert summary["oneOffScopeCorrectionApproved"] is True
    assert summary["nextRecommendedArtifact"] == "ATLAS-A19 private corrected-scope sqrt proof-attempt gate"


def test_atlas_a18_records_corrected_future_scope_only():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    scope = payload["correctedFutureScope"]
    assert summary["staleAllowedFile"] == STALE_ALLOWED_FILE
    assert summary["correctedAllowedFile"] == CORRECTED_ALLOWED_FILE
    assert summary["correctedAllowedFileExists"] is True
    assert summary["futureAllowedFiles"] == [CORRECTED_ALLOWED_FILE]
    assert summary["futureFileCountLimit"] == 1
    assert summary["futureAttemptWallClockLimitMinutes"] == 30
    assert summary["futureLeanRunLimit"] == 1
    assert scope["scopeCorrectionKind"] == "scope_correction_one_off_due_stale_a13_a16_file_reference"


def test_atlas_a18_decision_criteria_are_narrow():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    criteria = payload["decisionCriteria"]
    assert criteria["observedFileIsCurrentAtlasWitnessHome"] is True
    assert criteria["scopeUpdateReducesFutureConfusion"] is True
    assert criteria["zeroMachLibBehaviorChangeThisPhase"] is True
    assert criteria["staleScopeCreatesFutureMaintenanceCost"] is True


def test_atlas_a18_does_not_apply_correction_or_start_attempt():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["correctedScopeAppliedToMachLib"] is False
    assert summary["correctedAttemptGateCreated"] is False
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


def test_atlas_a18_preserves_runtime_public_product_and_target_blocks():
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


def test_atlas_a18_options_keep_pause_and_parking_available():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    options = {item["optionId"]: item for item in payload["options"]}
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert options["pause_for_atlas_v0_reference_document"]["selectionStatus"] == (
        "available_if_human_prefers_consolidation"
    )
    assert options["park_sqrt_candidate_due_scope_mismatch"]["selectionStatus"] == "not_selected"


def test_atlas_a18_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for option in payload["options"]:
        for key in TRUE_CLAIM_FLAGS:
            assert option["claimFlags"][key] is True
    for blocked in [
        "corrected_scope_applied_to_machlib",
        "corrected_attempt_gate_created",
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


def test_atlas_a18_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A18 Private Sqrt Attempt Scope Correction Selector")
    assert "## Decision Criteria" in report
    assert "## Corrected Future Scope" in report
    assert "## Remaining Blocks" in report


def test_atlas_a18_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a18_private_sqrt_attempt_scope_correction_selector.py",
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
    assert "ATLAS_A18_PRIVATE_SQRT_ATTEMPT_SCOPE_CORRECTION_SELECTOR_OK" in proc.stdout
