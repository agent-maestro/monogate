"""Tests for EML-D103 public-witness copy-review next-action selector."""

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

from scripts.eml_d103_public_witness_copy_review_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d103_consumes_d102_and_preserves_copy_boundary():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D103_PUBLIC_WITNESS_COPY_REVIEW_NEXT_SELECTOR_PASS"
    assert payload["sourcePacket"] == "eml-d102-expm1-boundary-public-witness-copy-packet"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["sourceSelectedCandidateId"] == "expm1_boundary_identity"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert summary["d102PublicWitnessCopyPacketCreated"] is True
    assert summary["d102PrivateCopyReviewOnly"] is True
    assert summary["d102PublicCopyDraftedForReview"] is True
    assert summary["d102ClaimBoundariesBoxIncluded"] is True
    assert summary["d102CopySectionCount"] == 5
    assert summary["d102RequiredCaveatCount"] == 7
    assert summary["d102BlockedPhraseCount"] == 11


def test_d103_selects_private_copy_freeze_and_parks_other_options():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["optionCount"] == 4
    assert summary["nextActionSelected"] is True
    assert summary["privateCopyFreezeSelected"] is True
    assert summary["selectedOptionId"] == "expm1_public_witness_copy_freeze_packet"
    assert summary["selectedNextArtifact"] == "EML-D104 expm1 public-witness copy freeze packet"
    assert option_by_id(payload, "expm1_public_witness_copy_freeze_packet")["selectionStatus"] == "selected_next"
    assert option_by_id(payload, "human_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_explicit_human_approval"
    )
    assert option_by_id(payload, "private_claim_topology_surface_mvp")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "next_public_witness_candidate_selector")["selectionStatus"] == (
        "candidate_later_after_freeze"
    )


def test_d103_blocks_approval_public_runtime_proof_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
        "copyFreezeStarted",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "claimTopologySurfaceCreated",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "boundedTrigFeasibilitySelected",
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


def test_d103_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {"next_action_selected", "private_copy_freeze_selected", "d102_copy_boundary_observed"}
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False


def test_d103_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D103")


def test_d103_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d103_public_witness_copy_review_next_selector.py",
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
    assert "EML_D103_PUBLIC_WITNESS_COPY_REVIEW_NEXT_SELECTOR_OK" in proc.stdout
