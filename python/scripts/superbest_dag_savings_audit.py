#!/usr/bin/env python3
"""Audit expression-level SuperBEST savings from DAG/common-subexpression reuse.

This intentionally does not change row-level SuperBEST costs. It asks a
different question: once an expression is a DAG rather than a tree, how many
operator nodes can be shared?
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from monogate import superbest  # noqa: E402


OP_ALIASES = {
    "log": "ln",
    "math.log": "ln",
    "np.log": "ln",
    "numpy.log": "ln",
    "torch.log": "ln",
    "math.exp": "exp",
    "np.exp": "exp",
    "numpy.exp": "exp",
    "torch.exp": "exp",
    "math.sqrt": "sqrt",
    "np.sqrt": "sqrt",
    "numpy.sqrt": "sqrt",
    "torch.sqrt": "sqrt",
    "math.sin": "sin",
    "np.sin": "sin",
    "numpy.sin": "sin",
    "torch.sin": "sin",
    "math.cos": "cos",
    "np.cos": "cos",
    "numpy.cos": "cos",
    "torch.cos": "cos",
}

POSITIVE_COSTS = dict(superbest.SUPERBEST_COSTS_POS)
EML_COSTS = dict(superbest.NAIVE_COSTS)


DEFAULT_CASES = [
    {
        "case_id": "repeat_exp_pair",
        "family": "repeated_exp",
        "expression": "exp(x) + exp(x)",
        "notes": "Smallest useful CSE example: one exp node reused.",
    },
    {
        "case_id": "shared_exp_ln_square",
        "family": "shared_subexpression",
        "expression": "(exp(x) + ln(x)) * (exp(x) + ln(x))",
        "notes": "Full inner add subtree is shared in the DAG view.",
    },
    {
        "case_id": "sigmoid_reuse",
        "family": "activation",
        "expression": "1 / (1 + exp(-x)) + exp(-x) / (1 + exp(-x))",
        "notes": "Shares exp(-x) and the denominator across two rational terms.",
    },
    {
        "case_id": "softmax_three_terms",
        "family": "softmax",
        "expression": "exp(a) / (exp(a) + exp(b) + exp(c)) + exp(b) / (exp(a) + exp(b) + exp(c))",
        "notes": "Shares exp terms and the normalizer across two softmax outputs.",
    },
    {
        "case_id": "rational_repeated_denominator",
        "family": "rational",
        "expression": "(x + 1) / (x - 1) + (x * x) / (x - 1)",
        "notes": "Shares denominator and one variable product-like subtree.",
    },
    {
        "case_id": "polynomial_repeated_square",
        "family": "polynomial",
        "expression": "(x * x) + (x * x) * y + (x * x) * z",
        "notes": "Shares x*x across three polynomial terms.",
    },
    {
        "case_id": "gelu_inner_sketch",
        "family": "activation",
        "expression": "x * (1 + tanh(k * (x + c * (x ** 3))))",
        "notes": "Internal GELU-like sketch; tanh remains an approximation/demo row.",
    },
    {
        "case_id": "log_ratio_shared_shift",
        "family": "log_rational",
        "expression": "ln(x + 1) / (x + 1) + 1 / (x + 1)",
        "notes": "Shares x+1 across log argument and denominators.",
    },
]


class UnsupportedExpression(ValueError):
    pass


@dataclass(frozen=True)
class AuditMetrics:
    tree_superbest_nodes: int
    dag_superbest_nodes: int
    tree_eml_nodes: int
    dag_eml_nodes: int
    repeated_subexpression_count: int
    repeated_subexpressions: tuple[dict, ...]

    @property
    def superbest_dag_delta(self) -> int:
        return self.tree_superbest_nodes - self.dag_superbest_nodes

    @property
    def eml_dag_delta(self) -> int:
        return self.tree_eml_nodes - self.dag_eml_nodes

    @property
    def dag_superbest_vs_tree_eml_delta(self) -> int:
        return self.tree_eml_nodes - self.dag_superbest_nodes

    @property
    def dag_superbest_vs_tree_eml_savings_pct(self) -> float:
        if self.tree_eml_nodes <= 0:
            return 0.0
        return round(self.dag_superbest_vs_tree_eml_delta / self.tree_eml_nodes * 100, 1)


def _name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_name(node.value)}.{node.attr}"
    raise UnsupportedExpression(f"unsupported function node: {ast.dump(node)}")


def _op_for_call(node: ast.Call) -> str:
    name = _name(node.func)
    return OP_ALIASES.get(name, name)


def _const_repr(node: ast.Constant) -> str:
    return repr(node.value)


def _fingerprint(node: ast.AST) -> tuple:
    if isinstance(node, ast.Expression):
        return _fingerprint(node.body)
    if isinstance(node, ast.Name):
        return ("var", node.id)
    if isinstance(node, ast.Constant):
        return ("const", _const_repr(node))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return ("op", "neg", (_fingerprint(node.operand),))
    if isinstance(node, ast.Call):
        op = _op_for_call(node)
        args = tuple(_fingerprint(arg) for arg in node.args)
        if op not in POSITIVE_COSTS and op not in EML_COSTS and op != "tanh":
            raise UnsupportedExpression(f"unsupported call op: {op}")
        return ("op", op, args)
    if isinstance(node, ast.BinOp):
        op = _binop_name(node.op)
        left = _fingerprint(node.left)
        right = _fingerprint(node.right)
        if op in {"add", "mul"}:
            left, right = sorted((left, right), key=repr)
        return ("op", op, (left, right))
    raise UnsupportedExpression(f"unsupported expression: {ast.dump(node)}")


def _binop_name(op: ast.operator) -> str:
    if isinstance(op, ast.Add):
        return "add"
    if isinstance(op, ast.Sub):
        return "sub"
    if isinstance(op, ast.Mult):
        return "mul"
    if isinstance(op, ast.Div):
        return "div"
    if isinstance(op, ast.Pow):
        return "pow"
    raise UnsupportedExpression(f"unsupported binary op: {op.__class__.__name__}")


def _op_name(fp: tuple) -> str | None:
    return fp[1] if fp and fp[0] == "op" else None


def _cost(op: str, table: dict[str, int]) -> int:
    if op == "tanh":
        # Internal demo approximation sketch: tanh as exp/mul/sub/add/div basket.
        return table.get("mul", 1) + table.get("exp", 1) + table.get("sub", 2) + table.get("add", 2) + table.get("div", 2)
    if op not in table:
        raise UnsupportedExpression(f"missing cost for op: {op}")
    return table[op]


def _walk_fingerprints(fp: tuple) -> Iterable[tuple]:
    yield fp
    if fp and fp[0] == "op":
        for child in fp[2]:
            yield from _walk_fingerprints(child)


def _tree_cost(fp: tuple, table: dict[str, int]) -> int:
    total = 0
    for node_fp in _walk_fingerprints(fp):
        op = _op_name(node_fp)
        if op:
            total += _cost(op, table)
    return total


def _dag_cost(fp: tuple, table: dict[str, int]) -> int:
    seen: set[tuple] = set()
    total = 0
    for node_fp in _walk_fingerprints(fp):
        op = _op_name(node_fp)
        if not op or node_fp in seen:
            continue
        seen.add(node_fp)
        total += _cost(op, table)
    return total


def audit_expression(expression: str) -> AuditMetrics:
    parsed = ast.parse(expression, mode="eval")
    fp = _fingerprint(parsed)
    counts: dict[tuple, int] = {}
    for node_fp in _walk_fingerprints(fp):
        if _op_name(node_fp):
            counts[node_fp] = counts.get(node_fp, 0) + 1

    repeated = []
    for node_fp, count in counts.items():
        if count <= 1:
            continue
        op = _op_name(node_fp)
        repeated.append(
            {
                "op": op,
                "count": count,
                "fingerprint": repr(node_fp),
                "superbest_saved_nodes": (count - 1) * _cost(op, POSITIVE_COSTS),
                "eml_saved_nodes": (count - 1) * _cost(op, EML_COSTS),
            }
        )
    repeated.sort(key=lambda item: (-item["superbest_saved_nodes"], item["op"], item["fingerprint"]))

    return AuditMetrics(
        tree_superbest_nodes=_tree_cost(fp, POSITIVE_COSTS),
        dag_superbest_nodes=_dag_cost(fp, POSITIVE_COSTS),
        tree_eml_nodes=_tree_cost(fp, EML_COSTS),
        dag_eml_nodes=_dag_cost(fp, EML_COSTS),
        repeated_subexpression_count=len(repeated),
        repeated_subexpressions=tuple(repeated),
    )


def run_audit(cases: list[dict]) -> dict:
    results = []
    for case in cases:
        metrics = audit_expression(case["expression"])
        results.append(
            {
                **case,
                "tree_superbest_nodes": metrics.tree_superbest_nodes,
                "dag_superbest_nodes": metrics.dag_superbest_nodes,
                "tree_eml_nodes": metrics.tree_eml_nodes,
                "dag_eml_nodes": metrics.dag_eml_nodes,
                "superbest_dag_delta": metrics.superbest_dag_delta,
                "eml_dag_delta": metrics.eml_dag_delta,
                "dag_superbest_vs_tree_eml_delta": metrics.dag_superbest_vs_tree_eml_delta,
                "dag_superbest_vs_tree_eml_savings_pct": metrics.dag_superbest_vs_tree_eml_savings_pct,
                "repeated_subexpression_count": metrics.repeated_subexpression_count,
                "repeated_subexpressions": list(metrics.repeated_subexpressions),
                "claim_boundary": "expression_level_dag_savings_not_row_level_cost_change",
            }
        )

    max_extra = max((r["superbest_dag_delta"] for r in results), default=0)
    avg_extra = round(sum(r["superbest_dag_delta"] for r in results) / len(results), 2) if results else 0.0
    best_case = max(results, key=lambda r: r["superbest_dag_delta"], default=None)
    return {
        "audit_id": "superbest_dag_savings_audit_2026_05_24",
        "status": "SUPERBEST_DAG_SAVINGS_AUDIT_COMPLETE",
        "canonical_row_table_changed": False,
        "new_row_optimality_claim": False,
        "public_theorem_claim": False,
        "open_problem_solved_claim": False,
        "case_count": len(results),
        "max_extra_superbest_dag_savings_nodes": max_extra,
        "average_extra_superbest_dag_savings_nodes": avg_extra,
        "best_case_id": best_case["case_id"] if best_case else None,
        "results": results,
        "recommended_next_action": "Prototype a DAG-aware optimizer pass for repeated subexpressions and label browser snippets as expression-level sketches.",
    }


def render_report(audit: dict) -> str:
    lines = [
        "# SuperBEST DAG Savings Audit",
        "",
        "Date: 2026-05-24",
        "",
        f"Status: `{audit['status']}`",
        "",
        "This audit looks for expression-level savings from common-subexpression sharing. It does not change the canonical row-level SuperBEST table.",
        "",
        "## Summary",
        "",
        f"- Cases audited: {audit['case_count']}",
        f"- Max extra SuperBEST DAG savings: {audit['max_extra_superbest_dag_savings_nodes']} nodes",
        f"- Average extra SuperBEST DAG savings: {audit['average_extra_superbest_dag_savings_nodes']} nodes",
        f"- Best case: `{audit['best_case_id']}`",
        "",
        "## Results",
        "",
        "| Case | Family | Tree BEST | DAG BEST | Extra DAG Savings | Tree EML | DAG BEST vs Tree EML |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in audit["results"]:
        lines.append(
            "| {case_id} | {family} | {tree_superbest_nodes} | {dag_superbest_nodes} | "
            "{superbest_dag_delta} | {tree_eml_nodes} | {dag_superbest_vs_tree_eml_savings_pct}% |".format(**result)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The next practical savings likely come from DAG-aware expression optimization, not from changing the saturated row table. Repeated denominators, repeated `exp` terms, and reused polynomial powers are the cleanest targets.",
            "",
            "## Boundaries",
            "",
            "- No canonical row cost changed.",
            "- No new row optimality claim is made.",
            "- No public theorem/proof/open-problem claim is made.",
            "- `sin`, `cos`, and activation sketches remain internal/demo rows unless separately reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, help="Optional JSON file containing a list of audit cases")
    parser.add_argument("--out-json", type=Path, default=ROOT / "python/results/superbest_dag_savings_audit_2026_05_24.json")
    parser.add_argument("--out-report", type=Path, default=ROOT / "reports/superbest_dag_savings_audit_2026_05_24.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    cases = json.loads(args.cases.read_text(encoding="utf-8")) if args.cases else DEFAULT_CASES
    audit = run_audit(cases)
    if args.strict and audit["case_count"] < 5:
        raise SystemExit("strict mode requires at least 5 audit cases")

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.out_report.write_text(render_report(audit), encoding="utf-8")
    print("SUPERBEST_DAG_SAVINGS_AUDIT_OK")
    print(f"cases={audit['case_count']} max_extra={audit['max_extra_superbest_dag_savings_nodes']} best={audit['best_case_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
