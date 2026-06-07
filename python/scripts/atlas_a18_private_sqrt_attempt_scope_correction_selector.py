#!/usr/bin/env python3
"""ATLAS-A18 private sqrt attempt scope correction selector."""

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

from scripts import atlas_a17_private_bounded_sqrt_proof_attempt_artifact as a17  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_sqrt_attempt_scope_correction_selector.v0"
STATUS = "ATLAS_A18_PRIVATE_SQRT_ATTEMPT_SCOPE_CORRECTION_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a18-private-sqrt-attempt-scope-correction-selector"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
STALE_ALLOWED_FILE = "MachLib/Real.lean"
CORRECTED_ALLOWED_FILE = "foundations/MachLib/EMLAtlasWitness.lean"
SELECTED_OPTION_ID = "approve_one_off_scope_correction_for_future_attempt"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A19 private corrected-scope sqrt proof-attempt gate"

TRUE_CLAIM_FLAGS = {
    "atlas_a17_consumed",
    "scope_correction_selector_created",
    "stale_scope_reviewed",
    "observed_witness_file_reviewed",
    "one_off_scope_correction_approved",
    "future_corrected_scope_recorded",
    "future_attempt_gate_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a17_consumed": True,
    "scope_correction_selector_created": True,
    "stale_scope_reviewed": True,
    "observed_witness_file_reviewed": True,
    "one_off_scope_correction_approved": True,
    "future_corrected_scope_recorded": True,
    "future_attempt_gate_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "corrected_scope_applied_to_machlib": False,
    "corrected_attempt_gate_created": False,
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
    "ATLAS-A18 is a private one-off scope correction selector; it approves a corrected future file scope but does not apply that correction to MachLib, edit code, run Lean, or start proof work.",
    "ATLAS-A18 records `foundations/MachLib/EMLAtlasWitness.lean` as the corrected future scope for this sqrt candidate only; it does not create a general file-scope correction policy or reusable preflight helper.",
    "ATLAS-A18 does not perform theorem lookup, claim exact theorem names, claim the sqrt candidate is true, valid, checked, Lean-ready, or provable, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, touch laptop-owned repositories, or claim public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    observed_file_exists = source["summary"]["observedLikelyWitnessFileExists"]
    return [
        {
            "optionId": SELECTED_OPTION_ID,
            "selectionStatus": "selected_next",
            "decision": "approve_corrected_future_scope_without_editing_machlib",
            "correctedScope": {
                "scopeCorrectionKind": "scope_correction_one_off_due_stale_a13_a16_file_reference",
                "staleAllowedFile": STALE_ALLOWED_FILE,
                "correctedAllowedFile": CORRECTED_ALLOWED_FILE,
                "correctedAllowedFileExists": observed_file_exists,
                "futureAllowedFiles": [CORRECTED_ALLOWED_FILE],
                "futureFileCountLimit": 1,
                "futureLeanRunLimit": 1,
                "futureAttemptWallClockLimitMinutes": 30,
            },
            "decisionCriteria": {
                "observedFileIsCurrentAtlasWitnessHome": observed_file_exists,
                "scopeUpdateReducesFutureConfusion": True,
                "zeroMachLibBehaviorChangeThisPhase": True,
                "staleScopeCreatesFutureMaintenanceCost": True,
            },
            "remainingBlocks": [
                "A18 does not edit MachLib",
                "A18 does not run Lean",
                "A18 does not perform theorem lookup",
                "candidate validity remains blocked",
                "public copy remains blocked",
            ],
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "pause_for_atlas_v0_reference_document",
            "selectionStatus": "available_if_human_prefers_consolidation",
            "decision": "pause_scope_correction_for_reference_document",
            "correctedScope": None,
            "decisionCriteria": None,
            "remainingBlocks": ["future attempt remains blocked", "public copy remains blocked"],
            "nextArtifact": "Future private EML Atlas v0 reference document",
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "optionId": "park_sqrt_candidate_due_scope_mismatch",
            "selectionStatus": "not_selected",
            "decision": "park_candidate_without_rejection",
            "correctedScope": None,
            "decisionCriteria": None,
            "remainingBlocks": ["no checked-witness claim", "target lower bound remains unreached"],
            "nextArtifact": "Park sqrt candidate after scope mismatch",
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a17.build_payload(atlas_gate_path, machlib_root)
    a17.validate_payload(source)
    options = build_options(source)
    selected = next(item for item in options if item["optionId"] == SELECTED_OPTION_ID)
    corrected_scope = selected["correctedScope"]
    criteria = selected["decisionCriteria"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceBlockerId": source["summary"]["blockerId"],
        "candidateId": source["summary"]["candidateId"],
        "scopeCorrectionSelectorCreated": True,
        "staleScopeReviewed": True,
        "observedWitnessFileReviewed": True,
        "staleAllowedFile": STALE_ALLOWED_FILE,
        "correctedAllowedFile": CORRECTED_ALLOWED_FILE,
        "correctedAllowedFileExists": corrected_scope["correctedAllowedFileExists"],
        "futureAllowedFiles": corrected_scope["futureAllowedFiles"],
        "futureFileCountLimit": corrected_scope["futureFileCountLimit"],
        "futureAttemptWallClockLimitMinutes": corrected_scope["futureAttemptWallClockLimitMinutes"],
        "futureLeanRunLimit": corrected_scope["futureLeanRunLimit"],
        "selectedOptionId": selected["optionId"],
        "selectedDecision": selected["decision"],
        "oneOffScopeCorrectionApproved": True,
        "futureCorrectedScopeRecorded": True,
        "futureAttemptGateRecommended": True,
        "correctedScopeAppliedToMachLib": False,
        "correctedAttemptGateCreated": False,
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
        artifact_type="private_sqrt_attempt_scope_correction_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceAttemptBlocker": source["attemptPreflight"]["blocker"],
            "options": options,
            "selectedOption": selected,
            "decisionCriteria": criteria,
            "correctedFutureScope": corrected_scope,
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
    if payload["sourceArtifact"] != "atlas-a17-private-bounded-sqrt-proof-attempt-artifact":
        raise ValueError("ATLAS-A18 must consume ATLAS-A17")
    if summary["sourceBlockerId"] != a17.BLOCKER_ID:
        raise ValueError("A18 must consume the A17 allowed-file blocker")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["staleAllowedFile"] != STALE_ALLOWED_FILE:
        raise ValueError("stale allowed file drift")
    if summary["correctedAllowedFile"] != CORRECTED_ALLOWED_FILE:
        raise ValueError("corrected allowed file drift")
    if summary["correctedAllowedFileExists"] is not True:
        raise ValueError("corrected file should exist")
    if summary["futureAllowedFiles"] != [CORRECTED_ALLOWED_FILE]:
        raise ValueError("future allowed files drift")
    if summary["futureFileCountLimit"] != 1:
        raise ValueError("future file count limit drift")
    if summary["futureAttemptWallClockLimitMinutes"] != 30:
        raise ValueError("future attempt budget drift")
    if summary["futureLeanRunLimit"] != 1:
        raise ValueError("future Lean run limit drift")
    if summary["selectedOptionId"] != SELECTED_OPTION_ID:
        raise ValueError("unexpected selected option")
    if summary["selectedDecision"] != "approve_corrected_future_scope_without_editing_machlib":
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
        "scopeCorrectionSelectorCreated",
        "staleScopeReviewed",
        "observedWitnessFileReviewed",
        "oneOffScopeCorrectionApproved",
        "futureCorrectedScopeRecorded",
        "futureAttemptGateRecommended",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "correctedScopeAppliedToMachLib",
        "correctedAttemptGateCreated",
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
        artifact_type="private_sqrt_attempt_scope_correction_selector",
        semantic_strength="private_one_off_scope_correction_selector_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a18_private_sqrt_attempt_scope_correction_selector/atlas_a18_private_sqrt_attempt_scope_correction_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a18_private_sqrt_attempt_scope_correction_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A19 as a corrected-scope gate before any MachLib edit or Lean run.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "selectedOptionId": payload["summary"]["selectedOptionId"],
            "staleAllowedFile": payload["summary"]["staleAllowedFile"],
            "correctedAllowedFile": payload["summary"]["correctedAllowedFile"],
            "correctedScopeAppliedToMachLib": payload["summary"]["correctedScopeAppliedToMachLib"],
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
        ("selected option", payload["summary"]["selectedOptionId"]),
        ("stale allowed file", payload["summary"]["staleAllowedFile"]),
        ("corrected allowed file", payload["summary"]["correctedAllowedFile"]),
        ("corrected file exists", payload["summary"]["correctedAllowedFileExists"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    criteria = payload["decisionCriteria"]
    criteria_lines = ["| Criterion | Result |", "|---|---|"]
    for key, value in criteria.items():
        criteria_lines.append(f"| `{key}` | `{value}` |")
    scope = payload["correctedFutureScope"]
    scope_lines = [
        f"- correction kind: `{scope['scopeCorrectionKind']}`",
        f"- future allowed files: `{', '.join(scope['futureAllowedFiles'])}`",
        f"- future file count limit: `{scope['futureFileCountLimit']}`",
        f"- future wall-clock limit minutes: `{scope['futureAttemptWallClockLimitMinutes']}`",
        f"- future Lean run limit: `{scope['futureLeanRunLimit']}`",
    ]
    block_lines = [f"- {item}" for item in payload["selectedOption"]["remainingBlocks"]]
    return render_markdown_report(
        title="ATLAS-A18 Private Sqrt Attempt Scope Correction Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Decision Criteria", criteria_lines),
            ("Corrected Future Scope", scope_lines),
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
    machlib_root: Path,
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path, machlib_root)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"atlas_a18_private_sqrt_attempt_scope_correction_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a18_private_sqrt_attempt_scope_correction_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a18_private_sqrt_attempt_scope_correction_selector.json"
    feed_path = command_feed_dir / f"atlas_a18_private_sqrt_attempt_scope_correction_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a18_private_sqrt_attempt_scope_correction_selector",
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
    print("ATLAS_A18_PRIVATE_SQRT_ATTEMPT_SCOPE_CORRECTION_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
