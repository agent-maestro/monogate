"""Tests for the DEML dual gate and extended operator registry."""

import math
import pytest

from monogate import DEML, exp_neg_deml, ln_deml, EML, EDL, EXL, EAL, EMN
from monogate.operators import ALL_OPERATORS, get_operator, _NODE_COUNTS


# ── Part 1: DEML gate correctness ────────────────────────────────────────────

class TestDEMLGate:
    def test_exp_neg_deml_identity(self):
        """deml(x, 1) = exp(-x) for 100 probe points."""
        xs = [i * 0.05 for i in range(-20, 21)]
        for x in xs:
            expected = math.exp(-x)
            got = exp_neg_deml(x)
            assert abs(got - expected) < 1e-12, (
                f"exp_neg_deml({x}) = {got}, expected {expected}"
            )

    def test_exp_neg_deml_at_zero(self):
        assert abs(exp_neg_deml(0.0) - 1.0) < 1e-14

    def test_exp_neg_deml_at_one(self):
        assert abs(exp_neg_deml(1.0) - math.exp(-1.0)) < 1e-14

    def test_deml_func_domain(self):
        """deml.func raises on y <= 0 (ln domain violation)."""
        with pytest.raises((ValueError, ZeroDivisionError, Exception)):
            DEML.func(0.0 + 0j, 0.0 + 0j)

    def test_ln_deml_correctness(self):
        """ln_deml falls back to EML's 3-node formula; check accuracy."""
        xs = [0.5, 1.0, math.e, 2.0, 10.0]
        for x in xs:
            assert abs(ln_deml(x) - math.log(x)) < 1e-10, (
                f"ln_deml({x}) = {ln_deml(x)}, expected {math.log(x)}"
            )

    def test_deml_meta(self):
        meta = DEML.__dict__.get("_meta", {})
        assert meta.get("gate") == "exp(-x) - ln(y)"
        assert meta.get("complete") is False
        assert meta.get("constant_name") == "1"


# ── Part 2: Registry integration ─────────────────────────────────────────────

class TestDEMLRegistry:
    def test_deml_in_all_operators(self):
        assert DEML in ALL_OPERATORS

    def test_get_operator_deml(self):
        assert get_operator("DEML") is DEML

    def test_deml_not_in_complete(self):
        from monogate.operators import COMPLETE_OPERATORS
        assert DEML not in COMPLETE_OPERATORS

    def test_node_counts_exp_neg_x(self):
        """exp(-x) should be 1 node for DEML and None for all others."""
        row = _NODE_COUNTS.get("exp(-x)")
        assert row is not None, "exp(-x) missing from _NODE_COUNTS"
        # Index 5 = DEML
        from monogate.operators import _OP_ORDER
        idx = _OP_ORDER.index("DEML")
        assert row[idx] == 1

    def test_node_counts_others_blocked(self):
        """All operators except DEML should be None for exp(-x)."""
        from monogate.operators import _OP_ORDER
        row = _NODE_COUNTS.get("exp(-x)", ())
        for name, val in zip(_OP_ORDER, row):
            if name != "DEML":
                assert val is None, f"{name} exp(-x) should be None (blocked), got {val}"


# ── Part 3: DEML in operator_comparison ──────────────────────────────────────

class TestDEMLComparison:
    def test_deml_in_operator_meta(self):
        from monogate.frontiers.operator_comparison import OPERATOR_META
        assert "DEML" in OPERATOR_META
        assert OPERATOR_META["DEML"]["gate"] == "exp(−a) − ln(b)"

    def test_eval_deml_exp_neg_x(self):
        """_eval_deml on a 1-node tree should reproduce exp(-x)."""
        from monogate.frontiers.operator_comparison import _eval_deml
        tree = {"op": "eml", "left": {"op": "leaf", "val": "x"},
                "right": {"op": "leaf", "val": "1.0"}}
        for x in [0.1, 0.5, 1.0, 2.0]:
            got = _eval_deml(tree, x)
            expected = math.exp(-x)
            assert abs(got - expected) < 1e-12, f"_eval_deml tree at x={x}: {got} vs {expected}"

    def test_node_count_table_includes_deml(self):
        from monogate.frontiers.operator_comparison import node_count_table
        table = node_count_table()
        assert "DEML" in table


# ── Part 4: DEML physics census smoke test ────────────────────────────────────

class TestDEMLCensus:
    def test_deml_native_on_exp_neg_x(self):
        """DEML should find exp(-x) as native (MSE < 1e-6) at depth=2."""
        import math
        from monogate.frontiers.deml_census import run_deml_census, DEML_NATIVE_THRESHOLD
        from monogate.frontiers.law_complexity import FUNCTIONAL_LAWS

        # Find the "Exponential decay" law
        decay_law = next(
            (l for l in FUNCTIONAL_LAWS if "decay" in l.get("name", "").lower()),
            None,
        )
        assert decay_law is not None, "Could not find exponential decay in FUNCTIONAL_LAWS"

        from monogate.search.mcts import mcts_search
        from monogate.frontiers.operator_comparison import _eval_deml

        fn = decay_law["fn"]
        lo, hi = decay_law["domain"]
        probe = [lo + (hi - lo) * i / 59 for i in range(60)]
        r = mcts_search(
            target_fn=fn,
            probe_points=probe,
            depth=2,
            n_simulations=500,
            seed=42,
            eval_tree_fn=_eval_deml,
        )
        assert r.best_mse < DEML_NATIVE_THRESHOLD, (
            f"DEML failed on exp(-x): MSE={r.best_mse:.6f} (expected < {DEML_NATIVE_THRESHOLD})"
        )

    def test_run_deml_census_quick(self):
        """run_deml_census returns expected keys and DEML finds at least 1 native law."""
        from monogate.frontiers.deml_census import run_deml_census
        results = run_deml_census(n_simulations=300, depth=2, verbose=False)

        assert "n_eml_native" in results
        assert "n_deml_native" in results
        assert "n_combined_native" in results
        assert "summary_table" in results
        assert results["n_total"] == 15
        assert results["n_deml_native"] >= 1, (
            f"Expected DEML to be native for at least 1 law, got {results['n_deml_native']}"
        )
        assert results["n_combined_native"] >= results["n_eml_native"]
        assert results["n_combined_native"] >= results["n_deml_native"]
