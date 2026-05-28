#!/usr/bin/env python3
"""EML-A11.1 mock compiler holdout packet set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_a11_mock_compiler_decision import CLAIM_FLAGS as A11_CLAIM_FLAGS  # noqa: E402
from scripts.eml_a11_mock_compiler_decision import build_mock_decisions  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a11_1_mock_compiler_holdouts.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_mock_compiler_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A11_1_MOCK_COMPILER_HOLDOUTS_PASS"

CLAIM_FLAGS = {
    **dict(A11_CLAIM_FLAGS),
    "holdout_set_public_approval": False,
}

NON_CLAIMS = [
    "A11.1 is a holdout packet set for the mock compiler decision layer.",
    "A11.1 does not implement, modify, or verify a real compiler.",
    "A11.1 does not claim compiler correctness, production readiness, runtime performance, public Atlas promotion, or EML advantage.",
]


def build_holdouts(packet_dir: Path, out_dir: Path, holdout_packet_dir: Path, decision_packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    built = build_mock_decisions(
        packet_dir,
        out_dir / "_a11_holdout_source",
        decision_packet_dir,
        out_dir / "_a11_reports",
        out_dir / "_a11_evidence",
        out_dir / "_a11_feeds",
        lens_out_dir=out_dir / "_lens_source",
        lens_packet_dir=out_dir / "_lens_packets",
        lens_report_dir=out_dir / "_lens_reports",
        lens_evidence_dir=out_dir / "_lens_evidence",
        lens_command_feed_dir=out_dir / "_lens_feeds",
    )
    decisions = built["payload"]["decisionPackets"]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_mock_compiler_holdout_packet_v0",
        "date": DATE,
        "status": STATUS,
        "holdoutId": "eml_a11_1_mock_compiler_holdouts",
        "sourcePacketDir": str(packet_dir),
        "decisionPackets": decisions,
        "summary": summarize(decisions),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    holdout_packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a11_1_mock_compiler_holdouts_{stamp}.json"
    holdout_packet_path = holdout_packet_dir / f"eml_a11_1_mock_compiler_holdouts_{stamp}.json"
    report_path = report_dir / f"eml_a11_1_mock_compiler_holdouts_{stamp}.md"
    evidence_path = evidence_dir / "eml_a11_1_mock_compiler_holdouts.json"
    feed_path = command_feed_dir / f"eml_a11_1_mock_compiler_holdouts_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    holdout_packet_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "holdout_packet_path": str(holdout_packet_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def summarize(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    by_compiler: dict[str, int] = {}
    by_guard: dict[str, int] = {}
    for packet in decisions:
        by_compiler[packet["compilerDecision"]] = by_compiler.get(packet["compilerDecision"], 0) + 1
        by_guard[packet["guardDecision"]] = by_guard.get(packet["guardDecision"], 0) + 1
    return {
        "holdoutCount": len(decisions),
        "byCompilerDecision": by_compiler,
        "byGuardDecision": by_guard,
        "protectedRuntimeLoweringCount": by_compiler.get("protected_runtime_lowering", 0),
        "blockedRequiresEvidenceCount": by_compiler.get("blocked_requires_evidence", 0),
        "proofShapeOnlyCount": by_compiler.get("proof_shape_only", 0),
        "realCompilerBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in decisions),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a11-1-mock-compiler-holdouts",
        "title": "EML-A11.1 Mock Compiler Holdouts",
        "reviewDecision": "mock_compiler_holdouts_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_holdout_mapping",
        "semanticStrength": "holdout_mock_compiler_decision_no_real_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Mock compiler holdout set only; no real compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a11_1.v0",
        "date": DATE,
        "title": "EML-A11.1 Mock Compiler Holdouts",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A11.2 add a protected-lowering fixture benchmark for the recommended runtime paths",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = ["# EML-A11.1 Mock Compiler Holdouts", "", f"Date: {DATE}", "", f"Status: `{payload['status']}`", "", "| Program | Guard decision | Mock compiler decision |", "|---|---|---|"]
    for packet in payload["decisionPackets"]:
        lines.append(f"| `{packet['programId']}` | `{packet['guardDecision']}` | `{packet['compilerDecision']}` |")
    lines.extend(["", "## Boundary", "", "- Holdout packet set for mock compiler decisions only.", "- No real compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.", ""])
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A11.1 payload")
    summary = payload["summary"]
    if summary["holdoutCount"] < 6:
        raise ValueError("expected at least six holdout decisions")
    if summary["protectedRuntimeLoweringCount"] < 2:
        raise ValueError("expected at least two protected lowering holdouts")
    if summary["blockedRequiresEvidenceCount"] < 2:
        raise ValueError("expected at least two blocked holdouts")
    if summary["proofShapeOnlyCount"] < 2:
        raise ValueError("expected at least two proof-shape holdouts")
    for key in ["realCompilerBehaviorChanged", "compilerCorrectnessClaim", "productionReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/fixtures/eml_expression_holdout_packets")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a11_1_mock_compiler_holdouts")
    parser.add_argument("--holdout-packet-dir", type=Path, default=ROOT / "python/results/eml_mock_compiler_holdout_packets")
    parser.add_argument("--decision-packet-dir", type=Path, default=ROOT / "python/results/eml_mock_compiler_holdout_decision_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_holdouts(args.packet_dir, args.out_dir, args.holdout_packet_dir, args.decision_packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A11_1_MOCK_COMPILER_HOLDOUTS_OK")
    print(f"holdouts={built['payload']['summary']['holdoutCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
