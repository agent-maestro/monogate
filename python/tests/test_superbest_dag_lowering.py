"""Tests for the compiler-style SuperBEST DAG lowering pass."""

from __future__ import annotations

import json
import subprocess
import sys

from scripts.superbest_dag_lowering import lower_expression, run_lowering


def test_lowering_emits_dependency_ordered_temps():
    lowered = lower_expression("(exp(x) + ln(x)) * (exp(x) + ln(x))")
    temps = lowered["temporaries"]
    assert [temp["temp"] for temp in temps] == ["_t1", "_t2", "_t0"]
    assert temps[0]["source"] == "BEST.exp(x)"
    assert temps[1]["source"] == "BEST.ln(x)"
    assert temps[2]["source"] == "(_t1 + _t2)"
    assert lowered["final_expr"] == "(_t0 * _t0)"


def test_lowering_reports_tree_and_dag_costs():
    lowered = lower_expression("exp(x) + exp(x)")
    assert lowered["tree_superbest_nodes"] == 4
    assert lowered["dag_superbest_nodes"] == 3
    assert lowered["extra_superbest_savings_nodes"] == 1


def test_lowering_exports_python_and_javascript():
    lowered = lower_expression("exp(x) + exp(x)")
    assert "def lowered_expr(x):" in lowered["python_source"]
    assert "_t0 = BEST.exp(x)" in lowered["python_source"]
    assert "function loweredExpr(x)" in lowered["javascript_source"]
    assert "const _t0 = Math.exp(x);" in lowered["javascript_source"]


def test_lowering_frontier_best_case_matches_expression_frontier():
    payload = run_lowering()
    assert payload["status"] == "SUPERBEST_DAG_LOWERING_PASS_READY"
    assert payload["best_case_id"] == "attention_three_logits_three_outputs"
    assert payload["max_extra_superbest_savings_nodes"] == 26
    assert payload["lowering_contract"]["emit_dependency_ordered_temporaries"] is True


def test_lowering_preserves_boundaries():
    payload = run_lowering()
    assert payload["boundary"]["expression_level_only"] is True
    assert payload["boundary"]["canonical_row_table_changed"] is False
    assert payload["boundary"]["new_row_optimality_claim"] is False
    assert payload["boundary"]["package_publish_performed"] is False


def test_lowering_cli_outputs_single_expression_json():
    proc = subprocess.run(
        [sys.executable, "python/scripts/superbest_dag_lowering.py", "exp(x) + exp(x)"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["temporary_count"] == 1
    assert payload["final_expr"] == "(_t0 + _t0)"
