#!/usr/bin/env python3
"""CPG-A10 private lint contract implementation hold review or pause selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a9_private_lint_contract_implementation_hold_boundary_packet as cpg_a9  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_lint_contract_implementation_hold_review_or_pause_selector.v0"
STATUS = "CPG_A10_PRIVATE_LINT_CONTRACT_IMPLEMENTATION_HOLD_REVIEW_OR_PAUSE_SELECTOR_PASS"

NEXT_RECOMMENDED_ARTIFACT = "pause compiler-plugin lane as sufficiently bounded"

TRUE_CLAIM_FLAGS = {
    "cpg_a9_consumed",
    "implementation_hold_boundary_review_created",
    "implementation_hold_boundary_review_passed",
    "pause_compiler_plugin_lane_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a9_consumed": True,
    "implementation_hold_boundary_review_created": True,
    "implementation_hold_boundary_review_passed": True,
    "pause_compiler_plugin_lane_selected": True,
    "d109_hold_respected": True,
    "implementation_hold_approved": False,
    "implementation_scope_approved": False,
    "implementation_review_gate_selected": False,
    "implementation_hold_boundary_revision_created": False,
    "lint_contract_static_tests_created": False,
    "lint_contract_static_tests_executed": False,
    "executable_lint_contract_created": False,
    "executable_lint_contract_executed": False,
    "lint_contract_implementation_created": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "lint_engine_implemented": False,
    "lint_engine_executed": False,
    "fixture_runner_implemented": False,
    "fixture_runner_executed": False,
    "automatic_rewrite_enabled": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "automatic_lowering_safety_claim": False,
    "runtime_performance_claim": False,
    "code_generation_claim": False,
    "runtime_lowering_changed": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_package_release_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "scientific_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "ip_license_terms_finalized": False,
    "accelerator_card_ready": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "CPG-A10 is a private implementation-hold review and pause selector only.",
    "CPG-A10 pauses the compiler-plugin lane as sufficiently bounded; it does not approve implementation.",
    "CPG-A10 does not create or execute static tests, lint contracts, compiler plugins, lint engines, fixture runners, rewrite engines, code generators, or runtime lowering paths.",
    "CPG-A10 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A10 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def review_checks(payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "checkId": "implementation_preconditions_recorded",
            "status": "pass" if payload["summary"]["implementationPreconditionCount"] == 4 else "fail",
            "reason": "CPG-A9 records the four preconditions required before implementation can be scoped.",
        },
        {
            "checkId": "blocked_implementation_surfaces_recorded",
            "status": "pass" if payload["summary"]["blockedImplementationSurfaceCount"] == 4 else "fail",
            "reason": "CPG-A9 records compiler-plugin, lint-engine, rewrite/lowering, and public-release blockers.",
        },
        {
            "checkId": "reviewer_questions_recorded",
            "status": "pass" if payload["summary"]["reviewerQuestionCount"] == 4 else "fail",
            "reason": "CPG-A9 records explicit reviewer questions before any implementation discussion.",
        },
        {
            "checkId": "implementation_hold_not_approved",
            "status": "pass" if payload["summary"]["implementationHoldApproved"] is False and payload["summary"]["implementationScopeApproved"] is False else "fail",
            "reason": "No implementation approval or scope approval is present.",
        },
        {
            "checkId": "no_static_tests_or_lint_contract_created",
            "status": "pass" if payload["summary"]["lintContractStaticTestsCreated"] is False and payload["summary"]["executableLintContractCreated"] is False else "fail",
            "reason": "No executable static tests or lint contract have been created.",
        },
        {
            "checkId": "no_lint_or_plugin_implementation",
            "status": "pass" if payload["summary"]["lintEngineImplemented"] is False and payload["summary"]["compilerPluginImplemented"] is False else "fail",
            "reason": "No lint engine or compiler plugin implementation is recorded.",
        },
        {
            "checkId": "forbidden_claims_remain_false",
            "status": "pass" if payload["summary"]["compilerCorrectnessClaim"] is False and payload["summary"]["runtimePerformanceClaim"] is False else "fail",
            "reason": "Compiler-correctness and runtime-performance claims remain false.",
        },
    ]


def candidate_next_actions() -> list[dict[str, str]]:
    return [
        {
            "actionId": "pause_compiler_plugin_lane",
            "decision": "selected_next",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "The lane now has guard notes, static fixtures, boundary contracts, fixture review, and implementation-hold boundaries without reviewer approval for implementation.",
        },
        {
            "actionId": "implementation_review_gate",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "No explicit reviewer approval or executable static-test contract exists.",
        },
        {
            "actionId": "implementation_hold_boundary_revision",
            "decision": "parked",
            "nextArtifact": "CPG-A11-alt private implementation hold boundary revision",
            "reason": "No hold-boundary review failure was recorded in this selector.",
        },
        {
            "actionId": "static_test_execution",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Executable static-test contract has not been drafted or approved.",
        },
        {
            "actionId": "public_docs_or_package",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Public docs or package work requires separate approval and readiness evidence.",
        },
    ]


def build_payload() -> dict[str, Any]:
    boundary = cpg_a9.build_payload()
    cpg_a9.validate_payload(boundary)
    checks = review_checks(boundary)
    actions = candidate_next_actions()
    selected = [action for action in actions if action["decision"] == "selected_next"]
    summary = {
        "sourceArtifact": boundary["artifactId"],
        "reviewCheckCount": len(checks),
        "reviewPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "reviewFailCount": sum(1 for check in checks if check["status"] != "pass"),
        "candidateActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "compilerPluginLanePaused": True,
        "implementationHoldApproved": False,
        "implementationScopeApproved": False,
        "implementationReviewGateSelected": False,
        "implementationHoldBoundaryRevisionCreated": False,
        "lintContractStaticTestsCreated": False,
        "lintContractStaticTestsExecuted": False,
        "executableLintContractCreated": False,
        "executableLintContractExecuted": False,
        "lintContractImplementationCreated": False,
        "compilerPluginImplemented": False,
        "compilerPluginExecuted": False,
        "lintEngineImplemented": False,
        "lintEngineExecuted": False,
        "fixtureRunnerImplemented": False,
        "fixtureRunnerExecuted": False,
        "compilerCorrectnessClaim": False,
        "semanticPreservationClaim": False,
        "automaticLoweringSafetyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="cpg-a10-private-lint-contract-implementation-hold-review-or-pause-selector",
        artifact_type="private_lint_contract_implementation_hold_review_or_pause_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": boundary["artifactId"],
            "reviewChecks": checks,
            "candidateNextActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a9-private-lint-contract-implementation-hold-boundary-packet":
        raise ValueError("CPG-A10 must consume CPG-A9")
    summary = payload["summary"]
    if summary["reviewFailCount"] != 0:
        raise ValueError("hold boundary review must have no failures")
    if summary["selectedActionId"] != "pause_compiler_plugin_lane":
        raise ValueError("CPG-A10 must pause the compiler plugin lane")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["compilerPluginLanePaused"] is not True:
        raise ValueError("compiler plugin lane must be paused")
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateNextActions"]}
    if decisions["implementation_review_gate"] != "blocked":
        raise ValueError("implementation review gate must be blocked")
    if decisions["static_test_execution"] != "blocked":
        raise ValueError("static test execution must be blocked")
    if decisions["implementation_hold_boundary_revision"] != "parked":
        raise ValueError("implementation hold revision must be parked")
    for key in [
        "implementationHoldApproved",
        "implementationScopeApproved",
        "implementationReviewGateSelected",
        "implementationHoldBoundaryRevisionCreated",
        "lintContractStaticTestsCreated",
        "lintContractStaticTestsExecuted",
        "executableLintContractCreated",
        "executableLintContractExecuted",
        "lintContractImplementationCreated",
        "compilerPluginImplemented",
        "compilerPluginExecuted",
        "lintEngineImplemented",
        "lintEngineExecuted",
        "fixtureRunnerImplemented",
        "fixtureRunnerExecuted",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "automaticLoweringSafetyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="private_implementation_hold_review_pause_selector_no_approval",
        source=f"python/results/cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector/cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "compilerPluginLanePaused": payload["summary"]["compilerPluginLanePaused"],
            "implementationHoldApproved": payload["summary"]["implementationHoldApproved"],
            "implementationScopeApproved": payload["summary"]["implementationScopeApproved"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A10 Private Lint Contract Implementation Hold Review or Pause Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("review pass count", payload["summary"]["reviewPassCount"]),
            ("review fail count", payload["summary"]["reviewFailCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("compiler plugin lane paused", payload["summary"]["compilerPluginLanePaused"]),
            ("implementation hold approved", payload["summary"]["implementationHoldApproved"]),
        ],
        sections=[
            (
                "Review Checks",
                [f"- `{check['checkId']}`: `{check['status']}` - {check['reason']}" for check in payload["reviewChecks"]],
            ),
            (
                "Candidate Next Actions",
                [
                    f"- `{action['actionId']}`: `{action['decision']}` - {action['reason']}"
                    for action in payload["candidateNextActions"]
                ],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector_{STAMP}.json"
    report_path = report_dir / f"cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector.json"
    feed_path = command_feed_dir / f"cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("CPG_A10_PRIVATE_LINT_CONTRACT_IMPLEMENTATION_HOLD_REVIEW_OR_PAUSE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
