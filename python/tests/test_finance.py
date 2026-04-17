"""Tests for monogate.finance — Black-Scholes and EML finance formulas."""

from __future__ import annotations

import math
import pytest

from monogate.finance import (
    black_scholes_call,
    black_scholes_put,
    bs_call_eml,
    bs_components_eml,
    bs_discount_cb,
    bs_log_moneyness_cb,
    bs_d1_cb,
    bs_d2_cb,
    FINANCE_CATALOG,
)


# ── Reference values (ATM, 1Y, 20% vol, 5% rate) ─────────────────────────────

S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.20
# Known BS call price for these params (computed independently): ~10.4506
BS_CALL_REF = black_scholes_call(S, K, r, T, sigma)


# ── black_scholes_call ────────────────────────────────────────────────────────

class TestBlackScholesCall:
    def test_atm_call_positive(self):
        assert black_scholes_call(S, K, r, T, sigma) > 0

    def test_deep_itm_call_near_intrinsic(self):
        c = black_scholes_call(200.0, 100.0, 0.05, 1.0, 0.20)
        assert c > 90.0

    def test_deep_otm_call_near_zero(self):
        c = black_scholes_call(50.0, 200.0, 0.05, 1.0, 0.20)
        assert c < 1.0

    def test_expired_call_intrinsic_itm(self):
        c = black_scholes_call(110.0, 100.0, 0.05, 0.0, 0.20)
        assert abs(c - 10.0) < 1e-10

    def test_expired_call_intrinsic_otm(self):
        c = black_scholes_call(90.0, 100.0, 0.05, 0.0, 0.20)
        assert c == 0.0

    def test_call_bounded_by_spot(self):
        c = black_scholes_call(S, K, r, T, sigma)
        assert c < S

    def test_call_increases_with_spot(self):
        c1 = black_scholes_call(90.0, K, r, T, sigma)
        c2 = black_scholes_call(110.0, K, r, T, sigma)
        assert c2 > c1

    def test_call_decreases_with_strike(self):
        c1 = black_scholes_call(S, 90.0, r, T, sigma)
        c2 = black_scholes_call(S, 110.0, r, T, sigma)
        assert c1 > c2

    def test_call_increases_with_vol(self):
        c1 = black_scholes_call(S, K, r, T, 0.10)
        c2 = black_scholes_call(S, K, r, T, 0.40)
        assert c2 > c1

    def test_call_increases_with_time(self):
        c1 = black_scholes_call(S, K, r, 0.5, sigma)
        c2 = black_scholes_call(S, K, r, 2.0, sigma)
        assert c2 > c1

    def test_known_value_approx(self):
        c = black_scholes_call(S, K, r, T, sigma)
        assert 10.0 < c < 11.0


# ── black_scholes_put ─────────────────────────────────────────────────────────

class TestBlackScholesPut:
    def test_atm_put_positive(self):
        assert black_scholes_put(S, K, r, T, sigma) > 0

    def test_put_call_parity(self):
        c = black_scholes_call(S, K, r, T, sigma)
        p = black_scholes_put(S, K, r, T, sigma)
        discount = math.exp(-r * T)
        parity = c - p - (S - K * discount)
        assert abs(parity) < 1e-8

    def test_expired_put_intrinsic_itm(self):
        p = black_scholes_put(90.0, 100.0, 0.05, 0.0, 0.20)
        assert abs(p - 10.0) < 1e-10

    def test_expired_put_intrinsic_otm(self):
        p = black_scholes_put(110.0, 100.0, 0.05, 0.0, 0.20)
        assert p == 0.0

    def test_deep_otm_put_near_zero(self):
        p = black_scholes_put(200.0, 100.0, 0.05, 1.0, 0.20)
        assert p < 1.0


# ── bs_discount_cb ────────────────────────────────────────────────────────────

class TestBsDiscount:
    def test_zero_rate_is_one(self):
        assert abs(bs_discount_cb(0.0, 1.0) - 1.0) < 1e-10

    def test_positive_rate_less_than_one(self):
        assert bs_discount_cb(0.05, 1.0) < 1.0

    def test_matches_exp(self):
        for rv in [0.01, 0.05, 0.10, 0.20]:
            for tv in [0.5, 1.0, 2.0]:
                assert abs(bs_discount_cb(rv, tv) - math.exp(-rv * tv)) < 1e-12

    def test_deml_node_count(self):
        entry = FINANCE_CATALOG["bs_discount"]
        assert entry["n_nodes"] == 1
        assert entry["backend"] == "DEML"


# ── bs_log_moneyness_cb ───────────────────────────────────────────────────────

