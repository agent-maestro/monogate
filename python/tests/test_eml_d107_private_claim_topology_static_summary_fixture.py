"""Tests for EML-D107 private Claim Topology static summary fixture."""

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

from scripts.eml_d107_private_claim_topology_static_summary_fixture import (
    CLAIM_FLAGS,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def table_by_id(payload, table_id: str):
    return next(item for item in payload["staticTables"] if item["tableId"] == table_id)


def row_by_id(table, key: str, value: str):
    return next(item for item in table["rows"] if item[key] == value)


def test_d107_consumes_d106_and_preserves_expm1_boundary():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D107_PRIVATE_CLAIM_TOPOLOGY_STATIC_SUMMARY_FIXTURE_PASS"
    assert payload["sourceSeed"] == "eml-d106-private-claim-topology-surface-seed"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert summary["sourceSurfaceSectionCount"] == 5
    assert summary["sourceSectionSeedRowCount"] == 14


def test_d107_records_static_tables_and_cards():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["staticTableCount"] == 4
    assert summary["acceptedFixtureRowCount"] == 2
    assert summary["blockedClaimRowCount"] == 4
    assert summary["dependencyRowCount"] == 2
    assert summary["reviewerActionRowCount"] == 3
    assert summary["guardrailCardCount"] == 3
    assert summary["reviewerCardCount"] == 4
    assert {table["tableId"] for table in payload["staticTables"]} == {
        "accepted_fixtures",
        "blocked_claims",
        "artifact_dependencies",
        "reviewer_actions",
    }


def test_d107_accepted_and_blocked_rows_are_reviewable():
    payload = build_payload(ATLAS_GATE)
    accepted_table = table_by_id(payload, "accepted_fixtures")
    accepted = row_by_id(accepted_table, "rowId", "d104_expm1_public_witness_copy_freeze")
    assert accepted["fixtureKind"] == "accepted_frozen_private_copy_boundary"
    assert accepted["reviewState"] == "frozen_private_no_public_approval"
    assert accepted["publicStatus"] == "held_private"

    blocked_table = table_by_id(payload, "blocked_claims")
    public_copy = row_by_id(blocked_table, "claimId", "public_copy_approved")
    renderer = row_by_id(blocked_table, "claimId", "renderer_correctness")
    replacement = row_by_id(blocked_table, "claimId", "protected_expm1_replacement")
    assert public_copy["status"] == "blocked"
    assert renderer["status"] == "blocked"
    assert replacement["status"] == "blocked"


def test_d107_dependencies_and_reviewer_actions_are_static():
    payload = build_payload(ATLAS_GATE)
    dependencies = table_by_id(payload, "artifact_dependencies")
    edge = row_by_id(dependencies, "edgeId", "d105_to_d106_select_private_topology_seed")
    assert edge["relationship"] == "selected_next_private_artifact"
    assert edge["preservedBoundaryCount"] == 4
    assert "rendererNonClaims" in edge["preserves"]

    actions = table_by_id(payload, "reviewer_actions")
    public_gate = row_by_id(actions, "actionId", "decide_public_copy_gate")
    surface_mvp = row_by_id(actions, "actionId", "implement_private_surface_mvp")
    assert public_gate["status"] == "blocked"
    assert public_gate["owner"] == "human"
    assert surface_mvp["status"] == "candidate_later"


def test_d107_guardrail_and_reviewer_cards_preserve_private_boundary():
    payload = build_payload(ATLAS_GATE)
    guardrail_ids = {card["cardId"] for card in payload["guardrailCards"]}
    reviewer_ids = {card["cardId"] for card in payload["reviewerCards"]}
    assert guardrail_ids == {"private_first", "no_visual_truth", "claim_boundary_visible"}
    assert reviewer_ids == {"current_scope", "witness_boundary", "runtime_boundary", "next_action"}
    no_visual_truth = next(card for card in payload["guardrailCards"] if card["cardId"] == "no_visual_truth")
    assert "renderer_correctness_claim" in no_visual_truth["blocks"]
    assert no_visual_truth["displayTextRequired"] == "Topology display is an index, not proof."


def test_d107_blocks_renderer_public_runtime_proof_and_laptop_claims():
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


def test_d107_claim_flags_are_static_summary_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_d107_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D107")


def test_d107_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d107_private_claim_topology_static_summary_fixture.py",
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
    assert "EML_D107_PRIVATE_CLAIM_TOPOLOGY_STATIC_SUMMARY_FIXTURE_OK" in proc.stdout
