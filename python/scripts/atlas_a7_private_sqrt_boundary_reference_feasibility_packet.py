#!/usr/bin/env python3
"""ATLAS-A7 private sqrt boundary reference-feasibility packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a6_private_reference_value_candidate_selector as a6  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_sqrt_boundary_reference_feasibility_packet.v0"
STATUS = "ATLAS_A7_PRIVATE_SQRT_BOUNDARY_REFERENCE_FEASIBILITY_PACKET_PASS"
ARTIFACT_ID = "atlas-a7-private-sqrt-boundary-reference-feasibility-packet"
SOURCE_ENTRY_ID = "sqrt_square_nonnegative_roundtrip_candidate"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A8 private sqrt boundary candidate value selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a6_consumed",
    "reference_feasibility_packet_created",
    "sqrt_entry_reviewed",
    "nonnegativity_guard_reviewed",
    "statement_shape_reviewed",
    "abs_normalization_caveat_recorded",
    "course_sdk_reference_value_recorded",
    "blocked_claims_recorded",
    "candidate_validity_blocked",
    "public_promotion_blocked",
    "next_private_selector_recommended",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a6_consumed": True,
    "reference_feasibility_packet_created": True,
    "sqrt_entry_reviewed": True,
    "nonnegativity_guard_reviewed": True,
    "statement_shape_reviewed": True,
    "abs_normalization_caveat_recorded": True,
    "course_sdk_reference_value_recorded": True,
    "blocked_claims_recorded": True,
    "candidate_validity_blocked": True,
    "public_promotion_blocked": True,
    "next_private_selector_recommended": True,
    "d109_hold_respected": True,
    "sqrt_candidate_packet_selected": False,
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
    "ATLAS-A7 is a private reference-feasibility packet; it does not prove, typecheck, implement, or validate the sqrt boundary entry.",
    "ATLAS-A7 records course/SDK reference value and the abs-normalization caveat for later selection; it does not claim the sqrt statement shape is Lean-ready or selected for proof.",
    "ATLAS-A7 does not edit MachLib, run Lean, start proof work, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def sqrt_score(source: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in source["referenceValueScores"] if item["entryId"] == SOURCE_ENTRY_ID)


def build_reference_review(source: dict[str, Any]) -> dict[str, Any]:
    score = sqrt_score(source)
    return {
        "entryId": score["entryId"],
        "candidateLabel": score["candidateLabel"],
        "familyHint": score["familyHint"],
        "guardHint": score["guardHint"],
        "statementShapeHint": score["statementShapeHint"],
        "referenceValueStatus": "high_reference_value_needs_statement_shape_review_not_candidate_validity",
        "guardReview": {
            "requiredGuard": "0 <= x",
            "guardPurpose": "keeps sqrt (x * x) aligned with the nonnegative branch and gives a clean course-facing guard",
            "knownCaveat": "future proof-facing form may require exact nonnegativity lemmas for square roots and multiplication",
        },
        "statementShapeReview": {
            "candidateStatementHint": "0 <= x -> eml (sqrt (x * x)) x = x",
            "statementShapeStatus": "reference_feasible_but_not_lean_ready",
            "absNormalizationCaveat": "The mathematically standard shape is sqrt (x * x) = |x|; the proposed guarded form relies on 0 <= x to reduce |x| to x.",
            "shapeCaveats": [
                "May need an abs-normalized intermediate statement before any Lean-facing candidate packet.",
                "May need exact theorem support for sqrt_mul_self or sq_sqrt-style lemmas.",
                "Must not imply runtime replacement of sqrt or multiplication.",
            ],
        },
        "referenceUsefulness": {
            "courseHook": "Explains why nonnegativity guards matter when simplifying square-root roundtrips.",
            "sdkGuardNoteHook": "Can ground a guard note that a sqrt-square simplification requires a nonnegative input condition.",
            "protectedRuntimeHint": "Useful as a boundary example for protected sqrt behavior, not as a lowering rule.",
            "publicWitnessPotential": "Potentially clear public example if later checked, because the non-claim boundary is easy to state.",
        },
        "reviewCaveats": [
            "The simple guarded statement is reference-feasible but may not be the best proof-facing statement.",
            "The abs-normalization step is the main proof-shape risk and must be handled before any candidate-validity claim.",
            "No theorem lookup, Lean typecheck, or MachLib proof attempt was performed.",
        ],
        "blockedClaims": [
            "not a checked witness",
            "not a candidate validity claim",
            "not selected as a proof branch",
            "no proof attempt started",
            "no MachLib edit",
            "no Lean typecheck",
            "no runtime lowering change",
            "no public copy approval",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a6.build_payload(atlas_gate_path)
    a6.validate_payload(source)
    review = build_reference_review(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedEntryId": source["summary"]["selectedEntryId"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "reviewedEntryId": review["entryId"],
        "familyHint": review["familyHint"],
        "guardHint": review["guardHint"],
        "statementShapeHint": review["statementShapeHint"],
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "referenceFeasibilityPacketCreated": True,
        "sqrtEntryReviewed": True,
        "nonnegativityGuardReviewed": True,
        "statementShapeReviewed": True,
        "absNormalizationCaveatRecorded": True,
        "courseSdkReferenceValueRecorded": True,
        "blockedClaimsRecorded": True,
        "candidateValidityBlocked": True,
        "sqrtCandidatePacketSelected": False,
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
        artifact_type="private_sqrt_boundary_reference_feasibility_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceSelectedOption": source["selectedOption"],
            "sqrtReferenceReview": review,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    review = payload["sqrtReferenceReview"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a6-private-reference-value-candidate-selector":
        raise ValueError("ATLAS-A7 must consume ATLAS-A6")
    if summary["sourceSelectedEntryId"] != SOURCE_ENTRY_ID or summary["reviewedEntryId"] != SOURCE_ENTRY_ID:
        raise ValueError("A7 must review the sqrt entry")
    if summary["guardHint"] != "0 <= x":
        raise ValueError("guard drift")
    if summary["statementShapeHint"] != "0 <= x -> eml (sqrt (x * x)) x = x":
        raise ValueError("statement shape drift")
    if review["statementShapeReview"]["statementShapeStatus"] != "reference_feasible_but_not_lean_ready":
        raise ValueError("statement shape status drift")
    if "sqrt (x * x) = |x|" not in review["statementShapeReview"]["absNormalizationCaveat"]:
        raise ValueError("missing abs-normalization caveat")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "referenceFeasibilityPacketCreated",
        "sqrtEntryReviewed",
        "nonnegativityGuardReviewed",
        "statementShapeReviewed",
        "absNormalizationCaveatRecorded",
        "courseSdkReferenceValueRecorded",
        "blockedClaimsRecorded",
        "candidateValidityBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "sqrtCandidatePacketSelected",
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
    for blocked in ["not a checked witness", "not a candidate validity claim", "no Lean typecheck"]:
        if blocked not in review["blockedClaims"]:
            raise ValueError(f"missing blocked claim: {blocked}")
    assert_claim_flags_bounded(review["claimFlags"], TRUE_CLAIM_FLAGS)
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_sqrt_boundary_reference_feasibility_packet",
        semantic_strength="private_reference_feasibility_packet_records_sqrt_guard_abs_caveat_no_validity_no_proof_no_public_promotion",
        source=f"python/results/atlas_a7_private_sqrt_boundary_reference_feasibility_packet/atlas_a7_private_sqrt_boundary_reference_feasibility_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a7_private_sqrt_boundary_reference_feasibility_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A8 as a private sqrt boundary candidate value selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "reviewedEntryId": payload["summary"]["reviewedEntryId"],
            "statementShapeStatus": payload["sqrtReferenceReview"]["statementShapeReview"]["statementShapeStatus"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["sqrtReferenceReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("reviewed entry", payload["summary"]["reviewedEntryId"]),
        ("guard", payload["summary"]["guardHint"]),
        ("statement shape", payload["summary"]["statementShapeHint"]),
        ("statement shape status", review["statementShapeReview"]["statementShapeStatus"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    caveat_lines = [f"- {item}" for item in review["reviewCaveats"]]
    reference_lines = [f"- {key}: {value}" for key, value in review["referenceUsefulness"].items()]
    blocked_lines = [f"- {item}" for item in review["blockedClaims"]]
    return render_markdown_report(
        title="ATLAS-A7 Private Sqrt Boundary Reference-Feasibility Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Reference Usefulness", reference_lines),
            ("Review Caveats", caveat_lines),
            ("Blocked Claims", blocked_lines),
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
    result_path = out_dir / f"atlas_a7_private_sqrt_boundary_reference_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a7_private_sqrt_boundary_reference_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a7_private_sqrt_boundary_reference_feasibility_packet.json"
    feed_path = command_feed_dir / f"atlas_a7_private_sqrt_boundary_reference_feasibility_packet_feed_{STAMP}.json"
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/atlas_a7_private_sqrt_boundary_reference_feasibility_packet",
    )
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
    print("ATLAS_A7_PRIVATE_SQRT_BOUNDARY_REFERENCE_FEASIBILITY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
