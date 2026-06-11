"""Tests for GB-VIS-A7 private adapter smoke fixture."""

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

from scripts.gb_vis_a7_private_adapter_smoke_fixture import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_gb_vis_a7_consumes_gb_vis_a6_and_records_smoke_rows():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A7_PRIVATE_ADAPTER_SMOKE_FIXTURE_PASS"
    assert payload["sourceAdapterContract"] == "gb-vis-a6-private-renderer-adapter-contract"
    assert payload["summary"]["sourceAdapterInputCount"] == 6
    assert payload["summary"]["adapterSmokeRowCount"] == 6


def test_gb_vis_a7_records_structure_and_overlay_smoke_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["structureSmokeRowCount"] == 1
    assert payload["summary"]["guardOverlaySmokeRowCount"] == 5
    structure = [row for row in payload["adapterSmokeRows"] if row["rendererLayer"] == "structure"]
    overlays = [row for row in payload["adapterSmokeRows"] if row["rendererLayer"] == "guard_overlay"]
    assert len(structure) == 1
    assert structure[0]["renderIntent"] == "layout_command_snapshot"
    assert {row["renderIntent"] for row in overlays} == {
        "show_expected_reject:claim_escalation",
        "show_expected_reject:trace_gap",
        "show_expected_reject:public_gate_bypass",
        "show_expected_reject:runtime_drift",
        "show_expected_reject:lane_owner_drift",
    }


def test_gb_vis_a7_smoke_rows_are_private_and_non_rendered():
    payload = build_payload(ATLAS_GATE)
    for row in payload["adapterSmokeRows"]:
        assert row["publicStatus"] == "held_private"
        assert row["smokeStatus"] == "pass"
        assert row["rendererExecuted"] is False
        assert row["pixelRendered"] is False
        assert "no_public_surface" in row["requiredGuards"]
        assert row["requiredGuardCount"] == len(row["requiredGuards"])


def test_gb_vis_a7_adapter_smoke_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["adapterSmokeCheckCount"] == 7
    assert payload["summary"]["adapterSmokeCheckPassCount"] == 7
    checks = {check["checkId"]: check for check in payload["adapterSmokeChecks"]}
    assert set(checks) == {
        "source_adapter_contract_is_gb_vis_a6",
        "smoke_rows_match_adapter_inputs",
        "structure_smoke_row_present",
        "guard_overlay_smoke_rows_present",
        "all_smoke_rows_remain_private",
        "all_smoke_rows_keep_no_public_surface_guard",
        "no_renderer_execution_or_pixels",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["observed"] == check["expected"]


def test_gb_vis_a7_records_no_renderer_public_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["privateAdapterSmokeFixtureRecorded"] is True
    assert payload["summary"]["gbVisA6AdapterContractConsumed"] is True
    assert payload["summary"]["adapterSmokeRowsRecorded"] is True
    assert payload["summary"]["adapterSmokeChecksRecorded"] is True
    assert payload["summary"]["adapterSmokeChecksPassed"] is True
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


def test_gb_vis_a7_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "private_adapter_smoke_fixture_recorded",
        "gb_vis_a6_adapter_contract_consumed",
        "adapter_smoke_rows_recorded",
        "adapter_smoke_checks_recorded",
        "adapter_smoke_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a7_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A7")


def test_gb_vis_a7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a7_private_adapter_smoke_fixture.py",
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
    assert "GB_VIS_A7_PRIVATE_ADAPTER_SMOKE_FIXTURE_OK" in proc.stdout
