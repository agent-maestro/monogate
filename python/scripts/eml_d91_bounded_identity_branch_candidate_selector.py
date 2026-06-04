#!/usr/bin/env python3
"""EML-D91 bounded identity branch candidate selector."""

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

from scripts import eml_d90_post_log1m_shifted_pause_next_selector as d90  # noqa: E402

DATE = "2026-06-04"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_d91_bounded_identity_branch_candidate_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D91_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"

SELECTED_CANDIDATE_ID = "log1p_affine_scaled_boundary_coordinate"
SELECTED_NEXT_ARTIFACT = "EML-D92 log1p affine-scaled boundary coordinate feasibility packet"
SELECTED_STATEMENT = "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"

CLAIM_FLAGS = {
    "bounded_identity_candidate_selected": True,
    "log1p_affine_scaled_candidate_selected": True,
    "fresh_candidate_non_duplicate_selected": True,
    "source_d90_selector_observed": True,
    "log1p_shifted_duplicate_reselected": False,
    "log1m_shifted_duplicate_reselected": False,
    "feasibility_packet_started": False,
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
    "EML-D91 is a selector-only private candidate packet after D90; it selects one fresh bounded identity candidate for later feasibility review.",
    "D91 does not prove the selected affine-scaled shifted-log statement, edit MachLib, typecheck Lean, start implementation, or change runtime lowering.",
    "D91 explicitly does not reselect the already checked log1p-shifted or log1m-shifted witnesses as fresh work.",
    "D91 does not record reviewer approval or rejection, approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p replacement, or broad EML superiority.",
]


