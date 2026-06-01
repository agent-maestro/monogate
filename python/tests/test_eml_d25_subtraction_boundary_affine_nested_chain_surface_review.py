"""Tests for EML-D25 affine-nested subtraction-boundary surface review."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d25_subtraction_boundary_affine_nested_chain_surface_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_d25_consumes_d24_and_records_private_witness():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D25_SUBTRACTION_BOUNDARY_AFFINE_NESTED_CHAIN_SURFACE_REVIEW_PASS"
    assert payload["sourceWitnessAttempt"] == "eml-d24-subtraction-boundary-affine-nested-chain-witness-attempt"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.subtraction_boundary_affine_nested_chain_witness"
    assert payload["summary"]["selectedOptionId"] == "affine_nested_chain_witness_attempt"
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True


def test_d25_records_four_surface_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceRowCount"] == 4
    assert row_by_id(payload, "machlib_witness_index_subtraction_boundary_affine_nested_chain")
    assert row_by_id(payload, "nested_subtraction_family_guardrail_affine_nested_chain")
    assert row_by_id(payload, "advantage_lab_subtraction_boundary_affine_nested_chain")
    assert row_by_id(payload, "public_atlas_subtraction_boundary_affine_nested_chain")


def test_d25_preserves_nested_guardrails_and_parked_options():
    payload = build_payload(ATLAS_GATE)
    guardrail = row_by_id(payload, "nested_subtraction_family_guardrail_affine_nested_chain")
    assert payload["summary"]["negativeControlBlockedBySelector"] is True
    assert payload["summary"]["twoStageWitnessRecordedPrivately"] is True
    assert payload["summary"]["deeperChainPreviouslyParked"] is True
    assert payload["summary"]["threeStageChainStillParked"] is True
    assert payload["summary"]["checkedWitnessCopyReviewStillParked"] is True
    assert payload["summary"]["familyPauseStillParked"] is True
    assert guardrail["surfaceStatus"] == "scoped_affine_nested_instance_only"
    assert "broad nested subtraction family" in guardrail["blockedClaims"]


def test_d25_keeps_standard_subtraction_runtime_control():
    payload = build_payload(ATLAS_GATE)
    advantage = row_by_id(payload, "advantage_lab_subtraction_boundary_affine_nested_chain")
    assert advantage["surfaceStatus"] == "runtime_control_remains_standard_subtraction"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["claimFlags"]["runtime_lowering_changed"] is False


def test_d25_keeps_public_surfaces_blocked():
    payload = build_payload(ATLAS_GATE)
    public_row = row_by_id(payload, "public_atlas_subtraction_boundary_affine_nested_chain")
    assert public_row["surfaceStatus"] == "held_private"
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    assert payload["summary"]["surfaceUpdated"] is False
    assert "public Atlas promotion" in public_row["blockedClaims"]


def test_d25_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["surfaceRows"]:
        assert all(value is False for value in row["claimFlags"].values())


def test_d25_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D25")


def test_d25_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d25_subtraction_boundary_affine_nested_chain_surface_review.py",
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
    assert "EML_D25_SUBTRACTION_BOUNDARY_AFFINE_NESTED_CHAIN_SURFACE_REVIEW_OK" in proc.stdout