class TestBsLogMoneyness:
    def test_atm_is_zero(self):
        assert abs(bs_log_moneyness_cb(100.0, 100.0)) < 1e-12

    def test_itm_positive(self):
        assert bs_log_moneyness_cb(110.0, 100.0) > 0

    def test_otm_negative(self):
        assert bs_log_moneyness_cb(90.0, 100.0) < 0

    def test_matches_log(self):
        for s in [80.0, 100.0, 120.0]:
            for k in [90.0, 100.0, 110.0]:
                assert abs(bs_log_moneyness_cb(s, k) - math.log(s / k)) < 1e-12

    def test_eml_node_count(self):
        entry = FINANCE_CATALOG["bs_log_moneyness"]
        assert entry["n_nodes"] == 3
        assert entry["backend"] == "EML"


# ── bs_d1_cb and bs_d2_cb ─────────────────────────────────────────────────────

class TestBsD1D2:
    def test_d2_equals_d1_minus_sigma_sqrt_t(self):
        d1 = bs_d1_cb(S, K, r, T, sigma)
        d2 = bs_d2_cb(S, K, r, T, sigma)
        assert abs(d2 - (d1 - sigma * math.sqrt(T))) < 1e-12

    def test_atm_d1_positive(self):
        d1 = bs_d1_cb(100.0, 100.0, 0.05, 1.0, 0.20)
        assert d1 > 0

    def test_deep_itm_d1_large(self):
        d1 = bs_d1_cb(200.0, 100.0, 0.05, 1.0, 0.20)
        assert d1 > 2.0

    def test_deep_otm_d1_negative(self):
        d1 = bs_d1_cb(50.0, 200.0, 0.05, 1.0, 0.20)
        assert d1 < -2.0


# ── bs_call_eml ───────────────────────────────────────────────────────────────

class TestBsCallEml:
    def test_matches_reference_atm(self):
        eml_c = bs_call_eml(S, K, r, T, sigma)
        ref_c = black_scholes_call(S, K, r, T, sigma)
        assert abs(eml_c - ref_c) < 1e-10

    def test_matches_reference_itm(self):
        eml_c = bs_call_eml(120.0, 100.0, r, T, sigma)
        ref_c = black_scholes_call(120.0, 100.0, r, T, sigma)
        assert abs(eml_c - ref_c) < 1e-10

    def test_matches_reference_otm(self):
        eml_c = bs_call_eml(80.0, 100.0, r, T, sigma)
        ref_c = black_scholes_call(80.0, 100.0, r, T, sigma)
        assert abs(eml_c - ref_c) < 1e-10

    def test_expired_intrinsic(self):
        c = bs_call_eml(110.0, 100.0, r, 0.0, sigma)
        assert abs(c - 10.0) < 1e-10


# ── bs_components_eml ─────────────────────────────────────────────────────────

class TestBsComponentsEml:
    def setup_method(self):
        self.comp = bs_components_eml()

    def test_returns_dict(self):
        assert isinstance(self.comp, dict)

    def test_has_all_keys(self):
        for key in ("discount", "log_moneyness", "d1", "d2", "N_d1", "N_d2",
                    "call_price", "eml_components"):
            assert key in self.comp

    def test_discount_is_exp_minusrT(self):
        assert abs(self.comp["discount"] - math.exp(-0.05 * 1.0)) < 1e-12

    def test_log_moneyness_atm_zero(self):
        assert abs(self.comp["log_moneyness"]) < 1e-12

    def test_normals_between_zero_and_one(self):
        assert 0 < self.comp["N_d1"] < 1
        assert 0 < self.comp["N_d2"] < 1

    def test_call_price_known_range(self):
        assert 10.0 < self.comp["call_price"] < 11.0

    def test_eml_components_has_tree_descriptions(self):
        ec = self.comp["eml_components"]
        assert "discount_tree" in ec
        assert "deml" in ec["discount_tree"].lower()


# ── FINANCE_CATALOG ───────────────────────────────────────────────────────────

class TestFinanceCatalog:
    def test_catalog_non_empty(self):
        assert len(FINANCE_CATALOG) >= 4

    def test_all_entries_have_required_keys(self):
        for name, entry in FINANCE_CATALOG.items():
            for key in ("equation", "formula", "n_nodes", "backend", "max_abs_error", "notes"):
                assert key in entry, f"Missing '{key}' in FINANCE_CATALOG['{name}']"

    def test_discount_entry_exact(self):
        e = FINANCE_CATALOG["bs_discount"]
        assert e["max_abs_error"] == 0.0
        assert e["n_nodes"] == 1

    def test_call_price_entry_present(self):
        assert "bs_call_price" in FINANCE_CATALOG

    def test_backends_valid(self):
        valid = {"DEML", "EML", "BEST", "CBEST", "EXL", "BEST+DEML+CBEST"}
        for name, entry in FINANCE_CATALOG.items():
            assert entry["backend"] in valid, f"Unknown backend in '{name}': {entry['backend']}"
