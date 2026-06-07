#!/usr/bin/env python3
"""ATLAS-A15 private scoped sqrt proof-attempt packet."""

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

from scripts import atlas_a14_private_sqrt_proof_attempt_readiness_selector as a14  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_scoped_sqrt_proof_attempt_packet.v0"
STATUS = "ATLAS_A15_PRIVATE_SCOPED_SQRT_PROOF_ATTEMPT_PACKET_PASS"
ARTIFACT_ID = "atlas-a15-private-scoped-sqrt-proof-attempt-packet"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
ATTEMPT_PACKET_ID = "sqrt_abs_normalized_nonnegative_private_scoped_attempt_packet"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A16 private sqrt proof-attempt open selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a14_consumed",
    "scoped_attempt_packet_created",
    "attempt_scope_recorded",
    "attempt_start_route_recorded",
    "attempt_budget_recorded",
    "abort_conditions_carried_forward",
    "open_selector_recommended",
    "candidate_validity_blocked",
    "actual_proof_attempt_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a14_consumed": True,
    "scoped_attempt_packet_created": True,
    "attempt_scope_recorded": True,
    "attempt_start_route_recorded": True,
    "attempt_budget_recorded": True,
    "abort_conditions_carried_forward": True,
    "open_selector_recommended": True,
    "candidate_validity_blocked": True,
    "actual_proof_attempt_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "proof_attempt_open_selector_created": False,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
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
    "ATLAS-A15 creates a private scoped attempt packet only; it does not open the attempt, edit MachLib, run Lean, or select the candidate for proof.",
    "ATLAS-A15 records the future attempt route, scope, budget, abort rules, and expected outputs; it does not perform theorem lookup, claim exact theorem names, or claim the candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A15 does not change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_attempt_packet(source: dict[str, Any]) -> dict[str, Any]:
    gate = source["sourceProofAttemptGate"]
    return {
        "attemptPacketId": ATTEMPT_PACKET_ID,
        "candidateId": CANDIDATE_ID,
        "attemptStatus": "private_scoped_attempt_packet_only_not_open_not_started",
        "allowedScope": gate["allowedScope"],
        "attemptBudget": gate["timeoutBudget"],
        "requiredStartingRoute": gate["requiredStartingRoute"],
        "abortConditions": gate["abortConditions"],
        "reviewCheckpoints": gate["reviewCheckpoints"],
        "expectedFutureOutputsIfOpened": [
            "one local patch candidate or precise blocker",
            "one generated attempt report",
            "one evidence packet preserving blocked validity and public claims",
            "one command feed for the next review selector",
        ],
        "mustNotDoInThisPhase": [
            "do not edit MachLib",
            "do not run Lean",
            "do not perform theorem lookup",
            "do not claim exact theorem names",
            "do not claim candidate validity",
            "do not promote public copy",
        ],
        "nextDecision": {
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "decisionStatus": "recommend_open_selector_not_attempt",
            "rationale": [
                "A15 defines the attempt artifact; a separate open selector must decide whether to consume it.",
                "The attempt remains closed so the lane can still pause or park before touching MachLib.",
            ],
        },
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a14.build_payload(atlas_gate_path)
    a14.validate_payload(source)
    attempt = build_attempt_packet(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "candidateId": attempt["candidateId"],
        "attemptPacketId": attempt["attemptPacketId"],
        "attemptStatus": attempt["attemptStatus"],
        "scopedAttemptPacketCreated": True,
        "attemptScopeRecorded": True,
        "attemptStartRouteRecorded": True,
        "attemptBudgetRecorded": True,
        "abortConditionsCarriedForward": True,
        "openSelectorRecommended": True,
        "proofAttemptOpenSelectorCreated": False,
        "candidateValidityBlocked": True,
        "actualProofAttemptBlocked": True,
        "machlibEditBlocked": True,
        "leanTypecheckBlocked": True,
        "candidateValidityClaim": False,
        "candidateSelectedForProof": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
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
        artifact_type="private_scoped_sqrt_proof_attempt_packet",
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
            "scopedAttemptPacket": attempt,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    attempt = payload["scopedAttemptPacket"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(attempt["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a14-private-sqrt-proof-attempt-readiness-selector":
        raise ValueError("ATLAS-A15 must consume ATLAS-A14")
    if summary["sourceSelectedOptionId"] != "recommend_future_scoped_sqrt_attempt_packet":
        raise ValueError("A15 must consume A14's selected attempt-packet recommendation")
    if summary["candidateId"] != CANDIDATE_ID or attempt["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["attemptPacketId"] != ATTEMPT_PACKET_ID:
        raise ValueError("attempt packet id drift")
    if attempt["allowedScope"]["allowedFiles"] != ["MachLib/Real.lean"]:
        raise ValueError("allowed file drift")
    if attempt["attemptBudget"]["futureAttemptWallClockLimitMinutes"] != 30:
        raise ValueError("timeout budget drift")
    if attempt["attemptBudget"]["futureLeanRunLimit"] != 1:
        raise ValueError("Lean run limit drift")
    if len(attempt["requiredStartingRoute"]) != 3:
        raise ValueError("expected three route steps")
    if len(attempt["abortConditions"]) != 5:
        raise ValueError("expected five abort conditions")
    if len(attempt["expectedFutureOutputsIfOpened"]) != 4:
        raise ValueError("expected four future outputs")
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
        "scopedAttemptPacketCreated",
        "attemptScopeRecorded",
        "attemptStartRouteRecorded",
        "attemptBudgetRecorded",
        "abortConditionsCarriedForward",
        "openSelectorRecommended",
        "candidateValidityBlocked",
        "actualProofAttemptBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "proofAttemptOpenSelectorCreated",
        "candidateValidityClaim",
        "candidateSelectedForProof",
        "candidateProved",
        "proofAttemptStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
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
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_scoped_sqrt_proof_attempt_packet",
        semantic_strength="private_attempt_packet_defined_no_attempt_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a15_private_scoped_sqrt_proof_attempt_packet/atlas_a15_private_scoped_sqrt_proof_attempt_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a15_private_scoped_sqrt_proof_attempt_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A16 as a private sqrt proof-attempt open selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "attemptPacketId": payload["summary"]["attemptPacketId"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    attempt = payload["scopedAttemptPacket"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("attempt packet id", payload["summary"]["attemptPacketId"]),
        ("attempt status", payload["summary"]["attemptStatus"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    scope_lines = [
        f"- allowed files: `{', '.join(attempt['allowedScope']['allowedFiles'])}`",
        f"- future wall-clock limit minutes: `{attempt['attemptBudget']['futureAttemptWallClockLimitMinutes']}`",
        f"- future Lean run limit: `{attempt['attemptBudget']['futureLeanRunLimit']}`",
    ]
    route_lines = ["| Step | Shape |", "|---|---|"]
    for item in attempt["requiredStartingRoute"]:
        shape = item["shape"].replace("|", "\\|")
        route_lines.append(f"| `{item['stepId']}` | `{shape}` |")
    abort_lines = [f"- {item}" for item in attempt["abortConditions"]]
    output_lines = [f"- {item}" for item in attempt["expectedFutureOutputsIfOpened"]]
    return render_markdown_report(
        title="ATLAS-A15 Private Scoped Sqrt Proof-Attempt Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Attempt Scope", scope_lines),
            ("Required Starting Route", route_lines),
            ("Abort Conditions", abort_lines),
            ("Expected Future Outputs If Opened", output_lines),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    atlas_gate_path: Path,
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"atlas_a15_private_scoped_sqrt_proof_attempt_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a15_private_scoped_sqrt_proof_attempt_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a15_private_scoped_sqrt_proof_attempt_packet.json"
    feed_path = command_feed_dir / f"atlas_a15_private_scoped_sqrt_proof_attempt_packet_feed_{STAMP}.json"
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/atlas_a15_private_scoped_sqrt_proof_attempt_packet",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.atlas_gate_path)
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.atlas_gate_path)
    print("ATLAS_A15_PRIVATE_SCOPED_SQRT_PROOF_ATTEMPT_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
