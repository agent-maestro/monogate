#!/usr/bin/env python3
"""FEF-P104 private reviewer handoff hold gate for the selected loop adapter."""

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

from scripts import fef_p103_loop_helper_adapter_installation_candidate as p103  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p104_loop_private_reviewer_handoff_hold_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P104_LOOP_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"

P103_PACKET = ROOT / "reports/evidence_packets/fef_p103_loop_helper_adapter_installation_candidate.json"
P103_RESULT = ROOT / "python/results/fef_p103_loop_helper_adapter_installation_candidate/fef_p103_loop_helper_adapter_installation_candidate_2026_05_31.json"

CLAIM_FLAGS = {
    "private_reviewer_handoff_claim": False,
    "private_reviewer_decision_recorded": False,
    "implementation_change_approved": False,
    "implementation_change_applied": False,
    "loop_helper_adapter_installed": False,
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
    "FEF-P104 records a private reviewer handoff hold gate only.",
    "FEF-P104 does not record reviewer approval or rejection.",
    "FEF-P104 does not approve the P103 selected loop helper adapter candidate.",
    "FEF-P104 does not apply the P103 candidate or produce source diffs.",
    "FEF-P104 does not install the selected loop helper adapter in eFrog or Forge.",
    "FEF-P104 does not execute a Forge-recompiled Python target.",
    "FEF-P104 does not claim supported loop re-ingest.",
    "FEF-P104 does not install loop lowering in Forge or eFrog.",
    "FEF-P104 does not claim loop/back-edge support.",
    "FEF-P104 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P104 does not claim runtime performance.",
    "FEF-P104 does not claim public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle_evidence() -> list[dict[str, str]]:
    return [
        {
            "phase": "P90-P92",
            "purpose": "Loop/back-edge fixture gate, expected samples, and selected boundedness policy.",
            "reviewFocus": "Confirm loop support starts blocked and P92 remains selected-fixture-only.",
        },
        {
            "phase": "P93-P94",
            "purpose": "Reference runtime and original C runtime gates for c_while_accumulate_v0.",
            "reviewFocus": "Confirm selected source semantics before generated-target work.",
        },
        {
            "phase": "P95-P98",
            "purpose": "Generated-target blocker, lowering rule packet, codegen fixture, and generated C runtime gate.",
            "reviewFocus": "Confirm generated runtime evidence is selected and does not install lowering.",
        },
        {
            "phase": "P99-P100",
            "purpose": "Selected re-ingest policy and fail-closed eFrog re-ingest execution probe.",
            "reviewFocus": "Confirm helper-call blocker is explicit and no re-ingested execution occurs.",
        },
        {
            "phase": "P101-P102",
            "purpose": "Selected helper adapter parse probe and parsed-EML-shaped Python comparison.",
            "reviewFocus": "Confirm P101 parses after local adapter and P102 comparison stays non-installed.",
        },
        {
            "phase": "P103",
            "purpose": "Selected loop helper adapter installation candidate.",
            "reviewFocus": "Confirm candidate is scoped, unapplied, and requires separate approval.",
        },
    ]


def build_reviewer_handoff_packet() -> dict[str, Any]:
    return {
        "handoffStatus": "ready_for_private_review",
        "reviewerDecisionStatus": "not_recorded",
        "reviewSurface": "private_only",
        "implementationStatus": "held_pending_reviewer_response",
        "bundleRange": "P90-P103",
        "reviewerMustInspect": [
            "P90-P92 loop fixture scope, expected samples, and selected boundedness policy.",
            "P93-P94 reference/original C runtime evidence.",
            "P95-P98 generated-target blocker, lowering rule, codegen fixture, and generated C runtime evidence.",
            "P99-P100 selected re-ingest policy and fail-closed helper-call blocker.",
            "P101-P102 selected helper adapter parse and parsed-EML comparison evidence.",
            "P103 candidate hooks, approval gates, rollback criteria, and unapplied status.",
        ],
        "reviewerQuestions": [
            "Is the P103 selected-fixture installation scope acceptable for a later separate implementation phase?",
            "Should the loop helper adapter remain held while another unsupported-form ladder is built?",
            "What extra evidence is needed before approving any adapter installation?",
            "Which blocked loop/back-edge claim is most likely to be misread by a future reviewer?",
            "Should the next artifact record an actual reviewer response or continue private evidence-building?",
        ],
        "allowedReviewerOutcomes": [
            "accept_private_scope_only",
            "approve_separate_implementation_phase",
            "request_candidate_tightening",
            "request_more_loop_fixtures",
            "hold_implementation_and_continue_ladder",
        ],
    }


def build_summary(
    p103_packet: dict[str, Any],
    p103_payload: dict[str, Any],
    bundle_evidence: list[dict[str, str]],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p103ValidationPass": p103_packet["validationStatus"] == "pass",
        "p103ClaimFlagsAllFalse": all(value is False for value in p103_packet["claimFlags"].values()),
        "selectedFixtureId": p103_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p103_payload["summary"]["selectedFixtureStillBlocked"],
        "bundleRange": handoff["bundleRange"],
        "bundleEvidenceCount": len(bundle_evidence),
        "reviewerQuestionCount": len(handoff["reviewerQuestions"]),
        "allowedReviewerOutcomeCount": len(handoff["allowedReviewerOutcomes"]),
        "reviewerHandoffReady": handoff["handoffStatus"] == "ready_for_private_review",
        "reviewerDecisionRecorded": False,
        "implementationHeldPendingReview": handoff["implementationStatus"] == "held_pending_reviewer_response",
        "implementationChangeApproved": False,
        "implementationChangeApplied": False,
        "implementationDiffProduced": False,
        "actualReingestExecutionPerformed": False,
        "loopHelperAdapterInstalled": False,
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
    p103_packet = read_json(P103_PACKET)
    p103_payload = read_json(P103_RESULT)
    p103.validate_payload(p103_payload)
    bundle_evidence = build_bundle_evidence()
    handoff = build_reviewer_handoff_packet()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p104-loop-private-reviewer-handoff-hold-gate",
        "decision": "loop_private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "sourcePacket": {
            "phase": "P103",
            "packetPath": str(P103_PACKET.relative_to(ROOT)),
            "resultPath": str(P103_RESULT.relative_to(ROOT)),
            "reviewDecision": p103_packet["reviewDecision"],
            "validationStatus": p103_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p103_payload["selectedFixture"]),
        "reviewerHandoffPacket": handoff,
        "bundleEvidence": bundle_evidence,
        "handoffChecklist": [
            {
                "id": "send_p90_p103_bundle",
                "status": "ready",
                "instruction": "Send the private P90-P103 loop evidence bundle to the reviewer.",
            },
            {
                "id": "inspect_p103_candidate",
                "status": "ready",
                "instruction": "Ask the reviewer to inspect the P103 candidate hooks, gates, and rollback criteria.",
            },
            {
                "id": "collect_reviewer_decision",
                "status": "pending_human",
                "instruction": "Record a real reviewer response in a later packet before implementation posture changes.",
            },
            {
                "id": "keep_implementation_held",
                "status": "required",
                "instruction": "Do not install loop helper adapter behavior or execute recompiled targets from this handoff.",
            },
            {
                "id": "preserve_claim_boundary",
                "status": "required",
                "instruction": "Keep support, correctness, equivalence, performance, package, checkout, and public claims false.",
            },
        ],
        "summary": build_summary(p103_packet, p103_payload, bundle_evidence, handoff),
        "releaseGates": [
            {"id": "private_reviewer_handoff", "status": "ready"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "implementation_change_approval", "status": "blocked_pending_reviewer"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "actual_reingest_execution", "status": "blocked_not_performed"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P104 packages the P90-P103 loop/back-edge evidence bundle for private review.",
            "P104 marks reviewer response as not recorded.",
            "P104 holds the P103 selected loop helper adapter candidate pending reviewer response.",
            "P104 records no source diff, installed adapter, or Forge-recompiled Python target execution.",
        ],
        "blockedStatements": [
            "A reviewer has approved the P103 candidate.",
            "A reviewer has rejected the P103 candidate.",
            "The implementation change has been approved.",
            "The implementation change has been applied.",
            "The selected loop helper adapter is installed in eFrog or Forge.",
            "A Forge-recompiled Python target was executed.",
            "Loop re-ingest is supported.",
            "Loop lowering is implemented.",
            "Loop/back-edge constructs are supported.",
            "The P92 boundedness policy is a general loop policy.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
            "Forge/eFrog is public-ready or package-ready.",
        ],
        "nextMilestones": [
            "Record the actual private reviewer response to P90-P104.",
            "If approved, create a separate implementation phase with source diffs and rollback checks.",
            "If held, continue the unsupported-form ladders without applying the P103 candidate.",
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
        "title": "FEF-P104 Loop Private Reviewer Handoff Hold Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private reviewer handoff only; no reviewer decision, implementation approval, source diff, adapter installation, recompiled target execution, loop/back-edge support, compiler correctness, formal equivalence, runtime performance, or public readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P104 packages P90-P103 for private review.",
            "Reviewer decision remains not recorded.",
            "P103 candidate implementation is held pending a real reviewer response.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p104_loop_private_reviewer_handoff_hold_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p104_loop_private_reviewer_handoff_hold_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p104_loop_private_reviewer_handoff_hold_gate.v0",
        "date": DATE,
        "title": "FEF-P104 Loop Private Reviewer Handoff Hold Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record actual private reviewer response before implementation posture changes.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    evidence_rows = ["| Phase | Review focus |", "|---|---|"]
    for item in payload["bundleEvidence"]:
        evidence_rows.append(f"| `{item['phase']}` | {item['reviewFocus']} |")
    return "\n".join(
        [
            "# FEF-P104 Loop Private Reviewer Handoff Hold Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P104 packages the selected loop helper adapter ladder for private review and keeps implementation held.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Bundle range: `{summary['bundleRange']}`",
            f"- Bundle evidence entries: `{summary['bundleEvidenceCount']}`",
            f"- Reviewer handoff ready: `{summary['reviewerHandoffReady']}`",
            f"- Reviewer decision recorded: `{summary['reviewerDecisionRecorded']}`",
            f"- Implementation held pending review: `{summary['implementationHeldPendingReview']}`",
            f"- Implementation approved: `{summary['implementationChangeApproved']}`",
            f"- Implementation applied: `{summary['implementationChangeApplied']}`",
            f"- Loop helper adapter installed: `{summary['loopHelperAdapterInstalled']}`",
            f"- Loop re-ingest supported: `{summary['loopReingestSupported']}`",
            "",
            "## Bundle Evidence",
            "",
            *evidence_rows,
            "",
            "## Boundary",
            "",
            "- Private reviewer handoff only.",
            "- No reviewer approval or rejection recorded.",
            "- No source diff or installed adapter.",
            "- No Forge-recompiled Python target execution.",
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P104 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P104 status")
    p103.validate_payload(read_json(P103_RESULT))
    summary = payload["summary"]
    for key in [
        "p103ValidationPass",
        "p103ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "reviewerHandoffReady",
        "implementationHeldPendingReview",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["bundleRange"] != "P90-P103":
        raise ValueError("unexpected bundle range")
    if summary["bundleEvidenceCount"] != 6:
        raise ValueError("expected six bundle evidence entries")
    if summary["reviewerQuestionCount"] != 5 or summary["allowedReviewerOutcomeCount"] != 5:
        raise ValueError("expected five reviewer questions and outcomes")
    for key in [
        "reviewerDecisionRecorded",
        "implementationChangeApproved",
        "implementationChangeApplied",
        "implementationDiffProduced",
        "actualReingestExecutionPerformed",
        "loopHelperAdapterInstalled",
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
    result_path = out_dir / f"fef_p104_loop_private_reviewer_handoff_hold_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p104_loop_private_reviewer_handoff_hold_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p104_loop_private_reviewer_handoff_hold_gate.json"
    feed_path = command_feed_dir / f"fef_p104_loop_private_reviewer_handoff_hold_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p104_loop_private_reviewer_handoff_hold_gate")
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
    print("FEF_P104_LOOP_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK")
    print(f"bundle={built['payload']['summary']['bundleRange']}")
    print(f"decision_recorded={built['payload']['summary']['reviewerDecisionRecorded']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
