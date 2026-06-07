#!/usr/bin/env python3
"""ATLAS-A23 private Atlas gap strategy selector."""

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

from scripts import atlas_a22_private_sqrt_candidate_reframe_or_park_selector as a22  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_atlas_gap_strategy_selector.v0"
STATUS = "ATLAS_A23_PRIVATE_ATLAS_GAP_STRATEGY_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a23-private-atlas-gap-strategy-selector"
SOURCE_CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
SELECTED_OPTION_ID = "refresh_non_sqrt_non_reciprocal_gap_pool"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A24 private reference-value gap pool refresh"

TRUE_CLAIM_FLAGS = {
    "atlas_a22_consumed",
    "gap_strategy_selector_created",
    "sqrt_park_decision_reviewed",
    "reciprocal_defer_context_recorded",
    "strategy_criteria_recorded",
    "gap_pool_refresh_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a22_consumed": True,
    "gap_strategy_selector_created": True,
    "sqrt_park_decision_reviewed": True,
    "reciprocal_defer_context_recorded": True,
    "strategy_criteria_recorded": True,
    "gap_pool_refresh_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "new_candidate_pool_created": False,
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
    "ATLAS-A23 is a private strategy selector; it does not create a new candidate pool, candidate packet, proof branch, checked witness, or validity claim.",
    "ATLAS-A23 keeps the EML-shaped sqrt candidate parked and records reciprocal as deferred context; it does not reject, disprove, prove, or reopen either candidate.",
    "ATLAS-A23 recommends a future reference-value gap-pool refresh, not MachLib work, Lean work, theorem lookup, public copy, runtime lowering, SDK/compiler/course copy, product implementation, or broad EML advantage claims.",
]

