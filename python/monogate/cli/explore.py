"""monogate.cli.explore — argparse CLI for the EML substrate.

Subcommands:

    monogate-explore witness EXPR      pretty-print the universality witness
    monogate-explore analyze EXPR      Pfaffian profile only
    monogate-explore identify EXPR     registry matches only
    monogate-explore class AXES        every member of an equivalence class
    monogate-explore corpus FILE       cluster a file of one-expr-per-line
    monogate-explore example NAME      run a built-in demo

Composes :func:`monogate.witness.universality_witness` plus the
existing eml-* APIs (`eml_cost.analyze`, `eml_discover.identify`,
`eml_graph.build_graph`).

Originally shipped as the standalone ``eml-explore`` package; folded
into monogate in 2.4.0 with the standalone repo archived. Both
``monogate-explore`` and ``eml-explore`` are registered as console
entry points so existing scripts that call ``eml-explore ...``
keep working.

Optional dependency: this module is gated on the ``[cli]`` extra,
which pulls ``[witness]`` plus ``eml-graph``.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable, Sequence

import sympy as sp

from eml_cost import analyze, fingerprint, fingerprint_axes
from eml_discover import identify

from ..witness import universality_witness, witness_to_dict


__all__ = ["main", "build_parser", "EXAMPLES"]


# ---------- helpers ----------------------------------------------------------


def _emit(args: argparse.Namespace, text: str, payload: dict[str, Any]) -> None:
    if args.json:
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(text)


def _parse_expr(s: str) -> sp.Basic:
    try:
        result: sp.Basic = sp.sympify(s)
        return result
    except Exception as exc:
        raise ValueError(f"could not parse expression {s!r}: {exc}") from exc


# ---------- subcommands ------------------------------------------------------


def cmd_analyze(args: argparse.Namespace) -> int:
    expr = _parse_expr(args.expr)
    a = analyze(expr)
    fp = fingerprint(expr)
    axes = fingerprint_axes(expr)
    text = (
        f"expression: {expr}\n"
        f"  predicted_depth:    {a.predicted_depth}\n"
        f"  pfaffian_r:         {a.pfaffian_r}\n"
        f"  max_path_r:         {a.max_path_r}\n"
        f"  eml_depth:          {a.eml_depth}\n"
        f"  structural_overhead:{a.structural_overhead}\n"
        f"  corrections:        c_osc={a.corrections.c_osc} "
        f"c_composite={a.corrections.c_composite} "
        f"delta_fused={a.corrections.delta_fused}\n"
        f"  fingerprint:        {fp}\n"
        f"  axes:               {axes}\n"
        f"  Pfaffian-not-EML:   {a.is_pfaffian_not_eml}"
    )
    payload = {
        "expr": str(expr),
        "predicted_depth": a.predicted_depth,
        "pfaffian_r": a.pfaffian_r,
        "max_path_r": a.max_path_r,
        "eml_depth": a.eml_depth,
        "structural_overhead": a.structural_overhead,
        "corrections": {
            "c_osc": a.corrections.c_osc,
            "c_composite": a.corrections.c_composite,
            "delta_fused": a.corrections.delta_fused,
        },
        "fingerprint": fp,
        "axes": axes,
        "is_pfaffian_not_eml": a.is_pfaffian_not_eml,
    }
    _emit(args, text, payload)
    return 0


def cmd_identify(args: argparse.Namespace) -> int:
    expr = _parse_expr(args.expr)
    matches = identify(expr, max_results=args.max)
    if not matches:
        text = f"no registry match for {expr}"
        _emit(args, text, {"expr": str(expr), "matches": []})
        return 0
    text_lines = [f"matches for {expr}:"]
    payload_matches: list[dict[str, Any]] = []
    for m in matches:
        text_lines.append(
            f"  - {m.formula.name}  ({m.confidence})  "
            f"[{getattr(m.formula, 'domain', '')}]"
        )
        payload_matches.append({
            "name": m.formula.name,
            "confidence": m.confidence,
            "domain": getattr(m.formula, "domain", ""),
            "citation": getattr(m.formula, "citation", ""),
            "description": getattr(m.formula, "description", ""),
        })
    _emit(args, "\n".join(text_lines), {"expr": str(expr), "matches": payload_matches})
    return 0


def cmd_witness(args: argparse.Namespace) -> int:
    expr = _parse_expr(args.expr)
    w = universality_witness(expr, walk_canonical=not args.no_walk)
    if args.json:
        print(json.dumps(witness_to_dict(w), indent=2, default=str))
        return 0
    lines = [f"witness for {w.input_expr_str}", "=" * 60]
    lines.append(f"  predicted_depth:    {w.profile.predicted_depth}")
    lines.append(f"  pfaffian_r:         {w.profile.pfaffian_r}")
    lines.append(f"  max_path_r:         {w.profile.max_path_r}")
    lines.append(f"  eml_depth:          {w.profile.eml_depth}")
    lines.append(f"  fingerprint:        {w.profile.fingerprint}")
    lines.append(f"  axes:               {w.profile.axes}")
    lines.append(f"  Pfaffian-not-EML:   {w.profile.is_pfaffian_not_eml}")
    lines.append("")
    if w.identified is not None:
        lines.append(
            f"  identified:         {w.identified.name} "
            f"({w.identified.confidence}) [{w.identified.domain}]"
        )
        if w.identified.citation:
            lines.append(f"  citation:           {w.identified.citation}")
    else:
        lines.append("  identified:         (no registry match)")
    if w.canonical_path:
        lines.append("")
        lines.append("  canonical-equivalent path:")
        for i, step in enumerate(w.canonical_path):
            arrow = "    " if i == 0 else "  > "
            lines.append(f"{arrow}{step.pattern_name:<28} cost={step.cost}  {step.expression_str}")
        lines.append(f"  savings:            {w.savings}")
    lines.append("")
    if w.verified_in_lean:
        lines.append(f"  Lean-verified:      yes  ({w.lean_url})")
    else:
        lines.append("  Lean-verified:      pending  (input outside EML class)")
    print("\n".join(lines))
    return 0


def cmd_class(args: argparse.Namespace) -> int:
    """Print every registry formula whose axes match the given string."""
    from eml_discover import FORMULAS

    target = args.axes.strip()
    members: list[dict[str, str]] = []
    for f in FORMULAS:
        try:
            ax = fingerprint_axes(f.expression_factory())
        except Exception:
            continue
        if ax == target:
            members.append({
                "name": f.name,
                "domain": getattr(f, "domain", ""),
                "citation": getattr(f, "citation", ""),
            })
    if not members:
        text = f"no registry formula in cost class {target}"
        _emit(args, text, {"axes": target, "members": []})
        return 0
    lines = [f"cost class {target}  ({len(members)} member(s)):"]
    for m in members:
        lines.append(f"  - {m['name']}  [{m['domain']}]")
    _emit(args, "\n".join(lines), {"axes": target, "members": members})
    return 0


def cmd_corpus(args: argparse.Namespace) -> int:
    """Read a file with one expression per line and cluster the corpus."""
    from eml_graph import build_graph

    with open(args.file, "r", encoding="utf-8") as f:
        raw_lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]

    parsed: list[sp.Basic] = []
    skipped: list[str] = []
    for s in raw_lines:
        try:
            parsed.append(sp.sympify(s))
        except Exception:
            skipped.append(s)

    g = build_graph(parsed, label_with_discover=True)
    sizes = g.class_sizes()

    text_lines = [
        f"corpus: {args.file}",
        f"  parsed:        {len(parsed)} / {len(raw_lines)} lines",
        f"  skipped:       {len(skipped)}",
        f"  nodes:         {g.num_nodes()}",
        f"  cost classes:  {g.num_classes()}",
        f"  largest class: {sizes[0] if sizes else 0}",
        "",
        f"top {args.top} class sizes:",
    ]
    top_axes_summary: list[dict[str, Any]] = []
    cls_items = sorted(g.classes.items(),
                       key=lambda kv: -len(kv[1].members))[:args.top]
    for axes, cls in cls_items:
        members_repr = []
        for idx in cls.members[:5]:
            label = g.nodes[idx].label or str(g.nodes[idx].expression)[:40]
            members_repr.append(label)
        text_lines.append(
            f"  {axes:30s} ({len(cls.members)})  e.g.: {', '.join(members_repr)}"
        )
        top_axes_summary.append({
            "axes": axes,
            "size": len(cls.members),
            "examples": members_repr,
        })

    _emit(args, "\n".join(text_lines), {
        "file": args.file,
        "parsed_count": len(parsed),
        "skipped_count": len(skipped),
        "graph_nodes": g.num_nodes(),
        "graph_classes": g.num_classes(),
        "top_classes": top_axes_summary,
    })
    return 0


# ---------- examples ---------------------------------------------------------


def example_cross_domain(args: argparse.Namespace) -> int:
    """Demo: Stefan-Boltzmann + perpetuity + kinetic-energy + Coulomb +
    de-Broglie all collapse into the same Pfaffian cost class."""
    targets = [
        ("Stefan-Boltzmann (sigma * T^4)", "sigma_sb * T**4"),
        ("perpetuity (C / r)",              "C / r"),
        ("kinetic energy (m * v^2 / 2)",    "m * v**2 / 2"),
        ("Coulomb's law (k * q1 * q2 / r)", "k_const * q1 * q2 / r"),
        ("de Broglie wavelength (h / p)",   "h / p"),
    ]
    text_lines = [
        "Cross-domain demo - formulas across physics, GR, finance",
        "all collapse into the same Pfaffian cost axes.",
        "",
    ]
    payload_rows: list[dict[str, Any]] = []
    seen_axes: set[str] = set()
    for label, src in targets:
        try:
            expr = sp.sympify(src)
            axes = fingerprint_axes(expr)
        except Exception:
            text_lines.append(f"  ({label} failed to parse)")
            continue
        seen_axes.add(axes)
        text_lines.append(f"  {label:40s}  axes={axes}")
        payload_rows.append({"label": label, "axes": axes, "expr": str(expr)})
    text_lines.append("")
    text_lines.append(
        f"distinct axes seen: {len(seen_axes)} (collapse ratio "
        f"{len(targets) / max(len(seen_axes), 1):.1f}x)"
    )
    _emit(args, "\n".join(text_lines), {
        "example": "cross-domain",
        "rows": payload_rows,
        "distinct_axes": len(seen_axes),
        "collapse_ratio": round(len(targets) / max(len(seen_axes), 1), 2),
    })
    return 0


def example_witness_walkthrough(args: argparse.Namespace) -> int:
    """Demo: run the witness pipeline on three illustrative expressions."""
    targets = [
        ("textbook sigmoid",  "exp(x) / (1 + exp(x))"),
        ("Pythagorean LHS",   "sin(x)**2 + cos(x)**2"),
        ("nested Bessel",     "besselj(0, x)"),
    ]
    text_lines = ["Witness walkthrough - three expressions, three behaviours.", ""]
    payload_rows: list[dict[str, Any]] = []
    for label, src in targets:
        w = universality_witness(src)
        text_lines.append(f"  --- {label} ---")
        text_lines.append(f"    expr:      {w.input_expr_str}")
        text_lines.append(f"    cost:      d={w.profile.predicted_depth}, r={w.profile.pfaffian_r}")
        if w.identified:
            text_lines.append(f"    matched:   {w.identified.name} ({w.identified.confidence})")
        else:
            text_lines.append("    matched:   (none)")
        if w.canonical_path:
            text_lines.append(
                f"    walked:    {len(w.canonical_path) - 1} step(s) "
                f"to {w.canonical_path[-1].expression_str}  "
                f"(savings={w.savings})"
            )
        elif w.profile.is_pfaffian_not_eml:
            text_lines.append("    walked:    n/a (Pfaffian-not-EML)")
        else:
            text_lines.append("    walked:    already canonical")
        text_lines.append("")
        payload_rows.append(witness_to_dict(w))
    _emit(args, "\n".join(text_lines), {
        "example": "witness-walkthrough",
        "rows": payload_rows,
    })
    return 0


EXAMPLES: dict[str, Callable[[argparse.Namespace], int]] = {
    "cross-domain":         example_cross_domain,
    "witness-walkthrough":  example_witness_walkthrough,
}


def cmd_example(args: argparse.Namespace) -> int:
    fn = EXAMPLES[args.name]
    return fn(args)


# ---------- argparse ---------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    from .. import __version__ as monogate_version

    parser = argparse.ArgumentParser(
        prog="monogate-explore",
        description=(
            "Cross-domain explorer for the EML substrate. Composes "
            "fingerprint, identify, path, build_graph, and "
            "universality_witness through one CLI."
        ),
    )
    parser.add_argument(
        "--version", action="version",
        version=f"monogate-explore (monogate {monogate_version})",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit JSON output instead of human-readable text.",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_w = sub.add_parser("witness",  help="Universality witness for an expression.")
    p_w.add_argument("expr")
    p_w.add_argument("--no-walk", action="store_true",
                     help="Skip the canonical-equivalent walk (faster).")
    p_w.set_defaults(func=cmd_witness)

    p_a = sub.add_parser("analyze",  help="Pfaffian profile of an expression.")
    p_a.add_argument("expr")
    p_a.set_defaults(func=cmd_analyze)

    p_i = sub.add_parser("identify", help="Registry matches for an expression.")
    p_i.add_argument("expr")
    p_i.add_argument("--max", type=int, default=5)
    p_i.set_defaults(func=cmd_identify)

    p_c = sub.add_parser("class",    help="Members of a Pfaffian-axes equivalence class.")
    p_c.add_argument("axes")
    p_c.set_defaults(func=cmd_class)

    p_corpus = sub.add_parser("corpus", help="Cluster a file of one-expr-per-line.")
    p_corpus.add_argument("file")
    p_corpus.add_argument("--top", type=int, default=10)
    p_corpus.set_defaults(func=cmd_corpus)

    p_e = sub.add_parser("example", help="Run a built-in demo.")
    p_e.add_argument("name", choices=sorted(EXAMPLES.keys()))
    p_e.set_defaults(func=cmd_example)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("aborted.", file=sys.stderr)
        return 130
    except Exception as exc:
        if getattr(args, "json", False):
            print(json.dumps({"error": str(exc), "type": type(exc).__name__}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
