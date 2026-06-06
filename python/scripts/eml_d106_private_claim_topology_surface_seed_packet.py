#!/usr/bin/env python3
"""EML-D106 private Claim Topology Surface seed packet."""

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

from scripts import eml_d105_post_expm1_public_witness_copy_freeze_next_selector as d105  # noqa: E402
from scripts import gb_vis_a1_claim_topology_renderer_contract as gb_vis_a1  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_private_claim_topology_surface_seed.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D106_PRIVATE_CLAIM_TOPOLOGY_SURFACE_SEED_PASS"

TRUE_CLAIM_FLAGS = {
    "private_claim_topology_seed_recorded",
    "d105_selector_consumed",
    "gb_vis_a1_contract_observed",
    "surface_sections_seeded",
    "topology_data_shape_seeded",
    "reviewer_action_queue_seeded",
    "private_guardrails_recorded",
}

CLAIM_FLAGS = {
    "private_claim_topology_seed_recorded": True,
    "d105_selector_consumed": True,
    "gb_vis_a1_contract_observed": True,
    "surface_sections_seeded": True,
    "topology_data_shape_seeded": True,
    "reviewer_action_queue_seeded": True,
    "private_guardrails_recorded": True,
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
    "EML-D106 records a private Claim Topology Surface seed packet only; it does not create, render, or execute a surface.",
    "D106 describes a reviewer-facing data shape and MVP scope for reducing evidence-packet review load; it does not claim renderer correctness, visualization quality, public readiness, or public copy approval.",
    "D106 preserves the D104/D105 expm1 public-witness copy freeze boundary and keeps MachLib, Lean, runtime lowering, SDK/compiler docs, course material, electronics, laptop-owned repos, and public surfaces untouched.",
]


