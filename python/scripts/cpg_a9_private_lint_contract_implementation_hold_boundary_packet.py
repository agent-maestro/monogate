#!/usr/bin/env python3
"""CPG-A9 private lint contract implementation hold boundary packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a8_private_lint_contract_static_fixture_review_or_implementation_hold_selector as cpg_a8  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_lint_contract_implementation_hold_boundary_packet.v0"
STATUS = "CPG_A9_PRIVATE_LINT_CONTRACT_IMPLEMENTATION_HOLD_BOUNDARY_PACKET_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A10 private lint contract implementation hold review or pause selector"

TRUE_CLAIM_FLAGS = {
    "cpg_a8_consumed",
    "implementation_hold_boundary_packet_created",
    "implementation_preconditions_recorded",
    "blocked_implementation_surfaces_recorded",
    "review_questions_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a8_consumed": True,
    "implementation_hold_boundary_packet_created": True,
    "implementation_preconditions_recorded": True,
    "blocked_implementation_surfaces_recorded": True,
    "review_questions_recorded": True,
    "d109_hold_respected": True,
    "implementation_hold_approved": False,
    "implementation_scope_approved": False,
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
    "CPG-A9 is a private implementation-hold boundary packet only; it does not approve implementation.",
    "CPG-A9 records preconditions and blockers for possible future implementation scoping.",
    "CPG-A9 does not create or execute static tests, lint contracts, compiler plugins, lint engines, fixture runners, rewrite engines, code generators, or runtime lowering paths.",
    "CPG-A9 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A9 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def implementation_preconditions() -> list[dict[str, str]]:
    return [
        {
            "preconditionId": "review_cpg_a7_static_fixtures",
            "requiredBefore": "any implementation scope approval",
            "reason": "Fixture shapes must be reviewed as private examples before they can guide implementation.",
        },
        {
            "preconditionId": "draft_executable_static_test_contract",
            "requiredBefore": "any lint engine execution",
            "reason": "An executable static-test contract must exist before behavior can be executed.",
        },
        {
            "preconditionId": "separate_reviewer_approval_required",
            "requiredBefore": "any implementation branch",
            "reason": "A human/reviewer decision must explicitly approve scope before code work starts.",
        },
        {
            "preconditionId": "public_docs_gate_required",
            "requiredBefore": "any public docs or package copy",
            "reason": "Public-facing copy requires separate readiness evidence and approval.",
        },
    ]


def blocked_implementation_surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surfaceId": "compiler_plugin_runtime_behavior",
            "blockedWork": ["compiler_plugin_implemented", "compiler_plugin_executed"],
            "reason": "Compiler plugin behavior is outside this boundary packet.",
        },
        {
            "surfaceId": "lint_engine_execution",
            "blockedWork": ["lint_engine_implemented", "lint_engine_executed", "executable_lint_contract_executed"],
            "reason": "No executable lint contract or test harness has been approved.",
        },
        {
            "surfaceId": "automatic_rewrite_or_lowering",
            "blockedWork": ["automatic_rewrite_enabled", "runtime_lowering_changed", "code_generation_claim"],
            "reason": "No semantic-preservation or lowering-safety proof is recorded.",
        },
        {
            "surfaceId": "public_release_surface",
            "blockedWork": ["public_readiness_claim", "public_package_release_claim", "sdk_stability_claim"],
            "reason": "Public release and SDK stability are separate lanes with separate evidence needs.",
        },
    ]


def reviewer_questions() -> list[str]:
    return [
        "Should the implementation hold remain fully closed until executable static-test fixtures exist?",
        "If implementation is ever scoped, should it be limited to report rendering with no AST rewrite hooks?",
        "What exact reviewer approval text would be required before any lint engine code is created?",
        "Should CPG-A10 pause the compiler-plugin lane as sufficiently bounded instead of moving toward implementation?",
    ]


def build_payload() -> dict[str, Any]:
    selector = cpg_a8.build_payload()
    cpg_a8.validate_payload(selector)
    preconditions = implementation_preconditions()
    blocked = blocked_implementation_surfaces()
    questions = reviewer_questions()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "implementationPreconditionCount": len(preconditions),
        "blockedImplementationSurfaceCount": len(blocked),
        "reviewerQuestionCount": len(questions),
        "implementationHoldApproved": False,
        "implementationScopeApproved": False,
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
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="cpg-a9-private-lint-contract-implementation-hold-boundary-packet",
        artifact_type="private_lint_contract_implementation_hold_boundary_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "implementationPreconditions": preconditions,
            "blockedImplementationSurfaces": blocked,
            "reviewerQuestions": questions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a8-private-lint-contract-static-fixture-review-or-implementation-hold-selector":
        raise ValueError("CPG-A9 must consume CPG-A8")
    summary = payload["summary"]
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["implementationPreconditionCount"] != len(payload["implementationPreconditions"]):
        raise ValueError("precondition count mismatch")
    if summary["blockedImplementationSurfaceCount"] != len(payload["blockedImplementationSurfaces"]):
        raise ValueError("blocked surface count mismatch")
    if {item["preconditionId"] for item in payload["implementationPreconditions"]} != {
        "review_cpg_a7_static_fixtures",
        "draft_executable_static_test_contract",
        "separate_reviewer_approval_required",
        "public_docs_gate_required",
    }:
        raise ValueError("unexpected implementation preconditions")
    if {item["surfaceId"] for item in payload["blockedImplementationSurfaces"]} != {
        "compiler_plugin_runtime_behavior",
        "lint_engine_execution",
        "automatic_rewrite_or_lowering",
        "public_release_surface",
    }:
        raise ValueError("unexpected blocked implementation surfaces")
    for key in [
        "implementationHoldApproved",
        "implementationScopeApproved",
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
        semantic_strength="private_implementation_hold_boundary_no_approval",
        source=f"python/results/cpg_a9_private_lint_contract_implementation_hold_boundary_packet/cpg_a9_private_lint_contract_implementation_hold_boundary_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a9_private_lint_contract_implementation_hold_boundary_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "implementationPreconditionCount": payload["summary"]["implementationPreconditionCount"],
            "blockedImplementationSurfaceCount": payload["summary"]["blockedImplementationSurfaceCount"],
            "implementationHoldApproved": payload["summary"]["implementationHoldApproved"],
            "implementationScopeApproved": payload["summary"]["implementationScopeApproved"],
            "lintContractImplementationCreated": payload["summary"]["lintContractImplementationCreated"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A9 Private Lint Contract Implementation Hold Boundary Packet",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("implementation precondition count", payload["summary"]["implementationPreconditionCount"]),
            ("blocked implementation surface count", payload["summary"]["blockedImplementationSurfaceCount"]),
            ("implementation hold approved", payload["summary"]["implementationHoldApproved"]),
            ("implementation scope approved", payload["summary"]["implementationScopeApproved"]),
            ("lint contract implementation created", payload["summary"]["lintContractImplementationCreated"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Implementation Preconditions",
                [
                    f"- `{item['preconditionId']}`: required before `{item['requiredBefore']}` - {item['reason']}"
                    for item in payload["implementationPreconditions"]
                ],
            ),
            (
                "Blocked Implementation Surfaces",
                [
                    f"- `{item['surfaceId']}`: blocks {', '.join(item['blockedWork'])}. Reason: {item['reason']}"
                    for item in payload["blockedImplementationSurfaces"]
                ],
            ),
            ("Reviewer Questions", [f"- {question}" for question in payload["reviewerQuestions"]]),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"cpg_a9_private_lint_contract_implementation_hold_boundary_packet_{STAMP}.json"
    report_path = report_dir / f"cpg_a9_private_lint_contract_implementation_hold_boundary_packet_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a9_private_lint_contract_implementation_hold_boundary_packet.json"
    feed_path = command_feed_dir / f"cpg_a9_private_lint_contract_implementation_hold_boundary_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/cpg_a9_private_lint_contract_implementation_hold_boundary_packet",
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
    print("CPG_A9_PRIVATE_LINT_CONTRACT_IMPLEMENTATION_HOLD_BOUNDARY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
