#!/usr/bin/env python3
"""ATLAS-A6 private reference-value candidate selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a5_private_reciprocal_boundary_feasibility_packet as a5  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_reference_value_candidate_selector.v0"
STATUS = "ATLAS_A6_PRIVATE_REFERENCE_VALUE_CANDIDATE_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a6-private-reference-value-candidate-selector"
RECIPROCAL_ENTRY_ID = "reciprocal_positive_boundary_candidate"
SQRT_ENTRY_ID = "sqrt_square_nonnegative_roundtrip_candidate"
SELECTED_OPTION_ID = "defer_reciprocal_and_review_sqrt_reference_value"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A7 private sqrt boundary reference-feasibility packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a5_consumed",
    "reference_value_selector_created",
    "practical_reference_criteria_recorded",
    "reciprocal_value_reviewed",
    "sqrt_value_reviewed",
    "reciprocal_promotion_deferred",
    "sqrt_reference_review_recommended",
    "candidate_validity_blocked",
    "public_promotion_blocked",
    "next_private_packet_recommended",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a5_consumed": True,
    "reference_value_selector_created": True,
    "practical_reference_criteria_recorded": True,
    "reciprocal_value_reviewed": True,
    "sqrt_value_reviewed": True,
    "reciprocal_promotion_deferred": True,
    "sqrt_reference_review_recommended": True,
    "candidate_validity_blocked": True,
    "public_promotion_blocked": True,
    "next_private_packet_recommended": True,
    "d109_hold_respected": True,
    "reciprocal_candidate_packet_selected": False,
    "sqrt_candidate_packet_selected": False,
    "feasibility_packet_created": False,
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
    "ATLAS-A6 is a private reference-value selector; it does not create a candidate packet, proof branch, checked witness, or validity claim.",
    "ATLAS-A6 defers reciprocal promotion because reciprocal is feasible but lower-reference-value than sqrt under the current Atlas gap criteria; it does not reject or disprove reciprocal.",
    "ATLAS-A6 recommends reviewing the sqrt entry's reference value next; it does not claim sqrt is valid, provable, checked, selected for proof, or public-ready.",
    "ATLAS-A6 does not edit MachLib, run Lean, start proof work, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]

CRITERIA = [
    "shape_diversity",
    "guard_clarity",
    "future_leverage",
    "proof_effort_value_ratio",
    "public_witness_potential",
]


def criterion_scores(entry_id: str) -> dict[str, Any]:
    if entry_id == RECIPROCAL_ENTRY_ID:
        scores = {
            "shape_diversity": 2,
            "guard_clarity": 5,
            "future_leverage": 3,
            "proof_effort_value_ratio": 4,
            "public_witness_potential": 3,
        }
        return {
            "entryId": entry_id,
            "candidateLabel": "guarded positive reciprocal boundary",
            "familyHint": "reciprocal_boundary",
            "guardHint": "0 < x",
            "statementShapeHint": "0 < x -> eml (x * (1 / x)) 1 = 1",
            "scores": scores,
            "totalScore": sum(scores.values()),
            "referenceValueStatus": "feasible_but_deferred_lower_shape_diversity",
            "rationale": [
                "Guard is clean and proof effort may be reasonable.",
                "Reference value is limited because the current Atlas already has several positive-domain/singularity-adjacent log-family rows.",
                "Useful as a later algebraic guard example, but not the strongest immediate gap filler.",
            ],
        }
    if entry_id == SQRT_ENTRY_ID:
        scores = {
            "shape_diversity": 5,
            "guard_clarity": 4,
            "future_leverage": 5,
            "proof_effort_value_ratio": 3,
            "public_witness_potential": 4,
        }
        return {
            "entryId": entry_id,
            "candidateLabel": "guarded sqrt-square nonnegative roundtrip",
            "familyHint": "sqrt_boundary",
            "guardHint": "0 <= x",
            "statementShapeHint": "0 <= x -> eml (sqrt (x * x)) x = x",
            "scores": scores,
            "totalScore": sum(scores.values()),
            "referenceValueStatus": "recommended_for_reference_feasibility_review",
            "rationale": [
                "Adds a non-log, non-subtraction composed-function shape.",
                "Nonnegativity guard is useful for course and SDK guard-note explanations.",
                "Has a clear caveat around abs-normalized theorem shape, which is exactly the kind of blocker a feasibility packet should expose.",
            ],
        }
    raise ValueError(f"unknown entry id: {entry_id}")


def build_options() -> list[dict[str, Any]]:
    return [
        {
            "optionId": "promote_reciprocal_to_candidate_packet",
            "selectionStatus": "deferred_lower_reference_value",
            "entryId": RECIPROCAL_ENTRY_ID,
            "nextArtifact": "Future reciprocal boundary candidate packet",
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "entryId": SQRT_ENTRY_ID,
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_gap_candidates_pending_atlas_v0_doc",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "entryId": None,
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a5.build_payload(atlas_gate_path)
    a5.validate_payload(source)
    reciprocal = criterion_scores(RECIPROCAL_ENTRY_ID)
    sqrt_entry = criterion_scores(SQRT_ENTRY_ID)
    options = build_options()
    selected = next(item for item in options if item["selectionStatus"] == "selected_next")
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedEntryId": source["summary"]["reviewedEntryId"],
        "sourceFeasibleForCandidateSelectorRecorded": source["summary"]["feasibleForCandidateSelectorRecorded"],
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "referenceValueSelectorCreated": True,
        "practicalReferenceCriteriaRecorded": True,
        "criteriaCount": len(CRITERIA),
        "reciprocalValueReviewed": True,
        "sqrtValueReviewed": True,
        "reciprocalTotalScore": reciprocal["totalScore"],
        "sqrtTotalScore": sqrt_entry["totalScore"],
        "selectedOptionId": selected["optionId"],
        "selectedEntryId": selected["entryId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "reciprocalPromotionDeferred": True,
        "sqrtReferenceReviewRecommended": True,
        "candidateValidityBlocked": True,
        "reciprocalCandidatePacketSelected": False,
        "sqrtCandidatePacketSelected": False,
        "feasibilityPacketCreated": False,
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
        artifact_type="private_reference_value_candidate_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "referenceCriteria": list(CRITERIA),
            "referenceValueScores": [reciprocal, sqrt_entry],
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
    if payload["sourceArtifact"] != "atlas-a5-private-reciprocal-boundary-feasibility-packet":
        raise ValueError("ATLAS-A6 must consume ATLAS-A5")
    if summary["sourceReviewedEntryId"] != RECIPROCAL_ENTRY_ID:
        raise ValueError("A6 must consume the reciprocal feasibility review")
    if summary["criteriaCount"] != 5 or payload["referenceCriteria"] != CRITERIA:
        raise ValueError("reference criteria drift")
    if summary["reciprocalTotalScore"] != 17:
        raise ValueError("reciprocal score drift")
    if summary["sqrtTotalScore"] != 21:
        raise ValueError("sqrt score drift")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedEntryId"] != SQRT_ENTRY_ID:
        raise ValueError("sqrt should be selected for reference-feasibility review")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected selected next artifact")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option must be selected_next")
    for key in [
        "referenceValueSelectorCreated",
        "practicalReferenceCriteriaRecorded",
        "reciprocalValueReviewed",
        "sqrtValueReviewed",
        "reciprocalPromotionDeferred",
        "sqrtReferenceReviewRecommended",
        "candidateValidityBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "reciprocalCandidatePacketSelected",
        "sqrtCandidatePacketSelected",
        "feasibilityPacketCreated",
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
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetLowerBoundReached"] is not False or summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("target gap drift")
    for item in payload["referenceValueScores"]:
        if set(item["scores"]) != set(CRITERIA):
            raise ValueError("criterion score keys drift")
    for item in payload["options"]:
        assert_claim_flags_bounded(item["claimFlags"], TRUE_CLAIM_FLAGS)
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_reference_value_candidate_selector",
        semantic_strength="private_selector_scores_reference_value_recommends_sqrt_feasibility_review_no_candidate_no_proof_no_public_promotion",
        source=f"python/results/atlas_a6_private_reference_value_candidate_selector/atlas_a6_private_reference_value_candidate_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a6_private_reference_value_candidate_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A7 as a private sqrt boundary reference-feasibility packet.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "selectedEntryId": payload["summary"]["selectedEntryId"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected entry", payload["summary"]["selectedEntryId"]),
        ("reciprocal score", payload["summary"]["reciprocalTotalScore"]),
        ("sqrt score", payload["summary"]["sqrtTotalScore"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    score_lines = ["| Entry | Shape | Guard | Leverage | Total | Status |", "|---|---:|---:|---:|---:|---|"]
    for item in payload["referenceValueScores"]:
        score_lines.append(
            f"| `{item['entryId']}` | {item['scores']['shape_diversity']} | {item['scores']['guard_clarity']} | "
            f"{item['scores']['future_leverage']} | {item['totalScore']} | `{item['referenceValueStatus']}` |"
        )
    return render_markdown_report(
        title="ATLAS-A6 Private Reference-Value Candidate Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[("Reference-Value Scores", score_lines)],
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
    result_path = out_dir / f"atlas_a6_private_reference_value_candidate_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a6_private_reference_value_candidate_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a6_private_reference_value_candidate_selector.json"
    feed_path = command_feed_dir / f"atlas_a6_private_reference_value_candidate_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/atlas_a6_private_reference_value_candidate_selector")
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
    print("ATLAS_A6_PRIVATE_REFERENCE_VALUE_CANDIDATE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
