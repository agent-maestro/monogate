#!/usr/bin/env python3
"""EH-A10 private command-center readability queue item selector.

Consumes EH-A9. Records the operator's attended broad-delegation as the
selection input. Selects PUB-R0 and PUB-R1 from the EH-A9 queue, records the
build ordering (PUB-R0 strictly before PUB-R1) and records that PUB-R1's
build remains gated on PUB-R0 ship. Implements neither item.
"""

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

from scripts import eh_a9_private_command_center_readability_queue_contract as eh_a9  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-10"
STAMP = DATE.replace("-", "_")
SOURCE_STAMP = "2026_06_10"
SCHEMA_VERSION = "monogate.private_command_center_readability_queue_item_selector.v0"
STATUS = "EH_A10_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_ITEM_SELECTOR_PASS"
ARTIFACT_ID = "eh-a10-private-command-center-readability-queue-item-selector"

SELECTION_INPUT = (
    "operator attended broad-delegation under CLAUDE.md broad-delegation rule recorded in "
    "monogate-research commit 8c5236c"
)

TRUE_CLAIM_FLAGS = {
    "eh_a9_consumed",
    "queue_items_reviewed",
    "selection_input_recorded",
    "pub_r0_selected",
    "pub_r1_selected",
    "pub_r1_build_gated_on_pub_r0_ship",
    "build_order_recorded",
    "public_surface_blocked",
}

CLAIM_FLAGS = {
    "eh_a9_consumed": True,
    "queue_items_reviewed": True,
    "selection_input_recorded": True,
    "pub_r0_selected": True,
    "pub_r1_selected": True,
    "pub_r1_build_gated_on_pub_r0_ship": True,
    "build_order_recorded": True,
    "public_surface_blocked": True,
    "queue_item_implementation_started": False,
    "pub_r0_built": False,
    "pub_r1_built": False,
    "ledger_generated": False,
    "drift_guard_implemented": False,
    "deploy_authorization_granted": False,
    "live_deploy_executed": False,
    "dashboard_ui_created": False,
    "all_feeds_scanned": False,
    "renderer_correctness_claim": False,
    "visualization_quality_claim": False,
    "health_report_completeness_claim": False,
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
    "EH-A10 selects queue items from EH-A9; it does not implement, build, generate, deploy, or authorize any deploy of the selected items.",
    "EH-A10's selection of PUB-R1 does not unblock PUB-R1's E2-E5; PUB-R1 build remains gated on PUB-R0 ship and on the human-authored deploy authorization artifact recorded as a separate later step.",
    "EH-A10 does not generate the brake-side ledger, implement a drift guard, render any HTML, or modify any public surface.",
    "EH-A10 does not reopen training-cost, Atlas, public-math, product-roadmap, or electronics lanes.",
    "EH-A10 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, consume reviewer response, record reviewer approval, start D110, edit MachLib, run Lean, change runtime lowering, or touch laptop-owned repositories.",
    "EH-A10 does not claim estimator accuracy, training savings, runtime performance, compiler correctness, hardware readiness, silicon readiness, public readiness, catalog completeness, or broad EML advantage.",
]


def load_eh_a9_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/eh_a9_private_command_center_readability_queue_contract"
        / f"eh_a9_private_command_center_readability_queue_contract_{SOURCE_STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    eh_a9.validate_payload(payload)
    return payload


