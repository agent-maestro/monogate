#!/usr/bin/env python3
"""RT-A1 RAMPART compatibility spike.

Converts RAMPART-style red-team fixture results into Monogate evidence packets.
This script does not install RAMPART, call live models, use API keys, run
private agents, deploy, trade, publish, or claim certified safety.
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

SCHEMA_VERSION = "monogate.rt_a1_rampart_compatibility_spike.v0"
REDTEAM_PACKET_SCHEMA_VERSION = "monogate.rampart_redteam_evidence_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "RT_A1_RAMPART_COMPATIBILITY_SPIKE_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "certified_safety_claim": False,
    "production_security_claim": False,
    "comprehensive_robustness_claim": False,
    "live_rampart_run_claim": False,
    "live_model_call_performed": False,
    "api_key_used": False,
    "deploy_performed": False,
    "trade_performed": False,
    "hardware_action_performed": False,
    "private_cockpit_leakage_validated_safe": False,
}

NON_CLAIMS = [
    "RT-A1 is a fixture-first compatibility spike, not a live RAMPART run.",
    "RT-A1 does not claim certified safety or comprehensive robustness.",
    "RT-A1 does not use API keys, live model calls, deployment, trading, or hardware.",
    "Passing fixtures support candidate robustness evidence only.",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out[:100] or "redteam"


def packet_from_result(result: dict[str, Any]) -> dict[str, Any]:
    verdict = result["evaluatorVerdict"]
    if verdict not in {"pass", "fail"}:
        raise ValueError(f"invalid evaluator verdict: {verdict}")
    if verdict == "fail" and not result.get("violatedPolicies"):
        raise ValueError(f"failing result must list violated policies: {result['resultId']}")
    return {
        "schemaVersion": REDTEAM_PACKET_SCHEMA_VERSION,
        "packetType": "rampart_redteam_evidence_packet_v0",
        "date": DATE,
        "resultId": result["resultId"],
        "sourceFramework": "microsoft/RAMPART-compatible-fixture",
        "liveRampartRun": False,
        "targetAgent": result["targetAgent"],
        "attackCategory": result["attackCategory"],
        "prompt": result["prompt"],
        "expectedPolicy": result["expectedPolicy"],
        "observedBehavior": result["observedBehavior"],
        "evaluatorVerdict": verdict,
        "violatedPolicies": result.get("violatedPolicies", []),
        "recommendedRhAction": result["recommendedRhAction"],
        "evidenceStrength": result["evidenceStrength"],
        "publicRobustnessClaimAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts: dict[str, int] = {}
    categories: dict[str, int] = {}
    for packet in packets:
        verdicts[packet["evaluatorVerdict"]] = verdicts.get(packet["evaluatorVerdict"], 0) + 1
        categories[packet["attackCategory"]] = categories.get(packet["attackCategory"], 0) + 1
    return {
        "redteamPacketCount": len(packets),
        "verdicts": verdicts,
        "attackCategories": categories,
        "failingPacketCount": verdicts.get("fail", 0),
        "passingPacketCount": verdicts.get("pass", 0),
        "liveRampartRun": False,
        "liveModelCallsPerformed": False,
        "apiKeysUsed": False,
        "deployPerformed": False,
        "tradePerformed": False,
        "hardwareActionPerformed": False,
        "publicRobustnessClaimAllowed": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "rt-a1-rampart-compatibility-spike",
        "title": "RT-A1 RAMPART Compatibility Spike",
        "reviewDecision": "rampart_fixture_evidence_packets_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "fixture_redteam_compatibility_no_live_rampart_or_safety_claim",
        "semanticReview": {
            "redteamPacketCount": payload["summary"]["redteamPacketCount"],
            "verdicts": payload["summary"]["verdicts"],
            "liveRampartRun": False,
            "liveModelCallsPerformed": False,
            "apiKeysUsed": False,
            "publicRobustnessClaimAllowed": False,
        },
        "claimBoundary": "RAMPART-compatible fixture conversion only; no live RAMPART execution, no certified safety, and no comprehensive robustness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Converts RAMPART-style red-team results into Monogate evidence packets.",
            "Routes failures toward RH-A1 blocked public claims.",
            "Keeps all live-run, secret, safety, deployment, trading, and hardware flags false.",
        ],
        "validationCommands": [
            "python python/scripts/rt_a1_rampart_compatibility_spike.py --build --strict",
            "python -m pytest -q python/tests/test_rt_a1_rampart_compatibility_spike.py",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# RT-A1 RAMPART Compatibility Spike",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "RT-A1 converts RAMPART-style red-team results into Monogate evidence",
        "packets. It is fixture-first and does not execute live RAMPART tests.",
        "",
        "## Red-Team Packets",
        "",
        "| Result | Target | Attack category | Verdict | RH action |",
        "|---|---|---|---|---|",
    ]
    for packet in payload["redteamPackets"]:
        lines.append(
            f"| `{packet['resultId']}` | `{packet['targetAgent']}` | `{packet['attackCategory']}` | "
            f"`{packet['evaluatorVerdict']}` | `{packet['recommendedRhAction']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Red-team packets: `{payload['summary']['redteamPacketCount']}`",
            f"- Passing packets: `{payload['summary']['passingPacketCount']}`",
            f"- Failing packets: `{payload['summary']['failingPacketCount']}`",
            f"- Live RAMPART run: `{payload['summary']['liveRampartRun']}`",
            f"- Live model calls: `{payload['summary']['liveModelCallsPerformed']}`",
            f"- API keys used: `{payload['summary']['apiKeysUsed']}`",
            f"- Public robustness claim allowed: `{payload['summary']['publicRobustnessClaimAllowed']}`",
            "",
            "## Boundary",
            "",
            "- Fixture compatibility only.",
            "- No certified safety or comprehensive robustness claim.",
            "- No secrets, deployment, trading, or hardware.",
            "- RAMPART fixture failures must block public robustness claims.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_redteam_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != REDTEAM_PACKET_SCHEMA_VERSION:
        raise ValueError("invalid red-team packet schema")
    if packet["evaluatorVerdict"] == "fail" and packet["recommendedRhAction"] != "blocked_public_claim":
        raise ValueError("failing red-team fixtures must recommend blocked_public_claim")
    if packet["publicRobustnessClaimAllowed"] is not False:
        raise ValueError("public robustness claim must remain false")
    for key, value in packet.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false for {packet['resultId']}: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid RT-A1 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid RT-A1 status")
    if payload["summary"]["redteamPacketCount"] < 4:
        raise ValueError("expected at least 4 red-team packets")
    for key in [
        "liveRampartRun",
        "liveModelCallsPerformed",
        "apiKeysUsed",
        "deployPerformed",
        "tradePerformed",
        "hardwareActionPerformed",
        "publicRobustnessClaimAllowed",
    ]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    if payload["summary"]["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")
    for packet in payload["redteamPackets"]:
        validate_redteam_packet(packet)


def build_spike(
    fixture_path: Path,
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
) -> dict[str, Any]:
    fixture = load_json(fixture_path)
    packets = [packet_from_result(result) for result in fixture["results"]]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceFixturePath": str(fixture_path),
        "redteamPackets": packets,
        "summary": summarize(packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"rt_a1_rampart_compatibility_spike_{stamp}.json"
    report_path = report_dir / f"rt_a1_rampart_compatibility_spike_{stamp}.md"
    evidence_path = evidence_dir / "rt_a1_rampart_compatibility_spike.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{slug(packet['resultId'])}_rampart_redteam_packet_{stamp}.json"
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
    parser.add_argument("--fixture-path", type=Path, default=ROOT / "python/fixtures/rampart/rt_a1_rampart_fixture_results.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/rt_a1_rampart_compatibility_spike")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/rampart_redteam_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_spike(args.fixture_path, args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("RT_A1_RAMPART_COMPATIBILITY_SPIKE_OK")
    print(f"redteam_packets={built['payload']['summary']['redteamPacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
