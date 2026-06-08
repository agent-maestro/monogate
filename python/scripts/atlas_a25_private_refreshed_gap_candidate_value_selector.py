#!/usr/bin/env python3
"""ATLAS-A25 private refreshed gap candidate value selector."""

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

from scripts import atlas_a24_private_reference_value_gap_pool_refresh as a24  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_refreshed_gap_candidate_value_selector.v0"
STATUS = "ATLAS_A25_PRIVATE_REFRESHED_GAP_CANDIDATE_VALUE_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a25-private-refreshed-gap-candidate-value-selector"
SOURCE_POOL_ID = "atlas_a24_reference_value_gap_pool_v0"
SELECTED_DIRECTION_ID = "exp_negation_multiplicative_identity_direction"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A26 private exp-negation boundary feasibility packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a24_consumed",
    "refreshed_gap_value_selector_created",
    "candidate_directions_reviewed",
    "selection_rationale_recorded",
    "exp_negation_direction_selected_for_future_feasibility",
    "higher_score_square_direction_deferred",
    "next_feasibility_packet_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a24_consumed": True,
    "refreshed_gap_value_selector_created": True,
    "candidate_directions_reviewed": True,
    "selection_rationale_recorded": True,
    "exp_negation_direction_selected_for_future_feasibility": True,
    "higher_score_square_direction_deferred": True,
    "next_feasibility_packet_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
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
    "runtime_exp_replacement_claim": False,
    "runtime_sqrt_replacement_claim": False,
    "runtime_reciprocal_replacement_claim": False,
    "atlas_v0_doc_pause_selected": False,
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
    "ATLAS-A25 is a private value selector; it recommends one future feasibility packet but does not create that packet, create a candidate packet, select a proof target, or claim validity.",
    "ATLAS-A25 selects the exp-negation direction for future feasibility despite the square direction's higher raw A24 score because the square direction may be too elementary for Atlas reference value.",
    "ATLAS-A25 does not edit MachLib, run Lean, perform theorem lookup, claim exact theorem names, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, touch laptop-owned repositories, or claim checked-witness status, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
]


