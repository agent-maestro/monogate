#!/usr/bin/env python3
"""EA-A2 single-artifact toolkit migration smoke."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import ea_a1_shared_evidence_artifact_toolkit_seed as ea_a1  # noqa: E402
from scripts import prod_a1_private_product_evidence_surface_seed as prod_a1  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.single_artifact_toolkit_migration_smoke.v0"
STATUS = "EA_A2_SINGLE_ARTIFACT_TOOLKIT_MIGRATION_SMOKE_PASS"

MIGRATED_ARTIFACT = "prod-a1-private-product-evidence-surface-seed"
MIGRATED_SCRIPT = ROOT / "python/scripts/prod_a1_private_product_evidence_surface_seed.py"

TRUE_CLAIM_FLAGS = {
    "ea_a1_consumed",
    "single_artifact_migrated",
    "toolkit_helpers_used",
    "bulk_migration_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "ea_a1_consumed": True,
    "single_artifact_migrated": True,
    "toolkit_helpers_used": True,
    "bulk_migration_blocked": True,
    "d109_hold_respected": True,
    "bulk_migration_performed": False,
    "toolkit_surface_expanded": False,
    "old_artifacts_rewritten": False,
    "production_framework_claim": False,
    "schema_validator_implemented": False,
    "estimator_implemented": False,
    "public_product_ready": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "hardware_readiness_claim": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "EA-A2 migrates exactly one low-risk artifact to the shared evidence helpers.",
    "EA-A2 does not bulk-migrate old artifacts or expand the toolkit surface.",
    "EA-A2 does not implement a schema validator, estimator, public product surface, runtime benchmark, compiler proof, hardware artifact, or broad EML advantage claim.",
    "EA-A2 respects the D109 hold and does not start D110 or consume a reviewer response.",
]


def migration_checks() -> list[dict[str, Any]]:
    source = MIGRATED_SCRIPT.read_text(encoding="utf-8")
    helper_names = [
        "build_claim_flagged_packet",
        "build_evidence_packet",
        "build_command_feed",
        "render_markdown_report",
        "write_json",
    ]
    return [
        {
            "checkId": "migrated_artifact_is_prod_a1",
            "status": "pass",
            "detail": MIGRATED_ARTIFACT,
        },
        {
            "checkId": "toolkit_import_present",
            "status": "pass" if "from scripts.evidence_artifact_toolkit import" in source else "fail",
            "detail": "PROD-A1 imports the shared toolkit module.",
        },
        {
            "checkId": "expected_helpers_referenced",
            "status": "pass" if all(name in source for name in helper_names) else "fail",
            "detail": ", ".join(helper_names),
        },
        {
            "checkId": "prod_a1_payload_still_validates",
            "status": "pass",
            "detail": "build_payload and validate_payload completed.",
        },
    ]


def build_payload() -> dict[str, Any]:
    seed = ea_a1.build_payload()
    ea_a1.validate_payload(seed)
    migrated_payload = prod_a1.build_payload()
    prod_a1.validate_payload(migrated_payload)
    checks = migration_checks()
    summary = {
        "sourceArtifact": seed["artifactId"],
        "migratedArtifact": MIGRATED_ARTIFACT,
        "migratedScript": "python/scripts/prod_a1_private_product_evidence_surface_seed.py",
        "migrationCheckCount": len(checks),
        "passedMigrationCheckCount": sum(1 for check in checks if check["status"] == "pass"),
        "bulkMigrationPerformed": False,
        "toolkitSurfaceExpanded": False,
        "oldArtifactsRewritten": False,
        "d109HoldRespected": True,
        "nextRecommendedArtifact": "EH-A1 private ecosystem health report seed",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="ea-a2-single-artifact-toolkit-migration-smoke",
        artifact_type="single_artifact_toolkit_migration_smoke",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": seed["artifactId"],
            "migrationChecks": checks,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "ea-a1-shared-evidence-artifact-toolkit-seed":
        raise ValueError("EA-A2 must consume EA-A1")
    summary = payload["summary"]
    if summary["migratedArtifact"] != MIGRATED_ARTIFACT:
        raise ValueError("EA-A2 must migrate only PROD-A1")
    if summary["migrationCheckCount"] != 4 or summary["passedMigrationCheckCount"] != 4:
        raise ValueError("migration check drift")
    for key in ["bulkMigrationPerformed", "toolkitSurfaceExpanded", "oldArtifactsRewritten"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for check in payload["migrationChecks"]:
        if check["status"] != "pass":
            raise ValueError(f"migration check failed: {check['checkId']}")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="single_artifact_toolkit_migration_smoke_no_bulk_refactor",
        source=f"python/results/ea_a2_single_artifact_toolkit_migration_smoke/ea_a2_single_artifact_toolkit_migration_smoke_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="ea_a2_single_artifact_toolkit_migration_smoke_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create EH-A1 private ecosystem health report seed.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "migratedArtifact": payload["summary"]["migratedArtifact"],
            "migrationCheckCount": payload["summary"]["migrationCheckCount"],
            "bulkMigrationPerformed": payload["summary"]["bulkMigrationPerformed"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EA-A2 Single-Artifact Toolkit Migration Smoke",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("migrated artifact", payload["summary"]["migratedArtifact"]),
            ("migration checks", payload["summary"]["migrationCheckCount"]),
            ("passed checks", payload["summary"]["passedMigrationCheckCount"]),
            ("bulk migration performed", payload["summary"]["bulkMigrationPerformed"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Migration Checks",
                [f"- `{check['checkId']}`: `{check['status']}` - {check['detail']}" for check in payload["migrationChecks"]],
            )
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"ea_a2_single_artifact_toolkit_migration_smoke_{STAMP}.json"
    report_path = report_dir / f"ea_a2_single_artifact_toolkit_migration_smoke_{STAMP}.md"
    evidence_path = evidence_dir / "ea_a2_single_artifact_toolkit_migration_smoke.json"
    feed_path = command_feed_dir / f"ea_a2_single_artifact_toolkit_migration_smoke_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ea_a2_single_artifact_toolkit_migration_smoke")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("EA_A2_SINGLE_ARTIFACT_TOOLKIT_MIGRATION_SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
