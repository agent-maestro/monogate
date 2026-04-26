"""monogate.jupyter — rich notebook display for the EML substrate.

Loading the extension installs an IPython display formatter that
augments every ``sp.Basic`` cell output with a Pfaffian profile
strip + identification badge underneath the usual LaTeX rendering.

    %load_ext monogate.jupyter

After that, evaluating any SymPy expression in a cell renders both
the math AND the EML annotation:

    >>> import sympy as sp
    >>> 1 / (1 + sp.exp(-sp.Symbol('x')))
    1/(1 + exp(-x))
    [EML  predicted_depth=2  pfaffian_r=1  id: sigmoid (canonical)  Lean-verified]

A cell magic is also registered:

    %%eml_witness
    1 / (1 + exp(-x))

This prints the full ``UniversalityWitness`` (profile + identification
+ canonical path + Lean-verified flag) in HTML form.

Originally shipped as the standalone ``eml-jupyter`` package; folded
into monogate in 2.4.0 with the standalone repo archived. The
old ``%load_ext eml_jupyter`` invocation continues to work via a
re-export module.

Optional dependency: this module is gated on the ``[jupyter]``
extra (which pulls ``[witness]`` plus ``ipython``).
"""
from __future__ import annotations

from ._formatter import (
    install_display_formatter,
    load_ipython_extension,
    render_witness_html,
    render_witness_text,
    uninstall_display_formatter,
    unload_ipython_extension,
)


__all__ = [
    "install_display_formatter",
    "uninstall_display_formatter",
    "render_witness_html",
    "render_witness_text",
    "load_ipython_extension",
    "unload_ipython_extension",
]
