"""Tests for EE-BRIDGE-A1 electronics evidence intake contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.ee_bridge_a1_electronics_evidence_intake_contract import (
    CLAIM_FLAGS,
    build_contract,
    build_outputs,
    validate_contract,
)


def test_ee_bridge_a1_records_intake_contract_without_hardware_claim():
    contract = build_contract()
    validate_contract(contract)
    assert contract["status"] == "EE_BRIDGE_A1_ELECTRONICS_EVIDENCE_INTAKE_CONTRACT_PASS"
    assert contract["decision"] == "electronics_evidence_intake_contract_recorded_no_hardware_claim"
    assert contract["summary"]["readyForLaptopAgentHandoff"] is True
    assert contract["summary"]["hardwareObserved"] is False
    assert contract["summary"]["liveCapturePerformed"] is False


def test_ee_bridge_a1_defines_expected_artifact_types_fields_and_outcomes():
    contract = build_contract()
    assert contract["summary"]["acceptedArtifactTypeCount"] == 4
    assert contract["summary"]["requiredFieldCount"] == 15
    assert contract["summary"]["reviewerOutcomeCount"] == 5
    assert "live_capture_packet" in {item["artifactType"] for item in contract["acceptedArtifactTypes"]}
    assert "deviceMetadata" in contract["requiredFields"]
    assert "blocked_claim_overreach" in contract["reviewerOutcomes"]


def test_ee_bridge_a1_keeps_laptop_agent_boundaries_intact():
    contract = build_contract()
    boundary = contract["handoffBoundary"]
    assert "monogate-electronics" in boundary["laptopAgentOwns"]
    assert "/electronics" in boundary["laptopAgentOwns"]
    assert boundary["monogateElectronicsRepoTouchedByThisSprint"] is False
    assert boundary["electronicsPublicSurfaceTouchedByThisSprint"] is False
    assert boundary["hardwareActionPerformed"] is False


def test_ee_bridge_a1_recommends_voltage_divider_as_first_vertical():
    contract = build_contract()
    assert contract["summary"]["recommendedFirstVertical"] == "voltage_divider_v0"
    verticals = {item["kernelId"]: item for item in contract["candidateVerticals"]}
    assert verticals["voltage_divider_v0"]["recommendedOrder"] == 1
    assert "RH-A2" in verticals["voltage_divider_v0"]["whyFirst"]


def test_ee_bridge_a1_registers_pid_dual_target_kernel():
    """`pid_dual_target_v0` is the 4th candidate vertical and the first
    dual-target (ESP32 + Arty A7) kernel. Pinned here so future contract
    edits don't accidentally drop it — the simulated_lesson_packet
    artifact under electronics_intake/ is keyed off this kernelId."""
    contract = build_contract()
    verticals = {item["kernelId"]: item for item in contract["candidateVerticals"]}
    assert "pid_dual_target_v0" in verticals
    assert verticals["pid_dual_target_v0"]["recommendedOrder"] == 4
    why = verticals["pid_dual_target_v0"]["whyFirst"]
    assert "ESP32" in why and "Arty A7" in why
    assert contract["summary"]["candidateVerticalCount"] >= 4


def test_ee_bridge_a1_claim_flags_remain_false():
    contract = build_contract()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in contract["claimFlags"].values())
    assert contract["summary"]["claimFlagsAllFalse"] is True


def test_ee_bridge_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EE-BRIDGE-A1")


def test_ee_bridge_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ee_bridge_a1_electronics_evidence_intake_contract.py",
            "--build",
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
    assert "EE_BRIDGE_A1_ELECTRONICS_EVIDENCE_INTAKE_CONTRACT_OK" in proc.stdout
