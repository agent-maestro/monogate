"""Regression tests for SuperBEST canonical surface synchronization."""

from __future__ import annotations

import json
import re
from pathlib import Path

from monogate import superbest


ROOT = Path(__file__).resolve().parents[2]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(data: dict) -> dict[str, dict]:
    return {row["op"].split("(", 1)[0].strip(): row for row in data["table"]}


def test_json_tables_match_python_canonical_totals():
    pos_total = sum(superbest.SUPERBEST_COSTS_POS[op] for op in superbest.SUPERBEST_V52_POS_OPS)
    gen_total = sum(superbest.SUPERBEST_COSTS_GEN[op] for op in superbest.SUPERBEST_V52_GEN_OPS)
    pos_naive = sum(superbest.NAIVE_COSTS[op] for op in superbest.SUPERBEST_V52_POS_OPS)
    gen_naive = sum(superbest.NAIVE_COSTS[op] for op in superbest.SUPERBEST_V52_GEN_OPS)

    for rel in [
        "blog/src/data/superbest.json",
        "python/results/superbest_v5_table.json",
    ]:
        data = _load(rel)
        assert data["version"] == "v5.3"
        assert data["totals"]["total_positive"]["value"] == pos_total == 14
        assert data["totals"]["total_general"]["value"] == gen_total == 16
        assert data["totals"]["savings_positive"]["naive_total"] == pos_naive == 73
        assert data["totals"]["savings_general"]["naive_total"] == gen_naive == 62
        assert "80.8%" in data["totals"]["positive_headline"]
        assert "74.2%" in data["totals"]["general_headline"]


def test_drifted_mul_and_div_rows_match_canonical():
    for rel in [
        "blog/src/data/superbest.json",
        "python/results/superbest_v5_table.json",
    ]:
        rows = _rows(_load(rel))
        assert rows["mul"]["cost_positive"] == superbest.SUPERBEST_COSTS_POS["mul"] == 1
        assert rows["mul"]["cost_general"] == superbest.SUPERBEST_COSTS_GEN["mul"] == 3
        assert rows["div"]["cost_positive"] == superbest.SUPERBEST_COSTS_POS["div"] == 2
        assert rows["div"]["cost_general"] == superbest.SUPERBEST_COSTS_GEN["div"] == 3


def test_capability_cards_match_canonical_headlines():
    for rel in [
        "capability_card_public.json",
        "blog/public/capability_card.json",
        "blog/public/.well-known/capcard.json",
    ]:
        data = _load(rel)
        cap = next(c for c in data["capabilities"] if c.get("id") == "routing.superbest_v5")
        assert cap["name"] == "SuperBEST v5.3 routing table"
        assert cap["constraints"]["positive_total_nodes"] == 14
        assert cap["constraints"]["positive_naive_total"] == 73
        assert cap["constraints"]["positive_savings_percent"] == 80.8
        assert cap["constraints"]["general_total_nodes"] == 16
        assert cap["constraints"]["general_naive_total"] == 62
        assert cap["constraints"]["general_savings_percent"] == 74.2

        bench = next(b for b in data["benchmarks"] if b.get("id") == "bench.superbest_table")
        assert bench["name"] == "SuperBEST v5.3 routing table values"
        assert "14n" in bench["notes"]
        assert "16n" in bench["notes"]
        assert "74.2" in bench["notes"]


def test_browser_superbest_cost_tables_match_canonical_values():
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
    for op, expected in {
        "mul": 1,
        "div": 2,
        "add": 2,
        "sub": 2,
        "pow": 1,
        "sqrt": 1,
        "recip": 1,
        "abs": 2,
    }.items():
        assert value(costs, op) == expected

    for op, expected in {"pow": 3, "sqrt": 8, "neg": 9, "abs": 5}.items():
        assert value(eml_costs, op) == expected
