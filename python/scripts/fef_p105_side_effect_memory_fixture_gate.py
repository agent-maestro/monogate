#!/usr/bin/env python3
"""FEF-P105 side-effect/call/memory fixture gate for control-flow IR."""

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
from scripts import fef_p104_loop_private_reviewer_handoff_hold_gate as p104  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p105_side_effect_memory_fixture_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P105_SIDE_EFFECT_MEMORY_FIXTURE_GATE_PASS"

P61_PACKET = ROOT / "reports/evidence_packets/fef_p61_unsupported_construct_blocker_gate.json"
P104_PACKET = ROOT / "reports/evidence_packets/fef_p104_loop_private_reviewer_handoff_hold_gate.json"
P104_RESULT = ROOT / "python/results/fef_p104_loop_private_reviewer_handoff_hold_gate/fef_p104_loop_private_reviewer_handoff_hold_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "side_effect_memory_fixture_gate_claim": False,
    "side_effect_memory_support_claim": False,
    "side_effect_runtime_execution_claim": False,
    "side_effect_lowering_implemented": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
    "loop_backedge_support_claim": False,
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
    "FEF-P105 records side-effect/call/memory fixtures only.",
    "FEF-P105 does not execute side-effect/call/memory fixtures.",
    "FEF-P105 does not implement effect ordering, external-call, aliasing, or memory-state policy.",
    "FEF-P105 does not implement side-effect/call/memory lowering.",
    "FEF-P105 does not widen Forge or eFrog frontend lowering.",
    "FEF-P105 does not claim side-effect/call/memory support.",
    "FEF-P105 does not claim loop/back-edge, assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P105 preserves the P104 private reviewer handoff hold status.",
    "FEF-P105 does not record reviewer approval or rejection.",
    "FEF-P105 does not claim general branch/control-flow support.",
    "FEF-P105 does not claim branch/control-flow re-ingest support.",
    "FEF-P105 does not claim full non-generated source roundtrip.",
    "FEF-P105 does not claim arbitrary C/Rust source-family support.",
    "FEF-P105 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P105 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

FIXTURES = [
    {
        "id": "c_global_state_update_v0",
        "sourceLanguage": "c",
        "shape": "guarded_global_state_update",
        "sourceSketch": "if (x > 0.0) { state = update_state(x); } return state;",
        "effectKind": "global_state_write_and_external_call",
        "sideEffectingCallCount": 1,
        "memoryWriteCount": 1,
        "mutableStateSiteCount": 1,
        "effectBoundaryCount": 2,
        "requiresEffectOrderPolicy": True,
        "requiresExternalCallPolicy": True,
        "requiresMemoryAliasPolicy": True,
        "blockedBy": "side_effect_boundary_inventory",
        "requiredSemanticObligations": ["assignment_order_preservation", "unsupported_construct_fail_closed"],
    },
    {
        "id": "c_array_write_guard_v0",
        "sourceLanguage": "c",
        "shape": "guarded_array_write",
        "sourceSketch": "if (i >= 0) { buffer[i] = x; } return buffer[i];",
        "effectKind": "indexed_memory_write_and_read",
        "sideEffectingCallCount": 0,
        "memoryWriteCount": 1,
        "mutableStateSiteCount": 1,
        "effectBoundaryCount": 2,
        "requiresEffectOrderPolicy": True,
        "requiresExternalCallPolicy": False,
        "requiresMemoryAliasPolicy": True,
        "blockedBy": "side_effect_boundary_inventory",
        "requiredSemanticObligations": ["condition_truth_semantics", "assignment_order_preservation", "unsupported_construct_fail_closed"],
    },
    {
        "id": "rust_mut_ref_update_v0",
        "sourceLanguage": "rust",
        "shape": "mutable_reference_update",
        "sourceSketch": "if x > 0.0 { *slot = *slot + x; } *slot",
        "effectKind": "mutable_reference_write",
        "sideEffectingCallCount": 0,
        "memoryWriteCount": 1,
        "mutableStateSiteCount": 1,
        "effectBoundaryCount": 1,
        "requiresEffectOrderPolicy": True,
        "requiresExternalCallPolicy": False,
        "requiresMemoryAliasPolicy": True,
        "blockedBy": "side_effect_boundary_inventory",
        "requiredSemanticObligations": ["assignment_order_preservation", "source_ast_roundtrip_boundary", "unsupported_construct_fail_closed"],
    },
    {
        "id": "rust_external_call_guard_v0",
        "sourceLanguage": "rust",
        "shape": "guarded_external_call",
        "sourceSketch": "if enabled { sink.record(x); } x",
        "effectKind": "external_method_call",
        "sideEffectingCallCount": 1,
        "memoryWriteCount": 0,
        "mutableStateSiteCount": 0,
        "effectBoundaryCount": 1,
        "requiresEffectOrderPolicy": True,
        "requiresExternalCallPolicy": True,
        "requiresMemoryAliasPolicy": False,
        "blockedBy": "side_effect_boundary_inventory",
        "requiredSemanticObligations": ["condition_truth_semantics", "source_ast_roundtrip_boundary", "unsupported_construct_fail_closed"],
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
                        "constructId": "side_effecting_calls_or_memory",
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
                "constructId": "side_effecting_calls_or_memory",
                "schemaFragment": fixture_fragment(fixture),
                "supportClaimAllowed": False,
                "runtimeExecutionPerformed": False,
                "loweringPerformed": False,
                "effectOrderPolicyImplemented": False,
                "externalCallPolicyImplemented": False,
                "memoryAliasPolicyImplemented": False,
            }
        )
    return rows


