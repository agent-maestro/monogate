"""Display formatters and IPython cell magic for the EML substrate."""
from __future__ import annotations

from typing import Any

import sympy as sp

from ..witness import UniversalityWitness, universality_witness


__all__ = [
    "install_display_formatter",
    "uninstall_display_formatter",
    "render_witness_html",
    "render_witness_text",
    "load_ipython_extension",
    "unload_ipython_extension",
]


# ----- public rendering helpers (callable from anywhere) ---------------------


def render_witness_text(w: UniversalityWitness) -> str:
    """One-line text summary suitable for the basic display formatter."""
    bits: list[str] = []
    bits.append(f"d={w.profile.predicted_depth}")
    bits.append(f"r={w.profile.pfaffian_r}")
    if w.identified is not None:
        bits.append(f"id: {w.identified.name} ({w.identified.confidence})")
    if w.profile.is_pfaffian_not_eml:
        bits.append("Pfaffian-not-EML")
    if w.verified_in_lean:
        bits.append("Lean-verified")
    return "[EML  " + "  ".join(bits) + "]"


def _severity_bg(w: UniversalityWitness) -> str:
    if w.profile.is_pfaffian_not_eml or w.profile.predicted_depth >= 5:
        return "#5a2222"  # high
    if w.profile.predicted_depth >= 3:
        return "#5a4422"  # mid
    return "#1f3a1f"      # low


def render_witness_html(w: UniversalityWitness) -> str:
    """Full HTML rendering with Pfaffian profile + identification.

    Self-contained; no external CSS / JS / images.
    """
    bg = _severity_bg(w)
    profile_rows = [
        ("predicted_depth", w.profile.predicted_depth),
        ("pfaffian_r", w.profile.pfaffian_r),
        ("max_path_r", w.profile.max_path_r),
        ("eml_depth", w.profile.eml_depth),
        ("structural_overhead", w.profile.structural_overhead),
        ("c_osc / c_composite / delta_fused",
         f"{w.profile.c_osc} / {w.profile.c_composite} / {w.profile.delta_fused}"),
        ("fingerprint", w.profile.fingerprint),
        ("axes", w.profile.axes),
    ]
    rows_html = "".join(
        f"<tr><td style='padding:2px 8px;color:#aaa;'>{k}</td>"
        f"<td style='padding:2px 8px;font-family:monospace;color:#eee;'>{v}</td></tr>"
        for k, v in profile_rows
    )

    ident_html = ""
    if w.identified is not None:
        ident_html = (
            f"<div style='margin-top:6px;padding:6px 10px;"
            f"background:#1a2a3a;border-left:3px solid #4a7aaa;color:#e8eef4;"
            f"font-family:sans-serif;'>"
            f"<b>{_escape(w.identified.name)}</b> "
            f"<span style='color:#9ab;font-size:90%;'>"
            f"({_escape(w.identified.confidence)} - {_escape(w.identified.domain)})"
            f"</span>"
            + (f"<br><span style='color:#aab;font-size:88%;'>"
               f"{_escape(w.identified.description)}</span>"
               if w.identified.description else "")
            + "</div>"
        )

    path_html = ""
    if w.canonical_path:
        path_rows = "".join(
            f"<tr><td style='padding:2px 8px;color:#888;font-family:monospace;'>"
            f"{_escape(step.pattern_name)}</td>"
            f"<td style='padding:2px 8px;color:#aaa;'>cost={step.cost}</td>"
            f"<td style='padding:2px 8px;font-family:monospace;color:#dde;'>"
            f"{_escape(step.expression_str)}</td></tr>"
            for step in w.canonical_path
        )
        path_html = (
            f"<div style='margin-top:6px;'>"
            f"<div style='color:#aaa;font-family:sans-serif;font-size:90%;'>"
            f"canonical path (savings: {w.savings})"
            f"</div>"
            f"<table style='border-collapse:collapse;font-size:85%;'>{path_rows}</table>"
            f"</div>"
        )

    if w.verified_in_lean:
        lean_url = w.lean_url or ""
        lean_html = (
            f"<div style='margin-top:6px;padding:4px 8px;"
            f"background:#0a3a1a;color:#7df;font-family:sans-serif;font-size:88%;'>"
            f"Lean-verified - "
            f"<a href='{_escape(lean_url)}' style='color:#7df;'>source</a>"
            f"</div>"
        )
    else:
        lean_html = (
            f"<div style='margin-top:6px;padding:4px 8px;"
            f"background:#222;color:#888;font-family:sans-serif;font-size:88%;'>"
            f"Lean-verified: pending  "
            f"(input outside the EML class the universality theorem covers)"
            f"</div>"
        )

    return (
        f"<div style='border-left:4px solid {bg};padding:8px 12px;"
        f"margin-top:4px;background:#15161a;color:#dde;"
        f"font-family:sans-serif;border-radius:0 4px 4px 0;'>"
        f"<div style='color:#888;font-size:88%;font-family:sans-serif;'>"
        f"EML witness for "
        f"<code style='color:#cef;'>{_escape(w.input_expr_str)}</code>"
        f"</div>"
        f"<table style='border-collapse:collapse;margin-top:4px;'>{rows_html}</table>"
        f"{ident_html}"
        f"{path_html}"
        f"{lean_html}"
        f"</div>"
    )


