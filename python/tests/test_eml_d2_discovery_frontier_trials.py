"""Tests for EML-D2 discovery frontier trials."""

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

from scripts.eml_d2_discovery_frontier_trials import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def packet_by_id(payload, candidate_id: str):
    return next(packet for packet in payload["trialPackets"] if packet["candidateId"] == candidate_id)


def test_d2_runs_three_bounded_trials():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D2_DISCOVERY_FRONTIER_TRIALS_PASS"
    assert payload["summary"]["trialCount"] == 3
    assert packet_by_id(payload, "constants_zero_one_e_boundary_v0")
    assert packet_by_id(payload, "subtraction_boundary_family_v1")
    assert packet_by_id(payload, "ordinary_polynomial_failure_v0")


def test_d2_identity_trials_pass():
    payload = build_payload()
    constants = packet_by_id(payload, "constants_zero_one_e_boundary_v0")
    subtraction = packet_by_id(payload, "subtraction_boundary_family_v1")
    assert constants["trialClass"] == "identity_boundary_supported"
    assert constants["result"]["identityPass"] is True
    assert subtraction["trialClass"] == "proof_shape_identity_supported"
    assert subtraction["result"]["identityPass"] is True
    assert payload["summary"]["identitySupportedCount"] == 2


def test_d2_failure_atlas_confirms_polynomial_control():
    payload = build_payload()
    polynomial = packet_by_id(payload, "ordinary_polynomial_failure_v0")
    assert polynomial["trialClass"] == "standard_control_confirmed"
    assert polynomial["result"]["standardControlPass"] is True
    profile = polynomial["result"]["profiles"][0]
    assert profile["emlEncodedLowerBoundNodes"] > profile["standardOperatorCount"]


def test_d2_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["candidateTestPerformed"] is True
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["trialPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_d2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D2")


def test_d2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d2_discovery_frontier_trials.py",
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
    assert "EML_D2_DISCOVERY_FRONTIER_TRIALS_OK" in proc.stdout
