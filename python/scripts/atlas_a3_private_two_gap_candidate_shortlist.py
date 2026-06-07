#!/usr/bin/env python3
"""ATLAS-A3 private two-gap candidate shortlist."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a2_private_gap_review_pause_selector as a2  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_two_gap_candidate_shortlist.v0"
STATUS = "ATLAS_A3_PRIVATE_TWO_GAP_CANDIDATE_SHORTLIST_PASS"
ARTIFACT_ID = "atlas-a3-private-two-gap-candidate-shortlist"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A4 private two-gap feasibility selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a2_consumed",
    "private_shortlist_created",
    "two_gap_entries_recorded",
    "material_diversity_recorded",
    "candidate_validity_blocked",
    "public_promotion_blocked",
    "next_private_selector_recommended",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a2_consumed": True,
    "private_shortlist_created": True,
    "two_gap_entries_recorded": True,
    "material_diversity_recorded": True,
    "candidate_validity_blocked": True,
    "public_promotion_blocked": True,
    "next_private_selector_recommended": True,
    "d109_hold_respected": True,
    "shortlist_entries_are_checked_witnesses": False,
    "candidate_validity_claim": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "feasibility_packet_created": False,
    "proof_attempt_started": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "runtime_lowering_changed": False,
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
    "ATLAS-A3 is a private shortlist over the ATLAS-A2 gap slots; shortlist entries are not checked witnesses and do not satisfy the Atlas target lower bound.",
    "ATLAS-A3 records two plausible, materially distinct gap entries for later feasibility review; it does not claim either entry is valid, provable, selected for proof, implemented, or ready for public explanation.",
    "ATLAS-A3 does not edit MachLib, run Lean, start proof work, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def shortlist_entry(
    entry_id: str,
    source_gap_slot_id: str,
    family_hint: str,
    candidate_label: str,
    eml_shape_hint: str,
    guard_hint: str,
    runtime_control_hint: str,
    why_materially_distinct: list[str],
    feasibility_questions: list[str],
) -> dict[str, Any]:
    return {
        "entryId": entry_id,
        "sourceGapSlotId": source_gap_slot_id,
        "status": "private_shortlist_entry_not_checked_not_selected_for_proof",
        "familyHint": family_hint,
        "candidateLabel": candidate_label,
        "emlShapeHint": eml_shape_hint,
        "guardHint": guard_hint,
        "runtimeControlHint": runtime_control_hint,
        "whyMateriallyDistinct": why_materially_distinct,
        "feasibilityQuestions": feasibility_questions,
        "blockedClaims": [
            "not a checked witness",
            "not selected as a proof branch",
            "no candidate validity claim",
            "no MachLib edit",
            "no Lean typecheck",
            "no runtime lowering change",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_shortlist(source: dict[str, Any]) -> list[dict[str, Any]]:
    slot_ids = [slot["slotId"] for slot in source["gapSlots"]]
    return [
        shortlist_entry(
            "reciprocal_positive_boundary_candidate",
            slot_ids[0],
            "reciprocal_boundary",
            "guarded positive reciprocal boundary",
            "0 < x -> eml (x * (1 / x)) 1 = 1",
            "0 < x",
            "division/reciprocal remains runtime control",
            [
                "non-log and non-subtraction family",
                "explicit positivity guard",
                "familiar algebraic boundary with small public-review footprint",
            ],
            [
                "Is the EML-shaped statement the right boundary form for reciprocal/division?",
                "Can the guard be kept as 0 < x without extra denominator caveats?",
                "Would this add real Atlas diversity rather than another elementary algebra row?",
            ],
        ),
        shortlist_entry(
            "sqrt_square_nonnegative_roundtrip_candidate",
            slot_ids[1],
            "sqrt_boundary",
            "guarded sqrt-square nonnegative roundtrip",
            "0 <= x -> eml (sqrt (x * x)) x = x",
            "0 <= x",
            "sqrt remains runtime control",
            [
                "non-log and non-subtraction family",
                "different runtime-control hint from log/log1p/expm1/subtraction",
                "simple guard that can be reviewed without performance or compiler claims",
            ],
            [
                "Is sqrt available in the intended MachLib/Lean namespace with the desired theorem support?",
                "Does the EML-shaped statement need an abs-normalized form instead?",
                "Can the nonnegative guard be stated without implying runtime replacement?",
            ],
        ),
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a2.build_payload(atlas_gate_path)
    a2.validate_payload(source)
    entries = build_shortlist(source)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceSelectedOptionId": source["summary"]["selectedOptionId"],
        "sourceSelectedNextArtifact": source["summary"]["selectedNextArtifact"],
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "gapSlotCount": len(source["gapSlots"]),
        "shortlistEntryCount": len(entries),
        "privateShortlistCreated": True,
        "twoGapEntriesRecorded": len(entries) == 2,
        "materialDiversityRecorded": True,
        "candidateValidityBlocked": True,
        "shortlistEntriesAreCheckedWitnesses": False,
        "candidateValidityClaim": False,
        "newIdentityCandidateSelected": False,
        "nextBoundedIdentityBranchSelected": False,
        "feasibilityPacketCreated": False,
        "proofAttemptStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "runtimeLoweringChanged": False,
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
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
        artifact_type="private_two_gap_candidate_shortlist",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "sourceGapSlots": source["gapSlots"],
            "shortlistEntries": entries,
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
    if payload["sourceArtifact"] != "atlas-a2-private-gap-review-pause-selector":
        raise ValueError("ATLAS-A3 must consume ATLAS-A2")
    if summary["sourceSelectedOptionId"] != "prepare_two_gap_candidate_shortlist":
        raise ValueError("ATLAS-A3 must consume A2's shortlist selection")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    if summary["gapSlotCount"] != 2 or len(payload["sourceGapSlots"]) != 2:
        raise ValueError("expected two source gap slots")
    if summary["shortlistEntryCount"] != 2 or len(payload["shortlistEntries"]) != 2:
        raise ValueError("expected exactly two shortlist entries")
    expected_entries = {
        "reciprocal_positive_boundary_candidate",
        "sqrt_square_nonnegative_roundtrip_candidate",
    }
    if {entry["entryId"] for entry in payload["shortlistEntries"]} != expected_entries:
        raise ValueError("shortlist entry drift")
    for entry in payload["shortlistEntries"]:
        if entry["status"] != "private_shortlist_entry_not_checked_not_selected_for_proof":
            raise ValueError("shortlist entries must not be checked or selected for proof")
        if "not a checked witness" not in entry["blockedClaims"]:
            raise ValueError("shortlist entries must block checked-witness claims")
        assert_claim_flags_bounded(entry["claimFlags"], TRUE_CLAIM_FLAGS)
    for key in [
        "privateShortlistCreated",
        "twoGapEntriesRecorded",
        "materialDiversityRecorded",
        "candidateValidityBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "shortlistEntriesAreCheckedWitnesses",
        "candidateValidityClaim",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "feasibilityPacketCreated",
        "proofAttemptStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "runtimeLoweringChanged",
        "publicPromotionAllowed",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "catalogCompletenessClaim",
        "targetLowerBoundReachedClaim",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_two_gap_candidate_shortlist",
        semantic_strength="private_shortlist_two_gap_entries_no_checked_witness_no_candidate_validity_no_proof_no_public_promotion",
        source=f"python/results/atlas_a3_private_two_gap_candidate_shortlist/atlas_a3_private_two_gap_candidate_shortlist_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a3_private_two_gap_candidate_shortlist_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A4 as a private two-gap feasibility selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "shortlistEntryCount": payload["summary"]["shortlistEntryCount"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "candidateValidityClaim": payload["summary"]["candidateValidityClaim"],
            "proofAttemptStarted": payload["summary"]["proofAttemptStarted"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("Atlas rows", payload["summary"]["atlasRowCount"]),
        ("target range", f"{payload['summary']['targetMin']}-{payload['summary']['targetMax']}"),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("shortlist entries", payload["summary"]["shortlistEntryCount"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    entry_lines = ["| Entry | Family hint | Guard hint | Runtime control hint |", "|---|---|---|---|"]
    for entry in payload["shortlistEntries"]:
        entry_lines.append(
            f"| `{entry['entryId']}` | `{entry['familyHint']}` | {entry['guardHint']} | {entry['runtimeControlHint']} |"
        )
    return render_markdown_report(
        title="ATLAS-A3 Private Two-Gap Candidate Shortlist",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[("Shortlist Entries", entry_lines)],
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
    result_path = out_dir / f"atlas_a3_private_two_gap_candidate_shortlist_{STAMP}.json"
    report_path = report_dir / f"atlas_a3_private_two_gap_candidate_shortlist_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a3_private_two_gap_candidate_shortlist.json"
    feed_path = command_feed_dir / f"atlas_a3_private_two_gap_candidate_shortlist_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/atlas_a3_private_two_gap_candidate_shortlist")
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
    print("ATLAS_A3_PRIVATE_TWO_GAP_CANDIDATE_SHORTLIST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
