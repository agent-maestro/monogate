#!/usr/bin/env python3
"""EML-D35 Course 2 lesson-outline claim-boundary packet."""

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

from scripts import eml_d34_course2_private_reference_packet as d34  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_course2_lesson_outline_claim_boundary.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D35_COURSE2_LESSON_OUTLINE_CLAIM_BOUNDARY_PASS"

CLAIM_FLAGS = {
    "course_outline_started": True,
    "private_outline_only": True,
    "lesson_packet_generated": False,
    "course_publication_started": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "advantage_lab_case_added": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "runtime_lowering_changed": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "arbitrary_depth_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D35 is a private Course 2 outline boundary packet; it does not generate lesson content or publish course copy.",
    "D35 sequences private planning anchors from D34; it does not add checked witnesses, prove theorems, edit MachLib, or typecheck Lean.",
    "D35 does not consume a laptop artifact or touch monogate-electronics, monogate-dev, public Atlas, or public education surfaces.",
]

OUTLINE_MODULES = [
    {
        "moduleId": "course2_orientation_claim_boundary",
        "moduleOrder": 1,
        "privateOutlineRole": "introduce_private_claim_boundaries",
        "referenceWitnessIds": [
            "constants_zero_one_e_boundary",
            "ln_from_eml_boundary",
        ],
    },
    {
        "moduleId": "course2_single_stage_subtraction_boundary",
        "moduleOrder": 2,
        "privateOutlineRole": "anchor_single_guarded_subtraction_instance",
        "referenceWitnessIds": [
            "subtraction_boundary_affine_offset",
        ],
    },
    {
        "moduleId": "course2_nested_chain_boundary",
        "moduleOrder": 3,
        "privateOutlineRole": "compare_two_stage_affine_nested_and_three_stage_instances",
        "referenceWitnessIds": [
            "subtraction_boundary_two_stage_chain",
            "subtraction_boundary_affine_nested_chain",
            "subtraction_boundary_three_stage_chain",
        ],
    },
    {
        "moduleId": "course2_runtime_and_public_copy_hold",
        "moduleOrder": 4,
        "privateOutlineRole": "state_runtime_controls_and_public_copy_hold",
        "referenceWitnessIds": [
            "subtraction_boundary_affine_offset",
            "subtraction_boundary_two_stage_chain",
            "subtraction_boundary_three_stage_chain",
        ],
    },
]

CLAIM_BOUNDARY_RULES = [
    {
        "ruleId": "private_outline_only",
        "ruleStatus": "required",
        "description": "The outline can guide private sequencing only; it is not a public lesson.",
    },
    {
        "ruleId": "frozen_witness_index_only",
        "ruleStatus": "required",
        "description": "Use only the six D34 reference witness ids as planning anchors.",
    },
    {
        "ruleId": "d30_caveats_required",
        "ruleStatus": "required",
        "description": "Carry D30 caveats into any later lesson packet draft.",
    },
    {
        "ruleId": "blocked_phrases_required",
        "ruleStatus": "required",
        "description": "Keep theorem-discovery, broad-family, runtime-performance, and public-ready language blocked.",
    },
    {
        "ruleId": "no_laptop_repo_touch",
        "ruleStatus": "required",
        "description": "Do not touch or infer laptop-agent outputs from this packet.",
    },
]

NEXT_ACTIONS = [
    {
        "actionId": "course2_private_lesson_packet_skeleton",
        "availability": "available_next_private_packet",
        "description": "Create a private lesson packet skeleton from the D35 outline boundaries.",
    },
    {
        "actionId": "course2_laptop_artifact_alignment",
        "availability": "available_after_real_laptop_artifact",
        "description": "Align with laptop-agent outputs only after a concrete artifact arrives through intake.",
    },
    {
        "actionId": "human_approved_public_copy_gate",
        "availability": "parked_requires_explicit_human_approval",
        "description": "Public copy remains parked until an explicit human-approved gate exists.",
    },
]


