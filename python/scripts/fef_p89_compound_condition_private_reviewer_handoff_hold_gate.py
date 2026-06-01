#!/usr/bin/env python3
"""FEF-P89 private reviewer handoff hold gate for the guarded-div proposal."""

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

from scripts import fef_p88_compound_condition_implementation_change_proposal as p88  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p89_compound_condition_private_reviewer_handoff_hold_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P89_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"

P88_PACKET = ROOT / "reports/evidence_packets/fef_p88_compound_condition_implementation_change_proposal.json"
P88_RESULT = ROOT / "python/results/fef_p88_compound_condition_implementation_change_proposal/fef_p88_compound_condition_implementation_change_proposal_2026_05_31.json"

CLAIM_FLAGS = {
    "private_reviewer_handoff_claim": False,
    "private_reviewer_decision_recorded": False,
    "implementation_change_approved": False,
    "implementation_change_applied": False,
    "guarded_div_source_primitive_installed": False,
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
    "FEF-P89 records a private reviewer handoff hold gate only.",
    "FEF-P89 does not record reviewer approval or rejection.",
    "FEF-P89 does not approve the P88 implementation-change proposal.",
    "FEF-P89 does not apply the P88 implementation-change proposal.",
    "FEF-P89 does not install a guarded-div source primitive in eFrog or Forge.",
    "FEF-P89 does not change eFrog or Forge source code.",
    "FEF-P89 does not execute re-ingested compound-condition code.",
    "FEF-P89 does not claim supported compound-condition re-ingest.",
    "FEF-P89 does not claim compiler-wide short-circuit semantics.",
    "FEF-P89 does not claim compound-condition support.",
    "FEF-P89 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P89 does not claim runtime performance.",
    "FEF-P89 does not claim public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle_evidence() -> list[dict[str, str]]:
    return [
        {
            "phase": "P47-P48",
            "purpose": "Private reviewer bundle index and intake packet.",
            "reviewFocus": "Confirm private-only review surface and no public release approval.",
        },
        {
            "phase": "P51",
            "purpose": "Branch/control-flow blocker gate.",
            "reviewFocus": "Confirm unsupported constructs remain blocked rather than silently supported.",
        },
        {
            "phase": "P57-P58",
            "purpose": "Selected branch closure matrix and private branch gap addendum.",
            "reviewFocus": "Confirm selected closures are not being described as general branch support.",
        },
        {
            "phase": "P59-P61",
            "purpose": "Control-flow IR inventory, schema, and unsupported-construct blocker gate.",
            "reviewFocus": "Confirm IR vocabulary and blocker routing before any implementation claim.",
        },
        {
            "phase": "P70-P73",
            "purpose": "Compound-condition fixture, expected samples, reference runtime, and original C runtime gate.",
            "reviewFocus": "Confirm selected fixture behavior and short-circuit non-evaluation expectations.",
        },
        {
            "phase": "P74-P78",
            "purpose": "Generated-target runtime blocker, lowering rule packet, helper codegen fixture, runtime gate, and re-ingest policy.",
            "reviewFocus": "Confirm generated target evidence stays separate from source-family support.",
        },
        {
            "phase": "P79-P82",
            "purpose": "Re-ingest execution probe plus nonzero, guard-helper, and assignment-normalization adapter probes.",
            "reviewFocus": "Confirm blockers are explicit and adapter probes are not implementation.",
        },
        {
            "phase": "P83-P85",
            "purpose": "Short-circuit execution policy, row-filtered parsed EML execution, and guarded-div source primitive execution.",
            "reviewFocus": "Confirm selected rows preserve zero-denominator and left-false non-evaluation.",
        },
        {
            "phase": "P86-P87",
            "purpose": "Guarded-div installation candidate and fail-closed re-ingest boundary probe.",
            "reviewFocus": "Confirm candidate is uninstalled and actual re-ingest execution remains false.",
        },
        {
            "phase": "P88",
            "purpose": "Implementation-change proposal for selected guarded-div adapter installation.",
            "reviewFocus": "Confirm proposal is scoped, unapplied, and requires separate approval.",
        },
        {
            "phase": "P89",
            "purpose": "Private reviewer handoff hold gate.",
            "reviewFocus": "Confirm reviewer response is not recorded and implementation is held.",
        },
    ]


def build_reviewer_handoff_packet() -> dict[str, Any]:
    return {
        "handoffStatus": "ready_for_private_review",
        "reviewerDecisionStatus": "not_recorded",
        "reviewSurface": "private_only",
        "implementationStatus": "held_pending_reviewer_response",
        "bundleRange": "P47-P88",
        "reviewerMustInspect": [
            "P47/P48 private reviewer bundle and intake boundary.",
            "P51-P61 control-flow IR inventory, schema, and unsupported-construct blocker gate.",
            "P70-P73 selected compound-condition fixture behavior and original C runtime evidence.",
            "P74-P78 generated-target runtime and re-ingest policy boundary.",
            "P79-P82 adapter probe blockers and assignment-normalization limits.",
            "P83-P87 guarded-div execution ladder and fail-closed re-ingest boundary.",
            "P88 proposal gates, rollback criteria, and unapplied implementation status.",
        ],
        "reviewerQuestions": [
            "Is the P88 selected-fixture implementation scope acceptable for a later separate implementation phase?",
            "Should implementation remain held while another unsupported-form ladder is built?",
            "What additional evidence is needed before approving any guarded-div adapter installation?",
            "Which blocked claim is most likely to be misread by a future reviewer?",
            "Should the next artifact record an actual reviewer response or continue private evidence-building?",
        ],
        "allowedReviewerOutcomes": [
            "accept_private_scope_only",
            "approve_separate_implementation_phase",
            "request_proposal_tightening",
            "request_more_non_generated_fixtures",
            "hold_implementation_and_continue_ladder",
        ],
    }


def build_summary(
    p88_packet: dict[str, Any],
    p88_payload: dict[str, Any],
    bundle_evidence: list[dict[str, str]],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p88ValidationPass": p88_packet["validationStatus"] == "pass",
        "p88ClaimFlagsAllFalse": all(value is False for value in p88_packet["claimFlags"].values()),
        "selectedFixtureId": p88_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p88_payload["summary"]["selectedFixtureStillBlocked"],
        "bundleRange": handoff["bundleRange"],
        "bundleEvidenceCount": len(bundle_evidence),
        "reviewerHandoffReady": handoff["handoffStatus"] == "ready_for_private_review",
        "reviewerDecisionRecorded": False,
        "implementationHeldPendingReview": handoff["implementationStatus"] == "held_pending_reviewer_response",
        "implementationChangeApproved": False,
        "implementationChangeApplied": False,
        "implementationDiffProduced": False,
        "actualReingestExecutionPerformed": False,
        "sourcePrimitiveInstalled": False,
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
    p88_packet = read_json(P88_PACKET)
    p88_payload = read_json(P88_RESULT)
    p88.validate_payload(p88_payload)
    bundle_evidence = build_bundle_evidence()
    handoff = build_reviewer_handoff_packet()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p89-compound-condition-private-reviewer-handoff-hold-gate",
        "decision": "private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "sourcePacket": {
            "phase": "P88",
            "packetPath": str(P88_PACKET.relative_to(ROOT)),
            "resultPath": str(P88_RESULT.relative_to(ROOT)),
            "reviewDecision": p88_packet["reviewDecision"],
            "validationStatus": p88_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p88_payload["selectedFixture"]),
        "reviewerHandoffPacket": handoff,
        "bundleEvidence": bundle_evidence,
        "handoffChecklist": [
            {
                "id": "send_p47_p88_bundle",
                "status": "ready",
                "instruction": "Send the private P47-P88 evidence bundle to the reviewer.",
            },
            {
                "id": "inspect_p88_proposal",
                "status": "ready",
                "instruction": "Ask the reviewer to inspect the P88 proposal scope, gates, and rollback criteria.",
            },
            {
                "id": "collect_reviewer_decision",
                "status": "pending_human",
                "instruction": "Record a real reviewer response in a later packet before implementation posture changes.",
            },
            {
                "id": "keep_implementation_held",
                "status": "required",
                "instruction": "Do not install guarded-div behavior or execute re-ingested code from this handoff.",
            },
            {
                "id": "preserve_claim_boundary",
                "status": "required",
                "instruction": "Keep support, correctness, equivalence, performance, package, checkout, and public claims false.",
            },
        ],
        "summary": build_summary(p88_packet, p88_payload, bundle_evidence, handoff),
        "releaseGates": [
            {"id": "private_reviewer_handoff", "status": "ready"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "implementation_change_approval", "status": "blocked_pending_reviewer"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "actual_reingest_execution", "status": "blocked_not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P89 packages the P47-P88 branch/control-flow evidence bundle for private review.",
            "P89 marks reviewer response as not recorded.",
            "P89 holds the P88 implementation proposal pending reviewer response.",
            "P89 records no source diff, installed primitive, or actual re-ingest execution.",
        ],
        "blockedStatements": [
            "A reviewer has approved the P88 proposal.",
            "A reviewer has rejected the P88 proposal.",
            "The implementation change has been approved.",
            "The implementation change has been applied.",
            "The guarded-div primitive is installed in eFrog or Forge.",
            "Re-ingested compound-condition code executed successfully.",
            "Compound-condition re-ingest is supported.",
            "The selected proposal proves compiler-wide short-circuit semantics.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
            "Forge/eFrog is public-ready or package-ready.",
        ],
        "nextMilestones": [
            "Record the actual private reviewer response to P47-P89.",
            "If approved, create a separate implementation phase with source diffs and rollback checks.",
            "If held, move to the next unsupported-form ladder without applying the P88 proposal.",
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
        "title": "FEF-P89 Compound-Condition Private Reviewer Handoff Hold Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private reviewer handoff hold gate only; no reviewer decision, implementation approval, applied source diff, installed eFrog/Forge behavior change, actual re-ingest execution, compound-condition support, compiler correctness, formal equivalence, runtime performance, package, checkout, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P89 packages P47-P88 for private review.",
            "Reviewer response is explicitly not recorded.",
            "The P88 implementation proposal remains held and unapplied.",
            "All support/correctness/performance/public claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p89_compound_condition_private_reviewer_handoff_hold_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p89_compound_condition_private_reviewer_handoff_hold_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p89_compound_condition_private_reviewer_handoff_hold_gate.v0",
        "date": DATE,
        "title": "FEF-P89 Compound-Condition Private Reviewer Handoff Hold Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record the actual private reviewer response, or hold and move to the next unsupported-form ladder.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    handoff = payload["reviewerHandoffPacket"]
    bundle_rows = [
        "| Phase | Purpose | Review Focus |",
        "|---|---|---|",
    ]
    for item in payload["bundleEvidence"]:
        bundle_rows.append(f"| `{item['phase']}` | {item['purpose']} | {item['reviewFocus']} |")
    checklist_rows = [
        "| Checklist Item | Status | Instruction |",
        "|---|---|---|",
    ]
    for item in payload["handoffChecklist"]:
        checklist_rows.append(f"| `{item['id']}` | `{item['status']}` | {item['instruction']} |")
    return "\n".join(
        [
            "# FEF-P89 Compound-Condition Private Reviewer Handoff Hold Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P89 packages the P47-P88 evidence bundle for private review and keeps implementation held.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Bundle range: `{summary['bundleRange']}`",
            f"- Bundle evidence rows: `{summary['bundleEvidenceCount']}`",
            f"- Reviewer handoff ready: `{summary['reviewerHandoffReady']}`",
            f"- Reviewer decision recorded: `{summary['reviewerDecisionRecorded']}`",
            f"- Implementation held pending review: `{summary['implementationHeldPendingReview']}`",
            f"- Implementation approved: `{summary['implementationChangeApproved']}`",
            f"- Implementation applied: `{summary['implementationChangeApplied']}`",
            f"- Actual re-ingest execution performed: `{summary['actualReingestExecutionPerformed']}`",
            "",
            "## Reviewer Handoff",
            "",
            f"- Handoff status: `{handoff['handoffStatus']}`",
            f"- Reviewer decision status: `{handoff['reviewerDecisionStatus']}`",
            f"- Review surface: `{handoff['reviewSurface']}`",
            f"- Implementation status: `{handoff['implementationStatus']}`",
            "",
            "## Reviewer Must Inspect",
            "",
            *[f"- {item}" for item in handoff["reviewerMustInspect"]],
            "",
            "## Reviewer Questions",
            "",
            *[f"- {item}" for item in handoff["reviewerQuestions"]],
            "",
            "## Allowed Reviewer Outcomes",
            "",
            *[f"- `{item}`" for item in handoff["allowedReviewerOutcomes"]],
            "",
            "## Bundle Evidence",
            "",
            *bundle_rows,
            "",
            "## Handoff Checklist",
            "",
            *checklist_rows,
            "",
            "## Boundary",
            "",
            "- Private reviewer handoff only.",
            "- No reviewer decision recorded.",
            "- No implementation approval or applied source diff.",
            "- No installed guarded-div primitive.",
            "- No actual re-ingest execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, runtime-performance, package, checkout, public-readiness, or production claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P89 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P89 status")
    p88.validate_payload(read_json(P88_RESULT))
    summary = payload["summary"]
    for key in [
        "p88ValidationPass",
        "p88ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "reviewerHandoffReady",
        "implementationHeldPendingReview",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if payload["reviewerHandoffPacket"]["reviewerDecisionStatus"] != "not_recorded":
        raise ValueError("reviewer decision must be not_recorded")
    if payload["reviewerHandoffPacket"]["implementationStatus"] != "held_pending_reviewer_response":
        raise ValueError("implementation must remain held")
    if summary["bundleRange"] != "P47-P88":
        raise ValueError("unexpected handoff bundle range")
    if summary["bundleEvidenceCount"] != 11:
        raise ValueError("expected eleven bundle evidence rows")
    for key in [
        "reviewerDecisionRecorded",
        "implementationChangeApproved",
        "implementationChangeApplied",
        "implementationDiffProduced",
        "actualReingestExecutionPerformed",
        "sourcePrimitiveInstalled",
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
        "private_reviewer_handoff": "ready",
        "private_reviewer_decision": "not_recorded",
        "implementation_change_approval": "blocked_pending_reviewer",
        "implementation_diff": "not_produced",
        "actual_reingest_execution": "blocked_not_performed",
        "compound_condition_support": "blocked",
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
    result_path = out_dir / f"fef_p89_compound_condition_private_reviewer_handoff_hold_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p89_compound_condition_private_reviewer_handoff_hold_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p89_compound_condition_private_reviewer_handoff_hold_gate.json"
    feed_path = command_feed_dir / f"fef_p89_compound_condition_private_reviewer_handoff_hold_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p89_compound_condition_private_reviewer_handoff_hold_gate")
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
    print("FEF_P89_COMPOUND_CONDITION_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK")
    print(f"handoff_ready={built['payload']['summary']['reviewerHandoffReady']}")
    print(f"reviewer_decision_recorded={built['payload']['summary']['reviewerDecisionRecorded']}")
    print(f"implementation_held={built['payload']['summary']['implementationHeldPendingReview']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
