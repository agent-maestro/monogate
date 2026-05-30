#!/usr/bin/env python3
"""FEF-P5 publication/copy review for monogate-forge-preview."""

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

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p5_publication_copy_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P5_PUBLICATION_COPY_REVIEW_PASS"

PACKAGE_ROOT = ROOT / "packages/monogate-forge-preview"
COPY_PATH = PACKAGE_ROOT / "PUBLIC_PREVIEW_COPY.md"

EVIDENCE_INPUTS = {
    "fefP1": ROOT / "reports/evidence_packets/fef_p1_public_compiler_preview_decision.json",
    "fefP2": ROOT / "reports/evidence_packets/fef_p2_clean_room_quickstart_scaffold.json",
    "fefP3": ROOT / "reports/evidence_packets/fef_p3_javascript_bridge_guard.json",
    "fefP4": ROOT / "reports/evidence_packets/fef_p4_non_python_source_semantic_comparison.json",
}

FORBIDDEN_PHRASES = [
    "36 shipped targets",
    "write math. get silicon",
    "bit-equivalent",
    "formally verified compiler",
    "lean proofs emitted",
    "zkproof target ready",
    "verilog target ready",
    "production toolchain",
    "checkout enabled",
    "public package available",
]

REQUIRED_BOUNDARY_PHRASES = [
    "not a public package release yet",
    "not a general compiler",
    "compiler-correctness proof",
    "formal semantic-equivalence result",
    "performance benchmark",
    "checkout-enabled product",
]

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "proof_claim": False,
    "package_published": False,
    "public_compiler_package_available": False,
    "public_checkout_enabled": False,
    "verilog_claim": False,
    "lean_proof_claim": False,
    "zkproof_claim": False,
    "silicon_claim": False,
}

