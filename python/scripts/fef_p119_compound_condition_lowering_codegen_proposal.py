#!/usr/bin/env python3
"""FEF-P119 selected compound-condition lowering/codegen proposal."""

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

from scripts import fef_p118_compound_condition_generated_target_runtime_blocker as p118  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p119_compound_condition_lowering_codegen_proposal.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P119_COMPOUND_CONDITION_LOWERING_CODEGEN_PROPOSAL_PASS"

P118_PACKET = ROOT / "reports/evidence_packets/fef_p118_compound_condition_generated_target_runtime_blocker.json"
P118_RESULT = ROOT / "python/results/fef_p118_compound_condition_generated_target_runtime_blocker/fef_p118_compound_condition_generated_target_runtime_blocker_2026_06_01.json"

CLAIM_FLAGS = {
    "compound_condition_lowering_codegen_proposal_claim": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_codegen_policy_implemented": False,
    "compound_condition_reingest_policy_implemented": False,
    "compound_condition_generated_target_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "short_circuit_policy_implemented": False,
    "boolean_normalization_policy_implemented": False,
    "predicate_order_policy_implemented": False,
    "compound_condition_support_claim": False,
    "implementation_diff_produced": False,
    "proposal_applied": False,
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
    "FEF-P119 records a selected compound-condition lowering/codegen proposal only.",
    "FEF-P119 does not apply the proposal or change eFrog or Forge source code.",
    "FEF-P119 does not produce an implementation diff.",
    "FEF-P119 does not produce generated fixture text.",
    "FEF-P119 does not execute generated target code.",
    "FEF-P119 does not execute re-ingested code.",
    "FEF-P119 does not implement short-circuit, predicate-order, or boolean-normalization policy in Forge or eFrog.",
    "FEF-P119 does not implement compound-condition lowering.",
    "FEF-P119 does not implement generated compound-condition codegen policy.",
    "FEF-P119 does not implement compound-condition re-ingest policy.",
    "FEF-P119 does not widen Forge or eFrog frontend lowering.",
    "FEF-P119 does not claim compound-condition support.",
    "FEF-P119 does not record reviewer approval or rejection.",
    "FEF-P119 does not claim general branch/control-flow support.",
    "FEF-P119 does not claim branch/control-flow re-ingest support.",
    "FEF-P119 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P119 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_proposal(p118_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposalId": "selected_and_guard_return_lowering_codegen_proposal_v0",
        "selectedFixtureId": p118_payload["summary"]["selectedFixtureId"],
        "status": "proposal_recorded_not_applied",
        "scope": "selected_c_and_guard_return_v0_only",
        "evidenceSource": "FEF-P118",
        "loweringIntent": {
            "sourceShape": "if (x > 0.0 && y > 0.0) { return x + y; } return 0.0;",
            "loweringKind": "ordered_short_circuit_guard_region_with_selected_return",
            "compoundOperator": "&&",
            "predicateEvaluationOrder": [
                "evaluate_left_predicate_x_gt_zero",
                "evaluate_right_predicate_y_gt_zero_only_if_left_true",
                "select_sum_return_only_if_both_predicates_true",
                "select_zero_return_otherwise",
            ],
            "booleanNormalizationModel": "source_order_preserving_boolean_temps",
            "returnModel": "selected_two_path_return_phi_or_select",
        },
        "codegenSketch": {
            "targetLanguage": "c",
            "fixtureOnly": True,
            "text": "bool left = x > 0.0; bool both = left ? (y > 0.0) : false; return both ? (x + y) : 0.0;",
            "requiredHelpers": ["mg_bool_from_predicate", "mg_select_f64"],
            "generatedFixtureTextProduced": False,
        },
        "intendedPipelineHooks": [
            {
                "hookId": "recognize_selected_and_guard_return",
                "targetSurface": "eFrog selected compound-condition source recognizer",
                "candidateAction": "match c_and_guard_return_v0 only and reject other compound-condition shapes",
            },
            {
                "hookId": "emit_source_ordered_predicate_temps",
                "targetSurface": "Forge selected compound-condition normalization",
                "candidateAction": "preserve left-to-right predicate order and explicit right-predicate gating",
            },
            {
                "hookId": "emit_selected_return_phi_or_select",
                "targetSurface": "Forge selected C generated-target fixture text",
                "candidateAction": "emit two-path return selection with sum path and zero path",
            },
            {
                "hookId": "require_p117_p118_evidence_before_run",
                "targetSurface": "generated target runtime gate",
                "candidateAction": "require inherited P117 pass evidence and P118 blocker prerequisites before execution",
            },
        ],
        "requiredApprovalGates": [
            "private reviewer accepts selected-fixture-only compound-condition lowering scope",
            "generated fixture text is recorded in a later phase before execution",
            "generated runtime harness proves selected short-circuit behavior before any support claim",
            "compound-condition re-ingest policy is recorded before any re-ingest probe",
            "existing P51-P119 regression remains green",
            "public/compiler correctness/performance/support claims remain false after any implementation phase",
        ],
        "rollbackCriteria": [
            "proposal matches compound-condition shapes outside c_and_guard_return_v0",
            "generated fixture evaluates the right predicate when the left predicate is false",
            "generated fixture changes selected return-path values",
            "any P117 selected row diverges after later generated fixture comparison",
            "any support/correctness/performance claim flag becomes true",
        ],
        "proposalApplied": False,
        "implementationDiffProduced": False,
        "generatedFixtureTextProduced": False,
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "installedInForge": False,
        "installedInEfrog": False,
        "compilerBehaviorChanged": False,
    }


