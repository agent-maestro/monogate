"""Tests for EML-D41 positive log-exp witness surface review."""

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

from scripts.eml_d41_positive_log_exp_witness_surface_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_d41_consumes_d40_and_records_private_witness():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D41_POSITIVE_LOG_EXP_WITNESS_SURFACE_REVIEW_PASS"
    assert payload["sourceWitnessAttempt"] == "eml-d40-positive-log-exp-roundtrip-witness-attempt"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert payload["summary"]["sourceSelectedCandidateId"] == "positive_log_exp_roundtrip_identity"
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True


def test_d41_records_four_surface_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceRowCount"] == 4
    assert row_by_id(payload, "machlib_witness_index_positive_log_exp_roundtrip")
    assert row_by_id(payload, "positive_domain_log_exp_guardrail")
    assert row_by_id(payload, "advantage_lab_positive_log_exp_roundtrip")
    assert row_by_id(payload, "public_atlas_positive_log_exp_roundtrip")


def test_d41_preserves_positive_domain_guardrail():
    payload = build_payload(ATLAS_GATE)
    guardrail = row_by_id(payload, "positive_domain_log_exp_guardrail")
    assert payload["summary"]["positiveDomainGuardRequired"] is True
    assert payload["summary"]["guardCount"] == 1
    assert guardrail["surfaceStatus"] == "scoped_positive_domain_identity_only"
    assert "unguarded log-domain use" in guardrail["blockedClaims"]


def test_d41_keeps_standard_log_exp_runtime_control():
    payload = build_payload(ATLAS_GATE)
    advantage = row_by_id(payload, "advantage_lab_positive_log_exp_roundtrip")
    assert advantage["surfaceStatus"] == "runtime_control_remains_standard_log_exp"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_remains_runtime_control"
    assert payload["claimFlags"]["runtime_lowering_changed"] is False
    assert payload["claimFlags"]["log_exp_replacement_claim"] is False


def test_d41_keeps_public_surfaces_blocked():
    payload = build_payload(ATLAS_GATE)
    public_row = row_by_id(payload, "public_atlas_positive_log_exp_roundtrip")
    assert public_row["surfaceStatus"] == "held_private"
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    assert payload["summary"]["surfaceUpdated"] is False
    assert "public Atlas promotion" in public_row["blockedClaims"]


def test_d41_keeps_laptop_and_electronics_work_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_d41_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["surfaceRows"]:
        assert all(value is False for value in row["claimFlags"].values())


def test_d41_points_to_next_branch_choice():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextAction"] == (
        "EML-D42 choose next bounded identity branch, private copy review, or pause without public promotion."
    )


def test_d41_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D41")


def test_d41_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d41_positive_log_exp_witness_surface_review.py",
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
    assert "EML_D41_POSITIVE_LOG_EXP_WITNESS_SURFACE_REVIEW_OK" in proc.stdout
