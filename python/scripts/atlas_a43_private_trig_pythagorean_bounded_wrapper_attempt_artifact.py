#!/usr/bin/env python3
"""ATLAS-A43 private trig pythagorean bounded wrapper attempt artifact."""

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

from scripts import atlas_a42_private_trig_pythagorean_wrapper_or_alias_attempt_gate as a42  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_trig_pythagorean_bounded_wrapper_attempt_artifact.v0"
STATUS = "ATLAS_A43_PRIVATE_TRIG_PYTHAGOREAN_BOUNDED_WRAPPER_ATTEMPT_ARTIFACT_PASS"
ARTIFACT_ID = "atlas-a43-private-trig-pythagorean-bounded-wrapper-attempt-artifact"
SOURCE_DIRECTION_ID = "trig_pythagorean_unit_identity_direction"
MACHLIB_NAME = "MachLib.Real.trig_pythagorean_unit_identity_witness"
MACHLIB_FILE = "foundations/MachLib/EMLAtlasWitness.lean"
DEPENDENCY_IDENTIFIER = "MachLib.Real.sin_sq_add_cos_sq"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A44 private trig pythagorean checked-wrapper surface review"

TRUE_CLAIM_FLAGS = {
    "atlas_a42_consumed",
    "bounded_wrapper_attempt_artifact_created",
    "wrapper_attempt_started",
    "wrapper_attempt_completed",
    "machlib_file_changed",
    "lean_typecheck_performed",
    "lean_typecheck_passed",
    "candidate_proved",
    "candidate_proved_this_phase",
    "checked_wrapper_witness_recorded",
    "dependency_identifier_used",
    "exact_theorem_names_claimed",
    "eml_companion_kept_deferred",
    "public_promotion_blocked",
    "runtime_claims_blocked",
    "d109_hold_respected",
    "target_lower_bound_reached_observed",
}

CLAIM_FLAGS = {
    "atlas_a42_consumed": True,
    "bounded_wrapper_attempt_artifact_created": True,
    "wrapper_attempt_started": True,
    "wrapper_attempt_completed": True,
    "machlib_file_changed": True,
    "lean_typecheck_performed": True,
    "lean_typecheck_passed": True,
    "candidate_proved": True,
    "candidate_proved_this_phase": True,
    "checked_wrapper_witness_recorded": True,
    "dependency_identifier_used": True,
    "exact_theorem_names_claimed": True,
    "eml_companion_kept_deferred": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "d109_hold_respected": True,
    "target_lower_bound_reached_observed": True,
    "alias_attempt_started": False,
    "candidate_rejected": False,
    "candidate_disproved": False,
    "proof_scope_broadened": False,
    "additional_machlib_file_changed": False,
    "additional_lean_check_performed": False,
    "runtime_lowering_changed": False,
    "runtime_exp_replacement_claim": False,
    "runtime_trig_replacement_claim": False,
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
    "ATLAS-A43 records one private MachLib wrapper witness and one successful local Lean build; it does not claim public readiness, public copy approval, runtime replacement, compiler correctness, or broad EML advantage.",
    "ATLAS-A43 uses the local dependency `MachLib.Real.sin_sq_add_cos_sq`; it records one checked wrapper only and does not broaden the trig proof surface.",
    "ATLAS-A43 keeps the EML companion hint deferred and does not claim a checked EML-shaped theorem, formal equivalence to EML semantics, product readiness, SDK/course material, or electronics/laptop artifact consumption.",
]


