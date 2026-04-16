"""Tests for monogate.neural_scorer — FeatureBasedEMLScorer, ExperienceBuffer, features."""

from __future__ import annotations

import math
import os
import tempfile

import numpy as np
import pytest

from monogate.neural_scorer import (
    N_FEATURES,
    ExperienceBuffer,
    FeatureBasedEMLScorer,
    extract_tree_features,
)
from monogate.search.mcts import _eml, _leaf


# ── Tree fixtures ─────────────────────────────────────────────────────────────

def leaf_x():
    return _leaf("x")

def leaf_1():
    return _leaf(1.0)

def depth1_tree():
    return _eml(_leaf("x"), _leaf(1.0))

def depth2_tree():
    return _eml(_eml(_leaf("x"), _leaf(1.0)), _leaf(2.0))

def depth3_tree():
    return _eml(_eml(_eml(_leaf("x"), _leaf(1.0)), _leaf(2.0)), _leaf(0.5))


# ── extract_tree_features ─────────────────────────────────────────────────────

def test_features_returns_ndarray():
    """extract_tree_features returns np.ndarray."""
    f = extract_tree_features(depth1_tree())
    assert isinstance(f, np.ndarray)


def test_features_correct_length():
    """Feature vector has exactly N_FEATURES (12) elements."""
    f = extract_tree_features(depth1_tree())
    assert len(f) == N_FEATURES
    assert N_FEATURES == 12


def test_features_all_finite():
    """All features are finite floats."""
    for tree in [leaf_x(), leaf_1(), depth1_tree(), depth2_tree(), depth3_tree()]:
        f = extract_tree_features(tree)
        assert all(math.isfinite(v) for v in f), f"Non-finite feature in {f}"


def test_features_leaf_x_depth_zero():
    """Leaf node has depth=0."""
    f = extract_tree_features(leaf_x())
    assert f[0] == 0.0  # depth


def test_features_leaf_eml_nodes_zero():
    """Leaf node has eml_nodes=0."""
    f = extract_tree_features(leaf_x())
    assert f[1] == 0.0  # eml_nodes


def test_features_leaf_ratio_one():
    """Single leaf has leaf_ratio=1.0."""
    f = extract_tree_features(leaf_1())
    assert f[3] == pytest.approx(1.0)  # leaf_ratio


def test_features_x_fraction_correct():
    """x_fraction is 1.0 for pure-x leaf, 0.0 for const leaf."""
    fx = extract_tree_features(leaf_x())
    fc = extract_tree_features(leaf_1())
    assert fx[4] == pytest.approx(1.0)  # x_fraction
    assert fc[4] == pytest.approx(0.0)


def test_features_depth_increases():
    """depth feature increases with tree depth."""
    f1 = extract_tree_features(depth1_tree())
    f2 = extract_tree_features(depth2_tree())
    f3 = extract_tree_features(depth3_tree())
    assert f1[0] < f2[0] < f3[0]


def test_features_eml_nodes_count():
    """eml_nodes matches tree structure."""
    assert extract_tree_features(depth1_tree())[1] == 1.0
    assert extract_tree_features(depth2_tree())[1] == 2.0
    assert extract_tree_features(depth3_tree())[1] == 3.0


def test_features_balance_leaf():
    """Single leaf has balance=1.0 (trivially balanced)."""
    f = extract_tree_features(leaf_1())
    assert f[9] == pytest.approx(1.0)  # balance


# ── ExperienceBuffer ──────────────────────────────────────────────────────────

def test_buffer_empty_on_init():
    """Buffer starts empty."""
    buf = ExperienceBuffer()
    assert len(buf) == 0


def test_buffer_add_grows():
    """Adding entries increases buffer length."""
    buf = ExperienceBuffer()
    feat = np.zeros(N_FEATURES)
    buf.add(feat, 0.8)
    assert len(buf) == 1


def test_buffer_respects_maxlen():
    """Buffer evicts oldest entries beyond maxlen."""
    buf = ExperienceBuffer(maxlen=5)
    feat = np.zeros(N_FEATURES)
    for i in range(10):
        buf.add(feat, float(i) / 10)
    assert len(buf) == 5


def test_buffer_reward_clipped():
    """Rewards outside [0,1] are clipped."""
    buf = ExperienceBuffer()
    buf.add(np.zeros(N_FEATURES), 5.0)
    buf.add(np.zeros(N_FEATURES), -1.0)
    _, y = buf.as_arrays()
    assert all(0.0 <= r <= 1.0 for r in y)


def test_buffer_as_arrays_shape():
    """as_arrays returns correct shapes."""
    buf = ExperienceBuffer()
    for _ in range(5):
        buf.add(np.ones(N_FEATURES), 0.5)
    X, y = buf.as_arrays()
    assert X.shape == (5, N_FEATURES)
    assert y.shape == (5,)


def test_buffer_serialization():
    """to_list / from_list round-trip preserves data."""
    buf = ExperienceBuffer(maxlen=10)
    for i in range(5):
        buf.add(np.arange(N_FEATURES, dtype=float) + i, float(i) / 5)
    data = buf.to_list()
    buf2 = ExperienceBuffer.from_list(data, maxlen=10)
    assert len(buf2) == len(buf)
    X1, y1 = buf.as_arrays()
    X2, y2 = buf2.as_arrays()
    np.testing.assert_allclose(X1, X2)
    np.testing.assert_allclose(y1, y2)


# ── FeatureBasedEMLScorer ─────────────────────────────────────────────────────

def test_scorer_construction():
    """FeatureBasedEMLScorer constructs without error."""
    s = FeatureBasedEMLScorer()
    assert s is not None