def reference_ids_from_rows(rows: list[dict[str, Any]]) -> set[str]:
    return {row["witnessId"] for row in rows}


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    reference = d34.build_payload(atlas_gate_path)
    d34.validate_payload(reference)
    reference_ids = reference_ids_from_rows(reference["courseReferenceRows"])
    module_reference_ids = {witness_id for module in OUTLINE_MODULES for witness_id in module["referenceWitnessIds"]}
    summary = {
        "sourceReferencePacket": reference["artifactId"],
        "courseReferencePacketStarted": reference["summary"]["courseReferencePacketStarted"],
        "privateCourseReferenceOnly": reference["summary"]["privateCourseReferenceOnly"],
        "courseOutlineStarted": True,
        "privateOutlineOnly": True,
        "courseReferenceRowCount": reference["summary"]["courseReferenceRowCount"],
        "outlineModuleCount": len(OUTLINE_MODULES),
        "claimBoundaryRuleCount": len(CLAIM_BOUNDARY_RULES),
        "nextActionCount": len(NEXT_ACTIONS),
        "referencedFrozenWitnessCount": len(module_reference_ids),
        "allModuleReferencesFrozen": module_reference_ids == reference_ids,
        "d30RequiredCaveatCount": reference["summary"]["d30RequiredCaveatCount"],
        "d30BlockedGlobalPhraseCount": reference["summary"]["d30BlockedGlobalPhraseCount"],
        "lessonPacketGenerated": False,
        "coursePublicationStarted": False,
        "publicCopyApproved": False,
        "humanApprovalRecorded": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "advantageLabCaseAdded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": reference["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "arbitraryDepthClaim": False,
        "publicReady": False,
        "claimFlagsAllBounded": CLAIM_FLAGS["course_outline_started"] is True
        and CLAIM_FLAGS["private_outline_only"] is True
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"course_outline_started", "private_outline_only"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_course2_lesson_outline_claim_boundary_v0",
        "artifactId": "eml-d35-course2-lesson-outline-claim-boundary",
        "status": STATUS,
        "decision": "course2_private_lesson_outline_claim_boundary_started",
        "date": DATE,
        "sourceReferencePacket": reference["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "outlineModules": list(OUTLINE_MODULES),
        "claimBoundaryRules": list(CLAIM_BOUNDARY_RULES),
        "nextActions": list(NEXT_ACTIONS),
        "preservedRequiredCaveats": list(reference["preservedRequiredCaveats"]),
        "preservedBlockedGlobalPhrases": list(reference["preservedBlockedGlobalPhrases"]),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceReferencePacket"] != "eml-d34-course2-private-reference-packet":
        raise ValueError("D35 must consume D34")
    if summary["courseReferencePacketStarted"] is not True or summary["privateCourseReferenceOnly"] is not True:
        raise ValueError("D34 private reference boundary must be preserved")
    if summary["courseOutlineStarted"] is not True or summary["privateOutlineOnly"] is not True:
        raise ValueError("D35 must start private outline boundary")
    if summary["courseReferenceRowCount"] != 6:
        raise ValueError("expected six Course 2 reference rows")
    if summary["outlineModuleCount"] != 4:
        raise ValueError("expected four outline modules")
    if summary["claimBoundaryRuleCount"] != 5:
        raise ValueError("expected five claim boundary rules")
    if summary["nextActionCount"] != 3:
        raise ValueError("expected three next actions")
    if summary["referencedFrozenWitnessCount"] != 6 or summary["allModuleReferencesFrozen"] is not True:
        raise ValueError("outline must reference exactly the frozen witness index")
    if summary["d30RequiredCaveatCount"] != 5 or summary["d30BlockedGlobalPhraseCount"] != 8:
        raise ValueError("D30 caveat/blocker counts drifted")
    for key in [
        "lessonPacketGenerated",
        "coursePublicationStarted",
        "publicCopyApproved",
        "humanApprovalRecorded",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "advantageLabCaseAdded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "runtimeLoweringChanged",
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "arbitraryDepthClaim",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_subtraction_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    if payload["claimFlags"]["course_outline_started"] is not True:
        raise ValueError("course outline flag must be true")
    if payload["claimFlags"]["private_outline_only"] is not True:
        raise ValueError("private outline flag must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"course_outline_started", "private_outline_only"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_course2_lesson_outline_claim_boundary",
        "validationStatus": "pass",
        "semanticStrength": "private_course2_outline_boundary_no_lesson_no_public_copy",
        "source": f"python/results/eml_d35_course2_lesson_outline_claim_boundary/eml_d35_course2_lesson_outline_claim_boundary_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d35_course2_lesson_outline_claim_boundary_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "outlineModuleCount": payload["summary"]["outlineModuleCount"],
        "nextAction": "Build a private Course 2 lesson packet skeleton; do not publish copy or touch laptop-owned repos.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D35 Course 2 Lesson Outline Claim Boundary",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D35 creates a private Course 2 lesson-outline boundary without generating lesson content.",
        "",
        "| Module | Role | Witness count |",
        "|---|---|---:|",
    ]
    for module in payload["outlineModules"]:
        lines.append(
            f"| `{module['moduleId']}` | `{module['privateOutlineRole']}` | {len(module['referenceWitnessIds'])} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- outline modules: `{payload['summary']['outlineModuleCount']}`",
            f"- private outline only: `{payload['summary']['privateOutlineOnly']}`",
            f"- all module references frozen: `{payload['summary']['allModuleReferencesFrozen']}`",
            f"- lesson packet generated: `{payload['summary']['lessonPacketGenerated']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- electronics repo touched: `{payload['summary']['electronicsRepoTouched']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d35_course2_lesson_outline_claim_boundary_{STAMP}.json"
    report_path = report_dir / f"eml_d35_course2_lesson_outline_claim_boundary_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d35_course2_lesson_outline_claim_boundary.json"
    feed_path = command_feed_dir / f"eml_d35_course2_lesson_outline_claim_boundary_feed_{STAMP}.json"
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
    stamp_0527 = "2026_05_27"
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--atlas-gate-path", type=Path, default=ROOT / f"python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_{stamp_0527}.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d35_course2_lesson_outline_claim_boundary")
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
    print("EML_D35_COURSE2_LESSON_OUTLINE_CLAIM_BOUNDARY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
