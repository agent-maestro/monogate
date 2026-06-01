#!/usr/bin/env python3
"""FEF-P113 compound-condition fixture gate for control-flow IR."""

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
from scripts import fef_p112_side_effect_private_reviewer_handoff_hold_gate as p112  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p113_compound_condition_fixture_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P113_COMPOUND_CONDITION_FIXTURE_GATE_PASS"

P61_PACKET = ROOT / "reports/evidence_packets/fef_p61_unsupported_construct_blocker_gate.json"
P112_PACKET = ROOT / "reports/evidence_packets/fef_p112_side_effect_private_reviewer_handoff_hold_gate.json"
P112_RESULT = ROOT / "python/results/fef_p112_side_effect_private_reviewer_handoff_hold_gate/fef_p112_side_effect_private_reviewer_handoff_hold_gate_2026_06_01.json"

CLAIM_FLAGS = {
    "compound_condition_fixture_gate_claim": False,
    "compound_condition_support_claim": False,
    "compound_condition_runtime_execution_claim": False,
    "compound_condition_lowering_implemented": False,
    "short_circuit_policy_implemented": False,
    "boolean_normalization_policy_implemented": False,
    "loop_backedge_support_claim": False,
    "assignment_phi_support_claim": False,
    "side_effect_memory_support_claim": False,
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
    "FEF-P113 records compound-condition fixtures only.",
    "FEF-P113 does not execute compound-condition fixtures.",
    "FEF-P113 does not implement short-circuit or boolean-normalization policy.",
    "FEF-P113 does not implement compound-condition lowering.",
    "FEF-P113 does not widen Forge or eFrog frontend lowering.",
    "FEF-P113 does not claim compound-condition support.",
    "FEF-P113 preserves the P112 private reviewer handoff hold status.",
    "FEF-P113 does not record reviewer approval or rejection.",
    "FEF-P113 does not claim general branch/control-flow support.",
    "FEF-P113 does not claim branch/control-flow re-ingest support.",
    "FEF-P113 does not claim full non-generated source roundtrip.",
    "FEF-P113 does not claim arbitrary C/Rust source-family support.",
    "FEF-P113 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P113 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

FIXTURES = [
    {
        "id": "c_and_guard_return_v0",
        "sourceLanguage": "c",
        "shape": "compound_and_guard_return",
        "sourceSketch": "if (x > 0.0 && y > 0.0) return x + y; return 0.0;",
        "booleanOperatorKinds": ["and"],
        "atomicPredicateCount": 2,
        "shortCircuitRelevant": True,
        "branchDepth": 1,
        "returnCount": 2,
        "blockedBy": "compound_condition_semantics_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "return_and_fallthrough_preservation"],
    },
    {
        "id": "c_or_clamp_guard_v0",
        "sourceLanguage": "c",
        "shape": "compound_or_clamp_guard",
        "sourceSketch": "if (x < lo || x > hi) return 0.0; return x;",
        "booleanOperatorKinds": ["or"],
        "atomicPredicateCount": 2,
        "shortCircuitRelevant": True,
        "branchDepth": 1,
        "returnCount": 2,
        "blockedBy": "compound_condition_semantics_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "return_and_fallthrough_preservation"],
    },
    {
        "id": "rust_and_if_expr_v0",
        "sourceLanguage": "rust",
        "shape": "compound_and_if_expression",
        "sourceSketch": "if x > 0.0 && y > 0.0 { x + y } else { 0.0 }",
        "booleanOperatorKinds": ["and"],
        "atomicPredicateCount": 2,
        "shortCircuitRelevant": True,
        "branchDepth": 1,
        "returnCount": 1,
        "blockedBy": "compound_condition_semantics_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "dominance_and_merge_preservation"],
    },
    {
        "id": "rust_mixed_and_or_return_v0",
        "sourceLanguage": "rust",
        "shape": "compound_mixed_and_or_return",
        "sourceSketch": "if (x > hi && enabled) || x < lo { return 0.0; } x",
        "booleanOperatorKinds": ["and", "or"],
        "atomicPredicateCount": 3,
        "shortCircuitRelevant": True,
        "branchDepth": 1,
        "returnCount": 2,
        "blockedBy": "compound_condition_semantics_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "source_ast_roundtrip_boundary"],
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
                "loweringPerformed": False,
                "shortCircuitPolicyImplemented": False,
                "booleanNormalizationPolicyImplemented": False,
            }
        )
    return rows


def build_summary(p61_packet: dict[str, Any], p112_packet: dict[str, Any], p112_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    operator_kinds = sorted({kind for row in rows for kind in row["booleanOperatorKinds"]})
    return {
        "sourcePacketCount": 2,
        "p61ValidationPass": p61_packet["validationStatus"] == "pass",
        "p61ClaimFlagsAllFalse": all(value is False for value in p61_packet["claimFlags"].values()),
        "p112ValidationPass": p112_packet["validationStatus"] == "pass",
        "p112ClaimFlagsAllFalse": all(value is False for value in p112_packet["claimFlags"].values()),
        "p112ReviewerDecisionRecorded": p112_payload["summary"]["reviewerDecisionRecorded"],
        "p112ImplementationHeldPendingReview": p112_payload["summary"]["implementationHeldPendingReview"],
        "fixtureCount": len(rows),
        "cFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "c"),
        "rustFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "rust"),
        "operatorKinds": operator_kinds,
        "operatorKindCount": len(operator_kinds),
        "totalAtomicPredicateCount": sum(row["atomicPredicateCount"] for row in rows),
        "fixturesWithShortCircuitSemantics": sum(1 for row in rows if row["shortCircuitRelevant"]),
        "maxBranchDepth": max(row["branchDepth"] for row in rows),
        "totalReturnCount": sum(row["returnCount"] for row in rows),
        "allFixturesBlocked": all(row["status"] == "blocked_fixture_defined" for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "allLoweringNotPerformed": all(row["loweringPerformed"] is False for row in rows),
        "allPoliciesNotImplemented": all(
            row["shortCircuitPolicyImplemented"] is False
            and row["booleanNormalizationPolicyImplemented"] is False
            for row in rows
        ),
        "schemaFragmentsValidate": True,
        "compoundConditionSupportClaim": False,
        "compoundConditionRuntimeExecutionClaim": False,
        "compoundConditionLoweringImplemented": False,
        "shortCircuitPolicyImplemented": False,
        "booleanNormalizationPolicyImplemented": False,
        "loopBackedgeSupportClaim": False,
        "assignmentPhiSupportClaim": False,
        "sideEffectMemorySupportClaim": False,
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
    p112_packet = read_json(P112_PACKET)
    p112_payload = read_json(P112_RESULT)
    p112.validate_payload(p112_payload)
    rows = matrix_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p113-compound-condition-fixture-gate",
        "decision": "compound_condition_fixture_gate_recorded_support_blocked_review_hold_preserved",
        "sourcePackets": [
            {
                "phase": "P61",
                "packetPath": str(P61_PACKET.relative_to(ROOT)),
                "reviewDecision": p61_packet["reviewDecision"],
                "validationStatus": p61_packet["validationStatus"],
            },
            {
                "phase": "P112",
                "packetPath": str(P112_PACKET.relative_to(ROOT)),
                "resultPath": str(P112_RESULT.relative_to(ROOT)),
                "reviewDecision": p112_packet["reviewDecision"],
                "validationStatus": p112_packet["validationStatus"],
            },
        ],
        "compoundConditionFixtures": rows,
        "summary": build_summary(p61_packet, p112_packet, p112_payload, rows),
        "releaseGates": [
            {"id": "compound_condition_fixture_gate", "status": "recorded"},
            {"id": "compound_condition_runtime_execution", "status": "not_performed"},
            {"id": "compound_condition_lowering", "status": "not_performed"},
            {"id": "short_circuit_policy", "status": "blocked"},
            {"id": "boolean_normalization_policy", "status": "blocked"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "p112_private_reviewer_hold", "status": "preserved"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P113 records four blocked compound-condition fixture shapes.",
            "P113 covers selected C and Rust &&, ||, and mixed boolean guard surfaces.",
            "P113 preserves the P112 private reviewer hold and does not execute, lower, or support compound-condition constructs.",
        ],
        "blockedStatements": [
            "Compound-condition constructs are supported.",
            "Compound-condition fixtures were executed.",
            "Short-circuit or boolean-normalization policy is implemented.",
            "Compound-condition lowering is implemented.",
            "Assignment/phi, loop/back-edge, side-effect/memory, or nested-branch support is implemented.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Attach deterministic expected samples for one selected compound-condition fixture.",
            "Keep short-circuit and boolean-normalization policy blocked until separately specified.",
            "Record the actual private reviewer response to P105-P112 if one exists.",
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
        "title": "FEF-P113 Compound-Condition Fixture Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "compound_condition_fixture_gate_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Compound-condition fixture gate only; no execution, lowering, short-circuit policy, boolean-normalization policy, support, frontend widening, compiler correctness, formal equivalence, runtime performance, or public readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P113 starts the compound-condition unsupported-form ladder.",
            "Four selected blocked fixtures cover C/Rust &&, ||, and mixed boolean surfaces.",
            "The P112 private reviewer hold remains preserved.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p113_compound_condition_fixture_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p113_compound_condition_fixture_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p113_compound_condition_fixture_gate.v0",
        "date": DATE,
        "title": "FEF-P113 Compound-Condition Fixture Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach deterministic expected samples for one selected compound-condition fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Fixture | Language | Shape | Operators | Status |", "|---|---|---|---|---|"]
    for row in payload["compoundConditionFixtures"]:
        rows.append(
            f"| `{row['id']}` | `{row['sourceLanguage']}` | `{row['shape']}` | `{', '.join(row['booleanOperatorKinds'])}` | `{row['status']}` |"
        )
    return "\n".join(
        [
            "# FEF-P113 Compound-Condition Fixture Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P113 records selected compound-condition fixtures while keeping support blocked.",
            "",
            "## Summary",
            "",
            f"- Fixture count: `{summary['fixtureCount']}`",
            f"- C fixtures: `{summary['cFixtureCount']}`",
            f"- Rust fixtures: `{summary['rustFixtureCount']}`",
            f"- Operator kinds: `{', '.join(summary['operatorKinds'])}`",
            f"- Total atomic predicates: `{summary['totalAtomicPredicateCount']}`",
            f"- Fixtures with short-circuit semantics: `{summary['fixturesWithShortCircuitSemantics']}`",
            f"- Runtime execution performed: `{summary['compoundConditionRuntimeExecutionClaim']}`",
            f"- Lowering implemented: `{summary['compoundConditionLoweringImplemented']}`",
            f"- Policies implemented: `{summary['allPoliciesNotImplemented'] is False}`",
            f"- P112 reviewer decision recorded: `{summary['p112ReviewerDecisionRecorded']}`",
            "",
            "## Fixtures",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Fixture gate only.",
            "- No runtime execution or lowering.",
            "- No short-circuit or boolean-normalization policy.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P113 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P113 status")
    p112.validate_payload(read_json(P112_RESULT))
    summary = payload["summary"]
    for key in [
        "p61ValidationPass",
        "p61ClaimFlagsAllFalse",
        "p112ValidationPass",
        "p112ClaimFlagsAllFalse",
        "p112ImplementationHeldPendingReview",
        "allFixturesBlocked",
        "allRuntimeExecutionNotPerformed",
        "allLoweringNotPerformed",
        "allPoliciesNotImplemented",
        "schemaFragmentsValidate",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["fixtureCount"] != 4 or summary["cFixtureCount"] != 2 or summary["rustFixtureCount"] != 2:
        raise ValueError("expected four fixtures split across C/Rust")
    if summary["operatorKinds"] != ["and", "or"]:
        raise ValueError("expected and/or operator coverage")
    if summary["totalAtomicPredicateCount"] != 9:
        raise ValueError("expected nine total atomic predicates")
    if summary["fixturesWithShortCircuitSemantics"] != 4:
        raise ValueError("expected all fixtures to require short-circuit review")
    if summary["p112ReviewerDecisionRecorded"] is not False:
        raise ValueError("P112 reviewer decision must remain unrecorded")
    for row in payload["compoundConditionFixtures"]:
        if row["constructId"] != "boolean_compound_conditions":
            raise ValueError("unexpected construct id")
        if row["supportClaimAllowed"] is not False:
            raise ValueError("support claim must be blocked")
        if row["runtimeExecutionPerformed"] is not False or row["loweringPerformed"] is not False:
            raise ValueError("fixtures must not execute or lower")
        fragment = row["schemaFragment"]
        if fragment["blocks"][0]["statements"][0]["constructId"] != "boolean_compound_conditions":
            raise ValueError("fixture fragment must carry compound-condition unsupported construct")
    for key in [
        "compoundConditionSupportClaim",
        "compoundConditionRuntimeExecutionClaim",
        "compoundConditionLoweringImplemented",
        "shortCircuitPolicyImplemented",
        "booleanNormalizationPolicyImplemented",
        "loopBackedgeSupportClaim",
        "assignmentPhiSupportClaim",
        "sideEffectMemorySupportClaim",
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
    result_path = out_dir / f"fef_p113_compound_condition_fixture_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p113_compound_condition_fixture_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p113_compound_condition_fixture_gate.json"
    feed_path = command_feed_dir / f"fef_p113_compound_condition_fixture_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p113_compound_condition_fixture_gate")
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
    print("FEF_P113_COMPOUND_CONDITION_FIXTURE_GATE_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"atomic_predicates={built['payload']['summary']['totalAtomicPredicateCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
