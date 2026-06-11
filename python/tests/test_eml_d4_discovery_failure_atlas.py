"""Tests for EML-D4 discovery failure atlas."""

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

from scripts.eml_d4_discovery_failure_atlas import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def packet_by_id(payload, candidate_id: str):
    return next(packet for packet in payload["failurePackets"] if packet["candidateId"] == candidate_id)


def test_d4_records_four_failure_packets():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D4_DISCOVERY_FAILURE_ATLAS_PASS"
    assert payload["summary"]["failurePacketCount"] == 4
    assert packet_by_id(payload, "ordinary_polynomial_failure_v0")
    assert packet_by_id(payload, "deep_tree_stability_failure_v1")
    assert packet_by_id(payload, "expm1_failure_boundary_v1")
    assert packet_by_id(payload, "logaddexp_failure_boundary_v1")


def test_d4_polynomial_records_standard_representation_win():
    payload = build_payload()
    packet = packet_by_id(payload, "ordinary_polynomial_failure_v0")
    assert packet["failureClass"] == "standard_representation_wins"
    profile = packet["result"]["profiles"][0]
    assert profile["emlEncodedLowerBoundNodes"] > profile["standardOperatorCount"]
    assert packet["result"]["recommendedDisposition"] == "standard_representation_wins"


def test_d4_deep_tree_blocks_unstable_runtime_use():
    payload = build_payload()
    packet = packet_by_id(payload, "deep_tree_stability_failure_v1")
    assert packet["failureClass"] == "blocked_unstable_deep_tree"
    profile = packet["result"]["profiles"][0]
    assert profile["guardDecision"] == "block_unstable_deep_tree"
    assert profile["finiteRatio"] < 1.0


def test_d4_protected_runtime_controls_win():
    payload = build_payload()
    expm1 = packet_by_id(payload, "expm1_failure_boundary_v1")
    logaddexp = packet_by_id(payload, "logaddexp_failure_boundary_v1")
    assert expm1["failureClass"] == "protected_standard_runtime_wins"
    assert logaddexp["failureClass"] == "protected_standard_runtime_wins"
    assert expm1["result"]["profiles"][0]["protectedNoWorseCount"] == expm1["result"]["profiles"][0]["sampleCount"]
    assert logaddexp["result"]["profiles"][0]["protectedNoWorseCount"] == logaddexp["result"]["profiles"][0]["sampleCount"]
    assert logaddexp["result"]["profiles"][0]["naiveNonFiniteCount"] > 0


def test_d4_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["candidateTestPerformed"] is True
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    assert payload["summary"]["runtimePerformanceClaim"] is False
    assert payload["summary"]["failureAtlasExhaustive"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["failurePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_d4_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D4")


def test_d4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d4_discovery_failure_atlas.py",
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
    assert "EML_D4_DISCOVERY_FAILURE_ATLAS_OK" in proc.stdout