def build_checked_wrapper(source: dict[str, Any]) -> dict[str, Any]:
    summary = source["summary"]
    return {
        "machlibName": MACHLIB_NAME,
        "machlibFile": MACHLIB_FILE,
        "namespace": summary["targetNamespace"],
        "checkedStatement": summary["proposedStatement"],
        "dependencyIdentifier": DEPENDENCY_IDENTIFIER,
        "proofShape": [
            "import MachLib.Trig",
            "add wrapper theorem in foundations/MachLib/EMLAtlasWitness.lean",
            "close wrapper with MachLib.Real.sin_sq_add_cos_sq x",
        ],
        "buildCommand": "cd foundations && lake build",
        "buildStatus": "passed",
        "knownUnrelatedWarnings": [
            "MachLib.ForgeTest declaration uses sorry",
            "MachLib.HighDimensional declaration uses sorry at line 377",
            "MachLib.HighDimensional declaration uses sorry at line 394",
        ],
        "attemptBounds": {
            "allowedFiles": [MACHLIB_FILE],
            "changedFiles": [MACHLIB_FILE],
            "leanCheckCount": 1,
            "proofScopeBroadened": False,
        },
        "emlCompanionStatus": "deferred_not_checked_not_formal_equivalence_claim",
        "runtimeControl": "standard_trig_functions_remain_runtime_controls",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a42.build_payload(atlas_gate_path, machlib_root)
    a42.validate_payload(source)
    checked = build_checked_wrapper(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceReviewedDirectionId": source["summary"]["sourceReviewedDirectionId"],
        "sourceCandidateId": source["summary"]["sourceCandidateId"],
        "sourceTargetFile": source["summary"]["targetFile"],
        "sourceTargetNamespace": source["summary"]["targetNamespace"],
        "sourceProposedWitnessName": source["summary"]["proposedWitnessName"],
        "boundedWrapperAttemptArtifactCreated": True,
        "wrapperAttemptStarted": True,
        "wrapperAttemptCompleted": True,
        "aliasAttemptStarted": False,
        "machlibName": checked["machlibName"],
        "machlibFile": checked["machlibFile"],
        "checkedStatement": checked["checkedStatement"],
        "dependencyIdentifier": checked["dependencyIdentifier"],
        "dependencyIdentifierUsed": True,
        "namespaceCorrectionRecorded": True,
        "machlibFileChanged": True,
        "additionalMachlibFileChanged": False,
        "leanTypecheckPerformed": True,
        "leanTypecheckPassed": True,
        "additionalLeanCheckPerformed": False,
        "candidateProved": True,
        "candidateProvedThisPhase": True,
        "checkedWrapperWitnessRecorded": True,
        "exactTheoremNamesClaimed": True,
        "candidateRejected": False,
        "candidateDisproved": False,
        "proofScopeBroadened": False,
        "emlCompanionKeptDeferred": True,
        "deferredCompanionStatement": source["summary"]["deferredCompanionStatement"],
        "runtimeControl": checked["runtimeControl"],
        "runtimeLoweringChanged": False,
        "runtimeExpReplacementClaim": False,
        "runtimeTrigReplacementClaim": False,
        "runtimeSqrtReplacementClaim": False,
        "runtimeReciprocalReplacementClaim": False,
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "atlasRowCount": source["summary"]["atlasRowCount"] + 1,
        "sourceAtlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": (source["summary"]["atlasRowCount"] + 1) >= source["summary"]["targetMin"],
        "targetLowerBoundReachedObserved": (source["summary"]["atlasRowCount"] + 1) >= source["summary"]["targetMin"],
        "additionalArtifactsNeededForLowerBound": max(
            0, source["summary"]["targetMin"] - (source["summary"]["atlasRowCount"] + 1)
        ),
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
        artifact_type="private_trig_pythagorean_bounded_wrapper_attempt_artifact",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAttemptGate": source["wrapperOrAliasAttemptGate"],
            "checkedWrapperWitness": checked,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    checked = payload["checkedWrapperWitness"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(checked["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a42-private-trig-pythagorean-wrapper-or-alias-attempt-gate":
        raise ValueError("ATLAS-A43 must consume ATLAS-A42")
    if summary["sourceReviewedDirectionId"] != SOURCE_DIRECTION_ID:
        raise ValueError("A43 must consume trig pythagorean direction")
    if summary["machlibName"] != MACHLIB_NAME:
        raise ValueError("MachLib name drift")
    if summary["machlibFile"] != MACHLIB_FILE:
        raise ValueError("MachLib file drift")
    if summary["checkedStatement"] != "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1":
        raise ValueError("checked statement drift")
    if summary["dependencyIdentifier"] != DEPENDENCY_IDENTIFIER:
        raise ValueError("dependency identifier drift")
    if summary["deferredCompanionStatement"] != "deferred_no_eml_shape_selected":
        raise ValueError("deferred companion drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["sourceAtlasRowCount"] != 14 or summary["atlasRowCount"] != 15:
        raise ValueError("Atlas row accounting drift")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not True:
        raise ValueError("target lower bound should now be reached")
    if summary["targetLowerBoundReachedObserved"] is not True:
        raise ValueError("target lower bound observation should be true")
    if summary["additionalArtifactsNeededForLowerBound"] != 0:
        raise ValueError("expected no additional artifact for lower bound")
    for key in [
        "boundedWrapperAttemptArtifactCreated",
        "wrapperAttemptStarted",
        "wrapperAttemptCompleted",
        "dependencyIdentifierUsed",
        "namespaceCorrectionRecorded",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "leanTypecheckPassed",
        "candidateProved",
        "candidateProvedThisPhase",
        "checkedWrapperWitnessRecorded",
        "exactTheoremNamesClaimed",
        "emlCompanionKeptDeferred",
        "d109HoldRespected",
        "targetLowerBoundReachedObserved",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "aliasAttemptStarted",
        "additionalMachlibFileChanged",
        "additionalLeanCheckPerformed",
        "candidateRejected",
        "candidateDisproved",
        "proofScopeBroadened",
        "runtimeLoweringChanged",
        "runtimeExpReplacementClaim",
        "runtimeTrigReplacementClaim",
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
        artifact_type="private_trig_pythagorean_bounded_wrapper_attempt_artifact",
        semantic_strength="private_checked_wrapper_witness_one_file_one_lean_build_public_runtime_product_claims_blocked",
        source=f"python/results/atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact/atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A44 as a private checked-wrapper surface review; keep public, runtime, product, and EML-companion claims blocked.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "machlibName": payload["summary"]["machlibName"],
            "machlibFile": payload["summary"]["machlibFile"],
            "dependencyIdentifier": payload["summary"]["dependencyIdentifier"],
            "leanTypecheckPassed": payload["summary"]["leanTypecheckPassed"],
            "candidateProvedThisPhase": payload["summary"]["candidateProvedThisPhase"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "runtimeExpReplacementClaim": payload["summary"]["runtimeExpReplacementClaim"],
            "runtimeTrigReplacementClaim": payload["summary"]["runtimeTrigReplacementClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    checked = payload["checkedWrapperWitness"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("MachLib name", payload["summary"]["machlibName"]),
        ("MachLib file", payload["summary"]["machlibFile"]),
        ("checked statement", payload["summary"]["checkedStatement"]),
        ("dependency identifier", payload["summary"]["dependencyIdentifier"]),
        ("Lean typecheck passed", payload["summary"]["leanTypecheckPassed"]),
        ("candidate proved this phase", payload["summary"]["candidateProvedThisPhase"]),
        ("EML companion deferred", payload["summary"]["emlCompanionKeptDeferred"]),
        ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ("runtime exp replacement claim", payload["summary"]["runtimeExpReplacementClaim"]),
        ("runtime trig replacement claim", payload["summary"]["runtimeTrigReplacementClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    proof_lines = [f"- {item}" for item in checked["proofShape"]]
    warning_lines = [f"- {item}" for item in checked["knownUnrelatedWarnings"]]
    bound_lines = [
        f"- allowed files: `{', '.join(checked['attemptBounds']['allowedFiles'])}`",
        f"- changed files: `{', '.join(checked['attemptBounds']['changedFiles'])}`",
        f"- Lean check count: `{checked['attemptBounds']['leanCheckCount']}`",
        f"- proof scope broadened: `{checked['attemptBounds']['proofScopeBroadened']}`",
    ]
    return render_markdown_report(
        title="ATLAS-A43 Private Trig Pythagorean Bounded Wrapper Attempt Artifact",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Proof Shape", proof_lines),
            ("Attempt Bounds", bound_lines),
            ("Known Unrelated Build Warnings", warning_lines),
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
    result_path = out_dir / f"atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact_{STAMP}.json"
    report_path = report_dir / f"atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact.json"
    feed_path = command_feed_dir / f"atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact",
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
    print("ATLAS_A43_PRIVATE_TRIG_PYTHAGOREAN_BOUNDED_WRAPPER_ATTEMPT_ARTIFACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
