#!/usr/bin/env python3
"""FEF-P99 selected re-ingest policy for the generated loop fixture."""

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

from scripts import fef_p98_loop_generated_target_runtime_gate as p98  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p99_loop_reingest_policy.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P99_LOOP_REINGEST_POLICY_PASS"

P98_PACKET = ROOT / "reports/evidence_packets/fef_p98_loop_generated_target_runtime_gate.json"
P98_RESULT = ROOT / "python/results/fef_p98_loop_generated_target_runtime_gate/fef_p98_loop_generated_target_runtime_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_reingest_policy_claim": False,
    "loop_reingest_execution_claim": False,
    "loop_reingest_supported": False,
    "loop_lowering_implemented": False,
    "loop_backedge_support_claim": False,
    "loop_backedge_semantics_implemented": False,
    "loop_boundedness_policy_general_claim": False,
    "selected_codegen_fixture_installed": False,
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
    "FEF-P99 records selected loop re-ingest policy only.",
    "FEF-P99 does not execute eFrog re-ingest.",
    "FEF-P99 does not install loop lowering in Forge or eFrog.",
    "FEF-P99 does not change Forge or eFrog lowering behavior.",
    "FEF-P99 does not implement loop headers, latches, variants, or back-edge semantics in Forge or eFrog.",
    "FEF-P99 does not implement a general loop boundedness policy.",
    "FEF-P99 does not claim loop/back-edge support.",
    "FEF-P99 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P99 does not claim general branch/control-flow support.",
    "FEF-P99 does not claim branch/control-flow re-ingest support.",
    "FEF-P99 does not claim full non-generated source roundtrip.",
    "FEF-P99 does not claim arbitrary C/Rust source-family support.",
    "FEF-P99 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P99 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_policy(p98_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "policyId": "selected_c_while_accumulate_loop_reingest_policy_v0",
        "selectedFixtureId": p98_payload["summary"]["selectedFixtureId"],
        "scope": "selected_generated_c_loop_fixture_only",
        "status": "policy_recorded_execution_blocked",
        "sourceTargetLanguage": "c",
        "reingestExecutionStatus": "not_executed",
        "requiredAcceptedSurface": [
            {
                "surfaceId": "static_helper_loop_effective_iterations",
                "description": "Accept selected helper definition that maps n to max(0, n).",
                "requiredToken": "static int mg_loop_effective_iterations(int n)",
            },
            {
                "surfaceId": "selected_generated_loop_function",
                "description": "Accept the selected generated loop fixture function signature.",
                "requiredToken": "double c_while_accumulate_v0_generated_fixture(double x, int n)",
            },
            {
                "surfaceId": "selected_effective_iteration_binding",
                "description": "Accept binding of selected effective iteration count.",
                "requiredToken": "int k = mg_loop_effective_iterations(n);",
            },
            {
                "surfaceId": "selected_closed_form_loop_return",
                "description": "Accept closed-form loop result selected by P96 lowering.",
                "requiredToken": "return x * (double)k;",
            },
        ],
        "requiredRejectedSurface": [
            {
                "surfaceId": "arbitrary_while_loop",
                "description": "Reject arbitrary while-loop syntax outside the selected generated closed-form fixture.",
            },
            {
                "surfaceId": "arbitrary_for_loop",
                "description": "Reject arbitrary for-loop syntax outside the selected generated closed-form fixture.",
            },
            {
                "surfaceId": "side_effect_loop_body",
                "description": "Reject loops with function calls, mutation beyond selected locals, volatile reads, or observable side effects.",
            },
            {
                "surfaceId": "unbounded_or_data_dependent_backedge",
                "description": "Reject back edges without the selected P92 boundedness policy and effective-iteration cap.",
            },
            {
                "surfaceId": "helper_runtime_import",
                "description": "Reject claims that the loop helper is installed globally in Forge/eFrog runtime packages.",
            },
        ],
        "requiredExecutionGate": [
            "parse selected generated C loop fixture",
            "recover selected effective-iteration helper",
            "recover selected closed-form loop return",
            "emit canonical selected EML or IR packet",
            "recompile to Python reference target",
            "compare against P98 generated C runtime rows",
            "record re-ingest packet with all broad claims false",
        ],
        "requiredComparisonRows": [
            {
                "sampleId": row["sampleId"],
                "expected": row.get("observed", row["expected"]),
                "path": row["path"],
                "effectiveIterationCount": row["effectiveIterationCount"],
                "reingestExecuted": False,
                "comparisonStatus": "pending_reingest_execution",
            }
            for row in p98_payload["runtimeComparison"]["rows"]
        ],
    }


