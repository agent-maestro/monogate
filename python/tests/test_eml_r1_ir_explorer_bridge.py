"""Tests for the EML-R1 IR Explorer bridge fixture."""

from __future__ import annotations

import json
import subprocess
import sys

from scripts.eml_r1_ir_explorer_bridge import build_evidence_packet, build_fixture, validate_fixture


def test_bridge_fixture_uses_existing_ir_shape():
    fixture = build_fixture()
    assert fixture["schemaVersion"] == "monogate.eml_r1.ir_explorer_bridge.v0"
    assert fixture["selectedProgram"]["programId"] == "attention_three_logits_three_outputs_v0"
    assert fixture["ir"]["nodeCount"] >= 10
    assert fixture["ir"]["edgeCount"] >= fixture["ir"]["nodeCount"] - 1
    assert fixture["ir"]["outputNode"] in {node["id"] for node in fixture["ir"]["nodes"]}


def test_bridge_fixture_has_real_shared_nodes():
    fixture = build_fixture()
    reused = fixture["ir"]["reusedNodes"]
    assert reused
    assert max(node["reuse_count"] for node in reused) >= 3
    assert fixture["costs"]["internalExtraDagSavingsNodes"] > 0


def test_bridge_replay_is_inspectable_and_parked():
    fixture = build_fixture()
    replay = fixture["replay"]
    assert replay["frameCount"] >= 10
    assert replay["terminalState"] == "PARKED"
    assert replay["frames"][-1]["lifecycle_state"] == "PARKED"
    assert replay["timeline"][0]["state"] == "INIT"
    for prev, cur in zip(replay["frames"], replay["frames"][1:]):
        assert cur["replay_hash_prev"] == prev["replay_hash"]


def test_bridge_claim_boundary_keeps_public_savings_false():
    fixture = build_fixture()
    assert fixture["costs"]["publicSavingsClaim"] is False
    assert fixture["claimBoundary"]["publicSavingsClaim"] is False
    assert fixture["claimBoundary"]["compilerBehaviorChanged"] is False
    assert fixture["claimBoundary"]["forgeBehaviorChanged"] is False
    assert fixture["claimBoundary"]["formalVerificationClaim"] is False
    assert fixture["claimBoundary"]["deployPerformed"] is False


def test_bridge_evidence_packet_is_candidate_only():
    fixture = build_fixture()
    packet = build_evidence_packet(fixture)
    validate_fixture(fixture, packet)
    assert packet["schemaVersion"] == "monogate.evidence_public_packet.v0"
    assert packet["reviewDecision"] == "candidate_only"
    assert packet["validationStatus"] == "pass"
    assert packet["replayStatus"] == "pass"
    assert packet["claimFlags"]["public_ready"] is False
    assert packet["claimFlags"]["public_savings_claim"] is False


def test_bridge_cli_strict_writes_json(tmp_path):
    fixture_path = tmp_path / "fixture.json"
    report_path = tmp_path / "report.md"
    packet_path = tmp_path / "packet.json"
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r1_ir_explorer_bridge.py",
            "--strict",
            "--out-json",
            str(fixture_path),
            "--out-report",
            str(report_path),
            "--out-packet",
            str(packet_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_R1_IR_EXPLORER_BRIDGE_OK" in proc.stdout
    fixture = json.loads(fixture_path.read_text())
    packet = json.loads(packet_path.read_text())
    assert report_path.read_text().startswith("# EML-R1 IR Explorer Bridge")
    assert fixture["artifactId"] == "eml-r1-ir-explorer-bridge"
    assert packet["claimFlags"]["public_savings_claim"] is False
