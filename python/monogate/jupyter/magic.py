"""IPython cell magic ``%%eml_witness``."""
from __future__ import annotations

from typing import Any

import sympy as sp


__all__ = ["EmlMagics"]


def _render(obj: Any) -> Any:
    """Build an IPython display object for a witness around ``obj``."""
    from IPython.display import HTML

    from ..witness import universality_witness

    if not isinstance(obj, sp.Basic):
        return HTML(    # type: ignore[no-untyped-call]
            f"<div style='color:#c66;font-family:sans-serif;'>"
            f"%%eml_witness: cell did not return a SymPy expression "
            f"(got <code>{type(obj).__name__}</code>)."
            f"</div>"
        )
    try:
        w = universality_witness(obj)
    except Exception as exc:
        return HTML(    # type: ignore[no-untyped-call]
            f"<div style='color:#c66;font-family:sans-serif;'>"
            f"%%eml_witness: universality_witness failed - "
            f"<code>{type(exc).__name__}: {exc}</code>"
            f"</div>"
        )
    from ._formatter import render_witness_html
    return HTML(render_witness_html(w))    # type: ignore[no-untyped-call]


def _make_magics_class() -> Any:
    """Construct the EmlMagics class lazily so we don't require
    IPython at import time of this module."""
    from IPython.core.magic import Magics, cell_magic, magics_class

    @magics_class
    class _EmlMagics(Magics):
        @cell_magic
        def eml_witness(self, _line: str, cell: str) -> Any:    # noqa: D401
            """Evaluate the cell as an expression and show its EML witness."""
            if self.shell is None:
                raise RuntimeError(
                    "%%eml_witness requires an active IPython shell."
                )
            obj = self.shell.ev(cell.strip())   # type: ignore[no-untyped-call]
            return _render(obj)

    return _EmlMagics


def __getattr__(name: str) -> Any:    # pragma: no cover — IPython-only path
    if name == "EmlMagics":
        return _make_magics_class()
    raise AttributeError(name)
