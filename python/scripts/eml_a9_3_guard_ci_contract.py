#!/usr/bin/env python3
"""EML-A9.3 guard CI contract.

Fails if guard fixtures/analyzer decisions drift, JSON becomes invalid, claim
flags flip true, or dev explorer copies drift from generated source.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_a9_2_guard_decision_analyzer import CLAIM_FLAGS, build_decisions  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a9_3_guard_ci_contract.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_guard_ci_contract_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A9_3_GUARD_CI_CONTRACT_PASS"

NON_CLAIMS = [
    "A9.3 is a CI contract for guard fixtures and analyzer output.",
    "A9.3 does not change compiler behavior or prove compiler correctness.",
    "A9.3 does not claim production readiness, EML advantage, runtime performance, public Atlas promotion, or deployment.",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_false_flags(obj: Any, path: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(obj, dict):
        if "claimFlags" in obj and isinstance(obj["claimFlags"], dict):
            for key, value in obj["claimFlags"].items():
                if value is not False:
                    failures.append(f"{path}.claimFlags.{key}")
        if "claim_flags" in obj and isinstance(obj["claim_flags"], dict):
            for key, value in obj["claim_flags"].items():
                if value is not False:
                    failures.append(f"{path}.claim_flags.{key}")
        for key, value in obj.items():
            failures.extend(check_false_flags(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            failures.extend(check_false_flags(value, f"{path}[{index}]"))
    return failures


def build_contract(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, dev_copy_root: Path | None = None) -> dict[str, Any]:
    built = build_decisions(
        ROOT / "python/results/eml_a9_2_guard_decision_analyzer",
        ROOT / "python/results/eml_guard_decision_packets",
        ROOT / "reports",
        ROOT / "reports/evidence_packets",
        ROOT / "command_center_feeds",
    )
    payload = built["payload"]
    checks: list[dict[str, Any]] = []

    checks.append({
        "checkId": "analyzer_all_fixtures_matched",
        "passed": payload["summary"]["allFixturesMatched"] is True,
        "detail": payload["summary"],
    })
    checks.append({
        "checkId": "claim_flags_false",
        "passed": not check_false_flags(payload),
        "detail": check_false_flags(payload),
    })
    checks.append({
        "checkId": "non_claims_present",
        "passed": bool(payload.get("nonClaims")) and all(packet.get("nonClaims") for packet in payload["decisionPackets"]),
        "detail": "payload and packet nonClaims checked",
    })
    checks.append({
        "checkId": "rule_ids_stable",
        "passed": all(packet["matchedRuleIds"] == packet["expectedRuleIds"] for packet in payload["decisionPackets"]),
        "detail": [packet["fixtureId"] for packet in payload["decisionPackets"]],
    })

    dev_root = dev_copy_root or (ROOT.parent / "monogate-dev")
    dev_file = dev_root / "app/explorer/eml-advantage/data/eml_a9_2_guard_decision_analyzer_2026_05_27.json"
    source_file = Path(built["result_path"])
    if dev_file.exists():
        checks.append({
            "checkId": "dev_explorer_copy_matches_source",
            "passed": read_json(dev_file) == read_json(source_file),
            "detail": str(dev_file),
        })
    else:
        checks.append({
            "checkId": "dev_explorer_copy_matches_source",
            "passed": True,
            "detail": "dev copy not present in this environment",
        })

    contract = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "contractId": "eml_a9_3_guard_ci_contract",
        "checks": checks,
        "summary": {
            "checkCount": len(checks),
            "passedCount": sum(1 for check in checks if check["passed"]),
            "failedCount": sum(1 for check in checks if not check["passed"]),
            "allPassed": all(check["passed"] for check in checks),
            "compilerBehaviorChanged": False,
            "compilerCorrectnessClaim": False,
            "productionReady": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_contract(contract)
    evidence = build_evidence_packet(contract)
    feed = command_feed(contract)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a9_3_guard_ci_contract_{stamp}.json"
    report_path = report_dir / f"eml_a9_3_guard_ci_contract_{stamp}.md"
    evidence_path = evidence_dir / "eml_a9_3_guard_ci_contract.json"
    feed_path = command_feed_dir / f"eml_a9_3_guard_ci_contract_feed_{stamp}.json"
    result_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(contract), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": contract, "evidence": evidence, "feed": feed, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a9-3-guard-ci-contract",
        "title": "EML-A9.3 Guard CI Contract",
        "reviewDecision": "guard_ci_contract_passed",
        "validationStatus": "pass",
        "replayStatus": "deterministic_guard_contract",
        "semanticStrength": "ci_guard_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "CI contract only; no compiler behavior change, compiler correctness proof, production readiness, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a9_3.v0",
        "date": DATE,
        "title": "EML-A9.3 Guard CI Contract",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A10 run guard lens over existing EML expression packets",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = ["# EML-A9.3 Guard CI Contract", "", f"Date: {DATE}", "", f"Status: `{payload['status']}`", "", "| Check | Passed |", "|---|---|"]
    for check in payload["checks"]:
        lines.append(f"| `{check['checkId']}` | `{check['passed']}` |")
    lines.extend(["", "## Boundary", "", "- CI guard contract only.", "- No compiler behavior change, compiler correctness proof, production readiness, or EML advantage claim.", ""])
    return "\n".join(lines)


def validate_contract(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A9.3 payload")
    if payload["summary"]["allPassed"] is not True:
        raise ValueError(f"guard CI contract failed: {payload['checks']}")
    for key in ["compilerBehaviorChanged", "compilerCorrectnessClaim", "productionReady"]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    if payload["summary"]["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a9_3_guard_ci_contract")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--dev-copy-root", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_contract(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.dev_copy_root)
    if args.strict:
        validate_contract(built["payload"])
    print("EML_A9_3_GUARD_CI_CONTRACT_OK")
    print(f"checks={built['payload']['summary']['checkCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