def build_decisions(source: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {item["entryId"]: item for item in source["candidateDirections"]}
    return [
        {
            "entryId": SELECTED_DIRECTION_ID,
            "selectionStatus": "selected_for_future_feasibility_packet",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "decision": "recommend_exp_negation_boundary_feasibility_packet",
            "valueRationale": [
                "Clean all-real guard surface.",
                "Adds exp-algebra shape without returning to log/subtraction/sqrt/reciprocal paths.",
                "Less elementary than the square nonnegativity guard while likely cheaper than trig/logistic routes.",
            ],
            "sourceDirection": by_id[SELECTED_DIRECTION_ID],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "entryId": "square_nonnegative_guard_direction",
            "selectionStatus": "deferred_despite_higher_raw_score",
            "nextArtifact": "Future private inequality-entry fit review",
            "decision": "defer_square_nonnegative_guard_direction",
            "valueRationale": [
                "Highest raw A24 score due to guard clarity and proof effort.",
                "Deferred because A24 recorded that it may be too elementary and may need a separate decision on whether inequality-only entries belong in Atlas v0.",
            ],
            "sourceDirection": by_id["square_nonnegative_guard_direction"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "entryId": "trig_pythagorean_unit_identity_direction",
            "selectionStatus": "deferred_higher_namespace_risk",
            "nextArtifact": "Future private trig namespace feasibility review",
            "decision": "defer_trig_pythagorean_unit_identity_direction",
            "valueRationale": [
                "Strong shape diversity and clean guard.",
                "Deferred because theorem namespace and proof-surface risk should not be the immediate post-sqrt recovery move.",
            ],
            "sourceDirection": by_id["trig_pythagorean_unit_identity_direction"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "entryId": "logistic_symmetry_boundary_direction",
            "selectionStatus": "deferred_definition_risk",
            "nextArtifact": "Future private logistic definition fit review",
            "decision": "defer_logistic_symmetry_boundary_direction",
            "valueRationale": [
                "High product/course reference value.",
                "Deferred because sigma must be defined precisely before any feasibility packet can be meaningful.",
            ],
            "sourceDirection": by_id["logistic_symmetry_boundary_direction"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a24.build_payload(atlas_gate_path, machlib_root)
    a24.validate_payload(source)
    decisions = build_decisions(source)
    selected = next(item for item in decisions if item["entryId"] == SELECTED_DIRECTION_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourcePoolId": source["summary"]["poolId"],
        "sourceCandidateDirectionCount": source["summary"]["candidateDirectionCount"],
        "sourceHighestReferenceValueEntryId": source["summary"]["highestReferenceValueEntryId"],
        "refreshedGapValueSelectorCreated": True,
        "candidateDirectionsReviewed": True,
        "selectionRationaleRecorded": True,
        "selectedDirectionId": selected["entryId"],
        "selectedDecision": selected["decision"],
        "selectedDirectionSourceScore": selected["sourceDirection"]["totalScore"],
        "higherScoreSquareDirectionDeferred": True,
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
        "runtimeExpReplacementClaim": False,
        "runtimeSqrtReplacementClaim": False,
        "runtimeReciprocalReplacementClaim": False,
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
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_refreshed_gap_candidate_value_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourcePoolId": source["summary"]["poolId"],
            "sourceCandidateDirections": source["candidateDirections"],
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
    if payload["sourceArtifact"] != "atlas-a24-private-reference-value-gap-pool-refresh":
        raise ValueError("ATLAS-A25 must consume ATLAS-A24")
    if summary["sourcePoolId"] != SOURCE_POOL_ID:
        raise ValueError("source pool id drift")
    if summary["sourceCandidateDirectionCount"] != 4:
        raise ValueError("expected four source directions")
    if summary["selectedDirectionId"] != SELECTED_DIRECTION_ID:
        raise ValueError("selected direction drift")
    if summary["selectedDecision"] != "recommend_exp_negation_boundary_feasibility_packet":
        raise ValueError("unexpected selected decision")
    if payload["selectedDecision"]["selectionStatus"] != "selected_for_future_feasibility_packet":
        raise ValueError("selected decision status drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "refreshedGapValueSelectorCreated",
        "candidateDirectionsReviewed",
        "selectionRationaleRecorded",
        "higherScoreSquareDirectionDeferred",
        "nextFeasibilityPacketRecommended",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
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
        "runtimeExpReplacementClaim",
        "runtimeSqrtReplacementClaim",
        "runtimeReciprocalReplacementClaim",
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
    for key in set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_refreshed_gap_candidate_value_selector",
        semantic_strength="private_value_selector_recommends_future_exp_negation_feasibility_no_packet_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a25_private_refreshed_gap_candidate_value_selector/atlas_a25_private_refreshed_gap_candidate_value_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a25_private_refreshed_gap_candidate_value_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A26 as a private exp-negation boundary feasibility packet; do not create a candidate packet or proof claim from A25.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "sourcePoolId": payload["summary"]["sourcePoolId"],
            "selectedDirectionId": payload["summary"]["selectedDirectionId"],
            "selectedDecision": payload["summary"]["selectedDecision"],
            "newCandidatePacketCreated": payload["summary"]["newCandidatePacketCreated"],
            "feasibilityPacketCreated": payload["summary"]["feasibilityPacketCreated"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("source pool", payload["summary"]["sourcePoolId"]),
        ("selected direction", payload["summary"]["selectedDirectionId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("selected source score", payload["summary"]["selectedDirectionSourceScore"]),
        ("higher-score square deferred", payload["summary"]["higherScoreSquareDirectionDeferred"]),
        ("new candidate packet created", payload["summary"]["newCandidatePacketCreated"]),
        ("feasibility packet created", payload["summary"]["feasibilityPacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    selected = payload["selectedDecision"]
    rationale_lines = [f"- {item}" for item in selected["valueRationale"]]
    decision_lines = ["| Direction | Status | Decision |", "|---|---|---|"]
    for decision in payload["valueDecisions"]:
        decision_lines.append(
            f"| `{decision['entryId']}` | `{decision['selectionStatus']}` | `{decision['decision']}` |"
        )
    return render_markdown_report(
        title="ATLAS-A25 Private Refreshed Gap Candidate Value Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Selected Rationale", rationale_lines),
            ("Value Decisions", decision_lines),
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
    result_path = out_dir / f"atlas_a25_private_refreshed_gap_candidate_value_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a25_private_refreshed_gap_candidate_value_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a25_private_refreshed_gap_candidate_value_selector.json"
    feed_path = command_feed_dir / f"atlas_a25_private_refreshed_gap_candidate_value_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a25_private_refreshed_gap_candidate_value_selector",
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
    print("ATLAS_A25_PRIVATE_REFRESHED_GAP_CANDIDATE_VALUE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
