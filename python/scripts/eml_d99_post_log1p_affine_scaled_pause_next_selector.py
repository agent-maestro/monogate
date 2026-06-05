#!/usr/bin/env python3
"""EML-D99 post log1p affine-scaled pause private next-action selector."""

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

from scripts import eml_d98_log1p_affine_scaled_branch_pause_freeze_packet as d98  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_post_log1p_affine_scaled_pause_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D99_POST_LOG1P_AFFINE_SCALED_PAUSE_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "consolidation_review_selected": True,
    "next_bounded_identity_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "private_reviewer_response_intake_selected": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
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
    "broad_log1p_family_claim": False,
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
    "EML-D99 is a selector-only private next-action packet after the D98 log1p affine-scaled branch pause/freeze.",
    "D99 selects a private bounded-artifact target-set consolidation review for a later phase; it does not create the review, define a new identity candidate, edit MachLib, typecheck Lean, start proof work, or implement runtime lowering.",
    "D99 does not record reviewer approval or rejection, approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p replacement, broad log1p-family theory, or broad EML superiority.",
]


def selector_option(
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


def freeze_row_by_id(payload: dict[str, Any], freeze_id: str) -> dict[str, Any]:
    return next(item for item in payload["freezeRows"] if item["freezeId"] == freeze_id)


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    freeze = d98.build_payload(atlas_gate_path)
    d98.validate_payload(freeze)
    frozen_row = freeze_row_by_id(freeze, "log1p_affine_scaled_boundary_coordinate_checked_copy")
    options = [
        selector_option(
            "bounded_artifact_target_set_consolidation_review",
            "private_consolidation_lane",
            "selected_next",
            94,
            "EML-D100 bounded artifact target-set consolidation review",
            [
                "D98 froze the affine log1p checked-witness copy boundary, closing the current log/log1p/log1m micro-lane for private handoff stability.",
                "The D-series operating rule now prefers consolidation after the D91-D98 affine branch instead of continuing to grow bounded identities indefinitely.",
                "A target-set review can count the current high-quality checked witnesses, identify gaps, and decide whether the next move should be public witness copy, SDK/compiler guard documentation, reviewer intake, or one materially different bounded candidate.",
            ],
            [
                "must not promote public copy or public Atlas entries",
                "must not claim the bounded set is complete",
                "must keep runtime, proof, MachLib, and reviewer-decision claims false unless separately selected",
            ],
        ),
        selector_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "candidate_later_after_consolidation_review",
            61,
            "Future bounded identity branch selector",
            [
                "Another bounded identity may still be useful if the consolidation review finds a materially different gap.",
                "Selecting it immediately would ignore the D-series cap and the newly frozen affine log1p branch boundary.",
            ],
            [
                "requires one precise non-duplicate candidate",
                "must be materially different from the existing log/log1p/log1m, subtraction, positive log-exp, probability-logit, and expm1 core",
                "must not start MachLib proof work in this selector",
            ],
        ),
        selector_option(
            "private_reviewer_response_intake",
            "private_review_lane",
            "candidate_later_requires_real_response",
            59,
            "Future private reviewer response intake",
            [
                "D98 is ready for private review, but this phase has no concrete reviewer response artifact.",
                "Reviewer response intake should wait until an actual response exists.",
            ],
            [
                "requires actual reviewer response artifact",
                "must distinguish request, approval, rejection, and hold",
                "must not treat a response as approval unless explicitly stated",
            ],
        ),
        selector_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later_after_consolidation_review",
            52,
            "Future bounded trig identity feasibility selector",
            [
                "A bounded trigonometric probe remains a possible frontier candidate.",
                "It should wait until the target-set review confirms that another identity branch is worth opening.",
            ],
            [
                "requires exact interval/domain guard",
                "requires negative controls before proof work",
                "must not imply broad EML advantage",
            ],
        ),
        selector_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_human_approval",
            38,
            "Future human-approved affine log1p public copy gate",
            [
                "D98 froze private copy boundaries but no human approval is recorded.",
                "Public copy should remain behind a separate human gate and likely after target-set consolidation.",
            ],
            [
                "requires explicit human approval",
                "must reuse D98 frozen caveats and blocked phrases",
                "must not imply log/log1p replacement, runtime advantage, broad family coverage, or public readiness",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceFreezePacket": freeze["artifactId"],
        "branchPauseStarted": freeze["summary"]["branchPauseStarted"],
        "checkedWitnessCopyFrozen": freeze["summary"]["checkedWitnessCopyFrozen"],
        "privateFreezePacket": freeze["summary"]["privateFreezePacket"],
        "duplicateShiftedBlocksPreserved": freeze["summary"]["duplicateShiftedBlocksPreserved"],
        "frozenWitnessName": frozen_row["machlibName"],
        "frozenCheckedStatement": frozen_row["checkedStatement"],
        "frozenGuardCount": len(frozen_row["guards"]),
        "frozenGuards": list(frozen_row["guards"]),
        "frozenCaveatCount": len(frozen_row["frozenCaveats"]),
        "frozenBlockedPhraseCount": len(frozen_row["frozenBlockedPhrases"]),
        "sourceNegativeControlCount": freeze["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": freeze["summary"]["sourceBlockerCount"],
        "sourceD96RequiredCaveatCount": freeze["summary"]["sourceD96RequiredCaveatCount"],
        "sourceD96BlockedGlobalPhraseCount": freeze["summary"]["sourceD96BlockedGlobalPhraseCount"],
        "sourceD96RowRequiredCaveatCount": freeze["summary"]["sourceD96RowRequiredCaveatCount"],
        "sourceD96RowBlockedPhraseCount": freeze["summary"]["sourceD96RowBlockedPhraseCount"],
        "runtimeLoweringControl": freeze["summary"]["runtimeLoweringControl"],
        "runtimeGuardrailStatus": freeze["summary"]["runtimeGuardrailStatus"],
        "guardBoundaryStatus": freeze["summary"]["guardBoundaryStatus"],
        "publicAtlasStatus": freeze["summary"]["publicAtlasStatus"],
        "optionCount": len(options),
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "nextActionSelected": True,
        "consolidationReviewSelected": True,
        "nextBoundedIdentityBranchSelected": False,
        "boundedTrigFeasibilitySelected": False,
        "privateReviewerResponseIntakeSelected": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
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
        "logExpReplacementClaim": False,
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsSelectorOnly": all(
            CLAIM_FLAGS[key] is True for key in ["next_action_selected", "consolidation_review_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"next_action_selected", "consolidation_review_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_post_log1p_affine_scaled_pause_next_selector_v0",
        "artifactId": "eml-d99-post-log1p-affine-scaled-pause-next-selector",
        "status": STATUS,
        "decision": "select_bounded_artifact_target_set_consolidation_review_after_log1p_affine_scaled_pause",
        "date": DATE,
        "sourceFreezePacket": freeze["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "selectorOptions": options,
        "selectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceFreezePacket"] != "eml-d98-log1p-affine-scaled-branch-pause-freeze-packet":
        raise ValueError("D99 must consume D98")
    for key in [
        "branchPauseStarted",
        "checkedWitnessCopyFrozen",
        "privateFreezePacket",
        "duplicateShiftedBlocksPreserved",
        "nextActionSelected",
        "consolidationReviewSelected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["frozenWitnessName"] != "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness":
        raise ValueError("unexpected frozen witness")
    if summary["frozenCheckedStatement"] != "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x":
        raise ValueError("unexpected frozen checked statement")
    if summary["frozenGuardCount"] != 1 or summary["frozenGuards"] != ["0 < 1 + a * x"]:
        raise ValueError("guard boundary drift")
    if summary["frozenCaveatCount"] != 10 or summary["frozenBlockedPhraseCount"] != 16:
        raise ValueError("frozen caveat/blocker counts drifted")
    if summary["sourceNegativeControlCount"] != 5 or summary["sourceBlockerCount"] != 5:
        raise ValueError("source negative control/blocker counts drifted")
    if summary["sourceD96RequiredCaveatCount"] != 10 or summary["sourceD96BlockedGlobalPhraseCount"] != 14:
        raise ValueError("D96 caveat/blocker counts drifted")
    if summary["sourceD96RowRequiredCaveatCount"] != 7 or summary["sourceD96RowBlockedPhraseCount"] != 13:
        raise ValueError("D96 row copy boundary counts drifted")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["runtimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("runtime guardrail drift")
    if summary["guardBoundaryStatus"] != "affine_scaled_positive_domain_boundary_required":
        raise ValueError("guard boundary status drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    if summary["optionCount"] != 5:
        raise ValueError("expected five options")
    if summary["selectedOptionId"] != "bounded_artifact_target_set_consolidation_review":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D100 bounded artifact target-set consolidation review":
        raise ValueError("unexpected next artifact")
    for key in [
        "nextBoundedIdentityBranchSelected",
        "boundedTrigFeasibilitySelected",
        "privateReviewerResponseIntakeSelected",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
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
    if summary["claimFlagsSelectorOnly"] is not True:
        raise ValueError("claim flags must remain selector-only")
    for key in ["next_action_selected", "consolidation_review_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "consolidation_review_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_post_log1p_affine_scaled_pause_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_consolidation_review_after_log1p_affine_scaled_pause_no_public_copy_no_implementation",
        "source": f"python/results/eml_d99_post_log1p_affine_scaled_pause_next_selector/eml_d99_post_log1p_affine_scaled_pause_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d99_post_log1p_affine_scaled_pause_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D100 as a private bounded artifact target-set consolidation review.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D99 Post Log1p Affine-Scaled Pause Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D99 selects the next private action after the D98 log1p affine-scaled pause/freeze without starting it.",
        "",
        "| Option | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for option in payload["selectorOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | {option['priorityScore']} | {option['nextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected next artifact: `{payload['summary']['selectedNextArtifact']}`",
            f"- frozen witness: `{payload['summary']['frozenWitnessName']}`",
            f"- frozen checked statement: `{payload['summary']['frozenCheckedStatement']}`",
            f"- duplicate shifted blocks preserved: `{payload['summary']['duplicateShiftedBlocksPreserved']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


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
    result_path = out_dir / f"eml_d99_post_log1p_affine_scaled_pause_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d99_post_log1p_affine_scaled_pause_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d99_post_log1p_affine_scaled_pause_next_selector.json"
    feed_path = command_feed_dir / f"eml_d99_post_log1p_affine_scaled_pause_next_selector_feed_{STAMP}.json"
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/eml_d99_post_log1p_affine_scaled_pause_next_selector",
    )
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
    print("EML_D99_POST_LOG1P_AFFINE_SCALED_PAUSE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
