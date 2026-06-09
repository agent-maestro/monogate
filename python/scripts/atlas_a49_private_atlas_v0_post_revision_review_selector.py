#!/usr/bin/env python3
"""ATLAS-A49 private Atlas v0 post-revision review selector."""

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
from scripts import atlas_a48_private_atlas_v0_row_wording_revision_packet as a48  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_atlas_v0_post_revision_review_selector.v0"
STATUS = "ATLAS_A49_PRIVATE_ATLAS_V0_POST_REVISION_REVIEW_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a49-private-atlas-v0-post-revision-review-selector"
SOURCE_ARTIFACT_ID = "atlas-a48-private-atlas-v0-row-wording-revision-packet"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A50 private Atlas v0 reviewer handoff packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a48_consumed",
    "post_revision_review_performed",
    "row_count_preserved",
    "private_reviewer_handoff_recommended",
    "public_promotion_blocked",
    "runtime_claims_blocked",
    "catalog_completeness_blocked",
    "next_reviewer_handoff_recommended",
}

CLAIM_FLAGS = {
    "atlas_a48_consumed": True,
    "post_revision_review_performed": True,
    "row_count_preserved": True,
    "private_reviewer_handoff_recommended": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "catalog_completeness_blocked": True,
    "next_reviewer_handoff_recommended": True,
    "atlas_row_added": False,
    "atlas_row_removed": False,
    "row_wording_changed": False,
    "private_reference_document_changed": False,
    "private_reviewer_response_consumed": False,
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
    "runtime_replacement_claim": False,
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
    "ATLAS-A49 reviews the A48-revised private Atlas seed and recommends a private reviewer handoff; it does not publish, approve public copy, update public/dev surfaces, or create SDK/course material.",
    "ATLAS-A49 preserves the fifteen-row private Atlas seed but does not claim catalog completeness, target-lower-bound promotion, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
    "ATLAS-A49 does not edit the private seed, add or remove rows, start proof work, create candidate or feasibility packets, edit MachLib, run Lean, perform theorem lookup, change runtime lowering, consume reviewer responses, start D110, or touch laptop-owned repositories.",
]


def count_table_rows(document_text: str) -> int:
    return sum(
        1
        for line in document_text.splitlines()
        if line.startswith("| ") and "| `MachLib.Real." in line
    )


def count_review_questions(document_text: str) -> int:
    in_section = False
    count = 0
    for line in document_text.splitlines():
        if line == "## Next Review Questions":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- "):
            count += 1
    return count


