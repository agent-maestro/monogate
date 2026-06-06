"""Tests for EML-D104 expm1 public-witness copy freeze packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d104_expm1_public_witness_copy_freeze_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d104_consumes_d103_and_preserves_selected_copy_boundary():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D104_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d103-public-witness-copy-review-next-selector"
    assert summary["selectedOptionId"] == "expm1_public_witness_copy_freeze_packet"
    assert summary["selectedNextArtifact"] == "EML-D104 expm1 public-witness copy freeze packet"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["sourceSelectedCandidateId"] == "expm1_boundary_identity"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"


def test_d104_freezes_d102_copy_sections_caveats_blockers_and_claim_boundaries():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    row = payload["freezeRows"][0]
    assert summary["d102CopySectionCount"] == 5
    assert summary["frozenSectionCount"] == 5
    assert summary["d102RequiredCaveatCount"] == 7
    assert summary["frozenCaveatCount"] == 7
    assert summary["d102BlockedPhraseCount"] == 11
    assert summary["frozenBlockedPhraseCount"] == 11
    assert summary["d102ClaimBoundariesBoxIncluded"] is True
    assert summary["privateCopyFreezeStarted"] is True
    assert summary["publicWitnessCopyFrozen"] is True
    assert summary["d102CopyBoundaryPreserved"] is True
    assert summary["claimBoundariesFrozen"] is True
    assert summary["freezeRowCount"] == 1
    assert row["freezeStatus"] == "private_public_witness_copy_boundary_frozen"
    assert "claim_boundaries" in row["frozenSectionIds"]
    assert row["publicPromotionAllowed"] is False


def test_d104_parks_public_gate_topology_and_next_candidate_options():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    parked_ids = {option["optionId"] for option in payload["parkedOptions"]}
    assert summary["parkedOptionCount"] == 3
    assert "human_public_copy_gate" in parked_ids
    assert "private_claim_topology_surface_mvp" in parked_ids
    assert "next_public_witness_candidate_selector" in parked_ids


def test_d104_blocks_public_approval_runtime_proof_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
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


def test_d104_claim_flags_are_frozen_only():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "private_copy_freeze_started",
        "public_witness_copy_frozen",
        "d102_copy_boundary_preserved",
        "claim_boundaries_frozen",
    }
    assert payload["summary"]["claimFlagsFrozenOnly"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False


def test_d104_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D104")


def test_d104_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d104_expm1_public_witness_copy_freeze_packet.py",
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
    assert "EML_D104_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_PACKET_OK" in proc.stdout
