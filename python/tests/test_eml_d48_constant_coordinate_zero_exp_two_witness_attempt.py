"""Tests for EML-D48 constant-coordinate zero-exp-two witness attempt."""

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

from scripts.eml_d48_constant_coordinate_zero_exp_two_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d48_consumes_d47_feasibility_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D48_CONSTANT_COORDINATE_ZERO_EXP_TWO_WITNESS_ATTEMPT_PASS"
    assert payload["sourceFeasibilitySelector"] == "eml-d47-constant-coordinate-refresh-feasibility-selector"
    assert payload["summary"]["sourceSelectedCandidateId"] == "zero_coordinate_exp_two_boundary"
    assert payload["summary"]["sourceSelectedFamily"] == "constant_coordinate_refresh"


def test_d48_records_checked_constant_coordinate_witness():
    payload = build_payload(ATLAS_GATE)
    selected = payload["selectedWitness"]
    assert selected["machlibName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert selected["present"] is True
    assert selected["localStatementPresent"] is True
    assert payload["summary"]["selectedWitnessPresent"] is True
    assert payload["summary"]["scopedWitnessChecked"] is True
    assert payload["summary"]["candidateProved"] is True


def test_d48_bridges_exp_two_to_one_plus_one_local_spelling():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceProposedStatement"] == "eml 0 (exp 2) = -1"
    assert payload["summary"]["checkedLeanStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["localSpellingUsesOnePlusOne"] is True
    assert "0 and 1" in payload["summary"]["localSpellingReason"]
    assert payload["selectedWitness"]["sourceProposedStatement"] == "eml 0 (exp 2) = -1"
    assert payload["selectedWitness"]["checkedLeanStatement"] == "eml 0 (exp (1 + 1)) = -1"


def test_d48_preserves_non_duplicate_boundary():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["existingConstantWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["duplicatesExistingConstantWitness"] is False
    assert payload["summary"]["sourceProposedWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert payload["summary"]["guardCount"] == 0


def test_d48_records_lake_build_pass():
    payload = build_payload(ATLAS_GATE)
    assert payload["verification"]["command"] == "cd ../machlib/foundations && lake build"
    assert payload["verification"]["observedStatus"] == "pass"
    assert payload["summary"]["machlibFileChanged"] is True
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["lakeBuildPassed"] is True
    assert payload["summary"]["implementationStarted"] is True
    assert payload["summary"]["proofAttemptStarted"] is True
    assert payload["summary"]["blockerRecorded"] is False


def test_d48_keeps_runtime_public_trig_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_and_arithmetic_remain_runtime_controls"
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d48_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in [
        "scoped_witness_checked",
        "constant_coordinate_feasibility_recorded",
        "non_duplicate_statement_selected",
        "implementation_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "candidate_proved",
        "proof_attempt_started",
    ]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {
            "scoped_witness_checked",
            "constant_coordinate_feasibility_recorded",
            "non_duplicate_statement_selected",
            "implementation_started",
            "machlib_file_changed",
            "lean_typecheck_performed",
            "candidate_proved",
            "proof_attempt_started",
        }:
            assert value is False


def test_d48_points_to_private_surface_review():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextArtifact"] == "EML-D49 constant-coordinate zero-exp-two private surface review"


def test_d48_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D48")


def test_d48_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d48_constant_coordinate_zero_exp_two_witness_attempt.py",
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
    assert "EML_D48_CONSTANT_COORDINATE_ZERO_EXP_TWO_WITNESS_ATTEMPT_OK" in proc.stdout
