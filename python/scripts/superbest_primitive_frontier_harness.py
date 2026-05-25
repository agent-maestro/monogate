#!/usr/bin/env python3
"""Bounded primitive-row frontier harness for SuperBEST.

The harness does not change canonical costs. It evaluates a conservative set of
primitive improvement hypotheses across domain grids, records exact blockers,
and separates positive-domain wins from general-domain mirages.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from monogate import superbest  # noqa: E402


BOUNDARY = {
    "internal_only": True,
    "canonical_row_table_changed": False,
    "new_row_optimality_claim": False,
    "public_theorem_claim": False,
    "open_problem_solved_claim": False,
    "package_publish_performed": False,
    "deploy_performed": False,
}

DOMAIN_GRIDS = {
    "positive": [(x, y) for x in [0.25, 0.5, 1.5, 3.0, 7.0] for y in [0.25, 0.75, 2.0, 5.0]],
    "general_nonzero": [
        (x, y)
        for x in [-7.0, -2.0, -0.5, 0.5, 2.0, 7.0]
        for y in [-5.0, -1.0, -0.25, 0.25, 1.5, 4.0]
    ],
    "general_with_zero": [
        (x, y)
        for x in [-3.0, -1.0, 0.0, 0.5, 2.0]
        for y in [-2.0, 0.0, 1.0, 4.0]
    ],
}

UNARY_GRIDS = {
    "all_real": [-7.0, -2.0, -0.5, 0.0, 0.25, 1.0, 3.0],
    "positive": [0.25, 0.5, 1.0, 2.0, 7.0],
}


def safe_call(fn: Callable, *args: float) -> tuple[bool, float | str]:
    try:
        value = fn(*args)
        if not math.isfinite(value):
            return False, "non-finite result"
        return True, value
    except Exception as exc:  # noqa: BLE001 - diagnostics are the point here.
        return False, exc.__class__.__name__ + ": " + str(exc)


def close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def target_binary(op: str, x: float, y: float) -> float:
    if op == "mul":
        return x * y
    if op == "div":
        return x / y
    if op == "add":
        return x + y
    if op == "sub":
        return x - y
    raise ValueError(f"unknown binary op {op}")


def target_unary(op: str, x: float) -> float:
    if op == "neg":
        return -x
    if op == "abs":
        return abs(x)
    raise ValueError(f"unknown unary op {op}")


def mul_positive_route(x: float, y: float) -> float:
    return math.exp(math.log(x)) * y


def div_positive_route(x: float, y: float) -> float:
    return math.exp(math.log(x)) / y


def add_two_node_route(x: float, y: float) -> float:
    return x - math.log(math.exp(-y))


def sub_two_node_route(x: float, y: float) -> float:
    return x - math.log(math.exp(y))


def neg_two_node_route(x: float) -> float:
    return math.log(math.exp(-x))


def sign_branched_mul(x: float, y: float) -> float:
    if x == 0 or y == 0:
        return 0.0
    return math.copysign(math.exp(math.log(abs(x)) + math.log(abs(y))), x * y)


def sign_branched_div(x: float, y: float) -> float:
    if y == 0:
        raise ZeroDivisionError("division by zero")
    if x == 0:
        return 0.0
    return math.copysign(math.exp(math.log(abs(x)) - math.log(abs(y))), x * y)


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    op: str
    arity: int
    target_domain: str
    candidate_nodes: int
    canonical_nodes: int
    source: str
    single_tree: bool
    public_safe: bool
    evaluator: Callable
    notes: str


CANDIDATES = [
    Candidate(
        "mul_positive_1n_route",
        "mul",
        2,
        "positive",
        1,
        superbest.SUPERBEST_COSTS_POS["mul"],
        "exp(log(x))*y",
        True,
        True,
        mul_positive_route,
        "Confirms canonical positive-domain route; not a new primitive saving.",
    ),
    Candidate(
        "mul_general_positive_route_attempt",
        "mul",
        2,
        "general_nonzero",
        1,
        superbest.SUPERBEST_COSTS_GEN["mul"],
        "exp(log(x))*y",
        True,
        False,
        mul_positive_route,
        "Expected to fail for x<=0; exact blocker for demoting mul_general.",
    ),
    Candidate(
        "mul_general_sign_branched_reference",
        "mul",
        2,
        "general_with_zero",
        4,
        superbest.SUPERBEST_COSTS_GEN["mul"],
        "sign(x*y)*exp(log(abs(x))+log(abs(y))) with zero branch",
        False,
        False,
        sign_branched_mul,
        "Works numerically but is not a single SuperBEST primitive tree.",
    ),
    Candidate(
        "div_positive_2n_route",
        "div",
        2,
        "positive",
        2,
        superbest.SUPERBEST_COSTS_POS["div"],
        "exp(log(x))/y",
        True,
        True,
        div_positive_route,
        "Confirms canonical positive-domain full-tree route.",
    ),
    Candidate(
        "div_general_positive_route_attempt",
        "div",
        2,
        "general_nonzero",
        2,
        superbest.SUPERBEST_COSTS_GEN["div"],
        "exp(log(x))/y",
        True,
        False,
        div_positive_route,
        "Expected to fail for x<=0; exact blocker for demoting div_general.",
    ),
    Candidate(
        "div_general_sign_branched_reference",
        "div",
        2,
        "general_nonzero",
        5,
        superbest.SUPERBEST_COSTS_GEN["div"],
        "sign(x*y)*exp(log(abs(x))-log(abs(y)))",
        False,
        False,
        sign_branched_div,
        "Works numerically on nonzero denominator but requires sign/abs branching.",
    ),
    Candidate(
        "add_general_2n_route",
        "add",
        2,
        "general_with_zero",
        2,
        superbest.SUPERBEST_COSTS_GEN["add"],
        "x-log(exp(-y))",
        True,
        True,
        add_two_node_route,
        "Confirms canonical all-real 2n route.",
    ),
    Candidate(
        "sub_general_2n_route",
        "sub",
        2,
        "general_with_zero",
        2,
        superbest.SUPERBEST_COSTS_GEN["sub"],
        "x-log(exp(y))",
        True,
        True,
        sub_two_node_route,
        "Confirms canonical all-real 2n route.",
    ),
    Candidate(
        "neg_general_2n_route",
        "neg",
        1,
        "all_real",
        2,
        superbest.SUPERBEST_COSTS_GEN["neg"],
        "log(exp(-x))",
        True,
        True,
        neg_two_node_route,
        "Confirms canonical all-real 2n route.",
    ),
]

ROW_FRONTIER_NOTES = {
    "mul_general": {
        "current_nodes": superbest.SUPERBEST_COSTS_GEN["mul"],
        "target_nodes": 2,
        "status": "BLOCKED_BY_SIGN_DOMAIN",
        "reason": "The 1n positive route uses log(x), so it fails for x<=0. Sign-aware versions require abs/sign branching and are not single primitive trees.",
    },
    "div_general": {
        "current_nodes": superbest.SUPERBEST_COSTS_GEN["div"],
        "target_nodes": 2,
        "status": "BLOCKED_BY_NUMERATOR_SIGN_DOMAIN",
        "reason": "The 2n positive route uses log(x), so it fails for x<=0. Sign-aware division requires abs/sign branching and zero-denominator handling.",
    },
    "add_general": {
        "current_nodes": superbest.SUPERBEST_COSTS_GEN["add"],
        "target_nodes": 1,
        "status": "NO_1N_CANDIDATE_FOUND_IN_HARNESS",
        "reason": "Canonical 2n route passes all-real grid; this harness found no 1n all-real candidate.",
    },
    "sub_general": {
        "current_nodes": superbest.SUPERBEST_COSTS_GEN["sub"],
        "target_nodes": 1,
        "status": "NO_1N_CANDIDATE_FOUND_IN_HARNESS",
        "reason": "Canonical 2n route passes all-real grid; this harness found no 1n all-real candidate.",
    },
    "neg_general": {
        "current_nodes": superbest.SUPERBEST_COSTS_GEN["neg"],
        "target_nodes": 1,
        "status": "NO_1N_CANDIDATE_FOUND_IN_HARNESS",
        "reason": "Canonical 2n route passes all-real grid; this harness found no 1n all-real candidate.",
    },
    "sin_cos": {
        "current_nodes": None,
        "target_nodes": None,
        "status": "NUMERICAL_METHOD_FRONTIER_NOT_PRIMITIVE_ROW",
        "reason": "Further sin/cos gains are likely approximation-method work, not a primitive row demotion in this harness.",
    },
}


def grid_for(candidate: Candidate) -> list:
    if candidate.arity == 1:
        return UNARY_GRIDS[candidate.target_domain]
    return DOMAIN_GRIDS[candidate.target_domain]


def evaluate_candidate(candidate: Candidate) -> dict:
    failures = []
    passes = 0
    for item in grid_for(candidate):
        args = (item,) if candidate.arity == 1 else item
        ok, value_or_error = safe_call(candidate.evaluator, *args)
        if ok:
            expected = target_unary(candidate.op, args[0]) if candidate.arity == 1 else target_binary(candidate.op, *args)
            if close(float(value_or_error), expected):
                passes += 1
            else:
                failures.append({"inputs": list(args), "kind": "wrong_value", "got": value_or_error, "expected": expected})
        else:
            failures.append({"inputs": list(args), "kind": "undefined_or_error", "error": value_or_error})
    total = passes + len(failures)
    empirical_pass = not failures
    if empirical_pass and candidate.single_tree and candidate.candidate_nodes < candidate.canonical_nodes:
        classification = "EMPIRICAL_IMPROVEMENT_CANDIDATE"
    elif empirical_pass and candidate.single_tree:
        classification = "CONFIRMED_EXISTING_ROUTE"
    elif empirical_pass and not candidate.single_tree:
        classification = "BRANCHED_REFERENCE_ONLY"
    else:
        classification = "INVALID_OR_DOMAIN_LIMITED"
    return {
        "candidate_id": candidate.candidate_id,
        "op": candidate.op,
        "arity": candidate.arity,
        "target_domain": candidate.target_domain,
        "candidate_nodes": candidate.candidate_nodes,
        "canonical_nodes": candidate.canonical_nodes,
        "source": candidate.source,
        "single_tree": candidate.single_tree,
        "public_safe": candidate.public_safe,
        "notes": candidate.notes,
        "grid_count": total,
        "pass_count": passes,
        "failure_count": len(failures),
        "first_failures": failures[:5],
        "empirical_pass": empirical_pass,
        "classification": classification,
    }


def run_harness() -> dict:
    candidates = [evaluate_candidate(candidate) for candidate in CANDIDATES]
    primitive_improvement_candidates = [
        item for item in candidates if item["classification"] == "EMPIRICAL_IMPROVEMENT_CANDIDATE"
    ]
    invalid_attempts = [item for item in candidates if item["classification"] == "INVALID_OR_DOMAIN_LIMITED"]
    return {
        "harness_id": "superbest_primitive_frontier_harness_2026_05_24",
        "status": "SUPERBEST_PRIMITIVE_FRONTIER_HARNESS_COMPLETE",
        "candidate_count": len(candidates),
        "primitive_improvement_candidate_count": len(primitive_improvement_candidates),
        "invalid_or_domain_limited_count": len(invalid_attempts),
        "confirmed_existing_route_count": sum(1 for item in candidates if item["classification"] == "CONFIRMED_EXISTING_ROUTE"),
        "branched_reference_only_count": sum(1 for item in candidates if item["classification"] == "BRANCHED_REFERENCE_ONLY"),
        "candidate_results": candidates,
        "row_frontier_notes": ROW_FRONTIER_NOTES,
        "blunt_result": "No canonical primitive row savings unlocked by this bounded harness. The plausible wins remain domain-narrowing, sign/branch-aware variants, or approximation-method work.",
        "recommended_next_build": {
            "name": "SUPERBEST_PRIMITIVE_ENUMERATOR_V2",
            "why": "A deeper enumerator could search symbolic primitive trees up to a bounded node count, but current blockers point to domain/sign barriers rather than easy row demotions.",
            "priority": "P2_AFTER_DAG_LOWERING",
        },
        "boundary": BOUNDARY,
    }


def render_report(payload: dict) -> str:
    lines = [
        "# SuperBEST Primitive Frontier Harness",
        "",
        "Date: 2026-05-24",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["blunt_result"],
        "",
        "## Summary",
        "",
        f"- Candidates tested: {payload['candidate_count']}",
        f"- Primitive improvement candidates: {payload['primitive_improvement_candidate_count']}",
        f"- Invalid/domain-limited attempts: {payload['invalid_or_domain_limited_count']}",
        f"- Confirmed existing routes: {payload['confirmed_existing_route_count']}",
        f"- Branched references only: {payload['branched_reference_only_count']}",
        "",
        "## Candidate Results",
        "",
        "| Candidate | Domain | Nodes | Classification | Failures |",
        "|---|---|---:|---|---:|",
    ]
    for item in payload["candidate_results"]:
        lines.append(
            f"| `{item['candidate_id']}` | {item['target_domain']} | {item['candidate_nodes']} | "
            f"{item['classification']} | {item['failure_count']} |"
        )
    lines.extend(["", "## Row Frontier Notes", ""])
    for row, note in payload["row_frontier_notes"].items():
        lines.append(f"- `{row}`: `{note['status']}` - {note['reason']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Internal harness only.",
            "- No canonical row table changed.",
            "- No new row optimality claim.",
            "- No public theorem/proof/open-problem claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=ROOT / "python/results/superbest_primitive_frontier_harness_2026_05_24.json")
    parser.add_argument("--out-report", type=Path, default=ROOT / "reports/superbest_primitive_frontier_harness_2026_05_24.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    payload = run_harness()
    if args.strict:
        if payload["candidate_count"] < 8:
            raise SystemExit("strict mode requires at least 8 primitive candidates")
        if payload["primitive_improvement_candidate_count"] != 0:
            raise SystemExit("unexpected primitive improvement candidate; requires human review")
        if payload["boundary"]["canonical_row_table_changed"] is not False:
            raise SystemExit("canonical row table must remain unchanged")
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out_report.write_text(render_report(payload), encoding="utf-8")
    print("SUPERBEST_PRIMITIVE_FRONTIER_HARNESS_OK")
    print(
        "candidates={candidate_count} improvements={primitive_improvement_candidate_count} invalid={invalid_or_domain_limited_count}".format(
            **payload
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
