"""Tests for GB-VIS-A2 static topology export fixture."""

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

from scripts.gb_vis_a2_static_topology_export_fixture import (
    CLAIM_FLAGS,
    GROUP_ORDER,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def node_view_by_id(payload, view_id: str):
    return next(item for item in payload["staticTopologyExport"]["nodeViews"] if item["viewId"] == view_id)


def edge_view_by_id(payload, view_id: str):
    return next(item for item in payload["staticTopologyExport"]["edgeViews"] if item["viewId"] == view_id)


def test_gb_vis_a2_consumes_gb_vis_a1_contract():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A2_STATIC_TOPOLOGY_EXPORT_FIXTURE_PASS"
    assert payload["sourceContract"] == "gb-vis-a1-claim-topology-renderer-contract"
    assert payload["staticTopologyExport"]["sourceContract"] == "gb-vis-a1-claim-topology-renderer-contract"


def test_gb_vis_a2_records_export_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceNodeCount"] == 23
    assert payload["summary"]["sourceEdgeCount"] == 16
    assert payload["summary"]["nodeViewCount"] == 23
    assert payload["summary"]["edgeViewCount"] == 16
    assert payload["summary"]["reviewerFilterCount"] == 5
    assert payload["summary"]["layoutGroupCount"] == 6
    assert payload["summary"]["rendererGuardrailCount"] == 4
    assert payload["summary"]["visualEncodingCount"] == 5


def test_gb_vis_a2_preserves_source_boundaries_in_layout_metadata():
    payload = build_payload(ATLAS_GATE)
    layout = payload["staticTopologyExport"]["layoutMetadata"]
    assert layout["groupOrder"] == GROUP_ORDER
    assert layout["sourceStatement"] == "eml x (exp 1) = exp x - 1"
    assert layout["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert layout["publicStatus"] == "held_private"
    assert payload["summary"]["sourceRuntimeControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["sourcePublicStatus"] == "held_private"


def test_gb_vis_a2_exports_source_and_failure_node_views():
    payload = build_payload(ATLAS_GATE)
    source = node_view_by_id(payload, "node_view:source_freeze_packet")
    failure = node_view_by_id(payload, "node_view:failure_mode:public_gate_bypass")
    assert source["group"] == "source_boundary"
    assert source["layout"]["column"] == 0
    assert "protected_expm1_runtime_control" in source["boundaryBadges"]
    assert failure["group"] == "failure_mode"
    assert "failure_mode:block" in failure["styleRefs"]
    assert "blocking_guard" in failure["boundaryBadges"]


def test_gb_vis_a2_exports_edge_routes():
    payload = build_payload(ATLAS_GATE)
    alpha = edge_view_by_id(payload, "edge_view:source_freeze_to_abstract_claim_alpha")
    gamma = edge_view_by_id(payload, "edge_view:abstract_claim_to_artifact_class:evidence_packet")
    guard = edge_view_by_id(payload, "edge_view:failure_mode_blocks:public_gate_bypass")
    assert alpha["route"] == "left_to_right_alpha"
    assert gamma["route"] == "left_to_right_gamma"
    assert guard["route"] == "guard_backlink"
    assert "edge_kind:blocks_claim_escalation" in guard["styleRefs"]


def test_gb_vis_a2_exports_reviewer_filters():
    payload = build_payload(ATLAS_GATE)
    filters = {item["filterId"]: item for item in payload["staticTopologyExport"]["reviewerFilters"]}
    assert set(filters) == {
        "show_private_boundaries",
        "show_runtime_boundaries",
        "show_failure_blocks",
        "node_kind_filter",
        "edge_kind_filter",
    }
    assert "held_private" in filters["show_private_boundaries"]["values"]
    assert "blocks_claim_escalation" in filters["edge_kind_filter"]["values"]


def test_gb_vis_a2_records_fixture_without_renderer_or_public_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["staticTopologyExportFixtureRecorded"] is True
    assert payload["summary"]["gbVisA1ContractConsumed"] is True
    assert payload["summary"]["nodeViewsExported"] is True
    assert payload["summary"]["edgeViewsExported"] is True
    assert payload["summary"]["reviewerFiltersExported"] is True
    assert payload["summary"]["layoutMetadataExported"] is True
    assert payload["summary"]["rendererGuardrailsPreserved"] is True
    assert payload["summary"]["rendererImplemented"] is False
    assert payload["summary"]["interactiveRendererImplemented"] is False
    assert payload["summary"]["visualizationStarted"] is False
    assert payload["summary"]["visualizationRendered"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["productionValidatorImplemented"] is False
    assert payload["summary"]["validatorSoundnessProved"] is False
    assert payload["summary"]["soundnessProved"] is False
    assert payload["summary"]["fullGaloisConnectionClaim"] is False
    assert payload["summary"]["abstractInterpretationSoundnessProved"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_gb_vis_a2_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "static_topology_export_fixture_recorded",
        "gb_vis_a1_contract_consumed",
        "node_views_exported",
        "edge_views_exported",
        "reviewer_filters_exported",
        "layout_metadata_exported",
        "renderer_guardrails_preserved",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a2_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A2")


def test_gb_vis_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a2_static_topology_export_fixture.py",
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
    assert "GB_VIS_A2_STATIC_TOPOLOGY_EXPORT_FIXTURE_OK" in proc.stdout
