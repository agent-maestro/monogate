#!/usr/bin/env python3
"""EML-A9.1 guard rule fixtures.

Creates expected input/output examples for A9 guard rules without changing
compiler behavior.
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

from scripts.eml_a9_compiler_guard_rules import CLAIM_FLAGS as A9_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a9_1_guard_rule_fixtures.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_guard_rule_fixture_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A9_1_GUARD_RULE_FIXTURES_PASS"

CLAIM_FLAGS = {
    **dict(A9_CLAIM_FLAGS),
    "guard_fixture_executed_as_compiler": False,
    "guard_analyzer_implemented": False,
}

NON_CLAIMS = [
    "A9.1 records expected guard-rule fixtures only.",
    "A9.1 does not change compiler behavior or implement guard analysis.",
    "A9.1 does not prove compiler correctness, EML advantage, runtime performance, public Atlas promotion, or deployment.",
]


def fixture_specs() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "proof_shape_subtraction_boundary_fixture_v0",
            "expression": "eml(log(v), exp(u))",
            "metadata": {"treeDepth": 2, "domainGuards": ["v > 0"], "claimIntent": "proof_shape", "runtimeProfile": "none"},
            "expectedDecision": "allow_proof_shape",
            "expectedRuleIds": ["prefer_eml_for_proof_shape_v0", "require_positive_log_domain_guard_v0"],
            "expectedLowering": None,
            "blockedClaims": ["runtime performance", "general EML superiority"],
        },
        {
            "fixtureId": "near_zero_expm1_fixture_v0",
            "expression": "eml(x,e)",
            "metadata": {"treeDepth": 1, "domainGuards": [], "claimIntent": "runtime", "runtimeProfile": "near_zero"},
            "expectedDecision": "recommend_protected_lowering",
            "expectedRuleIds": ["lower_expm1_near_zero_v0"],
            "expectedLowering": "expm1(x)",
            "blockedClaims": ["raw EML runtime win"],
        },
        {
            "fixtureId": "softplus_logaddexp_fixture_v0",
            "expression": "ln(exp(a)+exp(b))",
            "metadata": {"treeDepth": 3, "domainGuards": ["exp(a)+exp(b) > 0"], "claimIntent": "runtime", "runtimeProfile": "log_sum_exp"},
            "expectedDecision": "recommend_protected_lowering",
            "expectedRuleIds": ["lower_logaddexp_softplus_v0"],
            "expectedLowering": "logaddexp(a,b)",
            "blockedClaims": ["raw EML runtime win"],
        },
        {
            "fixtureId": "missing_log_domain_guard_fixture_v0",
            "expression": "eml(x,y)",
            "metadata": {"treeDepth": 1, "domainGuards": [], "claimIntent": "public_expression", "runtimeProfile": "unknown", "usesLogArgument": True},
            "expectedDecision": "block_missing_domain_guard",
            "expectedRuleIds": ["require_positive_log_domain_guard_v0"],
            "expectedLowering": None,
            "blockedClaims": ["public expression claim", "runtime lowering"],
        },
        {
            "fixtureId": "deep_tree_depth_12_fixture_v0",
            "expression": "fold_12(z -> eml(z,e))",
            "metadata": {"treeDepth": 12, "domainGuards": [], "claimIntent": "runtime", "runtimeProfile": "deep_tree"},
            "expectedDecision": "block_unstable_deep_tree",
            "expectedRuleIds": ["block_unstable_deep_tree_v0"],
            "expectedLowering": None,
            "blockedClaims": ["runtime performance", "public advantage"],
        },
        {
            "fixtureId": "advantage_claim_without_packets_fixture_v0",
            "expression": "eml candidate claim",
            "metadata": {"treeDepth": 1, "domainGuards": ["candidate supplied"], "claimIntent": "eml_advantage", "hasTrialPacket": False, "hasNegativeControlPacket": False},
            "expectedDecision": "block_claim_until_evidence",
            "expectedRuleIds": ["require_trial_packet_before_advantage_claim_v0"],
            "expectedLowering": None,
            "blockedClaims": ["EML advantage", "public Atlas promotion"],
        },
    ]


def packet_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_guard_rule_fixture_packet_v0",
        "date": DATE,
        **spec,
        "compilerBehaviorChanged": False,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_decision: dict[str, int] = {}
    for packet in packets:
        by_decision[packet["expectedDecision"]] = by_decision.get(packet["expectedDecision"], 0) + 1
    return {
        "fixtureCount": len(packets),
        "byExpectedDecision": by_decision,
        "compilerBehaviorChanged": False,
        "guardAnalyzerImplemented": False,
        "compilerCorrectnessClaim": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_fixtures(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    packets = [packet_from_spec(spec) for spec in fixture_specs()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "fixtureSetId": "eml_a9_1_guard_rule_fixtures",
        "fixturePackets": packets,
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
    result_path = out_dir / f"eml_a9_1_guard_rule_fixtures_{stamp}.json"
    report_path = report_dir / f"eml_a9_1_guard_rule_fixtures_{stamp}.md"
    evidence_path = evidence_dir / "eml_a9_1_guard_rule_fixtures.json"
    feed_path = command_feed_dir / f"eml_a9_1_guard_rule_fixtures_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        (packet_dir / f"{packet['fixtureId']}_guard_fixture_{stamp}.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a9-1-guard-rule-fixtures",
        "title": "EML-A9.1 Guard Rule Fixtures",
        "reviewDecision": "guard_rule_fixtures_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "fixtures_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected guard fixtures only; no analyzer implementation, compiler behavior change, or compiler correctness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "validationCommands": ["python python/scripts/eml_a9_1_guard_rule_fixtures.py --build --strict"],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a9_1.v0",
        "date": DATE,
        "title": "EML-A9.1 Guard Rule Fixtures",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A9.2 run deterministic guard decision analyzer",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = ["# EML-A9.1 Guard Rule Fixtures", "", f"Date: {DATE}", "", f"Status: `{payload['status']}`", "", "| Fixture | Expected decision | Rules |", "|---|---|---|"]
    for packet in payload["fixturePackets"]:
        lines.append(f"| `{packet['fixtureId']}` | `{packet['expectedDecision']}` | `{', '.join(packet['expectedRuleIds'])}` |")
    lines.extend(["", "## Boundary", "", "- Fixtures only.", "- No compiler behavior change, analyzer implementation, compiler correctness proof, runtime performance, or EML advantage claim.", ""])
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A9.1 payload")
    summary = payload["summary"]
    if summary["fixtureCount"] < 6:
        raise ValueError("expected at least six guard fixtures")
    for key in ["compilerBehaviorChanged", "guardAnalyzerImplemented", "compilerCorrectnessClaim"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["fixturePackets"]:
        if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
            raise ValueError("invalid fixture schema")
        if packet["compilerBehaviorChanged"] is not False:
            raise ValueError("fixture must not change compiler behavior")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a9_1_guard_rule_fixtures")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_guard_rule_fixture_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_fixtures(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A9_1_GUARD_RULE_FIXTURES_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
