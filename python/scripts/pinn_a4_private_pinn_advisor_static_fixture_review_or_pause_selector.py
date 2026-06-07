#!/usr/bin/env python3
"""PINN-A4 private PINN advisor static fixture review or pause selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import pinn_a3_private_pinn_advisor_static_fixture_packet as pinn_a3  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_pinn_advisor_static_fixture_review_or_pause_selector.v0"
STATUS = "PINN_A4_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_REVIEW_OR_PAUSE_SELECTOR_PASS"
NEXT_RECOMMENDED_ARTIFACT = "pause PINN advisor lane as sufficiently bounded"

TRUE_CLAIM_FLAGS = {
    "pinn_a3_consumed",
    "static_fixture_review_created",
    "static_fixture_review_passed",
    "pause_lane_selected",
    "implementation_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "pinn_a3_consumed": True,
    "static_fixture_review_created": True,
    "static_fixture_review_passed": True,
    "pause_lane_selected": True,
    "implementation_blocked": True,
    "d109_hold_respected": True,
    "static_fixture_revision_created": False,
    "fixture_runner_created": False,
    "static_fixtures_executed": False,
    "pinn_advisor_implemented": False,
    "pinn_advisor_executed": False,
    "pinn_training_executed": False,
    "pinn_solver_invoked": False,
    "pinn_diagnostic_claim": False,
    "scientific_correctness_claim": False,
    "pde_solution_validity_claim": False,
    "training_improvement_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "model_quality_claim": False,
    "runtime_performance_claim": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "sdk_stability_claim": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_docs_created": False,
    "public_package_release_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PINN-A4 is a private static-fixture review and pause selector only.",
    "PINN-A4 pauses the PINN advisor lane as sufficiently bounded; it does not approve implementation.",
    "PINN-A4 does not create or execute a fixture runner, implement or execute a PINN advisor, run training, invoke a solver, benchmark runtime, or evaluate scientific correctness.",
    "PINN-A4 does not approve public docs, product readiness, solver correctness, training improvement, runtime performance, or broad EML advantage.",
    "PINN-A4 does not touch laptop-owned electronics repositories, start D110, or consume reviewer response.",
]


def review_checks(fixtures: dict[str, Any]) -> list[dict[str, str]]:
    accepted_ids = {fixture["fixtureId"] for fixture in fixtures["acceptedFixtures"]}
    rejection_ids = {fixture["fixtureId"] for fixture in fixtures["rejectionFixtures"]}
    accepted_claim_flags_ok = all(
        value is False
        for fixture in fixtures["acceptedFixtures"]
        for value in fixture["packet"]["claim_flags"].values()
    )
    return [
        {
            "checkId": "accepted_fixture_count",
            "status": "pass" if fixtures["summary"]["acceptedFixtureCount"] == 3 else "fail",
            "reason": "PINN-A3 records three accepted private-advisory fixture shapes.",
        },
        {
            "checkId": "rejection_fixture_count",
            "status": "pass" if fixtures["summary"]["rejectionFixtureCount"] == 6 else "fail",
            "reason": "PINN-A3 records six rejection fixture shapes.",
        },
        {
            "checkId": "accepted_fixture_coverage",
            "status": "pass" if accepted_ids == {
                "accepted_loss_balance_warning_note",
                "accepted_residual_sampling_gap_note",
                "accepted_cost_caveat_attachment_note",
            } else "fail",
            "reason": "Accepted fixtures cover loss-balance, residual-sampling, and cost-caveat note shapes.",
        },
        {
            "checkId": "rejection_fixture_coverage",
            "status": "pass" if rejection_ids == {
                "missing_blocked_claims",
                "missing_required_caveats",
                "scientific_correctness_true",
                "training_improvement_true",
                "runtime_performance_true",
                "public_product_ready_true",
            } else "fail",
            "reason": "Rejection fixtures cover missing boundaries plus science/training/runtime/public claim escapes.",
        },
        {
            "checkId": "accepted_claim_flags_false",
            "status": "pass" if accepted_claim_flags_ok else "fail",
            "reason": "Accepted fixture packets carry false claim flags only.",
        },
        {
            "checkId": "runner_and_execution_absent",
            "status": "pass" if fixtures["summary"]["fixtureRunnerCreated"] is False and fixtures["summary"]["staticFixturesExecuted"] is False else "fail",
            "reason": "PINN-A3 creates fixture shapes only.",
        },
        {
            "checkId": "science_public_claims_false",
            "status": "pass" if fixtures["summary"]["scientificCorrectnessClaim"] is False and fixtures["summary"]["publicReadinessClaim"] is False else "fail",
            "reason": "Scientific correctness and public readiness claims remain false.",
        },
    ]


def candidate_actions() -> list[dict[str, Any]]:
    return [
        {
            "actionId": "pause_pinn_advisor_lane",
            "decision": "selected",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "The lane has a bounded brief, selector, and static fixture packet; implementation requires explicit future need.",
        },
        {
            "actionId": "static_fixture_revision",
            "decision": "parked",
            "nextArtifact": "PINN-A4-alt private PINN advisor fixture revision packet",
            "reason": "No fixture-review failure was recorded.",
        },
        {
            "actionId": "fixture_runner",
            "decision": "blocked",
            "nextArtifact": "future fixture runner only after explicit approval",
            "reason": "A runner would exceed the static fixture boundary.",
        },
        {
            "actionId": "advisor_implementation",
            "decision": "blocked",
            "nextArtifact": "future advisor implementation gate only after explicit product need and review",
            "reason": "No implementation approval, science evidence, or product need exists.",
        },
        {
            "actionId": "public_docs_gate",
            "decision": "blocked",
            "nextArtifact": "future public copy approval gate only after private review",
            "reason": "Public docs could imply product readiness or solver/training claims.",
        },
    ]


def build_payload() -> dict[str, Any]:
    fixtures = pinn_a3.build_payload()
    pinn_a3.validate_payload(fixtures)
    checks = review_checks(fixtures)
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    summary = {
        "sourceArtifact": fixtures["artifactId"],
        "reviewCheckCount": len(checks),
        "reviewPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "reviewFailCount": sum(1 for check in checks if check["status"] != "pass"),
        "candidateActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "lanePausedAsSufficientlyBounded": True,
        "staticFixtureRevisionCreated": False,
        "fixtureRunnerCreated": False,
        "staticFixturesExecuted": False,
        "advisorImplemented": False,
        "advisorExecuted": False,
        "trainingExecuted": False,
        "solverInvoked": False,
        "scientificCorrectnessClaim": False,
        "trainingImprovementClaim": False,
        "runtimePerformanceClaim": False,
        "publicReadinessClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="pinn-a4-private-pinn-advisor-static-fixture-review-or-pause-selector",
        artifact_type="private_pinn_advisor_static_fixture_review_or_pause_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": fixtures["artifactId"],
            "reviewChecks": checks,
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "pinn-a3-private-pinn-advisor-static-fixture-packet":
        raise ValueError("PINN-A4 must consume PINN-A3")
    summary = payload["summary"]
    if summary["reviewFailCount"] != 0:
        raise ValueError("fixture review must have no failures")
    if summary["selectedActionId"] != "pause_pinn_advisor_lane":
        raise ValueError("PINN-A4 should select lane pause")
    if summary["lanePausedAsSufficientlyBounded"] is not True:
        raise ValueError("PINN lane should be marked paused as sufficiently bounded")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    if decisions != {
        "pause_pinn_advisor_lane": "selected",
        "static_fixture_revision": "parked",
        "fixture_runner": "blocked",
        "advisor_implementation": "blocked",
        "public_docs_gate": "blocked",
    }:
        raise ValueError("unexpected candidate decisions")
    for key in [
        "staticFixtureRevisionCreated",
        "fixtureRunnerCreated",
        "staticFixturesExecuted",
        "advisorImplemented",
        "advisorExecuted",
        "trainingExecuted",
        "solverInvoked",
        "scientificCorrectnessClaim",
        "trainingImprovementClaim",
        "runtimePerformanceClaim",
        "publicReadinessClaim",
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
        semantic_strength="private_static_fixture_review_pause_no_implementation",
        source=f"python/results/pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector/pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="PINN advisor lane paused as sufficiently bounded; return to product roadmap selector or explicit bounded request.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "reviewPassCount": payload["summary"]["reviewPassCount"],
            "reviewFailCount": payload["summary"]["reviewFailCount"],
            "lanePausedAsSufficientlyBounded": payload["summary"]["lanePausedAsSufficientlyBounded"],
            "fixtureRunnerCreated": payload["summary"]["fixtureRunnerCreated"],
            "advisorImplemented": payload["summary"]["advisorImplemented"],
            "advisorExecuted": payload["summary"]["advisorExecuted"],
            "scientificCorrectnessClaim": payload["summary"]["scientificCorrectnessClaim"],
            "trainingImprovementClaim": payload["summary"]["trainingImprovementClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PINN-A4 Private PINN Advisor Static Fixture Review Or Pause Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("review pass count", payload["summary"]["reviewPassCount"]),
            ("review fail count", payload["summary"]["reviewFailCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("lane paused", payload["summary"]["lanePausedAsSufficientlyBounded"]),
            ("fixture runner created", payload["summary"]["fixtureRunnerCreated"]),
            ("advisor implemented", payload["summary"]["advisorImplemented"]),
            ("advisor executed", payload["summary"]["advisorExecuted"]),
            ("scientific correctness claim", payload["summary"]["scientificCorrectnessClaim"]),
            ("public readiness claim", payload["summary"]["publicReadinessClaim"]),
        ],
        sections=[
            (
                "Review Checks",
                [f"- `{check['checkId']}`: `{check['status']}` - {check['reason']}" for check in payload["reviewChecks"]],
            ),
            (
                "Candidate Actions",
                [
                    f"- `{action['actionId']}`: `{action['decision']}` - {action['reason']}"
                    for action in payload["candidateActions"]
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
    result_path = out_dir / f"pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector_{STAMP}.json"
    report_path = report_dir / f"pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector_{STAMP}.md"
    evidence_path = evidence_dir / "pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector.json"
    feed_path = command_feed_dir / f"pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector",
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
    print("PINN_A4_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_REVIEW_OR_PAUSE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
