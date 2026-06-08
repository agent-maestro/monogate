#!/usr/bin/env python3
"""ATLAS-A45 private Atlas lower-bound consolidation selector."""

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

from scripts import atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review as a44  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_atlas_lower_bound_consolidation_selector.v0"
STATUS = "ATLAS_A45_PRIVATE_ATLAS_LOWER_BOUND_CONSOLIDATION_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a45-private-atlas-lower-bound-consolidation-selector"
SOURCE_ARTIFACT_ID = "atlas-a44-private-trig-pythagorean-checked-wrapper-surface-review"
SELECTED_PATH_ID = "private_atlas_v0_reference_document_seed"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A46 private Atlas v0 reference document seed"

TRUE_CLAIM_FLAGS = {
    "atlas_a44_consumed",
    "lower_bound_observation_consumed",
    "consolidation_selector_created",
    "consolidation_paths_reviewed",
    "private_atlas_v0_seed_selected",
    "more_proof_branching_deferred",
    "public_promotion_blocked",
    "runtime_claims_blocked",
    "catalog_completeness_blocked",
    "next_reference_document_seed_recommended",
}

CLAIM_FLAGS = {
    "atlas_a44_consumed": True,
    "lower_bound_observation_consumed": True,
    "consolidation_selector_created": True,
    "consolidation_paths_reviewed": True,
    "private_atlas_v0_seed_selected": True,
    "more_proof_branching_deferred": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "catalog_completeness_blocked": True,
    "next_reference_document_seed_recommended": True,
    "atlas_document_created": False,
    "public_atlas_promotion": False,
    "public_copy_approved": False,
    "public_surface_updated": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "new_candidate_packet_created": False,
    "feasibility_packet_created": False,
    "candidate_selected_for_proof": False,
    "candidate_validity_claim": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
    "machlib_file_changed": False,
    "machlib_commit_created": False,
    "lean_typecheck_performed": False,
    "theorem_lookup_performed": False,
    "runtime_lowering_changed": False,
    "runtime_trig_replacement_claim": False,
    "runtime_exp_replacement_claim": False,
    "product_implementation_started": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "laptop_artifact_consumed": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "catalog_completeness_claim": False,
    "target_lower_bound_reached_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "ATLAS-A45 is a private selector only; it does not create the Atlas v0 document, publish anything, approve public copy, or create SDK/course material.",
    "ATLAS-A45 consumes the A44 lower-bound observation at fifteen private rows, but it does not claim catalog completeness, public readiness, target-lower-bound promotion, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
    "ATLAS-A45 does not start a new proof branch, create a candidate or feasibility packet, edit MachLib, run Lean, perform theorem lookup, change runtime lowering, consume reviewer responses, start D110, or touch laptop-owned repositories.",
]


