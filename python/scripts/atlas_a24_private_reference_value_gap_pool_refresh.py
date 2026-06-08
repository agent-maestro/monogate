#!/usr/bin/env python3
"""ATLAS-A24 private reference-value gap pool refresh."""

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

from scripts import atlas_a23_private_atlas_gap_strategy_selector as a23  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_reference_value_gap_pool_refresh.v0"
STATUS = "ATLAS_A24_PRIVATE_REFERENCE_VALUE_GAP_POOL_REFRESH_PASS"
ARTIFACT_ID = "atlas-a24-private-reference-value-gap-pool-refresh"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A25 private refreshed gap candidate value selector"
POOL_ID = "atlas_a24_reference_value_gap_pool_v0"

TRUE_CLAIM_FLAGS = {
    "atlas_a23_consumed",
    "gap_pool_refresh_created",
    "strategy_criteria_consumed",
    "excluded_paths_recorded",
    "candidate_directions_recorded",
    "candidate_direction_scores_recorded",
    "next_value_selector_recommended",
    "candidate_validity_blocked",
    "machlib_edit_blocked",
    "lean_typecheck_blocked",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a23_consumed": True,
    "gap_pool_refresh_created": True,
    "strategy_criteria_consumed": True,
    "excluded_paths_recorded": True,
    "candidate_directions_recorded": True,
    "candidate_direction_scores_recorded": True,
    "next_value_selector_recommended": True,
    "candidate_validity_blocked": True,
    "machlib_edit_blocked": True,
    "lean_typecheck_blocked": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "candidate_selected_for_packet": False,
    "new_candidate_packet_created": False,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_rejected": False,
    "candidate_disproved": False,
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
    "ATLAS-A24 creates a private refreshed candidate-direction pool only; it does not create a candidate packet, select a proof target, prove a witness, or claim candidate validity.",
    "ATLAS-A24 records scored directions for future review, not checked statements, theorem names, Lean-ready claims, runtime lowering changes, public copy, SDK/compiler/course copy, product implementation, or broad EML advantage.",
    "ATLAS-A24 keeps the blocked EML-shaped sqrt path excluded unless a new precise statement appears and keeps reciprocal deferred rather than rejected or disproved.",
]

EXCLUDED_PATHS = [
    {
        "pathId": "blocked_eml_sqrt_boundary_path",
        "source": "ATLAS-A22",
        "status": "excluded_from_a24_pool_unless_new_precise_statement",
        "reason": "A21/A22 recorded that the EML boundary alignment is not justified by the current local EML definition.",
    },
    {
        "pathId": "deferred_reciprocal_positive_boundary_path",
        "source": "ATLAS-A6/A23",
        "status": "deferred_not_rejected",
        "reason": "Earlier review found reciprocal feasible but lower reference value for Atlas diversity.",
    },
]


