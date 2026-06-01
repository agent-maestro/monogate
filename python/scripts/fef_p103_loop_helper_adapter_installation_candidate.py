#!/usr/bin/env python3
"""FEF-P103 selected loop helper adapter installation candidate."""

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

from scripts import fef_p102_loop_parsed_eml_python_comparison as p102  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p103_loop_helper_adapter_installation_candidate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P103_LOOP_HELPER_ADAPTER_INSTALLATION_CANDIDATE_PASS"

P102_PACKET = ROOT / "reports/evidence_packets/fef_p102_loop_parsed_eml_python_comparison.json"
P102_RESULT = ROOT / "python/results/fef_p102_loop_parsed_eml_python_comparison/fef_p102_loop_parsed_eml_python_comparison_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_helper_adapter_installation_candidate_claim": False,
    "loop_helper_adapter_installed": False,
    "loop_reingest_parse_success_claim": False,
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
    "FEF-P103 records a selected loop helper adapter installation candidate only.",
    "FEF-P103 does not apply the candidate or change eFrog or Forge source code.",
    "FEF-P103 does not install the selected loop helper adapter in eFrog or Forge.",
    "FEF-P103 does not execute a Forge-recompiled Python target.",
    "FEF-P103 does not claim supported loop re-ingest.",
    "FEF-P103 does not install loop lowering in Forge or eFrog.",
    "FEF-P103 does not implement loop headers, latches, variants, or back-edge semantics in Forge or eFrog.",
    "FEF-P103 does not claim loop/back-edge support.",
    "FEF-P103 does not claim general branch/control-flow support.",
    "FEF-P103 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P103 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_installation_candidate(p102_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidateId": "selected_loop_helper_inline_adapter_installation_candidate_v0",
        "sourceAdapterId": p102_payload["summary"]["selectedFixtureId"] + "_helper_inline_adapter",
        "evidenceSource": "FEF-P102",
        "status": "candidate_recorded_not_applied",
        "scope": "selected_c_while_accumulate_v0_generated_c_fixture_only",
        "changeType": "selected_local_adapter_candidate_installation",
        "intendedPipelineHooks": [
            {
                "hookId": "match_selected_loop_effective_iteration_helper_definition",
                "targetSurface": "eFrog C generated-target re-ingest pre-normalization",
                "sourcePattern": "static int mg_loop_effective_iterations(int n) { return n > 0 ? n : 0; }",
                "candidateAction": "remove selected helper definition before C decompile",
                "requiredPriorEvidence": ["FEF-P101", "FEF-P102"],
            },
            {
                "hookId": "inline_selected_loop_effective_iteration_call",
                "targetSurface": "eFrog C generated-target re-ingest pre-normalization",
                "sourcePattern": "int k = mg_loop_effective_iterations(n);",
                "candidateAction": "rewrite to int k = n > 0 ? n : 0;",
                "requiredPriorEvidence": ["FEF-P101", "FEF-P102"],
            },
            {
                "hookId": "preserve_selected_p92_boundedness_contract",
                "targetSurface": "selected loop runtime comparison harness",
                "sourcePattern": "c_while_accumulate_v0 P92 sample table",
                "candidateAction": "require exact P98/P102 seven-row comparison before any support claim",
                "requiredPriorEvidence": ["FEF-P92", "FEF-P98", "FEF-P102"],
            },
        ],
        "requiredApprovalGates": [
            "private reviewer accepts selected-fixture-only installation scope",
            "existing P51-P103 regression remains green",
            "new implementation phase records actual source diffs separately from this candidate",
            "actual Forge-recompiled Python target execution remains blocked until installation is intentionally applied",
            "public/compiler correctness/performance/support claims remain false after any implementation phase",
        ],
        "rollbackCriteria": [
            "adapter applies outside c_while_accumulate_v0 generated C fixture",
            "P101 parse success regresses",
            "any P102 selected parsed-EML comparison row diverges",
            "any loop/back-edge support flag becomes true",
            "claim flags drift to true",
        ],
        "candidateApplied": False,
        "implementationDiffProduced": False,
        "installedInEfrog": False,
        "installedInForge": False,
        "actualReingestExecutionPerformed": False,
        "compilerBehaviorChanged": False,
    }


