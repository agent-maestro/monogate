"""Tests for RT-A1 RAMPART compatibility spike."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.rt_a1_rampart_compatibility_spike import (
    CLAIM_FLAGS,
    build_spike,
    packet_from_result,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "python/fixtures/rampart/rt_a1_rampart_fixture_results.json"


def fixture_results():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["results"]


def result_by_id(result_id: str):
    return next(result for result in fixture_results() if result["resultId"] == result_id)


def test_fixture_is_offline_and_contains_expected_categories():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["liveRampartRun"] is False
    assert fixture["liveModelCallsPerformed"] is False
    assert fixture["apiKeysUsed"] is False
    categories = {result["attackCategory"] for result in fixture["results"]}
    assert {
        "forbidden_claim_flag_injection",
        "financial_advice_trading_injection",
        "external_theory_overclaim",
        "private_context_leakage",
    }.issubset(categories)


def test_pass_fixture_becomes_candidate_evidence_packet():
    packet = packet_from_result(result_by_id("builder-forbidden-claim-flag-injection-pass"))
    assert packet["schemaVersion"] == "monogate.rampart_redteam_evidence_packet.v0"
    assert packet["evaluatorVerdict"] == "pass"
    assert packet["recommendedRhAction"] == "candidate_only"
    assert packet["publicRobustnessClaimAllowed"] is False
    assert packet["claimFlags"]["certified_safety_claim"] is False


def test_fail_fixture_recommends_blocked_public_claim():
    packet = packet_from_result(result_by_id("command-cockpit-leakage-attempt-fail"))
    assert packet["evaluatorVerdict"] == "fail"
    assert packet["recommendedRhAction"] == "blocked_public_claim"
    assert "adapter_missing" in packet["violatedPolicies"]
    assert packet["claimFlags"]["private_cockpit_leakage_validated_safe"] is False


def test_claim_flags_are_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    for result in fixture_results():
        packet = packet_from_result(result)
        assert all(value is False for value in packet["claimFlags"].values())


def test_build_spike_outputs_packets_and_evidence(tmp_path):
    built = build_spike(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    payload = built["payload"]
    assert payload["status"] == "RT_A1_RAMPART_COMPATIBILITY_SPIKE_PASS"
    assert payload["summary"]["redteamPacketCount"] >= 4
    assert payload["summary"]["passingPacketCount"] >= 3
    assert payload["summary"]["failingPacketCount"] >= 1
    assert payload["summary"]["liveRampartRun"] is False
    assert payload["summary"]["liveModelCallsPerformed"] is False
    assert payload["summary"]["apiKeysUsed"] is False
    assert payload["summary"]["publicRobustnessClaimAllowed"] is False
    validate_payload(payload)
    assert Path(built["result_path"]).exists()
    assert Path(built["report_path"]).exists()
    assert Path(built["evidence_path"]).exists()


def test_generated_redteam_packet_files_parse(tmp_path):
    build_spike(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    paths = sorted((tmp_path / "packets").glob("*_rampart_redteam_packet_*.json"))
    assert len(paths) >= 4
    for path in paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.rampart_redteam_evidence_packet.v0"
        assert packet["publicRobustnessClaimAllowed"] is False


def test_evidence_packet_blocks_certified_safety_claim(tmp_path):
    built = build_spike(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    evidence = built["evidence"]
    assert evidence["schemaVersion"] == "monogate.evidence_public_packet.v0"
    assert evidence["semanticReview"]["liveRampartRun"] is False
    assert evidence["semanticReview"]["apiKeysUsed"] is False
    assert evidence["semanticReview"]["publicRobustnessClaimAllowed"] is False
    assert evidence["claimFlags"]["certified_safety_claim"] is False
    assert evidence["claimFlags"]["comprehensive_robustness_claim"] is False


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/rt_a1_rampart_compatibility_spike.py",
            "--build",
            "--fixture-path",
            str(FIXTURE),
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "RT_A1_RAMPART_COMPATIBILITY_SPIKE_OK" in proc.stdout
