#!/usr/bin/env python3
"""EML-R1 IR Explorer bridge fixture.

This promotes one existing EML IR substrate program into a candidate-only
Explorer fixture and evidence packet. It reuses the May 25 IR pipeline and
does not change compiler behavior or public savings claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_ir_pipeline import build_ir, validate_ir  # noqa: E402

DATE = "2026-05-27"
PROGRAM_ID = "attention_three_logits_three_outputs_v0"
ARTIFACT_ID = "eml-r1-ir-explorer-bridge"
EXPRESSION = (
    "exp(q*k1) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + "
    "exp(q*k2) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + "
    "exp(q*k3) / (exp(q*k1) + exp(q*k2) + exp(q*k3))"
)


def _edges(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for node in nodes:
        op = node.get("op") or "input"
        for arg in node.get("args", []):
            out.append({"from": arg, "to": node["id"], "op": op})
    return out


def _timeline(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    timeline = []
    for frame in frames:
        kernel = frame["kernel_id"]
        action = frame["guard_action"]
        if frame["lifecycle_state"] == "INIT":
            what = "The selected EML expression enters the replay runtime."
        elif frame["lifecycle_state"] == "READY":
            what = "Stable DAG node identifiers are assigned before node replay begins."
        elif kernel == "div":
            what = "A division node is replayed with a domain annotation, not a proof."
        elif frame["lifecycle_state"] == "END":
            what = "The output node is reached and the trace emits END."
        elif frame["lifecycle_state"] == "PARKED":
            what = "The replay packet parks at an explicit terminal boundary."
        else:
            what = f"The {kernel} node replays as a static expression step."
        timeline.append(
            {
                "frame_id": frame["frame_id"],
                "tick": frame["monotonic_tick"],
                "state": frame["lifecycle_state"],
                "kernel_id": kernel,
                "guard_action": action,
                "guard_reason": frame["guard_reason"],
                "replay_hash": frame["replay_hash"],
                "what_happened": what,
            }
        )
    return timeline


def build_fixture() -> dict[str, Any]:
    ir = build_ir(PROGRAM_ID, EXPRESSION)
    validate_ir(ir)
    reused_nodes = [
        {
            "id": node["id"],
            "kind": node["kind"],
            "op": node.get("op"),
            "source": node["source"],
            "reuse_count": node["reuse_count"],
        }
        for node in ir["nodes"]
        if node.get("reuse_count", 1) > 1
    ]
    frames = ir["replay_packet"]["frames"]
    tree_best = ir["tree_superbest_nodes"]
    dag_best = ir["dag_superbest_nodes"]
    tree_eml = ir["tree_eml_nodes"]
    dag_eml = ir["dag_eml_nodes"]
    return {
        "schemaVersion": "monogate.eml_r1.ir_explorer_bridge.v0",
        "artifactId": ARTIFACT_ID,
        "date": DATE,
        "status": "EML_R1_IR_EXPLORER_BRIDGE_CANDIDATE_PASS",
        "selectedProgram": {
            "programId": PROGRAM_ID,
            "family": "softmax_attention",
            "whySelected": "Existing EML IR substrate fixture with visible DAG sharing and replay frames.",
            "sourceExpression": EXPRESSION,
            "arguments": ir["arguments"],
        },
        "ir": {
            "schemaVersion": ir["schema_version"],
            "outputNode": ir["output_node"],
            "nodeCount": len(ir["nodes"]),
            "edgeCount": len(_edges(ir["nodes"])),
            "nodes": ir["nodes"],
            "edges": _edges(ir["nodes"]),
            "reusedNodes": reused_nodes,
            "lowering": ir["lowering"],
        },
        "costs": {
            "costModel": ir["cost_model"],
            "canonicalPublicTreeSuperbestNodes": tree_best,
            "internalDagSuperbestNodes": dag_best,
            "internalExtraDagSavingsNodes": ir["extra_superbest_savings_nodes"],
            "canonicalPublicTreeEmlNodes": tree_eml,
            "internalDagEmlNodes": dag_eml,
            "treeToDagSuperbestRatio": round(dag_best / tree_best, 4),
            "treeToDagEmlRatio": round(dag_eml / tree_eml, 4),
            "publicSavingsClaim": False,
        },
        "replay": {
            "packetId": ir["replay_packet"]["packet_id"],
            "frameCount": ir["replay_packet"]["frame_count"],
            "terminalState": ir["replay_packet"]["terminal_state"],
            "hashChainValid": True,
            "frames": frames,
            "timeline": _timeline(frames),
        },
        "claimBoundary": {
            "candidateOnly": True,
            "publicReady": False,
            "publicSavingsClaim": False,
            "compilerBehaviorChanged": False,
            "forgeBehaviorChanged": False,
            "formalVerificationClaim": False,
            "theoremProofClaim": False,
            "packagePublishPerformed": False,
            "deployPerformed": False,
            "boundaryText": "EML-R1 surfaces an existing IR/replay artifact for inspection. DAG savings remain internal candidate evidence, not a new public savings claim.",
        },
        "evidencePaths": [
            "python/scripts/eml_ir_pipeline.py",
            "python/scripts/eml_r1_ir_explorer_bridge.py",
            "python/results/eml_r1_ir_explorer_bridge_2026_05_27.json",
            "reports/eml_r1_ir_explorer_bridge_2026_05_27.md",
            "reports/evidence_packets/eml_r1_ir_explorer_bridge.json",
        ],
        "validationCommands": [
            "python python/scripts/eml_r1_ir_explorer_bridge.py --strict",
            "python -m pytest -q python/tests/test_eml_r1_ir_explorer_bridge.py",
        ],
    }


def build_evidence_packet(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.evidence_public_packet.v0",
        "artifactId": ARTIFACT_ID,
        "title": "EML-R1 IR Explorer Bridge",
        "reviewDecision": "candidate_only",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": "eml_ir_explorer_bridge_candidate_no_public_savings_claim",
        "semanticReview": {
            "program_id": fixture["selectedProgram"]["programId"],
            "source_expression": fixture["selectedProgram"]["sourceExpression"],
            "node_count": fixture["ir"]["nodeCount"],
            "edge_count": fixture["ir"]["edgeCount"],
            "reused_node_count": len(fixture["ir"]["reusedNodes"]),
            "frame_count": fixture["replay"]["frameCount"],
            "public_savings_claim": False,
            "internal_extra_dag_savings_nodes": fixture["costs"]["internalExtraDagSavingsNodes"],
        },
        "claimFlags": {
            "public_ready": False,
            "hardware_observed": False,
            "live_serial_capture_performed": False,
            "certified_safety_claim": False,
            "production_controller_claim": False,
            "compiler_behavior_changed": False,
            "forge_behavior_changed": False,
            "formal_verification_claim": False,
            "theorem_proof_claim": False,
            "public_savings_claim": False,
        },
        "claimBoundary": fixture["claimBoundary"]["boundaryText"],
        "nonClaims": [
            "No new public savings claim.",
            "No Forge compiler behavior change.",
            "No formal verification or theorem proof claim.",
            "No production controller or certified safety claim.",
            "No hardware observation.",
            "No package publish or deploy.",
        ],
        "reviewHighlights": [
            "Reuses the existing EML IR substrate pipeline.",
            "Shows a real DAG/shared-node fixture with replay frames.",
            "Keeps DAG savings as internal candidate evidence.",
        ],
        "validationCommands": fixture["validationCommands"],
        "timeline": [
            {"label": "IR selected", "status": "pass", "detail": "Canonical attention fixture selected from existing substrate work."},
            {"label": "Replay checked", "status": "pass", "detail": "Replay hash predecessor chain validated by the underlying IR pipeline."},
            {"label": "Claim boundary", "status": "pass", "detail": "Public savings claim remains false."},
        ],
        "reviewReasons": [
            "Useful for the public/dev inspector because it makes EML IR concrete without expanding claims.",
        ],
        "reviewNotes": "Candidate-only bridge from EML IR to the Explorer. Reviewer approval for local surfacing only.",
        "sourceReportPath": "reports/eml_r1_ir_explorer_bridge_2026_05_27.md",
        "evidencePaths": fixture["evidencePaths"],
    }


def render_report(fixture: dict[str, Any], packet: dict[str, Any]) -> str:
    costs = fixture["costs"]
    return "\n".join(
        [
            "# EML-R1 IR Explorer Bridge",
            "",
            f"Date: {DATE}",
            "",
            "Status: `EML_R1_IR_EXPLORER_BRIDGE_CANDIDATE_PASS`",
            "",
            "This sprint reconnects the EML phase to the evidence engine by turning one existing EML IR substrate artifact into an inspectable candidate fixture.",
            "",
            "## Selected Program",
            "",
            f"- Program: `{fixture['selectedProgram']['programId']}`",
            f"- Family: `{fixture['selectedProgram']['family']}`",
            f"- Expression: `{fixture['selectedProgram']['sourceExpression']}`",
            "",
            "## Inspector Metrics",
            "",
            f"- DAG nodes: `{fixture['ir']['nodeCount']}`",
            f"- DAG edges: `{fixture['ir']['edgeCount']}`",
            f"- Reused nodes: `{len(fixture['ir']['reusedNodes'])}`",
            f"- Replay frames: `{fixture['replay']['frameCount']}`",
            f"- Public tree SuperBEST baseline: `{costs['canonicalPublicTreeSuperbestNodes']}`",
            f"- Internal DAG SuperBEST candidate: `{costs['internalDagSuperbestNodes']}`",
            f"- Internal extra DAG savings nodes: `{costs['internalExtraDagSavingsNodes']}`",
            "",
            "## Claim Boundary",
            "",
            fixture["claimBoundary"]["boundaryText"],
            "",
            "- No new public savings claim.",
            "- No Forge/compiler behavior change.",
            "- No formal verification claim.",
            "- No package publish or deploy.",
            "",
            "## Evidence Packet",
            "",
            f"- Artifact: `{packet['artifactId']}`",
            f"- Reviewer decision: `{packet['reviewDecision']}`",
            f"- Validation status: `{packet['validationStatus']}`",
            f"- Replay status: `{packet['replayStatus']}`",
            "",
            "## Next EML Step",
            "",
            "Use this bridge as the first public-dev cockpit for EML IR, then extend EML-R2 toward a small IR packet builder that lets a reviewer choose expressions and inspect tree, DAG, replay, and non-claims before anything is surfaced.",
            "",
        ]
    )


def validate_fixture(fixture: dict[str, Any], packet: dict[str, Any]) -> None:
    if fixture["schemaVersion"] != "monogate.eml_r1.ir_explorer_bridge.v0":
        raise ValueError("fixture schema mismatch")
    if fixture["artifactId"] != ARTIFACT_ID:
        raise ValueError("artifact id mismatch")
    if fixture["claimBoundary"]["publicSavingsClaim"] is not False:
        raise ValueError("public savings claim must be false")
    if fixture["claimBoundary"]["compilerBehaviorChanged"] is not False:
        raise ValueError("compiler behavior must not change")
    if fixture["costs"]["internalExtraDagSavingsNodes"] <= 0:
        raise ValueError("expected positive internal DAG savings evidence")
    if fixture["replay"]["frameCount"] < 10:
        raise ValueError("expected inspectable replay frame count")
    if not fixture["ir"]["reusedNodes"]:
        raise ValueError("expected reused nodes")
    if packet["reviewDecision"] != "candidate_only":
        raise ValueError("packet must remain candidate-only")
    for key in [
        "public_ready",
        "hardware_observed",
        "live_serial_capture_performed",
        "certified_safety_claim",
        "production_controller_claim",
        "public_savings_claim",
    ]:
        if packet["claimFlags"].get(key) is not False:
            raise ValueError(f"packet claim flag must be false: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=ROOT / f"python/results/eml_r1_ir_explorer_bridge_{DATE.replace('-', '_')}.json")
    parser.add_argument("--out-report", type=Path, default=ROOT / f"reports/eml_r1_ir_explorer_bridge_{DATE.replace('-', '_')}.md")
    parser.add_argument("--out-packet", type=Path, default=ROOT / "reports/evidence_packets/eml_r1_ir_explorer_bridge.json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    fixture = build_fixture()
    packet = build_evidence_packet(fixture)
    validate_fixture(fixture, packet)
    if args.strict and packet["claimFlags"]["public_savings_claim"] is not False:
        raise SystemExit("public_savings_claim must be false")

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_packet.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out_packet.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out_report.write_text(render_report(fixture, packet), encoding="utf-8")

    print("EML_R1_IR_EXPLORER_BRIDGE_OK")
    print(f"artifact={ARTIFACT_ID} frames={fixture['replay']['frameCount']} reused={len(fixture['ir']['reusedNodes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
