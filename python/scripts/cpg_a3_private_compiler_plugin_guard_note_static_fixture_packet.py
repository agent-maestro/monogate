#!/usr/bin/env python3
"""CPG-A3 private compiler-plugin guard-note static fixture packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector as cpg_a2  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_compiler_plugin_guard_note_static_fixture_packet.v0"
STATUS = "CPG_A3_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_STATIC_FIXTURE_PACKET_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A4 private compiler-plugin static fixture review or executable lint contract selector"

TRUE_CLAIM_FLAGS = {
    "cpg_a2_consumed",
    "static_fixture_packet_created",
    "accepted_advisory_fixtures_recorded",
    "rejection_fixtures_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a2_consumed": True,
    "static_fixture_packet_created": True,
    "accepted_advisory_fixtures_recorded": True,
    "rejection_fixtures_recorded": True,
    "d109_hold_respected": True,
    "executable_lint_contract_created": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "lint_engine_implemented": False,
    "lint_engine_executed": False,
    "fixture_runner_implemented": False,
    "fixture_runner_executed": False,
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
    "CPG-A3 records static advisory/rejection fixtures only; it does not implement or execute a compiler plugin, lint engine, or fixture runner.",
    "CPG-A3 fixtures are review examples, not executable tests and not proof obligations.",
    "CPG-A3 does not authorize automatic rewrites, lowering, replacement, code generation, runtime mutation, public docs, or package release.",
    "CPG-A3 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A3 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def accepted_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "accepted_advisory_expression_surface_detection",
            "family": "accepted_advisory_expression_surface_detection",
            "sourceSnippet": "y = eml(x, exp(1))",
            "allowedOutput": "lint_warning",
            "expectedMessage": "Advisory detection only: candidate EML-shaped expression surface for human review.",
            "requiredBoundary": "no completeness, correctness, replacement, or target-readiness claim",
        },
        {
            "fixtureId": "accepted_guard_requirement_note",
            "family": "accepted_guard_requirement_note",
            "sourceSnippet": "z = exp(log(x))",
            "allowedOutput": "guard_checklist_item",
            "expectedMessage": "Guard reminder only: positive-domain guard such as 0 < x must be reviewed.",
            "requiredBoundary": "the guard note does not establish the guard or prove the expression",
        },
        {
            "fixtureId": "accepted_evidence_packet_link_hint",
            "family": "accepted_evidence_packet_link_hint",
            "sourceSnippet": "candidate = expm1_boundary_identity",
            "allowedOutput": "evidence_pointer",
            "expectedMessage": "Evidence pointer only: related private witness packet may exist.",
            "requiredBoundary": "no public readiness, completeness, or library coverage claim",
        },
    ]


def rejection_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "rejected_automatic_rewrite_or_lowering",
            "family": "rejected_automatic_rewrite_or_lowering",
            "sourceSnippet": "replace eml(x, exp(1)) with expm1(x)",
            "blockedOutput": "automatic_rewrite_or_lowering",
            "rejectionReason": "Automatic replacement/lowering would exceed advisory guard-note scope.",
            "blockedClaims": ["semantic_preservation_claim", "automatic_lowering_safety_claim"],
        },
        {
            "fixtureId": "rejected_runtime_performance_claim",
            "family": "rejected_runtime_performance_claim",
            "sourceSnippet": "eml rewrite saves runtime on this expression",
            "blockedOutput": "runtime_benchmark_claim",
            "rejectionReason": "Static advisory hints do not establish runtime measurements or savings.",
            "blockedClaims": ["runtime_performance_claim", "training_savings_claim"],
        },
        {
            "fixtureId": "rejected_public_readiness_claim",
            "family": "rejected_public_readiness_claim",
            "sourceSnippet": "publish plugin docs: EML compiler plugin is ready",
            "blockedOutput": "public_docs_or_copy",
            "rejectionReason": "Public/docs/package readiness requires separate explicit approval and release evidence.",
            "blockedClaims": ["public_readiness_claim", "public_package_release_claim", "compiler_correctness_claim"],
        },
    ]


def reviewer_questions() -> list[str]:
    return [
        "Are the accepted fixtures visibly advisory rather than executable behavior?",
        "Are the rejection fixtures strong enough to block automatic lowering and performance claims?",
        "Should CPG-A4 review these static fixtures before any executable lint contract is drafted?",
    ]


def build_payload() -> dict[str, Any]:
    selector = cpg_a2.build_payload()
    cpg_a2.validate_payload(selector)
    accepted = accepted_fixtures()
    rejected = rejection_fixtures()
    questions = reviewer_questions()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "acceptedFixtureCount": len(accepted),
        "rejectionFixtureCount": len(rejected),
        "fixtureCount": len(accepted) + len(rejected),
        "reviewerQuestionCount": len(questions),
        "executableLintContractCreated": False,
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
        artifact_id="cpg-a3-private-compiler-plugin-guard-note-static-fixture-packet",
        artifact_type="private_compiler_plugin_guard_note_static_fixture_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "acceptedFixtures": accepted,
            "rejectionFixtures": rejected,
            "reviewerQuestions": questions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a2-private-compiler-plugin-guard-note-fixture-or-lint-contract-selector":
        raise ValueError("CPG-A3 must consume CPG-A2")
    summary = payload["summary"]
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["acceptedFixtureCount"] != len(payload["acceptedFixtures"]):
        raise ValueError("accepted fixture count mismatch")
    if summary["rejectionFixtureCount"] != len(payload["rejectionFixtures"]):
        raise ValueError("rejection fixture count mismatch")
    if summary["fixtureCount"] != len(payload["acceptedFixtures"]) + len(payload["rejectionFixtures"]):
        raise ValueError("fixture count mismatch")
    accepted_families = {fixture["family"] for fixture in payload["acceptedFixtures"]}
    rejected_families = {fixture["family"] for fixture in payload["rejectionFixtures"]}
    if accepted_families != {
        "accepted_advisory_expression_surface_detection",
        "accepted_guard_requirement_note",
        "accepted_evidence_packet_link_hint",
    }:
        raise ValueError("unexpected accepted fixture families")
    if rejected_families != {
        "rejected_automatic_rewrite_or_lowering",
        "rejected_runtime_performance_claim",
        "rejected_public_readiness_claim",
    }:
        raise ValueError("unexpected rejection fixture families")
    for key in [
        "executableLintContractCreated",
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
        semantic_strength="private_static_guard_note_fixtures_no_lint_execution",
        source=f"python/results/cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet/cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "acceptedFixtureCount": payload["summary"]["acceptedFixtureCount"],
            "rejectionFixtureCount": payload["summary"]["rejectionFixtureCount"],
            "fixtureRunnerExecuted": payload["summary"]["fixtureRunnerExecuted"],
            "compilerPluginImplemented": payload["summary"]["compilerPluginImplemented"],
            "runtimePerformanceClaim": payload["summary"]["runtimePerformanceClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A3 Private Compiler-Plugin Guard-Note Static Fixture Packet",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("accepted fixture count", payload["summary"]["acceptedFixtureCount"]),
            ("rejection fixture count", payload["summary"]["rejectionFixtureCount"]),
            ("fixture runner executed", payload["summary"]["fixtureRunnerExecuted"]),
            ("compiler plugin implemented", payload["summary"]["compilerPluginImplemented"]),
            ("runtime performance claim", payload["summary"]["runtimePerformanceClaim"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Accepted Advisory Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: `{fixture['allowedOutput']}` - {fixture['expectedMessage']}"
                    for fixture in payload["acceptedFixtures"]
                ],
            ),
            (
                "Rejection Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: blocks `{fixture['blockedOutput']}` - {fixture['rejectionReason']}"
                    for fixture in payload["rejectionFixtures"]
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
    result_path = out_dir / f"cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet_{STAMP}.json"
    report_path = report_dir / f"cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet.json"
    feed_path = command_feed_dir / f"cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet")
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
    print("CPG_A3_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_STATIC_FIXTURE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
