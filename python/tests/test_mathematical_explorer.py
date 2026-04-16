"""Tests for the Mathematical Explorer upgrade (monogate v1.1.0+)."""
import pytest


def test_elegance_score_decreases_with_nodes():
    """Elegance is strictly decreasing in node count."""
    from monogate.prover import elegance_score

    assert elegance_score(1) > elegance_score(5)
    assert elegance_score(5) > elegance_score(10)
    assert elegance_score(10) > elegance_score(100)


def test_elegance_score_symmetry_penalty():
    """Symmetry penalty lowers elegance."""
    from monogate.prover import elegance_score

    assert elegance_score(5, 0.0) > elegance_score(5, 1.0)
    assert elegance_score(5, 0.0) == pytest.approx(1.0 / 5, rel=1e-9)
    assert elegance_score(5, 1.0) == pytest.approx(1.0 / 10, rel=1e-9)


def test_novelty_score_low_for_identical():
    """A catalog expression has near-zero novelty against itself."""
    from monogate.prover import novelty_score
    from monogate.identities import ALL_IDENTITIES

    expr = ALL_IDENTITIES[0].expression
    score = novelty_score(expr, [ALL_IDENTITIES[0]])
    assert score < 0.2  # very low novelty — tokens overlap maximally


def test_novelty_score_high_for_unrelated():
    """A completely new token set scores high novelty."""
    from monogate.prover import novelty_score
    from monogate.identities import ALL_IDENTITIES

    # "zeta" and "riemann" don't appear in the standard catalog
    score = novelty_score("zeta(x) == riemann_zeta(x)", ALL_IDENTITIES)
    assert score > 0.4


def test_interestingness_combined_range():
    """interestingness_score returns a value in [0, 1]."""
    from monogate.prover import interestingness_score
    from monogate.identities import ALL_IDENTITIES

    ist = interestingness_score(
        confidence=0.9,
        node_count=3,
        identity_str="sin(x)**2 + cos(x)**2 == 1",
        catalog=ALL_IDENTITIES,
    )
    assert 0.0 <= ist <= 1.0


def test_proof_sketch_exact_sympy():
    """_proof_sketch returns a human-readable string for exact proof."""
    from monogate.prover import EMLProverV2, ProofResult

    result = ProofResult(
        identity_str="exp(x+y)==exp(x)*exp(y)",
        status="proved_exact",
        verification_method="exact_sympy",
        confidence=1.0,
        max_residual=0.0,
        n_test_points=500,
        elapsed_s=0.1,
        lhs_tree=None,
        rhs_tree=None,
        witness_tree=None,
        node_count=0,
        mcts_simulations=0,
        lhs_formula="exp(x+y)",
        latex_proof="",
        sympy_simplification="0",
        notes="",
    )
    sketch = EMLProverV2._proof_sketch(result)
    assert "SymPy" in sketch or "symbolic" in sketch.lower()


def test_visualize_explorer_session_no_crash():
    """visualize_explorer_session() runs without error on minimal mock data."""
    import matplotlib
    matplotlib.use("Agg")
    from monogate.prover import EMLProverV2

    prover = EMLProverV2()
    fake_session = {
        "discovered": [],
        "n_total_discovered": 0,
        "learning_curve": [
            {
                "round": i + 1,
                "n_conjectures": 5,
                "n_proved": i % 3,
                "n_discovered_total": i,
                "scorer_trained": False,
                "scorer_buffer": i,
                "elapsed_s": 0.5,
                "best_interestingness": 0.1 * (i + 1),
                "adversarial_confirmed": 0,
            }
            for i in range(4)
        ],
    }
    # Should not raise
    prover.visualize_explorer_session(fake_session, output_path=None)


def test_explore_returns_new_keys():
    """explore() result dict includes best_interestingness and adversarial_confirmed."""
    from monogate.prover import EMLProverV2

    prover = EMLProverV2(enable_learning=False, verbose=False)
    session = prover.explore(n_rounds=1, n_per_round=5, temperature=0.5)

    lc = session["learning_curve"]
    assert len(lc) == 1
    assert "best_interestingness" in lc[0], (
        f"Missing 'best_interestingness' key: {lc[0].keys()}"
    )
    assert "adversarial_confirmed" in lc[0], (
        f"Missing 'adversarial_confirmed' key: {lc[0].keys()}"
    )


def test_identities_count():
    """identities.py should now contain at least 200 entries."""
    from monogate.identities import ALL_IDENTITIES

    assert len(ALL_IDENTITIES) >= 200, (
        f"Expected ≥ 200 identities, got {len(ALL_IDENTITIES)}"
    )


def test_grammar_extension_imports():
    """grammar_extension module imports cleanly and exposes key functions."""
    from monogate.frontiers.grammar_extension import (
        census_extended,
        barrier_closed,
        run_grammar_extension,
    )
    assert callable(census_extended)
    assert callable(barrier_closed)
    assert callable(run_grammar_extension)
