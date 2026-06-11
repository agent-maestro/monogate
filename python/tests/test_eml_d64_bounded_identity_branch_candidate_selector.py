"""Tests for EML-D64 bounded identity branch candidate selector."""

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

from scripts.eml_d64_bounded_identity_branch_candidate_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def candidate_by_id(payload, candidate_id: str):
    return next(item for item in payload["branchCandidates"] if item["candidateId"] == candidate_id)


def test_d64_consumes_d63_bounded_identity_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D64_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"
    assert payload["sourceSelector"] == "eml-d63-post-expm1-boundary-pause-next-selector"
    assert payload["summary"]["sourceSelectedOptionId"] == "next_bounded_identity_branch_selector"
    assert payload["summary"]["sourceSelectedNextArtifact"] == "EML-D64 bounded identity branch candidate selector"


def test_d64_preserves_d62_expm1_freeze_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceFrozenWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert payload["summary"]["sourceFrozenStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["sourceFrozenCaveatCount"] == 8
    assert payload["summary"]["sourceFrozenBlockedPhraseCount"] == 10
    assert payload["summary"]["sourceNonDuplicateWitnessName"] == "MachLib.Real.atlas_exp_from_eml_witness"
    assert payload["summary"]["sourceDuplicatesExistingExpBranchWitness"] is False
    assert payload["summary"]["sourceRuntimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["sourcePublicAtlasStatus"] == "held_private"


def test_d64_selects_probability_logit_boundary_coordinate():
    payload = build_payload(ATLAS_GATE)
    selected = candidate_by_id(payload, "probability_logit_boundary_coordinate")
    assert payload["decision"] == "select_probability_logit_boundary_coordinate_candidate"
    assert payload["summary"]["selectedCandidateId"] == "probability_logit_boundary_coordinate"
    assert payload["summary"]["selectedFamily"] == "guarded_probability_log_coordinate"
    assert payload["summary"]["selectedSourceFrontierId"] == "probability_logit_boundary_v0"
    assert payload["summary"]["selectedProposedStatement"] == (
        "0 < p and p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert payload["summary"]["selectedNextArtifact"] == "EML-D65 probability logit boundary coordinate feasibility packet"
    assert selected["selectionStatus"] == "selected_next"
    assert selected["guardShape"] == ["0 < p", "p < 1"]
    assert selected["duplicatesCheckedWitness"] is False


def test_d64_records_three_candidates_and_parks_later_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["candidateCount"] == 3
    assert candidate_by_id(payload, "bounded_trig_eml_probe_selector")["selectionStatus"] == "candidate_later"
    assert candidate_by_id(payload, "human_approved_expm1_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_human_approval"
    )
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False


def test_d64_keeps_protected_log_controls_as_runtime_controls():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d64_starts_no_feasibility_implementation_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["witnessFeasibilityRecorded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d64_keeps_public_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d64_claim_flags_are_candidate_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsCandidateOnly"] is True
    for key in ["bounded_identity_candidate_selected", "probability_logit_boundary_candidate_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"bounded_identity_candidate_selected", "probability_logit_boundary_candidate_selected"}:
            assert value is False
    for candidate in payload["branchCandidates"]:
        assert candidate["claimFlags"]["bounded_identity_candidate_selected"] is True
        assert candidate["claimFlags"]["probability_logit_boundary_candidate_selected"] is True
        for key, value in candidate["claimFlags"].items():
            if key not in {"bounded_identity_candidate_selected", "probability_logit_boundary_candidate_selected"}:
                assert value is False


def test_d64_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D64")


def test_d64_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d64_bounded_identity_branch_candidate_selector.py",
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
    assert "EML_D64_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK" in proc.stdout
