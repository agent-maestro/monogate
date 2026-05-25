#!/usr/bin/env python3
"""Synchronize public SuperBEST surfaces with the canonical Python table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from monogate import superbest  # noqa: E402


TABLE_JSON_PATHS = [
    ROOT / "blog/src/data/superbest.json",
    ROOT / "python/results/superbest_v5_table.json",
]

CARD_PATHS = [
    ROOT / "capability_card_public.json",
    ROOT / "blog/public/capability_card.json",
    ROOT / "blog/public/.well-known/capcard.json",
]


POS_OPS = superbest.SUPERBEST_V52_POS_OPS
GEN_OPS = superbest.SUPERBEST_V52_GEN_OPS
POS_TOTAL = sum(superbest.SUPERBEST_COSTS_POS[op] for op in POS_OPS)
GEN_TOTAL = sum(superbest.SUPERBEST_COSTS_GEN[op] for op in GEN_OPS)
POS_NAIVE = sum(superbest.NAIVE_COSTS[op] for op in POS_OPS)
GEN_NAIVE = sum(superbest.NAIVE_COSTS[op] for op in GEN_OPS)
POS_SAVINGS = round((POS_NAIVE - POS_TOTAL) / POS_NAIVE * 100, 1)
GEN_SAVINGS = round((GEN_NAIVE - GEN_TOTAL) / GEN_NAIVE * 100, 1)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _op_key(op: str) -> str:
    return op.split("(", 1)[0].strip()


def sync_table(path: Path) -> None:
    data = load_json(path)
    data["version"] = "v5.3"
    data["date"] = "2026-05-24"
    data["revision"] = (
        "Canonical surface reconciliation v5.3 — Python/blog/browser/capability-card "
        "surfaces aligned to monogate.superbest library totals; positive headline "
        "14/73 and general 8-op basket 16/62."
    )

    for row in data.get("table", []):
        op = _op_key(row.get("op", ""))
        if op in superbest.SUPERBEST_COSTS_POS:
            row["cost_positive"] = superbest.SUPERBEST_COSTS_POS[op]
        if op in superbest.SUPERBEST_COSTS_GEN:
            row["cost_general"] = superbest.SUPERBEST_COSTS_GEN[op]
        if op == "div":
            row["construction_positive"] = "EXL(0,x) then ELSb(ln(x), y) = x/y, x > 0, y > 0"
            row["construction_general"] = (
                "3-node general-domain construction tracked by the Python canonical table; "
                "DivLowerBound3Full records the 3-node lower-bound status."
            )
            row["domain_positive"] = "x > 0, y > 0 — full-tree cost is 2n"
            row["domain_general"] = "general signed-real basket entry tracked at 3n"
            row["notes"] = "v5.3 canonical sync: div_positive=2n full tree; div_general=3n."
            row.pop("cost_note", None)
            row.pop("cost_positive_full_tree", None)
        if op == "mul":
            row["construction_positive"] = "ELMl(ln(x), y) = exp(ln(x) + ln(y)) = x*y for x,y > 0"
            row["construction_general"] = "3-node general-domain construction tracked by Python exact table."
            row["domain_positive"] = "x > 0, y > 0 — direct 1-node positive-domain F16 construction"
            row["domain_general"] = "general signed-real basket entry tracked at 3n"
            row["notes"] = "v5.3 canonical sync: mul_positive=1n; mul_general=3n."
        if op == "pow":
            row["cost_general"] = 3
        if op == "sqrt":
            row["cost_general"] = superbest.SUPERBEST_COSTS_GEN["sqrt"]

    data["totals"] = {
        "total_positive": {
            "value": POS_TOTAL,
            "formula": (
                "exp(1) + ln(1) + neg(2) + add(2) + sub(2) + mul(1) + "
                "div(2) + recip(1) + pow(1) + sqrt(1) = 14"
            ),
            "note": (
                "Canonical v5.3 full-tree positive-domain 10-op headline from "
                "monogate.superbest; no precomputed-ln shortcut accounting."
            ),
            "undefined_ops": [],
        },
        "total_general": {
            "value": GEN_TOTAL,
            "formula": "exp(1) + ln(1) + mul(3) + div(3) + neg(2) + add(2) + sub(2) + abs(2) = 16",
            "note": (
                "Canonical v5.3 general-domain headline is the 8-op basket used by "
                "monogate.superbest. recip/pow/sqrt remain row-level domain-caveat entries, "
                "not headline members."
            ),
            "undefined_ops": [],
            "excluded_from_sum": ["recip", "pow", "sqrt"],
        },
        "positive_headline": f"{POS_TOTAL}n / {POS_SAVINGS}% savings (positive domain, 10-op headline vs {POS_NAIVE}n naive)",
        "general_headline": f"{GEN_TOTAL}n / {GEN_SAVINGS}% savings (general domain, 8-op basket vs {GEN_NAIVE}n naive)",
        "savings_positive": {
            "naive_total": POS_NAIVE,
            "superbest_positive_total": POS_TOTAL,
            "savings_n": POS_NAIVE - POS_TOTAL,
            "savings_pct": f"{POS_SAVINGS}%",
            "formula": "(73 - 14) / 73 = 59/73 = 0.8082... ≈ 80.8%",
        },
        "savings_general": {
            "naive_total": GEN_NAIVE,
            "superbest_general_total": GEN_TOTAL,
            "savings_n": GEN_NAIVE - GEN_TOTAL,
            "savings_pct": f"{GEN_SAVINGS}%",
            "formula": "(62 - 16) / 62 = 46/62 = 0.7419... ≈ 74.2%",
        },
    }
    data["sum_v5_positive"] = POS_TOTAL
    data["savings_v5_3_positive"] = f"{POS_SAVINGS}%"
    data["savings_v5_3_general"] = f"{GEN_SAVINGS}%"
    data["canonical_sync"] = {
        "source": "python/monogate/superbest.py",
        "date": "2026-05-24",
        "positive_ops": list(POS_OPS),
        "general_ops": list(GEN_OPS),
        "positive_total": POS_TOTAL,
        "positive_naive_total": POS_NAIVE,
        "general_total": GEN_TOTAL,
        "general_naive_total": GEN_NAIVE,
    }
    write_json(path, data)


def sync_card(path: Path) -> None:
    data = load_json(path)
    for cap in data.get("capabilities", []):
        if cap.get("id") == "routing.superbest_v5":
            cap["name"] = "SuperBEST v5.3 routing table"
            cap["description"] = (
                "Routing table mapping 10 positive-domain arithmetic operations to F16 "
                "expressions, achieving 14n / 80.8% savings vs the 73n naive baseline, "
                "plus a general-domain 8-op basket at 16n / 74.2% savings vs the 62n "
                "naive baseline. Library, blog, browser, and capability-card surfaces "
                "are synchronized from monogate.superbest."
            )
            constraints = cap.setdefault("constraints", {})
            constraints.update(
                {
                    "total_nodes": POS_TOTAL,
                    "naive_total": POS_NAIVE,
                    "savings_percent": POS_SAVINGS,
                    "positive_total_nodes": POS_TOTAL,
                    "positive_naive_total": POS_NAIVE,
                    "positive_savings_percent": POS_SAVINGS,
                    "general_total_nodes": GEN_TOTAL,
                    "general_naive_total": GEN_NAIVE,
                    "general_savings_percent": GEN_SAVINGS,
                    "canonical_source": "python/monogate/superbest.py",
                }
            )

    for bench in data.get("benchmarks", []):
        if bench.get("id") == "bench.superbest_table":
            bench["name"] = "SuperBEST v5.3 routing table values"
            bench["notes"] = (
                "Headline: 14n positive-domain 10-op basket (80.8 percent vs 73n naive). "
                "General domain: 16n 8-op basket (74.2 percent vs 62n naive). "
                "Source: blog/src/data/superbest.json v5.3 synchronized from monogate.superbest."
            )
            bench["metric"] = "node_count_positive_domain"
            bench["value"] = POS_TOTAL
            bench.setdefault("reproducibility", {})["command"] = (
                "python python/scripts/sync_superbest_canonical.py --strict"
            )
    write_json(path, data)


def check_strict() -> None:
    for path in TABLE_JSON_PATHS:
        data = load_json(path)
        assert data["version"] == "v5.3"
        assert data["totals"]["total_positive"]["value"] == POS_TOTAL
        assert data["totals"]["total_general"]["value"] == GEN_TOTAL
        assert data["totals"]["savings_general"]["naive_total"] == GEN_NAIVE
        rows = {_op_key(row["op"]): row for row in data["table"]}
        assert rows["mul"]["cost_positive"] == 1
        assert rows["mul"]["cost_general"] == 3
        assert rows["div"]["cost_positive"] == 2
        assert rows["div"]["cost_general"] == 3
    for path in CARD_PATHS:
        data = load_json(path)
        cap = next(c for c in data["capabilities"] if c.get("id") == "routing.superbest_v5")
        assert cap["name"].endswith("v5.3 routing table")
        assert cap["constraints"]["general_total_nodes"] == GEN_TOTAL
        bench = next(b for b in data["benchmarks"] if b.get("id") == "bench.superbest_table")
        assert "16n" in bench["notes"] and "74.2" in bench["notes"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="verify synchronized values after writing")
    args = parser.parse_args()
    for path in TABLE_JSON_PATHS:
        sync_table(path)
    for path in CARD_PATHS:
        sync_card(path)
    if args.strict:
        check_strict()
    print("SUPERBEST_CANONICAL_SYNC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
