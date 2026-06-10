#!/usr/bin/env python3
"""EH-A9 private command-center readability queue contract.

Container for command-center readability queue items. Defines the queue-item
record shape, enumerates the initial DEFINED-NOT-SELECTED items (PUB-R0, PUB-R1),
and records their dependencies and per-item entry/exit criteria. Implements no
queue item. Selects no queue item.
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

from scripts import eh_a8_private_next_lane_selector as eh_a8  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-10"
STAMP = DATE.replace("-", "_")
SOURCE_STAMP = "2026_06_09"
SCHEMA_VERSION = "monogate.private_command_center_readability_queue_contract.v0"
STATUS = "EH_A9_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_CONTRACT_PASS"
ARTIFACT_ID = "eh-a9-private-command-center-readability-queue-contract"
CONTAINER_ID = "EH-A9"

QUEUE_ITEM_RECORD_FIELDS = [
    "itemId",
    "title",
    "status",
    "container",
    "priority",
    "dependencies",
    "deliverable",
    "entryCriteria",
    "exitCriteria",
    "nonGoals",
    "notes",
]

DEFINED_NOT_SELECTED = "DEFINED_NOT_SELECTED"

TRUE_CLAIM_FLAGS = {
    "eh_a8_consumed",
    "queue_contract_defined",
    "queue_item_record_shape_defined",
    "queue_items_recorded",
    "pub_r0_recorded",
    "pub_r1_recorded",
    "pub_r1_depends_on_pub_r0_recorded",
    "broad_delegation_does_not_select",
    "public_surface_blocked",
}

CLAIM_FLAGS = {
    "eh_a8_consumed": True,
    "queue_contract_defined": True,
    "queue_item_record_shape_defined": True,
    "queue_items_recorded": True,
    "pub_r0_recorded": True,
    "pub_r1_recorded": True,
    "pub_r1_depends_on_pub_r0_recorded": True,
    "broad_delegation_does_not_select": True,
    "public_surface_blocked": True,
    "queue_item_selected": False,
    "queue_item_implementation_started": False,
    "pub_r0_built": False,
    "pub_r1_built": False,
    "ledger_generated": False,
    "drift_guard_implemented": False,
    "deploy_authorization_granted": False,
    "dashboard_ui_created": False,
    "dashboard_implementation_started": False,
    "renderer_correctness_claim": False,
    "visualization_quality_claim": False,
    "health_report_completeness_claim": False,
    "all_feeds_scanned": False,
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
    "EH-A9 is a queue contract; it defines the shape and enumerates items but does not implement, select, or expedite any queue item.",
    "EH-A9 does not build PUB-R0, build PUB-R1, generate the brake-side ledger, implement a drift guard, grant deploy authorization, or render any markdown/HTML form of the ledger.",
    "EH-A9 does not create a dashboard, scan all feeds, verify renderer correctness, claim visualization quality, or claim ecosystem completeness.",
    "EH-A9 does not reopen training-cost, Atlas, public-math, product-roadmap, or electronics lanes; broad delegation from the operator does not constitute selection of any enumerated item.",
    "EH-A9 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, consume reviewer response, record reviewer approval, start D110, edit MachLib, run Lean, change runtime lowering, or touch laptop-owned repositories.",
    "EH-A9 does not claim estimator accuracy, training savings, runtime performance, compiler correctness, hardware readiness, silicon readiness, public readiness, catalog completeness, or broad EML advantage.",
]


def load_eh_a8_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/eh_a8_private_next_lane_selector"
        / f"eh_a8_private_next_lane_selector_{SOURCE_STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    eh_a8.validate_payload(payload)
    return payload


def pub_r0_item() -> dict[str, Any]:
    return {
        "itemId": "PUB-R0",
        "title": "Canonical brake-side ledger generator (precursor)",
        "status": DEFINED_NOT_SELECTED,
        "container": CONTAINER_ID,
        "priority": "ordinary",
        "dependencies": [],
        "deliverable": (
            "One private bounded artifact whose canonical output is a single machine-generated JSON "
            "ledger enumerating held lanes, retracted claims, and negative results, derived from the "
            "graph / command-feed state. Any markdown or HTML form is a deterministic render of that "
            "JSON, never a parallel source."
        ),
        "entryCriteria": [
            "Container EH-A9 is shipped and accepted; PUB-R0 exists as a numbered queue item.",
            "A future EH-A* selector, run under normal procedure, selects PUB-R0. This contract does not pre-commit the selector.",
            "Input contract is named: which tool output(s) (e.g., builder_v2.py summary command) and which fields are consumed.",
        ],
        "exitCriteria": [
            "PUB-R0 emits a single canonical JSON ledger file enumerating held lanes, retracted claims, and negative results.",
            "Ledger contents are byte-derived from canonical state, never hand-written.",
            "Strict generator OK; focused PUB-R0 tests pass; compact regression passes; generated JSON parses cleanly; git diff --check passes.",
        ],
        "nonGoals": [
            "Does NOT publish, render to HTML, or update any public surface.",
            "Does NOT implement PUB-R1 or any other queue item.",
            "Does NOT reopen any held lane.",
            "Does NOT touch monogate-dev, monogate-electronics, /electronics, or any laptop-owned repository.",
        ],
        "notes": [
            "PUB-R0 has independent command-center value. The EH-A9 author may select PUB-R0 without selecting PUB-R1; this decouples the brakes from the public step entirely.",
            "Suggested input source: builder_v2.py summary plus the existing claim ledger files; exact contract is left to PUB-R0's own spec.",
        ],
    }


def pub_r1_item() -> dict[str, Any]:
    return {
        "itemId": "PUB-R1",
        "title": "Public-Surface Read Parity (r2)",
        "status": DEFINED_NOT_SELECTED,
        "container": CONTAINER_ID,
        "priority": "ordinary",
        "dependencies": ["PUB-R0"],
        "deliverable": (
            "One static, read-only public page (\"Evidence & Claims Status\" or similar), reachable "
            "from monogate.net, containing only: (1) Held lanes — name, holding artifact ID, one-line "
            "reason. (2) Retracted claims ledger — each retracted claim, retraction artifact ID, "
            "one-line reason. (3) Negative results — each booked negative result with its artifact ID. "
            "(4) Standing claim rule, quoted verbatim. (5) Lean status line — theorem count, core "
            "sorry count, discovered sorry count, as emitted by the graph tool. No adjectives. "
            "Explicit exclusions: no advantage percentages, no benchmarks, no roadmap, no performance "
            "language, no comparison to standard math, no prose beyond the one-liners above."
        ),
        "entryCriteria": [
            "E1 — Container shipped. EH-A9 queue contract is complete and accepted; PUB-R1 exists as a numbered item inside it.",
            "E2 — Canonical source exists. PUB-R0 is built; its canonical output is a single machine-generated JSON ledger derived from the graph / command-feed, not hand-written. Any markdown or HTML form is a deterministic render of that JSON, never a parallel source. The public page may render only this JSON. If the ledger cannot be generated from canonical state, PUB-R1 stays blocked.",
            "E3 — Drift guard defined, two stages. (a) Build-time: a check fails when the page to be published diverges from a fresh render of the current canonical JSON. (b) Post-deploy: a fetch-and-compare probe verifies the live page against the same render — the parity claim is about what a reader actually sees, not what was supposed to be published.",
            "E4 — Copy passes the standing rule. Every sentence on the page either (a) quotes the rule, (b) states a ledger fact with artifact ID, or (c) is navigation. For theorems and negative results, the displayed text is the one-line statement exactly as recorded in the canonical artifact — no paraphrase, no explanation, no \"why this matters\" or context sentence. Anything else fails review.",
            "E5 — Scoped deploy authorization. A human-authored authorization artifact exists unlocking the initial public deploy of this page and any subsequent redeploy whose page bytes are derived from current PUB-R0 output with no new content classes (the five classes in the deliverable are exhaustive). Adding a content class, changing page scope, or deploying anything else requires fresh authorization. The general no-public-deploy rail stays up.",
            "E6 — Selector naming. A future EH-A* selector, run under normal procedure, selects PUB-R1. This contract does not pre-commit the selector.",
        ],
        "exitCriteria": [
            "Page is live and statically readable without JavaScript.",
            "Page content is byte-derived from the PUB-R0 canonical JSON; build-time drift guard is green; post-deploy probe against the live page is green.",
            "Stale-reference check is green post-deploy.",
            "One commit, agent-letter style, recording the deploy authorization artifact ID alongside the page.",
        ],
        "nonGoals": [
            "Does NOT reopen any held lane (training-cost, Atlas, public-math, product-roadmap, electronics).",
            "Does NOT promote the public math draft.",
            "Does NOT add, modify, or imply any EML-advantage, estimator, savings, accuracy, runtime, silicon-readiness, or catalog-completeness claim.",
            "Does NOT touch monogate-dev, monogate-electronics, or /electronics.",
            "Does NOT introduce dynamic/JS-dependent content; the page must be fully readable to a no-JS reader.",
        ],
        "notes": [
            "Position PUB-R1 in the queue with ordinary priority. The external critique that motivated this item is the reason it exists, not a reason to expedite it.",
            "PUB-R0 is independently valuable; PUB-R1 depends on it. The EH-A9 author or future selector may queue PUB-R0 without queueing PUB-R1.",
            "The retracted-claims ledger is the highest-value display element. Resist any future pressure to trim it for appearance; its completeness is the argument.",
            "Known one-sidedness, accepted by design. PUB-R1 displays only the brake-side of the ledger (holds, retractions, negatives). A future sibling item (\"active claims with bounded-artifact pointers\") may be queued by ordinary procedure if a selector picks it; not expedited.",
        ],
    }


def build_queue_items() -> list[dict[str, Any]]:
    return [pub_r0_item(), pub_r1_item()]


def validate_queue_item_shape(item: dict[str, Any]) -> None:
    for field in QUEUE_ITEM_RECORD_FIELDS:
        if field not in item:
            raise ValueError(f"queue item missing field: {field}")
    if item["status"] != DEFINED_NOT_SELECTED:
        raise ValueError(f"queue item {item['itemId']} must be DEFINED_NOT_SELECTED")
    if item["container"] != CONTAINER_ID:
        raise ValueError(f"queue item {item['itemId']} container drift")
    if not isinstance(item["dependencies"], list):
        raise ValueError(f"queue item {item['itemId']} dependencies must be list")
    if not item["entryCriteria"] or not item["exitCriteria"]:
        raise ValueError(f"queue item {item['itemId']} must have entry and exit criteria")
    if not item["nonGoals"]:
        raise ValueError(f"queue item {item['itemId']} must have non-goals")


def build_payload() -> dict[str, Any]:
    eh_a8_payload = load_eh_a8_result()
    items = build_queue_items()
    for item in items:
        validate_queue_item_shape(item)
    summary = {
        "sourceArtifact": eh_a8_payload["artifactId"],
        "containerId": CONTAINER_ID,
        "queueItemRecordShapeDefined": True,
        "queueItemRecordFieldCount": len(QUEUE_ITEM_RECORD_FIELDS),
        "queueItemCount": len(items),
        "definedNotSelectedCount": sum(
            1 for item in items if item["status"] == DEFINED_NOT_SELECTED
        ),
        "selectedItemCount": sum(1 for item in items if item["status"] == "SELECTED"),
        "implementedItemCount": 0,
        "pubR0Recorded": any(item["itemId"] == "PUB-R0" for item in items),
        "pubR1Recorded": any(item["itemId"] == "PUB-R1" for item in items),
        "pubR1DependsOnPubR0": "PUB-R0"
        in next(item for item in items if item["itemId"] == "PUB-R1")["dependencies"],
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
        artifact_type="private_command_center_readability_queue_contract",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": eh_a8_payload["artifactId"],
            "queueItemRecordFields": list(QUEUE_ITEM_RECORD_FIELDS),
            "queueItems": items,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "eh-a8-private-next-lane-selector":
        raise ValueError("EH-A9 must consume EH-A8")
    summary = payload["summary"]
    if summary["containerId"] != CONTAINER_ID:
        raise ValueError("container id drift")
    if summary["queueItemRecordShapeDefined"] is not True:
        raise ValueError("queue item record shape must be defined")
    if summary["queueItemRecordFieldCount"] != len(QUEUE_ITEM_RECORD_FIELDS):
        raise ValueError("queue item record field count drift")
    if summary["queueItemCount"] < 2:
        raise ValueError("at least two queue items expected")
    if summary["definedNotSelectedCount"] != summary["queueItemCount"]:
        raise ValueError("every enumerated item must be DEFINED_NOT_SELECTED")
    if summary["selectedItemCount"] != 0:
        raise ValueError("no queue item may be SELECTED by this contract")
    if summary["implementedItemCount"] != 0:
        raise ValueError("no queue item may be implemented by this contract")
    if summary["pubR0Recorded"] is not True or summary["pubR1Recorded"] is not True:
        raise ValueError("both PUB-R0 and PUB-R1 must be recorded")
    if summary["pubR1DependsOnPubR0"] is not True:
        raise ValueError("PUB-R1 must depend on PUB-R0")
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
    items_by_id = {item["itemId"]: item for item in payload["queueItems"]}
    if {"PUB-R0", "PUB-R1"} - set(items_by_id):
        raise ValueError("PUB-R0 and PUB-R1 must both appear in queueItems")
    for item in payload["queueItems"]:
        validate_queue_item_shape(item)
    if "PUB-R0" not in items_by_id["PUB-R1"]["dependencies"]:
        raise ValueError("PUB-R1 must list PUB-R0 as a dependency")
    if items_by_id["PUB-R0"]["dependencies"]:
        raise ValueError("PUB-R0 must have no dependencies")
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
        semantic_strength="private_queue_contract_no_item_selection_or_implementation_claim",
        source=(
            f"python/results/eh_a9_private_command_center_readability_queue_contract/"
            f"eh_a9_private_command_center_readability_queue_contract_{STAMP}.json"
        ),
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a9_private_command_center_readability_queue_contract_feed",
        date=DATE,
        status=payload["status"],
        next_action=(
            "Use the queue contract to choose, under ordinary EH-A* selector procedure, "
            "at most one of PUB-R0 or PUB-R1 when a selector is next run; PUB-R0 may be "
            "selected without selecting PUB-R1."
        ),
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "containerId": payload["summary"]["containerId"],
            "queueItemCount": payload["summary"]["queueItemCount"],
            "definedNotSelectedCount": payload["summary"]["definedNotSelectedCount"],
            "selectedItemCount": payload["summary"]["selectedItemCount"],
            "implementedItemCount": payload["summary"]["implementedItemCount"],
            "pubR0Recorded": payload["summary"]["pubR0Recorded"],
            "pubR1Recorded": payload["summary"]["pubR1Recorded"],
            "pubR1DependsOnPubR0": payload["summary"]["pubR1DependsOnPubR0"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "laptopOwnedRepoTouched": payload["summary"]["laptopOwnedRepoTouched"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    items = payload["queueItems"]
    return render_markdown_report(
        title="EH-A9 Private Command-Center Readability Queue Contract",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("container id", payload["summary"]["containerId"]),
            ("queue items", payload["summary"]["queueItemCount"]),
            ("defined-not-selected", payload["summary"]["definedNotSelectedCount"]),
            ("selected by contract", payload["summary"]["selectedItemCount"]),
            ("implemented by contract", payload["summary"]["implementedItemCount"]),
            ("PUB-R0 recorded", payload["summary"]["pubR0Recorded"]),
            ("PUB-R1 recorded", payload["summary"]["pubR1Recorded"]),
            ("PUB-R1 depends on PUB-R0", payload["summary"]["pubR1DependsOnPubR0"]),
            ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ],
        sections=[
            (
                "Queue Item Record Shape",
                [f"- `{field}`" for field in payload["queueItemRecordFields"]],
            ),
            (
                "Queue Items",
                [
                    f"- `{item['itemId']}` ({item['status']}): {item['title']}; "
                    f"depends on: {item['dependencies'] or 'none'}; priority: {item['priority']}"
                    for item in items
                ],
            ),
            (
                "Guardrails",
                [
                    "- queue contract only; no queue item is selected or implemented by EH-A9",
                    "- broad delegation from the operator does not constitute selection",
                    "- no dashboard, public surface, or lane reopen",
                    "- no laptop-owned repo touch",
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
        / f"eh_a9_private_command_center_readability_queue_contract_{STAMP}.json"
    )
    report_path = (
        report_dir
        / f"eh_a9_private_command_center_readability_queue_contract_{STAMP}.md"
    )
    evidence_path = (
        evidence_dir / "eh_a9_private_command_center_readability_queue_contract.json"
    )
    feed_path = (
        command_feed_dir
        / f"eh_a9_private_command_center_readability_queue_contract_feed_{STAMP}.json"
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
        / "python/results/eh_a9_private_command_center_readability_queue_contract",
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
    print("EH_A9_PRIVATE_COMMAND_CENTER_READABILITY_QUEUE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
