#!/usr/bin/env python3
"""CPG-A2 private compiler-plugin guard-note fixture or lint-contract selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a1_private_compiler_plugin_guard_note_packet as cpg_a1  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_compiler_plugin_guard_note_fixture_or_lint_contract_selector.v0"
STATUS = "CPG_A2_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_FIXTURE_OR_LINT_CONTRACT_SELECTOR_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A3 private compiler-plugin guard-note static fixture packet"

TRUE_CLAIM_FLAGS = {
    "cpg_a1_consumed",
    "guard_note_next_selector_created",
    "static_fixture_packet_selected",
    "executable_lint_contract_parked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a1_consumed": True,
    "guard_note_next_selector_created": True,
    "static_fixture_packet_selected": True,
    "executable_lint_contract_parked": True,
    "d109_hold_respected": True,
    "static_fixture_packet_created": False,
    "executable_lint_contract_created": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "lint_engine_implemented": False,
    "lint_engine_executed": False,
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
    "CPG-A2 is a private selector only; it does not create fixtures or executable lint contracts.",
    "CPG-A2 selects static advisory fixtures before executable lint-contract work.",
    "CPG-A2 does not implement or execute a compiler plugin, lint engine, rewrite engine, code generator, or runtime lowering path.",
    "CPG-A2 does not claim compiler correctness, semantic preservation, automatic lowering safety, code generation correctness, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A2 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def candidate_next_actions() -> list[dict[str, Any]]:
    return [
        {
            "actionId": "static_guard_note_fixture_packet",
            "decision": "selected_next",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "Static fixtures can exercise advisory boundaries without implementing or executing a lint engine.",
            "expectedFixtureFamilies": [
                "accepted_advisory_expression_surface_detection",
                "accepted_guard_requirement_note",
                "accepted_evidence_packet_link_hint",
                "rejected_automatic_rewrite_or_lowering",
                "rejected_runtime_performance_claim",
                "rejected_public_readiness_claim",
            ],
        },
        {
            "actionId": "executable_lint_contract",
            "decision": "parked_until_static_fixtures_reviewed",
            "nextArtifact": "CPG-A4 private executable lint contract selector after CPG-A3 review",
            "reason": "Executable lint contracts would imply tool behavior; static advisory fixtures should be reviewed first.",
            "blockedUntil": "CPG-A3 static fixture packet exists and is reviewed",
        },
        {
            "actionId": "compiler_plugin_implementation",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Implementation remains blocked until advisory fixture and executable contract boundaries are reviewed.",
            "blockedUntil": "explicit implementation approval and bounded contract evidence",
        },
        {
            "actionId": "public_docs_or_package",
            "decision": "blocked",
            "nextArtifact": "none",
            "reason": "Public product/docs/package work would exceed the private advisory selector boundary.",
            "blockedUntil": "explicit public approval and separate release/readiness evidence",
        },
    ]


def build_payload() -> dict[str, Any]:
    guard_note = cpg_a1.build_payload()
    cpg_a1.validate_payload(guard_note)
    actions = candidate_next_actions()
    selected = [action for action in actions if action["decision"] == "selected_next"]
    summary = {
        "sourceArtifact": guard_note["artifactId"],
        "candidateActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "expectedFixtureFamilyCount": len(selected[0]["expectedFixtureFamilies"]),
        "executableLintContractCreated": False,
        "staticFixturePacketCreated": False,
        "compilerPluginImplemented": False,
        "compilerPluginExecuted": False,
        "lintEngineImplemented": False,
        "lintEngineExecuted": False,
        "compilerCorrectnessClaim": False,
        "semanticPreservationClaim": False,
        "automaticLoweringSafetyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="cpg-a2-private-compiler-plugin-guard-note-fixture-or-lint-contract-selector",
        artifact_type="private_compiler_plugin_guard_note_fixture_or_lint_contract_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": guard_note["artifactId"],
            "candidateNextActions": actions,
            "selectedFixtureFamilies": selected[0]["expectedFixtureFamilies"],
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a1-private-compiler-plugin-guard-note-packet":
        raise ValueError("CPG-A2 must consume CPG-A1")
    summary = payload["summary"]
    if summary["selectedActionId"] != "static_guard_note_fixture_packet":
        raise ValueError("CPG-A2 must select static guard-note fixtures first")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["expectedFixtureFamilyCount"] != len(payload["selectedFixtureFamilies"]):
        raise ValueError("fixture family count mismatch")
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateNextActions"]}
    if decisions["executable_lint_contract"] != "parked_until_static_fixtures_reviewed":
        raise ValueError("executable lint contract must be parked")
    if decisions["compiler_plugin_implementation"] != "blocked":
        raise ValueError("compiler plugin implementation must be blocked")
    for key in [
        "executableLintContractCreated",
        "staticFixturePacketCreated",
        "compilerPluginImplemented",
        "compilerPluginExecuted",
        "lintEngineImplemented",
        "lintEngineExecuted",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "automaticLoweringSafetyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    fixture_families = set(payload["selectedFixtureFamilies"])
    if not {
        "accepted_advisory_expression_surface_detection",
        "rejected_automatic_rewrite_or_lowering",
        "rejected_runtime_performance_claim",
    }.issubset(fixture_families):
        raise ValueError("required fixture families missing")
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
        semantic_strength="private_compiler_plugin_next_selector_no_plugin_or_lint_execution",
        source=f"python/results/cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector/cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "executableLintContractCreated": payload["summary"]["executableLintContractCreated"],
            "compilerPluginImplemented": payload["summary"]["compilerPluginImplemented"],
            "runtimePerformanceClaim": payload["summary"]["runtimePerformanceClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A2 Private Compiler-Plugin Guard-Note Fixture or Lint-Contract Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("expected fixture family count", payload["summary"]["expectedFixtureFamilyCount"]),
            ("executable lint contract created", payload["summary"]["executableLintContractCreated"]),
            ("compiler plugin implemented", payload["summary"]["compilerPluginImplemented"]),
            ("runtime performance claim", payload["summary"]["runtimePerformanceClaim"]),
        ],
        sections=[
            (
                "Candidate Next Actions",
                [
                    f"- `{action['actionId']}`: `{action['decision']}` - {action['reason']}"
                    for action in payload["candidateNextActions"]
                ],
            ),
            (
                "Selected Fixture Families",
                [f"- `{family}`" for family in payload["selectedFixtureFamilies"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector_{STAMP}.json"
    report_path = report_dir / f"cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector.json"
    feed_path = command_feed_dir / f"cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector")
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
    print("CPG_A2_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_FIXTURE_OR_LINT_CONTRACT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