STRATEGY_CRITERIA = [
    "shape_diversity_beyond_log_subtraction_sqrt_and_reciprocal",
    "clean_communicable_guard",
    "future_leverage_for_guard_notes_courses_or_private_sdk_notes",
    "reasonable_expected_proof_effort_relative_to_reference_value",
    "explicit_blocker_recording_before_any_candidate_packet",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "decision": "refresh_reference_value_gap_pool_before_more_candidate_packets",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "rationale": [
                "A22 parks the active EML-shaped sqrt path; continuing it would require a new precise statement.",
                "Earlier reciprocal review was feasible but lower reference value, so reopening it immediately would not improve Atlas shape diversity.",
                "The Atlas still needs two high-quality bounded artifacts to reach the lower target, and the next step should widen the candidate pool before choosing.",
            ],
            "constraints": [
                "exclude the blocked EML-shaped sqrt path unless a new precise statement is supplied",
                "treat pure sqrt/abs as preserved for later, not selected by A23",
                "treat reciprocal as deferred context, not rejected or disproved",
                "create no candidate packet in A23",
            ],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "reopen_pure_sqrt_abs_feasibility",
            "selectionStatus": "available_if_human_explicitly_wants_sqrt_path",
            "decision": "create_future_pure_sqrt_abs_feasibility_selector",
            "nextArtifact": "Future private pure sqrt/abs feasibility selector",
            "rationale": [
                "A22 preserves the pure sqrt/abs shape for later feasibility.",
                "This is not selected because A23's default objective is to reduce sqrt-path churn.",
            ],
            "constraints": ["must not reuse the blocked EML boundary statement"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "reopen_reciprocal_candidate_path",
            "selectionStatus": "available_if_human_prefers_simpler_algebraic_candidate",
            "decision": "return_to_deferred_reciprocal_candidate_selector",
            "nextArtifact": "Future private reciprocal boundary candidate selector",
            "rationale": [
                "Reciprocal remained feasible enough for later selector work.",
                "This is not selected because its reference value was previously lower than the sqrt diversity target and now both old gap candidates need a broader comparison set.",
            ],
            "constraints": ["must keep validity and runtime reciprocal replacement claims blocked"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_reference_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "decision": "pause_candidate_search_for_single_atlas_v0_doc",
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "rationale": [
                "A single Atlas v0 document remains useful, but the lower-bound target still has two open artifact slots.",
            ],
            "constraints": ["must not imply target lower bound has been reached"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a22.build_payload(atlas_gate_path, machlib_root)
    a22.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "sourceCandidateId": source["summary"]["candidateId"],
        "sourceSqrtCandidateParked": source["summary"]["currentEmlSqrtCandidateParked"],
        "sourcePureSqrtAbsPreserved": source["summary"]["pureSqrtAbsReframePreservedForLater"],
        "gapStrategySelectorCreated": True,
        "sqrtParkDecisionReviewed": True,
        "reciprocalDeferContextRecorded": True,
        "strategyCriteriaRecorded": True,
        "strategyCriteriaCount": len(STRATEGY_CRITERIA),
        "selectedOptionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "gapPoolRefreshRecommended": True,
        "newCandidatePoolCreated": False,
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
        artifact_type="private_atlas_gap_strategy_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "strategyCriteria": list(STRATEGY_CRITERIA),
            "options": options,
            "selectedOption": selected,
            "carriedContext": {
                "parkedSqrtCandidateId": source["summary"]["candidateId"],
                "preservedPureSqrtAbsCandidateId": source["summary"]["preservedFutureCandidateId"],
                "deferredReciprocalContext": "ATLAS-A6 deferred reciprocal promotion as feasible but lower reference value.",
            },
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    for option in payload["options"]:
        assert_claim_flags_bounded(option["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a22-private-sqrt-candidate-reframe-or-park-selector":
        raise ValueError("ATLAS-A23 must consume ATLAS-A22")
    if summary["sourceSelectedOptionId"] != "park_eml_sqrt_candidate_preserve_pure_sqrt_abs_reframe":
        raise ValueError("A23 must consume A22's park decision")
    if summary["sourceCandidateId"] != SOURCE_CANDIDATE_ID:
        raise ValueError("source candidate id drift")
    if summary["sourceSqrtCandidateParked"] is not True:
        raise ValueError("sqrt candidate should be parked by source")
    if summary["sourcePureSqrtAbsPreserved"] is not True:
        raise ValueError("pure sqrt/abs reframe should be preserved by source")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "refresh_reference_value_gap_pool_before_more_candidate_packets":
        raise ValueError("unexpected selected decision")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option must be selected_next")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["strategyCriteriaCount"] != len(STRATEGY_CRITERIA):
        raise ValueError("criteria count drift")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "gapStrategySelectorCreated",
        "sqrtParkDecisionReviewed",
        "reciprocalDeferContextRecorded",
        "strategyCriteriaRecorded",
        "gapPoolRefreshRecommended",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "newCandidatePoolCreated",
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
        artifact_type="private_atlas_gap_strategy_selector",
        semantic_strength="private_strategy_selector_recommends_gap_pool_refresh_no_candidate_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a23_private_atlas_gap_strategy_selector/atlas_a23_private_atlas_gap_strategy_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a23_private_atlas_gap_strategy_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A24 as a private reference-value gap pool refresh; create no proof or public claims from A23.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "sourceCandidateId": payload["summary"]["sourceCandidateId"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "selectedDecision": payload["summary"]["selectedDecision"],
            "gapPoolRefreshRecommended": payload["summary"]["gapPoolRefreshRecommended"],
            "newCandidatePoolCreated": payload["summary"]["newCandidatePoolCreated"],
            "newCandidatePacketCreated": payload["summary"]["newCandidatePacketCreated"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    selected = payload["selectedOption"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("source candidate id", payload["summary"]["sourceCandidateId"]),
        ("source sqrt candidate parked", payload["summary"]["sourceSqrtCandidateParked"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("new candidate pool created", payload["summary"]["newCandidatePoolCreated"]),
        ("new candidate packet created", payload["summary"]["newCandidatePacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    criteria_lines = [f"- `{item}`" for item in payload["strategyCriteria"]]
    rationale_lines = [f"- {item}" for item in selected["rationale"]]
    constraint_lines = [f"- {item}" for item in selected["constraints"]]
    option_lines = ["| Option | Status | Decision |", "|---|---|---|"]
    for option in payload["options"]:
        option_lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | `{option['decision']}` |"
        )
    return render_markdown_report(
        title="ATLAS-A23 Private Atlas Gap Strategy Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Strategy Criteria", criteria_lines),
            ("Selected Rationale", rationale_lines),
            ("Selected Constraints", constraint_lines),
            ("Options", option_lines),
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
    result_path = out_dir / f"atlas_a23_private_atlas_gap_strategy_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a23_private_atlas_gap_strategy_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a23_private_atlas_gap_strategy_selector.json"
    feed_path = command_feed_dir / f"atlas_a23_private_atlas_gap_strategy_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a23_private_atlas_gap_strategy_selector",
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
    print("ATLAS_A23_PRIVATE_ATLAS_GAP_STRATEGY_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
