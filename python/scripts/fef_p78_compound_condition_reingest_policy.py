#!/usr/bin/env python3
"""FEF-P78 selected re-ingest policy for the compound-condition fixture."""

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

from scripts import fef_p77_compound_condition_generated_target_runtime_gate as p77

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p78_compound_condition_reingest_policy.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P78_COMPOUND_CONDITION_REINGEST_POLICY_PASS"

P77_PACKET = ROOT / "reports/evidence_packets/fef_p77_compound_condition_generated_target_runtime_gate.json"
P77_RESULT = ROOT / "python/results/fef_p77_compound_condition_generated_target_runtime_gate/fef_p77_compound_condition_generated_target_runtime_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_reingest_policy_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_reingest_supported": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
    "guarded_division_runtime_helper_installed": False,
    "nonzero_predicate_runtime_helper_installed": False,
    "selected_codegen_fixture_installed_in_forge": False,
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
    "FEF-P78 records selected re-ingest policy only.",
    "FEF-P78 does not execute eFrog re-ingest.",
    "FEF-P78 does not install helper functions in Forge or eFrog.",
    "FEF-P78 does not change Forge or eFrog lowering behavior.",
    "FEF-P78 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P78 does not claim compound-condition support.",
    "FEF-P78 does not claim assignment/phi or nested branch support.",
    "FEF-P78 does not claim general branch/control-flow support.",
    "FEF-P78 does not claim branch/control-flow re-ingest support.",
    "FEF-P78 does not claim full non-generated source roundtrip.",
    "FEF-P78 does not claim arbitrary C/Rust source-family support.",
    "FEF-P78 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P78 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_policy(p77_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "policyId": "selected_c_and_short_circuit_guard_reingest_policy_v0",
        "selectedFixtureId": p77_payload["summary"]["selectedFixtureId"],
        "scope": "selected_generated_c_fixture_only",
        "status": "policy_recorded_execution_blocked",
        "sourceTargetLanguage": "c",
        "reingestExecutionStatus": "not_executed",
        "requiredAcceptedSurface": [
            {
                "surfaceId": "static_helper_step01",
                "description": "Accept static helper definition for mg_step01 as selected guard helper text.",
                "requiredToken": "static double mg_step01(double value)",
            },
            {
                "surfaceId": "static_helper_nonzero01",
                "description": "Accept static helper definition for mg_nonzero01 as selected nonzero guard helper text.",
                "requiredToken": "static double mg_nonzero01(double value)",
            },
            {
                "surfaceId": "static_helper_guarded_div",
                "description": "Accept static helper definition for mg_guarded_div as selected guarded division helper text.",
                "requiredToken": "static double mg_guarded_div(double numerator, double denominator, double default_value, double guard)",
            },
            {
                "surfaceId": "selected_if_guard_shape",
                "description": "Preserve selected left-false short-circuit skip shape by recognizing if (lhs != 0.0).",
                "requiredToken": "if (lhs != 0.0)",
            },
            {
                "surfaceId": "selected_return_shape",
                "description": "Accept selected affine return shape over lhs, rhs, and selected.",
                "requiredToken": "return lhs * rhs * selected;",
            },
        ],
        "requiredRejectedSurface": [
            {
                "surfaceId": "arbitrary_boolean_expression",
                "description": "Reject arbitrary && and || expressions outside the selected generated fixture.",
            },
            {
                "surfaceId": "side_effect_condition",
                "description": "Reject condition terms with function calls, mutation, assignment, volatile reads, or observable side effects.",
            },
            {
                "surfaceId": "nested_condition_tree",
                "description": "Reject nested compound-condition trees beyond the selected two-term shape.",
            },
            {
                "surfaceId": "helper_runtime_import",
                "description": "Reject claims that helpers are installed globally in Forge/eFrog runtime packages.",
            },
        ],
        "requiredExecutionGate": [
            "parse selected generated C fixture",
            "recover helper calls and selected guard shape",
            "emit canonical selected EML or IR packet",
            "recompile to Python reference target",
            "compare against P77 generated C runtime rows",
            "record re-ingest packet with all broad claims false",
        ],
        "requiredComparisonRows": [
            {
                "sampleId": row["sampleId"],
                "expected": row.get("observed", row["expected"]),
                "path": row["path"],
                "reingestExecuted": False,
                "comparisonStatus": "pending_reingest_execution",
            }
            for row in p77_payload["runtimeComparison"]["rows"]
        ],
    }


def policy_validation_rows(policy: dict[str, Any], p77_payload: dict[str, Any]) -> list[dict[str, Any]]:
    source = p77_payload["selectedCodegenFixture"]["source"]
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


