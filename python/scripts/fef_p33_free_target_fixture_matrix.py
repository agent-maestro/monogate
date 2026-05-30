#!/usr/bin/env python3
"""FEF-P33 selected-fixture free-target support matrix."""

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

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p33_free_target_fixture_matrix.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P33_FREE_TARGET_FIXTURE_MATRIX_PASS"

FIXTURE_BUILDERS = [
    {
        "id": "verified_add",
        "kind": "arithmetic",
        "sourceFixture": "examples/verified_add.eml",
        "builder": p31.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p31_free_target_emission_guard.json",
    },
    {
        "id": "runtime_helper_mix",
        "kind": "runtime_helper",
        "sourceFixture": "generated/runtime_helper_mix.eml",
        "builder": p32.build_payload,
        "evidencePath": "reports/evidence_packets/fef_p32_free_target_runtime_helper_guard.json",
    },
]

CLAIM_FLAGS = {
    "free_target_fixture_matrix_claim": False,
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
    "FEF-P33 records a selected-fixture matrix over FEF-P31 and FEF-P32 evidence.",
    "FEF-P33 does not add target runtime checks beyond the underlying selected validation levels.",
    "FEF-P33 does not claim all free targets are public-ready.",
    "FEF-P33 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P33 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P33 does not claim runtime performance, Verilog, silicon, hardware, Pro-target, or all-target readiness.",
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
                }
            )

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p33-free-target-fixture-matrix",
        "decision": "selected_fixture_matrix_all_free_targets_emit_and_validate",
        "fixtureRows": fixtures,
        "targetOrder": target_order,
        "matrixRows": matrix_rows,
        "summary": summarize(fixtures, matrix_rows, target_order),
        "releaseGates": [
            {"id": "selected_fixture_matrix_all_13_free_targets_emit", "status": "pass"},
            {"id": "selected_fixture_matrix_all_13_free_targets_validate", "status": "pass"},
            {"id": "all_free_targets_public_ready", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Add runtime execution checks for more free targets where local toolchains are available.",
            "Add a third selected fixture covering branch/control-flow lowering before public preview claims widen.",
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
) -> dict[str, Any]:
    by_target = []
    for target in target_order:
        rows = [row for row in matrix_rows if row["target"] == target]
        by_target.append(
            {
                "target": target,
                "fixtureCount": len(rows),
                "emissionPassCount": sum(1 for row in rows if row["emissionStatus"] == "pass"),
                "validationPassCount": sum(1 for row in rows if row["validationStatus"] == "pass"),
                "validationLevels": sorted({row["validationLevel"] for row in rows}),
            }
        )
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
        "byTarget": by_target,
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
        "title": "FEF-P33 Free Target Fixture Matrix",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_fixture_matrix_guard_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected-fixture matrix over two Forge free-target guards only; it consolidates bounded local-toolchain or structural validation and makes no all-free-target public readiness, compiler correctness, formal equivalence, publication, runtime performance, hardware, Pro-target, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "The matrix covers two selected fixtures: verified_add and runtime_helper_mix.",
            "Each fixture emits and validates across all 13 Forge free targets at the selected level.",
            "The matrix consolidates existing selected evidence and does not add broad semantic or runtime claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p33_free_target_fixture_matrix.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p33_free_target_fixture_matrix.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p33_free_target_fixture_matrix.v0",
        "date": DATE,
        "title": "FEF-P33 Free Target Fixture Matrix",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add runtime execution checks for more installed free-target toolchains or add a third selected branch/control-flow fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Fixture | Target | Emission | Validation | Level | Bytes |",
        "|---|---|---:|---:|---|---:|",
    ]
    for row in payload["matrixRows"]:
        rows.append(
            f"| `{row['fixtureId']}` | `{row['target']}` | `{row['emissionStatus']}` | "
            f"`{row['validationStatus']}` | `{row['validationLevel']}` | `{row['artifactBytes']}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P33 Free Target Fixture Matrix",
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
            "",
            "## Boundary",
            "",
            "- Selected-fixture matrix guard only.",
            "- Structural checks are not runtime checks.",
            "- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.",
            "- No package publication, checkout, performance, hardware, Pro-target, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P33 schema")
    summary = payload["summary"]
    if summary["fixtureCount"] != 2:
        raise ValueError("expected two selected fixtures")
    if summary["freeTargetCount"] != 13:
        raise ValueError("expected 13 free targets")
    if summary["matrixCellCount"] != 26:
        raise ValueError("expected a 2 x 13 fixture matrix")
    if summary["emissionPassCount"] != 26:
        raise ValueError("all matrix cells must emit")
    if summary["validationPassCount"] != 26:
        raise ValueError("all matrix cells must validate at the selected level")
    if summary["allMatrixEmissionPass"] is not True:
        raise ValueError("all matrix emission must pass")
    if summary["allMatrixValidationPass"] is not True:
        raise ValueError("all matrix validation must pass")
    if summary["validationFailedCells"]:
        raise ValueError("validation failures must remain empty")
    for key in [
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
    result_path = out_dir / f"fef_p33_free_target_fixture_matrix_{STAMP}.json"
    report_path = report_dir / f"fef_p33_free_target_fixture_matrix_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p33_free_target_fixture_matrix.json"
    feed_path = command_feed_dir / f"fef_p33_free_target_fixture_matrix_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p33_free_target_fixture_matrix")
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
    print("FEF_P33_FREE_TARGET_FIXTURE_MATRIX_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"free_targets={built['payload']['summary']['freeTargetCount']}")
    print(f"matrix_cells={built['payload']['summary']['matrixCellCount']}")
    print(f"validation_passes={built['payload']['summary']['validationPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
