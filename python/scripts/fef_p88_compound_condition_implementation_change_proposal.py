#!/usr/bin/env python3
"""FEF-P88 implementation-change proposal for the guarded-div candidate."""

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

from scripts import fef_p87_compound_condition_guarded_div_reingest_boundary_probe as p87  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p88_compound_condition_implementation_change_proposal.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P88_COMPOUND_CONDITION_IMPLEMENTATION_CHANGE_PROPOSAL_PASS"

P87_PACKET = ROOT / "reports/evidence_packets/fef_p87_compound_condition_guarded_div_reingest_boundary_probe.json"
P87_RESULT = ROOT / "python/results/fef_p87_compound_condition_guarded_div_reingest_boundary_probe/fef_p87_compound_condition_guarded_div_reingest_boundary_probe_2026_05_31.json"

CLAIM_FLAGS = {
    "implementation_change_proposed": False,
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
    "FEF-P88 records an implementation-change proposal only.",
    "FEF-P88 does not apply the proposed change.",
    "FEF-P88 does not install the guarded-div primitive in eFrog or Forge.",
    "FEF-P88 does not change eFrog or Forge source code.",
    "FEF-P88 does not execute re-ingested code.",
    "FEF-P88 does not claim supported compound-condition re-ingest.",
    "FEF-P88 does not claim compiler-wide short-circuit semantics.",
    "FEF-P88 does not claim compound-condition support.",
    "FEF-P88 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P88 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_change_proposal(p87_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposalId": "selected_guarded_div_adapter_installation_change_proposal_v0",
        "sourceBoundaryContract": p87_payload["boundaryContract"]["contractId"],
        "scope": "selected_c_and_short_circuit_guard_v0_only",
        "status": "proposal_recorded_not_applied",
        "changeType": "local_adapter_candidate_installation",
        "proposedChangeSet": [
            {
                "changeId": "install_selected_nonzero01_mapping",
                "targetSurface": "selected local adapter predicate mapping",
                "description": "Map the selected y != 0.0 predicate to nonzero01(y) for this fixture only.",
                "requiresPriorEvidence": ["FEF-P80", "FEF-P86", "FEF-P87"],
            },
            {
                "changeId": "install_selected_guarded_div_mapping",
                "targetSurface": "selected local adapter value mapping",
                "description": "Map guarded x / y to guarded_div(x, y, default=0.0, guard=nonzero01(y)) for this fixture only.",
                "requiresPriorEvidence": ["FEF-P85", "FEF-P86", "FEF-P87"],
            },
            {
                "changeId": "add_selected_non_evaluation_assertions",
                "targetSurface": "selected re-ingest comparison harness",
                "description": "Assert zero-denominator division skip and left-false right-side skip before runtime comparison.",
                "requiresPriorEvidence": ["FEF-P87"],
            },
        ],
        "requiredApprovalGates": [
            "private reviewer accepts selected-fixture-only implementation scope",
            "existing P51-P87 regression remains green",
            "new implementation phase records source diffs separately from this proposal",
            "actual re-ingest execution remains blocked until installation is intentionally applied",
            "public/compiler correctness/performance/support claims remain false after implementation",
        ],
        "rollbackCriteria": [
            "any zero-denominator row evaluates division",
            "any left-false row evaluates the right-side guard",
            "any selected P77 row diverges from expected value",
            "adapter applies outside c_and_short_circuit_guard_v0",
            "claim flags drift to true",
        ],
        "proposalApplied": False,
        "implementationDiffProduced": False,
        "actualReingestExecutionPerformed": False,
        "compilerBehaviorChanged": False,
    }


