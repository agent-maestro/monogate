"""Tests for the SuperBEST DAG optimizer prototype."""

from __future__ import annotations

import json
import subprocess
import sys

from scripts import superbest_dag_savings_audit as audit
from scripts.superbest_dag_optimizer import optimize_expression, run_cases


def test_optimizer_emits_shared_exp_temporary():
    result = optimize_expression("exp(x) + exp(x)")
    assert result.tree_superbest_nodes == 4
    assert result.dag_superbest_nodes == 3
    assert result.extra_superbest_savings_nodes == 1
    assert result.shared_nodes[0].op == "exp"
    assert "_t0 = BEST.exp(x)" in result.python_snippet
    assert "return (_t0 + _t0)" in result.python_snippet


def test_optimizer_prefers_full_repeated_subtree():
    result = optimize_expression("(exp(x) + ln(x)) * (exp(x) + ln(x))")
    assert result.tree_superbest_nodes == 9
    assert result.dag_superbest_nodes == 5
    assert result.extra_superbest_savings_nodes == 4
    assert result.shared_nodes[0].op == "add"
    assert "return (_t0 * _t0)" in result.python_snippet


def test_optimizer_signature_includes_all_variables():
    result = optimize_expression("exp(a) / (exp(a) + exp(b) + exp(c))")
    assert "def optimized_expr(a, b, c):" in result.python_snippet


def test_run_cases_preserves_boundary_flags():
    payload = run_cases(audit.DEFAULT_CASES)
    assert payload["case_count"] == len(audit.DEFAULT_CASES)
    assert payload["max_extra_superbest_savings_nodes"] == 9
    assert payload["boundary"]["expression_level_only"] is True
    assert payload["boundary"]["canonical_row_table_changed"] is False
    assert payload["boundary"]["new_row_optimality_claim"] is False
    assert payload["boundary"]["public_theorem_claim"] is False
    assert payload["boundary"]["open_problem_solved_claim"] is False


def test_optimizer_cli_single_expression_outputs_json():
    proc = subprocess.run(
        [sys.executable, "python/scripts/superbest_dag_optimizer.py", "exp(x) + exp(x)"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["extra_superbest_savings_nodes"] == 1
    assert payload["boundary"]["canonical_row_table_changed"] is False
