#!/usr/bin/env python3
"""EML-A10 expression packet guard lens.

Applies the A9 guard decision vocabulary to existing EML expression packets.
This is an analyzer over packet fixtures, not compiler behavior.
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

from scripts.eml_a9_2_guard_decision_analyzer import CLAIM_FLAGS as A9_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a10_expression_guard_lens.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_expression_guard_lens_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A10_EXPRESSION_GUARD_LENS_PASS"

CLAIM_FLAGS = {
    **dict(A9_CLAIM_FLAGS),
    "expression_guard_lens_production_ready": False,
}

NON_CLAIMS = [
    "A10 applies guard decisions to existing EML expression packets only.",
    "A10 does not change compiler behavior or prove compiler correctness.",
    "A10 does not claim production readiness, EML advantage, runtime performance, public Atlas promotion, or deployment.",
]


def load_expression_packets(packet_dir: Path) -> list[dict[str, Any]]:
    packets = []
    for path in sorted(packet_dir.glob("*.json")):
        packet = json.loads(path.read_text(encoding="utf-8"))
        packet["_sourcePath"] = str(path)
        packets.append(packet)
    return packets


def estimate_depth(expression: str) -> int:
    return max(expression.count("("), 1)


def analyze_packet(packet: dict[str, Any]) -> dict[str, Any]:
    expression = packet["expression"]
    program_id = packet["program_id"]
    lower = expression.lower().replace(" ", "")
    matched: list[str] = []
    decision = "allow_proof_shape"
    lowering = None
    reason = "Expression has no protected-runtime trigger in the current fixture lens."
    blocked_claims = ["general EML superiority", "runtime performance"]

    if "eml(log(v),exp(u))" in lower:
        matched = ["prefer_eml_for_proof_shape_v0", "subtraction_boundary_guarded_v0"]
        reason = "Guarded subtraction-boundary shape may remain proof/search evidence with non-claims attached."
    elif "ln(exp(a) + exp(b))" in expression or "ln(exp" in lower or "log(exp" in lower:
        decision = "recommend_protected_lowering"
        matched = ["lower_logaddexp_softplus_v0", "require_positive_log_domain_guard_v0"]
        lowering = "logaddexp-style protected lowering"
        reason = "Log-sum-exp/softplus shape should lower to protected runtime code."
    elif lower in {"eml(x,e)", "exp(x)-1", "exp(x)-ln(e)"}:
        decision = "recommend_protected_lowering"
        matched = ["lower_expm1_near_zero_v0", "prefer_protected_runtime_lowering_v0"]
        lowering = "expm1-style protected lowering"
        reason = "Near-zero exp-minus-one shape should lower to protected runtime code."
    elif estimate_depth(expression) >= 10:
        decision = "block_unstable_deep_tree"
        matched = ["block_unstable_deep_tree_v0"]
        reason = "Expression depth exceeds current guard lens tolerance."
        blocked_claims.append("deep-tree stability")
    elif "1 /" in expression or re.search(r"\bdiv\b|/", expression) or "eml(x,y)" in lower:
        decision = "block_missing_domain_guard"
        matched = ["require_positive_log_domain_guard_v0"]
        reason = "Division-like or raw EML expression requires explicit denominator/domain guard evidence before public/runtime strengthening."
        blocked_claims.append("public expression claim")
    else:
        matched = ["prefer_eml_for_proof_shape_v0"]

    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_expression_guard_lens_packet_v0",
        "date": DATE,
        "programId": program_id,
        "family": packet.get("family"),
        "sourcePath": packet.get("_sourcePath"),
        "expression": expression,
        "estimatedTreeDepth": estimate_depth(expression),
        "decision": decision,
        "matchedRuleIds": matched,
        "recommendedLowering": lowering,
        "reason": reason,
        "blockedClaims": blocked_claims,
        "compilerBehaviorChanged": False,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_decision: dict[str, int] = {}
    for packet in packets:
        by_decision[packet["decision"]] = by_decision.get(packet["decision"], 0) + 1
    return {
        "packetCount": len(packets),
        "byDecision": by_decision,
        "protectedLoweringCount": by_decision.get("recommend_protected_lowering", 0),
        "blockedCount": sum(count for decision, count in by_decision.items() if decision.startswith("block")),
        "compilerBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_lens(packet_dir: Path, out_dir: Path, lens_packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    lens_packets = [analyze_packet(packet) for packet in load_expression_packets(packet_dir)]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "lensId": "eml_a10_expression_guard_lens",
        "sourcePacketDir": str(packet_dir),
        "guardLensPackets": lens_packets,
        "summary": summarize(lens_packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    lens_packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a10_expression_guard_lens_{stamp}.json"
    report_path = report_dir / f"eml_a10_expression_guard_lens_{stamp}.md"
    evidence_path = evidence_dir / "eml_a10_expression_guard_lens.json"
    feed_path = command_feed_dir / f"eml_a10_expression_guard_lens_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in lens_packets:
        (lens_packet_dir / f"{packet['programId']}_guard_lens_{stamp}.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a10-expression-guard-lens",
        "title": "EML-A10 Expression Guard Lens",
        "reviewDecision": "expression_guard_lens_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_packet_analysis",
        "semanticStrength": "expression_guard_lens_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expression guard lens only; no compiler behavior change, compiler correctness proof, production readiness, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a10.v0",
        "date": DATE,
        "title": "EML-A10 Expression Guard Lens",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A10.1 integrate guard hints into packet builder drafts",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = ["# EML-A10 Expression Guard Lens", "", f"Date: {DATE}", "", f"Status: `{payload['status']}`", "", "| Program | Decision | Lowering |", "|---|---|---|"]
    for packet in payload["guardLensPackets"]:
        lines.append(f"| `{packet['programId']}` | `{packet['decision']}` | `{packet['recommendedLowering'] or 'none'}` |")
    lines.extend(["", "## Boundary", "", "- Expression packet guard lens only.", "- No compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.", ""])
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A10 payload")
    summary = payload["summary"]
    if summary["packetCount"] < 3:
        raise ValueError("expected at least three expression guard packets")
    if summary["protectedLoweringCount"] < 1:
        raise ValueError("expected at least one protected lowering recommendation")
    if summary["blockedCount"] < 1:
        raise ValueError("expected at least one blocked guard decision")
    for key in ["compilerBehaviorChanged", "compilerCorrectnessClaim", "productionReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/fixtures/eml_expression_packets")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a10_expression_guard_lens")
    parser.add_argument("--lens-packet-dir", type=Path, default=ROOT / "python/results/eml_expression_guard_lens_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_lens(args.packet_dir, args.out_dir, args.lens_packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A10_EXPRESSION_GUARD_LENS_OK")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
