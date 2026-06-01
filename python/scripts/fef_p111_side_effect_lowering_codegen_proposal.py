#!/usr/bin/env python3
"""FEF-P111 selected side-effect lowering/codegen proposal."""

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

from scripts import fef_p110_side_effect_generated_target_runtime_blocker as p110  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p111_side_effect_lowering_codegen_proposal.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P111_SIDE_EFFECT_LOWERING_CODEGEN_PROPOSAL_PASS"

P110_PACKET = ROOT / "reports/evidence_packets/fef_p110_side_effect_generated_target_runtime_blocker.json"
P110_RESULT = ROOT / "python/results/fef_p110_side_effect_generated_target_runtime_blocker/fef_p110_side_effect_generated_target_runtime_blocker_2026_06_01.json"

CLAIM_FLAGS = {
    "side_effect_lowering_codegen_proposal_claim": False,
    "side_effect_lowering_implemented": False,
    "side_effect_codegen_policy_implemented": False,
    "generated_target_execution_claim": False,
    "reingest_execution_claim": False,
    "live_external_call_claim": False,
    "unbounded_memory_mutation_claim": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
    "side_effect_memory_support_claim": False,
    "implementation_diff_produced": False,
    "proposal_applied": False,
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
    "FEF-P111 records a selected side-effect lowering/codegen proposal only.",
    "FEF-P111 does not apply the proposal or change eFrog or Forge source code.",
    "FEF-P111 does not produce an implementation diff.",
    "FEF-P111 does not execute generated target code.",
    "FEF-P111 does not execute re-ingested code.",
    "FEF-P111 does not perform live external calls.",
    "FEF-P111 does not perform unbounded memory mutation or aliasing.",
    "FEF-P111 does not implement side-effect/call/memory lowering.",
    "FEF-P111 does not implement generated side-effect codegen policy.",
    "FEF-P111 does not implement side-effect re-ingest policy.",
    "FEF-P111 does not implement effect ordering, external-call, aliasing, or memory-state policy in Forge or eFrog.",
    "FEF-P111 does not widen Forge or eFrog frontend lowering.",
    "FEF-P111 does not claim side-effect/call/memory support.",
    "FEF-P111 does not claim general branch/control-flow support.",
    "FEF-P111 does not claim branch/control-flow re-ingest support.",
    "FEF-P111 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P111 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_proposal(p110_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposalId": "selected_global_state_update_lowering_codegen_proposal_v0",
        "selectedFixtureId": p110_payload["summary"]["selectedFixtureId"],
        "status": "proposal_recorded_not_applied",
        "scope": "selected_c_global_state_update_v0_only",
        "evidenceSource": "FEF-P110",
        "loweringIntent": {
            "sourceShape": "if (x > 0.0) { state = update_state(x); } return state;",
            "loweringKind": "ordered_effect_region_with_guarded_state_update",
            "guardPredicate": "x > 0.0",
            "effectOrder": [
                "evaluate_guard",
                "call_deterministic_update_stub_if_guard_true",
                "write_bounded_state_cell_if_call_occurs",
                "return_bounded_state_cell",
            ],
            "stateModel": "single_explicit_state_cell_no_alias_escape",
            "externalCallModel": "deterministic_stubbed_update_state_only",
        },
        "codegenSketch": {
            "targetLanguage": "c",
            "fixtureOnly": True,
            "text": "if (x > 0.0) { state = mg_stub_update_state(x); } return state;",
            "requiredHelpers": ["mg_stub_update_state", "mg_state_capture_cell"],
            "generatedFixtureTextProduced": False,
        },
        "intendedPipelineHooks": [
            {
                "hookId": "recognize_selected_guarded_global_state_update",
                "targetSurface": "Forge selected side-effect lowering pre-codegen",
                "candidateAction": "match c_global_state_update_v0 only and reject all other side-effect shapes",
            },
            {
                "hookId": "emit_selected_stubbed_update_state_call",
                "targetSurface": "Forge selected C generated-target fixture text",
                "candidateAction": "emit deterministic stub-call surface instead of live external call",
            },
            {
                "hookId": "emit_bounded_state_capture_cell",
                "targetSurface": "generated runtime comparison harness",
                "candidateAction": "capture one explicit state cell and reject alias escape",
            },
            {
                "hookId": "require_p109_p110_evidence_before_run",
                "targetSurface": "generated target runtime gate",
                "candidateAction": "require inherited P109 pass evidence and P110 blocker prerequisites before execution",
            },
        ],
        "requiredApprovalGates": [
            "private reviewer accepts selected-fixture-only side-effect lowering scope",
            "generated fixture text is recorded in a later phase before execution",
            "generated runtime harness proves deterministic stub-call behavior before any support claim",
            "side-effect re-ingest policy is recorded before any re-ingest probe",
            "existing P51-P111 regression remains green",
            "public/compiler correctness/performance/support claims remain false after any implementation phase",
        ],
        "rollbackCriteria": [
            "proposal matches side-effect shapes outside c_global_state_update_v0",
            "generated fixture performs live external calls",
            "generated fixture permits alias escape or unbounded memory mutation",
            "any P109 selected row diverges after later generated fixture comparison",
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


def build_review_checks(proposal: dict[str, Any], p110_payload: dict[str, Any]) -> list[dict[str, Any]]:
    summary = p110_payload["summary"]
    checks = [
        ("proposal_scope_selected_fixture_only", proposal["scope"] == "selected_c_global_state_update_v0_only"),
        ("p110_gate_blocked_not_run", summary["generatedTargetGateStatus"] == "blocked_not_run"),
        ("p110_required_before_run_count_is_six", summary["requiredBeforeRunCount"] == 6),
        ("p109_inherited_rows_pass", summary["p109ComparisonCount"] == 7 and summary["p109PassCount"] == 7),
        ("p109_inherited_exact_agreement", summary["p109MaxAbsError"] == 0.0),
        ("p109_inherited_effect_counts", summary["p109StubbedCallCount"] == 4 and summary["p109BoundedStateWriteCount"] == 4),
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


def build_summary(p110_packet: dict[str, Any], p110_payload: dict[str, Any], proposal: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p110ValidationPass": p110_packet["validationStatus"] == "pass",
        "p110ClaimFlagsAllFalse": all(value is False for value in p110_packet["claimFlags"].values()),
        "selectedFixtureId": p110_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p110_payload["summary"]["selectedFixtureStillBlocked"],
        "proposalId": proposal["proposalId"],
        "proposalStatus": proposal["status"],
        "intendedPipelineHookCount": len(proposal["intendedPipelineHooks"]),
        "requiredApprovalGateCount": len(proposal["requiredApprovalGates"]),
        "rollbackCriteriaCount": len(proposal["rollbackCriteria"]),
        "reviewCheckCount": len(checks),
        "reviewCheckPassCount": sum(1 for check in checks if check["passed"]),
        "reviewCheckFailCount": sum(1 for check in checks if not check["passed"]),
        "p110GeneratedTargetGateStatus": p110_payload["summary"]["generatedTargetGateStatus"],
        "p110RequiredBeforeRunCount": p110_payload["summary"]["requiredBeforeRunCount"],
        "p109ComparisonCount": p110_payload["summary"]["p109ComparisonCount"],
        "p109PassCount": p110_payload["summary"]["p109PassCount"],
        "p109MaxAbsError": p110_payload["summary"]["p109MaxAbsError"],
        "p109StubbedCallCount": p110_payload["summary"]["p109StubbedCallCount"],
        "p109BoundedStateWriteCount": p110_payload["summary"]["p109BoundedStateWriteCount"],
        "proposalRecorded": True,
        "proposalApplied": proposal["proposalApplied"],
        "implementationDiffProduced": proposal["implementationDiffProduced"],
        "generatedFixtureTextProduced": proposal["generatedFixtureTextProduced"],
        "generatedTargetExecuted": proposal["generatedTargetExecuted"],
        "reingestedTargetExecuted": proposal["reingestedTargetExecuted"],
        "installedInForge": proposal["installedInForge"],
        "installedInEfrog": proposal["installedInEfrog"],
        "compilerBehaviorChanged": proposal["compilerBehaviorChanged"],
        "sideEffectLoweringImplemented": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "sideEffectMemorySupportClaim": False,
        "sideEffectCodegenPolicyImplemented": False,
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
    p110_packet = read_json(P110_PACKET)
    p110_payload = read_json(P110_RESULT)
    p110.validate_payload(p110_payload)
    proposal = build_proposal(p110_payload)
    checks = build_review_checks(proposal, p110_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p111-side-effect-lowering-codegen-proposal",
        "decision": "selected_side_effect_lowering_codegen_proposal_recorded_not_applied",
        "sourcePacket": {
            "phase": "P110",
            "packetPath": str(P110_PACKET.relative_to(ROOT)),
            "resultPath": str(P110_RESULT.relative_to(ROOT)),
            "reviewDecision": p110_packet["reviewDecision"],
            "validationStatus": p110_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p110_payload["selectedFixture"]),
        "loweringCodegenProposal": proposal,
        "reviewChecks": checks,
        "summary": build_summary(p110_packet, p110_payload, proposal, checks),
        "releaseGates": [
            {"id": "selected_side_effect_lowering_codegen_proposal", "status": "recorded_not_applied"},
            {"id": "private_reviewer_approval", "status": "required_not_recorded"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "generated_fixture_text", "status": "not_produced"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "side_effect_reingest_execution", "status": "not_performed"},
            {"id": "side_effect_memory_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P111 records a selected side-effect lowering/codegen proposal.",
            "The proposal has four scoped pipeline hooks, six approval gates, and five rollback criteria.",
            "P111 does not apply the proposal, produce fixture text, execute generated targets, or install lowering.",
        ],
        "blockedStatements": [
            "The side-effect lowering/codegen proposal has been applied.",
            "An implementation diff has been produced.",
            "Generated side-effect fixture text has been produced.",
            "Generated side-effect target code was executed.",
            "Re-ingested side-effect code was executed.",
            "Side-effect/call/memory lowering is implemented.",
            "Generated side-effect codegen policy is implemented.",
            "Side-effecting calls or memory operations are generally supported.",
            "General branch/control-flow support is established.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Record private reviewer response to the P47-P111 branch/control-flow bundle.",
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
        "title": "FEF-P111 Side-Effect Lowering Codegen Proposal",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_side_effect_lowering_codegen_proposal_not_applied",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected proposal only; no implementation diff, generated fixture text, generated execution, re-ingest execution, side-effect lowering, support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P111 records a selected side-effect lowering/codegen proposal for c_global_state_update_v0.",
            "P110 generated-target runtime remains blocked.",
            "Proposal application is held for a separate approved phase.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p111_side_effect_lowering_codegen_proposal.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p111_side_effect_lowering_codegen_proposal.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p111_side_effect_lowering_codegen_proposal.v0",
        "date": DATE,
        "title": "FEF-P111 Side-Effect Lowering Codegen Proposal",
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
            "# FEF-P111 Side-Effect Lowering Codegen Proposal",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P111 records a selected side-effect lowering/codegen proposal without applying it.",
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
            f"- P110 generated-target gate status: `{summary['p110GeneratedTargetGateStatus']}`",
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
            "- No side-effect lowering/codegen implementation.",
            "- No side-effect/call/memory support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P111 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P111 status")
    p110.validate_payload(read_json(P110_RESULT))
    summary = payload["summary"]
    for key in [
        "p110ValidationPass",
        "p110ClaimFlagsAllFalse",
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
    for key in [
        "proposalApplied",
        "implementationDiffProduced",
        "generatedFixtureTextProduced",
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "installedInForge",
        "installedInEfrog",
        "compilerBehaviorChanged",
        "sideEffectLoweringImplemented",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "sideEffectMemorySupportClaim",
        "sideEffectCodegenPolicyImplemented",
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
    result_path = out_dir / f"fef_p111_side_effect_lowering_codegen_proposal_{STAMP}.json"
    report_path = report_dir / f"fef_p111_side_effect_lowering_codegen_proposal_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p111_side_effect_lowering_codegen_proposal.json"
    feed_path = command_feed_dir / f"fef_p111_side_effect_lowering_codegen_proposal_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p111_side_effect_lowering_codegen_proposal")
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
    print("FEF_P111_SIDE_EFFECT_LOWERING_CODEGEN_PROPOSAL_OK")
    print(f"proposal={built['payload']['summary']['proposalStatus']}")
    print(f"review_checks={built['payload']['summary']['reviewCheckPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
