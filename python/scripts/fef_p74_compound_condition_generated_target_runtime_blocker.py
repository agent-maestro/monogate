#!/usr/bin/env python3
"""FEF-P74 generated-target runtime blocker for compound conditions."""

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

from scripts import fef_p73_compound_condition_original_c_runtime_gate as p73

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p74_compound_condition_generated_target_runtime_blocker.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P74_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_BLOCKER_PASS"

P73_PACKET = ROOT / "reports/evidence_packets/fef_p73_compound_condition_original_c_runtime_gate.json"
P73_RESULT = ROOT / "python/results/fef_p73_compound_condition_original_c_runtime_gate/fef_p73_compound_condition_original_c_runtime_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_generated_target_runtime_blocker_claim": False,
    "compound_condition_generated_target_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_lowering_claim": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
    "selected_original_c_compound_condition_source_execution_recorded": False,
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
    "FEF-P74 records a generated-target runtime blocker for the selected compound-condition fixture only.",
    "FEF-P74 does not execute generated target code.",
    "FEF-P74 does not execute re-ingested code.",
    "FEF-P74 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P74 does not implement compound-condition lowering.",
    "FEF-P74 does not widen Forge or eFrog frontend lowering.",
    "FEF-P74 does not claim compound-condition support.",
    "FEF-P74 does not claim assignment/phi or nested branch support.",
    "FEF-P74 does not claim general branch/control-flow support.",
    "FEF-P74 does not claim branch/control-flow re-ingest support.",
    "FEF-P74 does not claim full non-generated source roundtrip.",
    "FEF-P74 does not claim arbitrary C/Rust source-family support.",
    "FEF-P74 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P74 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def generated_target_gate(p73_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "gateId": "compound_condition_generated_target_runtime_gate_v0",
        "selectedFixtureId": p73_payload["summary"]["selectedFixtureId"],
        "status": "blocked_not_run",
        "blockedBy": "compound_condition_lowering_missing",
        "requiredBeforeRun": [
            "compound_condition_lowering_rule",
            "short_circuit_truth_semantics",
            "generated_target_fixture",
            "runtime_comparison_harness",
            "reingest_policy_for_generated_compound_condition",
        ],
        "inheritedOriginalRuntimeEvidence": {
            "phase": "P73",
            "comparisonCount": p73_payload["summary"]["comparisonCount"],
            "passCount": p73_payload["summary"]["passCount"],
            "maxAbsError": p73_payload["summary"]["maxAbsError"],
            "originalCSourceExecuted": p73_payload["summary"]["allOriginalCSourceExecuted"],
        },
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "supportClaimAllowed": False,
    }


