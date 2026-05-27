"""Tests for the private EML packet builder."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from scripts.eml_packet_builder import (
    DEFAULT_CLAIM_FLAGS,
    build_obligation_registry,
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
    assert evidence["semanticReview"]["obligation_count"] == result["obligations"]["summary"]["count"]
    assert evidence["semanticReview"]["domain_requirement_count"] == result["domainSafety"]["summary"]["domain_requirement_count"]
    assert evidence["semanticReview"]["blocked_public_claim_count"] == result["domainSafety"]["summary"]["blocked_public_claim_count"]


def test_replay_hash_chain_is_preserved():
    result = build_result(fixture_packet())
    frames = result["replay"]["frames"]
    assert frames[0]["replay_hash_prev"] is None
    for prev, cur in zip(frames, frames[1:]):
        assert cur["replay_hash_prev"] == prev["replay_hash"]


def test_ln_expression_generates_domain_obligation():
    result = build_result(fixture_packet("softplus_pair_v0"))
    cards = result["obligations"]["cards"]
    assert any(card["trigger"] == "ln" for card in cards)
    assert result["obligations"]["summary"]["domain_count"] >= 1
    assert result["obligations"]["summary"]["proved_count"] == 1


def test_domain_safety_lens_classifies_requirements_and_blocks_claims():
    result = build_result(fixture_packet("softplus_pair_v0"))
    lens = result["domainSafety"]
    assert lens["schemaVersion"] == "monogate.eml_domain_safety_lens.v0"
    assert lens["status"] == "candidate_only"
    assert lens["summary"]["domain_requirement_count"] == 1
    assert lens["summary"]["range_assumption_count"] == 2
    assert lens["summary"]["unresolved_obligation_count"] == 2
    assert lens["summary"]["checked_obligation_count"] == 1
    assert lens["summary"]["checked_domain_requirement_count"] == 1
    assert lens["summary"]["proved_count"] == 1
    assert lens["domainRequirements"][0]["requirement"] == "argument_positive"
    assert lens["domainRequirements"][0]["status"] == "checked_small_witness"
    assert lens["domainRequirements"][0]["checkedBy"] == "MachLib.Real.softplus_pair_log_argument_positive"
    assert "total_domain_safety_claim" not in lens["blockedPublicClaims"]
    assert "formal_verification_claim" in lens["blockedPublicClaims"]
    assert any("log-domain lift" in rewrite for rewrite in lens["possibleSafeRewrites"])


def test_domain_safety_lens_without_proof_manifest_stays_unresolved():
    result = build_result(fixture_packet("softplus_pair_v0"), proof_status_dir=None)
    lens = result["domainSafety"]
    assert lens["summary"]["unresolved_obligation_count"] == result["obligations"]["summary"]["count"]
    assert lens["summary"]["proved_count"] == 0
    assert lens["domainRequirements"][0]["status"] == "unresolved"
    assert "total_domain_safety_claim" in lens["blockedPublicClaims"]


def test_checked_witness_creates_safe_rewrite_proposal_without_compiler_change():
    result = build_result(fixture_packet("softplus_pair_v0"))
    proposals = result["safeRewriteProposals"]
    assert len(proposals) == 1
    assert proposals[0]["status"] == "candidate_no_compiler_change"
    assert proposals[0]["proofArtifact"] == "MachLib/EMLDomainSafety.lean"
    assert "Do not change compiler" in proposals[0]["blockedAction"]


def test_domain_safety_lens_records_declared_ranges_without_promoting_them():
    result = build_result(fixture_packet("gaussian_energy_v0"))
    lens = result["domainSafety"]
    assert lens["summary"]["domain_requirement_count"] == 0
    assert lens["summary"]["range_assumption_count"] == 1
    assert lens["rangeAssumptions"][0]["status"] == "declared_unverified"
    assert "range_safety_proved_claim" in lens["blockedPublicClaims"]
    assert lens["summary"]["proved_count"] == 0


def test_div_expression_generates_domain_obligation():
    result = build_result(fixture_packet("sigmoid_derivative_v0"))
    cards = result["obligations"]["cards"]
    assert any(card["trigger"] == "div" for card in cards)
    assert any(card["status"] == "checked_small_witness" for card in cards)
    assert result["domainSafety"]["summary"]["checked_obligation_count"] == 1
    assert result["domainSafety"]["domainRequirements"][0]["checkedBy"] == "MachLib.Real.sigmoid_denominator_nonzero"


def test_obligation_registry_tracks_checked_and_unresolved_work():
    results = [
        build_result(fixture_packet("gaussian_energy_v0")),
        build_result(fixture_packet("sigmoid_derivative_v0")),
        build_result(fixture_packet("softplus_pair_v0")),
    ]
    registry = build_obligation_registry(results)
    assert registry["schemaVersion"] == "monogate.eml_proof_obligation_registry.v0"
    assert registry["summary"]["obligation_count"] == 6
    assert registry["summary"]["domain_obligation_count"] == 2
    assert registry["summary"]["checked_witness_count"] == 2
    assert registry["summary"]["unresolved_obligation_count"] == 4
    assert all(entry["status"] != "checked_small_witness" for entry in registry["nextProofTargets"])
    assert registry["claimFlags"]["compiler_behavior_changed"] is False


def test_safe_ranges_generate_range_obligations():
    packet = fixture_packet("gaussian_energy_v0")
    result = build_result(packet)
    cards = result["obligations"]["cards"]
    assert any(card["kind"] == "range_safety" and card["input"] == "x" for card in cards)
    assert result["obligations"]["summary"]["range_safety_count"] == len(packet["safe_ranges"])


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
            "--obligation-dir",
            str(tmp_path / "obligations"),
            "--proof-status-dir",
            str(tmp_path / "proof_status"),
            "--registry-dir",
            str(tmp_path / "registry"),
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
    stub = __import__("pathlib").Path(paths["machlib_stub"]).read_text()
    manifest = json.loads(__import__("pathlib").Path(paths["machlib_stub_manifest"]).read_text())
    assert result["artifactId"] == "voltage-divider-v0"
    assert result["domainSafety"]["summary"]["domain_requirement_count"] == 1
    assert evidence["claimFlags"]["hardware_observed"] is False
    assert "namespace Monogate" in stub
    assert "contains no proofs" in stub
    assert manifest["schemaVersion"] == "monogate.eml_machlib_obligation_stub.v0"
    assert manifest["provedCount"] == 0
    assert manifest["claimFlags"]["formal_verification_claim"] is False
    assert manifest["claimFlags"]["theorem_proof_claim"] is False
    assert manifest["claimFlags"]["machlib_build_claim"] is False


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
            "--obligation-dir",
            str(tmp_path / "obligations"),
            "--proof-status-dir",
            str(tmp_path / "proof_status"),
            "--registry-dir",
            str(tmp_path / "registry"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_PACKET_BUILDER_FIXTURES_OK" in proc.stdout
    assert len(list((tmp_path / "results").glob("*.json"))) >= 3
    assert len(list((tmp_path / "evidence").glob("*.json"))) >= 3
    assert len(list((tmp_path / "obligations").glob("*/*_obligations.lean"))) >= 3
    assert len(list((tmp_path / "obligations").glob("*/*_machlib_stub_manifest.json"))) >= 3
    registries = list((tmp_path / "registry").glob("*.json"))
    assert len(registries) == 1
    registry = json.loads(registries[0].read_text())
    assert registry["summary"]["checked_witness_count"] == 0
