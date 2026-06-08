#!/usr/bin/env python3
"""ATLAS-A28 private scoped exp-negation candidate packet."""

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

from scripts import atlas_a27_private_exp_negation_candidate_packet_selector as a27  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_scoped_exp_negation_candidate_packet.v0"
STATUS = "ATLAS_A28_PRIVATE_SCOPED_EXP_NEGATION_CANDIDATE_PACKET_PASS"
ARTIFACT_ID = "atlas-a28-private-scoped-exp-negation-candidate-packet"
SOURCE_DIRECTION_ID = "exp_negation_multiplicative_identity_direction"
SELECTED_SCOPE_ID = "paired_pure_exp_with_eml_companion_hint"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A29 private exp-negation proof-scope feasibility packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a27_consumed",
    "candidate_packet_created",
    "candidate_scope_selected",
    "paired_scope_recorded",
    "pure_candidate_statement_recorded",
    "eml_companion_hint_recorded",
    "all_real_guard_recorded",
    "candidate_validity_blocked",
    "proof_scope_feasibility_recommended",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a27_consumed": True,
    "candidate_packet_created": True,
    "candidate_scope_selected": True,
    "paired_scope_recorded": True,
    "pure_candidate_statement_recorded": True,
    "eml_companion_hint_recorded": True,
    "all_real_guard_recorded": True,
    "candidate_validity_blocked": True,
    "proof_scope_feasibility_recommended": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_rejected": False,
    "candidate_disproved": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_scope_feasibility_performed": False,
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
    "checked_witness_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "ATLAS-A28 creates a private scoped candidate packet for review; it does not select the candidate for proof, prove it, edit MachLib, run Lean, or claim candidate validity.",
    "ATLAS-A28 records a paired scope with a pure exp statement and an EML companion hint; it does not claim that the EML hint is a checked theorem or that the pair is formally equivalent.",
    "ATLAS-A28 does not perform theorem lookup, claim exact theorem names, change runtime lowering, replace exp, publish or approve public copy, create SDK/compiler/course copy, touch laptop-owned repositories, or claim checked-witness status, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
]


