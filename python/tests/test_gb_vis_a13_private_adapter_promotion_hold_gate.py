"""Tests for GB-VIS-A13 private adapter promotion hold gate."""

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

from scripts.gb_vis_a13_private_adapter_promotion_hold_gate import (
    BLOCKED_STATEMENTS,
    CLAIM_FLAGS,
    REQUIRED_HELD_GATES,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_gb_vis_a13_consumes_gb_vis_a12_and_records_hold_gate():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "GB_VIS_A13_PRIVATE_ADAPTER_PROMOTION_HOLD_GATE_PASS"
    assert payload["sourceAdapterIntakeFeedGuard"] == "gb-vis-a12-private-adapter-intake-feed-guard"
    assert payload["sourceFeed"]["feedId"] == "gb_vis_a12_private_adapter_intake_feed_guard_feed"
    assert summary["privateAdapterPromotionHoldGateRecorded"] is True
    assert summary["gbVisA12AdapterIntakeFeedGuardConsumed"] is True
    assert summary["promotionAllowed"] is False


def test_gb_vis_a13_promotion_gates_are_held():
    payload = build_payload(ATLAS_GATE)
    gates = {gate["gateId"]: gate for gate in payload["promotionHoldGates"]}
    assert set(REQUIRED_HELD_GATES).issubset(gates)
    assert gates["source_next_action_private"]["observed"] is True
    assert gates["source_next_action_private"]["expected"] is True
    assert payload["summary"]["promotionHoldGateCount"] == 10
    for gate in gates.values():
        assert gate["promotionAllowed"] is False


def test_gb_vis_a13_promotion_hold_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    checks = {check["checkId"]: check for check in payload["promotionHoldChecks"]}
    assert payload["summary"]["promotionHoldCheckCount"] == 10
    assert payload["summary"]["promotionHoldPassCount"] == 10
    assert len(checks) == 10
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["observed"] == check["expected"]


def test_gb_vis_a13_blocks_renderer_public_and_artifact_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert payload["blockedStatements"] == BLOCKED_STATEMENTS
    assert summary["blockedStatementCount"] == len(BLOCKED_STATEMENTS)
    assert "GB-VIS artifacts are public-ready." in payload["blockedStatements"]
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["concreteAdapterArtifactAccepted"] is False
    assert summary["pixelRendererImplemented"] is False
    assert summary["rendererImplemented"] is False
    assert summary["rendererExecuted"] is False
    assert summary["visualizationRendered"] is False
    assert summary["visualCorrectnessProved"] is False
    assert summary["rendererSoundnessProved"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False


def test_gb_vis_a13_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "private_adapter_promotion_hold_gate_recorded",
        "gb_vis_a12_adapter_intake_feed_guard_consumed",
        "source_feed_rebuilt",
        "promotion_hold_gates_recorded",
        "promotion_hold_checks_recorded",
        "promotion_hold_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a13_next_action_stays_private():
    payload = build_payload(ATLAS_GATE)
    assert "without public promotion" in payload["summary"]["nextAction"]
    assert "without public promotion" in payload["sourceFeed"]["nextAction"]
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["rendererExecuted"] is False


def test_gb_vis_a13_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A13")


def test_gb_vis_a13_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a13_private_adapter_promotion_hold_gate.py",
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
    assert "GB_VIS_A13_PRIVATE_ADAPTER_PROMOTION_HOLD_GATE_OK" in proc.stdout
