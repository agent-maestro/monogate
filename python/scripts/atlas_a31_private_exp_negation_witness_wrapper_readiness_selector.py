#!/usr/bin/env python3
"""ATLAS-A31 private exp-negation witness-wrapper readiness selector."""

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

from scripts import atlas_a30_private_exp_negation_theorem_lookup_gate as a30  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_exp_negation_witness_wrapper_readiness_selector.v0"
STATUS = "ATLAS_A31_PRIVATE_EXP_NEGATION_WITNESS_WRAPPER_READINESS_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a31-private-exp-negation-witness-wrapper-readiness-selector"
SOURCE_DIRECTION_ID = "exp_negation_multiplicative_identity_direction"
SELECTED_DECISION_ID = "recommend_future_private_wrapper_or_alias_attempt_gate"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A32 private exp-negation wrapper-or-alias attempt gate"

TRUE_CLAIM_FLAGS = {
    "atlas_a30_consumed",
    "witness_wrapper_readiness_selector_created",
    "lookup_result_consumed",
    "primary_observed_identifier_reviewed",
    "wrapper_or_alias_future_gate_recommended",
    "eml_companion_kept_deferred",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a30_consumed": True,
    "witness_wrapper_readiness_selector_created": True,
    "lookup_result_consumed": True,
    "primary_observed_identifier_reviewed": True,
    "wrapper_or_alias_future_gate_recommended": True,
    "eml_companion_kept_deferred": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "wrapper_attempt_started": False,
    "wrapper_attempt_completed": False,
    "alias_attempt_started": False,
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
    "ATLAS-A31 is a private readiness selector; it recommends a future wrapper-or-alias attempt gate but does not start that attempt, edit MachLib, run Lean, or claim candidate validity.",
    "ATLAS-A31 reviews `MachLib.Real.exp_mul_exp_neg` as an observed local surface; it does not claim it as an imported proof dependency, exact dependency, checked witness, or completed proof.",
    "ATLAS-A31 keeps the EML companion hint deferred and does not claim a checked EML theorem, formal equivalence, runtime exp replacement, public readiness, runtime performance, compiler correctness, or broad EML advantage.",
]


