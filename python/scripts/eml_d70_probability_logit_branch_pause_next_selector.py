#!/usr/bin/env python3
"""EML-D70 probability-logit copy-review next-action selector."""

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

from scripts import eml_d69_probability_logit_checked_witness_copy_review_packet as d69  # noqa: E402

DATE = "2026-06-03"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_probability_logit_branch_pause_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D70_PROBABILITY_LOGIT_BRANCH_PAUSE_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "branch_pause_freeze_selected": True,
    "pause_started": False,
    "freeze_packet_started": False,
    "new_bounded_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_log_replacement_claim": False,
    "protected_log1p_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
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
    "EML-D70 selects the next private action after D69; it does not start the pause/freeze packet, proof work, implementation, or public copy.",
    "D70 preserves the D69 checked statement, probability interval guards, caveats, blocked phrases, and protected log/log1p runtime-control boundary.",
    "D70 does not approve public copy, promote public surfaces, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, replace protected log/log1p, or claim theorem discovery, runtime advantage, logit replacement, or broad EML superiority.",
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
    review = d69.build_payload(atlas_gate_path)
    d69.validate_payload(review)
    options = [
        decision_option(
            "probability_logit_branch_pause_freeze_packet",
            "private_pause_freeze_lane",
            "selected_next",
            86,
            "EML-D71 probability-logit branch pause and checked-witness copy freeze packet",
            [
                "D66 checked the witness, D67 surfaced it privately, D68 selected copy review, and D69 completed private copy review.",
                "A pause/freeze packet can stabilize the guarded statement, copy caveats, blocked phrases, runtime-control boundary, and public hold before another branch.",
                "The pause keeps the probability-logit witness reviewer-usable without treating private copy review as public approval.",
            ],
            [
                "define exactly what is frozen",
                "preserve D69 caveats, blocked phrases, and both interval guards",
                "do not treat the pause as public copy approval",
            ],
        ),
        decision_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "candidate_later_after_pause",
            64,
            "Future bounded identity branch selector",
            [
                "A new bounded identity branch remains useful after the probability-logit copy boundary is frozen.",
                "Starting it immediately would skip stabilization of the D69 copy-review boundary.",
            ],
            [
                "requires one precise non-duplicate statement",
                "must not start MachLib proof work in this selector",
                "must preserve protected log/log1p runtime controls",
            ],
        ),
        decision_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later_after_pause",
            55,
            "Future bounded trig identity feasibility selector",
            [
                "The trig probe remains a possible frontier candidate.",
                "It has higher guard and negative-control risk than freezing the just-reviewed probability-logit witness copy.",
            ],
            [
                "requires exact bounded interval guards",
                "requires negative controls",
                "avoid broad EML advantage language",
            ],
        ),
        decision_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_human_approval",
            42,
            "Future human-approved probability-logit public copy gate",
            [
                "D69 produced private-reviewable wording, but no human approval is recorded.",
                "Public copy should remain parked behind explicit approval after the private freeze packet.",
            ],
            [
                "requires explicit human approval",
                "must preserve protected log/log1p runtime-control caveats",
                "must not imply runtime advantage, public readiness, log replacement, log1p replacement, or logit replacement",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceReview": review["artifactId"],
        "sourceSelectedOptionId": review["summary"]["selectedOptionId"],
        "selectedWitnessName": review["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": review["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": review["summary"]["sourceSelectedFamily"],
        "checkedStatement": review["summary"]["checkedStatement"],
        "machlibFile": review["summary"]["machlibFile"],
        "guardCount": review["summary"]["guardCount"],
        "sourceDerivedDomainObligationCount": review["summary"]["sourceDerivedDomainObligationCount"],
        "sourceNegativeControlCount": review["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": review["summary"]["sourceBlockerCount"],
        "d67SurfaceRowCount": review["summary"]["d67SurfaceRowCount"],
        "d69CopyReviewStarted": review["summary"]["copyReviewStarted"],
        "d69PrivateCopyReviewOnly": review["summary"]["privateCopyReviewOnly"],
        "d69CheckedWitnessCopyReviewOnly": review["summary"]["checkedWitnessCopyReviewOnly"],
        "d69WitnessRowCount": review["summary"]["witnessRowCount"],
        "d69RequiredCaveatCount": review["summary"]["requiredCaveatCount"],
        "d69BlockedGlobalPhraseCount": review["summary"]["blockedGlobalPhraseCount"],
        "d69RowRequiredCaveatCount": review["summary"]["rowRequiredCaveatCount"],
        "d69RowBlockedPhraseCount": review["summary"]["rowBlockedPhraseCount"],
        "guardBoundaryStatus": review["summary"]["guardBoundaryStatus"],
        "runtimeGuardrailStatus": review["summary"]["runtimeGuardrailStatus"],
        "publicAtlasStatus": review["summary"]["publicAtlasStatus"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "nextActionSelected": True,
        "branchPauseFreezeSelected": True,
        "checkedWitnessCopyFreezePlanned": True,
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
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": review["summary"]["runtimeLoweringControl"],
        "logExpReplacementClaim": False,
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True for key in ["next_action_selected", "branch_pause_freeze_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"next_action_selected", "branch_pause_freeze_selected"}
        )
        and all(
            option["claimFlags"]["next_action_selected"] is True
            and option["claimFlags"]["branch_pause_freeze_selected"] is True
            and all(
                value is False
                for key, value in option["claimFlags"].items()
                if key not in {"next_action_selected", "branch_pause_freeze_selected"}
            )
            for option in options
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_probability_logit_branch_pause_next_selector_v0",
        "artifactId": "eml-d70-probability-logit-branch-pause-next-selector",
        "status": STATUS,
        "decision": "select_probability_logit_branch_pause_freeze_packet",
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
    if payload["sourceReview"] != "eml-d69-probability-logit-checked-witness-copy-review-packet":
        raise ValueError("D70 must consume D69")
    if summary["sourceSelectedOptionId"] != "probability_logit_checked_witness_copy_review_packet":
        raise ValueError("unexpected D69 selected option")
    if summary["selectedWitnessName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "probability_logit_boundary_coordinate":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "guarded_probability_log_coordinate":
        raise ValueError("unexpected family")
    if summary["checkedStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected checked statement")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    for key in [
        "d69CopyReviewStarted",
        "d69PrivateCopyReviewOnly",
        "d69CheckedWitnessCopyReviewOnly",
        "nextActionSelected",
        "branchPauseFreezeSelected",
        "checkedWitnessCopyFreezePlanned",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 2 or summary["sourceDerivedDomainObligationCount"] != 2:
        raise ValueError("probability-logit guard/domain counts drifted")
    if summary["sourceNegativeControlCount"] != 4 or summary["sourceBlockerCount"] != 4:
        raise ValueError("negative control/blocker counts drifted")
    if summary["d67SurfaceRowCount"] != 5:
        raise ValueError("D67 row count drift")
    if summary["d69WitnessRowCount"] != 1:
        raise ValueError("expected one D69 witness row")
    if summary["d69RequiredCaveatCount"] != 9 or summary["d69BlockedGlobalPhraseCount"] != 12:
        raise ValueError("D69 caveat/blocker counts drifted")
    if summary["d69RowRequiredCaveatCount"] != 6 or summary["d69RowBlockedPhraseCount"] != 10:
        raise ValueError("D69 row copy boundary counts drifted")
    if summary["guardBoundaryStatus"] != "guarded_domain_boundary_required":
        raise ValueError("guard boundary drift")
    if summary["runtimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("runtime guardrail drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    if summary["optionCount"] != 4:
        raise ValueError("expected four options")
    if summary["selectedOptionId"] != "probability_logit_branch_pause_freeze_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D71 probability-logit branch pause and checked-witness copy freeze packet":
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
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedLogReplacementClaim",
        "protectedLog1pReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in ["next_action_selected", "branch_pause_freeze_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "branch_pause_freeze_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_probability_logit_branch_pause_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_probability_logit_pause_freeze_choice_no_public_copy_no_implementation",
        "source": f"python/results/eml_d70_probability_logit_branch_pause_next_selector/eml_d70_probability_logit_branch_pause_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d70_probability_logit_branch_pause_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D71 as a private probability-logit branch pause and checked-witness copy freeze packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D70 Probability Logit Branch Pause Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D70 chooses the next private action after the probability-logit checked-witness copy review without starting it.",
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
            f"- checked statement: `{payload['summary']['checkedStatement']}`",
            f"- checked witness: `{payload['summary']['selectedWitnessName']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- branch pause/freeze selected: `{payload['summary']['branchPauseFreezeSelected']}`",
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
    result_path = out_dir / f"eml_d70_probability_logit_branch_pause_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d70_probability_logit_branch_pause_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d70_probability_logit_branch_pause_next_selector.json"
    feed_path = command_feed_dir / f"eml_d70_probability_logit_branch_pause_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d70_probability_logit_branch_pause_next_selector")
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
    print("EML_D70_PROBABILITY_LOGIT_BRANCH_PAUSE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
