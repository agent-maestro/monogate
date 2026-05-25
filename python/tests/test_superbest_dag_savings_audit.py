"""Tests for expression-level SuperBEST DAG savings audit."""

from __future__ import annotations

from monogate import superbest
from scripts.superbest_dag_savings_audit import audit_expression, run_audit


def test_repeated_exp_pair_saves_one_exp_node():
    metrics = audit_expression("exp(x) + exp(x)")
    assert metrics.tree_superbest_nodes == 4  # exp + exp + add
    assert metrics.dag_superbest_nodes == 3   # shared exp + add
    assert metrics.superbest_dag_delta == 1


def test_shared_inner_add_subtree_is_counted_once():
    metrics = audit_expression("(exp(x) + ln(x)) * (exp(x) + ln(x))")
    assert metrics.tree_superbest_nodes == 9
    assert metrics.dag_superbest_nodes == 5
    assert metrics.superbest_dag_delta == 4
    assert metrics.repeated_subexpression_count >= 3


def test_commutative_fingerprint_shares_reordered_add():
    metrics = audit_expression("(x + 1) * (1 + x)")
    assert metrics.tree_superbest_nodes == 5
    assert metrics.dag_superbest_nodes == 3
    assert metrics.superbest_dag_delta == 2


def test_noncommutative_subtraction_not_shared_when_reordered():
    metrics = audit_expression("(x - 1) + (1 - x)")
    assert metrics.tree_superbest_nodes == 6
    assert metrics.dag_superbest_nodes == 6
    assert metrics.superbest_dag_delta == 0


def test_softmax_style_expression_has_positive_dag_savings():
    metrics = audit_expression("exp(a) / (exp(a) + exp(b)) + exp(b) / (exp(a) + exp(b))")
    assert metrics.superbest_dag_delta > 0
    assert metrics.dag_superbest_vs_tree_eml_savings_pct > 0


def test_audit_does_not_change_canonical_row_table():
    before = dict(superbest.SUPERBEST_COSTS_POS)
    run_audit([
        {"case_id": "sample", "family": "test", "expression": "exp(x) + exp(x)", "notes": ""}
    ])
    assert superbest.SUPERBEST_COSTS_POS == before


def test_run_audit_boundary_flags_are_false():
    audit = run_audit([
        {"case_id": "sample", "family": "test", "expression": "exp(x) + exp(x)", "notes": ""}
    ])
    assert audit["canonical_row_table_changed"] is False
    assert audit["new_row_optimality_claim"] is False
    assert audit["public_theorem_claim"] is False
    assert audit["open_problem_solved_claim"] is False
