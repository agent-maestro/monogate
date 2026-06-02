#!/usr/bin/env python3
"""EML-D31 checked-witness review next decision."""

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

from scripts import eml_d30_checked_witness_copy_review_packet as d30  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_checked_witness_review_next_decision.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D31_CHECKED_WITNESS_REVIEW_NEXT_DECISION_PASS"

CLAIM_FLAGS = {
    "copy_review_started": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
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
    "EML-D31 is a selector-only next decision after D30; it does not publish D30 copy, approve public wording, edit MachLib, or typecheck Lean.",
    "D31 selects a private pause/freeze path for the subtraction-family ladder; it does not claim a broad nested subtraction family or any arbitrary-depth theorem.",
    "D31 keeps standard subtraction, standard log, standard exp, and standard constants as runtime controls where applicable.",
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
    review = d30.build_payload(atlas_gate_path)
    d30.validate_payload(review)
    options = [
        decision_option(
            "pause_subtraction_family_deepening",
            "private_pause_freeze_lane",
            "selected_next",
            78,
            "EML-D32 subtraction-family pause and checked-witness index freeze packet",
            [
                "D30 completed private copy review over six checked witnesses without public promotion.",
                "The checked witness ladder is now deep enough to stabilize language before opening another proof-family branch.",
                "A pause/freeze packet preserves Course 1 and Course 2 scaling value while keeping broad-family and public-readiness claims blocked.",
            ],
            [
                "define exactly what is frozen and what remains available for future branches",
                "preserve D30 caveats and blocked phrases",
                "do not treat the pause as public copy approval",
            ],
        ),
        decision_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_human_approval",
            59,
            "Future human-approved checked-witness public copy gate",
            [
                "D30 produced private-reviewable wording that can support future education copy.",
                "No explicit human approval is recorded in this artifact, so public copy remains parked.",
            ],
            [
                "requires explicit human approval",
                "must reuse D30 caveats",
                "must keep theorem-discovery and broad-family language blocked",
            ],
        ),
        decision_option(
            "new_bounded_identity_branch_selector",
            "private_proof_family_lane",
            "candidate_later_after_pause",
            51,
            "Future bounded identity branch selector",
            [
                "A new bounded branch remains possible after the checked-witness index is frozen.",
                "Starting it immediately would blur the D30 copy-review boundary and extend proof depth without a pause criterion.",
            ],
            [
                "choose only one bounded statement",
                "avoid nested-family expansion by default",
                "keep public copy and Advantage claims false",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceReview": review["artifactId"],
        "sourceDecision": review["sourceDecision"],
        "d30CopyReviewStarted": review["summary"]["copyReviewStarted"],
        "d30PrivateCopyReviewOnly": review["summary"]["privateCopyReviewOnly"],
        "d30WitnessRowCount": review["summary"]["witnessRowCount"],
        "d30RequiredCaveatCount": review["summary"]["requiredCaveatCount"],
        "d30BlockedGlobalPhraseCount": review["summary"]["blockedGlobalPhraseCount"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "familyDeepeningPauseSelected": True,
        "checkedWitnessIndexFreezePlanned": True,
        "humanApprovedPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "newBoundedBranchSelected": False,
        "copyReviewStartedInD31": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": review["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in option["claimFlags"].values()) for option in options),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "decisionType": "eml_checked_witness_review_next_decision_v0",
        "artifactId": "eml-d31-checked-witness-review-next-decision",
        "status": STATUS,
        "decision": "select_pause_subtraction_family_deepening",
        "date": DATE,
        "sourceReview": review["artifactId"],
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
    if payload["sourceReview"] != "eml-d30-checked-witness-copy-review-packet":
        raise ValueError("D31 must consume D30")
    if summary["d30CopyReviewStarted"] is not True:
        raise ValueError("D31 requires completed D30 private copy review")
    if summary["d30PrivateCopyReviewOnly"] is not True:
        raise ValueError("D30 private-only boundary must be preserved")
    if summary["d30WitnessRowCount"] != 6:
        raise ValueError("D31 expects six D30 witness rows")
    if summary["d30RequiredCaveatCount"] != 5 or summary["d30BlockedGlobalPhraseCount"] != 8:
        raise ValueError("D30 caveat/blocker counts drifted")
    if summary["optionCount"] != 3:
        raise ValueError("expected three D31 decision options")
    if summary["selectedOptionId"] != "pause_subtraction_family_deepening":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D32 subtraction-family pause and checked-witness index freeze packet":
        raise ValueError("unexpected next artifact")
    if summary["familyDeepeningPauseSelected"] is not True:
        raise ValueError("family pause must be selected")
    if summary["checkedWitnessIndexFreezePlanned"] is not True:
        raise ValueError("checked witness index freeze must be planned")
    for key in [
        "humanApprovedPublicCopyGateSelected",
        "humanApprovalRecorded",
        "newBoundedBranchSelected",
        "copyReviewStartedInD31",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "advantageLabCaseAdded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "runtimeLoweringChanged",
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
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
        "artifactType": "eml_checked_witness_review_next_decision",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_pause_decision_no_public_copy_no_implementation",
        "source": f"python/results/eml_d31_checked_witness_review_next_decision/eml_d31_checked_witness_review_next_decision_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d31_checked_witness_review_next_decision_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D32 as a private subtraction-family pause and checked-witness index freeze packet; do not publish D30 copy directly.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D31 Checked Witness Review Next Decision",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D31 chooses the next private branch after the checked-witness copy review.",
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
            f"- family deepening pause selected: `{payload['summary']['familyDeepeningPauseSelected']}`",
            f"- checked witness index freeze planned: `{payload['summary']['checkedWitnessIndexFreezePlanned']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
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
    result_path = out_dir / f"eml_d31_checked_witness_review_next_decision_{STAMP}.json"
    report_path = report_dir / f"eml_d31_checked_witness_review_next_decision_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d31_checked_witness_review_next_decision.json"
    feed_path = command_feed_dir / f"eml_d31_checked_witness_review_next_decision_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d31_checked_witness_review_next_decision")
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
    print("EML_D31_CHECKED_WITNESS_REVIEW_NEXT_DECISION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
