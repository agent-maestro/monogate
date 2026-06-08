"""Tests for ATLAS-A34 private exp-negation checked-wrapper surface review."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a34_private_exp_negation_checked_wrapper_surface_review import (
    CLAIM_FLAGS,
    DEPENDENCY_IDENTIFIER,
    MACHLIB_FILE,
    MACHLIB_NAME,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_atlas_a34_consumes_a33_surface():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    assert payload["status"] == "ATLAS_A34_PRIVATE_EXP_NEGATION_CHECKED_WRAPPER_SURFACE_REVIEW_PASS"
    assert payload["sourceArtifact"] == "atlas-a33-private-exp-negation-bounded-wrapper-attempt-artifact"
    assert payload["summary"]["sourceStatus"] == "ATLAS_A33_PRIVATE_EXP_NEGATION_BOUNDED_WRAPPER_ATTEMPT_ARTIFACT_PASS"


def test_atlas_a34_reviews_checked_wrapper_metadata():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["machlibName"] == MACHLIB_NAME
    assert summary["machlibFile"] == MACHLIB_FILE
    assert summary["checkedStatement"] == "forall x : Real, Real.exp x * Real.exp (-x) = 1"
    assert summary["dependencyIdentifier"] == DEPENDENCY_IDENTIFIER
    assert summary["sourceLeanTypecheckPassed"] is True
    assert summary["sourceCandidateProvedThisPhase"] is True
    assert summary["surfaceReviewCreated"] is True
    assert summary["checkedWrapperSurfaceReviewed"] is True
    assert summary["privateAtlasRowReviewed"] is True


def test_atlas_a34_records_five_surface_rows():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    assert payload["summary"]["surfaceRowCount"] == 5
    assert row_by_id(payload, "private_atlas_row_exp_negation_wrapper")["surfaceKind"] == "private_atlas_row"
    assert row_by_id(payload, "dependency_namespace_correction")["surfaceKind"] == "proof_dependency_boundary"
    assert row_by_id(payload, "eml_companion_deferred_boundary")["surfaceKind"] == "eml_companion_boundary"
    assert row_by_id(payload, "runtime_control_guardrail")["surfaceKind"] == "runtime_control_guardrail"
    assert row_by_id(payload, "public_surface_guardrail")["surfaceKind"] == "public_surface"


def test_atlas_a34_records_namespace_and_companion_boundaries():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    dependency = row_by_id(payload, "dependency_namespace_correction")
    companion = row_by_id(payload, "eml_companion_deferred_boundary")
    assert dependency["surfaceStatus"] == "corrected_dependency_identifier_recorded"
    assert "stale dependency namespace" in dependency["blockedClaims"]
    assert "MachLib.HyperbolicPreservation" in " ".join(dependency["rationale"])
    assert companion["surfaceStatus"] == "companion_hint_deferred"
    assert "formal EML equivalence" in companion["blockedClaims"]
    assert payload["summary"]["deferredCompanionStatement"] == "eml (x + (-x)) 1 = 1"


def test_atlas_a34_keeps_no_new_proof_or_machlib_work():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["candidateProvedThisPhase"] is False
    assert summary["proofAttemptStarted"] is False


def test_atlas_a34_keeps_public_runtime_product_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeExpReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False


def test_atlas_a34_preserves_target_accounting_and_next_selector():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 14
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 1
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a34_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for row in payload["surfaceRows"]:
        for key in TRUE_CLAIM_FLAGS:
            assert row["claimFlags"][key] is True
        for key, value in row["claimFlags"].items():
            if key not in TRUE_CLAIM_FLAGS:
                assert value is False
    for blocked in [
        "machlib_file_changed",
        "lean_typecheck_performed",
        "candidate_proved_this_phase",
        "proof_attempt_started",
        "runtime_lowering_changed",
        "runtime_exp_replacement_claim",
        "public_atlas_promotion",
        "public_copy_approved",
        "public_surface_updated",
        "sdk_compiler_docs_created",
        "course_material_created",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "catalog_completeness_claim",
        "target_lower_bound_reached_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "formal_equivalence_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a34_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A34 Private Exp-Negation Checked-Wrapper Surface Review")
    assert "## Surface Rows" in report
    assert "## Blocked Follow-Ups" in report


def test_atlas_a34_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a34_private_exp_negation_checked_wrapper_surface_review.py",
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
    assert "ATLAS_A34_PRIVATE_EXP_NEGATION_CHECKED_WRAPPER_SURFACE_REVIEW_OK" in proc.stdout
