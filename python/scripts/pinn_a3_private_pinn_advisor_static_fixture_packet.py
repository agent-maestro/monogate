#!/usr/bin/env python3
"""PINN-A3 private PINN advisor static fixture packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import pinn_a2_private_pinn_advisor_fixture_or_hold_selector as pinn_a2  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_pinn_advisor_static_fixture_packet.v0"
STATUS = "PINN_A3_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_PACKET_PASS"
NEXT_RECOMMENDED_ARTIFACT = "PINN-A4 private PINN advisor static fixture review or pause selector"

TRUE_CLAIM_FLAGS = {
    "pinn_a2_consumed",
    "static_fixture_packet_created",
    "accepted_fixtures_created",
    "rejection_fixtures_created",
    "blocked_claims_required",
    "implementation_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "pinn_a2_consumed": True,
    "static_fixture_packet_created": True,
    "accepted_fixtures_created": True,
    "rejection_fixtures_created": True,
    "blocked_claims_required": True,
    "implementation_blocked": True,
    "d109_hold_respected": True,
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
    "PINN-A3 creates static accepted/rejection fixture shapes only; it does not implement or execute a fixture runner.",
    "PINN-A3 does not implement or execute a PINN advisor, run training, invoke a solver, benchmark runtime, or evaluate scientific correctness.",
    "PINN-A3 fixtures are review examples for claim boundaries, not evidence that an advisor is useful or correct.",
    "PINN-A3 does not approve public docs, product readiness, solver correctness, training improvement, runtime performance, or broad EML advantage.",
    "PINN-A3 does not touch laptop-owned electronics repositories, start D110, or consume reviewer response.",
]

REQUIRED_CAVEATS = [
    "not_solver_correctness",
    "not_scientific_claim",
    "not_training_improvement",
    "cost_context_is_caveated",
    "human_review_required",
]

REQUIRED_BLOCKED_CLAIMS = [
    "PINN solver correctness",
    "scientific correctness",
    "PDE solution validity",
    "training improvement",
    "training cost savings",
    "estimator accuracy",
    "model quality improvement",
    "wall-clock runtime performance",
    "public product readiness",
    "broad EML advantage",
]

BASE_FALSE_CLAIM_FLAGS = {
    "pinn_diagnostic_claim": False,
    "scientific_correctness_claim": False,
    "pde_solution_validity_claim": False,
    "training_improvement_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "runtime_performance_claim": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "broad_eml_advantage_claim": False,
}


def accepted_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "accepted_loss_balance_warning_note",
            "expectedDisposition": "accept_private_advisory_note",
            "packet": {
                "advisor_note_id": "private-loss-balance-warning-example",
                "input_summary": {
                    "input_type": "loss_component_history_summary",
                    "equation_family": "harmonic_oscillator",
                    "missing_optional_context": ["regularization_loss_summary"],
                },
                "diagnostic_id": "loss_balance_warning",
                "advisory_text_shape": "Flag loss-scale imbalance for human review without interpreting solution quality.",
                "required_caveats": list(REQUIRED_CAVEATS),
                "blocked_claims": list(REQUIRED_BLOCKED_CLAIMS),
                "reviewer_next_steps": ["check loss scaling notes", "confirm no solution-quality wording"],
                "claim_flags": dict(BASE_FALSE_CLAIM_FLAGS),
            },
        },
        {
            "fixtureId": "accepted_residual_sampling_gap_note",
            "expectedDisposition": "accept_private_advisory_note",
            "packet": {
                "advisor_note_id": "private-residual-sampling-gap-example",
                "input_summary": {
                    "input_type": "residual_sampling_summary",
                    "equation_family": "burgers",
                    "missing_optional_context": ["known_singularity_notes"],
                },
                "diagnostic_id": "residual_sampling_gap",
                "advisory_text_shape": "Prompt human review of sparse/static collocation sampling without asserting coverage.",
                "required_caveats": list(REQUIRED_CAVEATS),
                "blocked_claims": list(REQUIRED_BLOCKED_CLAIMS),
                "reviewer_next_steps": ["review collocation strategy", "confirm no coverage guarantee"],
                "claim_flags": dict(BASE_FALSE_CLAIM_FLAGS),
            },
        },
        {
            "fixtureId": "accepted_cost_caveat_attachment_note",
            "expectedDisposition": "accept_private_advisory_note",
            "packet": {
                "advisor_note_id": "private-cost-caveat-attachment-example",
                "input_summary": {
                    "input_type": "cost_estimator_packet_summary",
                    "estimate_id": "private-static-expression-cost-shape-example",
                    "missing_optional_context": ["graph_cost_profile"],
                },
                "diagnostic_id": "cost_context_caveat_check",
                "advisory_text_shape": "Require cost caveats and blocked claims to travel with any cost-context note.",
                "required_caveats": list(REQUIRED_CAVEATS),
                "blocked_claims": list(REQUIRED_BLOCKED_CLAIMS),
                "reviewer_next_steps": ["verify cost caveat carriage", "confirm no wall-clock or savings claim"],
                "claim_flags": dict(BASE_FALSE_CLAIM_FLAGS),
            },
        },
    ]


def rejection_fixtures() -> list[dict[str, Any]]:
    accepted = accepted_fixtures()
    loss_packet = accepted[0]["packet"]
    sampling_packet = accepted[1]["packet"]
    cost_packet = accepted[2]["packet"]
    return [
        {
            "fixtureId": "missing_blocked_claims",
            "expectedDisposition": "reject",
            "mutation": "remove blocked_claims",
            "packet": {key: value for key, value in loss_packet.items() if key != "blocked_claims"},
        },
        {
            "fixtureId": "missing_required_caveats",
            "expectedDisposition": "reject",
            "mutation": "remove required_caveats",
            "packet": {key: value for key, value in loss_packet.items() if key != "required_caveats"},
        },
        {
            "fixtureId": "scientific_correctness_true",
            "expectedDisposition": "reject",
            "mutation": "set scientific_correctness_claim true",
            "packet": {
                **loss_packet,
                "claim_flags": {**loss_packet["claim_flags"], "scientific_correctness_claim": True},
            },
        },
        {
            "fixtureId": "training_improvement_true",
            "expectedDisposition": "reject",
            "mutation": "set training_improvement_claim true",
            "packet": {
                **sampling_packet,
                "claim_flags": {**sampling_packet["claim_flags"], "training_improvement_claim": True},
            },
        },
        {
            "fixtureId": "runtime_performance_true",
            "expectedDisposition": "reject",
            "mutation": "set runtime_performance_claim true",
            "packet": {
                **cost_packet,
                "claim_flags": {**cost_packet["claim_flags"], "runtime_performance_claim": True},
            },
        },
        {
            "fixtureId": "public_product_ready_true",
            "expectedDisposition": "reject",
            "mutation": "set public_product_ready true",
            "packet": {
                **cost_packet,
                "claim_flags": {**cost_packet["claim_flags"], "public_product_ready": True},
            },
        },
    ]


def reviewer_questions() -> list[dict[str, str]]:
    return [
        {
            "questionId": "accepted_fixtures_cover_safe_advice",
            "question": "Do the accepted fixtures cover useful advisor notes without implying solver or training claims?",
        },
        {
            "questionId": "rejection_fixtures_cover_claim_escape",
            "question": "Do the rejection fixtures catch the most likely claim-boundary escapes?",
        },
        {
            "questionId": "pause_or_review_next",
            "question": "Should PINN-A4 review these fixtures or pause the PINN advisor lane as sufficiently bounded?",
        },
    ]


def build_payload() -> dict[str, Any]:
    selector = pinn_a2.build_payload()
    pinn_a2.validate_payload(selector)
    accepted = accepted_fixtures()
    rejected = rejection_fixtures()
    questions = reviewer_questions()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "pinnA2SelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "acceptedFixtureCount": len(accepted),
        "rejectionFixtureCount": len(rejected),
        "staticFixtureCount": len(accepted) + len(rejected),
        "requiredCaveatCount": len(REQUIRED_CAVEATS),
        "requiredBlockedClaimCount": len(REQUIRED_BLOCKED_CLAIMS),
        "reviewerQuestionCount": len(questions),
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
        "staticFixturePacketCreated": True,
        "acceptedFixturesCreated": True,
        "rejectionFixturesCreated": True,
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
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="pinn-a3-private-pinn-advisor-static-fixture-packet",
        artifact_type="private_pinn_advisor_static_fixture_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "requiredCaveats": list(REQUIRED_CAVEATS),
            "requiredBlockedClaims": list(REQUIRED_BLOCKED_CLAIMS),
            "acceptedFixtures": accepted,
            "rejectionFixtures": rejected,
            "reviewerQuestions": questions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "pinn-a2-private-pinn-advisor-fixture-or-hold-selector":
        raise ValueError("PINN-A3 must consume PINN-A2")
    summary = payload["summary"]
    expected_counts = {
        "acceptedFixtureCount": len(payload["acceptedFixtures"]),
        "rejectionFixtureCount": len(payload["rejectionFixtures"]),
        "staticFixtureCount": len(payload["acceptedFixtures"]) + len(payload["rejectionFixtures"]),
        "requiredCaveatCount": len(payload["requiredCaveats"]),
        "requiredBlockedClaimCount": len(payload["requiredBlockedClaims"]),
        "reviewerQuestionCount": len(payload["reviewerQuestions"]),
    }
    for key, expected in expected_counts.items():
        if summary[key] != expected:
            raise ValueError(f"{key} mismatch")
    if summary["acceptedFixtureCount"] != 3:
        raise ValueError("expected three accepted fixtures")
    if summary["rejectionFixtureCount"] != 6:
        raise ValueError("expected six rejection fixtures")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    for fixture in payload["acceptedFixtures"]:
        packet = fixture["packet"]
        if fixture["expectedDisposition"] != "accept_private_advisory_note":
            raise ValueError("accepted fixture disposition mismatch")
        if packet["required_caveats"] != REQUIRED_CAVEATS:
            raise ValueError("accepted fixture must carry all required caveats")
        if packet["blocked_claims"] != REQUIRED_BLOCKED_CLAIMS:
            raise ValueError("accepted fixture must carry all blocked claims")
        for key, value in packet["claim_flags"].items():
            if value is not False:
                raise ValueError(f"accepted fixture claim flag {key} must remain false")
    rejection_ids = {fixture["fixtureId"] for fixture in payload["rejectionFixtures"]}
    expected_rejections = {
        "missing_blocked_claims",
        "missing_required_caveats",
        "scientific_correctness_true",
        "training_improvement_true",
        "runtime_performance_true",
        "public_product_ready_true",
    }
    if rejection_ids != expected_rejections:
        raise ValueError("unexpected rejection fixtures")
    for key in [
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
        semantic_strength="private_static_fixture_packet_no_execution_or_science_claim",
        source=f"python/results/pinn_a3_private_pinn_advisor_static_fixture_packet/pinn_a3_private_pinn_advisor_static_fixture_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="pinn_a3_private_pinn_advisor_static_fixture_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Review PINN-A3 fixtures or create PINN-A4 static fixture review/pause selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "acceptedFixtureCount": payload["summary"]["acceptedFixtureCount"],
            "rejectionFixtureCount": payload["summary"]["rejectionFixtureCount"],
            "staticFixtureCount": payload["summary"]["staticFixtureCount"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "fixtureRunnerCreated": payload["summary"]["fixtureRunnerCreated"],
            "staticFixturesExecuted": payload["summary"]["staticFixturesExecuted"],
            "advisorImplemented": payload["summary"]["advisorImplemented"],
            "advisorExecuted": payload["summary"]["advisorExecuted"],
            "scientificCorrectnessClaim": payload["summary"]["scientificCorrectnessClaim"],
            "trainingImprovementClaim": payload["summary"]["trainingImprovementClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PINN-A3 Private PINN Advisor Static Fixture Packet",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("accepted fixtures", payload["summary"]["acceptedFixtureCount"]),
            ("rejection fixtures", payload["summary"]["rejectionFixtureCount"]),
            ("static fixtures", payload["summary"]["staticFixtureCount"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
            ("fixture runner created", payload["summary"]["fixtureRunnerCreated"]),
            ("static fixtures executed", payload["summary"]["staticFixturesExecuted"]),
            ("advisor implemented", payload["summary"]["advisorImplemented"]),
            ("advisor executed", payload["summary"]["advisorExecuted"]),
            ("scientific correctness claim", payload["summary"]["scientificCorrectnessClaim"]),
            ("public readiness claim", payload["summary"]["publicReadinessClaim"]),
        ],
        sections=[
            (
                "Accepted Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: `{fixture['expectedDisposition']}`"
                    for fixture in payload["acceptedFixtures"]
                ],
            ),
            (
                "Rejection Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: `{fixture['expectedDisposition']}` - {fixture['mutation']}"
                    for fixture in payload["rejectionFixtures"]
                ],
            ),
            (
                "Reviewer Questions",
                [f"- `{item['questionId']}`: {item['question']}" for item in payload["reviewerQuestions"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"pinn_a3_private_pinn_advisor_static_fixture_packet_{STAMP}.json"
    report_path = report_dir / f"pinn_a3_private_pinn_advisor_static_fixture_packet_{STAMP}.md"
    evidence_path = evidence_dir / "pinn_a3_private_pinn_advisor_static_fixture_packet.json"
    feed_path = command_feed_dir / f"pinn_a3_private_pinn_advisor_static_fixture_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/pinn_a3_private_pinn_advisor_static_fixture_packet",
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
    print("PINN_A3_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
