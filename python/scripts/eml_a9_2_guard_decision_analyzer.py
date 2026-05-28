#!/usr/bin/env python3
"""EML-A9.2 guard decision analyzer.

Runs deterministic guard decisions over A9.1 fixtures. This is still not
compiler behavior; it is a reviewable analyzer fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_a9_1_guard_rule_fixtures import CLAIM_FLAGS as FIXTURE_CLAIM_FLAGS, build_fixtures  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a9_2_guard_decision_analyzer.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_guard_decision_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A9_2_GUARD_DECISION_ANALYZER_PASS"

CLAIM_FLAGS = {
    **dict(FIXTURE_CLAIM_FLAGS),
    "compiler_behavior_changed": False,
    "compiler_correctness_claim": False,
    "guard_analyzer_production_ready": False,
}

NON_CLAIMS = [
    "A9.2 runs a deterministic fixture analyzer only.",
    "A9.2 does not change compiler behavior or prove compiler correctness.",
    "A9.2 does not claim production readiness, EML advantage, runtime performance, public Atlas promotion, or deployment.",
]


def load_fixtures() -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="monogate_a9_2_fixtures_") as tmp:
        root = Path(tmp)
        built = build_fixtures(
            root / "fixtures",
            root / "fixture_packets",
            root / "reports",
            root / "evidence",
            root / "feeds",
        )
        return built["payload"]["fixturePackets"]


def analyze_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    meta = fixture["metadata"]
    expression = fixture["expression"]
    matched: list[str] = []
    decision = "allow_proof_shape"
    lowering = None
    reason = "Expression is allowed only for proof/search/teaching shape."

    if meta.get("claimIntent") == "eml_advantage" and not (meta.get("hasTrialPacket") and meta.get("hasNegativeControlPacket")):
        decision = "block_claim_until_evidence"
        matched = ["require_trial_packet_before_advantage_claim_v0"]
        reason = "Advantage claim is missing trial/control packets."
    elif int(meta.get("treeDepth", 0)) >= 10 or meta.get("runtimeProfile") == "deep_tree":
        decision = "block_unstable_deep_tree"
        matched = ["block_unstable_deep_tree_v0"]
        reason = "Deep EML tree needs holdout evidence before runtime/public surfacing."
    elif meta.get("usesLogArgument") and not meta.get("domainGuards"):
        decision = "block_missing_domain_guard"
        matched = ["require_positive_log_domain_guard_v0"]
        reason = "Log-domain use has no positive-domain guard."
    elif expression == "eml(x,e)" and meta.get("runtimeProfile") == "near_zero":
        decision = "recommend_protected_lowering"
        matched = ["lower_expm1_near_zero_v0"]
        lowering = "expm1(x)"
        reason = "Protected expm1 is required near zero."
    elif "ln(exp(a)+exp(b))" in expression or meta.get("runtimeProfile") == "log_sum_exp":
        decision = "recommend_protected_lowering"
        matched = ["lower_logaddexp_softplus_v0"]
        lowering = "logaddexp(a,b)"
        reason = "Protected logaddexp-style lowering is required."
    elif meta.get("claimIntent") == "proof_shape" and meta.get("domainGuards"):
        decision = "allow_proof_shape"
        matched = ["prefer_eml_for_proof_shape_v0", "require_positive_log_domain_guard_v0"]
        reason = "Proof-shape use is allowed because domain guards are explicit."

    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_guard_decision_packet_v0",
        "date": DATE,
        "fixtureId": fixture["fixtureId"],
        "expression": expression,
        "decision": decision,
        "matchedRuleIds": matched,
        "recommendedLowering": lowering,
        "reason": reason,
        "expectedDecision": fixture["expectedDecision"],
        "expectedRuleIds": fixture["expectedRuleIds"],
        "expectedDecisionMatched": decision == fixture["expectedDecision"],
        "expectedRulesMatched": set(matched) == set(fixture["expectedRuleIds"]),
        "compilerBehaviorChanged": False,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_decision: dict[str, int] = {}
    for packet in packets:
        by_decision[packet["decision"]] = by_decision.get(packet["decision"], 0) + 1
    return {
        "decisionCount": len(packets),
        "byDecision": by_decision,
        "expectedDecisionMatchCount": sum(1 for packet in packets if packet["expectedDecisionMatched"]),
        "expectedRuleMatchCount": sum(1 for packet in packets if packet["expectedRulesMatched"]),
        "allFixturesMatched": all(packet["expectedDecisionMatched"] and packet["expectedRulesMatched"] for packet in packets),
        "compilerBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_decisions(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    packets = [analyze_fixture(fixture) for fixture in load_fixtures()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "analyzerId": "eml_a9_2_guard_decision_analyzer",
        "decisionPackets": packets,
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
    result_path = out_dir / f"eml_a9_2_guard_decision_analyzer_{stamp}.json"
    report_path = report_dir / f"eml_a9_2_guard_decision_analyzer_{stamp}.md"
    evidence_path = evidence_dir / "eml_a9_2_guard_decision_analyzer.json"
    feed_path = command_feed_dir / f"eml_a9_2_guard_decision_analyzer_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        (packet_dir / f"{packet['fixtureId']}_guard_decision_{stamp}.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a9-2-guard-decision-analyzer",
        "title": "EML-A9.2 Guard Decision Analyzer",
        "reviewDecision": "guard_decision_fixture_analyzer_passed",
        "validationStatus": "pass",
        "replayStatus": "deterministic_fixture_analysis",
        "semanticStrength": "fixture_analyzer_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Fixture analyzer only; no compiler behavior change, compiler correctness proof, production readiness, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "validationCommands": ["python python/scripts/eml_a9_2_guard_decision_analyzer.py --build --strict"],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a9_2.v0",
        "date": DATE,
        "title": "EML-A9.2 Guard Decision Analyzer",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A9.3 expose guard decisions in the dev explorer",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = ["# EML-A9.2 Guard Decision Analyzer", "", f"Date: {DATE}", "", f"Status: `{payload['status']}`", "", "| Fixture | Decision | Rules matched |", "|---|---|---|"]
    for packet in payload["decisionPackets"]:
        lines.append(f"| `{packet['fixtureId']}` | `{packet['decision']}` | `{packet['expectedRulesMatched']}` |")
    lines.extend(["", "## Boundary", "", "- Fixture analyzer only.", "- No compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.", ""])
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A9.2 payload")
    summary = payload["summary"]
    if summary["decisionCount"] < 6:
        raise ValueError("expected at least six decisions")
    if summary["allFixturesMatched"] is not True:
        raise ValueError("all fixtures must match expected decisions and rules")
    for key in ["compilerBehaviorChanged", "compilerCorrectnessClaim", "productionReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["decisionPackets"]:
        if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
            raise ValueError("invalid decision schema")
        if packet["compilerBehaviorChanged"] is not False:
            raise ValueError("decision must not change compiler behavior")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a9_2_guard_decision_analyzer")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_guard_decision_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_decisions(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A9_2_GUARD_DECISION_ANALYZER_OK")
    print(f"decisions={built['payload']['summary']['decisionCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
