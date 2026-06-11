"""Tests for EML-D11 checked witness surface review."""

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

from scripts.eml_d11_checked_witness_surface_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_d11_consumes_d10_and_records_atlas_gate_witness():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D11_CHECKED_WITNESS_SURFACE_REVIEW_PASS"
    assert payload["sourceWitnessAttempt"] == "eml-d10-machlib-identity-witness-attempt"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["checkedWitnessRecordedInAtlasGate"] is True


def test_d11_keeps_public_promotion_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    public_row = row_by_id(payload, "public_atlas_constants_zero_and_e")
    assert public_row["surfaceStatus"] == "held_private"
    assert "public Atlas promotion" in public_row["blockedClaims"]


def test_d11_does_not_add_advantage_lab_case():
    payload = build_payload(ATLAS_GATE)
    advantage = row_by_id(payload, "advantage_lab_constants_zero_and_e")
    assert advantage["surfaceStatus"] == "not_in_current_case_set"
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["claimFlags"]["advantage_lab_case_added"] is False


def test_d11_records_three_surface_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceRowCount"] == 3
    assert row_by_id(payload, "atlas_promotion_gate_constants_zero_and_e")
    assert row_by_id(payload, "advantage_lab_constants_zero_and_e")
    assert row_by_id(payload, "public_atlas_constants_zero_and_e")


def test_d11_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceUpdated"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["surfaceRows"]:
        assert all(value is False for value in row["claimFlags"].values())


def test_d11_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D11")


def test_d11_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d11_checked_witness_surface_review.py",
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
    assert "EML_D11_CHECKED_WITNESS_SURFACE_REVIEW_OK" in proc.stdout
