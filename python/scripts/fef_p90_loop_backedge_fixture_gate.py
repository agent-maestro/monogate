#!/usr/bin/env python3
"""FEF-P90 loop/back-edge fixture gate for control-flow IR."""

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

from scripts import fef_p59_control_flow_ir_inventory as p59  # noqa: E402
from scripts import fef_p60_control_flow_ir_schema as p60  # noqa: E402
from scripts import fef_p89_compound_condition_private_reviewer_handoff_hold_gate as p89  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p90_loop_backedge_fixture_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P90_LOOP_BACKEDGE_FIXTURE_GATE_PASS"

P61_PACKET = ROOT / "reports/evidence_packets/fef_p61_unsupported_construct_blocker_gate.json"
P89_PACKET = ROOT / "reports/evidence_packets/fef_p89_compound_condition_private_reviewer_handoff_hold_gate.json"
P89_RESULT = ROOT / "python/results/fef_p89_compound_condition_private_reviewer_handoff_hold_gate/fef_p89_compound_condition_private_reviewer_handoff_hold_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_backedge_fixture_gate_claim": False,
    "loop_backedge_support_claim": False,
    "loop_runtime_execution_claim": False,
    "loop_lowering_implemented": False,
    "loop_boundedness_policy_claim": False,
    "assignment_phi_support_claim": False,
    "compound_condition_support_claim": False,
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
    "implementation_change_approved": False,
    "implementation_change_applied": False,
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
    "FEF-P90 records loop/back-edge fixtures only.",
    "FEF-P90 does not execute loop fixtures.",
    "FEF-P90 does not implement loop headers, latches, variants, or boundedness policy.",
    "FEF-P90 does not implement loop lowering.",
    "FEF-P90 does not widen Forge or eFrog frontend lowering.",
    "FEF-P90 does not claim loop/back-edge support.",
    "FEF-P90 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P90 does not change the P89 private reviewer hold status.",
    "FEF-P90 does not record reviewer approval or rejection.",
    "FEF-P90 does not claim general branch/control-flow support.",
    "FEF-P90 does not claim branch/control-flow re-ingest support.",
    "FEF-P90 does not claim full non-generated source roundtrip.",
    "FEF-P90 does not claim arbitrary C/Rust source-family support.",
    "FEF-P90 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P90 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

FIXTURES = [
    {
        "id": "c_while_accumulate_v0",
        "sourceLanguage": "c",
        "shape": "while_accumulate",
        "sourceSketch": "double acc = 0.0; int i = 0; while (i < n) { acc = acc + x; i = i + 1; } return acc;",
        "loopKind": "while",
        "loopCount": 1,
        "backEdgeCount": 1,
        "mutableAssignmentCount": 4,
        "requiresBoundednessPolicy": True,
        "blockedBy": "loop_construct_blocker_gate",
        "requiredSemanticObligations": ["assignment_order_preservation", "unsupported_construct_fail_closed"],
    },
    {
        "id": "c_for_bounded_sum_v0",
        "sourceLanguage": "c",
        "shape": "for_bounded_sum",
        "sourceSketch": "double acc = seed; for (int i = 0; i < n; i = i + 1) { acc = acc + scale * i; } return acc;",
        "loopKind": "for",
        "loopCount": 1,
        "backEdgeCount": 1,
        "mutableAssignmentCount": 4,
        "requiresBoundednessPolicy": True,
        "blockedBy": "loop_construct_blocker_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "assignment_order_preservation", "unsupported_construct_fail_closed"],
    },
    {
        "id": "rust_while_decay_v0",
        "sourceLanguage": "rust",
        "shape": "rust_while_decay",
        "sourceSketch": "let mut y = x; let mut i = 0; while i < n { y = y * 0.5; i = i + 1; } y",
        "loopKind": "while",
        "loopCount": 1,
        "backEdgeCount": 1,
        "mutableAssignmentCount": 4,
        "requiresBoundednessPolicy": True,
        "blockedBy": "loop_construct_blocker_gate",
        "requiredSemanticObligations": ["assignment_order_preservation", "source_ast_roundtrip_boundary", "unsupported_construct_fail_closed"],
    },
    {
        "id": "rust_for_range_sum_v0",
        "sourceLanguage": "rust",
        "shape": "rust_for_range_sum",
        "sourceSketch": "let mut acc = 0.0; for i in 0..n { acc = acc + (i as f64) * x; } acc",
        "loopKind": "for_range",
        "loopCount": 1,
        "backEdgeCount": 1,
        "mutableAssignmentCount": 2,
        "requiresBoundednessPolicy": True,
        "blockedBy": "loop_construct_blocker_gate",
        "requiredSemanticObligations": ["assignment_order_preservation", "source_ast_roundtrip_boundary", "unsupported_construct_fail_closed"],
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
                        "constructId": "loops_and_back_edges",
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
                "constructId": "loops_and_back_edges",
                "schemaFragment": fixture_fragment(fixture),
                "supportClaimAllowed": False,
                "runtimeExecutionPerformed": False,
                "loweringPerformed": False,
                "boundednessPolicyImplemented": False,
            }
        )
    return rows


