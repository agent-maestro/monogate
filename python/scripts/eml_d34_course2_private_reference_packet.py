#!/usr/bin/env python3
"""EML-D34 Course 2 private checked-witness reference packet."""

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

from scripts import eml_d33_post_freeze_next_selector as d33  # noqa: E402
from scripts import eml_d32_subtraction_family_pause_freeze_packet as d32  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_course2_private_reference_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D34_COURSE2_PRIVATE_REFERENCE_PACKET_PASS"

CLAIM_FLAGS = {
    "course_reference_packet_started": True,
    "private_course_reference_only": True,
    "course_publication_started": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "lesson_packet_generated": False,
    "electronics_repo_touched": False,
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
    "EML-D34 is a private Course 2 reference packet only; it does not create a public lesson packet or publish D30 copy.",
    "D34 references the frozen checked-witness index for planning language; it does not prove new theorems, edit MachLib, or typecheck Lean.",
    "D34 does not touch monogate-electronics, monogate-dev, public Atlas, or public education surfaces.",
]


def course_reference_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "witnessId": row["witnessId"],
        "machlibName": row["machlibName"],
        "course2ReferenceRole": "private_reference_only",
        "allowedUse": "bounded planning reference for Course 2 wording and sequencing",
        "requiredCaveatCount": row["requiredCaveatCount"],
        "blockedPhraseCount": row["blockedPhraseCount"],
        "runtimeControl": row["runtimeControl"],
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


COURSE2_REFERENCE_GUARDS = [
    {
        "guardId": "private_reference_only",
        "guardStatus": "required",
        "description": "Course 2 may use these witness rows as private planning references only.",
    },
    {
        "guardId": "frozen_index_preserved",
        "guardStatus": "required",
        "description": "Do not add, remove, rename, or generalize the six frozen witness ids in this packet.",
    },
    {
        "guardId": "d30_caveats_preserved",
        "guardStatus": "required",
        "description": "Carry D30 caveats forward when drafting any future course-facing wording.",
    },
    {
        "guardId": "blocked_phrases_preserved",
        "guardStatus": "required",
        "description": "Keep theorem-discovery, broad-family, runtime, compiler, formal-equivalence, and public-ready phrases blocked.",
    },
    {
        "guardId": "no_laptop_repo_touch",
        "guardStatus": "required",
        "description": "Do not touch monogate-electronics or monogate-dev from this research-side packet.",
    },
]

