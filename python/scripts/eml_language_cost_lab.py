#!/usr/bin/env python3
"""EML-L3 internal language cost lab.

This lab compares surface, expanded, canonical, and DAG-style operator counts
for EML language fixtures. It is a reviewer aid only: no public SuperBEST,
compiler, proof, or savings claim changes are made here.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE, language_to_expression_packet, parse_program  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS, build_result  # noqa: E402

SCHEMA_VERSION = "monogate.eml_language_cost_lab.v0"
STATUS = "EML_LANGUAGE_COST_LAB_PASS"


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def operator_count(node: dict[str, Any]) -> int:
    count = 1 if node.get("kind") == "op" else 0
    return count + sum(operator_count(child) for child in node.get("args", []))


def _operator_fingerprints(node: dict[str, Any]) -> list[str]:
    fingerprints = []
    if node.get("kind") == "op":
        fingerprints.append(_stable_json(node))
    for child in node.get("args", []):
        fingerprints.extend(_operator_fingerprints(child))
    return fingerprints


def repeated_canonical_subtrees(node: dict[str, Any]) -> list[dict[str, Any]]:
    counts = Counter(_operator_fingerprints(node))
    repeated = []
    for fingerprint, count in sorted(counts.items()):
        if count < 2:
            continue
        subtree = json.loads(fingerprint)
        repeated.append(
            {
                "fingerprint": "sha256:" + hashlib.sha256(fingerprint.encode()).hexdigest(),
                "op": subtree.get("op"),
                "count": count,
                "subtree": subtree,
            }
        )
    return repeated


def dag_unique_operator_count(node: dict[str, Any]) -> int:
    return len(set(_operator_fingerprints(node)))


def analyze_program(program: dict[str, Any]) -> dict[str, Any]:
    packet = language_to_expression_packet(program)
    packet_result = build_result(packet)
    obligations = packet_result["obligations"]["summary"]
    domain_safety = packet_result["domainSafety"]["summary"]
    surface_ops = operator_count(program["surfaceAst"])
    expanded_ops = operator_count(program["expandedAst"])
    canonical_ops = operator_count(program["canonicalAst"])
    repeated = repeated_canonical_subtrees(program["canonicalAst"])
    return {
        "programId": program["program_id"],
        "family": program["family"],
        "surfaceExpression": program["surface_expression"],
        "expandedExpression": program["normalized_expression"],
        "canonicalHash": program["canonicalHash"],
        "surfaceOperatorCount": surface_ops,
        "expandedOperatorCount": expanded_ops,
        "canonicalOperatorCount": canonical_ops,
        "expansionDelta": expanded_ops - surface_ops,
        "dagUniqueOperatorCount": dag_unique_operator_count(program["canonicalAst"]),
        "repeatedCanonicalSubtreeCount": len(repeated),
        "repeatedCanonicalSubtrees": repeated,
        "guardCount": len(program["guards"]),
        "letCount": len(program["lets"]),
        "proofObligationCount": obligations["count"],
        "domainObligationCount": obligations["domain_count"],
        "rangeSafetyObligationCount": obligations["range_safety_count"],
        "checkedWitnessCount": domain_safety["checked_obligation_count"],
        "blockedPublicClaimCount": domain_safety["blocked_public_claim_count"],
        "publicCostClaimChanged": False,
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-L3 Language Cost Lab",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is an internal language cost lab. It compares surface EML syntax,",
        "expanded expression trees, canonical trees, and DAG-style unique subtree",
        "counts. It does not change public SuperBEST claims.",
        "",
        "| Program | Surface ops | Expanded ops | DAG unique ops | Repeated subtrees | Obligations | Checked witnesses |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["programs"]:
        lines.append(
            f"| `{item['programId']}` | `{item['surfaceOperatorCount']}` | "
            f"`{item['expandedOperatorCount']}` | `{item['dagUniqueOperatorCount']}` | "
            f"`{item['repeatedCanonicalSubtreeCount']}` | `{item['proofObligationCount']}` | "
            f"`{item['checkedWitnessCount']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Internal DAG reuse is a measurement aid, not a public savings claim.",
            "- Surface-to-expanded deltas are language expansion facts, not proof claims.",
            "- Obligation and checked-witness counts come from the existing packet builder.",
            "- Forge/compiler behavior is unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def build_cost_lab(fixtures_dir: Path, out_dir: Path, report_dir: Path) -> dict[str, Any]:
    programs = [
        analyze_program(parse_program(path.read_text(encoding="utf-8")))
        for path in sorted(fixtures_dir.glob("*.eml"))
    ]
    totals = {
        "programCount": len(programs),
        "surfaceOperatorCount": sum(item["surfaceOperatorCount"] for item in programs),
        "expandedOperatorCount": sum(item["expandedOperatorCount"] for item in programs),
        "canonicalOperatorCount": sum(item["canonicalOperatorCount"] for item in programs),
        "dagUniqueOperatorCount": sum(item["dagUniqueOperatorCount"] for item in programs),
        "expansionDelta": sum(item["expansionDelta"] for item in programs),
        "repeatedCanonicalSubtreeCount": sum(item["repeatedCanonicalSubtreeCount"] for item in programs),
        "guardCount": sum(item["guardCount"] for item in programs),
        "letCount": sum(item["letCount"] for item in programs),
        "proofObligationCount": sum(item["proofObligationCount"] for item in programs),
        "checkedWitnessCount": sum(item["checkedWitnessCount"] for item in programs),
        "publicCostClaimChanged": False,
    }
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "programs": programs,
        "summary": totals,
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "This lab does not change public SuperBEST claims.",
            "This lab does not change Forge/compiler behavior.",
            "This lab does not prove semantic equivalence or theorem correctness.",
            "This lab does not publish packages or deploy.",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_language_cost_lab_{stamp}.json"
    report_path = report_dir / f"eml_l3_language_cost_lab_{stamp}.md"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path)}


def validate_cost_lab(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid cost lab schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid cost lab status")
    if payload["summary"]["programCount"] < 5:
        raise ValueError("expected at least 5 language programs")
    if payload["summary"]["publicCostClaimChanged"] is not False:
        raise ValueError("public cost claim must not change")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    for item in payload["programs"]:
        if item["publicCostClaimChanged"] is not False:
            raise ValueError(f"public cost claim changed for {item['programId']}")
        for key, value in item.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {item['programId']}: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures-dir", type=Path, default=ROOT / "python/fixtures/eml_language_programs")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_language_cost_lab")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--build-fixtures", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not args.build_fixtures:
        raise SystemExit("--build-fixtures is required")
    built = build_cost_lab(args.fixtures_dir, args.out_dir, args.report_dir)
    if args.strict:
        validate_cost_lab(built["payload"])
    print("EML_LANGUAGE_COST_LAB_OK")
    print(f"programs={built['payload']['summary']['programCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
