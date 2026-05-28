"""Tests for EML-A8.4 negative-control discipline."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a8_4_negative_control_discipline import CLAIM_FLAGS, build_guard, validate_payload


def build_tmp(tmp_path):
    return build_guard(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_id(payload, control_id: str):
    return next(packet for packet in payload["controlPackets"] if packet["controlId"] == control_id)


def test_build_guard_outputs_control_packets(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A8_4_NEGATIVE_CONTROL_DISCIPLINE_PASS"
    assert payload["summary"]["controlCount"] >= 5
    assert packet_by_id(payload, "expm1_runtime_anti_example_v1")
    assert packet_by_id(payload, "unstable_deep_tree_negative_control_v0")
    validate_payload(payload)


def test_control_status_counts(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["confirmedControlCount"] >= 4
    assert payload["summary"]["registeredForNextHoldoutCount"] >= 1
    assert payload["summary"]["byControlClass"]["protected_runtime"] >= 2
    assert payload["summary"]["byControlClass"]["non_eml_structure"] >= 2


def test_unstable_deep_tree_is_not_confirmed_yet(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "unstable_deep_tree_negative_control_v0")
    assert packet["expectedWinner"] == "blocked"
    assert packet["evidenceStatus"] == "registered_for_next_holdout"


def test_claim_flags_are_false_and_controls_not_exhaustive(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert payload["summary"]["negativeControlsExhaustive"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    for packet in payload["controlPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*_negative_control_*.json"))
    assert len(packets) >= 5
    for path in packets:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_negative_control_packet.v0"


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a8_4_negative_control_discipline.py",
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
    assert "EML_A8_4_NEGATIVE_CONTROL_DISCIPLINE_OK" in proc.stdout
