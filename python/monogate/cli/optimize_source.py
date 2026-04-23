"""SuperBEST source-to-source annotator.

Reads a Python file, finds every math expression involving
`math.*` / `numpy.*` / `np.*` unary calls + arithmetic operators, and
appends a machine-readable annotation block above each analysed
expression with the SuperBEST cost breakdown.

This is NOT a rewriter (yet) — it leaves the code semantically
unchanged and only ADDS comments.  A pure comment-annotation pass is
safe to run on any Python module; a true rewriter is future work.

Usage:
    python -m monogate.cli.optimize_source myfile.py
    python -m monogate.cli.optimize_source myfile.py --inplace
    python -m monogate.cli.optimize_source myfile.py --json
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

from .expr_optimizer import analyse


def has_math_tokens(src: str) -> bool:
    return any(tok in src for tok in (
        "math.", "numpy.", "np.", "torch.", "exp(", "log(", "sqrt("
    ))


def strip_ns(expr: str) -> str:
    return (expr
            .replace("math.", "")
            .replace("numpy.", "")
            .replace("np.", "")
            .replace("torch.", ""))


def analyse_source(src: str) -> list[dict]:
    """Return a list of {lineno, snippet, analysis} for every math-bearing
    expression in the source."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    reports: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Expr, ast.Assign, ast.AnnAssign, ast.Return)):
            continue
        try:
            snippet = ast.get_source_segment(src, node)
        except Exception:
            continue
        if not snippet:
            continue
        if not has_math_tokens(snippet):
            continue
        # Try to analyse the RHS of assignment or the plain expression
        target: str
        if isinstance(node, ast.Return) and node.value is not None:
            try:
                target = ast.get_source_segment(src, node.value) or ""
            except Exception:
                continue
        elif isinstance(node, ast.Assign):
            try:
                target = ast.get_source_segment(src, node.value) or ""
            except Exception:
                continue
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            try:
                target = ast.get_source_segment(src, node.value) or ""
            except Exception:
                continue
        elif isinstance(node, ast.Expr):
            try:
                target = ast.get_source_segment(src, node.value) or ""
            except Exception:
                continue
        else:
            continue
        if not target or not has_math_tokens(target):
            continue
        cleaned = strip_ns(target.strip())
        try:
            report = analyse(cleaned)
        except SyntaxError:
            continue
        reports.append({
            "lineno": getattr(node, "lineno", 0),
            "snippet": snippet,
            "analysed_expr": cleaned,
            "analysis": report,
        })
    return reports


def emit_annotations(src: str, reports: list[dict]) -> str:
    """Return new source with a SuperBEST annotation block inserted above
    each analysed expression.  Preserves line numbers ordering by
    annotating from bottom up."""
    lines = src.splitlines(keepends=False)
    for r in sorted(reports, key=lambda r: -r["lineno"]):
        rep = r["analysis"]
        indent_line = lines[r["lineno"] - 1] if r["lineno"] - 1 < len(lines) else ""
        indent = indent_line[:len(indent_line) - len(indent_line.lstrip())]
        comment = [
            f"{indent}# SuperBEST: {rep['naive_cost']}n naive -> {rep['superbest_cost']}n optimised "
            f"({rep['savings_pct_on_ops']}% saved; ELC {rep['elc_class']})",
        ]
        # Insert before the line (keep existing line)
        lines[r["lineno"] - 1: r["lineno"] - 1] = comment
    return "\n".join(lines) + ("\n" if src.endswith("\n") else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="SuperBEST source-code annotator")
    ap.add_argument("file", help="Python file to annotate")
    ap.add_argument("--inplace", action="store_true",
                    help="Write back to the source file (default: stdout)")
    ap.add_argument("--json", action="store_true",
                    help="Emit the raw report as JSON instead of annotated source")
    args = ap.parse_args(argv)

    p = Path(args.file)
    if not p.exists():
        print(f"file not found: {p}", file=sys.stderr); sys.exit(2)
    src = p.read_text(encoding="utf-8")
    reports = analyse_source(src)

    if args.json:
        sys.stdout.write(json.dumps({"file": str(p), "reports": reports},
                                     indent=2, ensure_ascii=False) + "\n")
        return

    annotated = emit_annotations(src, reports) if reports else src
    summary_line = (
        f"# SuperBEST annotator: {len(reports)} math expression(s) analysed; "
        + (f"aggregate savings "
           f"{sum(r['analysis']['naive_cost'] - r['analysis']['superbest_cost'] for r in reports)}n "
           f"out of {sum(r['analysis']['naive_cost'] for r in reports)}n naive"
           if reports else "no math expressions found")
        + "\n"
    )
    out_text = summary_line + annotated
    if args.inplace:
        p.write_text(out_text, encoding="utf-8")
        print(f"wrote {p}  ({len(reports)} annotations)", file=sys.stderr)
    else:
        sys.stdout.write(out_text)


if __name__ == "__main__":
    main()
