"""monogate.PUBLIC_API — curated 50-export reference.

monogate exports 200+ names for backward compatibility. New users
should start here: a curated list of the ~50 functions/classes that
cover 95% of typical use.

Use ``from monogate import X`` for any of these. The full API remains
importable; this is a documentation guide, not a restriction.

Created in E-189 (2026-04-26).
"""
from __future__ import annotations

PUBLIC_API: dict[str, list[str]] = {
    "Core EML operators (positive-domain)": [
        "op",            # the bare eml(x, y) = exp(x) - log(y)
        "exp_eml",       # 1-node exp
        "ln_eml",        # multi-node log
        "neg_eml",       # negation
        "add_eml",       # addition
        "sub_eml",       # subtraction
        "mul_eml",       # multiplication
        "div_eml",       # division
        "recip_eml",     # reciprocal
        "pow_eml",       # power
    ],
    "EDL family (better division/multiplication)": [
        "exp_edl",
        "ln_edl",
        "neg_edl",
        "div_edl",
        "mul_edl",
        "recip_edl",
        "pow_edl",
        "EDL_ONE",
        "EDL_NEG_ONE",
    ],
    "EXL family (better power)": [
        "ln_exl",
        "pow_exl",
        "EXL",
    ],
    "Hybrid + comparison": [
        "BEST",
        "HybridOperator",
        "Operator",
        "compare_op",
    ],
    "SymPy bridge (E-186)": [
        "from_sympy",
        "to_sympy",
        "node_count",
        "verify_identity",
        "PfaffianNotEMLError",
        "simplify_eml",
        "latex_eml",
    ],
    "End-to-end pipeline (E-188)": [
        "pipeline",
        "pipeline_batch",
        "PipelineResult",
    ],
    "Catalogs": [
        "IDENTITIES",
        "ALL_OPERATORS",
        "ALL_IDENTITIES",
    ],
}


def list_public_api() -> None:
    """Print the curated public API."""
    print("monogate — curated public API")
    print("=" * 60)
    for category, names in PUBLIC_API.items():
        print(f"\n{category}:")
        for name in names:
            print(f"  - {name}")
    total = sum(len(v) for v in PUBLIC_API.values())
    print(f"\n{total} curated names. Full API: 200+ for backward compat.")


if __name__ == "__main__":
    list_public_api()