def candidate_doors(eh_a9_payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = {item["itemId"]: item for item in eh_a9_payload["queueItems"]}
    doors = []
    doors.append(
        {
            "candidateId": "PUB-R0",
            "decision": "selected",
            "buildOrder": 1,
            "buildGate": "ready_to_build",
            "why": (
                "PUB-R0 is independently valuable as the canonical brake-side ledger source for the "
                "command center even if PUB-R1 is never built. It has no dependencies and may proceed."
            ),
            "deliverable": items["PUB-R0"]["deliverable"],
        }
    )
    doors.append(
        {
            "candidateId": "PUB-R1",
            "decision": "selected",
            "buildOrder": 2,
            "buildGate": "build_gated_on_pub_r0_ship_and_human_authored_deploy_authorization_artifact",
            "why": (
                "Operator attended broad-delegation explicitly named both items in scope. PUB-R1 "
                "is selected but its build cannot start until PUB-R0 ships and the E5 deploy "
                "authorization artifact is recorded."
            ),
            "deliverable": items["PUB-R1"]["deliverable"],
        }
    )
    return doors


def build_payload() -> dict[str, Any]:
    eh_a9_payload = load_eh_a9_result()
    doors = candidate_doors(eh_a9_payload)
    selected_ids = [door["candidateId"] for door in doors if door["decision"] == "selected"]
    summary = {
        "sourceArtifact": eh_a9_payload["artifactId"],
        "sourceContainerId": eh_a9_payload["summary"]["containerId"],
        "sourceQueueItemCount": eh_a9_payload["summary"]["queueItemCount"],
        "candidateDoorCount": len(doors),
        "selectedItemCount": len(selected_ids),
        "selectedItemIds": selected_ids,
        "buildOrderRecorded": True,
        "pubR0Selected": "PUB-R0" in selected_ids,
        "pubR1Selected": "PUB-R1" in selected_ids,
        "pubR1BuildGatedOnPubR0Ship": True,
        "selectionInput": SELECTION_INPUT,
        "digestVisibility": "private",
        "queueItemImplementationStarted": False,
        "pubR0Built": False,
        "pubR1Built": False,
        "deployAuthorizationGranted": False,
        "liveDeployExecuted": False,
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
        artifact_type="private_command_center_readability_queue_item_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": eh_a9_payload["artifactId"],
            "candidateDoors": doors,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "eh-a9-private-command-center-readability-queue-contract":
        raise ValueError("EH-A10 must consume EH-A9")
    summary = payload["summary"]
    if summary["sourceContainerId"] != "EH-A9":
        raise ValueError("source container id drift")
    if summary["sourceQueueItemCount"] < 2:
        raise ValueError("source queue item count drift")
    if summary["candidateDoorCount"] != 2:
        raise ValueError("expected exactly two candidate doors")
    if summary["selectedItemCount"] != 2:
        raise ValueError("expected two selected items per attended broad-delegation")
    if set(summary["selectedItemIds"]) != {"PUB-R0", "PUB-R1"}:
        raise ValueError("selected items must be PUB-R0 and PUB-R1")
    if summary["pubR0Selected"] is not True or summary["pubR1Selected"] is not True:
        raise ValueError("both PUB-R0 and PUB-R1 must be selected")
    if summary["pubR1BuildGatedOnPubR0Ship"] is not True:
        raise ValueError("PUB-R1 build gate on PUB-R0 ship must be recorded")
    if summary["selectionInput"] != SELECTION_INPUT:
        raise ValueError("selection input drift")
    for key in [
        "queueItemImplementationStarted",
        "pubR0Built",
        "pubR1Built",
        "deployAuthorizationGranted",
        "liveDeployExecuted",
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
    doors = {door["candidateId"]: door for door in payload["candidateDoors"]}
    if doors["PUB-R0"]["buildOrder"] != 1 or doors["PUB-R1"]["buildOrder"] != 2:
        raise ValueError("build order must be PUB-R0=1, PUB-R1=2")
    if doors["PUB-R0"]["buildGate"] != "ready_to_build":
        raise ValueError("PUB-R0 must be ready_to_build")
    if "build_gated_on_pub_r0_ship" not in doors["PUB-R1"]["buildGate"]:
        raise ValueError("PUB-R1 must remain gated on PUB-R0 ship")
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
        semantic_strength="private_queue_item_selection_no_implementation_or_deploy_authorization_claim",
        source=(
            f"python/results/eh_a10_private_command_center_readability_queue_item_selector/"
            f"eh_a10_private_command_center_readability_queue_item_selector_{STAMP}.json"
        ),
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a10_private_command_center_readability_queue_item_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action=(
            "Build PUB-R0 (the canonical brake-side ledger generator) first; on PUB-R0 ship, "
            "record the human-authored E5 deploy authorization artifact and build PUB-R1's page "
            "and drift guard locally; do not execute the live public deploy without explicit "
            "per-action confirmation."
        ),
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "sourceContainerId": payload["summary"]["sourceContainerId"],
            "candidateDoorCount": payload["summary"]["candidateDoorCount"],
            "selectedItemCount": payload["summary"]["selectedItemCount"],
            "selectedItemIds": payload["summary"]["selectedItemIds"],
            "pubR0Selected": payload["summary"]["pubR0Selected"],
            "pubR1Selected": payload["summary"]["pubR1Selected"],
            "pubR1BuildGatedOnPubR0Ship": payload["summary"]["pubR1BuildGatedOnPubR0Ship"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "deployAuthorizationGranted": payload["summary"]["deployAuthorizationGranted"],
            "liveDeployExecuted": payload["summary"]["liveDeployExecuted"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EH-A10 Private Command-Center Readability Queue Item Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("source container", payload["summary"]["sourceContainerId"]),
            ("candidate doors", payload["summary"]["candidateDoorCount"]),
            ("selected items", payload["summary"]["selectedItemCount"]),
            ("PUB-R0 selected", payload["summary"]["pubR0Selected"]),
            ("PUB-R1 selected", payload["summary"]["pubR1Selected"]),
            (
                "PUB-R1 build gated on PUB-R0 ship",
                payload["summary"]["pubR1BuildGatedOnPubR0Ship"],
            ),
            ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
            ("deploy authorization granted", payload["summary"]["deployAuthorizationGranted"]),
            ("live deploy executed", payload["summary"]["liveDeployExecuted"]),
        ],
        sections=[
            (
                "Selection Input",
                [f"- {payload['summary']['selectionInput']}"],
            ),
            (
                "Candidate Doors",
                [
                    f"- `{door['candidateId']}`: `{door['decision']}`; "
                    f"build order {door['buildOrder']}; gate: `{door['buildGate']}`; {door['why']}"
                    for door in payload["candidateDoors"]
                ],
            ),
            (
                "Guardrails",
                [
                    "- selector only; no queue item is built, generated, or deployed by EH-A10",
                    "- PUB-R1 build remains gated on PUB-R0 ship and on a separate E5 deploy authorization artifact",
                    "- no live public deploy is authorized by this selector",
                    "- no held-lane reopen; no laptop-owned repo touch",
                ],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(
    out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path
) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = (
        out_dir
        / f"eh_a10_private_command_center_readability_queue_item_selector_{STAMP}.json"
    )
    report_path = (
        report_dir
        / f"eh_a10_private_command_center_readability_queue_item_selector_{STAMP}.md"
    )
    evidence_path = (
        evidence_dir / "eh_a10_private_command_center_readability_queue_item_selector.json"
    )
    feed_path = (
        command_feed_dir
        / f"eh_a10_private_command_center_readability_queue_item_selector_feed_{STAMP}.json"
    )
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT
        / "python/results/eh_a10_private_command_center_readability_queue_item_selector",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument(
        "--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets"
    )
    parser.add_argument(
        "--command-feed-dir", type=Path, default=ROOT / "command_center_feeds"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("EH_A10_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_ITEM_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
