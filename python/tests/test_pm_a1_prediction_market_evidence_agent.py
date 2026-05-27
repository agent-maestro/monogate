"""Tests for PM-A1 read-only prediction market evidence agent."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.pm_a1_prediction_market_evidence_agent import (
    CLAIM_FLAGS,
    build_agent,
    forecast_packet,
    parse_resolution,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "python/fixtures/prediction_markets/pm_a1_fixture_markets.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_contains_kalshi_and_polymarket_markets():
    fixture = load_fixture()
    platforms = {market["platform"] for market in fixture["markets"]}
    assert {"kalshi", "polymarket"}.issubset(platforms)
    assert len(fixture["markets"]) >= 4


def test_resolution_parser_flags_ambiguous_flagship_market():
    market = next(item for item in load_fixture()["markets"] if "flagship" in item["question"].lower())
    resolution = parse_resolution(market)
    assert resolution["resolutionCriteriaUnderstood"] is True
    assert resolution["settlementRisk"] == "medium"
    assert "flagship" in resolution["ambiguityFlags"]
    assert resolution["parsedBoundary"]["requiresExactResolverWordingReview"] is True


def test_forecast_packet_is_read_only_and_human_reviewed():
    market = load_fixture()["markets"][0]
    packet = forecast_packet(market)
    assert packet["schemaVersion"] == "monogate.prediction_market_forecast_packet.v0"
    assert packet["tradePermission"] == "human_review_required"
    assert packet["executionPolicy"]["readOnly"] is True
    assert packet["executionPolicy"]["orderPlacementDisabled"] is True
    assert packet["executionPolicy"]["authenticatedTradingUsed"] is False
    assert packet["executionPolicy"]["tradingKeysRequired"] is False


def test_forecast_probability_and_edge_are_bounded():
    for market in load_fixture()["markets"]:
        packet = forecast_packet(market)
        assert 0 <= packet["marketPrice"] <= 1
        assert 0 <= packet["agentProbability"] <= 1
        assert packet["estimatedEdge"] == round(packet["agentProbability"] - packet["marketPrice"], 4)
        assert packet["confidence"] in {"low", "medium", "high"}


def test_claim_flags_are_all_false():
    assert CLAIM_FLAGS
    assert all(value is False for value in CLAIM_FLAGS.values())
    for market in load_fixture()["markets"]:
        packet = forecast_packet(market)
        assert all(value is False for value in packet["claimFlags"].values())
        assert "PM-A1 is not financial advice." in packet["nonClaims"]


def test_build_agent_outputs_payload_and_packets(tmp_path):
    built = build_agent(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    payload = built["payload"]
    assert payload["status"] == "PM_A1_PREDICTION_MARKET_EVIDENCE_AGENT_PASS"
    assert payload["summary"]["forecastPacketCount"] >= 4
    assert payload["summary"]["humanReviewRequiredForAll"] is True
    assert payload["summary"]["orderPlacementPerformed"] is False
    assert payload["summary"]["authenticatedTradingUsed"] is False
    validate_payload(payload)
    assert Path(built["result_path"]).exists()
    assert Path(built["report_path"]).exists()
    assert Path(built["evidence_path"]).exists()


def test_generated_forecast_packet_files_parse(tmp_path):
    build_agent(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    paths = sorted((tmp_path / "packets").glob("*_forecast_packet_*.json"))
    assert len(paths) >= 4
    for path in paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.prediction_market_forecast_packet.v0"
        assert packet["tradePermission"] == "human_review_required"


def test_evidence_packet_blocks_trading_claims(tmp_path):
    built = build_agent(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    evidence = built["evidence"]
    assert evidence["schemaVersion"] == "monogate.evidence_public_packet.v0"
    assert evidence["semanticReview"]["orderPlacementPerformed"] is False
    assert evidence["semanticReview"]["authenticatedTradingUsed"] is False
    assert evidence["semanticReview"]["humanReviewRequired"] is True
    assert all(value is False for value in evidence["claimFlags"].values())


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/pm_a1_prediction_market_evidence_agent.py",
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
    assert "PM_A1_PREDICTION_MARKET_EVIDENCE_AGENT_OK" in proc.stdout