def build_review_checks(proposal: dict[str, Any], p118_payload: dict[str, Any]) -> list[dict[str, Any]]:
    summary = p118_payload["summary"]
    checks = [
        ("proposal_scope_selected_fixture_only", proposal["scope"] == "selected_c_and_guard_return_v0_only"),
        ("p118_gate_blocked_not_run", summary["generatedTargetGateStatus"] == "blocked_not_run"),
        ("p118_required_before_run_count_is_five", summary["requiredBeforeRunCount"] == 5),
        ("p117_inherited_rows_pass", summary["p117ComparisonCount"] == 7 and summary["p117PassCount"] == 7),
        ("p117_inherited_exact_agreement", summary["p117MaxAbsError"] == 0.0),
        ("p117_inherited_short_circuit_counts", summary["p117RightPredicateEvaluatedCount"] == 4 and summary["p117ShortCircuitCount"] == 3),
        ("proposal_not_applied", proposal["proposalApplied"] is False),
        ("implementation_diff_not_produced", proposal["implementationDiffProduced"] is False),
        ("generated_fixture_text_not_produced", proposal["generatedFixtureTextProduced"] is False),
        ("generated_target_not_executed", proposal["generatedTargetExecuted"] is False),
        ("reingested_target_not_executed", proposal["reingestedTargetExecuted"] is False),
        ("not_installed_in_forge_or_efrog", proposal["installedInForge"] is False and proposal["installedInEfrog"] is False),
    ]
    return [
        {"checkId": check_id, "status": "pass" if passed else "fail", "passed": passed}
        for check_id, passed in checks
    ]


