#!/usr/bin/env python3
"""FEF-P110 generated-target runtime blocker for selected side effects."""

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

from scripts import fef_p109_side_effect_original_c_stubbed_runtime_gate as p109  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p110_side_effect_generated_target_runtime_blocker.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P110_SIDE_EFFECT_GENERATED_TARGET_RUNTIME_BLOCKER_PASS"

P109_PACKET = ROOT / "reports/evidence_packets/fef_p109_side_effect_original_c_stubbed_runtime_gate.json"
P109_RESULT = ROOT / "python/results/fef_p109_side_effect_original_c_stubbed_runtime_gate/fef_p109_side_effect_original_c_stubbed_runtime_gate_2026_06_01.json"

CLAIM_FLAGS = {
    "side_effect_generated_target_runtime_blocker_claim": False,
    "generated_target_execution_claim": False,
    "reingest_execution_claim": False,
    "live_external_call_claim": False,
    "unbounded_memory_mutation_claim": False,
    "side_effect_lowering_implemented": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
    "side_effect_memory_support_claim": False,
    "side_effect_codegen_policy_claim": False,
    "side_effect_reingest_policy_claim": False,
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
    "FEF-P110 records a generated-target runtime blocker for the selected side-effect fixture only.",
    "FEF-P110 does not execute generated target code.",
    "FEF-P110 does not execute re-ingested code.",
    "FEF-P110 does not perform live external calls.",
    "FEF-P110 does not perform unbounded memory mutation or aliasing.",
    "FEF-P110 does not implement side-effect/call/memory lowering.",
    "FEF-P110 does not implement generated side-effect codegen policy.",
    "FEF-P110 does not implement side-effect re-ingest policy.",
    "FEF-P110 does not implement effect ordering, external-call, aliasing, or memory-state policy in Forge or eFrog.",
    "FEF-P110 does not widen Forge or eFrog frontend lowering.",
    "FEF-P110 does not claim side-effect/call/memory support.",
    "FEF-P110 does not claim loop/back-edge, assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P110 does not record reviewer approval or rejection.",
    "FEF-P110 does not claim general branch/control-flow support.",
    "FEF-P110 does not claim branch/control-flow re-ingest support.",
    "FEF-P110 does not claim full non-generated source roundtrip.",
    "FEF-P110 does not claim arbitrary C/Rust source-family support.",
    "FEF-P110 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P110 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def generated_target_gate(p109_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "gateId": "side_effect_generated_target_runtime_gate_v0",
        "selectedFixtureId": p109_payload["summary"]["selectedFixtureId"],
        "status": "blocked_not_run",
        "blockedBy": "side_effect_lowering_and_codegen_policy_missing",
        "requiredBeforeRun": [
            "selected_side_effect_lowering_rule",
            "generated_side_effect_codegen_fixture",
            "deterministic_external_call_stub_policy_for_generated_targets",
            "bounded_state_capture_model_for_generated_targets",
            "generated_target_runtime_comparison_harness",
            "side_effect_reingest_policy_for_generated_targets",
        ],
        "inheritedOriginalStubbedRuntimeEvidence": {
            "phase": "P109",
            "comparisonCount": p109_payload["summary"]["comparisonCount"],
            "passCount": p109_payload["summary"]["passCount"],
            "maxAbsError": p109_payload["summary"]["maxAbsError"],
            "stubbedCallCount": p109_payload["summary"]["stubbedCallCount"],
            "boundedStateWriteCount": p109_payload["summary"]["boundedStateWriteCount"],
            "stubbedOriginalCSourceExecuted": p109_payload["summary"]["allStubbedOriginalCSourceExecuted"],
        },
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "liveExternalCallPerformed": False,
        "unboundedMemoryMutationPerformed": False,
        "supportClaimAllowed": False,
    }


