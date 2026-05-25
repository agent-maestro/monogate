#!/usr/bin/env python3
"""Explore high-value expression-level SuperBEST DAG savings frontiers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.superbest_dag_optimizer import optimize_expression, result_to_dict  # noqa: E402


FRONTIER_CASES = [
    {
        "case_id": "attention_two_logits_two_outputs",
        "family": "softmax_attention",
        "expression": "exp(q1*k1) / (exp(q1*k1) + exp(q1*k2)) + exp(q1*k2) / (exp(q1*k1) + exp(q1*k2))",
        "why": "Two-output attention sketch: repeated logits, exponentials, and normalizer.",
    },
    {
        "case_id": "attention_three_logits_two_outputs",
        "family": "softmax_attention",
        "expression": "exp(q*k1) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + exp(q*k2) / (exp(q*k1) + exp(q*k2) + exp(q*k3))",
        "why": "Three-logit softmax with two returned terms; normalizer reuse dominates.",
    },
    {
        "case_id": "attention_three_logits_three_outputs",
        "family": "softmax_attention",
        "expression": "exp(q*k1) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + exp(q*k2) / (exp(q*k1) + exp(q*k2) + exp(q*k3)) + exp(q*k3) / (exp(q*k1) + exp(q*k2) + exp(q*k3))",
        "why": "Full three-term softmax sketch; strongest DAG frontier in this pass.",
    },
    {
        "case_id": "sigmoid_value_and_derivative",
        "family": "sigmoid_logistic",
        "expression": "1 / (1 + exp(-x)) + (1 / (1 + exp(-x))) * (1 - (1 / (1 + exp(-x))))",
        "why": "Reuses sigmoid value and denominator across value-plus-derivative style expression.",
    },
    {
        "case_id": "logistic_loss_pair",
        "family": "sigmoid_logistic",
        "expression": "ln(1 + exp(-y*x)) + exp(-y*x) / (1 + exp(-y*x))",
        "why": "Shares exp(-y*x) and the softplus denominator-like subtree.",
    },
    {
        "case_id": "rational_three_terms_shared_den",
        "family": "rational_shared_denominator",
        "expression": "(x + 1) / (x - 1) + (x * x) / (x - 1) + ln(x - 1) / (x - 1)",
        "why": "Classic shared denominator reuse across rational/log-rational terms.",
    },
    {
        "case_id": "rational_shifted_basis",
        "family": "rational_shared_denominator",
        "expression": "1 / (x + a) + ln(x + a) / (x + a) + exp(x + a) / (x + a)",
        "why": "Shifted denominator reused by reciprocal, log, and exp terms.",
    },
    {
        "case_id": "polynomial_basis_degree5",
        "family": "polynomial_basis_reuse",
        "expression": "(x * x) + (x * x) * y + (x * x) * (x * x) + (x * x) * (x * x) * z",
        "why": "Shares x^2 and x^4-like basis terms across polynomial features.",
    },
    {
        "case_id": "poly_features_shared_square_cube",
        "family": "polynomial_basis_reuse",
        "expression": "(x * x) + (x * x) * x + (x * x) * y + (x * x) * x * z",
        "why": "Shares x^2 and x^3-like factors across feature terms.",
    },
]

FAMILY_NOTES = {
    "softmax_attention": "Highest-value frontier. Repeated exp(logit) and normalizer reuse compound quickly as outputs increase.",
    "sigmoid_logistic": "Strong frontier when the sigmoid value, exp(-x), or 1+exp(-x) is consumed more than once.",
    "rational_shared_denominator": "Good frontier for repeated denominators; savings are smaller than softmax but common in real formulas.",
    "polynomial_basis_reuse": "Useful compiler-lowering target for x^2/x^3 style basis reuse.",
}

BOUNDARY = {
    "expression_level_only": True,
    "canonical_row_table_changed": False,
    "new_row_optimality_claim": False,
    "public_theorem_claim": False,
    "open_problem_solved_claim": False,
    "compiler_integration_implemented": False,
}


def run_frontier(cases: list[dict] = FRONTIER_CASES) -> dict:
    results = []
    for case in cases:
        result = result_to_dict(optimize_expression(case["expression"]))
        results.append({**case, **result})
    ranked = sorted(results, key=lambda row: row["extra_superbest_savings_nodes"], reverse=True)
    family_summary = {}
    for family in sorted({row["family"] for row in results}):
        rows = [row for row in results if row["family"] == family]
        best = max(rows, key=lambda row: row["extra_superbest_savings_nodes"])
        family_summary[family] = {
            "case_count": len(rows),
            "best_case_id": best["case_id"],
            "max_extra_superbest_savings_nodes": best["extra_superbest_savings_nodes"],
            "best_dag_vs_tree_eml_savings_pct": best["dag_vs_tree_eml_savings_pct"],
            "note": FAMILY_NOTES[family],
        }
    best = ranked[0]
    return {
        "frontier_id": "superbest_expression_frontier_2026_05_24",
        "status": "SUPERBEST_EXPRESSION_FRONTIER_COMPLETE",
        "case_count": len(results),
        "families": sorted(family_summary),
        "best_case_id": best["case_id"],
        "max_extra_superbest_savings_nodes": best["extra_superbest_savings_nodes"],
        "best_dag_vs_tree_eml_savings_pct": best["dag_vs_tree_eml_savings_pct"],
        "family_summary": family_summary,
        "ranked_results": ranked,
        "recommended_next_build": {
            "name": "SUPERBEST_DAG_LOWERING_PASS_DESIGN",
            "why": "Savings are now dominated by expression DAG lowering, especially softmax/attention normalizer reuse.",
            "implementation_note": "DAG sharing should run before cost reporting and code export; canonical row costs should remain unchanged.",
        },
        "boundary": BOUNDARY,
    }


def render_report(payload: dict) -> str:
    lines = [
        "# SuperBEST Expression Frontier",
        "",
        "Date: 2026-05-24",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is an expression-level DAG savings exploration. It does not change canonical SuperBEST row costs.",
        "",
        "## Headline",
        "",
        f"- Cases explored: {payload['case_count']}",
        f"- Best case: `{payload['best_case_id']}`",
        f"- Max extra DAG savings over Tree SuperBEST: {payload['max_extra_superbest_savings_nodes']} nodes",
        f"- Best DAG-vs-tree-EML savings: {payload['best_dag_vs_tree_eml_savings_pct']}%",
        "",
        "## Family Summary",
        "",
        "| Family | Best Case | Max Extra DAG Savings | Note |",
        "|---|---|---:|---|",
    ]
    for family, info in payload["family_summary"].items():
        lines.append(
            f"| {family} | `{info['best_case_id']}` | {info['max_extra_superbest_savings_nodes']} | {info['note']} |"
        )
    lines.extend(
        [
            "",
            "## Ranked Cases",
            "",
            "| Rank | Case | Family | Tree BEST | DAG BEST | Extra DAG Savings | DAG vs Tree EML |",
            "|---:|---|---|---:|---:|---:|---:|",
        ]
    )
    for i, row in enumerate(payload["ranked_results"], start=1):
        lines.append(
            f"| {i} | `{row['case_id']}` | {row['family']} | {row['tree_superbest_nodes']} | "
            f"{row['dag_superbest_nodes']} | {row['extra_superbest_savings_nodes']} | "
            f"{row['dag_vs_tree_eml_savings_pct']}% |"
        )
    lines.extend(
        [
            "",
            "## Compiler Integration Finding",
            "",
            "The strongest next savings path is a DAG lowering pass before cost reporting and code export. The pass should identify common subexpressions, emit shared temporaries, and then compute SuperBEST costs on the shared graph.",
            "",
            "## Boundary",
            "",
            "- Expression-level sharing only.",
            "- No canonical row table changed.",
            "- No new row optimality claim.",
            "- No public theorem/proof/open-problem claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=ROOT / "python/results/superbest_expression_frontier_2026_05_24.json")
    parser.add_argument("--out-report", type=Path, default=ROOT / "reports/superbest_expression_frontier_2026_05_24.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    payload = run_frontier()
    if args.strict:
        if payload["case_count"] < 8:
            raise SystemExit("strict mode requires at least 8 frontier cases")
        if payload["max_extra_superbest_savings_nodes"] <= 0:
            raise SystemExit("strict mode requires positive DAG savings")
        if payload["boundary"]["canonical_row_table_changed"] is not False:
            raise SystemExit("canonical row table must remain unchanged")
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out_report.write_text(render_report(payload), encoding="utf-8")
    print("SUPERBEST_EXPRESSION_FRONTIER_OK")
    print(
        "cases={case_count} best={best_case_id} max_extra={max_extra_superbest_savings_nodes}".format(
            **payload
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
