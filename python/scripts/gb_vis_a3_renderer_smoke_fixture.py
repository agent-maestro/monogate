#!/usr/bin/env python3
"""GB-VIS-A3 private renderer smoke fixture packet."""

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

from scripts import gb_vis_a2_static_topology_export_fixture as a2  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.renderer_smoke_fixture.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A3_RENDERER_SMOKE_FIXTURE_PASS"

VIEWPORT = {"width": 1440, "height": 720}
NODE_SIZE = {"width": 184, "height": 44}

CLAIM_FLAGS = {
    "renderer_smoke_fixture_recorded": True,
    "gb_vis_a2_export_consumed": True,
    "node_draw_commands_recorded": True,
    "edge_draw_commands_recorded": True,
    "smoke_checks_recorded": True,
    "smoke_checks_passed": True,
    "renderer_implemented": False,
    "interactive_renderer_implemented": False,
    "renderer_executed": False,
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
    "GB-VIS-A3 records a private renderer smoke fixture only; it does not implement or execute an interactive renderer.",
    "GB-VIS-A3 derives deterministic draw commands and smoke checks from GB-VIS-A2 without proving visualization correctness, soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A3 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def node_draw_commands(export: dict[str, Any]) -> list[dict[str, Any]]:
    commands = []
    for view in export["nodeViews"]:
        layout = view["layout"]
        commands.append(
            {
                "commandId": f"draw_node:{view['nodeId']}",
                "commandType": "node_box",
                "nodeId": view["nodeId"],
                "label": view["label"],
                "group": view["group"],
                "bounds": {
                    "x": layout["x"],
                    "y": layout["y"],
                    "width": NODE_SIZE["width"],
                    "height": NODE_SIZE["height"],
                },
                "styleRefs": list(view["styleRefs"]),
                "boundaryBadges": list(view["boundaryBadges"]),
            }
        )
    return commands


def edge_draw_commands(export: dict[str, Any]) -> list[dict[str, Any]]:
    node_lookup = {view["nodeId"]: view for view in export["nodeViews"]}
    commands = []
    for view in export["edgeViews"]:
        source = node_lookup[view["source"]]["layout"]
        target = node_lookup[view["target"]]["layout"]
        commands.append(
            {
                "commandId": f"draw_edge:{view['edgeId']}",
                "commandType": "edge_path",
                "edgeId": view["edgeId"],
                "route": view["route"],
                "source": view["source"],
                "target": view["target"],
                "points": [
                    {"x": source["x"] + NODE_SIZE["width"], "y": source["y"] + NODE_SIZE["height"] // 2},
                    {"x": target["x"], "y": target["y"] + NODE_SIZE["height"] // 2},
                ],
                "styleRefs": list(view["styleRefs"]),
                "preserves": list(view["preserves"]),
            }
        )
    return commands


def legend_draw_commands(export: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "commandId": f"draw_legend:{encoding['encodingId']}",
            "commandType": "legend_row",
            "encodingId": encoding["encodingId"],
            "field": encoding["field"],
            "label": encoding["contract"],
        }
        for encoding in export["visualEncodings"]
    ]


def smoke_checks(export: dict[str, Any], nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    max_x = max(command["bounds"]["x"] + command["bounds"]["width"] for command in nodes)
    max_y = max(command["bounds"]["y"] + command["bounds"]["height"] for command in nodes)
    private_badges = sum("held_private" in command["boundaryBadges"] for command in nodes)
    runtime_badges = sum("protected_expm1_runtime_control" in command["boundaryBadges"] for command in nodes)
    guard_edges = sum(command["route"] == "guard_backlink" for command in edges)
    checks = [
        {
            "checkId": "node_draw_command_count_matches_export",
            "status": "pass",
            "observed": len(nodes),
            "expected": len(export["nodeViews"]),
        },
        {
            "checkId": "edge_draw_command_count_matches_export",
            "status": "pass",
            "observed": len(edges),
            "expected": len(export["edgeViews"]),
        },
        {
            "checkId": "node_bounds_fit_private_viewport",
            "status": "pass",
            "observed": {"maxX": max_x, "maxY": max_y},
            "expected": VIEWPORT,
        },
        {
            "checkId": "private_boundary_badges_present",
            "status": "pass",
            "observed": private_badges,
            "expectedMinimum": 1,
        },
        {
            "checkId": "runtime_boundary_badges_present",
            "status": "pass",
            "observed": runtime_badges,
            "expectedMinimum": 1,
        },
        {
            "checkId": "failure_mode_guard_routes_present",
            "status": "pass",
            "observed": guard_edges,
            "expectedMinimum": 5,
        },
    ]
    if max_x > VIEWPORT["width"] or max_y > VIEWPORT["height"]:
        raise ValueError("node bounds exceed private viewport")
    if private_badges < 1:
        raise ValueError("missing private boundary badge")
    if runtime_badges < 1:
        raise ValueError("missing runtime boundary badge")
    if guard_edges < 5:
        raise ValueError("missing failure mode guard routes")
    return checks


def build_smoke_fixture(export: dict[str, Any]) -> dict[str, Any]:
    nodes = node_draw_commands(export)
    edges = edge_draw_commands(export)
    legends = legend_draw_commands(export)
    checks = smoke_checks(export, nodes, edges)
    return {
        "fixtureFormat": "monogate.claim_topology_renderer_smoke_fixture.v0",
        "sourceExport": export["sourceContract"],
        "viewport": dict(VIEWPORT),
        "nodeSize": dict(NODE_SIZE),
        "nodeDrawCommands": nodes,
        "edgeDrawCommands": edges,
        "legendDrawCommands": legends,
        "smokeChecks": checks,
        "rendererGuardrails": export["rendererGuardrails"],
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a2.build_payload(atlas_gate_path)
    a2.validate_payload(source)
    export = source["staticTopologyExport"]
    fixture = build_smoke_fixture(export)
    summary = {
        "sourceExportPacket": source["artifactId"],
        "sourceContract": source["sourceContract"],
        "nodeDrawCommandCount": len(fixture["nodeDrawCommands"]),
        "edgeDrawCommandCount": len(fixture["edgeDrawCommands"]),
        "legendDrawCommandCount": len(fixture["legendDrawCommands"]),
        "smokeCheckCount": len(fixture["smokeChecks"]),
        "smokeCheckPassCount": sum(1 for check in fixture["smokeChecks"] if check["status"] == "pass"),
        "rendererGuardrailCount": len(fixture["rendererGuardrails"]),
        "sourceCheckedStatement": source["summary"]["sourceCheckedStatement"],
        "sourceRuntimeControl": source["summary"]["sourceRuntimeControl"],
        "sourcePublicStatus": source["summary"]["sourcePublicStatus"],
        "rendererSmokeFixtureRecorded": True,
        "gbVisA2ExportConsumed": True,
        "nodeDrawCommandsRecorded": True,
        "edgeDrawCommandsRecorded": True,
        "smokeChecksRecorded": True,
        "smokeChecksPassed": True,
        "rendererImplemented": False,
        "interactiveRendererImplemented": False,
        "rendererExecuted": False,
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
        "nextAction": "GB-VIS-A4 add private snapshot comparison fixture or ACT-A4 expand dry-run validator fixtures without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "renderer_smoke_fixture_recorded",
                "gb_vis_a2_export_consumed",
                "node_draw_commands_recorded",
                "edge_draw_commands_recorded",
                "smoke_checks_recorded",
                "smoke_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "renderer_smoke_fixture_recorded",
                "gb_vis_a2_export_consumed",
                "node_draw_commands_recorded",
                "edge_draw_commands_recorded",
                "smoke_checks_recorded",
                "smoke_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "renderer_smoke_fixture_v0",
        "artifactId": "gb-vis-a3-renderer-smoke-fixture",
        "status": STATUS,
        "decision": "record_private_renderer_smoke_fixture_no_interactive_renderer_execution",
        "date": DATE,
        "sourceExportPacket": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "rendererSmokeFixture": fixture,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    fixture = payload["rendererSmokeFixture"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceExportPacket"] != "gb-vis-a2-static-topology-export-fixture":
        raise ValueError("GB-VIS-A3 must consume GB-VIS-A2")
    if fixture["fixtureFormat"] != "monogate.claim_topology_renderer_smoke_fixture.v0":
        raise ValueError("unexpected fixture format")
    if summary["nodeDrawCommandCount"] != 23:
        raise ValueError("unexpected node draw command count")
    if summary["edgeDrawCommandCount"] != 16:
        raise ValueError("unexpected edge draw command count")
    if summary["legendDrawCommandCount"] != 5:
        raise ValueError("unexpected legend command count")
    if summary["smokeCheckCount"] != 6 or summary["smokeCheckPassCount"] != 6:
        raise ValueError("unexpected smoke check count")
    if summary["rendererGuardrailCount"] != 4:
        raise ValueError("unexpected renderer guardrail count")
    if summary["sourceCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("source statement drift")
    if summary["sourceRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime control drift")
    if summary["sourcePublicStatus"] != "held_private":
        raise ValueError("public status drift")
    for key in [
        "rendererSmokeFixtureRecorded",
        "gbVisA2ExportConsumed",
        "nodeDrawCommandsRecorded",
        "edgeDrawCommandsRecorded",
        "smokeChecksRecorded",
        "smokeChecksPassed",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "rendererImplemented",
        "interactiveRendererImplemented",
        "rendererExecuted",
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
        "renderer_smoke_fixture_recorded",
        "gb_vis_a2_export_consumed",
        "node_draw_commands_recorded",
        "edge_draw_commands_recorded",
        "smoke_checks_recorded",
        "smoke_checks_passed",
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
        "artifactType": "renderer_smoke_fixture",
        "validationStatus": "pass",
        "semanticStrength": "private_renderer_smoke_fixture_no_interactive_renderer_no_public_update",
        "source": f"python/results/gb_vis_a3_renderer_smoke_fixture/gb_vis_a3_renderer_smoke_fixture_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a3_renderer_smoke_fixture_feed",
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
        "# GB-VIS-A3 Renderer Smoke Fixture",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A3 records a private renderer smoke fixture without implementing or executing an interactive renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| node draw commands | `{payload['summary']['nodeDrawCommandCount']}` |",
        f"| edge draw commands | `{payload['summary']['edgeDrawCommandCount']}` |",
        f"| legend draw commands | `{payload['summary']['legendDrawCommandCount']}` |",
        f"| smoke checks | `{payload['summary']['smokeCheckCount']}` |",
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
    result_path = out_dir / f"gb_vis_a3_renderer_smoke_fixture_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a3_renderer_smoke_fixture_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a3_renderer_smoke_fixture.json"
    feed_path = command_feed_dir / f"gb_vis_a3_renderer_smoke_fixture_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a3_renderer_smoke_fixture")
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
    print("GB_VIS_A3_RENDERER_SMOKE_FIXTURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
