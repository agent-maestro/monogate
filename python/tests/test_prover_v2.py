"""Tests for EMLProverV2 — conjecture generation, proof compression, visualization."""

from __future__ import annotations

import math
import pytest

from monogate.prover import EMLProver, EMLProverV2, ProofResult, BenchmarkReport
from monogate.identities import ALL_IDENTITIES, TRIG_IDENTITIES, Identity


# ── Construction ──────────────────────────────────────────────────────────────

def test_emlprover_v2_is_subclass():
    """EMLProverV2 inherits from EMLProver."""
    assert issubclass(EMLProverV2, EMLProver)


def test_emlprover_v2_construction_defaults():
    """EMLProverV2 can be constructed with defaults."""
    p = EMLProverV2()
    assert p.n_probe == 500
    assert p.verbose is False


def test_emlprover_v2_construction_custom():
    """EMLProverV2 passes kwargs to EMLProver."""
    p = EMLProverV2(verbose=True, n_probe=100)
    assert p.n_probe == 100
    assert p.verbose is True


def test_emlprover_v2_has_all_methods():
    """EMLProverV2 has all expected methods."""
    p = EMLProverV2()
    assert hasattr(p, "prove")
    assert hasattr(p, "prove_batch")
    assert hasattr(p, "benchmark")
    assert hasattr(p, "generate_conjectures")
    assert hasattr(p, "compress_proof")
    assert hasattr(p, "visualize_proof")
    assert hasattr(p, "batch_prove")


# ── Identity catalog at 120+ ──────────────────────────────────────────────────

def test_all_identities_count_at_least_120():
    """ALL_IDENTITIES has ≥120 entries after v1.1.0 expansion."""
    assert len(ALL_IDENTITIES) >= 120


def test_all_identities_no_duplicates():
    """ALL_IDENTITIES has no duplicate expressions (excluding analog category).

    Analog identities intentionally share expression strings across domains.
    """
    exprs = [i.expression for i in ALL_IDENTITIES if i.category != "analog"]
    assert len(exprs) == len(set(exprs)), "Duplicate expressions found"


def test_trig_identities_at_least_27():
    """TRIG_IDENTITIES has ≥27 identities after expansion."""
    assert len(TRIG_IDENTITIES) >= 27


def test_all_identities_have_valid_categories():
    """All identities have a valid category string."""
    valid = {"trigonometric", "hyperbolic", "exponential", "special",
             "physics", "eml", "open", "analog"}
    for i in ALL_IDENTITIES:
        assert i.category in valid, f"Invalid category: {i.category} for {i.name}"


def test_all_identities_have_valid_difficulty():
    """All identities have a valid difficulty string."""
    valid = {"trivial", "easy", "medium", "hard", "open"}
    for i in ALL_IDENTITIES:
        assert i.difficulty in valid, f"Invalid difficulty: {i.difficulty} for {i.name}"


def test_all_identities_have_domain_tuple():
    """All identities have a 2-element domain tuple."""
    for i in ALL_IDENTITIES:
        assert len(i.domain) == 2, f"Domain not length 2 for {i.name}"
        assert i.domain[0] <= i.domain[1], f"lo > hi for {i.name}"


# ── generate_conjectures ──────────────────────────────────────────────────────

def test_generate_conjectures_returns_list():
    """generate_conjectures returns a list."""
    p = EMLProverV2()
    result = p.generate_conjectures(category="trig", n=5, seed=0)
    assert isinstance(result, list)


def test_generate_conjectures_returns_identity_objects():
    """generate_conjectures returns Identity objects."""
    p = EMLProverV2()
    result = p.generate_conjectures(category="trig", n=5, seed=0)
    for item in result:
        assert isinstance(item, Identity)


def test_generate_conjectures_max_n():
    """generate_conjectures returns at most n items."""
    p = EMLProverV2()
    result = p.generate_conjectures(n=3, seed=42)
    assert len(result) <= 3


def test_generate_conjectures_correct_category():
    """Generated conjectures have the requested category."""
    p = EMLProverV2()
    result = p.generate_conjectures(category="trig", n=10, seed=0)
    for item in result:
        assert item.category == "trigonometric"


def test_generate_conjectures_expected_method_unknown():
    """Generated conjectures have expected_method='unknown'."""
    p = EMLProverV2()
    result = p.generate_conjectures(n=5, seed=0)
    for item in result:
        assert item.expected_method == "unknown"


def test_generate_conjectures_not_in_catalog():
    """Generated conjectures are not identical to existing catalog entries."""
    p = EMLProverV2()
    existing = {i.expression for i in ALL_IDENTITIES}
    result = p.generate_conjectures(n=10, seed=0)
    for item in result:
        assert item.expression not in existing, (
            f"Generated conjecture duplicates catalog: {item.expression}"
        )


def test_generate_conjectures_numerically_valid():
    """Generated conjectures pass numerical check (they were selected for it)."""
    p = EMLProverV2()
    result = p.generate_conjectures(n=5, seed=0)
    for item in result:
        # Quick prove on the generated conjecture
        r = p.prove(item.expression, domain=item.domain, n_simulations=100)
        # Should be provable numerically (was numerically verified in generation)
        assert r.proved(), f"Conjecture failed proof: {item.expression}, {r.status}"


def test_generate_conjectures_reproducible():
    """Same seed → same conjectures."""
    p = EMLProverV2()
    r1 = p.generate_conjectures(n=5, seed=7)
    r2 = p.generate_conjectures(n=5, seed=7)
    assert [i.expression for i in r1] == [i.expression for i in r2]


