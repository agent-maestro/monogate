#!/usr/bin/env python3
"""EML IR v0 pipeline: expression -> DAG IR -> replay packet.

This is the missing bridge between existing SuperBEST DAG lowering and the
replay-native evidence stack. It is intentionally small: no Forge behavior
changes, no compiler integration claim, and no public headline savings change.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts import superbest_dag_savings_audit as audit  # noqa: E402
from scripts.superbest_dag_lowering import lower_expression  # noqa: E402


BOUNDARIES = {
    "internal_only": True,
    "compiler_behavior_changed": False,
    "canonical_row_table_changed": False,
    "public_ready": False,
    "public_theorem_claim": False,
    "formal_verification_claim": False,
    "package_publish_performed": False,
    "deploy_performed": False,
}


EXAMPLE_PROGRAMS = [
    {
        "program_id": "sigmoid_v0",
        "family": "sigmoid_logistic",
        "expression": "1 / (1 + exp(-x))",
        "why": "Canonical compact logistic expression.",
    },
    {
        "program_id": "sigmoid_value_and_derivative_v0",
        "family": "sigmoid_logistic",
        "expression": "1 / (1 + exp(-x)) + (1 / (1 + exp(-x))) * (1 - (1 / (1 + exp(-x))))",
        "why": "Shows value-plus-derivative reuse.",
    },
    {
        "program_id": "softmax_denominator_3_v0",
        "family": "softmax_attention",
        "expression": "exp(a) + exp(b) + exp(c)",
        "why": "Small denominator fixture for attention-style reuse.",
    },
    {
        "program_id": "attention_three_logits_three_outputs_v0",
        "family": "softmax_attention",
        "expression": "exp(q*k1) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + exp(q*k2) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + exp(q*k3) / (exp(q*k1) + exp(q*k2) + exp(q*k3))",
        "why": "Strong DAG savings fixture already identified by SuperBEST frontier work.",
    },
    {
        "program_id": "rational_shared_denominator_v0",
        "family": "rational_shared_denominator",
        "expression": "(x + 1) / (x - 1) + (x * x) / (x - 1) + ln(x - 1) / (x - 1)",
        "why": "Repeated denominator and log-rational term.",
    },
    {
        "program_id": "polynomial_basis_degree5_v0",
        "family": "polynomial_basis_reuse",
        "expression": "(x * x) + (x * x) * y + (x * x) * (x * x) + (x * x) * (x * x) * z",
        "why": "Basis reuse fixture for x^2/x^4-style terms.",
    },
    {
        "program_id": "voltage_divider_v0",
        "family": "trainer_board_math",
        "expression": "vin_norm * r2_ohm / (r1_ohm + r2_ohm)",
        "why": "Trainer Board-compatible math frame; simulated only.",
    },
    {
        "program_id": "threshold_reflex_target_v0",
        "family": "trainer_board_math",
        "expression": "((pot_raw - 0.55) / 0.10) + 0.5",
        "why": "Threshold-reflex target expression before clamp/rate-limit guard.",
    },
    {
        "program_id": "gaussian_v0",
        "family": "forge_efrog_fixture",
        "expression": "exp(-(x * x))",
        "why": "Small Forge/eFrog curriculum fixture.",
    },
    {
        "program_id": "log_sum_exp_pair_v0",
        "family": "softplus_logsumexp",
        "expression": "ln(exp(a) + exp(b))",
        "why": "Log-sum-exp style expression for future stable lowering work.",
    },
]


def _fingerprint(expression: str) -> tuple:
    return audit._fingerprint(ast.parse(expression, mode="eval"))


def _count_fingerprints(fp: tuple) -> dict[tuple, int]:
    counts: dict[tuple, int] = {}
    for item in audit._walk_fingerprints(fp):
        counts[item] = counts.get(item, 0) + 1
    return counts


def _op_name(fp: tuple) -> str | None:
    return audit._op_name(fp)


def _node_source(fp: tuple, id_by_fp: dict[tuple, str]) -> str:
    if fp[0] == "var":
        return fp[1]
    if fp[0] == "const":
        return fp[1]
    op = _op_name(fp)
    children = fp[2]
    args = [id_by_fp[child] for child in children]
    if op in {"neg", "exp", "ln", "sqrt", "sin", "cos", "tanh"}:
        return f"{op}({args[0]})"
    if op in {"add", "sub", "mul", "div", "pow"}:
        return f"{op}({', '.join(args)})"
    return repr(fp)


def _topological_fingerprints(fp: tuple) -> list[tuple]:
    seen: set[tuple] = set()
    ordered: list[tuple] = []

    def visit(item: tuple) -> None:
        if item in seen:
            return
        if item[0] == "op":
            for child in item[2]:
                visit(child)
        seen.add(item)
        ordered.append(item)

    visit(fp)
    return ordered


def _build_nodes(fp: tuple) -> tuple[list[dict[str, Any]], str]:
    ordered = _topological_fingerprints(fp)
    id_by_fp = {item: f"n{i}" for i, item in enumerate(ordered)}
    counts = _count_fingerprints(fp)
    nodes = []
    for item in ordered:
        op = _op_name(item)
        if item[0] == "var":
            kind = "input"
            args: list[str] = []
            source = item[1]
        elif item[0] == "const":
            kind = "constant"
            args = []
            source = item[1]
        else:
            kind = "operation"
            args = [id_by_fp[child] for child in item[2]]
            source = _node_source(item, id_by_fp)
        nodes.append(
            {
                "id": id_by_fp[item],
                "kind": kind,
                "op": op,
                "args": args,
                "source": source,
                "superbest_cost": audit._cost(op, audit.POSITIVE_COSTS) if op else 0,
                "eml_cost": audit._cost(op, audit.EML_COSTS) if op else 0,
                "reuse_count": counts.get(item, 1),
            }
        )
    return nodes, id_by_fp[fp]


def _stable_hash(prev: str | None, frame_without_hash: dict[str, Any]) -> str:
    material = {
        "prev": prev,
        "frame": frame_without_hash,
    }
    data = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _frame(
    *,
    program_id: str,
    frame_index: int,
    lifecycle_state: str,
    kernel_id: str,
    input_value: Any,
    requested_output: Any,
    safe_output: Any,
    guard_action: str,
    guard_reason: str,
    prev_hash: str | None,
) -> dict[str, Any]:
    base = {
        "frame_id": f"{program_id}:f{frame_index:04d}",
        "program_id": program_id,
        "runtime_id": "eml_ir_pipeline_v0",
        "kernel_id": kernel_id,
        "lifecycle_state": lifecycle_state,
        "monotonic_tick": frame_index,
        "timestamp_ms": frame_index,
        "input": input_value,
        "requested_output": requested_output,
        "safe_output": safe_output,
        "guard_action": guard_action,
        "guard_reason": guard_reason,
        "replay_hash_prev": prev_hash,
        "source": "eml_ir_substrate_v0",
        "evidence_level": "simulated",
    }
    return {**base, "replay_hash": _stable_hash(prev_hash, base)}


def _replay_packet(program_id: str, nodes: list[dict[str, Any]], output_node: str) -> dict[str, Any]:
    frames = []
    prev = None
    lifecycle_specs = [
        ("INIT", "eml_ir_loader", None, None, None, "ANNOTATE", "program accepted by local parser"),
        ("READY", "eml_ir_dag", None, None, None, "ANNOTATE", "DAG nodes assigned stable ids"),
    ]
    for spec in lifecycle_specs:
        frame = _frame(
            program_id=program_id,
            frame_index=len(frames),
            lifecycle_state=spec[0],
            kernel_id=spec[1],
            input_value=spec[2],
            requested_output=spec[3],
            safe_output=spec[4],
            guard_action=spec[5],
            guard_reason=spec[6],
            prev_hash=prev,
        )
        frames.append(frame)
        prev = frame["replay_hash"]
    for node in nodes:
        if node["kind"] != "operation":
            continue
        guard_action = "PASS"
        guard_reason = "static expression node"
        if node["op"] == "div":
            guard_action = "ANNOTATE"
            guard_reason = "division node; denominator domain is not proven by this prototype"
        frame = _frame(
            program_id=program_id,
            frame_index=len(frames),
            lifecycle_state="RUNNING",
            kernel_id=node["op"] or "unknown",
            input_value={"args": node["args"]},
            requested_output=node["id"],
            safe_output=node["id"],
            guard_action=guard_action,
            guard_reason=guard_reason,
            prev_hash=prev,
        )
        frames.append(frame)
        prev = frame["replay_hash"]
    for state, reason in [("END", f"output node {output_node} reached"), ("PARKED", "explicit replay terminal boundary")]:
        frame = _frame(
            program_id=program_id,
            frame_index=len(frames),
            lifecycle_state=state,
            kernel_id="eml_ir_runtime",
            input_value=None,
            requested_output=output_node,
            safe_output=output_node,
            guard_action="ANNOTATE",
            guard_reason=reason,
            prev_hash=prev,
        )
        frames.append(frame)
        prev = frame["replay_hash"]
    return {
        "packet_id": f"{program_id}:replay_packet_v0",
        "frame_count": len(frames),
        "terminal_state": "PARKED",
        "frames": frames,
    }


def build_ir(program_id: str, expression: str) -> dict[str, Any]:
    fp = _fingerprint(expression)
    lowering = lower_expression(expression)
    nodes, output_node = _build_nodes(fp)
    return {
        "schema_version": "eml-ir.v0",
        "program_id": program_id,
        "source_expression": expression,
        "arguments": lowering["arguments"],
        "nodes": nodes,
        "output_node": output_node,
        "cost_model": "superbest_v5_3_expression_dag",
        "tree_superbest_nodes": lowering["tree_superbest_nodes"],
        "dag_superbest_nodes": lowering["dag_superbest_nodes"],
        "tree_eml_nodes": lowering["tree_eml_nodes"],
        "dag_eml_nodes": lowering["dag_eml_nodes"],
        "extra_superbest_savings_nodes": lowering["extra_superbest_savings_nodes"],
        "lowering": {
            "temporary_count": lowering["temporary_count"],
            "temporaries": lowering["temporaries"],
            "final_expr": lowering["final_expr"],
            "python_source": lowering["python_source"],
            "javascript_source": lowering["javascript_source"],
        },
        "replay_packet": _replay_packet(program_id, nodes, output_node),
        "boundaries": BOUNDARIES,
    }


def validate_ir(program: dict[str, Any]) -> None:
    if program["schema_version"] != "eml-ir.v0":
        raise ValueError("schema_version mismatch")
    node_ids = {node["id"] for node in program["nodes"]}
    if program["output_node"] not in node_ids:
        raise ValueError("output_node missing from nodes")
    for node in program["nodes"]:
        for arg in node["args"]:
            if arg not in node_ids:
                raise ValueError(f"missing arg node {arg}")
    frames = program["replay_packet"]["frames"]
    if frames[-1]["lifecycle_state"] != "PARKED":
        raise ValueError("terminal frame must be PARKED")
    prev = None
    for index, frame in enumerate(frames):
        if frame["monotonic_tick"] != index:
            raise ValueError("non-monotonic tick")
        if frame["replay_hash_prev"] != prev:
            raise ValueError("broken replay hash predecessor")
        copy = dict(frame)
        replay_hash = copy.pop("replay_hash")
        if replay_hash != _stable_hash(prev, copy):
            raise ValueError("replay hash mismatch")
        prev = replay_hash
    for key, value in BOUNDARIES.items():
        if program["boundaries"].get(key) is not value:
            raise ValueError(f"boundary mismatch: {key}")


def run_pipeline(programs: list[dict[str, str]] = EXAMPLE_PROGRAMS) -> dict[str, Any]:
    built = []
    for item in programs:
        ir = build_ir(item["program_id"], item["expression"])
        validate_ir(ir)
        built.append({**item, "ir": ir})
    best = max(built, key=lambda row: row["ir"]["extra_superbest_savings_nodes"])
    return {
        "pipeline_id": "eml_ir_substrate_pipeline_v0_2026_05_25",
        "status": "EML_IR_SUBSTRATE_PIPELINE_READY",
        "source_inventory": {
            "reused_superbest_dag_lowering": "python/scripts/superbest_dag_lowering.py",
            "reused_superbest_frontier": "python/scripts/superbest_expression_frontier.py",
            "related_research_rfc": "monogate-research/rfcs/eml_kernel_contract_v0",
            "related_replay_runtime": "monogate-research/exploration/monogate_os_replay_frame_runtime_v0_2026_05_24",
            "related_engine_eml": "monogate-engine/docs/book/src/architecture-eml.md",
        },
        "program_count": len(built),
        "best_extra_superbest_savings_program_id": best["program_id"],
        "best_extra_superbest_savings_nodes": best["ir"]["extra_superbest_savings_nodes"],
        "programs": built,
        "boundaries": BOUNDARIES,
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML IR Substrate Pipeline v0",
        "",
        "Date: 2026-05-25",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This pass does not recreate the EML substrate work from scratch. It connects existing SuperBEST DAG lowering to an explicit EML IR shape and a replay packet shape.",
        "",
        "## Existing Work Reused",
        "",
    ]
    for label, path in payload["source_inventory"].items():
        lines.append(f"- `{label}`: `{path}`")
    lines.extend(
        [
            "",
            "## Program Summary",
            "",
            "| Program | Family | Tree BEST | DAG BEST | Extra DAG Savings | Frames |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in payload["programs"]:
        ir = row["ir"]
        lines.append(
            f"| `{row['program_id']}` | {row['family']} | {ir['tree_superbest_nodes']} | "
            f"{ir['dag_superbest_nodes']} | {ir['extra_superbest_savings_nodes']} | "
            f"{ir['replay_packet']['frame_count']} |"
        )
    lines.extend(
        [
            "",
            "## What This Unlocks",
            "",
            "- A canonical JSON shape for EML expressions as inspectable DAG programs.",
            "- SuperBEST Tree vs DAG costs on the same artifact.",
            "- Replay-native frames over expression nodes.",
            "- A bridge to future browser inspector and Monogate OS packet tooling.",
            "",
            "## Boundaries",
            "",
            "- Internal prototype only.",
            "- No Forge/compiler behavior changed.",
            "- No canonical SuperBEST row table changed.",
            "- No new public theorem/proof/open-problem claim.",
            "- No package publish or deploy.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("expression", nargs="?", help="Single expression to convert to EML IR")
    parser.add_argument("--program-id", default="adhoc_program_v0")
    parser.add_argument("--out-json", type=Path, default=ROOT / "python/results/eml_ir_substrate_pipeline_v0_2026_05_25.json")
    parser.add_argument("--out-report", type=Path, default=ROOT / "reports/eml_ir_substrate_pipeline_v0_2026_05_25.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if args.expression:
        program = build_ir(args.program_id, args.expression)
        validate_ir(program)
        print(json.dumps(program, indent=2, sort_keys=True))
        return 0
    payload = run_pipeline()
    if args.strict:
        if payload["program_count"] < 10:
            raise SystemExit("strict mode requires at least 10 EML IR programs")
        if payload["best_extra_superbest_savings_nodes"] <= 0:
            raise SystemExit("strict mode requires positive DAG savings")
        if payload["boundaries"]["compiler_behavior_changed"] is not False:
            raise SystemExit("compiler behavior must not change")
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out_report.write_text(render_report(payload), encoding="utf-8")
    print("EML_IR_SUBSTRATE_PIPELINE_OK")
    print(
        "programs={program_count} best={best_extra_superbest_savings_program_id} extra={best_extra_superbest_savings_nodes}".format(
            **payload
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
