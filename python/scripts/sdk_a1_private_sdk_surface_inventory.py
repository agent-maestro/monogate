#!/usr/bin/env python3
"""SDK-A1 private SDK surface inventory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eh_a4_private_ecosystem_health_digest_export_or_pause_selector as eh_a4  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_sdk_surface_inventory.v0"
STATUS = "SDK_A1_PRIVATE_SDK_SURFACE_INVENTORY_PASS"

TRUE_CLAIM_FLAGS = {
    "eh_a4_consumed",
    "private_sdk_surface_inventory_created",
    "surface_rows_recorded",
    "blocked_sdk_claims_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "eh_a4_consumed": True,
    "private_sdk_surface_inventory_created": True,
    "surface_rows_recorded": True,
    "blocked_sdk_claims_recorded": True,
    "d109_hold_respected": True,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_package_release_claim": False,
    "api_compatibility_claim": False,
    "semantic_versioning_commitment": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "runtime_performance_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
    "dashboard_ui_created": False,
    "sdk_implementation_changed": False,
}

NON_CLAIMS = [
    "SDK-A1 is a private inventory of existing SDK/API surfaces; it does not change implementation.",
    "SDK-A1 does not claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A1 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A1 respects the D109 hold and does not start D110, consume reviewer response, or record reviewer approval.",
    "SDK-A1 does not touch laptop-owned electronics repositories.",
]


def surface_rows() -> list[dict[str, Any]]:
    return [
        {
            "surfaceId": "python_package_core",
            "displayName": "Python package: monogate",
            "surfaceType": "python_imports_and_cli",
            "currentPosture": "existing_public_package_claims_require_review",
            "paths": ["python/pyproject.toml", "python/monogate", "python/README.md"],
            "knownEntryPoints": [
                "monogate-optimize",
                "monogate-validate",
                "monogate-capability-card",
                "monogate-explore",
                "eml-explore",
            ],
            "allowedPrivateUse": "Inventory imports, CLI names, extras, and examples before any stability promise.",
            "blockedClaims": ["SDK stability", "API compatibility", "runtime performance", "public readiness"],
        },
        {
            "surfaceId": "rust_extension_core",
            "displayName": "Rust extension: monogate-core",
            "surfaceType": "native_extension",
            "currentPosture": "experimental_native_backend",
            "paths": ["monogate-core/pyproject.toml", "monogate-core/src", "monogate-core/README.md"],
            "knownEntryPoints": ["monogate_core.eval_eml_batch", "monogate_core.eval_best_batch", "monogate_core.benchmark_rust"],
            "allowedPrivateUse": "Track native extension boundary and wrapper relationship.",
            "blockedClaims": ["runtime performance", "wheel distribution readiness", "hardware readiness"],
        },
        {
            "surfaceId": "forge_preview_package",
            "displayName": "Forge preview package",
            "surfaceType": "local_preview_cli",
            "currentPosture": "private_preview_scaffold",
            "paths": ["packages/monogate-forge-preview/pyproject.toml", "packages/monogate-forge-preview/README.md"],
            "knownEntryPoints": ["monogate-forge-preview"],
            "allowedPrivateUse": "Use for bounded fixture preview and packet generation only.",
            "blockedClaims": ["compiler correctness", "semantic preservation", "public package release readiness"],
        },
        {
            "surfaceId": "schemas_and_evidence_packets",
            "displayName": "Schemas and evidence packet artifacts",
            "surfaceType": "json_contracts",
            "currentPosture": "private_review_contracts",
            "paths": ["schemas", "reports/evidence_packets", "command_center_feeds"],
            "knownEntryPoints": ["JSON schema files", "evidence packet JSON", "command feed JSON"],
            "allowedPrivateUse": "Use as claim-bounded evidence contracts and review inputs.",
            "blockedClaims": ["complete ecosystem audit", "public readiness", "automatic approval"],
        },
        {
            "surfaceId": "research_artifact_scripts",
            "displayName": "Research artifact generators",
            "surfaceType": "private_cli_scripts",
            "currentPosture": "private_generator_tooling",
            "paths": ["python/scripts", "python/tests"],
            "knownEntryPoints": ["python python/scripts/* --build --strict"],
            "allowedPrivateUse": "Generate bounded artifacts and focused tests.",
            "blockedClaims": ["public SDK", "framework completeness", "automatic correctness"],
        },
        {
            "surfaceId": "blocked_electronics_and_dev_repos",
            "displayName": "Laptop-owned electronics/dev repositories",
            "surfaceType": "blocked_boundary",
            "currentPosture": "not_sdk_surface_for_research_agent",
            "paths": ["monogate-electronics", "monogate-dev", "/electronics"],
            "knownEntryPoints": [],
            "allowedPrivateUse": "Read-only status checks only unless a later explicit handoff changes ownership.",
            "blockedClaims": ["electronics readiness", "hardware readiness", "laptop-owned repo touch"],
        },
    ]


def blocked_sdk_claims() -> list[dict[str, str]]:
    return [
        {"claim": "SDK stability", "reason": "Inventory has not reviewed or frozen import/API compatibility."},
        {"claim": "public readiness", "reason": "No public release gate or reviewer approval is recorded."},
        {"claim": "API compatibility", "reason": "No compatibility matrix or deprecation policy is recorded."},
        {"claim": "semantic versioning commitment", "reason": "No versioning policy is selected by SDK-A1."},
        {"claim": "compiler correctness", "reason": "Forge preview remains bounded and does not prove compilation."},
        {"claim": "runtime performance", "reason": "Inventory reads surfaces only; it runs no benchmarks."},
        {"claim": "hardware readiness", "reason": "Hardware/electronics evidence is outside this research-side artifact."},
        {"claim": "broad EML advantage", "reason": "SDK-A1 is an inventory, not an advantage proof."},
    ]


def build_payload() -> dict[str, Any]:
    eh_payload = eh_a4.build_payload()
    eh_a4.validate_payload(eh_payload)
    rows = surface_rows()
    blocks = blocked_sdk_claims()
    summary = {
        "sourceArtifact": eh_payload["artifactId"],
        "surfaceRowCount": len(rows),
        "blockedSdkClaimCount": len(blocks),
        "stableSurfaceCount": 0,
        "experimentalOrPrivateSurfaceCount": 5,
        "blockedBoundarySurfaceCount": 1,
        "sdkImplementationChanged": False,
        "dashboardUiCreated": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": "SDK-A2 private SDK import and CLI smoke contract",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a1-private-sdk-surface-inventory",
        artifact_type="private_sdk_surface_inventory",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": eh_payload["artifactId"],
            "surfaceRows": rows,
            "blockedSdkClaims": blocks,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "eh-a4-private-ecosystem-health-digest-export-or-pause-selector":
        raise ValueError("SDK-A1 must consume EH-A4")
    summary = payload["summary"]
    if summary["surfaceRowCount"] != 6:
        raise ValueError("surface row count drift")
    if summary["blockedSdkClaimCount"] != 8:
        raise ValueError("blocked SDK claim count drift")
    if summary["stableSurfaceCount"] != 0:
        raise ValueError("SDK-A1 must not mark stable surfaces")
    if summary["blockedBoundarySurfaceCount"] != 1:
        raise ValueError("blocked boundary count drift")
    for key in [
        "sdkImplementationChanged",
        "dashboardUiCreated",
        "publicReadinessClaim",
        "sdkStabilityClaim",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    surface_ids = {row["surfaceId"] for row in payload["surfaceRows"]}
    expected = {
        "python_package_core",
        "rust_extension_core",
        "forge_preview_package",
        "schemas_and_evidence_packets",
        "research_artifact_scripts",
        "blocked_electronics_and_dev_repos",
    }
    if surface_ids != expected:
        raise ValueError("surface ids drift")
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
        semantic_strength="private_sdk_surface_inventory_no_stability_or_public_claim",
        source=f"python/results/sdk_a1_private_sdk_surface_inventory/sdk_a1_private_sdk_surface_inventory_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a1_private_sdk_surface_inventory_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create SDK-A2 private SDK import and CLI smoke contract.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "surfaceRowCount": payload["summary"]["surfaceRowCount"],
            "blockedSdkClaimCount": payload["summary"]["blockedSdkClaimCount"],
            "sdkStabilityClaim": payload["summary"]["sdkStabilityClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
            "sdkImplementationChanged": payload["summary"]["sdkImplementationChanged"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A1 Private SDK Surface Inventory",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("surface rows", payload["summary"]["surfaceRowCount"]),
            ("blocked SDK claims", payload["summary"]["blockedSdkClaimCount"]),
            ("stable surfaces", payload["summary"]["stableSurfaceCount"]),
            ("SDK stability claim", payload["summary"]["sdkStabilityClaim"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Surface Rows",
                [
                    f"- `{row['surfaceId']}`: `{row['currentPosture']}`; paths: {', '.join(row['paths'])}"
                    for row in payload["surfaceRows"]
                ],
            ),
            (
                "Blocked SDK Claims",
                [f"- {item['claim']}: {item['reason']}" for item in payload["blockedSdkClaims"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"sdk_a1_private_sdk_surface_inventory_{STAMP}.json"
    report_path = report_dir / f"sdk_a1_private_sdk_surface_inventory_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a1_private_sdk_surface_inventory.json"
    feed_path = command_feed_dir / f"sdk_a1_private_sdk_surface_inventory_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a1_private_sdk_surface_inventory")
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
    print("SDK_A1_PRIVATE_SDK_SURFACE_INVENTORY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
