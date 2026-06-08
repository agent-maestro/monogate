#!/usr/bin/env python3
"""ATLAS-A44 private trig pythagorean checked-wrapper surface review."""

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

from scripts import atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact as a43  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_trig_pythagorean_checked_wrapper_surface_review.v0"
STATUS = "ATLAS_A44_PRIVATE_TRIG_PYTHAGOREAN_CHECKED_WRAPPER_SURFACE_REVIEW_PASS"
ARTIFACT_ID = "atlas-a44-private-trig-pythagorean-checked-wrapper-surface-review"
SOURCE_ARTIFACT_ID = "atlas-a43-private-trig-pythagorean-bounded-wrapper-attempt-artifact"
MACHLIB_NAME = a43.MACHLIB_NAME
MACHLIB_FILE = a43.MACHLIB_FILE
DEPENDENCY_IDENTIFIER = a43.DEPENDENCY_IDENTIFIER
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A45 private Atlas lower-bound consolidation selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a43_consumed",
    "surface_review_created",
    "checked_wrapper_surface_reviewed",
    "private_atlas_row_reviewed",
    "candidate_proved_by_source_phase",
    "lean_typecheck_passed_by_source_phase",
    "machlib_dependency_identifier_recorded",
    "eml_companion_kept_deferred",
    "public_promotion_blocked",
    "runtime_claims_blocked",
    "next_lower_bound_selector_recommended",
    "target_lower_bound_observed",
}

CLAIM_FLAGS = {
    "atlas_a43_consumed": True,
    "surface_review_created": True,
    "checked_wrapper_surface_reviewed": True,
    "private_atlas_row_reviewed": True,
    "candidate_proved_by_source_phase": True,
    "lean_typecheck_passed_by_source_phase": True,
    "machlib_dependency_identifier_recorded": True,
    "eml_companion_kept_deferred": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "next_lower_bound_selector_recommended": True,
    "target_lower_bound_observed": True,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "runtime_lowering_changed": False,
    "runtime_trig_replacement_claim": False,
    "public_atlas_promotion": False,
    "public_copy_approved": False,
    "public_surface_updated": False,
    "public_education_promotion": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
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
    "ATLAS-A44 is a private surface review over the checked A43 wrapper; it does not edit MachLib, run Lean, or prove a new theorem.",
    "The reviewed surface is one pure trig Pythagorean wrapper identity; it does not claim a checked EML-shaped companion theorem, formal equivalence to EML semantics, runtime replacement, compiler correctness, or broad EML advantage.",
    "ATLAS-A44 records that the private Atlas lower bound is observed at fifteen rows, but it does not claim catalog completeness, public readiness, or target-lower-bound promotion.",
    "ATLAS-A44 does not approve public copy, update public/dev surfaces, create SDK/compiler/course material, consume reviewer responses, start D110, or touch laptop-owned repositories.",
]