def direction(
    entry_id: str,
    label: str,
    family_hint: str,
    shape_hint: str,
    guard_hint: str,
    scores: dict[str, int],
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "entryId": entry_id,
        "candidateLabel": label,
        "familyHint": family_hint,
        "shapeHint": shape_hint,
        "guardHint": guard_hint,
        "scores": scores,
        "totalScore": sum(scores.values()),
        "referenceStatus": "candidate_direction_for_future_selector_not_packet_not_validity_claim",
        "rationale": rationale,
        "expectedBlockersBeforePacket": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_candidate_directions() -> list[dict[str, Any]]:
    return [
        direction(
            "trig_pythagorean_unit_identity_direction",
            "bounded trigonometric unit identity",
            "trig_boundary",
            "sin x * sin x + cos x * cos x = 1",
            "all real x",
            {
                "shape_diversity": 5,
                "guard_clarity": 5,
                "future_leverage": 4,
                "proof_effort_value_ratio": 3,
                "blocker_clarity": 4,
            },
            [
                "Adds a genuinely different oscillatory/trigonometric shape to the Atlas pool.",
                "The guard is easy to communicate if the statement is kept over all real inputs.",
                "The proof surface may be more expensive, so it belongs in a selector before any packet.",
            ],
            [
                "confirm MachLib/Lean trig namespace and exact theorem spelling before packet",
                "avoid public claims about trig lowering or broad complex EML advantage",
            ],
        ),
        direction(
            "exp_negation_multiplicative_identity_direction",
            "exponential negation multiplicative identity",
            "exp_algebra_boundary",
            "exp x * exp (-x) = 1",
            "all real x",
            {
                "shape_diversity": 4,
                "guard_clarity": 5,
                "future_leverage": 4,
                "proof_effort_value_ratio": 4,
                "blocker_clarity": 4,
            },
            [
                "Adds an exponential algebra identity without returning to log/subtraction/sqrt/reciprocal paths.",
                "The domain is simple and easy to explain.",
                "May become a useful guard-note example for inverse-style expressions without runtime replacement claims.",
            ],
            [
                "verify exact EML-shaped boundary form before packet",
                "avoid relabeling as an exponential runtime optimization",
            ],
        ),
        direction(
            "square_nonnegative_guard_direction",
            "square nonnegativity guard identity",
            "polynomial_guard_boundary",
            "0 <= x * x",
            "all real x",
            {
                "shape_diversity": 4,
                "guard_clarity": 5,
                "future_leverage": 3,
                "proof_effort_value_ratio": 5,
                "blocker_clarity": 5,
            },
            [
                "Gives the Atlas a small polynomial/inequality guard shape rather than another function roundtrip.",
                "Likely low proof effort relative to its teaching value for guard formation.",
                "May be too elementary for public witness priority, so it needs value selection before packet work.",
            ],
            [
                "decide whether inequality-only entries belong in Atlas v0 before packet",
                "avoid treating triviality as broad mathematical coverage",
            ],
        ),
        direction(
            "logistic_symmetry_boundary_direction",
            "logistic symmetry boundary",
            "sigmoid_probability_boundary",
            "sigma (-x) = 1 - sigma x",
            "all real x after sigma definition is fixed",
            {
                "shape_diversity": 5,
                "guard_clarity": 3,
                "future_leverage": 5,
                "proof_effort_value_ratio": 2,
                "blocker_clarity": 3,
            },
            [
                "High product/course reference value because sigmoid/logistic forms connect to ML explanations.",
                "Adds probability-style shape diversity beyond the current checked rows.",
                "Definition and notation risk are high enough that A24 should only pool it, not select it.",
            ],
            [
                "define sigma precisely before any packet",
                "avoid ML performance, advisor, accelerator, or product claims",
            ],
        ),
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a23.build_payload(atlas_gate_path, machlib_root)
    a23.validate_payload(source)
    directions = sorted(build_candidate_directions(), key=lambda item: item["totalScore"], reverse=True)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "sourceSelectedDecision": source["summary"]["selectedDecision"],
        "poolId": POOL_ID,
        "gapPoolRefreshCreated": True,
        "strategyCriteriaConsumed": True,
        "strategyCriteriaCount": len(source["strategyCriteria"]),
        "excludedPathsRecorded": True,
        "excludedPathCount": len(EXCLUDED_PATHS),
        "candidateDirectionsRecorded": True,
        "candidateDirectionCount": len(directions),
        "candidateDirectionScoresRecorded": True,
        "highestReferenceValueEntryId": directions[0]["entryId"],
        "highestReferenceValueScore": directions[0]["totalScore"],
        "candidateSelectedForPacket": False,
        "newCandidatePacketCreated": False,
        "candidateValidityBlocked": True,
        "candidateSelectedForProof": False,
        "candidateValidityClaim": False,
        "candidateRejected": False,
        "candidateDisproved": False,
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
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_reference_value_gap_pool_refresh",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "strategyCriteria": source["strategyCriteria"],
            "excludedPaths": EXCLUDED_PATHS,
            "candidateDirections": directions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    for direction_item in payload["candidateDirections"]:
        assert_claim_flags_bounded(direction_item["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "atlas-a23-private-atlas-gap-strategy-selector":
        raise ValueError("ATLAS-A24 must consume ATLAS-A23")
    if summary["sourceSelectedOptionId"] != "refresh_non_sqrt_non_reciprocal_gap_pool":
        raise ValueError("A24 must consume A23's gap pool refresh selection")
    if summary["sourceSelectedDecision"] != "refresh_reference_value_gap_pool_before_more_candidate_packets":
        raise ValueError("unexpected source decision")
    if summary["poolId"] != POOL_ID:
        raise ValueError("pool id drift")
    if summary["strategyCriteriaCount"] != 5:
        raise ValueError("expected five strategy criteria")
    if summary["excludedPathCount"] != 2:
        raise ValueError("expected two excluded paths")
    if summary["candidateDirectionCount"] != 4:
        raise ValueError("expected four candidate directions")
    if summary["highestReferenceValueEntryId"] not in {item["entryId"] for item in payload["candidateDirections"]}:
        raise ValueError("highest entry must be in pool")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "gapPoolRefreshCreated",
        "strategyCriteriaConsumed",
        "excludedPathsRecorded",
        "candidateDirectionsRecorded",
        "candidateDirectionScoresRecorded",
        "candidateValidityBlocked",
        "machlibEditBlocked",
        "leanTypecheckBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "candidateSelectedForPacket",
        "newCandidatePacketCreated",
        "candidateSelectedForProof",
        "candidateValidityClaim",
        "candidateRejected",
        "candidateDisproved",
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
        artifact_type="private_reference_value_gap_pool_refresh",
        semantic_strength="private_gap_pool_refresh_records_scored_directions_no_candidate_packet_no_machlib_no_lean_no_validity",
        source=f"python/results/atlas_a24_private_reference_value_gap_pool_refresh/atlas_a24_private_reference_value_gap_pool_refresh_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a24_private_reference_value_gap_pool_refresh_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A25 as a private refreshed gap candidate value selector; do not create a candidate packet or proof claim from A24.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "poolId": payload["summary"]["poolId"],
            "candidateDirectionCount": payload["summary"]["candidateDirectionCount"],
            "highestReferenceValueEntryId": payload["summary"]["highestReferenceValueEntryId"],
            "candidateSelectedForPacket": payload["summary"]["candidateSelectedForPacket"],
            "newCandidatePacketCreated": payload["summary"]["newCandidatePacketCreated"],
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
        ("pool id", payload["summary"]["poolId"]),
        ("candidate directions", payload["summary"]["candidateDirectionCount"]),
        ("excluded paths", payload["summary"]["excludedPathCount"]),
        ("highest reference-value entry", payload["summary"]["highestReferenceValueEntryId"]),
        ("candidate selected for packet", payload["summary"]["candidateSelectedForPacket"]),
        ("new candidate packet created", payload["summary"]["newCandidatePacketCreated"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("MachLib changed", payload["summary"]["machlibFileChanged"]),
        ("Lean typecheck performed", payload["summary"]["leanTypecheckPerformed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    excluded_lines = [f"- `{item['pathId']}`: {item['status']} ({item['reason']})" for item in payload["excludedPaths"]]
    direction_lines = ["| Direction | Family | Guard | Score |", "|---|---|---|---|"]
    for item in payload["candidateDirections"]:
        direction_lines.append(
            f"| `{item['entryId']}` | `{item['familyHint']}` | `{item['guardHint']}` | `{item['totalScore']}` |"
        )
    return render_markdown_report(
        title="ATLAS-A24 Private Reference-Value Gap Pool Refresh",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Excluded Paths", excluded_lines),
            ("Candidate Directions", direction_lines),
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
    result_path = out_dir / f"atlas_a24_private_reference_value_gap_pool_refresh_{STAMP}.json"
    report_path = report_dir / f"atlas_a24_private_reference_value_gap_pool_refresh_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a24_private_reference_value_gap_pool_refresh.json"
    feed_path = command_feed_dir / f"atlas_a24_private_reference_value_gap_pool_refresh_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a24_private_reference_value_gap_pool_refresh",
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
    print("ATLAS_A24_PRIVATE_REFERENCE_VALUE_GAP_POOL_REFRESH_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
