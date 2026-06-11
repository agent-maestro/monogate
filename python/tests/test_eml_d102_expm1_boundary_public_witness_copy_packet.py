"""Tests for EML-D102 expm1-boundary public-witness copy packet."""

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

from scripts.eml_d102_expm1_boundary_public_witness_copy_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d102_consumes_d101_and_preserves_expm1_candidate():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D102_EXPM1_BOUNDARY_PUBLIC_WITNESS_COPY_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d101-private-public-witness-candidate-selector"
    assert summary["sourceSelectedOptionId"] == "expm1_boundary_identity_public_witness_candidate"
    assert summary["sourceSelectedCandidateId"] == "expm1_boundary_identity"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["selectedFamily"] == "expm1_boundary"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert summary["sourceNextArtifact"] == "EML-D102 expm1 boundary public-witness copy packet"


def test_d102_creates_private_review_copy_packet():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["publicWitnessCopyPacketCreated"] is True
    assert summary["privateCopyReviewOnly"] is True
    assert summary["publicCopyDraftedForReview"] is True
    assert summary["claimBoundariesBoxIncluded"] is True
    assert summary["copySectionCount"] == 5
    assert summary["requiredCaveatCount"] == 7
    assert summary["blockedPhraseCount"] == 11
    assert "## Original EML-Shaped Statement" in payload["privateDraftMarkdown"]
    assert "## Checked Lean / MachLib Witness" in payload["privateDraftMarkdown"]
    assert "## Guards / Domain Conditions" in payload["privateDraftMarkdown"]
    assert "## Claim Boundaries" in payload["privateDraftMarkdown"]
    assert "No EML advantage is claimed." in payload["privateDraftMarkdown"]
    assert "No claim is made that EML replaces protected `expm1`." in payload["privateDraftMarkdown"]


def test_d102_blocks_public_approval_runtime_proof_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "boundedTrigFeasibilitySelected",
        "claimTopologySurfaceCreated",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "advantageLabCaseAdded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "fullEmlSemanticsClaim",
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        assert summary[key] is False


def test_d102_claim_flags_are_copy_draft_only():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "public_witness_copy_packet_created",
        "private_copy_review_only",
        "public_copy_drafted_for_review",
        "expm1_boundary_candidate_preserved",
        "claim_boundaries_box_included",
    }
    assert payload["summary"]["claimFlagsCopyDraftOnly"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False


def test_d102_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D102")


def test_d102_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d102_expm1_boundary_public_witness_copy_packet.py",
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
    assert "EML_D102_EXPM1_BOUNDARY_PUBLIC_WITNESS_COPY_PACKET_OK" in proc.stdout
