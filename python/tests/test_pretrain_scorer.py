"""Tests for monogate.frontiers.pretrain_scorer and Phase 0b get/set_weights."""
import os
import tempfile

import numpy as np
import pytest


def test_get_set_weights_roundtrip():
    """get_weights → set_weights → score() is identical."""
    from monogate.neural_scorer import FeatureBasedEMLScorer

    scorer = FeatureBasedEMLScorer()
    # Inject non-trivial weights directly
    scorer._weights = [
        (np.random.randn(32, 12).astype(np.float32),
         np.random.randn(32).astype(np.float32)),
        (np.random.randn(16, 32).astype(np.float32),
         np.random.randn(16).astype(np.float32)),
        (np.random.randn(1, 16).astype(np.float32),
         np.random.randn(1).astype(np.float32)),
    ]
    scorer._trained = True

    tree = {"op": "leaf", "val": 1.0}
    score_before = scorer.score(tree)

    weights = scorer.get_weights()
    scorer2 = FeatureBasedEMLScorer()
    scorer2.set_weights(weights)
    score_after = scorer2.score(tree)

    assert abs(score_before - score_after) < 1e-6, (
        f"Score mismatch after weight roundtrip: {score_before} vs {score_after}"
    )


def test_save_load_roundtrip():
    """scorer.save(path) → new scorer.load(path) produces same scores."""
    from monogate.neural_scorer import FeatureBasedEMLScorer

    scorer = FeatureBasedEMLScorer()
    scorer._weights = [
        (np.random.randn(32, 12).astype(np.float32),
         np.random.randn(32).astype(np.float32)),
        (np.random.randn(16, 32).astype(np.float32),
         np.random.randn(16).astype(np.float32)),
        (np.random.randn(1, 16).astype(np.float32),
         np.random.randn(1).astype(np.float32)),
    ]
    scorer._trained = True

    tree = {"op": "leaf", "val": 2.0}
    score_before = scorer.score(tree)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp_path = f.name
    try:
        scorer.save(tmp_path)

        scorer2 = FeatureBasedEMLScorer()
        scorer2.load(tmp_path)
        score_after = scorer2.score(tree)

        assert abs(score_before - score_after) < 1e-6, (
            f"Score mismatch after save/load: {score_before} vs {score_after}"
        )
    finally:
        os.unlink(tmp_path)


def test_use_pretrained_param_accepted():
    """EMLProverV2(use_pretrained=True) instantiates without error."""
    from monogate.prover import EMLProverV2

    # Should not raise even if no pretrained file exists on disk
    prover = EMLProverV2(use_pretrained=True)
    assert prover is not None
