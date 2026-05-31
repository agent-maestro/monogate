#!/usr/bin/env python3
"""FEF-P36 selected free-target capability matrix with runtime overlay."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p31_free_target_emission_guard as p31
from scripts import fef_p32_free_target_runtime_helper_guard as p32
from scripts import fef_p34_clamp_guard_free_target_guard as p34
from scripts import fef_p35_clamp_guard_runtime_execution as p35

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p36_free_target_capability_matrix.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P36_FREE_TARGET_CAPABILITY_MATRIX_PASS"

FIXTURE_BUILDERS = [
    {
        "id": "verified_add",
        "kind": "arithmetic",
        "builder": p31.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p31_free_target_emission_guard.json",
    },
    {
        "id": "runtime_helper_mix",
        "kind": "runtime_helper",
        "builder": p32.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p32_free_target_runtime_helper_guard.json",
    },
    {
        "id": "clamp_guard_mix",
        "kind": "clamp_guard",
        "builder": p34.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p34_clamp_guard_free_target_guard.json",
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
    "FEF-P36 records a selected-fixture capability matrix over FEF-P31, FEF-P32, FEF-P34, and FEF-P35 evidence.",
    "FEF-P36 does not execute all 13 free targets.",
    "FEF-P36 does not add runtime checks beyond the FEF-P35 selected clamp/guard runtime guard.",
    "FEF-P36 does not claim arbitrary branch/control-flow support.",
    "FEF-P36 does not claim all free targets are public-ready.",
    "FEF-P36 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P36 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P36 does not claim runtime performance, Verilog, silicon, hardware, Pro-target, or all-target readiness.",
]


def run(cmd: list[str], *, timeout: int = 30) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return {
        "returnCode": proc.returncode,
        "status": "pass" if proc.returncode == 0 else "fail",
        "outputExcerpt": output[:900],
    }


@lru_cache(maxsize=1)
def _build_payload_cached() -> dict[str, Any]:
    fixtures = []
    matrix_rows = []
    target_order: list[str] = []

    for fixture in FIXTURE_BUILDERS:
        upstream_payload = fixture["builder"]()
        target_rows = upstream_payload["targetRows"]
        if not target_order:
            target_order = [row["target"] for row in target_rows]
        fixtures.append(
            {
                "id": fixture["id"],
                "kind": fixture["kind"],
                "sourceFixture": upstream_payload["sourceFixture"],
                "upstreamArtifactId": upstream_payload["artifactId"],
                "upstreamDecision": upstream_payload["decision"],
                "upstreamEvidencePath": fixture["evidencePath"],
                "summary": upstream_payload["summary"],
            }
        )
        for row in target_rows:
            matrix_rows.append(
                {
                    "fixtureId": fixture["id"],
                    "fixtureKind": fixture["kind"],
                    "sourceFixture": upstream_payload["sourceFixture"],
                    "target": row["target"],
                    "emissionStatus": row["emissionStatus"],
                    "validationStatus": row["validationStatus"],
                    "validationLevel": row["validationLevel"],
                    "artifactBytes": row["artifactBytes"],
                    "runtimeStatus": "not_attempted",
                    "runtimeLevel": "not_attempted_for_this_fixture_target",
                    "runtimeSampleCount": 0,
                    "runtimeMaxAbsError": None,
                }
            )

    runtime_payload = p35.build_payload()
    runtime_overlay = {
        (row["target"]): row
        for row in runtime_payload["runtimeRows"]
    }
    for row in matrix_rows:
        if row["fixtureId"] == "clamp_guard_mix" and row["target"] in runtime_overlay:
            runtime_row = runtime_overlay[row["target"]]
            row["runtimeStatus"] = runtime_row["runtimeStatus"]
            row["runtimeLevel"] = runtime_row["runtimeLevel"]
            row["runtimeSampleCount"] = runtime_row["sampleCount"]
            row["runtimeMaxAbsError"] = runtime_row["maxAbsError"]

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p36-free-target-capability-matrix",
        "decision": "selected_free_target_capability_matrix_with_runtime_overlay",
        "fixtureRows": fixtures,
        "targetOrder": target_order,
        "matrixRows": matrix_rows,
        "runtimeOverlay": {
            "sourceArtifactId": runtime_payload["artifactId"],
            "sourceFixture": runtime_payload["sourceFixture"],
            "runtimeTargets": runtime_payload["summary"]["runtimeTargets"],
            "sampleCountPerTarget": runtime_payload["summary"]["sampleCountPerTarget"],
            "totalSampleExecutions": runtime_payload["summary"]["totalSampleExecutions"],
            "maxAbsError": runtime_payload["summary"]["maxAbsError"],
        },
        "summary": summarize(fixtures, matrix_rows, target_order, runtime_payload),
        "releaseGates": [
            {"id": "selected_fixture_matrix_all_13_free_targets_emit", "status": "pass"},
            {"id": "selected_fixture_matrix_all_13_free_targets_validate", "status": "pass"},
            {"id": "selected_runtime_overlay_executes", "status": "pass"},
            {"id": "all_free_targets_runtime_execution", "status": "blocked"},
            {"id": "all_free_targets_public_ready", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Add runtime execution checks for additional free targets where local toolchains are available.",
            "Add runtime execution for additional selected fixtures, starting with verified_add.",
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
    fixtures: list[dict[str, Any]],
    matrix_rows: list[dict[str, Any]],
    target_order: list[str],
    runtime_payload: dict[str, Any],
) -> dict[str, Any]:
    by_target = []
    for target in target_order:
        rows = [row for row in matrix_rows if row["target"] == target]
        runtime_rows = [row for row in rows if row["runtimeStatus"] == "pass"]
        by_target.append(
            {
                "target": target,
                "fixtureCount": len(rows),
                "emissionPassCount": sum(1 for row in rows if row["emissionStatus"] == "pass"),
                "validationPassCount": sum(1 for row in rows if row["validationStatus"] == "pass"),
                "runtimePassCount": len(runtime_rows),
                "validationLevels": sorted({row["validationLevel"] for row in rows}),
            }
        )
    runtime_checked_rows = [row for row in matrix_rows if row["runtimeStatus"] == "pass"]
    return {
        "fixtureCount": len(fixtures),
        "freeTargetCount": len(target_order),
        "matrixCellCount": len(matrix_rows),
        "emissionPassCount": sum(1 for row in matrix_rows if row["emissionStatus"] == "pass"),
        "validationPassCount": sum(1 for row in matrix_rows if row["validationStatus"] == "pass"),
        "allMatrixEmissionPass": all(row["emissionStatus"] == "pass" for row in matrix_rows),
        "allMatrixValidationPass": all(row["validationStatus"] == "pass" for row in matrix_rows),
        "validationFailedCells": [
            {"fixtureId": row["fixtureId"], "target": row["target"]}
            for row in matrix_rows
            if row["validationStatus"] != "pass"
        ],
        "runtimeOverlayFixture": runtime_payload["sourceFixture"],
        "runtimeOverlayCellCount": len(runtime_checked_rows),
        "runtimeOverlayPassCount": sum(1 for row in runtime_checked_rows if row["runtimeStatus"] == "pass"),
        "runtimeOverlayTargets": [row["target"] for row in runtime_checked_rows],
        "runtimeOverlaySampleCount": sum(row["runtimeSampleCount"] for row in runtime_checked_rows),
        "runtimeOverlayMaxAbsError": max(row["runtimeMaxAbsError"] for row in runtime_checked_rows),
        "allRuntimeOverlayCellsPass": all(row["runtimeStatus"] == "pass" for row in runtime_checked_rows),
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
        "byTarget": by_target,
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P36 Free Target Capability Matrix",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_fixture_matrix_with_selected_runtime_overlay",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected fixture capability matrix only; it consolidates three fixture emission/validation guards and one selected runtime overlay for generated clamp_guard_mix targets, and makes no all-free-target runtime execution, public readiness, compiler correctness, formal equivalence, publication, runtime performance, hardware, Pro-target, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "The matrix covers verified_add, runtime_helper_mix, and clamp_guard_mix across all 13 free targets.",
            "All 39 fixture-target cells emit and validate at the selected level.",
            "The runtime overlay covers six clamp_guard_mix generated targets: C, C++, Rust, Python, JavaScript, and Java.",
            "The matrix consolidates selected evidence and does not publish or widen public preview claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p36_free_target_capability_matrix.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p36_free_target_capability_matrix.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p36_free_target_capability_matrix.v0",
        "date": DATE,
        "title": "FEF-P36 Free Target Capability Matrix",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add runtime execution checks for additional installed free-target toolchains or additional selected fixtures.",
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
            "# FEF-P36 Free Target Capability Matrix",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "## Fixtures",
            "",
            *[
                f"- `{fixture['id']}`: `{fixture['sourceFixture']}` ({fixture['kind']})"
                for fixture in payload["fixtureRows"]
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
            f"- Runtime overlay cells: `{summary['runtimeOverlayCellCount']}`",
            f"- Runtime overlay sample executions: `{summary['runtimeOverlaySampleCount']}`",
            f"- Runtime overlay max absolute error: `{summary['runtimeOverlayMaxAbsError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Selected fixture capability matrix only.",
            "- Runtime overlay covers selected clamp_guard_mix software targets only.",
            "- This guard does not execute all 13 free targets.",
            "- No arbitrary branch/control-flow support claim.",
            "- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.",
            "- No runtime performance, package publication, checkout, hardware, Pro-target, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P36 schema")
    summary = payload["summary"]
    if summary["fixtureCount"] != 3:
        raise ValueError("expected three selected fixtures")
    if summary["freeTargetCount"] != 13:
        raise ValueError("expected 13 free targets")
    if summary["matrixCellCount"] != 39:
        raise ValueError("expected a 3 x 13 fixture matrix")
    if summary["emissionPassCount"] != 39:
        raise ValueError("all matrix cells must emit")
    if summary["validationPassCount"] != 39:
        raise ValueError("all matrix cells must validate at the selected level")
    if summary["validationFailedCells"]:
        raise ValueError("validation failures must remain empty")
    if summary["runtimeOverlayCellCount"] != 6:
        raise ValueError("expected six runtime overlay cells")
    if summary["runtimeOverlayPassCount"] != 6:
        raise ValueError("all runtime overlay cells must pass")
    if summary["runtimeOverlayTargets"] != ["c", "cpp", "rust", "python", "java", "javascript"]:
        raise ValueError("unexpected runtime overlay target order")
    if summary["runtimeOverlaySampleCount"] != 42:
        raise ValueError("unexpected runtime overlay sample count")
    if summary["runtimeOverlayMaxAbsError"] > p35.ATOL:
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
    result_path = out_dir / f"fef_p36_free_target_capability_matrix_{STAMP}.json"
    report_path = report_dir / f"fef_p36_free_target_capability_matrix_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p36_free_target_capability_matrix.json"
    feed_path = command_feed_dir / f"fef_p36_free_target_capability_matrix_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p36_free_target_capability_matrix")
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
    print("FEF_P36_FREE_TARGET_CAPABILITY_MATRIX_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"free_targets={built['payload']['summary']['freeTargetCount']}")
    print(f"matrix_cells={built['payload']['summary']['matrixCellCount']}")
    print(f"runtime_overlay_cells={built['payload']['summary']['runtimeOverlayCellCount']}")
    print(f"runtime_samples={built['payload']['summary']['runtimeOverlaySampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
