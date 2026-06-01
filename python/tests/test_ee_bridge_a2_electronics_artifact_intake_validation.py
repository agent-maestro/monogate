"""Tests for EE-BRIDGE-A2 electronics artifact intake validation."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

from scripts.ee_bridge_a2_electronics_artifact_intake_validation import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    read_json,
    validate_candidate_artifact,
    validate_payload,
    CONTRACT_PATH,
    GUARD_INVENTORY_PATH,
    FIXTURE_PATH,
)


def test_ee_bridge_a2_validates_simulated_handoff_without_live_capture():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EE_BRIDGE_A2_ELECTRONICS_ARTIFACT_INTAKE_VALIDATION_PASS"
    assert payload["decision"] == "electronics_simulated_handoff_validated_live_capture_still_pending"
    assert summary["acceptedArtifactCount"] == 1
    assert summary["hardwareObserved"] is False
    assert summary["liveCapturePerformed"] is False
    assert summary["laptopAgentLiveArtifactReceived"] is False


def test_ee_bridge_a2_accepts_voltage_divider_simulated_packet():
    payload = build_payload()
    row = payload["acceptedArtifacts"][0]
    assert row["kernelId"] == "voltage_divider_v0"
    assert row["artifactType"] == "simulated_lesson_packet"
    assert row["captureStatus"] == "simulated_or_pending"
    assert row["decision"] == "private_reviewable_simulated"
    assert row["accepted"] is True
    assert row["claimFlagsAllFalse"] is True
    assert row["sampleRowCount"] == 3


def test_ee_bridge_a2_negative_controls_fail_closed():
    payload = build_payload()
    controls = {row["controlId"]: row for row in payload["negativeControls"]}
    assert controls["missing_device_metadata_live_capture_v0"]["actualDecision"] == "blocked_missing_metadata"
    assert controls["missing_device_metadata_live_capture_v0"]["passed"] is True
    assert controls["hardware_claim_overreach_v0"]["actualDecision"] == "blocked_claim_overreach"
    assert controls["hardware_claim_overreach_v0"]["passed"] is True


def test_ee_bridge_a2_candidate_validation_blocks_unknown_kernel():
    contract = read_json(CONTRACT_PATH)
    guard_inventory = read_json(GUARD_INVENTORY_PATH)
    fixture = read_json(FIXTURE_PATH)
    mutated = copy.deepcopy(fixture["artifacts"][0])
    mutated["kernelId"] = "unknown_kernel_v0"
    result = validate_candidate_artifact(mutated, contract, guard_inventory)
    assert result["accepted"] is False
    assert result["decision"] == "blocked_missing_metadata"
    assert "unknown_kernel_id" in result["reasonCodes"]


def test_ee_bridge_a2_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["monogateElectronicsRepoTouched"] is False
    assert summary["electronicsSurfaceTouched"] is False
    assert summary["readyForPrivateReview"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_ee_bridge_a2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EE-BRIDGE-A2")


def test_ee_bridge_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ee_bridge_a2_electronics_artifact_intake_validation.py",
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
    assert "EE_BRIDGE_A2_ELECTRONICS_ARTIFACT_INTAKE_VALIDATION_OK" in proc.stdout
