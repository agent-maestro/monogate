#!/usr/bin/env python3
"""FEF-P66 assignment/phi fixture gate for control-flow IR."""

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
SCHEMA_VERSION = "monogate.fef_p66_assignment_phi_fixture_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P66_ASSIGNMENT_PHI_FIXTURE_GATE_PASS"

P61_PACKET = ROOT / "reports/evidence_packets/fef_p61_unsupported_construct_blocker_gate.json"
P65_PACKET = ROOT / "reports/evidence_packets/fef_p65_nested_branch_original_c_runtime_gate.json"

CLAIM_FLAGS = {
    "assignment_phi_fixture_gate_claim": False,
    "assignment_phi_support_claim": False,
    "assignment_phi_runtime_execution_claim": False,
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
    "FEF-P66 records assignment/phi fixtures only.",
    "FEF-P66 does not execute assignment/phi fixtures.",
    "FEF-P66 does not implement mutable assignments across branches.",
    "FEF-P66 does not implement phi/select lowering.",
    "FEF-P66 does not widen Forge or eFrog frontend lowering.",
    "FEF-P66 does not claim assignment/phi support.",
    "FEF-P66 does not claim nested branch support.",
    "FEF-P66 does not claim general branch/control-flow support.",
    "FEF-P66 does not claim branch/control-flow re-ingest support.",
    "FEF-P66 does not claim full non-generated source roundtrip.",
    "FEF-P66 does not claim arbitrary C/Rust source-family support.",
    "FEF-P66 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P66 does not claim runtime performance.",
]

FIXTURES = [
    {
        "id": "c_branch_assignment_merge_v0",
        "sourceLanguage": "c",
        "shape": "branch_assignment_merge",
        "sourceSketch": "double z = x; if (x > 0.0) { z = y; } return z;",
        "assignmentCount": 2,
        "mergeCount": 1,
        "branchDepth": 1,
        "blockedBy": "assignment_phi_fixture_gate",
        "requiredSemanticObligations": ["assignment_order_preservation", "dominance_and_merge_preservation"],
    },
    {
        "id": "c_if_else_assignment_merge_v0",
        "sourceLanguage": "c",
        "shape": "if_else_assignment_merge",
        "sourceSketch": "double z = 0.0; if (x > y) { z = x; } else { z = y; } return z;",
        "assignmentCount": 3,
        "mergeCount": 1,
        "branchDepth": 1,
        "blockedBy": "assignment_phi_fixture_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "assignment_order_preservation", "dominance_and_merge_preservation"],
    },
    {
        "id": "rust_branch_mut_assignment_v0",
        "sourceLanguage": "rust",
        "shape": "rust_mut_assignment_merge",
        "sourceSketch": "let mut z = x; if x > 0.0 { z = y; } z",
        "assignmentCount": 2,
        "mergeCount": 1,
        "branchDepth": 1,
        "blockedBy": "assignment_phi_fixture_gate",
        "requiredSemanticObligations": ["assignment_order_preservation", "dominance_and_merge_preservation"],
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
                        "constructId": "mutable_assignments_across_branches",
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
                "constructId": "mutable_assignments_across_branches",
                "schemaFragment": fixture_fragment(fixture),
                "supportClaimAllowed": False,
                "runtimeExecutionPerformed": False,
            }
        )
    return rows


