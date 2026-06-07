#!/usr/bin/env python3
"""CPG-A7 private lint contract static test fixture packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a6_private_lint_contract_boundary_review_or_static_test_selector as cpg_a6  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_lint_contract_static_test_fixture_packet.v0"
STATUS = "CPG_A7_PRIVATE_LINT_CONTRACT_STATIC_TEST_FIXTURE_PACKET_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A8 private lint contract static fixture review or implementation hold selector"

TRUE_CLAIM_FLAGS = {
    "cpg_a6_consumed",
    "lint_contract_static_fixture_packet_created",
    "accepted_static_fixtures_recorded",
    "rejection_static_fixtures_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a6_consumed": True,
    "lint_contract_static_fixture_packet_created": True,
    "accepted_static_fixtures_recorded": True,
    "rejection_static_fixtures_recorded": True,
    "d109_hold_respected": True,
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
    "CPG-A7 records static fixture shapes only; it does not create or execute executable static tests.",
    "CPG-A7 fixtures are private review examples, not a lint engine, compiler plugin, or proof obligation.",
    "CPG-A7 does not implement or execute a compiler plugin, lint engine, lint contract, fixture runner, rewrite engine, code generator, or runtime lowering path.",
    "CPG-A7 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A7 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def accepted_static_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "accepted_boundary_advisory_notice",
            "input": {
                "source_snippet": "y = eml(x, exp(1))",
                "expression_family": "expm1_boundary",
                "evidence_pointer": "MachLib.Real.expm1_boundary_identity_witness",
                "guard_context": "no extra real-domain guard recorded",
            },
            "expectedOutputKind": "advisory_notice",
            "expectedBoundary": "human review note only; no rewrite or lowering instruction",
        },
        {
            "fixtureId": "accepted_positive_guard_checklist_item",
            "input": {
                "source_snippet": "z = exp(log(x))",
                "expression_family": "positive_log_exp_guard",
                "evidence_pointer": "MachLib.Real.positive_log_exp_roundtrip_witness",
                "guard_context": "0 < x must be established by caller/reviewer",
            },
            "expectedOutputKind": "guard_checklist_item",
            "expectedBoundary": "guard reminder only; no claim that the guard is proven",
        },
        {
            "fixtureId": "accepted_private_evidence_pointer",
            "input": {
                "source_snippet": "candidate = expm1_boundary_identity",
                "expression_family": "expm1_boundary",
                "evidence_pointer": "reports/evidence_packets/pubmath_or_d_series_expm1_boundary",
                "guard_context": "reviewer must inspect private packet before use",
            },
            "expectedOutputKind": "evidence_pointer",
            "expectedBoundary": "pointer for reviewer follow-up only; no public readiness claim",
        },
        {
            "fixtureId": "accepted_blocked_claim_notice",
            "input": {
                "source_snippet": "publish: compiler plugin accelerates this rewrite",
                "expression_family": "performance_claim_request",
                "evidence_pointer": "",
                "guard_context": "no benchmark protocol supplied",
            },
            "expectedOutputKind": "blocked_claim_notice",
            "expectedBoundary": "explicitly block performance/public/compiler claims",
        },
    ]


def rejection_static_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "rejected_automatic_rewrite_output",
            "input": "replace eml(x, exp(1)) with expm1(x)",
            "blockedOutputKind": "automatic_rewrite",
            "requiredRejectionReason": "Automatic rewrite exceeds advisory lint-contract scope.",
            "blockedClaims": ["semantic_preservation_claim", "automatic_lowering_safety_claim"],
        },
        {
            "fixtureId": "rejected_runtime_speedup_output",
            "input": "this lint rule proves a speedup",
            "blockedOutputKind": "runtime_speedup",
            "requiredRejectionReason": "No benchmark protocol or runtime measurement is recorded.",
            "blockedClaims": ["runtime_performance_claim", "training_savings_claim"],
        },
        {
            "fixtureId": "rejected_public_package_ready_output",
            "input": "EML compiler plugin package is ready to publish",
            "blockedOutputKind": "package_release_ready",
            "requiredRejectionReason": "Public/package readiness requires separate approval and evidence.",
            "blockedClaims": ["public_readiness_claim", "public_package_release_claim", "sdk_stability_claim"],
        },
        {
            "fixtureId": "rejected_guard_proven_output",
            "input": "the guard 0 < x is proven by the lint contract",
            "blockedOutputKind": "guard_proven",
            "requiredRejectionReason": "The lint-contract boundary may surface guard notes but cannot prove guards.",
            "blockedClaims": ["compiler_correctness_claim", "broad_eml_advantage_claim"],
        },
    ]


def reviewer_questions() -> list[str]:
    return [
        "Do the accepted static fixtures exercise every allowed output kind from CPG-A5?",
        "Do the rejection static fixtures cover the four rejection obligations from CPG-A5?",
        "Should CPG-A8 review these fixture shapes before any executable static tests are drafted?",
    ]


def build_payload() -> dict[str, Any]:
    selector = cpg_a6.build_payload()
    cpg_a6.validate_payload(selector)
    accepted = accepted_static_fixtures()
    rejected = rejection_static_fixtures()
    questions = reviewer_questions()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "acceptedStaticFixtureCount": len(accepted),
        "rejectionStaticFixtureCount": len(rejected),
        "staticFixtureCount": len(accepted) + len(rejected),
        "reviewerQuestionCount": len(questions),
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
        artifact_id="cpg-a7-private-lint-contract-static-test-fixture-packet",
        artifact_type="private_lint_contract_static_test_fixture_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "acceptedStaticFixtures": accepted,
            "rejectionStaticFixtures": rejected,
            "reviewerQuestions": questions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a6-private-lint-contract-boundary-review-or-static-test-selector":
        raise ValueError("CPG-A7 must consume CPG-A6")
    summary = payload["summary"]
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["acceptedStaticFixtureCount"] != len(payload["acceptedStaticFixtures"]):
        raise ValueError("accepted fixture count mismatch")
    if summary["rejectionStaticFixtureCount"] != len(payload["rejectionStaticFixtures"]):
        raise ValueError("rejection fixture count mismatch")
    if summary["staticFixtureCount"] != len(payload["acceptedStaticFixtures"]) + len(payload["rejectionStaticFixtures"]):
        raise ValueError("static fixture count mismatch")
    if {fixture["expectedOutputKind"] for fixture in payload["acceptedStaticFixtures"]} != {
        "advisory_notice",
        "guard_checklist_item",
        "evidence_pointer",
        "blocked_claim_notice",
    }:
        raise ValueError("accepted fixtures must cover allowed output kinds")
    if {fixture["blockedOutputKind"] for fixture in payload["rejectionStaticFixtures"]} != {
        "automatic_rewrite",
        "runtime_speedup",
        "package_release_ready",
        "guard_proven",
    }:
        raise ValueError("rejection fixtures must cover blocked output kinds")
    for key in [
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
        semantic_strength="private_static_fixture_packet_no_static_test_execution",
        source=f"python/results/cpg_a7_private_lint_contract_static_test_fixture_packet/cpg_a7_private_lint_contract_static_test_fixture_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a7_private_lint_contract_static_test_fixture_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "acceptedStaticFixtureCount": payload["summary"]["acceptedStaticFixtureCount"],
            "rejectionStaticFixtureCount": payload["summary"]["rejectionStaticFixtureCount"],
            "lintContractStaticTestsCreated": payload["summary"]["lintContractStaticTestsCreated"],
            "lintContractStaticTestsExecuted": payload["summary"]["lintContractStaticTestsExecuted"],
            "lintEngineImplemented": payload["summary"]["lintEngineImplemented"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A7 Private Lint Contract Static Test Fixture Packet",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("accepted static fixture count", payload["summary"]["acceptedStaticFixtureCount"]),
            ("rejection static fixture count", payload["summary"]["rejectionStaticFixtureCount"]),
            ("static fixture count", payload["summary"]["staticFixtureCount"]),
            ("static tests created", payload["summary"]["lintContractStaticTestsCreated"]),
            ("static tests executed", payload["summary"]["lintContractStaticTestsExecuted"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Accepted Static Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: `{fixture['expectedOutputKind']}` - {fixture['expectedBoundary']}"
                    for fixture in payload["acceptedStaticFixtures"]
                ],
            ),
            (
                "Rejection Static Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: block `{fixture['blockedOutputKind']}` - {fixture['requiredRejectionReason']}"
                    for fixture in payload["rejectionStaticFixtures"]
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
    result_path = out_dir / f"cpg_a7_private_lint_contract_static_test_fixture_packet_{STAMP}.json"
    report_path = report_dir / f"cpg_a7_private_lint_contract_static_test_fixture_packet_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a7_private_lint_contract_static_test_fixture_packet.json"
    feed_path = command_feed_dir / f"cpg_a7_private_lint_contract_static_test_fixture_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/cpg_a7_private_lint_contract_static_test_fixture_packet",
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
    print("CPG_A7_PRIVATE_LINT_CONTRACT_STATIC_TEST_FIXTURE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
