"""Tests for GB-VIS-A6 private renderer adapter contract."""

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

from scripts.gb_vis_a6_private_renderer_adapter_contract import (
    ADAPTER_FIELDS,
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_gb_vis_a6_consumes_gb_vis_a5_and_records_adapter_inputs():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A6_PRIVATE_RENDERER_ADAPTER_CONTRACT_PASS"
    assert payload["sourceIntegrationGate"] == "gb-vis-a5-private-renderer-integration-gate"
    assert payload["summary"]["sourceIntegrationRowCount"] == 6
    assert payload["summary"]["adapterInputCount"] == 6


def test_gb_vis_a6_records_structure_and_overlay_adapter_inputs():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["structureAdapterInputCount"] == 1
    assert payload["summary"]["guardOverlayAdapterInputCount"] == 5
    structure = [item for item in payload["adapterInputs"] if item["rendererLayer"] == "structure"]
    overlays = [item for item in payload["adapterInputs"] if item["rendererLayer"] == "guard_overlay"]
    assert len(structure) == 1
    assert structure[0]["renderIntent"] == "layout_command_snapshot"
    assert {item["failureMode"] for item in overlays} == {
        "claim_escalation",
        "trace_gap",
        "public_gate_bypass",
        "runtime_drift",
        "lane_owner_drift",
    }


def test_gb_vis_a6_adapter_fields_are_complete():
    payload = build_payload(ATLAS_GATE)
    assert payload["adapterFields"] == ADAPTER_FIELDS
    assert payload["summary"]["adapterFieldCount"] == len(ADAPTER_FIELDS)
    for item in payload["adapterInputs"]:
        for field in ADAPTER_FIELDS:
            assert field in item
        assert item["publicStatus"] == "held_private"
        assert "no_public_surface" in item["requiredGuards"]


def test_gb_vis_a6_adapter_guard_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["adapterGuardCheckCount"] == 8
    assert payload["summary"]["adapterGuardCheckPassCount"] == 8
    checks = {check["checkId"]: check for check in payload["adapterGuardChecks"]}
    assert set(checks) == {
        "source_integration_gate_is_gb_vis_a5",
        "adapter_input_count_matches_integration_rows",
        "structure_layer_adapter_input_present",
        "rejection_overlay_adapter_inputs_present",
        "adapter_fields_are_complete",
        "all_inputs_remain_private",
        "all_inputs_carry_no_public_surface_guard",
        "renderer_implementation_claims_remain_false",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["observed"] == check["expected"]


def test_gb_vis_a6_records_no_renderer_public_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["privateRendererAdapterContractRecorded"] is True
    assert payload["summary"]["gbVisA5IntegrationGateConsumed"] is True
    assert payload["summary"]["adapterInputsRecorded"] is True
    assert payload["summary"]["adapterFieldsRecorded"] is True
    assert payload["summary"]["adapterGuardChecksRecorded"] is True
    assert payload["summary"]["adapterGuardChecksPassed"] is True
    assert payload["summary"]["pixelRendererImplemented"] is False
    assert payload["summary"]["rendererImplemented"] is False
    assert payload["summary"]["interactiveRendererImplemented"] is False
    assert payload["summary"]["rendererExecuted"] is False
    assert payload["summary"]["visualizationStarted"] is False
    assert payload["summary"]["visualizationRendered"] is False
    assert payload["summary"]["visualCorrectnessProved"] is False
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


def test_gb_vis_a6_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "private_renderer_adapter_contract_recorded",
        "gb_vis_a5_integration_gate_consumed",
        "adapter_inputs_recorded",
        "adapter_fields_recorded",
        "adapter_guard_checks_recorded",
        "adapter_guard_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a6_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A6")


def test_gb_vis_a6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a6_private_renderer_adapter_contract.py",
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
    assert "GB_VIS_A6_PRIVATE_RENDERER_ADAPTER_CONTRACT_OK" in proc.stdout
