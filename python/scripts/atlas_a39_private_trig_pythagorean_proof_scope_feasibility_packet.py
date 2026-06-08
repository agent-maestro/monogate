#!/usr/bin/env python3
"""ATLAS-A39 private trig pythagorean proof-scope feasibility packet."""

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

from scripts import atlas_a38_private_scoped_trig_pythagorean_candidate_packet as a38  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_trig_pythagorean_proof_scope_feasibility_packet.v0"
STATUS = "ATLAS_A39_PRIVATE_TRIG_PYTHAGOREAN_PROOF_SCOPE_FEASIBILITY_PACKET_PASS"
ARTIFACT_ID = "atlas-a39-private-trig-pythagorean-proof-scope-feasibility-packet"
SOURCE_DIRECTION_ID = "trig_pythagorean_unit_identity_direction"
SELECTED_PROOF_SCOPE_ID = "prefer_pure_real_trig_statement_for_future_theorem_lookup_gate"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A40 private trig pythagorean theorem-lookup gate"

TRUE_CLAIM_FLAGS = {
    "atlas_a38_consumed",
    "proof_scope_feasibility_packet_created",
    "candidate_scope_reviewed",
    "pure_trig_scope_recommended",
    "eml_companion_deferred",
    "blockers_recorded",
    "candidate_validity_blocked",
    "theorem_lookup_gate_recommended",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "theorem_lookup_blocked",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "atlas_a38_consumed": True,
    "proof_scope_feasibility_packet_created": True,
    "candidate_scope_reviewed": True,
    "pure_trig_scope_recommended": True,
    "eml_companion_deferred": True,
    "blockers_recorded": True,
    "candidate_validity_blocked": True,
    "theorem_lookup_gate_recommended": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "theorem_lookup_blocked": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_rejected": False,
    "candidate_disproved": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_scope_finalized": False,
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
    "checked_witness_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "ATLAS-A39 is a private proof-scope feasibility packet; it recommends a future theorem-lookup gate but does not perform theorem lookup, select the candidate for proof, edit MachLib, run Lean, or claim candidate validity.",
    "ATLAS-A39 recommends narrowing future proof-scope review to the pure real trig statement first; it does not reject, disprove, prove, or formally relate any EML companion shape.",
    "ATLAS-A39 does not change runtime lowering, replace trig functions, publish or approve public copy, create SDK/compiler/course copy, touch laptop-owned repositories, or claim checked-witness status, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
]


