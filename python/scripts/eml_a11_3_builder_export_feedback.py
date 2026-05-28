#!/usr/bin/env python3
"""EML-A11.3 builder/export feedback integration.

Checks that exported builder-style drafts cite A11.2 stability evidence when
guard rules recommend protected lowerings. This is reviewer feedback only, not
compiler implementation or public approval.
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

from scripts.eml_a10_2_validate_builder_draft import CLAIM_FLAGS as A10_2_CLAIM_FLAGS  # noqa: E402
from scripts.eml_a10_2_validate_builder_draft import validate_draft  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a11_3_builder_export_feedback.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_builder_export_feedback_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A11_3_BUILDER_EXPORT_FEEDBACK_PASS"

DEFAULT_DRAFTS = [
    ROOT / "python/fixtures/eml_expression_packets/softplus_pair_v0.json",
    ROOT / "python/fixtures/eml_expression_holdout_packets/expm1_near_zero_holdout_v0.json",
]

CLAIM_FLAGS = {
    **dict(A10_2_CLAIM_FLAGS),
    "builder_export_public_approval": False,
    "builder_export_compiler_implementation_claim": False,
    "builder_export_runtime_performance_claim": False,
}

NON_CLAIMS = [
    "A11.3 connects builder/export guard feedback to A11.2 stability evidence.",
    "A11.3 does not approve public publication, implement compiler behavior, or prove compiler correctness.",
    "A11.3 does not claim runtime performance, production readiness, public Atlas promotion, or EML advantage.",
]


def build_feedback(
    drafts: list[Path],
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    validation_packets = [validate_draft(path) for path in drafts]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_builder_export_feedback_packet_v0",
        "date": DATE,
        "status": STATUS,
        "feedbackId": "eml_a11_3_builder_export_feedback",
        "sourceDrafts": [str(path) for path in drafts],
        "validationPackets": validation_packets,
        "summary": summarize(validation_packets),
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
    result_path = out_dir / f"eml_a11_3_builder_export_feedback_{stamp}.json"
    packet_path = packet_dir / f"eml_a11_3_builder_export_feedback_{stamp}.json"
    report_path = report_dir / f"eml_a11_3_builder_export_feedback_{stamp}.md"
    evidence_path = evidence_dir / "eml_a11_3_builder_export_feedback.json"
    feed_path = command_feed_dir / f"eml_a11_3_builder_export_feedback_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "packet_path": str(packet_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def summarize(validation_packets: list[dict[str, Any]]) -> dict[str, Any]:
    protected = [packet for packet in validation_packets if packet["decision"] == "recommend_protected_lowering"]
    citations = sum(len(packet["supportingEvidenceArtifacts"]) for packet in validation_packets)
    return {
        "draftCount": len(validation_packets),
        "protectedLoweringDraftCount": len(protected),
        "supportingEvidenceCitationCount": citations,
        "allProtectedLoweringsCiteA11_2": all(
            any(evidence["artifactId"] == "eml-a11-2-protected-lowering-benchmark" for evidence in packet["supportingEvidenceArtifacts"])
            for packet in protected
        ),
        "compilerBehaviorChanged": False,
        "compilerImplementationClaim": False,
        "compilerCorrectnessClaim": False,
        "runtimePerformanceClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a11-3-builder-export-feedback",
        "title": "EML-A11.3 Builder Export Feedback",
        "reviewDecision": "builder_export_feedback_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_export_feedback",
        "semanticStrength": "builder_feedback_with_stability_evidence_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Builder/export feedback only; no public approval, compiler implementation, compiler correctness, runtime performance, production readiness, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a11_3.v0",
        "date": DATE,
        "title": "EML-A11.3 Builder Export Feedback",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A12 build a tiny protected-lowering interpreter over guarded expression packets",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A11.3 Builder Export Feedback",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| Program | Decision | Lowering | Evidence citations |",
        "|---|---|---|---:|",
    ]
    for packet in payload["validationPackets"]:
        lines.append(
            f"| `{packet['programId']}` | `{packet['decision']}` | `{packet['recommendedLowering'] or 'none'}` | {len(packet['supportingEvidenceArtifacts'])} |"
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "- Builder/export feedback only.",
        "- No public approval, compiler implementation, compiler correctness, runtime performance, production readiness, or EML advantage claim.",
        "",
    ])
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A11.3 payload")
    summary = payload["summary"]
    if summary["draftCount"] < 2:
        raise ValueError("expected at least two export-feedback drafts")
    if summary["protectedLoweringDraftCount"] < 2:
        raise ValueError("expected at least two protected lowering drafts")
    if summary["allProtectedLoweringsCiteA11_2"] is not True:
        raise ValueError("protected lowering drafts must cite A11.2 evidence")
    for key in ["compilerBehaviorChanged", "compilerImplementationClaim", "compilerCorrectnessClaim", "runtimePerformanceClaim", "productionReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--draft", action="append", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a11_3_builder_export_feedback")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_builder_export_feedback_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    drafts = args.draft or DEFAULT_DRAFTS
    built = build_feedback(drafts, args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A11_3_BUILDER_EXPORT_FEEDBACK_OK")
    print(f"drafts={built['payload']['summary']['draftCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
