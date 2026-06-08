#!/usr/bin/env python3
"""ATLAS-A47 private Atlas v0 reference document review selector."""

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

from scripts import atlas_a46_private_atlas_v0_reference_document_seed as a46  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_atlas_v0_reference_document_review_selector.v0"
STATUS = "ATLAS_A47_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_REVIEW_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a47-private-atlas-v0-reference-document-review-selector"
SOURCE_ARTIFACT_ID = "atlas-a46-private-atlas-v0-reference-document-seed"
SELECTED_REVIEW_PATH_ID = "private_row_wording_revision_before_public_or_sdk_extraction"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A48 private Atlas v0 row wording revision packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a46_consumed",
    "private_reference_document_inspected",
    "review_selector_created",
    "review_rows_recorded",
    "private_row_wording_revision_recommended",
    "public_promotion_blocked",
    "runtime_claims_blocked",
    "catalog_completeness_blocked",
    "next_private_revision_packet_recommended",
}

CLAIM_FLAGS = {
    "atlas_a46_consumed": True,
    "private_reference_document_inspected": True,
    "review_selector_created": True,
    "review_rows_recorded": True,
    "private_row_wording_revision_recommended": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "catalog_completeness_blocked": True,
    "next_private_revision_packet_recommended": True,
    "document_changed": False,
    "atlas_row_added": False,
    "atlas_row_removed": False,
    "public_atlas_promotion": False,
    "public_copy_approved": False,
    "public_surface_updated": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "product_implementation_started": False,
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
    "ATLAS-A47 is a private review selector over the A46 Atlas seed; it does not edit the seed document, add or remove rows, publish anything, approve public copy, or create SDK/course material.",
    "ATLAS-A47 recommends a private row-wording revision packet before any public or SDK/course extraction; it does not claim catalog completeness, public readiness, target-lower-bound promotion, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
    "ATLAS-A47 does not start proof work, create candidate or feasibility packets, edit MachLib, run Lean, perform theorem lookup, change runtime lowering, consume reviewer responses, start D110, or touch laptop-owned repositories.",
]


