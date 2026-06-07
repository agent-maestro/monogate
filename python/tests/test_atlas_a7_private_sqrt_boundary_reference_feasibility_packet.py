"""Tests for ATLAS-A7 private sqrt boundary reference-feasibility packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a7_private_sqrt_boundary_reference_feasibility_packet import (
    CLAIM_FLAGS,
    ROOT,
    SOURCE_ENTRY_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a7_consumes_a6_and_reviews_sqrt_entry():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A7_PRIVATE_SQRT_BOUNDARY_REFERENCE_FEASIBILITY_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a6-private-reference-value-candidate-selector"
    assert summary["sourceStatus"] == "ATLAS_A6_PRIVATE_REFERENCE_VALUE_CANDIDATE_SELECTOR_PASS"
    assert summary["sourceSelectedEntryId"] == SOURCE_ENTRY_ID
    assert summary["reviewedEntryId"] == SOURCE_ENTRY_ID
    assert summary["referenceFeasibilityPacketCreated"] is True


def test_atlas_a7_records_guard_statement_and_abs_normalization_caveat():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    review = payload["sqrtReferenceReview"]
    shape = review["statementShapeReview"]
    assert summary["guardHint"] == "0 <= x"
    assert summary["statementShapeHint"] == "0 <= x -> eml (sqrt (x * x)) x = x"
    assert review["guardReview"]["requiredGuard"] == "0 <= x"
    assert shape["candidateStatementHint"] == "0 <= x -> eml (sqrt (x * x)) x = x"
    assert shape["statementShapeStatus"] == "reference_feasible_but_not_lean_ready"
    assert "sqrt (x * x) = |x|" in shape["absNormalizationCaveat"]
    assert summary["absNormalizationCaveatRecorded"] is True


def test_atlas_a7_records_course_sdk_reference_value():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    usefulness = payload["sqrtReferenceReview"]["referenceUsefulness"]
    assert summary["courseSdkReferenceValueRecorded"] is True
    assert "nonnegativity guards" in usefulness["courseHook"]
    assert "sqrt-square simplification" in usefulness["sdkGuardNoteHook"]
    assert usefulness["protectedRuntimeHint"].endswith("not as a lowering rule.")
    assert "public example" in usefulness["publicWitnessPotential"]


def test_atlas_a7_blocks_candidate_validity_proof_and_runtime_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    review = payload["sqrtReferenceReview"]
    assert summary["sqrtCandidatePacketSelected"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["newIdentityCandidateSelected"] is False
    assert summary["nextBoundedIdentityBranchSelected"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert "not a checked witness" in review["blockedClaims"]
    assert "not a candidate validity claim" in review["blockedClaims"]
    assert "no Lean typecheck" in review["blockedClaims"]


def test_atlas_a7_preserves_target_gap_and_next_artifact():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False
    assert summary["nextRecommendedArtifact"] == "ATLAS-A8 private sqrt boundary candidate value selector"


def test_atlas_a7_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "sqrt_candidate_packet_selected",
        "shortlist_entries_are_checked_witnesses",
        "candidate_validity_claim",
        "new_identity_candidate_selected",
        "next_bounded_identity_branch_selected",
        "proof_attempt_started",
        "candidate_proved",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "runtime_lowering_changed",
        "public_atlas_promotion",
        "public_copy_approved",
        "public_surface_updated",
        "sdk_compiler_docs_created",
        "course_material_created",
        "claim_topology_ui_created",
        "product_implementation_started",
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


def test_atlas_a7_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A7 Private Sqrt Boundary Reference-Feasibility Packet")
    assert "## Reference Usefulness" in report
    assert "## Blocked Claims" in report


def test_atlas_a7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a7_private_sqrt_boundary_reference_feasibility_packet.py",
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
    assert "ATLAS_A7_PRIVATE_SQRT_BOUNDARY_REFERENCE_FEASIBILITY_PACKET_OK" in proc.stdout