def build_paths(source: dict[str, Any]) -> list[dict[str, Any]]:
    atlas_count = source["summary"]["atlasRowCount"]
    return [
        {
            "pathId": SELECTED_PATH_ID,
            "selectionStatus": "selected",
            "decision": "seed_private_atlas_v0_reference_document",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "rationale": [
                f"A44 preserves a private Atlas row count of {atlas_count}, meeting the stated lower-bound observation.",
                "A single private reference document will reduce cognitive load more than another selector/proof branch.",
                "The document can group checked witnesses, guards, non-claims, and future public/SDK/course hooks without promoting any public claim.",
            ],
            "blockedUntilLater": [
                "public copy approval",
                "SDK/compiler guard-note extraction",
                "course reference extraction",
                "public Atlas/public math promotion",
            ],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "pathId": "continue_new_bounded_proof_branch",
            "selectionStatus": "deferred",
            "decision": "defer_more_proof_branching_after_lower_bound_observed",
            "nextArtifact": "Future private candidate only after Atlas v0 seed/review",
            "rationale": [
                "More proof branches may still be useful, but the immediate leverage is consolidation.",
                "The 15-25 target is a cap and quality filter, not an invitation to keep branching by default.",
            ],
            "blockedUntilLater": ["candidate selection", "feasibility packet", "proof attempt", "MachLib edit"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "pathId": "public_witness_promotion",
            "selectionStatus": "held",
            "decision": "hold_public_surface_until_explicit_copy_gate",
            "nextArtifact": "Future public-copy approval gate only after explicit human approval",
            "rationale": [
                "Public copy already has separate PUBMATH hold gates.",
                "A45 is not a publication or public-readiness decision.",
            ],
            "blockedUntilLater": ["public copy approval", "monogate-dev edit", "monogate.org promotion"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
        {
            "pathId": "product_or_course_extraction",
            "selectionStatus": "held",
            "decision": "hold_product_course_sdk_extraction_until_atlas_v0_seed_exists",
            "nextArtifact": "Future private extraction selector after Atlas v0 seed/review",
            "rationale": [
                "SDK, compiler, course, and product notes should cite a coherent private reference document, not scattered packets.",
                "No product implementation or course material is created by this selector.",
            ],
            "blockedUntilLater": ["SDK/compiler docs", "course material", "product implementation"],
            "claimFlags": dict(CLAIM_FLAGS),
        },
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a44.build_payload(atlas_gate_path, machlib_root)
    a44.validate_payload(source)
    paths = build_paths(source)
    selected = next(path for path in paths if path["pathId"] == SELECTED_PATH_ID)
    source_summary = source["summary"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceAtlasRowCount": source_summary["atlasRowCount"],
        "sourceAdditionalArtifactsNeededForLowerBound": source_summary[
            "additionalArtifactsNeededForLowerBound"
        ],
        "sourceTargetLowerBoundReached": source_summary["targetLowerBoundReached"],
        "lowerBoundObservationConsumed": True,
        "consolidationSelectorCreated": True,
        "consolidationPathsReviewed": True,
        "pathCount": len(paths),
        "selectedPathId": selected["pathId"],
        "selectedDecision": selected["decision"],
        "privateAtlasV0SeedSelected": True,
        "moreProofBranchingDeferred": True,
        "atlasDocumentCreated": False,
        "newCandidatePacketCreated": False,
        "feasibilityPacketCreated": False,
        "candidateSelectedForProof": False,
        "candidateValidityClaim": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "machlibFileChanged": False,
        "machlibCommitCreated": False,
        "leanTypecheckPerformed": False,
        "theoremLookupPerformed": False,
        "runtimeLoweringChanged": False,
        "runtimeTrigReplacementClaim": False,
        "runtimeExpReplacementClaim": False,
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "productImplementationStarted": False,
        "atlasRowCount": source_summary["atlasRowCount"],
        "targetMin": source_summary["targetMin"],
        "targetMax": source_summary["targetMax"],
        "targetLowerBoundReached": source_summary["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source_summary[
            "additionalArtifactsNeededForLowerBound"
        ],
        "catalogCompletenessBlocked": True,
        "catalogCompletenessClaim": False,
        "targetLowerBoundReachedClaim": False,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_atlas_lower_bound_consolidation_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "consolidationPaths": paths,
            "selectedPath": selected,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    for path in payload["consolidationPaths"]:
        assert_claim_flags_bounded(path["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != SOURCE_ARTIFACT_ID:
        raise ValueError("ATLAS-A45 must consume ATLAS-A44")
    if summary["selectedPathId"] != SELECTED_PATH_ID:
        raise ValueError("selected path drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["pathCount"] != 4:
        raise ValueError("expected four consolidation paths")
    for key in [
        "sourceTargetLowerBoundReached",
        "lowerBoundObservationConsumed",
        "consolidationSelectorCreated",
        "consolidationPathsReviewed",
        "privateAtlasV0SeedSelected",
        "moreProofBranchingDeferred",
        "catalogCompletenessBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "atlasDocumentCreated",
        "newCandidatePacketCreated",
        "feasibilityPacketCreated",
        "candidateSelectedForProof",
        "candidateValidityClaim",
        "candidateProved",
        "proofAttemptStarted",
        "machlibFileChanged",
        "machlibCommitCreated",
        "leanTypecheckPerformed",
        "theoremLookupPerformed",
        "runtimeLoweringChanged",
        "runtimeTrigReplacementClaim",
        "runtimeExpReplacementClaim",
        "publicPromotionAllowed",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "productImplementationStarted",
        "catalogCompletenessClaim",
        "targetLowerBoundReachedClaim",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["atlasRowCount"] != 15:
        raise ValueError("Atlas row count drift")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target drift")
    if summary["targetLowerBoundReached"] is not True:
        raise ValueError("target lower bound observation should remain true")
    if summary["additionalArtifactsNeededForLowerBound"] != 0:
        raise ValueError("expected no additional artifact for lower bound")
    for key in set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_atlas_lower_bound_consolidation_selector",
        semantic_strength="private_selector_only_lower_bound_observed_atlas_v0_seed_recommended_no_public_runtime_product_claims",
        source=f"python/results/atlas_a45_private_atlas_lower_bound_consolidation_selector/atlas_a45_private_atlas_lower_bound_consolidation_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a45_private_atlas_lower_bound_consolidation_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A46 as a private Atlas v0 reference document seed; do not publish, create SDK/course copy, start proof work, edit MachLib, run Lean, or claim catalog completeness.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedPathId": payload["summary"]["selectedPathId"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "additionalArtifactsNeededForLowerBound": payload["summary"][
                "additionalArtifactsNeededForLowerBound"
            ],
            "catalogCompletenessClaim": payload["summary"]["catalogCompletenessClaim"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("selected path", payload["summary"]["selectedPathId"]),
        ("selected decision", payload["summary"]["selectedDecision"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("Atlas document created", payload["summary"]["atlasDocumentCreated"]),
        ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ("catalog completeness claim", payload["summary"]["catalogCompletenessClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    path_lines = [
        f"- `{path['pathId']}`: {path['selectionStatus']} -> {path['decision']}"
        for path in payload["consolidationPaths"]
    ]
    blocked_lines = [
        "- Atlas v0 document is not created until A46",
        "- public copy and public/dev promotion remain blocked",
        "- SDK/compiler/course extraction remains blocked",
        "- proof branches, MachLib edits, Lean checks, and theorem lookup remain blocked",
        "- catalog completeness and target-lower-bound promotion claims remain blocked",
    ]
    return render_markdown_report(
        title="ATLAS-A45 Private Atlas Lower-Bound Consolidation Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Consolidation Paths", path_lines),
            ("Blocked Follow-Ups", blocked_lines),
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
    result_path = out_dir / f"atlas_a45_private_atlas_lower_bound_consolidation_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a45_private_atlas_lower_bound_consolidation_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a45_private_atlas_lower_bound_consolidation_selector.json"
    feed_path = command_feed_dir / f"atlas_a45_private_atlas_lower_bound_consolidation_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a45_private_atlas_lower_bound_consolidation_selector",
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
    print("ATLAS_A45_PRIVATE_ATLAS_LOWER_BOUND_CONSOLIDATION_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