def candidate_row(
    candidate_id: str,
    family: str,
    status: str,
    priority_score: int,
    proposed_statement: str,
    guards: list[str],
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
    duplicate_checked_witnesses: list[str],
    runtime_control: str,
) -> dict[str, Any]:
    return {
        "candidateId": candidate_id,
        "family": family,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "proposedStatement": proposed_statement,
        "guards": guards,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "duplicateCheckedWitnesses": duplicate_checked_witnesses,
        "freshRelativeToCheckedWitnesses": len(duplicate_checked_witnesses) == 0,
        "runtimeControl": runtime_control,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = d90.build_payload(atlas_gate_path)
    d90.validate_payload(source)
    source_summary = source["summary"]
    candidates = [
        candidate_row(
            SELECTED_CANDIDATE_ID,
            "guarded_log1p_affine_scaled_coordinate",
            "selected_next_feasibility_packet",
            92,
            SELECTED_STATEMENT,
            ["0 < 1 + a * x"],
            SELECTED_NEXT_ARTIFACT,
            [
                "It generalizes the checked log1p-shifted shape by moving the fresh work into the affine payload a * x rather than reusing x.",
                "The candidate remains bounded by one explicit shifted positive-domain guard and can be evaluated before any proof or MachLib edit begins.",
                "Protected log and log1p remain runtime controls while the candidate is only selected for feasibility review.",
            ],
            [
                "requires D92 feasibility packet before any proof attempt",
                "must keep the shifted positive-domain guard explicit",
                "must reject public or runtime claims unless separately reviewed",
                "must not collapse into the already checked a = 1 log1p-shifted witness",
            ],
            [],
            "protected_log_and_log1p_remain_runtime_controls",
        ),
        candidate_row(
            "log1p_shifted_boundary_coordinate",
            "guarded_log1p_shifted_coordinate",
            "blocked_duplicate_checked_witness",
            0,
            "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x",
            ["0 < 1 + x"],
            "not_selected_duplicate_checked_witness",
            [
                "This witness was already checked as MachLib.Real.log1p_shifted_boundary_coordinate_witness.",
                "Reselecting it as fresh candidate work would duplicate the prior shifted-log lane.",
            ],
            [
                "already checked as MachLib.Real.log1p_shifted_boundary_coordinate_witness",
                "already paused/frozen by D80 and observed by D81",
            ],
            ["MachLib.Real.log1p_shifted_boundary_coordinate_witness"],
            "protected_log_and_log1p_remain_runtime_controls",
        ),
        candidate_row(
            "log1m_shifted_boundary_coordinate",
            "guarded_log1m_shifted_coordinate",
            "blocked_duplicate_checked_witness",
            0,
            "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x",
            ["0 < 1 - x"],
            "not_selected_duplicate_checked_witness",
            [
                "This witness was already checked as MachLib.Real.log1m_shifted_boundary_coordinate_witness.",
                "Reselecting it as fresh candidate work would duplicate the just-paused log1m lane.",
            ],
            [
                "already checked as MachLib.Real.log1m_shifted_boundary_coordinate_witness",
                "already paused/frozen by D89 and observed by D90",
            ],
            ["MachLib.Real.log1m_shifted_boundary_coordinate_witness"],
            "protected_log_and_log1p_remain_runtime_controls",
        ),
        candidate_row(
            "bounded_trig_identity_feasibility_selector",
            "bounded_trig_probe",
            "candidate_later",
            58,
            "interval-guarded trig identity candidate to be defined later",
            [],
            "future bounded trig identity feasibility selector",
            [
                "The trig probe remains useful as a frontier branch.",
                "It should wait until the simpler affine-scaled shifted-log candidate receives feasibility review.",
            ],
            [
                "requires exact interval/domain guard",
                "requires negative controls before any proof work",
            ],
            [],
            "standard_trig_remains_runtime_control",
        ),
        candidate_row(
            "private_reviewer_response_intake",
            "private_review_lane",
            "candidate_later_requires_real_response",
            44,
            "actual reviewer response packet to be parsed only when one exists",
            [],
            "future private reviewer response intake",
            [
                "ACT-A16 is ready for private handoff but records no actual reviewer response.",
                "Reviewer intake remains a separate lane from bounded identity selection.",
            ],
            [
                "requires actual reviewer response artifact",
                "must not infer approval from handoff readiness",
            ],
            [],
            "not_a_runtime_candidate",
        ),
    ]
    selected = next(candidate for candidate in candidates if candidate["selectionStatus"] == "selected_next_feasibility_packet")
    duplicate_log1p = next(candidate for candidate in candidates if candidate["candidateId"] == "log1p_shifted_boundary_coordinate")
    duplicate_log1m = next(candidate for candidate in candidates if candidate["candidateId"] == "log1m_shifted_boundary_coordinate")
    summary = {
        "sourceSelector": source["artifactId"],
        "sourceSelectedOptionId": source_summary["selectedOptionId"],
        "sourceSelectedNextArtifact": source_summary["selectedNextArtifact"],
        "sourceFrozenWitnessName": source_summary["frozenWitnessName"],
        "sourceFrozenCheckedStatement": source_summary["frozenCheckedStatement"],
        "sourceFrozenGuards": list(source_summary["frozenGuards"]),
        "sourceDuplicateLog1pBlockPreserved": source_summary["duplicateLog1pBlockPreserved"],
        "sourceRuntimeLoweringControl": source_summary["runtimeLoweringControl"],
        "sourceRuntimeGuardrailStatus": source_summary["runtimeGuardrailStatus"],
        "sourcePublicAtlasStatus": source_summary["publicAtlasStatus"],
        "sourceActHandoffChainRange": source_summary["actHandoffChainRange"],
        "sourceActHandoffReady": source_summary["actHandoffReady"],
        "sourceActReviewerDecisionRecorded": source_summary["actReviewerDecisionRecorded"],
        "sourceActPromotionAllowed": source_summary["actPromotionAllowed"],
        "candidateCount": len(candidates),
        "selectedCandidateId": selected["candidateId"],
        "selectedFamily": selected["family"],
        "selectedNextArtifact": selected["nextArtifact"],
        "selectedProposedStatement": selected["proposedStatement"],
        "selectedGuardCount": len(selected["guards"]),
        "selectedGuards": list(selected["guards"]),
        "selectedDuplicateCheckedWitnessCount": len(selected["duplicateCheckedWitnesses"]),
        "selectedFreshRelativeToCheckedWitnesses": selected["freshRelativeToCheckedWitnesses"],
        "blockedDuplicateCandidateIds": [duplicate_log1p["candidateId"], duplicate_log1m["candidateId"]],
        "blockedDuplicateStatuses": [duplicate_log1p["selectionStatus"], duplicate_log1m["selectionStatus"]],
        "blockedDuplicateCheckedWitnesses": duplicate_log1p["duplicateCheckedWitnesses"]
        + duplicate_log1m["duplicateCheckedWitnesses"],
        "boundedIdentityCandidateSelected": True,
        "log1pAffineScaledCandidateSelected": True,
        "freshCandidateNonDuplicateSelected": True,
        "sourceD90SelectorObserved": True,
        "log1pShiftedDuplicateReselected": False,
        "log1mShiftedDuplicateReselected": False,
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
        "feasibilityPacketStarted": False,
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
        "claimFlagsCandidateSelectorOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "bounded_identity_candidate_selected",
                "log1p_affine_scaled_candidate_selected",
                "fresh_candidate_non_duplicate_selected",
                "source_d90_selector_observed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "bounded_identity_candidate_selected",
                "log1p_affine_scaled_candidate_selected",
                "fresh_candidate_non_duplicate_selected",
                "source_d90_selector_observed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_d91_bounded_identity_branch_candidate_selector_v0",
        "artifactId": "eml-d91-bounded-identity-branch-candidate-selector",
        "status": STATUS,
        "decision": "select_log1p_affine_scaled_boundary_coordinate_for_later_feasibility",
        "date": DATE,
        "sourceSelector": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "candidateRows": candidates,
        "selectedCandidate": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d90-post-log1m-shifted-pause-next-selector":
        raise ValueError("D91 must consume D90")
    if summary["sourceSelectedOptionId"] != "next_bounded_identity_branch_selector":
        raise ValueError("D90 must have selected the bounded identity branch selector")
    if summary["sourceSelectedNextArtifact"] != "EML-D91 bounded identity branch candidate selector":
        raise ValueError("D90 next artifact drift")
    if summary["sourceFrozenWitnessName"] != "MachLib.Real.log1m_shifted_boundary_coordinate_witness":
        raise ValueError("unexpected source frozen witness")
    if summary["sourceFrozenCheckedStatement"] != "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x":
        raise ValueError("unexpected source checked statement")
    if summary["sourceFrozenGuards"] != ["0 < 1 - x"]:
        raise ValueError("source shifted guard drift")
    if summary["sourceDuplicateLog1pBlockPreserved"] is not True:
        raise ValueError("duplicate-log1p source block drift")
    if summary["sourceRuntimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("source runtime control drift")
    if summary["sourceRuntimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("source runtime guardrail drift")
    if summary["sourcePublicAtlasStatus"] != "held_private":
        raise ValueError("source public hold drift")
    if summary["sourceActHandoffChainRange"] != "ACT-A13-A15":
        raise ValueError("unexpected ACT handoff chain")
    if summary["sourceActHandoffReady"] is not True:
        raise ValueError("ACT handoff readiness drift")
    if summary["sourceActReviewerDecisionRecorded"] is not False:
        raise ValueError("ACT reviewer decision must remain unrecorded")
    if summary["sourceActPromotionAllowed"] is not False:
        raise ValueError("ACT promotion must remain blocked")
    if summary["candidateCount"] != 5:
        raise ValueError("expected five candidates")
    if summary["selectedCandidateId"] != SELECTED_CANDIDATE_ID:
        raise ValueError("unexpected selected candidate")
    if summary["selectedFamily"] != "guarded_log1p_affine_scaled_coordinate":
        raise ValueError("unexpected selected family")
    if summary["selectedNextArtifact"] != SELECTED_NEXT_ARTIFACT:
        raise ValueError("unexpected selected next artifact")
    if summary["selectedProposedStatement"] != SELECTED_STATEMENT:
        raise ValueError("unexpected selected proposed statement")
    if summary["selectedGuardCount"] != 1 or summary["selectedGuards"] != ["0 < 1 + a * x"]:
        raise ValueError("selected guard drift")
    if summary["selectedDuplicateCheckedWitnessCount"] != 0 or summary["selectedFreshRelativeToCheckedWitnesses"] is not True:
        raise ValueError("selected candidate must be fresh relative to checked witnesses")
    if summary["blockedDuplicateCandidateIds"] != ["log1p_shifted_boundary_coordinate", "log1m_shifted_boundary_coordinate"]:
        raise ValueError("duplicate candidate rows missing")
    if summary["blockedDuplicateStatuses"] != ["blocked_duplicate_checked_witness", "blocked_duplicate_checked_witness"]:
        raise ValueError("duplicates must be blocked")
    if summary["blockedDuplicateCheckedWitnesses"] != [
        "MachLib.Real.log1p_shifted_boundary_coordinate_witness",
        "MachLib.Real.log1m_shifted_boundary_coordinate_witness",
    ]:
        raise ValueError("duplicate witness rows drifted")
    for key in [
        "boundedIdentityCandidateSelected",
        "log1pAffineScaledCandidateSelected",
        "freshCandidateNonDuplicateSelected",
        "sourceD90SelectorObserved",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "log1pShiftedDuplicateReselected",
        "log1mShiftedDuplicateReselected",
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
        "feasibilityPacketStarted",
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
    if summary["claimFlagsCandidateSelectorOnly"] is not True:
        raise ValueError("claim flags must remain candidate-selector-only")
    true_keys = {
        "bounded_identity_candidate_selected",
        "log1p_affine_scaled_candidate_selected",
        "fresh_candidate_non_duplicate_selected",
        "source_d90_selector_observed",
    }
    for key in true_keys:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in true_keys and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_d91_bounded_identity_branch_candidate_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_fresh_log1p_affine_scaled_candidate_no_feasibility_no_proof_no_runtime_no_public",
        "source": f"python/results/eml_d91_bounded_identity_branch_candidate_selector/eml_d91_bounded_identity_branch_candidate_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d91_bounded_identity_branch_candidate_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "blockedDuplicateCandidateIds": payload["summary"]["blockedDuplicateCandidateIds"],
        "nextAction": "Run EML-D92 as a log1p affine-scaled boundary coordinate feasibility packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D91 Bounded Identity Branch Candidate Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D91 selects one fresh bounded identity candidate after D90 and leaves feasibility, proof, runtime, public copy, and reviewer intake for later phases.",
        "",
        "| Candidate | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for candidate in payload["candidateRows"]:
        lines.append(
            f"| `{candidate['candidateId']}` | `{candidate['selectionStatus']}` | {candidate['priorityScore']} | {candidate['nextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected candidate: `{payload['summary']['selectedCandidateId']}`",
            f"- proposed statement: `{payload['summary']['selectedProposedStatement']}`",
            f"- selected next artifact: `{payload['summary']['selectedNextArtifact']}`",
            f"- blocked duplicates: `{', '.join(payload['summary']['blockedDuplicateCandidateIds'])}`",
            f"- source frozen witness: `{payload['summary']['sourceFrozenWitnessName']}`",
            f"- runtime control: `{payload['summary']['sourceRuntimeLoweringControl']}`",
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
    result_path = out_dir / f"eml_d91_bounded_identity_branch_candidate_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d91_bounded_identity_branch_candidate_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d91_bounded_identity_branch_candidate_selector.json"
    feed_path = command_feed_dir / f"eml_d91_bounded_identity_branch_candidate_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d91_bounded_identity_branch_candidate_selector")
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
    print("EML_D91_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
