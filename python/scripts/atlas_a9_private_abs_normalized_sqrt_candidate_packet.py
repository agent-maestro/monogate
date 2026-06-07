#!/usr/bin/env python3
"""ATLAS-A9 private abs-normalized sqrt boundary candidate packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a8_private_sqrt_candidate_value_selector as a8  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_abs_normalized_sqrt_candidate_packet.v0"
STATUS = "ATLAS_A9_PRIVATE_ABS_NORMALIZED_SQRT_CANDIDATE_PACKET_PASS"
ARTIFACT_ID = "atlas-a9-private-abs-normalized-sqrt-candidate-packet"
SOURCE_ENTRY_ID = "sqrt_square_nonnegative_roundtrip_candidate"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A10 private sqrt candidate proof-feasibility selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a8_consumed",
    "private_candidate_packet_created",
    "abs_normalized_intermediate_recorded",
    "guarded_explanatory_form_recorded",
    "guards_recorded",
    "blocked_claims_recorded",
    "candidate_validity_blocked",
    "proof_feasibility_selector_recommended",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a8_consumed": True,
    "private_candidate_packet_created": True,
    "abs_normalized_intermediate_recorded": True,
    "guarded_explanatory_form_recorded": True,
    "guards_recorded": True,
    "blocked_claims_recorded": True,
    "candidate_validity_blocked": True,
    "proof_feasibility_selector_recommended": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "candidate_validity_claim": False,
    "candidate_selected_for_proof": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "proof_feasibility_review_completed": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "runtime_lowering_changed": False,
    "runtime_sqrt_replacement_claim": False,
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
    "ATLAS-A9 creates a private candidate packet only; it does not claim the candidate is true, valid, checked, Lean-ready, or selected for proof.",
    "ATLAS-A9 records an abs-normalized intermediate and guarded explanatory form for later review; it does not edit MachLib, run Lean, or start proof work.",
    "ATLAS-A9 does not change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_candidate_packet(source: dict[str, Any]) -> dict[str, Any]:
    review = source["sourceSqrtReferenceReview"]
    return {
        "candidateId": CANDIDATE_ID,
        "sourceEntryId": SOURCE_ENTRY_ID,
        "candidateStatus": "private_candidate_packet_only_not_validity_not_proof",
        "sourceCandidateShape": source["summary"]["selectedCandidateShape"],
        "familyHint": review["familyHint"],
        "emlShapedStatementHint": review["statementShapeHint"],
        "proofFacingForms": {
            "absNormalizedIntermediate": "sqrt (x * x) = |x|",
            "guardedExplanatoryForm": "0 <= x -> sqrt (x * x) = x",
            "emlGuardedBoundaryHint": "0 <= x -> eml (sqrt (x * x)) x = x",
            "formStatus": "candidate_shapes_for_review_not_lean_ready",
        },
        "guards": [
            {
                "guardId": "real_input",
                "condition": "x : Real",
                "appliesTo": ["absNormalizedIntermediate", "guardedExplanatoryForm", "emlGuardedBoundaryHint"],
                "guardPurpose": "keeps the candidate in the real-number boundary family",
            },
            {
                "guardId": "nonnegative_input",
                "condition": "0 <= x",
                "appliesTo": ["guardedExplanatoryForm", "emlGuardedBoundaryHint"],
                "guardPurpose": "permits reducing abs(x) to x after the abs-normalized intermediate",
            },
        ],
        "reviewNotes": [
            "The abs-normalized intermediate is the proof-facing shape to inspect first.",
            "The guarded explanatory form is the course/SDK-facing shape, not a proof result.",
            "Any later Lean-facing attempt must choose exact theorem names and check guard direction before claiming validity.",
        ],
        "referenceHooks": review["referenceUsefulness"],
        "blockedClaims": [
            "not a checked witness",
            "not a candidate validity claim",
            "not selected for proof",
            "no proof attempt started",
            "no MachLib edit",
            "no Lean typecheck",
            "no runtime sqrt replacement",
            "no public copy approval",
            "no SDK/compiler/course copy created",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a8.build_payload(atlas_gate_path)
    a8.validate_payload(source)
    candidate = build_candidate_packet(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "sourceSelectedCandidateShape": source["summary"]["selectedCandidateShape"],
        "sourceCandidatePacketRecommended": source["summary"]["candidatePacketRecommended"],
        "sourceCandidatePacketCreated": source["summary"]["candidatePacketCreated"],
        "candidateId": candidate["candidateId"],
        "sourceEntryId": candidate["sourceEntryId"],
        "candidateStatus": candidate["candidateStatus"],
        "privateCandidatePacketCreated": True,
        "absNormalizedIntermediateRecorded": True,
        "guardedExplanatoryFormRecorded": True,
        "guardsRecorded": True,
        "blockedClaimsRecorded": True,
        "candidateValidityBlocked": True,
        "candidateValidityClaim": False,
        "candidateSelectedForProof": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "proofFeasibilityReviewCompleted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
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
        artifact_type="private_abs_normalized_sqrt_candidate_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceSelectedOption": source["selectedOption"],
            "candidatePacket": candidate,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    candidate = payload["candidatePacket"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(candidate["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a8-private-sqrt-candidate-value-selector":
        raise ValueError("ATLAS-A9 must consume ATLAS-A8")
    if summary["sourceSelectedOptionId"] != "create_abs_normalized_sqrt_candidate_packet":
        raise ValueError("A9 must consume A8's abs-normalized selection")
    if summary["sourceSelectedCandidateShape"] != "abs_normalized_then_guarded":
        raise ValueError("candidate shape drift")
    if summary["sourceCandidatePacketRecommended"] is not True:
        raise ValueError("A8 must recommend the candidate packet")
    if summary["sourceCandidatePacketCreated"] is not False:
        raise ValueError("A8 should not already create the candidate packet")
    if summary["candidateId"] != CANDIDATE_ID or candidate["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if candidate["proofFacingForms"]["absNormalizedIntermediate"] != "sqrt (x * x) = |x|":
        raise ValueError("missing abs-normalized intermediate")
    if candidate["proofFacingForms"]["guardedExplanatoryForm"] != "0 <= x -> sqrt (x * x) = x":
        raise ValueError("missing guarded explanatory form")
    if candidate["proofFacingForms"]["formStatus"] != "candidate_shapes_for_review_not_lean_ready":
        raise ValueError("candidate form must remain not Lean-ready")
    guard_conditions = {guard["condition"] for guard in candidate["guards"]}
    if guard_conditions != {"x : Real", "0 <= x"}:
        raise ValueError("guard drift")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "privateCandidatePacketCreated",
        "absNormalizedIntermediateRecorded",
        "guardedExplanatoryFormRecorded",
        "guardsRecorded",
        "blockedClaimsRecorded",
        "candidateValidityBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "candidateValidityClaim",
        "candidateSelectedForProof",
        "candidateProved",
        "proofAttemptStarted",
        "proofFeasibilityReviewCompleted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
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
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_abs_normalized_sqrt_candidate_packet",
        semantic_strength="private_candidate_packet_records_abs_normalized_sqrt_shapes_no_validity_no_proof",
        source=f"python/results/atlas_a9_private_abs_normalized_sqrt_candidate_packet/atlas_a9_private_abs_normalized_sqrt_candidate_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a9_private_abs_normalized_sqrt_candidate_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A10 as a private sqrt candidate proof-feasibility selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "candidateStatus": payload["summary"]["candidateStatus"],
            "absNormalizedIntermediate": payload["candidatePacket"]["proofFacingForms"]["absNormalizedIntermediate"],
            "guardedExplanatoryForm": payload["candidatePacket"]["proofFacingForms"]["guardedExplanatoryForm"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    forms = payload["candidatePacket"]["proofFacingForms"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("candidate status", payload["summary"]["candidateStatus"]),
        ("abs-normalized intermediate", forms["absNormalizedIntermediate"]),
        ("guarded explanatory form", forms["guardedExplanatoryForm"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    guard_lines = ["| Guard | Applies To | Purpose |", "|---|---|---|"]
    for guard in payload["candidatePacket"]["guards"]:
        guard_lines.append(
            f"| `{guard['condition']}` | `{', '.join(guard['appliesTo'])}` | {guard['guardPurpose']} |"
        )
    blocked_lines = [f"- {item}" for item in payload["candidatePacket"]["blockedClaims"]]
    return render_markdown_report(
        title="ATLAS-A9 Private Abs-Normalized Sqrt Candidate Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[("Guards", guard_lines), ("Blocked Claims", blocked_lines)],
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
    result_path = out_dir / f"atlas_a9_private_abs_normalized_sqrt_candidate_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a9_private_abs_normalized_sqrt_candidate_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a9_private_abs_normalized_sqrt_candidate_packet.json"
    feed_path = command_feed_dir / f"atlas_a9_private_abs_normalized_sqrt_candidate_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a9_private_abs_normalized_sqrt_candidate_packet",
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
    print("ATLAS_A9_PRIVATE_ABS_NORMALIZED_SQRT_CANDIDATE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
