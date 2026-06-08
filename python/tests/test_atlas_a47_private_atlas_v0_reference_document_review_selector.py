"""Tests for ATLAS-A47 private Atlas v0 reference document review selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a47_private_atlas_v0_reference_document_review_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_REVIEW_PATH_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)
from scripts import atlas_a46_private_atlas_v0_reference_document_seed as a46

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"
ATLAS_A1 = ROOT / "python/results/atlas_a1_private_checked_witness_table/atlas_a1_private_checked_witness_table_2026_06_06.json"
DOC_PATH = ROOT / a46.PRIVATE_DOC_PATH


def review_by_id(payload, review_id: str):
    return next(item for item in payload["reviewRows"] if item["reviewId"] == review_id)


def test_atlas_a47_consumes_a46_and_recommends_private_revision():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A47_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_REVIEW_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a46-private-atlas-v0-reference-document-seed"
    assert summary["sourceStatus"] == "ATLAS_A46_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_SEED_PASS"
    assert summary["selectedReviewPathId"] == SELECTED_REVIEW_PATH_ID
    assert summary["selectedDecision"] == "recommend_private_row_wording_revision_packet"
    assert summary["privateRowWordingRevisionRecommended"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a47_records_five_review_rows():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    assert payload["summary"]["reviewRowCount"] == 5
    assert review_by_id(payload, "row_count_and_source_integrity")["status"] == "reviewed_ok"
    assert review_by_id(payload, "non_claim_boundary")["status"] == "reviewed_ok"
    assert review_by_id(payload, "row_wording_readability")["status"] == "private_revision_recommended"
    assert review_by_id(payload, "public_surface_path")["status"] == "held"
    assert review_by_id(payload, "proof_and_runtime_path")["status"] == "held"


def test_atlas_a47_preserves_document_and_lower_bound_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    summary = payload["summary"]
    assert summary["privateReferenceDocumentInspected"] is True
    assert summary["documentPath"] == a46.PRIVATE_DOC_PATH
    assert summary["documentChanged"] is False
    assert summary["atlasRowAdded"] is False
    assert summary["atlasRowRemoved"] is False
    assert summary["atlasRowCount"] == 15
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is True
    assert summary["additionalArtifactsNeededForLowerBound"] == 0


def test_atlas_a47_keeps_public_product_proof_machlib_and_lean_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    summary = payload["summary"]
    assert summary["catalogCompletenessBlocked"] is True
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False
    assert summary["productImplementationStarted"] is False
    assert summary["newCandidatePacketCreated"] is False
    assert summary["feasibilityPacketCreated"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False


def test_atlas_a47_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for row in payload["reviewRows"]:
        for key in TRUE_CLAIM_FLAGS:
            assert row["claimFlags"][key] is True
        for key, value in row["claimFlags"].items():
            if key not in TRUE_CLAIM_FLAGS:
                assert value is False
    for blocked in [
        "document_changed",
        "atlas_row_added",
        "atlas_row_removed",
        "public_atlas_promotion",
        "public_copy_approved",
        "public_surface_updated",
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


def test_atlas_a47_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
        MACHLIB_ROOT,
        ATLAS_A1,
        DOC_PATH,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# ATLAS-A47 Private Atlas v0 Reference Document Review Selector")
    assert "## Review Rows" in report
    assert "## Blocked Follow-Ups" in report


def test_atlas_a47_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a47_private_atlas_v0_reference_document_review_selector.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
            "--machlib-root",
            str(MACHLIB_ROOT),
            "--atlas-a1-path",
            str(ATLAS_A1),
            "--doc-path",
            str(DOC_PATH),
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
    assert "ATLAS_A47_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_REVIEW_SELECTOR_OK" in proc.stdout
