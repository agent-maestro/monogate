#!/usr/bin/env python3
"""FEF-P46 Rust/C/Python hero-lane private preview release gate."""

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

from scripts import fef_p44_hero_target_hardening_gate as p44
from scripts import fef_p45_c_rust_roundtrip_attachment_gate as p45

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p46_hero_lane_private_preview_release_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P46_HERO_LANE_PRIVATE_PREVIEW_RELEASE_GATE_PASS"

FORBIDDEN_PHRASES = [
    "public ready",
    "public package available",
    "checkout enabled",
    "compiler correctness",
    "formal semantic equivalence",
    "runtime performance",
    "speedup",
    "production toolchain",
    "full c roundtrip",
    "full rust roundtrip",
    "all 13 free targets execute",
    "all free targets roundtrip",
    "verilog target ready",
    "lean proofs emitted",
    "zkproof target ready",
    "silicon ready",
]

REQUIRED_BOUNDARY_PHRASES = [
    "private preview evidence only",
    "not a public package release",
    "not a compiler-correctness proof",
    "not a formal semantic-equivalence result",
    "not a runtime-performance benchmark",
    "not a checkout-enabled product",
    "not full arbitrary c/rust source roundtrip",
]

PRIVATE_PREVIEW_COPY = """Private preview evidence only.

Forge/eFrog has a selected Rust/C/Python hero lane for private review. The lane
records selected runtime execution evidence for Rust, C, and Python across four
fixture families, plus selected generated-target C/Rust re-ingest evidence that
roundtrips through eFrog and recompiles to Python.

This is not a public package release, not a compiler-correctness proof, not a
formal semantic-equivalence result, not a runtime-performance benchmark, not a
checkout-enabled product, and not full arbitrary C/Rust source roundtrip.
"""

CLAIM_FLAGS = {
    "private_preview_release_action_claim": False,
    "public_preview_release_claim": False,
    "package_published": False,
    "checkout_enabled": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_free_targets_roundtrip_claim": False,
    "all_target_readiness_claim": False,
}

