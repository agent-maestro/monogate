#!/usr/bin/env python3
"""FEF-P47 private reviewer bundle index for the Rust/C/Python hero lane."""

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
SCHEMA_VERSION = "monogate.fef_p47_private_reviewer_bundle_index.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P47_PRIVATE_REVIEWER_BUNDLE_INDEX_PASS"

EVIDENCE_INPUTS = [
    {
        "id": "fefP43",
        "path": ROOT / "reports/evidence_packets/fef_p43_free_target_reality_matrix.json",
        "role": "target_level_reality_matrix",
    },
    {
        "id": "fefP44",
        "path": ROOT / "reports/evidence_packets/fef_p44_hero_target_hardening_gate.json",
        "role": "hero_lane_runtime_gate",
    },
    {
        "id": "fefP45",
        "path": ROOT / "reports/evidence_packets/fef_p45_c_rust_roundtrip_attachment_gate.json",
        "role": "selected_c_rust_roundtrip_attachment",
    },
    {
        "id": "fefP46",
        "path": ROOT / "reports/evidence_packets/fef_p46_hero_lane_private_preview_release_gate.json",
        "role": "private_preview_release_action_gate",
    },
]

CLAIM_FLAGS = {
    "private_reviewer_bundle_index_claim": False,
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
    "FEF-P47 records a private reviewer bundle index only.",
    "FEF-P47 does not publish a package.",
    "FEF-P47 does not enable checkout or commerce.",
    "FEF-P47 does not claim public readiness.",
    "FEF-P47 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P47 does not claim runtime performance.",
    "FEF-P47 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P47 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P47 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_rows() -> list[dict[str, Any]]:
    rows = []
    for item in EVIDENCE_INPUTS:
        packet = read_json(item["path"])
        review = packet.get("semanticReview", {})
        rows.append(
            {
                "id": item["id"],
                "role": item["role"],
                "path": str(item["path"].relative_to(ROOT)),
                "artifactId": packet.get("artifactId"),
                "title": packet.get("title"),
                "reviewDecision": packet.get("reviewDecision"),
                "validationStatus": packet.get("validationStatus"),
                "semanticStrength": packet.get("semanticStrength"),
                "claimFlagsAllFalse": all(
                    value is False for value in packet.get("claimFlags", {}).values()
                ),
                "reviewSummary": {
                    "heroTargets": review.get("heroTargets"),
                    "runtimePassTargets": review.get("runtimePassTargets"),
                    "roundtripPassTargets": review.get("roundtripPassTargets"),
                    "heroRuntimeCellCount": review.get("heroRuntimeCellCount"),
                    "heroRuntimeSampleExecutions": review.get("heroRuntimeSampleExecutions"),
                    "attachedTargets": review.get("attachedTargets"),
                    "attachmentPacketCount": review.get("attachmentPacketCount"),
                    "attachmentSampleCount": review.get("attachmentSampleCount"),
                    "privatePreviewReleaseActionApproved": review.get(
                        "privatePreviewReleaseActionApproved"
                    ),
                },
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    rows = evidence_rows()
    by_id = {row["id"]: row for row in rows}
    p43 = by_id["fefP43"]["reviewSummary"]
    p44 = by_id["fefP44"]["reviewSummary"]
    p45 = by_id["fefP45"]["reviewSummary"]
    p46 = by_id["fefP46"]["reviewSummary"]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p47-private-reviewer-bundle-index",
        "decision": "private_reviewer_bundle_index_ready_publication_blocked",
        "bundleTitle": "Rust/C/Python Hero Lane Private Reviewer Bundle",
        "evidenceRows": rows,
        "reviewerChecklist": [
            {
                "id": "target_reality_matrix_reviewed",
                "status": "ready",
                "instruction": "Start with FEF-P43 to see every free target row and the current runtime/roundtrip scope.",
            },
            {
                "id": "hero_runtime_lane_reviewed",
                "status": "ready",
                "instruction": "Use FEF-P44 to review the Rust/C/Python 12-cell runtime lane.",
            },
            {
                "id": "selected_c_rust_roundtrip_attachment_reviewed",
                "status": "ready",
                "instruction": "Use FEF-P45 for selected generated-target C/Rust re-ingest evidence only.",
            },
            {
                "id": "private_release_boundary_reviewed",
                "status": "ready",
                "instruction": "Use FEF-P46 for the private preview copy and release-action boundary.",
            },
            {
                "id": "public_claims_checked",
                "status": "required",
                "instruction": "Do not convert private-review wording into public package, correctness, performance, or all-target claims.",
            },
        ],
        "allowedPrivateReviewerStatements": [
            "Rust, C, and Python are the current private Forge/eFrog hero lane.",
            "The hero lane has selected runtime evidence over 12 fixture-target cells and 72 sample executions.",
            "Selected generated C/Rust targets have re-ingest attachment evidence over 10 packets and 34 sample comparisons.",
            "The private preview gate approves reviewer-facing evidence packaging only.",
        ],
        "blockedStatements": [
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
            "bundleEvidenceCount": len(rows),
            "allEvidenceValidationPass": all(row["validationStatus"] == "pass" for row in rows),
            "allEvidenceClaimFlagsFalse": all(row["claimFlagsAllFalse"] for row in rows),
            "heroTargets": p44["heroTargets"],
            "runtimePassTargets": p43["runtimePassTargets"],
            "roundtripPassTargets": p43["roundtripPassTargets"],
            "heroRuntimeCellCount": p44["heroRuntimeCellCount"],
            "heroRuntimeSampleExecutions": p44["heroRuntimeSampleExecutions"],
            "selectedRoundtripAttachmentTargets": p45["attachedTargets"],
            "selectedRoundtripAttachmentPackets": p45["attachmentPacketCount"],
            "selectedRoundtripAttachmentSamples": p45["attachmentSampleCount"],
            "privatePreviewReleaseActionApproved": p46["privatePreviewReleaseActionApproved"],
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
            "Give the reviewer this bundle index plus the four linked evidence packets.",
            "If broader C/Rust roundtrip is desired, add non-generated source fixtures under a separate gate.",
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
        "title": "FEF-P47 Private Reviewer Bundle Index",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "private_reviewer_bundle_index_publication_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private reviewer bundle index only; it links FEF-P43, FEF-P44, FEF-P45, and FEF-P46 while keeping package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, full C/Rust source roundtrip, all-free-target runtime, all-free-target roundtrip, hardware, silicon, and proof claims blocked.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P47 gives reviewers one index over P43, P44, P45, and P46.",
            "The bundle allows private hero-lane evidence statements only.",
            "The checklist names the evidence order and public-claim boundary.",
            "No package is published and no public release claim is made.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p47_private_reviewer_bundle_index.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p47_private_reviewer_bundle_index.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p47_private_reviewer_bundle_index.v0",
        "date": DATE,
        "title": "FEF-P47 Private Reviewer Bundle Index",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Hand the P47 reviewer bundle to a private reviewer or broaden C/Rust roundtrip with non-generated source fixtures.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    evidence_rows = [
        "| ID | Role | Status | Evidence |",
        "|---|---|---|---|",
    ]
    for row in payload["evidenceRows"]:
        evidence_rows.append(
            f"| `{row['id']}` | `{row['role']}` | `{row['validationStatus']}` | `{row['path']}` |"
        )
    checklist_rows = [
        "| Checklist Item | Status | Instruction |",
        "|---|---|---|",
    ]
    for item in payload["reviewerChecklist"]:
        checklist_rows.append(f"| `{item['id']}` | `{item['status']}` | {item['instruction']} |")
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P47 Private Reviewer Bundle Index",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Evidence Index",
            "",
            *evidence_rows,
            "",
            "## Reviewer Checklist",
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
            "## Summary",
            "",
            f"- Bundle evidence count: `{summary['bundleEvidenceCount']}`",
            f"- Hero targets: `{', '.join(summary['heroTargets'])}`",
            f"- Hero runtime cells: `{summary['heroRuntimeCellCount']}`",
            f"- Hero runtime samples: `{summary['heroRuntimeSampleExecutions']}`",
            f"- Selected roundtrip attachment targets: `{', '.join(summary['selectedRoundtripAttachmentTargets'])}`",
            f"- Selected roundtrip attachment packets: `{summary['selectedRoundtripAttachmentPackets']}`",
            f"- Selected roundtrip attachment samples: `{summary['selectedRoundtripAttachmentSamples']}`",
            "",
            "## Boundary",
            "",
            "- Private reviewer bundle index only.",
            "- No package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "- No full arbitrary C/Rust source roundtrip claim.",
            "- No all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P47 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P47 status")
    summary = payload["summary"]
    if summary["bundleEvidenceCount"] != 4:
        raise ValueError("expected four linked evidence packets")
    if summary["allEvidenceValidationPass"] is not True:
        raise ValueError("all linked evidence packets must validate")
    if summary["allEvidenceClaimFlagsFalse"] is not True:
        raise ValueError("all linked evidence claim flags must remain false")
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
    if summary["privatePreviewReleaseActionApproved"] is not True:
        raise ValueError("private preview release action should be approved")
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
    result_path = out_dir / f"fef_p47_private_reviewer_bundle_index_{STAMP}.json"
    report_path = report_dir / f"fef_p47_private_reviewer_bundle_index_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p47_private_reviewer_bundle_index.json"
    feed_path = command_feed_dir / f"fef_p47_private_reviewer_bundle_index_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p47_private_reviewer_bundle_index")
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
    print("FEF_P47_PRIVATE_REVIEWER_BUNDLE_INDEX_OK")
    print(f"bundle_evidence_count={built['payload']['summary']['bundleEvidenceCount']}")
    print(f"hero_targets={','.join(built['payload']['summary']['heroTargets'])}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