def build_readiness_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    summary = source["summary"]
    primary = source["theoremLookupReview"]["primaryObservedIdentifier"]
    common_false = dict(CLAIM_FLAGS)
    return [
        {
            "optionId": SELECTED_DECISION_ID,
            "selectionStatus": "selected_next",
            "decision": "recommend_future_wrapper_or_alias_attempt_gate_without_starting_it",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "readinessReasons": [
                "The primary observed identifier has the same pure exp multiplication statement shape.",
                "A wrapper-or-alias gate is narrower than starting an unconstrained proof attempt.",
                "The future gate can decide between wrapper theorem, alias-style theorem, or parking after checking the exact file/import surface.",
            ],
            "futureGateRequirements": [
                "choose wrapper theorem, alias-style theorem, or park outcome before editing MachLib",
                "state the exact future target file and namespace before any edit",
                "run Lean only inside the future gated attempt, not in this selector",
                "keep the EML companion deferred",
                "keep public, runtime, product, and broad EML claims blocked",
            ],
            "sourceSignals": {
                "sourceCandidateId": summary["sourceCandidateId"],
                "lookupScopeStatement": summary["lookupScopeStatement"],
                "primaryObservedIdentifier": primary["identifier"],
                "primaryObservedIdentifierFile": primary["file"],
                "primaryObservedIdentifierLineHint": primary["lineHint"],
                "primaryObservedIdentifierStatus": primary["matchStatus"],
            },
            "claimFlags": common_false,
        },
        {
            "optionId": "park_exp_negation_after_lookup",
            "selectionStatus": "available_if_reviewer_prefers_atlas_pause",
            "decision": "park_candidate_after_lookup_without_attempt",
            "nextArtifact": "Future private Atlas v0 consolidation packet",
            "readinessReasons": [
                "The candidate has a plausible local surface but Atlas consolidation may be higher leverage than another attempt gate.",
            ],
            "futureGateRequirements": [],
            "sourceSignals": None,
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "request_human_scope_review",
            "selectionStatus": "available_if_dependency_claim_wording_needs_review",
            "decision": "pause_before_attempt_gate_for_human_scope_review",
            "nextArtifact": "Future private exp-negation scope wording review",
            "readinessReasons": [
                "A reviewer may want to inspect whether observed identifier wording is too close to a dependency claim.",
            ],
            "futureGateRequirements": [],
            "sourceSignals": None,
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a30.build_payload(atlas_gate_path, machlib_root)
    a30.validate_payload(source)
    options = build_readiness_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_DECISION_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedDirectionId": source["summary"]["sourceReviewedDirectionId"],
        "sourceCandidateId": source["summary"]["sourceCandidateId"],
        "lookupResultConsumed": True,
        "witnessWrapperReadinessSelectorCreated": True,
        "selectedDecisionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "wrapperOrAliasFutureGateRecommended": True,
        "primaryObservedIdentifierReviewed": True,
        "primaryObservedIdentifier": source["summary"]["primaryObservedIdentifier"],
        "primaryObservedIdentifierFile": source["summary"]["primaryObservedIdentifierFile"],
        "primaryObservedIdentifierLineHint": source["summary"]["primaryObservedIdentifierLineHint"],
        "lookupScopeStatement": source["summary"]["lookupScopeStatement"],
        "lookupScopeGuard": source["summary"]["lookupScopeGuard"],
        "emlCompanionKeptDeferred": True,
        "deferredCompanionStatement": source["summary"]["deferredCompanionStatement"],
        "wrapperAttemptStarted": False,
        "wrapperAttemptCompleted": False,
        "aliasAttemptStarted": False,
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
        artifact_type="private_exp_negation_witness_wrapper_readiness_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceTheoremLookupReview": source["theoremLookupReview"],
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
    if payload["sourceArtifact"] != "atlas-a30-private-exp-negation-theorem-lookup-gate":
        raise ValueError("ATLAS-A31 must consume ATLAS-A30")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A31 must consume exp-negation direction")
    if summary["selectedDecisionId"] != SELECTED_DECISION_ID:
        raise ValueError("selected decision drift")
    if summary["primaryObservedIdentifier"] != "MachLib.Real.exp_mul_exp_neg":
        raise ValueError("primary observed identifier drift")
    if summary["lookupScopeStatement"] != "forall x : Real, Real.exp x * Real.exp (-x) = 1":
        raise ValueError("lookup statement drift")
    if summary["lookupScopeGuard"] != "all real x":
        raise ValueError("lookup guard drift")
    if summary["deferredCompanionStatement"] != "eml (x + (-x)) 1 = 1":
        raise ValueError("deferred companion drift")
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
        "lookupResultConsumed",
        "witnessWrapperReadinessSelectorCreated",
        "wrapperOrAliasFutureGateRecommended",
        "primaryObservedIdentifierReviewed",
        "emlCompanionKeptDeferred",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "wrapperAttemptStarted",
        "wrapperAttemptCompleted",
        "aliasAttemptStarted",
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
        artifact_type="private_exp_negation_witness_wrapper_readiness_selector",
        semantic_strength="private_selector_recommends_future_wrapper_or_alias_gate_no_attempt_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a31_private_exp_negation_witness_wrapper_readiness_selector/atlas_a31_private_exp_negation_witness_wrapper_readiness_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a31_private_exp_negation_witness_wrapper_readiness_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A32 as a private exp-negation wrapper-or-alias attempt gate; do not edit MachLib, run Lean, or claim validity from A31.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "sourceCandidateId": payload["summary"]["sourceCandidateId"],
            "selectedDecisionId": payload["summary"]["selectedDecisionId"],
            "primaryObservedIdentifier": payload["summary"]["primaryObservedIdentifier"],
            "wrapperAttemptStarted": payload["summary"]["wrapperAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "observedIdentifierClaimedAsDependency": payload["summary"]["observedIdentifierClaimedAsDependency"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    selected = payload["selectedOption"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("source candidate", payload["summary"]["sourceCandidateId"]),
        ("selected decision", payload["summary"]["selectedDecisionId"]),
        ("primary observed identifier", payload["summary"]["primaryObservedIdentifier"]),
        ("lookup scope", payload["summary"]["lookupScopeStatement"]),
        ("wrapper attempt started", payload["summary"]["wrapperAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("observed identifier claimed as dependency", payload["summary"]["observedIdentifierClaimedAsDependency"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    reason_lines = [f"- {item}" for item in selected["readinessReasons"]]
    requirement_lines = [f"- {item}" for item in selected["futureGateRequirements"]]
    option_lines = ["| Option | Status | Decision |", "|---|---|---|"]
    for option in payload["options"]:
        option_lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | `{option['decision']}` |"
        )
    return render_markdown_report(
        title="ATLAS-A31 Private Exp-Negation Witness-Wrapper Readiness Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Readiness Reasons", reason_lines),
            ("Future Gate Requirements", requirement_lines),
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
    result_path = out_dir / f"atlas_a31_private_exp_negation_witness_wrapper_readiness_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a31_private_exp_negation_witness_wrapper_readiness_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a31_private_exp_negation_witness_wrapper_readiness_selector.json"
    feed_path = command_feed_dir / f"atlas_a31_private_exp_negation_witness_wrapper_readiness_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a31_private_exp_negation_witness_wrapper_readiness_selector",
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
    print("ATLAS_A31_PRIVATE_EXP_NEGATION_WITNESS_WRAPPER_READINESS_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
