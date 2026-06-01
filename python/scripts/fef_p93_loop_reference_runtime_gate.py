#!/usr/bin/env python3
"""FEF-P93 reference-runtime gate for selected loop/back-edge samples."""

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

from scripts import fef_p92_loop_boundedness_policy as p92  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p93_loop_reference_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P93_LOOP_REFERENCE_RUNTIME_GATE_PASS"

P92_PACKET = ROOT / "reports/evidence_packets/fef_p92_loop_boundedness_policy.json"
P92_RESULT = ROOT / "python/results/fef_p92_loop_boundedness_policy/fef_p92_loop_boundedness_policy_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_reference_runtime_gate_claim": False,
    "loop_original_source_execution_claim": False,
    "loop_generated_target_execution_claim": False,
    "loop_reingest_execution_claim": False,
    "loop_lowering_claim": False,
    "loop_backedge_support_claim": False,
    "loop_boundedness_policy_general_claim": False,
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
    "FEF-P93 executes a local Python reference evaluator for the P91 loop expected-sample table only.",
    "FEF-P93 applies the P92 policy only as a precondition for the local reference evaluator.",
    "FEF-P93 does not execute original C loop source.",
    "FEF-P93 does not execute generated target code.",
    "FEF-P93 does not execute re-ingested code.",
    "FEF-P93 does not implement loop headers, latches, variants, or general boundedness policy.",
    "FEF-P93 does not implement loop lowering.",
    "FEF-P93 does not widen Forge or eFrog frontend lowering.",
    "FEF-P93 does not claim loop/back-edge support.",
    "FEF-P93 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P93 does not record reviewer approval or rejection.",
    "FEF-P93 does not approve or apply the P88 implementation proposal.",
    "FEF-P93 does not claim general branch/control-flow support.",
    "FEF-P93 does not claim branch/control-flow re-ingest support.",
    "FEF-P93 does not claim full non-generated source roundtrip.",
    "FEF-P93 does not claim arbitrary C/Rust source-family support.",
    "FEF-P93 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P93 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reference_runtime(x: float, n: int) -> dict[str, Any]:
    """Reference-only mirror of c_while_accumulate_v0 source semantics."""
    acc = 0.0
    i = 0
    effective_iterations = 0
    while i < n:
        acc = acc + x
        i = i + 1
        effective_iterations += 1
    return {
        "observed": acc,
        "finalI": i,
        "iterationCount": effective_iterations,
        "backEdgeTakenCount": effective_iterations,
        "loopConditionInitiallyTrue": n > 0,
    }


