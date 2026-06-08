#!/usr/bin/env python3
"""ATLAS-A46 private Atlas v0 reference document seed."""

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

from scripts import atlas_a33_private_exp_negation_bounded_wrapper_attempt_artifact as a33  # noqa: E402
from scripts import atlas_a43_private_trig_pythagorean_bounded_wrapper_attempt_artifact as a43  # noqa: E402
from scripts import atlas_a45_private_atlas_lower_bound_consolidation_selector as a45  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_atlas_v0_reference_document_seed.v0"
STATUS = "ATLAS_A46_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_SEED_PASS"
ARTIFACT_ID = "atlas-a46-private-atlas-v0-reference-document-seed"
SOURCE_ARTIFACT_ID = "atlas-a45-private-atlas-lower-bound-consolidation-selector"
ATLAS_A1_PATH = ROOT / "python/results/atlas_a1_private_checked_witness_table/atlas_a1_private_checked_witness_table_2026_06_06.json"
PRIVATE_DOC_PATH = "docs/research/private_atlas_v0_reference_seed.md"
NEXT_RECOMMENDED_ARTIFACT = "ATLAS-A47 private Atlas v0 reference document review selector"

TRUE_CLAIM_FLAGS = {
    "atlas_a45_consumed",
    "atlas_a1_table_consumed",
    "exp_negation_wrapper_consumed",
    "trig_wrapper_consumed",
    "private_reference_document_seed_created",
    "fifteen_private_rows_recorded",
    "lower_bound_observation_recorded",
    "public_promotion_blocked",
    "runtime_claims_blocked",
    "catalog_completeness_blocked",
    "next_review_selector_recommended",
}

CLAIM_FLAGS = {
    "atlas_a45_consumed": True,
    "atlas_a1_table_consumed": True,
    "exp_negation_wrapper_consumed": True,
    "trig_wrapper_consumed": True,
    "private_reference_document_seed_created": True,
    "fifteen_private_rows_recorded": True,
    "lower_bound_observation_recorded": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "catalog_completeness_blocked": True,
    "next_review_selector_recommended": True,
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
    "ATLAS-A46 creates a private reference-document seed only; it does not publish, approve public copy, update public/dev surfaces, or create SDK/course material.",
    "ATLAS-A46 records fifteen private checked-witness rows and the lower-bound observation, but it does not claim catalog completeness, target-lower-bound promotion, public readiness, runtime performance, compiler correctness, formal equivalence, or broad EML advantage.",
    "ATLAS-A46 does not start proof work, create candidate or feasibility packets, edit MachLib, run Lean, perform theorem lookup, change runtime lowering, consume reviewer responses, start D110, or touch laptop-owned repositories.",
]


