#!/usr/bin/env python3
"""EML-D107 private Claim Topology static summary fixture."""

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

from scripts import eml_d106_private_claim_topology_surface_seed_packet as d106  # noqa: E402

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_private_claim_topology_static_summary_fixture.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D107_PRIVATE_CLAIM_TOPOLOGY_STATIC_SUMMARY_FIXTURE_PASS"

TRUE_CLAIM_FLAGS = {
    "private_static_summary_fixture_recorded",
    "d106_seed_consumed",
    "static_tables_recorded",
    "reviewer_cards_recorded",
    "private_guardrails_preserved",
}

CLAIM_FLAGS = {
    "private_static_summary_fixture_recorded": True,
    "d106_seed_consumed": True,
    "static_tables_recorded": True,
    "reviewer_cards_recorded": True,
    "private_guardrails_preserved": True,
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
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
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
    "EML-D107 records a private static summary fixture only; it does not create, render, or execute a Claim Topology surface.",
    "D107 summarizes D106 seed rows into static reviewer tables and cards without claiming renderer correctness, visualization quality, public readiness, or public copy approval.",
    "D107 preserves the D104-D106 expm1 boundary and keeps MachLib, Lean, runtime lowering, SDK/compiler docs, course material, electronics, laptop-owned repos, and public surfaces untouched.",
]


def section_by_id(seed: dict[str, Any], section_id: str) -> dict[str, Any]:
    return next(section for section in seed["surfaceSections"] if section["sectionId"] == section_id)


def accepted_fixture_rows(seed: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in section_by_id(seed, "fixture_state_lanes")["seedRows"]:
        rows.append(
            {
                "rowId": row["artifactId"],
                "fixtureKind": row["fixtureKind"],
                "reviewState": row["reviewState"],
                "checkedWitnessName": row["checkedWitnessName"],
                "sourceStatement": row["sourceStatement"],
                "guardSummary": row["guardSummary"],
                "runtimeControl": row["runtimeControl"],
                "publicStatus": row["publicStatus"],
            }
        )
    return rows


def blocked_claim_rows(seed: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "claimId": row["claimId"],
            "status": row["status"],
            "reason": row["reason"],
            "sourceArtifact": row["sourceArtifact"],
        }
        for row in section_by_id(seed, "claim_boundaries_and_blocked_claims")["seedRows"]
    ]


def dependency_rows(seed: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "edgeId": row["edgeId"],
            "sourceArtifact": row["sourceArtifact"],
            "targetArtifact": row["targetArtifact"],
            "relationship": row["relationship"],
            "preservedBoundaryCount": len(row["preserves"]),
            "preserves": row["preserves"],
        }
        for row in section_by_id(seed, "artifact_dependency_edges")["seedRows"]
    ]


def reviewer_action_rows(seed: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "actionId": row["actionId"],
            "status": row["status"],
            "owner": row["owner"],
            "nextEvidenceNeeded": row["nextEvidenceNeeded"],
            "blockedUntil": row["blockedUntil"],
        }
        for row in section_by_id(seed, "reviewer_actions")["seedRows"]
    ]


def guardrail_cards(seed: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "cardId": row["guardrailId"],
            "displayTextRequired": row["displayTextRequired"],
            "blockedClaimCount": len(row["blocks"]),
            "blocks": row["blocks"],
        }
        for row in section_by_id(seed, "private_guardrails")["seedRows"]
    ]


