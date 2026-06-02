#!/usr/bin/env python3
"""GB-VIS-A2 private static topology export fixture packet."""

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

from scripts import gb_vis_a1_claim_topology_renderer_contract as a1  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.static_topology_export_fixture.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A2_STATIC_TOPOLOGY_EXPORT_FIXTURE_PASS"

GROUP_ORDER = [
    "source_boundary",
    "abstract_claim",
    "artifact_class",
    "validator_obligation",
    "dry_run_check",
    "failure_mode",
]

CLAIM_FLAGS = {
    "static_topology_export_fixture_recorded": True,
    "gb_vis_a1_contract_consumed": True,
    "node_views_exported": True,
    "edge_views_exported": True,
    "reviewer_filters_exported": True,
    "layout_metadata_exported": True,
    "renderer_guardrails_preserved": True,
    "renderer_implemented": False,
    "interactive_renderer_implemented": False,
    "visualization_started": False,
    "visualization_rendered": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "runtime_lowering_changed": False,
    "production_validator_implemented": False,
    "validator_soundness_proved": False,
    "soundness_proved": False,
    "full_galois_connection_claim": False,
    "abstract_interpretation_soundness_proved": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "proof_attempt_started": False,
    "candidate_proved": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "runtime_performance_claim": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "GB-VIS-A2 records a private static topology export fixture only; it does not implement or execute an interactive renderer.",
    "GB-VIS-A2 derives reviewer-inspectable node views, edge views, filters, and layout metadata from GB-VIS-A1 without proving soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A2 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def node_group(node: dict[str, Any]) -> str:
    kind = node["nodeKind"]
    if kind not in GROUP_ORDER:
        raise ValueError(f"unknown node kind: {kind}")
    return kind


def build_node_views(contract: dict[str, Any]) -> list[dict[str, Any]]:
    counters = {group: 0 for group in GROUP_ORDER}
    views = []
    for node in contract["topologyNodes"]:
        group = node_group(node)
        slot = counters[group]
        counters[group] += 1
        views.append(
            {
                "viewId": f"node_view:{node['nodeId']}",
                "nodeId": node["nodeId"],
                "label": node["label"],
                "nodeKind": node["nodeKind"],
                "group": group,
                "slot": slot,
                "layout": {
                    "x": GROUP_ORDER.index(group) * 240,
                    "y": slot * 72,
                    "column": GROUP_ORDER.index(group),
                    "row": slot,
                },
                "styleRefs": style_refs_for_node(node),
                "boundaryBadges": boundary_badges_for_node(node),
            }
        )
    return views


def style_refs_for_node(node: dict[str, Any]) -> list[str]:
    refs = [f"node_kind:{node['nodeKind']}"]
    if node.get("publicStatus") == "held_private":
        refs.append("public_status:held_private")
    if node.get("runtimeControl") in {"protected_expm1_remains_runtime_control", "no_runtime_change"}:
        refs.append("runtime_boundary:preserved")
    if node.get("severity") == "block":
        refs.append("failure_mode:block")
    if node.get("status") == "pass":
        refs.append("dry_run_status:pass")
    return refs


def boundary_badges_for_node(node: dict[str, Any]) -> list[str]:
    badges = []
    if node.get("publicStatus") == "held_private":
        badges.append("held_private")
    if node.get("runtimeControl") == "protected_expm1_remains_runtime_control":
        badges.append("protected_expm1_runtime_control")
    if node.get("runtimeControl") == "no_runtime_change":
        badges.append("no_runtime_change")
    if node.get("claimStrength") in {"blocking_guard", "validator_requirement_only", "dry_run_skeleton_check_only"}:
        badges.append(node["claimStrength"])
    return badges


def build_edge_views(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "viewId": f"edge_view:{edge['edgeId']}",
            "edgeId": edge["edgeId"],
            "source": edge["source"],
            "target": edge["target"],
            "edgeKind": edge["edgeKind"],
            "operator": edge["operator"],
            "route": edge_route(edge),
            "styleRefs": [f"edge_kind:{edge['edgeKind']}", f"operator:{edge['operator']}"],
            "preserves": list(edge["preserves"]),
        }
        for edge in contract["topologyEdges"]
    ]


