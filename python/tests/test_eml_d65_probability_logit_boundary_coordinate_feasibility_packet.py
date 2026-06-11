"""Tests for EML-D65 probability logit boundary coordinate feasibility packet."""

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

from scripts.eml_d65_probability_logit_boundary_coordinate_feasibility_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d65_consumes_d64_candidate_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D65_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_FEASIBILITY_PASS"
    assert payload["sourceCandidateSelector"] == "eml-d64-bounded-identity-branch-candidate-selector"
    assert payload["summary"]["sourceSelectedCandidateId"] == "probability_logit_boundary_coordinate"
    assert payload["summary"]["sourceSelectedFamily"] == "guarded_probability_log_coordinate"


def test_d65_preserves_selected_probability_logit_statement():
    payload = build_payload(ATLAS_GATE)
    witness = payload["proposedWitness"]
    assert payload["summary"]["sourceSelectedSourceFrontierId"] == "probability_logit_boundary_v0"
    assert payload["summary"]["sourceSelectedProposedStatement"] == (
        "0 < p and p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert witness["proposedMachlibName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"
    assert witness["proposedStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert witness["guardShape"] == ["0 < p", "p < 1"]


def test_d65_preserves_d62_and_d64_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceFrozenWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert payload["summary"]["sourceFrozenStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["sourceFrozenCaveatCount"] == 8
    assert payload["summary"]["sourceFrozenBlockedPhraseCount"] == 10
    assert payload["summary"]["sourceRuntimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["sourceSelectedNextArtifact"] == "EML-D65 probability logit boundary coordinate feasibility packet"


def test_d65_records_guarded_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["feasibilityRecorded"] is True
    assert payload["summary"]["feasibilityStatus"] == "feasible_for_guarded_scoped_witness_attempt"
    assert payload["summary"]["guardCount"] == 2
    assert payload["summary"]["derivedDomainObligationCount"] == 2
    assert payload["proposedWitness"]["derivedDomainObligations"] == ["0 < p", "0 < 1 - p"]
    assert payload["summary"]["expectedProofStepCount"] == 6
    assert payload["summary"]["feasibilityItemCount"] == 6
    assert payload["summary"]["negativeControlCount"] == 4
    assert payload["summary"]["blockerCount"] == 4


def test_d65_records_boundary_negative_controls():
    payload = build_payload(ATLAS_GATE)
    controls = {item["controlId"]: item for item in payload["negativeControls"]}
    assert controls["p_zero_boundary_blocked"]["status"] == "blocked_by_guard"
    assert controls["p_one_boundary_blocked"]["status"] == "blocked_by_guard"
    assert controls["ungarded_probability_coordinate_blocked"]["status"] == "blocked_by_guard"
    assert controls["runtime_logit_replacement_blocked"]["status"] == "blocked_by_claim_boundary"


def test_d65_keeps_protected_log_controls_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d65_starts_no_machlib_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["nextArtifact"] == "EML-D66 probability logit boundary coordinate MachLib witness attempt or blocker"


def test_d65_keeps_public_laptop_and_electronics_claims_blocked():
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


def test_d65_claim_flags_are_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsFeasibilityOnly"] is True
    for key in [
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "probability_logit_boundary_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
    ]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {
            "witness_feasibility_recorded",
            "bounded_identity_candidate_selected",
            "probability_logit_boundary_candidate_selected",
            "guarded_domain_obligations_recorded",
            "negative_controls_recorded",
        }:
            assert value is False


def test_d65_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D65")


def test_d65_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d65_probability_logit_boundary_coordinate_feasibility_packet.py",
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
    assert "EML_D65_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_FEASIBILITY_OK" in proc.stdout
