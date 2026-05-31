#!/usr/bin/env python3
"""FEF-P48 private reviewer intake packet for the Rust/C/Python hero lane."""

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

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p48_private_reviewer_intake_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P48_PRIVATE_REVIEWER_INTAKE_PACKET_PASS"
P47_PACKET = ROOT / "reports/evidence_packets/fef_p47_private_reviewer_bundle_index.json"
P47_REPORT = ROOT / "reports/fef_p47_private_reviewer_bundle_index_2026_05_30.md"

CLAIM_FLAGS = {
    "private_reviewer_intake_claim": False,
    "private_reviewer_decision_recorded": False,
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
    "FEF-P48 records a private reviewer intake packet only.",
    "FEF-P48 does not record reviewer approval or rejection.",
    "FEF-P48 does not publish a package.",
    "FEF-P48 does not enable checkout or commerce.",
    "FEF-P48 does not claim public readiness.",
    "FEF-P48 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P48 does not claim runtime performance.",
    "FEF-P48 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P48 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P48 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def p47_bundle_summary() -> dict[str, Any]:
    packet = read_json(P47_PACKET)
    review = packet.get("semanticReview", {})
    return {
        "artifactId": packet.get("artifactId"),
        "title": packet.get("title"),
        "reviewDecision": packet.get("reviewDecision"),
        "validationStatus": packet.get("validationStatus"),
        "semanticStrength": packet.get("semanticStrength"),
        "packetPath": str(P47_PACKET.relative_to(ROOT)),
        "reportPath": str(P47_REPORT.relative_to(ROOT)),
        "claimFlagsAllFalse": all(value is False for value in packet.get("claimFlags", {}).values()),
        "bundleEvidenceCount": review.get("bundleEvidenceCount"),
        "heroTargets": review.get("heroTargets"),
        "runtimePassTargets": review.get("runtimePassTargets"),
        "roundtripPassTargets": review.get("roundtripPassTargets"),
        "heroRuntimeCellCount": review.get("heroRuntimeCellCount"),
        "heroRuntimeSampleExecutions": review.get("heroRuntimeSampleExecutions"),
        "selectedRoundtripAttachmentTargets": review.get("selectedRoundtripAttachmentTargets"),
        "selectedRoundtripAttachmentPackets": review.get("selectedRoundtripAttachmentPackets"),
        "selectedRoundtripAttachmentSamples": review.get("selectedRoundtripAttachmentSamples"),
        "privatePreviewReleaseActionApproved": review.get("privatePreviewReleaseActionApproved"),
        "publicReady": review.get("publicReady"),
        "compilerCorrectnessClaim": review.get("compilerCorrectnessClaim"),
        "formalEquivalenceClaim": review.get("formalEquivalenceClaim"),
        "runtimePerformanceClaim": review.get("runtimePerformanceClaim"),
        "fullCRustRoundtripClaim": review.get("fullCRustRoundtripClaim"),
        "allFreeTargetsRuntimeExecutionClaim": review.get("allFreeTargetsRuntimeExecutionClaim"),
        "allFreeTargetsRoundtripClaim": review.get("allFreeTargetsRoundtripClaim"),
    }


def build_payload() -> dict[str, Any]:
    bundle = p47_bundle_summary()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p48-private-reviewer-intake-packet",
        "decision": "private_reviewer_intake_ready_no_reviewer_decision_recorded",
        "intakeTitle": "Rust/C/Python Hero Lane Private Reviewer Intake",
        "sourceBundle": bundle,
        "reviewerIntakePacket": {
            "intakeStatus": "ready_for_private_review",
            "reviewerDecisionStatus": "not_recorded",
            "reviewSurface": "private_only",
            "reviewerMustInspect": [
                "Whether the P43 target reality matrix is understandable and honestly scoped.",
                "Whether the P44 Rust/C/Python hero runtime lane is a useful private preview center.",
                "Whether the P45 selected generated-target C/Rust attachment wording is clear enough.",
                "Whether the P46 private preview boundary blocks public-package interpretation.",
                "Whether the P47 bundle index is sufficient for a first outside private reviewer.",
            ],
            "reviewerQuestions": [
                "Is Rust/C/Python the right first hero lane for Forge/eFrog?",
                "What single non-generated C/Rust fixture family should be added before public preview?",
                "Which blocked claim is most likely to be misread by an external reviewer?",
                "Does the private copy distinguish selected generated-target roundtrip from arbitrary source roundtrip?",
                "What evidence would be required before any package-publication task is allowed?",
            ],
            "allowedReviewerOutcomes": [
                "accept_private_scope",
                "request_copy_tightening",
                "request_non_generated_c_rust_fixtures",
                "request_runtime_toolchain_expansion",
                "hold_private_preview",
            ],
        },
        "handoffChecklist": [
            {
                "id": "send_p47_bundle",
                "status": "ready",
                "instruction": "Send the P47 report and evidence packet to the private reviewer.",
            },
            {
                "id": "send_p48_intake",
                "status": "ready",
                "instruction": "Send this P48 intake packet as the review rubric.",
            },
            {
                "id": "collect_reviewer_decision",
                "status": "pending_human",
                "instruction": "Record reviewer response in a later packet; this packet does not approve anything.",
            },
            {
                "id": "preserve_claim_boundary",
                "status": "required",
                "instruction": "Keep public/package/correctness/performance/all-target claims blocked during review.",
            },
        ],
        "allowedPrivateReviewerStatements": [
            "A private reviewer can inspect the Rust/C/Python hero lane bundle.",
            "The current bundle links the P43, P44, P45, and P46 evidence packets through P47.",
            "The reviewer is being asked to evaluate scope clarity and next evidence needs, not to approve public release.",
        ],
        "blockedStatements": [
            "A reviewer has approved the bundle.",
            "Forge/eFrog is public-ready.",
            "A package has been published.",
            "Checkout is enabled.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
            "Full arbitrary C/Rust source roundtrip is supported.",
            "All 13 free targets runtime-execute.",
            "All 13 free targets roundtrip.",
            "Hardware, silicon, Lean-proof, zkproof, Pro-target, production, or all-target readiness is established.",
        ],
        "summary": {
            "intakeReady": True,
            "reviewerDecisionRecorded": False,
            "sourceBundleValidationPass": bundle["validationStatus"] == "pass",
            "sourceBundleClaimFlagsAllFalse": bundle["claimFlagsAllFalse"],
            "sourceBundleEvidenceCount": bundle["bundleEvidenceCount"],
            "heroTargets": bundle["heroTargets"],
            "heroRuntimeCellCount": bundle["heroRuntimeCellCount"],
            "heroRuntimeSampleExecutions": bundle["heroRuntimeSampleExecutions"],
            "selectedRoundtripAttachmentTargets": bundle["selectedRoundtripAttachmentTargets"],
            "selectedRoundtripAttachmentPackets": bundle["selectedRoundtripAttachmentPackets"],
            "selectedRoundtripAttachmentSamples": bundle["selectedRoundtripAttachmentSamples"],
            "packagePublished": False,
            "checkoutEnabled": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "runtimePerformanceClaim": False,
            "fullCRustRoundtripClaim": False,
            "allFreeTargetsRuntimeExecutionClaim": False,
            "allFreeTargetsRoundtripClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextMilestones": [
            "Send P47 and P48 to a private reviewer.",
            "Record the reviewer response in a later packet before changing release posture.",
            "If reviewer asks for more evidence, prefer non-generated C/Rust source fixtures under a separate gate.",
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
        "title": "FEF-P48 Private Reviewer Intake Packet",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "private_reviewer_intake_ready_no_approval_recorded",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private reviewer intake packet only; it prepares review of the P47 bundle and records no reviewer approval, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, full C/Rust source roundtrip, all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P48 turns the P47 bundle into a private-review intake rubric.",
            "The reviewer can accept private scope, request copy tightening, request fixtures, or hold preview.",
            "No reviewer decision is recorded in this packet.",
            "All public release and correctness/performance/all-target claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p48_private_reviewer_intake_packet.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p48_private_reviewer_intake_packet.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p48_private_reviewer_intake_packet.v0",
        "date": DATE,
        "title": "FEF-P48 Private Reviewer Intake Packet",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Send P47/P48 to a private reviewer, then record the response before changing release posture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    bundle = payload["sourceBundle"]
    intake = payload["reviewerIntakePacket"]
    checklist_rows = [
        "| Checklist Item | Status | Instruction |",
        "|---|---|---|",
    ]
    for item in payload["handoffChecklist"]:
        checklist_rows.append(f"| `{item['id']}` | `{item['status']}` | {item['instruction']} |")
    return "\n".join(
        [
            "# FEF-P48 Private Reviewer Intake Packet",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Source Bundle",
            "",
            f"- Source packet: `{bundle['packetPath']}`",
            f"- Source report: `{bundle['reportPath']}`",
            f"- Source validation: `{bundle['validationStatus']}`",
            f"- Linked evidence count: `{bundle['bundleEvidenceCount']}`",
            f"- Hero targets: `{', '.join(bundle['heroTargets'])}`",
            f"- Hero runtime cells: `{bundle['heroRuntimeCellCount']}`",
            f"- Hero runtime samples: `{bundle['heroRuntimeSampleExecutions']}`",
            f"- Selected C/Rust attachment packets: `{bundle['selectedRoundtripAttachmentPackets']}`",
            f"- Selected C/Rust attachment samples: `{bundle['selectedRoundtripAttachmentSamples']}`",
            "",
            "## Reviewer Intake",
            "",
            f"- Intake status: `{intake['intakeStatus']}`",
            f"- Reviewer decision status: `{intake['reviewerDecisionStatus']}`",
            f"- Review surface: `{intake['reviewSurface']}`",
            "",
            "## Reviewer Must Inspect",
            "",
            *[f"- {item}" for item in intake["reviewerMustInspect"]],
            "",
            "## Reviewer Questions",
            "",
            *[f"- {item}" for item in intake["reviewerQuestions"]],
            "",
            "## Allowed Reviewer Outcomes",
            "",
            *[f"- `{item}`" for item in intake["allowedReviewerOutcomes"]],
            "",
            "## Handoff Checklist",
            "",
            *checklist_rows,
            "",
            "## Allowed Private Reviewer Statements",
            "",
            *[f"- {statement}" for statement in payload["allowedPrivateReviewerStatements"]],
            "",
            "## Blocked Statements",
            "",
            *[f"- {statement}" for statement in payload["blockedStatements"]],
            "",
            "## Boundary",
            "",
            "- Private reviewer intake only.",
            "- No reviewer decision, package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "- No full arbitrary C/Rust source roundtrip claim.",
            "- No all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P48 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P48 status")
    summary = payload["summary"]
    if summary["intakeReady"] is not True:
        raise ValueError("intake should be ready")
    if summary["reviewerDecisionRecorded"] is not False:
        raise ValueError("reviewer decision must not be recorded")
    if summary["sourceBundleValidationPass"] is not True:
        raise ValueError("source bundle must validate")
    if summary["sourceBundleClaimFlagsAllFalse"] is not True:
        raise ValueError("source bundle claim flags must remain false")
    if summary["sourceBundleEvidenceCount"] != 4:
        raise ValueError("expected four source bundle packets")
    if summary["heroTargets"] != ["rust", "c", "python"]:
        raise ValueError("unexpected hero target set")
    if summary["heroRuntimeCellCount"] != 12:
        raise ValueError("unexpected hero runtime cell count")
    if summary["heroRuntimeSampleExecutions"] != 72:
        raise ValueError("unexpected hero runtime sample count")
    if summary["selectedRoundtripAttachmentTargets"] != ["c", "rust"]:
        raise ValueError("unexpected selected attachment targets")
    if summary["selectedRoundtripAttachmentPackets"] != 10:
        raise ValueError("unexpected selected attachment packet count")
    if summary["selectedRoundtripAttachmentSamples"] != 34:
        raise ValueError("unexpected selected attachment sample count")
    for key in [
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "fullCRustRoundtripClaim",
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsRoundtripClaim",
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
    result_path = out_dir / f"fef_p48_private_reviewer_intake_packet_{STAMP}.json"
    report_path = report_dir / f"fef_p48_private_reviewer_intake_packet_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p48_private_reviewer_intake_packet.json"
    feed_path = command_feed_dir / f"fef_p48_private_reviewer_intake_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p48_private_reviewer_intake_packet")
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
    print("FEF_P48_PRIVATE_REVIEWER_INTAKE_PACKET_OK")
    print(f"intake_ready={built['payload']['summary']['intakeReady']}")
    print(f"reviewer_decision_recorded={built['payload']['summary']['reviewerDecisionRecorded']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
