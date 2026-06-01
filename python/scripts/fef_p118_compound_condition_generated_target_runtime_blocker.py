#!/usr/bin/env python3
"""FEF-P118 generated-target runtime blocker for selected compound conditions."""

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

from scripts import fef_p117_compound_condition_original_c_runtime_gate as p117  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p118_compound_condition_generated_target_runtime_blocker.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P118_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_BLOCKER_PASS"

P117_PACKET = ROOT / "reports/evidence_packets/fef_p117_compound_condition_original_c_runtime_gate.json"
P117_RESULT = ROOT / "python/results/fef_p117_compound_condition_original_c_runtime_gate/fef_p117_compound_condition_original_c_runtime_gate_2026_06_01.json"

CLAIM_FLAGS = {
    "compound_condition_generated_target_runtime_blocker_claim": False,
    "selected_original_c_source_execution_recorded": False,
    "compound_condition_generated_target_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_lowering_implemented": False,
    "short_circuit_policy_implemented": False,
    "boolean_normalization_policy_implemented": False,
    "predicate_order_policy_implemented": False,
    "compound_condition_support_claim": False,
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
    "FEF-P118 records a generated-target runtime blocker for one selected compound-condition fixture only.",
    "FEF-P118 does not execute generated target code.",
    "FEF-P118 does not execute re-ingested code.",
    "FEF-P118 does not implement short-circuit, predicate-order, or boolean-normalization policy in Forge or eFrog.",
    "FEF-P118 does not implement compound-condition lowering.",
    "FEF-P118 does not define generated compound-condition codegen.",
    "FEF-P118 does not define compound-condition re-ingest policy.",
    "FEF-P118 does not widen Forge or eFrog frontend lowering.",
    "FEF-P118 does not claim compound-condition support.",
    "FEF-P118 does not record reviewer approval or rejection.",
    "FEF-P118 does not claim general branch/control-flow support.",
    "FEF-P118 does not claim branch/control-flow re-ingest support.",
    "FEF-P118 does not claim full non-generated source roundtrip.",
    "FEF-P118 does not claim arbitrary C/Rust source-family support.",
    "FEF-P118 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P118 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def generated_target_gate(p117_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "gateId": "compound_condition_generated_target_runtime_gate_v0",
        "selectedFixtureId": p117_payload["summary"]["selectedFixtureId"],
        "status": "blocked_not_run",
        "blockedBy": "compound_condition_lowering_codegen_and_reingest_policy_missing",
        "requiredBeforeRun": [
            "selected_compound_condition_lowering_rule",
            "generated_compound_condition_codegen_fixture",
            "generated_target_short_circuit_policy",
            "generated_target_runtime_comparison_harness",
            "compound_condition_reingest_policy_for_generated_targets",
        ],
        "inheritedOriginalRuntimeEvidence": {
            "phase": "P117",
            "comparisonCount": p117_payload["summary"]["comparisonCount"],
            "passCount": p117_payload["summary"]["passCount"],
            "maxAbsError": p117_payload["summary"]["maxAbsError"],
            "rightPredicateEvaluatedCount": p117_payload["summary"]["rightPredicateEvaluatedCount"],
            "shortCircuitCount": p117_payload["summary"]["shortCircuitCount"],
            "originalCSourceExecuted": p117_payload["summary"]["allOriginalCSourceExecuted"],
        },
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "shortCircuitPolicyImplemented": False,
        "booleanNormalizationPolicyImplemented": False,
        "predicateOrderPolicyImplemented": False,
        "supportClaimAllowed": False,
    }