def build_summary(p61_packet: dict[str, Any], p65_packet: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 2,
        "p61ValidationPass": p61_packet["validationStatus"] == "pass",
        "p61ClaimFlagsAllFalse": all(value is False for value in p61_packet["claimFlags"].values()),
        "p65ValidationPass": p65_packet["validationStatus"] == "pass",
        "p65ClaimFlagsAllFalse": all(value is False for value in p65_packet["claimFlags"].values()),
        "fixtureCount": len(rows),
        "cFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "c"),
        "rustFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "rust"),
        "assignmentCount": sum(row["assignmentCount"] for row in rows),
        "mergeCount": sum(row["mergeCount"] for row in rows),
        "maxBranchDepth": max(row["branchDepth"] for row in rows),
        "allFixturesBlocked": all(row["status"] == "blocked_fixture_defined" for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "schemaFragmentsValidate": True,
        "assignmentPhiSupportClaim": False,
        "assignmentPhiRuntimeExecutionClaim": False,
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
    p65_packet = read_json(P65_PACKET)
    rows = matrix_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p66-assignment-phi-fixture-gate",
        "decision": "assignment_phi_fixture_gate_recorded_support_blocked",
        "sourcePackets": [
            {
                "phase": "P61",
                "packetPath": str(P61_PACKET.relative_to(ROOT)),
                "reviewDecision": p61_packet["reviewDecision"],
                "validationStatus": p61_packet["validationStatus"],
            },
            {
                "phase": "P65",
                "packetPath": str(P65_PACKET.relative_to(ROOT)),
                "reviewDecision": p65_packet["reviewDecision"],
                "validationStatus": p65_packet["validationStatus"],
            },
        ],
        "assignmentPhiFixtures": rows,
        "summary": build_summary(p61_packet, p65_packet, rows),
        "releaseGates": [
            {"id": "assignment_phi_fixture_gate", "status": "recorded"},
            {"id": "assignment_phi_runtime_execution", "status": "not_performed"},
            {"id": "assignment_phi_support", "status": "blocked"},
            {"id": "control_flow_ir_implementation", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "branch_control_flow_reingest", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P66 records blocked assignment/phi fixtures for private review.",
            "The gate covers selected C and Rust mutable-assignment merge shapes.",
            "P66 does not execute, lower, or claim support for assignment/phi constructs.",
        ],
        "blockedStatements": [
            "Assignment/phi lowering is implemented.",
            "Mutable assignments across branches are supported.",
            "Assignment/phi fixtures were executed.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Attach deterministic expected samples to one assignment/phi fixture.",
            "Build a compound-condition semantics gate for short-circuit shape.",
            "Keep assignment/phi support blocked until runtime, lowering, and re-ingest evidence exists.",
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
        "title": "FEF-P66 Assignment/Phi Fixture Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "assignment_phi_fixtures_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Assignment/phi fixture gate only; no runtime execution, assignment/phi lowering, support, frontend widening, branch re-ingest, full source roundtrip, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P66 records three blocked assignment/phi fixture shapes.",
            "The fixtures cover C and Rust mutable-assignment merge surfaces.",
            "Assignment/phi support and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p66_assignment_phi_fixture_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p66_assignment_phi_fixture_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p66_assignment_phi_fixture_gate.v0",
        "date": DATE,
        "title": "FEF-P66 Assignment/Phi Fixture Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach deterministic expected samples to one assignment/phi fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        "| Fixture | Language | Shape | Assignments | Merges | Status |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in payload["assignmentPhiFixtures"]:
        rows.append(
            f"| `{row['id']}` | `{row['sourceLanguage']}` | `{row['shape']}` | {row['assignmentCount']} | {row['mergeCount']} | `{row['status']}` |"
        )
    return "\n".join(
        [
            "# FEF-P66 Assignment/Phi Fixture Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P66 records blocked assignment/phi fixtures for mutable assignments across branches.",
            "",
            "## Summary",
            "",
            f"- Fixtures: `{summary['fixtureCount']}`",
            f"- C fixtures: `{summary['cFixtureCount']}`",
            f"- Rust fixtures: `{summary['rustFixtureCount']}`",
            f"- Total assignment sites: `{summary['assignmentCount']}`",
            f"- Total merge sites: `{summary['mergeCount']}`",
            f"- All fixtures blocked: `{summary['allFixturesBlocked']}`",
            f"- Runtime execution performed: `{not summary['allRuntimeExecutionNotPerformed']}`",
            f"- Assignment/phi support claim: `{summary['assignmentPhiSupportClaim']}`",
            f"- Control-flow IR implemented: `{summary['controlFlowIrImplemented']}`",
            f"- Frontend lowering changed: `{summary['frontendLoweringChanged']}`",
            "",
            "## Fixtures",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Fixture gate only; no assignment/phi execution.",
            "- No assignment/phi lowering or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_fixture(row: dict[str, Any]) -> None:
    if row["constructId"] != "mutable_assignments_across_branches":
        raise ValueError("fixture must target mutable assignment construct")
    if row["status"] != "blocked_fixture_defined":
        raise ValueError("assignment/phi fixture must remain blocked")
    if row["supportClaimAllowed"] is not False:
        raise ValueError("assignment/phi support claim must remain false")
    if row["runtimeExecutionPerformed"] is not False:
        raise ValueError("assignment/phi runtime execution must not be performed")
    fragment = row["schemaFragment"]
    p60.validate_fragment(fragment)
    statement = fragment["blocks"][0]["statements"][0]
    if statement["constructId"] != "mutable_assignments_across_branches":
        raise ValueError("schema fragment must be blocked by mutable assignment construct")
    if not all(value is False for value in fragment["claimFlags"].values()):
        raise ValueError("fragment claim flags must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P66 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P66 status")
    for row in payload["assignmentPhiFixtures"]:
        validate_fixture(row)
    summary = payload["summary"]
    for key in [
        "p61ValidationPass",
        "p61ClaimFlagsAllFalse",
        "p65ValidationPass",
        "p65ClaimFlagsAllFalse",
        "allFixturesBlocked",
        "allRuntimeExecutionNotPerformed",
        "schemaFragmentsValidate",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["fixtureCount"] != 3:
        raise ValueError("expected three assignment/phi fixtures")
    if summary["cFixtureCount"] != 2 or summary["rustFixtureCount"] != 1:
        raise ValueError("unexpected language fixture counts")
    if summary["assignmentCount"] != 7 or summary["mergeCount"] != 3:
        raise ValueError("unexpected assignment/merge counts")
    for key in [
        "assignmentPhiSupportClaim",
        "assignmentPhiRuntimeExecutionClaim",
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
    result_path = out_dir / f"fef_p66_assignment_phi_fixture_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p66_assignment_phi_fixture_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p66_assignment_phi_fixture_gate.json"
    feed_path = command_feed_dir / f"fef_p66_assignment_phi_fixture_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p66_assignment_phi_fixture_gate")
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
    print("FEF_P66_ASSIGNMENT_PHI_FIXTURE_GATE_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
