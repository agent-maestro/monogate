#!/usr/bin/env python3
"""EML-D36 Course 2 private lesson packet skeleton."""

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

from scripts import eml_d35_course2_lesson_outline_claim_boundary as d35  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_course2_private_lesson_packet_skeleton.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D36_COURSE2_PRIVATE_LESSON_PACKET_SKELETON_PASS"

CLAIM_FLAGS = {
    "lesson_packet_skeleton_started": True,
    "private_skeleton_only": True,
    "lesson_content_generated": False,
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
    "EML-D36 is a private Course 2 lesson packet skeleton only; it does not generate lesson prose or publish course copy.",
    "D36 maps D35 outline modules into skeleton slots; it does not add checked witnesses, prove theorems, edit MachLib, or typecheck Lean.",
    "D36 does not consume a laptop artifact or touch monogate-electronics, monogate-dev, public Atlas, or public education surfaces.",
]

SKELETON_SLOT_KINDS = [
    "private_objective_stub",
    "witness_anchor_stub",
    "claim_boundary_stub",
    "runtime_control_stub",
]

READINESS_GATES = [
    {
        "gateId": "private_skeleton_only",
        "gateStatus": "closed_to_public",
        "description": "The skeleton may be used for private drafting only.",
    },
    {
        "gateId": "frozen_witness_index_preserved",
        "gateStatus": "required",
        "description": "All skeleton witness anchors must come from the D35 frozen witness set.",
    },
    {
        "gateId": "d30_caveats_and_blockers_preserved",
        "gateStatus": "required",
        "description": "D30 caveats and blocked phrases remain attached to any future lesson prose.",
    },
    {
        "gateId": "no_laptop_artifact_inference",
        "gateStatus": "required",
        "description": "No hardware/laptop result may be inferred without concrete intake artifact.",
    },
    {
        "gateId": "no_public_copy_without_gate",
        "gateStatus": "closed_to_public",
        "description": "Public copy remains blocked until an explicit human-approved gate exists.",
    },
]

NEXT_ACTIONS = [
    {
        "actionId": "course2_private_lesson_draft_packet",
        "availability": "available_next_private_packet",
        "description": "Fill the D36 skeleton with private, claim-bounded draft prose.",
    },
    {
        "actionId": "course2_laptop_artifact_alignment",
        "availability": "available_after_real_laptop_artifact",
        "description": "Align with laptop outputs only after EE intake receives a concrete artifact.",
    },
    {
        "actionId": "human_approved_public_copy_gate",
        "availability": "parked_requires_explicit_human_approval",
        "description": "Public copy remains parked until explicit human approval is recorded.",
    },
]


