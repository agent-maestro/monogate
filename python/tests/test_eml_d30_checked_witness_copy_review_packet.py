"""Tests for EML-D30 checked-witness copy review packet."""

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

from scripts.eml_d30_checked_witness_copy_review_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, witness_id: str):
    return next(item for item in payload["witnessCopyRows"] if item["witnessId"] == witness_id)


def test_d30_consumes_d29_and_starts_private_copy_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D30_CHECKED_WITNESS_COPY_REVIEW_PACKET_PASS"
    assert payload["sourceDecision"] == "eml-d29-nested-family-next-branch-decision"
    assert payload["summary"]["selectedOptionId"] == "checked_witness_copy_review_packet"
    assert payload["summary"]["copyReviewStarted"] is True
    assert payload["summary"]["privateCopyReviewOnly"] is True


def test_d30_records_six_checked_witness_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["witnessRowCount"] == 6
    assert row_by_id(payload, "constants_zero_one_e_boundary")
    assert row_by_id(payload, "ln_from_eml_boundary")
    assert row_by_id(payload, "subtraction_boundary_affine_offset")
    assert row_by_id(payload, "subtraction_boundary_two_stage_chain")
    assert row_by_id(payload, "subtraction_boundary_affine_nested_chain")
    assert row_by_id(payload, "subtraction_boundary_three_stage_chain")


def test_d30_requires_guard_and_runtime_caveats():
    payload = build_payload(ATLAS_GATE)
    ln_row = row_by_id(payload, "ln_from_eml_boundary")
    three_stage = row_by_id(payload, "subtraction_boundary_three_stage_chain")
    assert "Always name the 0 < y guard." in ln_row["requiredCaveats"]
    assert "Always name 0 < a, 0 < b, and 0 < c." in three_stage["requiredCaveats"]
    assert ln_row["runtimeControl"] == "standard log(y) remains runtime control"
    assert three_stage["runtimeControl"] == "standard subtraction remains runtime control"


def test_d30_blocks_risky_public_or_broad_phrases():
    payload = build_payload(ATLAS_GATE)
    assert "theorem discovery" in payload["blockedGlobalPhrases"]
    assert "broad nested subtraction family" in payload["blockedGlobalPhrases"]
    affine = row_by_id(payload, "subtraction_boundary_affine_nested_chain")
    three_stage = row_by_id(payload, "subtraction_boundary_three_stage_chain")
    assert "nested subtraction family solved" in affine["blockedPhrases"]
    assert "arbitrary-depth nested theorem" in three_stage["blockedPhrases"]


def test_d30_keeps_public_surfaces_and_advantage_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsPublicFalse"] is True


def test_d30_keeps_broad_family_and_runtime_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["familyPauseStillParked"] is True
    assert payload["summary"]["newBranchSelectionStillParked"] is True


def test_d30_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    assert CLAIM_FLAGS["copy_review_started"] is True
    assert CLAIM_FLAGS["private_copy_review_only"] is True
    assert payload["claimFlags"]["copy_review_started"] is True
    assert payload["claimFlags"]["private_copy_review_only"] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only"}:
            assert value is False
    assert all(row["publicPromotionAllowed"] is False for row in payload["witnessCopyRows"])


def test_d30_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D30")


def test_d30_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d30_checked_witness_copy_review_packet.py",
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
    assert "EML_D30_CHECKED_WITNESS_COPY_REVIEW_PACKET_OK" in proc.stdout
