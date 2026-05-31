#!/usr/bin/env python3
"""FEF-P45 C/Rust selected roundtrip attachment gate."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p13_c_rust_generated_target_reingest as p13
from scripts import fef_p44_hero_target_hardening_gate as p44

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p45_c_rust_roundtrip_attachment_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P45_C_RUST_ROUNDTRIP_ATTACHMENT_GATE_PASS"

CLAIM_FLAGS = {
    "selected_c_rust_roundtrip_attachment_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "all_free_targets_roundtrip_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_free_targets_public_ready_claim": False,
    "target_all_ready_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "package_published": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
}

NON_CLAIMS = [
    "FEF-P45 attaches selected generated-target C/Rust re-ingest evidence to the FEF-P44 hero lane.",
    "FEF-P45 does not claim full arbitrary C or Rust source roundtrip.",
    "FEF-P45 does not add a new fixture family.",
    "FEF-P45 does not execute all 13 free targets.",
    "FEF-P45 does not claim all 13 free targets runtime-execute.",
    "FEF-P45 does not claim all 13 free targets roundtrip.",
    "FEF-P45 does not claim all free targets are public-ready.",
    "FEF-P45 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P45 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P45 does not claim runtime performance, Verilog, Lean proofs, zkproof proofs, silicon output, hardware readiness, Pro-target readiness, or all-target readiness.",
]


def attachment_rows(p13_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in ["c", "rust"]:
        packets = [
            packet
            for packet in p13_payload["reingestPackets"]
            if packet["generatedTargetLanguage"] == target
        ]
        rows.append(
            {
                "target": target,
                "attachmentStatus": "pass_selected_generated_target_reingest",
                "packetCount": len(packets),
                "passCount": sum(1 for packet in packets if packet["reingestStatus"] == "pass"),
                "sourceLanguages": sorted({packet["sourceLanguage"] for packet in packets}),
                "sourceCaseIds": [packet["sourceCaseId"] for packet in packets],
                "sampleCount": sum(packet["sampleCount"] for packet in packets),
                "maxAbsError": max(packet["maxAbsError"] for packet in packets),
                "maxRelError": max(packet["maxRelError"] for packet in packets),
                "attachedEvidenceKind": "selected_generated_target_reingest_to_python",
                "allowedClaim": (
                    f"{target}: selected Forge-generated {target} target outputs re-ingest "
                    "through eFrog, recompile to Python, and match generated target runtime "
                    "outputs on deterministic samples."
                ),
                "blockedClaims": [
                    "full arbitrary source roundtrip",
                    "all-free-target roundtrip",
                    "compiler correctness",
                    "formal semantic equivalence",
                    "public readiness",
                    "runtime performance",
                ],
            }
        )
    return rows


def summarize(
    p13_payload: dict[str, Any],
    p44_payload: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "attachedTargetCount": len(rows),
        "attachedTargets": [row["target"] for row in rows],
        "attachmentPacketCount": sum(row["packetCount"] for row in rows),
        "attachmentPassCount": sum(row["passCount"] for row in rows),
        "attachmentSampleCount": sum(row["sampleCount"] for row in rows),
        "attachmentMaxAbsError": max(row["maxAbsError"] for row in rows),
        "attachmentMaxRelError": max(row["maxRelError"] for row in rows),
        "sourceLanguages": p13_payload["summary"]["sourceLanguages"],
        "heroTargets": p44_payload["summary"]["heroTargets"],
        "heroRuntimeCellCount": p44_payload["summary"]["heroRuntimeCellCount"],
        "pythonRoundtripEvidenceAttached": p44_payload["summary"][
            "pythonRoundtripEvidenceAttached"
        ],
        "cSelectedGeneratedTargetRoundtripAttached": True,
        "rustSelectedGeneratedTargetRoundtripAttached": True,
        "fullCRoundtripClaim": False,
        "fullRustRoundtripClaim": False,
        "allFreeTargetsRoundtripClaim": False,
        "allFreeTargetsRuntimeExecutionClaim": False,
        "allFreeTargetsPublicReadyClaim": False,
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p13_payload = p13.build_payload()
    p44_payload = p44.build_payload()
    rows = attachment_rows(p13_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p45-c-rust-roundtrip-attachment-gate",
        "decision": "selected_c_rust_generated_target_roundtrip_attached_publication_blocked",
        "upstreamEvidence": {
            "fefP13": "reports/evidence_packets/fef_p13_c_rust_generated_target_reingest.json",
            "fefP44": "reports/evidence_packets/fef_p44_hero_target_hardening_gate.json",
        },
        "attachmentRows": rows,
        "summary": summarize(p13_payload, p44_payload, rows),
        "releaseGates": [
            {"id": "selected_c_generated_target_roundtrip_attached", "status": "pass"},
            {"id": "selected_rust_generated_target_roundtrip_attached", "status": "pass"},
            {"id": "full_c_roundtrip_claim", "status": "blocked"},
            {"id": "full_rust_roundtrip_claim", "status": "blocked"},
            {"id": "all_free_targets_roundtrip", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "public_readiness", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivateClaims": [
            "Selected generated C target outputs re-ingest through eFrog and recompile to Python over deterministic samples.",
            "Selected generated Rust target outputs re-ingest through eFrog and recompile to Python over deterministic samples.",
            "The selected C/Rust attachment covers 10 generated-target re-ingest packets and 34 sample comparisons.",
            "Rust, C, and Python remain the private hero lane; this attachment does not publish a package.",
        ],
        "blockedClaims": [
            "full arbitrary C source roundtrip",
            "full arbitrary Rust source roundtrip",
            "all-free-target roundtrip",
            "all-free-target runtime execution",
            "public readiness",
            "package publication",
            "checkout availability",
            "compiler correctness",
            "formal semantic equivalence",
            "runtime performance",
            "hardware/silicon/proof readiness",
        ],
        "nextMilestones": [
            "If the selected attachment is accepted, run a private preview release-action gate over Rust/C/Python.",
            "If broader C/Rust roundtrip is desired, add explicit non-generated source fixtures and keep this selected-generated-target claim separate.",
            "Do not relabel this as full C/Rust roundtrip without broader source-family evidence.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return copy.deepcopy(payload)


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P45 C/Rust Roundtrip Attachment Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_generated_c_rust_target_reingest_attached_to_hero_lane",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected generated-target C/Rust re-ingest attachment only; it attaches FEF-P13 evidence to the FEF-P44 hero lane and does not claim full arbitrary C/Rust roundtrip, all-free-target roundtrip, publication, public readiness, compiler correctness, formal equivalence, or runtime performance.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "C and Rust now have selected generated-target roundtrip attachment evidence.",
            "The attachment covers 10 selected re-ingest packets and 34 sample comparisons.",
            "Full arbitrary C/Rust source roundtrip remains blocked.",
            "The Rust/C/Python hero lane remains private and publication-blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p45_c_rust_roundtrip_attachment_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p45_c_rust_roundtrip_attachment_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p45_c_rust_roundtrip_attachment_gate.v0",
        "date": DATE,
        "title": "FEF-P45 C/Rust Roundtrip Attachment Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run a private preview release-action gate over the Rust/C/Python hero lane, or broaden C/Rust roundtrip with non-generated source fixtures.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Target | Attachment | Packets | Samples | Max Abs Error | Max Rel Error | Allowed Claim |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in payload["attachmentRows"]:
        rows.append(
            f"| `{row['target']}` | `{row['attachmentStatus']}` | `{row['packetCount']}` | "
            f"`{row['sampleCount']}` | `{row['maxAbsError']:.3e}` | "
            f"`{row['maxRelError']:.3e}` | {row['allowedClaim']} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P45 C/Rust Roundtrip Attachment Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Attachment Rows",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Attached targets: `{', '.join(summary['attachedTargets'])}`",
            f"- Attachment packets: `{summary['attachmentPacketCount']}`",
            f"- Attachment passes: `{summary['attachmentPassCount']}`",
            f"- Attachment samples: `{summary['attachmentSampleCount']}`",
            f"- Attachment max absolute error: `{summary['attachmentMaxAbsError']:.3e}`",
            f"- Attachment max relative error: `{summary['attachmentMaxRelError']:.3e}`",
            f"- Full C roundtrip claim: `{summary['fullCRoundtripClaim']}`",
            f"- Full Rust roundtrip claim: `{summary['fullRustRoundtripClaim']}`",
            "",
            "## Boundary",
            "",
            "- Selected generated-target C/Rust re-ingest attachment only.",
            "- No full arbitrary C/Rust source roundtrip claim.",
            "- No all-free-target roundtrip or runtime execution claim.",
            "- No package publication, checkout, public-readiness, compiler-correctness, formal-equivalence, runtime-performance, hardware, silicon, or proof claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P45 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P45 status")
    summary = payload["summary"]
    if summary["attachedTargets"] != ["c", "rust"]:
        raise ValueError("expected selected C and Rust attachments")
    if summary["attachmentPacketCount"] != 10:
        raise ValueError("expected 10 C/Rust attachment packets")
    if summary["attachmentPassCount"] != 10:
        raise ValueError("all C/Rust attachment packets must pass")
    if summary["attachmentSampleCount"] != 34:
        raise ValueError("unexpected C/Rust attachment sample count")
    if summary["attachmentMaxAbsError"] > 1.0e-9 and summary["attachmentMaxRelError"] > 1.0e-9:
        raise ValueError("attachment errors exceed selected tolerance")
    if summary["cSelectedGeneratedTargetRoundtripAttached"] is not True:
        raise ValueError("C selected attachment must be true")
    if summary["rustSelectedGeneratedTargetRoundtripAttached"] is not True:
        raise ValueError("Rust selected attachment must be true")
    for key in [
        "fullCRoundtripClaim",
        "fullRustRoundtripClaim",
        "allFreeTargetsRoundtripClaim",
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsPublicReadyClaim",
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p45_c_rust_roundtrip_attachment_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p45_c_rust_roundtrip_attachment_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p45_c_rust_roundtrip_attachment_gate.json"
    feed_path = command_feed_dir / f"fef_p45_c_rust_roundtrip_attachment_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p45_c_rust_roundtrip_attachment_gate")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P45_C_RUST_ROUNDTRIP_ATTACHMENT_GATE_OK")
    print(f"attached_targets={','.join(built['payload']['summary']['attachedTargets'])}")
    print(f"attachment_packets={built['payload']['summary']['attachmentPacketCount']}")
    print(f"attachment_samples={built['payload']['summary']['attachmentSampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