def build_summary(p117_packet: dict[str, Any], p117_payload: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p117ValidationPass": p117_packet["validationStatus"] == "pass",
        "p117ClaimFlagsAllFalse": all(value is False for value in p117_packet["claimFlags"].values()),
        "selectedFixtureId": p117_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p117_payload["summary"]["selectedFixtureStillBlocked"],
        "p117ComparisonCount": p117_payload["summary"]["comparisonCount"],
        "p117PassCount": p117_payload["summary"]["passCount"],
        "p117MaxAbsError": p117_payload["summary"]["maxAbsError"],
        "p117RightPredicateEvaluatedCount": p117_payload["summary"]["rightPredicateEvaluatedCount"],
        "p117ShortCircuitCount": p117_payload["summary"]["shortCircuitCount"],
        "generatedTargetGateStatus": gate["status"],
        "generatedTargetGateBlocked": gate["status"] == "blocked_not_run",
        "requiredBeforeRunCount": len(gate["requiredBeforeRun"]),
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "compoundConditionGeneratedTargetExecutionClaim": False,
        "compoundConditionReingestExecutionClaim": False,
        "compoundConditionLoweringImplemented": False,
        "shortCircuitPolicyImplemented": False,
        "booleanNormalizationPolicyImplemented": False,
        "predicateOrderPolicyImplemented": False,
        "compoundConditionSupportClaim": False,
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
    p117_packet = read_json(P117_PACKET)
    p117_payload = read_json(P117_RESULT)
    p117.validate_payload(p117_payload)
    gate = generated_target_gate(p117_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p118-compound-condition-generated-target-runtime-blocker",
        "decision": "compound_condition_generated_target_runtime_gate_blocked",
        "sourcePacket": {
            "phase": "P117",
            "packetPath": str(P117_PACKET.relative_to(ROOT)),
            "resultPath": str(P117_RESULT.relative_to(ROOT)),
            "reviewDecision": p117_packet["reviewDecision"],
            "validationStatus": p117_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p117_payload["selectedFixture"]),
        "generatedTargetRuntimeGate": gate,
        "summary": build_summary(p117_packet, p117_payload, gate),
        "releaseGates": [
            {"id": "original_c_compound_condition_runtime_execution", "status": "recorded_by_p117"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "generated_compound_condition_codegen_policy", "status": "blocked"},
            {"id": "generated_target_short_circuit_policy", "status": "blocked"},
            {"id": "compound_condition_reingest_policy", "status": "blocked"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P118 records that generated-target runtime comparison is blocked until selected compound-condition lowering and codegen policy exist.",
            "P117 original C runtime evidence remains attached as prior evidence.",
            "P118 is a fail-closed gate, not generated target evidence.",
        ],
        "blockedStatements": [
            "Generated compound-condition target code was executed.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit, predicate-order, or boolean-normalization policy was implemented in Forge or eFrog.",
            "Generated compound-condition codegen policy is implemented.",
            "Compound-condition re-ingest policy is implemented.",
            "Compound-condition lowering is implemented.",
            "Compound-condition constructs are supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Define a selected compound-condition lowering/codegen proposal before generated-target runtime execution.",
            "Define generated-target short-circuit and re-ingest policy before executing generated targets.",
            "Record a real private reviewer response if one exists before installing any lowering.",
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
        "title": "FEF-P118 Compound-Condition Generated Target Runtime Blocker",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "generated_target_runtime_blocked_until_compound_condition_lowering_codegen_policy_exists",
        "semanticReview": payload["summary"],
        "claimBoundary": "Generated-target runtime blocker only; no generated target execution, re-ingest execution, compound-condition lowering, generated codegen policy, support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P118 keeps the generated-target runtime gate fail-closed.",
            "P117 original C runtime evidence remains attached as prior evidence.",
            "Compound-condition lowering/codegen/re-ingest policy remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p118_compound_condition_generated_target_runtime_blocker.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p118_compound_condition_generated_target_runtime_blocker.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p118_compound_condition_generated_target_runtime_blocker.v0",
        "date": DATE,
        "title": "FEF-P118 Compound-Condition Generated Target Runtime Blocker",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Define selected compound-condition lowering/codegen policy before generated-target runtime execution.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    required = [f"- `{item}`" for item in payload["generatedTargetRuntimeGate"]["requiredBeforeRun"]]
    return "\n".join(
        [
            "# FEF-P118 Compound-Condition Generated Target Runtime Blocker",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P118 records generated-target runtime as blocked until selected compound-condition lowering/codegen policy exists.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- P117 comparisons: `{summary['p117ComparisonCount']}`",
            f"- P117 pass count: `{summary['p117PassCount']}`",
            f"- P117 max absolute error: `{summary['p117MaxAbsError']}`",
            f"- P117 right-predicate-evaluated rows: `{summary['p117RightPredicateEvaluatedCount']}`",
            f"- P117 short-circuit rows: `{summary['p117ShortCircuitCount']}`",
            f"- Generated-target gate status: `{summary['generatedTargetGateStatus']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Compound-condition lowering implemented: `{summary['compoundConditionLoweringImplemented']}`",
            f"- Compound-condition support claim: `{summary['compoundConditionSupportClaim']}`",
            "",
            "## Required Before Run",
            "",
            *required,
            "",
            "## Boundary",
            "",
            "- Generated-target runtime gate only; blocked and not run.",
            "- No generated target or re-ingested target execution.",
            "- No compound-condition lowering, generated codegen policy, or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_gate(gate: dict[str, Any]) -> None:
    if gate["status"] != "blocked_not_run":
        raise ValueError("generated-target gate must remain blocked")
    if gate["blockedBy"] != "compound_condition_lowering_codegen_and_reingest_policy_missing":
        raise ValueError("generated-target gate must be blocked by missing compound-condition lowering/codegen/reingest policy")
    if len(gate["requiredBeforeRun"]) != 5:
        raise ValueError("expected five required-before-run items")
    for key in [
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "shortCircuitPolicyImplemented",
        "booleanNormalizationPolicyImplemented",
        "predicateOrderPolicyImplemented",
        "supportClaimAllowed",
    ]:
        if gate[key] is not False:
            raise ValueError(f"{key} must remain false")
    inherited = gate["inheritedOriginalRuntimeEvidence"]
    if inherited["comparisonCount"] != 7 or inherited["passCount"] != 7 or inherited["maxAbsError"] != 0.0:
        raise ValueError("unexpected inherited P117 evidence summary")
    if inherited["rightPredicateEvaluatedCount"] != 4 or inherited["shortCircuitCount"] != 3:
        raise ValueError("unexpected inherited P117 short-circuit counts")
    if inherited["originalCSourceExecuted"] is not True:
        raise ValueError("P117 original C execution evidence should be inherited")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P118 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P118 status")
    p117.validate_payload(read_json(P117_RESULT))
    validate_gate(payload["generatedTargetRuntimeGate"])
    summary = payload["summary"]
    for key in [
        "p117ValidationPass",
        "p117ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "generatedTargetGateBlocked",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["requiredBeforeRunCount"] != 5:
        raise ValueError("expected five required-before-run items")
    if summary["p117ComparisonCount"] != 7 or summary["p117PassCount"] != 7:
        raise ValueError("unexpected inherited P117 comparison counts")
    if summary["p117MaxAbsError"] != 0.0:
        raise ValueError("unexpected inherited P117 max abs error")
    if summary["p117RightPredicateEvaluatedCount"] != 4 or summary["p117ShortCircuitCount"] != 3:
        raise ValueError("unexpected inherited P117 short-circuit counts")
    for key in [
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "compoundConditionGeneratedTargetExecutionClaim",
        "compoundConditionReingestExecutionClaim",
        "compoundConditionLoweringImplemented",
        "shortCircuitPolicyImplemented",
        "booleanNormalizationPolicyImplemented",
        "predicateOrderPolicyImplemented",
        "compoundConditionSupportClaim",
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
    result_path = out_dir / f"fef_p118_compound_condition_generated_target_runtime_blocker_{STAMP}.json"
    report_path = report_dir / f"fef_p118_compound_condition_generated_target_runtime_blocker_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p118_compound_condition_generated_target_runtime_blocker.json"
    feed_path = command_feed_dir / f"fef_p118_compound_condition_generated_target_runtime_blocker_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p118_compound_condition_generated_target_runtime_blocker")
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
    print("FEF_P118_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_BLOCKER_OK")
    print(f"status={built['payload']['summary']['generatedTargetGateStatus']}")
    print(f"required_before_run={built['payload']['summary']['requiredBeforeRunCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
