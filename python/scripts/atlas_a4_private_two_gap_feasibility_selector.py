#!/usr/bin/env python3
"""ATLAS-A4 private two-gap feasibility selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a3_private_two_gap_candidate_shortlist as a3  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_two_gap_feasibility_selector.v0"
STATUS = "ATLAS_A4_PRIVATE_TWO_GAP_FEASIBILITY_SELECTOR_PASS"
ARTIFACT_ID = "atlas-a4-private-two-gap-feasibility-selector"
SELECTED_ENTRY_ID = "reciprocal_positive_boundary_candidate"
PARKED_ENTRY_ID = "sqrt_square_nonnegative_roundtrip_candidate"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A5 private reciprocal boundary feasibility packet"

TRUE_CLAIM_FLAGS = {
    "atlas_a3_consumed",
    "private_feasibility_selector_created",
    "shortlist_entries_reviewed",
    "one_feasibility_packet_recommended",
    "sqrt_entry_parked",
    "candidate_validity_blocked",
    "public_promotion_blocked",
    "next_private_packet_recommended",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "atlas_a3_consumed": True,
    "private_feasibility_selector_created": True,
    "shortlist_entries_reviewed": True,
    "one_feasibility_packet_recommended": True,
    "sqrt_entry_parked": True,
    "candidate_validity_blocked": True,
    "public_promotion_blocked": True,
    "next_private_packet_recommended": True,
    "d109_hold_respected": True,
    "feasibility_packet_created": False,
    "shortlist_entries_are_checked_witnesses": False,
    "candidate_validity_claim": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
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
    "ATLAS-A4 is a private feasibility selector over the ATLAS-A3 shortlist; it does not create a feasibility packet, checked witness, proof branch, or validity claim.",
    "ATLAS-A4 recommends reviewing the reciprocal boundary entry first because it is the simpler non-log/non-subtraction gap; the sqrt entry is parked rather than rejected or disproved.",
    "ATLAS-A4 does not edit MachLib, run Lean, start proof work, change runtime lowering, publish or approve public copy, create SDK/compiler/course copy, implement a renderer, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.",
]


def decision(entry: dict[str, Any], status: str, score: int, rationale: list[str], blockers: list[str]) -> dict[str, Any]:
    return {
        "entryId": entry["entryId"],
        "candidateLabel": entry["candidateLabel"],
        "familyHint": entry["familyHint"],
        "selectionStatus": status,
        "priorityScore": score,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_decisions(source: dict[str, Any]) -> list[dict[str, Any]]:
    entries = {entry["entryId"]: entry for entry in source["shortlistEntries"]}
    reciprocal = entries[SELECTED_ENTRY_ID]
    sqrt_entry = entries[PARKED_ENTRY_ID]
    return [
        decision(
            reciprocal,
            "recommended_for_next_feasibility_packet",
            92,
            [
                "Simpler guard shape: 0 < x.",
                "Non-log and non-subtraction family with familiar algebraic review surface.",
                "Likely lower feasibility risk than sqrt namespace/theorem-shape questions.",
            ],
            [
                "must not claim candidate validity",
                "must not start proof or MachLib work in this selector",
                "must create only a bounded feasibility packet next",
            ],
        ),
        decision(
            sqrt_entry,
            "parked_for_later_feasibility_review",
            76,
            [
                "Useful runtime-control contrast, but sqrt theorem shape may require abs-normalized review.",
                "Parked so the lane can test the simpler reciprocal gap first.",
            ],
            [
                "not rejected",
                "not disproved",
                "requires later namespace and statement-shape review",
            ],
        ),
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a3.build_payload(atlas_gate_path)
    a3.validate_payload(source)
    decisions = build_decisions(source)
    selected = next(item for item in decisions if item["entryId"] == SELECTED_ENTRY_ID)
    parked = next(item for item in decisions if item["entryId"] == PARKED_ENTRY_ID)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "shortlistEntryCount": source["summary"]["shortlistEntryCount"],
        "atlasRowCount": source["summary"]["atlasRowCount"],
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "privateFeasibilitySelectorCreated": True,
        "shortlistEntriesReviewed": True,
        "selectedEntryId": selected["entryId"],
        "parkedEntryId": parked["entryId"],
        "oneFeasibilityPacketRecommended": True,
        "sqrtEntryParked": True,
        "feasibilityPacketCreated": False,
        "candidateValidityBlocked": True,
        "shortlistEntriesAreCheckedWitnesses": False,
        "candidateValidityClaim": False,
        "newIdentityCandidateSelected": False,
        "nextBoundedIdentityBranchSelected": False,
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
        artifact_type="private_two_gap_feasibility_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "shortlistEntries": source["shortlistEntries"],
            "feasibilityDecisions": decisions,
            "selectedDecision": selected,
            "parkedDecision": parked,
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
    if payload["sourceArtifact"] != "atlas-a3-private-two-gap-candidate-shortlist":
        raise ValueError("ATLAS-A4 must consume ATLAS-A3")
    if summary["shortlistEntryCount"] != 2 or len(payload["shortlistEntries"]) != 2:
        raise ValueError("expected two shortlist entries")
    if summary["selectedEntryId"] != SELECTED_ENTRY_ID:
        raise ValueError("unexpected selected entry")
    if summary["parkedEntryId"] != PARKED_ENTRY_ID:
        raise ValueError("unexpected parked entry")
    if payload["selectedDecision"]["selectionStatus"] != "recommended_for_next_feasibility_packet":
        raise ValueError("selected entry must be recommended for next feasibility packet")
    if payload["parkedDecision"]["selectionStatus"] != "parked_for_later_feasibility_review":
        raise ValueError("sqrt entry must be parked for later review")
    if summary["atlasRowCount"] != 13:
        raise ValueError("expected thirteen Atlas rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("target lower bound should remain unreached")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    for key in [
        "privateFeasibilitySelectorCreated",
        "shortlistEntriesReviewed",
        "oneFeasibilityPacketRecommended",
        "sqrtEntryParked",
        "candidateValidityBlocked",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "feasibilityPacketCreated",
        "shortlistEntriesAreCheckedWitnesses",
        "candidateValidityClaim",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
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
    for item in payload["feasibilityDecisions"]:
        assert_claim_flags_bounded(item["claimFlags"], TRUE_CLAIM_FLAGS)
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_two_gap_feasibility_selector",
        semantic_strength="private_selector_recommends_one_feasibility_packet_no_validity_no_proof_no_public_promotion",
        source=f"python/results/atlas_a4_private_two_gap_feasibility_selector/atlas_a4_private_two_gap_feasibility_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a4_private_two_gap_feasibility_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A5 as a private reciprocal boundary feasibility packet.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedEntryId": payload["summary"]["selectedEntryId"],
            "parkedEntryId": payload["summary"]["parkedEntryId"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "feasibilityPacketCreated": payload["summary"]["feasibilityPacketCreated"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("selected entry", payload["summary"]["selectedEntryId"]),
        ("parked entry", payload["summary"]["parkedEntryId"]),
        ("feasibility packet created", payload["summary"]["feasibilityPacketCreated"]),
        ("candidate validity claim", payload["summary"]["candidateValidityClaim"]),
        ("proof attempt started", payload["summary"]["proofAttemptStarted"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    decision_lines = ["| Entry | Status | Score |", "|---|---|---:|"]
    for item in payload["feasibilityDecisions"]:
        decision_lines.append(f"| `{item['entryId']}` | `{item['selectionStatus']}` | {item['priorityScore']} |")
    return render_markdown_report(
        title="ATLAS-A4 Private Two-Gap Feasibility Selector",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[("Feasibility Decisions", decision_lines)],
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
    result_path = out_dir / f"atlas_a4_private_two_gap_feasibility_selector_{STAMP}.json"
    report_path = report_dir / f"atlas_a4_private_two_gap_feasibility_selector_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a4_private_two_gap_feasibility_selector.json"
    feed_path = command_feed_dir / f"atlas_a4_private_two_gap_feasibility_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/atlas_a4_private_two_gap_feasibility_selector")
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
    print("ATLAS_A4_PRIVATE_TWO_GAP_FEASIBILITY_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