def build_summary(p73_packet: dict[str, Any], p73_payload: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p73ValidationPass": p73_packet["validationStatus"] == "pass",
        "p73ClaimFlagsAllFalse": all(value is False for value in p73_packet["claimFlags"].values()),
        "selectedFixtureId": p73_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p73_payload["summary"]["selectedFixtureStillBlocked"],
        "p73OriginalRuntimeComparisons": p73_payload["summary"]["comparisonCount"],
        "p73OriginalRuntimePassCount": p73_payload["summary"]["passCount"],
        "p73OriginalRuntimeMaxAbsError": p73_payload["summary"]["maxAbsError"],
        "generatedTargetGateStatus": gate["status"],
        "generatedTargetGateBlocked": gate["status"] == "blocked_not_run",
        "requiredBeforeRunCount": len(gate["requiredBeforeRun"]),
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "compoundConditionGeneratedTargetExecutionClaim": False,
        "compoundConditionReingestExecutionClaim": False,
        "compoundConditionLoweringClaim": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
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
    p73_packet = read_json(P73_PACKET)
    p73_payload = read_json(P73_RESULT)
    p73.validate_payload(p73_payload)
    gate = generated_target_gate(p73_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p74-compound-condition-generated-target-runtime-blocker",
        "decision": "compound_condition_generated_target_runtime_gate_blocked",
        "sourcePacket": {
            "phase": "P73",
            "packetPath": str(P73_PACKET.relative_to(ROOT)),
            "resultPath": str(P73_RESULT.relative_to(ROOT)),
            "reviewDecision": p73_packet["reviewDecision"],
            "validationStatus": p73_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p73_payload["selectedFixture"]),
        "generatedTargetRuntimeGate": gate,
        "summary": build_summary(p73_packet, p73_payload, gate),
        "releaseGates": [
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "short_circuit_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P74 records that generated-target runtime comparison is blocked until compound-condition lowering exists.",
            "P73 original C runtime evidence remains attached as prior evidence.",
            "P74 is a fail-closed gate, not generated target evidence.",
        ],
        "blockedStatements": [
            "Generated compound-condition target code was executed.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit condition semantics are implemented in Forge or eFrog.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Implement a selected compound-condition lowering rule before any generated-target runtime execution.",
            "Record private reviewer response to the P47-P74 branch/control-flow bundle.",
            "Move to another unsupported P59/P60 form with the same fixture/sample/reference/original-source ladder.",
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
        "title": "FEF-P74 Compound-Condition Generated Target Runtime Blocker",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "generated_target_runtime_blocked_until_lowering_exists",
        "semanticReview": payload["summary"],
        "claimBoundary": "Generated-target runtime blocker only; no generated target execution, re-ingest execution, compound-condition lowering, compound-condition support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P74 keeps the generated-target runtime gate fail-closed.",
            "P73 original C runtime evidence remains attached as prior evidence.",
            "Compound-condition lowering/support claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p74_compound_condition_generated_target_runtime_blocker.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p74_compound_condition_generated_target_runtime_blocker.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p74_compound_condition_generated_target_runtime_blocker.v0",
        "date": DATE,
        "title": "FEF-P74 Compound-Condition Generated Target Runtime Blocker",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Implement selected compound-condition lowering before generated-target runtime execution.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    required = [f"- `{item}`" for item in payload["generatedTargetRuntimeGate"]["requiredBeforeRun"]]
    return "\n".join(
        [
            "# FEF-P74 Compound-Condition Generated Target Runtime Blocker",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P74 records the generated-target runtime gate as blocked until compound-condition lowering exists.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- P73 original runtime comparisons: `{summary['p73OriginalRuntimeComparisons']}`",
            f"- P73 original runtime pass count: `{summary['p73OriginalRuntimePassCount']}`",
            f"- P73 max absolute error: `{summary['p73OriginalRuntimeMaxAbsError']}`",
            f"- Generated-target gate status: `{summary['generatedTargetGateStatus']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Compound-condition lowering claim: `{summary['compoundConditionLoweringClaim']}`",
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
            "- No short-circuit implementation, compound-condition lowering, or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_gate(gate: dict[str, Any]) -> None:
    if gate["status"] != "blocked_not_run":
        raise ValueError("generated-target gate must remain blocked")
    if gate["blockedBy"] != "compound_condition_lowering_missing":
        raise ValueError("generated-target gate must be blocked by missing compound-condition lowering")
    if len(gate["requiredBeforeRun"]) != 5:
        raise ValueError("expected five required-before-run items")
    if gate["generatedTargetExecuted"] is not False or gate["reingestedTargetExecuted"] is not False:
        raise ValueError("generated and re-ingested execution must remain false")
    if gate["supportClaimAllowed"] is not False:
        raise ValueError("support claim must remain false")
    inherited = gate["inheritedOriginalRuntimeEvidence"]
    if inherited["comparisonCount"] != 7 or inherited["passCount"] != 7 or inherited["maxAbsError"] != 0.0:
        raise ValueError("unexpected inherited P73 evidence summary")
    if inherited["originalCSourceExecuted"] is not True:
        raise ValueError("P73 original C execution evidence should be inherited")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P74 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P74 status")
    p73.validate_payload(read_json(P73_RESULT))
    validate_gate(payload["generatedTargetRuntimeGate"])
    summary = payload["summary"]
    for key in [
        "p73ValidationPass",
        "p73ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "generatedTargetGateBlocked",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedFixtureId"] != "c_and_short_circuit_guard_v0":
        raise ValueError("unexpected selected fixture")
    if summary["p73OriginalRuntimeComparisons"] != 7 or summary["p73OriginalRuntimePassCount"] != 7:
        raise ValueError("unexpected inherited P73 comparison counts")
    if summary["p73OriginalRuntimeMaxAbsError"] != 0.0:
        raise ValueError("unexpected inherited P73 max error")
    if summary["requiredBeforeRunCount"] != 5:
        raise ValueError("unexpected required-before-run count")
    for key in [
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "compoundConditionGeneratedTargetExecutionClaim",
        "compoundConditionReingestExecutionClaim",
        "compoundConditionLoweringClaim",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
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
    result_path = out_dir / f"fef_p74_compound_condition_generated_target_runtime_blocker_{STAMP}.json"
    report_path = report_dir / f"fef_p74_compound_condition_generated_target_runtime_blocker_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p74_compound_condition_generated_target_runtime_blocker.json"
    feed_path = command_feed_dir / f"fef_p74_compound_condition_generated_target_runtime_blocker_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p74_compound_condition_generated_target_runtime_blocker")
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
    print("FEF_P74_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_BLOCKER_OK")
    print(f"gate_status={built['payload']['summary']['generatedTargetGateStatus']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
