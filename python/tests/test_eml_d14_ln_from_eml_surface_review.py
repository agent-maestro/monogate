"""Tests for EML-D14 ln-from-EML surface review."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d14_ln_from_eml_surface_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_d14_consumes_d13_and_records_atlas_gate_witness():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D14_LN_FROM_EML_SURFACE_REVIEW_PASS"
    assert payload["sourceWitnessAttempt"] == "eml-d13-ln-from-eml-witness-attempt"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.ln_from_eml_boundary_witness"
    assert payload["summary"]["selectedCandidateId"] == "ln_from_eml_boundary_v1"
    assert payload["summary"]["checkedWitnessRecordedInAtlasGate"] is True


def test_d14_keeps_public_promotion_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    public_row = row_by_id(payload, "public_atlas_ln_from_eml")
    assert public_row["surfaceStatus"] == "held_private"
    assert "public Atlas promotion" in public_row["blockedClaims"]


def test_d14_keeps_standard_log_runtime_control():
    payload = build_payload(ATLAS_GATE)
    advantage = row_by_id(payload, "advantage_lab_ln_from_eml")
    assert advantage["surfaceStatus"] == "runtime_control_remains_standard_log"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_remains_runtime_control"
    assert payload["claimFlags"]["runtime_lowering_changed"] is False


def test_d14_records_three_surface_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceRowCount"] == 3
    assert row_by_id(payload, "atlas_promotion_gate_ln_from_eml")
    assert row_by_id(payload, "advantage_lab_ln_from_eml")
    assert row_by_id(payload, "public_atlas_ln_from_eml")


def test_d14_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceUpdated"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["surfaceRows"]:
        assert all(value is False for value in row["claimFlags"].values())


def test_d14_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D14")


def test_d14_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d14_ln_from_eml_surface_review.py",
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
    assert "EML_D14_LN_FROM_EML_SURFACE_REVIEW_OK" in proc.stdout
