"""Tests for EML-D92 log1p affine-scaled boundary coordinate feasibility packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet import (
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


def test_d92_consumes_d91_selected_affine_scaled_candidate():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D92_LOG1P_AFFINE_SCALED_BOUNDARY_COORDINATE_FEASIBILITY_PASS"
    assert payload["sourceCandidateSelector"] == "eml-d91-bounded-identity-branch-candidate-selector"
    assert summary["sourceSelectedCandidateId"] == SELECTED_CANDIDATE_ID
    assert summary["sourceSelectedFamily"] == "guarded_log1p_affine_scaled_coordinate"
    assert summary["sourceSelectedNextArtifact"] == "EML-D92 log1p affine-scaled boundary coordinate feasibility packet"


def test_d92_records_proposed_witness_and_guarded_statement():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    witness = payload["proposedWitness"]
    assert summary["proposedMachlibName"] == PROPOSED_MACHLIB_NAME
    assert witness["proposedMachlibName"] == PROPOSED_MACHLIB_NAME
    assert summary["proposedStatement"] == PROPOSED_STATEMENT
    assert witness["proposedStatement"] == PROPOSED_STATEMENT
    assert witness["guardShape"] == ["0 < 1 + a * x"]
    assert witness["derivedDomainObligations"] == ["0 < 1 + a * x", "0 < exp 1"]
    assert summary["guardCount"] == 1
    assert summary["derivedDomainObligationCount"] == 2


def test_d92_preserves_d91_duplicate_shifted_blocks():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["blockedDuplicateCandidateIds"] == [
        "log1p_shifted_boundary_coordinate",
        "log1m_shifted_boundary_coordinate",
    ]
    assert summary["blockedDuplicateStatuses"] == [
        "blocked_duplicate_checked_witness",
        "blocked_duplicate_checked_witness",
    ]
    assert summary["blockedDuplicateCheckedWitnesses"] == [
        "MachLib.Real.log1p_shifted_boundary_coordinate_witness",
        "MachLib.Real.log1m_shifted_boundary_coordinate_witness",
    ]
    assert summary["duplicateShiftedBlocksPreserved"] is True


def test_d92_preserves_d90_and_act_boundaries():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceFrozenWitnessName"] == "MachLib.Real.log1m_shifted_boundary_coordinate_witness"
    assert summary["sourceFrozenCheckedStatement"] == "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x"
    assert summary["sourceFrozenGuards"] == ["0 < 1 - x"]
    assert summary["sourceActHandoffReady"] is True
    assert summary["sourceActReviewerDecisionRecorded"] is False
    assert summary["sourceActPromotionAllowed"] is False


def test_d92_records_feasibility_items_negative_controls_and_blockers():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["feasibilityRecorded"] is True
    assert summary["feasibilityStatus"] == "feasible_for_guarded_scoped_witness_attempt"
    assert summary["expectedProofStepCount"] == 6
    assert summary["feasibilityItemCount"] == 7
    assert summary["negativeControlCount"] == 5
    assert summary["blockerCount"] == 5
    assert all(item["status"] == "satisfied" for item in payload["feasibilityItems"])
    assert {item["status"] for item in payload["negativeControls"]} <= {
        "blocked_by_guard",
        "blocked_by_claim_boundary",
        "blocked_by_duplicate_boundary",
    }


def test_d92_expected_proof_shape_is_affine_scaled_guarded_only():
    payload = build_payload(ATLAS_GATE)
    steps = payload["proposedWitness"]["expectedProofShape"]
    assert steps[0] == "introduce guard 0 < 1 + a * x"
    assert "rewrite exp (log (1 + a * x)) to 1 + a * x under the guard" in steps
    assert "normalize (1 + a * x) - 1 to a * x" in steps
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"


def test_d92_records_affine_specific_negative_controls():
    payload = build_payload(ATLAS_GATE)
    controls = {item["controlId"]: item for item in payload["negativeControls"]}
    assert controls["affine_shift_zero_boundary_blocked"]["status"] == "blocked_by_guard"
    assert controls["affine_shift_negative_boundary_blocked"]["status"] == "blocked_by_guard"
    assert controls["unguarded_affine_scaled_coordinate_blocked"]["status"] == "blocked_by_guard"
    assert controls["a_equals_one_duplicate_collapse_blocked_as_fresh_claim"]["status"] == (
        "blocked_by_duplicate_boundary"
    )
    assert controls["runtime_log1p_replacement_blocked"]["status"] == "blocked_by_claim_boundary"


def test_d92_starts_no_proof_machlib_runtime_public_or_laptop_work():
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


def test_d92_points_to_d93_witness_attempt_or_blocker():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextArtifact"] == NEXT_ARTIFACT
    assert payload["proposedWitness"]["nextArtifact"] == NEXT_ARTIFACT


def test_d92_claim_flags_are_feasibility_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsFeasibilityOnly"] is True
    true_keys = {
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "log1p_affine_scaled_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
        "duplicate_shifted_blocks_preserved",
        "source_d91_selector_observed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_d92_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D92")


def test_d92_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet.py",
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
    assert "EML_D92_LOG1P_AFFINE_SCALED_BOUNDARY_COORDINATE_FEASIBILITY_OK" in proc.stdout
