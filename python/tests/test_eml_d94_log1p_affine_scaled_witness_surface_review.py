"""Tests for EML-D94 log1p affine-scaled witness surface review."""

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

from scripts.eml_d94_log1p_affine_scaled_witness_surface_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_d94_consumes_d93_witness_attempt():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D94_LOG1P_AFFINE_SCALED_WITNESS_SURFACE_REVIEW_PASS"
    assert payload["sourceWitnessAttempt"] == "eml-d93-log1p-affine-scaled-boundary-coordinate-witness-attempt"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness"


def test_d94_preserves_checked_statement_guard_runtime_and_duplicate_block():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["checkedStatement"] == "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["sourceDuplicateShiftedBlocksPreserved"] is True
    assert payload["summary"]["duplicateShiftedBlocksPreserved"] is True
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    runtime = row_by_id(payload, "log1p_affine_scaled_runtime_control_guardrail")
    assert runtime["surfaceStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert "log1p replacement" in runtime["blockedClaims"]


def test_d94_records_five_private_surface_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceRowCount"] == 5
    assert row_by_id(payload, "machlib_witness_index_log1p_affine_scaled_boundary")["surfaceKind"] == "machlib_private_index"
    assert row_by_id(payload, "log1p_affine_scaled_guard_boundary")["surfaceKind"] == "candidate_boundary"
    assert row_by_id(payload, "log1p_affine_scaled_runtime_control_guardrail")["surfaceKind"] == "runtime_control_guardrail"
    assert row_by_id(payload, "advantage_lab_log1p_affine_scaled_boundary")["surfaceKind"] == "advantage_lab"
    assert row_by_id(payload, "public_atlas_log1p_affine_scaled_boundary")["surfaceKind"] == "public_surface"


def test_d94_preserves_d92_negative_controls_and_blockers():
    payload = build_payload(ATLAS_GATE)
    boundary = row_by_id(payload, "log1p_affine_scaled_guard_boundary")
    assert payload["summary"]["sourceNegativeControlCount"] == 5
    assert payload["summary"]["sourceBlockerCount"] == 5
    assert boundary["surfaceStatus"] == "affine_scaled_positive_domain_boundary_required"
    assert "1 + a * x <= 0 boundary" in boundary["blockedClaims"]
    assert "duplicate shifted-coordinate reuse" in boundary["blockedClaims"]
    assert "broad log1p-family claim" in boundary["blockedClaims"]
    assert "missing affine guard" in " ".join(boundary["rationale"])


def test_d94_records_checked_witness_privately_without_new_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True
    assert payload["summary"]["candidateProved"] is True
    assert payload["summary"]["buildPassed"] is True
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d94_keeps_public_reviewer_advantage_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["surfaceUpdated"] is False
    assert payload["summary"]["privateReviewerResponseIntakeSelected"] is False
    assert payload["summary"]["reviewerDecisionRecorded"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d94_claim_flags_are_all_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["surfaceRows"]:
        assert all(value is False for value in row["claimFlags"].values())


def test_d94_points_to_next_selector():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextAction"] == (
        "EML-D95 choose log1p affine-scaled checked-witness copy review, next bounded branch, private reviewer response intake, or human-approved public copy gate without public promotion."
    )


def test_d94_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D94")


def test_d94_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d94_log1p_affine_scaled_witness_surface_review.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
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
    assert "EML_D94_LOG1P_AFFINE_SCALED_WITNESS_SURFACE_REVIEW_OK" in proc.stdout
