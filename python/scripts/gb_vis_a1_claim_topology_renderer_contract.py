#!/usr/bin/env python3
"""GB-VIS-A1 claim topology renderer contract seed packet."""

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

from scripts import act_a1_abstract_concrete_trace_contract as a1  # noqa: E402
from scripts import act_a2_alpha_gamma_validator_obligations as a2  # noqa: E402
from scripts import act_a3_alpha_gamma_dry_run_validator_skeleton as a3  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.claim_topology_renderer_contract.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A1_CLAIM_TOPOLOGY_RENDERER_CONTRACT_PASS"

CLAIM_FLAGS = {
    "claim_topology_contract_recorded": True,
    "act_sources_consumed": True,
    "topology_nodes_recorded": True,
    "topology_edges_recorded": True,
    "visual_encoding_contract_recorded": True,
    "renderer_guardrails_recorded": True,
    "renderer_implemented": False,
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
    "GB-VIS-A1 records a claim-topology renderer contract seed only; it does not implement or execute a visualization renderer.",
    "GB-VIS-A1 maps ACT-A1/A2/A3 artifact relationships into inspectable topology nodes, edges, and visual encodings without proving soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A1 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def topology_nodes(contract: dict[str, Any], obligations: dict[str, Any], dry_run: dict[str, Any]) -> list[dict[str, Any]]:
    worked_example = contract["workedExamples"][0]
    nodes = [
        {
            "nodeId": "source_freeze_packet",
            "nodeKind": "source_boundary",
            "label": worked_example["sourceFreezePacket"],
            "claimStrength": worked_example["alphaResult"]["claimStrength"],
            "publicStatus": worked_example["alphaResult"]["publicStatus"],
            "runtimeControl": worked_example["alphaResult"]["runtimeControl"],
        },
        {
            "nodeId": "abstract_claim_object",
            "nodeKind": "abstract_claim",
            "label": worked_example["alphaResult"]["abstractClaimObjectId"],
            "claimStrength": worked_example["alphaResult"]["claimStrength"],
            "publicStatus": worked_example["alphaResult"]["publicStatus"],
            "runtimeControl": worked_example["alphaResult"]["runtimeControl"],
        },
    ]
    nodes.extend(
        {
            "nodeId": f"artifact_class:{item['classId']}",
            "nodeKind": "artifact_class",
            "label": item["classId"],
            "claimStrength": "admissible_concretion_class",
            "publicStatus": "inherits_source_boundary",
            "runtimeControl": "inherits_source_boundary",
        }
        for item in contract["artifactClasses"]
    )
    nodes.extend(
        {
            "nodeId": f"validator_obligation:{item['obligationId']}",
            "nodeKind": "validator_obligation",
            "label": item["obligationId"],
            "operator": item["operator"],
            "claimStrength": "validator_requirement_only",
            "publicStatus": "held_private",
            "runtimeControl": "no_runtime_change",
        }
        for item in obligations["validatorObligations"]
    )
    nodes.extend(
        {
            "nodeId": f"dry_run_check:{item['checkId']}",
            "nodeKind": "dry_run_check",
            "label": item["checkId"],
            "operator": item["operator"],
            "status": item["status"],
            "claimStrength": "dry_run_skeleton_check_only",
            "publicStatus": "held_private",
            "runtimeControl": "no_runtime_change",
        }
        for item in dry_run["dryRunChecks"]
    )
    nodes.extend(
        {
            "nodeId": f"failure_mode:{item['failureModeId']}",
            "nodeKind": "failure_mode",
            "label": item["failureModeId"],
            "severity": item["severity"],
            "claimStrength": "blocking_guard",
            "publicStatus": "held_private",
            "runtimeControl": "no_runtime_change",
        }
        for item in obligations["failureModes"]
    )
    return nodes


def topology_edges(contract: dict[str, Any], obligations: dict[str, Any], dry_run: dict[str, Any]) -> list[dict[str, Any]]:
    edges = [
        {
            "edgeId": "source_freeze_to_abstract_claim_alpha",
            "source": "source_freeze_packet",
            "target": "abstract_claim_object",
            "edgeKind": "alpha_abstraction",
            "operator": "alpha",
            "preserves": ["checkedStatement", "runtimeControl", "publicStatus", "nonClaims"],
        }
    ]
    edges.extend(
        {
            "edgeId": f"abstract_claim_to_artifact_class:{item['classId']}",
            "source": "abstract_claim_object",
            "target": f"artifact_class:{item['classId']}",
            "edgeKind": "gamma_admissibility",
            "operator": "gamma",
            "preserves": ["artifactClass", "claimStrengthBound", "traceability"],
        }
        for item in contract["artifactClasses"]
    )
    edges.extend(
        {
            "edgeId": f"obligation_to_dry_run:{check['sourceObligation']}",
            "source": f"validator_obligation:{check['sourceObligation']}",
            "target": f"dry_run_check:{check['checkId']}",
            "edgeKind": "validated_by_dry_run_skeleton",
            "operator": check["operator"],
            "preserves": ["obligationIdentity", "operator", "noRejectedFailureModes"],
        }
        for check in dry_run["dryRunChecks"]
    )
    edges.extend(
        {
            "edgeId": f"failure_mode_blocks:{item['failureModeId']}",
            "source": f"failure_mode:{item['failureModeId']}",
            "target": "abstract_claim_object",
            "edgeKind": "blocks_claim_escalation",
            "operator": "guard",
            "preserves": ["claimBoundary", "publicGate", "runtimeBoundary"],
        }
        for item in obligations["failureModes"]
    )
    return edges


def visual_encodings() -> list[dict[str, Any]]:
    return [
        {
            "encodingId": "node_kind_shape",
            "field": "nodeKind",
            "contract": "Different node kinds must be visibly distinguishable before any renderer is eligible.",
        },
        {
            "encodingId": "claim_strength_weight",
            "field": "claimStrength",
            "contract": "Claim strength must be represented as bounded weight or emphasis, never as proof status.",
        },
        {
            "encodingId": "public_status_gate_color",
            "field": "publicStatus",
            "contract": "Held-private and public-ready states must be visually separable, with held-private as the default.",
        },
        {
            "encodingId": "runtime_boundary_marker",
            "field": "runtimeControl",
            "contract": "Runtime-control boundaries must be visible wherever a node or edge could imply implementation change.",
        },
        {
            "encodingId": "failure_mode_block_marker",
            "field": "severity",
            "contract": "Blocking failure modes must render as blockers, not warnings or decorative annotations.",
        },
    ]


def renderer_guardrails() -> list[dict[str, Any]]:
    return [
        {
            "guardrailId": "no_public_surface_without_gate",
            "blocks": ["public_surface_updated", "public_ready", "public_copy_approved"],
        },
        {
            "guardrailId": "no_soundness_by_visual_pattern",
            "blocks": ["soundness_proved", "full_galois_connection_claim", "abstract_interpretation_soundness_proved"],
        },
        {
            "guardrailId": "no_runtime_change_by_renderer",
            "blocks": ["runtime_lowering_changed", "runtime_performance_claim"],
        },
        {
            "guardrailId": "no_lane_touch_by_renderer_contract",
            "blocks": ["electronics_repo_touched", "laptop_artifact_consumed", "machlib_file_changed"],
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    contract = a1.build_payload(atlas_gate_path)
    a1.validate_payload(contract)
    obligations = a2.build_payload(atlas_gate_path)
    a2.validate_payload(obligations)
    dry_run = a3.build_payload(atlas_gate_path)
    a3.validate_payload(dry_run)
    nodes = topology_nodes(contract, obligations, dry_run)
    edges = topology_edges(contract, obligations, dry_run)
    encodings = visual_encodings()
    guardrails = renderer_guardrails()
    summary = {
        "sourceContract": contract["artifactId"],
        "sourceObligationsPacket": obligations["artifactId"],
        "sourceDryRunPacket": dry_run["artifactId"],
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "artifactClassNodeCount": sum(1 for node in nodes if node["nodeKind"] == "artifact_class"),
        "validatorObligationNodeCount": sum(1 for node in nodes if node["nodeKind"] == "validator_obligation"),
        "dryRunCheckNodeCount": sum(1 for node in nodes if node["nodeKind"] == "dry_run_check"),
        "failureModeNodeCount": sum(1 for node in nodes if node["nodeKind"] == "failure_mode"),
        "visualEncodingCount": len(encodings),
        "rendererGuardrailCount": len(guardrails),
        "sourceCheckedStatement": contract["summary"]["sourceCheckedStatement"],
        "sourceRuntimeControl": contract["summary"]["sourceRuntimeControl"],
        "sourcePublicStatus": contract["summary"]["sourcePublicStatus"],
        "claimTopologyContractRecorded": True,
        "actSourcesConsumed": True,
        "topologyNodesRecorded": True,
        "topologyEdgesRecorded": True,
        "visualEncodingContractRecorded": True,
        "rendererGuardrailsRecorded": True,
        "rendererImplemented": False,
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
        "nextAction": "GB-VIS-A2 implement a private static topology export fixture or ACT-A4 expand dry-run validator fixtures without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "claim_topology_contract_recorded",
                "act_sources_consumed",
                "topology_nodes_recorded",
                "topology_edges_recorded",
                "visual_encoding_contract_recorded",
                "renderer_guardrails_recorded",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "claim_topology_contract_recorded",
                "act_sources_consumed",
                "topology_nodes_recorded",
                "topology_edges_recorded",
                "visual_encoding_contract_recorded",
                "renderer_guardrails_recorded",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "claim_topology_renderer_contract_v0",
        "artifactId": "gb-vis-a1-claim-topology-renderer-contract",
        "status": STATUS,
        "decision": "record_claim_topology_renderer_contract_no_visualization_execution",
        "date": DATE,
        "sourceContract": contract["artifactId"],
        "sourceObligationsPacket": obligations["artifactId"],
        "sourceDryRunPacket": dry_run["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "topologyNodes": nodes,
        "topologyEdges": edges,
        "visualEncodings": encodings,
        "rendererGuardrails": guardrails,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceContract"] != "act-a1-abstract-concrete-trace-contract":
        raise ValueError("GB-VIS-A1 must consume ACT-A1")
    if payload["sourceObligationsPacket"] != "act-a2-alpha-gamma-validator-obligations":
        raise ValueError("GB-VIS-A1 must consume ACT-A2")
    if payload["sourceDryRunPacket"] != "act-a3-alpha-gamma-dry-run-validator-skeleton":
        raise ValueError("GB-VIS-A1 must consume ACT-A3")
    if summary["nodeCount"] != 23:
        raise ValueError("unexpected topology node count")
    if summary["edgeCount"] != 16:
        raise ValueError("unexpected topology edge count")
    if summary["artifactClassNodeCount"] != 4:
        raise ValueError("unexpected artifact class node count")
    if summary["validatorObligationNodeCount"] != 6:
        raise ValueError("unexpected validator obligation node count")
    if summary["dryRunCheckNodeCount"] != 6:
        raise ValueError("unexpected dry-run check node count")
    if summary["failureModeNodeCount"] != 5:
        raise ValueError("unexpected failure mode node count")
    if summary["visualEncodingCount"] != 5:
        raise ValueError("unexpected visual encoding count")
    if summary["rendererGuardrailCount"] != 4:
        raise ValueError("unexpected renderer guardrail count")
    if summary["sourceCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("source statement drift")
    if summary["sourceRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime control drift")
    if summary["sourcePublicStatus"] != "held_private":
        raise ValueError("public status drift")
    for key in [
        "claimTopologyContractRecorded",
        "actSourcesConsumed",
        "topologyNodesRecorded",
        "topologyEdgesRecorded",
        "visualEncodingContractRecorded",
        "rendererGuardrailsRecorded",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "rendererImplemented",
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
        "claim_topology_contract_recorded",
        "act_sources_consumed",
        "topology_nodes_recorded",
        "topology_edges_recorded",
        "visual_encoding_contract_recorded",
        "renderer_guardrails_recorded",
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
        "artifactType": "claim_topology_renderer_contract",
        "validationStatus": "pass",
        "semanticStrength": "private_claim_topology_renderer_contract_no_visualization_execution_no_public_update",
        "source": f"python/results/gb_vis_a1_claim_topology_renderer_contract/gb_vis_a1_claim_topology_renderer_contract_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a1_claim_topology_renderer_contract_feed",
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
        "# GB-VIS-A1 Claim Topology Renderer Contract",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A1 records a private claim-topology renderer contract without implementing or executing a renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| nodes | `{payload['summary']['nodeCount']}` |",
        f"| edges | `{payload['summary']['edgeCount']}` |",
        f"| visual encodings | `{payload['summary']['visualEncodingCount']}` |",
        f"| renderer guardrails | `{payload['summary']['rendererGuardrailCount']}` |",
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
    result_path = out_dir / f"gb_vis_a1_claim_topology_renderer_contract_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a1_claim_topology_renderer_contract_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a1_claim_topology_renderer_contract.json"
    feed_path = command_feed_dir / f"gb_vis_a1_claim_topology_renderer_contract_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a1_claim_topology_renderer_contract")
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
    print("GB_VIS_A1_CLAIM_TOPOLOGY_RENDERER_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
