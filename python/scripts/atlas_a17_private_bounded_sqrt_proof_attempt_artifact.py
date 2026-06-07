#!/usr/bin/env python3
"""ATLAS-A17 private bounded sqrt proof-attempt artifact."""

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

from scripts import atlas_a16_private_sqrt_proof_attempt_open_selector as a16  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_bounded_sqrt_proof_attempt_artifact.v0"
STATUS = "ATLAS_A17_PRIVATE_BOUNDED_SQRT_PROOF_ATTEMPT_ARTIFACT_BLOCKED"
ARTIFACT_ID = "atlas-a17-private-bounded-sqrt-proof-attempt-artifact"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
ATTEMPT_PACKET_ID = "sqrt_abs_normalized_nonnegative_private_scoped_attempt_packet"
BLOCKER_ID = "allowed_file_missing_in_machlib_checkout"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A18 private sqrt attempt scope correction selector"
EXPECTED_ALLOWED_FILE = "MachLib/Real.lean"
OBSERVED_WITNESS_FILE = "foundations/MachLib/EMLAtlasWitness.lean"

TRUE_CLAIM_FLAGS = {
    "atlas_a16_consumed",
    "bounded_proof_attempt_artifact_created",
    "attempt_preflight_performed",
    "allowed_file_preflight_performed",
    "allowed_file_missing_blocker_recorded",
    "attempt_aborted_before_edit",
    "scope_correction_selector_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a16_consumed": True,
    "bounded_proof_attempt_artifact_created": True,
    "attempt_preflight_performed": True,
    "allowed_file_preflight_performed": True,
    "allowed_file_missing_blocker_recorded": True,
    "attempt_aborted_before_edit": True,
    "scope_correction_selector_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
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
    "scope_corrected_this_phase": False,
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
    "ATLAS-A17 creates a private bounded attempt artifact and aborts before edit because A16's allowed file path is not present in the MachLib checkout.",
    "ATLAS-A17 performs allowed-file preflight only; it does not edit MachLib, run Lean, perform theorem lookup, claim exact theorem names, or claim the sqrt candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A17 does not silently correct the attempt scope, change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_preflight(source: dict[str, Any], machlib_root: Path) -> dict[str, Any]:
    allowed_files = source["summary"]["allowedFiles"]
    checked_files = []
    for allowed_file in allowed_files:
        path = machlib_root / allowed_file
        checked_files.append(
            {
                "allowedFile": allowed_file,
                "absolutePath": str(path),
                "exists": path.exists(),
            }
        )
    observed_path = machlib_root / OBSERVED_WITNESS_FILE
    return {
        "machlibRoot": str(machlib_root),
        "allowedFiles": allowed_files,
        "checkedAllowedFiles": checked_files,
        "allAllowedFilesExist": all(item["exists"] for item in checked_files),
        "observedLikelyWitnessFile": OBSERVED_WITNESS_FILE,
        "observedLikelyWitnessFileExists": observed_path.exists(),
        "blocker": {
            "blockerId": BLOCKER_ID,
            "status": "blocks_attempt_before_edit",
            "description": (
                "The A16 attempt scope allows MachLib/Real.lean, but that path "
                "is not present in the observed MachLib checkout."
            ),
            "whyAbortInsteadOfCorrecting": [
                "A17 is bound by the A16 allowed-file list.",
                "Changing the allowed file would be a scope correction, not the bounded attempt itself.",
                "A separate selector should decide whether to replace the stale path with the observed witness file.",
            ],
        },
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a16.build_payload(atlas_gate_path)
    a16.validate_payload(source)
    preflight = build_preflight(source, machlib_root)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "sourceAttemptPacketId": source["summary"]["sourceAttemptPacketId"],
        "candidateId": source["summary"]["candidateId"],
        "boundedProofAttemptArtifactCreated": True,
        "attemptPreflightPerformed": True,
        "allowedFilePreflightPerformed": True,
        "allowedFiles": source["summary"]["allowedFiles"],
        "allowedFilesExist": preflight["allAllowedFilesExist"],
        "allowedFileMissingBlockerRecorded": True,
        "blockerId": BLOCKER_ID,
        "attemptStatus": "blocked_before_edit_due_allowed_file_missing",
        "attemptAbortedBeforeEdit": True,
        "observedLikelyWitnessFile": preflight["observedLikelyWitnessFile"],
        "observedLikelyWitnessFileExists": preflight["observedLikelyWitnessFileExists"],
        "scopeCorrectedThisPhase": False,
        "candidateValidityBlocked": True,
        "candidateSelectedForProof": False,
        "candidateValidityClaim": False,
        "candidateProved": False,
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
        artifact_type="private_bounded_sqrt_proof_attempt_artifact",
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
            "sourceAttemptLimits": {
                "allowedFiles": source["summary"]["allowedFiles"],
                "futureAttemptWallClockLimitMinutes": source["summary"]["futureAttemptWallClockLimitMinutes"],
                "futureLeanRunLimit": source["summary"]["futureLeanRunLimit"],
                "requiredRouteStepIds": source["summary"]["requiredRouteStepIds"],
                "abortConditionCount": source["summary"]["abortConditionCount"],
            },
            "attemptPreflight": preflight,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    preflight = payload["attemptPreflight"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a16-private-sqrt-proof-attempt-open-selector":
        raise ValueError("ATLAS-A17 must consume ATLAS-A16")
    if summary["sourceSelectedOptionId"] != "recommend_future_bounded_sqrt_proof_attempt_artifact":
        raise ValueError("A17 must consume A16's bounded attempt recommendation")
    if summary["sourceAttemptPacketId"] != ATTEMPT_PACKET_ID:
        raise ValueError("attempt packet id drift")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["allowedFiles"] != [EXPECTED_ALLOWED_FILE]:
        raise ValueError("allowed file drift")
    if summary["allowedFilesExist"] is not False:
        raise ValueError("A17 expects the allowed file to be missing")
    if preflight["checkedAllowedFiles"][0]["exists"] is not False:
        raise ValueError("allowed-file preflight should record missing file")
    if summary["blockerId"] != BLOCKER_ID:
        raise ValueError("blocker id drift")
    if summary["attemptStatus"] != "blocked_before_edit_due_allowed_file_missing":
        raise ValueError("unexpected attempt status")
    if summary["observedLikelyWitnessFile"] != OBSERVED_WITNESS_FILE:
        raise ValueError("observed witness file drift")
    if summary["observedLikelyWitnessFileExists"] is not True:
        raise ValueError("expected observed witness file to exist")
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
        "boundedProofAttemptArtifactCreated",
        "attemptPreflightPerformed",
        "allowedFilePreflightPerformed",
        "allowedFileMissingBlockerRecorded",
        "attemptAbortedBeforeEdit",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "scopeCorrectedThisPhase",
        "candidateSelectedForProof",
        "candidateValidityClaim",
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
        artifact_type="private_bounded_sqrt_proof_attempt_artifact",
        semantic_strength="private_attempt_artifact_blocked_by_allowed_file_mismatch_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a17_private_bounded_sqrt_proof_attempt_artifact/atlas_a17_private_bounded_sqrt_proof_attempt_artifact_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a17_private_bounded_sqrt_proof_attempt_artifact_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A18 as a private sqrt attempt scope correction selector before any MachLib edit or Lean run.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "attemptStatus": payload["summary"]["attemptStatus"],
            "blockerId": payload["summary"]["blockerId"],
            "allowedFiles": payload["summary"]["allowedFiles"],
            "allowedFilesExist": payload["summary"]["allowedFilesExist"],
            "observedLikelyWitnessFile": payload["summary"]["observedLikelyWitnessFile"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("attempt status", payload["summary"]["attemptStatus"]),
        ("blocker id", payload["summary"]["blockerId"]),
        ("allowed files exist", payload["summary"]["allowedFilesExist"]),
        ("observed likely witness file", payload["summary"]["observedLikelyWitnessFile"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    preflight = payload["attemptPreflight"]
    preflight_lines = ["| Allowed file | Exists |", "|---|---|"]
    for item in preflight["checkedAllowedFiles"]:
        preflight_lines.append(f"| `{item['allowedFile']}` | `{item['exists']}` |")
    blocker = preflight["blocker"]
    blocker_lines = [
        f"- status: `{blocker['status']}`",
        f"- description: {blocker['description']}",
    ]
    correction_lines = [f"- {item}" for item in blocker["whyAbortInsteadOfCorrecting"]]
    return render_markdown_report(
        title="ATLAS-A17 Private Bounded Sqrt Proof-Attempt Artifact",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Allowed-File Preflight", preflight_lines),
            ("Precise Blocker", blocker_lines),
            ("Why This Aborts Instead Of Correcting Scope", correction_lines),
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
    result_path = out_dir / f"atlas_a17_private_bounded_sqrt_proof_attempt_artifact_{STAMP}.json"
    report_path = report_dir / f"atlas_a17_private_bounded_sqrt_proof_attempt_artifact_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a17_private_bounded_sqrt_proof_attempt_artifact.json"
    feed_path = command_feed_dir / f"atlas_a17_private_bounded_sqrt_proof_attempt_artifact_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a17_private_bounded_sqrt_proof_attempt_artifact",
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
    print("ATLAS_A17_PRIVATE_BOUNDED_SQRT_PROOF_ATTEMPT_ARTIFACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