def skeleton_module(module: dict[str, Any]) -> dict[str, Any]:
    return {
        "moduleId": module["moduleId"],
        "moduleOrder": module["moduleOrder"],
        "sourceOutlineRole": module["privateOutlineRole"],
        "skeletonStatus": "private_skeleton_slot_open",
        "slotKinds": list(SKELETON_SLOT_KINDS),
        "referenceWitnessIds": list(module["referenceWitnessIds"]),
        "slotCount": len(SKELETON_SLOT_KINDS),
        "lessonContentGenerated": False,
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def reference_ids_from_modules(modules: list[dict[str, Any]]) -> set[str]:
    return {witness_id for module in modules for witness_id in module["referenceWitnessIds"]}


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    outline = d35.build_payload(atlas_gate_path)
    d35.validate_payload(outline)
    modules = [skeleton_module(module) for module in outline["outlineModules"]]
    reference_ids = reference_ids_from_modules(modules)
    summary = {
        "sourceOutlinePacket": outline["artifactId"],
        "courseOutlineStarted": outline["summary"]["courseOutlineStarted"],
        "privateOutlineOnly": outline["summary"]["privateOutlineOnly"],
        "lessonPacketSkeletonStarted": True,
        "privateSkeletonOnly": True,
        "skeletonModuleCount": len(modules),
        "skeletonSlotKindCount": len(SKELETON_SLOT_KINDS),
        "totalSkeletonSlotCount": sum(module["slotCount"] for module in modules),
        "readinessGateCount": len(READINESS_GATES),
        "nextActionCount": len(NEXT_ACTIONS),
        "referencedFrozenWitnessCount": len(reference_ids),
        "allSkeletonReferencesFrozen": outline["summary"]["allModuleReferencesFrozen"] is True
        and len(reference_ids) == outline["summary"]["referencedFrozenWitnessCount"],
        "d30RequiredCaveatCount": outline["summary"]["d30RequiredCaveatCount"],
        "d30BlockedGlobalPhraseCount": outline["summary"]["d30BlockedGlobalPhraseCount"],
        "lessonContentGenerated": False,
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
        "runtimeLoweringControl": outline["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "arbitraryDepthClaim": False,
        "publicReady": False,
        "claimFlagsAllBounded": CLAIM_FLAGS["lesson_packet_skeleton_started"] is True
        and CLAIM_FLAGS["private_skeleton_only"] is True
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"lesson_packet_skeleton_started", "private_skeleton_only"}
        )
        and all(
            module["claimFlags"]["lesson_packet_skeleton_started"] is True
            and module["claimFlags"]["private_skeleton_only"] is True
            and all(
                value is False
                for key, value in module["claimFlags"].items()
                if key not in {"lesson_packet_skeleton_started", "private_skeleton_only"}
            )
            for module in modules
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_course2_private_lesson_packet_skeleton_v0",
        "artifactId": "eml-d36-course2-private-lesson-packet-skeleton",
        "status": STATUS,
        "decision": "course2_private_lesson_packet_skeleton_started",
        "date": DATE,
        "sourceOutlinePacket": outline["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "skeletonModules": modules,
        "readinessGates": list(READINESS_GATES),
        "nextActions": list(NEXT_ACTIONS),
        "preservedRequiredCaveats": list(outline["preservedRequiredCaveats"]),
        "preservedBlockedGlobalPhrases": list(outline["preservedBlockedGlobalPhrases"]),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceOutlinePacket"] != "eml-d35-course2-lesson-outline-claim-boundary":
        raise ValueError("D36 must consume D35")
    if summary["courseOutlineStarted"] is not True or summary["privateOutlineOnly"] is not True:
        raise ValueError("D35 private outline boundary must be preserved")
    if summary["lessonPacketSkeletonStarted"] is not True or summary["privateSkeletonOnly"] is not True:
        raise ValueError("D36 must start private skeleton")
    if summary["skeletonModuleCount"] != 4:
        raise ValueError("expected four skeleton modules")
    if summary["skeletonSlotKindCount"] != 4 or summary["totalSkeletonSlotCount"] != 16:
        raise ValueError("unexpected skeleton slot count")
    if summary["readinessGateCount"] != 5:
        raise ValueError("expected five readiness gates")
    if summary["nextActionCount"] != 3:
        raise ValueError("expected three next actions")
    if summary["referencedFrozenWitnessCount"] != 6 or summary["allSkeletonReferencesFrozen"] is not True:
        raise ValueError("skeleton must reference exactly the frozen witness set")
    if summary["d30RequiredCaveatCount"] != 5 or summary["d30BlockedGlobalPhraseCount"] != 8:
        raise ValueError("D30 caveat/blocker counts drifted")
    for key in [
        "lessonContentGenerated",
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
    if payload["claimFlags"]["lesson_packet_skeleton_started"] is not True:
        raise ValueError("skeleton flag must be true")
    if payload["claimFlags"]["private_skeleton_only"] is not True:
        raise ValueError("private skeleton flag must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"lesson_packet_skeleton_started", "private_skeleton_only"} and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(module["lessonContentGenerated"] for module in payload["skeletonModules"]):
        raise ValueError("skeleton modules must not contain lesson content")
    if any(module["publicPromotionAllowed"] for module in payload["skeletonModules"]):
        raise ValueError("skeleton modules must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_course2_private_lesson_packet_skeleton",
        "validationStatus": "pass",
        "semanticStrength": "private_course2_skeleton_no_lesson_content_no_public_copy",
        "source": f"python/results/eml_d36_course2_private_lesson_packet_skeleton/eml_d36_course2_private_lesson_packet_skeleton_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d36_course2_private_lesson_packet_skeleton_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "skeletonModuleCount": payload["summary"]["skeletonModuleCount"],
        "nextAction": "Fill the private Course 2 lesson skeleton with claim-bounded draft prose; keep publication and laptop-owned repos untouched.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D36 Course 2 Private Lesson Packet Skeleton",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D36 creates a private Course 2 lesson packet skeleton without lesson prose.",
        "",
        "| Module | Slot count | Witness count |",
        "|---|---:|---:|",
    ]
    for module in payload["skeletonModules"]:
        lines.append(f"| `{module['moduleId']}` | {module['slotCount']} | {len(module['referenceWitnessIds'])} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- skeleton modules: `{payload['summary']['skeletonModuleCount']}`",
            f"- total skeleton slots: `{payload['summary']['totalSkeletonSlotCount']}`",
            f"- private skeleton only: `{payload['summary']['privateSkeletonOnly']}`",
            f"- lesson content generated: `{payload['summary']['lessonContentGenerated']}`",
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
    result_path = out_dir / f"eml_d36_course2_private_lesson_packet_skeleton_{STAMP}.json"
    report_path = report_dir / f"eml_d36_course2_private_lesson_packet_skeleton_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d36_course2_private_lesson_packet_skeleton.json"
    feed_path = command_feed_dir / f"eml_d36_course2_private_lesson_packet_skeleton_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d36_course2_private_lesson_packet_skeleton")
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
    print("EML_D36_COURSE2_PRIVATE_LESSON_PACKET_SKELETON_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