def load_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def normalize_a1_rows(a1_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in a1_payload["atlasRows"]:
        rows.append(
            {
                "witnessId": row["witnessId"],
                "family": row["family"],
                "machlibName": row["machlibName"],
                "statementSummary": row["statementSummary"],
                "guardSummary": row["guardSummary"],
                "runtimeControl": row["runtimeControl"],
                "sourceArtifact": a1_payload["artifactId"],
                "status": "private_checked_witness_row_from_a1",
            }
        )
    return rows


def wrapper_row(wrapper: dict[str, Any], witness_id: str, family: str, statement_summary: str) -> dict[str, Any]:
    checked = wrapper["checkedWrapperWitness"]
    return {
        "witnessId": witness_id,
        "family": family,
        "machlibName": checked["machlibName"],
        "statementSummary": statement_summary,
        "guardSummary": "all_real_no_extra_guard",
        "runtimeControl": checked["runtimeControl"],
        "sourceArtifact": wrapper["artifactId"],
        "status": "private_checked_wrapper_witness_row",
        "dependencyIdentifier": checked["dependencyIdentifier"],
        "checkedStatement": checked["checkedStatement"],
    }


def build_rows(a1_payload: dict[str, Any], exp_wrapper: dict[str, Any], trig_wrapper: dict[str, Any]) -> list[dict[str, Any]]:
    rows = normalize_a1_rows(a1_payload)
    rows.append(
        wrapper_row(
            exp_wrapper,
            "exp_negation_multiplicative_identity",
            "exp_algebra_boundary",
            "checked exp-negation multiplicative identity wrapper",
        )
    )
    rows.append(
        wrapper_row(
            trig_wrapper,
            "trig_pythagorean_unit_identity",
            "trig_boundary",
            "checked trig Pythagorean unit identity wrapper",
        )
    )
    return rows


def build_private_doc(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# Private EML Atlas v0 Reference Seed",
        "",
        "Status: private seed, not public copy",
        f"Date: {DATE}",
        "",
        "## Purpose",
        "",
        "This seed collects the currently reviewable private Atlas rows into one",
        "reader-facing reference document. It is meant to reduce the cost of",
        "reviewing scattered evidence packets and handoff notes.",
        "",
        "It is not a public Atlas, not a completeness claim, and not SDK/course",
        "copy. Each row remains bounded by its source artifact and non-claims.",
        "",
        "## Current Count",
        "",
        f"- private rows recorded: `{summary['atlasRowCount']}`",
        f"- target range: `{summary['targetMin']}`-`{summary['targetMax']}`",
        f"- additional artifacts needed for lower-bound observation: `{summary['additionalArtifactsNeededForLowerBound']}`",
        "- catalog completeness claim: `false`",
        "- public readiness claim: `false`",
        "",
        "## Rows",
        "",
        "| # | Witness | Family | Guard | Runtime Boundary | Source |",
        "|---:|---|---|---|---|---|",
    ]
    for idx, row in enumerate(rows, start=1):
        lines.append(
            "| {idx} | `{name}` | `{family}` | {guard} | {runtime} | `{source}` |".format(
                idx=idx,
                name=row["machlibName"],
                family=row["family"],
                guard=row["guardSummary"],
                runtime=row["runtimeControl"],
                source=row["sourceArtifact"],
            )
        )
    lines.extend(
        [
            "",
            "## Usefulness Notes",
            "",
            "- Public witness candidates: expm1 boundary, positive log-exp roundtrip, exp-negation wrapper, and trig Pythagorean wrapper need separate copy gates before use.",
            "- SDK/compiler guard-note candidates should be extracted only after private review confirms the row wording and non-claims.",
            "- Course references should cite guards and runtime boundaries, not broad EML advantage.",
            "",
            "## Non-Claims",
            "",
            "- No public Atlas or public math page is created by this seed.",
            "- No catalog completeness or target-lower-bound promotion is claimed.",
            "- No runtime replacement, runtime performance, compiler correctness, or formal equivalence is claimed.",
            "- No SDK/compiler documentation, course material, product implementation, or electronics/laptop artifact is created or consumed.",
            "",
            "## Next Review Questions",
            "",
            "- Are all row labels clear enough for a reviewer?",
            "- Which rows are strongest public-witness candidates after a separate copy gate?",
            "- Which rows have useful SDK/course guard-note hooks without overstating runtime behavior?",
            "- Should any row be parked before a future private Atlas v0 review packet?",
            "",
        ]
    )
    return "\n".join(lines)


def build_payload(atlas_gate_path: Path, machlib_root: Path, atlas_a1_path: Path = ATLAS_A1_PATH) -> dict[str, Any]:
    source = a45.build_payload(atlas_gate_path, machlib_root)
    a45.validate_payload(source)
    a1_payload = load_json(atlas_a1_path)
    exp_wrapper = a33.build_payload(atlas_gate_path, machlib_root)
    a33.validate_payload(exp_wrapper)
    trig_wrapper = a43.build_payload(atlas_gate_path, machlib_root)
    a43.validate_payload(trig_wrapper)
    rows = build_rows(a1_payload, exp_wrapper, trig_wrapper)
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "atlasA1Artifact": a1_payload["artifactId"],
        "expNegationArtifact": exp_wrapper["artifactId"],
        "trigPythagoreanArtifact": trig_wrapper["artifactId"],
        "privateReferenceDocumentSeedCreated": True,
        "documentPath": PRIVATE_DOC_PATH,
        "atlasRowCount": len(rows),
        "sourceA1RowCount": len(a1_payload["atlasRows"]),
        "addedWrapperRowCount": 2,
        "targetMin": source["summary"]["targetMin"],
        "targetMax": source["summary"]["targetMax"],
        "targetLowerBoundReached": len(rows) >= source["summary"]["targetMin"],
        "additionalArtifactsNeededForLowerBound": max(0, source["summary"]["targetMin"] - len(rows)),
        "lowerBoundObservationRecorded": True,
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
        artifact_type="private_atlas_v0_reference_document_seed",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "atlasRows": rows,
            "documentPreview": build_private_doc(rows, summary),
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
        raise ValueError("ATLAS-A46 must consume ATLAS-A45")
    if summary["documentPath"] != PRIVATE_DOC_PATH:
        raise ValueError("document path drift")
    if summary["sourceA1RowCount"] != 13:
        raise ValueError("A1 row count drift")
    if summary["addedWrapperRowCount"] != 2:
        raise ValueError("wrapper row count drift")
    if summary["atlasRowCount"] != 15 or len(payload["atlasRows"]) != 15:
        raise ValueError("expected fifteen private rows")
    if summary["targetMin"] != 15 or summary["targetMax"] != 25:
        raise ValueError("target range drift")
    if summary["targetLowerBoundReached"] is not True:
        raise ValueError("lower-bound observation should be true")
    if summary["additionalArtifactsNeededForLowerBound"] != 0:
        raise ValueError("expected no additional artifact for lower-bound observation")
    for key in [
        "privateReferenceDocumentSeedCreated",
        "lowerBoundObservationRecorded",
        "catalogCompletenessBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
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
        artifact_type="private_atlas_v0_reference_document_seed",
        semantic_strength="private_reference_document_seed_fifteen_rows_no_public_completeness_runtime_product_claims",
        source=f"python/results/atlas_a46_private_atlas_v0_reference_document_seed/atlas_a46_private_atlas_v0_reference_document_seed_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="atlas_a46_private_atlas_v0_reference_document_seed_feed",
        date=DATE,
        status=payload["status"],
        next_action="Run ATLAS-A47 as a private Atlas v0 reference document review selector; do not publish, extract SDK/course copy, start proof work, edit MachLib, run Lean, or claim catalog completeness.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "documentPath": payload["summary"]["documentPath"],
            "atlasRowCount": payload["summary"]["atlasRowCount"],
            "catalogCompletenessClaim": payload["summary"]["catalogCompletenessClaim"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    summary_rows = [
        ("source artifact", payload["summary"]["sourceArtifact"]),
        ("document path", payload["summary"]["documentPath"]),
        ("Atlas row count", payload["summary"]["atlasRowCount"]),
        ("A1 source rows", payload["summary"]["sourceA1RowCount"]),
        ("added wrapper rows", payload["summary"]["addedWrapperRowCount"]),
        ("catalog completeness claim", payload["summary"]["catalogCompletenessClaim"]),
        ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
    ]
    row_lines = [
        f"- `{row['witnessId']}` -> `{row['machlibName']}` ({row['family']})"
        for row in payload["atlasRows"]
    ]
    blocked_lines = [
        "- public copy and public/dev promotion remain blocked",
        "- SDK/compiler/course extraction remains blocked",
        "- proof branches, MachLib edits, Lean checks, and theorem lookup remain blocked",
        "- catalog completeness and target-lower-bound promotion claims remain blocked",
    ]
    return render_markdown_report(
        title="ATLAS-A46 Private Atlas v0 Reference Document Seed",
        status=payload["status"],
        summary_rows=summary_rows,
        sections=[
            ("Seed Rows", row_lines),
            ("Blocked Follow-Ups", blocked_lines),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    doc_path: Path,
    atlas_gate_path: Path,
    machlib_root: Path,
    atlas_a1_path: Path,
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path, machlib_root, atlas_a1_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"atlas_a46_private_atlas_v0_reference_document_seed_{STAMP}.json"
    report_path = report_dir / f"atlas_a46_private_atlas_v0_reference_document_seed_{STAMP}.md"
    evidence_path = evidence_dir / "atlas_a46_private_atlas_v0_reference_document_seed.json"
    feed_path = command_feed_dir / f"atlas_a46_private_atlas_v0_reference_document_seed_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(payload["documentPreview"], encoding="utf-8")
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
        "doc_path": str(doc_path),
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
    parser.add_argument("--atlas-a1-path", type=Path, default=ATLAS_A1_PATH)
    parser.add_argument("--doc-path", type=Path, default=ROOT / PRIVATE_DOC_PATH)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/atlas_a46_private_atlas_v0_reference_document_seed",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.atlas_gate_path, args.machlib_root, args.atlas_a1_path)
    validate_payload(payload)
    if args.build:
        build_outputs(
            args.out_dir,
            args.report_dir,
            args.evidence_dir,
            args.command_feed_dir,
            args.doc_path,
            args.atlas_gate_path,
            args.machlib_root,
            args.atlas_a1_path,
        )
    print("ATLAS_A46_PRIVATE_ATLAS_V0_REFERENCE_DOCUMENT_SEED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
