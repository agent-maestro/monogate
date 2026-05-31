#!/usr/bin/env python3
"""FEF-P44 Rust/C/Python hero-target hardening gate."""

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

from scripts import fef_p41_four_fixture_capability_matrix_refresh as p41
from scripts import fef_p43_free_target_reality_matrix as p43

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p44_hero_target_hardening_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P44_HERO_TARGET_HARDENING_GATE_PASS"

HERO_TARGETS = ["rust", "c", "python"]

CLAIM_FLAGS = {
    "hero_target_hardening_claim": False,
    "public_preview_release_claim": False,
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
    "FEF-P44 hardens only the selected Rust, C, and Python hero lane.",
    "FEF-P44 does not add a new fixture family.",
    "FEF-P44 does not execute all 13 free targets.",
    "FEF-P44 does not claim all 13 free targets runtime-execute.",
    "FEF-P44 does not claim all 13 free targets roundtrip.",
    "FEF-P44 does not claim all free targets are public-ready.",
    "FEF-P44 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P44 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P44 does not claim runtime performance, Verilog, Lean proofs, zkproof proofs, silicon output, hardware readiness, Pro-target readiness, or all-target readiness.",
]


def hero_fixture_rows(p41_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in HERO_TARGETS:
        for row in p41_payload["matrixRows"]:
            if row["target"] != target:
                continue
            rows.append(
                {
                    "target": row["target"],
                    "fixtureId": row["fixtureId"],
                    "fixtureKind": row["fixtureKind"],
                    "sourceFixture": row["sourceFixture"],
                    "emissionStatus": row["emissionStatus"],
                    "validationStatus": row["validationStatus"],
                    "validationLevel": row["validationLevel"],
                    "runtimeStatus": row["runtimeStatus"],
                    "runtimeLevel": row["runtimeLevel"],
                    "runtimeSampleCount": row["runtimeSampleCount"],
                    "runtimeMaxAbsError": row["runtimeMaxAbsError"],
                }
            )
    return rows


def summarize(
    p43_payload: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    target_rows = {row["target"]: row for row in p43_payload["targetRows"]}
    by_target = []
    for target in HERO_TARGETS:
        fixture_rows = [row for row in rows if row["target"] == target]
        by_target.append(
            {
                "target": target,
                "priorityClass": target_rows[target]["priorityClass"],
                "fixtureCount": len(fixture_rows),
                "emissionPassCount": sum(1 for row in fixture_rows if row["emissionStatus"] == "pass"),
                "validationPassCount": sum(1 for row in fixture_rows if row["validationStatus"] == "pass"),
                "runtimePassCount": sum(1 for row in fixture_rows if row["runtimeStatus"] == "pass"),
                "runtimeSampleExecutions": sum(row["runtimeSampleCount"] for row in fixture_rows),
                "runtimeMaxAbsError": max(row["runtimeMaxAbsError"] for row in fixture_rows),
                "roundtripStatus": target_rows[target]["roundtripStatus"],
                "runtimeToolchain": target_rows[target]["runtimeToolchain"],
            }
        )
    return {
        "heroTargetCount": len(HERO_TARGETS),
        "heroTargets": list(HERO_TARGETS),
        "fixtureCount": len({row["fixtureId"] for row in rows}),
        "heroRuntimeCellCount": len(rows),
        "heroEmissionPassCount": sum(1 for row in rows if row["emissionStatus"] == "pass"),
        "heroValidationPassCount": sum(1 for row in rows if row["validationStatus"] == "pass"),
        "heroRuntimePassCount": sum(1 for row in rows if row["runtimeStatus"] == "pass"),
        "heroRuntimeSampleExecutions": sum(row["runtimeSampleCount"] for row in rows),
        "heroRuntimeMaxAbsError": max(row["runtimeMaxAbsError"] for row in rows),
        "heroTargetsAllRuntimePass": all(
            row["runtimeStatus"] == "pass" and row["runtimeSampleCount"] > 0 for row in rows
        ),
        "heroTargetsAllToolchainsAvailable": all(
            target_rows[target]["runtimeToolchain"]["toolchainAvailable"] for target in HERO_TARGETS
        ),
        "heroTargetsByTarget": by_target,
        "pythonRoundtripEvidenceAttached": target_rows["python"]["roundtripStatus"]
        == "pass_selected_roundtrip_evidence",
        "rustRoundtripEvidenceAttached": target_rows["rust"]["roundtripStatus"]
        == "pass_selected_roundtrip_evidence",
        "cRoundtripEvidenceAttached": target_rows["c"]["roundtripStatus"]
        == "pass_selected_roundtrip_evidence",
        "releaseCandidateStatus": "private_hero_lane_candidate",
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
    p43_payload = p43.build_payload()
    rows = hero_fixture_rows(p41_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p44-hero-target-hardening-gate",
        "decision": "rust_c_python_hero_lane_hardened_publication_blocked",
        "upstreamEvidence": {
            "fefP41": "reports/evidence_packets/fef_p41_four_fixture_capability_matrix_refresh.json",
            "fefP43": "reports/evidence_packets/fef_p43_free_target_reality_matrix.json",
        },
        "heroTargets": list(HERO_TARGETS),
        "heroFixtureRows": rows,
        "summary": summarize(p43_payload, rows),
        "releaseGates": [
            {"id": "rust_c_python_hero_lane_selected", "status": "pass"},
            {"id": "hero_lane_four_fixture_runtime_cells_pass", "status": "pass"},
            {"id": "hero_lane_private_candidate", "status": "pass"},
            {"id": "rust_roundtrip_attached", "status": "blocked"},
            {"id": "c_roundtrip_attached", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "public_readiness", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivateClaims": [
            "Rust, C, and Python are the current Forge/eFrog hero hardening lane.",
            "The hero lane has selected runtime execution evidence for four fixture families.",
            "The hero lane contains 12 selected runtime cells and 72 sample executions.",
            "Python also has selected eFrog/Forge roundtrip evidence from the existing A13 packet.",
        ],
        "blockedClaims": [
            "public readiness",
            "package publication",
            "checkout availability",
            "all-free-target runtime execution",
            "all-free-target roundtrip",
            "Rust/C roundtrip readiness",
            "compiler correctness",
            "formal semantic equivalence",
            "runtime performance",
            "hardware/silicon/proof readiness",
        ],
        "nextMilestones": [
            "Attach selected eFrog/Forge roundtrip evidence for Rust or C if the decompiler surface is ready.",
            "Turn this hero lane into a private preview fixture bundle only after a separate release-action gate.",
            "Do not expand fixture families unless a reviewer names a missing behavior.",
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
        "title": "FEF-P44 Hero Target Hardening Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "rust_c_python_selected_runtime_hero_lane_private_candidate",
        "semanticReview": payload["summary"],
        "claimBoundary": "Rust/C/Python hero-target hardening gate only; selected runtime evidence covers four fixture families across three hero targets, Python has selected roundtrip evidence, Rust/C roundtrip remains blocked, and publication/public-readiness/compiler-correctness/formal-equivalence/runtime-performance claims remain blocked.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Rust, C, and Python are consolidated as the first hero hardening lane.",
            "All 12 hero fixture-target runtime cells pass with 72 total sample executions.",
            "Python has selected roundtrip evidence; Rust and C roundtrip remain explicit blockers.",
            "The lane is a private candidate only, not a public release or correctness claim.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p44_hero_target_hardening_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p44_hero_target_hardening_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p44_hero_target_hardening_gate.v0",
        "date": DATE,
        "title": "FEF-P44 Hero Target Hardening Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach selected Rust or C roundtrip evidence, or run an explicit private preview release-action gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Target | Fixture | Emission | Validation | Runtime | Samples | Max Abs Error |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["heroFixtureRows"]:
        rows.append(
            f"| `{row['target']}` | `{row['fixtureId']}` | `{row['emissionStatus']}` | "
            f"`{row['validationStatus']}` | `{row['runtimeStatus']}` | "
            f"`{row['runtimeSampleCount']}` | `{row['runtimeMaxAbsError']:.3e}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P44 Hero Target Hardening Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Hero Runtime Cells",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Hero targets: `{', '.join(summary['heroTargets'])}`",
            f"- Fixtures per hero target: `{summary['fixtureCount']}`",
            f"- Hero runtime cells: `{summary['heroRuntimeCellCount']}`",
            f"- Hero runtime passes: `{summary['heroRuntimePassCount']}`",
            f"- Hero runtime sample executions: `{summary['heroRuntimeSampleExecutions']}`",
            f"- Hero runtime max absolute error: `{summary['heroRuntimeMaxAbsError']:.3e}`",
            f"- Release candidate status: `{summary['releaseCandidateStatus']}`",
            f"- Python roundtrip evidence attached: `{summary['pythonRoundtripEvidenceAttached']}`",
            f"- Rust roundtrip evidence attached: `{summary['rustRoundtripEvidenceAttached']}`",
            f"- C roundtrip evidence attached: `{summary['cRoundtripEvidenceAttached']}`",
            "",
            "## Boundary",
            "",
            "- Rust/C/Python hero-target hardening gate only.",
            "- No new fixture family or all-target runtime execution claim.",
            "- No Rust/C roundtrip claim yet.",
            "- No package publication, checkout, public-readiness, compiler-correctness, formal-equivalence, runtime-performance, hardware, silicon, or proof claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P44 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P44 status")
    summary = payload["summary"]
    if summary["heroTargets"] != HERO_TARGETS:
        raise ValueError("unexpected hero target set")
    if summary["fixtureCount"] != 4:
        raise ValueError("expected four selected fixtures")
    if summary["heroRuntimeCellCount"] != 12:
        raise ValueError("expected 12 hero runtime cells")
    if summary["heroEmissionPassCount"] != 12 or summary["heroValidationPassCount"] != 12:
        raise ValueError("all hero cells must emit and validate")
    if summary["heroRuntimePassCount"] != 12:
        raise ValueError("all hero runtime cells must pass")
    if summary["heroRuntimeSampleExecutions"] != 72:
        raise ValueError("unexpected hero runtime sample count")
    if summary["heroRuntimeMaxAbsError"] > 1.0e-12:
        raise ValueError("hero runtime max abs error exceeds tolerance")
    if summary["heroTargetsAllRuntimePass"] is not True:
        raise ValueError("hero targets must all runtime-pass")
    if summary["heroTargetsAllToolchainsAvailable"] is not True:
        raise ValueError("hero target toolchains must be locally available")
    if summary["pythonRoundtripEvidenceAttached"] is not True:
        raise ValueError("python roundtrip evidence should be attached")
    if summary["rustRoundtripEvidenceAttached"] is not False:
        raise ValueError("rust roundtrip must remain blocked")
    if summary["cRoundtripEvidenceAttached"] is not False:
        raise ValueError("c roundtrip must remain blocked")
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
    result_path = out_dir / f"fef_p44_hero_target_hardening_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p44_hero_target_hardening_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p44_hero_target_hardening_gate.json"
    feed_path = command_feed_dir / f"fef_p44_hero_target_hardening_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p44_hero_target_hardening_gate")
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
    print("FEF_P44_HERO_TARGET_HARDENING_GATE_OK")
    print(f"hero_targets={','.join(built['payload']['summary']['heroTargets'])}")
    print(f"hero_runtime_cells={built['payload']['summary']['heroRuntimeCellCount']}")
    print(f"hero_runtime_samples={built['payload']['summary']['heroRuntimeSampleExecutions']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
