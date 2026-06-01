#!/usr/bin/env python3
"""FEF-P92 boundedness policy for the selected loop/back-edge samples."""

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

from scripts import fef_p91_loop_backedge_expected_samples as p91  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p92_loop_boundedness_policy.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P92_LOOP_BOUNDEDNESS_POLICY_PASS"

P91_PACKET = ROOT / "reports/evidence_packets/fef_p91_loop_backedge_expected_samples.json"
P91_RESULT = ROOT / "python/results/fef_p91_loop_backedge_expected_samples/fef_p91_loop_backedge_expected_samples_2026_05_31.json"

MAX_EFFECTIVE_ITERATIONS = 16

CLAIM_FLAGS = {
    "loop_boundedness_policy_claim": False,
    "loop_execution_allowed_claim": False,
    "loop_runtime_execution_claim": False,
    "loop_reference_runtime_claim": False,
    "loop_lowering_claim": False,
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
    "FEF-P92 records a selected loop boundedness policy only.",
    "FEF-P92 does not execute source, generated, or re-ingested loop code.",
    "FEF-P92 does not apply the policy to perform runtime comparison.",
    "FEF-P92 does not implement loop headers, latches, variants, or general boundedness policy.",
    "FEF-P92 does not implement loop lowering.",
    "FEF-P92 does not widen Forge or eFrog frontend lowering.",
    "FEF-P92 does not claim loop/back-edge support.",
    "FEF-P92 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P92 does not record reviewer approval or rejection.",
    "FEF-P92 does not approve or apply the P88 implementation proposal.",
    "FEF-P92 does not claim general branch/control-flow support.",
    "FEF-P92 does not claim branch/control-flow re-ingest support.",
    "FEF-P92 does not claim full non-generated source roundtrip.",
    "FEF-P92 does not claim arbitrary C/Rust source-family support.",
    "FEF-P92 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P92 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def effective_iteration_count(n: int) -> int:
    return max(0, int(n))


def build_policy(p91_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "policyId": "selected_c_while_accumulate_boundedness_policy_v0",
        "selectedFixtureId": p91_payload["summary"]["selectedFixtureId"],
        "scope": "selected_c_while_accumulate_v0_expected_samples_only",
        "status": "policy_recorded_execution_blocked",
        "maxEffectiveIterationCount": MAX_EFFECTIVE_ITERATIONS,
        "effectiveIterationDefinition": "max(0, int(n)) for the selected C while fixture",
        "requiredAcceptedSurface": [
            {
                "surfaceId": "integer_like_n",
                "description": "The selected sample must provide an integer-like n value.",
            },
            {
                "surfaceId": "finite_scalar_x",
                "description": "The selected sample must provide finite scalar x.",
            },
            {
                "surfaceId": "bounded_effective_iteration_count",
                "description": f"The selected sample must have max(0, n) <= {MAX_EFFECTIVE_ITERATIONS}.",
            },
            {
                "surfaceId": "local_accumulator_only",
                "description": "The selected fixture surface is limited to local acc/i mutation and no observable side effects.",
            },
        ],
        "requiredRejectedSurface": [
            {
                "surfaceId": "unknown_or_symbolic_loop_bound",
                "description": "Reject unknown, symbolic, non-integer, or externally supplied loop bounds without an explicit cap.",
            },
            {
                "surfaceId": "iteration_count_above_limit",
                "description": "Reject samples whose effective iteration count exceeds the selected cap.",
            },
            {
                "surfaceId": "non_finite_numeric_input",
                "description": "Reject NaN or infinite numeric inputs.",
            },
            {
                "surfaceId": "side_effecting_loop_body",
                "description": "Reject calls, memory writes, volatile reads, IO, pointer mutation, and non-local state.",
            },
            {
                "surfaceId": "nested_or_unstructured_loop",
                "description": "Reject nested loops, breaks, continues, labels, gotos, and unstructured back edges.",
            },
        ],
        "requiredExecutionGate": [
            "evaluate policy eligibility for each P91 sample",
            "keep loop execution disabled unless every selected sample is eligible",
            "run a reference evaluator only in a later phase",
            "compare reference outputs against P91 expected values only in a later phase",
            "record all support/correctness/performance claims false after the later gate",
        ],
        "policyAppliedToRuntime": False,
        "runtimeExecutionPerformed": False,
    }


def sample_policy_rows(policy: dict[str, Any], p91_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    max_iterations = policy["maxEffectiveIterationCount"]
    for sample in p91_payload["expectedSamples"]:
        n = int(sample["inputs"]["n"])
        x = float(sample["inputs"]["x"])
        effective_count = effective_iteration_count(n)
        integer_like_n = isinstance(sample["inputs"]["n"], int)
        finite_x = math.isfinite(x)
        within_limit = effective_count <= max_iterations
        eligible = integer_like_n and finite_x and within_limit
        rows.append(
            {
                "sampleId": sample["sampleId"],
                "inputN": n,
                "inputX": x,
                "effectiveIterationCount": effective_count,
                "integerLikeN": integer_like_n,
                "finiteX": finite_x,
                "withinIterationLimit": within_limit,
                "policyEligibleForFutureExecution": eligible,
                "policyStatus": "eligible_pending_execution" if eligible else "blocked_by_policy",
                "boundednessPolicyAppliedToRuntime": False,
                "runtimeExecutionPerformed": False,
                "expected": sample["expected"],
            }
        )
    return rows


def build_summary(
    p91_packet: dict[str, Any],
    p91_payload: dict[str, Any],
    policy: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p91ValidationPass": p91_packet["validationStatus"] == "pass",
        "p91ClaimFlagsAllFalse": all(value is False for value in p91_packet["claimFlags"].values()),
        "selectedFixtureId": p91_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p91_payload["summary"]["selectedFixtureStillBlocked"],
        "p91SampleCount": p91_payload["summary"]["sampleCount"],
        "policyId": policy["policyId"],
        "policyStatus": policy["status"],
        "policyScope": policy["scope"],
        "policyRecorded": True,
        "maxEffectiveIterationCount": policy["maxEffectiveIterationCount"],
        "requiredAcceptedSurfaceCount": len(policy["requiredAcceptedSurface"]),
        "requiredRejectedSurfaceCount": len(policy["requiredRejectedSurface"]),
        "requiredExecutionGateStepCount": len(policy["requiredExecutionGate"]),
        "samplePolicyRowCount": len(rows),
        "eligibleSampleCount": sum(1 for row in rows if row["policyEligibleForFutureExecution"]),
        "blockedSampleCount": sum(1 for row in rows if not row["policyEligibleForFutureExecution"]),
        "maxSampleEffectiveIterationCount": max(row["effectiveIterationCount"] for row in rows),
        "allSamplesWithinIterationLimit": all(row["withinIterationLimit"] is True for row in rows),
        "allSamplesFinite": all(row["finiteX"] is True for row in rows),
        "allSamplesIntegerLikeN": all(row["integerLikeN"] is True for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "policyAppliedToRuntime": False,
        "runtimeExecutionPerformed": False,
        "loopExecutionAllowedClaim": False,
        "loopRuntimeExecutionClaim": False,
        "loopReferenceRuntimeClaim": False,
        "loopLoweringClaim": False,
        "loopBackedgeSupportClaim": False,
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
    p91_packet = read_json(P91_PACKET)
    p91_payload = read_json(P91_RESULT)
    p91.validate_payload(p91_payload)
    policy = build_policy(p91_payload)
    rows = sample_policy_rows(policy, p91_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p92-loop-boundedness-policy",
        "decision": "loop_boundedness_policy_recorded_execution_blocked",
        "sourcePacket": {
            "phase": "P91",
            "packetPath": str(P91_PACKET.relative_to(ROOT)),
            "resultPath": str(P91_RESULT.relative_to(ROOT)),
            "reviewDecision": p91_packet["reviewDecision"],
            "validationStatus": p91_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p91_payload["selectedFixture"]),
        "boundednessPolicy": policy,
        "samplePolicyRows": rows,
        "summary": build_summary(p91_packet, p91_payload, policy, rows),
        "releaseGates": [
            {"id": "loop_boundedness_policy", "status": "recorded_execution_blocked"},
            {"id": "loop_policy_sample_eligibility", "status": "recorded"},
            {"id": "loop_runtime_execution", "status": "not_performed"},
            {"id": "loop_reference_runtime_gate", "status": "blocked_until_next_phase"},
            {"id": "loop_lowering", "status": "blocked"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "p89_private_reviewer_hold", "status": "preserved"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P92 records a selected boundedness policy for the P91 loop samples.",
            "All seven P91 samples are eligible for a future execution gate under the selected cap.",
            "P92 does not execute loop code or claim loop/back-edge support.",
        ],
        "blockedStatements": [
            "Loop fixtures were executed.",
            "Loop execution is now supported.",
            "Loop lowering is implemented.",
            "Loop headers, latches, variants, or back-edge semantics are supported.",
            "The selected boundedness policy is a general loop policy.",
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
            "Turn the selected P91 sample table into a reference runtime comparison gate under this policy.",
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
        "title": "FEF-P92 Loop Boundedness Policy",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "loop_boundedness_policy_recorded_execution_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected boundedness policy only; no loop execution, reference runtime gate, lowering, general boundedness policy, loop support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P92 records a selected boundedness policy for c_while_accumulate_v0.",
            "All P91 samples are eligible for future execution under the selected cap.",
            "Loop execution and support remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p92_loop_boundedness_policy.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p92_loop_boundedness_policy.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p92_loop_boundedness_policy.v0",
        "date": DATE,
        "title": "FEF-P92 Loop Boundedness Policy",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Turn the selected P91 sample table into a reference runtime comparison gate under the P92 policy.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | n | Effective Iterations | Eligible | Runtime |", "|---|---:|---:|---|---|"]
    for row in payload["samplePolicyRows"]:
        rows.append(
            f"| `{row['sampleId']}` | {row['inputN']} | {row['effectiveIterationCount']} | `{row['policyEligibleForFutureExecution']}` | `{row['runtimeExecutionPerformed']}` |"
        )
    return "\n".join(
        [
            "# FEF-P92 Loop Boundedness Policy",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P92 records a selected boundedness policy before any loop execution gate.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Policy: `{summary['policyId']}`",
            f"- Max effective iterations: `{summary['maxEffectiveIterationCount']}`",
            f"- Eligible samples: `{summary['eligibleSampleCount']}`",
            f"- Blocked samples: `{summary['blockedSampleCount']}`",
            f"- Max sample effective iterations: `{summary['maxSampleEffectiveIterationCount']}`",
            f"- Runtime execution performed: `{summary['runtimeExecutionPerformed']}`",
            f"- Policy applied to runtime: `{summary['policyAppliedToRuntime']}`",
            f"- Loop/back-edge support claim: `{summary['loopBackedgeSupportClaim']}`",
            "",
            "## Sample Policy Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Policy only; no loop execution.",
            "- No reference runtime comparison yet.",
            "- No general boundedness policy claim.",
            "- No loop lowering or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_policy_row(row: dict[str, Any]) -> None:
    expected_effective = effective_iteration_count(row["inputN"])
    if row["effectiveIterationCount"] != expected_effective:
        raise ValueError("effective iteration count mismatch")
    if row["withinIterationLimit"] != (expected_effective <= MAX_EFFECTIVE_ITERATIONS):
        raise ValueError("iteration-limit flag mismatch")
    expected_eligible = row["integerLikeN"] and row["finiteX"] and row["withinIterationLimit"]
    if row["policyEligibleForFutureExecution"] != expected_eligible:
        raise ValueError("policy eligibility mismatch")
    if row["boundednessPolicyAppliedToRuntime"] is not False:
        raise ValueError("policy must not be applied to runtime")
    if row["runtimeExecutionPerformed"] is not False:
        raise ValueError("runtime execution must not be performed")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P92 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P92 status")
    p91.validate_payload(read_json(P91_RESULT))
    summary = payload["summary"]
    for row in payload["samplePolicyRows"]:
        validate_policy_row(row)
    for key in [
        "p91ValidationPass",
        "p91ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "policyRecorded",
        "allSamplesWithinIterationLimit",
        "allSamplesFinite",
        "allSamplesIntegerLikeN",
        "allRuntimeExecutionNotPerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["policyStatus"] != "policy_recorded_execution_blocked":
        raise ValueError("policy must remain execution-blocked")
    if summary["maxEffectiveIterationCount"] != MAX_EFFECTIVE_ITERATIONS:
        raise ValueError("unexpected max iteration limit")
    if summary["samplePolicyRowCount"] != 7:
        raise ValueError("expected seven policy rows")
    if summary["eligibleSampleCount"] != 7 or summary["blockedSampleCount"] != 0:
        raise ValueError("expected all selected P91 samples to be eligible")
    if summary["maxSampleEffectiveIterationCount"] != 8:
        raise ValueError("unexpected max sample iteration count")
    if summary["requiredAcceptedSurfaceCount"] != 4:
        raise ValueError("expected four accepted surfaces")
    if summary["requiredRejectedSurfaceCount"] != 5:
        raise ValueError("expected five rejected surfaces")
    if summary["requiredExecutionGateStepCount"] != 5:
        raise ValueError("expected five execution gate steps")
    for key in [
        "policyAppliedToRuntime",
        "runtimeExecutionPerformed",
        "loopExecutionAllowedClaim",
        "loopRuntimeExecutionClaim",
        "loopReferenceRuntimeClaim",
        "loopLoweringClaim",
        "loopBackedgeSupportClaim",
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
        "loop_boundedness_policy": "recorded_execution_blocked",
        "loop_policy_sample_eligibility": "recorded",
        "loop_runtime_execution": "not_performed",
        "loop_reference_runtime_gate": "blocked_until_next_phase",
        "loop_lowering": "blocked",
        "loop_backedge_support": "blocked",
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
    result_path = out_dir / f"fef_p92_loop_boundedness_policy_{STAMP}.json"
    report_path = report_dir / f"fef_p92_loop_boundedness_policy_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p92_loop_boundedness_policy.json"
    feed_path = command_feed_dir / f"fef_p92_loop_boundedness_policy_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p92_loop_boundedness_policy")
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
    print("FEF_P92_LOOP_BOUNDEDNESS_POLICY_OK")
    print(f"eligible_samples={built['payload']['summary']['eligibleSampleCount']}")
    print(f"runtime_execution={built['payload']['summary']['runtimeExecutionPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
