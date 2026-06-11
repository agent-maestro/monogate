"""Tests for EML-D15 checked-witness next decision."""

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

from scripts.eml_d15_checked_witness_next_decision import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d15_consumes_d14_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D15_CHECKED_WITNESS_NEXT_DECISION_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d14-ln-from-eml-surface-review"
    assert payload["summary"]["checkedLnFromEmlSurfaceRecorded"] is True


def test_d15_selects_subtraction_boundary_family_selector():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedOptionId"] == "return_to_identity_selector_subtraction_boundary_family_v1"
    assert payload["summary"]["selectedCandidateId"] == "subtraction_boundary_family_v1"
    assert payload["summary"]["selectedProofTarget"] == "MachLib.Real.subtraction_boundary_family_generalization_witness"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D16 subtraction-boundary family witness selector"
    assert payload["selectedOption"]["selectionStatus"] == "selected_next"


def test_d15_parks_copy_review_and_prime_signature():
    payload = build_payload(ATLAS_GATE)
    copy_review = option_by_id(payload, "checked_witness_copy_review_packet")
    prime = option_by_id(payload, "prime_signature_log_recovery_feasibility_selector")
    assert copy_review["selectionStatus"] == "candidate_later"
    assert prime["selectionStatus"] == "candidate_later"
    assert "human wording review required" in copy_review["blockers"]
    assert "avoid RH/zeta implication leakage" in prime["blockers"]


def test_d15_does_not_start_copy_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStarted"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False


def test_d15_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for option in payload["decisionOptions"]:
        assert all(value is False for value in option["claimFlags"].values())


def test_d15_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D15")


def test_d15_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d15_checked_witness_next_decision.py",
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
    assert "EML_D15_CHECKED_WITNESS_NEXT_DECISION_OK" in proc.stdout
