#!/usr/bin/env python3
"""EML-D92 log1p affine-scaled boundary coordinate feasibility packet."""

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

from scripts import eml_d91_bounded_identity_branch_candidate_selector as d91  # noqa: E402

DATE = "2026-06-04"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D92_LOG1P_AFFINE_SCALED_BOUNDARY_COORDINATE_FEASIBILITY_PASS"

SELECTED_CANDIDATE_ID = "log1p_affine_scaled_boundary_coordinate"
PROPOSED_MACHLIB_NAME = "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness"
PROPOSED_STATEMENT = "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"
NEXT_ARTIFACT = "EML-D93 log1p affine-scaled boundary coordinate MachLib witness attempt or blocker"

CLAIM_FLAGS = {
    "witness_feasibility_recorded": True,
    "bounded_identity_candidate_selected": True,
    "log1p_affine_scaled_candidate_selected": True,
    "guarded_domain_obligations_recorded": True,
    "negative_controls_recorded": True,
    "duplicate_shifted_blocks_preserved": True,
    "source_d91_selector_observed": True,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_log_replacement_claim": False,
    "protected_log1p_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
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
    "EML-D92 records guarded feasibility only; it does not edit MachLib, typecheck Lean, or start a proof attempt.",
    "D92 keeps protected log/log1p controls as runtime controls and makes no log, log1p, or log-exp replacement claim.",
    "D92 preserves D91's duplicate blocks for the already checked log1p-shifted and log1m-shifted witnesses.",
    "D92 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, formal equivalence, broad log1p-family scope, or broad EML superiority.",
]

FEASIBILITY_ITEMS = [
    {
        "itemId": "selected_branch_matches_d91",
        "status": "satisfied",
        "evidence": "D91 selected log1p_affine_scaled_boundary_coordinate as selected_next_feasibility_packet.",
        "reviewNote": "The feasibility packet stays inside the selected bounded identity candidate.",
    },
    {
        "itemId": "domain_obligation_visible",
        "status": "satisfied",
        "evidence": "The statement carries guard 0 < 1 + a * x, making the logarithm argument positive.",
        "reviewNote": "The coordinate is feasible only as a guarded-domain statement.",
    },
    {
        "itemId": "proof_shape_visible",
        "status": "satisfied",
        "evidence": "Unfolding eml gives exp (log (1 + a * x)) - log (exp 1); guarded exp-log and log-exp rewrites reduce this to (1 + a * x) - 1.",
        "reviewNote": "The expected witness attempt should be a small guarded rewrite, not a search or runtime claim.",
    },
    {
        "itemId": "affine_payload_boundary_visible",
        "status": "satisfied",
        "evidence": "The affine payload a * x is kept inside the guarded shifted-log argument instead of asserting a separate global condition on a or x.",
        "reviewNote": "The guard is on the composed argument, not on standalone a or x values.",
    },
    {
        "itemId": "negative_controls_required",
        "status": "satisfied",
        "evidence": "Boundary controls for 1 + a * x = 0, 1 + a * x < 0, unguarded statements, and a = 1 duplicate collapse are recorded as blockers.",
        "reviewNote": "Any future proof attempt must preserve the positive affine-shifted-domain guard.",
    },
    {
        "itemId": "protected_log1p_runtime_control_preserved",
        "status": "satisfied",
        "evidence": "The packet keeps protected_log_and_log1p_remain_runtime_controls and records no runtime lowering change.",
        "reviewNote": "The identity may be proof-shape useful while protected logarithmic routines remain runtime controls.",
    },
    {
        "itemId": "duplicate_shifted_blocks_preserved",
        "status": "satisfied",
        "evidence": "D91 blocked both checked shifted-coordinate duplicates: MachLib.Real.log1p_shifted_boundary_coordinate_witness and MachLib.Real.log1m_shifted_boundary_coordinate_witness.",
        "reviewNote": "D92 evaluates only the affine-scaled candidate and does not reopen either checked shifted-log lane.",
    },
]

