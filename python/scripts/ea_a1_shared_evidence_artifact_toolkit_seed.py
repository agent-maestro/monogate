#!/usr/bin/env python3
"""EA-A1 shared evidence artifact toolkit seed."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import prod_a6_training_cost_estimator_fixture_packet as prod_a6  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.shared_evidence_artifact_toolkit_seed.v0"
STATUS = "EA_A1_SHARED_EVIDENCE_ARTIFACT_TOOLKIT_SEED_PASS"

TRUE_CLAIM_FLAGS = {
    "prod_a6_consumed",
    "shared_toolkit_seed_created",
    "json_packet_helper_seeded",
    "markdown_report_helper_seeded",
    "command_feed_helper_seeded",
    "old_artifacts_not_rewritten",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a6_consumed": True,
    "shared_toolkit_seed_created": True,
    "json_packet_helper_seeded": True,
    "markdown_report_helper_seeded": True,
    "command_feed_helper_seeded": True,
    "old_artifacts_not_rewritten": True,
    "d109_hold_respected": True,
    "broad_framework_created": False,
    "old_artifacts_rewritten": False,
    "production_framework_claim": False,
    "schema_validator_implemented": False,
    "estimator_implemented": False,
    "public_product_ready": False,
    "training_savings_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "hardware_readiness_claim": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "EA-A1 seeds a small shared evidence artifact toolkit; it is not a broad framework.",
    "EA-A1 does not rewrite old artifacts or claim universal coverage of all artifact styles.",
    "EA-A1 does not implement a training-cost estimator, schema validator, public product surface, runtime benchmark, compiler proof, hardware artifact, or broad EML advantage claim.",
    "EA-A1 respects the D109 hold and does not start D110 or consume a reviewer response.",
]


def helper_contracts() -> list[dict[str, Any]]:
    return [
        {
            "helperId": "claim_flagged_json_packet_builder",
            "moduleFunction": "build_claim_flagged_packet",
            "scope": "construct and bound-check JSON payloads with claim flags and non-claims",
            "outOfScope": "artifact-specific semantic validation",
        },
        {
            "helperId": "markdown_report_builder",
            "moduleFunction": "render_markdown_report",
            "scope": "render a compact status/summary/non-claims markdown report",
            "outOfScope": "custom narrative or public copy generation",
        },
        {
            "helperId": "command_feed_builder",
            "moduleFunction": "build_command_feed",
            "scope": "construct a compact private command feed with next action and claim flags",
            "outOfScope": "dashboard rendering or feed aggregation",
        },
    ]


def sample_summary() -> dict[str, Any]:
    return {
        "sourceArtifact": "prod-a6-training-cost-estimator-fixture-packet",
        "helperCount": 3,
        "oldArtifactsRewritten": False,
        "broadFrameworkCreated": False,
        "d109HoldRespected": True,
        "nextRecommendedArtifact": "EA-A2 migrate one low-risk artifact to shared evidence toolkit helpers",
    }


def build_payload() -> dict[str, Any]:
    fixture_packet = prod_a6.build_payload()
    prod_a6.validate_payload(fixture_packet)
    summary = sample_summary()
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="ea-a1-shared-evidence-artifact-toolkit-seed",
        artifact_type="shared_evidence_artifact_toolkit_seed",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": fixture_packet["artifactId"],
            "helperContracts": helper_contracts(),
            "toolkitModule": "python/scripts/evidence_artifact_toolkit.py",
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a6-training-cost-estimator-fixture-packet":
        raise ValueError("EA-A1 must consume PROD-A6")
    if payload["summary"]["helperCount"] != 3:
        raise ValueError("helper count drift")
    if [item["helperId"] for item in payload["helperContracts"]] != [
        "claim_flagged_json_packet_builder",
        "markdown_report_builder",
        "command_feed_builder",
    ]:
        raise ValueError("helper contract drift")
    for key in [
        "oldArtifactsRewritten",
        "broadFrameworkCreated",
    ]:
        if payload["summary"][key] is not False:
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
        semantic_strength="private_shared_toolkit_seed_three_helpers_no_framework_claim",
        source=f"python/results/ea_a1_shared_evidence_artifact_toolkit_seed/ea_a1_shared_evidence_artifact_toolkit_seed_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="ea_a1_shared_evidence_artifact_toolkit_seed_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create EA-A2 by migrating one low-risk artifact to the shared helpers.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "helperCount": payload["summary"]["helperCount"],
            "oldArtifactsRewritten": payload["summary"]["oldArtifactsRewritten"],
            "broadFrameworkCreated": payload["summary"]["broadFrameworkCreated"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EA-A1 Shared Evidence Artifact Toolkit Seed",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("helper count", payload["summary"]["helperCount"]),
            ("old artifacts rewritten", payload["summary"]["oldArtifactsRewritten"]),
            ("broad framework created", payload["summary"]["broadFrameworkCreated"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Helper Contracts",
                [
                    f"- `{item['helperId']}` -> `{item['moduleFunction']}`: {item['scope']}"
                    for item in payload["helperContracts"]
                ],
            )
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"ea_a1_shared_evidence_artifact_toolkit_seed_{STAMP}.json"
    report_path = report_dir / f"ea_a1_shared_evidence_artifact_toolkit_seed_{STAMP}.md"
    evidence_path = evidence_dir / "ea_a1_shared_evidence_artifact_toolkit_seed.json"
    feed_path = command_feed_dir / f"ea_a1_shared_evidence_artifact_toolkit_seed_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ea_a1_shared_evidence_artifact_toolkit_seed")
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
    print("EA_A1_SHARED_EVIDENCE_ARTIFACT_TOOLKIT_SEED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