def _escape(s: str) -> str:
    """Minimal HTML escape for safety."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


# ----- IPython integration --------------------------------------------------


_installed = False


def _format_basic_text(obj: Any, p: Any, cycle: bool) -> None:
    """Plain-text formatter following IPython's ``(obj, p, cycle)``
    pretty-printer convention."""
    if not isinstance(obj, sp.Basic):
        return
    if cycle:
        p.text(f"<EMLcycle: {type(obj).__name__}>")
        return
    try:
        w = universality_witness(obj)
        p.text(f"{obj}\n{render_witness_text(w)}")
    except Exception:
        p.text(str(obj))


def _format_basic_html(obj: Any) -> str | None:
    if not isinstance(obj, sp.Basic):
        return None
    try:
        w = universality_witness(obj)
    except Exception:
        return None
    try:
        latex = sp.latex(obj)
        head = f"<div>$${latex}$$</div>"
    except Exception:
        head = f"<div><code>{_escape(str(obj))}</code></div>"
    return head + render_witness_html(w)


def install_display_formatter(ip: Any) -> None:
    """Install the EML formatters on a given IPython InteractiveShell.

    Idempotent."""
    global _installed
    if _installed:
        return
    text_fmt = ip.display_formatter.formatters["text/plain"]
    html_fmt = ip.display_formatter.formatters["text/html"]
    text_fmt.for_type(sp.Basic, _format_basic_text)
    html_fmt.for_type(sp.Basic, _format_basic_html)
    # Terminal IPython ships text/html disabled (no rich display);
    # rich notebook frontends enable it automatically. We force-enable
    # so the formatter still emits in tests / programmatic calls.
    html_fmt.enabled = True
    _installed = True


def uninstall_display_formatter(ip: Any) -> None:
    """Remove the EML formatters from the given InteractiveShell."""
    global _installed
    if not _installed:
        return
    text_fmt = ip.display_formatter.formatters["text/plain"]
    html_fmt = ip.display_formatter.formatters["text/html"]
    try:
        text_fmt.pop(sp.Basic)
    except (KeyError, AttributeError):
        pass
    try:
        html_fmt.pop(sp.Basic)
    except (KeyError, AttributeError):
        pass
    _installed = False


def load_ipython_extension(ip: Any) -> None:
    """Hook called by ``%load_ext monogate.jupyter``."""
    install_display_formatter(ip)
    try:
        from .magic import EmlMagics
        ip.register_magics(EmlMagics)
    except Exception:
        pass


def unload_ipython_extension(ip: Any) -> None:
    """Hook called by ``%unload_ext monogate.jupyter``."""
    uninstall_display_formatter(ip)
