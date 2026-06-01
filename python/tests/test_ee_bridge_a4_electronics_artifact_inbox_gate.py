"""Tests for EE-BRIDGE-A4 electronics artifact inbox gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.ee_bridge_a4_electronics_artifact_inbox_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


VALID_ARTIFACT = {
    "lessonId": "electronics_voltage_divider_intro_v0",
    "kernelId": "voltage_divider_v0",
    "sourceRepo": "monogate-electronics",
    "sourcePath": "lessons/voltage-divider/intro.md",
    "artifactType": "simulated_lesson_packet",
    "equation": "v_out = v_in * r_bottom / (r_top + r_bottom)",
    "captureStatus": "simulated_or_pending",
    "deviceMetadata": {
        "deviceObserved": False,
        "deviceId": None,
        "instrument": None,
    },
    "calibrationContext": {
        "calibrated": False,
        "calibrationId": None,
    },
    "sampleRows": [
        {"v_in": 5.0, "r_top": 1000.0, "r_bottom": 1000.0, "expected": 2.5}
    ],
    "comparisonMethod": "deterministic_formula_replay",
    "maxObservedError": 0.0,
    "claimFlags": {
        "hardware_observed": False,
        "live_serial_capture_performed": False,
        "production_controller_claim": False,
        "certified_safety_claim": False,
        "runtime_performance_claim": False,
        "compiler_correctness_claim": False,
        "formal_equivalence_claim": False,
        "public_ready": False,
    },
    "reviewerAction": "private_reviewable_simulated",
    "nextValidator": "EE-A2 live capture packet only if hardware scope is explicitly approved",
}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def test_ee_bridge_a4_default_inbox_is_pending_without_artifact(tmp_path):
    missing = tmp_path / "missing.json"
    payload = build_payload(missing)
    validate_payload(payload)
    assert payload["status"] == "EE_BRIDGE_A4_ELECTRONICS_ARTIFACT_INBOX_GATE_PASS"
    assert payload["inboxStatus"] == "pending_no_artifact"
    assert payload["summary"]["artifactProvided"] is False
    assert payload["summary"]["validationRowCount"] == 0
    assert payload["summary"]["readyForPrivateReview"] is False


def test_ee_bridge_a4_validates_supplied_artifact(tmp_path):
    artifact_path = tmp_path / "returned.json"
    write_json(artifact_path, VALID_ARTIFACT)
    payload = build_payload(artifact_path)
    validate_payload(payload)
    assert payload["inboxStatus"] == "artifact_validated"
    assert payload["summary"]["artifactProvided"] is True
    assert payload["summary"]["acceptedArtifactCount"] == 1
    assert payload["summary"]["blockedArtifactCount"] == 0
    assert payload["summary"]["readyForPrivateReview"] is True
    assert payload["validationRows"][0]["kernelId"] == "voltage_divider_v0"


def test_ee_bridge_a4_blocks_claim_overreach_artifact(tmp_path):
    artifact = json.loads(json.dumps(VALID_ARTIFACT))
    artifact["claimFlags"]["hardware_observed"] = True
    artifact_path = tmp_path / "overreach.json"
    write_json(artifact_path, artifact)
    payload = build_payload(artifact_path)
    validate_payload(payload)
    assert payload["inboxStatus"] == "artifact_blocked"
    assert payload["summary"]["blockedArtifactCount"] == 1
    assert payload["validationRows"][0]["decision"] == "blocked_claim_overreach"


def test_ee_bridge_a4_accepts_artifact_list_payload(tmp_path):
    artifact_path = tmp_path / "bundle.json"
    write_json(artifact_path, {"artifacts": [VALID_ARTIFACT]})
    payload = build_payload(artifact_path)
    validate_payload(payload)
    assert payload["inboxStatus"] == "artifact_validated"
    assert payload["summary"]["validationRowCount"] == 1


def test_ee_bridge_a4_claim_flags_and_boundaries_remain_false(tmp_path):
    payload = build_payload(tmp_path / "missing.json")
    assert payload["summary"]["hardwareObserved"] is False
    assert payload["summary"]["liveCapturePerformed"] is False
    assert payload["summary"]["monogateElectronicsRepoTouched"] is False
    assert payload["summary"]["electronicsSurfaceTouched"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_ee_bridge_a4_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds", tmp_path / "missing.json")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EE-BRIDGE-A4")


def test_ee_bridge_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ee_bridge_a4_electronics_artifact_inbox_gate.py",
            "--build",
            "--artifact-path",
            str(tmp_path / "missing.json"),
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
    assert "EE_BRIDGE_A4_ELECTRONICS_ARTIFACT_INBOX_GATE_OK" in proc.stdout
