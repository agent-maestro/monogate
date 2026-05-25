#!/usr/bin/env python3
"""Lower expressions into SuperBEST DAG temporaries before cost reporting.

This is a small compiler-style prototype: parse an expression, identify repeated
subexpressions, emit dependency-ordered temporaries, and report Tree SuperBEST
vs DAG SuperBEST costs. It remains expression-level only and does not change
canonical SuperBEST row costs.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts import superbest_dag_savings_audit as audit  # noqa: E402
from scripts.superbest_dag_optimizer import (  # noqa: E402
    _emit_expr,
    _shared_nodes,
    _subtree_size,
    _vars,
    optimize_expression,
)
from scripts.superbest_expression_frontier import FRONTIER_CASES  # noqa: E402


BOUNDARY = {
    "expression_level_only": True,
    "canonical_row_table_changed": False,
    "new_row_optimality_claim": False,
    "public_theorem_claim": False,
    "open_problem_solved_claim": False,
    "package_publish_performed": False,
    "compiler_integration_prototype": True,
}


def _fingerprint(expression: str) -> tuple:
    return audit._fingerprint(ast.parse(expression, mode="eval"))


def _source_for_temp(fp: tuple, temp_by_fp: dict[tuple, str]) -> str:
    return _emit_expr(fp, temp_by_fp, current=fp)


def _ordered_temporaries(expression: str) -> list[dict]:
    fp = _fingerprint(expression)
    shared = _shared_nodes(fp)
    temp_by_fp = {node.fingerprint: node.temp for node in shared}
    emit_order = sorted(shared, key=lambda node: (_subtree_size(node.fingerprint), node.temp))
    return [
        {
            "temp": node.temp,
            "op": node.op,
            "reuse_count": node.count,
            "source": _source_for_temp(node.fingerprint, temp_by_fp),
            "superbest_cost": node.superbest_cost,
            "eml_cost": node.eml_cost,
            "subtree_size": _subtree_size(node.fingerprint),
        }
        for node in emit_order
    ]


def lower_expression(expression: str) -> dict:
    fp = _fingerprint(expression)
    result = optimize_expression(expression)
    temporaries = _ordered_temporaries(expression)
    temp_by_fp = {node.fingerprint: node.temp for node in _shared_nodes(fp)}
    final_expr = _emit_expr(fp, temp_by_fp)
    args = list(_vars(fp))
    return {
        "expression": expression,
        "arguments": args,
        "temporary_count": len(temporaries),
        "temporaries": temporaries,
        "final_expr": final_expr,
        "tree_superbest_nodes": result.tree_superbest_nodes,
        "dag_superbest_nodes": result.dag_superbest_nodes,
        "tree_eml_nodes": result.tree_eml_nodes,
        "dag_eml_nodes": result.dag_eml_nodes,
        "extra_superbest_savings_nodes": result.extra_superbest_savings_nodes,
        "dag_vs_tree_eml_savings_pct": result.dag_vs_tree_eml_savings_pct,
        "python_source": render_python(args, temporaries, final_expr),
        "javascript_source": render_javascript(args, temporaries, final_expr),
        "boundary": BOUNDARY,
    }


def render_python(args: list[str], temporaries: list[dict], final_expr: str) -> str:
    arg_src = ", ".join(args) or "x"
    lines = [
        "from monogate import BEST",
        "",
        f"def lowered_expr({arg_src}):",
        '    """SuperBEST DAG-lowered expression; shared temporaries first."""',
    ]
    for temp in temporaries:
        lines.append(f"    {temp['temp']} = {temp['source']}")
    lines.append(f"    return {final_expr}")
    return "\n".join(lines)


def _js_expr(expr: str) -> str:
    return (
        expr.replace("BEST.exp", "Math.exp")
        .replace("BEST.ln", "Math.log")
        .replace("BEST.neg", "BEST.neg")
        .replace("BEST.div", "BEST.div")
        .replace("BEST.pow", "Math.pow")
        .replace("BEST.sqrt", "Math.sqrt")
        .replace("BEST.sin", "Math.sin")
        .replace("BEST.cos", "Math.cos")
        .replace("BEST.tanh", "Math.tanh")
    )


def render_javascript(args: list[str], temporaries: list[dict], final_expr: str) -> str:
    arg_src = ", ".join(args) or "x"
    lines = [
        f"function loweredExpr({arg_src}) {{",
        "  const BEST = {",
        "    div: (x, y) => x / y,",
        "    neg: x => -x,",
        "  };",
    ]
    for temp in temporaries:
        lines.append(f"  const {temp['temp']} = {_js_expr(temp['source'])};")
    lines.append(f"  return {_js_expr(final_expr)};")
    lines.append("}")
    return "\n".join(lines)


def run_lowering(cases: list[dict] = FRONTIER_CASES) -> dict:
    lowered = []
    for case in cases:
        lowered.append({**case, **lower_expression(case["expression"])})
    ranked = sorted(lowered, key=lambda row: row["extra_superbest_savings_nodes"], reverse=True)
    best = ranked[0]
    return {
        "lowering_id": "superbest_dag_lowering_pass_2026_05_24",
        "status": "SUPERBEST_DAG_LOWERING_PASS_READY",
        "case_count": len(lowered),
        "best_case_id": best["case_id"],
        "max_extra_superbest_savings_nodes": best["extra_superbest_savings_nodes"],
        "ranked_results": ranked,
        "lowering_contract": {
            "parse_expression": True,
            "detect_repeated_subexpressions": True,
            "emit_dependency_ordered_temporaries": True,
            "report_tree_and_dag_costs": True,
            "export_python_source": True,
            "export_javascript_source": True,
            "canonical_row_table_changed": False,
        },
        "boundary": BOUNDARY,
    }


def render_report(payload: dict) -> str:
    lines = [
        "# SuperBEST DAG Lowering Pass",
        "",
        "Date: 2026-05-24",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is the first compiler-style lowering pass for expression-level SuperBEST DAG sharing. It emits dependency-ordered temporaries before reporting DAG costs or exporting code.",
        "",
        "## Summary",
        "",
        f"- Cases lowered: {payload['case_count']}",
        f"- Best case: `{payload['best_case_id']}`",
        f"- Max extra SuperBEST DAG savings: {payload['max_extra_superbest_savings_nodes']} nodes",
        "",
        "## Ranked Lowerings",
        "",
        "| Rank | Case | Temps | Tree BEST | DAG BEST | Extra DAG Savings |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for i, row in enumerate(payload["ranked_results"], start=1):
        lines.append(
            f"| {i} | `{row['case_id']}` | {row['temporary_count']} | "
            f"{row['tree_superbest_nodes']} | {row['dag_superbest_nodes']} | "
            f"{row['extra_superbest_savings_nodes']} |"
        )
    best = payload["ranked_results"][0]
    lines.extend(
        [
            "",
            "## Best Lowered Python Sketch",
            "",
            "```python",
            best["python_source"],
            "```",
            "",
            "## Boundary",
            "",
            "- Expression-level lowering only.",
            "- No canonical row costs changed.",
            "- No new row optimality claim.",
            "- No package publish or deploy.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("expression", nargs="?", help="Single expression to lower")
    parser.add_argument("--out-json", type=Path, default=ROOT / "python/results/superbest_dag_lowering_pass_2026_05_24.json")
    parser.add_argument("--out-report", type=Path, default=ROOT / "reports/superbest_dag_lowering_pass_2026_05_24.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if args.expression:
        print(json.dumps(lower_expression(args.expression), indent=2, sort_keys=True))
        return 0
    payload = run_lowering()
    if args.strict:
        if payload["case_count"] < 8:
            raise SystemExit("strict mode requires at least 8 lowered cases")
        if payload["max_extra_superbest_savings_nodes"] <= 0:
            raise SystemExit("strict mode requires positive DAG savings")
        if payload["boundary"]["canonical_row_table_changed"] is not False:
            raise SystemExit("canonical row table must remain unchanged")
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out_report.write_text(render_report(payload), encoding="utf-8")
    print("SUPERBEST_DAG_LOWERING_PASS_OK")
    print(
        "cases={case_count} best={best_case_id} max_extra={max_extra_superbest_savings_nodes}".format(
            **payload
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
