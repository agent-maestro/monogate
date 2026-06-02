#!/usr/bin/env python3
"""EML-D44 positive log-exp review next selector."""

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

from scripts import eml_d43_positive_log_exp_delta_copy_review_packet as d43  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_positive_log_exp_review_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D44_POSITIVE_LOG_EXP_REVIEW_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "pause_started": False,
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
    "EML-D44 selects the next private action after D43; it does not start a pause/freeze packet, approve public copy, edit MachLib, or typecheck Lean.",
    "D44 keeps the positive log-exp witness private and does not claim log/exp replacement, runtime advantage, theorem discovery, or broad EML superiority.",
    "D44 does not update courses, consume laptop artifacts, or touch laptop-owned repos.",
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
    review = d43.build_payload(atlas_gate_path)
    d43.validate_payload(review)
    options = [
        decision_option(
            "positive_log_exp_branch_pause_freeze_packet",
            "private_pause_freeze_lane",
            "selected_next",
            81,
            "EML-D45 positive log-exp branch pause and checked-witness delta freeze packet",
            [
                "D40 checked the witness, D41 surfaced it privately, and D43 completed private delta copy review.",
                "A pause/freeze packet stabilizes the new one-witness delta before another proof branch.",
                "The pause can preserve the public hold and the required 0 < x guard.",
            ],
            [
                "define exactly what is frozen",
                "preserve D43 caveats and blocked phrases",
                "do not treat the pause as public copy approval",
            ],
        ),
        decision_option(
            "constant_coordinate_refresh_selector",
            "private_bounded_identity_lane",
            "candidate_later_after_pause",
            62,
            "Future constant-coordinate refresh selector",
            [
                "D38 parked this option and it remains viable after the positive log-exp branch is paused.",
                "Starting it immediately would skip the D43 delta-copy stabilization step.",
            ],
            [
                "avoid duplicating existing constants witness",
                "define a new statement before implementation",
            ],
        ),
        decision_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later_after_pause",
            51,
            "Future bounded trig identity feasibility selector",
            [
                "A trig feasibility probe remains a possible later frontier.",
                "It carries higher guard and negative-control risk than freezing the just-reviewed witness.",
            ],
            [
                "requires exact statement",
                "requires stronger negative controls",
                "avoid broad EML advantage language",
            ],
        ),
        decision_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_human_approval",
            47,
            "Future human-approved positive log-exp public copy gate",
            [
                "D43 produced private-reviewable wording, but no human approval is recorded.",
                "Public copy must remain parked behind explicit approval.",
            ],
            [
                "requires explicit human approval",
                "must reuse D43 caveats and blocked phrases",
                "must not imply log/exp replacement or runtime advantage",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceReview": review["artifactId"],
        "selectedWitnessName": review["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": review["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": review["summary"]["sourceSelectedFamily"],
        "d43CopyReviewStarted": review["summary"]["copyReviewStarted"],
        "d43PrivateCopyReviewOnly": review["summary"]["privateCopyReviewOnly"],
        "d43DeltaCopyReviewOnly": review["summary"]["deltaCopyReviewOnly"],
        "d43WitnessRowCount": review["summary"]["witnessRowCount"],
        "d43RequiredCaveatCount": review["summary"]["requiredCaveatCount"],
        "d43BlockedGlobalPhraseCount": review["summary"]["blockedGlobalPhraseCount"],
        "positiveDomainGuardRequired": review["summary"]["positiveDomainGuardRequired"],
        "guardCount": review["summary"]["guardCount"],
        "publicHoldPreserved": review["summary"]["publicHoldPreserved"],
        "runtimeBoundaryPreserved": review["summary"]["runtimeBoundaryPreserved"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "branchPauseSelected": True,
        "checkedWitnessDeltaFreezePlanned": True,
        "newBoundedBranchSelected": False,
        "humanApprovedPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "pauseStarted": False,
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
        "logExpReplacementClaim": False,
        "runtimeLoweringControl": review["summary"]["runtimeLoweringControl"],
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsBounded": CLAIM_FLAGS["next_action_selected"] is True
        and all(value is False for key, value in CLAIM_FLAGS.items() if key != "next_action_selected")
        and all(
            option["claimFlags"]["next_action_selected"] is True
            and all(value is False for key, value in option["claimFlags"].items() if key != "next_action_selected")
            for option in options
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_positive_log_exp_review_next_selector_v0",
        "artifactId": "eml-d44-positive-log-exp-review-next-selector",
        "status": STATUS,
        "decision": "select_positive_log_exp_branch_pause_freeze_packet",
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
    if payload["sourceReview"] != "eml-d43-positive-log-exp-delta-copy-review-packet":
        raise ValueError("D44 must consume D43")
    if summary["selectedWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "positive_domain_log_exp_roundtrip":
        raise ValueError("unexpected family")
    for key in [
        "d43CopyReviewStarted",
        "d43PrivateCopyReviewOnly",
        "d43DeltaCopyReviewOnly",
        "positiveDomainGuardRequired",
        "publicHoldPreserved",
        "runtimeBoundaryPreserved",
        "branchPauseSelected",
        "checkedWitnessDeltaFreezePlanned",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 1:
        raise ValueError("guard count drift")
    if summary["d43WitnessRowCount"] != 1:
        raise ValueError("expected one D43 witness row")
    if summary["d43RequiredCaveatCount"] != 5 or summary["d43BlockedGlobalPhraseCount"] != 8:
        raise ValueError("D43 caveat/blocker counts drifted")
    if summary["optionCount"] != 4:
        raise ValueError("expected four options")
    if summary["selectedOptionId"] != "positive_log_exp_branch_pause_freeze_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D45 positive log-exp branch pause and checked-witness delta freeze packet":
        raise ValueError("unexpected next artifact")
    for key in [
        "newBoundedBranchSelected",
        "humanApprovedPublicCopyGateSelected",
        "humanApprovalRecorded",
        "pauseStarted",
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
    if summary["runtimeLoweringControl"] != "standard_log_exp_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    if payload["claimFlags"]["next_action_selected"] is not True:
        raise ValueError("next action selected flag must be true")
    for key, value in payload["claimFlags"].items():
        if key != "next_action_selected" and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_positive_log_exp_review_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_pause_freeze_choice_no_public_copy_no_implementation",
        "source": f"python/results/eml_d44_positive_log_exp_review_next_selector/eml_d44_positive_log_exp_review_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d44_positive_log_exp_review_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D45 as a private positive log-exp branch pause and checked-witness delta freeze packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D44 Positive Log-Exp Review Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D44 chooses the next private action after the positive log-exp delta copy review without starting it.",
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
            f"- branch pause selected: `{payload['summary']['branchPauseSelected']}`",
            f"- public hold preserved: `{payload['summary']['publicHoldPreserved']}`",
            f"- runtime boundary preserved: `{payload['summary']['runtimeBoundaryPreserved']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
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
    result_path = out_dir / f"eml_d44_positive_log_exp_review_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d44_positive_log_exp_review_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d44_positive_log_exp_review_next_selector.json"
    feed_path = command_feed_dir / f"eml_d44_positive_log_exp_review_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d44_positive_log_exp_review_next_selector")
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
    print("EML_D44_POSITIVE_LOG_EXP_REVIEW_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