def surface_sections(d105_payload: dict[str, Any]) -> list[dict[str, Any]]:
    summary = d105_payload["summary"]
    return [
        {
            "sectionId": "fixture_state_lanes",
            "title": "Accepted vs Rejected Fixtures",
            "privateOnly": True,
            "purpose": "Separate checked/frozen rows from rejected, parked, or blocked fixture families.",
            "fields": [
                "artifactId",
                "fixtureKind",
                "reviewState",
                "checkedWitnessName",
                "sourceStatement",
                "guardSummary",
                "runtimeControl",
                "publicStatus",
            ],
            "seedRows": [
                {
                    "artifactId": "d104_expm1_public_witness_copy_freeze",
                    "fixtureKind": "accepted_frozen_private_copy_boundary",
                    "reviewState": "frozen_private_no_public_approval",
                    "checkedWitnessName": summary["selectedWitnessName"],
                    "sourceStatement": summary["checkedStatement"],
                    "guardSummary": summary["guardSummary"],
                    "runtimeControl": summary["runtimeControl"],
                    "publicStatus": "held_private",
                },
                {
                    "artifactId": "d105_private_claim_topology_surface_seed_selection",
                    "fixtureKind": "selected_next_action",
                    "reviewState": "selected_private_seed_only",
                    "checkedWitnessName": summary["selectedWitnessName"],
                    "sourceStatement": summary["checkedStatement"],
                    "guardSummary": summary["guardSummary"],
                    "runtimeControl": summary["runtimeControl"],
                    "publicStatus": "held_private",
                },
            ],
        },
        {
            "sectionId": "claim_boundaries_and_blocked_claims",
            "title": "Claim Boundaries and Blocked Claims",
            "privateOnly": True,
            "purpose": "Show what the artifact claims and what it explicitly does not claim.",
            "fields": ["claimId", "status", "reason", "sourceArtifact"],
            "seedRows": [
                {
                    "claimId": "public_copy_approved",
                    "status": "blocked",
                    "reason": "D105 selected a private seed; no human approval or reviewer decision exists.",
                    "sourceArtifact": d105_payload["artifactId"],
                },
                {
                    "claimId": "renderer_correctness",
                    "status": "blocked",
                    "reason": "D106 seeds data shape only and no renderer is created or executed.",
                    "sourceArtifact": "eml-d106-private-claim-topology-surface-seed",
                },
                {
                    "claimId": "protected_expm1_replacement",
                    "status": "blocked",
                    "reason": "The expm1 witness remains a checked identity and protected expm1 remains runtime control.",
                    "sourceArtifact": d105_payload["artifactId"],
                },
                {
                    "claimId": "broad_eml_advantage",
                    "status": "blocked",
                    "reason": "A single bounded witness-copy boundary cannot support broad EML advantage claims.",
                    "sourceArtifact": d105_payload["artifactId"],
                },
            ],
        },
        {
            "sectionId": "artifact_dependency_edges",
            "title": "Artifact Dependencies",
            "privateOnly": True,
            "purpose": "Make it obvious which artifact depends on which prior evidence packet.",
            "fields": ["edgeId", "sourceArtifact", "targetArtifact", "relationship", "preserves"],
            "seedRows": [
                {
                    "edgeId": "d104_to_d105_preserve_freeze_boundary",
                    "sourceArtifact": "eml-d104-expm1-public-witness-copy-freeze-packet",
                    "targetArtifact": d105_payload["artifactId"],
                    "relationship": "consumed_by_selector",
                    "preserves": [
                        "checkedStatement",
                        "guardSummary",
                        "runtimeControl",
                        "frozenCopySections",
                        "claimBoundaries",
                    ],
                },
                {
                    "edgeId": "d105_to_d106_select_private_topology_seed",
                    "sourceArtifact": d105_payload["artifactId"],
                    "targetArtifact": "eml-d106-private-claim-topology-surface-seed",
                    "relationship": "selected_next_private_artifact",
                    "preserves": [
                        "selectedNextArtifact",
                        "publicHold",
                        "rendererNonClaims",
                        "reviewerDecisionHold",
                    ],
                },
            ],
        },
        {
            "sectionId": "reviewer_actions",
            "title": "Reviewer Actions and Next Steps",
            "privateOnly": True,
            "purpose": "Give a reviewer a short action queue instead of requiring manual JSON traversal.",
            "fields": ["actionId", "status", "owner", "nextEvidenceNeeded", "blockedUntil"],
            "seedRows": [
                {
                    "actionId": "review_d104_expm1_copy_boundary",
                    "status": "available_private_review",
                    "owner": "research_reviewer",
                    "nextEvidenceNeeded": "human review note or explicit hold",
                    "blockedUntil": "none",
                },
                {
                    "actionId": "decide_public_copy_gate",
                    "status": "blocked",
                    "owner": "human",
                    "nextEvidenceNeeded": "explicit human approval with preserved caveats",
                    "blockedUntil": "reviewer decision exists",
                },
                {
                    "actionId": "implement_private_surface_mvp",
                    "status": "candidate_later",
                    "owner": "research_tooling",
                    "nextEvidenceNeeded": "D107 or later explicit implementation packet",
                    "blockedUntil": "D106 seed accepted",
                },
            ],
        },
        {
            "sectionId": "private_guardrails",
            "title": "Private Guardrails",
            "privateOnly": True,
            "purpose": "Keep the topology view humble, local, and non-public.",
            "fields": ["guardrailId", "blocks", "displayTextRequired"],
            "seedRows": [
                {
                    "guardrailId": "private_first",
                    "blocks": ["public_surface_updated", "public_page_created", "public_ready"],
                    "displayTextRequired": "Private review aid only.",
                },
                {
                    "guardrailId": "no_visual_truth",
                    "blocks": ["renderer_correctness_claim", "visualization_quality_claim", "renderer_soundness_proved"],
                    "displayTextRequired": "Topology display is an index, not proof.",
                },
                {
                    "guardrailId": "claim_boundary_visible",
                    "blocks": ["broad_eml_advantage", "runtime_performance_claim", "compiler_correctness_claim"],
                    "displayTextRequired": "Claims remain bounded to cited evidence.",
                },
            ],
        },
    ]


