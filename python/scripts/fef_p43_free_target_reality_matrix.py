#!/usr/bin/env python3
"""FEF-P43 free-target reality matrix."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p41_four_fixture_capability_matrix_refresh as p41
from scripts import fef_p42_private_preview_readiness_gate as p42

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p43_free_target_reality_matrix.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P43_FREE_TARGET_REALITY_MATRIX_PASS"

TOOLCHAIN_PROBES = {
    "c": ["gcc"],
    "cpp": ["g++"],
    "rust": ["rustc"],
    "python": ["python"],
    "go": ["go"],
    "java": ["javac", "java"],
    "kotlin": ["kotlinc"],
    "csharp": ["dotnet"],
    "javascript": ["node"],
    "wasm": ["wasm-interp", "wasmtime"],
    "matlab": ["matlab", "octave"],
    "lean": ["lean"],
    "zkproof": [],
}

HERO_TARGETS = ["rust", "c", "python"]
ROUNTRIP_TARGETS_WITH_SELECTED_EVIDENCE = ["javascript", "python"]

CLAIM_FLAGS = {
    "free_target_reality_matrix_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_free_targets_roundtrip_claim": False,
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
    "FEF-P43 summarizes current free-target evidence by target.",
    "FEF-P43 does not execute new runtime checks.",
    "FEF-P43 does not add new fixture families.",
    "FEF-P43 does not claim all 13 free targets runtime-execute.",
    "FEF-P43 does not claim all 13 free targets roundtrip.",
    "FEF-P43 does not claim all free targets are public-ready.",
    "FEF-P43 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P43 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P43 does not claim runtime performance, Verilog, Lean proofs, zkproof proofs, silicon output, hardware readiness, Pro-target readiness, or all-target readiness.",
]


def probe_toolchain(target: str) -> dict[str, Any]:
    commands = TOOLCHAIN_PROBES[target]
    detected = [{"command": command, "path": shutil.which(command)} for command in commands]
    available = bool(commands) and all(item["path"] for item in detected)
    if target in {"wasm", "matlab"}:
        available = any(item["path"] for item in detected)
    if not commands:
        status = "not_applicable"
    elif available:
        status = "available"
    else:
        status = "missing"
    return {
        "target": target,
        "requiredCommands": commands,
        "detectedCommands": detected,
        "toolchainStatus": status,
        "toolchainAvailable": available,
    }


def target_rows(p41_payload: dict[str, Any]) -> list[dict[str, Any]]:
    matrix_rows = p41_payload["matrixRows"]
    summary_by_target = {
        row["target"]: row for row in p41_payload["summary"]["runtimeOverlayByTarget"]
    }
    rows = []
    for target in p41_payload["targetOrder"]:
        cells = [row for row in matrix_rows if row["target"] == target]
        runtime_summary = summary_by_target[target]
        toolchain = probe_toolchain(target)
        runtime_pass_count = runtime_summary["runtimePassCount"]
        if runtime_pass_count == len(cells):
            runtime_status = "pass_selected_fixture_runtime"
            runtime_claim = "Selected runtime execution evidence exists for all four selected fixtures on this target."
        elif toolchain["toolchainAvailable"]:
            runtime_status = "toolchain_detected_runtime_not_wired_or_not_claimed"
            runtime_claim = "Toolchain detected locally, but selected runtime execution is not wired or not claimable for this matrix."
        else:
            runtime_status = "not_attempted_missing_or_unclaimed_toolchain"
            runtime_claim = "No selected runtime execution evidence for this target in the current matrix."

        if target in ROUNTRIP_TARGETS_WITH_SELECTED_EVIDENCE:
            roundtrip_status = "pass_selected_roundtrip_evidence"
            roundtrip_claim = "Selected eFrog/Forge roundtrip evidence exists for this target language."
        else:
            roundtrip_status = "not_attempted"
            roundtrip_claim = "No selected eFrog/Forge roundtrip evidence is attached for this target language."

        if target in HERO_TARGETS and runtime_status == "pass_selected_fixture_runtime":
            priority = "hero_runtime_lane"
        elif target in ROUNTRIP_TARGETS_WITH_SELECTED_EVIDENCE:
            priority = "roundtrip_lane"
        elif toolchain["toolchainAvailable"]:
            priority = "detected_toolchain_followup"
        else:
            priority = "future_toolchain_or_semantics_followup"

        allowed_claim = (
            f"{target}: selected emission and validation pass for four fixture families"
        )
        if runtime_status == "pass_selected_fixture_runtime":
            allowed_claim += ", with selected runtime execution evidence."
        else:
            allowed_claim += ", without selected runtime execution evidence."

        rows.append(
            {
                "target": target,
                "priorityClass": priority,
                "codegenStatus": "pass" if all(row["emissionStatus"] == "pass" for row in cells) else "fail",
                "validationStatus": "pass" if all(row["validationStatus"] == "pass" for row in cells) else "fail",
                "fixtureCount": len(cells),
                "emissionPassCount": sum(1 for row in cells if row["emissionStatus"] == "pass"),
                "validationPassCount": sum(1 for row in cells if row["validationStatus"] == "pass"),
                "runtimeToolchain": toolchain,
                "runtimeCheckStatus": runtime_status,
                "runtimePassCount": runtime_pass_count,
                "runtimeSampleExecutions": runtime_summary["runtimeSampleExecutions"],
                "roundtripStatus": roundtrip_status,
                "allowedClaim": allowed_claim,
                "runtimeClaim": runtime_claim,
                "roundtripClaim": roundtrip_claim,
                "blockedClaims": [
                    "public readiness",
                    "production readiness",
                    "general compiler correctness",
                    "formal semantic equivalence",
                    "runtime performance",
                    "all-target readiness",
                ],
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], p41_summary: dict[str, Any], p42_summary: dict[str, Any]) -> dict[str, Any]:
    runtime_pass_targets = [row["target"] for row in rows if row["runtimeCheckStatus"] == "pass_selected_fixture_runtime"]
    detected_unwired_targets = [
        row["target"]
        for row in rows
        if row["runtimeCheckStatus"] == "toolchain_detected_runtime_not_wired_or_not_claimed"
    ]
    missing_or_unclaimed_targets = [
        row["target"]
        for row in rows
        if row["runtimeCheckStatus"] == "not_attempted_missing_or_unclaimed_toolchain"
    ]
    roundtrip_targets = [row["target"] for row in rows if row["roundtripStatus"] == "pass_selected_roundtrip_evidence"]
    return {
        "freeTargetCount": len(rows),
        "fixtureCount": p41_summary["fixtureCount"],
        "matrixCellCount": p41_summary["matrixCellCount"],
        "emissionPassTargetCount": sum(1 for row in rows if row["codegenStatus"] == "pass"),
        "validationPassTargetCount": sum(1 for row in rows if row["validationStatus"] == "pass"),
        "runtimePassTargetCount": len(runtime_pass_targets),
        "runtimePassTargets": runtime_pass_targets,
        "runtimeOverlayCellCount": p41_summary["runtimeOverlayCellCount"],
        "runtimeOverlaySampleExecutions": p41_summary["runtimeOverlaySampleExecutions"],
        "runtimeOverlayMaxAbsError": p41_summary["runtimeOverlayMaxAbsError"],
        "detectedToolchainRuntimeNotWiredTargets": detected_unwired_targets,
        "missingOrUnclaimedRuntimeTargets": missing_or_unclaimed_targets,
        "roundtripPassTargetCount": len(roundtrip_targets),
        "roundtripPassTargets": roundtrip_targets,
        "heroTargets": list(HERO_TARGETS),
        "privatePreviewPublicationBlocked": p42_summary["publicReady"] is False,
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "allFreeTargetsRuntimeExecutionClaim": False,
        "allFreeTargetsRoundtripClaim": False,
        "allFreeTargetsPublicReadyClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p41_payload = p41.build_payload()
    p42_payload = p42.build_payload()
    rows = target_rows(p41_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p43-free-target-reality-matrix",
        "decision": "free_target_reality_matrix_recorded_publication_blocked",
        "upstreamEvidence": {
            "fefP41": "reports/evidence_packets/fef_p41_four_fixture_capability_matrix_refresh.json",
            "fefP42": "reports/evidence_packets/fef_p42_private_preview_readiness_gate.json",
            "emlA13": "reports/evidence_packets/eml_a13_forge_efrog_roundtrip_advantage.json",
        },
        "targetRows": rows,
        "summary": summarize(rows, p41_payload["summary"], p42_payload["summary"]),
        "releaseGates": [
            {"id": "free_target_reality_matrix_recorded", "status": "pass"},
            {"id": "selected_four_fixture_matrix_recorded", "status": "pass"},
            {"id": "selected_runtime_targets_recorded", "status": "pass"},
            {"id": "all_free_targets_runtime_execution", "status": "blocked"},
            {"id": "all_free_targets_roundtrip", "status": "blocked"},
            {"id": "all_free_targets_public_ready", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Use Rust, C, and Python as the first hero-target hardening lane.",
            "Wire runtime execution for additional detected free-target toolchains only when the target semantics are narrow and testable.",
            "Keep Lean as proof-shape evidence until proof bodies are discharged without placeholder proof claims.",
            "Keep zkproof as circuit/evidence IR until a real proving system is wired and checked.",
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
        "title": "FEF-P43 Free Target Reality Matrix",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "target_level_reality_matrix_selected_evidence_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Target-level reality matrix only; selected emission/validation evidence exists for four fixture families across 13 free targets, selected runtime evidence exists only for six software targets, selected roundtrip evidence exists only for Python and JavaScript, and publication/public-readiness/compiler-correctness/formal-equivalence/runtime-performance claims remain blocked.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "All 13 free targets have selected four-fixture emission and validation evidence.",
            "C, C++, Rust, Python, JavaScript, and Java have selected runtime execution overlays.",
            "Python and JavaScript have selected eFrog/Forge roundtrip evidence.",
            "Rust, C, and Python are named as the first hero hardening lane.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p43_free_target_reality_matrix.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p43_free_target_reality_matrix.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p43_free_target_reality_matrix.v0",
        "date": DATE,
        "title": "FEF-P43 Free Target Reality Matrix",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Harden the Rust + C + Python hero lane or wire one additional detected runtime target behind a narrow guard.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Target | Priority | Codegen | Validation | Runtime | Runtime Samples | Roundtrip | Allowed Claim |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["targetRows"]:
        rows.append(
            f"| `{row['target']}` | `{row['priorityClass']}` | `{row['codegenStatus']}` | "
            f"`{row['validationStatus']}` | `{row['runtimeCheckStatus']}` | "
            f"`{row['runtimeSampleExecutions']}` | `{row['roundtripStatus']}` | {row['allowedClaim']} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P43 Free Target Reality Matrix",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Target Matrix",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Free targets checked: `{summary['freeTargetCount']}`",
            f"- Fixtures per target: `{summary['fixtureCount']}`",
            f"- Matrix cells checked: `{summary['matrixCellCount']}`",
            f"- Runtime pass targets: `{', '.join(summary['runtimePassTargets'])}`",
            f"- Runtime overlay sample executions: `{summary['runtimeOverlaySampleExecutions']}`",
            f"- Runtime overlay max absolute error: `{summary['runtimeOverlayMaxAbsError']:.3e}`",
            f"- Roundtrip pass targets: `{', '.join(summary['roundtripPassTargets'])}`",
            f"- Hero hardening targets: `{', '.join(summary['heroTargets'])}`",
            "",
            "## Boundary",
            "",
            "- Target-level reality matrix only.",
            "- No new runtime execution is performed by this pass.",
            "- No package publication, checkout, or public-readiness claim.",
            "- No all-free-target runtime or all-free-target roundtrip claim.",
            "- No compiler correctness, formal semantic equivalence, runtime performance, hardware, silicon, or proof claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P43 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P43 status")
    summary = payload["summary"]
    if summary["freeTargetCount"] != 13:
        raise ValueError("expected 13 free targets")
    if summary["fixtureCount"] != 4:
        raise ValueError("expected four fixture families")
    if summary["matrixCellCount"] != 52:
        raise ValueError("expected 52 target-fixture cells")
    if summary["emissionPassTargetCount"] != 13 or summary["validationPassTargetCount"] != 13:
        raise ValueError("all free targets must emit and validate in selected matrix")
    if summary["runtimePassTargets"] != ["c", "cpp", "rust", "python", "java", "javascript"]:
        raise ValueError("unexpected selected runtime target set")
    if summary["runtimeOverlaySampleExecutions"] != 144:
        raise ValueError("unexpected runtime sample count")
    if summary["runtimeOverlayMaxAbsError"] > 1.0e-12:
        raise ValueError("runtime overlay error exceeds tolerance")
    if summary["roundtripPassTargets"] != ["python", "javascript"]:
        raise ValueError("unexpected selected roundtrip target set")
    for key in [
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsRoundtripClaim",
        "allFreeTargetsPublicReadyClaim",
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
    result_path = out_dir / f"fef_p43_free_target_reality_matrix_{STAMP}.json"
    report_path = report_dir / f"fef_p43_free_target_reality_matrix_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p43_free_target_reality_matrix.json"
    feed_path = command_feed_dir / f"fef_p43_free_target_reality_matrix_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p43_free_target_reality_matrix")
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
    print("FEF_P43_FREE_TARGET_REALITY_MATRIX_OK")
    print(f"free_targets={built['payload']['summary']['freeTargetCount']}")
    print(f"runtime_pass_targets={','.join(built['payload']['summary']['runtimePassTargets'])}")
    print(f"roundtrip_pass_targets={','.join(built['payload']['summary']['roundtripPassTargets'])}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