def build_feasibility_review(source: dict[str, Any]) -> dict[str, Any]:
    candidate = source["candidatePacket"]
    return {
        "candidateId": candidate["candidateId"],
        "sourceDirectionId": candidate["sourceDirectionId"],
        "sourceScopeId": candidate["scopeId"],
        "selectedProofScopeId": SELECTED_PROOF_SCOPE_ID,
        "scopeDecision": "prefer_pure_real_trig_statement_for_future_theorem_lookup_gate",
        "recommendedFutureProofScope": {
            "statementText": candidate["statements"]["pureTrigStatement"]["statementText"],
            "guardText": candidate["guard"]["guardText"],
            "scopeStatus": "recommended_for_theorem_lookup_gate_not_selected_for_proof_not_checked",
        },
        "deferredCompanionScope": {
            "statementText": candidate["statements"]["emlCompanion"]["statementText"],
            "deferReason": "A38 explicitly deferred EML shape selection; keep any EML companion out of proof-scope review until separately selected.",
            "scopeStatus": "deferred_context_only_not_rejected_not_disproved_not_equivalence_claim",
        },
        "feasibilityReasons": [
            "The pure trig statement is concrete enough for a future theorem-lookup gate.",
            "The all-real guard is clean and avoids domain side conditions.",
            "Keeping the EML companion deferred avoids inventing a boundary shape before local notation and semantics are selected.",
        ],
        "blockersBeforeProofSelection": [
            "perform a bounded theorem-lookup gate before naming dependencies",
            "confirm whether the local import surface exposes the needed sin/cos identity facts",
            "decide whether future proof notation should remain repeated multiplication or use square notation",
            "decide whether a future MachLib attempt would be one theorem or an Atlas witness wrapper around an existing theorem",
            "keep runtime trig replacement, public copy, product, course, SDK, and broad EML claims blocked",
        ],
        "feasibilityStatus": "feasible_for_future_theorem_lookup_gate_not_proof_selection_not_validity_claim",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a38.build_payload(atlas_gate_path, machlib_root)
    a38.validate_payload(source)
    review = build_feasibility_review(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedDirectionId": source["summary"]["sourceReviewedDirectionId"],
        "sourceCandidateId": source["summary"]["candidateId"],
        "sourceSelectedScopeId": source["summary"]["selectedScopeId"],
        "proofScopeFeasibilityPacketCreated": True,
        "candidateScopeReviewed": True,
        "selectedProofScopeId": review["selectedProofScopeId"],
        "scopeDecision": review["scopeDecision"],
        "recommendedFutureProofScopeStatement": review["recommendedFutureProofScope"]["statementText"],
        "recommendedFutureProofScopeGuard": review["recommendedFutureProofScope"]["guardText"],
        "pureTrigScopeRecommended": True,
        "emlCompanionDeferred": True,
        "deferredCompanionStatement": review["deferredCompanionScope"]["statementText"],
        "deferredCompanionStatus": review["deferredCompanionScope"]["scopeStatus"],
        "blockersRecorded": True,
        "blockerCount": len(review["blockersBeforeProofSelection"]),
        "feasibilityStatus": review["feasibilityStatus"],
        "candidateSelectedForProof": False,
        "candidateValidityBlocked": True,
        "candidateValidityClaim": False,
        "candidateRejected": False,
        "candidateDisproved": False,
        "candidateProved": False,
        "proofScopeFinalized": False,
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
        "checkedWitnessClaim": False,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_trig_pythagorean_proof_scope_feasibility_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceCandidatePacket": source["candidatePacket"],
            "proofScopeFeasibilityReview": review,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    review = payload["proofScopeFeasibilityReview"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(review["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a38-private-scoped-trig-pythagorean-candidate-packet":
        raise ValueError("ATLAS-A39 must consume ATLAS-A38")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A39 must consume trig direction")
    if summary["selectedProofScopeId"] != SELECTED_PROOF_SCOPE_ID:
        raise ValueError("proof scope selection drift")
    if summary["recommendedFutureProofScopeStatement"] != "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1":
        raise ValueError("future proof scope statement drift")
    if summary["recommendedFutureProofScopeGuard"] != "all real x":
        raise ValueError("future proof guard drift")
    if summary["deferredCompanionStatement"] != "deferred_no_eml_shape_selected":
        raise ValueError("deferred companion drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["blockerCount"] != 5:
        raise ValueError("expected five blockers")
    if summary["atlasRowCount"] != 14:
        raise ValueError("expected fourteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 1:
        raise ValueError("expected one additional artifact for lower bound")
    for key in [
        "proofScopeFeasibilityPacketCreated",
        "candidateScopeReviewed",
        "pureTrigScopeRecommended",
        "emlCompanionDeferred",
        "blockersRecorded",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "theoremLookupBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "candidateSelectedForProof",
        "candidateValidityClaim",
        "candidateRejected",
        "candidateDisproved",
        "candidateProved",
        "proofScopeFinalized",
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
        "checkedWitnessClaim",
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
        artifact_type="private_trig_pythagorean_proof_scope_feasibility_packet",
        semantic_strength="private_proof_scope_feasibility_recommends_theorem_lookup_gate_no_lookup_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet/atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A40 as a private trig pythagorean theorem-lookup gate; do not start proof work, edit MachLib, run Lean, or claim validity from A39.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "sourceCandidateId": payload["summary"]["sourceCandidateId"],
            "selectedProofScopeId": payload["summary"]["selectedProofScopeId"],
            "recommendedFutureProofScopeStatement": payload["summary"]["recommendedFutureProofScopeStatement"],
            "deferredCompanionStatement": payload["summary"]["deferredCompanionStatement"],
            "candidateSelectedForProof": payload["summary"]["candidateSelectedForProof"],
            "theoremLookupPerformed": payload["summary"]["theoremLookupPerformed"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["proofScopeFeasibilityReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("source candidate", payload["summary"]["sourceCandidateId"]),
        ("selected proof scope", payload["summary"]["selectedProofScopeId"]),
        ("recommended future proof statement", payload["summary"]["recommendedFutureProofScopeStatement"]),
        ("recommended future proof guard", payload["summary"]["recommendedFutureProofScopeGuard"]),
        ("deferred companion", payload["summary"]["deferredCompanionStatement"]),
        ("candidate selected for proof", payload["summary"]["candidateSelectedForProof"]),
        ("theorem lookup performed", payload["summary"]["theoremLookupPerformed"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    reason_lines = [f"- {item}" for item in review["feasibilityReasons"]]
    blocker_lines = [f"- {item}" for item in review["blockersBeforeProofSelection"]]
    scope_lines = [
        f"- recommended proof scope: `{review['recommendedFutureProofScope']['statementText']}`",
        f"- recommended scope status: `{review['recommendedFutureProofScope']['scopeStatus']}`",
        f"- deferred companion: `{review['deferredCompanionScope']['statementText']}`",
        f"- deferred companion status: `{review['deferredCompanionScope']['scopeStatus']}`",
    ]
    return render_markdown_report(
        title="ATLAS-A39 Private Trig Pythagorean Proof-Scope Feasibility Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Scope Feasibility", scope_lines),
            ("Feasibility Reasons", reason_lines),
            ("Blockers Before Proof Selection", blocker_lines),
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
    result_path = out_dir / f"atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet.json"
    feed_path = command_feed_dir / f"atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet",
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
    print("ATLAS_A39_PRIVATE_TRIG_PYTHAGOREAN_PROOF_SCOPE_FEASIBILITY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