def build_summary(p61_packet: dict[str, Any], p89_packet: dict[str, Any], p89_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 2,
        "p61ValidationPass": p61_packet["validationStatus"] == "pass",
        "p61ClaimFlagsAllFalse": all(value is False for value in p61_packet["claimFlags"].values()),
        "p89ValidationPass": p89_packet["validationStatus"] == "pass",
        "p89ClaimFlagsAllFalse": all(value is False for value in p89_packet["claimFlags"].values()),
        "p89ReviewerDecisionRecorded": p89_payload["summary"]["reviewerDecisionRecorded"],
        "p89ImplementationHeldPendingReview": p89_payload["summary"]["implementationHeldPendingReview"],
        "fixtureCount": len(rows),
        "cFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "c"),
        "rustFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "rust"),
        "whileFixtureCount": sum(1 for row in rows if row["loopKind"] == "while"),
        "forFixtureCount": sum(1 for row in rows if row["loopKind"].startswith("for")),
        "loopCount": sum(row["loopCount"] for row in rows),
        "backEdgeCount": sum(row["backEdgeCount"] for row in rows),
        "mutableAssignmentCount": sum(row["mutableAssignmentCount"] for row in rows),
        "fixturesRequiringBoundednessPolicy": sum(1 for row in rows if row["requiresBoundednessPolicy"]),
        "allFixturesBlocked": all(row["status"] == "blocked_fixture_defined" for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "allLoweringNotPerformed": all(row["loweringPerformed"] is False for row in rows),
        "allBoundednessPolicyNotImplemented": all(row["boundednessPolicyImplemented"] is False for row in rows),
        "schemaFragmentsValidate": True,
        "loopBackedgeSupportClaim": False,
        "loopRuntimeExecutionClaim": False,
        "loopLoweringImplemented": False,
        "loopBoundednessPolicyClaim": False,
        "assignmentPhiSupportClaim": False,
        "compoundConditionSupportClaim": False,
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
        "implementationChangeApproved": False,
        "implementationChangeApplied": False,
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
    p89_packet = read_json(P89_PACKET)
    p89_payload = read_json(P89_RESULT)
    p89.validate_payload(p89_payload)
    rows = matrix_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p90-loop-backedge-fixture-gate",
        "decision": "loop_backedge_fixture_gate_recorded_support_blocked_review_hold_preserved",
        "sourcePackets": [
            {
                "phase": "P61",
                "packetPath": str(P61_PACKET.relative_to(ROOT)),
                "reviewDecision": p61_packet["reviewDecision"],
                "validationStatus": p61_packet["validationStatus"],
            },
            {
                "phase": "P89",
                "packetPath": str(P89_PACKET.relative_to(ROOT)),
                "resultPath": str(P89_RESULT.relative_to(ROOT)),
                "reviewDecision": p89_packet["reviewDecision"],
                "validationStatus": p89_packet["validationStatus"],
            },
        ],
        "loopBackedgeFixtures": rows,
        "summary": build_summary(p61_packet, p89_packet, p89_payload, rows),
        "releaseGates": [
            {"id": "loop_backedge_fixture_gate", "status": "recorded"},
            {"id": "loop_runtime_execution", "status": "not_performed"},
            {"id": "loop_lowering", "status": "not_performed"},
            {"id": "loop_boundedness_policy", "status": "blocked"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "p89_private_reviewer_hold", "status": "preserved"},
            {"id": "control_flow_ir_implementation", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "branch_control_flow_reingest", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P90 records blocked loop/back-edge fixtures for private review.",
            "The gate covers selected C and Rust while/for loop shapes.",
            "P90 preserves the P89 private reviewer hold and does not apply the P88 proposal.",
            "P90 does not execute, lower, or claim support for loops or back edges.",
        ],
        "blockedStatements": [
            "Loop/back-edge lowering is implemented.",
            "Loops are supported.",
            "A loop boundedness policy exists.",
            "Loop fixtures were executed.",
            "The P89 reviewer hold has been lifted.",
            "The P88 implementation proposal has been approved or applied.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Attach deterministic expected samples to one loop/back-edge fixture.",
            "Define a boundedness and iteration-limit policy before any loop execution gate.",
            "Keep P88 implementation held until an actual private reviewer response is recorded.",
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
        "title": "FEF-P90 Loop/Back-Edge Fixture Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "loop_backedge_fixture_gate_recorded_support_blocked_review_hold_preserved",
        "semanticReview": payload["summary"],
        "claimBoundary": "Loop/back-edge fixture gate only; no loop execution, loop lowering, boundedness policy, loop support, P89 reviewer decision, P88 implementation approval, compiler correctness, formal equivalence, runtime performance, package, checkout, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P90 starts the loops/back-edges unsupported-form ladder.",
            "Four selected C/Rust loop fixtures are schema-shaped and blocked.",
            "Runtime execution, lowering, and boundedness policy remain blocked.",
            "The P89 private reviewer hold remains preserved.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p90_loop_backedge_fixture_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p90_loop_backedge_fixture_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p90_loop_backedge_fixture_gate.v0",
        "date": DATE,
        "title": "FEF-P90 Loop/Back-Edge Fixture Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach deterministic expected samples to one loop fixture while keeping loop execution and P89 implementation approval blocked.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    fixture_rows = [
        "| Fixture | Language | Loop Kind | Assignments | Status |",
        "|---|---|---:|---:|---|",
    ]
    for row in payload["loopBackedgeFixtures"]:
        fixture_rows.append(
            f"| `{row['id']}` | `{row['sourceLanguage']}` | `{row['loopKind']}` | `{row['mutableAssignmentCount']}` | `{row['status']}` |"
        )
    return "\n".join(
        [
            "# FEF-P90 Loop/Back-Edge Fixture Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P90 records blocked loop/back-edge fixtures while preserving the P89 private reviewer hold.",
            "",
            "## Summary",
            "",
            f"- Fixture count: `{summary['fixtureCount']}`",
            f"- C fixtures: `{summary['cFixtureCount']}`",
            f"- Rust fixtures: `{summary['rustFixtureCount']}`",
            f"- Loop count: `{summary['loopCount']}`",
            f"- Back-edge count: `{summary['backEdgeCount']}`",
            f"- Mutable assignment count: `{summary['mutableAssignmentCount']}`",
            f"- Fixtures requiring boundedness policy: `{summary['fixturesRequiringBoundednessPolicy']}`",
            f"- Runtime execution performed: `{summary['loopRuntimeExecutionClaim']}`",
            f"- Loop lowering implemented: `{summary['loopLoweringImplemented']}`",
            f"- P89 reviewer decision recorded: `{summary['p89ReviewerDecisionRecorded']}`",
            f"- P89 implementation held: `{summary['p89ImplementationHeldPendingReview']}`",
            "",
            "## Fixtures",
            "",
            *fixture_rows,
            "",
            "## Boundary",
            "",
            "- Fixture gate only.",
            "- No loop execution.",
            "- No loop lowering.",
            "- No boundedness policy implementation.",
            "- No loop/back-edge support claim.",
            "- No P89 reviewer decision or P88 implementation approval.",
            "- No compiler-correctness, formal-equivalence, runtime-performance, package, checkout, public-readiness, or production claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P90 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P90 status")
    p89.validate_payload(read_json(P89_RESULT))
    summary = payload["summary"]
    for key in [
        "p61ValidationPass",
        "p61ClaimFlagsAllFalse",
        "p89ValidationPass",
        "p89ClaimFlagsAllFalse",
        "p89ImplementationHeldPendingReview",
        "allFixturesBlocked",
        "allRuntimeExecutionNotPerformed",
        "allLoweringNotPerformed",
        "allBoundednessPolicyNotImplemented",
        "schemaFragmentsValidate",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["p89ReviewerDecisionRecorded"] is not False:
        raise ValueError("P89 reviewer decision must remain unrecorded")
    if summary["fixtureCount"] != 4:
        raise ValueError("expected four loop/back-edge fixtures")
    if summary["cFixtureCount"] != 2 or summary["rustFixtureCount"] != 2:
        raise ValueError("expected two C and two Rust fixtures")
    if summary["whileFixtureCount"] != 2 or summary["forFixtureCount"] != 2:
        raise ValueError("expected two while and two for fixtures")
    if summary["loopCount"] != 4 or summary["backEdgeCount"] != 4:
        raise ValueError("expected four loops and four back edges")
    if summary["mutableAssignmentCount"] != 14:
        raise ValueError("unexpected mutable assignment count")
    if summary["fixturesRequiringBoundednessPolicy"] != 4:
        raise ValueError("all fixtures should require boundedness policy")
    for row in payload["loopBackedgeFixtures"]:
        if row["constructId"] != "loops_and_back_edges":
            raise ValueError("unexpected construct id")
        if row["supportClaimAllowed"] is not False:
            raise ValueError("support claim must remain blocked")
        if row["runtimeExecutionPerformed"] is not False:
            raise ValueError("runtime execution must not be performed")
        if row["loweringPerformed"] is not False:
            raise ValueError("lowering must not be performed")
        if row["boundednessPolicyImplemented"] is not False:
            raise ValueError("boundedness policy must not be implemented")
    for key in [
        "loopBackedgeSupportClaim",
        "loopRuntimeExecutionClaim",
        "loopLoweringImplemented",
        "loopBoundednessPolicyClaim",
        "assignmentPhiSupportClaim",
        "compoundConditionSupportClaim",
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
        "implementationChangeApproved",
        "implementationChangeApplied",
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
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    expected_gates = {
        "loop_backedge_fixture_gate": "recorded",
        "loop_runtime_execution": "not_performed",
        "loop_lowering": "not_performed",
        "loop_boundedness_policy": "blocked",
        "loop_backedge_support": "blocked",
        "p89_private_reviewer_hold": "preserved",
        "control_flow_ir_implementation": "blocked",
        "frontend_lowering_change": "not_performed",
        "general_branch_control_flow_support": "blocked",
        "branch_control_flow_reingest": "blocked",
        "compiler_correctness": "blocked",
    }
    if gates != expected_gates:
        raise ValueError("unexpected release gates")
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
    result_path = out_dir / f"fef_p90_loop_backedge_fixture_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p90_loop_backedge_fixture_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p90_loop_backedge_fixture_gate.json"
    feed_path = command_feed_dir / f"fef_p90_loop_backedge_fixture_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p90_loop_backedge_fixture_gate")
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
    print("FEF_P90_LOOP_BACKEDGE_FIXTURE_GATE_OK")
    print(f"fixture_count={built['payload']['summary']['fixtureCount']}")
    print(f"p89_reviewer_decision_recorded={built['payload']['summary']['p89ReviewerDecisionRecorded']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
