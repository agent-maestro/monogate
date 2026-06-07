#!/usr/bin/env python3
"""ATLAS-A22 private sqrt candidate reframe-or-park selector."""

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

from scripts import atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact as a21  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_sqrt_candidate_reframe_or_park_selector.v0"
STATUS = "ATLAS_A22_PRIVATE_SQRT_CANDIDATE_REFRAME_OR_PARK_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a22-private-sqrt-candidate-reframe-or-park-selector"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
PURE_REFRAME_ID = "sqrt_square_abs_normalized_pure_boundary_candidate"
SOURCE_BLOCKER_ID = "eml_boundary_alignment_not_justified_by_current_eml_definition"
SELECTED_OPTION_ID = "park_eml_sqrt_candidate_preserve_pure_sqrt_abs_reframe"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A23 private Atlas gap strategy selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a21_consumed",
    "reframe_or_park_selector_created",
    "alignment_blocker_reviewed",
    "current_eml_sqrt_candidate_parked",
    "pure_sqrt_abs_reframe_preserved_for_later",
    "atlas_gap_strategy_selector_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a21_consumed": True,
    "reframe_or_park_selector_created": True,
    "alignment_blocker_reviewed": True,
    "current_eml_sqrt_candidate_parked": True,
    "pure_sqrt_abs_reframe_preserved_for_later": True,
    "atlas_gap_strategy_selector_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "sqrt_candidate_reframed_this_phase": False,
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
    "ATLAS-A22 is a private selector that parks the current EML-shaped sqrt candidate without rejecting or disproving the underlying pure sqrt/abs idea.",
    "ATLAS-A22 preserves a possible pure sqrt/abs reframe for later but does not create a new candidate packet, state theorem names, start proof work, edit MachLib, or run Lean.",
    "ATLAS-A22 does not claim the EML-shaped sqrt candidate, pure sqrt/abs reframe, or any related statement is true, valid, checked, Lean-ready, provable, public-ready, useful for runtime lowering, useful for SDK/compiler/course material, or evidence of broad EML advantage.",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    blocker = source["attemptReview"]["blocker"]
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "decision": "park_current_eml_boundary_candidate_without_rejection",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "rationale": [
                "A21 records a blocker for EML boundary alignment, not a disproof of the pure sqrt/abs identity shape.",
                "The current EML-shaped candidate should not remain on a proof path without a new precise EML statement.",
                "Parking prevents more proof-governance churn and returns the Atlas lane to gap strategy.",
            ],
            "sourceBlocker": {
                "blockerId": blocker["blockerId"],
                "status": blocker["status"],
            },
            "preservedFutureCandidate": {
                "candidateId": PURE_REFRAME_ID,
                "shape": "0 <= x -> sqrt (x * x) = x",
                "status": "preserved_for_later_feasibility_not_created_not_selected",
                "claim": "no_validity_or_provability_claim",
            },
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "reframe_as_pure_sqrt_abs_feasibility_now",
            "selectionStatus": "available_if_human_explicitly_wants_sqrt_path",
            "decision": "create_future_pure_sqrt_abs_feasibility_selector",
            "nextArtifact": "Future private pure sqrt/abs feasibility selector",
            "rationale": [
                "The pure sqrt/abs shape may still add Atlas diversity if it is evaluated as its own non-EML boundary candidate.",
                "This should happen only as a fresh feasibility selector, not as a continuation of the blocked EML-alignment path.",
            ],
            "sourceBlocker": {
                "blockerId": blocker["blockerId"],
                "status": blocker["status"],
            },
            "preservedFutureCandidate": {
                "candidateId": PURE_REFRAME_ID,
                "shape": "0 <= x -> sqrt (x * x) = x",
                "status": "available_for_future_feasibility_only",
                "claim": "no_validity_or_provability_claim",
            },
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "require_new_precise_eml_statement_before_any_attempt",
            "selectionStatus": "not_selected",
            "decision": "require_new_eml_statement_before_any_future_eml_sqrt_attempt",
            "nextArtifact": "Future private precise EML sqrt statement selector",
            "rationale": [
                "This is valid if the Atlas still needs an EML-shaped sqrt entry.",
                "It is not selected because the immediate safer move is to park the misaligned candidate and resume gap strategy.",
            ],
            "sourceBlocker": {
                "blockerId": blocker["blockerId"],
                "status": blocker["status"],
            },
            "preservedFutureCandidate": None,
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a21.build_payload(atlas_gate_path, machlib_root)
    a21.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceBlockerId": source["summary"]["blockerId"],
        "candidateId": source["summary"]["candidateId"],
        "reframeOrParkSelectorCreated": True,
        "alignmentBlockerReviewed": True,
        "selectedOptionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "currentEmlSqrtCandidateParked": True,
        "pureSqrtAbsReframePreservedForLater": True,
        "preservedFutureCandidateId": PURE_REFRAME_ID,
        "sqrtCandidateReframedThisPhase": False,
        "newCandidatePacketCreated": False,
        "candidateRejected": False,
        "candidateDisproved": False,
        "candidateValidityBlocked": True,
        "candidateSelectedForProof": False,
        "candidateValidityClaim": False,
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
        artifact_type="private_sqrt_candidate_reframe_or_park_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceBlocker": source["attemptReview"]["blocker"],
            "options": options,
            "selectedOption": selected,
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
    if payload["sourceArtifact"] != "atlas-a21-private-corrected-scope-bounded-sqrt-attempt-artifact":
        raise ValueError("ATLAS-A22 must consume ATLAS-A21")
    if summary["sourceStatus"] != "ATLAS_A21_PRIVATE_CORRECTED_SCOPE_BOUNDED_SQRT_ATTEMPT_ARTIFACT_BLOCKED":
        raise ValueError("A22 should consume the blocked A21 artifact")
    if summary["sourceBlockerId"] != SOURCE_BLOCKER_ID:
        raise ValueError("source blocker id drift")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "park_current_eml_boundary_candidate_without_rejection":
        raise ValueError("unexpected selected decision")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option must be selected_next")
    if payload["selectedOption"]["preservedFutureCandidate"]["candidateId"] != PURE_REFRAME_ID:
        raise ValueError("future pure reframe id drift")
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
        "reframeOrParkSelectorCreated",
        "alignmentBlockerReviewed",
        "currentEmlSqrtCandidateParked",
        "pureSqrtAbsReframePreservedForLater",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "sqrtCandidateReframedThisPhase",
        "newCandidatePacketCreated",
        "candidateRejected",
        "candidateDisproved",
        "candidateSelectedForProof",
        "candidateValidityClaim",
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
        artifact_type="private_sqrt_candidate_reframe_or_park_selector",
        semantic_strength="private_selector_parks_eml_sqrt_candidate_preserves_pure_reframe_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a22_private_sqrt_candidate_reframe_or_park_selector/atlas_a22_private_sqrt_candidate_reframe_or_park_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a22_private_sqrt_candidate_reframe_or_park_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A23 as a private Atlas gap strategy selector; do not continue the blocked EML sqrt proof path without a new precise statement.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "sourceBlockerId": payload["summary"]["sourceBlockerId"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "currentEmlSqrtCandidateParked": payload["summary"]["currentEmlSqrtCandidateParked"],
            "pureSqrtAbsReframePreservedForLater": payload["summary"]["pureSqrtAbsReframePreservedForLater"],
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
        ("candidate id", payload["summary"]["candidateId"]),
        ("source blocker", payload["summary"]["sourceBlockerId"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("EML sqrt candidate parked", payload["summary"]["currentEmlSqrtCandidateParked"]),
        ("pure sqrt/abs reframe preserved", payload["summary"]["pureSqrtAbsReframePreservedForLater"]),
        ("new candidate packet created", payload["summary"]["newCandidatePacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    rationale_lines = [f"- {item}" for item in selected["rationale"]]
    preserved = selected["preservedFutureCandidate"]
    preserved_lines = [
        f"- candidate id: `{preserved['candidateId']}`",
        f"- shape: `{preserved['shape']}`",
        f"- status: `{preserved['status']}`",
        f"- claim: `{preserved['claim']}`",
    ]
    option_lines = ["| Option | Status | Decision |", "|---|---|---|"]
    for option in payload["options"]:
        option_lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | `{option['decision']}` |"
        )
    return render_markdown_report(
        title="ATLAS-A22 Private Sqrt Candidate Reframe-Or-Park Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Selected Rationale", rationale_lines),
            ("Preserved Future Candidate", preserved_lines),
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
    result_path = out_dir / f"atlas_a22_private_sqrt_candidate_reframe_or_park_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a22_private_sqrt_candidate_reframe_or_park_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a22_private_sqrt_candidate_reframe_or_park_selector.json"
    feed_path = command_feed_dir / f"atlas_a22_private_sqrt_candidate_reframe_or_park_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a22_private_sqrt_candidate_reframe_or_park_selector",
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
    print("ATLAS_A22_PRIVATE_SQRT_CANDIDATE_REFRAME_OR_PARK_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
