#!/usr/bin/env python3
"""CPG-A4 private compiler-plugin static fixture review or lint-contract selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet as cpg_a3  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_compiler_plugin_static_fixture_review_or_lint_contract_selector.v0"
STATUS = "CPG_A4_PRIVATE_COMPILER_PLUGIN_STATIC_FIXTURE_REVIEW_OR_LINT_CONTRACT_SELECTOR_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A5 private executable lint contract boundary packet"

TRUE_CLAIM_FLAGS = {
    "cpg_a3_consumed",
    "static_fixture_review_created",
    "static_fixture_review_passed",
    "executable_lint_contract_boundary_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a3_consumed": True,
    "static_fixture_review_created": True,
    "static_fixture_review_passed": True,
    "executable_lint_contract_boundary_selected": True,
    "d109_hold_respected": True,
    "executable_lint_contract_created": False,
    "executable_lint_contract_executed": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "lint_engine_implemented": False,
    "lint_engine_executed": False,
    "fixture_runner_implemented": False,
    "fixture_runner_executed": False,
    "fixture_revision_created": False,
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
    "CPG-A4 is a private static-fixture review and next-action selector only.",
    "CPG-A4 selects a boundary packet for an executable lint contract; it does not create or execute that contract.",
    "CPG-A4 does not implement or execute a compiler plugin, lint engine, fixture runner, rewrite engine, code generator, or runtime lowering path.",
    "CPG-A4 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A4 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def review_checks(payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "checkId": "accepted_fixture_count",
            "status": "pass" if payload["summary"]["acceptedFixtureCount"] == 3 else "fail",
            "reason": "CPG-A3 records the three selected accepted advisory fixture families.",
        },
        {
            "checkId": "rejection_fixture_count",
            "status": "pass" if payload["summary"]["rejectionFixtureCount"] == 3 else "fail",
            "reason": "CPG-A3 records the three selected rejection fixture families.",
        },
        {
            "checkId": "no_fixture_runner_execution",
            "status": "pass" if payload["summary"]["fixtureRunnerExecuted"] is False else "fail",
            "reason": "Static fixtures were not executed.",
        },
        {
            "checkId": "no_plugin_or_lint_execution",
            "status": "pass" if payload["summary"]["compilerPluginExecuted"] is False and payload["summary"]["lintEngineExecuted"] is False else "fail",
            "reason": "No plugin or lint engine execution is recorded.",
        },
        {
            "checkId": "forbidden_claims_false",
            "status": "pass" if payload["summary"]["runtimePerformanceClaim"] is False and payload["summary"]["compilerCorrectnessClaim"] is False else "fail",
            "reason": "Runtime-performance and compiler-correctness claims remain false.",
        },
        {
            "checkId": "next_action_points_to_review",
            "status": "pass" if "CPG-A4" in payload["summary"]["nextRecommendedArtifact"] else "fail",
            "reason": "CPG-A3 points to static fixture review before executable lint-contract work.",
        },
    ]


def candidate_next_actions() -> list[dict[str, str]]:
    return [
        {
            "actionId": "executable_lint_contract_boundary_packet",
            "decision": "selected_next",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "The static fixtures are structurally adequate for drafting a boundary-only executable lint contract packet.",
        },
        {
            "actionId": "static_fixture_revision_packet",
            "decision": "parked",
            "nextArtifact": "CPG-A5-alt private static fixture revision packet",
            "reason": "No structural fixture issue was found in this selector.",
        },
        {
            "actionId": "compiler_plugin_implementation",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Implementation remains blocked until contract boundary and execution gates are reviewed.",
        },
        {
            "actionId": "public_docs_or_package",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Public product/docs/package work requires separate approval and readiness evidence.",
        },
    ]


def build_payload() -> dict[str, Any]:
    static_fixtures = cpg_a3.build_payload()
    cpg_a3.validate_payload(static_fixtures)
    checks = review_checks(static_fixtures)
    actions = candidate_next_actions()
    selected = [action for action in actions if action["decision"] == "selected_next"]
    summary = {
        "sourceArtifact": static_fixtures["artifactId"],
        "reviewCheckCount": len(checks),
        "reviewPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "reviewFailCount": sum(1 for check in checks if check["status"] != "pass"),
        "candidateActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "executableLintContractCreated": False,
        "executableLintContractExecuted": False,
        "compilerPluginImplemented": False,
        "compilerPluginExecuted": False,
        "lintEngineImplemented": False,
        "lintEngineExecuted": False,
        "fixtureRunnerImplemented": False,
        "fixtureRunnerExecuted": False,
        "fixtureRevisionCreated": False,
        "compilerCorrectnessClaim": False,
        "semanticPreservationClaim": False,
        "automaticLoweringSafetyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="cpg-a4-private-compiler-plugin-static-fixture-review-or-lint-contract-selector",
        artifact_type="private_compiler_plugin_static_fixture_review_or_lint_contract_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": static_fixtures["artifactId"],
            "reviewChecks": checks,
            "candidateNextActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a3-private-compiler-plugin-guard-note-static-fixture-packet":
        raise ValueError("CPG-A4 must consume CPG-A3")
    summary = payload["summary"]
    if summary["reviewFailCount"] != 0:
        raise ValueError("static fixture review must have no failures")
    if summary["selectedActionId"] != "executable_lint_contract_boundary_packet":
        raise ValueError("CPG-A4 must select the lint contract boundary packet")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateNextActions"]}
    if decisions["static_fixture_revision_packet"] != "parked":
        raise ValueError("fixture revision must be parked")
    if decisions["compiler_plugin_implementation"] != "blocked":
        raise ValueError("compiler plugin implementation must be blocked")
    for key in [
        "executableLintContractCreated",
        "executableLintContractExecuted",
        "compilerPluginImplemented",
        "compilerPluginExecuted",
        "lintEngineImplemented",
        "lintEngineExecuted",
        "fixtureRunnerImplemented",
        "fixtureRunnerExecuted",
        "fixtureRevisionCreated",
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
        semantic_strength="private_static_fixture_review_no_lint_contract_execution",
        source=f"python/results/cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector/cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector_feed",
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
            "executableLintContractCreated": payload["summary"]["executableLintContractCreated"],
            "compilerPluginImplemented": payload["summary"]["compilerPluginImplemented"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A4 Private Compiler-Plugin Static Fixture Review or Lint-Contract Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("review pass count", payload["summary"]["reviewPassCount"]),
            ("review fail count", payload["summary"]["reviewFailCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("executable lint contract created", payload["summary"]["executableLintContractCreated"]),
            ("compiler plugin implemented", payload["summary"]["compilerPluginImplemented"]),
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
    result_path = out_dir / f"cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector_{STAMP}.json"
    report_path = report_dir / f"cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector.json"
    feed_path = command_feed_dir / f"cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector")
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
    print("CPG_A4_PRIVATE_COMPILER_PLUGIN_STATIC_FIXTURE_REVIEW_OR_LINT_CONTRACT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
