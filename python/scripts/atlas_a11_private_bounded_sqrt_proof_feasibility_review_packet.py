#!/usr/bin/env python3
"""ATLAS-A11 private bounded sqrt proof-feasibility review packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a10_private_sqrt_candidate_proof_feasibility_selector as a10  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_bounded_sqrt_proof_feasibility_review_packet.v0"
STATUS = "ATLAS_A11_PRIVATE_BOUNDED_SQRT_PROOF_FEASIBILITY_REVIEW_PACKET_PASS"
ARTIFACT_ID = "atlas-a11-private-bounded-sqrt-proof-feasibility-review-packet"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
RECOMMENDATION_ID = "proceed_to_private_proof_attempt_gate_selector"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A12 private sqrt proof-attempt gate selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a10_consumed",
    "proof_feasibility_review_packet_created",
    "candidate_packet_reviewed",
    "proof_shape_risks_recorded",
    "guard_direction_risks_recorded",
    "blocker_conditions_recorded",
    "private_attempt_gate_recommended",
    "candidate_validity_blocked",
    "proof_attempt_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a10_consumed": True,
    "proof_feasibility_review_packet_created": True,
    "candidate_packet_reviewed": True,
    "proof_shape_risks_recorded": True,
    "guard_direction_risks_recorded": True,
    "blocker_conditions_recorded": True,
    "private_attempt_gate_recommended": True,
    "candidate_validity_blocked": True,
    "proof_attempt_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "proof_attempt_gate_created": False,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "theorem_lookup_performed": False,
    "exact_theorem_names_claimed": False,
    "runtime_lowering_changed": False,
    "runtime_sqrt_replacement_claim": False,
    "atlas_v0_doc_pause_selected": False,
    "sqrt_candidate_parked": False,
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
    "ATLAS-A11 is a private proof-feasibility review packet; it records risks and a next gate recommendation but does not start proof work or select the candidate for proof.",
    "ATLAS-A11 names likely theorem-shape needs as review hints only; it does not perform theorem lookup, claim exact theorem names, run Lean, edit MachLib, or claim the candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A11 does not change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_review(source: dict[str, Any]) -> dict[str, Any]:
    summary = source["summary"]
    return {
        "candidateId": summary["candidateId"],
        "reviewStatus": "bounded_feasibility_review_only_not_proof_not_validity",
        "proofFacingRoute": [
            {
                "stepId": "abs_normalization",
                "shape": summary["absNormalizedIntermediate"],
                "purpose": "establish the absolute-value form before using the nonnegative guard",
                "status": "review_hint_not_checked",
            },
            {
                "stepId": "guard_reduction",
                "shape": summary["guardedExplanatoryForm"],
                "purpose": "use 0 <= x to reduce abs(x) to x",
                "status": "review_hint_not_checked",
            },
            {
                "stepId": "eml_boundary_alignment",
                "shape": summary["emlGuardedBoundaryHint"],
                "purpose": "align the mathematical equality with the EML-shaped boundary statement",
                "status": "review_hint_not_checked",
            },
        ],
        "likelyTheoremShapeNeeds": [
            "sqrt-square to absolute-value relationship over Real",
            "absolute-value reduction under nonnegative guard",
            "multiplication/square normalization compatible with the chosen EML expression form",
            "EML boundary rewriting support for the candidate expression shape",
        ],
        "guardDirectionRisks": [
            "Using `0 <= x` is necessary for reducing abs(x) to x; dropping it would change the statement to an absolute-value result.",
            "The guarded explanatory form must not be read backward as a general sqrt-square simplification for negative inputs.",
            "The EML boundary hint may need exact expression ordering before any Lean-facing packet.",
        ],
        "blockerConditions": [
            {
                "blockerId": "missing_abs_normalization_route",
                "blocks": "proof_attempt_gate",
                "condition": "If the proof route cannot express sqrt (x * x) through an abs-normalized intermediate, do not proceed.",
            },
            {
                "blockerId": "unclear_eml_expression_alignment",
                "blocks": "proof_attempt_gate",
                "condition": "If the EML expression shape does not align with existing boundary witness patterns, pause rather than edit MachLib.",
            },
            {
                "blockerId": "guard_direction_unclear",
                "blocks": "public_or_sdk_copy",
                "condition": "If the nonnegative guard cannot be explained in one sentence, keep the candidate private.",
            },
        ],
        "recommendation": {
            "recommendationId": RECOMMENDATION_ID,
            "recommendationStatus": "recommend_next_gate_not_proof",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "rationale": [
                "The proof-shape risks are explicit and bounded.",
                "The next useful artifact is a gate that decides whether a scoped proof attempt is allowed, not the proof attempt itself.",
                "A pause path remains available if the Atlas v0 reference document becomes higher leverage.",
            ],
        },
        "blockedClaims": [
            "not a checked witness",
            "not a candidate validity claim",
            "not selected for proof",
            "no proof attempt started",
            "no theorem lookup performed",
            "no exact theorem names claimed",
            "no MachLib edit",
            "no Lean typecheck",
            "no runtime sqrt replacement",
            "no public copy approval",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a10.build_payload(atlas_gate_path)
    a10.validate_payload(source)
    review = build_review(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "candidateId": review["candidateId"],
        "reviewStatus": review["reviewStatus"],
        "proofFeasibilityReviewPacketCreated": True,
        "candidatePacketReviewed": True,
        "proofShapeRisksRecorded": True,
        "guardDirectionRisksRecorded": True,
        "blockerConditionsRecorded": True,
        "recommendationId": review["recommendation"]["recommendationId"],
        "recommendationStatus": review["recommendation"]["recommendationStatus"],
        "privateAttemptGateRecommended": True,
        "proofAttemptGateCreated": False,
        "candidateValidityBlocked": True,
        "proofAttemptBlocked": True,
        "candidateValidityClaim": False,
        "candidateSelectedForProof": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "theoremLookupPerformed": False,
        "exactTheoremNamesClaimed": False,
        "runtimeLoweringChanged": False,
        "runtimeSqrtReplacementClaim": False,
        "atlasV0DocPauseSelected": False,
        "sqrtCandidateParked": False,
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
        artifact_type="private_bounded_sqrt_proof_feasibility_review_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceCandidatePacket": source["candidatePacket"],
            "proofFeasibilityReview": review,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    review = payload["proofFeasibilityReview"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(review["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a10-private-sqrt-candidate-proof-feasibility-selector":
        raise ValueError("ATLAS-A11 must consume ATLAS-A10")
    if summary["sourceSelectedOptionId"] != "create_bounded_sqrt_proof_feasibility_review_packet":
        raise ValueError("A11 must consume A10's bounded review selection")
    if summary["candidateId"] != CANDIDATE_ID or review["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if len(review["proofFacingRoute"]) != 3:
        raise ValueError("expected three proof-facing route hints")
    if not any("absolute-value" in item for item in review["likelyTheoremShapeNeeds"]):
        raise ValueError("missing abs theorem-shape need")
    if not any("0 <= x" in item for item in review["guardDirectionRisks"]):
        raise ValueError("missing nonnegative guard risk")
    if len(review["blockerConditions"]) != 3:
        raise ValueError("expected three blocker conditions")
    if summary["recommendationId"] != RECOMMENDATION_ID:
        raise ValueError("recommendation drift")
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
        "proofFeasibilityReviewPacketCreated",
        "candidatePacketReviewed",
        "proofShapeRisksRecorded",
        "guardDirectionRisksRecorded",
        "blockerConditionsRecorded",
        "privateAttemptGateRecommended",
        "candidateValidityBlocked",
        "proofAttemptBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "proofAttemptGateCreated",
        "candidateValidityClaim",
        "candidateSelectedForProof",
        "candidateProved",
        "proofAttemptStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "theoremLookupPerformed",
        "exactTheoremNamesClaimed",
        "runtimeLoweringChanged",
        "runtimeSqrtReplacementClaim",
        "atlasV0DocPauseSelected",
        "sqrtCandidateParked",
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
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_bounded_sqrt_proof_feasibility_review_packet",
        semantic_strength="private_review_records_sqrt_proof_shape_risks_no_proof_no_validity_no_theorem_lookup",
        source=f"python/results/atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet/atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A12 as a private sqrt proof-attempt gate selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "recommendationId": payload["summary"]["recommendationId"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "theoremLookupPerformed": payload["summary"]["theoremLookupPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["proofFeasibilityReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("review status", payload["summary"]["reviewStatus"]),
        ("recommendation", payload["summary"]["recommendationId"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("theorem lookup performed", payload["summary"]["theoremLookupPerformed"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    route_lines = ["| Step | Shape | Status |", "|---|---|---|"]
    for item in review["proofFacingRoute"]:
        shape = item["shape"].replace("|", "\\|")
        route_lines.append(f"| `{item['stepId']}` | `{shape}` | `{item['status']}` |")
    theorem_lines = [f"- {item}" for item in review["likelyTheoremShapeNeeds"]]
    risk_lines = [f"- {item}" for item in review["guardDirectionRisks"]]
    blocker_lines = [f"- `{item['blockerId']}`: {item['condition']}" for item in review["blockerConditions"]]
    return render_markdown_report(
        title="ATLAS-A11 Private Bounded Sqrt Proof-Feasibility Review Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Proof-Facing Route", route_lines),
            ("Likely Theorem-Shape Needs", theorem_lines),
            ("Guard Direction Risks", risk_lines),
            ("Blocker Conditions", blocker_lines),
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
    result_path = out_dir / f"atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet.json"
    feed_path = command_feed_dir / f"atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet",
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
    print("ATLAS_A11_PRIVATE_BOUNDED_SQRT_PROOF_FEASIBILITY_REVIEW_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
