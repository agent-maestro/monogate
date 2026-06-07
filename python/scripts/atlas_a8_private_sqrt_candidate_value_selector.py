#!/usr/bin/env python3
"""ATLAS-A8 private sqrt boundary candidate value selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a7_private_sqrt_boundary_reference_feasibility_packet as a7  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_sqrt_candidate_value_selector.v0"
STATUS = "ATLAS_A8_PRIVATE_SQRT_CANDIDATE_VALUE_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a8-private-sqrt-candidate-value-selector"
SOURCE_ENTRY_ID = "sqrt_square_nonnegative_roundtrip_candidate"
SELECTED_OPTION_ID = "create_abs_normalized_sqrt_candidate_packet"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A9 private abs-normalized sqrt boundary candidate packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a7_consumed",
    "candidate_value_selector_created",
    "sqrt_reference_value_reviewed",
    "abs_normalized_shape_selected",
    "candidate_packet_recommended",
    "candidate_validity_blocked",
    "public_promotion_blocked",
    "next_private_packet_recommended",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a7_consumed": True,
    "candidate_value_selector_created": True,
    "sqrt_reference_value_reviewed": True,
    "abs_normalized_shape_selected": True,
    "candidate_packet_recommended": True,
    "candidate_validity_blocked": True,
    "public_promotion_blocked": True,
    "next_private_packet_recommended": True,
    "d109_hold_respected": True,
    "candidate_packet_created": False,
    "sqrt_candidate_packet_selected": False,
    "simple_guarded_shape_selected": False,
    "atlas_v0_doc_pause_selected": False,
    "sqrt_entry_parked": False,
    "shortlist_entries_are_checked_witnesses": False,
    "candidate_validity_claim": False,
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
    "ATLAS-A8 is a private selector; it recommends a later candidate packet but does not create a candidate packet, checked witness, proof branch, or validity claim.",
    "ATLAS-A8 selects an abs-normalized sqrt candidate shape because A7 recorded the abs-normalization caveat; it does not claim that shape is Lean-ready or provable.",
    "ATLAS-A8 does not edit MachLib, run Lean, start proof work, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_options() -> list[dict[str, Any]]:
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "candidateShape": "abs_normalized_then_guarded",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "rationale": [
                "A7 records strong reference value for the sqrt boundary.",
                "A7 also records that the proof-facing route should likely pass through sqrt (x * x) = |x|.",
                "A candidate packet can preserve both the abs-normalized shape and the guarded public-facing reduction without starting proof work.",
            ],
            "blockers": [
                "must not claim candidate validity",
                "must not run Lean or edit MachLib",
                "must preserve public/runtime/product non-claims",
            ],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "create_simple_guarded_sqrt_candidate_packet",
            "selectionStatus": "rejected_for_now_due_abs_caveat",
            "candidateShape": "simple_guarded_only",
            "nextArtifact": "Future simple guarded sqrt candidate packet",
            "rationale": [
                "The simple guarded form is useful for explanation but too easy to overstate as proof-facing.",
            ],
            "blockers": ["abs-normalization caveat must be handled first"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_reference_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "candidateShape": None,
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "rationale": [
                "The Atlas already has enough material to start a single reference document draft.",
            ],
            "blockers": ["target lower bound remains unreached"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "park_sqrt_entry",
            "selectionStatus": "not_selected",
            "candidateShape": None,
            "nextArtifact": "Park sqrt entry pending reviewer input",
            "rationale": ["A7 made the blocker explicit, so parking remains possible."],
            "blockers": ["would leave the current two-artifact Atlas gap unchanged"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a7.build_payload(atlas_gate_path)
    a7.validate_payload(source)
    options = build_options()
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    review = source["sqrtReferenceReview"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedEntryId": source["summary"]["reviewedEntryId"],
        "sourceStatementShapeStatus": review["statementShapeReview"]["statementShapeStatus"],
        "sourceAbsNormalizationCaveatRecorded": source["summary"]["absNormalizationCaveatRecorded"],
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "candidateValueSelectorCreated": True,
        "sqrtReferenceValueReviewed": True,
        "selectedOptionId": selected["optionId"],
        "selectedCandidateShape": selected["candidateShape"],
        "selectedNextArtifact": selected["nextArtifact"],
        "absNormalizedShapeSelected": True,
        "candidatePacketRecommended": True,
        "candidatePacketCreated": False,
        "sqrtCandidatePacketSelected": False,
        "simpleGuardedShapeSelected": False,
        "atlasV0DocPauseSelected": False,
        "sqrtEntryParked": False,
        "candidateValidityBlocked": True,
        "shortlistEntriesAreCheckedWitnesses": False,
        "candidateValidityClaim": False,
        "newIdentityCandidateSelected": False,
        "nextBoundedIdentityBranchSelected": False,
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
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_sqrt_candidate_value_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceSqrtReferenceReview": review,
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
    if payload["sourceArtifact"] != "atlas-a7-private-sqrt-boundary-reference-feasibility-packet":
        raise ValueError("ATLAS-A8 must consume ATLAS-A7")
    if summary["sourceReviewedEntryId"] != SOURCE_ENTRY_ID:
        raise ValueError("A8 must consume the sqrt entry")
    if summary["sourceStatementShapeStatus"] != "reference_feasible_but_not_lean_ready":
        raise ValueError("A8 must preserve A7's not-Lean-ready caveat")
    if summary["sourceAbsNormalizationCaveatRecorded"] is not True:
        raise ValueError("A8 must preserve abs-normalization caveat")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedCandidateShape"] != "abs_normalized_then_guarded":
        raise ValueError("A8 must select abs-normalized candidate shape")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option must be selected_next")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected selected next artifact")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "candidateValueSelectorCreated",
        "sqrtReferenceValueReviewed",
        "absNormalizedShapeSelected",
        "candidatePacketRecommended",
        "candidateValidityBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "candidatePacketCreated",
        "sqrtCandidatePacketSelected",
        "simpleGuardedShapeSelected",
        "atlasV0DocPauseSelected",
        "sqrtEntryParked",
        "shortlistEntriesAreCheckedWitnesses",
        "candidateValidityClaim",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
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
    for item in payload["options"]:
        assert_claim_flags_bounded(item["claimFlags"], TRUE_CLAIM_FLAGS)
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_sqrt_candidate_value_selector",
        semantic_strength="private_selector_recommends_abs_normalized_sqrt_candidate_packet_no_candidate_no_validity_no_proof",
        source=f"python/results/atlas_a8_private_sqrt_candidate_value_selector/atlas_a8_private_sqrt_candidate_value_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a8_private_sqrt_candidate_value_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A9 as a private abs-normalized sqrt boundary candidate packet.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "selectedCandidateShape": payload["summary"]["selectedCandidateShape"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("candidate shape", payload["summary"]["selectedCandidateShape"]),
        ("candidate packet created", payload["summary"]["candidatePacketCreated"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    option_lines = ["| Option | Status | Shape |", "|---|---|---|"]
    for item in payload["options"]:
        option_lines.append(f"| `{item['optionId']}` | `{item['selectionStatus']}` | `{item['candidateShape']}` |")
    return render_markdown_report(
        title="ATLAS-A8 Private Sqrt Boundary Candidate Value Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[("Options", option_lines)],
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
    result_path = out_dir / f"atlas_a8_private_sqrt_candidate_value_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a8_private_sqrt_candidate_value_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a8_private_sqrt_candidate_value_selector.json"
    feed_path = command_feed_dir / f"atlas_a8_private_sqrt_candidate_value_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/atlas_a8_private_sqrt_candidate_value_selector")
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
    print("ATLAS_A8_PRIVATE_SQRT_CANDIDATE_VALUE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
