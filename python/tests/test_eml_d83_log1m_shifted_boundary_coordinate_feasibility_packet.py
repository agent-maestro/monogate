"""Tests for EML-D83 log1m shifted boundary coordinate feasibility packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d83_log1m_shifted_boundary_coordinate_feasibility_packet import (
    CLAIM_FLAGS,
    NEXT_ARTIFACT,
    PROPOSED_MACHLIB_NAME,
    PROPOSED_STATEMENT,
    ROOT,
    SELECTED_CANDIDATE_ID,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d83_consumes_d82_selected_log1m_candidate():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D83_LOG1M_SHIFTED_BOUNDARY_COORDINATE_FEASIBILITY_PASS"
    assert payload["sourceCandidateSelector"] == "eml-d82-bounded-identity-branch-candidate-selector"
    assert summary["sourceSelectedCandidateId"] == SELECTED_CANDIDATE_ID
    assert summary["sourceSelectedFamily"] == "guarded_log1m_shifted_coordinate"
    assert summary["sourceSelectedNextArtifact"] == "EML-D83 log1m shifted boundary coordinate feasibility packet"


def test_d83_records_proposed_witness_and_guarded_statement():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    witness = payload["proposedWitness"]
    assert summary["proposedMachlibName"] == PROPOSED_MACHLIB_NAME
    assert witness["proposedMachlibName"] == PROPOSED_MACHLIB_NAME
    assert summary["proposedStatement"] == PROPOSED_STATEMENT
    assert witness["proposedStatement"] == PROPOSED_STATEMENT
    assert witness["guardShape"] == ["0 < 1 - x"]
    assert witness["derivedDomainObligations"] == ["0 < 1 - x", "0 < exp 1"]
    assert summary["guardCount"] == 1
    assert summary["derivedDomainObligationCount"] == 2


def test_d83_preserves_d82_duplicate_log1p_block():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["blockedDuplicateCandidateId"] == "log1p_shifted_boundary_coordinate"
    assert summary["blockedDuplicateStatus"] == "blocked_duplicate_checked_witness"
    assert summary["blockedDuplicateCheckedWitnesses"] == ["MachLib.Real.log1p_shifted_boundary_coordinate_witness"]
    assert summary["duplicateLog1pBlockPreserved"] is True


def test_d83_preserves_d80_and_act_boundaries():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceD80FrozenWitnessName"] == "MachLib.Real.log1p_shifted_boundary_coordinate_witness"
    assert summary["sourceD80FrozenCheckedStatement"] == "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x"
    assert summary["sourceD80FrozenGuards"] == ["0 < 1 + x"]
    assert summary["sourceActHandoffReady"] is True
    assert summary["sourceActReviewerDecisionRecorded"] is False
    assert summary["sourceActPromotionAllowed"] is False


def test_d83_records_feasibility_items_negative_controls_and_blockers():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["feasibilityRecorded"] is True
    assert summary["feasibilityStatus"] == "feasible_for_guarded_scoped_witness_attempt"
    assert summary["expectedProofStepCount"] == 6
    assert summary["feasibilityItemCount"] == 6
    assert summary["negativeControlCount"] == 4
    assert summary["blockerCount"] == 4
    assert all(item["status"] == "satisfied" for item in payload["feasibilityItems"])
    assert {item["status"] for item in payload["negativeControls"]} <= {
        "blocked_by_guard",
        "blocked_by_claim_boundary",
    }


def test_d83_expected_proof_shape_is_guarded_log1m_only():
    payload = build_payload(ATLAS_GATE)
    steps = payload["proposedWitness"]["expectedProofShape"]
    assert steps[0] == "introduce guard 0 < 1 - x"
    assert "rewrite exp (log (1 - x)) to 1 - x under the guard" in steps
    assert "normalize (1 - x) - 1 to -x" in steps
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"


def test_d83_starts_no_proof_machlib_runtime_public_or_laptop_work():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["implementationStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["candidateProved"] is False
    assert summary["candidateProvedThisPhase"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["protectedLogReplacementClaim"] is False
    assert summary["protectedLog1pReplacementClaim"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicPromotionPerformed"] is False
    assert summary["privateReviewerResponseIntakeSelected"] is False
    assert summary["electronicsRepoTouched"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False


def test_d83_points_to_d84_witness_attempt_or_blocker():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextArtifact"] == NEXT_ARTIFACT
    assert payload["proposedWitness"]["nextArtifact"] == NEXT_ARTIFACT


def test_d83_claim_flags_are_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsFeasibilityOnly"] is True
    true_keys = {
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "log1m_shifted_boundary_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
        "duplicate_log1p_block_preserved",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_d83_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D83")


def test_d83_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d83_log1m_shifted_boundary_coordinate_feasibility_packet.py",
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
    assert "EML_D83_LOG1M_SHIFTED_BOUNDARY_COORDINATE_FEASIBILITY_OK" in proc.stdout
