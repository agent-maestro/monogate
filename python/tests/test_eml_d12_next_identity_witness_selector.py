"""Tests for EML-D12 next identity witness selector."""

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

from scripts.eml_d12_next_identity_witness_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def selector_by_id(payload, candidate_id: str):
    return next(item for item in payload["candidateSelectors"] if item["candidateId"] == candidate_id)


def test_d12_consumes_d11_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D12_NEXT_IDENTITY_WITNESS_SELECTOR_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d11-checked-witness-surface-review"
    assert payload["summary"]["constantsWitnessAlreadyChecked"] is True


def test_d12_selects_ln_from_eml_as_next_target():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedCandidateId"] == "ln_from_eml_boundary_v1"
    assert payload["summary"]["selectedProofTarget"] == "MachLib.Real.ln_from_eml_boundary_witness"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D13 ln-from-EML MachLib witness attempt"
    assert payload["selectedCandidate"]["selectionStatus"] == "selected_next"


def test_d12_records_three_remaining_candidates():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["candidateCount"] == 3
    assert selector_by_id(payload, "ln_from_eml_boundary_v1")
    assert selector_by_id(payload, "subtraction_boundary_family_v1")
    assert selector_by_id(payload, "prime_signature_log_recovery_v2")


def test_d12_keeps_subtraction_and_prime_for_later():
    payload = build_payload(ATLAS_GATE)
    assert selector_by_id(payload, "subtraction_boundary_family_v1")["selectionStatus"] == "candidate_later"
    assert selector_by_id(payload, "prime_signature_log_recovery_v2")["selectionStatus"] == "candidate_later"
    assert selector_by_id(payload, "subtraction_boundary_family_v1")["atlasProofStatus"] == "checked_machlib_witness_available"
    assert selector_by_id(payload, "prime_signature_log_recovery_v2")["atlasProofStatus"] == "candidate_machlib_witness"


def test_d12_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for selector in payload["candidateSelectors"]:
        assert all(value is False for value in selector["claimFlags"].values())


def test_d12_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D12")


def test_d12_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d12_next_identity_witness_selector.py",
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
    assert "EML_D12_NEXT_IDENTITY_WITNESS_SELECTOR_OK" in proc.stdout