def topology_data_shape(sections: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "shapeId": "private_claim_topology_surface_seed_shape_v0",
        "privateOnly": True,
        "nodeKinds": [
            "accepted_fixture",
            "negative_or_rejection_fixture",
            "blocked_claim",
            "artifact_packet",
            "reviewer_action",
            "guardrail",
        ],
        "edgeKinds": [
            "depends_on",
            "preserves_boundary",
            "blocks_claim",
            "requires_review_action",
            "parks_option",
        ],
        "requiredGlobalFields": [
            "artifactId",
            "privateOnly",
            "reviewState",
            "claimBoundaryStatus",
            "publicStatus",
            "sourceEvidencePath",
            "nextReviewerAction",
        ],
        "sectionIds": [section["sectionId"] for section in sections],
    }


def minimal_mvp_scope() -> list[dict[str, Any]]:
    return [
        {
            "mvpItemId": "static_markdown_or_json_summary",
            "status": "recommended_first",
            "description": "Generate a private static summary from evidence packets before any visual renderer.",
        },
        {
            "mvpItemId": "accepted_vs_blocked_table",
            "status": "recommended_first",
            "description": "Table accepted/frozen rows separately from blocked claims and parked options.",
        },
        {
            "mvpItemId": "dependency_edge_list",
            "status": "recommended_first",
            "description": "List source-to-target artifact edges with preserved claim boundaries.",
        },
        {
            "mvpItemId": "reviewer_action_queue",
            "status": "recommended_first",
            "description": "Show exactly what a reviewer can do next and what remains blocked.",
        },
        {
            "mvpItemId": "interactive_visual_renderer",
            "status": "defer",
            "description": "Defer until a later artifact explicitly implements and tests rendering.",
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d105.build_payload(atlas_gate_path)
    d105.validate_payload(selector)
    renderer_contract = gb_vis_a1.build_payload(atlas_gate_path)
    gb_vis_a1.validate_payload(renderer_contract)
    sections = surface_sections(selector)
    data_shape = topology_data_shape(sections)
    mvp = minimal_mvp_scope()
    section_seed_row_count = sum(len(section["seedRows"]) for section in sections)
    summary = {
        "sourceSelector": selector["artifactId"],
        "sourceRendererContract": renderer_contract["artifactId"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "checkedStatement": selector["summary"]["checkedStatement"],
        "guardSummary": selector["summary"]["guardSummary"],
        "runtimeControl": selector["summary"]["runtimeControl"],
        "selectedNextArtifactFromD105": selector["summary"]["selectedNextArtifact"],
        "surfaceSectionCount": len(sections),
        "sectionSeedRowCount": section_seed_row_count,
        "nodeKindCount": len(data_shape["nodeKinds"]),
        "edgeKindCount": len(data_shape["edgeKinds"]),
        "requiredGlobalFieldCount": len(data_shape["requiredGlobalFields"]),
        "mvpItemCount": len(mvp),
        "recommendedFirstMvpItemCount": sum(1 for item in mvp if item["status"] == "recommended_first"),
        "deferredMvpItemCount": sum(1 for item in mvp if item["status"] == "defer"),
        "privateClaimTopologySeedRecorded": True,
        "d105SelectorConsumed": True,
        "gbVisA1ContractObserved": True,
        "surfaceSectionsSeeded": True,
        "topologyDataShapeSeeded": True,
        "reviewerActionQueueSeeded": True,
        "privateGuardrailsRecorded": True,
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
        "packetType": "eml_private_claim_topology_surface_seed_v0",
        "artifactId": "eml-d106-private-claim-topology-surface-seed",
        "status": STATUS,
        "decision": "record_private_claim_topology_surface_seed_no_renderer_no_public_promotion",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceRendererContract": renderer_contract["artifactId"],
        "surfaceSections": sections,
        "topologyDataShape": data_shape,
        "minimalMvpScope": mvp,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d105-post-expm1-public-witness-copy-freeze-next-selector":
        raise ValueError("D106 must consume D105")
    if payload["sourceRendererContract"] != "gb-vis-a1-claim-topology-renderer-contract":
        raise ValueError("D106 must observe the existing GB-VIS-A1 topology contract")
    if summary["selectedNextArtifactFromD105"] != "EML-D106 private Claim Topology Surface seed packet":
        raise ValueError("D105 did not point to D106")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["guardSummary"] != "no extra real-domain guard recorded":
        raise ValueError("unexpected guard summary")
    if summary["runtimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("unexpected runtime control")
    if summary["surfaceSectionCount"] != 5:
        raise ValueError("expected five surface sections")
    if summary["sectionSeedRowCount"] != 14:
        raise ValueError("unexpected seed row count")
    if summary["nodeKindCount"] != 6 or summary["edgeKindCount"] != 5:
        raise ValueError("unexpected topology shape counts")
    if summary["recommendedFirstMvpItemCount"] != 4 or summary["deferredMvpItemCount"] != 1:
        raise ValueError("unexpected MVP split")
    for key in [
        "privateClaimTopologySeedRecorded",
        "d105SelectorConsumed",
        "gbVisA1ContractObserved",
        "surfaceSectionsSeeded",
        "topologyDataShapeSeeded",
        "reviewerActionQueueSeeded",
        "privateGuardrailsRecorded",
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
        "artifactType": "eml_private_claim_topology_surface_seed",
        "validationStatus": "pass",
        "semanticStrength": "private_claim_topology_surface_seed_no_renderer_no_public_update",
        "source": f"python/results/eml_d106_private_claim_topology_surface_seed_packet/eml_d106_private_claim_topology_surface_seed_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d106_private_claim_topology_surface_seed_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceSelector": payload["sourceSelector"],
        "surfaceSectionCount": payload["summary"]["surfaceSectionCount"],
        "claimTopologySurfaceCreated": payload["summary"]["claimTopologySurfaceCreated"],
        "rendererImplemented": payload["summary"]["rendererImplemented"],
        "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
        "nextAction": "Run EML-D107 as a private Claim Topology static summary fixture or record reviewer response.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D106 Private Claim Topology Surface Seed Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D106 records a private seed for making claim topology review easier. It does not create or render a surface.",
        "",
        "## Summary",
        "",
        f"- source selector: `{payload['sourceSelector']}`",
        f"- source topology contract observed: `{payload['sourceRendererContract']}`",
        f"- witness: `{payload['summary']['selectedWitnessName']}`",
        f"- checked statement: `{payload['summary']['checkedStatement']}`",
        f"- surface sections seeded: `{payload['summary']['surfaceSectionCount']}`",
        f"- seed rows: `{payload['summary']['sectionSeedRowCount']}`",
        f"- renderer implemented: `{payload['summary']['rendererImplemented']}`",
        f"- public surface updated: `{payload['summary']['publicSurfaceUpdated']}`",
        "",
        "## Seed Sections",
        "",
        "| Section | Rows | Purpose |",
        "|---|---:|---|",
    ]
    for section in payload["surfaceSections"]:
        lines.append(f"| `{section['sectionId']}` | {len(section['seedRows'])} | {section['purpose']} |")
    lines.extend(["", "## MVP Scope", ""])
    for item in payload["minimalMvpScope"]:
        lines.append(f"- `{item['mvpItemId']}`: `{item['status']}` - {item['description']}")
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
    result_path = out_dir / f"eml_d106_private_claim_topology_surface_seed_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d106_private_claim_topology_surface_seed_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d106_private_claim_topology_surface_seed_packet.json"
    feed_path = command_feed_dir / f"eml_d106_private_claim_topology_surface_seed_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d106_private_claim_topology_surface_seed_packet")
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
    print("EML_D106_PRIVATE_CLAIM_TOPOLOGY_SURFACE_SEED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
