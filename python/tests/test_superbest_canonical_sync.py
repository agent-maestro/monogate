"""Regression tests for SuperBEST canonical surface synchronization.

python/monogate/superbest.py holds the counts. The site table (blog/src/data/superbest.json), its
copy in python/results/, and the three capability cards must agree with it. The headline is the F16
recount of 2026-09-13; the census count with ln x = EXL(0, x) as one node (14n) is kept beside it.
The browser explorer (explorer/src/superbest.js) routes through the census operators EXL and ELSb,
so its cost table follows the census count.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from monogate import superbest


ROOT = Path(__file__).resolve().parents[2]
SITE_TABLES = ["blog/src/data/superbest.json", "python/results/superbest_v5_table.json"]
CARDS = [
    "capability_card_public.json",
    "blog/public/capability_card.json",
    "blog/public/.well-known/capcard.json",
]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(data: dict) -> dict[str, dict]:
    return {row["op"].split("(", 1)[0].strip(): row for row in data["table"]}


def test_json_tables_match_python_canonical_totals():
    pos_ops, gen_ops = superbest.SUPERBEST_F16_POS_OPS, superbest.SUPERBEST_F16_GEN_OPS
    pos_total = sum(superbest.SUPERBEST_COSTS_POS[op] for op in pos_ops)
    gen_total = sum(superbest.SUPERBEST_COSTS_GEN[op] for op in gen_ops)
    pos_naive = sum(superbest.NAIVE_COSTS[op] for op in pos_ops)
    gen_naive = sum(superbest.NAIVE_COSTS[op] for op in gen_ops)
    exl_total = sum(superbest.SUPERBEST_COSTS_POS_WITH_EXL[op] for op in pos_ops)

    for rel in SITE_TABLES:
        data = _load(rel)
        totals = data["totals"]
        assert data["version"] == "v5.3"
        assert totals["total_positive"]["value"] == pos_total == superbest.SUPERBEST_F16_POS_TOTAL == 15
        assert totals["total_general"]["value"] == gen_total == superbest.SUPERBEST_F16_GEN_TOTAL == 18
        assert totals["savings_positive"]["naive_total"] == pos_naive == 73
        assert totals["savings_general"]["naive_total"] == gen_naive == 54
        assert "79.5%" in totals["positive_headline"]
        assert "66.7%" in totals["general_headline"]
        assert totals["total_positive_with_exl"]["value"] == exl_total == superbest.SUPERBEST_V53_POS_TOTAL == 14
        assert totals["savings_positive_with_exl"]["savings_pct"] == "80.8%"

        sync = data["canonical_sync"]
        assert sync["positive_ops"] == list(pos_ops)
        assert sync["general_ops"] == list(gen_ops)
        assert (sync["positive_total"], sync["positive_naive_total"]) == (pos_total, pos_naive)
        assert (sync["general_total"], sync["general_naive_total"]) == (gen_total, gen_naive)
        assert sync["positive_total_with_exl"] == exl_total


def test_core_rows_match_canonical_costs():
    for rel in SITE_TABLES:
        rows = _rows(_load(rel))
        for op in superbest.SUPERBEST_F16_POS_OPS:
            assert rows[op]["cost_positive"] == superbest.SUPERBEST_COSTS_POS[op], (rel, op)
            # None (rendered as a dash) where the op has no all-reals entry
            assert rows[op]["cost_general"] == superbest.SUPERBEST_COSTS_GEN.get(op), (rel, op)


def test_capability_cards_match_canonical_headlines():
    for rel in CARDS:
        data = _load(rel)
        cap = next(c for c in data["capabilities"] if c.get("id") == "routing.superbest_v5")
        assert cap["name"] == "SuperBEST v5.3 routing table"
        c = cap["constraints"]
        assert (c["total_nodes"], c["naive_total"], c["savings_percent"]) == (15, 73, 79.5)
        assert c["positive_total_nodes"] == superbest.SUPERBEST_F16_POS_TOTAL
        assert c["positive_naive_total"] == superbest.SUPERBEST_F16_POS_NAIVE
        assert c["positive_savings_percent"] == superbest.SUPERBEST_F16_POS_SAVINGS_PCT
        assert c["general_total_nodes"] == superbest.SUPERBEST_F16_GEN_TOTAL
        assert c["general_naive_total"] == superbest.SUPERBEST_F16_GEN_NAIVE
        assert c["general_savings_percent"] == superbest.SUPERBEST_F16_GEN_SAVINGS_PCT
        assert c["positive_total_nodes_with_exl"] == superbest.SUPERBEST_V53_POS_TOTAL
        assert c["positive_savings_percent_with_exl"] == superbest.SUPERBEST_V53_POS_SAVINGS_PCT

        bench = next(b for b in data["benchmarks"] if b.get("id") == "bench.superbest_table")
        assert bench["name"] == "SuperBEST v5.3 routing table values"
        assert bench["value"] == 15
        for needle in ("15n", "18n", "66.7", "14n"):
            assert needle in bench["notes"]


def test_browser_superbest_cost_tables_match_census_values():
    text = (ROOT / "explorer/src/superbest.js").read_text(encoding="utf-8")
    cost_block = re.search(r"export const COSTS = \{(?P<body>.*?)\};", text, re.S)
    eml_block = re.search(r"export const EML_COSTS = \{(?P<body>.*?)\};", text, re.S)
    assert cost_block and eml_block

    def value(body: str, key: str) -> int:
        match = re.search(rf"\b{re.escape(key)}:(\d+)", body)
        assert match, f"missing {key}"
        return int(match.group(1))

    costs = cost_block.group("body")
    eml_costs = eml_block.group("body")
    for op in superbest.SUPERBEST_F16_POS_OPS:
        assert value(costs, op) == superbest.SUPERBEST_COSTS_POS_WITH_EXL[op], op

    for op in ("pow", "sqrt", "neg", "abs"):
        assert value(eml_costs, op) == superbest.NAIVE_COSTS[op], op
