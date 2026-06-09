#!/usr/bin/env python3
"""EH-A8 private next-lane selector after command-feed aggregation."""

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

from scripts import eh_a7_private_command_feed_lane_state_aggregation as eh_a7  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-09"
STAMP = DATE.replace("-", "_")
SOURCE_STAMP = "2026_06_08"
SCHEMA_VERSION = "monogate.private_next_lane_selector.v0"
STATUS = "EH_A8_PRIVATE_NEXT_LANE_SELECTOR_PASS"
ARTIFACT_ID = "eh-a8-private-next-lane-selector"
SELECTED_NEXT_ARTIFACT = "EH-A9 private command-center readability queue contract"
SELECTED_PATH = "private_command_center_readability_queue_contract"

TRUE_CLAIM_FLAGS = {
    "eh_a7_consumed",
    "held_lane_states_reviewed",
    "blocked_lane_continuations_recorded",
    "private_next_lane_selected",
    "command_center_readability_contract_selected",
    "public_surface_blocked",
}

CLAIM_FLAGS = {
    "eh_a7_consumed": True,
    "held_lane_states_reviewed": True,
    "blocked_lane_continuations_recorded": True,
    "private_next_lane_selected": True,
    "command_center_readability_contract_selected": True,
    "public_surface_blocked": True,
    "dashboard_ui_created": False,
    "dashboard_implementation_started": False,
    "all_feeds_scanned": False,
    "health_report_completeness_claim": False,
    "renderer_correctness_claim": False,
    "visualization_quality_claim": False,
    "public_dashboard_created": False,
    "public_surface_updated": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "training_cost_estimator_reopened": False,
    "training_cost_estimator_implemented": False,
    "estimate_values_produced": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "product_implementation_started": False,
    "product_roadmap_reopened": False,
    "atlas_reviewer_response_consumed": False,
    "atlas_public_promotion": False,
    "atlas_catalog_completeness_claim": False,
    "public_math_promotion": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "laptop_artifact_consumed": False,
    "electronics_inbox_reopened": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "runtime_lowering_changed": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "EH-A8 selects a private next-lane direction from EH-A7; it does not implement that direction.",
    "EH-A8 does not create a dashboard, scan all feeds, check external sources, verify renderer correctness, or claim visualization quality or ecosystem completeness.",
    "EH-A8 does not reopen training-cost, Atlas, public math, product roadmap, or electronics lanes.",
    "EH-A8 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, consume reviewer response, record reviewer approval, start D110, edit MachLib, run Lean, change runtime lowering, or touch laptop-owned repositories.",
    "EH-A8 does not claim estimator accuracy, training savings, runtime performance, compiler correctness, hardware readiness, silicon readiness, public readiness, catalog completeness, or broad EML advantage.",
]


def load_eh_a7_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/eh_a7_private_command_feed_lane_state_aggregation"
        / f"eh_a7_private_command_feed_lane_state_aggregation_{SOURCE_STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    eh_a7.validate_payload(payload)
    return payload


def blocked_lane_continuations(eh_a7_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = {row["laneId"]: row for row in eh_a7_payload["laneStateRows"]}
    return [
        {
            "laneId": "training-cost-estimator",
            "blockedContinuation": "estimator implementation or estimate-producing work",
            "reason": rows["training-cost-estimator"]["laneStatus"],
            "requiredTrigger": "explicit bounded reviewer or user request plus a concrete usefulness review condition",
        },
        {
            "laneId": "private-atlas-v0",
            "blockedContinuation": "proof work, row expansion, SDK/course extraction, or public Atlas promotion",
            "reason": rows["private-atlas-v0"]["laneStatus"],
            "requiredTrigger": "actual reviewer response text or explicit user redirect",
        },
        {
            "laneId": "public-math-review",
            "blockedContinuation": "public witness promotion or D110 response intake",
            "reason": rows["public-math-review"]["laneStatus"],
            "requiredTrigger": "actual private reviewer response text",
        },
        {
            "laneId": "product-roadmap",
            "blockedContinuation": "roadmap implementation or public product/docs work",
            "reason": rows["product-roadmap"]["laneStatus"],
            "requiredTrigger": "explicit bounded product/tooling request",
        },
        {
            "laneId": "electronics-inbox",
            "blockedContinuation": "electronics artifact intake or reviewer conversion",
            "reason": rows["electronics-inbox"]["laneStatus"],
            "requiredTrigger": "real laptop-agent artifact at inbox path or explicit --artifact-path",
        },
    ]


def candidate_doors(eh_a7_payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "candidateId": "private_command_center_readability_queue_contract",
            "decision": "selected",
            "why": "It improves human review of existing evidence without reopening held lanes or creating public/product claims.",
            "nextArtifact": SELECTED_NEXT_ARTIFACT,
        },
        {
            "candidateId": "atlas_v0_reference_document_revision",
            "decision": "blocked_for_now",
            "why": "ATLAS-A51 holds the private Atlas lane until actual reviewer response or explicit redirect.",
            "nextArtifact": None,
        },
        {
            "candidateId": "public_math_witness_promotion",
            "decision": "blocked_for_now",
            "why": "D109 records no reviewer response and blocks D110/public promotion until response exists.",
            "nextArtifact": None,
        },
        {
            "candidateId": "training_cost_estimator_reopen",
            "decision": "blocked_for_now",
            "why": "PROD-A21 holds the estimator lane; no implementation or estimate values are authorized.",
            "nextArtifact": None,
        },
        {
            "candidateId": "electronics_artifact_intake",
            "decision": "blocked_for_now",
            "why": "EE-BRIDGE-A4/A6 record that a real laptop-agent artifact is still pending.",
            "nextArtifact": None,
        },
    ]


