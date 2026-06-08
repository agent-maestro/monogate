#!/usr/bin/env python3
"""ATLAS-A26 private exp-negation boundary feasibility packet."""

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

from scripts import atlas_a25_private_refreshed_gap_candidate_value_selector as a25  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_exp_negation_boundary_feasibility_packet.v0"
STATUS = "ATLAS_A26_PRIVATE_EXP_NEGATION_BOUNDARY_FEASIBILITY_PACKET_PASS"
ARTIFACT_ID = "atlas-a26-private-exp-negation-boundary-feasibility-packet"
SOURCE_DIRECTION_ID = "exp_negation_multiplicative_identity_direction"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A27 private exp-negation candidate packet selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a25_consumed",
    "feasibility_packet_created",
    "exp_negation_direction_reviewed",
    "guard_reviewed",
    "statement_shape_reviewed",
    "reference_value_reviewed",
    "blockers_recorded",
    "feasible_for_candidate_selector_recorded",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a25_consumed": True,
    "feasibility_packet_created": True,
    "exp_negation_direction_reviewed": True,
    "guard_reviewed": True,
    "statement_shape_reviewed": True,
    "reference_value_reviewed": True,
    "blockers_recorded": True,
    "feasible_for_candidate_selector_recorded": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "new_candidate_packet_created": False,
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
    "ATLAS-A26 is a private feasibility packet; it does not create a candidate packet, select a proof target, edit MachLib, run Lean, or claim candidate validity.",
    "ATLAS-A26 records exp-negation statement-shape hints and blockers for later review; it does not claim theorem names, Lean readiness, proof feasibility beyond bounded selector suitability, or checked-witness status.",
    "ATLAS-A26 does not change runtime lowering, replace exp, publish or approve public copy, create SDK/compiler/course copy, touch laptop-owned repositories, or claim public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
]


def selected_direction(source: dict[str, Any]) -> dict[str, Any]:
    return source["selectedDecision"]["sourceDirection"]


