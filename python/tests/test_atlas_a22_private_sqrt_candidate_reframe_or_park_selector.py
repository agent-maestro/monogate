"""Tests for ATLAS-A22 private sqrt candidate reframe-or-park selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a22_private_sqrt_candidate_reframe_or_park_selector import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    PURE_REFRAME_ID,
    ROOT,
    SELECTED_OPTION_ID,
    SOURCE_BLOCKER_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"
MACHLIB_ROOT = ROOT.parent / "machlib"


def test_atlas_a22_consumes_a21_and_selects_park_path():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A22_PRIVATE_SQRT_CANDIDATE_REFRAME_OR_PARK_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "atlas-a21-private-corrected-scope-bounded-sqrt-attempt-artifact"
    assert summary["sourceStatus"] == "ATLAS_A21_PRIVATE_CORRECTED_SCOPE_BOUNDED_SQRT_ATTEMPT_ARTIFACT_BLOCKED"
    assert summary["sourceBlockerId"] == SOURCE_BLOCKER_ID
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["selectedOptionId"] == SELECTED_OPTION_ID
    assert summary["selectedDecision"] == "park_current_eml_boundary_candidate_without_rejection"
    assert summary["nextRecommendedArtifact"] == "ATLAS-A23 private Atlas gap strategy selector"


def test_atlas_a22_parks_current_eml_candidate_without_rejection_or_disproof():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    selected = payload["selectedOption"]
    assert summary["currentEmlSqrtCandidateParked"] is True
    assert selected["decision"] == "park_current_eml_boundary_candidate_without_rejection"
    assert selected["sourceBlocker"]["blockerId"] == SOURCE_BLOCKER_ID
    assert summary["candidateRejected"] is False
    assert summary["candidateDisproved"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateValidityBlocked"] is True


def test_atlas_a22_preserves_pure_reframe_but_does_not_create_candidate_packet():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    preserved = payload["selectedOption"]["preservedFutureCandidate"]
    assert summary["pureSqrtAbsReframePreservedForLater"] is True
    assert summary["preservedFutureCandidateId"] == PURE_REFRAME_ID
    assert preserved["candidateId"] == PURE_REFRAME_ID
    assert preserved["shape"] == "0 <= x -> sqrt (x * x) = x"
    assert preserved["status"] == "preserved_for_later_feasibility_not_created_not_selected"
    assert summary["sqrtCandidateReframedThisPhase"] is False
    assert summary["newCandidatePacketCreated"] is False


def test_atlas_a22_records_available_options():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    options = {item["optionId"]: item for item in payload["options"]}
    assert set(options) == {
        SELECTED_OPTION_ID,
        "reframe_as_pure_sqrt_abs_feasibility_now",
        "require_new_precise_eml_statement_before_any_attempt",
    }
    assert options[SELECTED_OPTION_ID]["selectionStatus"] == "selected_next"
    assert (
        options["reframe_as_pure_sqrt_abs_feasibility_now"]["selectionStatus"]
        == "available_if_human_explicitly_wants_sqrt_path"
    )
    assert options["require_new_precise_eml_statement_before_any_attempt"]["selectionStatus"] == "not_selected"


def test_atlas_a22_blocks_proof_edit_lean_theorem_public_runtime_and_product_claims():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["proofAttemptCompleted"] is False
    assert summary["machlibEditBlocked"] is True
    assert summary["machlibFileChanged"] is False
    assert summary["machlibCommitCreated"] is False
    assert summary["leanTypecheckBlocked"] is True
    assert summary["leanTypecheckPerformed"] is False
    assert summary["leanTypecheckPassed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a22_preserves_atlas_target_accounting():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["catalogCompletenessClaim"] is False
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a22_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE, MACHLIB_ROOT)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "sqrt_candidate_reframed_this_phase",
        "new_candidate_packet_created",
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
        "runtime_sqrt_replacement_claim",
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


def test_atlas_a22_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A22 Private Sqrt Candidate Reframe-Or-Park Selector")
    assert "## Selected Rationale" in report
    assert "## Preserved Future Candidate" in report
    assert "## Options" in report


def test_atlas_a22_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a22_private_sqrt_candidate_reframe_or_park_selector.py",
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
    assert "ATLAS_A22_PRIVATE_SQRT_CANDIDATE_REFRAME_OR_PARK_SELECTOR_OK" in proc.stdout
