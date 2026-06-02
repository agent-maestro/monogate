"""Tests for EML-D49 constant-coordinate zero-exp-two surface review."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d49_constant_coordinate_zero_exp_two_surface_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_d49_consumes_d48_witness_attempt():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D49_CONSTANT_COORDINATE_ZERO_EXP_TWO_SURFACE_REVIEW_PASS"
    assert payload["sourceWitnessAttempt"] == "eml-d48-constant-coordinate-zero-exp-two-witness-attempt"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"


def test_d49_preserves_source_and_checked_statement_spelling():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceProposedStatement"] == "eml 0 (exp 2) = -1"
    assert payload["summary"]["checkedLeanStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["localSpellingUsesOnePlusOne"] is True
    assert "0 and 1" in payload["summary"]["localSpellingReason"]
    spelling = row_by_id(payload, "constant_coordinate_local_spelling_guardrail")
    assert spelling["surfaceStatus"] == "one_plus_one_spelling_required"


def test_d49_records_five_private_surface_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceRowCount"] == 5
    assert row_by_id(payload, "machlib_witness_index_constant_coordinate_zero_exp_two")["surfaceKind"] == "machlib_private_index"
    assert row_by_id(payload, "constant_coordinate_local_spelling_guardrail")["surfaceKind"] == "local_spelling_guardrail"
    assert row_by_id(payload, "constant_coordinate_non_duplicate_guardrail")["surfaceKind"] == "candidate_boundary"
    assert row_by_id(payload, "advantage_lab_constant_coordinate_zero_exp_two")["surfaceKind"] == "advantage_lab"
    assert row_by_id(payload, "public_atlas_constant_coordinate_zero_exp_two")["surfaceKind"] == "public_surface"


def test_d49_preserves_non_duplicate_boundary():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["existingConstantWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["duplicatesExistingConstantWitness"] is False
    boundary = row_by_id(payload, "constant_coordinate_non_duplicate_guardrail")
    assert boundary["surfaceStatus"] == "non_duplicate_of_d10_constants_bundle"
    assert "D10 relabeling" in boundary["blockedClaims"]


def test_d49_records_checked_witness_privately_without_new_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True
    assert payload["summary"]["candidateProved"] is True
    assert payload["summary"]["guardCount"] == 0
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d49_keeps_public_advantage_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_and_arithmetic_remain_runtime_controls"
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["surfaceUpdated"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d49_claim_flags_are_all_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["surfaceRows"]:
        assert all(value is False for value in row["claimFlags"].values())


def test_d49_points_to_next_selector():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextAction"] == (
        "EML-D50 choose checked-witness copy review, next bounded branch, or human-approved public copy gate without public promotion."
    )


def test_d49_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D49")


def test_d49_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d49_constant_coordinate_zero_exp_two_surface_review.py",
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
    assert "EML_D49_CONSTANT_COORDINATE_ZERO_EXP_TWO_SURFACE_REVIEW_OK" in proc.stdout