NON_CLAIMS = [
    "FEF-P46 records a private preview release-action gate for the Rust/C/Python hero lane.",
    "FEF-P46 does not publish a package.",
    "FEF-P46 does not enable checkout or commerce.",
    "FEF-P46 does not claim public readiness.",
    "FEF-P46 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P46 does not claim runtime performance.",
    "FEF-P46 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P46 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P46 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]


def scan_private_copy(text: str) -> dict[str, Any]:
    lowered = " ".join(text.lower().split())
    forbidden_hits = [phrase for phrase in FORBIDDEN_PHRASES if phrase in lowered]
    required_missing = [phrase for phrase in REQUIRED_BOUNDARY_PHRASES if phrase not in lowered]
    return {
        "status": "pass" if not forbidden_hits and not required_missing else "fail",
        "forbiddenHits": forbidden_hits,
        "requiredBoundaryMissing": required_missing,
    }


def build_payload() -> dict[str, Any]:
    p44_payload = p44.build_payload()
    p45_payload = p45.build_payload()
    copy_scan = scan_private_copy(PRIVATE_PREVIEW_COPY)
    p44_summary = p44_payload["summary"]
    p45_summary = p45_payload["summary"]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p46-hero-lane-private-preview-release-gate",
        "decision": "rust_c_python_private_preview_release_action_approved_publication_blocked",
        "privatePreviewCopy": PRIVATE_PREVIEW_COPY,
        "privateCopyReview": copy_scan,
        "upstreamEvidence": {
            "fefP44": "reports/evidence_packets/fef_p44_hero_target_hardening_gate.json",
            "fefP45": "reports/evidence_packets/fef_p45_c_rust_roundtrip_attachment_gate.json",
        },
        "privatePreviewScope": {
            "heroTargets": p44_summary["heroTargets"],
            "fixtureCount": p44_summary["fixtureCount"],
            "heroRuntimeCellCount": p44_summary["heroRuntimeCellCount"],
            "heroRuntimeSampleExecutions": p44_summary["heroRuntimeSampleExecutions"],
            "selectedRoundtripAttachmentTargets": p45_summary["attachedTargets"],
            "selectedRoundtripAttachmentPackets": p45_summary["attachmentPacketCount"],
            "selectedRoundtripAttachmentSamples": p45_summary["attachmentSampleCount"],
            "selectedRoundtripAttachmentMaxAbsError": p45_summary["attachmentMaxAbsError"],
        },
        "releaseGates": [
            {"id": "private_preview_scope_recorded", "status": "pass"},
            {"id": "private_preview_copy_boundary_review_passed", "status": "pass"},
            {"id": "hero_lane_runtime_evidence_attached", "status": "pass"},
            {"id": "selected_c_rust_roundtrip_attachment_attached", "status": "pass"},
            {"id": "full_c_rust_roundtrip_claim", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_enabled", "status": "blocked"},
            {"id": "public_readiness", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivatePreviewClaims": [
            "Rust, C, and Python are the selected private hero lane.",
            "The hero lane records 12 selected runtime cells and 72 selected runtime sample executions.",
            "Selected generated C/Rust target outputs have 10 re-ingest packets and 34 sample comparisons.",
            "The private preview package may point reviewers to P44 and P45 evidence without claiming public readiness.",
        ],
        "blockedPublicClaims": [
            "public package availability",
            "checkout availability",
            "public readiness",
            "full arbitrary C/Rust source roundtrip",
            "all-free-target runtime execution",
            "all-free-target roundtrip",
            "compiler correctness",
            "formal semantic equivalence",
            "runtime performance",
            "production readiness",
            "Verilog/Lean proof/zkproof/silicon/hardware readiness",
        ],
        "summary": {
            "privateCopyReviewPassed": copy_scan["status"] == "pass",
            "heroTargets": p44_summary["heroTargets"],
            "heroRuntimeCellCount": p44_summary["heroRuntimeCellCount"],
            "heroRuntimeSampleExecutions": p44_summary["heroRuntimeSampleExecutions"],
            "selectedRoundtripAttachmentTargets": p45_summary["attachedTargets"],
            "selectedRoundtripAttachmentPackets": p45_summary["attachmentPacketCount"],
            "selectedRoundtripAttachmentSamples": p45_summary["attachmentSampleCount"],
            "privatePreviewReleaseActionApproved": True,
            "packagePublished": False,
            "checkoutEnabled": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "fullCRustRoundtripClaim": False,
            "allFreeTargetsRuntimeExecutionClaim": False,
            "allFreeTargetsRoundtripClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "runtimePerformanceClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextMilestones": [
            "Prepare a private reviewer bundle index that links P43, P44, P45, and this P46 gate.",
            "Broaden C/Rust roundtrip with non-generated source fixtures only under a separate gate.",
            "Keep public release blocked until publication, checkout, and public-readiness gates are explicitly passed.",
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
        "title": "FEF-P46 Hero Lane Private Preview Release Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "private_preview_release_action_publication_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private preview release-action gate only; it approves a bounded reviewer-facing Rust/C/Python hero-lane evidence bundle while keeping package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, full C/Rust roundtrip, all-free-target runtime, all-free-target roundtrip, hardware, silicon, and proof claims blocked.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Private preview scope is Rust/C/Python hero-lane evidence only.",
            "The private copy boundary passes with public/product/correctness/performance claims blocked.",
            "P44 runtime evidence and P45 selected C/Rust generated-target roundtrip attachment are both in scope.",
            "This does not publish a package or enable checkout.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p46_hero_lane_private_preview_release_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p46_hero_lane_private_preview_release_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p46_hero_lane_private_preview_release_gate.v0",
        "date": DATE,
        "title": "FEF-P46 Hero Lane Private Preview Release Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Prepare a private reviewer bundle index for the Rust/C/Python hero lane.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    scope = payload["privatePreviewScope"]
    lines = [
        "# FEF-P46 Hero Lane Private Preview Release Gate",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "## Private Preview Scope",
        "",
    ]
    for key, value in scope.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Release Gates",
            "",
            "| Gate | Status |",
            "|---|---|",
        ]
    )
    for gate in payload["releaseGates"]:
        lines.append(f"| `{gate['id']}` | `{gate['status']}` |")
    lines.extend(
        [
            "",
            "## Private Preview Copy",
            "",
            payload["privatePreviewCopy"].strip(),
            "",
            "## Boundary",
            "",
            "- Private preview release-action gate only.",
            "- No package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "- No full arbitrary C/Rust source roundtrip claim.",
            "- No all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P46 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P46 status")
    summary = payload["summary"]
    if summary["privateCopyReviewPassed"] is not True:
        raise ValueError("private preview copy review must pass")
    if summary["heroTargets"] != ["rust", "c", "python"]:
        raise ValueError("unexpected hero target set")
    if summary["heroRuntimeCellCount"] != 12:
        raise ValueError("expected 12 hero runtime cells")
    if summary["heroRuntimeSampleExecutions"] != 72:
        raise ValueError("expected 72 hero runtime sample executions")
    if summary["selectedRoundtripAttachmentTargets"] != ["c", "rust"]:
        raise ValueError("expected selected C/Rust roundtrip attachment targets")
    if summary["selectedRoundtripAttachmentPackets"] != 10:
        raise ValueError("expected 10 selected attachment packets")
    if summary["selectedRoundtripAttachmentSamples"] != 34:
        raise ValueError("expected 34 selected attachment samples")
    if summary["privatePreviewReleaseActionApproved"] is not True:
        raise ValueError("private preview release action should be approved")
    for key in [
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "fullCRustRoundtripClaim",
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsRoundtripClaim",
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
    result_path = out_dir / f"fef_p46_hero_lane_private_preview_release_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p46_hero_lane_private_preview_release_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p46_hero_lane_private_preview_release_gate.json"
    feed_path = command_feed_dir / f"fef_p46_hero_lane_private_preview_release_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p46_hero_lane_private_preview_release_gate")
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
    print("FEF_P46_HERO_LANE_PRIVATE_PREVIEW_RELEASE_GATE_OK")
    print(f"hero_targets={','.join(built['payload']['summary']['heroTargets'])}")
    print(f"release_action={built['payload']['summary']['privatePreviewReleaseActionApproved']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
