"""Tests for ATLAS-A11 private bounded sqrt proof-feasibility review packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a11_consumes_a10_and_creates_bounded_review_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A11_PRIVATE_BOUNDED_SQRT_PROOF_FEASIBILITY_REVIEW_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a10-private-sqrt-candidate-proof-feasibility-selector"
    assert summary["sourceSelectedOptionId"] == "create_bounded_sqrt_proof_feasibility_review_packet"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["proofFeasibilityReviewPacketCreated"] is True
    assert summary["nextRecommendedArtifact"] == "ATLAS-A12 private sqrt proof-attempt gate selector"


def test_atlas_a11_records_route_theorem_shape_needs_risks_and_blockers():
    payload = build_payload(ATLAS_GATE)
    review = payload["proofFeasibilityReview"]
    assert review["reviewStatus"] == "bounded_feasibility_review_only_not_proof_not_validity"
    assert [item["stepId"] for item in review["proofFacingRoute"]] == [
        "abs_normalization",
        "guard_reduction",
        "eml_boundary_alignment",
    ]
    assert any("absolute-value" in item for item in review["likelyTheoremShapeNeeds"])
    assert any("0 <= x" in item for item in review["guardDirectionRisks"])
    assert {item["blockerId"] for item in review["blockerConditions"]} == {
        "missing_abs_normalization_route",
        "unclear_eml_expression_alignment",
        "guard_direction_unclear",
    }


def test_atlas_a11_recommends_attempt_gate_but_starts_no_proof_or_lookup():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["privateAttemptGateRecommended"] is True
    assert summary["proofAttemptGateCreated"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["theoremLookupPerformed"] is False
    assert summary["exactTheoremNamesClaimed"] is False


def test_atlas_a11_preserves_runtime_public_and_product_blocks():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a11_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a11_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
        assert payload["proofFeasibilityReview"]["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "proof_attempt_gate_created",
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


def test_atlas_a11_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A11 Private Bounded Sqrt Proof-Feasibility Review Packet")
    assert "## Proof-Facing Route" in report
    assert "## Likely Theorem-Shape Needs" in report
    assert "## Guard Direction Risks" in report
    assert "## Blocker Conditions" in report


def test_atlas_a11_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet.py",
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
    assert "ATLAS_A11_PRIVATE_BOUNDED_SQRT_PROOF_FEASIBILITY_REVIEW_PACKET_OK" in proc.stdout
