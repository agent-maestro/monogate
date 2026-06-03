#!/usr/bin/env python3
"""EML-D71 probability-logit branch pause and checked-witness copy freeze packet."""

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

from scripts import eml_d70_probability_logit_branch_pause_next_selector as d70  # noqa: E402

DATE = "2026-06-03"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_probability_logit_branch_pause_freeze_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D71_PROBABILITY_LOGIT_BRANCH_PAUSE_FREEZE_PACKET_PASS"

CLAIM_FLAGS = {
    "branch_pause_started": True,
    "checked_witness_copy_frozen": True,
    "private_freeze_packet": True,
    "next_action_selected": False,
    "new_bounded_branch_selected": False,
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
    "EML-D71 pauses the probability-logit branch and freezes the checked private copy boundary only; it does not approve or publish public copy.",
    "D71 records no new proof attempt, no MachLib edit, no Lean typecheck, no implementation work, and no runtime lowering change.",
    "D71 does not claim theorem discovery, protected log/log1p replacement, logit replacement, runtime advantage, broad EML superiority, public readiness, course work, laptop intake, or electronics repo changes.",
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
    selector = d70.build_payload(atlas_gate_path)
    d70.validate_payload(selector)
    frozen_caveats = [
        "This checked-witness copy freeze is private-only.",
        "The checked statement is 0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p).",
        "The witness name is MachLib.Real.probability_logit_boundary_coordinate_witness.",
        "Both probability interval guards, 0 < p and p < 1, remain required.",
        "Protected log and log1p remain the runtime and domain controls.",
        "D65 negative controls for p = 0, p = 1, and unguarded statements remain blocked.",
        "The witness is one scoped MachLib theorem name, not a broad probability/logit theory.",
        "Advantage Lab and runtime-performance claims require separate evidence.",
        "Public Atlas and public education promotion remain false.",
    ]
    frozen_blocked_phrases = [
        "theorem discovery",
        "log replacement",
        "log1p replacement",
        "logit replacement",
        "protected log replacement",
        "protected log1p replacement",
        "runtime advantage",
        "probability/logit theory",
        "unguarded probability identity",
        "public ready",
        "broad EML advantage",
        "formal equivalence",
    ]
    freeze_rows = [
        freeze_row(
            "probability_logit_boundary_coordinate_checked_copy",
            selector["summary"]["selectedWitnessName"],
            selector["summary"]["checkedStatement"],
            ["0 < p", "p < 1"],
            frozen_caveats,
            frozen_blocked_phrases,
            selector["summary"]["runtimeLoweringControl"],
        )
    ]
    parked_options = [
        parked_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "parked_after_probability_logit_pause",
            "Available only through a later selector after the probability-logit checked-witness copy boundary is frozen.",
        ),
        parked_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "parked_after_probability_logit_pause",
            "Requires a separate guarded feasibility selector and negative controls.",
        ),
        parked_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "parked_requires_explicit_human_approval",
            "D71 freezes private copy boundaries but records no human approval for public use.",
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
        "d67SurfaceRowCount": selector["summary"]["d67SurfaceRowCount"],
        "frozenCaveatCount": len(frozen_caveats),
        "frozenBlockedPhraseCount": len(frozen_blocked_phrases),
        "sourceD69RequiredCaveatCount": selector["summary"]["d69RequiredCaveatCount"],
        "sourceD69BlockedGlobalPhraseCount": selector["summary"]["d69BlockedGlobalPhraseCount"],
        "sourceD69RowRequiredCaveatCount": selector["summary"]["d69RowRequiredCaveatCount"],
        "sourceD69RowBlockedPhraseCount": selector["summary"]["d69RowBlockedPhraseCount"],
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
        "humanApprovedPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "parkedNextBoundedIdentityBranchSelector": True,
        "parkedBoundedTrigFeasibility": True,
        "parkedHumanApprovedPublicCopyGate": True,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D72 select the next private post-pause action without public promotion.",
        "claimFlagsFrozenOnly": all(
            CLAIM_FLAGS[key] is True
            for key in ["branch_pause_started", "checked_witness_copy_frozen", "private_freeze_packet"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"branch_pause_started", "checked_witness_copy_frozen", "private_freeze_packet"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_probability_logit_branch_pause_freeze_packet_v0",
        "artifactId": "eml-d71-probability-logit-branch-pause-freeze-packet",
        "status": STATUS,
        "decision": "pause_probability_logit_branch_and_freeze_checked_witness_copy",
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
    if payload["sourceSelector"] != "eml-d70-probability-logit-branch-pause-next-selector":
        raise ValueError("D71 must consume D70")
    if summary["selectedOptionId"] != "probability_logit_branch_pause_freeze_packet":
        raise ValueError("unexpected D70 selected option")
    if summary["selectedNextArtifact"] != "EML-D71 probability-logit branch pause and checked-witness copy freeze packet":
        raise ValueError("unexpected D70 next artifact")
    if summary["sourceSelectedCandidateId"] != "probability_logit_boundary_coordinate":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "guarded_probability_log_coordinate":
        raise ValueError("unexpected family")
    if summary["selectedWitnessName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
        raise ValueError("unexpected witness")
    if summary["checkedStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected checked statement")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    for key in [
        "branchPauseStarted",
        "checkedWitnessCopyFrozen",
        "privateFreezePacket",
        "parkedNextBoundedIdentityBranchSelector",
        "parkedBoundedTrigFeasibility",
        "parkedHumanApprovedPublicCopyGate",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["freezeRowCount"] != 1:
        raise ValueError("expected one freeze row")
    if summary["guardCount"] != 2 or summary["sourceDerivedDomainObligationCount"] != 2:
        raise ValueError("probability-logit guard/domain counts drifted")
    if summary["sourceNegativeControlCount"] != 4 or summary["sourceBlockerCount"] != 4:
        raise ValueError("negative control/blocker counts drifted")
    if summary["d67SurfaceRowCount"] != 5:
        raise ValueError("D67 row count drift")
    if summary["frozenCaveatCount"] != 9:
        raise ValueError("unexpected caveat count")
    if summary["frozenBlockedPhraseCount"] != 12:
        raise ValueError("unexpected blocked phrase count")
    if summary["sourceD69RequiredCaveatCount"] != 9 or summary["sourceD69BlockedGlobalPhraseCount"] != 12:
        raise ValueError("D69 caveat/blocker counts drifted")
    if summary["sourceD69RowRequiredCaveatCount"] != 6 or summary["sourceD69RowBlockedPhraseCount"] != 10:
        raise ValueError("D69 row copy boundary counts drifted")
    if summary["runtimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("runtime guardrail drift")
    if summary["guardBoundaryStatus"] != "guarded_domain_boundary_required":
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
        "humanApprovedPublicCopyGateSelected",
        "humanApprovalRecorded",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["nextAction"] != "EML-D72 select the next private post-pause action without public promotion.":
        raise ValueError("unexpected next action")
    if summary["claimFlagsFrozenOnly"] is not True:
        raise ValueError("claim flags must remain freeze-only")
    for row in payload["freezeRows"]:
        if row["machlibName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
            raise ValueError("unexpected freeze row witness")
        if row["checkedStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
            raise ValueError("unexpected row checked statement")
        if row["guards"] != ["0 < p", "p < 1"]:
            raise ValueError("probability-logit freeze row must preserve both guards")
        if row["runtimeControl"] != "protected_log_and_log1p_remain_runtime_controls":
            raise ValueError("row runtime control drift")
        if row["publicPromotionAllowed"] is not False:
            raise ValueError("freeze row must not allow public promotion")
    for key in ["branch_pause_started", "checked_witness_copy_frozen", "private_freeze_packet"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"branch_pause_started", "checked_witness_copy_frozen", "private_freeze_packet"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_probability_logit_branch_pause_freeze_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_probability_logit_checked_witness_copy_frozen_public_copy_held_no_new_proof",
        "source": f"python/results/eml_d71_probability_logit_branch_pause_freeze_packet/eml_d71_probability_logit_branch_pause_freeze_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d71_probability_logit_branch_pause_freeze_packet_feed",
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
        "# EML-D71 Probability Logit Branch Pause Freeze Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D71 pauses the probability-logit branch and freezes the checked private witness copy boundary.",
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
    lines.extend(
        [
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
    result_path = out_dir / f"eml_d71_probability_logit_branch_pause_freeze_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d71_probability_logit_branch_pause_freeze_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d71_probability_logit_branch_pause_freeze_packet.json"
    feed_path = command_feed_dir / f"eml_d71_probability_logit_branch_pause_freeze_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d71_probability_logit_branch_pause_freeze_packet")
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
    print("EML_D71_PROBABILITY_LOGIT_BRANCH_PAUSE_FREEZE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