NON_CLAIMS = [
    "FEF-P5 reviews copy and release gates only.",
    "FEF-P5 does not publish a package.",
    "FEF-P5 does not enable checkout or commerce.",
    "FEF-P5 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P5 does not claim runtime performance, production readiness, Verilog, Lean proofs, zkproof, or silicon output.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_copy(text: str) -> dict[str, Any]:
    lowered = text.lower()
    claim_text = _copy_text_without_blocked_phrase_section(lowered)
    forbidden_hits = [phrase for phrase in FORBIDDEN_PHRASES if phrase in claim_text]
    required_missing = [phrase for phrase in REQUIRED_BOUNDARY_PHRASES if phrase not in lowered]
    return {
        "copyPath": str(COPY_PATH.relative_to(ROOT)),
        "forbiddenHits": forbidden_hits,
        "requiredBoundaryMissing": required_missing,
        "status": "pass" if not forbidden_hits and not required_missing else "fail",
    }


def _copy_text_without_blocked_phrase_section(lowered: str) -> str:
    marker = "## blocked public phrases"
    start = lowered.find(marker)
    if start < 0:
        return lowered
    next_section = lowered.find("\n## ", start + len(marker))
    if next_section < 0:
        return lowered[:start]
    return lowered[:start] + lowered[next_section:]


def evidence_summaries() -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for key, path in EVIDENCE_INPUTS.items():
        packet = read_json(path)
        summaries[key] = {
            "path": str(path.relative_to(ROOT)),
            "reviewDecision": packet.get("reviewDecision"),
            "validationStatus": packet.get("validationStatus"),
            "claimBoundary": packet.get("claimBoundary"),
            "claimFlagsAllFalse": all(value is False for value in packet.get("claimFlags", {}).values()),
        }
    return summaries


def build_payload() -> dict[str, Any]:
    text = COPY_PATH.read_text(encoding="utf-8")
    scan = scan_copy(text)
    evidence = evidence_summaries()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p5-publication-copy-review",
        "decision": "copy_review_passed_publication_blocked",
        "package": {
            "name": "monogate-forge-preview",
            "path": str(PACKAGE_ROOT.relative_to(ROOT)),
            "copyPath": str(COPY_PATH.relative_to(ROOT)),
            "distributionStatus": "local_scaffold_not_published",
        },
        "copyReview": scan,
        "evidenceInputs": evidence,
        "releaseGates": [
            {"id": "fef_p1_preview_shape_selected", "status": "pass"},
            {"id": "fef_p2_clean_room_local_quickstart_passed", "status": "pass"},
            {"id": "fef_p3_javascript_bridge_guard_passed", "status": "pass"},
            {"id": "fef_p4_javascript_source_semantic_comparison_passed", "status": "pass"},
            {"id": "public_copy_boundary_review_passed", "status": "pass"},
            {"id": "package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "allowedPublicClaims": [
            "A local monogate-forge-preview scaffold exists.",
            "The local scaffold supports selected Python/JavaScript preview commands.",
            "A fresh local virtualenv quickstart passed for the selected Gaussian fixture.",
            "The real eFrog bridge guard executes generated JavaScript modules through Node for hosted fixtures.",
            "Selected JavaScript source fixtures have bounded sample-grid comparison against Forge Python and JavaScript outputs.",
        ],
        "blockedPublicClaims": [
            "published package availability",
            "checkout availability",
            "general compiler correctness",
            "formal semantic equivalence",
            "runtime performance",
            "production toolchain readiness",
            "Verilog/Lean proof/zkproof/silicon readiness",
            "36 shipped targets",
        ],
        "summary": {
            "copyReviewPassed": scan["status"] == "pass",
            "evidenceInputsValid": all(item["validationStatus"] == "pass" for item in evidence.values()),
            "evidenceClaimFlagsAllFalse": all(item["claimFlagsAllFalse"] for item in evidence.values()),
            "packagePublished": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "checkoutEnabled": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextMilestones": [
            "Run an explicit release action if/when publication is desired.",
            "FEF-P6 broaden original-runtime semantic comparison to C/Rust/MATLAB where local toolchains are available.",
            "Keep Forge public site copy aligned to installable monogate until publication happens.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P5 Publication Copy Review",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "copy_boundary_review_pass_publication_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Publication/copy review only; no package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, production readiness, Verilog, Lean proof, zkproof, or silicon claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Approved-copy draft exists for the local monogate-forge-preview scaffold.",
            "Copy scan passes forbidden-phrase and required-boundary checks.",
            "Publication remains blocked; checkout remains disabled.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p5_publication_copy_review.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p5_publication_copy_review.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p5_publication_copy_review.v0",
        "date": DATE,
        "title": "FEF-P5 Publication Copy Review",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Choose between explicit release action or FEF-P6 broader original-runtime semantic comparison.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# FEF-P5 Publication Copy Review",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P5 reviews public-preview copy for `monogate-forge-preview` and",
        "keeps package publication blocked. This is a copy/release-gate artifact,",
        "not a package publication.",
        "",
        "## Copy Review",
        "",
        f"- Copy path: `{payload['copyReview']['copyPath']}`",
        f"- Copy review status: `{payload['copyReview']['status']}`",
        f"- Forbidden hits: `{len(payload['copyReview']['forbiddenHits'])}`",
        f"- Missing required boundaries: `{len(payload['copyReview']['requiredBoundaryMissing'])}`",
        "",
        "## Release Gates",
        "",
        "| Gate | Status |",
        "|---|---|",
    ]
    for gate in payload["releaseGates"]:
        lines.append(f"| `{gate['id']}` | `{gate['status']}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No package publication or checkout claim.",
            "- No public readiness claim.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No runtime performance, production, Verilog, Lean proof, zkproof, or silicon claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P5 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P5 status")
    summary = payload["summary"]
    if summary["copyReviewPassed"] is not True:
        raise ValueError("copy review must pass")
    if summary["evidenceInputsValid"] is not True:
        raise ValueError("evidence inputs must be valid")
    if summary["evidenceClaimFlagsAllFalse"] is not True:
        raise ValueError("evidence input claim flags must remain false")
    for key in ["packagePublished", "publicReady", "safeToPublishPublicly", "checkoutEnabled"]:
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
    result_path = out_dir / f"fef_p5_publication_copy_review_{STAMP}.json"
    report_path = report_dir / f"fef_p5_publication_copy_review_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p5_publication_copy_review.json"
    feed_path = command_feed_dir / f"fef_p5_publication_copy_review_feed_{STAMP}.json"
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/fef_p5_publication_copy_review",
    )
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
    print("FEF_P5_PUBLICATION_COPY_REVIEW_OK")
    print(f"decision={built['payload']['decision']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
