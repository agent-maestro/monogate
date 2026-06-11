"""Tests for ATLAS-A43 private trig pythagorean bounded wrapper attempt artifact."""

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

from scripts.atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact import (
    CLAIM_FLAGS,
    DEPENDENCY_IDENTIFIER,
    MACHLIB_FILE,
    MACHLIB_NAME,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SOURCE_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a43_consumes_a42_and_records_checked_wrapper():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A43_PRIVATE_TRIG_PYTHAGOREAN_BOUNDED_WRAPPER_ATTEMPT_ARTIFACT_PASS"
    assert payload["sourceArtifact"] == "atlas-a42-private-trig-pythagorean-wrapper-or-alias-attempt-gate"
    assert summary["sourceReviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["boundedWrapperAttemptArtifactCreated"] is True
    assert summary["wrapperAttemptStarted"] is True
    assert summary["wrapperAttemptCompleted"] is True
    assert summary["checkedWrapperWitnessRecorded"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a43_records_machlib_witness_and_dependency():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    checked = payload["checkedWrapperWitness"]
    assert summary["machlibName"] == MACHLIB_NAME
    assert summary["machlibFile"] == MACHLIB_FILE
    assert summary["checkedStatement"] == (
        "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1"
    )
    assert summary["dependencyIdentifier"] == DEPENDENCY_IDENTIFIER
    assert summary["dependencyIdentifierUsed"] is True
    assert summary["namespaceCorrectionRecorded"] is True
    assert checked["dependencyIdentifier"] == DEPENDENCY_IDENTIFIER


def test_atlas_a43_records_one_file_one_build_bounds():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    checked = payload["checkedWrapperWitness"]
    bounds = checked["attemptBounds"]
    assert bounds["allowedFiles"] == [MACHLIB_FILE]
    assert bounds["changedFiles"] == [MACHLIB_FILE]
    assert bounds["leanCheckCount"] == 1
    assert bounds["proofScopeBroadened"] is False
    assert payload["summary"]["additionalMachlibFileChanged"] is False
    assert payload["summary"]["additionalLeanCheckPerformed"] is False
    assert payload["summary"]["proofScopeBroadened"] is False


def test_atlas_a43_records_build_pass_and_warnings():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    checked = payload["checkedWrapperWitness"]
    assert summary["machlibFileChanged"] is True
    assert summary["leanTypecheckPerformed"] is True
    assert summary["leanTypecheckPassed"] is True
    assert summary["candidateProved"] is True
    assert summary["candidateProvedThisPhase"] is True
    assert checked["buildCommand"] == "cd foundations && lake build"
    assert checked["buildStatus"] == "passed"
    assert len(checked["knownUnrelatedWarnings"]) == 3


def test_atlas_a43_preserves_eml_runtime_public_and_product_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["emlCompanionKeptDeferred"] is True
    assert summary["deferredCompanionStatement"] == "deferred_no_eml_shape_selected"
    assert summary["runtimeControl"] == "standard_trig_functions_remain_runtime_controls"
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeExpReplacementClaim"] is False
    assert summary["runtimeTrigReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a43_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["sourceAtlasRowCount"] == 14
    assert summary["atlasRowCount"] == 15
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is True
    assert summary["targetLowerBoundReachedObserved"] is True
    assert summary["additionalArtifactsNeededForLowerBound"] == 0
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a43_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "alias_attempt_started",
        "candidate_rejected",
        "candidate_disproved",
        "proof_scope_broadened",
        "additional_machlib_file_changed",
        "additional_lean_check_performed",
        "runtime_lowering_changed",
        "runtime_exp_replacement_claim",
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
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "formal_equivalence_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a43_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A43 Private Trig Pythagorean Bounded Wrapper Attempt Artifact")
    assert "## Proof Shape" in report
    assert "## Attempt Bounds" in report
    assert "## Known Unrelated Build Warnings" in report


def test_atlas_a43_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact.py",
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
    assert "ATLAS_A43_PRIVATE_TRIG_PYTHAGOREAN_BOUNDED_WRAPPER_ATTEMPT_ARTIFACT_OK" in proc.stdout