def build_feasibility_review(direction: dict[str, Any]) -> dict[str, Any]:
    return {
        "entryId": direction["entryId"],
        "candidateLabel": direction["candidateLabel"],
        "familyHint": direction["familyHint"],
        "guardReview": {
            "requiredGuard": "all real x",
            "guardStatus": "clean_all_real_guard_surface",
            "guardCaveat": "future packet must still state whether the formal theorem is pure exp-algebra, EML-shaped, or both",
        },
        "statementShapeReview": {
            "pureShapeHint": "exp x * exp (-x) = 1",
            "possibleEmlBoundaryHint": "eml (x + (-x)) 1 = 1",
            "statementShapeStatus": "feasible_for_candidate_selector_not_checked_not_lean_ready",
            "shapeCaveats": [
                "The pure exp-algebra statement and any EML-shaped statement must not be conflated.",
                "The EML-shaped hint depends on the current local EML definition and exact allowed notation.",
                "Future packet must decide whether to use `-x`, `0 - x`, or another local negation spelling.",
            ],
        },
        "referenceValueReview": {
            "referenceStatus": "moderate_high_reference_value_for_atlas_gap",
            "whyUseful": [
                "Adds exp-algebra shape without returning to log/subtraction/sqrt/reciprocal paths.",
                "Uses a clean all-real guard, making non-claims easy to communicate.",
                "Could support future guard-note/course explanation as an inverse-style identity without runtime replacement claims.",
            ],
        },
        "blockersBeforeCandidatePacket": [
            "choose pure exp statement, EML-shaped statement, or paired statement scope",
            "confirm exact local notation for negation and multiplication before any candidate packet",
            "record whether this should be Atlas reference material or only a feeder for later proof feasibility",
            "keep runtime exp replacement, public copy, product, and broad EML claims blocked",
        ],
        "feasibilityStatus": "feasible_for_later_private_candidate_selector_not_candidate_packet_not_validity_claim",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a25.build_payload(atlas_gate_path, machlib_root)
    a25.validate_payload(source)
    direction = selected_direction(source)
    review = build_feasibility_review(direction)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedDirectionId": source["summary"]["selectedDirectionId"],
        "sourceSelectedDecision": source["summary"]["selectedDecision"],
        "reviewedDirectionId": review["entryId"],
        "feasibilityPacketCreated": True,
        "expNegationDirectionReviewed": True,
        "guardReviewed": True,
        "statementShapeReviewed": True,
        "referenceValueReviewed": True,
        "blockersRecorded": True,
        "feasibleForCandidateSelectorRecorded": True,
        "feasibilityStatus": review["feasibilityStatus"],
        "requiredGuard": review["guardReview"]["requiredGuard"],
        "pureShapeHint": review["statementShapeReview"]["pureShapeHint"],
        "possibleEmlBoundaryHint": review["statementShapeReview"]["possibleEmlBoundaryHint"],
        "newCandidatePacketCreated": False,
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
        artifact_type="private_exp_negation_boundary_feasibility_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceSelectedDecision": source["selectedDecision"],
            "feasibilityReview": review,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    review = payload["feasibilityReview"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(review["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a25-private-refreshed-gap-candidate-value-selector":
        raise ValueError("ATLAS-A26 must consume ATLAS-A25")
    if summary["sourceSelectedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A26 must consume the exp-negation selected direction")
    if summary["sourceSelectedDecision"] != "recommend_exp_negation_boundary_feasibility_packet":
        raise ValueError("unexpected source decision")
    if summary["reviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("reviewed direction drift")
    if summary["requiredGuard"] != "all real x":
        raise ValueError("guard drift")
    if summary["pureShapeHint"] != "exp x * exp (-x) = 1":
        raise ValueError("pure shape drift")
    if summary["possibleEmlBoundaryHint"] != "eml (x + (-x)) 1 = 1":
        raise ValueError("EML hint drift")
    if summary["feasibilityStatus"] != "feasible_for_later_private_candidate_selector_not_candidate_packet_not_validity_claim":
        raise ValueError("feasibility status drift")
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
        "feasibilityPacketCreated",
        "expNegationDirectionReviewed",
        "guardReviewed",
        "statementShapeReviewed",
        "referenceValueReviewed",
        "blockersRecorded",
        "feasibleForCandidateSelectorRecorded",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "newCandidatePacketCreated",
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
        artifact_type="private_exp_negation_boundary_feasibility_packet",
        semantic_strength="private_feasibility_packet_reviews_exp_negation_shape_no_candidate_packet_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a26_private_exp_negation_boundary_feasibility_packet/atlas_a26_private_exp_negation_boundary_feasibility_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a26_private_exp_negation_boundary_feasibility_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A27 as a private exp-negation candidate packet selector; do not create a candidate packet or proof claim from A26.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "reviewedDirectionId": payload["summary"]["reviewedDirectionId"],
            "feasibilityStatus": payload["summary"]["feasibilityStatus"],
            "requiredGuard": payload["summary"]["requiredGuard"],
            "pureShapeHint": payload["summary"]["pureShapeHint"],
            "possibleEmlBoundaryHint": payload["summary"]["possibleEmlBoundaryHint"],
            "newCandidatePacketCreated": payload["summary"]["newCandidatePacketCreated"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["feasibilityReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("reviewed direction", payload["summary"]["reviewedDirectionId"]),
        ("feasibility status", payload["summary"]["feasibilityStatus"]),
        ("required guard", payload["summary"]["requiredGuard"]),
        ("pure shape hint", payload["summary"]["pureShapeHint"]),
        ("possible EML boundary hint", payload["summary"]["possibleEmlBoundaryHint"]),
        ("new candidate packet created", payload["summary"]["newCandidatePacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    value_lines = [f"- {item}" for item in review["referenceValueReview"]["whyUseful"]]
    blocker_lines = [f"- {item}" for item in review["blockersBeforeCandidatePacket"]]
    caveat_lines = [f"- {item}" for item in review["statementShapeReview"]["shapeCaveats"]]
    return render_markdown_report(
        title="ATLAS-A26 Private Exp-Negation Boundary Feasibility Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Reference Value", value_lines),
            ("Statement Shape Caveats", caveat_lines),
            ("Blockers Before Candidate Packet", blocker_lines),
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
    result_path = out_dir / f"atlas_a26_private_exp_negation_boundary_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a26_private_exp_negation_boundary_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a26_private_exp_negation_boundary_feasibility_packet.json"
    feed_path = command_feed_dir / f"atlas_a26_private_exp_negation_boundary_feasibility_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a26_private_exp_negation_boundary_feasibility_packet",
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
    print("ATLAS_A26_PRIVATE_EXP_NEGATION_BOUNDARY_FEASIBILITY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
