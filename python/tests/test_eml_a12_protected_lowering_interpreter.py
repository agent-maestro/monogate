"""Tests for EML-A12 protected lowering interpreter."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a12_protected_lowering_interpreter import (
    CLAIM_FLAGS,
    build_interpreter,
    validate_payload,
)


def build_tmp(tmp_path):
    return build_interpreter(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_id(payload, case_id):
    return next(packet for packet in payload["casePackets"] if packet["caseId"] == case_id)


def test_interpreter_records_two_guarded_cases(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A12_PROTECTED_LOWERING_INTERPRETER_PASS"
    assert payload["summary"]["caseCount"] == 2
    assert payload["summary"]["frameCount"] >= 12
    assert payload["summary"]["interpreterExecuted"] is True
    validate_payload(payload)


def test_expm1_interpreter_keeps_protected_path_no_worse(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "expm1_near_zero_interpreter_v0")
    assert packet["recommendedLowering"] == "expm1"
    assert packet["summary"]["allProtectedFinite"] is True
    assert packet["summary"]["allProtectedNoWorse"] is True
    assert packet["summary"]["protectedNoWorseCount"] == packet["summary"]["frameCount"]


def test_logsumexp_interpreter_avoids_naive_overflow_edges(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "logsumexp_edge_grid_interpreter_v0")
    assert packet["recommendedLowering"] == "max_shifted_logsumexp"
    assert packet["summary"]["naiveNonFiniteCount"] >= 1
    assert packet["summary"]["protectedNonFiniteCount"] == 0
    assert packet["summary"]["allProtectedNoWorse"] is True


def test_a12_claim_flags_remain_false(tmp_path):
    built = build_tmp(tmp_path)
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in built["payload"]["claimFlags"].values())
    assert all(value is False for value in built["evidence"]["claimFlags"].values())
    for packet in built["payload"]["casePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_a12_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    paths = [built["result_path"], built["evidence_path"], built["feed_path"]]
    paths.extend(str(path) for path in (tmp_path / "packets").glob("*.json"))
    for path in paths:
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_a12_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a12_protected_lowering_interpreter.py",
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
    assert "EML_A12_PROTECTED_LOWERING_INTERPRETER_OK" in proc.stdout
