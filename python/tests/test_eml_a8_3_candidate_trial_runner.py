"""Tests for EML-A8.3 candidate trial runner."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a8_3_candidate_trial_runner import CLAIM_FLAGS, build_trials, validate_payload


def build_tmp(tmp_path):
    return build_trials(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_id(payload, candidate_id: str):
    return next(packet for packet in payload["trialPackets"] if packet["candidateId"] == candidate_id)


def test_build_trials_outputs_three_packets(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A8_3_CANDIDATE_TRIAL_RUNNER_PASS"
    assert payload["summary"]["trialCount"] == 3
    assert packet_by_id(payload, "safe_log_domain_lift_v0")
    assert packet_by_id(payload, "ln_from_eml_boundary_v0")
    assert packet_by_id(payload, "expm1_runtime_anti_example_v1")
    validate_payload(payload)


def test_trial_classes_cover_positive_and_negative_results(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    classes = payload["summary"]["byTrialClass"]
    assert classes["eml_proof_shape_supported"] == 1
    assert classes["mixed_identity_supported"] == 1
    assert classes["standard_runtime_win_confirmed"] == 1
    assert payload["summary"]["blockedCount"] == 0


def test_safe_log_domain_lift_positive_on_all_profiles(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "safe_log_domain_lift_v0")
    assert packet["trialClass"] == "eml_proof_shape_supported"
    for profile in packet["profiles"]:
        assert profile["positiveLiftRatio"] == 1.0
        assert profile["eml"]["pass"] is True


def test_ln_from_eml_is_identity_not_runtime_win(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "ln_from_eml_boundary_v0")
    assert packet["trialClass"] == "mixed_identity_supported"
    assert "not a runtime win" in " ".join(packet["evidenceNotes"])
    for profile in packet["profiles"]:
        assert profile["domainPositiveRatio"] == 1.0
        assert profile["eml"]["pass"] is True
        assert profile["standard"]["pass"] is True


def test_expm1_anti_example_confirms_standard_win(tmp_path):
    packet = packet_by_id(build_tmp(tmp_path)["payload"], "expm1_runtime_anti_example_v1")
    assert packet["trialClass"] == "standard_runtime_win_confirmed"
    for profile in packet["profiles"]:
        assert profile["winner"] == "standard"
        assert profile["standardImprovementFactor"] >= 1000.0


def test_claim_flags_stay_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert payload["summary"]["candidateTrialPerformed"] is True
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    for packet in payload["trialPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*_trial_*.json"))
    assert len(packets) == 3
    for path in packets:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_candidate_trial_packet.v0"


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a8_3_candidate_trial_runner.py",
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
    assert "EML_A8_3_CANDIDATE_TRIAL_RUNNER_OK" in proc.stdout
