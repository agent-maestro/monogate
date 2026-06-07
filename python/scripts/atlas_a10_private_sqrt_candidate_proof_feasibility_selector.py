#!/usr/bin/env python3
"""ATLAS-A10 private sqrt candidate proof-feasibility selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a9_private_abs_normalized_sqrt_candidate_packet as a9  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_sqrt_candidate_proof_feasibility_selector.v0"
STATUS = "ATLAS_A10_PRIVATE_SQRT_CANDIDATE_PROOF_FEASIBILITY_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a10-private-sqrt-candidate-proof-feasibility-selector"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
SELECTED_OPTION_ID = "create_bounded_sqrt_proof_feasibility_review_packet"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A11 private bounded sqrt proof-feasibility review packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a9_consumed",
    "proof_feasibility_selector_created",
    "candidate_packet_reviewed",
    "abs_normalized_shape_reviewed",
    "guard_shape_reviewed",
    "bounded_review_packet_recommended",
    "candidate_validity_blocked",
    "proof_attempt_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a9_consumed": True,
    "proof_feasibility_selector_created": True,
    "candidate_packet_reviewed": True,
    "abs_normalized_shape_reviewed": True,
    "guard_shape_reviewed": True,
    "bounded_review_packet_recommended": True,
    "candidate_validity_blocked": True,
    "proof_attempt_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "proof_feasibility_review_packet_created": False,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "theorem_lookup_performed": False,
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
    "ATLAS-A10 is a private selector; it recommends a later proof-feasibility review packet but does not create that packet, start proof work, or select the candidate for proof.",
    "ATLAS-A10 reviews the A9 candidate packet shape only; it does not claim the sqrt candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A10 does not edit MachLib, run Lean, perform theorem lookup, change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = source["candidatePacket"]
    forms = candidate["proofFacingForms"]
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "decision": "create_private_review_packet_without_starting_proof",
            "rationale": [
                "A9 records both the abs-normalized intermediate and the guarded explanatory form.",
                "The guard list is small and communicable: real input plus nonnegative input.",
                "The next useful work is a bounded feasibility review of proof shape risks, not a MachLib edit.",
            ],
            "reviewInputs": {
                "candidateId": candidate["candidateId"],
                "absNormalizedIntermediate": forms["absNormalizedIntermediate"],
                "guardedExplanatoryForm": forms["guardedExplanatoryForm"],
                "guards": [guard["condition"] for guard in candidate["guards"]],
            },
            "blockedActions": [
                "do not edit MachLib",
                "do not run Lean",
                "do not perform theorem lookup",
                "do not claim validity",
                "do not create public copy",
            ],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_reference_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "decision": "pause_candidate_review_for_reference_document",
            "rationale": [
                "A9 is already useful as a private reference entry even without proof-feasibility work.",
            ],
            "reviewInputs": None,
            "blockedActions": ["target lower bound remains unreached", "no public copy approval"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "park_sqrt_candidate_packet",
            "selectionStatus": "not_selected",
            "nextArtifact": "Park A9 candidate pending reviewer input",
            "decision": "park_candidate_without_rejection",
            "rationale": [
                "Parking remains possible because A9 makes the abs-normalization caveat explicit.",
            ],
            "reviewInputs": None,
            "blockedActions": ["would leave the current two-artifact Atlas gap unchanged"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a9.build_payload(atlas_gate_path)
    a9.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    candidate = source["candidatePacket"]
    forms = candidate["proofFacingForms"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "candidateId": candidate["candidateId"],
        "candidateStatus": candidate["candidateStatus"],
        "absNormalizedIntermediate": forms["absNormalizedIntermediate"],
        "guardedExplanatoryForm": forms["guardedExplanatoryForm"],
        "emlGuardedBoundaryHint": forms["emlGuardedBoundaryHint"],
        "guardConditions": [guard["condition"] for guard in candidate["guards"]],
        "proofFeasibilitySelectorCreated": True,
        "candidatePacketReviewed": True,
        "absNormalizedShapeReviewed": True,
        "guardShapeReviewed": True,
        "selectedOptionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "boundedReviewPacketRecommended": True,
        "proofFeasibilityReviewPacketCreated": False,
        "candidateValidityBlocked": True,
        "proofAttemptBlocked": True,
        "candidateValidityClaim": False,
        "candidateSelectedForProof": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "theoremLookupPerformed": False,
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
        artifact_type="private_sqrt_candidate_proof_feasibility_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "candidatePacket": candidate,
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
    if payload["sourceArtifact"] != "atlas-a9-private-abs-normalized-sqrt-candidate-packet":
        raise ValueError("ATLAS-A10 must consume ATLAS-A9")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["absNormalizedIntermediate"] != "sqrt (x * x) = |x|":
        raise ValueError("missing abs-normalized intermediate")
    if summary["guardedExplanatoryForm"] != "0 <= x -> sqrt (x * x) = x":
        raise ValueError("missing guarded explanatory form")
    if summary["guardConditions"] != ["x : Real", "0 <= x"]:
        raise ValueError("guard condition drift")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "create_private_review_packet_without_starting_proof":
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
        "proofFeasibilitySelectorCreated",
        "candidatePacketReviewed",
        "absNormalizedShapeReviewed",
        "guardShapeReviewed",
        "boundedReviewPacketRecommended",
        "candidateValidityBlocked",
        "proofAttemptBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "proofFeasibilityReviewPacketCreated",
        "candidateValidityClaim",
        "candidateSelectedForProof",
        "candidateProved",
        "proofAttemptStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "theoremLookupPerformed",
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
        artifact_type="private_sqrt_candidate_proof_feasibility_selector",
        semantic_strength="private_selector_recommends_bounded_sqrt_proof_feasibility_review_no_proof_no_validity",
        source=f"python/results/atlas_a10_private_sqrt_candidate_proof_feasibility_selector/atlas_a10_private_sqrt_candidate_proof_feasibility_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a10_private_sqrt_candidate_proof_feasibility_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A11 as a private bounded sqrt proof-feasibility review packet.",
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
        ("review packet created", payload["summary"]["proofFeasibilityReviewPacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    option_lines = ["| Option | Status | Decision |", "|---|---|---|"]
    for item in payload["options"]:
        option_lines.append(f"| `{item['optionId']}` | `{item['selectionStatus']}` | `{item['decision']}` |")
    input_lines = [
        f"- abs-normalized intermediate: `{payload['summary']['absNormalizedIntermediate']}`",
        f"- guarded explanatory form: `{payload['summary']['guardedExplanatoryForm']}`",
        f"- EML guarded boundary hint: `{payload['summary']['emlGuardedBoundaryHint']}`",
        f"- guards: `{', '.join(payload['summary']['guardConditions'])}`",
    ]
    return render_markdown_report(
        title="ATLAS-A10 Private Sqrt Candidate Proof-Feasibility Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[("Review Inputs", input_lines), ("Options", option_lines)],
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
    result_path = out_dir / f"atlas_a10_private_sqrt_candidate_proof_feasibility_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a10_private_sqrt_candidate_proof_feasibility_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a10_private_sqrt_candidate_proof_feasibility_selector.json"
    feed_path = command_feed_dir / f"atlas_a10_private_sqrt_candidate_proof_feasibility_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a10_private_sqrt_candidate_proof_feasibility_selector",
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
    print("ATLAS_A10_PRIVATE_SQRT_CANDIDATE_PROOF_FEASIBILITY_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
