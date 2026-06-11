"""Tests for ATLAS-A48 private Atlas v0 row wording revision packet."""

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

from scripts.atlas_a48_private_atlas_v0_row_wording_revision_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
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


def test_atlas_a48_consumes_a47_and_records_wording_revision():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A48_PRIVATE_ATLAS_V0_ROW_WORDING_REVISION_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a47-private-atlas-v0-reference-document-review-selector"
    assert summary["sourceStatus"] == "ATLAS_A47_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_REVIEW_SELECTOR_PASS"
    assert summary["privateReferenceDocumentRevised"] is True
    assert summary["rowWordingRevised"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a48_preserves_rows_and_lower_bound_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 15
    assert summary["rowCountPreserved"] is True
    assert summary["atlasRowAdded"] is False
    assert summary["atlasRowRemoved"] is False
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is True
    assert summary["additionalArtifactsNeededForLowerBound"] == 0


def test_atlas_a48_revised_document_uses_human_readable_runtime_wording():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    summary = payload["summary"]
    doc = DOC_PATH.read_text(encoding="utf-8")
    assert summary["revisedPhraseCount"] >= 4
    assert summary["staleInternalRuntimePhraseCount"] == 0
    assert "standard log/exp remains the runtime control" in doc
    assert "protected `log` and `log1p` remain the runtime controls" in doc
    assert "all real inputs; no extra guard" in doc
    assert "standard_trig_functions_remain_runtime_controls" not in doc


def test_atlas_a48_keeps_public_product_proof_machlib_and_lean_blocks():
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


def test_atlas_a48_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
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


def test_atlas_a48_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A48 Private Atlas v0 Row Wording Revision Packet")
    assert "## Revised Wording Signals" in report
    assert "## Blocked Follow-Ups" in report


def test_atlas_a48_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a48_private_atlas_v0_row_wording_revision_packet.py",
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
    assert "ATLAS_A48_PRIVATE_ATLAS_V0_ROW_WORDING_REVISION_PACKET_OK" in proc.stdout
