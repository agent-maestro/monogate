#!/usr/bin/env python3
"""FEF-P120 private reviewer handoff hold gate for the compound-condition ladder."""

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

from scripts import fef_p119_compound_condition_lowering_codegen_proposal as p119  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p120_compound_condition_private_reviewer_handoff_hold_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P120_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"

P119_PACKET = ROOT / "reports/evidence_packets/fef_p119_compound_condition_lowering_codegen_proposal.json"
P119_RESULT = ROOT / "python/results/fef_p119_compound_condition_lowering_codegen_proposal/fef_p119_compound_condition_lowering_codegen_proposal_2026_06_01.json"

CLAIM_FLAGS = {
    "compound_condition_private_reviewer_handoff_claim": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "implementation_change_approved": False,
    "implementation_change_applied": False,
    "implementation_diff_produced": False,
    "generated_fixture_text_produced": False,
    "compound_condition_generated_target_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_codegen_policy_implemented": False,
    "compound_condition_reingest_policy_implemented": False,
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
    "FEF-P120 records a private reviewer handoff hold gate only.",
    "FEF-P120 does not record reviewer approval or rejection.",
    "FEF-P120 does not approve the P119 selected compound-condition lowering/codegen proposal.",
    "FEF-P120 does not apply the P119 proposal or produce source diffs.",
    "FEF-P120 does not produce generated compound-condition fixture text.",
    "FEF-P120 does not execute generated compound-condition target code.",
    "FEF-P120 does not execute re-ingested compound-condition code.",
    "FEF-P120 does not implement short-circuit, predicate-order, or boolean-normalization policy in Forge or eFrog.",
    "FEF-P120 does not implement compound-condition lowering.",
    "FEF-P120 does not implement generated compound-condition codegen or re-ingest policy.",
    "FEF-P120 does not claim compound-condition support.",
    "FEF-P120 does not claim general branch/control-flow support.",
    "FEF-P120 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P120 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle_evidence() -> list[dict[str, str]]:
    return [
        {
            "phase": "P113",
            "decision": "compound_condition_fixture_gate_recorded_support_blocked_review_hold_preserved",
            "purpose": "Compound-condition fixture inventory and selected c_and_guard_return_v0 scope.",
            "reviewFocus": "Confirm compound-condition support starts blocked and reviewer holds are preserved.",
        },
        {
            "phase": "P114",
            "decision": "compound_condition_expected_samples_recorded_support_blocked",
            "purpose": "Expected deterministic source semantics for the selected && fixture.",
            "reviewFocus": "Confirm right-predicate evaluation and short-circuit rows are explicit.",
        },
        {
            "phase": "P115",
            "decision": "compound_condition_policy_specified_not_applied_reference_runtime_eligible_next",
            "purpose": "Selected short-circuit, predicate truth-table, boolean-normalization, and return-path policy.",
            "reviewFocus": "Confirm policy is specified only and not installed.",
        },
        {
            "phase": "P116",
            "decision": "compound_condition_reference_runtime_gate_recorded_support_blocked",
            "purpose": "Modeled reference runtime under P115 policy.",
            "reviewFocus": "Confirm modeled reference agreement and no source/generated execution claim.",
        },
        {
            "phase": "P117",
            "decision": "compound_condition_original_c_runtime_recorded_support_blocked",
            "purpose": "Original C runtime comparison for c_and_guard_return_v0.",
            "reviewFocus": "Confirm seven original C rows pass with exact agreement.",
        },
        {
            "phase": "P118",
            "decision": "compound_condition_generated_target_runtime_gate_blocked",
            "purpose": "Generated-target runtime gate remains blocked until prerequisites are met.",
            "reviewFocus": "Confirm no generated compound-condition target execution has occurred.",
        },
        {
            "phase": "P119",
            "decision": "selected_compound_condition_lowering_codegen_proposal_recorded_not_applied",
            "purpose": "Selected compound-condition lowering/codegen proposal with approval gates and rollback criteria.",
            "reviewFocus": "Confirm proposal is scoped, unapplied, and requires separate approval.",
        },
    ]


def build_reviewer_handoff_packet(p119_payload: dict[str, Any]) -> dict[str, Any]:
    proposal = p119_payload["loweringCodegenProposal"]
    return {
        "handoffStatus": "ready_for_private_review",
        "reviewerDecisionStatus": "not_recorded",
        "reviewSurface": "private_only",
        "implementationStatus": "held_pending_reviewer_response",
        "bundleRange": "P113-P119",
        "heldProposalId": proposal["proposalId"],
        "heldProposalStatus": proposal["status"],
        "allowedPrivateOutcomes": [
            "accept_selected_fixture_only_private_scope",
            "request_copy_tightening",
            "request_generated_fixture_text_before_approval",
            "request_more_compound_condition_fixtures",
            "request_reviewer_hold",
            "request_stronger_reingest_or_short_circuit_policy",
        ],
        "reviewerMustInspect": [
            "P113 fixture inventory and unsupported compound-condition boundary.",
            "P114 expected samples and short-circuit distribution.",
            "P115 specified-not-applied short-circuit/normalization policy.",
            "P116 modeled reference runtime gate.",
            "P117 original C runtime comparison.",
            "P118 generated-target runtime blocker.",
            "P119 proposal hooks, approval gates, rollback criteria, and not-applied status.",
        ],
    }


def build_handoff_checklist() -> list[dict[str, str]]:
    return [
        {"id": "p113_fixture_inventory_reviewed", "status": "ready"},
        {"id": "p114_expected_samples_reviewed", "status": "ready"},
        {"id": "p115_policy_gate_reviewed", "status": "ready"},
        {"id": "p116_reference_runtime_reviewed", "status": "ready"},
        {"id": "p117_original_c_runtime_reviewed", "status": "ready"},
        {"id": "p118_generated_target_blocker_reviewed", "status": "ready"},
        {"id": "p119_proposal_and_rollback_gates_reviewed", "status": "ready"},
    ]


def build_summary(
    p119_packet: dict[str, Any],
    p119_payload: dict[str, Any],
    bundle_evidence: list[dict[str, str]],
    handoff: dict[str, Any],
    checklist: list[dict[str, str]],
) -> dict[str, Any]:
    p119_summary = p119_payload["summary"]
    proposal = p119_payload["loweringCodegenProposal"]
    return {
        "sourcePacketCount": 1,
        "p119ValidationPass": p119_packet["validationStatus"] == "pass",
        "p119ClaimFlagsAllFalse": all(value is False for value in p119_packet["claimFlags"].values()),
        "selectedFixtureId": p119_summary["selectedFixtureId"],
        "selectedFixtureStillBlocked": p119_summary["selectedFixtureStillBlocked"],
        "proposalId": proposal["proposalId"],
        "proposalStatus": proposal["status"],
        "proposalHeld": True,
        "bundleRange": handoff["bundleRange"],
        "bundleEvidenceEntryCount": len(bundle_evidence),
        "handoffChecklistCount": len(checklist),
        "allowedPrivateOutcomeCount": len(handoff["allowedPrivateOutcomes"]),
        "reviewerHandoffReady": handoff["handoffStatus"] == "ready_for_private_review",
        "reviewerDecisionRecorded": False,
        "reviewerDecisionStatus": handoff["reviewerDecisionStatus"],
        "implementationHeldPendingReview": handoff["implementationStatus"] == "held_pending_reviewer_response",
        "implementationApproved": False,
        "implementationApplied": False,
        "implementationDiffProduced": False,
        "generatedFixtureTextProduced": False,
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "compoundConditionLoweringImplemented": False,
        "compoundConditionCodegenPolicyImplemented": False,
        "compoundConditionReingestPolicyImplemented": False,
        "shortCircuitPolicyImplemented": False,
        "booleanNormalizationPolicyImplemented": False,
        "predicateOrderPolicyImplemented": False,
        "compoundConditionSupportClaim": False,
        "p119ReviewCheckCount": p119_summary["reviewCheckCount"],
        "p119ReviewCheckPassCount": p119_summary["reviewCheckPassCount"],
        "p119ReviewCheckFailCount": p119_summary["reviewCheckFailCount"],
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
    p119_packet = read_json(P119_PACKET)
    p119_payload = read_json(P119_RESULT)
    p119.validate_payload(p119_payload)
    bundle_evidence = build_bundle_evidence()
    handoff = build_reviewer_handoff_packet(p119_payload)
    checklist = build_handoff_checklist()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p120-compound-condition-private-reviewer-handoff-hold-gate",
        "decision": "compound_condition_private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "sourcePacket": {
            "phase": "P119",
            "packetPath": str(P119_PACKET.relative_to(ROOT)),
            "resultPath": str(P119_RESULT.relative_to(ROOT)),
            "reviewDecision": p119_packet["reviewDecision"],
            "validationStatus": p119_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p119_payload["selectedFixture"]),
        "reviewerHandoffPacket": handoff,
        "bundleEvidence": bundle_evidence,
        "handoffChecklist": checklist,
        "summary": build_summary(p119_packet, p119_payload, bundle_evidence, handoff, checklist),
        "releaseGates": [
            {"id": "compound_condition_private_reviewer_handoff", "status": "ready"},
            {"id": "reviewer_decision", "status": "not_recorded"},
            {"id": "implementation_change", "status": "held"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "generated_fixture_text", "status": "not_produced"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P120 packages the P113-P119 compound-condition evidence bundle for private review.",
            "P120 marks reviewer response as not recorded.",
            "P120 holds the P119 selected compound-condition lowering/codegen proposal pending reviewer response.",
            "P120 records no approval, rejection, source diff, generated fixture text, generated execution, or re-ingest execution.",
        ],
        "blockedStatements": [
            "A reviewer has approved the P119 compound-condition lowering/codegen proposal.",
            "A reviewer has rejected the P119 compound-condition lowering/codegen proposal.",
            "The implementation change has been approved.",
            "The implementation change has been applied.",
            "An implementation diff has been produced.",
            "Generated compound-condition fixture text has been produced.",
            "Generated compound-condition target code was executed.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit, predicate-order, or boolean-normalization policy is implemented.",
            "Compound-condition lowering is implemented.",
            "Generated compound-condition codegen policy is implemented.",
            "Compound-condition constructs are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
            "Forge/eFrog is public-ready or package-ready.",
        ],
        "nextMilestones": [
            "Record the actual private reviewer response to P113-P120.",
            "If approved, create a separate implementation phase with source diffs and rollback checks.",
            "If held, continue unsupported-form ladders without applying the P119 proposal.",
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
        "title": "FEF-P120 Compound-Condition Private Reviewer Handoff Hold Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "compound_condition_private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private reviewer handoff only; no reviewer decision, approval, rejection, implementation diff, generated fixture text, generated execution, re-ingest execution, compound-condition lowering, support, compiler correctness, formal equivalence, runtime performance, or public readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P120 packages P113-P119 for private review.",
            "Reviewer decision remains not recorded.",
            "P119 proposal remains held and not applied.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p120_compound_condition_private_reviewer_handoff_hold_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p120_compound_condition_private_reviewer_handoff_hold_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p120_compound_condition_private_reviewer_handoff_hold_gate.v0",
        "date": DATE,
        "title": "FEF-P120 Compound-Condition Private Reviewer Handoff Hold Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record actual private reviewer response before implementation posture changes.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    evidence_rows = ["| Phase | Decision | Review focus |", "|---|---|---|"]
    for item in payload["bundleEvidence"]:
        evidence_rows.append(f"| `{item['phase']}` | `{item['decision']}` | {item['reviewFocus']} |")
    checklist_rows = ["| Checklist item | Status |", "|---|---|"]
    for item in payload["handoffChecklist"]:
        checklist_rows.append(f"| `{item['id']}` | `{item['status']}` |")
    return "\n".join(
        [
            "# FEF-P120 Compound-Condition Private Reviewer Handoff Hold Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P120 packages the selected compound-condition ladder for private review and keeps implementation held.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Bundle range: `{summary['bundleRange']}`",
            f"- Bundle evidence entries: `{summary['bundleEvidenceEntryCount']}`",
            f"- Held proposal: `{summary['proposalId']}`",
            f"- Reviewer handoff ready: `{summary['reviewerHandoffReady']}`",
            f"- Reviewer decision status: `{summary['reviewerDecisionStatus']}`",
            f"- Implementation held pending review: `{summary['implementationHeldPendingReview']}`",
            f"- Implementation approved: `{summary['implementationApproved']}`",
            f"- Implementation applied: `{summary['implementationApplied']}`",
            f"- Generated fixture text produced: `{summary['generatedFixtureTextProduced']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Compound-condition lowering implemented: `{summary['compoundConditionLoweringImplemented']}`",
            f"- P119 review checks passing: `{summary['p119ReviewCheckPassCount']}` / `{summary['p119ReviewCheckCount']}`",
            "",
            "## Bundle Evidence",
            "",
            *evidence_rows,
            "",
            "## Handoff Checklist",
            "",
            *checklist_rows,
            "",
            "## Boundary",
            "",
            "- Private reviewer handoff only.",
            "- No reviewer approval or rejection recorded.",
            "- No source diff, generated fixture text, generated execution, or re-ingest execution.",
            "- No compound-condition lowering or support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P120 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P120 status")
    p119.validate_payload(read_json(P119_RESULT))
    summary = payload["summary"]
    for key in [
        "p119ValidationPass",
        "p119ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "proposalHeld",
        "reviewerHandoffReady",
        "implementationHeldPendingReview",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["reviewerDecisionStatus"] != "not_recorded":
        raise ValueError("reviewer decision must remain not recorded")
    if summary["bundleRange"] != "P113-P119":
        raise ValueError("unexpected bundle range")
    if summary["bundleEvidenceEntryCount"] != 7 or summary["handoffChecklistCount"] != 7:
        raise ValueError("expected seven bundle entries and checklist rows")
    if summary["allowedPrivateOutcomeCount"] != 6:
        raise ValueError("expected six allowed private outcomes")
    if summary["p119ReviewCheckCount"] != 12 or summary["p119ReviewCheckFailCount"] != 0:
        raise ValueError("expected twelve passing P119 review checks")
    for key in [
        "reviewerDecisionRecorded",
        "implementationApproved",
        "implementationApplied",
        "implementationDiffProduced",
        "generatedFixtureTextProduced",
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
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
    result_path = out_dir / f"fef_p120_compound_condition_private_reviewer_handoff_hold_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p120_compound_condition_private_reviewer_handoff_hold_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p120_compound_condition_private_reviewer_handoff_hold_gate.json"
    feed_path = command_feed_dir / f"fef_p120_compound_condition_private_reviewer_handoff_hold_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p120_compound_condition_private_reviewer_handoff_hold_gate")
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
    print("FEF_P120_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK")
    print(f"reviewer_decision={built['payload']['summary']['reviewerDecisionStatus']}")
    print(f"bundle_entries={built['payload']['summary']['bundleEvidenceEntryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
