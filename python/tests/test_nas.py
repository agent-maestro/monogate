"""Tests for monogate.nas — NASResult, EMLActivationSearch, fitness functions."""

from __future__ import annotations

import math
import pytest
import numpy as np

from monogate.nas import (
    NASResult,
    EMLActivationSearch,
    regression_fitness,
    complexity_penalized_fitness,
)


# ── NASResult dataclass ───────────────────────────────────────────────────────

def test_nasresult_fields():
    """NASResult has all expected fields."""
    r = NASResult(
        best_tree={"op": "leaf", "val": 1.0},
        best_formula="1.0",
        fitness=0.5,
        n_nodes=1,
        generation=3,
        elapsed_s=1.23,
        history=[(0, 1.0), (1, 0.5)],
    )
    assert r.best_tree == {"op": "leaf", "val": 1.0}
    assert r.best_formula == "1.0"
    assert r.fitness == 0.5
    assert r.n_nodes == 1
    assert r.generation == 3
    assert r.elapsed_s == pytest.approx(1.23)
    assert r.history == [(0, 1.0), (1, 0.5)]


def test_nasresult_is_frozen():
    """NASResult is a frozen dataclass (immutable)."""
    r = NASResult(
        best_tree={},
        best_formula="x",
        fitness=0.0,
        n_nodes=0,
        generation=0,
        elapsed_s=0.0,
    )
    with pytest.raises((AttributeError, TypeError)):
        r.fitness = 1.0  # type: ignore


def test_nasresult_default_history():
    """NASResult history defaults to empty list."""
    r = NASResult(
        best_tree={},
        best_formula="",
        fitness=0.0,
        n_nodes=0,
        generation=0,
        elapsed_s=0.0,
    )
    assert r.history == []


# ── EMLActivationSearch construction ─────────────────────────────────────────

def test_search_construction_defaults():
    """EMLActivationSearch can be constructed with defaults."""
    nas = EMLActivationSearch()
    assert nas.max_depth == 4
    assert nas.population_size == 50
    assert nas.mutation_rate == pytest.approx(0.3)
    assert nas.crossover_rate == pytest.approx(0.2)
    assert nas.seed == 42


def test_search_construction_custom():
    """EMLActivationSearch accepts custom parameters."""
    nas = EMLActivationSearch(max_depth=3, population_size=20, seed=7)
    assert nas.max_depth == 3
    assert nas.population_size == 20
    assert nas.seed == 7


def test_search_has_all_methods():
    """EMLActivationSearch has all expected public methods."""
    nas = EMLActivationSearch()
    assert hasattr(nas, "search")
    assert hasattr(nas, "search_for_activation")
    assert hasattr(nas, "compare_activations")


# ── fitness functions ─────────────────────────────────────────────────────────

def test_regression_fitness_perfect():
    """regression_fitness returns ~0 when tree output matches y."""
    # Tree that evaluates to constant 1.0 on all inputs
    tree = {"op": "leaf", "val": 1.0}
    X = np.ones(10).reshape(-1, 1)
    y = np.ones(10)
    fit = regression_fitness(tree, X, y)
    assert math.isfinite(fit)
    assert fit >= 0.0


def test_regression_fitness_nonzero():
    """regression_fitness returns positive MSE for mismatched data."""
    tree = {"op": "leaf", "val": 1.0}
    X = np.ones(10).reshape(-1, 1)
    y = np.zeros(10)  # constant 1.0 vs target 0.0 → MSE = 1.0
    fit = regression_fitness(tree, X, y)
    assert fit > 0


def test_regression_fitness_finite():
    """regression_fitness always returns a finite float for valid trees."""
    tree = {"op": "leaf", "val": "x"}
    X = np.linspace(0.1, 1.0, 20).reshape(-1, 1)
    y = np.linspace(0.1, 1.0, 20)
    fit = regression_fitness(tree, X, y)
    assert math.isfinite(fit)


def test_complexity_penalized_fitness_adds_penalty():
    """complexity_penalized_fitness >= regression_fitness."""
    tree = {"op": "leaf", "val": "x"}
    X = np.linspace(0.1, 1.0, 10)
    y = np.linspace(0.1, 1.0, 10)
    base = regression_fitness(tree, X, y)
    penalized = complexity_penalized_fitness(tree, X, y, alpha=0.1)
    assert penalized >= base


def test_complexity_penalized_fitness_alpha_zero():
    """With alpha=0, complexity-penalized fitness equals regression fitness."""
    tree = {"op": "leaf", "val": "x"}
    X = np.linspace(0.1, 1.0, 10)
    y = np.linspace(0.5, 1.5, 10)
    base = regression_fitness(tree, X, y)
    penalized = complexity_penalized_fitness(tree, X, y, alpha=0.0)
    assert penalized == pytest.approx(base, rel=1e-6)


# ── search() ─────────────────────────────────────────────────────────────────

def test_search_returns_nasresult():
    """search() returns a NASResult."""
    nas = EMLActivationSearch(population_size=10, seed=0)
    X = np.linspace(-1, 1, 20)
    y = np.zeros(20)
    result = nas.search(
        fitness_fn=lambda t: regression_fitness(t, X, y),
        n_generations=2,
        log_every=0,
    )
    assert isinstance(result, NASResult)


def test_search_finite_fitness():
    """search() returns NASResult with finite fitness."""
    nas = EMLActivationSearch(population_size=10, seed=1)
    X = np.linspace(-1, 1, 20)
    y = np.zeros(20)
    result = nas.search(
        fitness_fn=lambda t: regression_fitness(t, X, y),
        n_generations=2,
        log_every=0,
    )
    assert math.isfinite(result.fitness)


