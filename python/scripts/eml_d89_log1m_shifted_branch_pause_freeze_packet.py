#!/usr/bin/env python3
"""EML-D89 log1m-shifted branch pause and checked-witness copy freeze packet."""

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

from scripts import eml_d88_log1m_shifted_post_copy_review_next_selector as d88  # noqa: E402

DATE = "2026-06-04"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_log1m_shifted_branch_pause_freeze_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D89_LOG1M_SHIFTED_BRANCH_PAUSE_FREEZE_PACKET_PASS"

CLAIM_FLAGS = {
    "branch_pause_started": True,
    "checked_witness_copy_frozen": True,
    "private_freeze_packet": True,
    "duplicate_log1p_block_preserved": True,
    "next_action_selected": False,
    "new_bounded_branch_selected": False,
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
    "EML-D89 pauses the log1m-shifted branch and freezes the checked private copy boundary only; it does not approve or publish public copy.",
    "D89 records no new proof attempt, no MachLib edit, no Lean typecheck, no implementation work, no reviewer decision, and no runtime lowering change.",
    "D89 preserves the D83/D82 duplicate-log1p block and does not reopen the checked log1p-shifted lane as fresh work.",
    "D89 does not claim theorem discovery, protected log/log1p replacement, runtime advantage, broad EML superiority, public readiness, course work, laptop intake, or electronics repo changes.",
]


