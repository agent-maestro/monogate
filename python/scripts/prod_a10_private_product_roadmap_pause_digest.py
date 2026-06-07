#!/usr/bin/env python3
"""PROD-A10 private product roadmap pause digest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import prod_a9_private_product_roadmap_post_pinn_selector as prod_a9  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_product_roadmap_pause_digest.v0"
STATUS = "PROD_A10_PRIVATE_PRODUCT_ROADMAP_PAUSE_DIGEST_PASS"
NEXT_RECOMMENDED_ARTIFACT = "pause product roadmap lane unless explicit bounded request arrives"

TRUE_CLAIM_FLAGS = {
    "prod_a9_consumed",
    "product_roadmap_pause_digest_created",
    "lane_states_summarized",
    "reopen_conditions_recorded",
    "blocked_claims_recorded",
    "product_roadmap_lane_paused",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a9_consumed": True,
    "product_roadmap_pause_digest_created": True,
    "lane_states_summarized": True,
    "reopen_conditions_recorded": True,
    "blocked_claims_recorded": True,
    "product_roadmap_lane_paused": True,
    "d109_hold_respected": True,
    "product_implementation_started": False,
    "sdk_implementation_changed": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "training_cost_estimator_implemented": False,
    "training_cost_estimator_executed": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "pinn_advisor_implemented": False,
    "pinn_advisor_executed": False,
    "pinn_training_executed": False,
    "scientific_correctness_claim": False,
    "training_improvement_claim": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "automatic_lowering_safety_claim": False,
    "runtime_performance_claim": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_docs_created": False,
    "public_package_release_claim": False,
    "ip_license_terms_finalized": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "accelerator_card_ready": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PROD-A10 is a private pause digest; it does not implement or execute any product.",
    "PROD-A10 does not approve public docs, package release, SDK stability, compiler correctness, estimator accuracy, training savings, scientific correctness, hardware readiness, silicon readiness, or broad EML advantage.",
    "PROD-A10 does not reopen SDK, compiler-plugin, training-cost, PINN, IP-license, accelerator-card, public-copy, or hardware work.",
    "PROD-A10 does not touch laptop-owned electronics repositories, start D110, or consume reviewer response.",
]

BLOCKED_CLAIMS = [
    "public product readiness",
    "SDK stability",
    "public package release readiness",
    "training cost savings",
    "estimator accuracy",
    "scientific correctness",
    "training improvement",
    "compiler correctness",
    "semantic preservation",
    "automatic lowering safety",
    "runtime performance",
    "hardware readiness",
    "silicon readiness",
    "IP license readiness",
    "accelerator card readiness",
    "reviewer approval",
    "broad EML advantage",
]


def digest_rows(selector: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "laneId": state["laneId"],
            "state": state["state"],
            "evidence": state["evidence"],
            "reopenCondition": state["nextPolicy"],
        }
        for state in selector["laneStates"]
    ]


def reopen_conditions() -> list[dict[str, str]]:
    return [
        {
            "conditionId": "explicit_bounded_product_request",
            "status": "allowed_reopen_trigger",
            "description": "A specific bounded product request names one lane and preserves non-claims.",
        },
        {
            "conditionId": "actual_private_reviewer_response",
            "status": "allowed_reopen_trigger",
            "description": "A real reviewer response exists and points to a product or public-copy action.",
        },
        {
            "conditionId": "laptop_electronics_artifact",
            "status": "allowed_reopen_trigger",
            "description": "A concrete laptop/electronics artifact arrives for guarded intake.",
        },
        {
            "conditionId": "public_launch_impulse",
            "status": "blocked_reopen_trigger",
            "description": "General desire for public docs, packaging, or launch copy is not sufficient.",
        },
    ]


def build_payload() -> dict[str, Any]:
    selector = prod_a9.build_payload()
    prod_a9.validate_payload(selector)
    rows = digest_rows(selector)
    conditions = reopen_conditions()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "digestRowCount": len(rows),
        "pausedLaneCount": selector["summary"]["pausedLaneCount"],
        "seededParkedLaneCount": selector["summary"]["seededParkedLaneCount"],
        "blockedLaneCount": selector["summary"]["blockedLaneCount"],
        "blockedClaimCount": len(BLOCKED_CLAIMS),
        "reopenConditionCount": len(conditions),
        "productRoadmapLanePaused": True,
        "productImplementationStarted": False,
        "publicReadinessClaim": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="prod-a10-private-product-roadmap-pause-digest",
        artifact_type="private_product_roadmap_pause_digest",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "digestRows": rows,
            "reopenConditions": conditions,
            "blockedClaims": list(BLOCKED_CLAIMS),
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "prod-a9-private-product-roadmap-post-pinn-selector":
        raise ValueError("PROD-A10 must consume PROD-A9")
    summary = payload["summary"]
    if summary["digestRowCount"] != 6:
        raise ValueError("expected six digest rows")
    if summary["productRoadmapLanePaused"] is not True:
        raise ValueError("product roadmap lane must be paused")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    states = {row["laneId"]: row["state"] for row in payload["digestRows"]}
    if states != {
        "monogate_sdk": "paused_as_seeded",
        "eml_compiler_plugin": "paused_as_seeded",
        "training_cost_estimator": "seeded_and_parked",
        "pinn_advisor": "paused_as_seeded",
        "eml_ip_core_license": "blocked_until_hardware_evidence",
        "eml_accelerator_card": "blocked_until_laptop_hardware_evidence",
    }:
        raise ValueError("unexpected digest lane states")
    condition_statuses = {condition["conditionId"]: condition["status"] for condition in payload["reopenConditions"]}
    if condition_statuses["public_launch_impulse"] != "blocked_reopen_trigger":
        raise ValueError("public launch impulse must remain blocked")
    if set(payload["blockedClaims"]) != set(BLOCKED_CLAIMS):
        raise ValueError("blocked claims mismatch")
    for key in ["productImplementationStarted", "publicReadinessClaim"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
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
        semantic_strength="private_product_roadmap_pause_digest_no_implementation",
        source=f"python/results/prod_a10_private_product_roadmap_pause_digest/prod_a10_private_product_roadmap_pause_digest_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a10_private_product_roadmap_pause_digest_feed",
        date=DATE,
        status=payload["status"],
        next_action="Product roadmap lane paused; resume only on explicit bounded request, reviewer response, or laptop/electronics artifact.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "digestRowCount": payload["summary"]["digestRowCount"],
            "blockedClaimCount": payload["summary"]["blockedClaimCount"],
            "productRoadmapLanePaused": payload["summary"]["productRoadmapLanePaused"],
            "productImplementationStarted": payload["summary"]["productImplementationStarted"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A10 Private Product Roadmap Pause Digest",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("digest rows", payload["summary"]["digestRowCount"]),
            ("paused lanes", payload["summary"]["pausedLaneCount"]),
            ("seeded/parked lanes", payload["summary"]["seededParkedLaneCount"]),
            ("blocked lanes", payload["summary"]["blockedLaneCount"]),
            ("blocked claims", payload["summary"]["blockedClaimCount"]),
            ("product roadmap lane paused", payload["summary"]["productRoadmapLanePaused"]),
            ("product implementation started", payload["summary"]["productImplementationStarted"]),
            ("public readiness claim", payload["summary"]["publicReadinessClaim"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Digest Rows",
                [f"- `{row['laneId']}`: `{row['state']}` - {row['reopenCondition']}" for row in payload["digestRows"]],
            ),
            (
                "Reopen Conditions",
                [
                    f"- `{condition['conditionId']}`: `{condition['status']}` - {condition['description']}"
                    for condition in payload["reopenConditions"]
                ],
            ),
            ("Blocked Claims", [f"- {claim}" for claim in payload["blockedClaims"]]),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a10_private_product_roadmap_pause_digest_{STAMP}.json"
    report_path = report_dir / f"prod_a10_private_product_roadmap_pause_digest_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a10_private_product_roadmap_pause_digest.json"
    feed_path = command_feed_dir / f"prod_a10_private_product_roadmap_pause_digest_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a10_private_product_roadmap_pause_digest")
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
    print("PROD_A10_PRIVATE_PRODUCT_ROADMAP_PAUSE_DIGEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
