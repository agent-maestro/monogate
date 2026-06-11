"""Tests for ATLAS-A46 private Atlas v0 reference document seed."""

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

from scripts.atlas_a46_private_atlas_v0_reference_document_seed import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    PRIVATE_DOC_PATH,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"
ATLAS_A1 = ROOT / "python/results/atlas_a1_private_checked_witness_table/atlas_a1_private_checked_witness_table_2026_06_06.json"


def test_atlas_a46_consumes_a45_and_creates_private_doc_seed():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A46_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_SEED_PASS"
    assert payload["sourceArtifact"] == "atlas-a45-private-atlas-lower-bound-consolidation-selector"
    assert summary["sourceStatus"] == "ATLAS_A45_PRIVATE_ATLAS_LOWER_BOUND_CONSOLIDATION_SELECTOR_PASS"
    assert summary["privateReferenceDocumentSeedCreated"] is True
    assert summary["documentPath"] == PRIVATE_DOC_PATH
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a46_records_fifteen_private_rows_from_a1_and_wrappers():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1)
    summary = payload["summary"]
    rows = payload["atlasRows"]
    assert summary["sourceA1RowCount"] == 13
    assert summary["addedWrapperRowCount"] == 2
    assert summary["atlasRowCount"] == 15
    assert len(rows) == 15
    names = {row["machlibName"] for row in rows}
    assert "MachLib.Real.exp_negation_multiplicative_identity_witness" in names
    assert "MachLib.Real.trig_pythagorean_unit_identity_witness" in names


def test_atlas_a46_preserves_lower_bound_observation_without_completeness_claim():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1)
    summary = payload["summary"]
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is True
    assert summary["additionalArtifactsNeededForLowerBound"] == 0
    assert summary["lowerBoundObservationRecorded"] is True
    assert summary["catalogCompletenessBlocked"] is True
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a46_document_preview_is_private_and_reviewable():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1)
    preview = payload["documentPreview"]
    assert preview.startswith("# Private EML Atlas v0 Reference Seed")
    assert "Status: private seed, not public copy" in preview
    assert "| # | Witness | Family | Guard | Runtime Boundary | Source |" in preview
    assert "MachLib.Real.trig_pythagorean_unit_identity_witness" in preview
    assert "catalog completeness claim: `false`" in preview
    assert "No public Atlas or public math page is created by this seed." in preview


def test_atlas_a46_keeps_public_product_proof_machlib_and_lean_blocks():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1)
    summary = payload["summary"]
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


def test_atlas_a46_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
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


def test_atlas_a46_writes_outputs_and_private_doc(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        tmp_path / "docs" / "private_atlas.md",
        ATLAS_GATE,
        MACHLIB_ROOT,
        ATLAS_A1,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    doc = Path(built["doc_path"]).read_text(encoding="utf-8")
    assert report.startswith("# ATLAS-A46 Private Atlas v0 Reference Document Seed")
    assert "## Seed Rows" in report
    assert doc.startswith("# Private EML Atlas v0 Reference Seed")


def test_atlas_a46_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a46_private_atlas_v0_reference_document_seed.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
            "--machlib-root",
            str(MACHLIB_ROOT),
            "--atlas-a1-path",
            str(ATLAS_A1),
            "--doc-path",
            str(tmp_path / "private_atlas.md"),
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
    assert "ATLAS_A46_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_SEED_OK" in proc.stdout
