"""Tests for FEF-P12 C/Rust generated-target runtime."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p12_c_rust_generated_target_runtime import (
    CLAIM_FLAGS,
    SELECTED_CASE_IDS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p12_records_selected_c_rust_runtime_family():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P12_C_RUST_GENERATED_TARGET_RUNTIME_PASS"
    assert payload["summary"]["caseCount"] == len(SELECTED_CASE_IDS)
    assert payload["summary"]["packetCount"] == len(SELECTED_CASE_IDS) * 2
    assert payload["summary"]["passCount"] == payload["summary"]["packetCount"]


def test_fef_p12_covers_expected_sources_and_targets():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["sourceLanguages"] == ["c", "javascript", "python", "rust"]
    assert summary["generatedTargetLanguages"] == ["c", "rust"]
    assert summary["referenceTargetLanguages"] == ["python"]
    assert summary["sampleCount"] == 34


def test_fef_p12_packets_compare_runtime_to_python_reference():
    payload = build_payload()
    for packet in payload["runtimePackets"]:
        assert packet["generatedTargetLanguage"] in {"c", "rust"}
        assert packet["referenceTargetLanguage"] == "python"
        assert packet["runtimeStatus"] == "pass"
        assert packet["maxAbsError"] <= 1e-9 or packet["maxRelError"] <= 1e-9
        assert set(packet["frames"][0]["values"]) == {
            "generatedTargetRuntime",
            "pythonReference",
        }


def test_fef_p12_release_gates_and_p11_link_remain_bounded():
    payload = build_payload()
    assert payload["fefP11Link"]["reviewDecision"] == "per_target_validation_policy_recorded"
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_c_generated_target_runtime"] == "pass"
    assert gates["selected_rust_generated_target_runtime"] == "pass"
    assert gates["target_all_ready_claim"] == "blocked"
    assert gates["public_package_published"] == "blocked"


def test_fef_p12_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["runtimePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p12_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packets) == len(SELECTED_CASE_IDS) * 2
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P12")


def test_fef_p12_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p12_c_rust_generated_target_runtime.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
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
    assert "FEF_P12_C_RUST_GENERATED_TARGET_RUNTIME_OK" in proc.stdout
