"""Tests for the private EML packet builder."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from scripts.eml_packet_builder import (
    DEFAULT_CLAIM_FLAGS,
    build_evidence_packet,
    build_result,
    load_packet,
    validate_expression_packet,
)


def fixture_packet(name: str = "softplus_pair_v0") -> dict:
    return load_packet(__import__("pathlib").Path(f"python/fixtures/eml_expression_packets/{name}.json"))


def test_fixture_packet_validates():
    packet = fixture_packet()
    validate_expression_packet(packet)
    assert packet["schemaVersion"] == "monogate.eml_expression_packet.v0"
    assert packet["claim_flags"]["public_savings_claim"] is False


def test_builder_emits_ir_replay_and_candidate_review():
    result = build_result(fixture_packet())
    assert result["schemaVersion"] == "monogate.eml_packet_builder.result.v0"
    assert result["status"] == "EML_PACKET_BUILDER_CANDIDATE_PASS"
    assert result["review"]["decision"] == "candidate_only"
    assert result["ir"]["nodeCount"] >= 1
    assert result["replay"]["terminalState"] == "PARKED"
    assert result["replay"]["frames"][-1]["lifecycle_state"] == "PARKED"


def test_builder_keeps_public_savings_false_even_with_internal_dag_delta():
    result = build_result(fixture_packet("gaussian_energy_v0"))
    assert result["costs"]["publicSavingsClaim"] is False
    assert result["costs"]["internalExtraDagSavingsNodes"] >= 0
    assert "No new public savings claim." in result["review"]["nonClaims"]


def test_evidence_packet_matches_public_packet_shape():
    result = build_result(fixture_packet("sigmoid_derivative_v0"))
    evidence = build_evidence_packet(result)
    assert evidence["schemaVersion"] == "monogate.evidence_public_packet.v0"
    assert evidence["reviewDecision"] == "candidate_only"
    assert evidence["validationStatus"] == "pass"
    assert evidence["replayStatus"] == "pass"
    assert evidence["claimFlags"]["public_ready"] is False
    assert evidence["claimFlags"]["hardware_observed"] is False
    assert evidence["claimFlags"]["public_savings_claim"] is False


def test_replay_hash_chain_is_preserved():
    result = build_result(fixture_packet())
    frames = result["replay"]["frames"]
    assert frames[0]["replay_hash_prev"] is None
    for prev, cur in zip(frames, frames[1:]):
        assert cur["replay_hash_prev"] == prev["replay_hash"]


def test_public_savings_claim_flip_is_blocked():
    packet = fixture_packet()
    packet["claim_flags"] = {**packet["claim_flags"], "public_savings_claim": True}
    with pytest.raises(ValueError, match="public_savings_claim"):
        validate_expression_packet(packet)


def test_hardware_claim_flip_is_blocked():
    packet = fixture_packet()
    packet["claim_flags"] = {**packet["claim_flags"], "hardware_observed": True}
    with pytest.raises(ValueError, match="hardware_observed"):
        validate_expression_packet(packet)


def test_declared_inputs_must_match_expression_arguments():
    packet = fixture_packet()
    packet["inputs"] = ["a"]
    with pytest.raises(ValueError, match="declared inputs"):
        build_result(packet)


def test_bad_expression_blocks():
    packet = {
        "schemaVersion": "monogate.eml_expression_packet.v0",
        "program_id": "bad_expression_v0",
        "family": "negative_test",
        "expression": "exp(",
        "inputs": ["x"],
        "units": {"x": "dimensionless"},
        "safe_ranges": {"x": {"min": -1.0, "max": 1.0}},
        "physical_meaning": "Malformed expression negative test.",
        "source_repo": "monogate",
        "claim_flags": dict(DEFAULT_CLAIM_FLAGS),
    }
    with pytest.raises(SyntaxError):
        build_result(packet)


def test_cli_direct_expression_writes_outputs(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_packet_builder.py",
            "--expression",
            "vin * r2 / (r1 + r2)",
            "--program-id",
            "voltage_divider_v0",
            "--family",
            "electronics",
            "--inputs",
            "vin,r1,r2",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "EML_PACKET_BUILDER_OK" in proc.stdout
    paths = json.loads(proc.stdout.split("\n", 2)[2])
    result = json.loads(__import__("pathlib").Path(paths["result"]).read_text())
    evidence = json.loads(__import__("pathlib").Path(paths["evidence"]).read_text())
    assert result["artifactId"] == "voltage-divider-v0"
    assert evidence["claimFlags"]["hardware_observed"] is False


def test_cli_build_fixtures(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_packet_builder.py",
            "--build-fixtures",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "EML_PACKET_BUILDER_FIXTURES_OK" in proc.stdout
    assert len(list((tmp_path / "results").glob("*.json"))) >= 3
    assert len(list((tmp_path / "evidence").glob("*.json"))) >= 3