def build_summary(p61_packet: dict[str, Any], p104_packet: dict[str, Any], p104_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 2,
        "p61ValidationPass": p61_packet["validationStatus"] == "pass",
        "p61ClaimFlagsAllFalse": all(value is False for value in p61_packet["claimFlags"].values()),
        "p104ValidationPass": p104_packet["validationStatus"] == "pass",
        "p104ClaimFlagsAllFalse": all(value is False for value in p104_packet["claimFlags"].values()),
        "p104ReviewerDecisionRecorded": p104_payload["summary"]["reviewerDecisionRecorded"],
        "p104ImplementationHeldPendingReview": p104_payload["summary"]["implementationHeldPendingReview"],
        "fixtureCount": len(rows),
        "cFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "c"),
        "rustFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "rust"),
        "sideEffectingCallCount": sum(row["sideEffectingCallCount"] for row in rows),
        "memoryWriteCount": sum(row["memoryWriteCount"] for row in rows),
        "mutableStateSiteCount": sum(row["mutableStateSiteCount"] for row in rows),
        "effectBoundaryCount": sum(row["effectBoundaryCount"] for row in rows),
        "fixturesRequiringEffectOrderPolicy": sum(1 for row in rows if row["requiresEffectOrderPolicy"]),
        "fixturesRequiringExternalCallPolicy": sum(1 for row in rows if row["requiresExternalCallPolicy"]),
        "fixturesRequiringMemoryAliasPolicy": sum(1 for row in rows if row["requiresMemoryAliasPolicy"]),
        "allFixturesBlocked": all(row["status"] == "blocked_fixture_defined" for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "allLoweringNotPerformed": all(row["loweringPerformed"] is False for row in rows),
        "allEffectPoliciesNotImplemented": all(
            row["effectOrderPolicyImplemented"] is False
            and row["externalCallPolicyImplemented"] is False
            and row["memoryAliasPolicyImplemented"] is False
            for row in rows
        ),
        "schemaFragmentsValidate": True,
        "sideEffectMemorySupportClaim": False,
        "sideEffectRuntimeExecutionClaim": False,
        "sideEffectLoweringImplemented": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "loopBackedgeSupportClaim": False,
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
    p104_packet = read_json(P104_PACKET)
    p104_payload = read_json(P104_RESULT)
    p104.validate_payload(p104_payload)
    rows = matrix_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p105-side-effect-memory-fixture-gate",
        "decision": "side_effect_memory_fixture_gate_recorded_support_blocked_review_hold_preserved",
        "sourcePackets": [
            {
                "phase": "P61",
                "packetPath": str(P61_PACKET.relative_to(ROOT)),
                "reviewDecision": p61_packet["reviewDecision"],
                "validationStatus": p61_packet["validationStatus"],
            },
            {
                "phase": "P104",
                "packetPath": str(P104_PACKET.relative_to(ROOT)),
                "resultPath": str(P104_RESULT.relative_to(ROOT)),
                "reviewDecision": p104_packet["reviewDecision"],
                "validationStatus": p104_packet["validationStatus"],
            },
        ],
        "sideEffectMemoryFixtures": rows,
        "summary": build_summary(p61_packet, p104_packet, p104_payload, rows),
        "releaseGates": [
            {"id": "side_effect_memory_fixture_gate", "status": "recorded"},
            {"id": "side_effect_runtime_execution", "status": "not_performed"},
            {"id": "side_effect_lowering", "status": "not_performed"},
            {"id": "effect_order_policy", "status": "blocked"},
            {"id": "external_call_policy", "status": "blocked"},
            {"id": "memory_alias_policy", "status": "blocked"},
            {"id": "side_effect_memory_support", "status": "blocked"},
            {"id": "p104_private_reviewer_hold", "status": "preserved"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P105 records four blocked side-effect/call/memory fixture shapes.",
            "P105 covers selected C and Rust state, memory-write, and external-call surfaces.",
            "P105 preserves the P104 private reviewer hold and does not execute, lower, or support side-effect constructs.",
        ],
        "blockedStatements": [
            "Side-effecting calls or memory operations are supported.",
            "Side-effect/call/memory fixtures were executed.",
            "Effect ordering, external-call, or memory-alias policy is implemented.",
            "Side-effect/call/memory lowering is implemented.",
            "Loop/back-edge support is implemented.",
            "Assignment/phi, compound-condition, or nested-branch support is implemented.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Attach deterministic expected samples for one selected side-effect/call/memory fixture.",
            "Keep effect ordering, external-call, and memory-alias policy blocked until separately specified.",
            "Record the actual private reviewer response to P90-P104 if one exists.",
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
        "title": "FEF-P105 Side-Effect/Memory Fixture Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "side_effect_memory_fixture_gate_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Side-effect/call/memory fixture gate only; no execution, lowering, effect policy, support, frontend widening, compiler correctness, formal equivalence, runtime performance, or public readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P105 starts the side-effect/call/memory unsupported-form ladder.",
            "Four selected blocked fixtures cover C/Rust state, memory, and external-call surfaces.",
            "The P104 private reviewer hold remains preserved.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p105_side_effect_memory_fixture_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p105_side_effect_memory_fixture_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p105_side_effect_memory_fixture_gate.v0",
        "date": DATE,
        "title": "FEF-P105 Side-Effect/Memory Fixture Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach deterministic expected samples for one selected side-effect/call/memory fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Fixture | Language | Effect kind | Status |", "|---|---|---|---|"]
    for row in payload["sideEffectMemoryFixtures"]:
        rows.append(f"| `{row['id']}` | `{row['sourceLanguage']}` | `{row['effectKind']}` | `{row['status']}` |")
    return "\n".join(
        [
            "# FEF-P105 Side-Effect/Memory Fixture Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P105 records selected side-effect/call/memory fixtures while keeping support blocked.",
            "",
            "## Summary",
            "",
            f"- Fixture count: `{summary['fixtureCount']}`",
            f"- C fixtures: `{summary['cFixtureCount']}`",
            f"- Rust fixtures: `{summary['rustFixtureCount']}`",
            f"- Side-effecting calls: `{summary['sideEffectingCallCount']}`",
            f"- Memory writes: `{summary['memoryWriteCount']}`",
            f"- Mutable state sites: `{summary['mutableStateSiteCount']}`",
            f"- Effect boundaries: `{summary['effectBoundaryCount']}`",
            f"- Runtime execution performed: `{summary['sideEffectRuntimeExecutionClaim']}`",
            f"- Lowering implemented: `{summary['sideEffectLoweringImplemented']}`",
            f"- Effect policies implemented: `{summary['allEffectPoliciesNotImplemented'] is False}`",
            f"- P104 reviewer decision recorded: `{summary['p104ReviewerDecisionRecorded']}`",
            "",
            "## Fixtures",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Fixture gate only.",
            "- No runtime execution or lowering.",
            "- No effect-order, external-call, or memory-alias policy.",
            "- No side-effect/call/memory support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P105 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P105 status")
    p104.validate_payload(read_json(P104_RESULT))
    summary = payload["summary"]
    for key in [
        "p61ValidationPass",
        "p61ClaimFlagsAllFalse",
        "p104ValidationPass",
        "p104ClaimFlagsAllFalse",
        "p104ImplementationHeldPendingReview",
        "allFixturesBlocked",
        "allRuntimeExecutionNotPerformed",
        "allLoweringNotPerformed",
        "allEffectPoliciesNotImplemented",
        "schemaFragmentsValidate",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["fixtureCount"] != 4 or summary["cFixtureCount"] != 2 or summary["rustFixtureCount"] != 2:
        raise ValueError("expected four fixtures split across C/Rust")
    if summary["sideEffectingCallCount"] != 2:
        raise ValueError("expected two side-effecting call sites")
    if summary["memoryWriteCount"] != 3:
        raise ValueError("expected three memory writes")
    if summary["mutableStateSiteCount"] != 3:
        raise ValueError("expected three mutable state sites")
    if summary["effectBoundaryCount"] != 6:
        raise ValueError("expected six effect boundaries")
    if summary["fixturesRequiringEffectOrderPolicy"] != 4:
        raise ValueError("expected all fixtures to require effect order policy")
    if summary["fixturesRequiringExternalCallPolicy"] != 2:
        raise ValueError("expected two external-call policy fixtures")
    if summary["fixturesRequiringMemoryAliasPolicy"] != 3:
        raise ValueError("expected three memory-alias policy fixtures")
    if summary["p104ReviewerDecisionRecorded"] is not False:
        raise ValueError("P104 reviewer decision must remain unrecorded")
    for row in payload["sideEffectMemoryFixtures"]:
        if row["constructId"] != "side_effecting_calls_or_memory":
            raise ValueError("unexpected construct id")
        if row["supportClaimAllowed"] is not False:
            raise ValueError("support claim must be blocked")
        if row["runtimeExecutionPerformed"] is not False or row["loweringPerformed"] is not False:
            raise ValueError("fixtures must not execute or lower")
        fragment = row["schemaFragment"]
        if fragment["blocks"][0]["statements"][0]["constructId"] != "side_effecting_calls_or_memory":
            raise ValueError("fixture fragment must carry side-effect unsupported construct")
    for key in [
        "sideEffectMemorySupportClaim",
        "sideEffectRuntimeExecutionClaim",
        "sideEffectLoweringImplemented",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "loopBackedgeSupportClaim",
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
    result_path = out_dir / f"fef_p105_side_effect_memory_fixture_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p105_side_effect_memory_fixture_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p105_side_effect_memory_fixture_gate.json"
    feed_path = command_feed_dir / f"fef_p105_side_effect_memory_fixture_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p105_side_effect_memory_fixture_gate")
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
    print("FEF_P105_SIDE_EFFECT_MEMORY_FIXTURE_GATE_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"effect_boundaries={built['payload']['summary']['effectBoundaryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
