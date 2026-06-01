#!/usr/bin/env python3
"""EML-D26 next nested-family branch decision."""

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

from scripts import eml_d25_subtraction_boundary_affine_nested_chain_surface_review as d25  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_nested_family_next_branch_decision.v1"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D26_NESTED_FAMILY_NEXT_BRANCH_DECISION_PASS"

CLAIM_FLAGS = {
    "copy_review_started": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "runtime_lowering_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D26 chooses the next private nested-family branch after D25; it does not start copy review, edit MachLib, or typecheck Lean.",
    "D26 does not prove a theorem, prove a broad nested subtraction family, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.",
    "The selected three-stage branch is selector-only; standard subtraction remains the runtime lowering control.",
]


def decision_option(
    option_id: str,
    lane: str,
    status: str,
    priority_score: int,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "lane": lane,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    surface = d25.build_payload(atlas_gate_path)
    d25.validate_payload(surface)
    options = [
        decision_option(
            "three_stage_chain_witness_attempt",
            "private_proof_family_lane",
            "selected_next",
            68,
            "EML-D27 subtraction-boundary three-stage chain witness attempt",
            [
                "D21 checked the minimal two-stage nested chain.",
                "D24 checked the affine-nested chain after D23 selected it.",
                "D25 surfaced the affine-nested witness privately while preserving the three-stage branch as a separate parked option.",
                "The three-stage target is now the smallest remaining depth-extension of the checked nested-chain proof shape.",
            ],
            [
                "review exact Lean statement before MachLib edit",
                "avoid broad nested-family claim",
                "preserve all positive log-domain guards",
            ],
        ),
        decision_option(
            "checked_witness_copy_review_packet",
            "public_copy_review_lane",
            "candidate_later",
            61,
            "Future checked-witness copy review packet",
            [
                "The checked witness set is now substantial enough for private copy review.",
                "Copy review would help future public education but should remain separate from the active proof-family branch selector.",
            ],
            [
                "human wording review required",
                "public promotion must remain false until separately approved",
                "avoid theorem-discovery language",
            ],
        ),
        decision_option(
            "pause_subtraction_family_deepening",
            "private_halt_lane",
            "candidate_later",
            52,
            "Future branch-pause packet",
            [
                "Pausing is reasonable if the three-stage attempt exposes proof-surface drift or claim confusion.",
                "D25 preserved the family guardrail, so one explicit selector step toward the final parked depth-extension remains bounded.",
            ],
            [
                "define pause criteria",
                "preserve current checked-witness index",
                "do not turn pause into public copy approval",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceSurfaceReview": surface["artifactId"],
        "checkedWitnessRecordedPrivately": surface["summary"]["checkedWitnessRecordedPrivately"],
        "negativeControlBlockedBySelector": surface["summary"]["negativeControlBlockedBySelector"],
        "twoStageWitnessRecordedPrivately": surface["summary"]["twoStageWitnessRecordedPrivately"],
        "affineNestedWitnessRecordedPrivately": surface["summary"]["checkedWitnessRecordedPrivately"],
        "threeStageChainPreviouslyParked": surface["summary"]["threeStageChainStillParked"],
        "checkedWitnessCopyReviewPreviouslyParked": surface["summary"]["checkedWitnessCopyReviewStillParked"],
        "familyPausePreviouslyParked": surface["summary"]["familyPauseStillParked"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "copyReviewStarted": False,
        "publicPromotionPerformed": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": surface["summary"]["runtimeLoweringControl"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in option["claimFlags"].values()) for option in options),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "decisionType": "eml_nested_family_next_branch_decision_v1",
        "artifactId": "eml-d26-nested-family-next-branch-decision",
        "status": STATUS,
        "decision": "select_three_stage_chain_witness_attempt",
        "date": DATE,
        "sourceSurfaceReview": surface["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "decisionOptions": options,
        "selectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSurfaceReview"] != "eml-d25-subtraction-boundary-affine-nested-chain-surface-review":
        raise ValueError("D26 must consume D25")
    if summary["checkedWitnessRecordedPrivately"] is not True:
        raise ValueError("D26 requires private affine-nested surface review")
    if summary["negativeControlBlockedBySelector"] is not True:
        raise ValueError("negative-control block must be preserved")
    if summary["twoStageWitnessRecordedPrivately"] is not True:
        raise ValueError("two-stage witness chain must stay recorded")
    if summary["affineNestedWitnessRecordedPrivately"] is not True:
        raise ValueError("affine-nested witness must be recorded privately")
    if summary["threeStageChainPreviouslyParked"] is not True:
        raise ValueError("three-stage branch must come from parked D25 option")
    if summary["checkedWitnessCopyReviewPreviouslyParked"] is not True:
        raise ValueError("copy review parked status must be preserved")
    if summary["familyPausePreviouslyParked"] is not True:
        raise ValueError("family pause parked status must be preserved")
    if summary["optionCount"] != 3:
        raise ValueError("expected three decision options")
    if summary["selectedOptionId"] != "three_stage_chain_witness_attempt":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D27 subtraction-boundary three-stage chain witness attempt":
        raise ValueError("unexpected next artifact")
    for key in [
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "copyReviewStarted",
        "publicPromotionPerformed",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "runtimeLoweringChanged",
        "publicReady",
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
        "artifactType": "eml_nested_family_next_branch_decision",
        "validationStatus": "pass",
        "semanticStrength": "private_branch_decision_no_copy_review_no_implementation",
        "source": f"python/results/eml_d26_nested_family_next_branch_decision/eml_d26_nested_family_next_branch_decision_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d26_nested_family_next_branch_decision_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D27 as a scoped MachLib attempt or blocker packet for the three-stage chain; do not claim broad nested-family support.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D26 Next Nested-Family Branch Decision",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D26 chooses the next private branch after the affine-nested chain surface review.",
        "",
        "| Option | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for option in payload["decisionOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | {option['priorityScore']} | {option['nextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected next artifact: `{payload['summary']['selectedNextArtifact']}`",
            f"- broad nested subtraction claim: `{payload['summary']['broadNestedSubtractionClaim']}`",
            f"- copy review started: `{payload['summary']['copyReviewStarted']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- runtime lowering control: `{payload['summary']['runtimeLoweringControl']}`",
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
    result_path = out_dir / f"eml_d26_nested_family_next_branch_decision_{STAMP}.json"
    report_path = report_dir / f"eml_d26_nested_family_next_branch_decision_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d26_nested_family_next_branch_decision.json"
    feed_path = command_feed_dir / f"eml_d26_nested_family_next_branch_decision_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d26_nested_family_next_branch_decision")
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
    print("EML_D26_NESTED_FAMILY_NEXT_BRANCH_DECISION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
