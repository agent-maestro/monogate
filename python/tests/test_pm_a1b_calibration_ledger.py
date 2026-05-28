"""Tests for PM-A1B prediction-market calibration ledger."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.pm_a1_prediction_market_evidence_agent import build_agent
from scripts.pm_a1b_calibration_ledger import (
    CLAIM_FLAGS,
    build_ledger,
    build_ledger_payload,
    edge_bucket,
    ledger_entry,
    probability_bucket,
    score_if_resolved,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[2]
PM_A1_FIXTURE = ROOT / "python/fixtures/prediction_markets/pm_a1_fixture_markets.json"


def build_pm_a1(tmp_path):
    return build_agent(
        PM_A1_FIXTURE,
        tmp_path / "pm_a1",
        tmp_path / "forecast_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )


def test_probability_bucket_is_decile_label():
    assert probability_bucket(0.01) == "0.0-0.1"
    assert probability_bucket(0.46) == "0.4-0.5"
    assert probability_bucket(0.99) == "0.9-1.0"


def test_edge_bucket_labels_review_magnitude():
    assert edge_bucket(-0.1) == "negative_large"
    assert edge_bucket(-0.04) == "negative_small"
    assert edge_bucket(0.0) == "near_market"
    assert edge_bucket(0.04) == "positive_small"
    assert edge_bucket(0.1) == "positive_large"


def test_score_if_resolved_leaves_pending_scores_null():
    scores = score_if_resolved(0.63, None)
    assert scores["brierScore"] is None
    assert scores["logLoss"] is None


def test_score_if_resolved_computes_brier_and_log_loss():
    yes_scores = score_if_resolved(0.75, True)
    no_scores = score_if_resolved(0.75, False)
    assert yes_scores["brierScore"] == 0.0625
    assert no_scores["brierScore"] == 0.5625
    assert yes_scores["logLoss"] < no_scores["logLoss"]


def test_ledger_entry_from_forecast_packet_is_pending_and_unscored(tmp_path):
    packet = build_pm_a1(tmp_path)["payload"]["forecastPackets"][0]
    entry = ledger_entry(packet)
    assert entry["marketId"] == packet["marketId"]
    assert entry["outcomeStatus"] == "pending_resolution"
    assert entry["outcomeValue"] is None
    assert entry["brierScore"] is None
    assert entry["logLoss"] is None
    assert entry["eligibleForFutureScoring"] is True
    assert entry["tradePermission"] == "human_review_required"


def test_build_ledger_payload_covers_all_forecast_packets(tmp_path):
    pm_a1 = build_pm_a1(tmp_path)
    ledger = build_ledger_payload(Path(pm_a1["result_path"]), pm_a1["payload"]["forecastPackets"])
    assert ledger["schemaVersion"] == "monogate.prediction_market_calibration_ledger.v0"
    assert ledger["ledgerType"] == "prediction_market_calibration_ledger_v0"
    assert ledger["summary"]["ledgerEntryCount"] == pm_a1["payload"]["summary"]["forecastPacketCount"]
    assert ledger["summary"]["pendingResolutionCount"] == ledger["summary"]["ledgerEntryCount"]
    assert ledger["summary"]["resolvedCount"] == 0
    assert ledger["summary"]["scoredCount"] == 0


def test_claim_flags_are_all_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    pm_a1 = build_pm_a1(tmp_path)
    ledger = build_ledger_payload(Path(pm_a1["result_path"]), pm_a1["payload"]["forecastPackets"])
    assert all(value is False for value in ledger["claimFlags"].values())
    for entry in ledger["entries"]:
        assert all(value is False for value in entry["claimFlags"].values())


def test_build_ledger_outputs_artifacts(tmp_path):
    pm_a1 = build_pm_a1(tmp_path)
    built = build_ledger(
        Path(pm_a1["result_path"]),
        tmp_path / "pm_a1b",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    payload = built["payload"]
    assert payload["status"] == "PM_A1B_CALIBRATION_LEDGER_PASS"
    assert payload["summary"]["ledgerEntryCount"] >= 4
    assert payload["summary"]["pendingResolutionCount"] >= 4
    assert payload["summary"]["outcomeScoringPerformed"] is False
    assert payload["summary"]["orderPlacementPerformed"] is False
    assert payload["summary"]["authenticatedTradingUsed"] is False
    assert payload["summary"]["financialAdviceClaim"] is False
    assert payload["summary"]["profitableStrategyClaim"] is False
    assert payload["summary"]["calibratedForecasterClaim"] is False
    validate_payload(payload)
    assert Path(built["result_path"]).exists()
    assert Path(built["ledger_path"]).exists()
    assert Path(built["report_path"]).exists()
    assert Path(built["evidence_path"]).exists()
    assert Path(built["feed_path"]).exists()


def test_evidence_packet_blocks_skill_and_trading_claims(tmp_path):
    pm_a1 = build_pm_a1(tmp_path)
    built = build_ledger(
        Path(pm_a1["result_path"]),
        tmp_path / "pm_a1b",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    evidence = built["evidence"]
    assert evidence["schemaVersion"] == "monogate.evidence_public_packet.v0"
    assert evidence["semanticReview"]["orderPlacementPerformed"] is False
    assert evidence["semanticReview"]["authenticatedTradingUsed"] is False
    assert evidence["semanticReview"]["profitableStrategyClaim"] is False
    assert evidence["semanticReview"]["calibratedForecasterClaim"] is False
    assert all(value is False for value in evidence["claimFlags"].values())


def test_command_feed_points_to_outcome_resolver(tmp_path):
    pm_a1 = build_pm_a1(tmp_path)
    built = build_ledger(
        Path(pm_a1["result_path"]),
        tmp_path / "pm_a1b",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    feed = built["feed"]
    assert feed["schemaVersion"] == "monogate.command_feed.pm_a1b.v0"
    assert feed["nextRecommendedSprint"] == "PM-A1C outcome resolver fixture"
    assert all(value is False for value in feed["claimFlags"].values())


def test_cli_build_strict(tmp_path):
    pm_a1 = build_pm_a1(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/pm_a1b_calibration_ledger.py",
            "--build",
            "--forecast-path",
            pm_a1["result_path"],
            "--out-dir",
            str(tmp_path / "pm_a1b"),
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
    assert "PM_A1B_CALIBRATION_LEDGER_OK" in proc.stdout
