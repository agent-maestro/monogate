#!/usr/bin/env python3
"""EML-D37 research lane reset selector."""

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

from scripts import eml_d36_course2_private_lesson_packet_skeleton as d36  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_research_lane_reset_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D37_RESEARCH_LANE_RESET_SELECTOR_PASS"

CLAIM_FLAGS = {
    "research_lane_reset_selected": True,
    "course_drafting_parked_research_side": True,
    "bounded_identity_selector_selected": True,
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
    "EML-D37 resets the research lane after D36; it does not fill the Course 2 skeleton or generate course prose.",
    "D37 parks research-side course drafting for the user/laptop-agent lane and selects a bounded EML identity selector as the next research-side artifact.",
    "D37 starts no MachLib edit, Lean typecheck, proof attempt, runtime-lowering change, public surface update, or laptop-owned repo touch.",
]


def lane_option(
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
    skeleton = d36.build_payload(atlas_gate_path)
    d36.validate_payload(skeleton)
    options = [
        lane_option(
            "bounded_eml_identity_branch_selector",
            "eml_research_lane",
            "selected_next",
            86,
            "EML-D38 bounded EML identity branch selector",
            [
                "D36 completed a private course skeleton, but user/laptop-agent own course drafting and criteria.",
                "Research-side work should return to advancing EML with bounded identity candidates and explicit non-claims.",
                "A selector-only artifact avoids premature MachLib edits while choosing a precise next research target.",
            ],
            [
                "must choose one bounded identity family only",
                "must not reopen broad subtraction-family claims",
                "must not typecheck or edit MachLib in the selector",
            ],
        ),
        lane_option(
            "monogate_evidence_pipeline_hardening",
            "platform_tooling_lane",
            "candidate_later",
            68,
            "Future evidence pipeline hardening packet",
            [
                "Evidence tooling remains valuable for Monogate as a whole.",
                "The immediate correction is to move away from course drafting and back into EML advancement.",
            ],
            [
                "define concrete schema or reviewer gap",
                "avoid public-surface expansion without approval",
            ],
        ),
        lane_option(
            "course_artifact_reviewer_intake",
            "course_reviewer_lane",
            "parked_until_laptop_artifact",
            52,
            "Future course artifact reviewer intake packet",
            [
                "The research side should review course artifacts only after the user/laptop-agent produces them.",
                "No concrete course packet from the laptop lane is recorded in D37.",
            ],
            [
                "requires concrete laptop/user course artifact",
                "must not touch monogate-electronics or monogate-dev",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceSkeletonPacket": skeleton["artifactId"],
        "lessonPacketSkeletonStarted": skeleton["summary"]["lessonPacketSkeletonStarted"],
        "privateSkeletonOnly": skeleton["summary"]["privateSkeletonOnly"],
        "skeletonModuleCount": skeleton["summary"]["skeletonModuleCount"],
        "researchLaneResetSelected": True,
        "courseDraftingParkedResearchSide": True,
        "courseOwner": "user_and_laptop_agent",
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "boundedIdentitySelectorSelected": True,
        "courseDraftPacketStarted": False,
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
        "runtimeLoweringControl": skeleton["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "arbitraryDepthClaim": False,
        "publicReady": False,
        "claimFlagsAllBounded": CLAIM_FLAGS["research_lane_reset_selected"] is True
        and CLAIM_FLAGS["course_drafting_parked_research_side"] is True
        and CLAIM_FLAGS["bounded_identity_selector_selected"] is True
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "research_lane_reset_selected",
                "course_drafting_parked_research_side",
                "bounded_identity_selector_selected",
            }
        )
        and all(
            option["claimFlags"]["research_lane_reset_selected"] is True
            and option["claimFlags"]["course_drafting_parked_research_side"] is True
            and option["claimFlags"]["bounded_identity_selector_selected"] is True
            and all(
                value is False
                for key, value in option["claimFlags"].items()
                if key
                not in {
                    "research_lane_reset_selected",
                    "course_drafting_parked_research_side",
                    "bounded_identity_selector_selected",
                }
            )
            for option in options
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_research_lane_reset_selector_v0",
        "artifactId": "eml-d37-research-lane-reset-selector",
        "status": STATUS,
        "decision": "select_bounded_eml_identity_branch_selector",
        "date": DATE,
        "sourceSkeletonPacket": skeleton["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "laneOptions": options,
        "selectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSkeletonPacket"] != "eml-d36-course2-private-lesson-packet-skeleton":
        raise ValueError("D37 must consume D36")
    if summary["lessonPacketSkeletonStarted"] is not True or summary["privateSkeletonOnly"] is not True:
        raise ValueError("D36 skeleton boundary must be preserved")
    if summary["researchLaneResetSelected"] is not True:
        raise ValueError("research lane reset must be selected")
    if summary["courseDraftingParkedResearchSide"] is not True:
        raise ValueError("course drafting must be parked research-side")
    if summary["courseOwner"] != "user_and_laptop_agent":
        raise ValueError("course owner must be user/laptop agent")
    if summary["optionCount"] != 3:
        raise ValueError("expected three lane options")
    if summary["selectedOptionId"] != "bounded_eml_identity_branch_selector":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D38 bounded EML identity branch selector":
        raise ValueError("unexpected next artifact")
    if summary["boundedIdentitySelectorSelected"] is not True:
        raise ValueError("bounded identity selector must be selected")
    for key in [
        "courseDraftPacketStarted",
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
    for key in [
        "research_lane_reset_selected",
        "course_drafting_parked_research_side",
        "bounded_identity_selector_selected",
    ]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {
            "research_lane_reset_selected",
            "course_drafting_parked_research_side",
            "bounded_identity_selector_selected",
        } and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_research_lane_reset_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_research_lane_reset_no_course_draft_no_public_copy",
        "source": f"python/results/eml_d37_research_lane_reset_selector/eml_d37_research_lane_reset_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d37_research_lane_reset_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D38 as a bounded EML identity branch selector; keep course drafting in the user/laptop-agent lane.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D37 Research Lane Reset Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D37 parks research-side course drafting and selects the next EML research lane.",
        "",
        "| Option | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for option in payload["laneOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | {option['priorityScore']} | {option['nextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- course owner: `{payload['summary']['courseOwner']}`",
            f"- selected next artifact: `{payload['summary']['selectedNextArtifact']}`",
            f"- course draft packet started: `{payload['summary']['courseDraftPacketStarted']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
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
    result_path = out_dir / f"eml_d37_research_lane_reset_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d37_research_lane_reset_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d37_research_lane_reset_selector.json"
    feed_path = command_feed_dir / f"eml_d37_research_lane_reset_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d37_research_lane_reset_selector")
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
    print("EML_D37_RESEARCH_LANE_RESET_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