def build_summary(p118_packet: dict[str, Any], p118_payload: dict[str, Any], proposal: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p118ValidationPass": p118_packet["validationStatus"] == "pass",
        "p118ClaimFlagsAllFalse": all(value is False for value in p118_packet["claimFlags"].values()),
        "selectedFixtureId": p118_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p118_payload["summary"]["selectedFixtureStillBlocked"],
        "proposalId": proposal["proposalId"],
        "proposalStatus": proposal["status"],
        "intendedPipelineHookCount": len(proposal["intendedPipelineHooks"]),
        "requiredApprovalGateCount": len(proposal["requiredApprovalGates"]),
        "rollbackCriteriaCount": len(proposal["rollbackCriteria"]),
        "reviewCheckCount": len(checks),
        "reviewCheckPassCount": sum(1 for check in checks if check["passed"]),
        "reviewCheckFailCount": sum(1 for check in checks if not check["passed"]),
        "p118GeneratedTargetGateStatus": p118_payload["summary"]["generatedTargetGateStatus"],
        "p118RequiredBeforeRunCount": p118_payload["summary"]["requiredBeforeRunCount"],
        "p117ComparisonCount": p118_payload["summary"]["p117ComparisonCount"],
        "p117PassCount": p118_payload["summary"]["p117PassCount"],
        "p117MaxAbsError": p118_payload["summary"]["p117MaxAbsError"],
        "p117RightPredicateEvaluatedCount": p118_payload["summary"]["p117RightPredicateEvaluatedCount"],
        "p117ShortCircuitCount": p118_payload["summary"]["p117ShortCircuitCount"],
        "proposalRecorded": True,
        "proposalApplied": proposal["proposalApplied"],
        "implementationDiffProduced": proposal["implementationDiffProduced"],
        "generatedFixtureTextProduced": proposal["generatedFixtureTextProduced"],
        "generatedTargetExecuted": proposal["generatedTargetExecuted"],
        "reingestedTargetExecuted": proposal["reingestedTargetExecuted"],
        "installedInForge": proposal["installedInForge"],
        "installedInEfrog": proposal["installedInEfrog"],
        "compilerBehaviorChanged": proposal["compilerBehaviorChanged"],
        "compoundConditionLoweringImplemented": False,
        "compoundConditionCodegenPolicyImplemented": False,
        "compoundConditionReingestPolicyImplemented": False,
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
    p118_packet = read_json(P118_PACKET)
    p118_payload = read_json(P118_RESULT)
    p118.validate_payload(p118_payload)
    proposal = build_proposal(p118_payload)
    checks = build_review_checks(proposal, p118_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p119-compound-condition-lowering-codegen-proposal",
        "decision": "selected_compound_condition_lowering_codegen_proposal_recorded_not_applied",
        "sourcePacket": {
            "phase": "P118",
            "packetPath": str(P118_PACKET.relative_to(ROOT)),
            "resultPath": str(P118_RESULT.relative_to(ROOT)),
            "reviewDecision": p118_packet["reviewDecision"],
            "validationStatus": p118_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p118_payload["selectedFixture"]),
        "loweringCodegenProposal": proposal,
        "reviewChecks": checks,
        "summary": build_summary(p118_packet, p118_payload, proposal, checks),
        "releaseGates": [
            {"id": "selected_compound_condition_lowering_codegen_proposal", "status": "recorded_not_applied"},
            {"id": "private_reviewer_approval", "status": "required_not_recorded"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "generated_fixture_text", "status": "not_produced"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P119 records a selected compound-condition lowering/codegen proposal.",
            "The proposal has four scoped pipeline hooks, six approval gates, and five rollback criteria.",
            "P119 does not apply the proposal, produce fixture text, execute generated targets, or install lowering.",
        ],
        "blockedStatements": [
            "The compound-condition lowering/codegen proposal has been applied.",
            "An implementation diff has been produced.",
            "Generated compound-condition fixture text has been produced.",
            "Generated compound-condition target code was executed.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit, predicate-order, or boolean-normalization policy is implemented.",
            "Compound-condition lowering is implemented.",
            "Generated compound-condition codegen policy is implemented.",
            "Compound-condition constructs are supported.",
            "General branch/control-flow support is established.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Record private reviewer response to the P47-P119 branch/control-flow bundle.",
            "If approved, create a separate implementation phase with source diffs and rollback checks.",
            "If held, continue the unsupported-form ladders without applying this proposal.",
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
        "title": "FEF-P119 Compound-Condition Lowering Codegen Proposal",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_compound_condition_lowering_codegen_proposal_not_applied",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected proposal only; no implementation diff, generated fixture text, generated execution, re-ingest execution, compound-condition lowering, support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P119 records a selected compound-condition lowering/codegen proposal for c_and_guard_return_v0.",
            "P118 generated-target runtime remains blocked.",
            "Proposal application is held for a separate approved phase.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p119_compound_condition_lowering_codegen_proposal.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p119_compound_condition_lowering_codegen_proposal.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p119_compound_condition_lowering_codegen_proposal.v0",
        "date": DATE,
        "title": "FEF-P119 Compound-Condition Lowering Codegen Proposal",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record private reviewer response or create a separate approved implementation phase.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    hooks = ["| Hook | Target surface |", "|---|---|"]
    for hook in payload["loweringCodegenProposal"]["intendedPipelineHooks"]:
        hooks.append(f"| `{hook['hookId']}` | `{hook['targetSurface']}` |")
    checks = ["| Check | Status |", "|---|---|"]
    for check in payload["reviewChecks"]:
        checks.append(f"| `{check['checkId']}` | `{check['status']}` |")
    return "\n".join(
        [
            "# FEF-P119 Compound-Condition Lowering Codegen Proposal",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P119 records a selected compound-condition lowering/codegen proposal without applying it.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Proposal id: `{summary['proposalId']}`",
            f"- Proposal status: `{summary['proposalStatus']}`",
            f"- Pipeline hooks: `{summary['intendedPipelineHookCount']}`",
            f"- Approval gates: `{summary['requiredApprovalGateCount']}`",
            f"- Rollback criteria: `{summary['rollbackCriteriaCount']}`",
            f"- Review checks passing: `{summary['reviewCheckPassCount']}` / `{summary['reviewCheckCount']}`",
            f"- P118 generated-target gate status: `{summary['p118GeneratedTargetGateStatus']}`",
            f"- Proposal applied: `{summary['proposalApplied']}`",
            f"- Implementation diff produced: `{summary['implementationDiffProduced']}`",
            f"- Generated fixture text produced: `{summary['generatedFixtureTextProduced']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            "",
            "## Intended Pipeline Hooks",
            "",
            *hooks,
            "",
            "## Review Checks",
            "",
            *checks,
            "",
            "## Boundary",
            "",
            "- Proposal only; not applied.",
            "- No source diff, generated fixture text, generated execution, or re-ingest execution.",
            "- No compound-condition lowering/codegen implementation.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P119 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P119 status")
    p118.validate_payload(read_json(P118_RESULT))
    summary = payload["summary"]
    for key in [
        "p118ValidationPass",
        "p118ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "proposalRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["proposalStatus"] != "proposal_recorded_not_applied":
        raise ValueError("proposal must remain not applied")
    if summary["intendedPipelineHookCount"] != 4:
        raise ValueError("expected four pipeline hooks")
    if summary["requiredApprovalGateCount"] != 6:
        raise ValueError("expected six approval gates")
    if summary["rollbackCriteriaCount"] != 5:
        raise ValueError("expected five rollback criteria")
    if summary["reviewCheckCount"] != 12 or summary["reviewCheckFailCount"] != 0:
        raise ValueError("expected twelve passing review checks")
    if summary["p118GeneratedTargetGateStatus"] != "blocked_not_run":
        raise ValueError("P118 generated-target gate must remain blocked")
    if summary["p118RequiredBeforeRunCount"] != 5:
        raise ValueError("unexpected inherited P118 required-before-run count")
    if summary["p117ComparisonCount"] != 7 or summary["p117PassCount"] != 7:
        raise ValueError("unexpected inherited P117 comparison counts")
    if summary["p117MaxAbsError"] != 0.0:
        raise ValueError("unexpected inherited P117 max abs error")
    if summary["p117RightPredicateEvaluatedCount"] != 4 or summary["p117ShortCircuitCount"] != 3:
        raise ValueError("unexpected inherited P117 short-circuit counts")
    for key in [
        "proposalApplied",
        "implementationDiffProduced",
        "generatedFixtureTextProduced",
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "installedInForge",
        "installedInEfrog",
        "compilerBehaviorChanged",
        "compoundConditionLoweringImplemented",
        "compoundConditionCodegenPolicyImplemented",
        "compoundConditionReingestPolicyImplemented",
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
    result_path = out_dir / f"fef_p119_compound_condition_lowering_codegen_proposal_{STAMP}.json"
    report_path = report_dir / f"fef_p119_compound_condition_lowering_codegen_proposal_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p119_compound_condition_lowering_codegen_proposal.json"
    feed_path = command_feed_dir / f"fef_p119_compound_condition_lowering_codegen_proposal_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p119_compound_condition_lowering_codegen_proposal")
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
    print("FEF_P119_COMPOUND_CONDITION_LOWERING_CODEGEN_PROPOSAL_OK")
    print(f"proposal={built['payload']['summary']['proposalStatus']}")
    print(f"review_checks={built['payload']['summary']['reviewCheckPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
