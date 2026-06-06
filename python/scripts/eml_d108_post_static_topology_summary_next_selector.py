#!/usr/bin/env python3
"""EML-D108 post static topology summary next-action selector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eml_d107_private_claim_topology_static_summary_fixture as d107  # noqa: E402

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_post_static_topology_summary_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D108_POST_STATIC_TOPOLOGY_SUMMARY_NEXT_SELECTOR_PASS"

TRUE_CLAIM_FLAGS = {
    "next_action_selected",
    "d107_static_summary_consumed",
    "private_reviewer_response_intake_selected",
}

CLAIM_FLAGS = {
    "next_action_selected": True,
    "d107_static_summary_consumed": True,
    "private_reviewer_response_intake_selected": True,
    "reviewer_response_consumed": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "private_summary_implementation_selected": False,
    "implementation_approved": False,
    "claim_topology_surface_created": False,
    "interactive_renderer_implemented": False,
    "renderer_implemented": False,
    "renderer_executed": False,
    "visualization_rendered": False,
    "visualization_quality_claim": False,
    "renderer_correctness_claim": False,
    "renderer_soundness_proved": False,
    "public_surface_updated": False,
    "public_page_created": False,
    "public_copy_approved": False,
    "public_ready": False,
    "human_approval_recorded": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "next_public_witness_candidate_selected": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "runtime_performance_claim": False,
    "protected_expm1_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
    "theorem_discovery_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "catalog_completeness_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
}

NON_CLAIMS = [
    "EML-D108 selects the next private action after D107; it does not consume a reviewer response.",
    "D108 selects private reviewer response intake because D107 completed a static summary and any implementation packet requires separate approval.",
    "D108 does not implement, render, execute, or publish a Claim Topology surface; it does not approve public copy, edit MachLib, typecheck Lean, change runtime lowering, consume laptop artifacts, touch laptop-owned repos, or claim renderer correctness, visualization quality, public readiness, compiler correctness, formal equivalence, protected expm1 replacement, theorem discovery, or broad EML advantage.",
]


def selector_option(
    option_id: str,
    lane: str,
    status: str,
    priority_score: int,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "lane": lane,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    summary_fixture = d107.build_payload(atlas_gate_path)
    d107.validate_payload(summary_fixture)
    options = [
        selector_option(
            "private_reviewer_response_intake",
            "private_review_lane",
            "selected_next",
            92,
            "EML-D109 private reviewer response intake packet",
            [
                "D107 produced the static summary fixture, so the next valuable step is human/reviewer response rather than more automatic topology expansion.",
                "Reviewer response can decide whether the summary is useful, should be held, or needs bounded implementation approval.",
                "This respects the D-series consolidation cap and avoids silent public or renderer claims.",
            ],
            [
                "requires an actual reviewer response before D109 can record substance",
                "must not treat silence as approval",
                "must preserve D107 static-summary non-claims",
            ],
        ),
        selector_option(
            "private_summary_implementation_packet",
            "private_tooling_implementation_lane",
            "parked_requires_explicit_approval",
            63,
            "Future separately approved private summary implementation packet",
            [
                "A private implementation may be useful, but D107's handoff requires separate approval first.",
                "Implementation should wait until a reviewer confirms the static summary shape is worth turning into tooling.",
            ],
            [
                "requires explicit approval",
                "must remain private",
                "must not claim renderer correctness or visualization quality",
            ],
        ),
        selector_option(
            "human_public_copy_gate",
            "public_copy_gate_lane",
            "parked_requires_explicit_human_approval",
            45,
            "Future human-approved public copy gate",
            [
                "D104-D107 preserve the expm1 copy boundary but still record no human approval.",
                "Public copy should remain blocked until explicit approval exists.",
            ],
            [
                "requires explicit human approval",
                "requires reviewer decision record",
                "must preserve D104-D107 caveats and blocked claims",
            ],
        ),
        selector_option(
            "next_bounded_identity_branch_selector",
            "bounded_identity_lane",
            "parked_after_reviewer_response",
            31,
            "Future bounded identity branch selector",
            [
                "The D-series should not expand the witness catalog indefinitely.",
                "Another bounded identity should wait until reviewer response clarifies consolidation needs.",
            ],
            [
                "requires reviewer response or explicit research redirection",
                "must not count selector-only packets as bounded artifacts",
                "must avoid broad EML advantage language",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    source_summary = summary_fixture["summary"]
    summary = {
        "sourceStaticSummary": summary_fixture["artifactId"],
        "selectedWitnessName": source_summary["selectedWitnessName"],
        "checkedStatement": source_summary["checkedStatement"],
        "guardSummary": source_summary["guardSummary"],
        "runtimeControl": source_summary["runtimeControl"],
        "d107StaticTableCount": source_summary["staticTableCount"],
        "d107AcceptedFixtureRowCount": source_summary["acceptedFixtureRowCount"],
        "d107BlockedClaimRowCount": source_summary["blockedClaimRowCount"],
        "d107DependencyRowCount": source_summary["dependencyRowCount"],
        "d107ReviewerActionRowCount": source_summary["reviewerActionRowCount"],
        "d107GuardrailCardCount": source_summary["guardrailCardCount"],
        "d107ReviewerCardCount": source_summary["reviewerCardCount"],
        "optionCount": len(options),
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "nextActionSelected": True,
        "d107StaticSummaryConsumed": True,
        "privateReviewerResponseIntakeSelected": True,
        "reviewerResponseConsumed": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "privateSummaryImplementationSelected": False,
        "implementationApproved": False,
        "claimTopologySurfaceCreated": False,
        "interactiveRendererImplemented": False,
        "rendererImplemented": False,
        "rendererExecuted": False,
        "visualizationRendered": False,
        "visualizationQualityClaim": False,
        "rendererCorrectnessClaim": False,
        "rendererSoundnessProved": False,
        "publicSurfaceUpdated": False,
        "publicPageCreated": False,
        "publicCopyApproved": False,
        "publicReady": False,
        "humanApprovalRecorded": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "newIdentityCandidateSelected": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "runtimeLoweringChanged": False,
        "runtimePerformanceClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "fullEmlSemanticsClaim": False,
        "catalogCompletenessClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "claimFlagsBounded": all(CLAIM_FLAGS[key] is True for key in TRUE_CLAIM_FLAGS)
        and all(value is False for key, value in CLAIM_FLAGS.items() if key not in TRUE_CLAIM_FLAGS),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_post_static_topology_summary_next_selector_v0",
        "artifactId": "eml-d108-post-static-topology-summary-next-selector",
        "status": STATUS,
        "decision": "select_private_reviewer_response_intake_after_static_topology_summary_no_implementation",
        "date": DATE,
        "sourceStaticSummary": summary_fixture["artifactId"],
        "selectorOptions": options,
        "selectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceStaticSummary"] != "eml-d107-private-claim-topology-static-summary-fixture":
        raise ValueError("D108 must consume D107")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["guardSummary"] != "no extra real-domain guard recorded":
        raise ValueError("unexpected guard summary")
    if summary["runtimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("unexpected runtime control")
    expected_counts = {
        "d107StaticTableCount": 4,
        "d107AcceptedFixtureRowCount": 2,
        "d107BlockedClaimRowCount": 4,
        "d107DependencyRowCount": 2,
        "d107ReviewerActionRowCount": 3,
        "d107GuardrailCardCount": 3,
        "d107ReviewerCardCount": 4,
        "optionCount": 4,
    }
    for key, expected in expected_counts.items():
        if summary[key] != expected:
            raise ValueError(f"{key} drift")
    if summary["selectedOptionId"] != "private_reviewer_response_intake":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D109 private reviewer response intake packet":
        raise ValueError("unexpected next artifact")
    for key in ["nextActionSelected", "d107StaticSummaryConsumed", "privateReviewerResponseIntakeSelected"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "reviewerResponseConsumed",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "privateSummaryImplementationSelected",
        "implementationApproved",
        "claimTopologySurfaceCreated",
        "interactiveRendererImplemented",
        "rendererImplemented",
        "rendererExecuted",
        "visualizationRendered",
        "visualizationQualityClaim",
        "rendererCorrectnessClaim",
        "rendererSoundnessProved",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "publicCopyApproved",
        "publicReady",
        "humanApprovalRecorded",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "newIdentityCandidateSelected",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "runtimeLoweringChanged",
        "runtimePerformanceClaim",
        "protectedExpm1ReplacementClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "fullEmlSemanticsClaim",
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags are not bounded")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_post_static_topology_summary_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_selects_reviewer_response_after_static_summary_no_implementation_no_public_update",
        "source": f"python/results/eml_d108_post_static_topology_summary_next_selector/eml_d108_post_static_topology_summary_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d108_post_static_topology_summary_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceStaticSummary": payload["sourceStaticSummary"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "reviewerResponseConsumed": payload["summary"]["reviewerResponseConsumed"],
        "implementationApproved": payload["summary"]["implementationApproved"],
        "rendererImplemented": payload["summary"]["rendererImplemented"],
        "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
        "nextAction": "Run EML-D109 only when an actual private reviewer response exists.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D108 Post Static Topology Summary Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D108 selects the next private action after D107. It does not consume a reviewer response or implement a surface.",
        "",
        "## Summary",
        "",
        f"- source static summary: `{payload['sourceStaticSummary']}`",
        f"- selected option: `{payload['summary']['selectedOptionId']}`",
        f"- next artifact: `{payload['summary']['selectedNextArtifact']}`",
        f"- reviewer response consumed: `{payload['summary']['reviewerResponseConsumed']}`",
        f"- implementation approved: `{payload['summary']['implementationApproved']}`",
        f"- renderer implemented: `{payload['summary']['rendererImplemented']}`",
        f"- public surface updated: `{payload['summary']['publicSurfaceUpdated']}`",
        "",
        "## Options",
        "",
        "| Option | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for option in payload["selectorOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | {option['priorityScore']} | {option['nextArtifact']} |"
        )
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    atlas_gate_path: Path,
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d108_post_static_topology_summary_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d108_post_static_topology_summary_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d108_post_static_topology_summary_next_selector.json"
    feed_path = command_feed_dir / f"eml_d108_post_static_topology_summary_next_selector_feed_{STAMP}.json"
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
        "--atlas-gate-path",
        type=Path,
        default=ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d108_post_static_topology_summary_next_selector")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.atlas_gate_path)
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.atlas_gate_path)
    print("EML_D108_POST_STATIC_TOPOLOGY_SUMMARY_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
