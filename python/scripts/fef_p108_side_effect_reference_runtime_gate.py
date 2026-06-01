#!/usr/bin/env python3
"""FEF-P108 reference-runtime gate for selected side-effect samples."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p107_side_effect_policy_gate as p107  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p108_side_effect_reference_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P108_SIDE_EFFECT_REFERENCE_RUNTIME_GATE_PASS"

P107_PACKET = ROOT / "reports/evidence_packets/fef_p107_side_effect_policy_gate.json"
P107_RESULT = ROOT / "python/results/fef_p107_side_effect_policy_gate/fef_p107_side_effect_policy_gate_2026_06_01.json"

CLAIM_FLAGS = {
    "side_effect_reference_runtime_gate_claim": False,
    "live_external_call_claim": False,
    "real_memory_mutation_claim": False,
    "original_source_execution_claim": False,
    "generated_target_execution_claim": False,
    "reingest_execution_claim": False,
    "side_effect_runtime_execution_claim": False,
    "side_effect_lowering_implemented": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
    "side_effect_memory_support_claim": False,
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
    "FEF-P108 runs a local modeled Python reference evaluator for the P106 side-effect expected-sample table only.",
    "FEF-P108 uses deterministic fixture-supplied external-call return values under the P107 policy.",
    "FEF-P108 does not perform live external calls.",
    "FEF-P108 does not mutate real runtime memory or global state.",
    "FEF-P108 does not execute original C source.",
    "FEF-P108 does not execute generated target code.",
    "FEF-P108 does not execute re-ingested code.",
    "FEF-P108 does not implement effect ordering, external-call, aliasing, or memory-state policy in Forge or eFrog.",
    "FEF-P108 does not implement side-effect/call/memory lowering.",
    "FEF-P108 does not widen Forge or eFrog frontend lowering.",
    "FEF-P108 does not claim side-effect/call/memory support.",
    "FEF-P108 does not claim loop/back-edge, assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P108 does not record reviewer approval or rejection.",
    "FEF-P108 does not claim general branch/control-flow support.",
    "FEF-P108 does not claim branch/control-flow re-ingest support.",
    "FEF-P108 does not claim full non-generated source roundtrip.",
    "FEF-P108 does not claim arbitrary C/Rust source-family support.",
    "FEF-P108 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P108 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def modeled_reference_runtime(sample: dict[str, Any]) -> dict[str, Any]:
    """Reference-only model of c_global_state_update_v0 under P107 policy."""
    x = float(sample["inputs"]["x"])
    initial_state = float(sample["inputs"]["initialState"])
    guard_true = x > 0.0
    ordered_events = ["evaluate_guard"]
    final_state = initial_state
    modeled_call_return = sample["inputs"]["externalCallReturn"]
    if guard_true:
        ordered_events.append("perform_modeled_call_if_guard_true")
        final_state = float(modeled_call_return)
        ordered_events.append("write_modeled_state_if_call_occurs")
    ordered_events.append("return_final_state")
    return {
        "observed": final_state,
        "finalState": final_state,
        "guardTrue": guard_true,
        "modeledCallExpected": guard_true,
        "modeledStateWriteExpected": guard_true,
        "modeledCallReturn": modeled_call_return if guard_true else None,
        "orderedEvents": ordered_events,
        "liveExternalCallPerformed": False,
        "realMemoryMutationPerformed": False,
    }


def comparison_rows(p107_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for sample in p107_payload["sourcePacketPayload"]["expectedSamples"]:
        runtime = modeled_reference_runtime(sample)
        observed = float(runtime["observed"])
        expected = float(sample["expectedReturn"])
        abs_error = abs(observed - expected)
        rows.append(
            {
                "sampleId": sample["sampleId"],
                "inputs": copy.deepcopy(sample["inputs"]),
                "path": sample["path"],
                "expected": expected,
                "observed": observed,
                "absError": abs_error,
                "pass": math.isfinite(observed) and abs_error == 0.0,
                "guardTrue": runtime["guardTrue"],
                "modeledCallExpected": runtime["modeledCallExpected"],
                "modeledStateWriteExpected": runtime["modeledStateWriteExpected"],
                "modeledCallReturn": runtime["modeledCallReturn"],
                "orderedEvents": runtime["orderedEvents"],
                "referenceRuntimeOnly": True,
                "p107PolicyUsedAsPrecondition": True,
                "liveExternalCallPerformed": runtime["liveExternalCallPerformed"],
                "realMemoryMutationPerformed": runtime["realMemoryMutationPerformed"],
                "originalSourceExecuted": False,
                "generatedTargetExecuted": False,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def p107_with_source_payload() -> dict[str, Any]:
    payload = read_json(P107_RESULT)
    p107.validate_payload(payload)
    source = read_json(ROOT / payload["sourcePacket"]["resultPath"])
    payload = copy.deepcopy(payload)
    payload["sourcePacketPayload"] = source
    return payload


def build_summary(p107_packet: dict[str, Any], p107_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p107ValidationPass": p107_packet["validationStatus"] == "pass",
        "p107ClaimFlagsAllFalse": all(value is False for value in p107_packet["claimFlags"].values()),
        "selectedFixtureId": p107_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p107_payload["summary"]["selectedFixtureStillBlocked"],
        "p107PolicyRuleCount": p107_payload["summary"]["policyRuleCount"],
        "p107EligibleForReferenceRuntimeNextGate": p107_payload["summary"]["eligibleForReferenceRuntimeNextGate"],
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "guardTrueCount": sum(1 for row in rows if row["guardTrue"]),
        "guardFalseCount": sum(1 for row in rows if not row["guardTrue"]),
        "modeledCallCount": sum(1 for row in rows if row["modeledCallExpected"]),
        "modeledStateWriteCount": sum(1 for row in rows if row["modeledStateWriteExpected"]),
        "maxAbsError": max(row["absError"] for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "allReferenceRuntimeOnly": all(row["referenceRuntimeOnly"] is True for row in rows),
        "allP107PolicyUsedAsPrecondition": all(row["p107PolicyUsedAsPrecondition"] is True for row in rows),
        "liveExternalCallPerformed": any(row["liveExternalCallPerformed"] for row in rows),
        "realMemoryMutationPerformed": any(row["realMemoryMutationPerformed"] for row in rows),
        "originalSourceExecuted": any(row["originalSourceExecuted"] for row in rows),
        "generatedTargetExecuted": any(row["generatedTargetExecuted"] for row in rows),
        "reingestedTargetExecuted": any(row["reingestedTargetExecuted"] for row in rows),
        "sideEffectLoweringImplemented": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "sideEffectMemorySupportClaim": False,
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
    p107_packet = read_json(P107_PACKET)
    p107_payload = p107_with_source_payload()
    rows = comparison_rows(p107_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p108-side-effect-reference-runtime-gate",
        "decision": "side_effect_reference_runtime_gate_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P107",
            "packetPath": str(P107_PACKET.relative_to(ROOT)),
            "resultPath": str(P107_RESULT.relative_to(ROOT)),
            "reviewDecision": p107_packet["reviewDecision"],
            "validationStatus": p107_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p107_payload["selectedFixture"]),
        "policyRules": copy.deepcopy(p107_payload["policyRules"]),
        "runtimeComparison": {
            "comparisonKind": "local_modeled_python_reference_runtime_against_side_effect_expected_samples_under_p107_policy",
            "sourceLanguage": "python_reference_harness",
            "p107PolicyUsedAsPrecondition": True,
            "liveExternalCallPerformed": False,
            "realMemoryMutationPerformed": False,
            "originalSourceExecuted": False,
            "generatedTargetExecuted": False,
            "reingestedTargetExecuted": False,
            "rows": rows,
        },
        "summary": build_summary(p107_packet, p107_payload, rows),
        "releaseGates": [
            {"id": "side_effect_reference_runtime_gate", "status": "recorded"},
            {"id": "live_external_call_execution", "status": "not_performed"},
            {"id": "real_memory_mutation", "status": "not_performed"},
            {"id": "original_source_runtime_execution", "status": "not_performed"},
            {"id": "generated_target_runtime_execution", "status": "not_performed"},
            {"id": "side_effect_reingest_execution", "status": "not_performed"},
            {"id": "effect_order_policy", "status": "used_as_reference_precondition_not_implemented"},
            {"id": "external_call_policy", "status": "used_as_reference_precondition_not_implemented"},
            {"id": "memory_alias_policy", "status": "used_as_reference_precondition_not_implemented"},
            {"id": "side_effect_lowering", "status": "blocked"},
            {"id": "side_effect_memory_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P108 runs a local modeled Python reference evaluator over the P106 sample table under the P107 policy.",
            "All seven selected comparisons pass with zero absolute error.",
            "P108 is reference-table consistency evidence only; it is not live external-call, real memory-mutation, original-source, generated-target, or re-ingest evidence.",
        ],
        "blockedStatements": [
            "A live external call was performed.",
            "Runtime memory or global state was mutated.",
            "The original C side-effect source was executed.",
            "Generated side-effect target code was executed.",
            "Re-ingested side-effect code was executed.",
            "Effect-order, external-call, or memory-alias policy was implemented in Forge or eFrog.",
            "Side-effect/call/memory lowering is implemented.",
            "Side-effecting calls or memory operations are supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Compile and run the selected original C fixture only if the external call is replaced by a deterministic local stub and state capture remains bounded.",
            "Keep generated target execution and re-ingest blocked until side-effect lowering policy exists.",
            "Record a real private reviewer response if one exists before installing any adapter or lowering.",
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
        "title": "FEF-P108 Side-Effect Reference Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "side_effect_reference_runtime_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Modeled reference-runtime gate only; no live external call, real memory mutation, original-source execution, generated-target execution, re-ingest execution, side-effect lowering, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P108 evaluates seven P106 samples under the P107 policy.",
            "All seven modeled reference comparisons pass with zero absolute error.",
            "Live side effects remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p108_side_effect_reference_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p108_side_effect_reference_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p108_side_effect_reference_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P108 Side-Effect Reference Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Compile and run the selected original C fixture only with deterministic local external-call stubbing and bounded state capture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Path | Expected | Observed | Pass |", "|---|---|---:|---:|---|"]
    for row in payload["runtimeComparison"]["rows"]:
        rows.append(f"| `{row['sampleId']}` | `{row['path']}` | `{row['expected']}` | `{row['observed']}` | `{row['pass']}` |")
    return "\n".join(
        [
            "# FEF-P108 Side-Effect Reference Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P108 runs a modeled local reference evaluator for selected side-effect samples.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Comparison count: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Guard true count: `{summary['guardTrueCount']}`",
            f"- Guard false count: `{summary['guardFalseCount']}`",
            f"- Modeled call count: `{summary['modeledCallCount']}`",
            f"- Modeled state write count: `{summary['modeledStateWriteCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Live external call performed: `{summary['liveExternalCallPerformed']}`",
            f"- Real memory mutation performed: `{summary['realMemoryMutationPerformed']}`",
            f"- Original source executed: `{summary['originalSourceExecuted']}`",
            "",
            "## Comparisons",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Modeled reference runtime only.",
            "- No live external calls performed.",
            "- No real runtime memory writes or global-state mutation.",
            "- No original-source, generated-target, or re-ingested execution.",
            "- No side-effect/call/memory support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P108 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P108 status")
    p107.validate_payload(read_json(P107_RESULT))
    summary = payload["summary"]
    for key in [
        "p107ValidationPass",
        "p107ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "p107EligibleForReferenceRuntimeNextGate",
        "allObservedFinite",
        "allReferenceRuntimeOnly",
        "allP107PolicyUsedAsPrecondition",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["comparisonCount"] != 7:
        raise ValueError("expected seven comparisons")
    if summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("expected seven passing comparisons")
    if summary["guardTrueCount"] != 4 or summary["guardFalseCount"] != 3:
        raise ValueError("unexpected guard distribution")
    if summary["modeledCallCount"] != 4 or summary["modeledStateWriteCount"] != 4:
        raise ValueError("unexpected modeled effect distribution")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("expected zero max abs error")
    for key in [
        "liveExternalCallPerformed",
        "realMemoryMutationPerformed",
        "originalSourceExecuted",
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "sideEffectLoweringImplemented",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "sideEffectMemorySupportClaim",
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
    result_path = out_dir / f"fef_p108_side_effect_reference_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p108_side_effect_reference_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p108_side_effect_reference_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p108_side_effect_reference_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p108_side_effect_reference_runtime_gate")
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
    print("FEF_P108_SIDE_EFFECT_REFERENCE_RUNTIME_GATE_OK")
    print(f"comparisons={built['payload']['summary']['comparisonCount']}")
    print(f"pass={built['payload']['summary']['passCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
