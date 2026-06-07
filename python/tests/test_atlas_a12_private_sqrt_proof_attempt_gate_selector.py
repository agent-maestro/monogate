"""Tests for ATLAS-A12 private sqrt proof-attempt gate selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a12_private_sqrt_proof_attempt_gate_selector import (
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


def test_atlas_a12_consumes_a11_and_selects_scoped_gate_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A12_PRIVATE_SQRT_PROOF_ATTEMPT_GATE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a11-private-bounded-sqrt-proof-feasibility-review-packet"
    assert summary["sourceRecommendationId"] == "proceed_to_private_proof_attempt_gate_selector"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedDecision"] == "create_gate_packet_without_starting_attempt"
    assert summary["nextRecommendedArtifact"] == "ATLAS-A13 private scoped sqrt proof-attempt gate packet"


def test_atlas_a12_reviews_route_and_blocker_counts():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["boundedReviewConsumed"] is True
    assert summary["blockersReviewed"] is True
    assert summary["proofFacingRouteStepCount"] == 3
    assert summary["blockerConditionCount"] == 3


def test_atlas_a12_recommends_gate_but_creates_no_gate_or_attempt():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["proofAttemptGateSelectorCreated"] is True
    assert summary["scopedGatePacketRecommended"] is True
    assert summary["proofAttemptGatePacketCreated"] is False
    assert summary["actualProofAttemptBlocked"] is True
    assert summary["machlibEditBlocked"] is True
    assert summary["leanTypecheckBlocked"] is True
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False


def test_atlas_a12_options_keep_pause_and_parking_available():
    payload = build_payload(ATLAS_GATE)
    options = {item["optionId"]: item for item in payload["options"]}
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert options["pause_for_atlas_v0_reference_document"]["selectionStatus"] == (
        "available_if_human_prefers_consolidation"
    )
    assert options["park_sqrt_candidate_after_review"]["selectionStatus"] == "not_selected"
    assert "gate packet must still not edit MachLib or run Lean" in options[SELECTED_OPTION_ID]["scopeConstraints"]


def test_atlas_a12_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a12_claim_flags_stay_bounded():
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
        "proof_attempt_gate_packet_created",
        "candidate_selected_for_proof",
        "candidate_validity_claim",
        "candidate_proved",
        "proof_attempt_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "theorem_lookup_performed",
        "exact_theorem_names_claimed",
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


def test_atlas_a12_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A12 Private Sqrt Proof-Attempt Gate Selector")
    assert "## Selected Gate Constraints" in report
    assert "## Options" in report


def test_atlas_a12_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a12_private_sqrt_proof_attempt_gate_selector.py",
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
    assert "ATLAS_A12_PRIVATE_SQRT_PROOF_ATTEMPT_GATE_SELECTOR_OK" in proc.stdout
