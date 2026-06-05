#!/usr/bin/env python3
"""EML-D100 bounded artifact target-set consolidation review."""

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

from scripts import eml_d99_post_log1p_affine_scaled_pause_next_selector as d99  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_bounded_artifact_target_set_consolidation_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D100_BOUNDED_ARTIFACT_TARGET_SET_CONSOLIDATION_REVIEW_PASS"

TARGET_MIN = 15
TARGET_MAX = 25

CLAIM_FLAGS = {
    "consolidation_review_created": True,
    "private_review_only": True,
    "checked_witness_core_counted": True,
    "affine_log1p_branch_frozen_observed": True,
    "next_private_consolidation_step_recommended": True,
    "new_identity_candidate_selected": False,
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
    "catalog_completeness_claim": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D100 is a private consolidation review; it does not create public copy, public Atlas rows, SDK/compiler docs, or course material.",
    "D100 counts a current checked-witness consolidation core and recommends a later private public-witness candidate selector; it does not claim the catalog is complete.",
    "D100 does not define a new identity candidate, edit MachLib, typecheck Lean, start proof work, change runtime lowering, approve reviewer decisions, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, compiler correctness, formal equivalence, public readiness, broad log1p-family coverage, or broad EML superiority.",
]


def witness_row(
    witness_id: str,
    machlib_name: str,
    family: str,
    statement_summary: str,
    guard_summary: str,
    runtime_control: str,
    consolidation_status: str,
) -> dict[str, Any]:
    return {
        "witnessId": witness_id,
        "machlibName": machlib_name,
        "family": family,
        "statementSummary": statement_summary,
        "guardSummary": guard_summary,
        "runtimeControl": runtime_control,
        "consolidationStatus": consolidation_status,
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def next_step_option(
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


def build_witness_rows() -> list[dict[str, Any]]:
    return [
        witness_row(
            "constants_zero_one_e_boundary",
            "MachLib.Real.constants_zero_one_e_boundary_witness",
            "constants_boundary",
            "checked constants zero/one/e EML boundary witness",
            "constant-domain boundary",
            "standard constants remain runtime controls",
            "core_checked_candidate",
        ),
        witness_row(
            "ln_from_eml_boundary",
            "MachLib.Real.ln_from_eml_boundary_witness",
            "log_boundary",
            "checked ln-from-EML boundary witness",
            "positive logarithm domain guard",
            "standard_log_exp_remains_runtime_control",
            "core_checked_candidate",
        ),
        witness_row(
            "subtraction_boundary_affine_offset",
            "MachLib.Real.subtraction_boundary_affine_offset_witness",
            "subtraction_boundary",
            "checked affine-offset subtraction boundary witness",
            "0 < x + y",
            "standard_subtraction_remains_runtime_control",
            "core_checked_candidate",
        ),
        witness_row(
            "subtraction_boundary_two_stage_chain",
            "MachLib.Real.subtraction_boundary_two_stage_chain_witness",
            "nested_subtraction_boundary",
            "checked two-stage nested subtraction boundary witness",
            "positive log-input guards",
            "standard_subtraction_remains_runtime_control",
            "core_checked_candidate",
        ),
        witness_row(
            "subtraction_boundary_affine_nested_chain",
            "MachLib.Real.subtraction_boundary_affine_nested_chain_witness",
            "nested_subtraction_boundary",
            "checked affine-nested subtraction boundary witness",
            "0 < x + y and 0 < z",
            "standard_subtraction_remains_runtime_control",
            "core_checked_candidate",
        ),
        witness_row(
            "subtraction_boundary_three_stage_chain",
            "MachLib.Real.subtraction_boundary_three_stage_chain_witness",
            "nested_subtraction_boundary",
            "checked three-stage nested subtraction boundary witness",
            "positive log-input guards",
            "standard_subtraction_remains_runtime_control",
            "core_checked_candidate",
        ),
        witness_row(
            "positive_log_exp_roundtrip",
            "MachLib.Real.positive_log_exp_roundtrip_witness",
            "positive_log_exp",
            "checked positive log-exp roundtrip witness",
            "0 < x",
            "standard_log_exp_remains_runtime_control",
            "core_checked_candidate",
        ),
        witness_row(
            "expm1_boundary_identity",
            "MachLib.Real.expm1_boundary_identity_witness",
            "expm1_boundary",
            "checked expm1 boundary identity witness",
            "no extra real-domain guard recorded",
            "protected_expm1_remains_runtime_control",
            "core_checked_candidate",
        ),
        witness_row(
            "constant_coordinate_zero_exp_two",
            "MachLib.Real.constant_coordinate_zero_exp_two_witness",
            "constant_coordinate",
            "checked constant-coordinate zero-exp-two witness",
            "local exp (1 + 1) spelling boundary",
            "standard constants remain runtime controls",
            "core_checked_candidate",
        ),
        witness_row(
            "probability_logit_boundary_coordinate",
            "MachLib.Real.probability_logit_boundary_coordinate_witness",
            "probability_logit_boundary",
            "checked probability-logit boundary coordinate witness",
            "0 < p and p < 1",
            "protected_log_and_log1p_remain_runtime_controls",
            "core_checked_candidate",
        ),
        witness_row(
            "log1p_shifted_boundary_coordinate",
            "MachLib.Real.log1p_shifted_boundary_coordinate_witness",
            "log1p_shifted_boundary",
            "checked log1p shifted boundary coordinate witness",
            "0 < 1 + x",
            "protected_log_and_log1p_remain_runtime_controls",
            "core_checked_candidate",
        ),
        witness_row(
            "log1m_shifted_boundary_coordinate",
            "MachLib.Real.log1m_shifted_boundary_coordinate_witness",
            "log1m_shifted_boundary",
            "checked log1m shifted boundary coordinate witness",
            "0 < 1 - x",
            "protected_log_and_log1p_remain_runtime_controls",
            "core_checked_candidate",
        ),
        witness_row(
            "log1p_affine_scaled_boundary_coordinate",
            "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness",
            "log1p_affine_scaled_boundary",
            "checked log1p affine-scaled boundary coordinate witness",
            "0 < 1 + a * x",
            "protected_log_and_log1p_remain_runtime_controls",
            "core_checked_candidate_frozen_after_d98",
        ),
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d99.build_payload(atlas_gate_path)
    d99.validate_payload(selector)
    rows = build_witness_rows()
    next_steps = [
        next_step_option(
            "private_public_witness_candidate_selector",
            "private_public_witness_lane",
            "recommended_next",
            92,
            "EML-D101 private public-witness candidate selector",
            [
                "The checked core is now large enough to choose one humble public-witness candidate privately.",
                "A selector can choose one witness for bounded public-page drafting without approving public copy.",
                "This turns consolidation into reviewable product value before another proof branch.",
            ],
            [
                "must select exactly one candidate",
                "must not publish or approve public copy",
                "must preserve guards, runtime controls, and non-claims",
            ],
        ),
        next_step_option(
            "private_claim_topology_surface_mvp",
            "private_claim_topology_lane",
            "candidate_later",
            80,
            "Future private Claim Topology / Evidence Surface MVP",
            [
                "A topology view can reduce reviewer load across evidence packets.",
                "It should remain private until renderer and claim-boundary non-claims are explicit.",
            ],
            [
                "must not claim visualization correctness",
                "must not claim public readiness",
                "must preserve accepted versus blocked fixture distinctions",
            ],
        ),
        next_step_option(
            "sdk_compiler_guard_note_excerpt",
            "private_sdk_compiler_docs_lane",
            "candidate_later",
            72,
            "Future SDK/compiler guard-note excerpt packet",
            [
                "The checked core can ground guard documentation for SDK/compiler planning.",
                "A docs packet should wait until one public-witness candidate is privately selected.",
            ],
            [
                "must not claim compiler correctness",
                "must not claim runtime performance",
                "must not imply automatic lowering",
            ],
        ),
        next_step_option(
            "next_materially_distinct_bounded_branch_selector",
            "private_bounded_identity_lane",
            "candidate_later_if_gap_remains",
            55,
            "Future materially distinct bounded branch selector",
            [
                "Another branch is only useful if consolidation finds a real gap.",
                "The log/log1p/log1m and subtraction shapes are already represented strongly.",
            ],
            [
                "requires a materially distinct candidate",
                "must not duplicate the current checked core",
                "must not start proof work in the selector",
            ],
        ),
    ]
    selected = next(option for option in next_steps if option["selectionStatus"] == "recommended_next")
    checked_count = len(rows)
    summary = {
        "sourceSelector": selector["artifactId"],
        "sourceSelectedOptionId": selector["summary"]["selectedOptionId"],
        "sourceSelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "d99ConsolidationReviewSelected": selector["summary"]["consolidationReviewSelected"],
        "d98BranchPauseStarted": selector["summary"]["branchPauseStarted"],
        "d98CheckedWitnessCopyFrozen": selector["summary"]["checkedWitnessCopyFrozen"],
        "d98DuplicateShiftedBlocksPreserved": selector["summary"]["duplicateShiftedBlocksPreserved"],
        "d98FrozenWitnessName": selector["summary"]["frozenWitnessName"],
        "d98FrozenCheckedStatement": selector["summary"]["frozenCheckedStatement"],
        "d98FrozenGuardCount": selector["summary"]["frozenGuardCount"],
        "d98FrozenCaveatCount": selector["summary"]["frozenCaveatCount"],
        "d98FrozenBlockedPhraseCount": selector["summary"]["frozenBlockedPhraseCount"],
        "targetMin": TARGET_MIN,
        "targetMax": TARGET_MAX,
        "checkedWitnessCoreCount": checked_count,
        "targetLowerBoundReached": checked_count >= TARGET_MIN,
        "targetUpperBoundExceeded": checked_count > TARGET_MAX,
        "additionalArtifactsNeededForLowerBound": max(TARGET_MIN - checked_count, 0),
        "remainingSlotsBeforeUpperBound": max(TARGET_MAX - checked_count, 0),
        "selectorOnlyPacketsCountedAsFinalArtifacts": False,
        "affineLog1pBranchFrozenObserved": True,
        "consolidationReviewCreated": True,
        "privateReviewOnly": True,
        "checkedWitnessCoreCounted": True,
        "recommendedNextOptionId": selected["optionId"],
        "recommendedNextArtifact": selected["nextArtifact"],
        "nextPrivateConsolidationStepRecommended": True,
        "nextStepOptionCount": len(next_steps),
        "newIdentityCandidateSelected": False,
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
        "catalogCompletenessClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsReviewOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "consolidation_review_created",
                "private_review_only",
                "checked_witness_core_counted",
                "affine_log1p_branch_frozen_observed",
                "next_private_consolidation_step_recommended",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "consolidation_review_created",
                "private_review_only",
                "checked_witness_core_counted",
                "affine_log1p_branch_frozen_observed",
                "next_private_consolidation_step_recommended",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_bounded_artifact_target_set_consolidation_review_v0",
        "artifactId": "eml-d100-bounded-artifact-target-set-consolidation-review",
        "status": STATUS,
        "decision": "create_private_bounded_artifact_target_set_review_and_recommend_public_witness_candidate_selector",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "targetRange": {"min": TARGET_MIN, "max": TARGET_MAX},
        "checkedWitnessRows": rows,
        "nextStepOptions": next_steps,
        "recommendedNextStep": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d99-post-log1p-affine-scaled-pause-next-selector":
        raise ValueError("D100 must consume D99")
    for key in [
        "d99ConsolidationReviewSelected",
        "d98BranchPauseStarted",
        "d98CheckedWitnessCopyFrozen",
        "d98DuplicateShiftedBlocksPreserved",
        "affineLog1pBranchFrozenObserved",
        "consolidationReviewCreated",
        "privateReviewOnly",
        "checkedWitnessCoreCounted",
        "nextPrivateConsolidationStepRecommended",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["sourceSelectedOptionId"] != "bounded_artifact_target_set_consolidation_review":
        raise ValueError("unexpected D99 selected option")
    if summary["sourceSelectedNextArtifact"] != "EML-D100 bounded artifact target-set consolidation review":
        raise ValueError("unexpected D99 next artifact")
    if summary["d98FrozenWitnessName"] != "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness":
        raise ValueError("unexpected D98 frozen witness")
    if summary["d98FrozenCheckedStatement"] != "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x":
        raise ValueError("unexpected D98 frozen statement")
    if summary["d98FrozenGuardCount"] != 1:
        raise ValueError("D98 frozen guard count drift")
    if summary["d98FrozenCaveatCount"] != 10 or summary["d98FrozenBlockedPhraseCount"] != 16:
        raise ValueError("D98 frozen copy counts drift")
    if summary["targetMin"] != TARGET_MIN or summary["targetMax"] != TARGET_MAX:
        raise ValueError("target range drift")
    if summary["checkedWitnessCoreCount"] != 13:
        raise ValueError("checked witness core count drift")
    if len(payload["checkedWitnessRows"]) != summary["checkedWitnessCoreCount"]:
        raise ValueError("witness row count mismatch")
    if summary["targetLowerBoundReached"] is not False:
        raise ValueError("13 checked witnesses should not reach lower bound 15")
    if summary["targetUpperBoundExceeded"] is not False:
        raise ValueError("target upper bound should not be exceeded")
    if summary["additionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("expected two additional high-quality artifacts to reach lower bound")
    if summary["remainingSlotsBeforeUpperBound"] != 12:
        raise ValueError("remaining target slots drift")
    if summary["selectorOnlyPacketsCountedAsFinalArtifacts"] is not False:
        raise ValueError("selector-only packets must not count as final artifacts")
    if summary["recommendedNextOptionId"] != "private_public_witness_candidate_selector":
        raise ValueError("unexpected recommended next option")
    if summary["recommendedNextArtifact"] != "EML-D101 private public-witness candidate selector":
        raise ValueError("unexpected recommended next artifact")
    if summary["nextStepOptionCount"] != 4:
        raise ValueError("expected four next-step options")
    for key in [
        "newIdentityCandidateSelected",
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
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsReviewOnly"] is not True:
        raise ValueError("claim flags must remain review-only")
    allowed_true = {
        "consolidation_review_created",
        "private_review_only",
        "checked_witness_core_counted",
        "affine_log1p_branch_frozen_observed",
        "next_private_consolidation_step_recommended",
    }
    for key in allowed_true:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(row["publicPromotionAllowed"] for row in payload["checkedWitnessRows"]):
        raise ValueError("consolidation rows must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_bounded_artifact_target_set_consolidation_review",
        "validationStatus": "pass",
        "semanticStrength": "private_target_set_review_counts_checked_witness_core_recommends_public_witness_selector_no_public_copy_no_new_proof",
        "source": f"python/results/eml_d100_bounded_artifact_target_set_consolidation_review/eml_d100_bounded_artifact_target_set_consolidation_review_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d100_bounded_artifact_target_set_consolidation_review_feed",
        "date": DATE,
        "status": payload["status"],
        "checkedWitnessCoreCount": payload["summary"]["checkedWitnessCoreCount"],
        "recommendedNextOptionId": payload["summary"]["recommendedNextOptionId"],
        "recommendedNextArtifact": payload["summary"]["recommendedNextArtifact"],
        "nextAction": "Run EML-D101 as a private public-witness candidate selector.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D100 Bounded Artifact Target-Set Consolidation Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D100 privately reviews the bounded checked-witness target set after the affine log1p branch freeze.",
        "",
        "## Summary",
        "",
        f"- checked witness core count: `{payload['summary']['checkedWitnessCoreCount']}`",
        f"- target range: `{payload['summary']['targetMin']}`-`{payload['summary']['targetMax']}`",
        f"- additional artifacts needed for lower bound: `{payload['summary']['additionalArtifactsNeededForLowerBound']}`",
        f"- selector-only packets counted as final artifacts: `{payload['summary']['selectorOnlyPacketsCountedAsFinalArtifacts']}`",
        f"- recommended next artifact: `{payload['summary']['recommendedNextArtifact']}`",
        f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
        "",
        "| Witness | Family | Runtime control | Status |",
        "|---|---|---|---|",
    ]
    for row in payload["checkedWitnessRows"]:
        lines.append(
            f"| `{row['machlibName']}` | `{row['family']}` | {row['runtimeControl']} | `{row['consolidationStatus']}` |"
        )
    lines.extend(["", "## Next Step Options", "", "| Option | Status | Score | Next artifact |", "|---|---|---:|---|"])
    for option in payload["nextStepOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | {option['priorityScore']} | {option['nextArtifact']} |"
        )
    lines.extend(["", "## Non-Claims", ""])
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
    result_path = out_dir / f"eml_d100_bounded_artifact_target_set_consolidation_review_{STAMP}.json"
    report_path = report_dir / f"eml_d100_bounded_artifact_target_set_consolidation_review_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d100_bounded_artifact_target_set_consolidation_review.json"
    feed_path = command_feed_dir / f"eml_d100_bounded_artifact_target_set_consolidation_review_feed_{STAMP}.json"
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
        default=ROOT / "python/results/eml_d100_bounded_artifact_target_set_consolidation_review",
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
    print("EML_D100_BOUNDED_ARTIFACT_TARGET_SET_CONSOLIDATION_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