def build_summary(p109_packet: dict[str, Any], p109_payload: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p109ValidationPass": p109_packet["validationStatus"] == "pass",
        "p109ClaimFlagsAllFalse": all(value is False for value in p109_packet["claimFlags"].values()),
        "selectedFixtureId": p109_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p109_payload["summary"]["selectedFixtureStillBlocked"],
        "p109ComparisonCount": p109_payload["summary"]["comparisonCount"],
        "p109PassCount": p109_payload["summary"]["passCount"],
        "p109MaxAbsError": p109_payload["summary"]["maxAbsError"],
        "p109StubbedCallCount": p109_payload["summary"]["stubbedCallCount"],
        "p109BoundedStateWriteCount": p109_payload["summary"]["boundedStateWriteCount"],
        "generatedTargetGateStatus": gate["status"],
        "generatedTargetGateBlocked": gate["status"] == "blocked_not_run",
        "requiredBeforeRunCount": len(gate["requiredBeforeRun"]),
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "liveExternalCallPerformed": False,
        "unboundedMemoryMutationPerformed": False,
        "sideEffectLoweringImplemented": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "sideEffectMemorySupportClaim": False,
        "sideEffectCodegenPolicyClaim": False,
        "sideEffectReingestPolicyClaim": False,
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
    p109_packet = read_json(P109_PACKET)
    p109_payload = read_json(P109_RESULT)
    p109.validate_payload(p109_payload)
    gate = generated_target_gate(p109_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p110-side-effect-generated-target-runtime-blocker",
        "decision": "side_effect_generated_target_runtime_gate_blocked",
        "sourcePacket": {
            "phase": "P109",
            "packetPath": str(P109_PACKET.relative_to(ROOT)),
            "resultPath": str(P109_RESULT.relative_to(ROOT)),
            "reviewDecision": p109_packet["reviewDecision"],
            "validationStatus": p109_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p109_payload["selectedFixture"]),
        "generatedTargetRuntimeGate": gate,
        "summary": build_summary(p109_packet, p109_payload, gate),
        "releaseGates": [
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "side_effect_lowering", "status": "blocked"},
            {"id": "generated_side_effect_codegen_policy", "status": "blocked"},
            {"id": "side_effect_reingest_policy", "status": "blocked"},
            {"id": "side_effect_memory_support", "status": "blocked"},
            {"id": "live_external_call_execution", "status": "not_performed"},
            {"id": "unbounded_memory_mutation", "status": "not_performed"},
            {"id": "side_effect_reingest_execution", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P110 records that generated-target runtime comparison is blocked until selected side-effect lowering and codegen policy exist.",
            "P109 original C stubbed-runtime evidence remains attached as prior evidence.",
            "P110 is a fail-closed gate, not generated target evidence.",
        ],
        "blockedStatements": [
            "Generated side-effect target code was executed.",
            "Re-ingested side-effect code was executed.",
            "Live external calls were performed.",
            "Unbounded memory mutation or aliasing was supported.",
            "Side-effect/call/memory lowering is implemented.",
            "Generated side-effect codegen policy is implemented.",
            "Side-effect re-ingest policy is implemented.",
            "Side-effecting calls or memory operations are generally supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Define a selected side-effect lowering/codegen proposal before generated-target runtime execution.",
            "Record private reviewer response to the P47-P110 branch/control-flow bundle.",
            "Keep generated target and re-ingest execution blocked until policy and fixture text exist.",
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
        "title": "FEF-P110 Side-Effect Generated Target Runtime Blocker",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "generated_target_runtime_blocked_until_side_effect_lowering_codegen_policy_exists",
        "semanticReview": payload["summary"],
        "claimBoundary": "Generated-target runtime blocker only; no generated target execution, re-ingest execution, live external call, unbounded memory mutation, side-effect lowering, codegen policy, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P110 keeps the generated-target runtime gate fail-closed.",
            "P109 original C stubbed-runtime evidence remains attached as prior evidence.",
            "Side-effect lowering/codegen/re-ingest policy remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p110_side_effect_generated_target_runtime_blocker.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p110_side_effect_generated_target_runtime_blocker.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p110_side_effect_generated_target_runtime_blocker.v0",
        "date": DATE,
        "title": "FEF-P110 Side-Effect Generated Target Runtime Blocker",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Define selected side-effect lowering/codegen policy before generated-target runtime execution.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    required = [f"- `{item}`" for item in payload["generatedTargetRuntimeGate"]["requiredBeforeRun"]]
    return "\n".join(
        [
            "# FEF-P110 Side-Effect Generated Target Runtime Blocker",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P110 records generated-target runtime as blocked until selected side-effect lowering/codegen policy exists.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- P109 comparisons: `{summary['p109ComparisonCount']}`",
            f"- P109 pass count: `{summary['p109PassCount']}`",
            f"- P109 max absolute error: `{summary['p109MaxAbsError']}`",
            f"- P109 stubbed call count: `{summary['p109StubbedCallCount']}`",
            f"- P109 bounded state write count: `{summary['p109BoundedStateWriteCount']}`",
            f"- Generated-target gate status: `{summary['generatedTargetGateStatus']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Side-effect lowering implemented: `{summary['sideEffectLoweringImplemented']}`",
            f"- Side-effect support claim: `{summary['sideEffectMemorySupportClaim']}`",
            "",
            "## Required Before Run",
            "",
            *required,
            "",
            "## Boundary",
            "",
            "- Generated-target runtime gate only; blocked and not run.",
            "- No generated target or re-ingested target execution.",
            "- No live external call or unbounded memory mutation.",
            "- No side-effect lowering, generated codegen policy, or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_gate(gate: dict[str, Any]) -> None:
    if gate["status"] != "blocked_not_run":
        raise ValueError("generated-target gate must remain blocked")
    if gate["blockedBy"] != "side_effect_lowering_and_codegen_policy_missing":
        raise ValueError("generated-target gate must be blocked by missing side-effect lowering/codegen policy")
    if len(gate["requiredBeforeRun"]) != 6:
        raise ValueError("expected six required-before-run items")
    for key in ["generatedTargetExecuted", "reingestedTargetExecuted", "liveExternalCallPerformed", "unboundedMemoryMutationPerformed", "supportClaimAllowed"]:
        if gate[key] is not False:
            raise ValueError(f"{key} must remain false")
    inherited = gate["inheritedOriginalStubbedRuntimeEvidence"]
    if inherited["comparisonCount"] != 7 or inherited["passCount"] != 7 or inherited["maxAbsError"] != 0.0:
        raise ValueError("unexpected inherited P109 evidence summary")
    if inherited["stubbedCallCount"] != 4 or inherited["boundedStateWriteCount"] != 4:
        raise ValueError("unexpected inherited P109 effect counts")
    if inherited["stubbedOriginalCSourceExecuted"] is not True:
        raise ValueError("P109 stubbed original C execution evidence should be inherited")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P110 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P110 status")
    p109.validate_payload(read_json(P109_RESULT))
    validate_gate(payload["generatedTargetRuntimeGate"])
    summary = payload["summary"]
    for key in [
        "p109ValidationPass",
        "p109ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "generatedTargetGateBlocked",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["requiredBeforeRunCount"] != 6:
        raise ValueError("expected six required-before-run items")
    if summary["p109ComparisonCount"] != 7 or summary["p109PassCount"] != 7:
        raise ValueError("unexpected inherited P109 comparison counts")
    if summary["p109MaxAbsError"] != 0.0:
        raise ValueError("unexpected inherited P109 max abs error")
    for key in [
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "liveExternalCallPerformed",
        "unboundedMemoryMutationPerformed",
        "sideEffectLoweringImplemented",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "sideEffectMemorySupportClaim",
        "sideEffectCodegenPolicyClaim",
        "sideEffectReingestPolicyClaim",
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
    result_path = out_dir / f"fef_p110_side_effect_generated_target_runtime_blocker_{STAMP}.json"
    report_path = report_dir / f"fef_p110_side_effect_generated_target_runtime_blocker_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p110_side_effect_generated_target_runtime_blocker.json"
    feed_path = command_feed_dir / f"fef_p110_side_effect_generated_target_runtime_blocker_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p110_side_effect_generated_target_runtime_blocker")
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
    print("FEF_P110_SIDE_EFFECT_GENERATED_TARGET_RUNTIME_BLOCKER_OK")
    print(f"status={built['payload']['summary']['generatedTargetGateStatus']}")
    print(f"required_before_run={built['payload']['summary']['requiredBeforeRunCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