def build_review_checks(proposal: dict[str, Any], p87_payload: dict[str, Any]) -> list[dict[str, Any]]:
    summary = p87_payload["summary"]
    checks = [
        ("source_boundary_contract_present", bool(proposal["sourceBoundaryContract"])),
        ("proposal_scope_selected_fixture_only", proposal["scope"] == "selected_c_and_short_circuit_guard_v0_only"),
        ("p87_boundary_pass_count_is_seven", summary["boundaryPassCount"] == 7),
        ("p87_boundary_fail_count_is_zero", summary["boundaryFailCount"] == 0),
        ("zero_denominator_non_evaluation_preserved", summary["zeroDenominatorRowsWithDivisionSkipped"] == 2),
        ("left_false_non_evaluation_preserved", summary["leftFalseRowsWithRightSideSkipped"] == 3),
        ("proposal_not_applied", proposal["proposalApplied"] is False),
        ("implementation_diff_not_produced", proposal["implementationDiffProduced"] is False),
        ("actual_reingest_execution_not_performed", proposal["actualReingestExecutionPerformed"] is False),
    ]
    return [
        {
            "checkId": check_id,
            "status": "pass" if passed else "fail",
            "passed": passed,
        }
        for check_id, passed in checks
    ]


def build_summary(p87_packet: dict[str, Any], p87_payload: dict[str, Any], proposal: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p87ValidationPass": p87_packet["validationStatus"] == "pass",
        "p87ClaimFlagsAllFalse": all(value is False for value in p87_packet["claimFlags"].values()),
        "selectedFixtureId": p87_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p87_payload["summary"]["selectedFixtureStillBlocked"],
        "proposalId": proposal["proposalId"],
        "proposalStatus": proposal["status"],
        "changeSetCount": len(proposal["proposedChangeSet"]),
        "requiredApprovalGateCount": len(proposal["requiredApprovalGates"]),
        "rollbackCriteriaCount": len(proposal["rollbackCriteria"]),
        "reviewCheckCount": len(checks),
        "reviewCheckPassCount": sum(1 for check in checks if check["passed"]),
        "reviewCheckFailCount": sum(1 for check in checks if not check["passed"]),
        "proposalApplied": proposal["proposalApplied"],
        "implementationDiffProduced": proposal["implementationDiffProduced"],
        "actualReingestExecutionPerformed": proposal["actualReingestExecutionPerformed"],
        "implementationChangeProposalRecorded": True,
        "implementationChangeApplied": False,
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
    p87_packet = read_json(P87_PACKET)
    p87_payload = read_json(P87_RESULT)
    p87.validate_payload(p87_payload)
    proposal = build_change_proposal(p87_payload)
    checks = build_review_checks(proposal, p87_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p88-compound-condition-implementation-change-proposal",
        "decision": "selected_guarded_div_implementation_change_proposal_recorded_not_applied",
        "sourcePacket": {
            "phase": "P87",
            "packetPath": str(P87_PACKET.relative_to(ROOT)),
            "resultPath": str(P87_RESULT.relative_to(ROOT)),
            "reviewDecision": p87_packet["reviewDecision"],
            "validationStatus": p87_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p87_payload["selectedFixture"]),
        "implementationChangeProposal": proposal,
        "reviewChecks": checks,
        "summary": build_summary(p87_packet, p87_payload, proposal, checks),
        "releaseGates": [
            {"id": "implementation_change_proposal", "status": "recorded_not_applied"},
            {"id": "private_reviewer_approval", "status": "required_not_recorded"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "actual_reingest_execution", "status": "blocked_not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P88 records an explicit selected-fixture implementation-change proposal.",
            "The proposal has three scoped change items, five approval gates, and five rollback criteria.",
            "P88 does not apply the proposed change or execute re-ingested code.",
            "Compound-condition support remains blocked.",
        ],
        "blockedStatements": [
            "The implementation change has been applied.",
            "The selected guarded-div primitive is installed in eFrog or Forge.",
            "Re-ingested compound-condition code executed successfully.",
            "Compound-condition re-ingest is supported.",
            "The selected proposal proves compiler-wide short-circuit semantics.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Record private reviewer response to the P47-P88 branch/control-flow bundle.",
            "If approved, create a separate implementation phase with source diffs and rollback checks.",
            "If held, move to the next unsupported-form ladder without applying this proposal.",
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
        "title": "FEF-P88 Compound-Condition Implementation Change Proposal",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_guarded_div_implementation_change_proposal_recorded_not_applied",
        "semanticReview": payload["summary"],
        "claimBoundary": "Implementation-change proposal only; no applied source diff, installed eFrog/Forge behavior change, actual re-ingest execution, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P88 packages the guarded-div candidate as an explicit implementation-change proposal.",
            "The proposal requires private reviewer approval and a separate implementation phase before changes.",
            "All support/correctness/performance claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p88_compound_condition_implementation_change_proposal.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p88_compound_condition_implementation_change_proposal.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p88_compound_condition_implementation_change_proposal.v0",
        "date": DATE,
        "title": "FEF-P88 Compound-Condition Implementation Change Proposal",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record private reviewer response or hold and move to next unsupported-form ladder.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    changes = [
        f"- `{change['changeId']}`: {change['description']}"
        for change in payload["implementationChangeProposal"]["proposedChangeSet"]
    ]
    checks = [
        f"- `{check['checkId']}`: `{check['status']}`"
        for check in payload["reviewChecks"]
    ]
    return "\n".join(
        [
            "# FEF-P88 Compound-Condition Implementation Change Proposal",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P88 records a proposed implementation change without applying it.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Proposal: `{summary['proposalId']}`",
            f"- Change set count: `{summary['changeSetCount']}`",
            f"- Required approval gates: `{summary['requiredApprovalGateCount']}`",
            f"- Rollback criteria: `{summary['rollbackCriteriaCount']}`",
            f"- Review checks: `{summary['reviewCheckPassCount']}` passed / `{summary['reviewCheckFailCount']}` failed",
            f"- Proposal applied: `{summary['proposalApplied']}`",
            f"- Implementation diff produced: `{summary['implementationDiffProduced']}`",
            f"- Actual re-ingest execution performed: `{summary['actualReingestExecutionPerformed']}`",
            "",
            "## Proposed Changes",
            "",
            *changes,
            "",
            "## Review Checks",
            "",
            *checks,
            "",
            "## Boundary",
            "",
            "- Proposal only.",
            "- No source diff applied.",
            "- No installed eFrog or Forge behavior change.",
            "- No actual re-ingest execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P88 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P88 status")
    p87.validate_payload(read_json(P87_RESULT))
    summary = payload["summary"]
    for key in [
        "p87ValidationPass",
        "p87ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "implementationChangeProposalRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["proposalStatus"] != "proposal_recorded_not_applied":
        raise ValueError("proposal must remain unapplied")
    if summary["changeSetCount"] != 3:
        raise ValueError("expected three proposed change items")
    if summary["requiredApprovalGateCount"] != 5:
        raise ValueError("expected five approval gates")
    if summary["rollbackCriteriaCount"] != 5:
        raise ValueError("expected five rollback criteria")
    if summary["reviewCheckCount"] != 9 or summary["reviewCheckFailCount"] != 0:
        raise ValueError("expected all review checks to pass")
    for key in [
        "proposalApplied",
        "implementationDiffProduced",
        "actualReingestExecutionPerformed",
        "implementationChangeApplied",
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
    result_path = out_dir / f"fef_p88_compound_condition_implementation_change_proposal_{STAMP}.json"
    report_path = report_dir / f"fef_p88_compound_condition_implementation_change_proposal_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p88_compound_condition_implementation_change_proposal.json"
    feed_path = command_feed_dir / f"fef_p88_compound_condition_implementation_change_proposal_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p88_compound_condition_implementation_change_proposal")
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
    print("FEF_P88_COMPOUND_CONDITION_IMPLEMENTATION_CHANGE_PROPOSAL_OK")
    print(f"proposal_applied={built['payload']['summary']['proposalApplied']}")
    print(f"review_checks_passed={built['payload']['summary']['reviewCheckPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
