"""Tests for EML-D55 bounded identity branch candidate selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d55_bounded_identity_branch_candidate_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def candidate_by_id(payload, candidate_id: str):
    return next(item for item in payload["branchCandidates"] if item["candidateId"] == candidate_id)


def test_d55_consumes_d54_bounded_identity_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D55_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"
    assert payload["sourceSelector"] == "eml-d54-post-constant-coordinate-pause-next-selector"
    assert payload["summary"]["sourceSelectedOptionId"] == "next_bounded_identity_branch_selector"
    assert payload["summary"]["sourceSelectedNextArtifact"] == "EML-D55 bounded identity branch candidate selector"


def test_d55_preserves_d53_freeze_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceFrozenWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert payload["summary"]["sourceFrozenStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["sourceFrozenCaveatCount"] == 8
    assert payload["summary"]["sourceFrozenBlockedPhraseCount"] == 10
    assert payload["summary"]["sourceLocalSpellingUsesOnePlusOne"] is True
    assert payload["summary"]["sourceExistingConstantWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["sourceDuplicatesExistingConstantWitness"] is False


def test_d55_selects_expm1_boundary_identity_candidate():
    payload = build_payload(ATLAS_GATE)
    selected = candidate_by_id(payload, "expm1_boundary_identity")
    assert payload["decision"] == "select_expm1_boundary_identity_candidate"
    assert payload["summary"]["selectedCandidateId"] == "expm1_boundary_identity"
    assert payload["summary"]["selectedFamily"] == "protected_runtime_boundary_identity"
    assert payload["summary"]["selectedSourceFrontierId"] == "expm1_failure_boundary_v1"
    assert payload["summary"]["selectedProposedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D56 expm1 boundary identity feasibility packet"
    assert selected["selectionStatus"] == "selected_next"
    assert selected["guardShape"] == []
    assert selected["duplicatesCheckedWitness"] is False


def test_d55_records_three_candidates_and_parks_later_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["candidateCount"] == 3
    assert candidate_by_id(payload, "probability_logit_boundary_coordinate")["selectionStatus"] == "candidate_later"
    assert candidate_by_id(payload, "bounded_trig_eml_probe_selector")["selectionStatus"] == "candidate_later"
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False


def test_d55_keeps_protected_expm1_as_runtime_control():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d55_starts_no_feasibility_implementation_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["witnessFeasibilityRecorded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d55_keeps_public_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d55_claim_flags_are_candidate_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsCandidateOnly"] is True
    for key in ["bounded_identity_candidate_selected", "expm1_boundary_candidate_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"bounded_identity_candidate_selected", "expm1_boundary_candidate_selected"}:
            assert value is False
    for candidate in payload["branchCandidates"]:
        assert candidate["claimFlags"]["bounded_identity_candidate_selected"] is True
        assert candidate["claimFlags"]["expm1_boundary_candidate_selected"] is True
        for key, value in candidate["claimFlags"].items():
            if key not in {"bounded_identity_candidate_selected", "expm1_boundary_candidate_selected"}:
                assert value is False


def test_d55_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D55")


def test_d55_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d55_bounded_identity_branch_candidate_selector.py",
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
    assert "EML_D55_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK" in proc.stdout
