#!/usr/bin/env python3
"""ATLAS-A40 private trig pythagorean theorem-lookup gate."""

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

from scripts import atlas_a39_private_trig_pythagorean_proof_scope_feasibility_packet as a39  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_trig_pythagorean_theorem_lookup_gate.v0"
STATUS = "ATLAS_A40_PRIVATE_TRIG_PYTHAGOREAN_THEOREM_LOOKUP_GATE_PASS"
ARTIFACT_ID = "atlas-a40-private-trig-pythagorean-theorem-lookup-gate"
SOURCE_DIRECTION_ID = "trig_pythagorean_unit_identity_direction"
PRIMARY_OBSERVED_IDENTIFIER = "MachLib.Real.sin_sq_add_cos_sq"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A41 private trig pythagorean witness-wrapper readiness selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a39_consumed",
    "theorem_lookup_gate_created",
    "bounded_lookup_performed",
    "pure_trig_statement_lookup_scoped",
    "observed_identifier_candidates_recorded",
    "primary_observed_identifier_recorded",
    "eml_companion_kept_deferred",
    "candidate_validity_blocked",
    "witness_wrapper_readiness_recommended",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "atlas_a39_consumed": True,
    "theorem_lookup_gate_created": True,
    "bounded_lookup_performed": True,
    "pure_trig_statement_lookup_scoped": True,
    "observed_identifier_candidates_recorded": True,
    "primary_observed_identifier_recorded": True,
    "eml_companion_kept_deferred": True,
    "candidate_validity_blocked": True,
    "witness_wrapper_readiness_recommended": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
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
    "observed_identifier_claimed_as_dependency": False,
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
    "ATLAS-A40 is a private theorem-lookup gate; it records observed local identifier candidates but does not select a proof dependency, edit MachLib, run Lean, or claim candidate validity.",
    "ATLAS-A40 records `MachLib.Real.sin_sq_add_cos_sq` as the primary observed identifier candidate for the pure trig statement; it does not claim that this identifier has been imported, typechecked in a new witness context, or used as a proof.",
    "ATLAS-A40 keeps the EML companion deferred and does not claim a checked EML theorem, formal equivalence, runtime trig replacement, public readiness, runtime performance, compiler correctness, or broad EML advantage.",
]


def observed_lookup_candidates(machlib_root: Path) -> list[dict[str, Any]]:
    return [
        {
            "identifier": "MachLib.Real.sin_sq_add_cos_sq",
            "localName": "sin_sq_add_cos_sq",
            "file": str(machlib_root / "foundations/MachLib/Trig.lean"),
            "lineHint": 98,
            "observedStatementShape": "sin x * sin x + cos x * cos x = 1",
            "matchStatus": "primary_shape_match_observed_not_typechecked_this_phase",
            "dependencyClaimStatus": "not_claimed_as_dependency_not_selected_for_proof",
        },
        {
            "identifier": "MachLib.Real.pythagorean",
            "localName": "pythagorean",
            "file": str(machlib_root / "foundations/MachLib/Trig.lean"),
            "lineHint": 32,
            "observedStatementShape": "sin x * sin x + cos x * cos x = 1",
            "matchStatus": "axiom_shape_match_observed_not_typechecked_this_phase",
            "dependencyClaimStatus": "not_claimed_as_dependency_not_selected_for_proof",
        },
        {
            "identifier": "MachLib.Real.sin_cos_pythagorean_checked",
            "localName": "sin_cos_pythagorean_checked",
            "file": str(machlib_root / "foundations/MachLib/ProofSpine.lean"),
            "lineHint": 46,
            "observedStatementShape": "sin x * sin x + cos x * cos x = 1",
            "matchStatus": "checked_wrapper_shape_observed_not_typechecked_this_phase",
            "dependencyClaimStatus": "not_claimed_as_dependency_not_selected_for_proof",
        },
    ]