NEGATIVE_CONTROLS = [
    {
        "controlId": "affine_shift_zero_boundary_blocked",
        "status": "blocked_by_guard",
        "blockedCondition": "1 + a * x = 0",
        "reason": "log (1 + a * x) is outside the guarded real-log rewrite domain.",
    },
    {
        "controlId": "affine_shift_negative_boundary_blocked",
        "status": "blocked_by_guard",
        "blockedCondition": "1 + a * x < 0",
        "reason": "1 + a * x is not positive, so the guarded exp-log rewrite is unavailable.",
    },
    {
        "controlId": "unguarded_affine_scaled_coordinate_blocked",
        "status": "blocked_by_guard",
        "blockedCondition": "missing 0 < 1 + a * x",
        "reason": "The feasibility argument depends on the affine-shifted logarithm argument being positive.",
    },
    {
        "controlId": "a_equals_one_duplicate_collapse_blocked_as_fresh_claim",
        "status": "blocked_by_duplicate_boundary",
        "blockedCondition": "treating the a = 1 specialization as fresh work",
        "reason": "The a = 1 specialization collapses to the already checked log1p-shifted witness and must not be claimed as a new artifact.",
    },
    {
        "controlId": "runtime_log1p_replacement_blocked",
        "status": "blocked_by_claim_boundary",
        "blockedCondition": "claiming log/log1p runtime replacement",
        "reason": "D92 records proof-shape feasibility only and keeps protected log/log1p runtime controls.",
    },
]

BLOCKERS = [
    {
        "blockerId": "domain_edge_loss",
        "severity": "hard_blocker",
        "description": "Any future witness attempt must carry the guard 0 < 1 + a * x before rewriting exp (log (1 + a * x)).",
    },
    {
        "blockerId": "affine_specialization_overclaim",
        "severity": "hard_blocker",
        "description": "The a = 1 specialization must remain identified as the already checked log1p-shifted witness, not a fresh result.",
    },
    {
        "blockerId": "runtime_relabeling",
        "severity": "hard_blocker",
        "description": "The identity must not be relabeled as runtime lowering, log/log1p replacement, or runtime advantage.",
    },
    {
        "blockerId": "proof_or_typecheck_claim",
        "severity": "hard_blocker",
        "description": "D92 records feasibility only; any proof, Lean typecheck, or MachLib edit requires a separate D93 phase.",
    },
    {
        "blockerId": "broad_log1p_family_language",
        "severity": "hard_blocker",
        "description": "The packet must not broaden the single guarded affine-scaled coordinate into all log1p, logarithm, or affine-domain identities.",
    },
]


