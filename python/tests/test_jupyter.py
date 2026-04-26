"""Tests for monogate.jupyter (folded in from eml-jupyter 0.1.2 in monogate 2.4.0)."""
from __future__ import annotations

import re

import pytest
import sympy as sp

pytest.importorskip("eml_cost")
pytest.importorskip("eml_discover")
pytest.importorskip("eml_rewrite")

from monogate.jupyter import (   # noqa: E402
    install_display_formatter,
    render_witness_html,
    render_witness_text,
    uninstall_display_formatter,
)
from monogate.witness import universality_witness   # noqa: E402


x = sp.Symbol("x")


def test_render_witness_text_includes_depth():
    w = universality_witness("1/(1+exp(-x))")
    s = render_witness_text(w)
    assert s.startswith("[EML")
    assert s.endswith("]")
    assert "d=" in s
    assert "r=" in s


def test_render_witness_text_includes_lean_when_verified():
    """sin(x) is in the EML class — Lean-verified badge present."""
    w = universality_witness("sin(x)")
    s = render_witness_text(w)
    assert "Lean-verified" in s


def test_render_witness_text_omits_lean_for_pfaffian_not_eml():
    """Bessel is OUTSIDE the EML class — no Lean-verified badge."""
    w = universality_witness(sp.besselj(0, x))
    s = render_witness_text(w)
    assert "Lean-verified" not in s


def test_render_witness_html_returns_div():
    w = universality_witness("sin(x)")
    h = render_witness_html(w)
    assert h.startswith("<div")
    assert h.rstrip().endswith("</div>")


def test_render_witness_html_includes_input_expr():
    w = universality_witness("exp(sin(x))")
    h = render_witness_html(w)
    assert "exp(sin(x))" in h


def test_render_witness_html_includes_pfaffian_axes():
    w = universality_witness("sin(x)")
    h = render_witness_html(w)
    assert "fingerprint" in h
    assert "axes" in h
    assert re.search(r"p\d+-d\d+-w\d+-c-?\d+", h) is not None


def test_render_witness_html_shows_lean_verified_for_eml_class():
    w = universality_witness("sin(x)")
    h = render_witness_html(w)
    assert "Lean-verified" in h
    assert "pending" not in h


def test_render_witness_html_shows_lean_pending_for_pfaffian_not_eml():
    w = universality_witness(sp.besselj(0, x))
    h = render_witness_html(w)
    assert "pending" in h


def test_render_witness_html_high_severity_color_on_bessel():
    w = universality_witness(sp.besselj(0, x))
    h = render_witness_html(w)
    assert "5a2222" in h


def test_render_witness_html_low_severity_color_on_canonical_sigmoid():
    w = universality_witness("1/(1+exp(-x))")
    h = render_witness_html(w)
    assert "1f3a1f" in h


def test_render_witness_html_includes_canonical_path_for_textbook_sigmoid():
    w = universality_witness(sp.exp(x) / (1 + sp.exp(x)))
    h = render_witness_html(w)
    assert "canonical path" in h
    assert "savings" in h


def _has_ipython() -> bool:
    try:
        import IPython   # noqa: F401
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _has_ipython(), reason="IPython not installed")
def test_install_uninstall_idempotent():
    from IPython.testing.globalipapp import get_ipython
    ip = get_ipython()
    install_display_formatter(ip)
    install_display_formatter(ip)
    uninstall_display_formatter(ip)
    uninstall_display_formatter(ip)


@pytest.mark.skipif(not _has_ipython(), reason="IPython not installed")
def test_text_formatter_decorates_sympy_basic():
    from IPython.testing.globalipapp import get_ipython
    ip = get_ipython()
    install_display_formatter(ip)
    try:
        format_dict, _ = ip.display_formatter.format(sp.sin(x))
        text = format_dict.get("text/plain", "")
        assert "[EML" in text
    finally:
        uninstall_display_formatter(ip)


@pytest.mark.skipif(not _has_ipython(), reason="IPython not installed")
def test_html_formatter_decorates_sympy_basic():
    from IPython.testing.globalipapp import get_ipython
    ip = get_ipython()
    install_display_formatter(ip)
    try:
        format_dict, _ = ip.display_formatter.format(sp.sin(x))
        html = format_dict.get("text/html", "")
        assert "<div" in html
        assert "fingerprint" in html
    finally:
        uninstall_display_formatter(ip)
