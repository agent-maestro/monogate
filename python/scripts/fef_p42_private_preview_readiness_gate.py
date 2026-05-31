#!/usr/bin/env python3
"""FEF-P42 private preview readiness gate over selected Forge/eFrog evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p5_publication_copy_review as p5

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p42_private_preview_readiness_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P42_PRIVATE_PREVIEW_READINESS_GATE_PASS"

EVIDENCE_INPUTS = {
    "fefP31": ROOT / "reports/evidence_packets/fef_p31_free_target_emission_guard.json",
    "fefP32": ROOT / "reports/evidence_packets/fef_p32_free_target_runtime_helper_guard.json",
    "fefP34": ROOT / "reports/evidence_packets/fef_p34_clamp_guard_free_target_guard.json",
    "fefP35": ROOT / "reports/evidence_packets/fef_p35_clamp_guard_runtime_execution.json",
    "fefP37": ROOT / "reports/evidence_packets/fef_p37_verified_add_runtime_execution.json",
    "fefP38": ROOT / "reports/evidence_packets/fef_p38_runtime_helper_mix_runtime_execution.json",
    "fefP40": ROOT / "reports/evidence_packets/fef_p40_affine_poly_fixture_runtime_guard.json",
    "fefP41": ROOT / "reports/evidence_packets/fef_p41_four_fixture_capability_matrix_refresh.json",
}

FORBIDDEN_PHRASES = [
    "public ready",
    "public package available",
    "checkout enabled",
    "compiler correctness",
    "formal semantic equivalence",
    "runtime performance",
    "speedup",
    "production toolchain",
    "verilog target ready",
    "lean proofs emitted",
    "zkproof target ready",
    "silicon ready",
    "36 shipped targets",
    "all 13 free targets execute",
]

REQUIRED_BOUNDARY_PHRASES = [
    "private preview evidence only",
    "not a public package release",
    "not a compiler-correctness proof",
    "not a formal semantic-equivalence result",
    "not a runtime-performance benchmark",
    "not a checkout-enabled product",
]

PRIVATE_PREVIEW_COPY = """Private preview evidence only.

Forge/eFrog has selected private evidence for four fixture families across the
13 Forge free targets. The current selected matrix records emission and bounded
validation for verified_add, runtime_helper_mix, clamp_guard_mix, and
affine_poly_mix. Runtime execution is attached only for installed software
toolchains: C, C++, Rust, Python, JavaScript, and Java.

