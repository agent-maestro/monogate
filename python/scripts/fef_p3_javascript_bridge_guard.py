#!/usr/bin/env python3
"""FEF-P3 JavaScript runtime execution in the real eFrog bridge guard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p3_javascript_bridge_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P3_JAVASCRIPT_BRIDGE_GUARD_PASS"

FEF_P2_PATH = ROOT / "reports/evidence_packets/fef_p2_clean_room_quickstart_scaffold.json"
BRIDGE_GUARD_DIR = ROOT / "python/results/fef_p3_javascript_bridge_guard/bridge_guard_outputs"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "proof_claim": False,
    "package_published": False,
    "public_compiler_package_available": False,
    "public_checkout_enabled": False,
    "verilog_claim": False,
    "lean_proof_claim": False,
    "zkproof_claim": False,
    "silicon_claim": False,
}

NON_CLAIMS = [
    "FEF-P3 records JavaScript runtime execution in the real eFrog bridge guard.",
    "FEF-P3 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P3 does not publish a package or enable public checkout.",
    "FEF-P3 does not claim runtime performance, production readiness, Verilog, Lean proofs, zkproof, or silicon output.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    fef_p2 = read_json(FEF_P2_PATH)
    guard = read_json(BRIDGE_GUARD_DIR / "bridge_guard_report.json")
    matrix = read_json(BRIDGE_GUARD_DIR / "roundtrip_matrix" / "roundtrip_matrix.json")
    results = matrix["results"]
    js_results = [r for r in results if r["target_language"] == "javascript"]
    py_results = [r for r in results if r["target_language"] == "python"]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p3-javascript-bridge-guard",
        "decision": "javascript_runtime_execution_added_to_bridge_guard",
        "guard": {
            "path": str(BRIDGE_GUARD_DIR.relative_to(ROOT)),
            "status": guard["status"],
            "checks": guard["checks"],
            "claimBoundaries": guard["claim_boundaries"],
        },
        "roundtripMatrix": {
            "path": str((BRIDGE_GUARD_DIR / "roundtrip_matrix" / "roundtrip_matrix.json").relative_to(ROOT)),
            "passed": matrix["passed"],
            "targetLanguages": matrix["target_languages"],
            "resultCount": len(results),
            "pythonResultCount": len(py_results),
            "javascriptResultCount": len(js_results),
            "javascriptRuntimeExecutionPassCount": sum(
                1 for r in js_results if r["runtime_validation"] == "javascript_runtime_execution_passed"
            ),
            "sourceLanguages": sorted({r["source_language"] for r in results}),
            "results": results,
        },
        "fefP2Link": {
            "path": str(FEF_P2_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p2["reviewDecision"],
        },
        "releaseGates": [
            {"id": "bridge_guard_runs_python_and_javascript", "status": "pass"},
            {"id": "python_bytecode_compile_guard_passed", "status": "pass"},
            {"id": "javascript_runtime_execution_guard_passed", "status": "pass"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "summary": {
            "bridgeGuardStatus": guard["status"],
            "roundtripMatrixPassed": matrix["passed"],
            "targetLanguages": matrix["target_languages"],
            "resultCount": len(results),
            "pythonResultCount": len(py_results),
            "javascriptResultCount": len(js_results),
            "javascriptRuntimeExecutionPassCount": sum(
                1 for r in js_results if r["runtime_validation"] == "javascript_runtime_execution_passed"
            ),
            "packagePublished": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextMilestones": [
            "FEF-P4 non-Python source semantic comparison",
            "FEF-P5 publication decision and public copy update only after claim review",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P3 JavaScript Bridge Guard",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "bridge_guard_javascript_runtime_smoke_pass",
        "semanticReview": payload["summary"],
        "claimBoundary": "JavaScript generated-target runtime execution guard only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, or silicon claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "The real eFrog bridge guard now runs Python and JavaScript hosted roundtrip targets.",
            "Generated JavaScript modules are imported by Node and exported functions are executed on deterministic numeric inputs.",
            "The recorded guard matrix has 10 passing results: five Python bytecode checks and five JavaScript runtime executions.",
        ],
        "validationCommands": [
            "python -m pytest -q tests/test_bridge_artifacts.py -k 'roundtrip_matrix or bridge_guard'",
            "python -m efrog.cli --bridge-guard --out-dir /tmp/fef_p3_bridge_guard_probe",
            "python python/scripts/fef_p3_javascript_bridge_guard.py --build --strict",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p3_javascript_bridge_guard.v0",
        "date": DATE,
        "title": "FEF-P3 JavaScript Bridge Guard",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run FEF-P4 non-Python source semantic comparison before any publication decision.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# FEF-P3 JavaScript Bridge Guard",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P3 attaches JavaScript runtime execution to the real eFrog bridge",
        "guard. This is a generated-target runtime smoke, not compiler",
        "correctness or formal equivalence.",
        "",
        "## Guard Result",
        "",
        f"- Bridge guard status: `{summary['bridgeGuardStatus']}`",
        f"- Targets: `{','.join(summary['targetLanguages'])}`",
        f"- Total results: `{summary['resultCount']}`",
        f"- Python bytecode results: `{summary['pythonResultCount']}`",
        f"- JavaScript runtime results: `{summary['javascriptResultCount']}`",
        f"- JavaScript runtime passes: `{summary['javascriptRuntimeExecutionPassCount']}`",
        "",
        "## Release Gates",
        "",
        "| Gate | Status |",
        "|---|---|",
    ]
    for gate in payload["releaseGates"]:
        lines.append(f"| `{gate['id']}` | `{gate['status']}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No package publication or checkout claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No runtime performance, production, Verilog, Lean proof, zkproof, or silicon claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["bridgeGuardStatus"] != "pass":
        raise ValueError("bridge guard must pass")
    if summary["roundtripMatrixPassed"] is not True:
        raise ValueError("roundtrip matrix must pass")
    if summary["targetLanguages"] != ["python", "javascript"]:
        raise ValueError("bridge guard must cover Python and JavaScript")
    if summary["resultCount"] != 10:
        raise ValueError("expected 10 hosted bridge results")
    if summary["pythonResultCount"] != 5:
        raise ValueError("expected five Python results")
    if summary["javascriptResultCount"] != 5:
        raise ValueError("expected five JavaScript results")
    if summary["javascriptRuntimeExecutionPassCount"] != 5:
        raise ValueError("all JavaScript results must execute at runtime")
    for key in ["packagePublished", "publicReady", "safeToPublishPublicly"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p3_javascript_bridge_guard_{STAMP}.json"
    report_path = report_dir / f"fef_p3_javascript_bridge_guard_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p3_javascript_bridge_guard.json"
    feed_path = command_feed_dir / f"fef_p3_javascript_bridge_guard_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/fef_p3_javascript_bridge_guard",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir) if args.build else {"payload": build_payload()}
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P3_JAVASCRIPT_BRIDGE_GUARD_OK")
    print(f"decision={built['payload']['decision']}")
    if "result_path" in built:
        print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
