"""Tests for ATLAS-A45 private Atlas lower-bound consolidation selector."""

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

from scripts.atlas_a45_private_atlas_lower_bound_consolidation_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_PATH_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def path_by_id(payload, path_id: str):
    return next(item for item in payload["consolidationPaths"] if item["pathId"] == path_id)


def test_atlas_a45_consumes_a44_and_selects_private_atlas_v0_seed():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A45_PRIVATE_ATLAS_LOWER_BOUND_CONSOLIDATION_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a44-private-trig-pythagorean-checked-wrapper-surface-review"
    assert summary["sourceStatus"] == "ATLAS_A44_PRIVATE_TRIG_PYTHAGOREAN_CHECKED_WRAPPER_SURFACE_REVIEW_PASS"
    assert summary["selectedPathId"] == SELECTED_PATH_ID
    assert summary["selectedDecision"] == "seed_private_atlas_v0_reference_document"
    assert summary["privateAtlasV0SeedSelected"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a45_reviews_four_consolidation_paths():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    assert payload["summary"]["pathCount"] == 4
    assert path_by_id(payload, "private_atlas_v0_reference_document_seed")["selectionStatus"] == "selected"
    assert path_by_id(payload, "continue_new_bounded_proof_branch")["selectionStatus"] == "deferred"
    assert path_by_id(payload, "public_witness_promotion")["selectionStatus"] == "held"
    assert path_by_id(payload, "product_or_course_extraction")["selectionStatus"] == "held"
    assert payload["summary"]["moreProofBranchingDeferred"] is True


def test_atlas_a45_preserves_lower_bound_observation_without_completeness_claim():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["sourceAtlasRowCount"] == 15
    assert summary["atlasRowCount"] == 15
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is True
    assert summary["additionalArtifactsNeededForLowerBound"] == 0
    assert summary["lowerBoundObservationConsumed"] is True
    assert summary["catalogCompletenessBlocked"] is True
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a45_creates_no_document_packet_proof_machlib_or_lean_work():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasDocumentCreated"] is False
    assert summary["newCandidatePacketCreated"] is False
    assert summary["feasibilityPacketCreated"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["theoremLookupPerformed"] is False


def test_atlas_a45_keeps_public_runtime_product_and_review_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeTrigReplacementClaim"] is False
    assert summary["runtimeExpReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False
    assert summary["productImplementationStarted"] is False
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False


def test_atlas_a45_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for path in payload["consolidationPaths"]:
        for key in TRUE_CLAIM_FLAGS:
            assert path["claimFlags"][key] is True
        for key, value in path["claimFlags"].items():
            if key not in TRUE_CLAIM_FLAGS:
                assert value is False
    for blocked in [
        "atlas_document_created",
        "public_atlas_promotion",
        "public_copy_approved",
        "sdk_compiler_docs_created",
        "course_material_created",
        "new_candidate_packet_created",
        "candidate_validity_claim",
        "proof_attempt_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "theorem_lookup_performed",
        "runtime_lowering_changed",
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


def test_atlas_a45_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A45 Private Atlas Lower-Bound Consolidation Selector")
    assert "## Consolidation Paths" in report
    assert "## Blocked Follow-Ups" in report


def test_atlas_a45_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a45_private_atlas_lower_bound_consolidation_selector.py",
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
    assert "ATLAS_A45_PRIVATE_ATLAS_LOWER_BOUND_CONSOLIDATION_SELECTOR_OK" in proc.stdout