def surface_row(
    surface_id: str,
    surface_kind: str,
    status: str,
    action: str,
    rationale: list[str],
    blocked_claims: list[str],
) -> dict[str, Any]:
    return {
        "surfaceId": surface_id,
        "surfaceKind": surface_kind,
        "surfaceStatus": status,
        "recommendedAction": action,
        "rationale": rationale,
        "blockedClaims": blocked_claims,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_surface_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    summary = source["summary"]
    return [
        surface_row(
            "private_atlas_row_trig_pythagorean_wrapper",
            "private_atlas_row",
            "reviewed_as_checked_wrapper_row",
            "keep_as_private_atlas_row_candidate",
            [
                f"A43 records `{summary['machlibName']}`.",
                f"The checked statement is `{summary['checkedStatement']}`.",
                "The surface adds trig-identity shape diversity without adding guards.",
            ],
            ["public Atlas promotion", "catalog completeness", "target lower bound reached"],
        ),
        surface_row(
            "dependency_identifier_boundary",
            "proof_dependency_boundary",
            "dependency_identifier_recorded",
            "retain_dependency_identifier_as_private_review_metadata",
            [
                f"A43 uses `{summary['dependencyIdentifier']}`.",
                "The dependency is a local MachLib trig theorem used to close the wrapper.",
                "Future reviewer-facing copy should name the wrapper theorem, not overstate the dependency as a public contract.",
            ],
            ["public proof-dependency contract", "unchecked theorem-name claim"],
        ),
        surface_row(
            "eml_companion_deferred_boundary",
            "eml_companion_boundary",
            "companion_hint_deferred",
            "keep_eml_companion_out_of_checked_claims",
            [
                f"The deferred companion hint remains `{summary['deferredCompanionStatement']}`.",
                "A43 proves only the pure real trig identity wrapper.",
                "No formal bridge from the companion hint to EML semantics is claimed.",
            ],
            ["checked EML companion", "formal EML equivalence", "full EML semantics"],
        ),
        surface_row(
            "runtime_control_guardrail",
            "runtime_control_guardrail",
            "standard_trig_runtime_control_preserved",
            "keep_standard_trig_as_runtime_control",
            [
                f"A43 records runtime control as `{summary['runtimeControl']}`.",
                "The witness is useful as proof/reference material, not a runtime replacement.",
                "No trig lowering, performance, or compiler behavior changed.",
            ],
            ["runtime trig replacement", "runtime performance", "compiler correctness"],
        ),
        surface_row(
            "public_surface_guardrail",
            "public_surface",
            "held_private",
            "require_explicit_public_copy_gate_before_public_use",
            [
                "The wrapper is private-review evidence only.",
                "No public math page, SDK note, course reference, or dev route is updated by A44.",
                "Any future public use needs a separate copy gate that preserves the non-claims.",
            ],
            ["public readiness", "public copy approval", "public/dev surface update"],
        ),
    ]


def build_payload(atlas_gate_path: Path, machlib_root: Path) -> dict[str, Any]:
    source = a43.build_payload(atlas_gate_path, machlib_root)
    a43.validate_payload(source)
    surface_rows = build_surface_rows(source)
    source_summary = source["summary"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "machlibName": source_summary["machlibName"],
        "machlibFile": source_summary["machlibFile"],
        "checkedStatement": source_summary["checkedStatement"],
        "dependencyIdentifier": source_summary["dependencyIdentifier"],
        "sourceLeanTypecheckPassed": source_summary["leanTypecheckPassed"],
        "sourceCandidateProvedThisPhase": source_summary["candidateProvedThisPhase"],
        "surfaceReviewCreated": True,
        "checkedWrapperSurfaceReviewed": True,
        "privateAtlasRowReviewed": True,
        "surfaceRowCount": len(surface_rows),
        "guardSummary": "all_real_no_extra_guard",
        "shapeDiversity": "pure_trig_pythagorean_unit_identity",
        "representationalUsefulness": "private_reference_for_trig_identity_guard_notes_only",
        "futureLeverage": [
            "private Atlas row",
            "possible guarded SDK note after separate copy gate",
            "possible course reference after separate course gate",
        ],
        "emlCompanionKeptDeferred": True,
        "deferredCompanionStatement": source_summary["deferredCompanionStatement"],
        "runtimeControl": source_summary["runtimeControl"],
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "runtimeTrigReplacementClaim": False,
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "atlasRowCount": source_summary["atlasRowCount"],
        "targetMin": source_summary["targetMin"],
        "targetMax": source_summary["targetMax"],
        "targetLowerBoundReached": source_summary["targetLowerBoundReached"],
        "targetLowerBoundObserved": source_summary["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source_summary["additionalArtifactsNeededForLowerBound"],
        "catalogCompletenessClaim": False,
        "targetLowerBoundReachedClaim": False,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_trig_pythagorean_checked_wrapper_surface_review",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceCheckedWrapperWitness": source["checkedWrapperWitness"],
            "surfaceRows": surface_rows,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    for row in payload["surfaceRows"]:
        assert_claim_flags_bounded(row["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != SOURCE_ARTIFACT_ID:
        raise ValueError("ATLAS-A44 must consume ATLAS-A43")
    if summary["machlibName"] != MACHLIB_NAME:
        raise ValueError("MachLib name drift")
    if summary["machlibFile"] != MACHLIB_FILE:
        raise ValueError("MachLib file drift")
    if summary["checkedStatement"] != "forall x : Real, Real.sin x * Real.sin x + Real.cos x * Real.cos x = 1":
        raise ValueError("checked statement drift")
    if summary["dependencyIdentifier"] != DEPENDENCY_IDENTIFIER:
        raise ValueError("dependency drift")
    if summary["guardSummary"] != "all_real_no_extra_guard":
        raise ValueError("guard summary drift")
    if summary["surfaceRowCount"] != 5:
        raise ValueError("expected five surface rows")
    for key in [
        "sourceLeanTypecheckPassed",
        "sourceCandidateProvedThisPhase",
        "surfaceReviewCreated",
        "checkedWrapperSurfaceReviewed",
        "privateAtlasRowReviewed",
        "emlCompanionKeptDeferred",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "runtimeTrigReplacementClaim",
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
    if summary["atlasRowCount"] != 15:
        raise ValueError("Atlas row count drift")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target drift")
    if summary["targetLowerBoundReached"] is not True:
        raise ValueError("target lower bound should be observed")
    if summary["targetLowerBoundObserved"] is not True:
        raise ValueError("target lower bound observation should be true")
    if summary["additionalArtifactsNeededForLowerBound"] != 0:
        raise ValueError("expected no additional bounded artifact for lower bound")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("next artifact drift")
    for key in set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_trig_pythagorean_checked_wrapper_surface_review",
        semantic_strength="private_surface_review_over_checked_wrapper_no_new_proof_public_runtime_product_claims_blocked",
        source=f"python/results/atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review/atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A45 as a private lower-bound consolidation selector; do not start proof, public, runtime, product, or course work without a new gate.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "machlibName": payload["summary"]["machlibName"],
            "surfaceRowCount": payload["summary"]["surfaceRowCount"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "additionalArtifactsNeededForLowerBound": payload["summary"]["additionalArtifactsNeededForLowerBound"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "runtimeTrigReplacementClaim": payload["summary"]["runtimeTrigReplacementClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("MachLib name", payload["summary"]["machlibName"]),
        ("MachLib file", payload["summary"]["machlibFile"]),
        ("checked statement", payload["summary"]["checkedStatement"]),
        ("dependency identifier", payload["summary"]["dependencyIdentifier"]),
        ("guard summary", payload["summary"]["guardSummary"]),
        ("surface row count", payload["summary"]["surfaceRowCount"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ("runtime trig replacement claim", payload["summary"]["runtimeTrigReplacementClaim"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    surface_lines = [
        f"- `{row['surfaceId']}`: {row['surfaceStatus']} -> {row['recommendedAction']}"
        for row in payload["surfaceRows"]
    ]
    blocked_lines = [
        "- checked EML companion theorem remains blocked",
        "- formal EML equivalence remains blocked",
        "- runtime replacement and performance claims remain blocked",
        "- public copy, SDK notes, and course references remain blocked",
    ]
    return render_markdown_report(
        title="ATLAS-A44 Private Trig Pythagorean Checked-Wrapper Surface Review",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Surface Rows", surface_lines),
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
    result_path = out_dir / f"atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review_{STAMP}.json"
    report_path = report_dir / f"atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review.json"
    feed_path = command_feed_dir / f"atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review_feed_{STAMP}.json"
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
        default=ROOT / "python/results/atlas_a44_private_trig_pythagorean_checked_wrapper_surface_review",
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
    print("ATLAS_A44_PRIVATE_TRIG_PYTHAGOREAN_CHECKED_WRAPPER_SURFACE_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