def edge_route(edge: dict[str, Any]) -> str:
    if edge["edgeKind"] == "blocks_claim_escalation":
        return "guard_backlink"
    if edge["operator"] == "alpha":
        return "left_to_right_alpha"
    if edge["operator"] == "gamma":
        return "left_to_right_gamma"
    if edge["operator"] == "alpha_gamma_roundtrip":
        return "roundtrip_check"
    return "left_to_right_validation"


def reviewer_filters(contract: dict[str, Any]) -> list[dict[str, Any]]:
    node_kinds = sorted({node["nodeKind"] for node in contract["topologyNodes"]})
    edge_kinds = sorted({edge["edgeKind"] for edge in contract["topologyEdges"]})
    return [
        {
            "filterId": "show_private_boundaries",
            "field": "publicStatus",
            "values": ["held_private", "inherits_source_boundary"],
            "default": True,
        },
        {
            "filterId": "show_runtime_boundaries",
            "field": "runtimeControl",
            "values": ["protected_expm1_remains_runtime_control", "no_runtime_change", "inherits_source_boundary"],
            "default": True,
        },
        {
            "filterId": "show_failure_blocks",
            "field": "nodeKind",
            "values": ["failure_mode"],
            "default": True,
        },
        {
            "filterId": "node_kind_filter",
            "field": "nodeKind",
            "values": node_kinds,
            "default": True,
        },
        {
            "filterId": "edge_kind_filter",
            "field": "edgeKind",
            "values": edge_kinds,
            "default": True,
        },
    ]


def layout_metadata(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "layoutId": "gb_vis_a2_static_columns_v0",
        "layoutType": "deterministic_columns",
        "groupOrder": list(GROUP_ORDER),
        "nodeCount": len(contract["topologyNodes"]),
        "edgeCount": len(contract["topologyEdges"]),
        "sourceStatement": contract["summary"]["sourceCheckedStatement"],
        "runtimeControl": contract["summary"]["sourceRuntimeControl"],
        "publicStatus": contract["summary"]["sourcePublicStatus"],
    }


