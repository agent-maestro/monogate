#!/usr/bin/env python3
"""PM-A1 read-only prediction market evidence agent.

This builds deterministic forecast packets from fixture market data. It does
not use trading credentials, place orders, provide financial advice, or claim
profitable prediction. The purpose is to prove that Monogate's evidence grammar
can wrap prediction-market reasoning before any trading integration exists.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.pm_a1_prediction_market_evidence_agent.v0"
FORECAST_SCHEMA_VERSION = "monogate.prediction_market_forecast_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PM_A1_PREDICTION_MARKET_EVIDENCE_AGENT_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "financial_advice_claim": False,
    "profitable_strategy_claim": False,
    "autonomous_trading_claim": False,
    "order_placement_performed": False,
    "authenticated_trading_used": False,
    "trade_recommendation_claim": False,
    "certified_safety_claim": False,
    "production_controller_claim": False,
    "theorem_proof_claim": False,
}

NON_CLAIMS = [
    "PM-A1 is not financial advice.",
    "PM-A1 does not claim profitable prediction or market edge.",
    "PM-A1 does not place orders or use authenticated trading endpoints.",
    "PM-A1 requires human review before any trade decision.",
    "PM-A1 uses deterministic fixture data by default, not live market execution.",
]

AMBIGUITY_TERMS = [
    "flagship",
    "significant",
    "major",
    "named",
    "substantially",
    "approximately",
    "rumor",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out[:90] or "market"


def clamp_probability(value: float) -> float:
    return min(0.99, max(0.01, value))


def parse_resolution(market: dict[str, Any]) -> dict[str, Any]:
    criteria = market.get("resolutionCriteria", "")
    question = market.get("question", "")
    text = f"{question} {criteria}".lower()
    ambiguity_flags = [term for term in AMBIGUITY_TERMS if term in text]
    has_deadline = bool(market.get("closeTime")) or " by " in text or "next " in text
    source = market.get("resolutionSource", "")
    return {
        "resolutionCriteriaUnderstood": bool(criteria and source and has_deadline),
        "resolutionSource": source,
        "closeTime": market.get("closeTime"),
        "ambiguityFlags": ambiguity_flags,
        "settlementRisk": "medium" if ambiguity_flags else "low",
        "parsedBoundary": {
            "hasDeadline": has_deadline,
            "hasNamedResolutionSource": bool(source),
            "requiresExactResolverWordingReview": bool(ambiguity_flags),
        },
    }


def evidence_quality(evidence: list[dict[str, Any]], resolution: dict[str, Any]) -> dict[str, Any]:
    total_weight = sum(float(item.get("weight", 0.0)) for item in evidence)
    stale_count = sum(1 for item in evidence if int(item.get("stalenessDays", 999)) > 14)
    quality = "medium"
    if total_weight >= 0.75 and stale_count == 0 and resolution["settlementRisk"] == "low":
        quality = "high"
    if total_weight < 0.45 or stale_count > 0 or resolution["settlementRisk"] == "medium":
        quality = "low"
    return {
        "evidenceItemCount": len(evidence),
        "totalEvidenceWeight": round(total_weight, 4),
        "staleEvidenceCount": stale_count,
        "evidenceQuality": quality,
    }


def forecast_probability(market: dict[str, Any]) -> dict[str, Any]:
    market_price = float(market["marketPrice"])
    evidence = market.get("evidence", [])
    market_prior_weight = 0.42
    weighted_sum = market_price * market_prior_weight
    total_weight = market_prior_weight
    contributions = [
        {
            "sourceId": "market_price_prior",
            "probabilitySignal": round(market_price, 4),
            "weight": market_prior_weight,
            "contribution": round(market_price * market_prior_weight, 6),
        }
    ]
    for item in evidence:
        signal = clamp_probability(float(item["probabilitySignal"]))
        weight = max(0.0, float(item["weight"]))
        weighted_sum += signal * weight
        total_weight += weight
        contributions.append(
            {
                "sourceId": item["sourceId"],
                "probabilitySignal": round(signal, 4),
                "weight": round(weight, 4),
                "contribution": round(signal * weight, 6),
            }
        )
    probability = clamp_probability(weighted_sum / total_weight)
    return {
        "agentProbability": round(probability, 4),
        "estimatedEdge": round(probability - market_price, 4),
        "marketPriorWeight": market_prior_weight,
        "contributions": contributions,
    }


def confidence_for(edge: float, quality: dict[str, Any], resolution: dict[str, Any]) -> str:
    abs_edge = abs(edge)
    if resolution["settlementRisk"] != "low":
        return "low"
    if quality["evidenceQuality"] == "high" and abs_edge >= 0.08:
        return "high"
    if quality["evidenceQuality"] in {"medium", "high"} and abs_edge >= 0.04:
        return "medium"
    return "low"


def review_flags(packet: dict[str, Any]) -> list[str]:
    flags = []
    if packet["resolution"]["settlementRisk"] != "low":
        flags.append("review_resolution_ambiguity")
    if abs(packet["estimatedEdge"]) < 0.04:
        flags.append("edge_below_review_threshold")
    if packet["liquidityUsd"] < 50000:
        flags.append("low_liquidity_market")
    if packet["confidence"] == "low":
        flags.append("low_confidence_forecast")
    return flags or ["human_review_required_even_without_flags"]


def forecast_packet(market: dict[str, Any]) -> dict[str, Any]:
    resolution = parse_resolution(market)
    quality = evidence_quality(market.get("evidence", []), resolution)
    forecast = forecast_probability(market)
    confidence = confidence_for(forecast["estimatedEdge"], quality, resolution)
    packet = {
        "schemaVersion": FORECAST_SCHEMA_VERSION,
        "packetType": "prediction_market_forecast_packet_v0",
        "date": DATE,
        "marketId": market["marketId"],
        "platform": market["platform"],
        "category": market["category"],
        "question": market["question"],
        "marketPrice": round(float(market["marketPrice"]), 4),
        "agentProbability": forecast["agentProbability"],
        "estimatedEdge": forecast["estimatedEdge"],
        "confidence": confidence,
        "liquidityUsd": float(market["liquidityUsd"]),
        "resolution": resolution,
        "evidenceQuality": quality,
        "evidence": market.get("evidence", []),
        "forecastContributions": forecast["contributions"],
        "tradePermission": "human_review_required",
        "executionPolicy": {
            "readOnly": True,
            "orderPlacementDisabled": True,
            "authenticatedTradingUsed": False,
            "tradingKeysRequired": False,
            "humanApprovalRequired": True,
        },
        "calibrationStatus": {
            "outcomeKnown": False,
            "eligibleForBrierScoreAfterResolution": True,
            "eligibleForLogLossAfterResolution": True,
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    packet["reviewFlags"] = review_flags(packet)
    return packet


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "pm-a1-prediction-market-evidence-agent",
        "title": "PM-A1 Read-Only Prediction Market Evidence Agent",
        "reviewDecision": "read_only_candidate_forecast_packets_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "read_only_fixture_forecast_packets_no_trading_claim",
        "semanticReview": {
            "forecastPacketCount": payload["summary"]["forecastPacketCount"],
            "platforms": payload["summary"]["platforms"],
            "orderPlacementPerformed": False,
            "authenticatedTradingUsed": False,
            "humanReviewRequired": True,
        },
        "claimBoundary": "Read-only candidate forecast packets only; no financial advice, autonomous trading, or profitable strategy claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Parses market resolution criteria into a reviewable boundary.",
            "Combines market price and fixture evidence into a deterministic candidate probability.",
            "Keeps trade permission at human_review_required for every packet.",
            "Creates calibration-ready logs without placing orders.",
        ],
        "validationCommands": [
            "python python/scripts/pm_a1_prediction_market_evidence_agent.py --build --strict",
            "python -m pytest -q python/tests/test_pm_a1_prediction_market_evidence_agent.py",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PM-A1 Read-Only Prediction Market Evidence Agent",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PM-A1 tests whether Monogate evidence packets can govern prediction-market",
        "research before any live trading integration exists.",
        "",
        "## Forecast Packets",
        "",
        "| Market | Platform | Market price | Agent probability | Edge | Confidence | Trade permission |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for packet in payload["forecastPackets"]:
        lines.append(
            f"| `{packet['marketId']}` | `{packet['platform']}` | "
            f"{packet['marketPrice']:.4f} | {packet['agentProbability']:.4f} | "
            f"{packet['estimatedEdge']:.4f} | `{packet['confidence']}` | `{packet['tradePermission']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Forecast packets: `{payload['summary']['forecastPacketCount']}`",
            f"- Platforms: `{', '.join(payload['summary']['platforms'])}`",
            f"- Human review required for all packets: `{payload['summary']['humanReviewRequiredForAll']}`",
            f"- Order placement performed: `{payload['summary']['orderPlacementPerformed']}`",
            f"- Authenticated trading used: `{payload['summary']['authenticatedTradingUsed']}`",
            "",
            "## Boundary",
            "",
            "- No financial advice.",
            "- No autonomous trading.",
            "- No order placement.",
            "- No profitable strategy claim.",
            "- Fixture data by default; live public ingestion should be a separate gated step.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_forecast_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != FORECAST_SCHEMA_VERSION:
        raise ValueError("invalid forecast packet schema")
    if not 0 <= packet["marketPrice"] <= 1:
        raise ValueError("market price out of range")
    if not 0 <= packet["agentProbability"] <= 1:
        raise ValueError("agent probability out of range")
    if round(packet["agentProbability"] - packet["marketPrice"], 4) != packet["estimatedEdge"]:
        raise ValueError("estimated edge mismatch")
    if packet["tradePermission"] != "human_review_required":
        raise ValueError("trade permission must require human review")
    execution = packet["executionPolicy"]
    if execution["readOnly"] is not True:
        raise ValueError("packet must be read-only")
    if execution["orderPlacementDisabled"] is not True:
        raise ValueError("order placement must be disabled")
    if execution["authenticatedTradingUsed"] is not False:
        raise ValueError("authenticated trading must remain false")
    for key, value in packet.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PM-A1 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PM-A1 status")
    if payload["summary"]["forecastPacketCount"] < 4:
        raise ValueError("expected at least 4 forecast packets")
    if payload["summary"]["orderPlacementPerformed"] is not False:
        raise ValueError("order placement must remain false")
    if payload["summary"]["authenticatedTradingUsed"] is not False:
        raise ValueError("authenticated trading must remain false")
    if payload["summary"]["humanReviewRequiredForAll"] is not True:
        raise ValueError("all packets must require human review")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")
    for packet in payload["forecastPackets"]:
        validate_forecast_packet(packet)


def build_agent(
    fixture_path: Path,
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
) -> dict[str, Any]:
    fixture = load_json(fixture_path)
    packets = [forecast_packet(market) for market in fixture["markets"]]
    platforms = sorted({packet["platform"] for packet in packets})
    summary = {
        "forecastPacketCount": len(packets),
        "platforms": platforms,
        "humanReviewRequiredForAll": all(packet["tradePermission"] == "human_review_required" for packet in packets),
        "orderPlacementPerformed": False,
        "authenticatedTradingUsed": False,
        "readOnly": True,
        "maxAbsoluteEdge": round(max(abs(packet["estimatedEdge"]) for packet in packets), 4),
    }
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceFixturePath": str(fixture_path),
        "forecastPackets": packets,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    evidence = build_evidence_packet(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"pm_a1_prediction_market_evidence_agent_{stamp}.json"
    report_path = report_dir / f"pm_a1_prediction_market_evidence_agent_{stamp}.md"
    evidence_path = evidence_dir / "pm_a1_prediction_market_evidence_agent.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{slug(packet['marketId'])}_forecast_packet_{stamp}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--fixture-path",
        type=Path,
        default=ROOT / "python/fixtures/prediction_markets/pm_a1_fixture_markets.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/pm_a1_prediction_market_evidence_agent")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/prediction_market_forecast_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_agent(args.fixture_path, args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("PM_A1_PREDICTION_MARKET_EVIDENCE_AGENT_OK")
    print(f"forecast_packets={built['payload']['summary']['forecastPacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
