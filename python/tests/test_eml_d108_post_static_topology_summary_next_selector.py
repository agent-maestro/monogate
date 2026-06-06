"""Tests for EML-D108 post static topology summary next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d108_post_static_topology_summary_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d108_consumes_d107_and_preserves_static_summary_boundary():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D108_POST_STATIC_TOPOLOGY_SUMMARY_NEXT_SELECTOR_PASS"
    assert payload["sourceStaticSummary"] == "eml-d107-private-claim-topology-static-summary-fixture"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert summary["d107StaticTableCount"] == 4
    assert summary["d107AcceptedFixtureRowCount"] == 2
    assert summary["d107BlockedClaimRowCount"] == 4
    assert summary["d107DependencyRowCount"] == 2
    assert summary["d107ReviewerActionRowCount"] == 3
    assert summary["d107GuardrailCardCount"] == 3
    assert summary["d107ReviewerCardCount"] == 4


def test_d108_selects_reviewer_response_intake_and_parks_implementation():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["optionCount"] == 4
    assert summary["nextActionSelected"] is True
    assert summary["d107StaticSummaryConsumed"] is True
    assert summary["privateReviewerResponseIntakeSelected"] is True
    assert summary["selectedOptionId"] == "private_reviewer_response_intake"
    assert summary["selectedNextArtifact"] == "EML-D109 private reviewer response intake packet"
    assert option_by_id(payload, "private_reviewer_response_intake")["selectionStatus"] == "selected_next"
    assert option_by_id(payload, "private_summary_implementation_packet")["selectionStatus"] == (
        "parked_requires_explicit_approval"
    )
    assert option_by_id(payload, "human_public_copy_gate")["selectionStatus"] == (
        "parked_requires_explicit_human_approval"
    )
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == (
        "parked_after_reviewer_response"
    )


def test_d108_does_not_consume_or_invent_reviewer_decision():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["reviewerResponseConsumed"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["reviewerRejectionRecorded"] is False
    assert summary["humanApprovalRecorded"] is False
    assert summary["implementationApproved"] is False


def test_d108_blocks_renderer_public_runtime_proof_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
        "privateSummaryImplementationSelected",
        "claimTopologySurfaceCreated",
        "interactiveRendererImplemented",
        "rendererImplemented",
        "rendererExecuted",
        "visualizationRendered",
        "visualizationQualityClaim",
        "rendererCorrectnessClaim",
        "rendererSoundnessProved",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "publicCopyApproved",
        "publicReady",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "newIdentityCandidateSelected",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "runtimeLoweringChanged",
        "runtimePerformanceClaim",
        "protectedExpm1ReplacementClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "fullEmlSemanticsClaim",
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
    ]:
        assert summary[key] is False


def test_d108_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_d108_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D108")


def test_d108_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d108_post_static_topology_summary_next_selector.py",
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
    assert "EML_D108_POST_STATIC_TOPOLOGY_SUMMARY_NEXT_SELECTOR_OK" in proc.stdout