def build_candidate_packet(source: dict[str, Any]) -> dict[str, Any]:
    summary = source["summary"]
    return {
        "candidateId": "atlas_candidate_exp_negation_multiplicative_identity_scoped_v0",
        "sourceDirectionId": summary["sourceReviewedDirectionId"],
        "scopeId": SELECTED_SCOPE_ID,
        "scopeDecision": "record_paired_scope_for_later_proof_scope_feasibility",
        "guard": {
            "guardText": "all real x",
            "guardSource": "ATLAS-A26/A27 source guard",
            "guardStatus": "recorded_not_lean_checked_this_phase",
        },
        "statements": {
            "pureExpStatement": {
                "statementText": "forall x : Real, Real.exp x * Real.exp (-x) = 1",
                "sourceHint": summary["sourcePureShapeHint"],
                "statementRole": "primary_candidate_shape_for_future_scope_feasibility",
                "validityStatus": "not_checked_not_proved_not_selected_for_proof",
            },
            "emlCompanionHint": {
                "statementText": "eml (x + (-x)) 1 = 1",
                "sourceHint": summary["sourcePossibleEmlBoundaryHint"],
                "statementRole": "companion_hint_only_until_local_notation_and_definition_are_rechecked",
                "validityStatus": "not_checked_not_proved_not_formal_equivalence_claim",
            },
        },
        "reviewValue": [
            "Adds an exp-family Atlas candidate with a clean all-real guard.",
            "Keeps the pure exp statement separate from the EML-shaped companion hint.",
            "Creates a concrete next packet for proof-scope feasibility without starting proof work.",
        ],
        "blockersBeforeProofSelection": [
            "decide whether A29 should scope only the pure exp statement or keep a paired scope",
            "perform theorem lookup before naming any Lean theorem dependency",
            "check exact local notation and import surface before any MachLib edit",
            "keep runtime exp replacement, public copy, product, and broad EML claims blocked",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a27.build_payload(atlas_gate_path, machlib_root)
    a27.validate_payload(source)
    candidate = build_candidate_packet(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedDirectionId": source["summary"]["sourceReviewedDirectionId"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "sourceSelectedDecision": source["summary"]["selectedDecision"],
        "candidatePacketCreated": True,
        "candidateId": candidate["candidateId"],
        "selectedScopeId": candidate["scopeId"],
        "scopeDecision": candidate["scopeDecision"],
        "pairedScopeRecorded": True,
        "guard": candidate["guard"]["guardText"],
        "allRealGuardRecorded": True,
        "pureCandidateStatementRecorded": True,
        "pureCandidateStatement": candidate["statements"]["pureExpStatement"]["statementText"],
        "pureCandidateValidityStatus": candidate["statements"]["pureExpStatement"]["validityStatus"],
        "emlCompanionHintRecorded": True,
        "emlCompanionHint": candidate["statements"]["emlCompanionHint"]["statementText"],
        "emlCompanionValidityStatus": candidate["statements"]["emlCompanionHint"]["validityStatus"],
        "candidateSelectedForProof": False,
        "candidateValidityBlocked": True,
        "candidateValidityClaim": False,
        "candidateRejected": False,
        "candidateDisproved": False,
        "candidateProved": False,
        "proofScopeFeasibilityPerformed": False,
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
        "checkedWitnessClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_scoped_exp_negation_candidate_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceSelector": source["selectedOption"],
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
    if payload["sourceArtifact"] != "atlas-a27-private-exp-negation-candidate-packet-selector":
        raise ValueError("ATLAS-A28 must consume ATLAS-A27")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A28 must consume exp-negation direction")
    if summary["selectedScopeId"] != SELECTED_SCOPE_ID:
        raise ValueError("scope selection drift")
    if summary["guard"] != "all real x":
        raise ValueError("guard drift")
    if summary["pureCandidateStatement"] != "forall x : Real, Real.exp x * Real.exp (-x) = 1":
        raise ValueError("pure statement drift")
    if summary["emlCompanionHint"] != "eml (x + (-x)) 1 = 1":
        raise ValueError("EML companion drift")
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
        "candidatePacketCreated",
        "pairedScopeRecorded",
        "allRealGuardRecorded",
        "pureCandidateStatementRecorded",
        "emlCompanionHintRecorded",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "candidateSelectedForProof",
        "candidateValidityClaim",
        "candidateRejected",
        "candidateDisproved",
        "candidateProved",
        "proofScopeFeasibilityPerformed",
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
        artifact_type="private_scoped_exp_negation_candidate_packet",
        semantic_strength="private_scoped_candidate_packet_no_proof_selection_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a28_private_scoped_exp_negation_candidate_packet/atlas_a28_private_scoped_exp_negation_candidate_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a28_private_scoped_exp_negation_candidate_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A29 as a private exp-negation proof-scope feasibility packet; do not start proof work or claim validity from A28.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "selectedScopeId": payload["summary"]["selectedScopeId"],
            "guard": payload["summary"]["guard"],
            "pureCandidateStatement": payload["summary"]["pureCandidateStatement"],
            "emlCompanionHint": payload["summary"]["emlCompanionHint"],
            "candidateSelectedForProof": payload["summary"]["candidateSelectedForProof"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    candidate = payload["candidatePacket"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("selected scope", payload["summary"]["selectedScopeId"]),
        ("guard", payload["summary"]["guard"]),
        ("pure candidate statement", payload["summary"]["pureCandidateStatement"]),
        ("EML companion hint", payload["summary"]["emlCompanionHint"]),
        ("candidate selected for proof", payload["summary"]["candidateSelectedForProof"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    value_lines = [f"- {item}" for item in candidate["reviewValue"]]
    blocker_lines = [f"- {item}" for item in candidate["blockersBeforeProofSelection"]]
    statement_lines = [
        f"- pure exp statement: `{candidate['statements']['pureExpStatement']['statementText']}`",
        f"- pure exp status: `{candidate['statements']['pureExpStatement']['validityStatus']}`",
        f"- EML companion hint: `{candidate['statements']['emlCompanionHint']['statementText']}`",
        f"- EML companion status: `{candidate['statements']['emlCompanionHint']['validityStatus']}`",
    ]
    return render_markdown_report(
        title="ATLAS-A28 Private Scoped Exp-Negation Candidate Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Candidate Statements", statement_lines),
            ("Review Value", value_lines),
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
    result_path = out_dir / f"atlas_a28_private_scoped_exp_negation_candidate_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a28_private_scoped_exp_negation_candidate_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a28_private_scoped_exp_negation_candidate_packet.json"
    feed_path = command_feed_dir / f"atlas_a28_private_scoped_exp_negation_candidate_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a28_private_scoped_exp_negation_candidate_packet",
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
    print("ATLAS_A28_PRIVATE_SCOPED_EXP_NEGATION_CANDIDATE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