def policy_validation_rows(policy: dict[str, Any], p98_payload: dict[str, Any]) -> list[dict[str, Any]]:
    source = p98_payload["selectedCodegenFixture"]["source"]
    rows = []
    for item in policy["requiredAcceptedSurface"]:
        present = item["requiredToken"] in source
        rows.append(
            {
                "surfaceId": item["surfaceId"],
                "kind": "required_accept",
                "tokenPresentInSelectedFixture": present,
                "pass": present,
                "reingestExecuted": False,
            }
        )
    for item in policy["requiredRejectedSurface"]:
        rows.append(
            {
                "surfaceId": item["surfaceId"],
                "kind": "required_reject",
                "tokenPresentInSelectedFixture": False,
                "pass": True,
                "reingestExecuted": False,
            }
        )
    return rows


def build_summary(p98_packet: dict[str, Any], p98_payload: dict[str, Any], policy: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p98ValidationPass": p98_packet["validationStatus"] == "pass",
        "p98ClaimFlagsAllFalse": all(value is False for value in p98_packet["claimFlags"].values()),
        "selectedFixtureId": p98_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p98_payload["summary"]["selectedFixtureStillBlocked"],
        "p98GeneratedRuntimePassCount": p98_payload["summary"]["passCount"],
        "p98GeneratedRuntimeMaxAbsError": p98_payload["summary"]["maxAbsError"],
        "policyId": policy["policyId"],
        "policyStatus": policy["status"],
        "policyScope": policy["scope"],
        "requiredAcceptedSurfaceCount": len(policy["requiredAcceptedSurface"]),
        "requiredRejectedSurfaceCount": len(policy["requiredRejectedSurface"]),
        "requiredExecutionGateStepCount": len(policy["requiredExecutionGate"]),
        "requiredComparisonRowCount": len(policy["requiredComparisonRows"]),
        "policyValidationPassCount": sum(1 for row in rows if row["pass"]),
        "policyValidationFailCount": sum(1 for row in rows if not row["pass"]),
        "reingestPolicyRecorded": True,
        "reingestExecuted": False,
        "loopReingestSupported": False,
        "selectedCodegenFixtureInstalled": False,
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "loopLoweringImplemented": False,
        "loopBackedgeSupportClaim": False,
        "loopBackedgeSemanticsImplemented": False,
        "loopBoundednessPolicyGeneralClaim": False,
        "assignmentPhiSupportClaim": False,
        "compoundConditionSupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
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
    p98_packet = read_json(P98_PACKET)
    p98_payload = read_json(P98_RESULT)
    p98.validate_payload(p98_payload)
    policy = selected_policy(p98_payload)
    rows = policy_validation_rows(policy, p98_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p99-loop-reingest-policy",
        "decision": "selected_loop_reingest_policy_recorded_execution_blocked",
        "sourcePacket": {
            "phase": "P98",
            "packetPath": str(P98_PACKET.relative_to(ROOT)),
            "resultPath": str(P98_RESULT.relative_to(ROOT)),
            "reviewDecision": p98_packet["reviewDecision"],
            "validationStatus": p98_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p98_payload["selectedFixture"]),
        "selectedCodegenFixture": copy.deepcopy(p98_payload["selectedCodegenFixture"]),
        "reingestPolicy": policy,
        "policyValidationRows": rows,
        "summary": build_summary(p98_packet, p98_payload, policy, rows),
        "releaseGates": [
            {"id": "selected_loop_reingest_policy", "status": "recorded_execution_blocked"},
            {"id": "selected_loop_reingest_execution", "status": "not_performed"},
            {"id": "loop_lowering_installation", "status": "not_performed"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "loop_backedge_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P99 records selected re-ingest policy for the generated loop fixture.",
            "The policy lists accepted helper/codegen surfaces and rejected unsupported loop surfaces.",
            "P99 does not execute eFrog re-ingest or claim re-ingest support.",
        ],
        "blockedStatements": [
            "Re-ingested loop code was executed.",
            "Loop re-ingest is supported.",
            "Generated loop runtime support is installed in Forge or eFrog.",
            "Loop header, latch, variant, or back-edge semantics are implemented in Forge or eFrog.",
            "Loop lowering is implemented.",
            "Loop/back-edge constructs are supported.",
            "The P92 boundedness policy is a general loop policy.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Execute the selected generated loop re-ingest gate.",
            "Compare re-ingested Python target rows against P98 generated C runtime rows.",
            "Record private reviewer response to the P47-P99 branch/control-flow bundle.",
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
        "title": "FEF-P99 Loop Re-ingest Policy",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_loop_reingest_policy_recorded_execution_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected loop re-ingest policy only; no eFrog re-ingest execution, loop lowering installation, Forge/eFrog behavior change, loop/back-edge support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P99 names the accepted selected helper/codegen surfaces for a future loop re-ingest gate.",
            "P99 names unsupported loop surfaces that must remain rejected.",
            "Re-ingest execution remains blocked for a separate gate.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p99_loop_reingest_policy.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p99_loop_reingest_policy.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p99_loop_reingest_policy.v0",
        "date": DATE,
        "title": "FEF-P99 Loop Re-ingest Policy",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Execute the selected generated loop re-ingest gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Surface | Kind | Pass | Re-ingest Executed |", "|---|---|---|---|"]
    for row in payload["policyValidationRows"]:
        rows.append(
            f"| `{row['surfaceId']}` | `{row['kind']}` | `{row['pass']}` | `{row['reingestExecuted']}` |"
        )
    accepted = [f"- `{item['surfaceId']}`: `{item['requiredToken']}`" for item in payload["reingestPolicy"]["requiredAcceptedSurface"]]
    rejected = [f"- `{item['surfaceId']}`: {item['description']}" for item in payload["reingestPolicy"]["requiredRejectedSurface"]]
    return "\n".join(
        [
            "# FEF-P99 Loop Re-ingest Policy",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P99 records selected loop re-ingest policy without executing re-ingest.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Policy id: `{summary['policyId']}`",
            f"- Policy status: `{summary['policyStatus']}`",
            f"- Policy scope: `{summary['policyScope']}`",
            f"- Required accepted surfaces: `{summary['requiredAcceptedSurfaceCount']}`",
            f"- Required rejected surfaces: `{summary['requiredRejectedSurfaceCount']}`",
            f"- Required execution gate steps: `{summary['requiredExecutionGateStepCount']}`",
            f"- Required comparison rows: `{summary['requiredComparisonRowCount']}`",
            f"- Policy validation pass count: `{summary['policyValidationPassCount']}`",
            f"- Policy validation fail count: `{summary['policyValidationFailCount']}`",
            f"- Re-ingest executed: `{summary['reingestExecuted']}`",
            f"- Loop re-ingest supported: `{summary['loopReingestSupported']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Accepted Surface",
            "",
            *accepted,
            "",
            "## Rejected Surface",
            "",
            *rejected,
            "",
            "## Policy Validation Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected loop re-ingest policy only.",
            "- No eFrog re-ingest execution.",
            "- No Forge/eFrog behavior change or loop lowering installation.",
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_policy(policy: dict[str, Any]) -> None:
    if policy["status"] != "policy_recorded_execution_blocked":
        raise ValueError("policy must remain execution-blocked")
    if policy["scope"] != "selected_generated_c_loop_fixture_only":
        raise ValueError("policy must remain selected-fixture-only")
    if policy["reingestExecutionStatus"] != "not_executed":
        raise ValueError("re-ingest must not execute in P99")
    if len(policy["requiredAcceptedSurface"]) != 4:
        raise ValueError("unexpected accepted surface count")
    if len(policy["requiredRejectedSurface"]) != 5:
        raise ValueError("unexpected rejected surface count")
    if len(policy["requiredComparisonRows"]) != 7:
        raise ValueError("expected seven pending comparison rows")
    if any(row["reingestExecuted"] is not False for row in policy["requiredComparisonRows"]):
        raise ValueError("required comparison rows must be pending re-ingest")


def validate_row(row: dict[str, Any]) -> None:
    if row["pass"] is not True:
        raise ValueError("policy validation row must pass")
    if row["reingestExecuted"] is not False:
        raise ValueError("policy validation must not execute re-ingest")
    if row["kind"] == "required_accept" and row["tokenPresentInSelectedFixture"] is not True:
        raise ValueError("required accepted token missing from selected fixture")
    if row["kind"] == "required_reject" and row["tokenPresentInSelectedFixture"] is not False:
        raise ValueError("rejected surface must not be detected as selected fixture token")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P99 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P99 status")
    p98.validate_payload(read_json(P98_RESULT))
    validate_policy(payload["reingestPolicy"])
    for row in payload["policyValidationRows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p98ValidationPass",
        "p98ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "reingestPolicyRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["p98GeneratedRuntimePassCount"] != 7 or summary["p98GeneratedRuntimeMaxAbsError"] != 0.0:
        raise ValueError("P98 source evidence must remain exact")
    if summary["requiredAcceptedSurfaceCount"] != 4 or summary["requiredRejectedSurfaceCount"] != 5:
        raise ValueError("unexpected policy surface counts")
    if summary["requiredComparisonRowCount"] != 7:
        raise ValueError("unexpected comparison row count")
    if summary["policyValidationFailCount"] != 0:
        raise ValueError("policy validation must not fail")
    for key in [
        "reingestExecuted",
        "loopReingestSupported",
        "selectedCodegenFixtureInstalled",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "loopLoweringImplemented",
        "loopBackedgeSupportClaim",
        "loopBackedgeSemanticsImplemented",
        "loopBoundednessPolicyGeneralClaim",
        "assignmentPhiSupportClaim",
        "compoundConditionSupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
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
    result_path = out_dir / f"fef_p99_loop_reingest_policy_{STAMP}.json"
    report_path = report_dir / f"fef_p99_loop_reingest_policy_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p99_loop_reingest_policy.json"
    feed_path = command_feed_dir / f"fef_p99_loop_reingest_policy_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p99_loop_reingest_policy")
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
    print("FEF_P99_LOOP_REINGEST_POLICY_OK")
    print(f"policy_status={built['payload']['summary']['policyStatus']}")
    print(f"accepted_surface_count={built['payload']['summary']['requiredAcceptedSurfaceCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
