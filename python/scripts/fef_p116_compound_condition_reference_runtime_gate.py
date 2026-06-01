#!/usr/bin/env python3
"""FEF-P116 reference-runtime gate for selected compound-condition samples."""

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

from scripts import fef_p115_compound_condition_policy_gate as p115  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p116_compound_condition_reference_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P116_COMPOUND_CONDITION_REFERENCE_RUNTIME_GATE_PASS"

P115_PACKET = ROOT / "reports/evidence_packets/fef_p115_compound_condition_policy_gate.json"
P115_RESULT = ROOT / "python/results/fef_p115_compound_condition_policy_gate/fef_p115_compound_condition_policy_gate_2026_06_01.json"

CLAIM_FLAGS = {
    "compound_condition_reference_runtime_gate_claim": False,
    "compound_condition_source_execution_claim": False,
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
    "FEF-P116 runs a local modeled Python reference evaluator for the P114 compound-condition expected-sample table only.",
    "FEF-P116 uses the P115 specified policy as a reference precondition only.",
    "FEF-P116 does not execute original C source.",
    "FEF-P116 does not execute generated target code.",
    "FEF-P116 does not execute re-ingested code.",
    "FEF-P116 does not implement short-circuit, predicate-order, or boolean-normalization policy in Forge or eFrog.",
    "FEF-P116 does not implement compound-condition lowering.",
    "FEF-P116 does not widen Forge or eFrog frontend lowering.",
    "FEF-P116 does not claim compound-condition support.",
    "FEF-P116 does not record reviewer approval or rejection.",
    "FEF-P116 does not claim general branch/control-flow support.",
    "FEF-P116 does not claim branch/control-flow re-ingest support.",
    "FEF-P116 does not claim full non-generated source roundtrip.",
    "FEF-P116 does not claim arbitrary C/Rust source-family support.",
    "FEF-P116 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P116 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def modeled_reference_runtime(sample: dict[str, Any]) -> dict[str, Any]:
    """Reference-only model of c_and_guard_return_v0 under P115 policy."""
    x = float(sample["inputs"]["x"])
    y = float(sample["inputs"]["y"])
    left_value = x > 0.0
    ordered_events = ["evaluate_left_predicate"]
    right_evaluated = left_value
    right_value = None
    observed = 0.0
    if right_evaluated:
        ordered_events.append("evaluate_right_predicate")
        right_value = y > 0.0
        if right_value:
            ordered_events.append("return_sum")
            observed = x + y
        else:
            ordered_events.append("return_zero")
    else:
        ordered_events.append("short_circuit_skip_right_predicate")
        ordered_events.append("return_zero")
    return {
        "observed": observed,
        "leftPredicateValue": left_value,
        "rightPredicateEvaluated": right_evaluated,
        "rightPredicateValue": right_value,
        "orderedEvents": ordered_events,
    }


def p115_with_source_payload() -> dict[str, Any]:
    payload = read_json(P115_RESULT)
    p115.validate_payload(payload)
    source = read_json(ROOT / payload["sourcePacket"]["resultPath"])
    payload = copy.deepcopy(payload)
    payload["sourcePacketPayload"] = source
    return payload


def comparison_rows(p115_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for sample in p115_payload["sourcePacketPayload"]["expectedSamples"]:
        runtime = modeled_reference_runtime(sample)
        observed = float(runtime["observed"])
        expected = float(sample["expected"])
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
                "leftPredicateValue": runtime["leftPredicateValue"],
                "rightPredicateEvaluated": runtime["rightPredicateEvaluated"],
                "rightPredicateValue": runtime["rightPredicateValue"],
                "orderedEvents": runtime["orderedEvents"],
                "referenceRuntimeOnly": True,
                "p115PolicyUsedAsPrecondition": True,
                "originalSourceExecuted": False,
                "generatedTargetExecuted": False,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p115_packet: dict[str, Any], p115_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p115ValidationPass": p115_packet["validationStatus"] == "pass",
        "p115ClaimFlagsAllFalse": all(value is False for value in p115_packet["claimFlags"].values()),
        "selectedFixtureId": p115_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p115_payload["summary"]["selectedFixtureStillBlocked"],
        "p115PolicyRuleCount": p115_payload["summary"]["policyRuleCount"],
        "p115EligibleForReferenceRuntimeNextGate": p115_payload["summary"]["eligibleForReferenceRuntimeNextGate"],
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "rightPredicateEvaluatedCount": sum(1 for row in rows if row["rightPredicateEvaluated"]),
        "shortCircuitCount": sum(1 for row in rows if not row["rightPredicateEvaluated"]),
        "maxAbsError": max(row["absError"] for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "allReferenceRuntimeOnly": all(row["referenceRuntimeOnly"] is True for row in rows),
        "allP115PolicyUsedAsPrecondition": all(row["p115PolicyUsedAsPrecondition"] is True for row in rows),
        "originalSourceExecuted": any(row["originalSourceExecuted"] for row in rows),
        "generatedTargetExecuted": any(row["generatedTargetExecuted"] for row in rows),
        "reingestedTargetExecuted": any(row["reingestedTargetExecuted"] for row in rows),
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
    p115_packet = read_json(P115_PACKET)
    p115_payload = p115_with_source_payload()
    rows = comparison_rows(p115_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p116-compound-condition-reference-runtime-gate",
        "decision": "compound_condition_reference_runtime_gate_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P115",
            "packetPath": str(P115_PACKET.relative_to(ROOT)),
            "resultPath": str(P115_RESULT.relative_to(ROOT)),
            "reviewDecision": p115_packet["reviewDecision"],
            "validationStatus": p115_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p115_payload["selectedFixture"]),
        "policyRules": copy.deepcopy(p115_payload["policyRules"]),
        "runtimeComparison": {
            "comparisonKind": "local_modeled_python_reference_runtime_against_compound_condition_expected_samples_under_p115_policy",
            "sourceLanguage": "python_reference_harness",
            "p115PolicyUsedAsPrecondition": True,
            "originalSourceExecuted": False,
            "generatedTargetExecuted": False,
            "reingestedTargetExecuted": False,
            "rows": rows,
        },
        "summary": build_summary(p115_packet, p115_payload, rows),
        "releaseGates": [
            {"id": "compound_condition_reference_runtime_gate", "status": "recorded"},
            {"id": "original_c_compound_condition_runtime_execution", "status": "not_performed"},
            {"id": "generated_target_runtime_execution", "status": "not_performed"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "short_circuit_policy", "status": "used_as_reference_precondition_not_implemented"},
            {"id": "predicate_truth_policy", "status": "used_as_reference_precondition_not_implemented"},
            {"id": "boolean_normalization_policy", "status": "used_as_reference_precondition_not_implemented"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P116 runs a local modeled Python reference evaluator over the P114 sample table under the P115 policy.",
            "All seven selected comparisons pass with zero absolute error.",
            "P116 is reference-table consistency evidence only; it is not original-source, generated-target, or re-ingest evidence.",
        ],
        "blockedStatements": [
            "The original C compound-condition source was executed.",
            "Generated compound-condition target code was executed.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit, predicate-order, or boolean-normalization policy was implemented in Forge or eFrog.",
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
            "Compile and run the selected original C fixture only if source execution remains isolated from generated target and re-ingest claims.",
            "Keep generated target execution and re-ingest blocked until compound-condition lowering policy exists.",
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
        "title": "FEF-P116 Compound-Condition Reference Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "compound_condition_reference_runtime_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Modeled reference-runtime gate only; no original-source execution, generated-target execution, re-ingest execution, implemented short-circuit policy, implemented boolean-normalization policy, compound-condition lowering, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P116 evaluates seven P114 samples under the P115 policy.",
            "All seven modeled reference comparisons pass with zero absolute error.",
            "Source/generated/re-ingest execution remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p116_compound_condition_reference_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p116_compound_condition_reference_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p116_compound_condition_reference_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P116 Compound-Condition Reference Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Compile and run the selected original C fixture only if source execution remains isolated from generated target and re-ingest claims.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Path | Expected | Observed | Right Evaluated | Pass |", "|---|---|---:|---:|---|---|"]
    for row in payload["runtimeComparison"]["rows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['path']}` | `{row['expected']}` | `{row['observed']}` | `{row['rightPredicateEvaluated']}` | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P116 Compound-Condition Reference Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P116 runs a modeled local reference evaluator for selected compound-condition samples.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Comparison count: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Right predicate evaluated rows: `{summary['rightPredicateEvaluatedCount']}`",
            f"- Short-circuit rows: `{summary['shortCircuitCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Reference runtime only: `{summary['allReferenceRuntimeOnly']}`",
            f"- Original source executed: `{summary['originalSourceExecuted']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Compound-condition support claim: `{summary['compoundConditionSupportClaim']}`",
            "",
            "## Comparisons",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Reference-runtime table consistency only.",
            "- No original C compound-condition source execution.",
            "- No generated target or re-ingested target execution.",
            "- No applied short-circuit or boolean-normalization policy.",
            "- No compound-condition lowering or support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_row(row: dict[str, Any]) -> None:
    runtime = modeled_reference_runtime(row)
    if row["observed"] != runtime["observed"]:
        raise ValueError("observed value does not match reference runtime")
    if row["expected"] != runtime["observed"]:
        raise ValueError("expected value does not match reference runtime")
    if row["rightPredicateEvaluated"] != runtime["rightPredicateEvaluated"]:
        raise ValueError("right predicate evaluation does not match reference runtime")
    if row["rightPredicateValue"] != runtime["rightPredicateValue"]:
        raise ValueError("right predicate value does not match reference runtime")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("reference runtime comparison must pass exactly")
    if row["referenceRuntimeOnly"] is not True:
        raise ValueError("row must remain reference-runtime-only")
    for key in ["originalSourceExecuted", "generatedTargetExecuted", "reingestedTargetExecuted"]:
        if row[key] is not False:
            raise ValueError(f"{key} must be false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P116 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P116 status")
    p115.validate_payload(read_json(P115_RESULT))
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p115ValidationPass",
        "p115ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "p115EligibleForReferenceRuntimeNextGate",
        "allObservedFinite",
        "allReferenceRuntimeOnly",
        "allP115PolicyUsedAsPrecondition",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["comparisonCount"] != 7 or summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("unexpected comparison counts")
    if summary["rightPredicateEvaluatedCount"] != 4 or summary["shortCircuitCount"] != 3:
        raise ValueError("unexpected short-circuit counts")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("maxAbsError must be zero")
    for key in [
        "originalSourceExecuted",
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
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
    result_path = out_dir / f"fef_p116_compound_condition_reference_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p116_compound_condition_reference_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p116_compound_condition_reference_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p116_compound_condition_reference_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p116_compound_condition_reference_runtime_gate")
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
    print("FEF_P116_COMPOUND_CONDITION_REFERENCE_RUNTIME_GATE_OK")
    print(f"comparisons={built['payload']['summary']['comparisonCount']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
