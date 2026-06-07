#!/usr/bin/env python3
"""ATLAS-A12 private sqrt proof-attempt gate selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a11_private_bounded_sqrt_proof_feasibility_review_packet as a11  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_sqrt_proof_attempt_gate_selector.v0"
STATUS = "ATLAS_A12_PRIVATE_SQRT_PROOF_ATTEMPT_GATE_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a12-private-sqrt-proof-attempt-gate-selector"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
SELECTED_OPTION_ID = "create_scoped_private_sqrt_proof_attempt_gate_packet"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A13 private scoped sqrt proof-attempt gate packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a11_consumed",
    "proof_attempt_gate_selector_created",
    "bounded_review_consumed",
    "blockers_reviewed",
    "scoped_gate_packet_recommended",
    "candidate_validity_blocked",
    "actual_proof_attempt_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a11_consumed": True,
    "proof_attempt_gate_selector_created": True,
    "bounded_review_consumed": True,
    "blockers_reviewed": True,
    "scoped_gate_packet_recommended": True,
    "candidate_validity_blocked": True,
    "actual_proof_attempt_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "proof_attempt_gate_packet_created": False,
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
    "ATLAS-A12 is a private selector; it recommends a future scoped proof-attempt gate packet but does not create that gate packet, start proof work, or select the candidate for proof.",
    "ATLAS-A12 consumes A11's review risks and blockers only; it does not perform theorem lookup, claim exact theorem names, run Lean, edit MachLib, or claim the candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A12 does not change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    review = source["proofFeasibilityReview"]
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "decision": "create_gate_packet_without_starting_attempt",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "scopeConstraints": [
                "gate packet may define allowed files and exact timeout budget",
                "gate packet may require starting from abs-normalized route",
                "gate packet may require aborting on expression-alignment drift",
                "gate packet must still not edit MachLib or run Lean",
            ],
            "sourceReviewSignals": {
                "recommendationId": review["recommendation"]["recommendationId"],
                "blockerCount": len(review["blockerConditions"]),
                "routeStepCount": len(review["proofFacingRoute"]),
            },
            "rationale": [
                "A11 recorded bounded proof-shape risks and blocker conditions.",
                "A gate packet can define whether a later proof attempt is allowed without starting it.",
                "This keeps the Atlas lane staged rather than jumping directly into MachLib.",
            ],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_reference_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "decision": "pause_proof_gate_for_reference_document",
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "scopeConstraints": [],
            "sourceReviewSignals": None,
            "rationale": ["A11 is already useful as reference material without opening a proof gate."],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "park_sqrt_candidate_after_review",
            "selectionStatus": "not_selected",
            "decision": "park_candidate_without_rejection",
            "nextArtifact": "Park sqrt candidate after A11 review",
            "scopeConstraints": [],
            "sourceReviewSignals": None,
            "rationale": ["Parking remains valid if proof-gate work is not worth the review cost."],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a11.build_payload(atlas_gate_path)
    a11.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    review = source["proofFeasibilityReview"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceRecommendationId": source["summary"]["recommendationId"],
        "candidateId": source["summary"]["candidateId"],
        "proofAttemptGateSelectorCreated": True,
        "boundedReviewConsumed": True,
        "blockersReviewed": True,
        "proofFacingRouteStepCount": len(review["proofFacingRoute"]),
        "blockerConditionCount": len(review["blockerConditions"]),
        "selectedOptionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "scopedGatePacketRecommended": True,
        "proofAttemptGatePacketCreated": False,
        "candidateValidityBlocked": True,
        "actualProofAttemptBlocked": True,
        "machlibEditBlocked": True,
        "leanTypecheckBlocked": True,
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
        artifact_type="private_sqrt_proof_attempt_gate_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceProofFeasibilityReview": review,
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
    if payload["sourceArtifact"] != "atlas-a11-private-bounded-sqrt-proof-feasibility-review-packet":
        raise ValueError("ATLAS-A12 must consume ATLAS-A11")
    if summary["sourceRecommendationId"] != "proceed_to_private_proof_attempt_gate_selector":
        raise ValueError("A12 must consume A11's proceed-to-gate recommendation")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["proofFacingRouteStepCount"] != 3:
        raise ValueError("expected three route steps")
    if summary["blockerConditionCount"] != 3:
        raise ValueError("expected three blockers")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "create_gate_packet_without_starting_attempt":
        raise ValueError("unexpected selected decision")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option must be selected_next")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "proofAttemptGateSelectorCreated",
        "boundedReviewConsumed",
        "blockersReviewed",
        "scopedGatePacketRecommended",
        "candidateValidityBlocked",
        "actualProofAttemptBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "proofAttemptGatePacketCreated",
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
    for item in payload["options"]:
        assert_claim_flags_bounded(item["claimFlags"], TRUE_CLAIM_FLAGS)
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_sqrt_proof_attempt_gate_selector",
        semantic_strength="private_selector_recommends_scoped_sqrt_proof_attempt_gate_packet_no_attempt_no_validity",
        source=f"python/results/atlas_a12_private_sqrt_proof_attempt_gate_selector/atlas_a12_private_sqrt_proof_attempt_gate_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a12_private_sqrt_proof_attempt_gate_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A13 as a private scoped sqrt proof-attempt gate packet.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "selectedDecision": payload["summary"]["selectedDecision"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("gate packet created", payload["summary"]["proofAttemptGatePacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    option_lines = ["| Option | Status | Decision |", "|---|---|---|"]
    for item in payload["options"]:
        option_lines.append(f"| `{item['optionId']}` | `{item['selectionStatus']}` | `{item['decision']}` |")
    constraint_lines = [f"- {item}" for item in payload["selectedOption"]["scopeConstraints"]]
    return render_markdown_report(
        title="ATLAS-A12 Private Sqrt Proof-Attempt Gate Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[("Selected Gate Constraints", constraint_lines), ("Options", option_lines)],
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
    result_path = out_dir / f"atlas_a12_private_sqrt_proof_attempt_gate_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a12_private_sqrt_proof_attempt_gate_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a12_private_sqrt_proof_attempt_gate_selector.json"
    feed_path = command_feed_dir / f"atlas_a12_private_sqrt_proof_attempt_gate_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/atlas_a12_private_sqrt_proof_attempt_gate_selector")
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
    print("ATLAS_A12_PRIVATE_SQRT_PROOF_ATTEMPT_GATE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
