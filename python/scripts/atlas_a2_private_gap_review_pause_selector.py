#!/usr/bin/env python3
"""ATLAS-A2 private Atlas gap review or pause selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a1_private_checked_witness_table as a1  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    assert_claim_flags_bounded,
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-07"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_atlas_gap_review_pause_selector.v0"
STATUS = "ATLAS_A2_PRIVATE_GAP_REVIEW_PAUSE_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a2-private-gap-review-pause-selector"
SELECTED_OPTION_ID = "prepare_two_gap_candidate_shortlist"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A3 private two-gap candidate shortlist"

TRUE_CLAIM_FLAGS = {
    "atlas_a1_consumed",
    "private_gap_review_created",
    "target_gap_recorded",
    "family_balance_reviewed",
    "two_gap_slots_required",
    "next_private_selector_recommended",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a1_consumed": True,
    "private_gap_review_created": True,
    "target_gap_recorded": True,
    "family_balance_reviewed": True,
    "two_gap_slots_required": True,
    "next_private_selector_recommended": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "private_atlas_table_sufficient_for_current_review": False,
    "pause_selected": False,
    "external_input_wait_selected": False,
    "candidate_shortlist_created": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "proof_attempt_started": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "runtime_lowering_changed": False,
    "public_atlas_promotion": False,
    "public_copy_approved": False,
    "public_surface_updated": False,
    "public_education_promotion": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "claim_topology_ui_created": False,
    "renderer_implemented": False,
    "visualization_quality_claim": False,
    "product_implementation_started": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "laptop_artifact_consumed": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "catalog_completeness_claim": False,
    "target_lower_bound_reached_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "ATLAS-A2 is a private selector over the ATLAS-A1 table; it does not add checked witnesses or claim the Atlas target lower bound is reached.",
    "ATLAS-A2 recommends preparing a two-gap shortlist because the current checked row count is thirteen against a fifteen-row lower bound; it does not select identities, start proof work, edit MachLib, run Lean, or change runtime lowering.",
    "ATLAS-A2 does not publish or approve public copy, create SDK/compiler/course copy, implement a claim-topology renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def option(
    option_id: str,
    selection_status: str,
    priority_score: int,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "selectionStatus": selection_status,
        "priorityScore": priority_score,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    needed = source["summary"]["additionalArtifactsNeededForLowerBound"]
    return [
        option(
            "prepare_two_gap_candidate_shortlist",
            "selected_next",
            94,
            NEXT_RECOMMENDED_ARTIFACT,
            [
                f"ATLAS-A1 records {source['summary']['atlasRowCount']} checked rows and {needed} rows still needed for the lower bound.",
                "The current table is useful, but a lower-bound Atlas claim remains blocked until two more high-quality checked artifacts exist.",
                "A shortlist can identify material gap shapes without selecting identities or starting proof work.",
            ],
            [
                "must list exactly two gap slots",
                "must not claim candidate validity",
                "must not start proof, Lean, MachLib, or runtime work",
            ],
        ),
        option(
            "pause_on_private_atlas_table",
            "available_if_human_prefers_review",
            78,
            "Pause Atlas lane on ATLAS-A1 private table",
            [
                "ATLAS-A1 already reduces reviewer load by making the current checked rows visible.",
                "Pausing is acceptable if review, product, or electronics input is more valuable than expanding the checked set.",
            ],
            [
                "target lower bound remains unreached",
                "must not imply catalog completeness",
            ],
        ),
        option(
            "wait_for_reviewer_product_or_electronics_input",
            "available_if_external_signal_arrives",
            70,
            "Hold Atlas lane pending actual external input",
            [
                "A reviewer or concrete product/electronics artifact may change which gaps matter most.",
                "Waiting avoids speculative proof-branch expansion.",
            ],
            [
                "requires actual input text or artifact",
                "must not consume absent reviewer responses",
            ],
        ),
    ]


def build_gap_slots(source: dict[str, Any]) -> list[dict[str, Any]]:
    represented = sorted(source["familyCounts"])
    return [
        {
            "slotId": "gap_slot_1_non_log_non_subtraction_boundary",
            "slotRole": "material_diversity_gap",
            "status": "slot_required_not_candidate_selected",
            "desiredProperties": [
                "not another log/log1p/log1m/probability-logit boundary",
                "not another nested subtraction boundary",
                "small enough for human review",
                "guard conditions explicit and easy to audit",
            ],
            "representedFamiliesConsidered": represented,
            "blockedClaims": [
                "no candidate identity selected",
                "no proof attempt started",
                "no MachLib or Lean work started",
            ],
        },
        {
            "slotId": "gap_slot_2_runtime_control_contrast_boundary",
            "slotRole": "runtime_control_contrast_gap",
            "status": "slot_required_not_candidate_selected",
            "desiredProperties": [
                "uses a runtime-control boundary not already dominated by protected log/log1p/expm1 or subtraction",
                "keeps the mathematical statement familiar enough for public-review potential",
                "has guards that can be stated without broad compiler or performance claims",
            ],
            "representedFamiliesConsidered": represented,
            "blockedClaims": [
                "no candidate identity selected",
                "no runtime lowering changed",
                "no performance or compiler-correctness claim",
            ],
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a1.build_payload(atlas_gate_path)
    a1.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    gap_slots = build_gap_slots(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "familyCount": source["summary"]["familyCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "remainingSlotsBeforeUpperBound": source["summary"]["remainingSlotsBeforeUpperBound"],
        "privateGapReviewCreated": True,
        "targetGapRecorded": True,
        "familyBalanceReviewed": True,
        "twoGapSlotsRequired": len(gap_slots) == 2,
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "nextPrivateSelectorRecommended": True,
        "privateAtlasTableSufficientForCurrentReview": False,
        "pauseSelected": False,
        "externalInputWaitSelected": False,
        "candidateShortlistCreated": False,
        "newIdentityCandidateSelected": False,
        "proofAttemptStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "runtimeLoweringChanged": False,
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "catalogCompletenessClaim": False,
        "targetLowerBoundReachedClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_atlas_gap_review_pause_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "familyCounts": source["familyCounts"],
            "gapSlots": gap_slots,
            "options": options,
            "selectedOption": selected,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a1-private-checked-witness-table":
        raise ValueError("ATLAS-A2 must consume ATLAS-A1")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected exactly two missing rows for lower bound")
    if len(payload["gapSlots"]) != 2 or summary["twoGapSlotsRequired"] is not True:
        raise ValueError("expected exactly two required gap slots")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected selected next artifact")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option must be selected_next")
    for key in [
        "privateGapReviewCreated",
        "targetGapRecorded",
        "familyBalanceReviewed",
        "twoGapSlotsRequired",
        "nextPrivateSelectorRecommended",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "privateAtlasTableSufficientForCurrentReview",
        "pauseSelected",
        "externalInputWaitSelected",
        "candidateShortlistCreated",
        "newIdentityCandidateSelected",
        "proofAttemptStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "runtimeLoweringChanged",
        "publicPromotionAllowed",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "catalogCompletenessClaim",
        "targetLowerBoundReachedClaim",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")
    for slot in payload["gapSlots"]:
        if slot["status"] != "slot_required_not_candidate_selected":
            raise ValueError("gap slots must not select candidates")
    for option_row in payload["options"]:
        assert_claim_flags_bounded(option_row["claimFlags"], TRUE_CLAIM_FLAGS)


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_atlas_gap_review_pause_selector",
        semantic_strength="private_selector_records_two_missing_gap_slots_no_candidate_no_proof_no_public_promotion",
        source=f"python/results/atlas_a2_private_gap_review_pause_selector/atlas_a2_private_gap_review_pause_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a2_private_gap_review_pause_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A3 as a private two-gap candidate shortlist.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "additionalArtifactsNeededForLowerBound": payload["summary"]["additionalArtifactsNeededForLowerBound"],
            "gapSlotCount": len(payload["gapSlots"]),
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("Atlas rows", payload["summary"]["atlasRowCount"]),
        ("target range", f"{payload['summary']['targetMin']}-{payload['summary']['targetMax']}"),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
        ("candidate shortlist created", payload["summary"]["candidateShortlistCreated"]),
        ("public promotion allowed", payload["summary"]["publicPromotionAllowed"]),
    ]
    gap_lines = ["| Slot | Role | Status |", "|---|---|---|"]
    for slot in payload["gapSlots"]:
        gap_lines.append(f"| `{slot['slotId']}` | `{slot['slotRole']}` | `{slot['status']}` |")
    option_lines = ["| Option | Status | Score | Next artifact |", "|---|---|---:|---|"]
    for item in payload["options"]:
        option_lines.append(
            f"| `{item['optionId']}` | `{item['selectionStatus']}` | {item['priorityScore']} | {item['nextArtifact']} |"
        )
    return render_markdown_report(
        title="ATLAS-A2 Private Atlas Gap Review Or Pause Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Gap Slots", gap_lines),
            ("Options", option_lines),
        ],
        non_claims=payload["nonClaims"],
    )


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
    result_path = out_dir / f"atlas_a2_private_gap_review_pause_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a2_private_gap_review_pause_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a2_private_gap_review_pause_selector.json"
    feed_path = command_feed_dir / f"atlas_a2_private_gap_review_pause_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/atlas_a2_private_gap_review_pause_selector")
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
    print("ATLAS_A2_PRIVATE_GAP_REVIEW_PAUSE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
