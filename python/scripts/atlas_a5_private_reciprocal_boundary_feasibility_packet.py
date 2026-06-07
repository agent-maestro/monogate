#!/usr/bin/env python3
"""ATLAS-A5 private reciprocal boundary feasibility packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a4_private_two_gap_feasibility_selector as a4  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_reciprocal_boundary_feasibility_packet.v0"
STATUS = "ATLAS_A5_PRIVATE_RECIPROCAL_BOUNDARY_FEASIBILITY_PACKET_PASS"
ARTIFACT_ID = "atlas-a5-private-reciprocal-boundary-feasibility-packet"
SOURCE_ENTRY_ID = "reciprocal_positive_boundary_candidate"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A6 private reciprocal boundary candidate selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a4_consumed",
    "feasibility_packet_created",
    "reciprocal_entry_reviewed",
    "guard_reviewed",
    "statement_shape_reviewed",
    "caveats_recorded",
    "blocked_claims_recorded",
    "feasible_for_candidate_selector_recorded",
    "candidate_validity_blocked",
    "public_promotion_blocked",
    "next_private_selector_recommended",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a4_consumed": True,
    "feasibility_packet_created": True,
    "reciprocal_entry_reviewed": True,
    "guard_reviewed": True,
    "statement_shape_reviewed": True,
    "caveats_recorded": True,
    "blocked_claims_recorded": True,
    "feasible_for_candidate_selector_recorded": True,
    "candidate_validity_blocked": True,
    "public_promotion_blocked": True,
    "next_private_selector_recommended": True,
    "d109_hold_respected": True,
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
    "ATLAS-A5 is a private feasibility packet; it does not prove, typecheck, implement, or validate the reciprocal boundary entry.",
    "ATLAS-A5 records that the reciprocal entry is feasible enough for a later private candidate selector, not that it is true, selected for proof, or a checked witness.",
    "ATLAS-A5 does not edit MachLib, run Lean, start proof work, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def selected_entry(source: dict[str, Any]) -> dict[str, Any]:
    return next(entry for entry in source["shortlistEntries"] if entry["entryId"] == SOURCE_ENTRY_ID)


def build_feasibility_review(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "entryId": entry["entryId"],
        "candidateLabel": entry["candidateLabel"],
        "familyHint": entry["familyHint"],
        "emlShapeHint": entry["emlShapeHint"],
        "guardHint": entry["guardHint"],
        "runtimeControlHint": entry["runtimeControlHint"],
        "feasibilityStatus": "feasible_for_later_private_candidate_selector_not_validity_claim",
        "guardReview": {
            "requiredGuard": "0 < x",
            "guardPurpose": "ensures the reciprocal denominator is nonzero and keeps the review surface positive-domain bounded",
            "knownCaveat": "future Lean spelling may use x⁻¹ or / notation rather than 1 / x",
        },
        "statementShapeReview": {
            "candidateStatementHint": "0 < x -> eml (x * (1 / x)) 1 = 1",
            "statementShapeStatus": "plausible_for_candidate_selector_not_checked",
            "shapeCaveats": [
                "May need exact EML boundary spelling aligned with existing MachLib conventions.",
                "May need reciprocal notation normalized before any Lean-facing packet.",
                "Must not imply runtime replacement of division or reciprocal.",
            ],
        },
        "reviewCaveats": [
            "0 < x is stronger than x != 0; this is acceptable for a bounded positive-domain candidate but should be explicit.",
            "The statement is algebraically familiar, but no theorem lookup, Lean typecheck, or MachLib proof attempt was performed.",
            "Feasibility here only means the entry is small and bounded enough for a later private selector.",
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
    source = a4.build_payload(atlas_gate_path)
    a4.validate_payload(source)
    entry = selected_entry(source)
    review = build_feasibility_review(entry)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedEntryId": source["summary"]["selectedEntryId"],
        "sourceParkedEntryId": source["summary"]["parkedEntryId"],
        "reviewedEntryId": review["entryId"],
        "familyHint": review["familyHint"],
        "guardHint": review["guardHint"],
        "statementShapeHint": review["emlShapeHint"],
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "feasibilityPacketCreated": True,
        "reciprocalEntryReviewed": True,
        "guardReviewed": True,
        "statementShapeReviewed": True,
        "caveatsRecorded": True,
        "blockedClaimsRecorded": True,
        "feasibleForCandidateSelectorRecorded": True,
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
        artifact_type="private_reciprocal_boundary_feasibility_packet",
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
            "sourceParkedDecision": source["parkedDecision"],
            "feasibilityReview": review,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    review = payload["feasibilityReview"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a4-private-two-gap-feasibility-selector":
        raise ValueError("ATLAS-A5 must consume ATLAS-A4")
    if summary["sourceSelectedEntryId"] != SOURCE_ENTRY_ID or summary["reviewedEntryId"] != SOURCE_ENTRY_ID:
        raise ValueError("A5 must review the reciprocal entry")
    if summary["sourceParkedEntryId"] != "sqrt_square_nonnegative_roundtrip_candidate":
        raise ValueError("sqrt entry should remain parked")
    if review["feasibilityStatus"] != "feasible_for_later_private_candidate_selector_not_validity_claim":
        raise ValueError("unexpected feasibility status")
    if review["guardReview"]["requiredGuard"] != "0 < x":
        raise ValueError("guard drift")
    if review["statementShapeReview"]["candidateStatementHint"] != "0 < x -> eml (x * (1 / x)) 1 = 1":
        raise ValueError("statement shape drift")
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
        "reciprocalEntryReviewed",
        "guardReviewed",
        "statementShapeReviewed",
        "caveatsRecorded",
        "blockedClaimsRecorded",
        "feasibleForCandidateSelectorRecorded",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
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
        artifact_type="private_reciprocal_boundary_feasibility_packet",
        semantic_strength="private_feasibility_packet_records_reciprocal_review_no_validity_no_proof_no_public_promotion",
        source=f"python/results/atlas_a5_private_reciprocal_boundary_feasibility_packet/atlas_a5_private_reciprocal_boundary_feasibility_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a5_private_reciprocal_boundary_feasibility_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A6 as a private reciprocal boundary candidate selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "reviewedEntryId": payload["summary"]["reviewedEntryId"],
            "feasibilityStatus": payload["feasibilityReview"]["feasibilityStatus"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["feasibilityReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("reviewed entry", payload["summary"]["reviewedEntryId"]),
        ("guard", payload["summary"]["guardHint"]),
        ("statement shape", payload["summary"]["statementShapeHint"]),
        ("feasibility status", review["feasibilityStatus"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    caveat_lines = [f"- {item}" for item in review["reviewCaveats"]]
    blocked_lines = [f"- {item}" for item in review["blockedClaims"]]
    return render_markdown_report(
        title="ATLAS-A5 Private Reciprocal Boundary Feasibility Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
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
    result_path = out_dir / f"atlas_a5_private_reciprocal_boundary_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a5_private_reciprocal_boundary_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a5_private_reciprocal_boundary_feasibility_packet.json"
    feed_path = command_feed_dir / f"atlas_a5_private_reciprocal_boundary_feasibility_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a5_private_reciprocal_boundary_feasibility_packet",
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
    print("ATLAS_A5_PRIVATE_RECIPROCAL_BOUNDARY_FEASIBILITY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