def build_payload() -> dict[str, Any]:
    eh_a7_payload = load_eh_a7_result()
    blocked = blocked_lane_continuations(eh_a7_payload)
    candidates = candidate_doors(eh_a7_payload)
    summary = {
        "sourceArtifact": eh_a7_payload["artifactId"],
        "sourceLaneStateRowCount": eh_a7_payload["summary"]["laneStateRowCount"],
        "sourceHeldOrPausedRowCount": eh_a7_payload["summary"]["heldOrPausedRowCount"],
        "blockedContinuationCount": len(blocked),
        "candidateDoorCount": len(candidates),
        "selectedPath": SELECTED_PATH,
        "selectedNextArtifact": SELECTED_NEXT_ARTIFACT,
        "digestVisibility": "private",
        "dashboardUiCreated": False,
        "publicSurfaceUpdated": False,
        "trainingCostEstimatorReopened": False,
        "productRoadmapReopened": False,
        "reviewerResponseConsumed": False,
        "reviewerApprovalRecorded": False,
        "d110Started": False,
        "laptopArtifactConsumed": False,
        "laptopOwnedRepoTouched": False,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_next_lane_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": eh_a7_payload["artifactId"],
            "blockedLaneContinuations": blocked,
            "candidateDoors": candidates,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "eh-a7-private-command-feed-lane-state-aggregation":
        raise ValueError("EH-A8 must consume EH-A7")
    summary = payload["summary"]
    if summary["sourceLaneStateRowCount"] != 7:
        raise ValueError("EH-A7 lane row count drift")
    if summary["sourceHeldOrPausedRowCount"] < 5:
        raise ValueError("EH-A7 held/paused count drift")
    if summary["blockedContinuationCount"] != 5:
        raise ValueError("blocked continuation count drift")
    if summary["selectedPath"] != SELECTED_PATH:
        raise ValueError("unexpected selected path")
    if summary["selectedNextArtifact"] != SELECTED_NEXT_ARTIFACT:
        raise ValueError("unexpected selected next artifact")
    for key in [
        "dashboardUiCreated",
        "publicSurfaceUpdated",
        "trainingCostEstimatorReopened",
        "productRoadmapReopened",
        "reviewerResponseConsumed",
        "reviewerApprovalRecorded",
        "d110Started",
        "laptopArtifactConsumed",
        "laptopOwnedRepoTouched",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    selected = [door for door in payload["candidateDoors"] if door["decision"] == "selected"]
    if len(selected) != 1 or selected[0]["candidateId"] != SELECTED_PATH:
        raise ValueError("exactly one expected candidate must be selected")
    blocked_lanes = {item["laneId"] for item in payload["blockedLaneContinuations"]}
    for lane in [
        "training-cost-estimator",
        "private-atlas-v0",
        "public-math-review",
        "product-roadmap",
        "electronics-inbox",
    ]:
        if lane not in blocked_lanes:
            raise ValueError(f"{lane} continuation must be blocked")
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
        semantic_strength="private_next_lane_selector_no_dashboard_or_lane_reopen_claim",
        source=f"python/results/eh_a8_private_next_lane_selector/eh_a8_private_next_lane_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a8_private_next_lane_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Build EH-A9 as a private command-center readability queue contract; do not reopen held lanes.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedPath": payload["summary"]["selectedPath"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "blockedContinuationCount": payload["summary"]["blockedContinuationCount"],
            "candidateDoorCount": payload["summary"]["candidateDoorCount"],
            "dashboardUiCreated": payload["summary"]["dashboardUiCreated"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "trainingCostEstimatorReopened": payload["summary"]["trainingCostEstimatorReopened"],
            "laptopOwnedRepoTouched": payload["summary"]["laptopOwnedRepoTouched"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EH-A8 Private Next-Lane Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("selected path", payload["summary"]["selectedPath"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("blocked continuations", payload["summary"]["blockedContinuationCount"]),
            ("candidate doors", payload["summary"]["candidateDoorCount"]),
            ("dashboard UI created", payload["summary"]["dashboardUiCreated"]),
            ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ],
        sections=[
            (
                "Candidate Doors",
                [
                    f"- `{door['candidateId']}`: `{door['decision']}`; {door['why']}"
                    for door in payload["candidateDoors"]
                ],
            ),
            (
                "Blocked Lane Continuations",
                [
                    f"- `{item['laneId']}`: {item['blockedContinuation']}; trigger: {item['requiredTrigger']}"
                    for item in payload["blockedLaneContinuations"]
                ],
            ),
            (
                "Guardrails",
                [
                    "- selector only; no EH-A9 implementation in this artifact",
                    "- no held-lane reopen",
                    "- no dashboard or public surface",
                    "- no laptop-owned repo touch",
                ],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eh_a8_private_next_lane_selector_{STAMP}.json"
    report_path = report_dir / f"eh_a8_private_next_lane_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a8_private_next_lane_selector.json"
    feed_path = command_feed_dir / f"eh_a8_private_next_lane_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eh_a8_private_next_lane_selector")
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
    print("EH_A8_PRIVATE_NEXT_LANE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
