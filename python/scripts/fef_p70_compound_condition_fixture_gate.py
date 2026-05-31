#!/usr/bin/env python3
"""FEF-P70 compound-condition fixture gate for control-flow IR."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p59_control_flow_ir_inventory as p59
from scripts import fef_p60_control_flow_ir_schema as p60

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p70_compound_condition_fixture_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P70_COMPOUND_CONDITION_FIXTURE_GATE_PASS"

P61_PACKET = ROOT / "reports/evidence_packets/fef_p61_unsupported_construct_blocker_gate.json"
P69_PACKET = ROOT / "reports/evidence_packets/fef_p69_assignment_phi_original_c_runtime_gate.json"

CLAIM_FLAGS = {
    "compound_condition_fixture_gate_claim": False,
    "compound_condition_support_claim": False,
    "compound_condition_runtime_execution_claim": False,
    "assignment_phi_support_claim": False,
    "nested_branch_support_claim": False,
    "control_flow_ir_implemented": False,
    "frontend_lowering_changed": False,
    "unsupported_constructs_supported": False,
    "general_branch_control_flow_claim": False,
    "branch_control_flow_reingest_claim": False,
    "full_non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "arbitrary_source_family_claim": False,
    "private_reviewer_decision_recorded": False,
    "public_preview_release_claim": False,
    "package_published": False,
    "checkout_enabled": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "production_ready": False,
}

NON_CLAIMS = [
    "FEF-P70 records compound-condition fixtures only.",
    "FEF-P70 does not execute compound-condition fixtures.",
    "FEF-P70 does not implement short-circuit condition semantics.",
    "FEF-P70 does not implement compound-condition lowering.",
    "FEF-P70 does not widen Forge or eFrog frontend lowering.",
    "FEF-P70 does not claim compound-condition support.",
    "FEF-P70 does not claim assignment/phi or nested branch support.",
    "FEF-P70 does not claim general branch/control-flow support.",
    "FEF-P70 does not claim branch/control-flow re-ingest support.",
    "FEF-P70 does not claim full non-generated source roundtrip.",
    "FEF-P70 does not claim arbitrary C/Rust source-family support.",
    "FEF-P70 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P70 does not claim runtime performance.",
]

FIXTURES = [
    {
        "id": "c_and_short_circuit_guard_v0",
        "sourceLanguage": "c",
        "shape": "and_short_circuit_guard",
        "sourceSketch": "if (x > 0.0 && y != 0.0) { return x / y; } return 0.0;",
        "operator": "&&",
        "conditionCount": 2,
        "shortCircuitSites": 1,
        "branchDepth": 1,
        "blockedBy": "compound_condition_semantics_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "unsupported_construct_fail_closed"],
    },
    {
        "id": "c_or_short_circuit_default_v0",
        "sourceLanguage": "c",
        "shape": "or_short_circuit_default",
        "sourceSketch": "if (x <= 0.0 || y <= 0.0) { return 0.0; } return x + y;",
        "operator": "||",
        "conditionCount": 2,
        "shortCircuitSites": 1,
        "branchDepth": 1,
        "blockedBy": "compound_condition_semantics_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "return_and_fallthrough_preservation"],
    },
    {
        "id": "rust_and_short_circuit_guard_v0",
        "sourceLanguage": "rust",
        "shape": "rust_and_short_circuit_guard",
        "sourceSketch": "if x > 0.0 && y > 0.0 { x + y } else { 0.0 }",
        "operator": "&&",
        "conditionCount": 2,
        "shortCircuitSites": 1,
        "branchDepth": 1,
        "blockedBy": "compound_condition_semantics_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "dominance_and_merge_preservation"],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_fragment(fixture: dict[str, Any]) -> dict[str, Any]:
    obligations = [
        copy.deepcopy(item)
        for item in p59.SEMANTIC_OBLIGATIONS
        if item["id"] in fixture["requiredSemanticObligations"] or item["id"] == "unsupported_construct_fail_closed"
    ]
    while len(obligations) < 6:
        existing = {item["id"] for item in obligations}
        next_item = next(item for item in p59.SEMANTIC_OBLIGATIONS if item["id"] not in existing)
        obligations.append(copy.deepcopy(next_item))
    return {
        "schemaVersion": p60.CONTROL_FLOW_IR_SCHEMA_VERSION,
        "programId": fixture["id"],
        "sourceLanguage": fixture["sourceLanguage"],
        "functionName": fixture["id"].replace("_v0", ""),
        "feature": fixture["shape"],
        "entryBlockId": "entry",
        "exitBlockId": "exit",
        "blocks": [
            {
                "id": "entry",
                "kind": "cfg_entry",
                "statements": [
                    {
                        "kind": "unsupported_construct",
                        "constructId": "boolean_compound_conditions",
                        "expr": fixture["sourceSketch"],
                        "blockedBy": fixture["blockedBy"],
                    }
                ],
                "terminator": {"kind": "unreachable"},
            },
            {"id": "exit", "kind": "cfg_exit", "statements": [], "terminator": {"kind": "unreachable"}},
        ],
        "unsupportedConstructs": copy.deepcopy(p59.UNSUPPORTED_FORMS),
        "semanticObligations": obligations[:6],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def matrix_rows() -> list[dict[str, Any]]:
    rows = []
    for fixture in FIXTURES:
        rows.append(
            {
                **copy.deepcopy(fixture),
                "status": "blocked_fixture_defined",
                "constructId": "boolean_compound_conditions",
                "schemaFragment": fixture_fragment(fixture),
                "supportClaimAllowed": False,
                "runtimeExecutionPerformed": False,
            }
        )
    return rows


def build_summary(p61_packet: dict[str, Any], p69_packet: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 2,
        "p61ValidationPass": p61_packet["validationStatus"] == "pass",
        "p61ClaimFlagsAllFalse": all(value is False for value in p61_packet["claimFlags"].values()),
        "p69ValidationPass": p69_packet["validationStatus"] == "pass",
        "p69ClaimFlagsAllFalse": all(value is False for value in p69_packet["claimFlags"].values()),
        "fixtureCount": len(rows),
        "cFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "c"),
        "rustFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "rust"),
        "andFixtureCount": sum(1 for row in rows if row["operator"] == "&&"),
        "orFixtureCount": sum(1 for row in rows if row["operator"] == "||"),
        "conditionCount": sum(row["conditionCount"] for row in rows),
        "shortCircuitSiteCount": sum(row["shortCircuitSites"] for row in rows),
        "maxBranchDepth": max(row["branchDepth"] for row in rows),
        "allFixturesBlocked": all(row["status"] == "blocked_fixture_defined" for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "schemaFragmentsValidate": True,
        "compoundConditionSupportClaim": False,
        "compoundConditionRuntimeExecutionClaim": False,
        "assignmentPhiSupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "frontendLoweringChanged": False,
        "unsupportedConstructsSupported": False,
        "generalBranchControlFlowClaim": False,
        "branchControlFlowReingestClaim": False,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "fullCRustRoundtripClaim": False,
        "arbitrarySourceFamilyClaim": False,
        "reviewerDecisionRecorded": False,
        "packagePublished": False,
        "checkoutEnabled": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p61_packet = read_json(P61_PACKET)
    p69_packet = read_json(P69_PACKET)
    rows = matrix_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p70-compound-condition-fixture-gate",
        "decision": "compound_condition_fixture_gate_recorded_support_blocked",
        "sourcePackets": [
            {
                "phase": "P61",
                "packetPath": str(P61_PACKET.relative_to(ROOT)),
                "reviewDecision": p61_packet["reviewDecision"],
                "validationStatus": p61_packet["validationStatus"],
            },
            {
                "phase": "P69",
                "packetPath": str(P69_PACKET.relative_to(ROOT)),
                "reviewDecision": p69_packet["reviewDecision"],
                "validationStatus": p69_packet["validationStatus"],
            },
        ],
        "compoundConditionFixtures": rows,
        "summary": build_summary(p61_packet, p69_packet, rows),
        "releaseGates": [
            {"id": "compound_condition_fixture_gate", "status": "recorded"},
            {"id": "compound_condition_runtime_execution", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "control_flow_ir_implementation", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "branch_control_flow_reingest", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P70 records blocked compound-condition fixtures for private review.",
            "The gate covers selected C and Rust short-circuit condition shapes.",
            "P70 does not execute, lower, or claim support for compound conditions.",
        ],
        "blockedStatements": [
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compound-condition fixtures were executed.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Attach deterministic expected samples to one compound-condition fixture.",
            "Keep compound-condition support blocked until runtime, lowering, and re-ingest evidence exists.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return copy.deepcopy(payload)


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P70 Compound-Condition Fixture Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "compound_condition_fixtures_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Compound-condition fixture gate only; no runtime execution, compound-condition lowering, support, frontend widening, branch re-ingest, full source roundtrip, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P70 records three blocked compound-condition fixture shapes.",
            "The fixtures cover C and Rust short-circuit boolean condition surfaces.",
            "Compound-condition support and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p70_compound_condition_fixture_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p70_compound_condition_fixture_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p70_compound_condition_fixture_gate.v0",
        "date": DATE,
        "title": "FEF-P70 Compound-Condition Fixture Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach deterministic expected samples to one compound-condition fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        "| Fixture | Language | Operator | Shape | Conditions | Status |",
        "|---|---|---|---|---:|---|",
    ]
    for row in payload["compoundConditionFixtures"]:
        rows.append(
            f"| `{row['id']}` | `{row['sourceLanguage']}` | `{row['operator']}` | `{row['shape']}` | {row['conditionCount']} | `{row['status']}` |"
        )
    return "\n".join(
        [
            "# FEF-P70 Compound-Condition Fixture Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P70 records blocked compound-condition fixtures for short-circuit boolean conditions.",
            "",
            "## Summary",
            "",
            f"- Fixtures: `{summary['fixtureCount']}`",
            f"- C fixtures: `{summary['cFixtureCount']}`",
            f"- Rust fixtures: `{summary['rustFixtureCount']}`",
            f"- `&&` fixtures: `{summary['andFixtureCount']}`",
            f"- `||` fixtures: `{summary['orFixtureCount']}`",
            f"- Total condition terms: `{summary['conditionCount']}`",
            f"- Short-circuit sites: `{summary['shortCircuitSiteCount']}`",
            f"- All fixtures blocked: `{summary['allFixturesBlocked']}`",
            f"- Runtime execution performed: `{not summary['allRuntimeExecutionNotPerformed']}`",
            f"- Compound-condition support claim: `{summary['compoundConditionSupportClaim']}`",
            f"- Control-flow IR implemented: `{summary['controlFlowIrImplemented']}`",
            "",
            "## Fixtures",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Fixture gate only; no compound-condition execution.",
            "- No compound-condition lowering or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_fixture(row: dict[str, Any]) -> None:
    if row["constructId"] != "boolean_compound_conditions":
        raise ValueError("fixture must target boolean compound condition construct")
    if row["status"] != "blocked_fixture_defined":
        raise ValueError("compound-condition fixture must remain blocked")
    if row["supportClaimAllowed"] is not False:
        raise ValueError("compound-condition support claim must remain false")
    if row["runtimeExecutionPerformed"] is not False:
        raise ValueError("compound-condition runtime execution must not be performed")
    fragment = row["schemaFragment"]
    p60.validate_fragment(fragment)
    statement = fragment["blocks"][0]["statements"][0]
    if statement["constructId"] != "boolean_compound_conditions":
        raise ValueError("schema fragment must be blocked by compound condition construct")
    if not all(value is False for value in fragment["claimFlags"].values()):
        raise ValueError("fragment claim flags must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P70 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P70 status")
    for row in payload["compoundConditionFixtures"]:
        validate_fixture(row)
    summary = payload["summary"]
    for key in [
        "p61ValidationPass",
        "p61ClaimFlagsAllFalse",
        "p69ValidationPass",
        "p69ClaimFlagsAllFalse",
        "allFixturesBlocked",
        "allRuntimeExecutionNotPerformed",
        "schemaFragmentsValidate",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["fixtureCount"] != 3:
        raise ValueError("expected three compound-condition fixtures")
    if summary["cFixtureCount"] != 2 or summary["rustFixtureCount"] != 1:
        raise ValueError("unexpected language fixture counts")
    if summary["andFixtureCount"] != 2 or summary["orFixtureCount"] != 1:
        raise ValueError("unexpected operator fixture counts")
    if summary["conditionCount"] != 6 or summary["shortCircuitSiteCount"] != 3:
        raise ValueError("unexpected condition/short-circuit counts")
    for key in [
        "compoundConditionSupportClaim",
        "compoundConditionRuntimeExecutionClaim",
        "assignmentPhiSupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "frontendLoweringChanged",
        "unsupportedConstructsSupported",
        "generalBranchControlFlowClaim",
        "branchControlFlowReingestClaim",
        "fullNonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "arbitrarySourceFamilyClaim",
        "reviewerDecisionRecorded",
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "productionReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flags must remain false")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p70_compound_condition_fixture_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p70_compound_condition_fixture_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p70_compound_condition_fixture_gate.json"
    feed_path = command_feed_dir / f"fef_p70_compound_condition_fixture_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p70_compound_condition_fixture_gate")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P70_COMPOUND_CONDITION_FIXTURE_GATE_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