def build_export(contract: dict[str, Any]) -> dict[str, Any]:
    node_views = build_node_views(contract)
    edge_views = build_edge_views(contract)
    filters = reviewer_filters(contract)
    return {
        "exportFormat": "monogate.claim_topology_static_export.v0",
        "sourceContract": contract["artifactId"],
        "layoutMetadata": layout_metadata(contract),
        "nodeViews": node_views,
        "edgeViews": edge_views,
        "reviewerFilters": filters,
        "rendererGuardrails": contract["rendererGuardrails"],
        "visualEncodings": contract["visualEncodings"],
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    contract = a1.build_payload(atlas_gate_path)
    a1.validate_payload(contract)
    export = build_export(contract)
    summary = {
        "sourceContract": contract["artifactId"],
        "sourceNodeCount": contract["summary"]["nodeCount"],
        "sourceEdgeCount": contract["summary"]["edgeCount"],
        "nodeViewCount": len(export["nodeViews"]),
        "edgeViewCount": len(export["edgeViews"]),
        "reviewerFilterCount": len(export["reviewerFilters"]),
        "layoutGroupCount": len(export["layoutMetadata"]["groupOrder"]),
        "rendererGuardrailCount": len(export["rendererGuardrails"]),
        "visualEncodingCount": len(export["visualEncodings"]),
        "sourceCheckedStatement": contract["summary"]["sourceCheckedStatement"],
        "sourceRuntimeControl": contract["summary"]["sourceRuntimeControl"],
        "sourcePublicStatus": contract["summary"]["sourcePublicStatus"],
        "staticTopologyExportFixtureRecorded": True,
        "gbVisA1ContractConsumed": True,
        "nodeViewsExported": True,
        "edgeViewsExported": True,
        "reviewerFiltersExported": True,
        "layoutMetadataExported": True,
        "rendererGuardrailsPreserved": True,
        "rendererImplemented": False,
        "interactiveRendererImplemented": False,
        "visualizationStarted": False,
        "visualizationRendered": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "runtimeLoweringChanged": False,
        "productionValidatorImplemented": False,
        "validatorSoundnessProved": False,
        "soundnessProved": False,
        "fullGaloisConnectionClaim": False,
        "abstractInterpretationSoundnessProved": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "proofAttemptStarted": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "GB-VIS-A3 implement a private renderer smoke fixture or ACT-A4 expand dry-run validator fixtures without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "static_topology_export_fixture_recorded",
                "gb_vis_a1_contract_consumed",
                "node_views_exported",
                "edge_views_exported",
                "reviewer_filters_exported",
                "layout_metadata_exported",
                "renderer_guardrails_preserved",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "static_topology_export_fixture_recorded",
                "gb_vis_a1_contract_consumed",
                "node_views_exported",
                "edge_views_exported",
                "reviewer_filters_exported",
                "layout_metadata_exported",
                "renderer_guardrails_preserved",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "static_topology_export_fixture_v0",
        "artifactId": "gb-vis-a2-static-topology-export-fixture",
        "status": STATUS,
        "decision": "record_private_static_topology_export_fixture_no_interactive_renderer",
        "date": DATE,
        "sourceContract": contract["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "staticTopologyExport": export,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    export = payload["staticTopologyExport"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceContract"] != "gb-vis-a1-claim-topology-renderer-contract":
        raise ValueError("GB-VIS-A2 must consume GB-VIS-A1")
    if export["exportFormat"] != "monogate.claim_topology_static_export.v0":
        raise ValueError("unexpected export format")
    if summary["sourceNodeCount"] != 23 or summary["nodeViewCount"] != 23:
        raise ValueError("node view count drift")
    if summary["sourceEdgeCount"] != 16 or summary["edgeViewCount"] != 16:
        raise ValueError("edge view count drift")
    if summary["reviewerFilterCount"] != 5:
        raise ValueError("reviewer filter count drift")
    if summary["layoutGroupCount"] != 6:
        raise ValueError("layout group count drift")
    if summary["rendererGuardrailCount"] != 4:
        raise ValueError("renderer guardrail count drift")
    if summary["visualEncodingCount"] != 5:
        raise ValueError("visual encoding count drift")
    if summary["sourceCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("source statement drift")
    if summary["sourceRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime control drift")
    if summary["sourcePublicStatus"] != "held_private":
        raise ValueError("public status drift")
    if export["layoutMetadata"]["groupOrder"] != GROUP_ORDER:
        raise ValueError("layout group order drift")
    for key in [
        "staticTopologyExportFixtureRecorded",
        "gbVisA1ContractConsumed",
        "nodeViewsExported",
        "edgeViewsExported",
        "reviewerFiltersExported",
        "layoutMetadataExported",
        "rendererGuardrailsPreserved",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "rendererImplemented",
        "interactiveRendererImplemented",
        "visualizationStarted",
        "visualizationRendered",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "runtimeLoweringChanged",
        "productionValidatorImplemented",
        "validatorSoundnessProved",
        "soundnessProved",
        "fullGaloisConnectionClaim",
        "abstractInterpretationSoundnessProved",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "proofAttemptStarted",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    true_keys = {
        "static_topology_export_fixture_recorded",
        "gb_vis_a1_contract_consumed",
        "node_views_exported",
        "edge_views_exported",
        "reviewer_filters_exported",
        "layout_metadata_exported",
        "renderer_guardrails_preserved",
    }
    for key in true_keys:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in true_keys and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "static_topology_export_fixture",
        "validationStatus": "pass",
        "semanticStrength": "private_static_topology_export_fixture_no_interactive_renderer_no_public_update",
        "source": f"python/results/gb_vis_a2_static_topology_export_fixture/gb_vis_a2_static_topology_export_fixture_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a2_static_topology_export_fixture_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# GB-VIS-A2 Static Topology Export Fixture",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A2 records a private static topology export fixture without implementing or executing an interactive renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| node views | `{payload['summary']['nodeViewCount']}` |",
        f"| edge views | `{payload['summary']['edgeViewCount']}` |",
        f"| reviewer filters | `{payload['summary']['reviewerFilterCount']}` |",
        f"| layout groups | `{payload['summary']['layoutGroupCount']}` |",
        "",
        "## Non-Claims",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"gb_vis_a2_static_topology_export_fixture_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a2_static_topology_export_fixture_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a2_static_topology_export_fixture.json"
    feed_path = command_feed_dir / f"gb_vis_a2_static_topology_export_fixture_feed_{STAMP}.json"
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
    parser.add_argument("--atlas-gate-path", type=Path, default=ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a2_static_topology_export_fixture")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.atlas_gate_path)
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.atlas_gate_path)
    print("GB_VIS_A2_STATIC_TOPOLOGY_EXPORT_FIXTURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
