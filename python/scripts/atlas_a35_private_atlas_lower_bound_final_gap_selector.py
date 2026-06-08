#!/usr/bin/env python3
"""ATLAS-A35 private Atlas lower-bound final gap selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.setrecursionlimit(10000)

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a34_private_exp_negation_checked_wrapper_surface_review as a34  # noqa: E402
from scripts import atlas_a24_private_reference_value_gap_pool_refresh as a24  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    assert_claim_flags_bounded,
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_atlas_lower_bound_final_gap_selector.v0"
STATUS = "ATLAS_A35_PRIVATE_ATLAS_LOWER_BOUND_FINAL_GAP_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a35-private-atlas-lower-bound-final-gap-selector"
SOURCE_ARTIFACT_ID = "atlas-a34-private-exp-negation-checked-wrapper-surface-review"
SELECTED_DIRECTION_ID = "trig_pythagorean_unit_identity_direction"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A36 private trig pythagorean feasibility packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a34_consumed",
    "a24_gap_pool_referenced",
    "lower_bound_gap_selector_created",
    "candidate_directions_reviewed",
    "selection_rationale_recorded",
    "trig_direction_selected_for_future_feasibility",
    "exp_negation_marked_already_reviewed",
    "square_direction_deferred_as_too_elementary",
    "logistic_direction_deferred_definition_risk",
    "next_feasibility_packet_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "atlas_a34_consumed": True,
    "a24_gap_pool_referenced": True,
    "lower_bound_gap_selector_created": True,
    "candidate_directions_reviewed": True,
    "selection_rationale_recorded": True,
    "trig_direction_selected_for_future_feasibility": True,
    "exp_negation_marked_already_reviewed": True,
    "square_direction_deferred_as_too_elementary": True,
    "logistic_direction_deferred_definition_risk": True,
    "next_feasibility_packet_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "new_candidate_packet_created": False,
    "feasibility_packet_created": False,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_rejected": False,
    "candidate_disproved": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "proof_attempt_completed": False,
    "machlib_file_changed": False,
    "machlib_commit_created": False,
    "lean_typecheck_performed": False,
    "lean_typecheck_passed": False,
    "theorem_lookup_performed": False,
    "exact_theorem_names_claimed": False,
    "runtime_lowering_changed": False,
    "runtime_trig_replacement_claim": False,
    "runtime_exp_replacement_claim": False,
    "public_atlas_promotion": False,
    "public_copy_approved": False,
    "public_surface_updated": False,
    "public_education_promotion": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "product_implementation_started": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "laptop_artifact_consumed": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "catalog_completeness_claim": False,
    "target_lower_bound_reached_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "ATLAS-A35 is a private selector for the next lower-bound gap; it does not create the feasibility packet, candidate packet, proof branch, checked witness, or validity claim.",
    "ATLAS-A35 selects the trig pythagorean direction for future feasibility because it adds shape diversity after exp-negation; it does not claim theorem names, Lean readiness, proof feasibility beyond selector suitability, or checked-witness status.",
    "ATLAS-A35 does not edit MachLib, run Lean, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, start D110, touch laptop-owned repositories, or claim target lower-bound reached, catalog completeness, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
]


def build_decisions(pool: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {item["entryId"]: item for item in pool["candidateDirections"]}
    return [
        {
            "entryId": SELECTED_DIRECTION_ID,
            "selectionStatus": "selected_for_future_feasibility_packet",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "decision": "recommend_trig_pythagorean_feasibility_packet",
            "valueRationale": [
                "Adds genuine trig/oscillatory shape diversity after the exp-negation wrapper filled the exp-algebra slot.",
                "The intended guard is all real x, which is communicable for reviewers if the statement stays narrow.",
                "The proof-surface risk is visible and can be bounded by a feasibility packet before theorem lookup or MachLib edits.",
            ],
            "sourceDirection": by_id[SELECTED_DIRECTION_ID],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "entryId": "square_nonnegative_guard_direction",
            "selectionStatus": "deferred_as_too_elementary_for_final_lower_bound_slot",
            "nextArtifact": "Future private inequality-entry fit review",
            "decision": "defer_square_nonnegative_guard_direction",
            "valueRationale": [
                "The square direction has high raw score and clear guards.",
                "It remains potentially useful for guard pedagogy but may be too elementary as the 15th row.",
            ],
            "sourceDirection": by_id["square_nonnegative_guard_direction"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "entryId": "exp_negation_multiplicative_identity_direction",
            "selectionStatus": "already_reviewed_as_a33_a34_private_row_candidate",
            "nextArtifact": "None; exp-negation surface review already completed.",
            "decision": "do_not_select_duplicate_exp_negation_direction",
            "valueRationale": [
                "A33 created the checked wrapper and A34 reviewed its private surface.",
                "Selecting it again would not close the remaining lower-bound gap.",
            ],
            "sourceDirection": by_id["exp_negation_multiplicative_identity_direction"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "entryId": "logistic_symmetry_boundary_direction",
            "selectionStatus": "deferred_definition_risk",
            "nextArtifact": "Future private logistic definition fit review",
            "decision": "defer_logistic_symmetry_boundary_direction",
            "valueRationale": [
                "The logistic direction has strong course/product reference value.",
                "It still needs a precise sigma definition before feasibility review would be meaningful.",
            ],
            "sourceDirection": by_id["logistic_symmetry_boundary_direction"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a34.build_payload(atlas_gate_path, machlib_root)
    a34.validate_payload(source)
    pool = a24.build_payload(atlas_gate_path, machlib_root)
    a24.validate_payload(pool)
    decisions = build_decisions(pool)
    selected = next(item for item in decisions if item["entryId"] == SELECTED_DIRECTION_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceAtlasRowCount": source["summary"]["atlasRowCount"],
        "sourceAdditionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "gapPoolArtifact": pool["artifactId"],
        "gapPoolId": pool["summary"]["poolId"],
        "gapPoolCandidateDirectionCount": pool["summary"]["candidateDirectionCount"],
        "lowerBoundGapSelectorCreated": True,
        "candidateDirectionsReviewed": True,
        "selectionRationaleRecorded": True,
        "selectedDirectionId": selected["entryId"],
        "selectedDecision": selected["decision"],
        "selectedDirectionSourceScore": selected["sourceDirection"]["totalScore"],
        "selectedFamilyHint": selected["sourceDirection"]["familyHint"],
        "selectedShapeHint": selected["sourceDirection"]["shapeHint"],
        "selectedGuardHint": selected["sourceDirection"]["guardHint"],
        "trigDirectionSelectedForFutureFeasibility": True,
        "expNegationMarkedAlreadyReviewed": True,
        "squareDirectionDeferredAsTooElementary": True,
        "logisticDirectionDeferredDefinitionRisk": True,
        "nextFeasibilityPacketRecommended": True,
        "newCandidatePacketCreated": False,
        "feasibilityPacketCreated": False,
        "candidateValidityBlocked": True,
        "candidateSelectedForProof": False,
        "candidateValidityClaim": False,
        "candidateRejected": False,
        "candidateDisproved": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "proofAttemptCompleted": False,
        "machlibEditBlocked": True,
        "machlibFileChanged": False,
        "machlibCommitCreated": False,
        "leanTypecheckBlocked": True,
        "leanTypecheckPerformed": False,
        "leanTypecheckPassed": False,
        "theoremLookupPerformed": False,
        "exactTheoremNamesClaimed": False,
        "runtimeLoweringChanged": False,
        "runtimeTrigReplacementClaim": False,
        "runtimeExpReplacementClaim": False,
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "catalogCompletenessClaim": False,
        "targetLowerBoundReachedClaim": False,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_atlas_lower_bound_final_gap_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "gapPoolArtifact": pool["artifactId"],
            "valueDecisions": decisions,
            "selectedDecision": selected,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    for decision in payload["valueDecisions"]:
        assert_claim_flags_bounded(decision["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != SOURCE_ARTIFACT_ID:
        raise ValueError("ATLAS-A35 must consume ATLAS-A34")
    if summary["selectedDirectionId"] != SELECTED_DIRECTION_ID:
        raise ValueError("selected direction drift")
    if summary["selectedFamilyHint"] != "trig_boundary":
        raise ValueError("selected family drift")
    if summary["selectedShapeHint"] != "sin x * sin x + cos x * cos x = 1":
        raise ValueError("selected shape drift")
    if summary["selectedGuardHint"] != "all real x":
        raise ValueError("selected guard drift")
    if summary["gapPoolCandidateDirectionCount"] != 4:
        raise ValueError("gap pool count drift")
    for key in [
        "lowerBoundGapSelectorCreated",
        "candidateDirectionsReviewed",
        "selectionRationaleRecorded",
        "trigDirectionSelectedForFutureFeasibility",
        "expNegationMarkedAlreadyReviewed",
        "squareDirectionDeferredAsTooElementary",
        "logisticDirectionDeferredDefinitionRisk",
        "nextFeasibilityPacketRecommended",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "newCandidatePacketCreated",
        "feasibilityPacketCreated",
        "candidateSelectedForProof",
        "candidateValidityClaim",
        "candidateRejected",
        "candidateDisproved",
        "candidateProved",
        "proofAttemptStarted",
        "proofAttemptCompleted",
        "machlibFileChanged",
        "machlibCommitCreated",
        "leanTypecheckPerformed",
        "leanTypecheckPassed",
        "theoremLookupPerformed",
        "exactTheoremNamesClaimed",
        "runtimeLoweringChanged",
        "runtimeTrigReplacementClaim",
        "runtimeExpReplacementClaim",
        "publicPromotionAllowed",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "catalogCompletenessClaim",
        "targetLowerBoundReachedClaim",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["atlasRowCount"] != 14:
        raise ValueError("Atlas row count drift")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound must remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 1:
        raise ValueError("expected one additional bounded artifact")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_atlas_lower_bound_final_gap_selector",
        semantic_strength="private_selector_only_trig_feasibility_recommended_no_validity_public_runtime_product_claims",
        source=f"python/results/atlas_a35_private_atlas_lower_bound_final_gap_selector/atlas_a35_private_atlas_lower_bound_final_gap_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a35_private_atlas_lower_bound_final_gap_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A36 as a private trig pythagorean feasibility packet only; do not perform theorem lookup, proof, MachLib edits, Lean checks, public, runtime, product, or course work.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedDirectionId": payload["summary"]["selectedDirectionId"],
            "selectedShapeHint": payload["summary"]["selectedShapeHint"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "additionalArtifactsNeededForLowerBound": payload["summary"]["additionalArtifactsNeededForLowerBound"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("gap pool artifact", payload["summary"]["gapPoolArtifact"]),
        ("selected direction", payload["summary"]["selectedDirectionId"]),
        ("selected family", payload["summary"]["selectedFamilyHint"]),
        ("selected shape", payload["summary"]["selectedShapeHint"]),
        ("selected guard", payload["summary"]["selectedGuardHint"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("MachLib file changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    decision_lines = [
        f"- `{item['entryId']}`: {item['selectionStatus']} -> {item['decision']}"
        for item in payload["valueDecisions"]
    ]
    blocker_lines = [
        "- confirm trig theorem namespace and exact theorem spelling only in a future feasibility/theorem-lookup gate",
        "- keep candidate validity, proof, MachLib edit, and Lean checks blocked in A35",
        "- keep runtime trig replacement, public copy, SDK/course material, and product claims blocked",
    ]
    return render_markdown_report(
        title="ATLAS-A35 Private Atlas Lower-Bound Final Gap Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Value Decisions", decision_lines),
            ("Blocked Before A36", blocker_lines),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    atlas_gate_path: Path,
    machlib_root: Path,
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path, machlib_root)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"atlas_a35_private_atlas_lower_bound_final_gap_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a35_private_atlas_lower_bound_final_gap_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a35_private_atlas_lower_bound_final_gap_selector.json"
    feed_path = command_feed_dir / f"atlas_a35_private_atlas_lower_bound_final_gap_selector_feed_{STAMP}.json"
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
    parser.add_argument("--machlib-root", type=Path, default=ROOT.parent / "machlib")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/atlas_a35_private_atlas_lower_bound_final_gap_selector",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.atlas_gate_path, args.machlib_root)
    validate_payload(payload)
    if args.build:
        build_outputs(
            args.out_dir,
            args.report_dir,
            args.evidence_dir,
            args.command_feed_dir,
            args.atlas_gate_path,
            args.machlib_root,
        )
    print("ATLAS_A35_PRIVATE_ATLAS_LOWER_BOUND_FINAL_GAP_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
