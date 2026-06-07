#!/usr/bin/env python3
"""ATLAS-A1 private checked-witness table."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eml_d100_bounded_artifact_target_set_consolidation_review as d100  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    assert_claim_flags_bounded,
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_checked_witness_atlas_table.v0"
STATUS = "ATLAS_A1_PRIVATE_CHECKED_WITNESS_TABLE_PASS"
ARTIFACT_ID = "atlas-a1-private-checked-witness-table"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A2 private Atlas gap review or pause selector"

TRUE_CLAIM_FLAGS = {
    "d100_consumed",
    "private_atlas_table_created",
    "checked_witness_rows_recorded",
    "family_counts_recorded",
    "target_status_recorded",
    "public_promotion_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "d100_consumed": True,
    "private_atlas_table_created": True,
    "checked_witness_rows_recorded": True,
    "family_counts_recorded": True,
    "target_status_recorded": True,
    "public_promotion_blocked": True,
    "d109_hold_respected": True,
    "public_atlas_promotion": False,
    "public_copy_approved": False,
    "public_surface_updated": False,
    "public_education_promotion": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "proof_attempt_started": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "runtime_lowering_changed": False,
    "renderer_implemented": False,
    "visualization_quality_claim": False,
    "claim_topology_ui_created": False,
    "product_implementation_started": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "laptop_artifact_consumed": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "catalog_completeness_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "ATLAS-A1 is a private table over the already consolidated D100 checked-witness rows; it is not a public Atlas page or public-copy approval.",
    "ATLAS-A1 records families, guards, runtime controls, and target-set status for reviewer legibility; it does not claim the witness catalog is complete.",
    "ATLAS-A1 does not select a new identity, edit MachLib, typecheck Lean, start proof work, change runtime lowering, create SDK/compiler/course copy, implement a visualization, consume reviewer responses, touch laptop-owned repositories, or claim runtime performance, compiler correctness, formal equivalence, public readiness, or broad EML advantage.",
]

EXPECTED_WITNESS_IDS = {
    "constants_zero_one_e_boundary",
    "ln_from_eml_boundary",
    "subtraction_boundary_affine_offset",
    "subtraction_boundary_two_stage_chain",
    "subtraction_boundary_affine_nested_chain",
    "subtraction_boundary_three_stage_chain",
    "positive_log_exp_roundtrip",
    "expm1_boundary_identity",
    "constant_coordinate_zero_exp_two",
    "probability_logit_boundary_coordinate",
    "log1p_shifted_boundary_coordinate",
    "log1m_shifted_boundary_coordinate",
    "log1p_affine_scaled_boundary_coordinate",
}


def atlas_row(source_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "witnessId": source_row["witnessId"],
        "machlibName": source_row["machlibName"],
        "family": source_row["family"],
        "statementSummary": source_row["statementSummary"],
        "guardSummary": source_row["guardSummary"],
        "runtimeControl": source_row["runtimeControl"],
        "consolidationStatus": source_row["consolidationStatus"],
        "atlasVisibility": "private_only",
        "reviewRole": "checked_witness_core",
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def family_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(row["family"] for row in rows).items()))


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = d100.build_payload(atlas_gate_path)
    d100.validate_payload(source)
    rows = [atlas_row(row) for row in source["checkedWitnessRows"]]
    counts = family_counts(rows)
    checked_count = len(rows)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "sourceCheckedWitnessCoreCount": source["summary"]["checkedWitnessCoreCount"],
        "atlasRowCount": checked_count,
        "familyCount": len(counts),
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": source["summary"]["targetLowerBoundReached"],
        "targetUpperBoundExceeded": source["summary"]["targetUpperBoundExceeded"],
        "additionalArtifactsNeededForLowerBound": source["summary"]["additionalArtifactsNeededForLowerBound"],
        "remainingSlotsBeforeUpperBound": source["summary"]["remainingSlotsBeforeUpperBound"],
        "selectorOnlyPacketsCountedAsFinalArtifacts": source["summary"]["selectorOnlyPacketsCountedAsFinalArtifacts"],
        "privateAtlasTableCreated": True,
        "privateReviewOnly": True,
        "allRowsPrivateOnly": all(row["atlasVisibility"] == "private_only" for row in rows),
        "allRowsBlockPublicPromotion": all(row["publicPromotionAllowed"] is False for row in rows),
        "publicPromotionAllowed": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "catalogCompletenessClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_checked_witness_atlas_table",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "sourceAtlasGatePath": str(atlas_gate_path),
            "targetRange": source["targetRange"],
            "familyCounts": counts,
            "atlasRows": rows,
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
    if payload["sourceArtifact"] != "eml-d100-bounded-artifact-target-set-consolidation-review":
        raise ValueError("ATLAS-A1 must consume D100")
    rows = payload["atlasRows"]
    if len(rows) != 13 or summary["atlasRowCount"] != 13:
        raise ValueError("expected 13 private Atlas rows from D100")
    if {row["witnessId"] for row in rows} != EXPECTED_WITNESS_IDS:
        raise ValueError("witness id set drift")
    if summary["sourceCheckedWitnessCoreCount"] != 13:
        raise ValueError("source checked witness count drift")
    if payload["familyCounts"] != family_counts(rows):
        raise ValueError("family count drift")
    if sum(payload["familyCounts"].values()) != len(rows):
        raise ValueError("family counts must sum to row count")
    if summary["familyCount"] != len(payload["familyCounts"]):
        raise ValueError("family count summary drift")
    if summary["targetMin"] != d100.TARGET_MIN or summary["targetMax"] != d100.TARGET_MAX:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("13 checked rows should not reach lower bound 15")
    if summary["targetUpperBoundExceeded"] is not False:
        raise ValueError("target upper bound should not be exceeded")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional artifacts for lower bound")
    if summary["remainingSlotsBeforeUpperBound"] != 12:
        raise ValueError("remaining slots drift")
    if summary["selectorOnlyPacketsCountedAsFinalArtifacts"] is not False:
        raise ValueError("selector-only packets must not count as final artifacts")
    for row in rows:
        if row["atlasVisibility"] != "private_only":
            raise ValueError("Atlas rows must remain private-only")
        if row["reviewRole"] != "checked_witness_core":
            raise ValueError("unexpected review role")
        if row["publicPromotionAllowed"] is not False:
            raise ValueError("public promotion must remain blocked")
        assert_claim_flags_bounded(row["claimFlags"], TRUE_CLAIM_FLAGS)
    for key in [
        "privateAtlasTableCreated",
        "privateReviewOnly",
        "allRowsPrivateOnly",
        "allRowsBlockPublicPromotion",
        "d109HoldRespected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "publicPromotionAllowed",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "catalogCompletenessClaim",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next recommended artifact")
    required_false = set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS
    for key in required_false:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type="private_checked_witness_atlas_table",
        semantic_strength="private_table_over_d100_checked_witness_rows_no_public_promotion_no_new_proof_no_runtime_change",
        source=f"python/results/atlas_a1_private_checked_witness_table/atlas_a1_private_checked_witness_table_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a1_private_checked_witness_table_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A2 as a private Atlas gap review or pause selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "familyCount": payload["summary"]["familyCount"],
            "additionalArtifactsNeededForLowerBound": payload["summary"]["additionalArtifactsNeededForLowerBound"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("Atlas rows", payload["summary"]["atlasRowCount"]),
        ("families", payload["summary"]["familyCount"]),
        ("target range", f"{payload['summary']['targetMin']}-{payload['summary']['targetMax']}"),
        ("additional artifacts needed for lower bound", payload["summary"]["additionalArtifactsNeededForLowerBound"]),
        ("public promotion allowed", payload["summary"]["publicPromotionAllowed"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    witness_lines = [
        "| Witness | Family | Guard | Runtime control |",
        "|---|---|---|---|",
    ]
    for row in payload["atlasRows"]:
        witness_lines.append(
            f"| `{row['witnessId']}` | `{row['family']}` | {row['guardSummary']} | {row['runtimeControl']} |"
        )
    family_lines = ["| Family | Count |", "|---|---:|"]
    for family, count in payload["familyCounts"].items():
        family_lines.append(f"| `{family}` | {count} |")
    return render_markdown_report(
        title="ATLAS-A1 Private Checked Witness Table",
        status=payload["status"],
        summary_rows=rows,
        sections=[
            ("Family Counts", family_lines),
            ("Private Atlas Rows", witness_lines),
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
    result_path = out_dir / f"atlas_a1_private_checked_witness_table_{STAMP}.json"
    report_path = report_dir / f"atlas_a1_private_checked_witness_table_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a1_private_checked_witness_table.json"
    feed_path = command_feed_dir / f"atlas_a1_private_checked_witness_table_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/atlas_a1_private_checked_witness_table")
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
    print("ATLAS_A1_PRIVATE_CHECKED_WITNESS_TABLE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
