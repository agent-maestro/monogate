#!/usr/bin/env python3
"""Private EML expression packet builder.

Input: expression metadata packet.
Output: EML IR, replay summary, Evidence Packet v0, and a short report.

This is EML-R2 plumbing. It does not change Forge/compiler behavior and does
not create public savings, formal verification, or hardware claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_ir_pipeline import build_ir, validate_ir  # noqa: E402

DATE = "2026-05-27"
SCHEMA_VERSION = "monogate.eml_expression_packet.v0"
RESULT_SCHEMA_VERSION = "monogate.eml_packet_builder.result.v0"
FORBIDDEN_TRUE_FLAGS = [
    "public_ready",
    "public_savings_claim",
    "hardware_observed",
    "live_serial_capture_performed",
    "certified_safety_claim",
    "production_controller_claim",
    "formal_verification_claim",
    "theorem_proof_claim",
    "compiler_behavior_changed",
    "forge_behavior_changed",
]
DEFAULT_CLAIM_FLAGS = {key: False for key in FORBIDDEN_TRUE_FLAGS}


def artifact_id(program_id: str) -> str:
    return program_id.replace("_", "-")


def _edges(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    edges = []
    for node in nodes:
        op = node.get("op") or "input"
        for arg in node.get("args", []):
            edges.append({"from": arg, "to": node["id"], "op": op})
    return edges


def _timeline(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for frame in frames:
        kernel = frame["kernel_id"]
        if frame["lifecycle_state"] == "INIT":
            what = "The EML expression packet enters the local IR runtime."
        elif frame["lifecycle_state"] == "READY":
            what = "Stable DAG node identifiers are assigned."
        elif kernel == "div":
            what = "A division node is replayed with a domain annotation, not a proof."
        elif frame["lifecycle_state"] == "END":
            what = "The output node is reached."
        elif frame["lifecycle_state"] == "PARKED":
            what = "The replay packet parks at the terminal boundary."
        else:
            what = f"The {kernel} node replays as a static expression step."
        out.append(
            {
                "frame_id": frame["frame_id"],
                "tick": frame["monotonic_tick"],
                "state": frame["lifecycle_state"],
                "kernel_id": kernel,
                "guard_action": frame["guard_action"],
                "guard_reason": frame["guard_reason"],
                "replay_hash": frame["replay_hash"],
                "what_happened": what,
            }
        )
    return out


def _build_obligations(packet: dict[str, Any], ir: dict[str, Any]) -> list[dict[str, Any]]:
    obligations: list[dict[str, Any]] = []
    program_id = packet["program_id"]
    for node in ir["nodes"]:
        op = node.get("op")
        if op == "div":
            obligations.append(
                {
                    "obligationId": f"{program_id}:domain:{node['id']}:div-denominator-nonzero",
                    "kind": "domain",
                    "status": "candidate_only",
                    "trigger": "div",
                    "nodeId": node["id"],
                    "description": "Division node requires evidence that the denominator is not zero over declared inputs/ranges.",
                    "proofTarget": "denominator_nonzero",
                    "nonClaim": "This card records a proof obligation; it does not prove the denominator condition.",
                }
            )
        elif op == "ln":
            obligations.append(
                {
                    "obligationId": f"{program_id}:domain:{node['id']}:ln-argument-positive",
                    "kind": "domain",
                    "status": "candidate_only",
                    "trigger": "ln",
                    "nodeId": node["id"],
                    "description": "Log node requires evidence that its argument is positive over declared inputs/ranges.",
                    "proofTarget": "log_argument_positive",
                    "nonClaim": "This card records a proof obligation; it does not prove positivity.",
                }
            )
        elif op == "sqrt":
            obligations.append(
                {
                    "obligationId": f"{program_id}:domain:{node['id']}:sqrt-argument-nonnegative",
                    "kind": "domain",
                    "status": "candidate_only",
                    "trigger": "sqrt",
                    "nodeId": node["id"],
                    "description": "Square-root node requires evidence that its argument is nonnegative over declared inputs/ranges.",
                    "proofTarget": "sqrt_argument_nonnegative",
                    "nonClaim": "This card records a proof obligation; it does not prove nonnegativity.",
                }
            )
    for name, bounds in sorted(packet.get("safe_ranges", {}).items()):
        obligations.append(
            {
                "obligationId": f"{program_id}:range:{name}:declared-safe-range",
                "kind": "range_safety",
                "status": "candidate_only",
                "trigger": "safe_range",
                "input": name,
                "description": f"Input {name} declares range [{bounds['min']}, {bounds['max']}]; downstream runtime or proof work must preserve this boundary.",
                "proofTarget": "input_range_respected",
                "nonClaim": "This card records a declared range boundary; it is not hardware evidence or a certified safety proof.",
            }
        )
    return obligations


def packet_from_cli(args: argparse.Namespace) -> dict[str, Any]:
    if not args.expression:
        raise ValueError("--expression is required when --packet is not provided")
    inputs = [item.strip() for item in args.inputs.split(",") if item.strip()] if args.inputs else []
    return {
        "schemaVersion": SCHEMA_VERSION,
        "program_id": args.program_id,
        "family": args.family,
        "expression": args.expression,
        "inputs": inputs,
        "units": {name: "unspecified" for name in inputs},
        "safe_ranges": {},
        "physical_meaning": args.physical_meaning,
        "source_repo": args.source_repo,
        "simulated_trace_samples": [],
        "claim_flags": dict(DEFAULT_CLAIM_FLAGS),
    }


def load_packet(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_expression_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("schemaVersion must be monogate.eml_expression_packet.v0")
    program_id = packet.get("program_id")
    if not isinstance(program_id, str) or not re.match(r"^[a-z][a-z0-9_]*_v[0-9]+$", program_id):
        raise ValueError("program_id must match ^[a-z][a-z0-9_]*_v[0-9]+$")
    for key in ["family", "expression", "physical_meaning", "source_repo"]:
        if not isinstance(packet.get(key), str) or not packet[key]:
            raise ValueError(f"{key} must be a non-empty string")
    inputs = packet.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("inputs must be a non-empty list")
    if len(set(inputs)) != len(inputs):
        raise ValueError("inputs must be unique")
    for name in inputs:
        if not isinstance(name, str) or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            raise ValueError(f"invalid input name: {name!r}")
    units = packet.get("units")
    if not isinstance(units, dict):
        raise ValueError("units must be an object")
    safe_ranges = packet.get("safe_ranges")
    if not isinstance(safe_ranges, dict):
        raise ValueError("safe_ranges must be an object")
    for name, bounds in safe_ranges.items():
        if not isinstance(bounds, dict) or "min" not in bounds or "max" not in bounds:
            raise ValueError(f"safe range for {name} must include min and max")
        if not isinstance(bounds["min"], (int, float)) or not isinstance(bounds["max"], (int, float)):
            raise ValueError(f"safe range for {name} must be numeric")
        if bounds["min"] > bounds["max"]:
            raise ValueError(f"safe range for {name} has min > max")
    claim_flags = packet.get("claim_flags")
    if not isinstance(claim_flags, dict):
        raise ValueError("claim_flags must be an object")
    missing = [key for key in FORBIDDEN_TRUE_FLAGS if key not in claim_flags]
    if missing:
        raise ValueError(f"claim_flags missing required keys: {', '.join(missing)}")
    for key in FORBIDDEN_TRUE_FLAGS:
        if claim_flags.get(key) is not False:
            raise ValueError(f"forbidden claim flag must be false: {key}")


def build_result(packet: dict[str, Any]) -> dict[str, Any]:
    validate_expression_packet(packet)
    ir = build_ir(packet["program_id"], packet["expression"])
    validate_ir(ir)
    ir_args = set(ir["arguments"])
    declared_inputs = set(packet["inputs"])
    if ir_args != declared_inputs:
        raise ValueError(
            "declared inputs must match parsed expression arguments: "
            f"declared={sorted(declared_inputs)} parsed={sorted(ir_args)}"
        )
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
    edges = _edges(ir["nodes"])
    obligations = _build_obligations(packet, ir)
    return {
        "schemaVersion": RESULT_SCHEMA_VERSION,
        "artifactId": artifact_id(packet["program_id"]),
        "date": DATE,
        "status": "EML_PACKET_BUILDER_CANDIDATE_PASS",
        "sourcePacket": packet,
        "ir": {
            "schemaVersion": ir["schema_version"],
            "programId": ir["program_id"],
            "outputNode": ir["output_node"],
            "nodeCount": len(ir["nodes"]),
            "edgeCount": len(edges),
            "nodes": ir["nodes"],
            "edges": edges,
            "reusedNodes": reused_nodes,
            "lowering": ir["lowering"],
        },
        "costs": {
            "costModel": ir["cost_model"],
            "canonicalPublicTreeSuperbestNodes": ir["tree_superbest_nodes"],
            "internalDagSuperbestNodes": ir["dag_superbest_nodes"],
            "internalExtraDagSavingsNodes": ir["extra_superbest_savings_nodes"],
            "canonicalPublicTreeEmlNodes": ir["tree_eml_nodes"],
            "internalDagEmlNodes": ir["dag_eml_nodes"],
            "publicSavingsClaim": False,
        },
        "replay": {
            "packetId": ir["replay_packet"]["packet_id"],
            "frameCount": ir["replay_packet"]["frame_count"],
            "terminalState": ir["replay_packet"]["terminal_state"],
            "hashChainValid": True,
            "frames": ir["replay_packet"]["frames"],
            "timeline": _timeline(ir["replay_packet"]["frames"]),
        },
        "review": {
            "decision": "candidate_only",
            "validationStatus": "pass",
            "replayStatus": "pass",
            "semanticStrength": "eml_expression_packet_candidate_no_public_savings_claim",
            "claimBoundary": "Generated EML packet is candidate-only. DAG savings are internal evidence, not a public savings claim.",
            "nonClaims": [
                "No new public savings claim.",
                "No Forge/compiler behavior change.",
                "No theorem or formal verification claim.",
                "No hardware observation.",
                "No certified safety or production controller claim.",
                "No package publish or deploy.",
            ],
        },
        "obligations": {
            "schemaVersion": "monogate.eml_obligation_cards.v0",
            "status": "candidate_only",
            "cards": obligations,
            "summary": {
                "count": len(obligations),
                "domain_count": sum(1 for item in obligations if item["kind"] == "domain"),
                "range_safety_count": sum(1 for item in obligations if item["kind"] == "range_safety"),
                "proved_count": 0,
            },
            "nonClaims": [
                "Obligation cards are not proofs.",
                "Range cards are not hardware observations.",
                "Domain cards are not formal verification claims.",
            ],
        },
        "validationCommands": [
            "python python/scripts/eml_packet_builder.py --build-fixtures --strict",
            "python -m pytest -q python/tests/test_eml_packet_builder.py",
        ],
    }


def build_evidence_packet(result: dict[str, Any]) -> dict[str, Any]:
    packet = result["sourcePacket"]
    return {
        "schemaVersion": "monogate.evidence_public_packet.v0",
        "artifactId": result["artifactId"],
        "title": f"EML Packet: {packet['program_id']}",
        "reviewDecision": "candidate_only",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": result["review"]["semanticStrength"],
        "semanticReview": {
            "program_id": packet["program_id"],
            "family": packet["family"],
            "source_expression": packet["expression"],
            "input_count": len(packet["inputs"]),
            "node_count": result["ir"]["nodeCount"],
            "edge_count": result["ir"]["edgeCount"],
            "reused_node_count": len(result["ir"]["reusedNodes"]),
            "frame_count": result["replay"]["frameCount"],
            "obligation_count": result["obligations"]["summary"]["count"],
            "domain_obligation_count": result["obligations"]["summary"]["domain_count"],
            "range_safety_obligation_count": result["obligations"]["summary"]["range_safety_count"],
            "public_savings_claim": False,
            "internal_extra_dag_savings_nodes": result["costs"]["internalExtraDagSavingsNodes"],
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "claimBoundary": result["review"]["claimBoundary"],
        "nonClaims": result["review"]["nonClaims"],
        "reviewHighlights": [
            "Built from an EML Expression Packet v0 input.",
            "Generated EML IR and replay frames with the existing IR substrate pipeline.",
            "Generated candidate proof-obligation cards for domain and range boundaries.",
            "Kept public savings and hardware/proof claims false.",
        ],
        "validationCommands": result["validationCommands"],
        "timeline": [
            {"label": "Packet intake", "status": "pass", "detail": "Expression packet validated locally."},
            {"label": "IR/replay", "status": "pass", "detail": "Existing EML IR pipeline emitted a parked replay packet."},
            {"label": "Claim boundary", "status": "pass", "detail": "Forbidden public/hardware/proof claims remain false."},
        ],
        "reviewReasons": [
            "Private intake artifact for deciding whether an EML expression should be surfaced later.",
        ],
        "reviewNotes": "Candidate-only private EML packet-builder output.",
        "sourceReportPath": f"reports/eml_packets/{packet['program_id']}_packet_builder_{DATE.replace('-', '_')}.md",
        "evidencePaths": [
            "schemas/eml_expression_packet_v0.json",
            "python/scripts/eml_packet_builder.py",
            f"python/results/eml_packets/{packet['program_id']}_packet_{DATE.replace('-', '_')}.json",
            f"reports/evidence_packets/{packet['program_id']}_eml_packet.json",
        ],
    }


def render_report(result: dict[str, Any], evidence: dict[str, Any]) -> str:
    packet = result["sourcePacket"]
    return "\n".join(
        [
            f"# EML Packet Builder Result: {packet['program_id']}",
            "",
            f"Date: {DATE}",
            "",
            "Status: `EML_PACKET_BUILDER_CANDIDATE_PASS`",
            "",
            "## Source Packet",
            "",
            f"- Family: `{packet['family']}`",
            f"- Expression: `{packet['expression']}`",
            f"- Inputs: `{', '.join(packet['inputs'])}`",
            f"- Source repo: `{packet['source_repo']}`",
            f"- Meaning: {packet['physical_meaning']}",
            "",
            "## Generated Artifact",
            "",
            f"- Artifact: `{result['artifactId']}`",
            f"- DAG nodes: `{result['ir']['nodeCount']}`",
            f"- DAG edges: `{result['ir']['edgeCount']}`",
            f"- Reused nodes: `{len(result['ir']['reusedNodes'])}`",
            f"- Replay frames: `{result['replay']['frameCount']}`",
            f"- Obligation cards: `{result['obligations']['summary']['count']}`",
            f"- Public tree SuperBEST baseline: `{result['costs']['canonicalPublicTreeSuperbestNodes']}`",
            f"- Internal DAG SuperBEST candidate: `{result['costs']['internalDagSuperbestNodes']}`",
            "",
            "## Review",
            "",
            f"- Decision: `{evidence['reviewDecision']}`",
            f"- Validation: `{evidence['validationStatus']}`",
            f"- Replay: `{evidence['replayStatus']}`",
            f"- Semantic strength: `{evidence['semanticStrength']}`",
            "",
            "## Obligation Cards",
            "",
            f"- Domain obligations: `{result['obligations']['summary']['domain_count']}`",
            f"- Range-safety obligations: `{result['obligations']['summary']['range_safety_count']}`",
            f"- Proved obligations: `{result['obligations']['summary']['proved_count']}`",
            "",
            "## Non-Claims",
            "",
            "- No new public savings claim.",
            "- No Forge/compiler behavior change.",
            "- No theorem or formal verification claim.",
            "- No hardware observation.",
            "- No certified safety or production controller claim.",
            "- No package publish or deploy.",
            "",
        ]
    )


def write_outputs(result: dict[str, Any], out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Path]:
    program_id = result["sourcePacket"]["program_id"]
    stamp = DATE.replace("-", "_")
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"{program_id}_packet_{stamp}.json"
    report_path = report_dir / f"{program_id}_packet_builder_{stamp}.md"
    evidence_path = evidence_dir / f"{program_id}_eml_packet.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(result, evidence), encoding="utf-8")
    return {
        "result": result_path,
        "report": report_path,
        "evidence": evidence_path,
    }


def build_one(packet: dict[str, Any], out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    result = build_result(packet)
    paths = write_outputs(result, out_dir, report_dir, evidence_dir)
    return {"result": result, "paths": {key: str(value) for key, value in paths.items()}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, help="EML Expression Packet v0 JSON file")
    parser.add_argument("--expression", help="Expression for direct CLI intake")
    parser.add_argument("--program-id", default="adhoc_expression_v0")
    parser.add_argument("--family", default="adhoc")
    parser.add_argument("--inputs", default="", help="Comma-separated input names for direct CLI intake")
    parser.add_argument("--physical-meaning", default="Ad hoc EML expression packet.")
    parser.add_argument("--source-repo", default="monogate")
    parser.add_argument("--fixtures-dir", type=Path, default=ROOT / "python/fixtures/eml_expression_packets")
    parser.add_argument("--build-fixtures", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports/eml_packets")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.build_fixtures:
        packets = [load_packet(path) for path in sorted(args.fixtures_dir.glob("*.json"))]
        if args.strict and len(packets) < 3:
            raise SystemExit("strict mode requires at least 3 fixture packets")
        built = [build_one(packet, args.out_dir, args.report_dir, args.evidence_dir) for packet in packets]
        print("EML_PACKET_BUILDER_FIXTURES_OK")
        print(f"packets={len(built)}")
        return 0

    packet = load_packet(args.packet) if args.packet else packet_from_cli(args)
    built = build_one(packet, args.out_dir, args.report_dir, args.evidence_dir)
    if args.strict and built["result"]["review"]["decision"] != "candidate_only":
        raise SystemExit("strict mode requires candidate_only review decision")
    print("EML_PACKET_BUILDER_OK")
    print(f"artifact={built['result']['artifactId']} frames={built['result']['replay']['frameCount']}")
    print(json.dumps(built["paths"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