def build_review_checks(candidate: dict[str, Any], p102_payload: dict[str, Any]) -> list[dict[str, Any]]:
    summary = p102_payload["summary"]
    checks = [
        ("candidate_scope_selected_fixture_only", candidate["scope"] == "selected_c_while_accumulate_v0_generated_c_fixture_only"),
        ("p102_row_count_is_seven", summary["rowCount"] == 7),
        ("p102_all_rows_pass", summary["passCount"] == 7 and summary["failCount"] == 0),
        ("p102_exact_agreement", summary["maxAbsError"] == 0.0),
        ("p101_parse_succeeded", summary["p101ReingestParseSucceeded"] is True),
        ("p101_helper_blocker_cleared", summary["p101PreviousBlockerCleared"] is True),
        ("candidate_not_applied", candidate["candidateApplied"] is False),
        ("implementation_diff_not_produced", candidate["implementationDiffProduced"] is False),
        ("actual_reingest_execution_not_performed", candidate["actualReingestExecutionPerformed"] is False),
        ("adapter_not_installed_in_efrog", candidate["installedInEfrog"] is False),
        ("adapter_not_installed_in_forge", candidate["installedInForge"] is False),
    ]
    return [
        {
            "checkId": check_id,
            "status": "pass" if passed else "fail",
            "passed": passed,
        }
        for check_id, passed in checks
    ]


