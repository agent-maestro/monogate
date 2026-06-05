#!/usr/bin/env python3
"""EML-D95 log1p affine-scaled private surface next-action selector."""

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

from scripts import eml_d94_log1p_affine_scaled_witness_surface_review as d94  # noqa: E402

DATE = "2026-06-04"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_log1p_affine_scaled_surface_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D95_LOG1P_AFFINE_SCALED_SURFACE_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "checked_witness_copy_review_selected": True,
    "next_bounded_branch_selected": False,
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
    "EML-D95 is a selector-only private next-action packet after D94; it does not start copy review, proof work, implementation, public copy, or a public gate.",
    "D95 selects a checked-witness copy review packet so the D93/D94 log1p affine-scaled witness can get claim-bounded wording before any public or Advantage consideration.",
    "D95 preserves the duplicate shifted-coordinate blocks and does not reopen the checked log1p-shifted or log1m-shifted lanes as fresh work.",
    "D95 does not edit MachLib, typecheck Lean, consume laptop artifacts, touch laptop-owned repos, approve public copy, replace log/log1p runtime controls, claim runtime advantage, or claim broad EML superiority.",
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


def surface_row_by_id(payload: dict[str, Any], surface_id: str) -> dict[str, Any]:
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    surface = d94.build_payload(atlas_gate_path)
    d94.validate_payload(surface)
    runtime_row = surface_row_by_id(surface, "log1p_affine_scaled_runtime_control_guardrail")
    guard_row = surface_row_by_id(surface, "log1p_affine_scaled_guard_boundary")
    public_row = surface_row_by_id(surface, "public_atlas_log1p_affine_scaled_boundary")
    options = [
        selector_option(
            "log1p_affine_scaled_checked_witness_copy_review_packet",
            "private_copy_review_lane",
            "selected_next",
            87,
            "EML-D96 log1p affine-scaled checked-witness copy review packet",
            [
                "D93 checked the witness and D94 surfaced five private rows, but public-safe wording is still unreviewed.",
                "A copy-review packet can freeze allowed phrases, affine guard caveats, runtime caveats, duplicate shifted-coordinate caveats, and blocked claims before any public gate is considered.",
                "This keeps the checked witness useful for reviewers while preserving protected log and log1p as runtime controls.",
            ],
            [
                "must preserve the affine positive-domain guard 0 < 1 + a * x",
                "must preserve protected log/log1p runtime-control language",
                "must preserve duplicate shifted-coordinate blocks",
                "must block log, log1p, runtime replacement, runtime advantage, and broad log1p-family claims",
                "must not treat checked witness copy review as public approval",
            ],
        ),
        selector_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "candidate_later_after_copy_review",
            66,
            "Future bounded identity branch selector",
            [
                "A next bounded branch remains valuable after the log1p affine-scaled witness wording is stabilized.",
                "Starting another branch first would leave the checked log1p affine-scaled witness with only surface rows and no copy boundary.",
            ],
            [
                "requires exactly one non-duplicate candidate",
                "must not start MachLib proof work in the selector",
                "must preserve D94 public, runtime, and duplicate shifted-coordinate holds",
            ],
        ),
        selector_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "candidate_later",
            53,
            "Future bounded trig identity feasibility selector",
            [
                "The bounded trig probe remains a useful frontier lane.",
                "It carries higher guard and negative-control risk than stabilizing the already checked log1p affine-scaled witness copy.",
            ],
            [
                "requires exact bounded interval guards",
                "requires negative controls before proof work",
                "must not imply broad EML advantage",
            ],
        ),
        selector_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_human_approval",
            41,
            "Future human-approved log1p affine-scaled public copy gate",
            [
                "D94 records public Atlas as held private.",
                "Human approval should come after private copy review, not before the guard, runtime, and duplicate shifted-coordinate caveats are frozen.",
            ],
            [
                "requires explicit human approval",
                "requires copy-reviewed caveats and blocked phrases",
                "must not imply public readiness, runtime advantage, or log/log1p replacement",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceSurfaceReview": surface["artifactId"],
        "selectedWitnessName": surface["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": surface["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": surface["summary"]["sourceSelectedFamily"],
        "checkedStatement": surface["summary"]["checkedStatement"],
        "machlibFile": surface["summary"]["machlibFile"],
        "guardCount": surface["summary"]["guardCount"],
        "sourceDerivedDomainObligationCount": surface["summary"]["sourceDerivedDomainObligationCount"],
        "sourceNegativeControlCount": surface["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": surface["summary"]["sourceBlockerCount"],
        "sourceDuplicateShiftedBlocksPreserved": surface["summary"]["sourceDuplicateShiftedBlocksPreserved"],
        "duplicateShiftedBlocksPreserved": surface["summary"]["duplicateShiftedBlocksPreserved"],
        "d94SurfaceRowCount": surface["summary"]["surfaceRowCount"],
        "d94CheckedWitnessRecordedPrivately": surface["summary"]["checkedWitnessRecordedPrivately"],
        "d94CandidateProved": surface["summary"]["candidateProved"],
        "d94BuildPassed": surface["summary"]["buildPassed"],
        "guardBoundaryStatus": guard_row["surfaceStatus"],
        "runtimeGuardrailStatus": runtime_row["surfaceStatus"],
        "publicAtlasStatus": public_row["surfaceStatus"],
        "runtimeLoweringControl": surface["summary"]["runtimeLoweringControl"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "nextActionSelected": True,
        "checkedWitnessCopyReviewSelected": True,
        "nextBoundedBranchSelected": False,
        "boundedTrigFeasibilitySelected": False,
        "privateReviewerResponseIntakeSelected": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "copyReviewStarted": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsSelectorOnly": all(
            CLAIM_FLAGS[key] is True
            for key in ["next_action_selected", "checked_witness_copy_review_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"next_action_selected", "checked_witness_copy_review_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_log1p_affine_scaled_surface_next_selector_v0",
        "artifactId": "eml-d95-log1p-affine-scaled-surface-next-selector",
        "status": STATUS,
        "decision": "select_log1p_affine_scaled_checked_witness_copy_review_packet",
        "date": DATE,
        "sourceSurfaceReview": surface["artifactId"],
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
    if payload["sourceSurfaceReview"] != "eml-d94-log1p-affine-scaled-witness-surface-review":
        raise ValueError("D95 must consume D94")
    if summary["selectedWitnessName"] != "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "log1p_affine_scaled_boundary_coordinate":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "guarded_log1p_affine_scaled_coordinate":
        raise ValueError("unexpected family")
    if summary["checkedStatement"] != "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x":
        raise ValueError("unexpected checked statement")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    if summary["guardCount"] != 1:
        raise ValueError("expected one guard")
    if summary["sourceDerivedDomainObligationCount"] != 2:
        raise ValueError("derived domain obligation count drift")
    if summary["sourceNegativeControlCount"] != 5 or summary["sourceBlockerCount"] != 5:
        raise ValueError("negative control/blocker counts drift")
    if summary["sourceDuplicateShiftedBlocksPreserved"] is not True or summary["duplicateShiftedBlocksPreserved"] is not True:
        raise ValueError("duplicate shifted-coordinate block drift")
    if summary["d94SurfaceRowCount"] != 5:
        raise ValueError("expected five D94 rows")
    for key in ["d94CheckedWitnessRecordedPrivately", "d94CandidateProved", "d94BuildPassed"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardBoundaryStatus"] != "affine_scaled_positive_domain_boundary_required":
        raise ValueError("guard boundary drift")
    if summary["runtimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("runtime guardrail drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["selectedOptionId"] != "log1p_affine_scaled_checked_witness_copy_review_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D96 log1p affine-scaled checked-witness copy review packet":
        raise ValueError("unexpected next artifact")
    if summary["optionCount"] != 4:
        raise ValueError("expected four options")
    for key in ["nextActionSelected", "checkedWitnessCopyReviewSelected"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "nextBoundedBranchSelected",
        "boundedTrigFeasibilitySelected",
        "privateReviewerResponseIntakeSelected",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "copyReviewStarted",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedLogReplacementClaim",
        "protectedLog1pReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsSelectorOnly"] is not True:
        raise ValueError("claim flags must remain selector-only")
    for key in ["next_action_selected", "checked_witness_copy_review_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "checked_witness_copy_review_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_log1p_affine_scaled_surface_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_checked_witness_copy_review_next_no_public_update",
        "source": f"python/results/eml_d95_log1p_affine_scaled_surface_next_selector/eml_d95_log1p_affine_scaled_surface_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d95_log1p_affine_scaled_surface_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D96 as a private log1p affine-scaled checked-witness copy review packet; do not promote public copy.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D95 Log1p Affine-Scaled Surface Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D95 selects the next private log1p affine-scaled checked-witness action without starting public copy.",
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
            f"- selected witness: `{payload['summary']['selectedWitnessName']}`",
            f"- duplicate shifted blocks preserved: `{payload['summary']['duplicateShiftedBlocksPreserved']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- copy review started: `{payload['summary']['copyReviewStarted']}`",
            f"- public ready: `{payload['summary']['publicReady']}`",
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
    result_path = out_dir / f"eml_d95_log1p_affine_scaled_surface_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d95_log1p_affine_scaled_surface_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d95_log1p_affine_scaled_surface_next_selector.json"
    feed_path = command_feed_dir / f"eml_d95_log1p_affine_scaled_surface_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d95_log1p_affine_scaled_surface_next_selector")
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
    print("EML_D95_LOG1P_AFFINE_SCALED_SURFACE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
