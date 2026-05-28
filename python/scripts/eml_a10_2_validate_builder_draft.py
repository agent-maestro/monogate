#!/usr/bin/env python3
"""EML-A10.2 local builder draft guard validator.

Validates one exported EML Expression Packet v0-style draft with the same
guard vocabulary used by A10. This is a local reviewer aid, not compiler
behavior and not public approval.
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
from scripts.eml_a10_expression_guard_lens import analyze_packet  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a10_2_builder_draft_guard_validation.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_builder_draft_guard_validation_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A10_2_BUILDER_DRAFT_VALIDATION_PASS"

CLAIM_FLAGS = {
    **dict(A10_CLAIM_FLAGS),
    "builder_draft_public_approval": False,
    "builder_draft_compiler_ready": False,
}

NON_CLAIMS = [
    "A10.2 validates one local EML builder draft against guard rules.",
    "A10.2 does not approve publication, change compiler behavior, or prove compiler correctness.",
    "A10.2 does not claim production readiness, runtime performance, public Atlas promotion, or EML advantage.",
]

A11_2_ARTIFACT_ID = "eml-a11-2-protected-lowering-benchmark"
A11_2_RESULT_PATH = "python/results/eml_a11_2_protected_lowering_benchmark/eml_a11_2_protected_lowering_benchmark_2026_05_27.json"


def supporting_evidence_for_lowering(lowering: str | None) -> list[dict[str, Any]]:
    if lowering == "expm1-style protected lowering":
        return [{
            "artifactId": A11_2_ARTIFACT_ID,
            "caseId": "expm1_near_zero",
            "evidencePath": A11_2_RESULT_PATH,
            "evidenceKind": "deterministic_numeric_stability_fixture",
            "supports": "protected expm1-style lowering is no worse than naive exp(x)-1 on the recorded edge grid",
            "doesNotSupport": ["runtime performance", "compiler correctness", "production readiness", "general EML superiority"],
        }]
    if lowering == "logaddexp-style protected lowering":
        return [{
            "artifactId": A11_2_ARTIFACT_ID,
            "caseId": "logsumexp_edge_grid",
            "evidencePath": A11_2_RESULT_PATH,
            "evidenceKind": "deterministic_numeric_stability_fixture",
            "supports": "protected log-sum-exp lowering remains finite on the recorded edge grid where naive forms can fail",
            "doesNotSupport": ["runtime performance", "compiler correctness", "production readiness", "general EML superiority"],
        }]
    return []


def load_draft(path: Path) -> dict[str, Any]:
    draft = json.loads(path.read_text(encoding="utf-8"))
    required = ["program_id", "expression"]
    missing = [key for key in required if key not in draft]
    if missing:
        raise ValueError(f"draft is missing required EML expression fields: {missing}")
    draft["_sourcePath"] = str(path)
    return draft


def validate_draft(draft_path: Path) -> dict[str, Any]:
    draft = load_draft(draft_path)
    guard = analyze_packet(draft)
    supporting_evidence = supporting_evidence_for_lowering(guard["recommendedLowering"])
    validation_packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_builder_draft_guard_validation_packet_v0",
        "date": DATE,
        "sourceDraftPath": str(draft_path),
        "programId": guard["programId"],
        "family": guard.get("family"),
        "expression": guard["expression"],
        "estimatedTreeDepth": guard["estimatedTreeDepth"],
        "decision": guard["decision"],
        "matchedRuleIds": guard["matchedRuleIds"],
        "recommendedLowering": guard["recommendedLowering"],
        "supportingEvidenceArtifacts": supporting_evidence,
        "reason": guard["reason"],
        "blockedClaims": guard["blockedClaims"],
        "localReviewerAction": local_reviewer_action(guard["decision"], supporting_evidence),
        "compilerBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "productionReady": False,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    return validation_packet


def local_reviewer_action(decision: str, supporting_evidence: list[dict[str, Any]] | None = None) -> str:
    if decision == "recommend_protected_lowering":
        if supporting_evidence:
            return "may cite attached protected-lowering stability evidence, but keep speed/compiler claims blocked"
        return "keep candidate private until protected lowering evidence is attached"
    if decision.startswith("block"):
        return "do not surface as public or runtime-strengthened evidence until the blocker is discharged"
    return "may remain a proof-shape candidate with non-claims attached"


def build_validation(draft_path: Path, out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    validation_packet = validate_draft(draft_path)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "validatorId": "eml_a10_2_builder_draft_guard_validation",
        "sourceDraftPath": str(draft_path),
        "validationPacket": validation_packet,
        "summary": {
            "programId": validation_packet["programId"],
            "decision": validation_packet["decision"],
            "matchedRuleCount": len(validation_packet["matchedRuleIds"]),
            "blockedClaimCount": len(validation_packet["blockedClaims"]),
            "supportingEvidenceCount": len(validation_packet["supportingEvidenceArtifacts"]),
            "compilerBehaviorChanged": False,
            "compilerCorrectnessClaim": False,
            "productionReady": False,
            "claimFlagsAllFalse": all(value is False for value in validation_packet["claimFlags"].values()),
        },
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
    result_path = out_dir / f"eml_a10_2_builder_draft_validation_{stamp}.json"
    packet_path = packet_dir / f"{validation_packet['programId']}_builder_draft_guard_validation_{stamp}.json"
    report_path = report_dir / f"eml_a10_2_builder_draft_validation_{stamp}.md"
    evidence_path = evidence_dir / "eml_a10_2_builder_draft_validation.json"
    feed_path = command_feed_dir / f"eml_a10_2_builder_draft_validation_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet_path.write_text(json.dumps(validation_packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "packet_path": str(packet_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a10-2-builder-draft-guard-validation",
        "title": "EML-A10.2 Builder Draft Guard Validation",
        "reviewDecision": "local_builder_draft_guard_validated",
        "validationStatus": "pass",
        "replayStatus": "deterministic_single_draft_analysis",
        "semanticStrength": "local_guard_validation_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Local draft validation only; no public approval, compiler behavior change, compiler correctness proof, production readiness, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a10_2.v0",
        "date": DATE,
        "title": "EML-A10.2 Builder Draft Guard Validation",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A11 route guard decisions into a mock compiler decision layer",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["validationPacket"]
    return "\n".join([
        "# EML-A10.2 Builder Draft Guard Validation",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"- Program: `{packet['programId']}`",
        f"- Decision: `{packet['decision']}`",
        f"- Recommended lowering: `{packet['recommendedLowering'] or 'none'}`",
        f"- Supporting evidence artifacts: {len(packet['supportingEvidenceArtifacts'])}",
        f"- Reviewer action: {packet['localReviewerAction']}",
        "",
        "## Boundary",
        "",
        "- Local draft validation only.",
        "- No public approval, compiler behavior change, compiler correctness proof, production readiness, runtime performance, or EML advantage claim.",
        "",
    ])


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A10.2 payload")
    summary = payload["summary"]
    if summary["matchedRuleCount"] < 1:
        raise ValueError("expected at least one matched guard rule")
    if payload["validationPacket"]["decision"] == "recommend_protected_lowering" and summary["supportingEvidenceCount"] < 1:
        raise ValueError("protected lowering recommendations must cite supporting evidence")
    for key in ["compilerBehaviorChanged", "compilerCorrectnessClaim", "productionReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft_path", type=Path)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a10_2_builder_draft_validation")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_builder_draft_guard_validation_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_validation(args.draft_path, args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A10_2_BUILDER_DRAFT_VALIDATION_OK")
    print(f"decision={built['payload']['summary']['decision']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
