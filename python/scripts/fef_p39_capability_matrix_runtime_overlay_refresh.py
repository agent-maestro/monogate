#!/usr/bin/env python3
"""FEF-P39 selected capability matrix runtime overlay refresh."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p35_clamp_guard_runtime_execution as p35
from scripts import fef_p36_free_target_capability_matrix as p36
from scripts import fef_p37_verified_add_runtime_execution as p37
from scripts import fef_p38_runtime_helper_mix_runtime_execution as p38

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p39_capability_matrix_runtime_overlay_refresh.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P39_CAPABILITY_MATRIX_RUNTIME_OVERLAY_REFRESH_PASS"

RUNTIME_SOURCES = [
    {
        "fixtureId": "verified_add",
        "builder": p37.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p37_verified_add_runtime_execution.json",
    },
    {
        "fixtureId": "runtime_helper_mix",
        "builder": p38.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p38_runtime_helper_mix_runtime_execution.json",
    },
    {
        "fixtureId": "clamp_guard_mix",
        "builder": p35.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p35_clamp_guard_runtime_execution.json",
    },
]

CLAIM_FLAGS = {
    "free_target_capability_matrix_claim": False,
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
    "FEF-P39 refreshes the selected capability matrix runtime overlay using prior FEF-P35, FEF-P37, and FEF-P38 runtime evidence.",
    "FEF-P39 does not execute all 13 free targets.",
    "FEF-P39 does not add new runtime toolchains beyond C, C++, Rust, Python, JavaScript, and Java.",
    "FEF-P39 does not claim arbitrary branch/control-flow support.",
    "FEF-P39 does not claim all free targets are public-ready.",
    "FEF-P39 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P39 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P39 does not claim runtime performance, Verilog, silicon, hardware, Pro-target, or all-target readiness.",
]


@lru_cache(maxsize=1)
def _build_payload_cached() -> dict[str, Any]:
    base = p36.build_payload()
    matrix_rows = copy.deepcopy(base["matrixRows"])
    runtime_sources = []
    runtime_overlay_rows = []

    for source in RUNTIME_SOURCES:
        runtime_payload = source["builder"]()
        runtime_sources.append(
            {
                "fixtureId": source["fixtureId"],
                "sourceFixture": runtime_payload["sourceFixture"],
                "sourceArtifactId": runtime_payload["artifactId"],
                "sourceDecision": runtime_payload["decision"],
                "sourceEvidencePath": source["evidencePath"],
                "runtimeTargets": runtime_payload["summary"]["runtimeTargets"],
                "sampleCountPerTarget": runtime_payload["summary"]["sampleCountPerTarget"],
                "totalSampleExecutions": runtime_payload["summary"]["totalSampleExecutions"],
                "maxAbsError": runtime_payload["summary"]["maxAbsError"],
            }
        )
        runtime_by_target = {row["target"]: row for row in runtime_payload["runtimeRows"]}
        for row in matrix_rows:
            if row["fixtureId"] != source["fixtureId"] or row["target"] not in runtime_by_target:
                continue
            runtime_row = runtime_by_target[row["target"]]
            row["runtimeStatus"] = runtime_row["runtimeStatus"]
            row["runtimeLevel"] = runtime_row["runtimeLevel"]
            row["runtimeSampleCount"] = runtime_row["sampleCount"]
            row["runtimeMaxAbsError"] = runtime_row["maxAbsError"]
            runtime_overlay_rows.append(
                {
                    "fixtureId": row["fixtureId"],
                    "target": row["target"],
                    "runtimeStatus": row["runtimeStatus"],
                    "runtimeLevel": row["runtimeLevel"],
                    "sampleCount": row["runtimeSampleCount"],
                    "maxAbsError": row["runtimeMaxAbsError"],
                }
            )

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p39-capability-matrix-runtime-overlay-refresh",
        "decision": "selected_capability_matrix_runtime_overlay_refreshed",
        "baseMatrixArtifactId": base["artifactId"],
        "fixtureRows": copy.deepcopy(base["fixtureRows"]),
        "targetOrder": copy.deepcopy(base["targetOrder"]),
        "matrixRows": matrix_rows,
        "runtimeSources": runtime_sources,
        "runtimeOverlayRows": runtime_overlay_rows,
        "summary": summarize(base, matrix_rows, runtime_sources, runtime_overlay_rows),
        "releaseGates": [
            {"id": "selected_fixture_matrix_all_13_free_targets_emit", "status": "pass"},
            {"id": "selected_fixture_matrix_all_13_free_targets_validate", "status": "pass"},
            {"id": "selected_runtime_overlay_executes_for_three_fixtures", "status": "pass"},
            {"id": "all_free_targets_runtime_execution", "status": "blocked"},
            {"id": "all_free_targets_public_ready", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Add runtime execution checks for additional free targets where local toolchains are installed.",
            "Add more fixture families before any public preview claim widens.",
            "Keep public package publication blocked until explicit release action.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_payload() -> dict[str, Any]:
    return copy.deepcopy(_build_payload_cached())


def summarize(
    base: dict[str, Any],
    matrix_rows: list[dict[str, Any]],
    runtime_sources: list[dict[str, Any]],
    runtime_overlay_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    by_fixture = []
    for source in runtime_sources:
        rows = [row for row in runtime_overlay_rows if row["fixtureId"] == source["fixtureId"]]
        by_fixture.append(
            {
                "fixtureId": source["fixtureId"],
                "sourceFixture": source["sourceFixture"],
                "runtimeCellCount": len(rows),
                "runtimePassCount": sum(1 for row in rows if row["runtimeStatus"] == "pass"),
                "runtimeTargets": [row["target"] for row in rows],
                "runtimeSampleExecutions": sum(row["sampleCount"] for row in rows),
                "runtimeMaxAbsError": max(row["maxAbsError"] for row in rows),
            }
        )
    by_target = []
    for target in base["targetOrder"]:
        rows = [row for row in matrix_rows if row["target"] == target]
        runtime_rows = [row for row in rows if row["runtimeStatus"] == "pass"]
        by_target.append(
            {
                "target": target,
                "fixtureCount": len(rows),
                "emissionPassCount": sum(1 for row in rows if row["emissionStatus"] == "pass"),
                "validationPassCount": sum(1 for row in rows if row["validationStatus"] == "pass"),
                "runtimePassCount": len(runtime_rows),
                "runtimeSampleExecutions": sum(row["runtimeSampleCount"] for row in runtime_rows),
            }
        )
    return {
        "fixtureCount": base["summary"]["fixtureCount"],
        "freeTargetCount": base["summary"]["freeTargetCount"],
        "matrixCellCount": base["summary"]["matrixCellCount"],
        "emissionPassCount": sum(1 for row in matrix_rows if row["emissionStatus"] == "pass"),
        "validationPassCount": sum(1 for row in matrix_rows if row["validationStatus"] == "pass"),
        "allMatrixEmissionPass": all(row["emissionStatus"] == "pass" for row in matrix_rows),
        "allMatrixValidationPass": all(row["validationStatus"] == "pass" for row in matrix_rows),
        "runtimeOverlayFixtureCount": len(runtime_sources),
        "runtimeOverlayCellCount": len(runtime_overlay_rows),
        "runtimeOverlayPassCount": sum(1 for row in runtime_overlay_rows if row["runtimeStatus"] == "pass"),
        "runtimeOverlayTargetSet": sorted({row["target"] for row in runtime_overlay_rows}),
        "runtimeOverlaySampleExecutions": sum(row["sampleCount"] for row in runtime_overlay_rows),
        "runtimeOverlayMaxAbsError": max(row["maxAbsError"] for row in runtime_overlay_rows),
        "runtimeOverlayByFixture": by_fixture,
        "runtimeOverlayByTarget": by_target,
        "allRuntimeOverlayCellsPass": all(row["runtimeStatus"] == "pass" for row in runtime_overlay_rows),
        "allFreeTargetsRuntimeExecutionClaim": False,
        "allFreeTargetsPublicReadyClaim": False,
        "targetAllReadyClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P39 Capability Matrix Runtime Overlay Refresh",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_fixture_matrix_with_three_selected_runtime_overlays",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected capability matrix refresh only; it overlays prior runtime execution evidence for three selected fixtures across six installed software targets, and makes no all-free-target runtime execution, public readiness, compiler correctness, formal equivalence, publication, runtime performance, hardware, Pro-target, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "The matrix still covers verified_add, runtime_helper_mix, and clamp_guard_mix across all 13 free targets.",
            "All 39 fixture-target cells emit and validate at the selected level.",
            "Runtime overlays now cover all three selected fixtures across C, C++, Rust, Python, JavaScript, and Java.",
            "The refreshed runtime overlay records 18 selected runtime cells and 108 total sample executions.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p39_capability_matrix_runtime_overlay_refresh.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p39_capability_matrix_runtime_overlay_refresh.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p39_capability_matrix_runtime_overlay_refresh.v0",
        "date": DATE,
        "title": "FEF-P39 Capability Matrix Runtime Overlay Refresh",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add runtime checks for additional installed free-target toolchains or broaden fixture families.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Fixture | Target | Emission | Validation | Runtime | Samples | Max Abs Error |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["matrixRows"]:
        max_abs = "n/a" if row["runtimeMaxAbsError"] is None else f"{row['runtimeMaxAbsError']:.3e}"
        rows.append(
            f"| `{row['fixtureId']}` | `{row['target']}` | `{row['emissionStatus']}` | "
            f"`{row['validationStatus']}` | `{row['runtimeStatus']}` | "
            f"`{row['runtimeSampleCount']}` | `{max_abs}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P39 Capability Matrix Runtime Overlay Refresh",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Runtime Sources",
            "",
            *[
                f"- `{source['fixtureId']}`: `{source['sourceFixture']}` "
                f"(`{source['totalSampleExecutions']}` samples, max abs error "
                f"`{source['maxAbsError']:.3e}`)"
                for source in payload["runtimeSources"]
            ],
            "",
            "## Matrix",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Fixtures checked: `{summary['fixtureCount']}`",
            f"- Free targets checked: `{summary['freeTargetCount']}`",
            f"- Matrix cells checked: `{summary['matrixCellCount']}`",
            f"- Emission passes: `{summary['emissionPassCount']}`",
            f"- Validation passes: `{summary['validationPassCount']}`",
            f"- Runtime overlay fixtures: `{summary['runtimeOverlayFixtureCount']}`",
            f"- Runtime overlay cells: `{summary['runtimeOverlayCellCount']}`",
            f"- Runtime overlay sample executions: `{summary['runtimeOverlaySampleExecutions']}`",
            f"- Runtime overlay max absolute error: `{summary['runtimeOverlayMaxAbsError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Selected capability matrix refresh only.",
            "- Runtime overlays cover selected C, C++, Rust, Python, JavaScript, and Java generated targets only.",
            "- This refresh does not execute all 13 free targets.",
            "- No arbitrary branch/control-flow support claim.",
            "- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.",
            "- No runtime performance, package publication, checkout, hardware, Pro-target, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P39 schema")
    summary = payload["summary"]
    if summary["fixtureCount"] != 3:
        raise ValueError("expected three selected fixtures")
    if summary["freeTargetCount"] != 13:
        raise ValueError("expected 13 free targets")
    if summary["matrixCellCount"] != 39:
        raise ValueError("expected a 3 x 13 fixture matrix")
    if summary["emissionPassCount"] != 39 or summary["validationPassCount"] != 39:
        raise ValueError("all matrix cells must emit and validate")
    if summary["runtimeOverlayFixtureCount"] != 3:
        raise ValueError("expected runtime overlays for three fixtures")
    if summary["runtimeOverlayCellCount"] != 18:
        raise ValueError("expected 18 runtime overlay cells")
    if summary["runtimeOverlayPassCount"] != 18:
        raise ValueError("all runtime overlay cells must pass")
    if summary["runtimeOverlayTargetSet"] != ["c", "cpp", "java", "javascript", "python", "rust"]:
        raise ValueError("unexpected runtime overlay target set")
    if summary["runtimeOverlaySampleExecutions"] != 108:
        raise ValueError("unexpected runtime overlay sample execution count")
    if summary["runtimeOverlayMaxAbsError"] > p38.ATOL:
        raise ValueError("runtime overlay error exceeds tolerance")
    for key in [
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsPublicReadyClaim",
        "targetAllReadyClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p39_capability_matrix_runtime_overlay_refresh_{STAMP}.json"
    report_path = report_dir / f"fef_p39_capability_matrix_runtime_overlay_refresh_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p39_capability_matrix_runtime_overlay_refresh.json"
    feed_path = command_feed_dir / f"fef_p39_capability_matrix_runtime_overlay_refresh_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p39_capability_matrix_runtime_overlay_refresh")
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
    print("FEF_P39_CAPABILITY_MATRIX_RUNTIME_OVERLAY_REFRESH_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"free_targets={built['payload']['summary']['freeTargetCount']}")
    print(f"matrix_cells={built['payload']['summary']['matrixCellCount']}")
    print(f"runtime_overlay_cells={built['payload']['summary']['runtimeOverlayCellCount']}")
    print(f"runtime_samples={built['payload']['summary']['runtimeOverlaySampleExecutions']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
