"""Tests for EML-D56 expm1 boundary identity feasibility packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d56_expm1_boundary_identity_feasibility_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d56_consumes_d55_candidate_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D56_EXPM1_BOUNDARY_IDENTITY_FEASIBILITY_PASS"
    assert payload["sourceCandidateSelector"] == "eml-d55-bounded-identity-branch-candidate-selector"
    assert payload["summary"]["sourceSelectedCandidateId"] == "expm1_boundary_identity"
    assert payload["summary"]["sourceSelectedFamily"] == "protected_runtime_boundary_identity"


def test_d56_preserves_selected_statement_and_source_frontier():
    payload = build_payload(ATLAS_GATE)
    witness = payload["proposedWitness"]
    assert payload["summary"]["sourceSelectedSourceFrontierId"] == "expm1_failure_boundary_v1"
    assert payload["summary"]["sourceSelectedProposedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["proposedStatement"] == "eml x (exp 1) = exp x - 1"
    assert witness["proposedMachlibName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert witness["proposedStatement"] == "eml x (exp 1) = exp x - 1"
    assert witness["guardShape"] == []


def test_d56_preserves_d53_freeze_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceFrozenWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert payload["summary"]["sourceFrozenStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["sourceFrozenCaveatCount"] == 8
    assert payload["summary"]["sourceFrozenBlockedPhraseCount"] == 10


def test_d56_records_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["feasibilityRecorded"] is True
    assert payload["summary"]["feasibilityStatus"] == "feasible_for_scoped_witness_attempt"
    assert payload["summary"]["guardCount"] == 0
    assert payload["summary"]["noDomainGuardRequired"] is True
    assert payload["summary"]["expectedProofStepCount"] == 3
    assert payload["summary"]["feasibilityItemCount"] == 5
    assert payload["summary"]["blockerCount"] == 4


def test_d56_keeps_runtime_expm1_control_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceRuntimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["runtimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d56_starts_no_machlib_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["nextArtifact"] == "EML-D57 expm1 boundary identity MachLib witness attempt or blocker"


def test_d56_keeps_public_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
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


def test_d56_claim_flags_are_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    for key in [
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "expm1_boundary_candidate_selected",
    ]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {
            "witness_feasibility_recorded",
            "bounded_identity_candidate_selected",
            "expm1_boundary_candidate_selected",
        }:
            assert value is False


def test_d56_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D56")


def test_d56_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d56_expm1_boundary_identity_feasibility_packet.py",
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
    assert "EML_D56_EXPM1_BOUNDARY_IDENTITY_FEASIBILITY_OK" in proc.stdout
