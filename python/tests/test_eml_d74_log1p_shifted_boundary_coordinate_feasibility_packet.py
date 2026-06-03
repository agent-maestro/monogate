"""Tests for EML-D74 log1p shifted boundary coordinate feasibility packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d74_log1p_shifted_boundary_coordinate_feasibility_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d74_consumes_d73_candidate_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D74_LOG1P_SHIFTED_BOUNDARY_COORDINATE_FEASIBILITY_PASS"
    assert payload["sourceCandidateSelector"] == "eml-d73-bounded-identity-branch-candidate-selector"
    assert payload["summary"]["sourceSelectedCandidateId"] == "log1p_shifted_boundary_coordinate"
    assert payload["summary"]["sourceSelectedFamily"] == "guarded_log1p_shifted_coordinate"


def test_d74_preserves_selected_log1p_shifted_statement():
    payload = build_payload(ATLAS_GATE)
    witness = payload["proposedWitness"]
    assert payload["summary"]["sourceSelectedSourceFrontierId"] == "post_probability_logit_pause_identity_lane"
    assert payload["summary"]["sourceSelectedProposedStatement"] == (
        "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x"
    )
    assert witness["proposedMachlibName"] == "MachLib.Real.log1p_shifted_boundary_coordinate_witness"
    assert witness["proposedStatement"] == "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x"
    assert witness["guardShape"] == ["0 < 1 + x"]


def test_d74_preserves_d71_and_d73_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceFrozenWitnessName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"
    assert payload["summary"]["sourceFrozenStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert payload["summary"]["sourceFrozenGuardCount"] == 2
    assert payload["summary"]["sourceFrozenCaveatCount"] == 9
    assert payload["summary"]["sourceFrozenBlockedPhraseCount"] == 12
    assert payload["summary"]["sourceRuntimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["sourceSelectedNextArtifact"] == "EML-D74 log1p shifted boundary coordinate feasibility packet"


def test_d74_records_guarded_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["feasibilityRecorded"] is True
    assert payload["summary"]["feasibilityStatus"] == "feasible_for_guarded_scoped_witness_attempt"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["derivedDomainObligationCount"] == 2
    assert payload["proposedWitness"]["derivedDomainObligations"] == ["0 < 1 + x", "0 < exp 1"]
    assert payload["summary"]["expectedProofStepCount"] == 6
    assert payload["summary"]["feasibilityItemCount"] == 6
    assert payload["summary"]["negativeControlCount"] == 4
    assert payload["summary"]["blockerCount"] == 4


def test_d74_records_shifted_boundary_negative_controls():
    payload = build_payload(ATLAS_GATE)
    controls = {item["controlId"]: item for item in payload["negativeControls"]}
    assert controls["x_minus_one_boundary_blocked"]["status"] == "blocked_by_guard"
    assert controls["x_below_minus_one_blocked"]["status"] == "blocked_by_guard"
    assert controls["unguarded_log1p_shifted_coordinate_blocked"]["status"] == "blocked_by_guard"
    assert controls["runtime_log1p_replacement_blocked"]["status"] == "blocked_by_claim_boundary"


def test_d74_keeps_protected_log_controls_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d74_starts_no_machlib_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["nextArtifact"] == "EML-D75 log1p shifted boundary coordinate MachLib witness attempt or blocker"


def test_d74_keeps_public_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d74_claim_flags_are_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsFeasibilityOnly"] is True
    for key in [
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "log1p_shifted_boundary_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
    ]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {
            "witness_feasibility_recorded",
            "bounded_identity_candidate_selected",
            "log1p_shifted_boundary_candidate_selected",
            "guarded_domain_obligations_recorded",
            "negative_controls_recorded",
        }:
            assert value is False


def test_d74_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D74")


def test_d74_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d74_log1p_shifted_boundary_coordinate_feasibility_packet.py",
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
    assert "EML_D74_LOG1P_SHIFTED_BOUNDARY_COORDINATE_FEASIBILITY_OK" in proc.stdout
