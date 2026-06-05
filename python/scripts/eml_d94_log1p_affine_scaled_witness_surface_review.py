#!/usr/bin/env python3
"""EML-D94 log1p affine-scaled checked-witness private surface review."""

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

from scripts import eml_d93_log1p_affine_scaled_boundary_coordinate_witness_attempt as d93  # noqa: E402

DATE = "2026-06-04"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_log1p_affine_scaled_witness_surface_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D94_LOG1P_AFFINE_SCALED_WITNESS_SURFACE_REVIEW_PASS"

CLAIM_FLAGS = {
    "surface_updated": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_log_replacement_claim": False,
    "protected_log1p_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "bounded_trig_feasibility_selected": False,
    "private_reviewer_response_intake_selected": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
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
    "EML-D94 is a private surface review over the checked D93 log1p affine-scaled witness; it does not update public pages or promote Atlas copy.",
    "The checked identity is one scoped guarded proof/teaching-shape witness; protected log and log1p remain runtime controls.",
    "D94 preserves the duplicate shifted-coordinate blocks and does not reopen the checked log1p-shifted or log1m-shifted lanes as fresh work.",
    "D94 does not edit MachLib, typecheck Lean, approve public copy, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p replacement, formal equivalence, or broad EML superiority.",
]


def surface_row(
    surface_id: str,
    surface_kind: str,
    status: str,
    evidence_strength: str,
    action: str,
    rationale: list[str],
    blocked_claims: list[str],
) -> dict[str, Any]:
    return {
        "surfaceId": surface_id,
        "surfaceKind": surface_kind,
        "surfaceStatus": status,
        "evidenceStrength": evidence_strength,
        "recommendedAction": action,
        "rationale": rationale,
        "blockedClaims": blocked_claims,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    witness = d93.build_payload(atlas_gate_path)
    d93.validate_payload(witness)
    surface_rows = [
        surface_row(
            "machlib_witness_index_log1p_affine_scaled_boundary",
            "machlib_private_index",
            "checked_witness_recorded_private",
            "scoped_guarded_log1p_affine_scaled_coordinate_checked",
            "record_as_private_checked_witness",
            [
                "D93 checks MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness.",
                "The checked statement is guarded by 0 < 1 + a * x.",
                "The witness is scoped to one affine-scaled logarithm coordinate and does not create a broad log1p theory.",
            ],
            ["public readiness", "theorem discovery", "broad log1p theory"],
        ),
        surface_row(
            "log1p_affine_scaled_guard_boundary",
            "candidate_boundary",
            "affine_scaled_positive_domain_boundary_required",
            "d92_negative_controls_and_blockers_preserved",
            "keep_affine_scaled_positive_guard_and_boundary_controls",
            [
                "D92 records one guard, two derived domain obligations, five negative controls, and five blockers.",
                "D93 preserves the guard shape 0 < 1 + a * x.",
                "Boundary cases with 1 + a * x <= 0, missing affine guard, duplicate shifted-coordinate reuse, and broad log1p-family statements remain blocked.",
            ],
            [
                "unguarded log1p affine-scaled coordinate",
                "1 + a * x <= 0 boundary",
                "duplicate shifted-coordinate reuse",
                "broad log1p-family claim",
            ],
        ),
        surface_row(
            "log1p_affine_scaled_runtime_control_guardrail",
            "runtime_control_guardrail",
            "protected_log_and_log1p_runtime_controls_required",
            "protected_log_and_log1p_runtime_controls_preserved",
            "keep_protected_log_and_log1p_as_runtime_controls",
            [
                "D92 and D93 keep protected_log_and_log1p_remain_runtime_controls.",
                "The identity may support proof/teaching shape but does not replace log or log1p runtime behavior.",
                "Future copy must block runtime advantage and logarithmic replacement language.",
            ],
            ["log replacement", "log1p replacement", "runtime advantage"],
        ),
        surface_row(
            "advantage_lab_log1p_affine_scaled_boundary",
            "advantage_lab",
            "runtime_control_remains_protected_log_and_log1p",
            "scoped_log1p_affine_scaled_coordinate_witness_available",
            "do_not_add_runtime_advantage_row_without_new_runtime_evidence",
            [
                "The witness strengthens private proof/teaching shape only.",
                "Protected log and log1p remain runtime controls.",
                "No Advantage Lab case should be added without separate runtime evidence.",
            ],
            ["runtime advantage", "log/log1p replacement", "broad EML advantage"],
        ),
        surface_row(
            "public_atlas_log1p_affine_scaled_boundary",
            "public_surface",
            "held_private",
            "checked_machlib_witness_available_private",
            "require_human_copy_review_before_public_change",
            [
                "D93 proof status is real but public wording has not been reviewed.",
                "No monogate.org or monogate.dev public route is changed by D94.",
                "Safe public wording must preserve guard, runtime-control, duplicate shifted-coordinate, and non-broadness caveats.",
            ],
            ["public readiness", "public theorem claim", "public Atlas promotion"],
        ),
    ]
    summary = {
        "sourceWitnessAttempt": witness["artifactId"],
        "selectedWitnessName": witness["summary"]["machlibName"],
        "sourceSelectedCandidateId": witness["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": witness["summary"]["sourceSelectedFamily"],
        "checkedStatement": witness["summary"]["checkedStatement"],
        "machlibFile": witness["summary"]["machlibFile"],
        "guardCount": witness["summary"]["guardCount"],
        "sourceDerivedDomainObligationCount": witness["summary"]["derivedDomainObligationCount"],
        "sourceNegativeControlCount": witness["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": witness["summary"]["sourceBlockerCount"],
        "sourceDuplicateShiftedBlocksPreserved": witness["summary"]["sourceDuplicateShiftedBlocksPreserved"],
        "duplicateShiftedBlocksPreserved": witness["summary"]["duplicateShiftedBlocksPreserved"],
        "checkedWitnessRecordedPrivately": witness["summary"]["candidateProved"],
        "candidateProved": witness["summary"]["candidateProved"],
        "buildPassed": witness["summary"]["buildPassed"],
        "surfaceRowCount": len(surface_rows),
        "runtimeLoweringControl": witness["summary"]["runtimeLoweringControl"],
        "publicPromotionPerformed": False,
        "publicEducationCandidate": False,
        "publicCopyApproved": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "surfaceUpdated": False,
        "boundedTrigFeasibilitySelected": False,
        "privateReviewerResponseIntakeSelected": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D95 choose log1p affine-scaled checked-witness copy review, next bounded branch, private reviewer response intake, or human-approved public copy gate without public promotion.",
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in row["claimFlags"].values()) for row in surface_rows),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_log1p_affine_scaled_witness_surface_review_v0",
        "artifactId": "eml-d94-log1p-affine-scaled-witness-surface-review",
        "status": STATUS,
        "decision": "surface_checked_log1p_affine_scaled_witness_as_private_review_evidence_only",
        "date": DATE,
        "sourceWitnessAttempt": witness["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "surfaceRows": surface_rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceWitnessAttempt"] != "eml-d93-log1p-affine-scaled-boundary-coordinate-witness-attempt":
        raise ValueError("D94 must consume D93")
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
    if summary["surfaceRowCount"] != 5:
        raise ValueError("expected five surface rows")
    for key in ["checkedWitnessRecordedPrivately", "candidateProved", "buildPassed", "duplicateShiftedBlocksPreserved"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["sourceDuplicateShiftedBlocksPreserved"] is not True:
        raise ValueError("source duplicate block drift")
    if summary["guardCount"] != 1:
        raise ValueError("log1p affine-scaled witness should preserve one guard")
    if summary["sourceDerivedDomainObligationCount"] != 2:
        raise ValueError("D92 derived domain obligation count drift")
    if summary["sourceNegativeControlCount"] != 5 or summary["sourceBlockerCount"] != 5:
        raise ValueError("D92 negative control/blocker counts drift")
    for key in [
        "publicPromotionPerformed",
        "publicEducationCandidate",
        "publicCopyApproved",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedLogReplacementClaim",
        "protectedLog1pReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "surfaceUpdated",
        "boundedTrigFeasibilitySelected",
        "privateReviewerResponseIntakeSelected",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["nextAction"] != "EML-D95 choose log1p affine-scaled checked-witness copy review, next bounded branch, private reviewer response intake, or human-approved public copy gate without public promotion.":
        raise ValueError("unexpected next action")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_log1p_affine_scaled_witness_surface_review",
        "validationStatus": "pass",
        "semanticStrength": "checked_log1p_affine_scaled_witness_private_surface_review_no_public_update",
        "source": f"python/results/eml_d94_log1p_affine_scaled_witness_surface_review/eml_d94_log1p_affine_scaled_witness_surface_review_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d94_log1p_affine_scaled_witness_surface_review_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D94 Log1p Affine-Scaled Witness Surface Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D94 surfaces the checked log1p affine-scaled witness privately without public copy approval.",
        "",
        "| Surface | Status | Action |",
        "|---|---|---|",
    ]
    for row in payload["surfaceRows"]:
        lines.append(f"| `{row['surfaceId']}` | `{row['surfaceStatus']}` | {row['recommendedAction']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected witness: `{payload['summary']['selectedWitnessName']}`",
            f"- checked statement: `{payload['summary']['checkedStatement']}`",
            f"- guard count: `{payload['summary']['guardCount']}`",
            f"- duplicate shifted blocks preserved: `{payload['summary']['duplicateShiftedBlocksPreserved']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- surface updated: `{payload['summary']['surfaceUpdated']}`",
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
    result_path = out_dir / f"eml_d94_log1p_affine_scaled_witness_surface_review_{STAMP}.json"
    report_path = report_dir / f"eml_d94_log1p_affine_scaled_witness_surface_review_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d94_log1p_affine_scaled_witness_surface_review.json"
    feed_path = command_feed_dir / f"eml_d94_log1p_affine_scaled_witness_surface_review_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d94_log1p_affine_scaled_witness_surface_review")
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
    print("EML_D94_LOG1P_AFFINE_SCALED_WITNESS_SURFACE_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
