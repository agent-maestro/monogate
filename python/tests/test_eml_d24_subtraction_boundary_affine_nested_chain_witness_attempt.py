"""Tests for EML-D24 affine-nested subtraction-boundary witness attempt."""

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

from scripts.eml_d24_subtraction_boundary_affine_nested_chain_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d24_consumes_d23_branch_decision():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D24_SUBTRACTION_BOUNDARY_AFFINE_NESTED_CHAIN_WITNESS_ATTEMPT_PASS"
    assert payload["sourceBranchDecision"] == "eml-d23-nested-family-next-branch-decision"
    assert payload["summary"]["selectedOptionId"] == "affine_nested_chain_witness_attempt"


def test_d24_records_checked_affine_nested_witness():
    payload = build_payload(ATLAS_GATE)
    selected = payload["selectedWitness"]
    assert selected["machlibName"] == "MachLib.Real.subtraction_boundary_affine_nested_chain_witness"
    assert selected["present"] is True
    assert payload["summary"]["selectedWitnessPresent"] is True
    assert payload["summary"]["scopedWitnessChecked"] is True


def test_d24_records_lake_build_pass():
    payload = build_payload(ATLAS_GATE)
    assert payload["verification"]["observedStatus"] == "pass"
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["lakeBuildPassed"] is True
    assert payload["summary"]["machlibFileChanged"] is True


def test_d24_preserves_d23_guardrails():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["negativeControlBlockedBySelector"] is True
    assert payload["summary"]["twoStageWitnessRecordedPrivately"] is True
    assert payload["summary"]["deeperChainPreviouslyParked"] is True
    assert payload["summary"]["copyReviewStarted"] is False


def test_d24_keeps_broad_nested_and_runtime_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"


def test_d24_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert payload["summary"]["theoremDiscoveryClaim"] is False
    assert payload["summary"]["publicReady"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_d24_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D24")


def test_d24_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d24_subtraction_boundary_affine_nested_chain_witness_attempt.py",
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
    assert "EML_D24_SUBTRACTION_BOUNDARY_AFFINE_NESTED_CHAIN_WITNESS_ATTEMPT_OK" in proc.stdout
