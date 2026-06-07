#!/usr/bin/env python3
"""CPG-A8 private lint contract static fixture review or implementation hold selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a7_private_lint_contract_static_test_fixture_packet as cpg_a7  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_lint_contract_static_fixture_review_or_implementation_hold_selector.v0"
STATUS = "CPG_A8_PRIVATE_LINT_CONTRACT_STATIC_FIXTURE_REVIEW_OR_IMPLEMENTATION_HOLD_SELECTOR_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A9 private lint contract implementation hold boundary packet"

TRUE_CLAIM_FLAGS = {
    "cpg_a7_consumed",
    "static_fixture_review_created",
    "static_fixture_review_passed",
    "implementation_hold_boundary_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a7_consumed": True,
    "static_fixture_review_created": True,
    "static_fixture_review_passed": True,
    "implementation_hold_boundary_selected": True,
    "d109_hold_respected": True,
    "implementation_hold_boundary_packet_created": False,
    "implementation_hold_approved": False,
    "lint_contract_static_fixture_revision_created": False,
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
    "CPG-A8 is a private static-fixture review and next-action selector only.",
    "CPG-A8 selects an implementation-hold boundary packet; it does not approve implementation.",
    "CPG-A8 does not create or execute static tests, lint contracts, compiler plugins, lint engines, fixture runners, rewrite engines, code generators, or runtime lowering paths.",
    "CPG-A8 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A8 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def review_checks(payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "checkId": "accepted_static_fixture_count",
            "status": "pass" if payload["summary"]["acceptedStaticFixtureCount"] == 4 else "fail",
            "reason": "CPG-A7 records four accepted static fixture shapes.",
        },
        {
            "checkId": "rejection_static_fixture_count",
            "status": "pass" if payload["summary"]["rejectionStaticFixtureCount"] == 4 else "fail",
            "reason": "CPG-A7 records four rejection static fixture shapes.",
        },
        {
            "checkId": "allowed_output_kind_coverage",
            "status": "pass" if {fixture["expectedOutputKind"] for fixture in payload["acceptedStaticFixtures"]} == {
                "advisory_notice",
                "guard_checklist_item",
                "evidence_pointer",
                "blocked_claim_notice",
            } else "fail",
            "reason": "Accepted fixtures cover every allowed output kind from the boundary packet.",
        },
        {
            "checkId": "blocked_output_kind_coverage",
            "status": "pass" if {fixture["blockedOutputKind"] for fixture in payload["rejectionStaticFixtures"]} == {
                "automatic_rewrite",
                "runtime_speedup",
                "package_release_ready",
                "guard_proven",
            } else "fail",
            "reason": "Rejection fixtures cover rewrite, performance, public/package, and guard-proof requests.",
        },
        {
            "checkId": "no_static_tests_created_or_executed",
            "status": "pass" if payload["summary"]["lintContractStaticTestsCreated"] is False and payload["summary"]["lintContractStaticTestsExecuted"] is False else "fail",
            "reason": "CPG-A7 records fixture shapes only.",
        },
        {
            "checkId": "no_lint_contract_or_engine_execution",
            "status": "pass" if payload["summary"]["executableLintContractExecuted"] is False and payload["summary"]["lintEngineExecuted"] is False else "fail",
            "reason": "No lint contract or lint engine execution is recorded.",
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
            "actionId": "implementation_hold_boundary_packet",
            "decision": "selected_next",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "Static fixture shapes are broad enough to draft a boundary packet for whether implementation should remain held or be scoped.",
        },
        {
            "actionId": "static_fixture_revision_packet",
            "decision": "parked",
            "nextArtifact": "CPG-A9-alt private lint contract static fixture revision packet",
            "reason": "No fixture-review failure was recorded in this selector.",
        },
        {
            "actionId": "static_test_execution",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Static fixture shapes are not executable static tests.",
        },
        {
            "actionId": "lint_contract_implementation",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Implementation remains blocked until an implementation-hold boundary packet exists and is reviewed.",
        },
        {
            "actionId": "public_docs_or_package",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Public docs or package work requires separate approval and readiness evidence.",
        },
    ]


def build_payload() -> dict[str, Any]:
    fixtures = cpg_a7.build_payload()
    cpg_a7.validate_payload(fixtures)
    checks = review_checks(fixtures)
    actions = candidate_next_actions()
    selected = [action for action in actions if action["decision"] == "selected_next"]
    summary = {
        "sourceArtifact": fixtures["artifactId"],
        "reviewCheckCount": len(checks),
        "reviewPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "reviewFailCount": sum(1 for check in checks if check["status"] != "pass"),
        "candidateActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "implementationHoldBoundaryPacketCreated": False,
        "implementationHoldApproved": False,
        "lintContractStaticFixtureRevisionCreated": False,
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
        artifact_id="cpg-a8-private-lint-contract-static-fixture-review-or-implementation-hold-selector",
        artifact_type="private_lint_contract_static_fixture_review_or_implementation_hold_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": fixtures["artifactId"],
            "reviewChecks": checks,
            "candidateNextActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a7-private-lint-contract-static-test-fixture-packet":
        raise ValueError("CPG-A8 must consume CPG-A7")
    summary = payload["summary"]
    if summary["reviewFailCount"] != 0:
        raise ValueError("static fixture review must have no failures")
    if summary["selectedActionId"] != "implementation_hold_boundary_packet":
        raise ValueError("CPG-A8 must select the implementation hold boundary packet")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateNextActions"]}
    if decisions["static_fixture_revision_packet"] != "parked":
        raise ValueError("static fixture revision must be parked")
    if decisions["static_test_execution"] != "blocked":
        raise ValueError("static test execution must be blocked")
    if decisions["lint_contract_implementation"] != "blocked":
        raise ValueError("lint contract implementation must be blocked")
    for key in [
        "implementationHoldBoundaryPacketCreated",
        "implementationHoldApproved",
        "lintContractStaticFixtureRevisionCreated",
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
        semantic_strength="private_static_fixture_review_no_implementation_hold_approval",
        source=f"python/results/cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector/cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "reviewPassCount": payload["summary"]["reviewPassCount"],
            "reviewFailCount": payload["summary"]["reviewFailCount"],
            "implementationHoldApproved": payload["summary"]["implementationHoldApproved"],
            "lintContractImplementationCreated": payload["summary"]["lintContractImplementationCreated"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A8 Private Lint Contract Static Fixture Review or Implementation Hold Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("review pass count", payload["summary"]["reviewPassCount"]),
            ("review fail count", payload["summary"]["reviewFailCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("implementation hold approved", payload["summary"]["implementationHoldApproved"]),
            ("lint contract implementation created", payload["summary"]["lintContractImplementationCreated"]),
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
    result_path = out_dir / f"cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector_{STAMP}.json"
    report_path = report_dir / f"cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector.json"
    feed_path = command_feed_dir / f"cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector",
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
    print("CPG_A8_PRIVATE_LINT_CONTRACT_STATIC_FIXTURE_REVIEW_OR_IMPLEMENTATION_HOLD_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
