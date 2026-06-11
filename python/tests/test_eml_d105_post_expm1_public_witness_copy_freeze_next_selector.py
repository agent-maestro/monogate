"""Tests for EML-D105 post expm1 public-witness copy freeze next selector."""

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

from scripts.eml_d105_post_expm1_public_witness_copy_freeze_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d105_consumes_d104_and_preserves_frozen_copy_boundary():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D105_POST_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_NEXT_SELECTOR_PASS"
    assert payload["sourceFreezePacket"] == "eml-d104-expm1-public-witness-copy-freeze-packet"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["sourceSelectedCandidateId"] == "expm1_boundary_identity"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert summary["d104PrivateCopyFreezeStarted"] is True
    assert summary["d104PublicWitnessCopyFrozen"] is True
    assert summary["d104CopyBoundaryPreserved"] is True
    assert summary["d104ClaimBoundariesFrozen"] is True
    assert summary["d104FreezeRowCount"] == 1
    assert summary["d104FrozenSectionCount"] == 5
    assert summary["d104FrozenCaveatCount"] == 7
    assert summary["d104FrozenBlockedPhraseCount"] == 11


def test_d105_selects_private_claim_topology_seed_and_parks_other_options():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["optionCount"] == 4
    assert summary["nextActionSelected"] is True
    assert summary["privateClaimTopologySurfaceSelected"] is True
    assert summary["selectedOptionId"] == "private_claim_topology_surface_seed"
    assert summary["selectedNextArtifact"] == "EML-D106 private Claim Topology Surface seed packet"
    assert option_by_id(payload, "private_claim_topology_surface_seed")["selectionStatus"] == "selected_next"
    assert option_by_id(payload, "human_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_explicit_human_approval"
    )
    assert option_by_id(payload, "sdk_compiler_guard_note_excerpt")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "next_public_witness_candidate_selector")["selectionStatus"] == (
        "candidate_later_after_topology_seed"
    )


def test_d105_blocks_public_renderer_runtime_proof_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
        "claimTopologySurfaceCreated",
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
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "nextPublicWitnessCandidateSelected",
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
        "rendererCorrectnessClaim",
        "visualizationQualityClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        assert summary[key] is False


def test_d105_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "next_action_selected",
        "private_claim_topology_surface_selected",
        "d104_copy_boundary_observed",
    }
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False


def test_d105_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D105")


def test_d105_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d105_post_expm1_public_witness_copy_freeze_next_selector.py",
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
    assert "EML_D105_POST_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_NEXT_SELECTOR_OK" in proc.stdout
