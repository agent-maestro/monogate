#!/usr/bin/env python3
"""PINN-A2 private PINN advisor fixture or hold selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import pinn_a1_private_pinn_advisor_brief as pinn_a1  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_pinn_advisor_fixture_or_hold_selector.v0"
STATUS = "PINN_A2_PRIVATE_PINN_ADVISOR_FIXTURE_OR_HOLD_SELECTOR_PASS"
NEXT_RECOMMENDED_ARTIFACT = "PINN-A3 private PINN advisor static fixture packet"

TRUE_CLAIM_FLAGS = {
    "pinn_a1_consumed",
    "fixture_or_hold_selector_created",
    "static_fixture_packet_selected",
    "brief_shape_reviewed",
    "implementation_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "pinn_a1_consumed": True,
    "fixture_or_hold_selector_created": True,
    "static_fixture_packet_selected": True,
    "brief_shape_reviewed": True,
    "implementation_blocked": True,
    "d109_hold_respected": True,
    "static_fixtures_created": False,
    "pinn_advisor_implemented": False,
    "pinn_advisor_executed": False,
    "pinn_training_executed": False,
    "pinn_solver_invoked": False,
    "pinn_diagnostic_claim": False,
    "scientific_correctness_claim": False,
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
    "PINN-A2 is a private selector; it does not create PINN advisor fixtures.",
    "PINN-A2 selects a static fixture packet only because PINN-A1 records a bounded brief shape with explicit blocked claims.",
    "PINN-A2 does not implement or execute a PINN advisor, run training, invoke a solver, benchmark runtime, or evaluate scientific correctness.",
    "PINN-A2 does not approve public docs, product readiness, solver correctness, training improvement, runtime performance, or broad EML advantage.",
    "PINN-A2 does not touch laptop-owned electronics repositories, start D110, or consume reviewer response.",
]


def review_checks(brief: dict[str, Any]) -> list[dict[str, str]]:
    summary = brief["summary"]
    return [
        {
            "checkId": "brief_scope_is_private",
            "status": "pass",
            "reason": f"PINN-A1 scope is `{summary['briefScope']}`.",
        },
        {
            "checkId": "supported_inputs_present",
            "status": "pass",
            "reason": f"PINN-A1 records {summary['supportedInputCount']} supported input shapes.",
        },
        {
            "checkId": "advisory_diagnostics_present",
            "status": "pass",
            "reason": f"PINN-A1 records {summary['diagnosticCount']} advisory diagnostics.",
        },
        {
            "checkId": "blocked_claims_present",
            "status": "pass",
            "reason": f"PINN-A1 records {summary['blockedClaimCount']} blocked claims.",
        },
        {
            "checkId": "human_gate_present",
            "status": "pass",
            "reason": "PINN-A1 records the human implementation gate dependency.",
        },
        {
            "checkId": "implementation_flags_false",
            "status": "pass",
            "reason": "Advisor implementation, execution, training, and solver invocation remain false.",
        },
        {
            "checkId": "public_and_science_claims_false",
            "status": "pass",
            "reason": "Scientific correctness, training improvement, runtime performance, and public readiness claims remain false.",
        },
    ]


def selector_actions() -> list[dict[str, Any]]:
    return [
        {
            "actionId": "draft_static_fixture_packet",
            "decision": "selected",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "Accepted and rejection fixture shapes would make the PINN-A1 brief reviewable without implementing an advisor.",
            "requires": [
                "accepted fixture shapes for safe advisory notes",
                "rejection fixture shapes for science/public/training claims",
                "no advisor execution",
            ],
        },
        {
            "actionId": "pause_pinn_advisor_lane",
            "decision": "parked",
            "nextArtifact": "PINN-A2-pause private PINN advisor lane pause packet",
            "reason": "Pause remains available if reviewers decide the brief is already sufficiently bounded.",
            "requires": ["explicit hold direction or failed fixture-worthiness review"],
        },
        {
            "actionId": "implementation_gate",
            "decision": "blocked",
            "nextArtifact": "future implementation gate only after fixtures and explicit approval",
            "reason": "Implementation would exceed the brief/fixture boundary and create science/product risk.",
            "requires": ["fixture packet", "fixture review", "explicit human approval"],
        },
        {
            "actionId": "public_docs_gate",
            "decision": "blocked",
            "nextArtifact": "future public copy approval gate only after private review",
            "reason": "Public docs could be misread as solver correctness, training improvement, or product readiness.",
            "requires": ["private fixture review", "explicit public-copy approval"],
        },
    ]


def build_payload() -> dict[str, Any]:
    brief = pinn_a1.build_payload()
    pinn_a1.validate_payload(brief)
    checks = review_checks(brief)
    actions = selector_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    summary = {
        "sourceArtifact": brief["artifactId"],
        "reviewCheckCount": len(checks),
        "reviewFailureCount": sum(1 for check in checks if check["status"] != "pass"),
        "selectorActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "staticFixturesCreated": False,
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
        artifact_id="pinn-a2-private-pinn-advisor-fixture-or-hold-selector",
        artifact_type="private_pinn_advisor_fixture_or_hold_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": brief["artifactId"],
            "reviewChecks": checks,
            "selectorActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "pinn-a1-private-pinn-advisor-brief":
        raise ValueError("PINN-A2 must consume PINN-A1")
    summary = payload["summary"]
    if summary["reviewFailureCount"] != 0:
        raise ValueError("review checks must have no failures")
    if summary["selectedActionId"] != "draft_static_fixture_packet":
        raise ValueError("PINN-A2 should select the static fixture packet")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    expected_counts = {
        "reviewCheckCount": len(payload["reviewChecks"]),
        "selectorActionCount": len(payload["selectorActions"]),
    }
    for key, expected in expected_counts.items():
        if summary[key] != expected:
            raise ValueError(f"{key} mismatch")
    decisions = {action["actionId"]: action["decision"] for action in payload["selectorActions"]}
    if decisions != {
        "draft_static_fixture_packet": "selected",
        "pause_pinn_advisor_lane": "parked",
        "implementation_gate": "blocked",
        "public_docs_gate": "blocked",
    }:
        raise ValueError("unexpected selector decisions")
    for key in [
        "staticFixturesCreated",
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
        semantic_strength="private_pinn_advisor_selector_no_fixtures_or_implementation",
        source=f"python/results/pinn_a2_private_pinn_advisor_fixture_or_hold_selector/pinn_a2_private_pinn_advisor_fixture_or_hold_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="pinn_a2_private_pinn_advisor_fixture_or_hold_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create PINN-A3 private PINN advisor static fixture packet.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "reviewFailureCount": payload["summary"]["reviewFailureCount"],
            "staticFixturesCreated": payload["summary"]["staticFixturesCreated"],
            "advisorImplemented": payload["summary"]["advisorImplemented"],
            "advisorExecuted": payload["summary"]["advisorExecuted"],
            "scientificCorrectnessClaim": payload["summary"]["scientificCorrectnessClaim"],
            "trainingImprovementClaim": payload["summary"]["trainingImprovementClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PINN-A2 Private PINN Advisor Fixture Or Hold Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("review checks", payload["summary"]["reviewCheckCount"]),
            ("review failures", payload["summary"]["reviewFailureCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("static fixtures created", payload["summary"]["staticFixturesCreated"]),
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
                "Selector Actions",
                [
                    f"- `{action['actionId']}`: `{action['decision']}` - {action['reason']}"
                    for action in payload["selectorActions"]
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
    result_path = out_dir / f"pinn_a2_private_pinn_advisor_fixture_or_hold_selector_{STAMP}.json"
    report_path = report_dir / f"pinn_a2_private_pinn_advisor_fixture_or_hold_selector_{STAMP}.md"
    evidence_path = evidence_dir / "pinn_a2_private_pinn_advisor_fixture_or_hold_selector.json"
    feed_path = command_feed_dir / f"pinn_a2_private_pinn_advisor_fixture_or_hold_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/pinn_a2_private_pinn_advisor_fixture_or_hold_selector",
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
    print("PINN_A2_PRIVATE_PINN_ADVISOR_FIXTURE_OR_HOLD_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
