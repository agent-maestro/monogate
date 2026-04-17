"""Tests for monogate.frontiers.analog_renaissance and cross-domain analogies."""

from __future__ import annotations

import math
import pytest

from monogate.frontiers.analog_renaissance import (
    AnalogRenaissance,
    CrossDomainAnalogy,
    DOMAINS,
    _get_eval_fn,
    _get_tree_fn,
)
from monogate.identities import ANALOG_IDENTITIES, ALL_IDENTITIES, get_by_category


# ── AnalogRenaissance registry ────────────────────────────────────────────────

class TestAnalogRenaissanceRegistry:
    def setup_method(self):
        self.ar = AnalogRenaissance()

    def test_registry_non_empty(self):
        assert len(self.ar.registry) > 0

    def test_all_records_are_cross_domain_analogy(self):
        for a in self.ar.registry:
            assert isinstance(a, CrossDomainAnalogy)

    def test_all_fields_populated(self):
        for a in self.ar.registry:
            assert a.shared_tree
            assert a.source_domain
            assert a.target_domain
            assert a.source_formula
            assert a.target_formula
            assert a.n_nodes >= 1
            assert a.backend in ("DEML", "BEST", "EML", "EXL", "CBEST")
            assert a.proof_tier in ("exact", "numerical")

    def test_source_and_target_differ(self):
        for a in self.ar.registry:
            assert a.source_domain != a.target_domain, (
                f"Source and target should differ: {a.source_domain}"
            )

    def test_registry_covers_all_three_main_domains(self):
        domains = {a.source_domain for a in self.ar.registry} | {a.target_domain for a in self.ar.registry}
        assert "electronics" in domains
        assert "astrophysics" in domains
        assert "finance" in domains

    def test_multiple_tree_shapes_present(self):
        shapes = self.ar.all_tree_shapes()
        assert len(shapes) >= 4  # deml decay, 1-deml, gaussian, sech, power

    def test_deml_decay_tree_present(self):
        shapes = self.ar.all_tree_shapes()
        assert "deml(x, 1)" in shapes

    def test_gaussian_tree_present(self):
        shapes = self.ar.all_tree_shapes()
        assert "deml(x*x, 1)" in shapes

    def test_soliton_tree_present(self):
        shapes = self.ar.all_tree_shapes()
        assert "recip(cosh(x))" in shapes

    def test_at_least_ten_analogies(self):
        assert len(self.ar.registry) >= 10


# ── Crack functions ───────────────────────────────────────────────────────────

class TestCrackFunctions:
    def setup_method(self):
        self.ar = AnalogRenaissance()

    def test_crack_electronics_non_empty(self):
        result = self.ar.crack_electronics()
        assert len(result) >= 2

    def test_crack_astrophysics_non_empty(self):
        result = self.ar.crack_astrophysics()
        assert len(result) >= 3

    def test_crack_finance_non_empty(self):
        result = self.ar.crack_finance()
        assert len(result) >= 3

    def test_crack_electronics_all_have_electronics(self):
        for a in self.ar.crack_electronics():
            assert "electronics" in (a.source_domain, a.target_domain)

    def test_crack_astrophysics_all_have_astrophysics(self):
        for a in self.ar.crack_astrophysics():
            assert "astrophysics" in (a.source_domain, a.target_domain)

    def test_crack_finance_all_have_finance(self):
        for a in self.ar.crack_finance():
            assert "finance" in (a.source_domain, a.target_domain)


# ── find_analogies ────────────────────────────────────────────────────────────

class TestFindAnalogies:
    def setup_method(self):
        self.ar = AnalogRenaissance()

    def test_find_deml_decay(self):
        results = self.ar.find_analogies("deml(x, 1)")
        assert len(results) >= 3  # electronics, astrophysics, finance, thermodynamics

    def test_find_soliton(self):
        results = self.ar.find_analogies("recip(cosh(x))")
        assert len(results) >= 1

    def test_find_nonexistent_returns_empty(self):
        results = self.ar.find_analogies("nonexistent_tree")
        assert results == []

    def test_all_results_have_correct_tree(self):
        for tree in self.ar.all_tree_shapes():
            for a in self.ar.find_analogies(tree):
                assert a.shared_tree == tree