def build_summary(p102_packet: dict[str, Any], p102_payload: dict[str, Any], candidate: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p102ValidationPass": p102_packet["validationStatus"] == "pass",
        "p102ClaimFlagsAllFalse": all(value is False for value in p102_packet["claimFlags"].values()),
        "selectedFixtureId": p102_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p102_payload["summary"]["selectedFixtureStillBlocked"],
        "candidateId": candidate["candidateId"],
        "candidateStatus": candidate["status"],
        "intendedPipelineHookCount": len(candidate["intendedPipelineHooks"]),
        "requiredApprovalGateCount": len(candidate["requiredApprovalGates"]),
        "rollbackCriteriaCount": len(candidate["rollbackCriteria"]),
        "reviewCheckCount": len(checks),
        "reviewCheckPassCount": sum(1 for check in checks if check["passed"]),
        "reviewCheckFailCount": sum(1 for check in checks if not check["passed"]),
        "p102RowCount": p102_payload["summary"]["rowCount"],
        "p102PassCount": p102_payload["summary"]["passCount"],
        "p102FailCount": p102_payload["summary"]["failCount"],
        "p102MaxAbsError": p102_payload["summary"]["maxAbsError"],
        "p101ReingestParseSucceeded": p102_payload["summary"]["p101ReingestParseSucceeded"],
        "p101PreviousBlockerCleared": p102_payload["summary"]["p101PreviousBlockerCleared"],
        "installationCandidateRecorded": True,
        "candidateApplied": candidate["candidateApplied"],
        "implementationDiffProduced": candidate["implementationDiffProduced"],
        "actualReingestExecutionPerformed": candidate["actualReingestExecutionPerformed"],
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
    p102_packet = read_json(P102_PACKET)
    p102_payload = read_json(P102_RESULT)
    p102.validate_payload(p102_payload)
    candidate = build_installation_candidate(p102_payload)
    checks = build_review_checks(candidate, p102_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p103-loop-helper-adapter-installation-candidate",
        "decision": "selected_loop_helper_adapter_installation_candidate_recorded_not_applied",
        "sourcePacket": {
            "phase": "P102",
            "packetPath": str(P102_PACKET.relative_to(ROOT)),
            "resultPath": str(P102_RESULT.relative_to(ROOT)),
            "reviewDecision": p102_packet["reviewDecision"],
            "validationStatus": p102_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p102_payload["selectedFixture"]),
        "installationCandidate": candidate,
        "reviewChecks": checks,
        "summary": build_summary(p102_packet, p102_payload, candidate, checks),
        "releaseGates": [
            {"id": "selected_loop_helper_adapter_installation_candidate", "status": "recorded_not_applied"},
            {"id": "private_reviewer_approval", "status": "required_not_recorded"},
            {"id": "implementation_diff", "status": "not_produced"},
            {"id": "actual_reingest_execution", "status": "blocked_not_performed"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P103 records a selected loop helper adapter installation candidate.",
            "The candidate has three scoped pipeline hooks, five approval gates, and five rollback criteria.",
            "P103 does not apply the candidate, install an adapter, or execute a Forge-recompiled Python target.",
            "Loop/back-edge support remains blocked.",
        ],
        "blockedStatements": [
            "The selected loop helper adapter has been installed.",
            "The implementation change has been applied.",
            "A Forge-recompiled Python target was executed.",
            "Loop re-ingest is supported.",
            "Loop lowering is implemented.",
            "Loop/back-edge constructs are supported.",
            "The P92 boundedness policy is a general loop policy.",
            "Loop headers, latches, variants, or back-edge semantics are implemented.",
            "General branch/control-flow support is established.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Record private reviewer response to the P47-P103 branch/control-flow bundle.",
            "If approved, create a separate implementation phase with source diffs and rollback checks.",
            "If held, continue the unsupported-form ladders without applying this candidate.",
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
        "title": "FEF-P103 Loop Helper Adapter Installation Candidate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_loop_helper_adapter_installation_candidate_not_applied",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected installation candidate only; no adapter installation, implementation diff, Forge-recompiled Python execution, loop/back-edge support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P103 records three scoped pipeline hooks for the selected helper adapter candidate.",
            "P102 prerequisite rows remain seven passing comparisons with zero observed error.",
            "Candidate application and source diffs are held for a separate approved phase.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p103_loop_helper_adapter_installation_candidate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p103_loop_helper_adapter_installation_candidate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p103_loop_helper_adapter_installation_candidate.v0",
        "date": DATE,
        "title": "FEF-P103 Loop Helper Adapter Installation Candidate",
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
    for hook in payload["installationCandidate"]["intendedPipelineHooks"]:
        hooks.append(f"| `{hook['hookId']}` | `{hook['targetSurface']}` |")
    checks = ["| Check | Status |", "|---|---|"]
    for check in payload["reviewChecks"]:
        checks.append(f"| `{check['checkId']}` | `{check['status']}` |")
    return "\n".join(
        [
            "# FEF-P103 Loop Helper Adapter Installation Candidate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P103 records a selected installation candidate without applying it.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Candidate id: `{summary['candidateId']}`",
            f"- Candidate status: `{summary['candidateStatus']}`",
            f"- Pipeline hooks: `{summary['intendedPipelineHookCount']}`",
            f"- Approval gates: `{summary['requiredApprovalGateCount']}`",
            f"- Rollback criteria: `{summary['rollbackCriteriaCount']}`",
            f"- Review checks passing: `{summary['reviewCheckPassCount']}` / `{summary['reviewCheckCount']}`",
            f"- P102 rows/pass/fail: `{summary['p102RowCount']}` / `{summary['p102PassCount']}` / `{summary['p102FailCount']}`",
            f"- P102 max absolute error: `{summary['p102MaxAbsError']}`",
            f"- Candidate applied: `{summary['candidateApplied']}`",
            f"- Implementation diff produced: `{summary['implementationDiffProduced']}`",
            f"- Loop helper adapter installed: `{summary['loopHelperAdapterInstalled']}`",
            f"- Loop re-ingest supported: `{summary['loopReingestSupported']}`",
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
            "- Selected installation candidate only.",
            "- No source diff or installed adapter.",
            "- No Forge-recompiled Python target execution.",
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P103 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P103 status")
    p102.validate_payload(read_json(P102_RESULT))
    summary = payload["summary"]
    for key in [
        "p102ValidationPass",
        "p102ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "p101ReingestParseSucceeded",
        "p101PreviousBlockerCleared",
        "installationCandidateRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["intendedPipelineHookCount"] != 3:
        raise ValueError("expected three intended pipeline hooks")
    if summary["requiredApprovalGateCount"] != 5:
        raise ValueError("expected five approval gates")
    if summary["rollbackCriteriaCount"] != 5:
        raise ValueError("expected five rollback criteria")
    if summary["reviewCheckCount"] != 11 or summary["reviewCheckFailCount"] != 0:
        raise ValueError("expected eleven passing review checks")
    if summary["p102RowCount"] != 7 or summary["p102PassCount"] != 7 or summary["p102FailCount"] != 0:
        raise ValueError("expected P102 seven-row pass prerequisite")
    if summary["p102MaxAbsError"] != 0.0:
        raise ValueError("expected exact P102 agreement")
    for key in [
        "candidateApplied",
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
    result_path = out_dir / f"fef_p103_loop_helper_adapter_installation_candidate_{STAMP}.json"
    report_path = report_dir / f"fef_p103_loop_helper_adapter_installation_candidate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p103_loop_helper_adapter_installation_candidate.json"
    feed_path = command_feed_dir / f"fef_p103_loop_helper_adapter_installation_candidate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p103_loop_helper_adapter_installation_candidate")
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
    print("FEF_P103_LOOP_HELPER_ADAPTER_INSTALLATION_CANDIDATE_OK")
    print(f"candidate={built['payload']['summary']['candidateId']}")
    print(f"review_checks={built['payload']['summary']['reviewCheckPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
