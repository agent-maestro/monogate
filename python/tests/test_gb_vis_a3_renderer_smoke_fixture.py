"""Tests for GB-VIS-A3 renderer smoke fixture."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.gb_vis_a3_renderer_smoke_fixture import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def smoke_check_by_id(payload, check_id: str):
    return next(item for item in payload["rendererSmokeFixture"]["smokeChecks"] if item["checkId"] == check_id)


def test_gb_vis_a3_consumes_gb_vis_a2_export():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A3_RENDERER_SMOKE_FIXTURE_PASS"
    assert payload["sourceExportPacket"] == "gb-vis-a2-static-topology-export-fixture"


def test_gb_vis_a3_records_draw_command_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nodeDrawCommandCount"] == 23
    assert payload["summary"]["edgeDrawCommandCount"] == 16
    assert payload["summary"]["legendDrawCommandCount"] == 5
    assert payload["summary"]["smokeCheckCount"] == 6
    assert payload["summary"]["smokeCheckPassCount"] == 6
    assert payload["summary"]["rendererGuardrailCount"] == 4


def test_gb_vis_a3_preserves_source_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceCheckedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["sourceRuntimeControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["sourcePublicStatus"] == "held_private"
    node = next(item for item in payload["rendererSmokeFixture"]["nodeDrawCommands"] if item["nodeId"] == "source_freeze_packet")
    assert "protected_expm1_runtime_control" in node["boundaryBadges"]


def test_gb_vis_a3_records_smoke_checks():
    payload = build_payload(ATLAS_GATE)
    node_count = smoke_check_by_id(payload, "node_draw_command_count_matches_export")
    edge_count = smoke_check_by_id(payload, "edge_draw_command_count_matches_export")
    bounds = smoke_check_by_id(payload, "node_bounds_fit_private_viewport")
    private = smoke_check_by_id(payload, "private_boundary_badges_present")
    runtime = smoke_check_by_id(payload, "runtime_boundary_badges_present")
    guards = smoke_check_by_id(payload, "failure_mode_guard_routes_present")
    assert node_count["observed"] == 23
    assert edge_count["observed"] == 16
    assert bounds["observed"]["maxX"] <= bounds["expected"]["width"]
    assert private["observed"] >= private["expectedMinimum"]
    assert runtime["observed"] >= runtime["expectedMinimum"]
    assert guards["observed"] >= guards["expectedMinimum"]


def test_gb_vis_a3_records_edge_paths_and_guard_routes():
    payload = build_payload(ATLAS_GATE)
    edges = payload["rendererSmokeFixture"]["edgeDrawCommands"]
    guard = next(item for item in edges if item["edgeId"] == "failure_mode_blocks:public_gate_bypass")
    alpha = next(item for item in edges if item["edgeId"] == "source_freeze_to_abstract_claim_alpha")
    assert guard["route"] == "guard_backlink"
    assert alpha["route"] == "left_to_right_alpha"
    assert len(guard["points"]) == 2
    assert "edge_kind:blocks_claim_escalation" in guard["styleRefs"]


def test_gb_vis_a3_records_fixture_without_renderer_or_public_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["rendererSmokeFixtureRecorded"] is True
    assert payload["summary"]["gbVisA2ExportConsumed"] is True
    assert payload["summary"]["nodeDrawCommandsRecorded"] is True
    assert payload["summary"]["edgeDrawCommandsRecorded"] is True
    assert payload["summary"]["smokeChecksRecorded"] is True
    assert payload["summary"]["smokeChecksPassed"] is True
    assert payload["summary"]["rendererImplemented"] is False
    assert payload["summary"]["interactiveRendererImplemented"] is False
    assert payload["summary"]["rendererExecuted"] is False
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


def test_gb_vis_a3_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "renderer_smoke_fixture_recorded",
        "gb_vis_a2_export_consumed",
        "node_draw_commands_recorded",
        "edge_draw_commands_recorded",
        "smoke_checks_recorded",
        "smoke_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a3_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A3")


def test_gb_vis_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a3_renderer_smoke_fixture.py",
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
    assert "GB_VIS_A3_RENDERER_SMOKE_FIXTURE_OK" in proc.stdout