def comparison_rows(p92_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for policy_row in p92_payload["samplePolicyRows"]:
        x = float(policy_row["inputX"])
        n = int(policy_row["inputN"])
        runtime = reference_runtime(x, n)
        observed = float(runtime["observed"])
        expected = float(policy_row["expected"])
        abs_error = abs(observed - expected)
        eligible = policy_row["policyEligibleForFutureExecution"]
        rows.append(
            {
                "sampleId": policy_row["sampleId"],
                "inputs": {"x": x, "n": n},
                "expected": expected,
                "observed": observed,
                "absError": abs_error,
                "pass": eligible and math.isfinite(observed) and abs_error == 0.0,
                "path": "zero_iterations" if runtime["iterationCount"] == 0 else "single_iteration" if runtime["iterationCount"] == 1 else "multi_iteration",
                "policyEligibleForExecution": eligible,
                "policyEffectiveIterationCount": policy_row["effectiveIterationCount"],
                "iterationCount": runtime["iterationCount"],
                "backEdgeTakenCount": runtime["backEdgeTakenCount"],
                "loopConditionInitiallyTrue": runtime["loopConditionInitiallyTrue"],
                "referenceRuntimeOnly": True,
                "originalSourceExecuted": False,
                "generatedTargetExecuted": False,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p92_packet: dict[str, Any], p92_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p92ValidationPass": p92_packet["validationStatus"] == "pass",
        "p92ClaimFlagsAllFalse": all(value is False for value in p92_packet["claimFlags"].values()),
        "selectedFixtureId": p92_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p92_payload["summary"]["selectedFixtureStillBlocked"],
        "p92PolicyId": p92_payload["summary"]["policyId"],
        "p92PolicyStatus": p92_payload["summary"]["policyStatus"],
        "p92EligibleSampleCount": p92_payload["summary"]["eligibleSampleCount"],
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "zeroIterationCount": sum(1 for row in rows if row["iterationCount"] == 0),
        "singleIterationCount": sum(1 for row in rows if row["iterationCount"] == 1),
        "multiIterationCount": sum(1 for row in rows if row["iterationCount"] > 1),
        "maxIterationCount": max(row["iterationCount"] for row in rows),
        "totalBackEdgeTakenCount": sum(row["backEdgeTakenCount"] for row in rows),
        "maxAbsError": max(row["absError"] for row in rows),
        "allPolicyEligible": all(row["policyEligibleForExecution"] is True for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "allReferenceRuntimeOnly": all(row["referenceRuntimeOnly"] is True for row in rows),
        "originalSourceExecuted": any(row["originalSourceExecuted"] for row in rows),
        "generatedTargetExecuted": any(row["generatedTargetExecuted"] for row in rows),
        "reingestedTargetExecuted": any(row["reingestedTargetExecuted"] for row in rows),
        "loopOriginalSourceExecutionClaim": False,
        "loopGeneratedTargetExecutionClaim": False,
        "loopReingestExecutionClaim": False,
        "loopLoweringClaim": False,
        "loopBackedgeSupportClaim": False,
        "loopBoundednessPolicyGeneralClaim": False,
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
    p92_packet = read_json(P92_PACKET)
    p92_payload = read_json(P92_RESULT)
    p92.validate_payload(p92_payload)
    rows = comparison_rows(p92_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p93-loop-reference-runtime-gate",
        "decision": "loop_reference_runtime_gate_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P92",
            "packetPath": str(P92_PACKET.relative_to(ROOT)),
            "resultPath": str(P92_RESULT.relative_to(ROOT)),
            "reviewDecision": p92_packet["reviewDecision"],
            "validationStatus": p92_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p92_payload["selectedFixture"]),
        "boundednessPolicy": copy.deepcopy(p92_payload["boundednessPolicy"]),
        "runtimeComparison": {
            "comparisonKind": "local_python_reference_runtime_against_loop_expected_samples_under_p92_policy",
            "sourceLanguage": "python_reference_harness",
            "policyAppliedAsPrecondition": True,
            "originalSourceExecuted": False,
            "generatedTargetExecuted": False,
            "reingestedTargetExecuted": False,
            "rows": rows,
        },
        "summary": build_summary(p92_packet, p92_payload, rows),
        "releaseGates": [
            {"id": "loop_reference_runtime_gate", "status": "recorded"},
            {"id": "original_c_loop_runtime_execution", "status": "not_performed"},
            {"id": "generated_target_runtime_execution", "status": "not_performed"},
            {"id": "loop_reingest_execution", "status": "not_performed"},
            {"id": "loop_lowering", "status": "blocked"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "loop_boundedness_generalization", "status": "blocked"},
            {"id": "p89_private_reviewer_hold", "status": "preserved"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P93 runs a local Python reference evaluator over the P91 loop expected samples under the P92 policy.",
            "All seven selected comparisons pass with zero absolute error.",
            "P93 is a reference table consistency gate, not original-source, generated-target, or re-ingest evidence.",
        ],
        "blockedStatements": [
            "The original C loop source was executed.",
            "Generated loop target code was executed.",
            "Re-ingested loop code was executed.",
            "Loop lowering is implemented.",
            "Loop headers, latches, variants, or back-edge semantics are supported.",
            "The P92 boundedness policy is a general loop policy.",
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
            "Replace the reference harness with original-source execution for the selected C loop fixture.",
            "Keep loop/back-edge support blocked until lowering and re-ingest evidence exists.",
            "Keep the P89/P88 implementation hold unchanged unless a real reviewer response exists.",
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
        "title": "FEF-P93 Loop Reference Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "loop_reference_runtime_table_consistency_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Reference-runtime table consistency only; no original C execution, generated target execution, re-ingest execution, loop lowering, loop/back-edge support, general boundedness policy, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P93 compares a local Python reference evaluator against all P91 loop expected samples.",
            "All seven comparisons pass with zero absolute error under the P92 policy.",
            "The selected loop fixture remains blocked for implementation/support claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p93_loop_reference_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p93_loop_reference_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p93_loop_reference_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P93 Loop Reference Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Replace the reference harness with original-source execution for the selected C loop fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | n | Expected | Observed | Abs Error | Pass |", "|---|---:|---:|---:|---:|---:|---|"]
    for row in payload["runtimeComparison"]["rows"]:
        rows.append(
            f"| `{row['sampleId']}` | {row['inputs']['x']} | {row['inputs']['n']} | {row['expected']} | {row['observed']} | {row['absError']} | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P93 Loop Reference Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P93 runs a local reference evaluator over selected loop samples under the P92 policy.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Comparisons: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Max iteration count: `{summary['maxIterationCount']}`",
            f"- Total back-edge taken count: `{summary['totalBackEdgeTakenCount']}`",
            f"- Reference runtime only: `{summary['allReferenceRuntimeOnly']}`",
            f"- Original source executed: `{summary['originalSourceExecuted']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            "",
            "## Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Reference runtime table consistency only.",
            "- No original C, generated target, or re-ingested execution.",
            "- No loop lowering or loop/back-edge support claim.",
            "- No general boundedness policy claim.",
            "- No frontend lowering change.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_row(row: dict[str, Any]) -> None:
    runtime = reference_runtime(float(row["inputs"]["x"]), int(row["inputs"]["n"]))
    if row["observed"] != runtime["observed"]:
        raise ValueError("observed value does not match reference runtime")
    if row["iterationCount"] != runtime["iterationCount"]:
        raise ValueError("iteration count does not match reference runtime")
    if row["backEdgeTakenCount"] != runtime["backEdgeTakenCount"]:
        raise ValueError("back-edge count does not match reference runtime")
    if row["observed"] != row["expected"]:
        raise ValueError("observed value must match expected")
    if row["absError"] != abs(row["observed"] - row["expected"]):
        raise ValueError("absolute error mismatch")
    if row["policyEligibleForExecution"] is not True:
        raise ValueError("all selected rows must be policy eligible")
    if row["referenceRuntimeOnly"] is not True:
        raise ValueError("row must remain reference-runtime-only")
    for key in ["originalSourceExecuted", "generatedTargetExecuted", "reingestedTargetExecuted"]:
        if row[key] is not False:
            raise ValueError(f"{key} must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P93 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P93 status")
    p92.validate_payload(read_json(P92_RESULT))
    summary = payload["summary"]
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
    for key in [
        "p92ValidationPass",
        "p92ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allPolicyEligible",
        "allObservedFinite",
        "allReferenceRuntimeOnly",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["comparisonCount"] != 7 or summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("expected seven passing comparisons")
    if summary["zeroIterationCount"] != 2:
        raise ValueError("expected two zero-iteration rows")
    if summary["singleIterationCount"] != 1:
        raise ValueError("expected one single-iteration row")
    if summary["multiIterationCount"] != 4:
        raise ValueError("expected four multi-iteration rows")
    if summary["maxIterationCount"] != 8:
        raise ValueError("expected max iteration count of eight")
    if summary["totalBackEdgeTakenCount"] != 21:
        raise ValueError("unexpected back-edge total")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("expected zero max abs error")
    for key in [
        "originalSourceExecuted",
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "loopOriginalSourceExecutionClaim",
        "loopGeneratedTargetExecutionClaim",
        "loopReingestExecutionClaim",
        "loopLoweringClaim",
        "loopBackedgeSupportClaim",
        "loopBoundednessPolicyGeneralClaim",
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
        "loop_reference_runtime_gate": "recorded",
        "original_c_loop_runtime_execution": "not_performed",
        "generated_target_runtime_execution": "not_performed",
        "loop_reingest_execution": "not_performed",
        "loop_lowering": "blocked",
        "loop_backedge_support": "blocked",
        "loop_boundedness_generalization": "blocked",
        "p89_private_reviewer_hold": "preserved",
        "frontend_lowering_change": "not_performed",
        "general_branch_control_flow_support": "blocked",
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
    result_path = out_dir / f"fef_p93_loop_reference_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p93_loop_reference_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p93_loop_reference_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p93_loop_reference_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p93_loop_reference_runtime_gate")
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
    print("FEF_P93_LOOP_REFERENCE_RUNTIME_GATE_OK")
    print(f"pass_count={built['payload']['summary']['passCount']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
