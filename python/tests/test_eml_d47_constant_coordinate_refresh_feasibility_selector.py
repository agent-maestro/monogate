"""Tests for EML-D47 constant-coordinate refresh feasibility selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d47_constant_coordinate_refresh_feasibility_selector import (
    CLAIM_FLAGS,
    EXISTING_CONSTANT_WITNESS_STATEMENTS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d47_consumes_d46_constant_coordinate_selection():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D47_CONSTANT_COORDINATE_REFRESH_FEASIBILITY_SELECTOR_PASS"
    assert payload["sourceSelector"] == "eml-d46-post-positive-log-exp-pause-next-selector"
    assert payload["summary"]["sourceSelectedOptionId"] == "constant_coordinate_refresh_selector"
    assert payload["summary"]["d46ConstantCoordinateRefreshSelected"] is True


def test_d47_preserves_d46_frozen_log_exp_context():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["d46FrozenWitnessName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert payload["summary"]["d46FrozenCheckedStatement"] == "0 < x -> exp (log x) = x"
    assert payload["summary"]["d46PublicHoldPreserved"] is True


def test_d47_selects_non_duplicate_zero_exp_two_statement():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "select_zero_coordinate_exp_two_boundary_feasibility"
    assert payload["summary"]["selectedCandidateId"] == "zero_coordinate_exp_two_boundary"
    assert payload["summary"]["selectedFamily"] == "constant_coordinate_refresh"
    assert payload["summary"]["selectedProposedStatement"] == "eml 0 (exp 2) = -1"
    assert payload["summary"]["selectedProposedWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert payload["summary"]["selectedDuplicateStatus"] == "non_duplicate_of_constants_zero_one_e_boundary_witness"
    assert payload["summary"]["nonDuplicateStatementSelected"] is True
    assert payload["summary"]["duplicatesExistingConstantWitness"] is False


def test_d47_names_existing_constants_witness_to_avoid_duplication():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["existingConstantWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["existingConstantWitnessStatementCount"] == 3
    assert EXISTING_CONSTANT_WITNESS_STATEMENTS == [
        "eml 0 (exp 1) = 0",
        "eml 0 1 = 1",
        "eml 1 1 = exp 1",
    ]
    assert payload["summary"]["selectedProposedStatement"] not in EXISTING_CONSTANT_WITNESS_STATEMENTS


def test_d47_is_feasibility_only_before_witness_attempt():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["feasibilitySelectorStarted"] is True
    assert payload["summary"]["constantCoordinateCandidateSelected"] is True
    assert payload["summary"]["selectedNextArtifact"] == (
        "EML-D48 constant-coordinate zero-exp-two witness attempt or blocker packet"
    )
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d47_keeps_public_trig_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_and_arithmetic_remain_runtime_controls"
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d47_claim_flags_are_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsFeasibilityOnly"] is True
    for key in [
        "feasibility_selector_started",
        "constant_coordinate_candidate_selected",
        "non_duplicate_statement_selected",
    ]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {
            "feasibility_selector_started",
            "constant_coordinate_candidate_selected",
            "non_duplicate_statement_selected",
        }:
            assert value is False
    for row in payload["candidateRows"]:
        for key, value in row["claimFlags"].items():
            if key not in {
                "feasibility_selector_started",
                "constant_coordinate_candidate_selected",
                "non_duplicate_statement_selected",
            }:
                assert value is False


def test_d47_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D47")


def test_d47_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d47_constant_coordinate_refresh_feasibility_selector.py",
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
    assert "EML_D47_CONSTANT_COORDINATE_REFRESH_FEASIBILITY_SELECTOR_OK" in proc.stdout
