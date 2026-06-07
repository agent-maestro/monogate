#!/usr/bin/env python3
"""ATLAS-A13 private scoped sqrt proof-attempt gate packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a12_private_sqrt_proof_attempt_gate_selector as a12  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_scoped_sqrt_proof_attempt_gate_packet.v0"
STATUS = "ATLAS_A13_PRIVATE_SCOPED_SQRT_PROOF_ATTEMPT_GATE_PACKET_PASS"
ARTIFACT_ID = "atlas-a13-private-scoped-sqrt-proof-attempt-gate-packet"
CANDIDATE_ID = "sqrt_square_abs_normalized_nonnegative_boundary_candidate"
GATE_ID = "sqrt_abs_normalized_nonnegative_private_attempt_gate"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A14 private sqrt proof-attempt readiness selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a12_consumed",
    "proof_attempt_gate_packet_created",
    "allowed_scope_recorded",
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
    "atlas_a12_consumed": True,
    "proof_attempt_gate_packet_created": True,
    "allowed_scope_recorded": True,
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
    "ATLAS-A13 creates a private proof-attempt gate packet only; it does not create a readiness selector, start proof work, or select the candidate for proof.",
    "ATLAS-A13 records allowed scope, budgets, abort conditions, required route, and checkpoints; it does not perform theorem lookup, claim exact theorem names, run Lean, edit MachLib, or claim the candidate is true, valid, checked, Lean-ready, or provable.",
    "ATLAS-A13 does not change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def build_gate_packet(source: dict[str, Any]) -> dict[str, Any]:
    review = source["sourceProofFeasibilityReview"]
    return {
        "gateId": GATE_ID,
        "candidateId": CANDIDATE_ID,
        "gateStatus": "private_gate_packet_only_no_attempt_no_validity",
        "allowedScope": {
            "allowedRepositories": ["machlib"],
            "allowedFiles": ["MachLib/Real.lean"],
            "allowedOperations": [
                "read existing local theorem surroundings",
                "draft at most one private proof-attempt patch in a later artifact",
                "abort before any broad refactor or helper theorem expansion",
            ],
            "blockedOperations": [
                "no edits in ATLAS-A13",
                "no Lean run in ATLAS-A13",
                "no theorem lookup in ATLAS-A13",
                "no runtime changes",
                "no public/dev/electronics repository touch",
            ],
        },
        "timeoutBudget": {
            "futureAttemptWallClockLimitMinutes": 30,
            "futureLeanRunLimit": 1,
            "futurePatchSizeGuidance": "minimal candidate-local edit only",
            "budgetStatus": "budget_for_future_gate_review_not_consumed",
        },
        "requiredStartingRoute": [
            {
                "stepId": item["stepId"],
                "shape": item["shape"],
                "required": True,
            }
            for item in review["proofFacingRoute"]
        ],
        "abortConditions": [
            "abort if exact expression alignment cannot be stated before editing",
            "abort if the proof route needs a new helper theorem",
            "abort if the candidate requires broad EML boundary rewrites",
            "abort if the nonnegative guard direction becomes ambiguous",
            "abort if any public, runtime, SDK, or course claim becomes tempting",
        ],
        "reviewCheckpoints": [
            "confirm target statement before any future patch",
            "confirm abs-normalized route is still the first proof step",
            "confirm guard reduction remains under `0 <= x`",
            "confirm future attempt leaves runtime sqrt behavior untouched",
            "record blocker instead of forcing proof if the route drifts",
        ],
        "nextDecision": {
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "decisionStatus": "recommend_readiness_selector_not_attempt",
            "rationale": [
                "A13 defines the attempt boundary; a readiness selector should decide whether to consume it.",
                "Actual proof work remains blocked until a later explicit gate opens it.",
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


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a12.build_payload(atlas_gate_path)
    a12.validate_payload(source)
    gate = build_gate_packet(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "candidateId": gate["candidateId"],
        "gateId": gate["gateId"],
        "gateStatus": gate["gateStatus"],
        "proofAttemptGatePacketCreated": True,
        "allowedScopeRecorded": True,
        "timeoutBudgetRecorded": True,
        "abortConditionsRecorded": True,
        "requiredRouteRecorded": True,
        "reviewCheckpointsRecorded": True,
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
        artifact_type="private_scoped_sqrt_proof_attempt_gate_packet",
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
            "proofAttemptGate": gate,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    gate = payload["proofAttemptGate"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(gate["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a12-private-sqrt-proof-attempt-gate-selector":
        raise ValueError("ATLAS-A13 must consume ATLAS-A12")
    if summary["sourceSelectedOptionId"] != "create_scoped_private_sqrt_proof_attempt_gate_packet":
        raise ValueError("A13 must consume A12's scoped gate selection")
    if summary["candidateId"] != CANDIDATE_ID or gate["candidateId"] != CANDIDATE_ID:
        raise ValueError("candidate id drift")
    if summary["gateId"] != GATE_ID or gate["gateId"] != GATE_ID:
        raise ValueError("gate id drift")
    if gate["allowedScope"]["allowedRepositories"] != ["machlib"]:
        raise ValueError("allowed repo drift")
    if gate["allowedScope"]["allowedFiles"] != ["MachLib/Real.lean"]:
        raise ValueError("allowed file drift")
    if gate["timeoutBudget"]["futureAttemptWallClockLimitMinutes"] != 30:
        raise ValueError("timeout budget drift")
    if gate["timeoutBudget"]["futureLeanRunLimit"] != 1:
        raise ValueError("future Lean run limit drift")
    if len(gate["requiredStartingRoute"]) != 3:
        raise ValueError("expected three route steps")
    if len(gate["abortConditions"]) != 5:
        raise ValueError("expected five abort conditions")
    if len(gate["reviewCheckpoints"]) != 5:
        raise ValueError("expected five review checkpoints")
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
        "proofAttemptGatePacketCreated",
        "allowedScopeRecorded",
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
        artifact_type="private_scoped_sqrt_proof_attempt_gate_packet",
        semantic_strength="private_gate_packet_defines_sqrt_attempt_scope_no_attempt_no_validity_no_lean",
        source=f"python/results/atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet/atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A14 as a private sqrt proof-attempt readiness selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "candidateId": payload["summary"]["candidateId"],
            "gateId": payload["summary"]["gateId"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
            "machlibFileChanged": payload["summary"]["machlibFileChanged"],
            "leanTypecheckPerformed": payload["summary"]["leanTypecheckPerformed"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    gate = payload["proofAttemptGate"]
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("candidate id", payload["summary"]["candidateId"]),
        ("gate id", payload["summary"]["gateId"]),
        ("gate status", payload["summary"]["gateStatus"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    scope_lines = [
        f"- allowed repositories: `{', '.join(gate['allowedScope']['allowedRepositories'])}`",
        f"- allowed files: `{', '.join(gate['allowedScope']['allowedFiles'])}`",
        "- blocked operations:",
    ]
    scope_lines.extend(f"  - {item}" for item in gate["allowedScope"]["blockedOperations"])
    budget_lines = [
        f"- future attempt wall-clock limit minutes: `{gate['timeoutBudget']['futureAttemptWallClockLimitMinutes']}`",
        f"- future Lean run limit: `{gate['timeoutBudget']['futureLeanRunLimit']}`",
        f"- patch size guidance: `{gate['timeoutBudget']['futurePatchSizeGuidance']}`",
    ]
    route_lines = ["| Step | Shape |", "|---|---|"]
    for item in gate["requiredStartingRoute"]:
        route_lines.append(f"| `{item['stepId']}` | `{item['shape'].replace('|', '\\|')}` |")
    abort_lines = [f"- {item}" for item in gate["abortConditions"]]
    checkpoint_lines = [f"- {item}" for item in gate["reviewCheckpoints"]]
    return render_markdown_report(
        title="ATLAS-A13 Private Scoped Sqrt Proof-Attempt Gate Packet",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Allowed Scope", scope_lines),
            ("Timeout Budget", budget_lines),
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
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet_{STAMP}.json"
    report_path = report_dir / f"atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet.json"
    feed_path = command_feed_dir / f"atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a13_private_scoped_sqrt_proof_attempt_gate_packet",
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
    print("ATLAS_A13_PRIVATE_SCOPED_SQRT_PROOF_ATTEMPT_GATE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