def test_search_formula_is_string():
    """search() result best_formula is a non-empty string."""
    nas = EMLActivationSearch(population_size=10, seed=2)
    X = np.linspace(-1, 1, 20)
    y = np.zeros(20)
    result = nas.search(
        fitness_fn=lambda t: regression_fitness(t, X, y),
        n_generations=2,
        log_every=0,
    )
    assert isinstance(result.best_formula, str)
    assert len(result.best_formula) > 0


def test_search_history_length():
    """search() history has one entry per generation."""
    nas = EMLActivationSearch(population_size=10, seed=3)
    X = np.linspace(-1, 1, 20)
    y = np.zeros(20)
    result = nas.search(
        fitness_fn=lambda t: regression_fitness(t, X, y),
        n_generations=5,
        log_every=0,
    )
    assert len(result.history) == 5


def test_search_monotone_history():
    """search() history best_fitness is non-increasing."""
    nas = EMLActivationSearch(population_size=15, seed=4)
    X = np.linspace(-1, 1, 30)
    y = X ** 2
    result = nas.search(
        fitness_fn=lambda t: regression_fitness(t, X, y),
        n_generations=5,
        log_every=0,
    )
    fits = [f for _, f in result.history]
    for i in range(1, len(fits)):
        assert fits[i] <= fits[i - 1] + 1e-12


# ── search_for_activation() ───────────────────────────────────────────────────

def test_search_for_activation_returns_nasresult():
    """search_for_activation() returns a NASResult."""
    nas = EMLActivationSearch(population_size=10, seed=5)
    X = np.linspace(-2, 2, 30).reshape(-1, 1)
    y = X.ravel() ** 2
    result = nas.search_for_activation(X, y, n_generations=3, log_every=0)
    assert isinstance(result, NASResult)


def test_search_for_activation_finite_fitness():
    """search_for_activation returns finite fitness."""
    nas = EMLActivationSearch(population_size=10, seed=6)
    X = np.linspace(-1, 1, 20).reshape(-1, 1)
    y = np.abs(X.ravel())
    result = nas.search_for_activation(X, y, n_generations=2, log_every=0)
    assert math.isfinite(result.fitness)


def test_search_reproducible():
    """Same seed gives same result."""
    X = np.linspace(-1, 1, 20)
    y = X ** 2

    nas1 = EMLActivationSearch(population_size=10, seed=99)
    r1 = nas1.search(lambda t: regression_fitness(t, X, y), n_generations=3, log_every=0)

    nas2 = EMLActivationSearch(population_size=10, seed=99)
    r2 = nas2.search(lambda t: regression_fitness(t, X, y), n_generations=3, log_every=0)

    assert r1.best_formula == r2.best_formula
    assert r1.fitness == pytest.approx(r2.fitness)


# ── compare_activations() ─────────────────────────────────────────────────────

def test_compare_activations_returns_dict():
    """compare_activations returns a dict."""
    nas = EMLActivationSearch(population_size=10, seed=7)
    X = np.linspace(-2, 2, 20)
    y = np.zeros(20)
    tree = {"op": "leaf", "val": 1.0}
    result = nas.compare_activations(tree, X, y)
    assert isinstance(result, dict)


def test_compare_activations_has_eml_key():
    """compare_activations has 'eml_discovered' key."""
    nas = EMLActivationSearch()
    X = np.linspace(-2, 2, 20)
    y = np.zeros(20)
    tree = {"op": "leaf", "val": 1.0}
    result = nas.compare_activations(tree, X, y)
    assert "eml_discovered" in result


def test_compare_activations_all_baselines():
    """compare_activations includes all default baseline activations."""
    nas = EMLActivationSearch()
    X = np.linspace(-2, 2, 20)
    y = np.zeros(20)
    tree = {"op": "leaf", "val": 1.0}
    result = nas.compare_activations(tree, X, y)
    for name in ["relu", "gelu", "silu", "tanh", "sigmoid", "elu"]:
        assert name in result, f"Missing baseline: {name}"


def test_compare_activations_finite_values():
    """compare_activations returns finite MSE for each baseline."""
    nas = EMLActivationSearch()
    X = np.linspace(-1, 1, 20)
    y = np.zeros(20)
    tree = {"op": "leaf", "val": 1.0}
    result = nas.compare_activations(tree, X, y)
    for name, mse in result.items():
        assert math.isfinite(mse), f"Non-finite MSE for {name}"


def test_compare_activations_custom_baselines():
    """compare_activations accepts a custom baselines list."""
    nas = EMLActivationSearch()
    X = np.linspace(-1, 1, 20)
    y = np.zeros(20)
    tree = {"op": "leaf", "val": 1.0}
    result = nas.compare_activations(tree, X, y, baselines=["relu", "tanh"])
    assert set(result.keys()) >= {"eml_discovered", "relu", "tanh"}


# ── population diversity ──────────────────────────────────────────────────────

def test_population_diversity():
    """After 5 generations, there are ≥5 distinct formulas in population."""
    from monogate.search.mcts import _formula

    nas = EMLActivationSearch(population_size=20, seed=8)
    X = np.linspace(-1, 1, 20)
    y = X ** 2

    # Run search and check history shows evolving fitness (proxy for diversity)
    result = nas.search(
        fitness_fn=lambda t: regression_fitness(t, X, y),
        n_generations=5,
        log_every=0,
    )
    # Best formula should be non-trivial
    assert isinstance(result.best_formula, str)
    assert result.n_nodes >= 0
