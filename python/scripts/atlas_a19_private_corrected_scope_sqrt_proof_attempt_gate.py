#!/usr/bin/env python3
"""ATLAS-A19 private corrected-scope sqrt proof-attempt gate."""

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

from scripts import atlas_a18_private_sqrt_attempt_scope_correction_selector as a18  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_corrected_scope_sqrt_proof_attempt_gate.v0"
STATUS = "ATLAS_A19_PRIVATE_CORRECTED_SCOPE_SQRT_PROOF_ATTEMPT_GATE_PASS"
ARTIFACT_ID = "atlas-a19-private-corrected-scope-sqrt-proof-attempt-gate"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
GATE_ID = "sqrt_abs_normalized_nonnegative_corrected_scope_private_attempt_gate"
CORRECTED_ALLOWED_FILE = "foundations/MachLib/EMLAtlasWitness.lean"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A20 private corrected-scope sqrt attempt readiness selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a18_consumed",
    "corrected_scope_gate_created",
    "corrected_allowed_scope_recorded",
    "timeout_budget_recorded",
    "abort_conditions_recorded",
    "required_route_recorded",
    "review_checkpoints_recorded",
    "readiness_selector_recommended",
    "candidate_validity_blocked",
    "actual_proof_attempt_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a18_consumed": True,
    "corrected_scope_gate_created": True,
    "corrected_allowed_scope_recorded": True,
    "timeout_budget_recorded": True,
    "abort_conditions_recorded": True,
    "required_route_recorded": True,
    "review_checkpoints_recorded": True,
    "readiness_selector_recommended": True,
    "candidate_validity_blocked": True,
    "actual_proof_attempt_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "proof_attempt_readiness_selector_created": False,
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
    "ATLAS-A19 creates a private corrected-scope proof-attempt gate only; it does not create a readiness selector, start proof work, edit MachLib, or run Lean.",
    "ATLAS-A19 records the corrected future allowed file `foundations/MachLib/EMLAtlasWitness.lean`, budget, route, abort conditions, and checkpoints; it does not perform theorem lookup, claim exact theorem names, or claim the sqrt candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A19 does not change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, touch laptop-owned repositories, or claim public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_gate(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "gateId": GATE_ID,
        "candidateId": CANDIDATE_ID,
        "gateStatus": "private_corrected_scope_gate_only_no_attempt_no_validity",
        "allowedScope": {
            "allowedRepositories": ["machlib"],
            "allowedFiles": [CORRECTED_ALLOWED_FILE],
            "allowedOperations": [
                "read existing local witness surroundings in a later artifact",
                "draft at most one private proof-attempt patch in a later artifact",
                "abort before helper theorem expansion or broad refactor",
            ],
            "blockedOperations": [
                "no edits in ATLAS-A19",
                "no Lean run in ATLAS-A19",
                "no theorem lookup in ATLAS-A19",
                "no runtime changes",
                "no public/dev/electronics repository touch",
            ],
        },
        "timeoutBudget": {
            "futureAttemptWallClockLimitMinutes": source["summary"]["futureAttemptWallClockLimitMinutes"],
            "futureLeanRunLimit": source["summary"]["futureLeanRunLimit"],
            "futurePatchSizeGuidance": "minimal candidate-local edit only",
            "budgetStatus": "budget_for_future_corrected_scope_attempt_not_consumed",
        },
        "requiredStartingRoute": [
            {"stepId": "abs_normalization", "shape": "sqrt (x * x) = |x|", "required": True},
            {"stepId": "guard_reduction", "shape": "0 <= x -> sqrt (x * x) = x", "required": True},
            {
                "stepId": "eml_boundary_alignment",
                "shape": "0 <= x -> eml (sqrt (x * x)) x = x",
                "required": True,
            },
        ],
        "abortConditions": [
            "abort if corrected allowed file no longer exists",
            "abort if exact expression alignment cannot be stated before editing",
            "abort if the proof route needs a new helper theorem",
            "abort if the candidate requires broad EML boundary rewrites",
            "abort if the nonnegative guard direction becomes ambiguous",
            "abort if any public, runtime, SDK, or course claim becomes tempting",
        ],
        "reviewCheckpoints": [
            "confirm corrected allowed file before any future patch",
            "confirm target statement before any future patch",
            "confirm abs-normalized route is still the first proof step",
            "confirm guard reduction remains under `0 <= x`",
            "confirm future attempt leaves runtime sqrt behavior untouched",
            "record blocker instead of forcing proof if the route drifts",
        ],
        "nextDecision": {
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "decisionStatus": "recommend_corrected_scope_readiness_selector_not_attempt",
            "rationale": [
                "A19 creates the corrected-scope gate; a separate readiness selector should decide whether to consume it.",
                "Actual proof work remains blocked until a later explicit artifact opens it.",
            ],
        },
        "blockedClaims": [
            "not a checked witness",
            "not selected for proof",
            "no proof attempt started",
            "no theorem lookup performed",
            "no exact theorem names claimed",
            "no MachLib edit",
            "no Lean typecheck",
            "no runtime sqrt replacement",
            "no public copy approval",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a18.build_payload(atlas_gate_path, machlib_root)
    a18.validate_payload(source)
    gate = build_gate(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "candidateId": gate["candidateId"],
        "gateId": gate["gateId"],
        "gateStatus": gate["gateStatus"],
        "correctedScopeGateCreated": True,
        "correctedAllowedScopeRecorded": True,
        "allowedFiles": gate["allowedScope"]["allowedFiles"],
        "timeoutBudgetRecorded": True,
        "futureAttemptWallClockLimitMinutes": gate["timeoutBudget"]["futureAttemptWallClockLimitMinutes"],
        "futureLeanRunLimit": gate["timeoutBudget"]["futureLeanRunLimit"],
        "abortConditionsRecorded": True,
        "abortConditionCount": len(gate["abortConditions"]),
        "requiredRouteRecorded": True,
        "requiredRouteStepIds": [item["stepId"] for item in gate["requiredStartingRoute"]],
        "reviewCheckpointsRecorded": True,
        "reviewCheckpointCount": len(gate["reviewCheckpoints"]),
        "readinessSelectorRecommended": True,
        "proofAttemptReadinessSelectorCreated": False,
        "candidateValidityBlocked": True,
        "actualProofAttemptBlocked": True,
        "machlibEditBlocked": True,
        "leanTypecheckBlocked": True,
        "candidateValidityClaim": False,
        "candidateSelectedForProof": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "proofAttemptCompleted": False,
        "machlibFileChanged": False,
        "machlibCommitCreated": False,
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
        artifact_type="private_corrected_scope_sqrt_proof_attempt_gate",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceCorrectedFutureScope": source["correctedFutureScope"],
            "correctedScopeGate": gate,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    gate = payload["correctedScopeGate"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(gate["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a18-private-sqrt-attempt-scope-correction-selector":
        raise ValueError("ATLAS-A19 must consume ATLAS-A18")
    if summary["sourceSelectedOptionId"] != "approve_one_off_scope_correction_for_future_attempt":
        raise ValueError("A19 must consume A18's selected scope correction")
    if summary["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["gateId"] != GATE_ID:
        raise ValueError("gate id drift")
    if summary["allowedFiles"] != [CORRECTED_ALLOWED_FILE]:
        raise ValueError("corrected allowed file drift")
    if summary["futureAttemptWallClockLimitMinutes"] != 30:
        raise ValueError("future attempt budget drift")
    if summary["futureLeanRunLimit"] != 1:
        raise ValueError("future Lean run limit drift")
    if summary["requiredRouteStepIds"] != ["abs_normalization", "guard_reduction", "eml_boundary_alignment"]:
        raise ValueError("route drift")
    if summary["abortConditionCount"] != 6:
        raise ValueError("abort condition count drift")
    if summary["reviewCheckpointCount"] != 6:
        raise ValueError("review checkpoint count drift")
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
        "correctedScopeGateCreated",
        "correctedAllowedScopeRecorded",
        "timeoutBudgetRecorded",
        "abortConditionsRecorded",
        "requiredRouteRecorded",
        "reviewCheckpointsRecorded",
        "readinessSelectorRecommended",
        "candidateValidityBlocked",
        "actualProofAttemptBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "proofAttemptReadinessSelectorCreated",
        "candidateValidityClaim",
        "candidateSelectedForProof",
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
        artifact_type="private_corrected_scope_sqrt_proof_attempt_gate",
        semantic_strength="private_corrected_scope_gate_no_attempt_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate/atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A20 as a corrected-scope readiness selector; do not edit MachLib or run Lean until a later artifact opens the attempt.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "gateId": payload["summary"]["gateId"],
            "allowedFiles": payload["summary"]["allowedFiles"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    gate = payload["correctedScopeGate"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("gate id", payload["summary"]["gateId"]),
        ("gate status", payload["summary"]["gateStatus"]),
        ("allowed files", ", ".join(payload["summary"]["allowedFiles"])),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    scope_lines = [
        f"- allowed repositories: `{', '.join(gate['allowedScope']['allowedRepositories'])}`",
        f"- allowed files: `{', '.join(gate['allowedScope']['allowedFiles'])}`",
        f"- future wall-clock limit minutes: `{gate['timeoutBudget']['futureAttemptWallClockLimitMinutes']}`",
        f"- future Lean run limit: `{gate['timeoutBudget']['futureLeanRunLimit']}`",
    ]
    route_lines = ["| Step | Shape |", "|---|---|"]
    for item in gate["requiredStartingRoute"]:
        shape = item["shape"].replace("|", "\\|")
        route_lines.append(f"| `{item['stepId']}` | `{shape}` |")
    abort_lines = [f"- {item}" for item in gate["abortConditions"]]
    checkpoint_lines = [f"- {item}" for item in gate["reviewCheckpoints"]]
    return render_markdown_report(
        title="ATLAS-A19 Private Corrected-Scope Sqrt Proof-Attempt Gate",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Corrected Allowed Scope And Budget", scope_lines),
            ("Required Starting Route", route_lines),
            ("Abort Conditions", abort_lines),
            ("Review Checkpoints", checkpoint_lines),
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
    result_path = out_dir / f"atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate_{STAMP}.json"
    report_path = report_dir / f"atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate.json"
    feed_path = command_feed_dir / f"atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a19_private_corrected_scope_sqrt_proof_attempt_gate",
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
    print("ATLAS_A19_PRIVATE_CORRECTED_SCOPE_SQRT_PROOF_ATTEMPT_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
