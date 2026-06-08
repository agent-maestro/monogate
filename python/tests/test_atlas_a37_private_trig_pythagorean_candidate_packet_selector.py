"""Tests for ATLAS-A37 private trig pythagorean candidate packet selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a37_private_trig_pythagorean_candidate_packet_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    ROOT,
    SELECTED_OPTION_ID,
    SOURCE_DIRECTION_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a37_consumes_a36_and_recommends_future_packet():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A37_PRIVATE_TRIG_PYTHAGOREAN_CANDIDATE_PACKET_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a36-private-trig-pythagorean-feasibility-packet"
    assert summary["sourceReviewedDirectionId"] == SOURCE_DIRECTION_ID
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedDecision"] == "recommend_pure_trig_candidate_packet_without_creating_it"
    assert summary["futureCandidatePacketRecommended"] is True
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_atlas_a37_carries_source_guard_shape_and_blockers():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    selected = payload["selectedOption"]
    assert summary["feasibilityReviewConsumed"] is True
    assert summary["pureTrigScopeSelectedForFuturePacket"] is True
    assert summary["sourceRequiredGuard"] == "all real x"
    assert summary["sourcePureShapeHint"] == "sin x * sin x + cos x * cos x = 1"
    assert summary["sourcePossibleEmlBoundaryHint"] == "deferred_no_eml_shape_selected"
    assert summary["sourceBlockerCount"] == 4
    assert selected["sourceSignals"]["blockerCount"] == 4
    assert len(selected["scopeRequirementsForFuturePacket"]) == 3


def test_atlas_a37_records_options():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    options = {item["optionId"]: item for item in payload["options"]}
    assert set(options) == {
        SELECTED_OPTION_ID,
        "hold_for_trig_notation_clarification",
        "pause_for_atlas_v0_document",
    }
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert options["hold_for_trig_notation_clarification"]["selectionStatus"] == (
        "available_if_reviewer_wants_notation_choice_first"
    )
    assert options["pause_for_atlas_v0_document"]["selectionStatus"] == "available_if_human_prefers_consolidation"


def test_atlas_a37_creates_no_candidate_packet_or_proof_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["newCandidatePacketCreated"] is False
    assert summary["candidatePacketCreatedThisPhase"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateRejected"] is False
    assert summary["candidateDisproved"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False


def test_atlas_a37_blocks_edit_lean_lookup_public_runtime_and_product_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["machlibEditBlocked"] is True
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckBlocked"] is True
    assert summary["leanTypecheckPerformed"] is False
    assert summary["leanTypecheckPassed"] is False
    assert summary["theoremLookupBlocked"] is True
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeTrigReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a37_preserves_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 14
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 1
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a37_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "new_candidate_packet_created",
        "candidate_packet_created_this_phase",
        "candidate_selected_for_proof",
        "candidate_validity_claim",
        "candidate_rejected",
        "candidate_disproved",
        "candidate_proved",
        "proof_attempt_started",
        "proof_attempt_completed",
        "machlib_file_changed",
        "machlib_commit_created",
        "lean_typecheck_performed",
        "lean_typecheck_passed",
        "theorem_lookup_performed",
        "exact_theorem_names_claimed",
        "runtime_lowering_changed",
        "runtime_trig_replacement_claim",
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


def test_atlas_a37_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
        MACHLIB_ROOT,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# ATLAS-A37 Private Trig Pythagorean Candidate Packet Selector")
    assert "## Readiness Reasons" in report
    assert "## Future Packet Scope Requirements" in report
    assert "## Options" in report


def test_atlas_a37_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a37_private_trig_pythagorean_candidate_packet_selector.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
            "--machlib-root",
            str(MACHLIB_ROOT),
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
    assert "ATLAS_A37_PRIVATE_TRIG_PYTHAGOREAN_CANDIDATE_PACKET_SELECTOR_OK" in proc.stdout