def build_payload(
    atlas_gate_path: Path,
    machlib_root: Path,
    atlas_a1_path: Path = a46.ATLAS_A1_PATH,
    doc_path: Path = ROOT / a46.PRIVATE_DOC_PATH,
) -> dict[str, Any]:
    source = a48.build_payload(atlas_gate_path, machlib_root, atlas_a1_path, doc_path)
    a48.validate_payload(source)
    document_text = doc_path.read_text(encoding="utf-8")
    review_signals = [
        "fifteen private rows remain present",
        "A48 revised runtime-boundary wording is present",
        "next-review questions remain explicit",
        "public and catalog-completeness non-claims remain present",
    ]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "documentPath": source["summary"]["documentPath"],
        "postRevisionReviewPerformed": True,
        "privateReviewerHandoffRecommended": True,
        "recommendedPath": "private_reviewer_handoff_before_public_or_sdk_extraction",
        "atlasRowCount": count_table_rows(document_text),
        "rowCountPreserved": count_table_rows(document_text) == source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "reviewQuestionCount": count_review_questions(document_text),
        "revisedRuntimeWordingPresent": source["summary"]["revisedPhraseCount"] >= 4,
        "staleInternalRuntimePhraseCount": source["summary"]["staleInternalRuntimePhraseCount"],
        "atlasRowAdded": False,
        "atlasRowRemoved": False,
        "rowWordingChanged": False,
        "privateReferenceDocumentChanged": False,
        "catalogCompletenessBlocked": True,
        "catalogCompletenessClaim": False,
        "targetLowerBoundReachedClaim": False,
        "privateReviewerResponseConsumed": False,
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
        "runtimeReplacementClaim": False,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_atlas_v0_post_revision_review_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "reviewSignals": review_signals,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != SOURCE_ARTIFACT_ID:
        raise ValueError("ATLAS-A49 must consume ATLAS-A48")
    if summary["documentPath"] != a46.PRIVATE_DOC_PATH:
        raise ValueError("document path drift")
    if summary["atlasRowCount"] != 15 or summary["rowCountPreserved"] is not True:
        raise ValueError("expected fifteen preserved rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["additionalArtifactsNeededForLowerBound"] != 0:
        raise ValueError("expected no additional artifact for lower-bound observation")
    if summary["reviewQuestionCount"] < 4:
        raise ValueError("expected private review questions to remain explicit")
    if summary["revisedRuntimeWordingPresent"] is not True:
        raise ValueError("expected revised runtime wording")
    if summary["staleInternalRuntimePhraseCount"] != 0:
        raise ValueError("stale internal runtime phrase remains")
    for key in [
        "postRevisionReviewPerformed",
        "privateReviewerHandoffRecommended",
        "rowCountPreserved",
        "catalogCompletenessBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "atlasRowAdded",
        "atlasRowRemoved",
        "rowWordingChanged",
        "privateReferenceDocumentChanged",
        "catalogCompletenessClaim",
        "targetLowerBoundReachedClaim",
        "privateReviewerResponseConsumed",
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
        "runtimeReplacementClaim",
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
        artifact_type="private_atlas_v0_post_revision_review_selector",
        semantic_strength="private_post_revision_review_selector_only_no_public_completeness_runtime_product_claims",
        source=f"python/results/atlas_a49_private_atlas_v0_post_revision_review_selector/atlas_a49_private_atlas_v0_post_revision_review_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a49_private_atlas_v0_post_revision_review_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A50 as a private Atlas v0 reviewer handoff packet; do not publish, extract SDK/course copy, start proof work, edit MachLib, run Lean, or claim catalog completeness.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "documentPath": payload["summary"]["documentPath"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "rowCountPreserved": payload["summary"]["rowCountPreserved"],
            "reviewQuestionCount": payload["summary"]["reviewQuestionCount"],
            "recommendedPath": payload["summary"]["recommendedPath"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("document path", payload["summary"]["documentPath"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("row count preserved", payload["summary"]["rowCountPreserved"]),
        ("review question count", payload["summary"]["reviewQuestionCount"]),
        ("recommended path", payload["summary"]["recommendedPath"]),
        ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ("catalog completeness claim", payload["summary"]["catalogCompletenessClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    review_lines = [f"- {signal}" for signal in payload["reviewSignals"]]
    blocked_lines = [
        "- public copy and public/dev promotion remain blocked",
        "- SDK/compiler/course extraction remains blocked",
        "- proof branches, MachLib edits, Lean checks, and theorem lookup remain blocked",
        "- reviewer response consumption remains blocked until actual response text exists",
        "- catalog completeness and target-lower-bound promotion claims remain blocked",
    ]
    return render_markdown_report(
        title="ATLAS-A49 Private Atlas v0 Post-Revision Review Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Review Signals", review_lines),
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
    result_path = out_dir / f"atlas_a49_private_atlas_v0_post_revision_review_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a49_private_atlas_v0_post_revision_review_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a49_private_atlas_v0_post_revision_review_selector.json"
    feed_path = command_feed_dir / f"atlas_a49_private_atlas_v0_post_revision_review_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a49_private_atlas_v0_post_revision_review_selector",
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
    print("ATLAS_A49_PRIVATE_ATLAS_V0_POST_REVISION_REVIEW_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
