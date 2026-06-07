"""Tests for ATLAS-A9 private abs-normalized sqrt candidate packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a9_private_abs_normalized_sqrt_candidate_packet import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    ROOT,
    SOURCE_ENTRY_ID,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a9_consumes_a8_and_creates_private_candidate_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A9_PRIVATE_ABS_NORMALIZED_SQRT_CANDIDATE_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a8-private-sqrt-candidate-value-selector"
    assert summary["sourceSelectedOptionId"] == "create_abs_normalized_sqrt_candidate_packet"
    assert summary["sourceSelectedCandidateShape"] == "abs_normalized_then_guarded"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["sourceEntryId"] == SOURCE_ENTRY_ID
    assert summary["privateCandidatePacketCreated"] is True
    assert summary["nextRecommendedArtifact"] == "ATLAS-A10 private sqrt candidate proof-feasibility selector"


def test_atlas_a9_records_abs_normalized_and_guarded_forms():
    payload = build_payload(ATLAS_GATE)
    candidate = payload["candidatePacket"]
    forms = candidate["proofFacingForms"]
    assert forms["absNormalizedIntermediate"] == "sqrt (x * x) = |x|"
    assert forms["guardedExplanatoryForm"] == "0 <= x -> sqrt (x * x) = x"
    assert forms["emlGuardedBoundaryHint"] == "0 <= x -> eml (sqrt (x * x)) x = x"
    assert forms["formStatus"] == "candidate_shapes_for_review_not_lean_ready"


def test_atlas_a9_records_guards_and_blocked_claims():
    payload = build_payload(ATLAS_GATE)
    candidate = payload["candidatePacket"]
    guards = {guard["guardId"]: guard for guard in candidate["guards"]}
    assert guards["real_input"]["condition"] == "x : Real"
    assert guards["nonnegative_input"]["condition"] == "0 <= x"
    assert "no Lean typecheck" in candidate["blockedClaims"]
    assert "no runtime sqrt replacement" in candidate["blockedClaims"]
    assert "no public copy approval" in candidate["blockedClaims"]


def test_atlas_a9_creates_packet_but_no_validity_proof_or_runtime_claim():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["privateCandidatePacketCreated"] is True
    assert summary["candidateValidityBlocked"] is True
    assert summary["candidateValidityClaim"] is False
    assert summary["candidateSelectedForProof"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["publicCopyApproved"] is False


def test_atlas_a9_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a9_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
        assert payload["candidatePacket"]["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "candidate_validity_claim",
        "candidate_selected_for_proof",
        "candidate_proved",
        "proof_attempt_started",
        "proof_feasibility_review_completed",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "runtime_lowering_changed",
        "runtime_sqrt_replacement_claim",
        "public_atlas_promotion",
        "public_copy_approved",
        "public_surface_updated",
        "sdk_compiler_docs_created",
        "course_material_created",
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


def test_atlas_a9_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A9 Private Abs-Normalized Sqrt Candidate Packet")
    assert "## Guards" in report
    assert "## Blocked Claims" in report


def test_atlas_a9_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a9_private_abs_normalized_sqrt_candidate_packet.py",
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
    assert "ATLAS_A9_PRIVATE_ABS_NORMALIZED_SQRT_CANDIDATE_PACKET_OK" in proc.stdout
