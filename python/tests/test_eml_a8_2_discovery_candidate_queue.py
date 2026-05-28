"""Tests for EML-A8.2 discovery candidate queue."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a8_2_discovery_candidate_queue import CLAIM_FLAGS, build_queue, validate_payload


def build_tmp(tmp_path):
    return build_queue(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_id(payload, candidate_id: str):
    return next(packet for packet in payload["candidatePackets"] if packet["candidateId"] == candidate_id)


def test_build_queue_outputs_candidate_packets(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A8_2_DISCOVERY_CANDIDATE_QUEUE_PASS"
    assert payload["summary"]["candidateCount"] >= 12
    assert packet_by_id(payload, "bose_fermi_maxwell_triad_v0")
    assert packet_by_id(payload, "logaddexp_runtime_anti_example_v1")
    validate_payload(payload)


def test_queue_contains_multiple_classes(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    classes = payload["summary"]["byQueueClass"]
    assert classes["ready_for_advantage_lab"] >= 2
    assert classes["needs_machlib_witness"] >= 2
    assert classes["needs_symbolic_search"] >= 1
    assert classes["needs_math_review"] >= 1


def test_candidate_flags_are_private_and_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["claimFlagsAllFalse"] is True
    for packet in payload["candidatePackets"]:
        assert packet["publicClaimAllowed"] is False
        assert packet["readyForPublicAtlas"] is False
        assert all(value is False for value in packet["claimFlags"].values())


def test_top_candidate_is_high_priority(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    top = packet_by_id(payload, payload["summary"]["topCandidateId"])
    assert top["priorityScore"] >= 40
    assert top["queueClass"] in {"ready_for_advantage_lab", "needs_machlib_witness"}


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*_discovery_candidate_*.json"))
    assert len(packets) >= 12
    for path in packets:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_discovery_candidate_packet.v0"


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a8_2_discovery_candidate_queue.py",
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
    assert "EML_A8_2_DISCOVERY_CANDIDATE_QUEUE_OK" in proc.stdout
