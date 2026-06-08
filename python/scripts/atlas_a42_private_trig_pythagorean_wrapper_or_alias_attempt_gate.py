#!/usr/bin/env python3
"""ATLAS-A42 private trig pythagorean wrapper-or-alias attempt gate."""

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

from scripts import atlas_a41_private_trig_pythagorean_witness_wrapper_readiness_selector as a41  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_trig_pythagorean_wrapper_or_alias_attempt_gate.v0"
STATUS = "ATLAS_A42_PRIVATE_TRIG_PYTHAGOREAN_WRAPPER_OR_ALIAS_ATTEMPT_GATE_PASS"
ARTIFACT_ID = "atlas-a42-private-trig-pythagorean-wrapper-or-alias-attempt-gate"
SOURCE_DIRECTION_ID = "trig_pythagorean_unit_identity_direction"
SELECTED_ATTEMPT_SHAPE_ID = "future_wrapper_theorem_in_eml_atlas_witness"
TARGET_FILE = "foundations/MachLib/EMLAtlasWitness.lean"
TARGET_NAMESPACE = "MachLib.Real"
PROPOSED_WITNESS_NAME = "trig_pythagorean_unit_identity_witness"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A43 private trig pythagorean bounded wrapper attempt artifact"

TRUE_CLAIM_FLAGS = {
    "atlas_a41_consumed",
    "wrapper_or_alias_attempt_gate_created",
    "attempt_shape_selected",
    "target_file_recorded",
    "target_namespace_recorded",
    "proposed_witness_name_recorded",
    "future_wrapper_attempt_recommended",
    "eml_companion_kept_deferred",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "atlas_a41_consumed": True,
    "wrapper_or_alias_attempt_gate_created": True,
    "attempt_shape_selected": True,
    "target_file_recorded": True,
    "target_namespace_recorded": True,
    "proposed_witness_name_recorded": True,
    "future_wrapper_attempt_recommended": True,
    "eml_companion_kept_deferred": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
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
    "ATLAS-A42 is a private attempt gate; it selects a future wrapper-theorem attempt shape and target file but does not start the attempt, edit MachLib, run Lean, or claim candidate validity.",
    "ATLAS-A42 records `MachLib.Real.sin_sq_add_cos_sq` as the observed local surface the future wrapper may inspect; it does not claim that identifier as an imported proof dependency, exact dependency, checked witness, or completed proof.",
    "ATLAS-A42 keeps the EML companion deferred and does not claim a checked EML theorem, formal equivalence, runtime trig replacement, public readiness, runtime performance, compiler correctness, or broad EML advantage.",
]


