"""Tests for EML-D106 private Claim Topology Surface seed packet."""

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

from scripts.eml_d106_private_claim_topology_surface_seed_packet import (
    CLAIM_FLAGS,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def section_by_id(payload, section_id: str):
    return next(item for item in payload["surfaceSections"] if item["sectionId"] == section_id)


def row_by_id(section, key: str, value: str):
    return next(item for item in section["seedRows"] if item[key] == value)


def test_d106_consumes_d105_and_observes_gb_vis_contract():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D106_PRIVATE_CLAIM_TOPOLOGY_SURFACE_SEED_PASS"
    assert payload["sourceSelector"] == "eml-d105-post-expm1-public-witness-copy-freeze-next-selector"
    assert payload["sourceRendererContract"] == "gb-vis-a1-claim-topology-renderer-contract"
    assert summary["selectedNextArtifactFromD105"] == "EML-D106 private Claim Topology Surface seed packet"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"


def test_d106_seeds_private_surface_sections_and_shape():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["surfaceSectionCount"] == 5
    assert summary["sectionSeedRowCount"] == 14
    assert summary["nodeKindCount"] == 6
    assert summary["edgeKindCount"] == 5
    assert summary["requiredGlobalFieldCount"] == 7
    assert {section["sectionId"] for section in payload["surfaceSections"]} == {
        "fixture_state_lanes",
        "claim_boundaries_and_blocked_claims",
        "artifact_dependency_edges",
        "reviewer_actions",
        "private_guardrails",
    }
    assert "accepted_fixture" in payload["topologyDataShape"]["nodeKinds"]
    assert "negative_or_rejection_fixture" in payload["topologyDataShape"]["nodeKinds"]
    assert "blocks_claim" in payload["topologyDataShape"]["edgeKinds"]


def test_d106_fixture_and_blocked_claim_rows_preserve_boundaries():
    payload = build_payload(ATLAS_GATE)
    fixtures = section_by_id(payload, "fixture_state_lanes")
    accepted = row_by_id(fixtures, "artifactId", "d104_expm1_public_witness_copy_freeze")
    assert accepted["fixtureKind"] == "accepted_frozen_private_copy_boundary"
    assert accepted["reviewState"] == "frozen_private_no_public_approval"
    assert accepted["checkedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert accepted["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert accepted["publicStatus"] == "held_private"

    blocked = section_by_id(payload, "claim_boundaries_and_blocked_claims")
    public_copy = row_by_id(blocked, "claimId", "public_copy_approved")
    renderer = row_by_id(blocked, "claimId", "renderer_correctness")
    advantage = row_by_id(blocked, "claimId", "broad_eml_advantage")
    assert public_copy["status"] == "blocked"
    assert renderer["status"] == "blocked"
    assert advantage["status"] == "blocked"


def test_d106_records_dependencies_and_reviewer_actions():
    payload = build_payload(ATLAS_GATE)
    dependencies = section_by_id(payload, "artifact_dependency_edges")
    d105_to_d106 = row_by_id(dependencies, "edgeId", "d105_to_d106_select_private_topology_seed")
    assert d105_to_d106["relationship"] == "selected_next_private_artifact"
    assert "rendererNonClaims" in d105_to_d106["preserves"]

    actions = section_by_id(payload, "reviewer_actions")
    public_gate = row_by_id(actions, "actionId", "decide_public_copy_gate")
    mvp = row_by_id(actions, "actionId", "implement_private_surface_mvp")
    assert public_gate["status"] == "blocked"
    assert public_gate["owner"] == "human"
    assert mvp["status"] == "candidate_later"
    assert mvp["blockedUntil"] == "D106 seed accepted"


def test_d106_mvp_scope_defers_interactive_renderer():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["mvpItemCount"] == 5
    assert summary["recommendedFirstMvpItemCount"] == 4
    assert summary["deferredMvpItemCount"] == 1
    deferred = next(item for item in payload["minimalMvpScope"] if item["status"] == "defer")
    assert deferred["mvpItemId"] == "interactive_visual_renderer"


def test_d106_blocks_renderer_public_runtime_proof_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
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
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
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


def test_d106_claim_flags_are_seed_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_d106_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D106")


def test_d106_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d106_private_claim_topology_surface_seed_packet.py",
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
    assert "EML_D106_PRIVATE_CLAIM_TOPOLOGY_SURFACE_SEED_OK" in proc.stdout
