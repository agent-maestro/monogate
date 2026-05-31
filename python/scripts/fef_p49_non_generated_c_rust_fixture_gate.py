#!/usr/bin/env python3
"""FEF-P49 non-generated C/Rust fixture gate for the hero lane."""

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

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p49_non_generated_c_rust_fixture_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P49_NON_GENERATED_C_RUST_FIXTURE_GATE_PASS"

P6_PACKET = ROOT / "reports/evidence_packets/fef_p6_broader_original_runtime_semantic_comparison.json"
P48_PACKET = ROOT / "reports/evidence_packets/fef_p48_private_reviewer_intake_packet.json"

CLAIM_FLAGS = {
    "non_generated_c_rust_fixture_evidence_attached": False,
    "non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "all_free_targets_roundtrip_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_target_readiness_claim": False,
    "private_reviewer_decision_recorded": False,
    "public_preview_release_claim": False,
    "package_published": False,
    "checkout_enabled": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
}

NON_CLAIMS = [
    "FEF-P49 attaches selected non-generated C/Rust source fixture semantic evidence to the hero-lane review surface.",
    "FEF-P49 does not claim non-generated source roundtrip.",
    "FEF-P49 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P49 does not record reviewer approval or rejection.",
    "FEF-P49 does not publish a package.",
    "FEF-P49 does not enable checkout or commerce.",
    "FEF-P49 does not claim public readiness.",
    "FEF-P49 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P49 does not claim runtime performance.",
    "FEF-P49 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P49 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_packet_summaries() -> dict[str, dict[str, Any]]:
    p6 = read_json(P6_PACKET)
    p48 = read_json(P48_PACKET)
    p6_review = p6.get("semanticReview", {})
    p48_review = p48.get("semanticReview", {})
    return {
        "fefP6": {
            "path": str(P6_PACKET.relative_to(ROOT)),
            "title": p6.get("title"),
            "reviewDecision": p6.get("reviewDecision"),
            "validationStatus": p6.get("validationStatus"),
            "semanticStrength": p6.get("semanticStrength"),
            "claimFlagsAllFalse": all(value is False for value in p6.get("claimFlags", {}).values()),
            "caseCount": p6_review.get("caseCount"),
            "passCount": p6_review.get("passCount"),
            "sampleCount": p6_review.get("sampleCount"),
            "sourceLanguages": p6_review.get("sourceLanguages"),
            "targetLanguages": p6_review.get("targetLanguages"),
            "maxAbsError": p6_review.get("maxAbsError"),
            "maxRelError": p6_review.get("maxRelError"),
            "unavailableOriginalRuntimes": p6_review.get("unavailableOriginalRuntimes"),
        },
        "fefP48": {
            "path": str(P48_PACKET.relative_to(ROOT)),
            "title": p48.get("title"),
            "reviewDecision": p48.get("reviewDecision"),
            "validationStatus": p48.get("validationStatus"),
            "semanticStrength": p48.get("semanticStrength"),
            "claimFlagsAllFalse": all(value is False for value in p48.get("claimFlags", {}).values()),
            "intakeReady": p48_review.get("intakeReady"),
            "reviewerDecisionRecorded": p48_review.get("reviewerDecisionRecorded"),
            "heroTargets": p48_review.get("heroTargets"),
            "heroRuntimeCellCount": p48_review.get("heroRuntimeCellCount"),
            "heroRuntimeSampleExecutions": p48_review.get("heroRuntimeSampleExecutions"),
            "selectedRoundtripAttachmentTargets": p48_review.get("selectedRoundtripAttachmentTargets"),
            "selectedRoundtripAttachmentPackets": p48_review.get("selectedRoundtripAttachmentPackets"),
            "selectedRoundtripAttachmentSamples": p48_review.get("selectedRoundtripAttachmentSamples"),
        },
    }


def build_payload() -> dict[str, Any]:
    sources = source_packet_summaries()
    p6 = sources["fefP6"]
    p48 = sources["fefP48"]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p49-non-generated-c-rust-fixture-gate",
        "decision": "selected_non_generated_c_rust_semantic_evidence_attached_roundtrip_blocked",
        "sourceEvidence": sources,
        "attachmentRows": [
            {
                "id": "non_generated_c_rust_source_semantic_evidence",
                "status": "pass_attached",
                "sourcePacket": p6["path"],
                "evidenceKind": "selected_original_runtime_semantic_comparison",
                "sourceLanguages": p6["sourceLanguages"],
                "targetLanguages": p6["targetLanguages"],
                "caseCount": p6["caseCount"],
                "sampleCount": p6["sampleCount"],
                "allowedClaim": (
                    "Selected non-generated C/Rust source fixtures decompile through eFrog, "
                    "compile to Forge Python/JavaScript, and match original local runtimes "
                    "over deterministic samples."
                ),
                "blockedClaims": [
                    "non-generated source roundtrip",
                    "full arbitrary C/Rust source roundtrip",
                    "compiler correctness",
                    "formal semantic equivalence",
                    "runtime performance",
                    "public readiness",
                ],
            }
        ],
        "releaseGates": [
            {"id": "selected_non_generated_c_rust_semantic_evidence_attached", "status": "pass"},
            {"id": "non_generated_source_roundtrip_claim", "status": "blocked"},
            {"id": "full_c_rust_roundtrip_claim", "status": "blocked"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "public_readiness", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivateClaims": [
            "Selected non-generated C/Rust source fixtures have original-runtime semantic comparison evidence.",
            "The attached non-generated source fixture evidence covers 5 cases and 23 deterministic samples.",
            "The evidence compares original C/Rust runtimes against Forge Python/JavaScript outputs after eFrog decompilation.",
            "This evidence can inform private reviewer assessment of the Rust/C/Python hero lane.",
        ],
        "blockedClaims": [
            "non-generated source roundtrip is supported",
            "full arbitrary C/Rust source roundtrip is supported",
            "Forge/eFrog is public-ready",
            "a package has been published",
            "checkout is enabled",
            "compiler correctness has been proved",
            "formal semantic equivalence has been proved",
            "runtime performance has been established",
            "all 13 free targets runtime-execute",
            "all 13 free targets roundtrip",
            "hardware, silicon, Lean-proof, zkproof, Pro-target, production, or all-target readiness is established",
        ],
        "summary": {
            "nonGeneratedCRustSemanticEvidenceAttached": True,
            "nonGeneratedSourceRoundtripClaim": False,
            "fullCRustRoundtripClaim": False,
            "reviewerDecisionRecorded": False,
            "sourceEvidenceValidationPass": all(
                item["validationStatus"] == "pass" for item in sources.values()
            ),
            "sourceEvidenceClaimFlagsAllFalse": all(
                item["claimFlagsAllFalse"] is True for item in sources.values()
            ),
            "p48IntakeReady": p48["intakeReady"],
            "heroTargets": p48["heroTargets"],
            "heroRuntimeCellCount": p48["heroRuntimeCellCount"],
            "heroRuntimeSampleExecutions": p48["heroRuntimeSampleExecutions"],
            "selectedGeneratedRoundtripAttachmentTargets": p48[
                "selectedRoundtripAttachmentTargets"
            ],
            "selectedGeneratedRoundtripAttachmentPackets": p48[
                "selectedRoundtripAttachmentPackets"
            ],
            "selectedGeneratedRoundtripAttachmentSamples": p48[
                "selectedRoundtripAttachmentSamples"
            ],
            "nonGeneratedSourceCaseCount": p6["caseCount"],
            "nonGeneratedSourcePassCount": p6["passCount"],
            "nonGeneratedSourceSampleCount": p6["sampleCount"],
            "nonGeneratedSourceLanguages": p6["sourceLanguages"],
            "nonGeneratedTargetLanguages": p6["targetLanguages"],
            "nonGeneratedMaxAbsError": p6["maxAbsError"],
            "nonGeneratedMaxRelError": p6["maxRelError"],
            "packagePublished": False,
            "checkoutEnabled": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "runtimePerformanceClaim": False,
            "allFreeTargetsRuntimeExecutionClaim": False,
            "allFreeTargetsRoundtripClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextMilestones": [
            "Ask the private reviewer whether P49 answers the non-generated C/Rust fixture request.",
            "If broader roundtrip is required, build an explicit non-generated source re-ingest gate instead of relabeling P49.",
            "Keep package publication blocked until reviewer response and release-action gates are recorded.",
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
        "title": "FEF-P49 Non-Generated C/Rust Fixture Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_non_generated_c_rust_semantic_evidence_attached_roundtrip_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected non-generated C/Rust source semantic evidence attachment only; it attaches FEF-P6 evidence to the P48 private-review intake and does not claim non-generated source roundtrip, full C/Rust source roundtrip, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof readiness.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P49 attaches selected non-generated C/Rust source fixture semantic evidence to the hero-lane review surface.",
            "The attached evidence covers 5 original-runtime cases and 23 deterministic samples.",
            "This is semantic comparison evidence, not non-generated source roundtrip.",
            "No reviewer decision or public release claim is recorded.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p49_non_generated_c_rust_fixture_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p49_non_generated_c_rust_fixture_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p49_non_generated_c_rust_fixture_gate.v0",
        "date": DATE,
        "title": "FEF-P49 Non-Generated C/Rust Fixture Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Ask the private reviewer whether P49 satisfies the requested non-generated C/Rust fixture evidence, or build a separate source re-ingest gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        "| Attachment | Status | Evidence kind | Cases | Samples | Blocked scope |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in payload["attachmentRows"]:
        rows.append(
            f"| `{row['id']}` | `{row['status']}` | `{row['evidenceKind']}` | {row['caseCount']} | {row['sampleCount']} | `{', '.join(row['blockedClaims'][:2])}` |"
        )
    return "\n".join(
        [
            "# FEF-P49 Non-Generated C/Rust Fixture Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Attachment",
            "",
            *rows,
            "",
            "## Allowed Private Claims",
            "",
            *[f"- {claim}" for claim in payload["allowedPrivateClaims"]],
            "",
            "## Blocked Claims",
            "",
            *[f"- {claim}" for claim in payload["blockedClaims"]],
            "",
            "## Summary",
            "",
            f"- Hero targets: `{', '.join(summary['heroTargets'])}`",
            f"- Selected generated roundtrip attachment packets: `{summary['selectedGeneratedRoundtripAttachmentPackets']}`",
            f"- Selected generated roundtrip attachment samples: `{summary['selectedGeneratedRoundtripAttachmentSamples']}`",
            f"- Non-generated source cases: `{summary['nonGeneratedSourceCaseCount']}`",
            f"- Non-generated source samples: `{summary['nonGeneratedSourceSampleCount']}`",
            f"- Non-generated source languages: `{', '.join(summary['nonGeneratedSourceLanguages'])}`",
            f"- Non-generated target languages: `{', '.join(summary['nonGeneratedTargetLanguages'])}`",
            f"- Non-generated max abs error: `{summary['nonGeneratedMaxAbsError']:.3e}`",
            f"- Non-generated max rel error: `{summary['nonGeneratedMaxRelError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Selected non-generated C/Rust source semantic evidence attachment only.",
            "- No non-generated source roundtrip claim.",
            "- No full arbitrary C/Rust source roundtrip claim.",
            "- No reviewer decision, package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "- No all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P49 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P49 status")
    summary = payload["summary"]
    if summary["nonGeneratedCRustSemanticEvidenceAttached"] is not True:
        raise ValueError("non-generated C/Rust evidence should be attached")
    if summary["sourceEvidenceValidationPass"] is not True:
        raise ValueError("source evidence must validate")
    if summary["sourceEvidenceClaimFlagsAllFalse"] is not True:
        raise ValueError("source evidence claim flags must remain false")
    if summary["p48IntakeReady"] is not True:
        raise ValueError("P48 intake must be ready")
    if summary["heroTargets"] != ["rust", "c", "python"]:
        raise ValueError("unexpected hero targets")
    if summary["selectedGeneratedRoundtripAttachmentTargets"] != ["c", "rust"]:
        raise ValueError("unexpected selected generated roundtrip targets")
    if summary["nonGeneratedSourceCaseCount"] != 5:
        raise ValueError("unexpected non-generated source case count")
    if summary["nonGeneratedSourcePassCount"] != 5:
        raise ValueError("all non-generated source cases must pass")
    if summary["nonGeneratedSourceSampleCount"] != 23:
        raise ValueError("unexpected non-generated sample count")
    if summary["nonGeneratedSourceLanguages"] != ["c", "rust"]:
        raise ValueError("expected C/Rust source languages")
    if summary["nonGeneratedTargetLanguages"] != ["python", "javascript"]:
        raise ValueError("expected Python/JavaScript comparison targets")
    for key in [
        "nonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "reviewerDecisionRecorded",
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
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
    result_path = out_dir / f"fef_p49_non_generated_c_rust_fixture_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p49_non_generated_c_rust_fixture_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p49_non_generated_c_rust_fixture_gate.json"
    feed_path = command_feed_dir / f"fef_p49_non_generated_c_rust_fixture_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p49_non_generated_c_rust_fixture_gate")
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
    print("FEF_P49_NON_GENERATED_C_RUST_FIXTURE_GATE_OK")
    print(f"non_generated_cases={built['payload']['summary']['nonGeneratedSourceCaseCount']}")
    print(f"non_generated_samples={built['payload']['summary']['nonGeneratedSourceSampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
