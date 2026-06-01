#!/usr/bin/env python3
"""FEF-P112 private reviewer handoff hold gate for the side-effect ladder."""

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

from scripts import fef_p111_side_effect_lowering_codegen_proposal as p111  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p112_side_effect_private_reviewer_handoff_hold_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P112_SIDE_EFFECT_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"

P111_PACKET = ROOT / "reports/evidence_packets/fef_p111_side_effect_lowering_codegen_proposal.json"
P111_RESULT = ROOT / "python/results/fef_p111_side_effect_lowering_codegen_proposal/fef_p111_side_effect_lowering_codegen_proposal_2026_06_01.json"

CLAIM_FLAGS = {
    "side_effect_private_reviewer_handoff_claim": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "implementation_change_approved": False,
    "implementation_change_applied": False,
    "implementation_diff_produced": False,
    "generated_fixture_text_produced": False,
    "generated_target_execution_claim": False,
    "reingest_execution_claim": False,
    "live_external_call_claim": False,
    "unbounded_memory_mutation_claim": False,
    "side_effect_lowering_implemented": False,
    "side_effect_codegen_policy_implemented": False,
    "side_effect_reingest_policy_implemented": False,
    "side_effect_memory_support_claim": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
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
    "FEF-P112 records a private reviewer handoff hold gate only.",
    "FEF-P112 does not record reviewer approval or rejection.",
    "FEF-P112 does not approve the P111 selected side-effect lowering/codegen proposal.",
    "FEF-P112 does not apply the P111 proposal or produce source diffs.",
    "FEF-P112 does not produce generated side-effect fixture text.",
    "FEF-P112 does not execute generated side-effect target code.",
    "FEF-P112 does not execute re-ingested side-effect code.",
    "FEF-P112 does not perform live external calls.",
    "FEF-P112 does not perform unbounded memory mutation or aliasing.",
    "FEF-P112 does not implement side-effect/call/memory lowering.",
    "FEF-P112 does not implement generated side-effect codegen or re-ingest policy.",
    "FEF-P112 does not claim side-effect/call/memory support.",
    "FEF-P112 does not claim general branch/control-flow support.",
    "FEF-P112 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P112 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle_evidence() -> list[dict[str, str]]:
    return [
        {
            "phase": "P105",
            "decision": "side_effect_memory_fixture_gate_recorded_support_blocked_review_hold_preserved",
            "purpose": "Side-effect/call/memory fixture inventory and selected c_global_state_update_v0 scope.",
            "reviewFocus": "Confirm side-effect support starts blocked and reviewer hold is preserved.",
        },
        {
            "phase": "P106",
            "decision": "side_effect_expected_samples_recorded_support_blocked",
            "purpose": "Expected deterministic sample behavior for the selected side-effect fixture.",
            "reviewFocus": "Confirm expected state updates and blocked invalid support claims.",
        },
        {
            "phase": "P107",
            "decision": "side_effect_policy_specified_not_applied_reference_runtime_eligible_next",
            "purpose": "Selected side-effect policy for deterministic stub calls and bounded state cells.",
            "reviewFocus": "Confirm policy is specified only and not installed.",
        },
        {
            "phase": "P108",
            "decision": "side_effect_reference_runtime_gate_recorded_support_blocked",
            "purpose": "Modeled reference runtime gate for selected side-effect behavior.",
            "reviewFocus": "Confirm reference runtime evidence exists before original C comparison.",
        },
        {
            "phase": "P109",
            "decision": "side_effect_original_c_stubbed_runtime_gate_recorded_support_blocked",
            "purpose": "Original C stubbed runtime comparison for c_global_state_update_v0.",
            "reviewFocus": "Confirm deterministic stub-call/state-write counts and exact agreement.",
        },
        {
            "phase": "P110",
            "decision": "side_effect_generated_target_runtime_gate_blocked",
            "purpose": "Generated-target runtime gate remains blocked until prerequisites are met.",
            "reviewFocus": "Confirm no generated side-effect target execution has occurred.",
        },
        {
            "phase": "P111",
            "decision": "selected_side_effect_lowering_codegen_proposal_recorded_not_applied",
            "purpose": "Selected side-effect lowering/codegen proposal with approval gates and rollback criteria.",
            "reviewFocus": "Confirm proposal is scoped, unapplied, and requires separate approval.",
        },
    ]


def build_reviewer_handoff_packet(p111_payload: dict[str, Any]) -> dict[str, Any]:
    proposal = p111_payload["loweringCodegenProposal"]
    return {
        "handoffStatus": "ready_for_private_review",
        "reviewerDecisionStatus": "not_recorded",
        "reviewSurface": "private_only",
        "implementationStatus": "held_pending_reviewer_response",
        "bundleRange": "P105-P111",
        "heldProposalId": proposal["proposalId"],
        "heldProposalStatus": proposal["status"],
        "allowedPrivateOutcomes": [
            "accept_selected_fixture_only_private_scope",
            "request_copy_tightening",
            "request_generated_fixture_text_before_approval",
            "request_more_side_effect_memory_fixtures",
            "request_reviewer_hold",
            "request_stronger_alias_external_call_policy",
        ],
        "reviewerMustInspect": [
            "P105 fixture inventory and unsupported side-effect/memory boundary.",
            "P106 expected deterministic samples.",
            "P107 side-effect policy specification and not-applied status.",
            "P108 modeled reference runtime gate.",
            "P109 original C stubbed runtime comparison.",
            "P110 generated-target runtime blocker.",
            "P111 proposal hooks, approval gates, rollback criteria, and not-applied status.",
        ],
    }


def build_handoff_checklist() -> list[dict[str, str]]:
    return [
        {"id": "p105_fixture_inventory_reviewed", "status": "ready"},
        {"id": "p106_expected_samples_reviewed", "status": "ready"},
        {"id": "p107_policy_gate_reviewed", "status": "ready"},
        {"id": "p108_reference_runtime_reviewed", "status": "ready"},
        {"id": "p109_original_c_stubbed_runtime_reviewed", "status": "ready"},
        {"id": "p110_generated_target_blocker_reviewed", "status": "ready"},
        {"id": "p111_proposal_and_rollback_gates_reviewed", "status": "ready"},
    ]


def build_summary(
    p111_packet: dict[str, Any],
    p111_payload: dict[str, Any],
    bundle_evidence: list[dict[str, str]],
    handoff: dict[str, Any],
    checklist: list[dict[str, str]],
) -> dict[str, Any]:
    p111_summary = p111_payload["summary"]
    proposal = p111_payload["loweringCodegenProposal"]
    return {
        "sourcePacketCount": 1,
        "p111ValidationPass": p111_packet["validationStatus"] == "pass",
        "p111ClaimFlagsAllFalse": all(value is False for value in p111_packet["claimFlags"].values()),
        "selectedFixtureId": p111_summary["selectedFixtureId"],
        "selectedFixtureStillBlocked": p111_summary["selectedFixtureStillBlocked"],
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
        "sideEffectLoweringImplemented": False,
        "sideEffectCodegenPolicyImplemented": False,
        "sideEffectReingestPolicyImplemented": False,
        "sideEffectMemorySupportClaim": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "liveExternalCallClaim": False,
        "unboundedMemoryMutationClaim": False,
        "p111ReviewCheckCount": p111_summary["reviewCheckCount"],
        "p111ReviewCheckPassCount": p111_summary["reviewCheckPassCount"],
        "p111ReviewCheckFailCount": p111_summary["reviewCheckFailCount"],
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
    p111_packet = read_json(P111_PACKET)
    p111_payload = read_json(P111_RESULT)
    p111.validate_payload(p111_payload)
    bundle_evidence = build_bundle_evidence()
    handoff = build_reviewer_handoff_packet(p111_payload)
    checklist = build_handoff_checklist()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p112-side-effect-private-reviewer-handoff-hold-gate",
        "decision": "side_effect_private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "sourcePacket": {
            "phase": "P111",
            "packetPath": str(P111_PACKET.relative_to(ROOT)),
            "resultPath": str(P111_RESULT.relative_to(ROOT)),
            "reviewDecision": p111_packet["reviewDecision"],
            "validationStatus": p111_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p111_payload["selectedFixture"]),
        "reviewerHandoffPacket": handoff,
        "bundleEvidence": bundle_evidence,
        "handoffChecklist": checklist,
        "summary": build_summary(p111_packet, p111_payload, bundle_evidence, handoff, checklist),
        "releaseGates": [
            {"id": "side_effect_private_reviewer_handoff", "status": "ready"},
            {"id": "reviewer_decision", "status": "not_recorded"},
            {"id": "implementation_change", "status": "held"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "generated_fixture_text", "status": "not_produced"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "side_effect_reingest_execution", "status": "not_performed"},
            {"id": "side_effect_lowering", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P112 packages the P105-P111 side-effect/call/memory evidence bundle for private review.",
            "P112 marks reviewer response as not recorded.",
            "P112 holds the P111 selected side-effect lowering/codegen proposal pending reviewer response.",
            "P112 records no approval, rejection, source diff, generated fixture text, generated execution, or re-ingest execution.",
        ],
        "blockedStatements": [
            "A reviewer has approved the P111 side-effect lowering/codegen proposal.",
            "A reviewer has rejected the P111 side-effect lowering/codegen proposal.",
            "The implementation change has been approved.",
            "The implementation change has been applied.",
            "An implementation diff has been produced.",
            "Generated side-effect fixture text has been produced.",
            "Generated side-effect target code was executed.",
            "Re-ingested side-effect code was executed.",
            "Side-effect/call/memory lowering is implemented.",
            "Generated side-effect codegen policy is implemented.",
            "Side-effecting calls or memory operations are generally supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
            "Forge/eFrog is public-ready or package-ready.",
        ],
        "nextMilestones": [
            "Record the actual private reviewer response to P105-P112.",
            "If approved, create a separate implementation phase with source diffs and rollback checks.",
            "If held, continue unsupported-form ladders without applying the P111 proposal.",
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
        "title": "FEF-P112 Side-Effect Private Reviewer Handoff Hold Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "side_effect_private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private reviewer handoff only; no reviewer decision, approval, rejection, implementation diff, generated fixture text, generated execution, re-ingest execution, side-effect lowering, support, compiler correctness, formal equivalence, runtime performance, or public readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P112 packages P105-P111 for private review.",
            "Reviewer decision remains not recorded.",
            "P111 proposal remains held and not applied.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p112_side_effect_private_reviewer_handoff_hold_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p112_side_effect_private_reviewer_handoff_hold_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p112_side_effect_private_reviewer_handoff_hold_gate.v0",
        "date": DATE,
        "title": "FEF-P112 Side-Effect Private Reviewer Handoff Hold Gate",
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
            "# FEF-P112 Side-Effect Private Reviewer Handoff Hold Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P112 packages the selected side-effect/call/memory ladder for private review and keeps implementation held.",
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
            f"- Side-effect lowering implemented: `{summary['sideEffectLoweringImplemented']}`",
            f"- P111 review checks passing: `{summary['p111ReviewCheckPassCount']}` / `{summary['p111ReviewCheckCount']}`",
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
            "- No side-effect/call/memory lowering or support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P112 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P112 status")
    p111.validate_payload(read_json(P111_RESULT))
    summary = payload["summary"]
    for key in [
        "p111ValidationPass",
        "p111ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "proposalHeld",
        "reviewerHandoffReady",
        "implementationHeldPendingReview",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["bundleRange"] != "P105-P111":
        raise ValueError("unexpected bundle range")
    if summary["bundleEvidenceEntryCount"] != 7:
        raise ValueError("expected seven bundle evidence entries")
    if summary["handoffChecklistCount"] != 7:
        raise ValueError("expected seven handoff checklist entries")
    if summary["allowedPrivateOutcomeCount"] != 6:
        raise ValueError("expected six allowed private outcomes")
    if summary["reviewerDecisionStatus"] != "not_recorded":
        raise ValueError("reviewer decision status must remain not_recorded")
    if summary["proposalStatus"] != "proposal_recorded_not_applied":
        raise ValueError("proposal must remain not applied")
    if summary["p111ReviewCheckCount"] != 12 or summary["p111ReviewCheckFailCount"] != 0:
        raise ValueError("expected twelve passing P111 review checks")
    for key in [
        "reviewerDecisionRecorded",
        "implementationApproved",
        "implementationApplied",
        "implementationDiffProduced",
        "generatedFixtureTextProduced",
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "sideEffectLoweringImplemented",
        "sideEffectCodegenPolicyImplemented",
        "sideEffectReingestPolicyImplemented",
        "sideEffectMemorySupportClaim",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "liveExternalCallClaim",
        "unboundedMemoryMutationClaim",
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
    result_path = out_dir / f"fef_p112_side_effect_private_reviewer_handoff_hold_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p112_side_effect_private_reviewer_handoff_hold_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p112_side_effect_private_reviewer_handoff_hold_gate.json"
    feed_path = command_feed_dir / f"fef_p112_side_effect_private_reviewer_handoff_hold_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p112_side_effect_private_reviewer_handoff_hold_gate")
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
    print("FEF_P112_SIDE_EFFECT_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK")
    print(f"bundle={built['payload']['summary']['bundleRange']}")
    print(f"decision_status={built['payload']['summary']['reviewerDecisionStatus']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
