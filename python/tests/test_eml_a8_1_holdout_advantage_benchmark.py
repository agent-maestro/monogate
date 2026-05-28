"""Tests for EML-A8.1 holdout advantage benchmark."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a8_1_holdout_advantage_benchmark import (
    CLAIM_FLAGS,
    build_benchmark,
    validate_payload,
)
from scripts.eml_language_kernel import DATE


ROOT = Path(__file__).resolve().parents[2]
STAMP = DATE.replace("-", "_")
ADVANTAGE = ROOT / f"python/results/eml_advantage_lab/eml_advantage_lab_{STAMP}.json"


def build_tmp(tmp_path):
    return build_benchmark(
        ADVANTAGE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_id(payload, case_id: str):
    return next(packet for packet in payload["holdoutPackets"] if packet["caseId"] == case_id)


def test_build_holdout_benchmark_outputs_expected_packets(tmp_path):
    built = build_tmp(tmp_path)
    payload = built["payload"]
    assert payload["status"] == "EML_A8_1_HOLDOUT_ADVANTAGE_BENCHMARK_PASS"
    assert payload["summary"]["holdoutPacketCount"] >= 12
    assert packet_by_id(payload, "exp_from_eml_v0")
    assert packet_by_id(payload, "prime_signature_log_recovery_v0")
    assert packet_by_id(payload, "gaussian_bumps_negative_control_v0")
    validate_payload(payload)


def test_holdout_profiles_exist_for_runtime_cases(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    packet = packet_by_id(payload, "softplus_pair_v0")
    profiles = {profile["profile"] for profile in packet["profiles"]}
    assert {"holdout_shifted", "edge", "stress"} == profiles


def test_negative_controls_pass_as_controls(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    controls = [packet for packet in payload["holdoutPackets"] if packet["family"] == "negative_control"]
    assert len(controls) == 3
    assert all(packet["holdoutConfidence"] == "control_pass" for packet in controls)
    assert payload["summary"]["negativeControlPassCount"] == 3


def test_research_only_is_retained_for_psi_residual(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    packet = packet_by_id(payload, "psi_residual_template_v0")
    assert packet["holdoutClass"] == "research_only_retained"
    assert packet["holdoutConfidence"] == "retained"


def test_claim_flags_are_all_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["claimFlagsAllFalse"] is True
    for packet in payload["holdoutPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))
    packet_paths = sorted((tmp_path / "packets").glob("*_holdout_packet_*.json"))
    assert len(packet_paths) >= 12
    for path in packet_paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_advantage_holdout_packet.v0"


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a8_1_holdout_advantage_benchmark.py",
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
    assert "EML_A8_1_HOLDOUT_ADVANTAGE_BENCHMARK_OK" in proc.stdout
