#!/usr/bin/env python3
"""ATLAS-A21 private corrected-scope bounded sqrt attempt artifact."""

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

from scripts import atlas_a20_private_corrected_scope_sqrt_attempt_readiness_selector as a20  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_corrected_scope_bounded_sqrt_attempt_artifact.v0"
STATUS = "ATLAS_A21_PRIVATE_CORRECTED_SCOPE_BOUNDED_SQRT_ATTEMPT_ARTIFACT_BLOCKED"
ARTIFACT_ID = "atlas-a21-private-corrected-scope-bounded-sqrt-attempt-artifact"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
CORRECTED_ALLOWED_FILE = "foundations/MachLib/EMLAtlasWitness.lean"
BLOCKER_ID = "eml_boundary_alignment_not_justified_by_current_eml_definition"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A22 private sqrt candidate reframe-or-park selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a20_consumed",
    "bounded_attempt_artifact_created",
    "corrected_allowed_file_preflight_performed",
    "target_statement_alignment_reviewed",
    "eml_definition_alignment_blocker_recorded",
    "attempt_aborted_before_edit",
    "reframe_or_park_selector_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a20_consumed": True,
    "bounded_attempt_artifact_created": True,
    "corrected_allowed_file_preflight_performed": True,
    "target_statement_alignment_reviewed": True,
    "eml_definition_alignment_blocker_recorded": True,
    "attempt_aborted_before_edit": True,
    "reframe_or_park_selector_recommended": True,
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
    "runtime_lowering_changed": False,
    "runtime_sqrt_replacement_claim": False,
    "atlas_v0_doc_pause_selected": False,
    "sqrt_candidate_parked": False,
    "sqrt_candidate_reframed": False,
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
    "ATLAS-A21 creates a private corrected-scope bounded attempt artifact and aborts before edit because the proposed EML alignment is not justified by the current EML definition.",
    "ATLAS-A21 performs pre-edit target-statement alignment review only; it does not edit MachLib, run Lean, perform theorem lookup, claim exact theorem names, or claim the sqrt candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A21 does not reframe or park the candidate, change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, touch laptop-owned repositories, or claim public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_attempt_review(source: dict[str, Any], machlib_root: Path) -> dict[str, Any]:
    allowed_file = source["summary"]["allowedFiles"][0]
    allowed_path = machlib_root / allowed_file
    return {
        "attemptStatus": "blocked_before_patch_due_eml_definition_alignment",
        "allowedFile": allowed_file,
        "allowedFileExists": allowed_path.exists(),
        "targetStatementsReviewed": [
            {
                "statementId": "abs_normalization",
                "shape": "sqrt (x * x) = abs x",
                "status": "not_attempted_this_phase",
                "note": "This may be a meaningful sqrt/abs route, but A21 stops before proving it because the EML boundary alignment fails first.",
            },
            {
                "statementId": "guard_reduction",
                "shape": "0 <= x -> sqrt (x * x) = x",
                "status": "not_attempted_this_phase",
                "note": "This depends on the abs-normalized route and remains unproved in A21.",
            },
            {
                "statementId": "eml_boundary_alignment",
                "shape": "0 <= x -> eml (sqrt (x * x)) x = x",
                "status": "blocked_before_patch",
                "note": "The local EML definition is `eml a b := exp a - log b`; the proposed statement would require an additional relationship between `exp (sqrt (x * x)) - log x` and `x` that is not part of the current route.",
            },
        ],
        "blocker": {
            "blockerId": BLOCKER_ID,
            "status": "blocks_patch_before_machlib_edit",
            "whyAbortInsteadOfPatch": [
                "A19 requires confirming the target statement before any future patch.",
                "The proposed EML alignment does not follow from the current EML definition and recorded route.",
                "Forcing a MachLib theorem here would either fail or require a different candidate statement.",
            ],
        },
        "futureSafeOptions": [
            "park the sqrt candidate without rejection",
            "reframe as a pure sqrt/abs witness outside EML boundary alignment",
            "reframe only if a precise EML-shaped statement can be stated before editing",
        ],
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a20.build_payload(atlas_gate_path, machlib_root)
    a20.validate_payload(source)
    review = build_attempt_review(source, machlib_root)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "candidateId": source["summary"]["candidateId"],
        "boundedAttemptArtifactCreated": True,
        "attemptStatus": review["attemptStatus"],
        "correctedAllowedFilePreflightPerformed": True,
        "allowedFiles": source["summary"]["allowedFiles"],
        "allowedFileExists": review["allowedFileExists"],
        "targetStatementAlignmentReviewed": True,
        "emlDefinitionAlignmentBlockerRecorded": True,
        "blockerId": BLOCKER_ID,
        "attemptAbortedBeforeEdit": True,
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
        "sqrtCandidateParked": False,
        "sqrtCandidateReframed": False,
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
        artifact_type="private_corrected_scope_bounded_sqrt_attempt_artifact",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceCorrectedScopeGate": source["sourceCorrectedScopeGate"],
            "attemptReview": review,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    review = payload["attemptReview"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a20-private-corrected-scope-sqrt-attempt-readiness-selector":
        raise ValueError("ATLAS-A21 must consume ATLAS-A20")
    if summary["sourceSelectedOptionId"] != "recommend_future_corrected_scope_bounded_attempt_artifact":
        raise ValueError("A21 must consume A20's selected future attempt recommendation")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["allowedFiles"] != [CORRECTED_ALLOWED_FILE]:
        raise ValueError("corrected allowed file drift")
    if summary["allowedFileExists"] is not True:
        raise ValueError("corrected allowed file should exist")
    if summary["attemptStatus"] != "blocked_before_patch_due_eml_definition_alignment":
        raise ValueError("unexpected attempt status")
    if summary["blockerId"] != BLOCKER_ID:
        raise ValueError("blocker id drift")
    if review["blocker"]["blockerId"] != BLOCKER_ID:
        raise ValueError("review blocker id drift")
    if len(review["targetStatementsReviewed"]) != 3:
        raise ValueError("expected three reviewed target statements")
    if review["targetStatementsReviewed"][2]["status"] != "blocked_before_patch":
        raise ValueError("EML alignment statement should be blocked")
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
        "boundedAttemptArtifactCreated",
        "correctedAllowedFilePreflightPerformed",
        "targetStatementAlignmentReviewed",
        "emlDefinitionAlignmentBlockerRecorded",
        "attemptAbortedBeforeEdit",
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
        "sqrtCandidateParked",
        "sqrtCandidateReframed",
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
        artifact_type="private_corrected_scope_bounded_sqrt_attempt_artifact",
        semantic_strength="private_attempt_artifact_blocked_by_eml_definition_alignment_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact/atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A22 as a private sqrt candidate reframe-or-park selector; do not edit MachLib or claim validity from A21.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "attemptStatus": payload["summary"]["attemptStatus"],
            "blockerId": payload["summary"]["blockerId"],
            "allowedFiles": payload["summary"]["allowedFiles"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    review = payload["attemptReview"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("attempt status", payload["summary"]["attemptStatus"]),
        ("blocker id", payload["summary"]["blockerId"]),
        ("allowed files", ", ".join(payload["summary"]["allowedFiles"])),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    target_lines = ["| Statement | Status | Shape |", "|---|---|---|"]
    for item in review["targetStatementsReviewed"]:
        shape = item["shape"].replace("|", "\\|")
        target_lines.append(f"| `{item['statementId']}` | `{item['status']}` | `{shape}` |")
    blocker_lines = [
        f"- status: `{review['blocker']['status']}`",
        f"- blocker id: `{review['blocker']['blockerId']}`",
    ]
    blocker_lines.extend(f"- {item}" for item in review["blocker"]["whyAbortInsteadOfPatch"])
    option_lines = [f"- {item}" for item in review["futureSafeOptions"]]
    return render_markdown_report(
        title="ATLAS-A21 Private Corrected-Scope Bounded Sqrt Attempt Artifact",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Target Statement Review", target_lines),
            ("Precise Blocker", blocker_lines),
            ("Future Safe Options", option_lines),
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
    result_path = out_dir / f"atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact_{STAMP}.json"
    report_path = report_dir / f"atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact.json"
    feed_path = command_feed_dir / f"atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a21_private_corrected_scope_bounded_sqrt_attempt_artifact",
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
    print("ATLAS_A21_PRIVATE_CORRECTED_SCOPE_BOUNDED_SQRT_ATTEMPT_ARTIFACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
