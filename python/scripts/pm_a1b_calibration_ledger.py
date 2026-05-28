#!/usr/bin/env python3
"""PM-A1B prediction-market calibration ledger.

Builds a scoring-ready ledger from PM-A1 forecast packets. Outcomes are pending
by default; Brier/log-loss values remain null until real resolution evidence is
attached. This script does not ingest live markets, provide financial advice,
place orders, use trading credentials, or claim profitability.
"""

from __future__ import annotations

import argparse
import json
from math import log
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.pm_a1_prediction_market_evidence_agent import CLAIM_FLAGS as PM_CLAIM_FLAGS  # noqa: E402

SCHEMA_VERSION = "monogate.pm_a1b_calibration_ledger.v0"
LEDGER_SCHEMA_VERSION = "monogate.prediction_market_calibration_ledger.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PM_A1B_CALIBRATION_LEDGER_PASS"

CLAIM_FLAGS = dict(PM_CLAIM_FLAGS)
CLAIM_FLAGS.update(
    {
        "calibrated_forecaster_claim": False,
        "positive_expected_value_claim": False,
        "outcome_scoring_performed": False,
        "live_market_ingestion_performed": False,
    }
)

NON_CLAIMS = [
    "PM-A1B is a calibration-ready ledger, not financial advice.",
    "PM-A1B does not claim profitable prediction, positive expected value, or calibrated skill.",
    "PM-A1B does not place orders or use authenticated trading endpoints.",
    "PM-A1B does not score unresolved markets as wins or losses.",
    "Brier and log-loss values remain null until resolution evidence is attached.",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def probability_bucket(probability: float) -> str:
    lower = int(min(9, max(0, probability * 10)))
    return f"{lower / 10:.1f}-{(lower + 1) / 10:.1f}"


def edge_bucket(edge: float) -> str:
    if edge <= -0.08:
        return "negative_large"
    if edge < -0.03:
        return "negative_small"
    if edge <= 0.03:
        return "near_market"
    if edge < 0.08:
        return "positive_small"
    return "positive_large"


def score_if_resolved(probability: float, outcome: bool | None) -> dict[str, float | None]:
    if outcome is None:
        return {"brierScore": None, "logLoss": None}
    y = 1.0 if outcome else 0.0
    p = min(0.999999, max(0.000001, probability))
    return {
        "brierScore": round((p - y) ** 2, 8),
        "logLoss": round(-(y * log(p) + (1.0 - y) * log(1.0 - p)), 8),
    }


def ledger_entry(packet: dict[str, Any]) -> dict[str, Any]:
    probability = float(packet["agentProbability"])
    outcome = packet.get("resolvedOutcome")
    if outcome is not None and not isinstance(outcome, bool):
        raise ValueError(f"resolvedOutcome must be boolean or null for {packet['marketId']}")
    scores = score_if_resolved(probability, outcome)
    outcome_status = "resolved" if outcome is not None else "pending_resolution"
    return {
        "marketId": packet["marketId"],
        "platform": packet["platform"],
        "category": packet["category"],
        "question": packet["question"],
        "forecastDate": packet["date"],
        "resolutionCloseTime": packet["resolution"]["closeTime"],
        "resolutionSource": packet["resolution"]["resolutionSource"],
        "settlementRisk": packet["resolution"]["settlementRisk"],
        "forecastProbability": probability,
        "marketPrice": float(packet["marketPrice"]),
        "estimatedEdge": float(packet["estimatedEdge"]),
        "confidence": packet["confidence"],
        "probabilityBucket": probability_bucket(probability),
        "edgeBucket": edge_bucket(float(packet["estimatedEdge"])),
        "outcomeStatus": outcome_status,
        "outcomeValue": outcome,
        "outcomeEvidencePath": packet.get("outcomeEvidencePath"),
        "eligibleForFutureScoring": outcome is None,
        "scoringStatus": "pending_resolution" if outcome is None else "scored",
        "brierScore": scores["brierScore"],
        "logLoss": scores["logLoss"],
        "tradePermission": packet["tradePermission"],
        "reviewFlags": packet.get("reviewFlags", []),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(entries: list[dict[str, Any]]) -> dict[str, Any]:
    pending = sum(1 for entry in entries if entry["outcomeStatus"] == "pending_resolution")
    resolved = sum(1 for entry in entries if entry["outcomeStatus"] == "resolved")
    buckets: dict[str, int] = {}
    platforms: dict[str, int] = {}
    for entry in entries:
        buckets[entry["probabilityBucket"]] = buckets.get(entry["probabilityBucket"], 0) + 1
        platforms[entry["platform"]] = platforms.get(entry["platform"], 0) + 1
    return {
        "ledgerEntryCount": len(entries),
        "pendingResolutionCount": pending,
        "resolvedCount": resolved,
        "scoredCount": sum(1 for entry in entries if entry["scoringStatus"] == "scored"),
        "probabilityBuckets": buckets,
        "platforms": platforms,
        "orderPlacementPerformed": False,
        "authenticatedTradingUsed": False,
        "liveMarketIngestionPerformed": False,
        "financialAdviceClaim": False,
        "profitableStrategyClaim": False,
        "calibratedForecasterClaim": False,
        "outcomeScoringPerformed": resolved > 0,
        "claimFlagsAllFalse": all(all(value is False for value in entry["claimFlags"].values()) for entry in entries),
    }


def build_ledger_payload(source_path: Path, forecast_packets: list[dict[str, Any]]) -> dict[str, Any]:
    entries = [ledger_entry(packet) for packet in forecast_packets]
    ledger = {
        "schemaVersion": LEDGER_SCHEMA_VERSION,
        "ledgerType": "prediction_market_calibration_ledger_v0",
        "date": DATE,
        "sourceForecastPath": str(source_path),
        "entries": entries,
        "summary": summarize(entries),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    return ledger


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "pm-a1b-calibration-ledger",
        "title": "PM-A1B Prediction Market Calibration Ledger",
        "reviewDecision": "calibration_ready_ledger_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "calibration_ledger_no_outcome_skill_or_trading_claim",
        "semanticReview": {
            "ledgerEntryCount": payload["summary"]["ledgerEntryCount"],
            "pendingResolutionCount": payload["summary"]["pendingResolutionCount"],
            "resolvedCount": payload["summary"]["resolvedCount"],
            "scoredCount": payload["summary"]["scoredCount"],
            "orderPlacementPerformed": False,
            "authenticatedTradingUsed": False,
            "financialAdviceClaim": False,
            "profitableStrategyClaim": False,
            "calibratedForecasterClaim": False,
        },
        "claimBoundary": "Calibration-ready ledger only; no outcome skill, profitable strategy, financial advice, or trading claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Creates one calibration ledger entry per PM-A1 forecast packet.",
            "Keeps unresolved outcomes pending with null Brier/log-loss values.",
            "Adds probability and edge buckets for future calibration analysis.",
            "Keeps trading, financial advice, profitability, and calibrated-skill flags false.",
        ],
        "validationCommands": [
            "python python/scripts/pm_a1b_calibration_ledger.py --build --strict",
            "python -m pytest -q python/tests/test_pm_a1b_calibration_ledger.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.pm_a1b.v0",
        "date": DATE,
        "title": "PM-A1B Calibration Ledger",
        "status": payload["status"],
        "summary": payload["summary"],
        "nextRecommendedSprint": "PM-A1C outcome resolver fixture",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PM-A1B Prediction Market Calibration Ledger",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PM-A1B converts read-only forecast packets into a scoring-ready",
        "calibration ledger. Outcomes are pending unless explicit resolution",
        "evidence is attached.",
        "",
        "## Ledger Entries",
        "",
        "| Market | Probability | Market price | Bucket | Outcome | Brier | Log loss |",
        "|---|---:|---:|---|---|---:|---:|",
    ]
    for entry in payload["ledger"]["entries"]:
        brier = "null" if entry["brierScore"] is None else f"{entry['brierScore']:.6f}"
        log_loss = "null" if entry["logLoss"] is None else f"{entry['logLoss']:.6f}"
        lines.append(
            f"| `{entry['marketId']}` | {entry['forecastProbability']:.4f} | "
            f"{entry['marketPrice']:.4f} | `{entry['probabilityBucket']}` | "
            f"`{entry['outcomeStatus']}` | {brier} | {log_loss} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Ledger entries: `{summary['ledgerEntryCount']}`",
            f"- Pending resolution: `{summary['pendingResolutionCount']}`",
            f"- Resolved: `{summary['resolvedCount']}`",
            f"- Scored: `{summary['scoredCount']}`",
            f"- Order placement performed: `{summary['orderPlacementPerformed']}`",
            f"- Authenticated trading used: `{summary['authenticatedTradingUsed']}`",
            f"- Calibrated forecaster claim: `{summary['calibratedForecasterClaim']}`",
            "",
            "## Boundary",
            "",
            "- No financial advice.",
            "- No profitable strategy claim.",
            "- No calibrated-skill claim.",
            "- No order placement or authenticated trading.",
            "- No Brier/log-loss scoring until outcomes are resolved.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_ledger(ledger: dict[str, Any]) -> None:
    if ledger.get("schemaVersion") != LEDGER_SCHEMA_VERSION:
        raise ValueError("invalid calibration ledger schema")
    if not ledger.get("entries"):
        raise ValueError("ledger must contain entries")
    for key, value in ledger.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"ledger claim flag must remain false: {key}")
    for entry in ledger["entries"]:
        if not 0 <= entry["forecastProbability"] <= 1:
            raise ValueError("forecast probability out of range")
        if not 0 <= entry["marketPrice"] <= 1:
            raise ValueError("market price out of range")
        if entry["outcomeStatus"] == "pending_resolution":
            if entry["outcomeValue"] is not None or entry["brierScore"] is not None or entry["logLoss"] is not None:
                raise ValueError(f"pending entry must not be scored: {entry['marketId']}")
        for key, value in entry.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"entry claim flag must remain false for {entry['marketId']}: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PM-A1B schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PM-A1B status")
    validate_ledger(payload["ledger"])
    summary = payload["summary"]
    if summary["ledgerEntryCount"] < 4:
        raise ValueError("expected at least 4 ledger entries")
    for key in [
        "orderPlacementPerformed",
        "authenticatedTradingUsed",
        "liveMarketIngestionPerformed",
        "financialAdviceClaim",
        "profitableStrategyClaim",
        "calibratedForecasterClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["outcomeScoringPerformed"] is not False:
        raise ValueError("fixture run should not score unresolved outcomes")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_ledger(
    forecast_path: Path,
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    source = load_json(forecast_path)
    forecast_packets = source["forecastPackets"]
    ledger = build_ledger_payload(forecast_path, forecast_packets)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceForecastPath": str(forecast_path),
        "ledger": ledger,
        "summary": ledger["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"pm_a1b_calibration_ledger_{stamp}.json"
    ledger_path = out_dir / f"prediction_market_calibration_ledger_{stamp}.json"
    report_path = report_dir / f"pm_a1b_calibration_ledger_{stamp}.md"
    evidence_path = evidence_dir / "pm_a1b_calibration_ledger.json"
    feed_path = command_feed_dir / f"pm_a1b_calibration_ledger_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "ledger": ledger,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "ledger_path": str(ledger_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--forecast-path",
        type=Path,
        default=ROOT / f"python/results/pm_a1_prediction_market_evidence_agent/pm_a1_prediction_market_evidence_agent_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/pm_a1b_calibration_ledger")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_ledger(args.forecast_path, args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("PM_A1B_CALIBRATION_LEDGER_OK")
    print(f"ledger_entries={built['payload']['summary']['ledgerEntryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
