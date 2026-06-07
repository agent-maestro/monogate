#!/usr/bin/env python3
"""ATLAS-A16 private sqrt proof-attempt open selector."""

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

from scripts import atlas_a15_private_scoped_sqrt_proof_attempt_packet as a15  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_sqrt_proof_attempt_open_selector.v0"
STATUS = "ATLAS_A16_PRIVATE_SQRT_PROOF_ATTEMPT_OPEN_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a16-private-sqrt-proof-attempt-open-selector"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
ATTEMPT_PACKET_ID = "sqrt_abs_normalized_nonnegative_private_scoped_attempt_packet"
SELECTED_OPTION_ID = "recommend_future_bounded_sqrt_proof_attempt_artifact"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A17 private bounded sqrt proof-attempt artifact"

TRUE_CLAIM_FLAGS = {
    "atlas_a15_consumed",
    "proof_attempt_open_selector_created",
    "scoped_attempt_packet_reviewed",
    "attempt_scope_reviewed",
    "attempt_route_reviewed",
    "attempt_budget_reviewed",
    "future_bounded_attempt_artifact_recommended",
    "candidate_validity_blocked",
    "actual_proof_attempt_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a15_consumed": True,
    "proof_attempt_open_selector_created": True,
    "scoped_attempt_packet_reviewed": True,
    "attempt_scope_reviewed": True,
    "attempt_route_reviewed": True,
    "attempt_budget_reviewed": True,
    "future_bounded_attempt_artifact_recommended": True,
    "candidate_validity_blocked": True,
    "actual_proof_attempt_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "bounded_proof_attempt_artifact_created": False,
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
    "ATLAS-A16 is a private open selector only; it recommends a future bounded proof-attempt artifact but does not create that artifact, start proof work, edit MachLib, or run Lean.",
    "ATLAS-A16 reviews A15's scoped attempt packet and selects the next bounded attempt artifact path; it does not perform theorem lookup, claim exact theorem names, or claim the candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A16 does not change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    attempt = source["scopedAttemptPacket"]
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "decision": "recommend_bounded_attempt_artifact_without_starting_attempt",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "openRationale": [
                "A15 has a narrow file scope and a one-run future Lean budget.",
                "A15 records the required abs-normalized route before any later MachLib edit.",
                "A future attempt artifact can either produce one local patch candidate or a precise blocker.",
            ],
            "strictFutureLimits": {
                "allowedFiles": attempt["allowedScope"]["allowedFiles"],
                "futureAttemptWallClockLimitMinutes": attempt["attemptBudget"][
                    "futureAttemptWallClockLimitMinutes"
                ],
                "futureLeanRunLimit": attempt["attemptBudget"]["futureLeanRunLimit"],
                "requiredRouteStepIds": [item["stepId"] for item in attempt["requiredStartingRoute"]],
                "abortConditionCount": len(attempt["abortConditions"]),
                "expectedFutureOutputCount": len(attempt["expectedFutureOutputsIfOpened"]),
            },
            "remainingBlocks": [
                "A16 does not create the bounded attempt artifact",
                "A16 does not edit MachLib",
                "A16 does not run Lean",
                "candidate validity remains blocked",
                "public copy remains blocked",
            ],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_reference_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "decision": "pause_attempt_path_for_reference_document",
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "openRationale": [
                "The candidate already has useful reference-shape evidence without proof attempt cost.",
            ],
            "strictFutureLimits": None,
            "remainingBlocks": ["proof path would remain closed", "public copy remains blocked"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "park_sqrt_candidate_before_attempt",
            "selectionStatus": "not_selected",
            "decision": "park_candidate_without_rejection",
            "nextArtifact": "Park sqrt candidate before bounded attempt",
            "openRationale": ["Parking remains valid if the future attempt cost is not worth the Atlas value."],
            "strictFutureLimits": None,
            "remainingBlocks": ["no checked-witness claim", "target lower bound remains unreached"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a15.build_payload(atlas_gate_path)
    a15.validate_payload(source)
    attempt = source["scopedAttemptPacket"]
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceAttemptPacketId": source["summary"]["attemptPacketId"],
        "candidateId": source["summary"]["candidateId"],
        "proofAttemptOpenSelectorCreated": True,
        "scopedAttemptPacketReviewed": True,
        "attemptScopeReviewed": True,
        "attemptRouteReviewed": True,
        "attemptBudgetReviewed": True,
        "allowedFiles": attempt["allowedScope"]["allowedFiles"],
        "futureAttemptWallClockLimitMinutes": attempt["attemptBudget"]["futureAttemptWallClockLimitMinutes"],
        "futureLeanRunLimit": attempt["attemptBudget"]["futureLeanRunLimit"],
        "requiredRouteStepIds": [item["stepId"] for item in attempt["requiredStartingRoute"]],
        "abortConditionCount": len(attempt["abortConditions"]),
        "expectedFutureOutputCount": len(attempt["expectedFutureOutputsIfOpened"]),
        "selectedOptionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "futureBoundedAttemptArtifactRecommended": True,
        "boundedProofAttemptArtifactCreated": False,
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
        artifact_type="private_sqrt_proof_attempt_open_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceScopedAttemptPacket": attempt,
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
    if payload["sourceArtifact"] != "atlas-a15-private-scoped-sqrt-proof-attempt-packet":
        raise ValueError("ATLAS-A16 must consume ATLAS-A15")
    if summary["sourceAttemptPacketId"] != ATTEMPT_PACKET_ID:
        raise ValueError("attempt packet id drift")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["allowedFiles"] != ["MachLib/Real.lean"]:
        raise ValueError("allowed file drift")
    if summary["futureAttemptWallClockLimitMinutes"] != 30:
        raise ValueError("timeout budget drift")
    if summary["futureLeanRunLimit"] != 1:
        raise ValueError("Lean run limit drift")
    if summary["requiredRouteStepIds"] != ["abs_normalization", "guard_reduction", "eml_boundary_alignment"]:
        raise ValueError("route drift")
    if summary["abortConditionCount"] != 5:
        raise ValueError("abort count drift")
    if summary["expectedFutureOutputCount"] != 4:
        raise ValueError("future output count drift")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "recommend_bounded_attempt_artifact_without_starting_attempt":
        raise ValueError("unexpected selected decision")
    if payload["selectedOption"]["selectionStatus"] != "selected_next":
        raise ValueError("selected option must be selected_next")
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
        "proofAttemptOpenSelectorCreated",
        "scopedAttemptPacketReviewed",
        "attemptScopeReviewed",
        "attemptRouteReviewed",
        "attemptBudgetReviewed",
        "futureBoundedAttemptArtifactRecommended",
        "candidateValidityBlocked",
        "actualProofAttemptBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "boundedProofAttemptArtifactCreated",
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
        artifact_type="private_sqrt_proof_attempt_open_selector",
        semantic_strength="private_open_selector_recommends_future_bounded_attempt_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a16_private_sqrt_proof_attempt_open_selector/atlas_a16_private_sqrt_proof_attempt_open_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a16_private_sqrt_proof_attempt_open_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A17 as a private bounded sqrt proof-attempt artifact only if the attempt budget and abort rules are preserved.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "futureBoundedAttemptArtifactRecommended": payload["summary"][
                "futureBoundedAttemptArtifactRecommended"
            ],
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
        ("source attempt packet", payload["summary"]["sourceAttemptPacketId"]),
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    rationale_lines = [f"- {item}" for item in selected["openRationale"]]
    limit = selected["strictFutureLimits"]
    limit_lines = [
        f"- allowed files: `{', '.join(limit['allowedFiles'])}`",
        f"- future wall-clock limit minutes: `{limit['futureAttemptWallClockLimitMinutes']}`",
        f"- future Lean run limit: `{limit['futureLeanRunLimit']}`",
        f"- required route step ids: `{', '.join(limit['requiredRouteStepIds'])}`",
        f"- abort condition count: `{limit['abortConditionCount']}`",
        f"- expected future output count: `{limit['expectedFutureOutputCount']}`",
    ]
    option_lines = ["| Option | Status | Decision |", "|---|---|---|"]
    for option in payload["options"]:
        option_lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | `{option['decision']}` |"
        )
    block_lines = [f"- {item}" for item in selected["remainingBlocks"]]
    return render_markdown_report(
        title="ATLAS-A16 Private Sqrt Proof-Attempt Open Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Open Rationale", rationale_lines),
            ("Strict Future Attempt Limits", limit_lines),
            ("Options", option_lines),
            ("Remaining Blocks", block_lines),
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
    result_path = out_dir / f"atlas_a16_private_sqrt_proof_attempt_open_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a16_private_sqrt_proof_attempt_open_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a16_private_sqrt_proof_attempt_open_selector.json"
    feed_path = command_feed_dir / f"atlas_a16_private_sqrt_proof_attempt_open_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a16_private_sqrt_proof_attempt_open_selector",
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
    print("ATLAS_A16_PRIVATE_SQRT_PROOF_ATTEMPT_OPEN_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