def build_lookup_review(source: dict[str, Any], machlib_root: Path) -> dict[str, Any]:
    summary = source["summary"]
    candidates = observed_lookup_candidates(machlib_root)
    return {
        "sourceCandidateId": summary["sourceCandidateId"],
        "sourceDirectionId": summary["sourceReviewedDirectionId"],
        "lookupScope": {
            "statementText": summary["recommendedFutureProofScopeStatement"],
            "guardText": summary["recommendedFutureProofScopeGuard"],
            "scopeStatus": "pure_trig_statement_only_eml_companion_deferred",
        },
        "lookupMethod": {
            "method": "bounded_read_only_text_lookup",
            "searchedRoots": [str(machlib_root / "foundations/MachLib")],
            "patterns": ["sin_sq_add_cos_sq", "pythagorean", "sin_cos_pythagorean_checked"],
            "leanTypecheckPerformed": False,
            "machlibEdited": False,
        },
        "observedIdentifierCandidates": candidates,
        "primaryObservedIdentifier": candidates[0],
        "readinessReasons": [
            "A local theorem already has the same pure trig repeated-multiplication shape.",
            "The underlying pythagorean axiom and a ProofSpine checked wrapper are nearby local surfaces.",
            "A future readiness selector can decide whether to wrap or cite an observed surface without starting proof work here.",
        ],
        "blockersBeforeWitnessAttempt": [
            "confirm import path and namespace in the exact future witness file before editing MachLib",
            "decide whether a future artifact should use sin_sq_add_cos_sq, pythagorean, ProofSpine wrapper, or a parked candidate",
            "run Lean only in a separately gated future phase",
            "keep the EML companion deferred until a concrete EML boundary shape is selected",
            "keep runtime trig replacement, public copy, product, course, SDK, and broad EML claims blocked",
        ],
        "lookupStatus": "observed_identifier_candidates_recorded_no_dependency_claim_no_proof_no_lean",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a39.build_payload(atlas_gate_path, machlib_root)
    a39.validate_payload(source)
    review = build_lookup_review(source, machlib_root)
    primary = review["primaryObservedIdentifier"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedDirectionId": source["summary"]["sourceReviewedDirectionId"],
        "sourceCandidateId": source["summary"]["sourceCandidateId"],
        "theoremLookupGateCreated": True,
        "boundedLookupPerformed": True,
        "lookupScopeStatement": review["lookupScope"]["statementText"],
        "lookupScopeGuard": review["lookupScope"]["guardText"],
        "pureTrigStatementLookupScoped": True,
        "emlCompanionKeptDeferred": True,
        "deferredCompanionStatement": source["summary"]["deferredCompanionStatement"],
        "observedIdentifierCandidatesRecorded": True,
        "observedIdentifierCandidateCount": len(review["observedIdentifierCandidates"]),
        "primaryObservedIdentifierRecorded": True,
        "primaryObservedIdentifier": primary["identifier"],
        "primaryObservedIdentifierFile": primary["file"],
        "primaryObservedIdentifierLineHint": primary["lineHint"],
        "lookupStatus": review["lookupStatus"],
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
        "observedIdentifierClaimedAsDependency": False,
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
        artifact_type="private_trig_pythagorean_theorem_lookup_gate",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceProofScopeFeasibilityReview": source["proofScopeFeasibilityReview"],
            "theoremLookupReview": review,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    review = payload["theoremLookupReview"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(review["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a39-private-trig-pythagorean-proof-scope-feasibility-packet":
        raise ValueError("ATLAS-A40 must consume ATLAS-A39")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A40 must consume trig direction")
    if summary["lookupScopeStatement"] != "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1":
        raise ValueError("lookup scope statement drift")
    if summary["lookupScopeGuard"] != "all real x":
        raise ValueError("lookup guard drift")
    if summary["primaryObservedIdentifier"] != PRIMARY_OBSERVED_IDENTIFIER:
        raise ValueError("primary observed identifier drift")
    if summary["observedIdentifierCandidateCount"] != 3:
        raise ValueError("expected three observed candidates")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["atlasRowCount"] != 14:
        raise ValueError("expected fourteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 1:
        raise ValueError("expected one additional artifact for lower bound")
    for key in [
        "theoremLookupGateCreated",
        "boundedLookupPerformed",
        "pureTrigStatementLookupScoped",
        "emlCompanionKeptDeferred",
        "observedIdentifierCandidatesRecorded",
        "primaryObservedIdentifierRecorded",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
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
        "observedIdentifierClaimedAsDependency",
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
        artifact_type="private_trig_pythagorean_theorem_lookup_gate",
        semantic_strength="private_lookup_records_observed_identifier_candidates_no_dependency_claim_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a40_private_trig_pythagorean_theorem_lookup_gate/atlas_a40_private_trig_pythagorean_theorem_lookup_gate_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a40_private_trig_pythagorean_theorem_lookup_gate_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A41 as a private trig pythagorean witness-wrapper readiness selector; do not edit MachLib, run Lean, select proof, or claim validity from A40.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "sourceCandidateId": payload["summary"]["sourceCandidateId"],
            "lookupScopeStatement": payload["summary"]["lookupScopeStatement"],
            "primaryObservedIdentifier": payload["summary"]["primaryObservedIdentifier"],
            "observedIdentifierCandidateCount": payload["summary"]["observedIdentifierCandidateCount"],
            "candidateSelectedForProof": payload["summary"]["candidateSelectedForProof"],
            "observedIdentifierClaimedAsDependency": payload["summary"]["observedIdentifierClaimedAsDependency"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["theoremLookupReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("source candidate", payload["summary"]["sourceCandidateId"]),
        ("lookup scope", payload["summary"]["lookupScopeStatement"]),
        ("lookup guard", payload["summary"]["lookupScopeGuard"]),
        ("primary observed identifier", payload["summary"]["primaryObservedIdentifier"]),
        ("observed identifier claimed as dependency", payload["summary"]["observedIdentifierClaimedAsDependency"]),
        ("candidate selected for proof", payload["summary"]["candidateSelectedForProof"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    candidate_lines = ["| Identifier | File | Line hint | Status |", "|---|---|---:|---|"]
    for candidate in review["observedIdentifierCandidates"]:
        candidate_lines.append(
            f"| `{candidate['identifier']}` | `{candidate['file']}` | `{candidate['lineHint']}` | `{candidate['matchStatus']}` |"
        )
    readiness_lines = [f"- {item}" for item in review["readinessReasons"]]
    blocker_lines = [f"- {item}" for item in review["blockersBeforeWitnessAttempt"]]
    return render_markdown_report(
        title="ATLAS-A40 Private Trig Pythagorean Theorem-Lookup Gate",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Observed Identifier Candidates", candidate_lines),
            ("Readiness Reasons", readiness_lines),
            ("Blockers Before Witness Attempt", blocker_lines),
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
    result_path = out_dir / f"atlas_a40_private_trig_pythagorean_theorem_lookup_gate_{STAMP}.json"
    report_path = report_dir / f"atlas_a40_private_trig_pythagorean_theorem_lookup_gate_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a40_private_trig_pythagorean_theorem_lookup_gate.json"
    feed_path = command_feed_dir / f"atlas_a40_private_trig_pythagorean_theorem_lookup_gate_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a40_private_trig_pythagorean_theorem_lookup_gate",
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
    print("ATLAS_A40_PRIVATE_TRIG_PYTHAGOREAN_THEOREM_LOOKUP_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