def candidate_by_id(payload: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in payload["candidateRows"] if item["candidateId"] == candidate_id)


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d91.build_payload(atlas_gate_path)
    d91.validate_payload(selector)
    selected = selector["selectedCandidate"]
    duplicate_log1p = candidate_by_id(selector, "log1p_shifted_boundary_coordinate")
    duplicate_log1m = candidate_by_id(selector, "log1m_shifted_boundary_coordinate")
    proposed_witness = {
        "candidateId": selected["candidateId"],
        "family": selected["family"],
        "proposedMachlibName": PROPOSED_MACHLIB_NAME,
        "statementKind": "guarded_real_identity",
        "sourceProposedStatement": selected["proposedStatement"],
        "proposedStatement": PROPOSED_STATEMENT,
        "guardShape": list(selected["guards"]),
        "derivedDomainObligations": ["0 < 1 + a * x", "0 < exp 1"],
        "guardPolicy": "affine_shifted_positive_log_guard_required",
        "semanticControl": "guarded_real_exp_log_and_log_exp_rewrite_control",
        "runtimeControl": selected["runtimeControl"],
        "expectedProofShape": [
            "introduce guard 0 < 1 + a * x",
            "unfold eml",
            "rewrite exp (log (1 + a * x)) to 1 + a * x under the guard",
            "rewrite log (exp 1) to 1",
            "normalize (1 + a * x) - 1 to a * x",
            "preserve protected log/log1p runtime controls",
        ],
        "nextArtifact": NEXT_ARTIFACT,
    }
    summary = {
        "sourceCandidateSelector": selector["artifactId"],
        "sourceSelectedCandidateId": selector["summary"]["selectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["selectedFamily"],
        "sourceSelectedProposedStatement": selector["summary"]["selectedProposedStatement"],
        "sourceSelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "sourceRuntimeLoweringControl": selector["summary"]["sourceRuntimeLoweringControl"],
        "sourceFrozenWitnessName": selector["summary"]["sourceFrozenWitnessName"],
        "sourceFrozenCheckedStatement": selector["summary"]["sourceFrozenCheckedStatement"],
        "sourceFrozenGuards": list(selector["summary"]["sourceFrozenGuards"]),
        "sourceActHandoffReady": selector["summary"]["sourceActHandoffReady"],
        "sourceActReviewerDecisionRecorded": selector["summary"]["sourceActReviewerDecisionRecorded"],
        "sourceActPromotionAllowed": selector["summary"]["sourceActPromotionAllowed"],
        "blockedDuplicateCandidateIds": [duplicate_log1p["candidateId"], duplicate_log1m["candidateId"]],
        "blockedDuplicateStatuses": [duplicate_log1p["selectionStatus"], duplicate_log1m["selectionStatus"]],
        "blockedDuplicateCheckedWitnesses": duplicate_log1p["duplicateCheckedWitnesses"]
        + duplicate_log1m["duplicateCheckedWitnesses"],
        "feasibilityRecorded": True,
        "feasibilityStatus": "feasible_for_guarded_scoped_witness_attempt",
        "proposedMachlibName": proposed_witness["proposedMachlibName"],
        "proposedStatement": proposed_witness["proposedStatement"],
        "guardCount": len(proposed_witness["guardShape"]),
        "derivedDomainObligationCount": len(proposed_witness["derivedDomainObligations"]),
        "expectedProofStepCount": len(proposed_witness["expectedProofShape"]),
        "feasibilityItemCount": len(FEASIBILITY_ITEMS),
        "negativeControlCount": len(NEGATIVE_CONTROLS),
        "blockerCount": len(BLOCKERS),
        "duplicateShiftedBlocksPreserved": True,
        "sourceD91SelectorObserved": True,
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
        "runtimeLoweringControl": selected["runtimeControl"],
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "publicCopyApproved": False,
        "advantageLabCaseAdded": False,
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
        "nextArtifact": proposed_witness["nextArtifact"],
        "claimFlagsFeasibilityOnly": all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "witness_feasibility_recorded",
                "bounded_identity_candidate_selected",
                "log1p_affine_scaled_candidate_selected",
                "guarded_domain_obligations_recorded",
                "negative_controls_recorded",
                "duplicate_shifted_blocks_preserved",
                "source_d91_selector_observed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_v0",
        "artifactId": "eml-d92-log1p-affine-scaled-boundary-coordinate-feasibility-packet",
        "status": STATUS,
        "decision": "record_log1p_affine_scaled_boundary_coordinate_feasibility",
        "date": DATE,
        "sourceCandidateSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "proposedWitness": proposed_witness,
        "feasibilityItems": list(FEASIBILITY_ITEMS),
        "negativeControls": list(NEGATIVE_CONTROLS),
        "blockers": list(BLOCKERS),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    witness = payload["proposedWitness"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceCandidateSelector"] != "eml-d91-bounded-identity-branch-candidate-selector":
        raise ValueError("D92 must consume D91")
    if summary["sourceSelectedCandidateId"] != SELECTED_CANDIDATE_ID:
        raise ValueError("D92 must preserve the D91 selected candidate")
    if summary["sourceSelectedFamily"] != "guarded_log1p_affine_scaled_coordinate":
        raise ValueError("D92 must preserve the D91 selected family")
    if summary["sourceSelectedProposedStatement"] != PROPOSED_STATEMENT:
        raise ValueError("unexpected source proposed statement")
    if summary["sourceSelectedNextArtifact"] != "EML-D92 log1p affine-scaled boundary coordinate feasibility packet":
        raise ValueError("unexpected D91 next artifact")
    if summary["sourceRuntimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("D91 runtime control drift")
    if summary["sourceFrozenWitnessName"] != "MachLib.Real.log1m_shifted_boundary_coordinate_witness":
        raise ValueError("D90 frozen witness drift")
    if summary["sourceFrozenCheckedStatement"] != "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x":
        raise ValueError("D90 frozen statement drift")
    if summary["sourceFrozenGuards"] != ["0 < 1 - x"]:
        raise ValueError("D90 frozen guard drift")
    if summary["sourceActHandoffReady"] is not True:
        raise ValueError("ACT handoff readiness drift")
    if summary["sourceActReviewerDecisionRecorded"] is not False or summary["sourceActPromotionAllowed"] is not False:
        raise ValueError("ACT decision/promotion must remain blocked")
    if summary["blockedDuplicateCandidateIds"] != [
        "log1p_shifted_boundary_coordinate",
        "log1m_shifted_boundary_coordinate",
    ]:
        raise ValueError("duplicate shifted blocks missing")
    if summary["blockedDuplicateStatuses"] != [
        "blocked_duplicate_checked_witness",
        "blocked_duplicate_checked_witness",
    ]:
        raise ValueError("duplicate shifted block status drift")
    if summary["blockedDuplicateCheckedWitnesses"] != [
        "MachLib.Real.log1p_shifted_boundary_coordinate_witness",
        "MachLib.Real.log1m_shifted_boundary_coordinate_witness",
    ]:
        raise ValueError("duplicate checked witness drift")
    if witness["proposedMachlibName"] != PROPOSED_MACHLIB_NAME:
        raise ValueError("unexpected proposed MachLib name")
    if witness["proposedStatement"] != PROPOSED_STATEMENT:
        raise ValueError("unexpected proposed statement")
    if witness["guardShape"] != ["0 < 1 + a * x"]:
        raise ValueError("unexpected guard shape")
    if witness["derivedDomainObligations"] != ["0 < 1 + a * x", "0 < exp 1"]:
        raise ValueError("unexpected derived domain obligations")
    if summary["guardCount"] != 1:
        raise ValueError("expected one guard")
    if summary["derivedDomainObligationCount"] != 2:
        raise ValueError("expected two derived domain obligations")
    if summary["feasibilityRecorded"] is not True:
        raise ValueError("feasibility must be recorded")
    if summary["feasibilityStatus"] != "feasible_for_guarded_scoped_witness_attempt":
        raise ValueError("unexpected feasibility status")
    if summary["expectedProofStepCount"] != 6:
        raise ValueError("expected six proof-shape notes")
    if summary["feasibilityItemCount"] != 7:
        raise ValueError("expected seven feasibility items")
    if summary["negativeControlCount"] != 5:
        raise ValueError("expected five negative controls")
    if summary["blockerCount"] != 5:
        raise ValueError("expected five blockers")
    if summary["duplicateShiftedBlocksPreserved"] is not True:
        raise ValueError("duplicate shifted blocks must be preserved")
    if summary["sourceD91SelectorObserved"] is not True:
        raise ValueError("D91 selector observation must be recorded")
    for key in [
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
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicCopyApproved",
        "advantageLabCaseAdded",
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
    if summary["nextArtifact"] != NEXT_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsFeasibilityOnly"] is not True:
        raise ValueError("claim flags must remain feasibility-only")
    true_keys = {
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "log1p_affine_scaled_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
        "duplicate_shifted_blocks_preserved",
        "source_d91_selector_observed",
    }
    for key in true_keys:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in true_keys and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(item["status"] != "satisfied" for item in payload["feasibilityItems"]):
        raise ValueError("all feasibility items must be satisfied")
    allowed_statuses = {
        "blocked_by_guard",
        "blocked_by_claim_boundary",
        "blocked_by_duplicate_boundary",
    }
    if any(item["status"] not in allowed_statuses for item in payload["negativeControls"]):
        raise ValueError("negative controls must be blocked")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_guarded_affine_scaled_feasibility_packet_no_machlib_edit_no_typecheck_no_runtime_no_public",
        "source": f"python/results/eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet/eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "proposedMachlibName": payload["summary"]["proposedMachlibName"],
        "proposedStatement": payload["summary"]["proposedStatement"],
        "guardCount": payload["summary"]["guardCount"],
        "negativeControlCount": payload["summary"]["negativeControlCount"],
        "nextAction": "Run EML-D93 only as a scoped guarded MachLib witness attempt or precise blocker.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D92 Log1p Affine-Scaled Boundary Coordinate Feasibility Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Proposed witness: `{payload['summary']['proposedMachlibName']}`",
        "",
        f"Statement: `{payload['summary']['proposedStatement']}`",
        "",
        "D92 records guarded feasibility before any MachLib edit, Lean typecheck, or proof attempt.",
        "",
        "## Feasibility Items",
        "",
        "| Item | Status | Review note |",
        "|---|---|---|",
    ]
    for item in payload["feasibilityItems"]:
        lines.append(f"| `{item['itemId']}` | `{item['status']}` | {item['reviewNote']} |")
    lines.extend(
        [
            "",
            "## Negative Controls",
            "",
            "| Control | Status | Reason |",
            "|---|---|---|",
        ]
    )
    for item in payload["negativeControls"]:
        lines.append(f"| `{item['controlId']}` | `{item['status']}` | {item['reason']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- source candidate: `{payload['summary']['sourceSelectedCandidateId']}`",
            f"- guard count: `{payload['summary']['guardCount']}`",
            f"- derived domain obligation count: `{payload['summary']['derivedDomainObligationCount']}`",
            f"- duplicate shifted blocks preserved: `{payload['summary']['duplicateShiftedBlocksPreserved']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- candidate proved: `{payload['summary']['candidateProved']}`",
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
    result_path = out_dir / f"eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet.json"
    feed_path = command_feed_dir / f"eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/eml_d92_log1p_affine_scaled_boundary_coordinate_feasibility_packet",
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
    print("EML_D92_LOG1P_AFFINE_SCALED_BOUNDARY_COORDINATE_FEASIBILITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
