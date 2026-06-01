#!/usr/bin/env python3
"""FEF-P128 private reviewer handoff hold gate for the source-preserving ladder."""

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

from scripts import fef_p127_rust_early_return_source_order_checker as p127  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p128_source_preserving_private_reviewer_handoff_hold_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P128_SOURCE_PRESERVING_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_PASS"

P127_PACKET = ROOT / "reports/evidence_packets/fef_p127_rust_early_return_source_order_checker.json"
P127_RESULT = ROOT / "python/results/fef_p127_rust_early_return_source_order_checker/fef_p127_rust_early_return_source_order_checker_2026_06_01.json"

CLAIM_FLAGS = {
    "source_preserving_private_reviewer_handoff_claim": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "implementation_change_approved": False,
    "implementation_change_applied": False,
    "implementation_diff_produced": False,
    "source_parser_executed": False,
    "source_reemitter_executed": False,
    "preservation_oracle_executed": False,
    "source_fidelity_validated": False,
    "source_preserving_roundtrip_support_claim": False,
    "non_generated_source_roundtrip_claim": False,
    "full_non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "arbitrary_source_family_claim": False,
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
    "FEF-P128 records a private reviewer handoff hold gate only.",
    "FEF-P128 does not record reviewer approval or rejection.",
    "FEF-P128 does not approve source-preserving roundtrip implementation.",
    "FEF-P128 does not apply source parser or re-emitter changes.",
    "FEF-P128 does not run a preservation oracle.",
    "FEF-P128 does not validate token, whitespace, comment, formatting, or source-layout fidelity.",
    "FEF-P128 does not execute source, generated, or re-ingested code.",
    "FEF-P128 does not implement source-preserving roundtrip support.",
    "FEF-P128 does not widen Forge or eFrog frontend lowering.",
    "FEF-P128 does not apply held P111 or P119 proposals.",
    "FEF-P128 does not claim general branch/control-flow support.",
    "FEF-P128 does not claim full non-generated source roundtrip.",
    "FEF-P128 does not claim arbitrary C/Rust source-family support.",
    "FEF-P128 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P128 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle_evidence() -> list[dict[str, Any]]:
    return [
        {
            "phase": "P121",
            "decision": "source_preserving_fixture_gate_recorded_support_blocked_review_hold_preserved",
            "purpose": "Four blocked C/Rust source-preserving fixture shapes for layout, comments, token boundaries, Rust tail expressions, and fallthrough order.",
            "reviewFocus": "Confirm the source-preserving lane starts blocked and preserves the P120 reviewer hold.",
            "fixtureIds": [
                "c_if_else_source_layout_v0",
                "c_nested_source_order_v0",
                "rust_if_expr_source_layout_v0",
                "rust_early_return_source_order_v0",
            ],
        },
        {
            "phase": "P122",
            "decision": "source_preserving_expected_rows_recorded_support_blocked",
            "purpose": "Expected preservation rows for c_if_else_source_layout_v0.",
            "reviewFocus": "Confirm the selected C if/else layout surface is explicit before any checker or implementation claim.",
            "expectedRows": 8,
        },
        {
            "phase": "P123",
            "decision": "source_preserving_expected_row_checker_recorded_support_blocked",
            "purpose": "Local expected-row checker for the selected C if/else source sketch.",
            "reviewFocus": "Confirm the checker matches the stored sketch but does not parse, re-emit, or validate fidelity.",
            "checkerPasses": 8,
        },
        {
            "phase": "P124",
            "decision": "source_preserving_negative_control_checker_recorded_support_blocked",
            "purpose": "Negative-control checker for mutated c_if_else_source_layout_v0 sketches.",
            "reviewFocus": "Confirm intentionally mutated sketches fail closed with expected failed-row sets.",
            "negativeControls": 4,
            "expectedFailedRows": 12,
        },
        {
            "phase": "P125",
            "decision": "second_source_preserving_fixture_expected_rows_checker_negative_controls_recorded_support_blocked",
            "purpose": "Same checker discipline for c_nested_source_order_v0.",
            "reviewFocus": "Confirm a second C source-order fixture uses the discipline without claiming support.",
            "expectedRows": 7,
            "negativeControls": 3,
        },
        {
            "phase": "P126",
            "decision": "rust_source_preserving_fixture_expected_rows_checker_negative_controls_recorded_support_blocked",
            "purpose": "Same checker discipline for rust_if_expr_source_layout_v0.",
            "reviewFocus": "Confirm the first Rust source-preserving fixture is bounded to source-sketch rows.",
            "expectedRows": 7,
            "negativeControls": 3,
        },
        {
            "phase": "P127",
            "decision": "rust_early_return_source_order_expected_rows_checker_negative_controls_recorded_support_blocked",
            "purpose": "Same checker discipline for rust_early_return_source_order_v0.",
            "reviewFocus": "Confirm the Rust early-return/fallthrough fixture is checked and still support-blocked.",
            "expectedRows": 8,
            "negativeControls": 3,
        },
    ]


def build_reviewer_handoff_packet() -> dict[str, Any]:
    return {
        "handoffStatus": "ready_for_private_review",
        "reviewerDecisionStatus": "not_recorded",
        "reviewSurface": "private_only",
        "implementationStatus": "held_pending_reviewer_response",
        "bundleRange": "P121-P127",
        "allowedPrivateOutcomes": [
            "accept_fixture_discipline_private_scope",
            "request_copy_tightening",
            "request_real_parser_or_reemitter_design_before_support",
            "request_preservation_oracle_before_support",
            "request_token_comment_whitespace_fidelity_tests",
            "request_runtime_or_reingest_attachment",
            "request_reviewer_hold",
        ],
        "reviewerMustInspect": [
            "P121 blocked fixture matrix and P120 hold preservation.",
            "P122 expected rows for c_if_else_source_layout_v0.",
            "P123 local expected-row checker and mismatch behavior.",
            "P124 negative controls for c_if_else_source_layout_v0.",
            "P125 second C source-order fixture checker.",
            "P126 Rust if-expression source-layout checker.",
            "P127 Rust early-return/fallthrough source-order checker.",
        ],
        "pivotCriteria": [
            "A real reviewer response is recorded before any implementation posture changes.",
            "A separate implementation phase is created before source parser, re-emitter, or preservation-oracle work.",
            "Source-preserving support remains blocked until token/comment/layout fidelity evidence exists.",
            "Public/package/checkout posture remains blocked until a separate release gate changes it.",
        ],
    }


def build_handoff_checklist() -> list[dict[str, str]]:
    return [
        {"id": "p121_fixture_gate_reviewed", "status": "ready"},
        {"id": "p122_expected_rows_reviewed", "status": "ready"},
        {"id": "p123_checker_reviewed", "status": "ready"},
        {"id": "p124_negative_controls_reviewed", "status": "ready"},
        {"id": "p125_second_fixture_reviewed", "status": "ready"},
        {"id": "p126_rust_if_expr_fixture_reviewed", "status": "ready"},
        {"id": "p127_rust_early_return_fixture_reviewed", "status": "ready"},
    ]


def build_summary(
    p127_packet: dict[str, Any],
    p127_payload: dict[str, Any],
    bundle_evidence: list[dict[str, Any]],
    handoff: dict[str, Any],
    checklist: list[dict[str, str]],
) -> dict[str, Any]:
    p127_summary = p127_payload["summary"]
    return {
        "sourcePacketCount": 1,
        "p127ValidationPass": p127_packet["validationStatus"] == "pass",
        "p127ClaimFlagsAllFalse": all(value is False for value in p127_packet["claimFlags"].values()),
        "selectedFixtureId": p127_summary["selectedFixtureId"],
        "selectedFixtureStillBlocked": p127_summary["selectedFixtureStillBlocked"],
        "bundleRange": handoff["bundleRange"],
        "bundleEvidenceEntryCount": len(bundle_evidence),
        "handoffChecklistCount": len(checklist),
        "allowedPrivateOutcomeCount": len(handoff["allowedPrivateOutcomes"]),
        "reviewerMustInspectCount": len(handoff["reviewerMustInspect"]),
        "pivotCriteriaCount": len(handoff["pivotCriteria"]),
        "reviewerHandoffReady": handoff["handoffStatus"] == "ready_for_private_review",
        "reviewerDecisionRecorded": False,
        "reviewerDecisionStatus": handoff["reviewerDecisionStatus"],
        "implementationHeldPendingReview": handoff["implementationStatus"] == "held_pending_reviewer_response",
        "implementationApproved": False,
        "implementationApplied": False,
        "implementationDiffProduced": False,
        "sourceParserExecuted": False,
        "sourceReemitterExecuted": False,
        "preservationOracleExecuted": False,
        "sourceFidelityValidated": False,
        "runtimeExecutionPerformed": False,
        "frontendLoweringChanged": False,
        "sourcePreservingRoundtripSupportClaim": False,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "p121ToP127BundleComplete": [item["phase"] for item in bundle_evidence] == ["P121", "P122", "P123", "P124", "P125", "P126", "P127"],
        "sourcePreservingFixtureCount": 4,
        "checkerFixtureCount": 4,
        "totalExpectedRowsAcrossCheckerFixtures": 30,
        "totalCheckerPassesAcrossCheckerFixtures": 30,
        "totalNegativeControlsAcrossCheckerFixtures": 13,
        "totalExpectedFailedRowsAcrossNegativeControls": 37,
        "p127CheckerPassCount": p127_summary["checkerPassCount"],
        "p127NegativeControlExpectedFailureCount": p127_summary["negativeControlExpectedFailureCount"],
        "compoundConditionSupportClaim": False,
        "loopBackedgeSupportClaim": False,
        "assignmentPhiSupportClaim": False,
        "sideEffectMemorySupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "unsupportedConstructsSupported": False,
        "generalBranchControlFlowClaim": False,
        "branchControlFlowReingestClaim": False,
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
    p127_packet = read_json(P127_PACKET)
    p127_payload = read_json(P127_RESULT)
    p127.validate_payload(p127_payload)
    bundle_evidence = build_bundle_evidence()
    handoff = build_reviewer_handoff_packet()
    checklist = build_handoff_checklist()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p128-source-preserving-private-reviewer-handoff-hold-gate",
        "decision": "source_preserving_private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "sourcePacket": {
            "phase": "P127",
            "packetPath": str(P127_PACKET.relative_to(ROOT)),
            "resultPath": str(P127_RESULT.relative_to(ROOT)),
            "reviewDecision": p127_packet["reviewDecision"],
            "validationStatus": p127_packet["validationStatus"],
        },
        "reviewerHandoffPacket": handoff,
        "bundleEvidence": bundle_evidence,
        "handoffChecklist": checklist,
        "summary": build_summary(p127_packet, p127_payload, bundle_evidence, handoff, checklist),
        "releaseGates": [
            {"id": "source_preserving_private_reviewer_handoff", "status": "ready"},
            {"id": "reviewer_decision", "status": "not_recorded"},
            {"id": "implementation_change", "status": "held"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "source_parser_execution", "status": "not_performed"},
            {"id": "source_reemitter_execution", "status": "not_performed"},
            {"id": "preservation_oracle_execution", "status": "not_run"},
            {"id": "source_fidelity_validation", "status": "not_performed"},
            {"id": "source_preserving_roundtrip_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P128 packages the P121-P127 source-preserving evidence bundle for private review.",
            "P128 marks reviewer response as not recorded.",
            "P128 holds source-preserving implementation pending reviewer response.",
            "P128 records no parser, re-emitter, preservation-oracle, fidelity-validation, support, public-readiness, compiler-correctness, or runtime-performance claim.",
        ],
        "blockedStatements": [
            "A reviewer has approved source-preserving roundtrip implementation.",
            "A reviewer has rejected source-preserving roundtrip implementation.",
            "The implementation change has been approved.",
            "The implementation change has been applied.",
            "An implementation diff has been produced.",
            "Non-generated source was parsed for source-preserving roundtrip.",
            "Non-generated source was re-emitted.",
            "A preservation oracle checked source fidelity.",
            "Token, whitespace, comment, or formatting fidelity has been validated.",
            "Source-preserving roundtrip is supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
            "Forge/eFrog is public-ready or package-ready.",
        ],
        "nextMilestones": [
            "Record the actual private reviewer response to P121-P128.",
            "If approved, create a separate implementation phase with source diffs, parser/re-emitter scope, preservation-oracle criteria, and rollback checks.",
            "If held, keep source-preserving support blocked and pivot to reviewer response capture or release-boundary consolidation.",
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
        "title": "FEF-P128 Source-Preserving Private Reviewer Handoff Hold Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "source_preserving_private_reviewer_handoff_ready_response_not_recorded_implementation_held",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private reviewer handoff only; no reviewer decision, approval, rejection, implementation diff, source parser execution, source re-emitter execution, preservation-oracle execution, source-fidelity validation, source-preserving support, full source roundtrip, compiler correctness, formal equivalence, runtime performance, or public readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P128 packages P121-P127 for private review.",
            "Reviewer decision remains not recorded.",
            "Source-preserving implementation remains held and not applied.",
            "The next pivot point is an actual reviewer response or a separate approved implementation phase.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p128_source_preserving_private_reviewer_handoff_hold_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p128_source_preserving_private_reviewer_handoff_hold_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p128_source_preserving_private_reviewer_handoff_hold_gate.v0",
        "date": DATE,
        "title": "FEF-P128 Source-Preserving Private Reviewer Handoff Hold Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record actual private reviewer response before source-preserving implementation posture changes.",
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
    return "\n".join([
        "# FEF-P128 Source-Preserving Private Reviewer Handoff Hold Gate",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P128 packages the source-preserving fixture ladder for private review and keeps implementation held.",
        "",
        "## Summary",
        "",
        f"- Bundle range: `{summary['bundleRange']}`",
        f"- Bundle evidence entries: `{summary['bundleEvidenceEntryCount']}`",
        f"- Reviewer handoff ready: `{summary['reviewerHandoffReady']}`",
        f"- Reviewer decision status: `{summary['reviewerDecisionStatus']}`",
        f"- Implementation held pending review: `{summary['implementationHeldPendingReview']}`",
        f"- Implementation approved: `{summary['implementationApproved']}`",
        f"- Implementation applied: `{summary['implementationApplied']}`",
        f"- Source parser executed: `{summary['sourceParserExecuted']}`",
        f"- Source re-emitter executed: `{summary['sourceReemitterExecuted']}`",
        f"- Preservation oracle executed: `{summary['preservationOracleExecuted']}`",
        f"- Source fidelity validated: `{summary['sourceFidelityValidated']}`",
        f"- Source-preserving support claim: `{summary['sourcePreservingRoundtripSupportClaim']}`",
        f"- Checker fixtures: `{summary['checkerFixtureCount']}`",
        f"- Expected rows across checker fixtures: `{summary['totalExpectedRowsAcrossCheckerFixtures']}`",
        f"- Negative controls across checker fixtures: `{summary['totalNegativeControlsAcrossCheckerFixtures']}`",
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
        "- No source parser, re-emitter, preservation oracle, or source-fidelity validation.",
        "- No source-preserving roundtrip support claim.",
        "- No compiler-correctness, formal-equivalence, runtime-performance, package, checkout, or public-readiness claim.",
        "",
    ])


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P128 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P128 status")
    p127.validate_payload(read_json(P127_RESULT))
    summary = payload["summary"]
    for key in [
        "p127ValidationPass",
        "p127ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "reviewerHandoffReady",
        "implementationHeldPendingReview",
        "p121ToP127BundleComplete",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["reviewerDecisionStatus"] != "not_recorded":
        raise ValueError("reviewer decision must remain not recorded")
    if summary["bundleRange"] != "P121-P127":
        raise ValueError("unexpected bundle range")
    if summary["bundleEvidenceEntryCount"] != 7 or summary["handoffChecklistCount"] != 7:
        raise ValueError("expected seven bundle entries and checklist rows")
    if summary["allowedPrivateOutcomeCount"] != 7 or summary["reviewerMustInspectCount"] != 7:
        raise ValueError("expected seven reviewer outcomes and inspection rows")
    if summary["pivotCriteriaCount"] != 4:
        raise ValueError("expected four pivot criteria")
    if summary["sourcePreservingFixtureCount"] != 4 or summary["checkerFixtureCount"] != 4:
        raise ValueError("unexpected fixture counts")
    if summary["totalExpectedRowsAcrossCheckerFixtures"] != 30 or summary["totalCheckerPassesAcrossCheckerFixtures"] != 30:
        raise ValueError("unexpected expected-row/checker totals")
    if summary["totalNegativeControlsAcrossCheckerFixtures"] != 13 or summary["totalExpectedFailedRowsAcrossNegativeControls"] != 37:
        raise ValueError("unexpected negative-control totals")
    for key in [
        "reviewerDecisionRecorded",
        "implementationApproved",
        "implementationApplied",
        "implementationDiffProduced",
        "sourceParserExecuted",
        "sourceReemitterExecuted",
        "preservationOracleExecuted",
        "sourceFidelityValidated",
        "runtimeExecutionPerformed",
        "frontendLoweringChanged",
        "sourcePreservingRoundtripSupportClaim",
        "fullNonGeneratedSourceRoundtripClaim",
        "compoundConditionSupportClaim",
        "loopBackedgeSupportClaim",
        "assignmentPhiSupportClaim",
        "sideEffectMemorySupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "unsupportedConstructsSupported",
        "generalBranchControlFlowClaim",
        "branchControlFlowReingestClaim",
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
    result_path = out_dir / f"fef_p128_source_preserving_private_reviewer_handoff_hold_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p128_source_preserving_private_reviewer_handoff_hold_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p128_source_preserving_private_reviewer_handoff_hold_gate.json"
    feed_path = command_feed_dir / f"fef_p128_source_preserving_private_reviewer_handoff_hold_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p128_source_preserving_private_reviewer_handoff_hold_gate")
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
    print("FEF_P128_SOURCE_PRESERVING_PRIVATE_REVIEWER_HANDOFF_HOLD_GATE_OK")
    print(f"reviewer_decision={built['payload']['summary']['reviewerDecisionStatus']}")
    print(f"bundle_entries={built['payload']['summary']['bundleEvidenceEntryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