# ── summary_table ─────────────────────────────────────────────────────────────

class TestSummaryTable:
    def setup_method(self):
        self.ar = AnalogRenaissance()

    def test_summary_table_returns_string(self):
        t = self.ar.summary_table()
        assert isinstance(t, str)

    def test_summary_table_contains_markdown_header(self):
        t = self.ar.summary_table()
        assert "## EML Analog Renaissance" in t

    def test_summary_table_contains_all_tree_shapes(self):
        t = self.ar.summary_table()
        for shape in self.ar.all_tree_shapes():
            assert shape in t

    def test_summary_table_has_table_rows(self):
        t = self.ar.summary_table()
        rows = [l for l in t.split("\n") if l.startswith("|") and "deml" in l.lower() or
                l.startswith("|") and "cosh" in l.lower() or
                l.startswith("|") and "eml" in l.lower()]
        assert len(rows) >= 5

    def test_cross_domain_summary_is_dict(self):
        d = self.ar.cross_domain_summary()
        assert isinstance(d, dict)
        assert len(d) >= 4


# ── Numerical verification ────────────────────────────────────────────────────

class TestNumericalVerification:
    def setup_method(self):
        self.ar = AnalogRenaissance()

    def test_deml_decay_analogies_verify(self):
        for a in self.ar.find_analogies("deml(x, 1)"):
            result = self.ar.verify_analogy(a, n_probes=20)
            if result.get("verified") is not None:
                assert result["verified"], (
                    f"Failed verification: {a.source_formula} -> {a.target_formula}: "
                    f"max_err={result.get('max_source_error')}"
                )

    def test_growth_analogies_verify(self):
        for a in self.ar.find_analogies("1 - deml(x, 1)"):
            result = self.ar.verify_analogy(a, n_probes=20)
            if result.get("verified") is not None:
                assert result["verified"]

    def test_gaussian_analogies_verify(self):
        for a in self.ar.find_analogies("deml(x*x, 1)"):
            result = self.ar.verify_analogy(a, n_probes=20)
            if result.get("verified") is not None:
                assert result["verified"]

    def test_soliton_analogies_verify(self):
        for a in self.ar.find_analogies("recip(cosh(x))"):
            result = self.ar.verify_analogy(a, n_probes=20)
            if result.get("verified") is not None:
                assert result["verified"]


# ── Eval helper functions ─────────────────────────────────────────────────────

class TestEvalHelpers:
    def test_deml_tree_fn(self):
        fn = _get_tree_fn("deml(x, 1)")
        assert fn is not None
        assert abs(fn(0.0) - 1.0) < 1e-10
        assert abs(fn(1.0) - math.exp(-1.0)) < 1e-10

    def test_growth_tree_fn(self):
        fn = _get_tree_fn("1 - deml(x, 1)")
        assert fn is not None
        assert abs(fn(0.0) - 0.0) < 1e-10
        assert abs(fn(1.0) - (1.0 - math.exp(-1.0))) < 1e-10

    def test_gaussian_tree_fn(self):
        fn = _get_tree_fn("deml(x*x, 1)")
        assert fn is not None
        assert abs(fn(0.0) - 1.0) < 1e-10
        assert abs(fn(1.0) - math.exp(-1.0)) < 1e-10

    def test_soliton_tree_fn(self):
        fn = _get_tree_fn("recip(cosh(x))")
        assert fn is not None
        assert abs(fn(0.0) - 1.0) < 1e-10
        assert abs(fn(1.0) - 1.0 / math.cosh(1.0)) < 1e-10

    def test_unknown_tree_returns_none(self):
        fn = _get_tree_fn("unknown_tree")
        assert fn is None

    def test_deml_eval_fn_matches_tree(self):
        tree_fn = _get_tree_fn("deml(x, 1)")
        formula_fn = _get_eval_fn("V(t) = V0 * exp(-t/tau)")
        assert tree_fn is not None and formula_fn is not None
        for x in [0.5, 1.0, 2.0, 3.0]:
            assert abs(tree_fn(x) - formula_fn(x)) < 1e-10

    def test_growth_eval_fn_matches_tree(self):
        tree_fn = _get_tree_fn("1 - deml(x, 1)")
        formula_fn = _get_eval_fn("V(t) = Vs * (1 - exp(-t/tau))")
        assert tree_fn is not None and formula_fn is not None
        for x in [0.5, 1.0, 2.0, 3.0]:
            assert abs(tree_fn(x) - formula_fn(x)) < 1e-10