def freeze_row(
    freeze_id: str,
    machlib_name: str,
    checked_statement: str,
    guards: list[str],
    frozen_caveats: list[str],
    frozen_blocked_phrases: list[str],
    runtime_control: str,
) -> dict[str, Any]:
    return {
        "freezeId": freeze_id,
        "machlibName": machlib_name,
        "checkedStatement": checked_statement,
        "guards": guards,
        "frozenCaveats": frozen_caveats,
        "frozenBlockedPhrases": frozen_blocked_phrases,
        "runtimeControl": runtime_control,
        "freezeStatus": "private_checked_witness_copy_frozen",
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def parked_option(option_id: str, lane: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "lane": lane,
        "status": status,
        "reason": reason,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d88.build_payload(atlas_gate_path)
    d88.validate_payload(selector)
    frozen_caveats = [
        "This checked-witness copy freeze is private-only.",
        "The checked statement is 0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x.",
        "The witness name is MachLib.Real.log1m_shifted_boundary_coordinate_witness.",
        "The shifted positive-domain guard, 0 < 1 - x, remains required.",
        "Protected log and log1p remain the runtime and domain controls.",
        "D83 negative controls for x = 1, x > 1, and unguarded statements remain blocked.",
        "The D83/D82 duplicate-log1p block remains preserved.",
        "The witness is one scoped MachLib theorem name, not a broad log1m, log1p, or logarithm theory.",
        "Advantage Lab and runtime-performance claims require separate evidence.",
        "Public Atlas and public education promotion remain false.",
    ]
    frozen_blocked_phrases = [
        "theorem discovery",
        "log replacement",
        "log1p replacement",
        "protected log replacement",
        "protected log1p replacement",
        "runtime advantage",
        "log1m theory",
        "log1p theory",
        "logarithm theory",
        "unguarded shifted logarithm identity",
        "public ready",
        "broad EML advantage",
        "formal equivalence",
    ]
    freeze_rows = [
        freeze_row(
            "log1m_shifted_boundary_coordinate_checked_copy",
            selector["summary"]["selectedWitnessName"],
            selector["summary"]["checkedStatement"],
            ["0 < 1 - x"],
            frozen_caveats,
            frozen_blocked_phrases,
            selector["summary"]["runtimeLoweringControl"],
        )
    ]
    parked_options = [
        parked_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "parked_after_log1m_shifted_pause",
            "Available only through a later selector after the log1m-shifted checked-witness copy boundary is frozen.",
        ),
        parked_option(
            "private_reviewer_response_intake",
            "private_reviewer_intake_lane",
            "parked_requires_actual_reviewer_response",
            "Requires a real reviewer response artifact; D89 records no reviewer approval, rejection, or artifact acceptance.",
        ),
        parked_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "parked_after_log1m_shifted_pause",
            "Requires a separate guarded feasibility selector and negative controls.",
        ),
        parked_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "parked_requires_explicit_human_approval",
            "D89 freezes private copy boundaries but records no human approval for public use.",
        ),
    ]
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "selectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "sourceSelectedCandidateId": selector["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["sourceSelectedFamily"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "checkedStatement": selector["summary"]["checkedStatement"],
        "machlibFile": selector["summary"]["machlibFile"],
        "branchPauseStarted": True,
        "checkedWitnessCopyFrozen": True,
        "privateFreezePacket": True,
        "freezeRowCount": len(freeze_rows),
        "guardCount": selector["summary"]["guardCount"],
        "sourceDerivedDomainObligationCount": selector["summary"]["sourceDerivedDomainObligationCount"],
        "sourceNegativeControlCount": selector["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": selector["summary"]["sourceBlockerCount"],
        "sourceDuplicateLog1pBlockPreserved": selector["summary"]["sourceDuplicateLog1pBlockPreserved"],
        "duplicateLog1pBlockPreserved": selector["summary"]["duplicateLog1pBlockPreserved"],
        "d85SurfaceRowCount": selector["summary"]["d85SurfaceRowCount"],
        "frozenCaveatCount": len(frozen_caveats),
        "frozenBlockedPhraseCount": len(frozen_blocked_phrases),
        "sourceD87RequiredCaveatCount": selector["summary"]["d87RequiredCaveatCount"],
        "sourceD87BlockedGlobalPhraseCount": selector["summary"]["d87BlockedGlobalPhraseCount"],
        "sourceD87RowRequiredCaveatCount": selector["summary"]["d87RowRequiredCaveatCount"],
        "sourceD87RowBlockedPhraseCount": selector["summary"]["d87RowBlockedPhraseCount"],
        "runtimeGuardrailStatus": selector["summary"]["runtimeGuardrailStatus"],
        "guardBoundaryStatus": selector["summary"]["guardBoundaryStatus"],
        "publicAtlasStatus": selector["summary"]["publicAtlasStatus"],
        "runtimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
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
        "newBoundedBranchSelected": False,
        "boundedTrigFeasibilitySelected": False,
        "privateReviewerResponseIntakeSelected": False,
        "humanApprovedPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "parkedNextBoundedIdentityBranchSelector": True,
        "parkedPrivateReviewerResponseIntake": True,
        "parkedBoundedTrigFeasibility": True,
        "parkedHumanApprovedPublicCopyGate": True,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D90 select the next private post-pause action without public promotion.",
        "claimFlagsFrozenOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "branch_pause_started",
                "checked_witness_copy_frozen",
                "private_freeze_packet",
                "duplicate_log1p_block_preserved",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "branch_pause_started",
                "checked_witness_copy_frozen",
                "private_freeze_packet",
                "duplicate_log1p_block_preserved",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_log1m_shifted_branch_pause_freeze_packet_v0",
        "artifactId": "eml-d89-log1m-shifted-branch-pause-freeze-packet",
        "status": STATUS,
        "decision": "pause_log1m_shifted_branch_and_freeze_checked_witness_copy",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "freezeRows": freeze_rows,
        "parkedOptions": parked_options,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d88-log1m-shifted-post-copy-review-next-selector":
        raise ValueError("D89 must consume D88")
    if summary["selectedOptionId"] != "log1m_shifted_branch_pause_freeze_packet":
        raise ValueError("unexpected D88 selected option")
    if summary["selectedNextArtifact"] != "EML-D89 log1m-shifted branch pause and checked-witness copy freeze packet":
        raise ValueError("unexpected D88 next artifact")
    if summary["sourceSelectedCandidateId"] != "log1m_shifted_boundary_coordinate":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "guarded_log1m_shifted_coordinate":
        raise ValueError("unexpected family")
    if summary["selectedWitnessName"] != "MachLib.Real.log1m_shifted_boundary_coordinate_witness":
        raise ValueError("unexpected witness")
    if summary["checkedStatement"] != "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x":
        raise ValueError("unexpected checked statement")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    for key in [
        "branchPauseStarted",
        "checkedWitnessCopyFrozen",
        "privateFreezePacket",
        "sourceDuplicateLog1pBlockPreserved",
        "duplicateLog1pBlockPreserved",
        "parkedNextBoundedIdentityBranchSelector",
        "parkedPrivateReviewerResponseIntake",
        "parkedBoundedTrigFeasibility",
        "parkedHumanApprovedPublicCopyGate",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["freezeRowCount"] != 1:
        raise ValueError("expected one freeze row")
    if summary["guardCount"] != 1 or summary["sourceDerivedDomainObligationCount"] != 2:
        raise ValueError("log1m-shifted guard/domain counts drifted")
    if summary["sourceNegativeControlCount"] != 4 or summary["sourceBlockerCount"] != 4:
        raise ValueError("negative control/blocker counts drifted")
    if summary["d85SurfaceRowCount"] != 5:
        raise ValueError("D85 row count drift")
    if summary["frozenCaveatCount"] != 10:
        raise ValueError("unexpected caveat count")
    if summary["frozenBlockedPhraseCount"] != 13:
        raise ValueError("unexpected blocked phrase count")
    if summary["sourceD87RequiredCaveatCount"] != 10 or summary["sourceD87BlockedGlobalPhraseCount"] != 13:
        raise ValueError("D87 caveat/blocker counts drifted")
    if summary["sourceD87RowRequiredCaveatCount"] != 7 or summary["sourceD87RowBlockedPhraseCount"] != 12:
        raise ValueError("D87 row copy boundary counts drifted")
    if summary["runtimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("runtime guardrail drift")
    if summary["guardBoundaryStatus"] != "shifted_positive_domain_boundary_required":
        raise ValueError("guard boundary drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    for key in [
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
        "newBoundedBranchSelected",
        "boundedTrigFeasibilitySelected",
        "privateReviewerResponseIntakeSelected",
        "humanApprovedPublicCopyGateSelected",
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
    if summary["nextAction"] != "EML-D90 select the next private post-pause action without public promotion.":
        raise ValueError("unexpected next action")
    if summary["claimFlagsFrozenOnly"] is not True:
        raise ValueError("claim flags must remain freeze-only")
    for row in payload["freezeRows"]:
        if row["machlibName"] != "MachLib.Real.log1m_shifted_boundary_coordinate_witness":
            raise ValueError("unexpected freeze row witness")
        if row["checkedStatement"] != "0 < 1 - x -> eml (log (1 - x)) (exp 1) = -x":
            raise ValueError("unexpected row checked statement")
        if row["guards"] != ["0 < 1 - x"]:
            raise ValueError("log1m-shifted freeze row must preserve the shifted guard")
        if row["runtimeControl"] != "protected_log_and_log1p_remain_runtime_controls":
            raise ValueError("row runtime control drift")
        if row["publicPromotionAllowed"] is not False:
            raise ValueError("freeze row must not allow public promotion")
    allowed_true = {
        "branch_pause_started",
        "checked_witness_copy_frozen",
        "private_freeze_packet",
        "duplicate_log1p_block_preserved",
    }
    for key in allowed_true:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_log1m_shifted_branch_pause_freeze_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_log1m_shifted_checked_witness_copy_frozen_public_copy_held_no_new_proof",
        "source": f"python/results/eml_d89_log1m_shifted_branch_pause_freeze_packet/eml_d89_log1m_shifted_branch_pause_freeze_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d89_log1m_shifted_branch_pause_freeze_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "freezeRowCount": payload["summary"]["freezeRowCount"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D89 Log1m-Shifted Branch Pause Freeze Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D89 pauses the log1m-shifted branch and freezes the checked private witness copy boundary.",
        "",
        "| Freeze row | Witness | Checked statement | Runtime control |",
        "|---|---|---|---|",
    ]
    for row in payload["freezeRows"]:
        lines.append(
            f"| `{row['freezeId']}` | `{row['machlibName']}` | `{row['checkedStatement']}` | {row['runtimeControl']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- branch pause started: `{payload['summary']['branchPauseStarted']}`",
            f"- checked witness copy frozen: `{payload['summary']['checkedWitnessCopyFrozen']}`",
            f"- duplicate-log1p block preserved: `{payload['summary']['duplicateLog1pBlockPreserved']}`",
            f"- guard count: `{payload['summary']['guardCount']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- public hold status: `{payload['summary']['publicAtlasStatus']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- next action: `{payload['summary']['nextAction']}`",
            "",
            "## Parked Options",
            "",
        ]
    )
    lines.extend(f"- `{item['optionId']}`: `{item['status']}`" for item in payload["parkedOptions"])
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
    result_path = out_dir / f"eml_d89_log1m_shifted_branch_pause_freeze_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d89_log1m_shifted_branch_pause_freeze_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d89_log1m_shifted_branch_pause_freeze_packet.json"
    feed_path = command_feed_dir / f"eml_d89_log1m_shifted_branch_pause_freeze_packet_feed_{STAMP}.json"
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
        default=ROOT / "python/results/eml_d89_log1m_shifted_branch_pause_freeze_packet",
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
    print("EML_D89_LOG1M_SHIFTED_BRANCH_PAUSE_FREEZE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
