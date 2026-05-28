#!/usr/bin/env python3
"""EML-A11 mock compiler decision layer.

Routes A10 guard-lens packets into explicit mock compiler decisions. This is
not a compiler implementation and does not change Forge or EML compiler
behavior.
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

from scripts.eml_a10_expression_guard_lens import CLAIM_FLAGS as A10_CLAIM_FLAGS  # noqa: E402
from scripts.eml_a10_expression_guard_lens import build_lens  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a11_mock_compiler_decision.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_mock_compiler_decision_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A11_MOCK_COMPILER_DECISION_PASS"

CLAIM_FLAGS = {
    **dict(A10_CLAIM_FLAGS),
    "mock_compiler_is_real_compiler": False,
    "compiler_behavior_changed": False,
    "compiler_correctness_proved": False,
}

NON_CLAIMS = [
    "A11 is a mock compiler decision layer over A10 guard-lens packets.",
    "A11 does not implement, modify, or verify a real compiler.",
    "A11 does not claim compiler correctness, production readiness, runtime performance, public Atlas promotion, or EML advantage.",
]


def decision_for_guard(packet: dict[str, Any]) -> dict[str, Any]:
    guard_decision = packet["decision"]
    if guard_decision == "recommend_protected_lowering":
        compiler_decision = "protected_runtime_lowering"
        runtime_target = packet["recommendedLowering"]
        required_evidence = ["protected lowering fixture", "domain guard evidence", "numeric stability check"]
    elif guard_decision.startswith("block"):
        compiler_decision = "blocked_requires_evidence"
        runtime_target = None
        required_evidence = ["guard blocker discharge", "reviewer approval packet"]
    else:
        compiler_decision = "proof_shape_only"
        runtime_target = None
        required_evidence = ["keep non-claims attached", "no runtime-strengthened claim"]

    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_mock_compiler_decision_packet_v0",
        "date": DATE,
        "programId": packet["programId"],
        "family": packet.get("family"),
        "expression": packet["expression"],
        "guardDecision": guard_decision,
        "matchedRuleIds": packet["matchedRuleIds"],
        "compilerDecision": compiler_decision,
        "runtimeTarget": runtime_target,
        "requiredEvidence": required_evidence,
        "blockedClaims": packet["blockedClaims"],
        "realCompilerBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "productionReady": False,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    by_decision: dict[str, int] = {}
    for packet in decisions:
        key = packet["compilerDecision"]
        by_decision[key] = by_decision.get(key, 0) + 1
    return {
        "decisionCount": len(decisions),
        "byCompilerDecision": by_decision,
        "protectedRuntimeLoweringCount": by_decision.get("protected_runtime_lowering", 0),
        "blockedRequiresEvidenceCount": by_decision.get("blocked_requires_evidence", 0),
        "proofShapeOnlyCount": by_decision.get("proof_shape_only", 0),
        "realCompilerBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in decisions),
    }


def build_mock_decisions(packet_dir: Path, out_dir: Path, decision_packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    lens = build_lens(
        packet_dir,
        ROOT / "python/results/eml_a10_expression_guard_lens",
        ROOT / "python/results/eml_expression_guard_lens_packets",
        ROOT / "reports",
        ROOT / "reports/evidence_packets",
        ROOT / "command_center_feeds",
    )["payload"]
    decisions = [decision_for_guard(packet) for packet in lens["guardLensPackets"]]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "mockCompilerId": "eml_a11_mock_compiler_decision",
        "sourceLensId": lens["lensId"],
        "decisionPackets": decisions,
        "summary": summarize(decisions),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    decision_packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a11_mock_compiler_decision_{stamp}.json"
    report_path = report_dir / f"eml_a11_mock_compiler_decision_{stamp}.md"
    evidence_path = evidence_dir / "eml_a11_mock_compiler_decision.json"
    feed_path = command_feed_dir / f"eml_a11_mock_compiler_decision_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in decisions:
        (decision_packet_dir / f"{packet['programId']}_mock_compiler_decision_{stamp}.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a11-mock-compiler-decision",
        "title": "EML-A11 Mock Compiler Decision Layer",
        "reviewDecision": "mock_compiler_decisions_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_guard_to_decision_mapping",
        "semanticStrength": "mock_compiler_decision_no_real_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Mock compiler decisions only; no real compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a11.v0",
        "date": DATE,
        "title": "EML-A11 Mock Compiler Decision Layer",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A11.1 add holdout packets and require the mock compiler mapping in CI",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = ["# EML-A11 Mock Compiler Decision Layer", "", f"Date: {DATE}", "", f"Status: `{payload['status']}`", "", "| Program | Guard decision | Mock compiler decision |", "|---|---|---|"]
    for packet in payload["decisionPackets"]:
        lines.append(f"| `{packet['programId']}` | `{packet['guardDecision']}` | `{packet['compilerDecision']}` |")
    lines.extend(["", "## Boundary", "", "- Mock compiler decision layer only.", "- No real compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.", ""])
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A11 payload")
    summary = payload["summary"]
    if summary["decisionCount"] < 3:
        raise ValueError("expected at least three mock compiler decisions")
    if summary["protectedRuntimeLoweringCount"] < 1:
        raise ValueError("expected a protected runtime lowering decision")
    if summary["blockedRequiresEvidenceCount"] < 1:
        raise ValueError("expected a blocked requires-evidence decision")
    if summary["proofShapeOnlyCount"] < 1:
        raise ValueError("expected a proof-shape-only decision")
    for key in ["realCompilerBehaviorChanged", "compilerCorrectnessClaim", "productionReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/fixtures/eml_expression_packets")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a11_mock_compiler_decision")
    parser.add_argument("--decision-packet-dir", type=Path, default=ROOT / "python/results/eml_mock_compiler_decision_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_mock_decisions(args.packet_dir, args.out_dir, args.decision_packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A11_MOCK_COMPILER_DECISION_OK")
    print(f"decisions={built['payload']['summary']['decisionCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
