"""Tests for ATLAS-A10 private sqrt candidate proof-feasibility selector."""

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

from scripts.atlas_a10_private_sqrt_candidate_proof_feasibility_selector import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    ROOT,
    SELECTED_OPTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a10_consumes_a9_and_selects_bounded_review_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A10_PRIVATE_SQRT_CANDIDATE_PROOF_FEASIBILITY_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a9-private-abs-normalized-sqrt-candidate-packet"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedDecision"] == "create_private_review_packet_without_starting_proof"
    assert summary["nextRecommendedArtifact"] == "ATLAS-A11 private bounded sqrt proof-feasibility review packet"


def test_atlas_a10_preserves_candidate_forms_and_guards():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["absNormalizedIntermediate"] == "sqrt (x * x) = |x|"
    assert summary["guardedExplanatoryForm"] == "0 <= x -> sqrt (x * x) = x"
    assert summary["emlGuardedBoundaryHint"] == "0 <= x -> eml (sqrt (x * x)) x = x"
    assert summary["guardConditions"] == ["x : Real", "0 <= x"]


def test_atlas_a10_recommends_review_but_creates_no_review_or_proof():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["proofFeasibilitySelectorCreated"] is True
    assert summary["candidatePacketReviewed"] is True
    assert summary["boundedReviewPacketRecommended"] is True
    assert summary["proofFeasibilityReviewPacketCreated"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["theoremLookupPerformed"] is False


def test_atlas_a10_options_keep_pause_and_parking_available():
    payload = build_payload(ATLAS_GATE)
    options = {item["optionId"]: item for item in payload["options"]}
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert options["pause_for_atlas_v0_reference_document"]["selectionStatus"] == (
        "available_if_human_prefers_consolidation"
    )
    assert options["park_sqrt_candidate_packet"]["selectionStatus"] == "not_selected"


def test_atlas_a10_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a10_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for option in payload["options"]:
        for key in TRUE_CLAIM_FLAGS:
            assert option["claimFlags"][key] is True
    for blocked in [
        "proof_feasibility_review_packet_created",
        "candidate_selected_for_proof",
        "candidate_validity_claim",
        "candidate_proved",
        "proof_attempt_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "theorem_lookup_performed",
        "runtime_lowering_changed",
        "runtime_sqrt_replacement_claim",
        "atlas_v0_doc_pause_selected",
        "sqrt_candidate_parked",
        "public_atlas_promotion",
        "public_copy_approved",
        "sdk_compiler_docs_created",
        "course_material_created",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "catalog_completeness_claim",
        "target_lower_bound_reached_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a10_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# ATLAS-A10 Private Sqrt Candidate Proof-Feasibility Selector")
    assert "## Review Inputs" in report
    assert "## Options" in report


def test_atlas_a10_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a10_private_sqrt_candidate_proof_feasibility_selector.py",
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
    assert "ATLAS_A10_PRIVATE_SQRT_CANDIDATE_PROOF_FEASIBILITY_SELECTOR_OK" in proc.stdout
