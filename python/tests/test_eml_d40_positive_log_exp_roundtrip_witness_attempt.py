"""Tests for EML-D40 positive log-exp roundtrip witness attempt."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d40_positive_log_exp_roundtrip_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d40_consumes_d39_feasibility_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D40_POSITIVE_LOG_EXP_ROUNDTRIP_WITNESS_ATTEMPT_PASS"
    assert payload["sourceFeasibilityPacket"] == "eml-d39-positive-log-exp-roundtrip-feasibility-packet"
    assert payload["summary"]["sourceSelectedCandidateId"] == "positive_log_exp_roundtrip_identity"
    assert payload["summary"]["sourceSelectedFamily"] == "positive_domain_log_exp_roundtrip"


def test_d40_records_checked_positive_log_exp_witness():
    payload = build_payload(ATLAS_GATE)
    selected = payload["selectedWitness"]
    assert selected["machlibName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert selected["present"] is True
    assert selected["guardShape"] == ["0 < x"]
    assert selected["proofSketch"] == "exact exp_log hx"
    assert payload["summary"]["selectedWitnessPresent"] is True
    assert payload["summary"]["scopedWitnessChecked"] is True
    assert payload["summary"]["candidateProved"] is True


def test_d40_preserves_guarded_statement():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["proposedStatement"] == "0 < x -> exp (log x) = x"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["positiveDomainGuardRequired"] is True


def test_d40_records_lake_build_pass():
    payload = build_payload(ATLAS_GATE)
    assert payload["verification"]["command"] == "cd ../machlib/foundations && lake build"
    assert payload["verification"]["observedStatus"] == "pass"
    assert payload["summary"]["machlibFileChanged"] is True
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["lakeBuildPassed"] is True
    assert payload["summary"]["implementationStarted"] is True
    assert payload["summary"]["proofAttemptStarted"] is True


def test_d40_keeps_runtime_log_exp_and_public_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_remains_runtime_control"
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicReady"] is False


def test_d40_keeps_course_and_laptop_work_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_d40_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in [
        "scoped_witness_checked",
        "witness_feasibility_recorded",
        "bounded_identity_branch_selected",
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
            "witness_feasibility_recorded",
            "bounded_identity_branch_selected",
            "implementation_started",
            "machlib_file_changed",
            "lean_typecheck_performed",
            "candidate_proved",
            "proof_attempt_started",
        }:
            assert value is False


def test_d40_points_to_private_surface_review():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextArtifact"] == "EML-D41 positive log-exp witness private surface review"


def test_d40_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D40")


def test_d40_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d40_positive_log_exp_roundtrip_witness_attempt.py",
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
    assert "EML_D40_POSITIVE_LOG_EXP_ROUNDTRIP_WITNESS_ATTEMPT_OK" in proc.stdout
