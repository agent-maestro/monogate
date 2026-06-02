"""Tests for EML-D57 expm1 boundary identity witness attempt."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d57_expm1_boundary_identity_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d57_consumes_d56_feasibility_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D57_EXPM1_BOUNDARY_IDENTITY_WITNESS_ATTEMPT_PASS"
    assert payload["sourceFeasibilityPacket"] == "eml-d56-expm1-boundary-identity-feasibility-packet"
    assert payload["summary"]["sourceSelectedCandidateId"] == "expm1_boundary_identity"
    assert payload["summary"]["sourceFeasibilityStatus"] == "feasible_for_scoped_witness_attempt"


def test_d57_records_checked_machlib_witness():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["machlibName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["guardCount"] == 0
    assert payload["summary"]["proofStepCount"] == 2
    assert payload["summary"]["buildPassed"] is True


def test_d57_marks_only_scoped_implementation_claims_true():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is True
    assert payload["summary"]["machlibFileChanged"] is True
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["candidateProved"] is True
    assert payload["summary"]["proofAttemptStarted"] is True
    assert payload["summary"]["claimFlagsCheckedOnly"] is True


def test_d57_keeps_runtime_and_public_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["checkedWitness"]["publicPromotionAllowed"] is False


def test_d57_keeps_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False


def test_d57_claim_flags_are_checked_only():
    payload = build_payload(ATLAS_GATE)
    true_keys = {
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "expm1_boundary_candidate_selected",
        "implementation_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "candidate_proved",
        "proof_attempt_started",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_d57_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D57")


def test_d57_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d57_expm1_boundary_identity_witness_attempt.py",
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
    assert "EML_D57_EXPM1_BOUNDARY_IDENTITY_WITNESS_ATTEMPT_OK" in proc.stdout
