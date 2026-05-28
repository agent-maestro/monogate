#!/usr/bin/env python3
"""EML-A8.4 negative-control discipline.

Registers the cases where EML should not win and ties them to existing A8.1
and A8.3 evidence. This is a guardrail over the Advantage Lab, not a new
superiority claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a8_4_negative_control_discipline.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_negative_control_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A8_4_NEGATIVE_CONTROL_DISCIPLINE_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "negative_controls_exhaustive": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "runtime_performance_claim": False,
    "public_ready": False,
    "public_atlas_promotion": False,
    "theorem_discovery_claim": False,
    "compiler_correctness_claim": False,
    "deploy_performed": False,
}

NON_CLAIMS = [
    "A8.4 registers negative controls for reviewer discipline.",
    "A8.4 does not claim the controls are exhaustive.",
    "A8.4 does not prove EML advantage, broad EML superiority, theorem discovery, compiler correctness, runtime performance, public Atlas promotion, or deployment.",
]


def control_specs() -> list[dict[str, Any]]:
    return [
        {
            "controlId": "expm1_runtime_anti_example_v1",
            "expectedWinner": "standard",
            "controlClass": "protected_runtime",
            "evidenceStatus": "confirmed",
            "sourceEvidence": "reports/eml_a8_3_candidate_trial_runner_2026_05_27.md",
            "reason": "Protected expm1 beats raw exp(x)-1 near zero.",
        },
        {
            "controlId": "logaddexp_negative_control_v0",
            "expectedWinner": "standard",
            "controlClass": "protected_runtime",
            "evidenceStatus": "confirmed",
            "sourceEvidence": "reports/eml_a8_1_holdout_advantage_benchmark_2026_05_27.md",
            "reason": "Protected logaddexp-style runtime remains the expected stable lowering.",
        },
        {
            "controlId": "gaussian_bumps_negative_control_v0",
            "expectedWinner": "standard",
            "controlClass": "non_eml_structure",
            "evidenceStatus": "confirmed",
            "sourceEvidence": "reports/eml_a8_1_holdout_advantage_benchmark_2026_05_27.md",
            "reason": "Gaussian bumps are intentionally not an EML-native advantage case.",
        },
        {
            "controlId": "arbitrary_polynomial_negative_control_v0",
            "expectedWinner": "standard",
            "controlClass": "non_eml_structure",
            "evidenceStatus": "confirmed",
            "sourceEvidence": "reports/eml_a8_1_holdout_advantage_benchmark_2026_05_27.md",
            "reason": "Arbitrary polynomial structure should not be rebranded as an EML moat.",
        },
        {
            "controlId": "unstable_deep_tree_negative_control_v0",
            "expectedWinner": "blocked",
            "controlClass": "unstable_deep_tree",
            "evidenceStatus": "registered_for_next_holdout",
            "sourceEvidence": "docs/eml_advantage_lab_2026_05_27.md",
            "reason": "Deep EML trees can amplify finite-precision and domain failures; this must be tested before any depth-scaling claim.",
        },
    ]


def packet_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_negative_control_packet_v0",
        "date": DATE,
        **spec,
        "mustFailIf": [
            "future lab marks this case as EML win without a stronger validator",
            "future public copy treats this control as an EML advantage result",
            "future packet flips any claim flag to true",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for packet in packets:
        by_class[packet["controlClass"]] = by_class.get(packet["controlClass"], 0) + 1
        by_status[packet["evidenceStatus"]] = by_status.get(packet["evidenceStatus"], 0) + 1
    return {
        "controlCount": len(packets),
        "byControlClass": by_class,
        "byEvidenceStatus": by_status,
        "confirmedControlCount": by_status.get("confirmed", 0),
        "registeredForNextHoldoutCount": by_status.get("registered_for_next_holdout", 0),
        "negativeControlsExhaustive": False,
        "emlAdvantageProved": False,
        "publicAtlasPromotion": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_guard(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    packets = [packet_from_spec(spec) for spec in control_specs()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "guardId": "eml_a8_4_negative_control_discipline",
        "controlPackets": packets,
        "summary": summarize(packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a8_4_negative_control_discipline_{stamp}.json"
    report_path = report_dir / f"eml_a8_4_negative_control_discipline_{stamp}.md"
    evidence_path = evidence_dir / "eml_a8_4_negative_control_discipline.json"
    feed_path = command_feed_dir / f"eml_a8_4_negative_control_discipline_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{packet['controlId']}_negative_control_{stamp}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a8-4-negative-control-discipline",
        "title": "EML-A8.4 Negative-Control Discipline",
        "reviewDecision": "negative_control_guard_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "negative_control_registry_no_superiority_claim",
        "semanticReview": {
            "controlCount": payload["summary"]["controlCount"],
            "confirmedControlCount": payload["summary"]["confirmedControlCount"],
            "negativeControlsExhaustive": False,
        },
        "claimBoundary": "Negative-control guard only; no exhaustive falsification, EML advantage proof, runtime performance, or public promotion claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Registers protected runtime cases where standard math should win.",
            "Keeps non-EML structures from being overinterpreted as EML moat evidence.",
            "Adds unstable deep trees as an explicit next holdout target.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a8_4_negative_control_discipline.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a8_4_negative_control_discipline.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a8_4.v0",
        "date": DATE,
        "title": "EML-A8.4 Negative-Control Discipline",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Run unstable_deep_tree_negative_control_v0 in the next holdout benchmark",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A8.4 Negative-Control Discipline",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A8.4 records the cases where EML should lose or remain blocked.",
        "This prevents the Advantage Lab from becoming a one-way promotion tool.",
        "",
        "| Control | Class | Expected winner | Evidence status |",
        "|---|---|---|---|",
    ]
    for packet in payload["controlPackets"]:
        lines.append(
            f"| `{packet['controlId']}` | `{packet['controlClass']}` | "
            f"`{packet['expectedWinner']}` | `{packet['evidenceStatus']}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Controls: `{summary['controlCount']}`",
            f"- Confirmed controls: `{summary['confirmedControlCount']}`",
            f"- Registered for next holdout: `{summary['registeredForNextHoldoutCount']}`",
            f"- Negative controls exhaustive: `{summary['negativeControlsExhaustive']}`",
            f"- EML advantage proved: `{summary['emlAdvantageProved']}`",
            "",
            "## Boundary",
            "",
            "- Negative-control guard only.",
            "- No exhaustive falsification, public promotion, broad EML superiority, runtime performance, theorem discovery, or compiler correctness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A8.4 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid A8.4 status")
    summary = payload["summary"]
    if summary["controlCount"] < 5:
        raise ValueError("expected at least five negative controls")
    if summary["confirmedControlCount"] < 4:
        raise ValueError("expected at least four confirmed controls")
    if summary["registeredForNextHoldoutCount"] < 1:
        raise ValueError("expected one next-holdout registration")
    for key in ["negativeControlsExhaustive", "emlAdvantageProved", "publicAtlasPromotion"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["controlPackets"]:
        if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid control packet schema: {packet.get('controlId')}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['controlId']}: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a8_4_negative_control_discipline")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_negative_control_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_guard(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A8_4_NEGATIVE_CONTROL_DISCIPLINE_OK")
    print(f"controls={built['payload']['summary']['controlCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