def reviewer_cards(seed: dict[str, Any]) -> list[dict[str, Any]]:
    summary = seed["summary"]
    return [
        {
            "cardId": "current_scope",
            "title": "Current Scope",
            "body": "Private static summary of one frozen expm1 witness-copy boundary and its blocked claims.",
            "sourceArtifact": seed["artifactId"],
        },
        {
            "cardId": "witness_boundary",
            "title": "Witness Boundary",
            "body": summary["checkedStatement"],
            "sourceArtifact": summary["selectedWitnessName"],
        },
        {
            "cardId": "runtime_boundary",
            "title": "Runtime Boundary",
            "body": summary["runtimeControl"],
            "sourceArtifact": seed["artifactId"],
        },
        {
            "cardId": "next_action",
            "title": "Next Action",
            "body": "Record reviewer response or create a later private implementation packet only if approved.",
            "sourceArtifact": seed["artifactId"],
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    seed = d106.build_payload(atlas_gate_path)
    d106.validate_payload(seed)
    accepted = accepted_fixture_rows(seed)
    blocked = blocked_claim_rows(seed)
    dependencies = dependency_rows(seed)
    actions = reviewer_action_rows(seed)
    guardrails = guardrail_cards(seed)
    cards = reviewer_cards(seed)
    static_tables = [
        {
            "tableId": "accepted_fixtures",
            "title": "Accepted/Frozen Fixtures",
            "rowCount": len(accepted),
            "rows": accepted,
        },
        {
            "tableId": "blocked_claims",
            "title": "Blocked Claims",
            "rowCount": len(blocked),
            "rows": blocked,
        },
        {
            "tableId": "artifact_dependencies",
            "title": "Artifact Dependencies",
            "rowCount": len(dependencies),
            "rows": dependencies,
        },
        {
            "tableId": "reviewer_actions",
            "title": "Reviewer Actions",
            "rowCount": len(actions),
            "rows": actions,
        },
    ]
    summary = {
        "sourceSeed": seed["artifactId"],
        "selectedWitnessName": seed["summary"]["selectedWitnessName"],
        "checkedStatement": seed["summary"]["checkedStatement"],
        "guardSummary": seed["summary"]["guardSummary"],
        "runtimeControl": seed["summary"]["runtimeControl"],
        "sourceSurfaceSectionCount": seed["summary"]["surfaceSectionCount"],
        "sourceSectionSeedRowCount": seed["summary"]["sectionSeedRowCount"],
        "staticTableCount": len(static_tables),
        "acceptedFixtureRowCount": len(accepted),
        "blockedClaimRowCount": len(blocked),
        "dependencyRowCount": len(dependencies),
        "reviewerActionRowCount": len(actions),
        "guardrailCardCount": len(guardrails),
        "reviewerCardCount": len(cards),
        "privateStaticSummaryFixtureRecorded": True,
        "d106SeedConsumed": True,
        "staticTablesRecorded": True,
        "reviewerCardsRecorded": True,
        "privateGuardrailsPreserved": True,
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
        "reviewerDecisionRecorded": False,
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
        "packetType": "eml_private_claim_topology_static_summary_fixture_v0",
        "artifactId": "eml-d107-private-claim-topology-static-summary-fixture",
        "status": STATUS,
        "decision": "record_private_static_claim_topology_summary_no_renderer_no_public_promotion",
        "date": DATE,
        "sourceSeed": seed["artifactId"],
        "staticTables": static_tables,
        "guardrailCards": guardrails,
        "reviewerCards": cards,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSeed"] != "eml-d106-private-claim-topology-surface-seed":
        raise ValueError("D107 must consume D106")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["guardSummary"] != "no extra real-domain guard recorded":
        raise ValueError("unexpected guard summary")
    if summary["runtimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("unexpected runtime control")
    if summary["sourceSurfaceSectionCount"] != 5 or summary["sourceSectionSeedRowCount"] != 14:
        raise ValueError("D106 seed shape drift")
    expected_counts = {
        "staticTableCount": 4,
        "acceptedFixtureRowCount": 2,
        "blockedClaimRowCount": 4,
        "dependencyRowCount": 2,
        "reviewerActionRowCount": 3,
        "guardrailCardCount": 3,
        "reviewerCardCount": 4,
    }
    for key, expected in expected_counts.items():
        if summary[key] != expected:
            raise ValueError(f"{key} drift")
    for key in [
        "privateStaticSummaryFixtureRecorded",
        "d106SeedConsumed",
        "staticTablesRecorded",
        "reviewerCardsRecorded",
        "privateGuardrailsPreserved",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
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
        "reviewerDecisionRecorded",
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
        "artifactType": "eml_private_claim_topology_static_summary_fixture",
        "validationStatus": "pass",
        "semanticStrength": "private_static_claim_topology_summary_fixture_no_renderer_no_public_update",
        "source": f"python/results/eml_d107_private_claim_topology_static_summary_fixture/eml_d107_private_claim_topology_static_summary_fixture_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d107_private_claim_topology_static_summary_fixture_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceSeed": payload["sourceSeed"],
        "staticTableCount": payload["summary"]["staticTableCount"],
        "blockedClaimRowCount": payload["summary"]["blockedClaimRowCount"],
        "reviewerActionRowCount": payload["summary"]["reviewerActionRowCount"],
        "rendererImplemented": payload["summary"]["rendererImplemented"],
        "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
        "nextAction": "Record private reviewer response or create a separately approved private summary implementation packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D107 Private Claim Topology Static Summary Fixture",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D107 records a private static summary fixture from D106 seed rows. It does not create or render a surface.",
        "",
        "## Summary",
        "",
        f"- source seed: `{payload['sourceSeed']}`",
        f"- witness: `{payload['summary']['selectedWitnessName']}`",
        f"- checked statement: `{payload['summary']['checkedStatement']}`",
        f"- static tables: `{payload['summary']['staticTableCount']}`",
        f"- blocked claim rows: `{payload['summary']['blockedClaimRowCount']}`",
        f"- reviewer action rows: `{payload['summary']['reviewerActionRowCount']}`",
        f"- renderer implemented: `{payload['summary']['rendererImplemented']}`",
        f"- public surface updated: `{payload['summary']['publicSurfaceUpdated']}`",
        "",
    ]
    for table in payload["staticTables"]:
        lines.extend(
            [
                f"## {table['title']}",
                "",
                f"Rows: `{table['rowCount']}`",
                "",
            ]
        )
    lines.extend(["## Guardrail Cards", ""])
    for card in payload["guardrailCards"]:
        lines.append(f"- `{card['cardId']}` blocks {card['blockedClaimCount']} claims: {card['displayTextRequired']}")
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
    result_path = out_dir / f"eml_d107_private_claim_topology_static_summary_fixture_{STAMP}.json"
    report_path = report_dir / f"eml_d107_private_claim_topology_static_summary_fixture_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d107_private_claim_topology_static_summary_fixture.json"
    feed_path = command_feed_dir / f"eml_d107_private_claim_topology_static_summary_fixture_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d107_private_claim_topology_static_summary_fixture")
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
    print("EML_D107_PRIVATE_CLAIM_TOPOLOGY_STATIC_SUMMARY_FIXTURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
