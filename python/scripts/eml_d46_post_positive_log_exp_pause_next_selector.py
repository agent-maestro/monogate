#!/usr/bin/env python3
"""EML-D46 post positive-log-exp pause private next-action selector."""

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

from scripts import eml_d45_positive_log_exp_branch_pause_freeze_packet as d45  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_post_positive_log_exp_pause_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D46_POST_POSITIVE_LOG_EXP_PAUSE_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "constant_coordinate_refresh_selected": True,
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
    "EML-D46 is a selector-only private next-action packet after the D45 positive log-exp pause/freeze.",
    "D46 selects a constant-coordinate refresh selector for a later phase; it does not define a new statement, edit MachLib, typecheck Lean, or start a proof attempt.",
    "D46 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/exp replacement, or broad EML superiority.",
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
    freeze = d45.build_payload(atlas_gate_path)
    d45.validate_payload(freeze)
    frozen_row = freeze_row_by_id(freeze, "positive_log_exp_roundtrip_checked_delta")
    options = [
        selector_option(
            "constant_coordinate_refresh_selector",
            "private_bounded_identity_lane",
            "selected_next",
            77,
            "EML-D47 constant-coordinate refresh feasibility selector",
            [
                "D45 stabilized the positive log-exp branch, so the private identity lane can move to the lower-risk parked constants refresh.",
                "A selector phase can prevent duplicate D10/D11 constants work by requiring a new precise statement before implementation.",
                "This keeps the research side advancing without public-copy approval or laptop/course scope.",
            ],
            [
                "must avoid duplicating MachLib.Real.constants_zero_one_e_boundary_witness",
                "must define one precise non-duplicate statement before any MachLib edit",
                "must keep implementation and proof-attempt claims false in D47 unless separately selected",
            ],
        ),
        selector_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later",
            56,
            "Future bounded trig identity feasibility selector",
            [
                "A trigonometric probe remains a useful frontier candidate.",
                "It is more speculative than refreshing a small identity lane and needs stronger negative controls.",
            ],
            [
                "requires exact statement",
                "requires bounded interval guard",
                "requires negative controls before proof work",
            ],
        ),
        selector_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_human_approval",
            39,
            "Future human-approved positive log-exp public copy gate",
            [
                "D45 froze private copy boundaries but no human approval is recorded.",
                "Public copy should remain behind an explicit gate.",
            ],
            [
                "requires explicit human approval",
                "must reuse the frozen D45 caveats and blocked phrases",
                "must not imply log/exp replacement or runtime advantage",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceFreezePacket": freeze["artifactId"],
        "branchPauseStarted": freeze["summary"]["branchPauseStarted"],
        "checkedWitnessDeltaFrozen": freeze["summary"]["checkedWitnessDeltaFrozen"],
        "privateFreezePacket": freeze["summary"]["privateFreezePacket"],
        "frozenWitnessName": frozen_row["machlibName"],
        "frozenCheckedStatement": frozen_row["checkedStatement"],
        "frozenGuardCount": len(frozen_row["guards"]),
        "frozenCaveatCount": len(frozen_row["frozenCaveats"]),
        "frozenBlockedPhraseCount": len(frozen_row["frozenBlockedPhrases"]),
        "positiveDomainGuardRequired": freeze["summary"]["positiveDomainGuardRequired"],
        "publicHoldPreserved": freeze["summary"]["publicHoldPreserved"],
        "runtimeBoundaryPreserved": freeze["summary"]["runtimeBoundaryPreserved"],
        "runtimeLoweringControl": freeze["summary"]["runtimeLoweringControl"],
        "optionCount": len(options),
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "nextActionSelected": True,
        "constantCoordinateRefreshSelected": True,
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
        "logExpReplacementClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsSelectorOnly": all(
            CLAIM_FLAGS[key] is True
            for key in ["next_action_selected", "constant_coordinate_refresh_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"next_action_selected", "constant_coordinate_refresh_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_post_positive_log_exp_pause_next_selector_v0",
        "artifactId": "eml-d46-post-positive-log-exp-pause-next-selector",
        "status": STATUS,
        "decision": "select_constant_coordinate_refresh_selector",
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
    if payload["sourceFreezePacket"] != "eml-d45-positive-log-exp-branch-pause-freeze-packet":
        raise ValueError("D46 must consume D45")
    for key in [
        "branchPauseStarted",
        "checkedWitnessDeltaFrozen",
        "privateFreezePacket",
        "positiveDomainGuardRequired",
        "publicHoldPreserved",
        "runtimeBoundaryPreserved",
        "nextActionSelected",
        "constantCoordinateRefreshSelected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["frozenWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected frozen witness")
    if summary["frozenCheckedStatement"] != "0 < x -> exp (log x) = x":
        raise ValueError("unexpected frozen statement")
    if summary["frozenGuardCount"] != 1:
        raise ValueError("guard count drift")
    if summary["frozenCaveatCount"] != 5 or summary["frozenBlockedPhraseCount"] != 8:
        raise ValueError("frozen caveat/blocker counts drifted")
    if summary["optionCount"] != 3:
        raise ValueError("expected three options")
    if summary["selectedOptionId"] != "constant_coordinate_refresh_selector":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D47 constant-coordinate refresh feasibility selector":
        raise ValueError("unexpected next artifact")
    if summary["runtimeLoweringControl"] != "standard_log_exp_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    for key in [
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
    if summary["claimFlagsSelectorOnly"] is not True:
        raise ValueError("claim flags must remain selector-only")
    for key in ["next_action_selected", "constant_coordinate_refresh_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "constant_coordinate_refresh_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_post_positive_log_exp_pause_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_constant_coordinate_refresh_next_no_public_copy_no_implementation",
        "source": f"python/results/eml_d46_post_positive_log_exp_pause_next_selector/eml_d46_post_positive_log_exp_pause_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d46_post_positive_log_exp_pause_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D47 as a constant-coordinate refresh feasibility selector.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D46 Post Positive Log-Exp Pause Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D46 selects the next private action after the D45 positive log-exp pause/freeze without starting it.",
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
            f"- frozen statement: `{payload['summary']['frozenCheckedStatement']}`",
            f"- public hold preserved: `{payload['summary']['publicHoldPreserved']}`",
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
    result_path = out_dir / f"eml_d46_post_positive_log_exp_pause_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d46_post_positive_log_exp_pause_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d46_post_positive_log_exp_pause_next_selector.json"
    feed_path = command_feed_dir / f"eml_d46_post_positive_log_exp_pause_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d46_post_positive_log_exp_pause_next_selector")
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
    print("EML_D46_POST_POSITIVE_LOG_EXP_PAUSE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
