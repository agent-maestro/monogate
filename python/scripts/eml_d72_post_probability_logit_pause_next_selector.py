#!/usr/bin/env python3
"""EML-D72 post probability-logit pause private next-action selector."""

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

from scripts import eml_d71_probability_logit_branch_pause_freeze_packet as d71  # noqa: E402

DATE = "2026-06-03"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_post_probability_logit_pause_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D72_POST_PROBABILITY_LOGIT_PAUSE_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "next_bounded_identity_branch_selected": True,
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
    "EML-D72 is a selector-only private next-action packet after the D71 probability-logit pause/freeze.",
    "D72 selects a next bounded identity branch selector for a later phase; it does not define a new statement, edit MachLib, typecheck Lean, or start a proof attempt.",
    "D72 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p/logit replacement, or broad EML superiority.",
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
    freeze = d71.build_payload(atlas_gate_path)
    d71.validate_payload(freeze)
    frozen_row = freeze_row_by_id(freeze, "probability_logit_boundary_coordinate_checked_copy")
    options = [
        selector_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "selected_next",
            84,
            "EML-D73 bounded identity branch candidate selector",
            [
                "D71 froze the probability-logit checked-witness copy, so the private identity lane can safely choose a fresh bounded branch.",
                "A selector phase can enforce non-duplication, guard requirements, and negative controls before any proof work or MachLib edit.",
                "This resumes EML research while public copy, implementation, runtime lowering, and laptop/course scope remain blocked.",
            ],
            [
                "must define exactly one next bounded identity candidate",
                "must avoid duplicating checked MachLib witnesses",
                "must preserve protected log/log1p as runtime controls unless separately justified",
                "must keep proof-attempt and implementation claims false unless separately selected",
            ],
        ),
        selector_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later",
            60,
            "Future bounded trig identity feasibility selector",
            [
                "A bounded trigonometric probe remains useful, but it has higher guard and negative-control risk.",
                "It should follow a simpler bounded identity selector unless the reviewer explicitly redirects.",
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
            39,
            "Future human-approved probability-logit public copy gate",
            [
                "D71 froze private copy boundaries but no human approval is recorded.",
                "Public copy should remain behind an explicit human gate after private selector work stabilizes.",
            ],
            [
                "requires explicit human approval",
                "must reuse D71 frozen caveats and blocked phrases",
                "must not imply log/log1p/logit replacement, runtime advantage, or public readiness",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceFreezePacket": freeze["artifactId"],
        "branchPauseStarted": freeze["summary"]["branchPauseStarted"],
        "checkedWitnessCopyFrozen": freeze["summary"]["checkedWitnessCopyFrozen"],
        "privateFreezePacket": freeze["summary"]["privateFreezePacket"],
        "frozenWitnessName": frozen_row["machlibName"],
        "frozenCheckedStatement": frozen_row["checkedStatement"],
        "frozenGuardCount": len(frozen_row["guards"]),
        "frozenGuards": list(frozen_row["guards"]),
        "frozenCaveatCount": len(frozen_row["frozenCaveats"]),
        "frozenBlockedPhraseCount": len(frozen_row["frozenBlockedPhrases"]),
        "sourceNegativeControlCount": freeze["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": freeze["summary"]["sourceBlockerCount"],
        "runtimeLoweringControl": freeze["summary"]["runtimeLoweringControl"],
        "runtimeGuardrailStatus": freeze["summary"]["runtimeGuardrailStatus"],
        "guardBoundaryStatus": freeze["summary"]["guardBoundaryStatus"],
        "publicAtlasStatus": freeze["summary"]["publicAtlasStatus"],
        "optionCount": len(options),
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "nextActionSelected": True,
        "nextBoundedIdentityBranchSelected": True,
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
        "logExpReplacementClaim": False,
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsSelectorOnly": all(
            CLAIM_FLAGS[key] is True
            for key in ["next_action_selected", "next_bounded_identity_branch_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"next_action_selected", "next_bounded_identity_branch_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_post_probability_logit_pause_next_selector_v0",
        "artifactId": "eml-d72-post-probability-logit-pause-next-selector",
        "status": STATUS,
        "decision": "select_next_bounded_identity_branch_selector",
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
    if payload["sourceFreezePacket"] != "eml-d71-probability-logit-branch-pause-freeze-packet":
        raise ValueError("D72 must consume D71")
    for key in [
        "branchPauseStarted",
        "checkedWitnessCopyFrozen",
        "privateFreezePacket",
        "nextActionSelected",
        "nextBoundedIdentityBranchSelected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["frozenWitnessName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
        raise ValueError("unexpected frozen witness")
    if summary["frozenCheckedStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected frozen checked statement")
    if summary["frozenGuardCount"] != 2 or summary["frozenGuards"] != ["0 < p", "p < 1"]:
        raise ValueError("guard boundary drift")
    if summary["frozenCaveatCount"] != 9 or summary["frozenBlockedPhraseCount"] != 12:
        raise ValueError("frozen caveat/blocker counts drifted")
    if summary["sourceNegativeControlCount"] != 4 or summary["sourceBlockerCount"] != 4:
        raise ValueError("source negative control/blocker counts drifted")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["runtimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("runtime guardrail drift")
    if summary["guardBoundaryStatus"] != "guarded_domain_boundary_required":
        raise ValueError("guard boundary status drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    if summary["optionCount"] != 3:
        raise ValueError("expected three options")
    if summary["selectedOptionId"] != "next_bounded_identity_branch_selector":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D73 bounded identity branch candidate selector":
        raise ValueError("unexpected next artifact")
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
    for key in ["next_action_selected", "next_bounded_identity_branch_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "next_bounded_identity_branch_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_post_probability_logit_pause_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_next_bounded_identity_branch_no_public_copy_no_implementation",
        "source": f"python/results/eml_d72_post_probability_logit_pause_next_selector/eml_d72_post_probability_logit_pause_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d72_post_probability_logit_pause_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D73 as a bounded identity branch candidate selector.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D72 Post Probability-Logit Pause Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D72 selects the next private action after the D71 probability-logit pause/freeze without starting it.",
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
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
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
    result_path = out_dir / f"eml_d72_post_probability_logit_pause_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d72_post_probability_logit_pause_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d72_post_probability_logit_pause_next_selector.json"
    feed_path = command_feed_dir / f"eml_d72_post_probability_logit_pause_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d72_post_probability_logit_pause_next_selector")
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
    print("EML_D72_POST_PROBABILITY_LOGIT_PAUSE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