This is not a public package release, not a compiler-correctness proof, not a
formal semantic-equivalence result, not a runtime-performance benchmark, and
not a checkout-enabled product.
"""

CLAIM_FLAGS = {
    **dict(p5.CLAIM_FLAGS),
    "private_preview_release_ready": False,
    "selected_evidence_reviewed": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_target_readiness_claim": False,
}

NON_CLAIMS = [
    "FEF-P42 reviews selected private evidence readiness only.",
    "FEF-P42 does not publish a package.",
    "FEF-P42 does not enable checkout or commerce.",
    "FEF-P42 does not claim public readiness.",
    "FEF-P42 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P42 does not claim runtime performance, production readiness, Verilog, Lean proofs, zkproof, silicon output, all-target readiness, or all-free-target runtime execution.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_private_copy(text: str) -> dict[str, Any]:
    lowered = " ".join(text.lower().split())
    forbidden_hits = [phrase for phrase in FORBIDDEN_PHRASES if phrase in lowered]
    required_missing = [phrase for phrase in REQUIRED_BOUNDARY_PHRASES if phrase not in lowered]
    return {
        "status": "pass" if not forbidden_hits and not required_missing else "fail",
        "forbiddenHits": forbidden_hits,
        "requiredBoundaryMissing": required_missing,
    }


def evidence_summaries() -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for key, path in EVIDENCE_INPUTS.items():
        packet = read_json(path)
        review = packet.get("semanticReview", {})
        summaries[key] = {
            "path": str(path.relative_to(ROOT)),
            "reviewDecision": packet.get("reviewDecision"),
            "validationStatus": packet.get("validationStatus"),
            "semanticStrength": packet.get("semanticStrength"),
            "claimFlagsAllFalse": all(value is False for value in packet.get("claimFlags", {}).values()),
            "summary": {
                "fixtureCount": review.get("fixtureCount"),
                "freeTargetCount": review.get("freeTargetCount"),
                "matrixCellCount": review.get("matrixCellCount"),
                "runtimeOverlayCellCount": review.get("runtimeOverlayCellCount"),
                "runtimeOverlaySampleExecutions": review.get("runtimeOverlaySampleExecutions"),
                "runtimeOverlayMaxAbsError": review.get("runtimeOverlayMaxAbsError"),
                "totalSampleExecutions": review.get("totalSampleExecutions"),
                "maxAbsError": review.get("maxAbsError"),
            },
        }
    return summaries


def build_payload() -> dict[str, Any]:
    evidence = evidence_summaries()
    p41_summary = evidence["fefP41"]["summary"]
    copy_scan = scan_private_copy(PRIVATE_PREVIEW_COPY)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p42-private-preview-readiness-gate",
        "decision": "selected_private_preview_evidence_reviewed_publication_blocked",
        "privatePreviewCopy": PRIVATE_PREVIEW_COPY,
        "privateCopyReview": copy_scan,
        "evidenceInputs": evidence,
        "selectedCapabilitySnapshot": {
            "fixtureCount": p41_summary["fixtureCount"],
            "freeTargetCount": p41_summary["freeTargetCount"],
            "matrixCellCount": p41_summary["matrixCellCount"],
            "runtimeOverlayCellCount": p41_summary["runtimeOverlayCellCount"],
            "runtimeOverlaySampleExecutions": p41_summary["runtimeOverlaySampleExecutions"],
            "runtimeOverlayMaxAbsError": p41_summary["runtimeOverlayMaxAbsError"],
        },
        "releaseGates": [
            {"id": "selected_four_fixture_matrix_recorded", "status": "pass"},
            {"id": "selected_runtime_overlays_recorded", "status": "pass"},
            {"id": "private_preview_copy_boundary_review_passed", "status": "pass"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
            {"id": "public_readiness", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivatePreviewClaims": [
            "Selected private evidence covers four fixture families across all 13 Forge free targets.",
            "The selected matrix has 52 emission/validation passes.",
            "Selected runtime overlays cover C, C++, Rust, Python, JavaScript, and Java.",
            "The selected runtime overlays include 24 runtime cells and 144 sample executions.",
        ],
        "blockedPublicClaims": [
            "public package availability",
            "checkout availability",
            "public readiness",
            "all-free-target runtime execution",
            "general compiler correctness",
            "formal semantic equivalence",
            "runtime performance",
            "production toolchain readiness",
            "Verilog/Lean proof/zkproof/silicon readiness",
            "36 shipped targets",
        ],
        "summary": {
            "privateCopyReviewPassed": copy_scan["status"] == "pass",
            "evidenceInputsValid": all(item["validationStatus"] == "pass" for item in evidence.values()),
            "evidenceClaimFlagsAllFalse": all(item["claimFlagsAllFalse"] for item in evidence.values()),
            "fixtureCount": p41_summary["fixtureCount"],
            "freeTargetCount": p41_summary["freeTargetCount"],
            "matrixCellCount": p41_summary["matrixCellCount"],
            "runtimeOverlayCellCount": p41_summary["runtimeOverlayCellCount"],
            "runtimeOverlaySampleExecutions": p41_summary["runtimeOverlaySampleExecutions"],
            "runtimeOverlayMaxAbsError": p41_summary["runtimeOverlayMaxAbsError"],
            "packagePublished": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "checkoutEnabled": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextMilestones": [
            "Stop automatic fixture expansion unless a reviewer names a missing fixture family.",
            "If publication is desired, run a separate explicit release-action gate.",
            "If broader runtime support is desired, install additional target toolchains and add narrow runtime guards.",
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
        "title": "FEF-P42 Private Preview Readiness Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_private_preview_evidence_review_publication_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private preview evidence readiness gate only; no package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, production readiness, all-free-target runtime execution, Verilog, Lean proof, zkproof, or silicon claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selected evidence now includes a four-fixture x 13-free-target matrix.",
            "Runtime overlays cover six installed software targets, not all 13 free targets.",
            "Private preview copy boundary passes while publication, checkout, and public readiness remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p42_private_preview_readiness_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p42_private_preview_readiness_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p42_private_preview_readiness_gate.v0",
        "date": DATE,
        "title": "FEF-P42 Private Preview Readiness Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Choose explicit release-action gate, broader installed-toolchain runtime support, or stop Forge/eFrog expansion for now.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# FEF-P42 Private Preview Readiness Gate",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "## Selected Capability Snapshot",
        "",
    ]
    for key, value in payload["selectedCapabilitySnapshot"].items():
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
            "- Private preview evidence gate only.",
            "- No package publication or checkout claim.",
            "- No public readiness claim.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No runtime performance, production, all-free-target runtime, Verilog, Lean proof, zkproof, or silicon claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P42 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P42 status")
    summary = payload["summary"]
    if summary["privateCopyReviewPassed"] is not True:
        raise ValueError("private preview copy review must pass")
    if summary["evidenceInputsValid"] is not True:
        raise ValueError("evidence inputs must be valid")
    if summary["evidenceClaimFlagsAllFalse"] is not True:
        raise ValueError("evidence claim flags must remain false")
    expected = {
        "fixtureCount": 4,
        "freeTargetCount": 13,
        "matrixCellCount": 52,
        "runtimeOverlayCellCount": 24,
        "runtimeOverlaySampleExecutions": 144,
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise ValueError(f"unexpected {key}: {summary[key]}")
    if summary["runtimeOverlayMaxAbsError"] > 1.0e-12:
        raise ValueError("runtime overlay error exceeds tolerance")
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
    result_path = out_dir / f"fef_p42_private_preview_readiness_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p42_private_preview_readiness_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p42_private_preview_readiness_gate.json"
    feed_path = command_feed_dir / f"fef_p42_private_preview_readiness_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p42_private_preview_readiness_gate")
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
    print("FEF_P42_PRIVATE_PREVIEW_READINESS_GATE_OK")
    print(f"decision={built['payload']['decision']}")
    print(f"matrix_cells={built['payload']['summary']['matrixCellCount']}")
    print(f"runtime_samples={built['payload']['summary']['runtimeOverlaySampleExecutions']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
