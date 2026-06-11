"""Tests for ATLAS-A51 private Atlas reviewer response hold selector."""

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

from scripts.atlas_a51_private_atlas_reviewer_response_hold_selector import (
    CLAIM_FLAGS,
    HOLD_REASONS,
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


def test_atlas_a51_consumes_a50_and_selects_private_hold():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A51_PRIVATE_ATLAS_REVIEWER_RESPONSE_HOLD_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a50-private-atlas-v0-reviewer-handoff-packet"
    assert summary["sourceStatus"] == "ATLAS_A50_PRIVATE_ATLAS_V0_REVIEWER_HANDOFF_PACKET_PASS"
    assert summary["noReviewerResponseRecorded"] is True
    assert summary["privateHoldSelected"] is True
    assert summary["recommendedPath"] == "hold_private_atlas_lane_until_actual_reviewer_response_or_explicit_redirect"
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a51_preserves_rows_and_handoff_visibility():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 15
    assert summary["rowCountPreserved"] is True
    assert summary["atlasRowAdded"] is False
    assert summary["atlasRowRemoved"] is False
    assert summary["rowWordingChanged"] is False
    assert summary["privateReferenceDocumentChanged"] is False
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["additionalArtifactsNeededForLowerBound"] == 0
    assert summary["allowedReviewerActionCount"] >= 4
    assert summary["reviewQuestionCount"] >= 4


def test_atlas_a51_records_hold_reasons_without_response_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    summary = payload["summary"]
    assert summary["holdReasonCount"] == len(HOLD_REASONS)
    assert "No explicit approval, revision request, row-parking request, or hold decision was supplied." in payload["holdReasons"]
    assert summary["privateReviewerResponseConsumed"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert summary["reviewerApprovalClaim"] is False
    assert summary["reviewerRevisionRequestClaim"] is False
    assert summary["reviewerHoldDecisionClaim"] is False


def test_atlas_a51_keeps_public_product_proof_machlib_and_lean_blocks():
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
    assert summary["runtimeReplacementClaim"] is False
    assert summary["d110Started"] is False


def test_atlas_a51_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT, ATLAS_A1, DOC_PATH)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "atlas_row_added",
        "atlas_row_removed",
        "row_wording_changed",
        "private_reference_document_changed",
        "private_reviewer_response_consumed",
        "reviewer_approval_claim",
        "reviewer_revision_request_claim",
        "reviewer_hold_decision_claim",
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
        "runtime_replacement_claim",
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


def test_atlas_a51_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A51 Private Atlas Reviewer Response Hold Selector")
    assert "## Hold Reasons" in report
    assert "A50 handoff is not reviewer approval" in report


def test_atlas_a51_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a51_private_atlas_reviewer_response_hold_selector.py",
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
    assert "ATLAS_A51_PRIVATE_ATLAS_REVIEWER_RESPONSE_HOLD_SELECTOR_OK" in proc.stdout
