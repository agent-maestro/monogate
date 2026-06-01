#!/usr/bin/env python3
"""EML-D22 subtraction-boundary two-stage chain surface review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eml_d21_subtraction_boundary_two_stage_chain_witness_attempt as d21  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_subtraction_boundary_two_stage_chain_surface_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D22_SUBTRACTION_BOUNDARY_TWO_STAGE_CHAIN_SURFACE_REVIEW_PASS"

CLAIM_FLAGS = {
    "surface_updated": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D22 is a private surface review over the checked D21 two-stage nested subtraction-boundary witness; it does not update public pages or promote Atlas copy.",
    "The two-stage witness is one scoped nested-chain instance, not a broad nested subtraction theorem or a general subtraction-family theorem.",
    "Standard subtraction remains the runtime lowering control; D22 does not add an Advantage Lab runtime case or claim runtime performance.",
]


def surface_row(
    surface_id: str,
    surface_kind: str,
    status: str,
    evidence_strength: str,
    action: str,
    rationale: list[str],
    blocked_claims: list[str],
) -> dict[str, Any]:
    return {
        "surfaceId": surface_id,
        "surfaceKind": surface_kind,
        "surfaceStatus": status,
        "evidenceStrength": evidence_strength,
        "recommendedAction": action,
        "rationale": rationale,
        "blockedClaims": blocked_claims,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    witness = d21.build_payload(atlas_gate_path)
    d21.validate_payload(witness)
    surface_rows = [
        surface_row(
            "machlib_witness_index_subtraction_boundary_two_stage_chain",
            "machlib_private_index",
            "checked_witness_recorded_private",
            "scoped_machlib_two_stage_nested_subtraction_identity_witness_checked",
            "record_as_private_checked_witness",
            [
                "D21 checks MachLib.Real.subtraction_boundary_two_stage_chain_witness.",
                "The checked statement is eml (log v) (exp (eml (log w) (exp u))) = v - (w - u) under 0 < v and 0 < w.",
                "Lake build passed with only pre-existing unrelated sorry warnings.",
            ],
            ["theorem discovery", "broad nested subtraction theorem", "public readiness"],
        ),
        surface_row(
            "nested_subtraction_family_guardrail_two_stage_chain",
            "family_claim_guardrail",
            "scoped_nested_instance_only",
            "selector_guardrails_preserved",
            "keep_nested_family_claim_blocked_until_more_cases_exist",
            [
                "D20 blocked the unguarded nested negative control before D21.",
                "D20 parked the affine-nested and three-stage variants before D21.",
                "D21 proves one guarded two-stage instance, not every nested chain.",
            ],
            ["broad nested subtraction family", "unguarded nested log-domain use", "deeper-chain proof expansion"],
        ),
        surface_row(
            "advantage_lab_subtraction_boundary_two_stage_chain",
            "advantage_lab",
            "runtime_control_remains_standard_subtraction",
            "scoped_machlib_nested_identity_witness_available",
            "do_not_add_runtime_advantage_row_without_new_runtime_evidence",
            [
                "The witness strengthens proof/teaching shape only.",
                "Standard subtraction remains the runtime lowering control.",
                "Any future Advantage row must preserve the runtime-control boundary.",
            ],
            ["runtime advantage", "public performance", "runtime lowering superiority"],
        ),
        surface_row(
            "public_atlas_subtraction_boundary_two_stage_chain",
            "public_surface",
            "held_private",
            "checked_machlib_witness_available_private",
            "require_human_copy_review_before_public_change",
            [
                "D21 proof status is real but public wording has not been reviewed.",
                "No monogate.org or monogate.dev public route is changed by D22.",
                "The safe public voice must explain this as one scoped two-stage nested instance.",
            ],
            ["public readiness", "public theorem claim", "public Atlas promotion"],
        ),
    ]
    summary = {
        "sourceWitnessAttempt": witness["artifactId"],
        "selectedWitnessName": witness["summary"]["selectedWitnessName"],
        "selectedStatementId": witness["summary"]["selectedStatementId"],
        "surfaceRowCount": len(surface_rows),
        "checkedWitnessRecordedPrivately": witness["summary"]["scopedWitnessChecked"],
        "negativeControlBlockedBySelector": witness["summary"]["negativeControlBlockedBySelector"],
        "affineNestedChainParkedBySelector": witness["summary"]["affineNestedChainParkedBySelector"],
        "deeperChainParkedBySelector": witness["summary"]["deeperChainParkedBySelector"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "publicPromotionPerformed": False,
        "publicEducationCandidate": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": witness["summary"]["runtimeLoweringControl"],
        "surfaceUpdated": False,
        "nextAction": "EML-D23 choose next nested-family branch or checked-witness copy-review packet.",
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in row["claimFlags"].values()) for row in surface_rows),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_subtraction_boundary_two_stage_chain_surface_review_v0",
        "artifactId": "eml-d22-subtraction-boundary-two-stage-chain-surface-review",
        "status": STATUS,
        "decision": "surface_checked_two_stage_chain_witness_as_private_review_evidence_only",
        "date": DATE,
        "sourceWitnessAttempt": witness["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "surfaceRows": surface_rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceWitnessAttempt"] != "eml-d21-subtraction-boundary-two-stage-chain-witness-attempt":
        raise ValueError("D22 must consume D21")
    if summary["selectedWitnessName"] != "MachLib.Real.subtraction_boundary_two_stage_chain_witness":
        raise ValueError("unexpected witness")
    if summary["selectedStatementId"] != "subtraction_boundary_two_stage_chain_v1":
        raise ValueError("unexpected statement")
    if summary["surfaceRowCount"] != 4:
        raise ValueError("expected four surface rows")
    if summary["checkedWitnessRecordedPrivately"] is not True:
        raise ValueError("checked witness must be recorded")
    if summary["negativeControlBlockedBySelector"] is not True:
        raise ValueError("negative-control block must be preserved")
    if summary["affineNestedChainParkedBySelector"] is not True or summary["deeperChainParkedBySelector"] is not True:
        raise ValueError("parked nested variants must be preserved")
    for key in [
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "publicPromotionPerformed",
        "publicEducationCandidate",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "surfaceUpdated",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_subtraction_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_subtraction_boundary_two_stage_chain_surface_review",
        "validationStatus": "pass",
        "semanticStrength": "checked_two_stage_chain_witness_private_surface_review_no_public_update",
        "source": f"python/results/eml_d22_subtraction_boundary_two_stage_chain_surface_review/eml_d22_subtraction_boundary_two_stage_chain_surface_review_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d22_subtraction_boundary_two_stage_chain_surface_review_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D22 Subtraction Boundary Two-Stage Chain Surface Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected witness: `{payload['summary']['selectedWitnessName']}`",
        "",
        "D22 routes the checked D21 two-stage witness into private review surfaces without public promotion.",
        "",
        "| Surface | Status | Evidence strength | Action |",
        "|---|---|---|---|",
    ]
    for row in payload["surfaceRows"]:
        lines.append(
            f"| `{row['surfaceId']}` | `{row['surfaceStatus']}` | `{row['evidenceStrength']}` | {row['recommendedAction']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- checked witness recorded privately: `{payload['summary']['checkedWitnessRecordedPrivately']}`",
            f"- negative control blocked by selector: `{payload['summary']['negativeControlBlockedBySelector']}`",
            f"- affine nested chain parked by selector: `{payload['summary']['affineNestedChainParkedBySelector']}`",
            f"- deeper chain parked by selector: `{payload['summary']['deeperChainParkedBySelector']}`",
            f"- broad nested subtraction claim: `{payload['summary']['broadNestedSubtractionClaim']}`",
            f"- runtime lowering control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- surface updated: `{payload['summary']['surfaceUpdated']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d22_subtraction_boundary_two_stage_chain_surface_review_{STAMP}.json"
    report_path = report_dir / f"eml_d22_subtraction_boundary_two_stage_chain_surface_review_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d22_subtraction_boundary_two_stage_chain_surface_review.json"
    feed_path = command_feed_dir / f"eml_d22_subtraction_boundary_two_stage_chain_surface_review_feed_{STAMP}.json"
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
    stamp_0527 = "2026_05_27"
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--atlas-gate-path", type=Path, default=ROOT / f"python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_{stamp_0527}.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d22_subtraction_boundary_two_stage_chain_surface_review")
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
    print("EML_D22_SUBTRACTION_BOUNDARY_TWO_STAGE_CHAIN_SURFACE_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
