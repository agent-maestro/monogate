"""Tests for EML-D3 discovery holdout/search trials."""

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

from scripts.eml_d3_discovery_holdout_search_trials import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def packet_by_id(payload, candidate_id: str):
    return next(packet for packet in payload["trialPackets"] if packet["candidateId"] == candidate_id)


def test_d3_runs_four_holdout_search_trials():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D3_DISCOVERY_HOLDOUT_SEARCH_TRIALS_PASS"
    assert payload["summary"]["trialCount"] == 4
    assert packet_by_id(payload, "probability_logit_boundary_v0")
    assert packet_by_id(payload, "normalized_exponential_family_v0")
    assert packet_by_id(payload, "damped_oscillator_eml_phase_v0")
    assert packet_by_id(payload, "psi_residual_two_zero_holdout_v1")


def test_d3_probability_logit_is_guarded_search_coordinate():
    payload = build_payload()
    packet = packet_by_id(payload, "probability_logit_boundary_v0")
    assert packet["trialClass"] == "guarded_search_coordinate_reviewable"
    assert packet["result"]["protectedStandardNoWorse"] is True
    assert packet["result"]["domainObligationsVisible"] == ["p > 0", "1 - p > 0"]


def test_d3_normalized_exponential_confirms_protected_runtime_control():
    payload = build_payload()
    packet = packet_by_id(payload, "normalized_exponential_family_v0")
    assert packet["trialClass"] == "protected_runtime_control_confirmed"
    assert packet["result"]["protectedStandardNoWorse"] is True
    profile = packet["result"]["profiles"][0]
    assert profile["protectedLogsumexpFinite"]["finiteRatio"] == 1.0
    assert profile["naiveLogsumexpFinite"]["finiteRatio"] < 1.0


def test_d3_damped_oscillator_has_parameter_recovery_signal():
    payload = build_payload()
    packet = packet_by_id(payload, "damped_oscillator_eml_phase_v0")
    assert packet["trialClass"] == "parameter_recovery_signal_supported"
    assert packet["result"]["parameterRecoverySignal"] is True
    assert packet["result"]["negativeControlsPassed"] is True


def test_d3_psi_residual_remains_ambiguous():
    payload = build_payload()
    packet = packet_by_id(payload, "psi_residual_two_zero_holdout_v1")
    assert packet["trialClass"] == "ambiguous_symbolic_search_retained"
    assert packet["result"]["searchSignalStatus"] == "ambiguous_requires_preregistered_a6_1"
    assert "standardLowerHoldoutMse" in packet["result"]
    assert "emlCloserToFirstKnownZero" in packet["result"]


def test_d3_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["candidateTestPerformed"] is True
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    assert payload["summary"]["runtimePerformanceClaim"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["trialPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_d3_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D3")


def test_d3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d3_discovery_holdout_search_trials.py",
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
    assert "EML_D3_DISCOVERY_HOLDOUT_SEARCH_TRIALS_OK" in proc.stdout