NEXT_COURSE2_ACTIONS = [
    {
        "actionId": "course2_lesson_outline_claim_boundary",
        "availability": "available_next_private_packet",
        "description": "Draft a private Course 2 outline that references the frozen witnesses only as claim-bounded planning anchors.",
    },
    {
        "actionId": "course2_laptop_artifact_intake_alignment",
        "availability": "available_after_real_laptop_artifact",
        "description": "Use EE-BRIDGE/EE-GUARD intake only after the laptop agent returns a concrete artifact.",
    },
    {
        "actionId": "human_approved_public_copy_gate",
        "availability": "parked_requires_explicit_human_approval",
        "description": "Public copy remains parked until a separate human-approved gate exists.",
    },
]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d33.build_payload(atlas_gate_path)
    d33.validate_payload(selector)
    freeze = d32.build_payload(atlas_gate_path)
    d32.validate_payload(freeze)
    rows = [course_reference_row(row) for row in freeze["frozenWitnessRows"]]
    summary = {
        "sourceSelector": selector["artifactId"],
        "sourceFreezePacket": freeze["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "courseReferencePacketStarted": True,
        "privateCourseReferenceOnly": True,
        "frozenWitnessCount": freeze["summary"]["frozenWitnessCount"],
        "courseReferenceRowCount": len(rows),
        "course2GuardCount": len(COURSE2_REFERENCE_GUARDS),
        "nextCourse2ActionCount": len(NEXT_COURSE2_ACTIONS),
        "d30RequiredCaveatCount": freeze["summary"]["d30RequiredCaveatCount"],
        "d30BlockedGlobalPhraseCount": freeze["summary"]["d30BlockedGlobalPhraseCount"],
        "familyDeepeningPaused": freeze["summary"]["familyDeepeningPaused"],
        "checkedWitnessIndexFrozen": freeze["summary"]["checkedWitnessIndexFrozen"],
        "coursePublicationStarted": False,
        "lessonPacketGenerated": False,
        "publicCopyApproved": False,
        "humanApprovalRecorded": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "electronicsRepoTouched": False,
        "advantageLabCaseAdded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": freeze["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "arbitraryDepthClaim": False,
        "publicReady": False,
        "claimFlagsAllBounded": CLAIM_FLAGS["course_reference_packet_started"] is True
        and CLAIM_FLAGS["private_course_reference_only"] is True
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"course_reference_packet_started", "private_course_reference_only"}
        )
        and all(
            row["claimFlags"]["course_reference_packet_started"] is True
            and row["claimFlags"]["private_course_reference_only"] is True
            and all(
                value is False
                for key, value in row["claimFlags"].items()
                if key not in {"course_reference_packet_started", "private_course_reference_only"}
            )
            for row in rows
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_course2_private_reference_packet_v0",
        "artifactId": "eml-d34-course2-private-reference-packet",
        "status": STATUS,
        "decision": "course2_private_checked_witness_reference_packet_started",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceFreezePacket": freeze["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "courseReferenceRows": rows,
        "course2ReferenceGuards": list(COURSE2_REFERENCE_GUARDS),
        "nextCourse2Actions": list(NEXT_COURSE2_ACTIONS),
        "preservedRequiredCaveats": list(freeze["preservedRequiredCaveats"]),
        "preservedBlockedGlobalPhrases": list(freeze["preservedBlockedGlobalPhrases"]),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d33-post-freeze-next-selector":
        raise ValueError("D34 must consume D33")
    if payload["sourceFreezePacket"] != "eml-d32-subtraction-family-pause-freeze-packet":
        raise ValueError("D34 must preserve D32 freeze packet")
    if summary["selectedOptionId"] != "course_scaling_private_reference":
        raise ValueError("D34 requires D33 course reference selection")
    if summary["courseReferencePacketStarted"] is not True or summary["privateCourseReferenceOnly"] is not True:
        raise ValueError("D34 must start private Course 2 reference packet")
    if summary["frozenWitnessCount"] != 6 or summary["courseReferenceRowCount"] != 6:
        raise ValueError("expected six Course 2 reference rows")
    if summary["course2GuardCount"] != 5:
        raise ValueError("expected five Course 2 guards")
    if summary["nextCourse2ActionCount"] != 3:
        raise ValueError("expected three next Course 2 actions")
    if summary["d30RequiredCaveatCount"] != 5 or summary["d30BlockedGlobalPhraseCount"] != 8:
        raise ValueError("D30 caveat/blocker counts drifted")
    if summary["familyDeepeningPaused"] is not True or summary["checkedWitnessIndexFrozen"] is not True:
        raise ValueError("D32 pause/freeze must remain true")
    for key in [
        "coursePublicationStarted",
        "lessonPacketGenerated",
        "publicCopyApproved",
        "humanApprovalRecorded",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "electronicsRepoTouched",
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
    if payload["claimFlags"]["course_reference_packet_started"] is not True:
        raise ValueError("Course reference flag must be true")
    if payload["claimFlags"]["private_course_reference_only"] is not True:
        raise ValueError("private Course reference flag must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"course_reference_packet_started", "private_course_reference_only"} and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(row["publicPromotionAllowed"] for row in payload["courseReferenceRows"]):
        raise ValueError("course reference rows must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_course2_private_reference_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_course2_reference_packet_no_public_copy_no_repo_touch",
        "source": f"python/results/eml_d34_course2_private_reference_packet/eml_d34_course2_private_reference_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d34_course2_private_reference_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "courseReferenceRowCount": payload["summary"]["courseReferenceRowCount"],
        "nextAction": "Build a private Course 2 lesson-outline claim-boundary packet; do not publish D30 copy or touch laptop-owned repos.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D34 Course 2 Private Reference Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D34 creates a private Course 2 reference packet from the frozen checked-witness index.",
        "",
        "| Witness | Course 2 role | Runtime control |",
        "|---|---|---|",
    ]
    for row in payload["courseReferenceRows"]:
        lines.append(f"| `{row['witnessId']}` | `{row['course2ReferenceRole']}` | {row['runtimeControl']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Course reference rows: `{payload['summary']['courseReferenceRowCount']}`",
            f"- private Course reference only: `{payload['summary']['privateCourseReferenceOnly']}`",
            f"- lesson packet generated: `{payload['summary']['lessonPacketGenerated']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- electronics repo touched: `{payload['summary']['electronicsRepoTouched']}`",
            f"- runtime lowering changed: `{payload['summary']['runtimeLoweringChanged']}`",
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
    result_path = out_dir / f"eml_d34_course2_private_reference_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d34_course2_private_reference_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d34_course2_private_reference_packet.json"
    feed_path = command_feed_dir / f"eml_d34_course2_private_reference_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d34_course2_private_reference_packet")
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
    print("EML_D34_COURSE2_PRIVATE_REFERENCE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