def build_attempt_gate(source: dict[str, Any]) -> dict[str, Any]:
    summary = source["summary"]
    return {
        "selectedAttemptShapeId": SELECTED_ATTEMPT_SHAPE_ID,
        "decision": "select_future_wrapper_theorem_attempt_without_editing_machlib",
        "target": {
            "file": TARGET_FILE,
            "namespace": TARGET_NAMESPACE,
            "proposedWitnessName": PROPOSED_WITNESS_NAME,
            "proposedStatement": summary["lookupScopeStatement"],
            "targetStatus": "recorded_for_future_attempt_not_edited_not_typechecked",
        },
        "observedSurface": {
            "identifier": summary["primaryObservedIdentifier"],
            "file": summary["primaryObservedIdentifierFile"],
            "lineHint": summary["primaryObservedIdentifierLineHint"],
            "dependencyStatus": "observed_surface_only_not_claimed_as_dependency",
        },
        "futureAttemptPlan": [
            "open only foundations/MachLib/EMLAtlasWitness.lean in the future attempt",
            "try a wrapper theorem before an alias-style theorem",
            "use the observed sin_sq_add_cos_sq surface only after import and namespace are confirmed",
            "run exactly one future Lean check if the attempt is explicitly opened",
            "abort without broadening scope if the target import or namespace is wrong",
        ],
        "blockedAlternatives": [
            "do not edit Trig.lean or ProofSpine.lean in this path",
            "do not include the EML companion hint in the first wrapper attempt",
            "do not start public copy or SDK/course documentation from this gate",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a41.build_payload(atlas_gate_path, machlib_root)
    a41.validate_payload(source)
    gate = build_attempt_gate(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedDirectionId": source["summary"]["sourceReviewedDirectionId"],
        "sourceCandidateId": source["summary"]["sourceCandidateId"],
        "wrapperOrAliasAttemptGateCreated": True,
        "attemptShapeSelected": True,
        "selectedAttemptShapeId": gate["selectedAttemptShapeId"],
        "selectedDecision": gate["decision"],
        "targetFileRecorded": True,
        "targetFile": gate["target"]["file"],
        "targetNamespaceRecorded": True,
        "targetNamespace": gate["target"]["namespace"],
        "proposedWitnessNameRecorded": True,
        "proposedWitnessName": gate["target"]["proposedWitnessName"],
        "proposedStatement": gate["target"]["proposedStatement"],
        "primaryObservedIdentifier": gate["observedSurface"]["identifier"],
        "primaryObservedIdentifierFile": gate["observedSurface"]["file"],
        "primaryObservedIdentifierLineHint": gate["observedSurface"]["lineHint"],
        "emlCompanionKeptDeferred": True,
        "deferredCompanionStatement": source["summary"]["deferredCompanionStatement"],
        "futureWrapperAttemptRecommended": True,
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
        artifact_type="private_trig_pythagorean_wrapper_or_alias_attempt_gate",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceSelectedOption": source["selectedOption"],
            "wrapperOrAliasAttemptGate": gate,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    gate = payload["wrapperOrAliasAttemptGate"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(gate["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a41-private-trig-pythagorean-witness-wrapper-readiness-selector":
        raise ValueError("ATLAS-A42 must consume ATLAS-A41")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A42 must consume trig direction")
    if summary["selectedAttemptShapeId"] != SELECTED_ATTEMPT_SHAPE_ID:
        raise ValueError("attempt shape drift")
    if summary["targetFile"] != TARGET_FILE:
        raise ValueError("target file drift")
    if summary["targetNamespace"] != TARGET_NAMESPACE:
        raise ValueError("target namespace drift")
    if summary["proposedWitnessName"] != PROPOSED_WITNESS_NAME:
        raise ValueError("witness name drift")
    if summary["proposedStatement"] != "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1":
        raise ValueError("proposed statement drift")
    if summary["primaryObservedIdentifier"] != "MachLib.Real.sin_sq_add_cos_sq":
        raise ValueError("primary observed identifier drift")
    if summary["deferredCompanionStatement"] != "deferred_no_eml_shape_selected":
        raise ValueError("deferred companion drift")
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
        "wrapperOrAliasAttemptGateCreated",
        "attemptShapeSelected",
        "targetFileRecorded",
        "targetNamespaceRecorded",
        "proposedWitnessNameRecorded",
        "emlCompanionKeptDeferred",
        "futureWrapperAttemptRecommended",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
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
        artifact_type="private_trig_pythagorean_wrapper_or_alias_attempt_gate",
        semantic_strength="private_gate_records_future_wrapper_attempt_shape_no_attempt_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate/atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A43 as a private bounded wrapper attempt artifact only if the one-file/one-Lean-check bounds remain intact.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedAttemptShapeId": payload["summary"]["selectedAttemptShapeId"],
            "targetFile": payload["summary"]["targetFile"],
            "targetNamespace": payload["summary"]["targetNamespace"],
            "proposedWitnessName": payload["summary"]["proposedWitnessName"],
            "wrapperAttemptStarted": payload["summary"]["wrapperAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    gate = payload["wrapperOrAliasAttemptGate"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("source candidate", payload["summary"]["sourceCandidateId"]),
        ("selected attempt shape", payload["summary"]["selectedAttemptShapeId"]),
        ("target file", payload["summary"]["targetFile"]),
        ("target namespace", payload["summary"]["targetNamespace"]),
        ("proposed witness name", payload["summary"]["proposedWitnessName"]),
        ("proposed statement", payload["summary"]["proposedStatement"]),
        ("wrapper attempt started", payload["summary"]["wrapperAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    plan_lines = [f"- {item}" for item in gate["futureAttemptPlan"]]
    blocked_lines = [f"- {item}" for item in gate["blockedAlternatives"]]
    target_lines = [
        f"- file: `{gate['target']['file']}`",
        f"- namespace: `{gate['target']['namespace']}`",
        f"- proposed witness: `{gate['target']['proposedWitnessName']}`",
        f"- proposed statement: `{gate['target']['proposedStatement']}`",
        f"- observed surface: `{gate['observedSurface']['identifier']}`",
        f"- observed surface status: `{gate['observedSurface']['dependencyStatus']}`",
    ]
    return render_markdown_report(
        title="ATLAS-A42 Private Trig Pythagorean Wrapper-Or-Alias Attempt Gate",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Target Shape", target_lines),
            ("Future Attempt Plan", plan_lines),
            ("Blocked Alternatives", blocked_lines),
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
    result_path = out_dir / f"atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate_{STAMP}.json"
    report_path = report_dir / f"atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate.json"
    feed_path = command_feed_dir / f"atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate",
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
    print("ATLAS_A42_PRIVATE_TRIG_PYTHAGOREAN_WRAPPER_OR_ALIAS_ATTEMPT_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
