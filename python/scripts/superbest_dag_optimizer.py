#!/usr/bin/env python3
"""Prototype DAG-aware SuperBEST optimizer.

This emits shared temporaries for repeated subexpressions. It is an
expression-level prototype only: it does not change canonical SuperBEST row
costs or claim new row optimality.
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts import superbest_dag_savings_audit as audit  # noqa: E402


@dataclass(frozen=True)
class SharedNode:
    fingerprint: tuple
    op: str
    count: int
    temp: str
    superbest_cost: int
    eml_cost: int


@dataclass(frozen=True)
class DagOptimizeResult:
    expression: str
    tree_superbest_nodes: int
    dag_superbest_nodes: int
    tree_eml_nodes: int
    dag_eml_nodes: int
    shared_nodes: tuple[SharedNode, ...]
    python_snippet: str
    boundary: dict

    @property
    def extra_superbest_savings_nodes(self) -> int:
        return self.tree_superbest_nodes - self.dag_superbest_nodes

    @property
    def dag_vs_tree_eml_savings_pct(self) -> float:
        if self.tree_eml_nodes <= 0:
            return 0.0
        return round((self.tree_eml_nodes - self.dag_superbest_nodes) / self.tree_eml_nodes * 100, 1)


def _subtree_size(fp: tuple) -> int:
    return sum(1 for _ in audit._walk_fingerprints(fp))


def _count_fingerprints(fp: tuple) -> dict[tuple, int]:
    counts: dict[tuple, int] = {}
    for node_fp in audit._walk_fingerprints(fp):
        if audit._op_name(node_fp):
            counts[node_fp] = counts.get(node_fp, 0) + 1
    return counts


def _shared_nodes(fp: tuple) -> tuple[SharedNode, ...]:
    nodes = []
    for node_fp, count in _count_fingerprints(fp).items():
        op = audit._op_name(node_fp)
        if not op or count <= 1:
            continue
        nodes.append(
            SharedNode(
                fingerprint=node_fp,
                op=op,
                count=count,
                temp=f"_t{len(nodes)}",
                superbest_cost=audit._cost(op, audit.POSITIVE_COSTS),
                eml_cost=audit._cost(op, audit.EML_COSTS),
            )
        )
    nodes.sort(
        key=lambda node: (
            -_subtree_size(node.fingerprint),
            -((node.count - 1) * node.superbest_cost),
            node.op,
            repr(node.fingerprint),
        )
    )
    return tuple(
        SharedNode(
            fingerprint=node.fingerprint,
            op=node.op,
            count=node.count,
            temp=f"_t{i}",
            superbest_cost=node.superbest_cost,
            eml_cost=node.eml_cost,
        )
        for i, node in enumerate(nodes)
    )


def _vars(fp: tuple) -> tuple[str, ...]:
    names = {node_fp[1] for node_fp in audit._walk_fingerprints(fp) if node_fp and node_fp[0] == "var"}
    return tuple(sorted(names))


def _is_leaf(fp: tuple) -> bool:
    return fp[0] in {"var", "const"}


def _leaf_source(fp: tuple) -> str:
    if fp[0] == "var":
        return fp[1]
    if fp[0] == "const":
        return fp[1]
    raise ValueError(f"not a leaf: {fp!r}")


def _emit_expr(fp: tuple, temp_by_fp: dict[tuple, str], current: tuple | None = None) -> str:
    if fp in temp_by_fp and fp != current:
        return temp_by_fp[fp]
    if _is_leaf(fp):
        return _leaf_source(fp)
    op = audit._op_name(fp)
    children = fp[2]
    args = [_emit_expr(child, temp_by_fp, current=current) for child in children]
    if op in {"neg", "exp", "ln", "sqrt", "sin", "cos", "tanh"}:
        return f"BEST.{op}({args[0]})"
    if op == "add":
        return f"({args[0]} + {args[1]})"
    if op == "sub":
        return f"({args[0]} - {args[1]})"
    if op == "mul":
        return f"({args[0]} * {args[1]})"
    if op == "div":
        return f"BEST.div({args[0]}, {args[1]})"
    if op == "pow":
        return f"BEST.pow({args[0]}, {args[1]})"
    raise ValueError(f"unsupported op: {op}")


def _snippet(fp: tuple, shared: tuple[SharedNode, ...]) -> str:
    temp_by_fp = {node.fingerprint: node.temp for node in shared}
    emit_order = sorted(shared, key=lambda node: (_subtree_size(node.fingerprint), node.temp))
    args = ", ".join(_vars(fp)) or "x"
    lines = [
        "from monogate import BEST",
        "",
        f"def optimized_expr({args}):",
        '    """DAG-aware SuperBEST sketch; expression-level sharing only."""',
    ]
    for node in emit_order:
        expr = _emit_expr(node.fingerprint, temp_by_fp, current=node.fingerprint)
        lines.append(f"    {node.temp} = {expr}  # shared {node.op}, reused {node.count}x")
    result = _emit_expr(fp, temp_by_fp)
    lines.append(f"    return {result}")
    return "\n".join(lines)


def optimize_expression(expression: str) -> DagOptimizeResult:
    parsed = ast.parse(expression, mode="eval")
    fp = audit._fingerprint(parsed)
    metrics = audit.audit_expression(expression)
    shared = _shared_nodes(fp)
    return DagOptimizeResult(
        expression=expression,
        tree_superbest_nodes=metrics.tree_superbest_nodes,
        dag_superbest_nodes=metrics.dag_superbest_nodes,
        tree_eml_nodes=metrics.tree_eml_nodes,
        dag_eml_nodes=metrics.dag_eml_nodes,
        shared_nodes=shared,
        python_snippet=_snippet(fp, shared),
        boundary={
            "expression_level_only": True,
            "canonical_row_table_changed": False,
            "new_row_optimality_claim": False,
            "public_theorem_claim": False,
            "open_problem_solved_claim": False,
        },
    )


def result_to_dict(result: DagOptimizeResult) -> dict:
    return {
        "expression": result.expression,
        "tree_superbest_nodes": result.tree_superbest_nodes,
        "dag_superbest_nodes": result.dag_superbest_nodes,
        "tree_eml_nodes": result.tree_eml_nodes,
        "dag_eml_nodes": result.dag_eml_nodes,
        "extra_superbest_savings_nodes": result.extra_superbest_savings_nodes,
        "dag_vs_tree_eml_savings_pct": result.dag_vs_tree_eml_savings_pct,
        "shared_nodes": [
            {
                "temp": node.temp,
                "op": node.op,
                "count": node.count,
                "superbest_cost": node.superbest_cost,
                "eml_cost": node.eml_cost,
                "fingerprint": repr(node.fingerprint),
            }
            for node in result.shared_nodes
        ],
        "python_snippet": result.python_snippet,
        "boundary": result.boundary,
    }


def run_cases(cases: list[dict]) -> dict:
    results = []
    for case in cases:
        result = optimize_expression(case["expression"])
        results.append({**case, **result_to_dict(result)})
    best = max(results, key=lambda item: item["extra_superbest_savings_nodes"], default=None)
    return {
        "optimizer_id": "superbest_dag_optimizer_prototype_2026_05_24",
        "status": "SUPERBEST_DAG_OPTIMIZER_PROTOTYPE_READY",
        "case_count": len(results),
        "best_case_id": best["case_id"] if best else None,
        "max_extra_superbest_savings_nodes": best["extra_superbest_savings_nodes"] if best else 0,
        "results": results,
        "boundary": {
            "expression_level_only": True,
            "canonical_row_table_changed": False,
            "new_row_optimality_claim": False,
            "public_theorem_claim": False,
            "open_problem_solved_claim": False,
        },
    }


def render_report(payload: dict) -> str:
    lines = [
        "# SuperBEST DAG Optimizer Prototype",
        "",
        "Date: 2026-05-24",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This prototype emits shared temporaries for repeated subexpressions. It is an expression-level optimizer sketch, not a row-level SuperBEST table change.",
        "",
        "## Summary",
        "",
        f"- Cases optimized: {payload['case_count']}",
        f"- Best case: `{payload['best_case_id']}`",
        f"- Max extra SuperBEST DAG savings: {payload['max_extra_superbest_savings_nodes']} nodes",
        "",
        "## Cases",
        "",
        "| Case | Tree BEST | DAG BEST | Extra DAG Savings | Shared Nodes |",
        "|---|---:|---:|---:|---:|",
    ]
    for result in payload["results"]:
        lines.append(
            "| {case_id} | {tree_superbest_nodes} | {dag_superbest_nodes} | "
            "{extra_superbest_savings_nodes} | {shared_count} |".format(
                shared_count=len(result["shared_nodes"]),
                **result,
            )
        )
    if payload["results"]:
        lines.extend(
            [
                "",
                "## Example Snippet",
                "",
                "```python",
                payload["results"][0]["python_snippet"],
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Expression-level sharing only.",
            "- No canonical row costs changed.",
            "- No new row optimality claim.",
            "- No public theorem/proof/open-problem claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("expression", nargs="?", help="Single expression to optimize")
    parser.add_argument("--cases", type=Path, help="Optional JSON list of cases")
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "python/results/superbest_dag_optimizer_2026_05_24.json",
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=ROOT / "reports/superbest_dag_optimizer_2026_05_24.md",
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.expression:
        payload = result_to_dict(optimize_expression(args.expression))
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    cases = json.loads(args.cases.read_text(encoding="utf-8")) if args.cases else audit.DEFAULT_CASES
    payload = run_cases(cases)
    if args.strict and payload["case_count"] < 5:
        raise SystemExit("strict mode requires at least 5 cases")
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.out_report.write_text(render_report(payload), encoding="utf-8")
    print("SUPERBEST_DAG_OPTIMIZER_OK")
    print(
        "cases={case_count} max_extra={max_extra_superbest_savings_nodes} best={best_case_id}".format(
            **payload
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