def test_scorer_untrained_returns_half():
    """Untrained scorer returns 0.5 (neutral)."""
    s = FeatureBasedEMLScorer()
    score = s.score(depth1_tree())
    assert score == pytest.approx(0.5)


def test_scorer_is_trained_false_initially():
    """is_trained() is False before any updates."""
    s = FeatureBasedEMLScorer()
    assert s.is_trained() is False


def test_scorer_update_accepted():
    """update() accepts valid inputs without error."""
    s = FeatureBasedEMLScorer(min_samples=5, retrain_every=5)
    s.update(depth1_tree(), 0.8)  # should not raise
    assert len(s._buffer) == 1


def test_scorer_trains_after_min_samples():
    """After min_samples updates, is_trained() becomes True."""
    s = FeatureBasedEMLScorer(min_samples=5, retrain_every=5)
    tree = depth1_tree()
    for _ in range(6):
        s.update(tree, 0.8)
    assert s.is_trained() is True


def test_scorer_score_in_range_after_training():
    """After training, score() returns value in [0, 1]."""
    s = FeatureBasedEMLScorer(min_samples=5, retrain_every=5)
    tree = depth1_tree()
    for _ in range(6):
        s.update(tree, 0.8)
    score = s.score(tree)
    assert 0.0 <= score <= 1.0


def test_scorer_save_load(tmp_path):
    """save() / load() round-trip preserves trained state."""
    s = FeatureBasedEMLScorer(min_samples=5, retrain_every=5)
    tree = depth1_tree()
    for _ in range(6):
        s.update(tree, 0.8)
    assert s.is_trained()

    path = str(tmp_path / "scorer.json")
    s.save(path)
    assert os.path.exists(path)

    s2 = FeatureBasedEMLScorer()
    s2.load(path)
    assert s2.is_trained()
    score1 = s.score(tree)
    score2 = s2.score(tree)
    assert score1 == pytest.approx(score2, abs=1e-6)


# ── MCTS integration ──────────────────────────────────────────────────────────

def test_mcts_search_no_scorer():
    """mcts_search still works with external_scorer=None (backward compat)."""
    from monogate.search.mcts import mcts_search
    result = mcts_search(
        lambda x: x ** 2,
        probe_points=list(range(-3, 4)),
        depth=2,
        n_simulations=50,
        external_scorer=None,
    )
    assert math.isfinite(result.best_mse)


def test_mcts_search_with_constant_scorer():
    """mcts_search works with a constant scorer (always 0.5)."""
    from monogate.search.mcts import mcts_search
    result = mcts_search(
        lambda x: x ** 2,
        probe_points=list(range(-3, 4)),
        depth=2,
        n_simulations=50,
        external_scorer=lambda t: 0.5,
    )
    assert math.isfinite(result.best_mse)


# ── EMLProver integration ─────────────────────────────────────────────────────

def test_emlprover_with_scorer_none():
    """EMLProver(scorer=None) constructs without error."""
    from monogate.prover import EMLProver
    p = EMLProver(scorer=None)
    assert p.scorer is None


def test_emlprover_with_scorer():
    """EMLProver accepts a scorer and stores it."""
    from monogate.prover import EMLProver
    scorer = FeatureBasedEMLScorer()
    p = EMLProver(scorer=scorer)
    assert p.scorer is scorer


def test_emlproverv2_enable_learning_false():
    """EMLProverV2(enable_learning=False) has scorer=None."""
    from monogate.prover import EMLProverV2
    p = EMLProverV2(enable_learning=False)
    assert p.scorer is None


def test_emlproverv2_enable_learning_true():
    """EMLProverV2(enable_learning=True) creates a scorer."""
    from monogate.prover import EMLProverV2
    p = EMLProverV2(enable_learning=True)
    assert isinstance(p.scorer, FeatureBasedEMLScorer)


def test_emlproverv2_prove_still_works():
    """EMLProverV2 with scorer can still prove identities."""
    from monogate.prover import EMLProverV2
    p = EMLProverV2(enable_learning=True)
    r = p.prove("exp(x) == exp(x)")
    assert r.proved()


# ── Interactive visualization ─────────────────────────────────────────────────

def test_visualize_interactive_import_error():
    """visualize_proof_interactive raises ImportError when plotly absent."""
    import importlib
    import sys
    plotly_present = importlib.util.find_spec("plotly") is not None

    from monogate.prover import EMLProverV2
    p = EMLProverV2()
    result = p.prove("exp(x) == exp(x)")

    if not plotly_present:
        with pytest.raises(ImportError, match="plotly"):
            p.visualize_proof_interactive(result)
    else:
        fig = p.visualize_proof_interactive(result)
        assert fig is not None


def test_visualize_interactive_html(tmp_path):
    """visualize_proof_interactive saves HTML when plotly present."""
    try:
        import plotly  # noqa: F401
    except ImportError:
        pytest.skip("plotly not installed")

    from monogate.prover import EMLProverV2
    p = EMLProverV2()
    result = p.prove("sin(x)**2 + cos(x)**2 == 1")
    out = str(tmp_path / "proof.html")
    p.visualize_proof_interactive(result, output_path=out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 100


# ── Catalog size ──────────────────────────────────────────────────────────────

def test_catalog_at_least_150():
    """ALL_IDENTITIES has ≥150 entries."""
    from monogate.identities import ALL_IDENTITIES
    assert len(ALL_IDENTITIES) >= 150


def test_catalog_no_duplicates():
    """No duplicate expressions in expanded catalog."""
    from monogate.identities import ALL_IDENTITIES
    exprs = [i.expression for i in ALL_IDENTITIES]
    assert len(exprs) == len(set(exprs))
