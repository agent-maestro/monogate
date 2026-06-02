#!/usr/bin/env python3
"""EML-D42 positive log-exp next-action selector."""

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

from scripts import eml_d41_positive_log_exp_witness_surface_review as d41  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_positive_log_exp_next_action_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D42_POSITIVE_LOG_EXP_NEXT_ACTION_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "copy_review_started": False,
    "pause_started": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
    "surface_updated": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "advantage_lab_case_added": False,
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
    "EML-D42 selects one next private research action after D41; it does not start copy review, pause/freeze, implementation, or proof work.",
    "D42 does not promote public Atlas or public education copy and does not claim log/exp replacement or runtime advantage.",
    "D42 keeps course drafting in the user/laptop-agent lane and touches no laptop-owned repos.",
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
    surface = d41.build_payload(atlas_gate_path)
    d41.validate_payload(surface)
    options = [
        decision_option(
            "positive_log_exp_delta_copy_review_packet",
            "private_copy_review_lane",
            "selected_next",
            78,
            "EML-D43 positive log-exp checked-witness delta copy review packet",
            [
                "D40 added a new checked witness after the D32 frozen six-witness index.",
                "D41 surfaced the witness privately and preserved public, runtime, and guard boundaries.",
                "A delta copy-review packet can update the private wording discipline without reopening course drafting or public copy.",
            ],
            [
                "copy review must remain private",
                "preserve the 0 < x guard",
                "avoid log/exp replacement and runtime advantage language",
                "do not treat D43 as public copy approval",
            ],
        ),
        decision_option(
            "constant_coordinate_refresh_selector",
            "private_bounded_identity_lane",
            "candidate_later",
            61,
            "Future constant-coordinate refresh selector",
            [
                "D38 parked constant-coordinate refresh as a bounded later option.",
                "It should wait until the new checked witness is copy-reviewed privately.",
            ],
            [
                "avoid duplicating existing constants witness",
                "define a new statement before implementation",
            ],
        ),
        decision_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later",
            49,
            "Future bounded trig identity feasibility selector",
            [
                "D38 parked trig identity work as a speculative later probe.",
                "It has higher guard and negative-control risk than reviewing the new checked witness.",
            ],
            [
                "requires exact statement",
                "requires stronger negative controls",
                "avoid broad EML advantage language",
            ],
        ),
        decision_option(
            "positive_log_exp_branch_pause",
            "private_pause_lane",
            "candidate_later",
            56,
            "Future positive log-exp branch pause/freeze packet",
            [
                "A pause may be appropriate after a private delta copy review establishes safe wording.",
                "D41 already holds public surfaces, so a pause can wait one selector step.",
            ],
            [
                "define pause criteria",
                "preserve the checked witness index",
                "do not turn pause into public copy approval",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceSurfaceReview": surface["artifactId"],
        "selectedWitnessName": surface["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": surface["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": surface["summary"]["sourceSelectedFamily"],
        "checkedWitnessRecordedPrivately": surface["summary"]["checkedWitnessRecordedPrivately"],
        "candidateProved": surface["summary"]["candidateProved"],
        "positiveDomainGuardRequired": surface["summary"]["positiveDomainGuardRequired"],
        "guardCount": surface["summary"]["guardCount"],
        "publicHoldPreserved": surface["summary"]["publicPromotionPerformed"] is False
        and surface["summary"]["publicEducationCandidate"] is False
        and surface["summary"]["surfaceUpdated"] is False,
        "runtimeBoundaryPreserved": surface["summary"]["runtimeLoweringChanged"] is False
        and surface["summary"]["logExpReplacementClaim"] is False,
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "copyReviewStarted": False,
        "pauseStarted": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "publicPromotionPerformed": False,
        "publicEducationCandidate": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "runtimeLoweringControl": surface["summary"]["runtimeLoweringControl"],
        "surfaceUpdated": False,
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
        "selectorType": "eml_positive_log_exp_next_action_selector_v0",
        "artifactId": "eml-d42-positive-log-exp-next-action-selector",
        "status": STATUS,
        "decision": "select_positive_log_exp_delta_copy_review_packet",
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
    if payload["sourceSurfaceReview"] != "eml-d41-positive-log-exp-witness-surface-review":
        raise ValueError("D42 must consume D41")
    if summary["selectedWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("unexpected selected candidate")
    if summary["sourceSelectedFamily"] != "positive_domain_log_exp_roundtrip":
        raise ValueError("unexpected selected family")
    for key in ["checkedWitnessRecordedPrivately", "candidateProved", "positiveDomainGuardRequired", "publicHoldPreserved", "runtimeBoundaryPreserved"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 1:
        raise ValueError("guard count drift")
    if summary["optionCount"] != 4:
        raise ValueError("expected four options")
    if summary["selectedOptionId"] != "positive_log_exp_delta_copy_review_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D43 positive log-exp checked-witness delta copy review packet":
        raise ValueError("unexpected next artifact")
    for key in [
        "copyReviewStarted",
        "pauseStarted",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "publicPromotionPerformed",
        "publicEducationCandidate",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "surfaceUpdated",
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
        "artifactType": "eml_positive_log_exp_next_action_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_next_action_selector_no_copy_review_no_implementation",
        "source": f"python/results/eml_d42_positive_log_exp_next_action_selector/eml_d42_positive_log_exp_next_action_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d42_positive_log_exp_next_action_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D43 as a private positive log-exp checked-witness delta copy review packet; do not publish copy.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D42 Positive Log-Exp Next-Action Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D42 chooses the next private research action after D41 without starting it.",
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
            f"- public hold preserved: `{payload['summary']['publicHoldPreserved']}`",
            f"- runtime boundary preserved: `{payload['summary']['runtimeBoundaryPreserved']}`",
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
    result_path = out_dir / f"eml_d42_positive_log_exp_next_action_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d42_positive_log_exp_next_action_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d42_positive_log_exp_next_action_selector.json"
    feed_path = command_feed_dir / f"eml_d42_positive_log_exp_next_action_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d42_positive_log_exp_next_action_selector")
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
    print("EML_D42_POSITIVE_LOG_EXP_NEXT_ACTION_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
