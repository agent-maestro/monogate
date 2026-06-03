#!/usr/bin/env python3
"""EML-D63 post expm1-boundary pause private next-action selector."""

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

from scripts import eml_d62_expm1_boundary_branch_pause_freeze_packet as d62  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_post_expm1_boundary_pause_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D63_POST_EXPM1_BOUNDARY_PAUSE_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "next_bounded_identity_branch_selected": True,
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
    "protected_expm1_replacement_claim": False,
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
    "EML-D63 is a selector-only private next-action packet after the D62 expm1-boundary pause/freeze.",
    "D63 selects a next bounded identity branch selector for a later phase; it does not define a new statement, edit MachLib, typecheck Lean, or start a proof attempt.",
    "D63 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, protected expm1 replacement, or broad EML superiority.",
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
    freeze = d62.build_payload(atlas_gate_path)
    d62.validate_payload(freeze)
    frozen_row = freeze_row_by_id(freeze, "expm1_boundary_identity_checked_copy")
    options = [
        selector_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "selected_next",
            82,
            "EML-D64 bounded identity branch candidate selector",
            [
                "D62 froze the expm1-boundary checked-witness copy, so the private identity lane can safely choose a fresh bounded branch.",
                "A selector phase can enforce non-duplication and guard requirements before any proof work or MachLib edit.",
                "This resumes EML research while public copy, implementation, and laptop/course scope remain blocked.",
            ],
            [
                "must define exactly one next bounded identity candidate",
                "must avoid duplicating checked MachLib witnesses",
                "must preserve protected expm1 as runtime control unless separately justified",
                "must keep proof-attempt and implementation claims false unless separately selected",
            ],
        ),
        selector_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later",
            57,
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
            38,
            "Future human-approved expm1-boundary public copy gate",
            [
                "D62 froze private copy boundaries but no human approval is recorded.",
                "Public copy should remain behind an explicit human gate after private selector work stabilizes.",
            ],
            [
                "requires explicit human approval",
                "must reuse D62 frozen caveats and blocked phrases",
                "must not imply protected expm1 replacement, runtime advantage, or public readiness",
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
        "frozenCaveatCount": len(frozen_row["frozenCaveats"]),
        "frozenBlockedPhraseCount": len(frozen_row["frozenBlockedPhrases"]),
        "nonDuplicateWitnessName": frozen_row["nonDuplicateWitnessName"],
        "duplicatesExistingExpBranchWitness": frozen_row["duplicatesExistingExpBranchWitness"],
        "runtimeLoweringControl": freeze["summary"]["runtimeLoweringControl"],
        "runtimeGuardrailStatus": freeze["summary"]["runtimeGuardrailStatus"],
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
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
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
        "selectorType": "eml_post_expm1_boundary_pause_next_selector_v0",
        "artifactId": "eml-d63-post-expm1-boundary-pause-next-selector",
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
    if payload["sourceFreezePacket"] != "eml-d62-expm1-boundary-branch-pause-freeze-packet":
        raise ValueError("D63 must consume D62")
    for key in [
        "branchPauseStarted",
        "checkedWitnessCopyFrozen",
        "privateFreezePacket",
        "nextActionSelected",
        "nextBoundedIdentityBranchSelected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["frozenWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected frozen witness")
    if summary["frozenCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected frozen checked statement")
    if summary["frozenGuardCount"] != 0:
        raise ValueError("guard count drift")
    if summary["frozenCaveatCount"] != 8 or summary["frozenBlockedPhraseCount"] != 10:
        raise ValueError("frozen caveat/blocker counts drifted")
    if summary["nonDuplicateWitnessName"] != "MachLib.Real.atlas_exp_from_eml_witness":
        raise ValueError("unexpected non-duplicate witness")
    if summary["duplicatesExistingExpBranchWitness"] is not False:
        raise ValueError("non-duplicate boundary drift")
    if summary["runtimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["runtimeGuardrailStatus"] != "protected_expm1_runtime_control_required":
        raise ValueError("runtime guardrail drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    if summary["optionCount"] != 3:
        raise ValueError("expected three options")
    if summary["selectedOptionId"] != "next_bounded_identity_branch_selector":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D64 bounded identity branch candidate selector":
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
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
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
        "artifactType": "eml_post_expm1_boundary_pause_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_next_bounded_identity_branch_no_public_copy_no_implementation",
        "source": f"python/results/eml_d63_post_expm1_boundary_pause_next_selector/eml_d63_post_expm1_boundary_pause_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d63_post_expm1_boundary_pause_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D64 as a bounded identity branch candidate selector.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D63 Post Expm1-Boundary Pause Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D63 selects the next private action after the D62 expm1-boundary pause/freeze without starting it.",
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
    result_path = out_dir / f"eml_d63_post_expm1_boundary_pause_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d63_post_expm1_boundary_pause_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d63_post_expm1_boundary_pause_next_selector.json"
    feed_path = command_feed_dir / f"eml_d63_post_expm1_boundary_pause_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d63_post_expm1_boundary_pause_next_selector")
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
    print("EML_D63_POST_EXPM1_BOUNDARY_PAUSE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
