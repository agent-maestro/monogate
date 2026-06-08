#!/usr/bin/env python3
"""ATLAS-A36 private trig pythagorean feasibility packet."""

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

from scripts import atlas_a35_private_atlas_lower_bound_final_gap_selector as a35  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_trig_pythagorean_feasibility_packet.v0"
STATUS = "ATLAS_A36_PRIVATE_TRIG_PYTHAGOREAN_FEASIBILITY_PACKET_PASS"
ARTIFACT_ID = "atlas-a36-private-trig-pythagorean-feasibility-packet"
SOURCE_DIRECTION_ID = "trig_pythagorean_unit_identity_direction"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A37 private trig pythagorean candidate packet selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a35_consumed",
    "feasibility_packet_created",
    "trig_direction_reviewed",
    "guard_reviewed",
    "statement_shape_reviewed",
    "reference_value_reviewed",
    "blockers_recorded",
    "feasible_for_candidate_selector_recorded",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "theorem_lookup_blocked",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "atlas_a35_consumed": True,
    "feasibility_packet_created": True,
    "trig_direction_reviewed": True,
    "guard_reviewed": True,
    "statement_shape_reviewed": True,
    "reference_value_reviewed": True,
    "blockers_recorded": True,
    "feasible_for_candidate_selector_recorded": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "theorem_lookup_blocked": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
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
    "runtime_trig_replacement_claim": False,
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
    "ATLAS-A36 is a private feasibility packet; it does not create a candidate packet, select a proof target, edit MachLib, run Lean, perform theorem lookup, or claim candidate validity.",
    "ATLAS-A36 records trig statement-shape hints and blockers for later review; it does not claim exact theorem names, Lean readiness, proof feasibility beyond bounded selector suitability, or checked-witness status.",
    "ATLAS-A36 does not change runtime lowering, replace trig functions, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, start D110, touch laptop-owned repositories, or claim target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
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
            "guardCaveat": "future candidate packet must keep this as a pure trig identity unless a separate EML-shaped statement is explicitly gated",
        },
        "statementShapeReview": {
            "pureShapeHint": "sin x * sin x + cos x * cos x = 1",
            "possibleEmlBoundaryHint": "deferred_no_eml_shape_selected",
            "statementShapeStatus": "feasible_for_candidate_selector_not_checked_not_lean_ready",
            "shapeCaveats": [
                "The statement should stay pure trig until a separate EML boundary shape is justified.",
                "Future theorem lookup must decide exact local notation for powers versus repeated multiplication.",
                "The identity should not be widened into broad trigonometric lowering, runtime, or complex-domain claims.",
            ],
        },
        "referenceValueReview": {
            "referenceStatus": "high_reference_value_for_final_lower_bound_gap",
            "whyUseful": [
                "Adds oscillatory/trigonometric shape diversity beyond log, subtraction, sqrt, reciprocal, and exp-algebra rows.",
                "Has a simple all-real guard that is easy to explain to reviewers.",
                "Can become a useful Atlas/course reference only after a later checked witness and copy gate.",
            ],
        },
        "blockersBeforeCandidatePacket": [
            "decide whether the future candidate packet should use repeated multiplication or square notation",
            "confirm the target remains a pure real trig identity with no EML companion claim",
            "record theorem-lookup risk without performing theorem lookup in A36",
            "keep runtime trig replacement, public copy, product, SDK, course, and broad EML claims blocked",
        ],
        "feasibilityStatus": "feasible_for_later_private_candidate_selector_not_candidate_packet_not_validity_claim",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a35.build_payload(atlas_gate_path, machlib_root)
    a35.validate_payload(source)
    direction = selected_direction(source)
    review = build_feasibility_review(direction)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedDirectionId": source["summary"]["selectedDirectionId"],
        "sourceSelectedDecision": source["summary"]["selectedDecision"],
        "reviewedDirectionId": review["entryId"],
        "feasibilityPacketCreated": True,
        "trigDirectionReviewed": True,
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
        "theoremLookupBlocked": True,
        "theoremLookupPerformed": False,
        "exactTheoremNamesClaimed": False,
        "runtimeLoweringChanged": False,
        "runtimeTrigReplacementClaim": False,
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
        artifact_type="private_trig_pythagorean_feasibility_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
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
    if payload["sourceArtifact"] != "atlas-a35-private-atlas-lower-bound-final-gap-selector":
        raise ValueError("ATLAS-A36 must consume ATLAS-A35")
    if summary["sourceSelectedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A36 must consume the trig selected direction")
    if summary["sourceSelectedDecision"] != "recommend_trig_pythagorean_feasibility_packet":
        raise ValueError("unexpected source decision")
    if summary["reviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("reviewed direction drift")
    if summary["requiredGuard"] != "all real x":
        raise ValueError("guard drift")
    if summary["pureShapeHint"] != "sin x * sin x + cos x * cos x = 1":
        raise ValueError("pure shape drift")
    if summary["possibleEmlBoundaryHint"] != "deferred_no_eml_shape_selected":
        raise ValueError("EML hint drift")
    if summary["feasibilityStatus"] != "feasible_for_later_private_candidate_selector_not_candidate_packet_not_validity_claim":
        raise ValueError("feasibility status drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["atlasRowCount"] != 14:
        raise ValueError("expected fourteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 1:
        raise ValueError("expected one additional artifact for lower bound")
    for key in [
        "feasibilityPacketCreated",
        "trigDirectionReviewed",
        "guardReviewed",
        "statementShapeReviewed",
        "referenceValueReviewed",
        "blockersRecorded",
        "feasibleForCandidateSelectorRecorded",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "theoremLookupBlocked",
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
        "runtimeTrigReplacementClaim",
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


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_trig_pythagorean_feasibility_packet",
        semantic_strength="private_feasibility_packet_only_trig_candidate_selector_recommended_no_validity_public_runtime_product_claims",
        source=f"python/results/atlas_a36_private_trig_pythagorean_feasibility_packet/atlas_a36_private_trig_pythagorean_feasibility_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a36_private_trig_pythagorean_feasibility_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A37 as a private trig pythagorean candidate packet selector only; keep theorem lookup, proof, MachLib edits, Lean checks, public, runtime, product, and course work blocked.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "reviewedDirectionId": payload["summary"]["reviewedDirectionId"],
            "pureShapeHint": payload["summary"]["pureShapeHint"],
            "requiredGuard": payload["summary"]["requiredGuard"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "additionalArtifactsNeededForLowerBound": payload["summary"]["additionalArtifactsNeededForLowerBound"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["feasibilityReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("reviewed direction", payload["summary"]["reviewedDirectionId"]),
        ("required guard", payload["summary"]["requiredGuard"]),
        ("pure shape hint", payload["summary"]["pureShapeHint"]),
        ("possible EML boundary hint", payload["summary"]["possibleEmlBoundaryHint"]),
        ("feasibility status", payload["summary"]["feasibilityStatus"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("theorem lookup performed", payload["summary"]["theoremLookupPerformed"]),
        ("MachLib file changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    reference_lines = [f"- {item}" for item in review["referenceValueReview"]["whyUseful"]]
    caveat_lines = [f"- {item}" for item in review["statementShapeReview"]["shapeCaveats"]]
    blocker_lines = [f"- {item}" for item in review["blockersBeforeCandidatePacket"]]
    return render_markdown_report(
        title="ATLAS-A36 Private Trig Pythagorean Feasibility Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Reference Value", reference_lines),
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
    result_path = out_dir / f"atlas_a36_private_trig_pythagorean_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a36_private_trig_pythagorean_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a36_private_trig_pythagorean_feasibility_packet.json"
    feed_path = command_feed_dir / f"atlas_a36_private_trig_pythagorean_feasibility_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a36_private_trig_pythagorean_feasibility_packet",
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
    print("ATLAS_A36_PRIVATE_TRIG_PYTHAGOREAN_FEASIBILITY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
