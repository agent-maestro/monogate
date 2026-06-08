#!/usr/bin/env python3
"""ATLAS-A37 private trig pythagorean candidate packet selector."""

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

from scripts import atlas_a36_private_trig_pythagorean_feasibility_packet as a36  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_trig_pythagorean_candidate_packet_selector.v0"
STATUS = "ATLAS_A37_PRIVATE_TRIG_PYTHAGOREAN_CANDIDATE_PACKET_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a37-private-trig-pythagorean-candidate-packet-selector"
SOURCE_DIRECTION_ID = "trig_pythagorean_unit_identity_direction"
SELECTED_OPTION_ID = "recommend_future_pure_trig_candidate_packet"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A38 private scoped trig pythagorean candidate packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a36_consumed",
    "candidate_packet_selector_created",
    "feasibility_review_consumed",
    "pure_trig_scope_selected_for_future_packet",
    "future_candidate_packet_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "theorem_lookup_blocked",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "atlas_a36_consumed": True,
    "candidate_packet_selector_created": True,
    "feasibility_review_consumed": True,
    "pure_trig_scope_selected_for_future_packet": True,
    "future_candidate_packet_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "theorem_lookup_blocked": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
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
    "ATLAS-A37 is a private selector; it recommends a future scoped candidate packet but does not create that packet, select a proof target, edit MachLib, run Lean, perform theorem lookup, or claim candidate validity.",
    "ATLAS-A37 selects pure real trig statement scope for a future candidate packet; it does not add an EML companion, claim exact theorem names, or claim Lean readiness.",
    "ATLAS-A37 does not change runtime lowering, replace trig functions, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, start D110, touch laptop-owned repositories, or claim target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    review = source["feasibilityReview"]
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "decision": "recommend_pure_trig_candidate_packet_without_creating_it",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "readinessReasons": [
                "A36 recorded a clean all-real guard surface.",
                "A36 explicitly deferred EML boundary shape, making pure trig scope the narrow candidate path.",
                "A36 recorded theorem-lookup and notation risks as blockers before proof work.",
            ],
            "scopeRequirementsForFuturePacket": [
                "use pure real trig identity scope only",
                "use repeated multiplication shape unless a later packet explicitly switches notation",
                "state that candidate validity, theorem lookup, proof, and runtime claims remain blocked",
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
            "optionId": "hold_for_trig_notation_clarification",
            "selectionStatus": "available_if_reviewer_wants_notation_choice_first",
            "decision": "pause_before_candidate_packet_for_square_vs_multiplication_notation",
            "nextArtifact": "Future private trig notation clarification selector",
            "readinessReasons": [
                "A36 recorded repeated multiplication versus square notation as a blocker.",
            ],
            "scopeRequirementsForFuturePacket": [],
            "sourceSignals": None,
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "decision": "pause_trig_path_for_atlas_v0_doc",
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "readinessReasons": [
                "The trig path is bounded enough to pause without losing context.",
            ],
            "scopeRequirementsForFuturePacket": [],
            "sourceSignals": None,
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a36.build_payload(atlas_gate_path, machlib_root)
    a36.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    signals = selected["sourceSignals"]
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
        "pureTrigScopeSelectedForFuturePacket": True,
        "sourceRequiredGuard": signals["requiredGuard"],
        "sourcePureShapeHint": signals["pureShapeHint"],
        "sourcePossibleEmlBoundaryHint": signals["possibleEmlBoundaryHint"],
        "sourceBlockerCount": signals["blockerCount"],
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
        artifact_type="private_trig_pythagorean_candidate_packet_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
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
    if payload["sourceArtifact"] != "atlas-a36-private-trig-pythagorean-feasibility-packet":
        raise ValueError("ATLAS-A37 must consume ATLAS-A36")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A37 must consume trig direction")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "recommend_pure_trig_candidate_packet_without_creating_it":
        raise ValueError("unexpected selected decision")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option status drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["sourceRequiredGuard"] != "all real x":
        raise ValueError("guard drift")
    if summary["sourcePureShapeHint"] != "sin x * sin x + cos x * cos x = 1":
        raise ValueError("pure shape drift")
    if summary["sourcePossibleEmlBoundaryHint"] != "deferred_no_eml_shape_selected":
        raise ValueError("EML hint drift")
    if summary["sourceBlockerCount"] != 4:
        raise ValueError("expected four blockers")
    if summary["atlasRowCount"] != 14:
        raise ValueError("expected fourteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 1:
        raise ValueError("expected one additional artifact for lower bound")
    for key in [
        "candidatePacketSelectorCreated",
        "feasibilityReviewConsumed",
        "futureCandidatePacketRecommended",
        "pureTrigScopeSelectedForFuturePacket",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "theoremLookupBlocked",
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
        artifact_type="private_trig_pythagorean_candidate_packet_selector",
        semantic_strength="private_selector_only_future_candidate_packet_recommended_no_packet_validity_public_runtime_product_claims",
        source=f"python/results/atlas_a37_private_trig_pythagorean_candidate_packet_selector/atlas_a37_private_trig_pythagorean_candidate_packet_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a37_private_trig_pythagorean_candidate_packet_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A38 as a private scoped trig pythagorean candidate packet only; keep theorem lookup, proof, MachLib edits, Lean checks, public, runtime, product, and course work blocked.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "sourcePureShapeHint": payload["summary"]["sourcePureShapeHint"],
            "sourceRequiredGuard": payload["summary"]["sourceRequiredGuard"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "additionalArtifactsNeededForLowerBound": payload["summary"]["additionalArtifactsNeededForLowerBound"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    selected = payload["selectedOption"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("source guard", payload["summary"]["sourceRequiredGuard"]),
        ("source pure shape", payload["summary"]["sourcePureShapeHint"]),
        ("source EML hint", payload["summary"]["sourcePossibleEmlBoundaryHint"]),
        ("source blocker count", payload["summary"]["sourceBlockerCount"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("candidate packet created this phase", payload["summary"]["candidatePacketCreatedThisPhase"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("theorem lookup performed", payload["summary"]["theoremLookupPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    readiness_lines = [f"- {item}" for item in selected["readinessReasons"]]
    scope_lines = [f"- {item}" for item in selected["scopeRequirementsForFuturePacket"]]
    option_lines = [f"- `{item['optionId']}`: {item['selectionStatus']} -> {item['decision']}" for item in payload["options"]]
    return render_markdown_report(
        title="ATLAS-A37 Private Trig Pythagorean Candidate Packet Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Readiness Reasons", readiness_lines),
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
    result_path = out_dir / f"atlas_a37_private_trig_pythagorean_candidate_packet_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a37_private_trig_pythagorean_candidate_packet_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a37_private_trig_pythagorean_candidate_packet_selector.json"
    feed_path = command_feed_dir / f"atlas_a37_private_trig_pythagorean_candidate_packet_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a37_private_trig_pythagorean_candidate_packet_selector",
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
    print("ATLAS_A37_PRIVATE_TRIG_PYTHAGOREAN_CANDIDATE_PACKET_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