def review_row(
    review_id: str,
    status: str,
    action: str,
    rationale: list[str],
    blocked_claims: list[str],
) -> dict[str, Any]:
    return {
        "reviewId": review_id,
        "status": status,
        "recommendedAction": action,
        "rationale": rationale,
        "blockedClaims": blocked_claims,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_review_rows(source: dict[str, Any], document_text: str) -> list[dict[str, Any]]:
    summary = source["summary"]
    return [
        review_row(
            "row_count_and_source_integrity",
            "reviewed_ok",
            "keep_fifteen_private_rows",
            [
                f"A46 records {summary['atlasRowCount']} private rows.",
                "The seed includes thirteen A1 rows plus the A33 and A43 wrapper rows.",
                "No row-addition or row-removal action is recommended in A47.",
            ],
            ["catalog completeness", "target-lower-bound promotion"],
        ),
        review_row(
            "non_claim_boundary",
            "reviewed_ok",
            "retain_non_claim_section",
            [
                "The seed explicitly says it is not public copy.",
                "The seed blocks public Atlas, completeness, runtime replacement, compiler correctness, and formal equivalence claims.",
                f"Non-claim phrase present: {'No public Atlas or public math page is created by this seed.' in document_text}",
            ],
            ["public readiness", "public copy approval", "formal equivalence"],
        ),
        review_row(
            "row_wording_readability",
            "private_revision_recommended",
            "polish_row_wording_before_any_extraction",
            [
                "Several runtime and guard cells still use internal underscore-style labels.",
                "The row table is reviewable, but a private wording pass would make it more useful for future SDK/course/public-copy gates.",
                "A47 recommends a wording revision packet rather than publishing or extracting from the seed as-is.",
            ],
            ["public copy", "SDK/compiler docs", "course material"],
        ),
        review_row(
            "public_surface_path",
            "held",
            "require_explicit_public_copy_gate_after_private_revision",
            [
                "Public witness promotion remains a separate lane.",
                "A47 does not select a public page, public Atlas, or monogate-dev edit.",
            ],
            ["public Atlas promotion", "public/dev surface update", "public readiness"],
        ),
        review_row(
            "proof_and_runtime_path",
            "held",
            "do_not_restart_proof_or_runtime_work_from_review_selector",
            [
                "The Atlas seed is a reference consolidation artifact.",
                "No proof branch, theorem lookup, Lean check, MachLib edit, or runtime lowering is needed for this review selector.",
            ],
            ["new proof", "runtime replacement", "compiler correctness"],
        ),
    ]


def build_payload(
    atlas_gate_path: Path,
    machlib_root: Path,
    atlas_a1_path: Path = a46.ATLAS_A1_PATH,
    doc_path: Path = ROOT / a46.PRIVATE_DOC_PATH,
) -> dict[str, Any]:
    source = a46.build_payload(atlas_gate_path, machlib_root, atlas_a1_path)
    a46.validate_payload(source)
    document_text = doc_path.read_text(encoding="utf-8")
    review_rows = build_review_rows(source, document_text)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "documentPath": source["summary"]["documentPath"],
        "privateReferenceDocumentInspected": True,
        "reviewSelectorCreated": True,
        "reviewRowsRecorded": True,
        "reviewRowCount": len(review_rows),
        "selectedReviewPathId": SELECTED_REVIEW_PATH_ID,
        "selectedDecision": "recommend_private_row_wording_revision_packet",
        "privateRowWordingRevisionRecommended": True,
        "documentChanged": False,
        "atlasRowAdded": False,
        "atlasRowRemoved": False,
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "catalogCompletenessBlocked": True,
        "catalogCompletenessClaim": False,
        "targetLowerBoundReachedClaim": False,
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "productImplementationStarted": False,
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
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_atlas_v0_reference_document_review_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "reviewRows": review_rows,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    for row in payload["reviewRows"]:
        assert_claim_flags_bounded(row["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != SOURCE_ARTIFACT_ID:
        raise ValueError("ATLAS-A47 must consume ATLAS-A46")
    if summary["documentPath"] != a46.PRIVATE_DOC_PATH:
        raise ValueError("document path drift")
    if summary["selectedReviewPathId"] != SELECTED_REVIEW_PATH_ID:
        raise ValueError("selected review path drift")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    if summary["reviewRowCount"] != 5:
        raise ValueError("expected five review rows")
    if summary["atlasRowCount"] != 15:
        raise ValueError("Atlas row count drift")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not True:
        raise ValueError("lower-bound observation should remain true")
    if summary["additionalArtifactsNeededForLowerBound"] != 0:
        raise ValueError("expected no additional artifact for lower-bound observation")
    for key in [
        "privateReferenceDocumentInspected",
        "reviewSelectorCreated",
        "reviewRowsRecorded",
        "privateRowWordingRevisionRecommended",
        "catalogCompletenessBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "documentChanged",
        "atlasRowAdded",
        "atlasRowRemoved",
        "catalogCompletenessClaim",
        "targetLowerBoundReachedClaim",
        "publicPromotionAllowed",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "productImplementationStarted",
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
        artifact_type="private_atlas_v0_reference_document_review_selector",
        semantic_strength="private_review_selector_recommends_row_wording_revision_no_public_completeness_runtime_product_claims",
        source=f"python/results/atlas_a47_private_atlas_v0_reference_document_review_selector/atlas_a47_private_atlas_v0_reference_document_review_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a47_private_atlas_v0_reference_document_review_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A48 as a private Atlas v0 row wording revision packet; do not publish, extract SDK/course copy, start proof work, edit MachLib, run Lean, or claim catalog completeness.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "documentPath": payload["summary"]["documentPath"],
            "reviewRowCount": payload["summary"]["reviewRowCount"],
            "selectedReviewPathId": payload["summary"]["selectedReviewPathId"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "documentChanged": payload["summary"]["documentChanged"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("document path", payload["summary"]["documentPath"]),
        ("review rows", payload["summary"]["reviewRowCount"]),
        ("selected review path", payload["summary"]["selectedReviewPathId"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("document changed", payload["summary"]["documentChanged"]),
        ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ("catalog completeness claim", payload["summary"]["catalogCompletenessClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    review_lines = [
        f"- `{row['reviewId']}`: {row['status']} -> {row['recommendedAction']}"
        for row in payload["reviewRows"]
    ]
    blocked_lines = [
        "- seed document is not edited until A48",
        "- public copy and public/dev promotion remain blocked",
        "- SDK/compiler/course extraction remains blocked",
        "- proof branches, MachLib edits, Lean checks, and theorem lookup remain blocked",
        "- catalog completeness and target-lower-bound promotion claims remain blocked",
    ]
    return render_markdown_report(
        title="ATLAS-A47 Private Atlas v0 Reference Document Review Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Review Rows", review_lines),
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
    atlas_a1_path: Path,
    doc_path: Path,
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path, machlib_root, atlas_a1_path, doc_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"atlas_a47_private_atlas_v0_reference_document_review_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a47_private_atlas_v0_reference_document_review_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a47_private_atlas_v0_reference_document_review_selector.json"
    feed_path = command_feed_dir / f"atlas_a47_private_atlas_v0_reference_document_review_selector_feed_{STAMP}.json"
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
    parser.add_argument("--atlas-a1-path", type=Path, default=a46.ATLAS_A1_PATH)
    parser.add_argument("--doc-path", type=Path, default=ROOT / a46.PRIVATE_DOC_PATH)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/atlas_a47_private_atlas_v0_reference_document_review_selector",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.atlas_gate_path, args.machlib_root, args.atlas_a1_path, args.doc_path)
    validate_payload(payload)
    if args.build:
        build_outputs(
            args.out_dir,
            args.report_dir,
            args.evidence_dir,
            args.command_feed_dir,
            args.atlas_gate_path,
            args.machlib_root,
            args.atlas_a1_path,
            args.doc_path,
        )
    print("ATLAS_A47_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_REVIEW_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
