#!/usr/bin/env python3
"""EML-D52 constant-coordinate review next-action selector."""

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

from scripts import eml_d51_constant_coordinate_delta_copy_review_packet as d51  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_constant_coordinate_review_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D52_CONSTANT_COORDINATE_REVIEW_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "pause_freeze_selected": True,
    "pause_started": False,
    "freeze_packet_started": False,
    "new_bounded_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "human_public_copy_gate_selected": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "arbitrary_depth_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D52 selects the next private action after D51; it does not start the pause/freeze packet, proof work, implementation, or public copy.",
    "D52 preserves the D51 copy-review caveats, the local exp (1 + 1) spelling note, and the non-duplicate boundary against the D10 constants bundle.",
    "D52 does not approve public copy, promote public surfaces, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery or broad EML superiority.",
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
    review = d51.build_payload(atlas_gate_path)
    d51.validate_payload(review)
    options = [
        decision_option(
            "constant_coordinate_branch_pause_freeze_packet",
            "private_pause_freeze_lane",
            "selected_next",
            82,
            "EML-D53 constant-coordinate branch pause and checked-witness delta freeze packet",
            [
                "D48 checked the witness, D49 surfaced it privately, and D51 completed private delta copy review.",
                "A pause/freeze packet stabilizes the checked constant-coordinate delta before another proof branch.",
                "The pause can preserve the local exp (1 + 1) spelling note, D51 caveats, and public hold.",
            ],
            [
                "define exactly what is frozen",
                "preserve D51 caveats and blocked phrases",
                "do not treat the pause as public copy approval",
            ],
        ),
        decision_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "candidate_later_after_pause",
            61,
            "Future bounded identity branch selector",
            [
                "A new bounded identity branch remains useful after the constant-coordinate delta is frozen.",
                "Starting it immediately would skip stabilization of the D51 copy-review boundary.",
            ],
            [
                "requires one precise statement",
                "must avoid duplicating checked witnesses",
                "must keep implementation separate",
            ],
        ),
        decision_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later_after_pause",
            53,
            "Future bounded trig identity feasibility selector",
            [
                "The trig probe remains a possible frontier candidate.",
                "It has higher guard and negative-control risk than freezing the just-reviewed witness.",
            ],
            [
                "requires exact bounded interval guard",
                "requires negative controls",
                "avoid broad EML advantage language",
            ],
        ),
        decision_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_human_approval",
            40,
            "Future human-approved constant-coordinate public copy gate",
            [
                "D51 produced private-reviewable wording, but no human approval is recorded.",
                "Public copy must remain parked behind explicit approval.",
            ],
            [
                "requires explicit human approval",
                "must preserve local spelling and non-duplicate caveats",
                "must not imply runtime advantage or public readiness",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceReview": review["artifactId"],
        "selectedWitnessName": review["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": review["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": review["summary"]["sourceSelectedFamily"],
        "sourceProposedStatement": review["summary"]["sourceProposedStatement"],
        "checkedLeanStatement": review["summary"]["checkedLeanStatement"],
        "localSpellingUsesOnePlusOne": review["summary"]["localSpellingUsesOnePlusOne"],
        "existingConstantWitnessName": review["summary"]["existingConstantWitnessName"],
        "duplicatesExistingConstantWitness": review["summary"]["duplicatesExistingConstantWitness"],
        "d51CopyReviewStarted": review["summary"]["copyReviewStarted"],
        "d51PrivateCopyReviewOnly": review["summary"]["privateCopyReviewOnly"],
        "d51DeltaCopyReviewOnly": review["summary"]["deltaCopyReviewOnly"],
        "d51WitnessRowCount": review["summary"]["witnessRowCount"],
        "d51RequiredCaveatCount": review["summary"]["requiredCaveatCount"],
        "d51BlockedGlobalPhraseCount": review["summary"]["blockedGlobalPhraseCount"],
        "guardCount": review["summary"]["guardCount"],
        "publicHoldPreserved": review["summary"]["publicHoldPreserved"],
        "runtimeBoundaryPreserved": review["summary"]["runtimeBoundaryPreserved"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "pauseFreezeSelected": True,
        "checkedWitnessDeltaFreezePlanned": True,
        "pauseStarted": False,
        "freezePacketStarted": False,
        "newBoundedBranchSelected": False,
        "boundedTrigFeasibilitySelected": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": review["summary"]["runtimeLoweringControl"],
        "logExpReplacementClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True for key in ["next_action_selected", "pause_freeze_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"next_action_selected", "pause_freeze_selected"}
        )
        and all(
            option["claimFlags"]["next_action_selected"] is True
            and option["claimFlags"]["pause_freeze_selected"] is True
            and all(
                value is False
                for key, value in option["claimFlags"].items()
                if key not in {"next_action_selected", "pause_freeze_selected"}
            )
            for option in options
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_constant_coordinate_review_next_selector_v0",
        "artifactId": "eml-d52-constant-coordinate-review-next-selector",
        "status": STATUS,
        "decision": "select_constant_coordinate_branch_pause_freeze_packet",
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
    if payload["sourceReview"] != "eml-d51-constant-coordinate-delta-copy-review-packet":
        raise ValueError("D52 must consume D51")
    if summary["selectedWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "zero_coordinate_exp_two_boundary":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "constant_coordinate_refresh":
        raise ValueError("unexpected family")
    if summary["sourceProposedStatement"] != "eml 0 (exp 2) = -1":
        raise ValueError("unexpected source statement")
    if summary["checkedLeanStatement"] != "eml 0 (exp (1 + 1)) = -1":
        raise ValueError("unexpected checked Lean statement")
    for key in [
        "localSpellingUsesOnePlusOne",
        "d51CopyReviewStarted",
        "d51PrivateCopyReviewOnly",
        "d51DeltaCopyReviewOnly",
        "publicHoldPreserved",
        "runtimeBoundaryPreserved",
        "pauseFreezeSelected",
        "checkedWitnessDeltaFreezePlanned",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["existingConstantWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("unexpected existing constants witness")
    if summary["duplicatesExistingConstantWitness"] is not False:
        raise ValueError("non-duplicate boundary drift")
    if summary["guardCount"] != 0:
        raise ValueError("constant-coordinate witness should not add guards")
    if summary["d51WitnessRowCount"] != 1:
        raise ValueError("expected one D51 witness row")
    if summary["d51RequiredCaveatCount"] != 8 or summary["d51BlockedGlobalPhraseCount"] != 10:
        raise ValueError("D51 caveat/blocker counts drifted")
    if summary["optionCount"] != 4:
        raise ValueError("expected four options")
    if summary["selectedOptionId"] != "constant_coordinate_branch_pause_freeze_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D53 constant-coordinate branch pause and checked-witness delta freeze packet":
        raise ValueError("unexpected next artifact")
    for key in [
        "pauseStarted",
        "freezePacketStarted",
        "newBoundedBranchSelected",
        "boundedTrigFeasibilitySelected",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "advantageLabCaseAdded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_log_exp_and_arithmetic_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in ["next_action_selected", "pause_freeze_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "pause_freeze_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_constant_coordinate_review_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_pause_freeze_choice_no_public_copy_no_implementation",
        "source": f"python/results/eml_d52_constant_coordinate_review_next_selector/eml_d52_constant_coordinate_review_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d52_constant_coordinate_review_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D53 as a private constant-coordinate branch pause and checked-witness delta freeze packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D52 Constant-Coordinate Review Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D52 chooses the next private action after the constant-coordinate delta copy review without starting it.",
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
            f"- source statement: `{payload['summary']['sourceProposedStatement']}`",
            f"- checked Lean statement: `{payload['summary']['checkedLeanStatement']}`",
            f"- public hold preserved: `{payload['summary']['publicHoldPreserved']}`",
            f"- pause started: `{payload['summary']['pauseStarted']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
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
    result_path = out_dir / f"eml_d52_constant_coordinate_review_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d52_constant_coordinate_review_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d52_constant_coordinate_review_next_selector.json"
    feed_path = command_feed_dir / f"eml_d52_constant_coordinate_review_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--atlas-gate-path", type=Path, default=ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d52_constant_coordinate_review_next_selector")
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
    print("EML_D52_CONSTANT_COORDINATE_REVIEW_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
