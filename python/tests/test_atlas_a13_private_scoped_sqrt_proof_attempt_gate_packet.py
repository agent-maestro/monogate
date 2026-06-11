"""Tests for ATLAS-A13 private scoped sqrt proof-attempt gate packet."""

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

from scripts.atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet import (
    CANDIDATE_ID,
    CLAIM_FLAGS,
    GATE_ID,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a13_consumes_a12_and_creates_gate_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A13_PRIVATE_SCOPED_SQRT_PROOF_ATTEMPT_GATE_PACKET_PASS"
    assert payload["sourceArtifact"] == "atlas-a12-private-sqrt-proof-attempt-gate-selector"
    assert summary["sourceSelectedOptionId"] == "create_scoped_private_sqrt_proof_attempt_gate_packet"
    assert summary["candidateId"] == CANDIDATE_ID
    assert summary["gateId"] == GATE_ID
    assert summary["proofAttemptGatePacketCreated"] is True
    assert summary["nextRecommendedArtifact"] == "ATLAS-A14 private sqrt proof-attempt readiness selector"


def test_atlas_a13_records_scope_budget_route_aborts_and_checkpoints():
    payload = build_payload(ATLAS_GATE)
    gate = payload["proofAttemptGate"]
    assert gate["allowedScope"]["allowedRepositories"] == ["machlib"]
    assert gate["allowedScope"]["allowedFiles"] == ["MachLib/Real.lean"]
    assert gate["timeoutBudget"]["futureAttemptWallClockLimitMinutes"] == 30
    assert gate["timeoutBudget"]["futureLeanRunLimit"] == 1
    assert [item["stepId"] for item in gate["requiredStartingRoute"]] == [
        "abs_normalization",
        "guard_reduction",
        "eml_boundary_alignment",
    ]
    assert len(gate["abortConditions"]) == 5
    assert len(gate["reviewCheckpoints"]) == 5


def test_atlas_a13_creates_gate_but_no_readiness_selector_or_attempt():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["proofAttemptGatePacketCreated"] is True
    assert summary["readinessSelectorRecommended"] is True
    assert summary["proofAttemptReadinessSelectorCreated"] is False
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


def test_atlas_a13_preserves_runtime_public_and_product_blocks():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["runtimeLoweringChanged"] is False
    assert summary["runtimeSqrtReplacementClaim"] is False
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["sdkCompilerDocsCreated"] is False
    assert summary["courseMaterialCreated"] is False


def test_atlas_a13_preserves_target_gap():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["atlasRowCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["targetLowerBoundReachedClaim"] is False


def test_atlas_a13_claim_flags_stay_bounded():
    payload = build_payload(ATLAS_GATE)
    for key in TRUE_CLAIM_FLAGS:
        assert payload["claimFlags"][key] is True
        assert payload["proofAttemptGate"]["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False
    for blocked in [
        "proof_attempt_readiness_selector_created",
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


def test_atlas_a13_writes_outputs(tmp_path):
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
    assert report.startswith("# ATLAS-A13 Private Scoped Sqrt Proof-Attempt Gate Packet")
    assert "## Allowed Scope" in report
    assert "## Timeout Budget" in report
    assert "## Required Starting Route" in report
    assert "## Abort Conditions" in report
    assert "## Review Checkpoints" in report


def test_atlas_a13_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet.py",
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
    assert "ATLAS_A13_PRIVATE_SCOPED_SQRT_PROOF_ATTEMPT_GATE_PACKET_OK" in proc.stdout
