"""Tests for EML-D73 bounded identity branch candidate selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d73_bounded_identity_branch_candidate_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def candidate_by_id(payload, candidate_id: str):
    return next(item for item in payload["branchCandidates"] if item["candidateId"] == candidate_id)


def test_d73_consumes_d72_bounded_identity_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D73_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"
    assert payload["sourceSelector"] == "eml-d72-post-probability-logit-pause-next-selector"
    assert payload["summary"]["sourceSelectedOptionId"] == "next_bounded_identity_branch_selector"
    assert payload["summary"]["sourceSelectedNextArtifact"] == "EML-D73 bounded identity branch candidate selector"


def test_d73_preserves_d71_probability_logit_freeze_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceFrozenWitnessName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"
    assert payload["summary"]["sourceFrozenStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert payload["summary"]["sourceFrozenGuardCount"] == 2
    assert payload["summary"]["sourceFrozenGuards"] == ["0 < p", "p < 1"]
    assert payload["summary"]["sourceFrozenCaveatCount"] == 9
    assert payload["summary"]["sourceFrozenBlockedPhraseCount"] == 12
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert payload["summary"]["sourceRuntimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["sourcePublicAtlasStatus"] == "held_private"


def test_d73_selects_log1p_shifted_boundary_coordinate():
    payload = build_payload(ATLAS_GATE)
    selected = candidate_by_id(payload, "log1p_shifted_boundary_coordinate")
    assert payload["decision"] == "select_log1p_shifted_boundary_coordinate_candidate"
    assert payload["summary"]["selectedCandidateId"] == "log1p_shifted_boundary_coordinate"
    assert payload["summary"]["selectedFamily"] == "guarded_log1p_shifted_coordinate"
    assert payload["summary"]["selectedSourceFrontierId"] == "post_probability_logit_pause_identity_lane"
    assert payload["summary"]["selectedProposedStatement"] == (
        "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x"
    )
    assert payload["summary"]["selectedNextArtifact"] == "EML-D74 log1p shifted boundary coordinate feasibility packet"
    assert selected["selectionStatus"] == "selected_next"
    assert selected["guardShape"] == ["0 < 1 + x"]
    assert selected["duplicatesCheckedWitness"] is False


def test_d73_records_three_candidates_and_parks_later_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["candidateCount"] == 3
    assert candidate_by_id(payload, "bounded_trig_eml_probe_selector")["selectionStatus"] == "candidate_later"
    assert candidate_by_id(payload, "human_approved_probability_logit_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_human_approval"
    )
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d73_keeps_protected_log_controls_as_runtime_controls():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d73_starts_no_feasibility_implementation_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["witnessFeasibilityRecorded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d73_keeps_public_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d73_claim_flags_are_candidate_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsCandidateOnly"] is True
    for key in ["bounded_identity_candidate_selected", "log1p_shifted_boundary_candidate_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"bounded_identity_candidate_selected", "log1p_shifted_boundary_candidate_selected"}:
            assert value is False
    for candidate in payload["branchCandidates"]:
        assert candidate["claimFlags"]["bounded_identity_candidate_selected"] is True
        assert candidate["claimFlags"]["log1p_shifted_boundary_candidate_selected"] is True
        for key, value in candidate["claimFlags"].items():
            if key not in {"bounded_identity_candidate_selected", "log1p_shifted_boundary_candidate_selected"}:
                assert value is False


def test_d73_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D73")


def test_d73_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d73_bounded_identity_branch_candidate_selector.py",
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
    assert "EML_D73_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK" in proc.stdout
