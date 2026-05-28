"""Tests for EML-A8.5 deep-tree holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a8_5_deep_tree_holdout import CLAIM_FLAGS, build_holdout, validate_payload


def build_tmp(tmp_path):
    return build_holdout(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_id(payload, case_id):
    return next(packet for packet in payload["holdoutPackets"] if packet["caseId"] == case_id)


def test_build_holdout_outputs_packets(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A8_5_DEEP_TREE_HOLDOUT_PASS"
    assert payload["summary"]["packetCount"] >= 5
    assert packet_by_id(payload, "unstable_deep_tree_negative_control_v0")
    validate_payload(payload)


def test_holdout_has_block_and_standard_win(tmp_path):
    summary = build_tmp(tmp_path)["payload"]["summary"]
    assert summary["blockedCount"] >= 1
    assert summary["standardRuntimeWinCount"] >= 1
    assert summary["maxTreeDepth"] >= 8


def test_unstable_deep_tree_is_blocked(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "unstable_deep_tree_negative_control_v0")
    assert packet["holdoutClass"] == "blocked_unstable_deep_tree"
    assert any(profile["winner"] == "blocked" for profile in packet["profiles"])


def test_near_zero_chain_confirms_standard_runtime_win(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "deep_expm1_chain_near_zero_v0")
    assert packet["holdoutClass"] == "standard_runtime_win"
    assert all(profile["winner"] in {"standard", "tie"} for profile in packet["profiles"])


def test_claim_flags_remain_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert payload["summary"]["deepTreeStabilityClaim"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    for packet in payload["holdoutPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*_deep_tree_holdout_*.json"))
    assert len(packets) >= 5


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a8_5_deep_tree_holdout.py",
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
    assert "EML_A8_5_DEEP_TREE_HOLDOUT_OK" in proc.stdout