def build_summary(p77_packet: dict[str, Any], p77_payload: dict[str, Any], policy: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p77ValidationPass": p77_packet["validationStatus"] == "pass",
        "p77ClaimFlagsAllFalse": all(value is False for value in p77_packet["claimFlags"].values()),
        "selectedFixtureId": p77_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p77_payload["summary"]["selectedFixtureStillBlocked"],
        "p77GeneratedRuntimePassCount": p77_payload["summary"]["passCount"],
        "p77GeneratedRuntimeMaxAbsError": p77_payload["summary"]["maxAbsError"],
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
        "compoundConditionReingestSupported": False,
        "helperRuntimeInstalled": False,
        "codegenFixtureInstalledInForge": False,
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "compoundConditionLoweringImplemented": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
        "guardedDivisionRuntimeHelperInstalled": False,
        "nonzeroPredicateRuntimeHelperInstalled": False,
        "assignmentPhiSupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
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
    p77_packet = read_json(P77_PACKET)
    p77_payload = read_json(P77_RESULT)
    p77.validate_payload(p77_payload)
    policy = selected_policy(p77_payload)
    rows = policy_validation_rows(policy, p77_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p78-compound-condition-reingest-policy",
        "decision": "selected_compound_condition_reingest_policy_recorded_execution_blocked",
        "sourcePacket": {
            "phase": "P77",
            "packetPath": str(P77_PACKET.relative_to(ROOT)),
            "resultPath": str(P77_RESULT.relative_to(ROOT)),
            "reviewDecision": p77_packet["reviewDecision"],
            "validationStatus": p77_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p77_payload["selectedFixture"]),
        "selectedCodegenFixture": copy.deepcopy(p77_payload["selectedCodegenFixture"]),
        "reingestPolicy": policy,
        "policyValidationRows": rows,
        "summary": build_summary(p77_packet, p77_payload, policy, rows),
        "releaseGates": [
            {"id": "selected_reingest_policy", "status": "recorded_execution_blocked"},
            {"id": "selected_reingest_execution", "status": "not_performed"},
            {"id": "helper_runtime_installation", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "short_circuit_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P78 records selected re-ingest policy for the generated compound-condition fixture.",
            "The policy lists accepted helper/guard surfaces and rejected unsupported surfaces.",
            "P78 does not execute eFrog re-ingest or claim re-ingest support.",
        ],
        "blockedStatements": [
            "Re-ingested compound-condition code was executed.",
            "Compound-condition re-ingest is supported.",
            "Generated compound-condition runtime support is installed in Forge or eFrog.",
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
            "Execute the selected generated compound-condition re-ingest gate.",
            "Compare re-ingested Python target rows against P77 generated C runtime rows.",
            "Record private reviewer response to the P47-P78 branch/control-flow bundle.",
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
        "title": "FEF-P78 Compound-Condition Re-ingest Policy",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_reingest_policy_recorded_execution_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected re-ingest policy only; no eFrog re-ingest execution, helper installation, Forge/eFrog behavior change, compound-condition support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P78 names the accepted selected helper/codegen surfaces for a future re-ingest gate.",
            "P78 names unsupported surfaces that must remain rejected.",
            "Re-ingest execution remains blocked for a separate gate.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p78_compound_condition_reingest_policy.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p78_compound_condition_reingest_policy.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p78_compound_condition_reingest_policy.v0",
        "date": DATE,
        "title": "FEF-P78 Compound-Condition Re-ingest Policy",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Execute the selected generated compound-condition re-ingest gate.",
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
            "# FEF-P78 Compound-Condition Re-ingest Policy",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P78 records selected re-ingest policy without executing re-ingest.",
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
            f"- Compound-condition re-ingest supported: `{summary['compoundConditionReingestSupported']}`",
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
            "- Selected re-ingest policy only.",
            "- No eFrog re-ingest execution.",
            "- No Forge/eFrog behavior change or helper installation.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_policy(policy: dict[str, Any]) -> None:
    if policy["status"] != "policy_recorded_execution_blocked":
        raise ValueError("policy must remain execution-blocked")
    if policy["scope"] != "selected_generated_c_fixture_only":
        raise ValueError("policy must remain selected-fixture-only")
    if policy["reingestExecutionStatus"] != "not_executed":
        raise ValueError("re-ingest must not execute in P78")
    if len(policy["requiredAcceptedSurface"]) != 5:
        raise ValueError("unexpected accepted surface count")
    if len(policy["requiredRejectedSurface"]) != 4:
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
        raise ValueError("invalid FEF-P78 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P78 status")
    p77.validate_payload(read_json(P77_RESULT))
    validate_policy(payload["reingestPolicy"])
    for row in payload["policyValidationRows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p77ValidationPass",
        "p77ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "reingestPolicyRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["p77GeneratedRuntimePassCount"] != 7 or summary["p77GeneratedRuntimeMaxAbsError"] != 0.0:
        raise ValueError("P77 source evidence must remain exact")
    if summary["requiredAcceptedSurfaceCount"] != 5 or summary["requiredRejectedSurfaceCount"] != 4:
        raise ValueError("unexpected policy surface counts")
    if summary["requiredComparisonRowCount"] != 7:
        raise ValueError("unexpected comparison row count")
    if summary["policyValidationFailCount"] != 0:
        raise ValueError("policy validation must not fail")
    for key in [
        "reingestExecuted",
        "compoundConditionReingestSupported",
        "helperRuntimeInstalled",
        "codegenFixtureInstalledInForge",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "compoundConditionLoweringImplemented",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
        "guardedDivisionRuntimeHelperInstalled",
        "nonzeroPredicateRuntimeHelperInstalled",
        "assignmentPhiSupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
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
    result_path = out_dir / f"fef_p78_compound_condition_reingest_policy_{STAMP}.json"
    report_path = report_dir / f"fef_p78_compound_condition_reingest_policy_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p78_compound_condition_reingest_policy.json"
    feed_path = command_feed_dir / f"fef_p78_compound_condition_reingest_policy_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p78_compound_condition_reingest_policy")
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
    print("FEF_P78_COMPOUND_CONDITION_REINGEST_POLICY_OK")
    print(f"policy_status={built['payload']['summary']['policyStatus']}")
    print(f"accepted_surface_count={built['payload']['summary']['requiredAcceptedSurfaceCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