def test_generate_conjectures_different_seeds():
    """Different seeds can produce different conjectures."""
    p = EMLProverV2()
    r1 = p.generate_conjectures(n=5, seed=0)
    r2 = p.generate_conjectures(n=5, seed=999)
    # Just check both ran without error
    assert isinstance(r1, list)
    assert isinstance(r2, list)


def test_generate_conjectures_hyperbolic_category():
    """generate_conjectures works with 'hyperbolic' category alias."""
    p = EMLProverV2()
    result = p.generate_conjectures(category="hyperbolic", n=5, seed=0)
    assert isinstance(result, list)
    for item in result:
        assert item.category == "hyperbolic"


# ── compress_proof ────────────────────────────────────────────────────────────

def test_compress_proof_no_witness_returns_original():
    """compress_proof with no witness_tree returns original unchanged."""
    p = EMLProverV2()
    result = p.prove("exp(x) == exp(x)")
    compressed = p.compress_proof(result)
    assert isinstance(compressed, ProofResult)


def test_compress_proof_returns_proof_result():
    """compress_proof always returns a ProofResult."""
    p = EMLProverV2()
    result = p.prove("sin(x)**2 + cos(x)**2 == 1")
    compressed = p.compress_proof(result, n_simulations=50)
    assert isinstance(compressed, ProofResult)


def test_compress_proof_same_identity():
    """compress_proof preserves the identity string."""
    p = EMLProverV2()
    result = p.prove("exp(x) - log(1) == exp(x)")
    compressed = p.compress_proof(result, n_simulations=50)
    assert compressed.identity_str == result.identity_str


def test_compress_proof_node_count_not_worse():
    """compress_proof returns same or fewer nodes."""
    p = EMLProverV2()
    result = p.prove("exp(x) - log(1) == exp(x)")
    compressed = p.compress_proof(result, n_simulations=50)
    assert compressed.node_count <= result.node_count


# ── visualize_proof ───────────────────────────────────────────────────────────

def test_visualize_proof_requires_matplotlib():
    """visualize_proof raises ImportError if matplotlib absent (smoke test if present)."""
    try:
        import matplotlib
        _has_mpl = True
    except ImportError:
        _has_mpl = False

    p = EMLProverV2()
    result = p.prove("sin(x)**2 + cos(x)**2 == 1")

    if not _has_mpl:
        with pytest.raises(ImportError):
            p.visualize_proof(result)
    else:
        import matplotlib
        matplotlib.use("Agg")  # non-interactive backend for tests
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            p.visualize_proof(result, output_path=path)
            assert os.path.exists(path)
        finally:
            if os.path.exists(path):
                os.unlink(path)


def test_visualize_proof_all_styles(tmp_path):
    """visualize_proof accepts all style values without crashing."""
    try:
        import matplotlib
        matplotlib.use("Agg")
    except ImportError:
        pytest.skip("matplotlib not installed")

    p = EMLProverV2()
    result = p.prove("sin(x)**2 + cos(x)**2 == 1")

    for style in ("tree", "radial", "step"):
        out = str(tmp_path / f"{style}.png")
        p.visualize_proof(result, style=style, output_path=out)


# ── batch_prove ───────────────────────────────────────────────────────────────

def test_batch_prove_returns_benchmark_report():
    """batch_prove returns a BenchmarkReport."""
    p = EMLProverV2()
    report = p.batch_prove(["exp(x) == exp(x)", "sin(x)**2 + cos(x)**2 == 1"],
                           show_progress=False)
    assert isinstance(report, BenchmarkReport)


def test_batch_prove_with_identity_objects():
    """batch_prove accepts Identity objects."""
    p = EMLProverV2()
    items = [i for i in ALL_IDENTITIES if i.difficulty == "trivial"][:3]
    report = p.batch_prove(items, show_progress=False)
    assert report.n_total == len(items)


def test_batch_prove_empty():
    """batch_prove on empty list returns empty BenchmarkReport."""
    p = EMLProverV2()
    report = p.batch_prove([], show_progress=False)
    assert report.n_total == 0
    assert report.success_rate == 0.0


def test_batch_prove_all_easy():
    """batch_prove on easy trivial identities shows good success rate."""
    p = EMLProverV2()
    items = [i for i in ALL_IDENTITIES if i.difficulty == "trivial"][:5]
    report = p.batch_prove(items, show_progress=False)
    # Trivial identities should have high success rate
    assert report.success_rate >= 0.6


def test_batch_prove_preserves_order():
    """batch_prove results preserve input order."""
    p = EMLProverV2()
    exprs = ["exp(x) == exp(x)", "sin(-x) == -sin(x)"]
    report = p.batch_prove(exprs, show_progress=False)
    assert report.results[0].identity_str == exprs[0]
    assert report.results[1].identity_str == exprs[1]


# ── Inherited prove still works ───────────────────────────────────────────────

def test_inherited_prove_works():
    """EMLProverV2 can still prove identities via inherited prove()."""
    p = EMLProverV2()
    r = p.prove("sin(x)**2 + cos(x)**2 == 1")
    assert r.proved()


def test_inherited_benchmark_works():
    """EMLProverV2.benchmark() still works."""
    p = EMLProverV2()
    report = p.benchmark(n_simulations=50, timeout=10.0)
    assert isinstance(report, BenchmarkReport)
    assert report.n_total > 0