# ── ANALOG_IDENTITIES catalog ─────────────────────────────────────────────────

class TestAnalogIdentities:
    def test_analog_identities_non_empty(self):
        assert len(ANALOG_IDENTITIES) >= 15

    def test_at_least_twenty_analog_identities(self):
        assert len(ANALOG_IDENTITIES) >= 20

    def test_all_category_analog(self):
        for ident in ANALOG_IDENTITIES:
            assert ident.category == "analog"

    def test_analog_in_all_identities(self):
        analog_from_all = [i for i in ALL_IDENTITIES if i.category == "analog"]
        assert len(analog_from_all) == len(ANALOG_IDENTITIES)

    def test_get_by_category_analog(self):
        analog = get_by_category("analog")
        assert len(analog) >= 15

    def test_all_have_domain(self):
        for ident in ANALOG_IDENTITIES:
            assert ident.domain is not None
            assert len(ident.domain) == 2
            assert ident.domain[0] < ident.domain[1]

    def test_all_have_notes(self):
        for ident in ANALOG_IDENTITIES:
            assert ident.notes, f"Missing notes for: {ident.name}"

    def test_deml_decay_identity_present(self):
        names = [i.name for i in ANALOG_IDENTITIES]
        assert any("RC discharge" in n for n in names)

    def test_stellar_cooling_present(self):
        names = [i.name for i in ANALOG_IDENTITIES]
        assert any("cooling" in n.lower() or "stellar" in n.lower() for n in names)

    def test_finance_identity_present(self):
        names = [i.name for i in ANALOG_IDENTITIES]
        assert any("discount" in n.lower() or "Black-Scholes" in n or "finance" in n.lower()
                   for n in names)

    def test_gaussian_identity_present(self):
        names = [i.name for i in ANALOG_IDENTITIES]
        assert any("gaussian" in n.lower() or "heat kernel" in n.lower() for n in names)

    def test_soliton_identity_present(self):
        names = [i.name for i in ANALOG_IDENTITIES]
        assert any("soliton" in n.lower() or "sech" in n.lower() for n in names)

    def test_all_difficulties_valid(self):
        valid = {"trivial", "easy", "medium", "hard", "open"}
        for ident in ANALOG_IDENTITIES:
            assert ident.difficulty in valid, f"Bad difficulty: {ident.difficulty}"


# ── CrossDomainAnalogy dataclass ──────────────────────────────────────────────

class TestCrossDomainAnalogyDataclass:
    def test_one_liner_format(self):
        a = CrossDomainAnalogy(
            shared_tree="deml(x, 1)",
            source_domain="electronics",
            source_formula="V(t) = V0 * exp(-t/tau)",
            source_constant="t/tau",
            target_domain="astrophysics",
            target_formula="T(t) = T_env + DT * exp(-t/tau_cool)",
            target_constant="t/tau_cool",
            n_nodes=1,
            backend="DEML",
            proof_tier="exact",
        )
        line = a.one_liner()
        assert "electronics" in line
        assert "astrophysics" in line
        assert "deml(x, 1)" in line
        assert "1n" in line

    def test_frozen_dataclass(self):
        a = CrossDomainAnalogy(
            shared_tree="deml(x, 1)",
            source_domain="electronics",
            source_formula="test",
            source_constant="x",
            target_domain="finance",
            target_formula="test2",
            target_constant="x",
            n_nodes=1,
            backend="DEML",
            proof_tier="exact",
        )
        with pytest.raises(Exception):
            a.n_nodes = 99  # type: ignore[misc]
