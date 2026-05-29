#!/usr/bin/env python3
"""EML-A17 private review dry run.

Runs one concrete private workflow:

A14 Gaussian stable export packet -> packet-builder-style candidate review
packet -> A15 Glass Box mount card.

This is a file-backed dry run only. It does not edit command-center UI, engine,
Forge, or eFrog behavior.
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

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_a17_private_review_dry_run.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A17_PRIVATE_REVIEW_DRY_RUN_PASS"

EXPORT_PACKET_PATH = ROOT / "python/results/eml_forge_efrog_export_packets/gaussian_stable_holdout_semantic_compare_v0_export_packet_v0_2026_05_29.json"
MOUNT_CARD_PATH = ROOT / "python/results/eml_glassbox_mount_cards/gaussian_stable_holdout_semantic_compare_v0_glassbox_mount_card_v0_2026_05_29.json"
A14_EVIDENCE_PATH = ROOT / "reports/evidence_packets/eml_a14_forge_efrog_export_ux.json"
A15_EVIDENCE_PATH = ROOT / "reports/evidence_packets/eml_a15_glassbox_evidence_mount.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "automatic_approval": False,
    "deployment_performed": False,
    "engine_behavior_changed": False,
    "engine_files_modified": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "production_runtime_claim": False,
    "certified_safety_claim": False,
    "broad_eml_advantage_claim": False,
    "proof_claim": False,
}

NON_CLAIMS = [
    "A17 is a private dry run over existing A14/A15 artifacts.",
    "A17 does not change Forge, eFrog, command-center, or Monogate Engine behavior.",
    "A17 does not approve public display or deployment.",
    "A17 does not prove compiler correctness, formal equivalence, runtime performance, production runtime, certified safety, or broad EML advantage.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("_", "-")
        .replace(" ", "-")
        .replace("/", "-")
        .strip("-")
    )


def build_candidate_review_packet(export_packet: dict[str, Any], mount_card: dict[str, Any]) -> dict[str, Any]:
    title = "Gaussian Stable Forge/eFrog Glass Box Candidate Review"
    packet = {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": slugify(title),
        "title": title,
        "reviewDecision": "candidate_only",
        "validationStatus": "pass",
        "replayStatus": "not_applicable_private_review_dry_run",
        "semanticStrength": "private_review_dry_run_from_a14_export_to_a15_mount_card",
        "semanticReview": {
            "artifact_type": "compiler_output",
            "generated_by": "A17 private review dry run",
            "source_artifact_id": "eml-a14-forge-efrog-export-ux",
            "source_packet_type": export_packet["schemaVersion"],
            "source_decision": export_packet["reviewerDecision"],
            "source_validation_status": export_packet["semanticSampleGridStatus"],
            "source_replay_status": export_packet["roundtripLinkStatus"],
            "evidence_strength": "gaussian_stable_export_packet_plus_glassbox_mount_card",
            "reviewer_action": "Keep private; use as the first end-to-end packet-builder dry run.",
            "next_step": "Use this candidate to drive the future Glass Box adapter once the engine worktree is coordinated.",
            "function_name": export_packet["functionName"],
            "source_path": export_packet["sourcePath"],
            "canonical_eml_hash": export_packet["canonicalEmlHash"],
            "semantic_sample_count": export_packet["semanticSampleCount"],
            "roundtrip_case_count": export_packet["roundtripCaseCount"],
            "roundtrip_link_status": export_packet["roundtripLinkStatus"],
            "glassbox_mount_card_id": mount_card["mountCardId"],
            "glassbox_slot": mount_card["glassBoxSlot"],
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "claimBoundary": "Candidate-only private review packet; no public surfacing, compiler correctness, formal equivalence, runtime performance, production runtime, certified safety, or broad EML advantage claim.",
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Starts from the Gaussian stable A14 export packet.",
            "Preserves the canonical EML hash and roundtrip-link status.",
            "Links to the corresponding A15 Glass Box mount card.",
            "Keeps all public, runtime, proof, compiler, and safety claims blocked.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a17_private_review_dry_run.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a17_private_review_dry_run.py",
        ],
        "timeline": [
            {
                "label": "A14 export selected",
                "status": "pass",
                "detail": export_packet["exportId"],
            },
            {
                "label": "Candidate review packet generated",
                "status": "candidate",
                "detail": "Private packet-builder-style candidate only.",
            },
            {
                "label": "A15 mount card linked",
                "status": "pass",
                "detail": mount_card["mountCardId"],
            },
        ],
        "reviewReasons": [],
        "reviewNotes": "Generated by A17 private dry run. Treat as draft until reviewer approval.",
        "sourceReportPath": str(EXPORT_PACKET_PATH.relative_to(ROOT)),
        "evidencePaths": [
            str(EXPORT_PACKET_PATH.relative_to(ROOT)),
            str(MOUNT_CARD_PATH.relative_to(ROOT)),
            str(A14_EVIDENCE_PATH.relative_to(ROOT)),
            str(A15_EVIDENCE_PATH.relative_to(ROOT)),
        ],
    }
    validate_candidate_review_packet(packet)
    return packet


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    export_packet = read_json(EXPORT_PACKET_PATH)
    mount_card = read_json(MOUNT_CARD_PATH)
    candidate = build_candidate_review_packet(export_packet, mount_card)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-a17-private-review-dry-run",
        "selectedCase": "gaussian_stable_holdout_semantic_compare_v0",
        "chain": [
            "A14 export packet",
            "packet-builder-style candidate review packet",
            "A15 Glass Box mount card",
        ],
        "sourceEvidence": candidate["evidencePaths"],
        "candidateReviewPacketId": candidate["artifactId"],
        "summary": {
            "dryRunCount": 1,
            "candidateReviewPacketCount": 1,
            "selectedFunction": export_packet["functionName"],
            "semanticSampleCount": export_packet["semanticSampleCount"],
            "roundtripCaseCount": export_packet["roundtripCaseCount"],
            "roundtripLinked": export_packet["roundtripLinkStatus"] == "linked_by_canonical_eml_hash",
            "mountCardLinked": mount_card["sourceExportId"] == export_packet["exportId"],
            "automaticApproval": False,
            "publicReady": False,
            "deploymentPerformed": False,
            "engineFilesModified": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload, candidate)
    return payload, candidate


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "EML-A17 Private Review Dry Run",
        "reviewDecision": "private_dry_run_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable_private_review_dry_run",
        "semanticStrength": "one_case_private_workflow_from_a14_to_a15",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private dry run only; candidate review packet remains candidate-only and no public, runtime, compiler, proof, or safety claim is made.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Completes one file-backed A14 -> packet-builder candidate -> A15 workflow.",
            "Uses Gaussian stable because it is a true holdout source family.",
            "Keeps Glass Box adapter implementation deferred until engine worktree coordination.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a17_private_review_dry_run.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a17_private_review_dry_run.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a17_private_review_dry_run.v0",
        "date": DATE,
        "title": "EML-A17 Private Review Dry Run",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Repeat the dry run through the live command-center UI or implement saved private drafts.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any], candidate: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# EML-A17 Private Review Dry Run",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A17 runs one concrete private workflow from A14 export evidence to an A15 Glass Box mount card.",
        "",
        "## Chain",
        "",
    ]
    for step in payload["chain"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "## Candidate",
            "",
            f"- Candidate packet: `{candidate['artifactId']}`",
            f"- Function: `{summary['selectedFunction']}`",
            f"- Semantic samples: `{summary['semanticSampleCount']}`",
            f"- Roundtrip cases: `{summary['roundtripCaseCount']}`",
            f"- Roundtrip linked: `{summary['roundtripLinked']}`",
            f"- Mount card linked: `{summary['mountCardLinked']}`",
            "",
            "## Boundary",
            "",
            "- Candidate-only private review packet.",
            "- No automatic approval.",
            "- No public-readiness or deployment claim.",
            "- No engine file modification.",
            "- No compiler correctness, formal equivalence, runtime performance, production runtime, certified safety, proof, or broad EML advantage claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_candidate_review_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != EVIDENCE_SCHEMA_VERSION:
        raise ValueError("invalid candidate packet schema")
    if packet["reviewDecision"] != "candidate_only":
        raise ValueError("candidate packet must remain candidate_only")
    if packet["semanticReview"]["function_name"] != "gaussian_stable":
        raise ValueError("A17 must use gaussian_stable")
    if packet["semanticReview"]["roundtrip_link_status"] != "linked_by_canonical_eml_hash":
        raise ValueError("A17 selected case should be roundtrip-linked")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any], candidate: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["dryRunCount"] != 1:
        raise ValueError("expected one dry run")
    if summary["candidateReviewPacketCount"] != 1:
        raise ValueError("expected one candidate review packet")
    if summary["mountCardLinked"] is not True:
        raise ValueError("mount card must link to selected export")
    for key in ["automaticApproval", "publicReady", "deploymentPerformed", "engineFilesModified"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    if candidate["artifactId"] != payload["candidateReviewPacketId"]:
        raise ValueError("candidate id mismatch")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, candidate_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload, candidate = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_a17_private_review_dry_run_{STAMP}.json"
    candidate_path = candidate_dir / f"{candidate['artifactId']}_{STAMP}.json"
    report_path = report_dir / f"eml_a17_private_review_dry_run_{STAMP}.md"
    evidence_path = evidence_dir / "eml_a17_private_review_dry_run.json"
    feed_path = command_feed_dir / f"eml_a17_private_review_dry_run_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload, candidate), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "candidate": candidate,
        "result_path": str(result_path),
        "candidate_path": str(candidate_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a17_private_review_dry_run")
    parser.add_argument("--candidate-dir", type=Path, default=ROOT / "python/results/eml_private_review_candidate_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.candidate_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"], built["candidate"])
    print("EML_A17_PRIVATE_REVIEW_DRY_RUN_OK")
    print(f"candidate={built['payload']['candidateReviewPacketId']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
