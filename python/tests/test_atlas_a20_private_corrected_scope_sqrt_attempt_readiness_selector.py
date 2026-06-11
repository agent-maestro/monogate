"""Tests for ATLAS-A20 private corrected-scope sqrt attempt readiness selector."""

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

from scripts.atlas_a20_private_corrected_scope_sqrt_attempt_readiness_selector import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    CORRECTED_ALLOWED_FILE,
    GATE_ID,
    ROOT,
    SELECTED_OPTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a20_consumes_a19_and_recommends_future_attempt_artifact():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A20_PRIVATE_CORRECTED_SCOPE_SQRT_ATTEMPT_READINESS_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a19-private-corrected-scope-sqrt-proof-attempt-gate"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["gateId"] == GATE_ID
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedDecision"] == "recommend_corrected_scope_attempt_artifact_without_starting_attempt"
    assert summary["nextRecommendedArtifact"] == "ATLAS-A21 private corrected-scope bounded sqrt attempt artifact"


def test_atlas_a20_reviews_corrected_gate_scope_budget_and_aborts():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["correctedScopeReadinessSelectorCreated"] is True
    assert summary["correctedGateReviewed"] is True
    assert summary["correctedScopeBudgetReviewed"] is True
    assert summary["abortConditionsReviewed"] is True
    assert summary["allowedFiles"] == [CORRECTED_ALLOWED_FILE]
    assert summary["futureAttemptWallClockLimitMinutes"] == 30
    assert summary["futureLeanRunLimit"] == 1
    assert summary["abortConditionCount"] == 6
    assert summary["reviewCheckpointCount"] == 6


def test_atlas_a20_recommends_future_attempt_but_starts_no_attempt():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["futureCorrectedScopeAttemptRecommended"] is True
    assert summary["boundedAttemptArtifactCreated"] is False
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


def test_atlas_a20_options_keep_pause_and_parking_available():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    options = {item["optionId"]: item for item in payload["options"]}
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert options["pause_for_atlas_v0_reference_document"]["selectionStatus"] == (
        "available_if_human_prefers_consolidation"
    )
    assert options["park_sqrt_candidate_before_corrected_scope_attempt"]["selectionStatus"] == "not_selected"


def test_atlas_a20_preserves_runtime_public_product_and_target_blocks():
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


def test_atlas_a20_claim_flags_stay_bounded():
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
        "bounded_attempt_artifact_created",
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


def test_atlas_a20_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A20 Private Corrected-Scope Sqrt Attempt Readiness Selector")
    assert "## Readiness Reasons" in report
    assert "## Remaining Blocks" in report
    assert "## Options" in report


def test_atlas_a20_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a20_private_corrected_scope_sqrt_attempt_readiness_selector.py",
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
    assert "ATLAS_A20_PRIVATE_CORRECTED_SCOPE_SQRT_ATTEMPT_READINESS_SELECTOR_OK" in proc.stdout
