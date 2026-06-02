"""Tests for GB-VIS-A5 private renderer integration gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.gb_vis_a5_private_renderer_integration_gate import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_gb_vis_a5_consumes_gb_vis_a4_and_act_a5():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A5_PRIVATE_RENDERER_INTEGRATION_GATE_PASS"
    assert payload["sourceSnapshotPacket"] == "gb-vis-a4-snapshot-comparison-fixture"
    assert payload["sourceRejectionPacket"] == "act-a5-negative-rejection-fixtures"


def test_gb_vis_a5_records_integration_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["integrationRowCount"] == 6
    assert payload["summary"]["structureLayerRowCount"] == 1
    assert payload["summary"]["rejectionOverlayRowCount"] == 5
    assert payload["summary"]["snapshotNodeCommandCount"] == 23
    assert payload["summary"]["snapshotEdgeCommandCount"] == 16
    assert payload["summary"]["snapshotComparisonPassCount"] == 6
    assert payload["summary"]["rejectionFailureModeCount"] == 5
    assert payload["summary"]["unexpectedAcceptCount"] == 0


def test_gb_vis_a5_rejection_overlays_cover_act_a5_modes():
    payload = build_payload(ATLAS_GATE)
    overlay_rows = [row for row in payload["integrationRows"] if row["rowType"] == "rejection_overlay"]
    assert {row["failureMode"] for row in overlay_rows} == {
        "claim_escalation",
        "trace_gap",
        "public_gate_bypass",
        "runtime_drift",
        "lane_owner_drift",
    }
    for row in overlay_rows:
        assert row["expectedStatus"] == "reject"
        assert row["overlayBadge"] == f"expected_reject:{row['failureMode']}"
        assert row["rendererInputStatus"] == "private_input_contract_only"


def test_gb_vis_a5_records_private_structure_layer():
    payload = build_payload(ATLAS_GATE)
    structure_rows = [row for row in payload["integrationRows"] if row["rowType"] == "structure_layer"]
    assert len(structure_rows) == 1
    row = structure_rows[0]
    assert row["sourcePacket"] == "gb-vis-a4-snapshot-comparison-fixture"
    assert row["nodeCommandCount"] == 23
    assert row["edgeCommandCount"] == 16
    assert row["legendCommandCount"] == 5
    assert row["rendererInputStatus"] == "private_input_contract_only"
    assert set(row["digestFields"]) == {
        "nodeDigest",
        "edgeDigest",
        "legendDigest",
        "smokeCheckDigest",
        "guardrailDigest",
        "viewportDigest",
    }


def test_gb_vis_a5_records_integration_checks():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["integrationCheckCount"] == 8
    assert payload["summary"]["integrationCheckPassCount"] == 8
    checks = {check["checkId"]: check for check in payload["integrationChecks"]}
    assert set(checks) == {
        "snapshot_source_is_gb_vis_a4",
        "rejection_source_is_act_a5",
        "snapshot_comparison_still_passes",
        "rejection_modes_have_overlay_rows",
        "overlay_rows_remain_expected_reject",
        "private_renderer_input_status_only",
        "no_unexpected_accepts_from_act_a5",
        "renderer_execution_claims_remain_false",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["observed"] == check["expected"]


def test_gb_vis_a5_records_no_renderer_public_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["privateRendererIntegrationGateRecorded"] is True
    assert payload["summary"]["gbVisA4SnapshotConsumed"] is True
    assert payload["summary"]["actA5RejectionFixturesConsumed"] is True
    assert payload["summary"]["integrationRowsRecorded"] is True
    assert payload["summary"]["integrationGateChecksRecorded"] is True
    assert payload["summary"]["integrationGateChecksPassed"] is True
    assert payload["summary"]["rendererInputContractRecorded"] is True
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


def test_gb_vis_a5_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "private_renderer_integration_gate_recorded",
        "gb_vis_a4_snapshot_consumed",
        "act_a5_rejection_fixtures_consumed",
        "integration_rows_recorded",
        "integration_gate_checks_recorded",
        "integration_gate_checks_passed",
        "renderer_input_contract_recorded",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a5_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A5")


def test_gb_vis_a5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a5_private_renderer_integration_gate.py",
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
    assert "GB_VIS_A5_PRIVATE_RENDERER_INTEGRATION_GATE_OK" in proc.stdout
