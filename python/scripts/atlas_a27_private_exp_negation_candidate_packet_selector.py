#!/usr/bin/env python3
"""ATLAS-A27 private exp-negation candidate packet selector."""

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

from scripts import atlas_a26_private_exp_negation_boundary_feasibility_packet as a26  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_exp_negation_candidate_packet_selector.v0"
STATUS = "ATLAS_A27_PRIVATE_EXP_NEGATION_CANDIDATE_PACKET_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a27-private-exp-negation-candidate-packet-selector"
SOURCE_DIRECTION_ID = "exp_negation_multiplicative_identity_direction"
SELECTED_OPTION_ID = "recommend_future_scoped_exp_negation_candidate_packet"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A28 private scoped exp-negation candidate packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a26_consumed",
    "candidate_packet_selector_created",
    "feasibility_review_consumed",
    "scope_choice_required_recorded",
    "future_candidate_packet_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a26_consumed": True,
    "candidate_packet_selector_created": True,
    "feasibility_review_consumed": True,
    "scope_choice_required_recorded": True,
    "future_candidate_packet_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "new_candidate_packet_created": False,
    "candidate_packet_created_this_phase": False,
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
    "ATLAS-A27 is a private selector; it recommends a future scoped candidate packet but does not create that packet, select a proof target, edit MachLib, run Lean, or claim candidate validity.",
    "ATLAS-A27 requires the future packet to choose pure exp, EML-shaped, or paired statement scope; it does not resolve that statement scope in this phase.",
    "ATLAS-A27 does not perform theorem lookup, claim exact theorem names, change runtime lowering, replace exp, publish or approve public copy, create SDK/compiler/course copy, touch laptop-owned repositories, or claim checked-witness status, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    review = source["feasibilityReview"]
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "decision": "recommend_scoped_candidate_packet_without_creating_it",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "readinessReasons": [
                "A26 recorded a clean all-real guard surface.",
                "A26 recorded both pure and possible EML-shaped hints without conflating them.",
                "A26 recorded explicit blockers before any packet, making a scoped packet selector appropriate.",
            ],
            "scopeRequirementsForFuturePacket": [
                "choose pure exp statement, EML-shaped statement, or paired statement scope",
                "state that candidate validity remains blocked",
                "carry forward runtime exp replacement and public-copy non-claims",
            ],
            "sourceSignals": {
                "reviewedDirectionId": review["entryId"],
                "requiredGuard": review["guardReview"]["requiredGuard"],
                "pureShapeHint": review["statementShapeReview"]["pureShapeHint"],
                "possibleEmlBoundaryHint": review["statementShapeReview"]["possibleEmlBoundaryHint"],
                "blockerCount": len(review["blockersBeforeCandidatePacket"]),
            },
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "hold_for_statement_scope_clarification",
            "selectionStatus": "available_if_human_wants_scope_decision_first",
            "decision": "pause_before_candidate_packet_for_scope_clarification",
            "nextArtifact": "Future private exp-negation statement-scope clarification selector",
            "readinessReasons": [
                "A26 left pure-vs-EML-vs-paired scope unresolved.",
            ],
            "scopeRequirementsForFuturePacket": [],
            "sourceSignals": None,
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "decision": "pause_exp_negation_path_for_atlas_v0_doc",
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "readinessReasons": [
                "The exp-negation path is now bounded enough to pause without losing context.",
            ],
            "scopeRequirementsForFuturePacket": [],
            "sourceSignals": None,
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a26.build_payload(atlas_gate_path, machlib_root)
    a26.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedDirectionId": source["summary"]["reviewedDirectionId"],
        "sourceFeasibilityStatus": source["summary"]["feasibilityStatus"],
        "candidatePacketSelectorCreated": True,
        "feasibilityReviewConsumed": True,
        "selectedOptionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "futureCandidatePacketRecommended": True,
        "scopeChoiceRequiredRecorded": True,
        "sourceRequiredGuard": selected["sourceSignals"]["requiredGuard"],
        "sourcePureShapeHint": selected["sourceSignals"]["pureShapeHint"],
        "sourcePossibleEmlBoundaryHint": selected["sourceSignals"]["possibleEmlBoundaryHint"],
        "sourceBlockerCount": selected["sourceSignals"]["blockerCount"],
        "newCandidatePacketCreated": False,
        "candidatePacketCreatedThisPhase": False,
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
        artifact_type="private_exp_negation_candidate_packet_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceFeasibilityReview": source["feasibilityReview"],
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
    if payload["sourceArtifact"] != "atlas-a26-private-exp-negation-boundary-feasibility-packet":
        raise ValueError("ATLAS-A27 must consume ATLAS-A26")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A27 must consume exp-negation direction")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "recommend_scoped_candidate_packet_without_creating_it":
        raise ValueError("unexpected selected decision")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option status drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["sourceRequiredGuard"] != "all real x":
        raise ValueError("guard drift")
    if summary["sourcePureShapeHint"] != "exp x * exp (-x) = 1":
        raise ValueError("pure shape drift")
    if summary["sourcePossibleEmlBoundaryHint"] != "eml (x + (-x)) 1 = 1":
        raise ValueError("EML hint drift")
    if summary["sourceBlockerCount"] != 4:
        raise ValueError("expected four blockers")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "candidatePacketSelectorCreated",
        "feasibilityReviewConsumed",
        "futureCandidatePacketRecommended",
        "scopeChoiceRequiredRecorded",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "newCandidatePacketCreated",
        "candidatePacketCreatedThisPhase",
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
        artifact_type="private_exp_negation_candidate_packet_selector",
        semantic_strength="private_selector_recommends_future_scoped_candidate_packet_no_packet_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a27_private_exp_negation_candidate_packet_selector/atlas_a27_private_exp_negation_candidate_packet_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a27_private_exp_negation_candidate_packet_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A28 as a private scoped exp-negation candidate packet; do not start proof work or claim validity from A27.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "selectedDecision": payload["summary"]["selectedDecision"],
            "sourceReviewedDirectionId": payload["summary"]["sourceReviewedDirectionId"],
            "newCandidatePacketCreated": payload["summary"]["newCandidatePacketCreated"],
            "candidatePacketCreatedThisPhase": payload["summary"]["candidatePacketCreatedThisPhase"],
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
        ("reviewed direction", payload["summary"]["sourceReviewedDirectionId"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("source guard", payload["summary"]["sourceRequiredGuard"]),
        ("source pure shape", payload["summary"]["sourcePureShapeHint"]),
        ("source EML hint", payload["summary"]["sourcePossibleEmlBoundaryHint"]),
        ("new candidate packet created", payload["summary"]["newCandidatePacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    reason_lines = [f"- {item}" for item in selected["readinessReasons"]]
    scope_lines = [f"- {item}" for item in selected["scopeRequirementsForFuturePacket"]]
    option_lines = ["| Option | Status | Decision |", "|---|---|---|"]
    for option in payload["options"]:
        option_lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | `{option['decision']}` |"
        )
    return render_markdown_report(
        title="ATLAS-A27 Private Exp-Negation Candidate Packet Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Readiness Reasons", reason_lines),
            ("Future Packet Scope Requirements", scope_lines),
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
    result_path = out_dir / f"atlas_a27_private_exp_negation_candidate_packet_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a27_private_exp_negation_candidate_packet_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a27_private_exp_negation_candidate_packet_selector.json"
    feed_path = command_feed_dir / f"atlas_a27_private_exp_negation_candidate_packet_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a27_private_exp_negation_candidate_packet_selector",
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
    print("ATLAS_A27_PRIVATE_EXP_NEGATION_CANDIDATE_PACKET_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
