"""Tests for RH-A1 universal claim review harness."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.rh_a1_universal_claim_review_harness import (
    CLAIM_FLAGS,
    build_harness,
    infer_evidence_strength,
    review_claim,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "python/fixtures/review_harness/rh_a1_claims.json"


def fixture_claims():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["claims"]


def claim_by_id(claim_id: str):
    return next(claim for claim in fixture_claims() if claim["claimId"] == claim_id)


def test_fixture_covers_core_lanes():
    lanes = {claim["sourceLane"] for claim in fixture_claims()}
    assert {"eml", "prediction_market", "external_theory", "electronics", "compiler", "machlib", "ai_answer"}.issubset(lanes)


def test_eml_general_speed_claim_is_blocked():
    packet = review_claim(claim_by_id("eml-softplus-general-speed-claim"))
    assert packet["decision"] == "blocked_public_claim"
    assert packet["allowedSurface"] == "private"
    assert packet["evidenceStrength"] == "local_measurement_only"
    assert "general_performance_superiority" in packet["blockedClaims"]
    assert "r10_cost_stability" in packet["requiredValidators"]


def test_prediction_market_profit_claim_is_blocked():
    packet = review_claim(claim_by_id("pm-a1-profitable-agent-claim"))
    assert packet["decision"] == "blocked_public_claim"
    assert packet["evidenceStrength"] == "fixture_only"
    assert "financial_advice" in packet["blockedClaims"]
    assert "profitable_strategy" in packet["blockedClaims"]
    assert "calibration_ledger" in packet["requiredValidators"]


def test_external_theory_toe_claim_is_blocked():
    packet = review_claim(claim_by_id("oph-correct-theory-of-everything-claim"))
    assert packet["decision"] == "blocked_public_claim"
    assert packet["evidenceStrength"] == "source_only"
    assert "theory_of_everything_endorsement" in packet["blockedClaims"]
    assert "contradiction_scan" in packet["requiredValidators"]
    assert any("No endorsement" in item for item in packet["nonClaims"])


def test_hardware_observed_claim_requires_live_capture():
    packet = review_claim(claim_by_id("electronics-voltage-divider-hardware-observed"))
    assert packet["decision"] == "blocked_public_claim"
    assert packet["evidenceStrength"] == "fixture_only"
    assert "hardware_validated_without_live_capture" in packet["blockedClaims"]
    assert "live_capture_packet" in packet["requiredValidators"]
    assert packet["claimFlags"]["hardware_observed"] is False


def test_compiler_correctness_claim_is_blocked():
    packet = review_claim(claim_by_id("r11-compiler-lowering-correctness"))
    assert packet["decision"] == "blocked_public_claim"
    assert packet["evidenceStrength"] == "local_measurement_only"
    assert "compiler_correctness_without_proof" in packet["blockedClaims"]
    assert "formal_compiler_proof" in packet["requiredValidators"]
    assert packet["claimFlags"]["compiler_correctness_claim"] is False


def test_machlib_witness_gets_bounded_public_approval_only():
    packet = review_claim(claim_by_id("machlib-subtraction-boundary-witness"))
    assert packet["decision"] == "approved_bounded_public_claim"
    assert packet["allowedSurface"] == "public_bounded"
    assert packet["evidenceStrength"] == "small_checked_witness"
    assert "general_theorem_claim_beyond_checked_witness" in packet["blockedClaims"]
    assert "machlib_lake_build" in packet["requiredValidators"]


def test_ai_answer_without_evidence_requires_human_review():
    packet = review_claim(claim_by_id("ai-answer-ready-for-publication"))
    assert packet["decision"] == "human_review_required"
    assert packet["evidenceStrength"] == "none"
    assert packet["allowedSurface"] == "candidate"
    assert "no evidence paths attached" in packet["reviewNotes"]


def test_claim_flags_are_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    for claim in fixture_claims():
        packet = review_claim(claim)
        assert all(value is False for value in packet["claimFlags"].values())


def test_build_harness_outputs_review_packets(tmp_path):
    built = build_harness(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    payload = built["payload"]
    assert payload["status"] == "RH_A1_UNIVERSAL_CLAIM_REVIEW_HARNESS_PASS"
    assert payload["summary"]["reviewPacketCount"] >= 7
    assert payload["summary"]["blockedPublicClaims"] >= 5
    assert payload["summary"]["boundedPublicApprovals"] == 1
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert payload["summary"]["tradePerformed"] is False
    assert payload["summary"]["hardwareActionPerformed"] is False
    assert payload["summary"]["compilerBehaviorChanged"] is False
    validate_payload(payload)
    assert Path(built["result_path"]).exists()
    assert Path(built["report_path"]).exists()
    assert Path(built["evidence_path"]).exists()


def test_generated_review_packet_files_parse(tmp_path):
    build_harness(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    paths = sorted((tmp_path / "packets").glob("*_claim_review_packet_*.json"))
    assert len(paths) >= 7
    for path in paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.claim_review_packet.v0"
        assert packet["packetType"] == "claim_review_packet_v0"


def test_infer_evidence_strength_for_missing_evidence():
    assert infer_evidence_strength(claim_by_id("ai-answer-ready-for-publication")) == "none"


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/rh_a1_universal_claim_review_harness.py",
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
    assert "RH_A1_UNIVERSAL_CLAIM_REVIEW_HARNESS_OK" in proc.stdout
