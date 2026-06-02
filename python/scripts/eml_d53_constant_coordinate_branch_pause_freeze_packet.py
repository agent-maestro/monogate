#!/usr/bin/env python3
"""EML-D53 constant-coordinate branch pause and checked-witness delta freeze packet."""

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

from scripts import eml_d52_constant_coordinate_review_next_selector as d52  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_constant_coordinate_branch_pause_freeze_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D53_CONSTANT_COORDINATE_BRANCH_PAUSE_FREEZE_PACKET_PASS"

CLAIM_FLAGS = {
    "branch_pause_started": True,
    "checked_witness_delta_frozen": True,
    "private_freeze_packet": True,
    "next_action_selected": False,
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
    "EML-D53 pauses the constant-coordinate branch and freezes the checked private delta only; it does not approve or publish public copy.",
    "D53 records no new proof attempt, no MachLib edit, no Lean typecheck, no implementation work, and no runtime lowering change.",
    "D53 does not claim theorem discovery, log/exp replacement, runtime advantage, broad EML superiority, public readiness, course work, laptop intake, or electronics repo changes.",
]


def freeze_row(
    freeze_id: str,
    machlib_name: str,
    source_statement: str,
    checked_statement: str,
    local_spelling_note: str,
    existing_constant_witness_name: str,
    frozen_caveats: list[str],
    frozen_blocked_phrases: list[str],
    runtime_control: str,
) -> dict[str, Any]:
    return {
        "freezeId": freeze_id,
        "machlibName": machlib_name,
        "sourceStatement": source_statement,
        "checkedStatement": checked_statement,
        "localSpellingNote": local_spelling_note,
        "existingConstantWitnessName": existing_constant_witness_name,
        "duplicatesExistingConstantWitness": False,
        "guards": [],
        "frozenCaveats": frozen_caveats,
        "frozenBlockedPhrases": frozen_blocked_phrases,
        "runtimeControl": runtime_control,
        "freezeStatus": "private_checked_witness_delta_frozen",
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
    selector = d52.build_payload(atlas_gate_path)
    d52.validate_payload(selector)
    frozen_caveats = [
        "This delta freeze is private-only.",
        "The D47 source statement is eml 0 (exp 2) = -1.",
        "The checked Lean statement is eml 0 (exp (1 + 1)) = -1.",
        "MachLib.Basic currently provides Real numeral instances for 0 and 1 only.",
        "The witness is non-duplicate with the D10 constants bundle.",
        "The witness is one scoped MachLib theorem name, not a broad constants theory.",
        "Standard log/exp and arithmetic remain the semantic and runtime controls.",
        "Public Atlas and public education promotion remain false.",
    ]
    frozen_blocked_phrases = [
        "theorem discovery",
        "log/exp replacement",
        "runtime advantage",
        "public ready",
        "broad EML advantage",
        "compiler correctness",
        "formal equivalence",
        "full EML semantics",
        "all constants",
        "duplicate constants bundle",
    ]
    local_spelling_note = (
        "MachLib.Basic currently provides Real numeral instances for 0 and 1 only, "
        "so D47's exp 2 target is checked locally as exp (1 + 1)."
    )
    freeze_rows = [
        freeze_row(
            "constant_coordinate_zero_exp_two_checked_delta",
            selector["summary"]["selectedWitnessName"],
            selector["summary"]["sourceProposedStatement"],
            selector["summary"]["checkedLeanStatement"],
            local_spelling_note,
            selector["summary"]["existingConstantWitnessName"],
            frozen_caveats,
            frozen_blocked_phrases,
            selector["summary"]["runtimeLoweringControl"],
        )
    ]
    parked_options = [
        parked_option(
            "next_bounded_identity_branch_selector",
            "private_bounded_identity_lane",
            "parked_after_constant_coordinate_pause",
            "Available only through a later selector after the constant-coordinate checked delta is frozen.",
        ),
        parked_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "parked_after_constant_coordinate_pause",
            "Requires a separate guarded feasibility selector and negative controls.",
        ),
        parked_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "parked_requires_explicit_human_approval",
            "D53 freezes private copy boundaries but records no human approval for public use.",
        ),
    ]
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "selectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "sourceSelectedCandidateId": selector["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["sourceSelectedFamily"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "sourceProposedStatement": selector["summary"]["sourceProposedStatement"],
        "checkedLeanStatement": selector["summary"]["checkedLeanStatement"],
        "localSpellingUsesOnePlusOne": selector["summary"]["localSpellingUsesOnePlusOne"],
        "existingConstantWitnessName": selector["summary"]["existingConstantWitnessName"],
        "duplicatesExistingConstantWitness": selector["summary"]["duplicatesExistingConstantWitness"],
        "branchPauseStarted": True,
        "checkedWitnessDeltaFrozen": True,
        "privateFreezePacket": True,
        "freezeRowCount": len(freeze_rows),
        "guardCount": 0,
        "frozenCaveatCount": len(frozen_caveats),
        "frozenBlockedPhraseCount": len(frozen_blocked_phrases),
        "sourceD51RequiredCaveatCount": selector["summary"]["d51RequiredCaveatCount"],
        "sourceD51BlockedGlobalPhraseCount": selector["summary"]["d51BlockedGlobalPhraseCount"],
        "publicHoldPreserved": selector["summary"]["publicHoldPreserved"],
        "runtimeBoundaryPreserved": selector["summary"]["runtimeBoundaryPreserved"],
        "runtimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
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
        "nextAction": "EML-D54 select the next private post-pause action without public promotion.",
        "claimFlagsFrozenOnly": all(
            CLAIM_FLAGS[key] is True
            for key in ["branch_pause_started", "checked_witness_delta_frozen", "private_freeze_packet"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"branch_pause_started", "checked_witness_delta_frozen", "private_freeze_packet"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_constant_coordinate_branch_pause_freeze_packet_v0",
        "artifactId": "eml-d53-constant-coordinate-branch-pause-freeze-packet",
        "status": STATUS,
        "decision": "pause_constant_coordinate_branch_and_freeze_checked_witness_delta",
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
    if payload["sourceSelector"] != "eml-d52-constant-coordinate-review-next-selector":
        raise ValueError("D53 must consume D52")
    if summary["selectedOptionId"] != "constant_coordinate_branch_pause_freeze_packet":
        raise ValueError("unexpected D52 selected option")
    if summary["selectedNextArtifact"] != "EML-D53 constant-coordinate branch pause and checked-witness delta freeze packet":
        raise ValueError("unexpected D52 next artifact")
    if summary["sourceSelectedCandidateId"] != "zero_coordinate_exp_two_boundary":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "constant_coordinate_refresh":
        raise ValueError("unexpected family")
    if summary["selectedWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("unexpected witness")
    if summary["sourceProposedStatement"] != "eml 0 (exp 2) = -1":
        raise ValueError("unexpected source statement")
    if summary["checkedLeanStatement"] != "eml 0 (exp (1 + 1)) = -1":
        raise ValueError("unexpected checked Lean statement")
    if summary["localSpellingUsesOnePlusOne"] is not True:
        raise ValueError("local spelling note must remain frozen")
    if summary["existingConstantWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("unexpected existing constants witness")
    if summary["duplicatesExistingConstantWitness"] is not False:
        raise ValueError("non-duplicate boundary drift")
    for key in [
        "branchPauseStarted",
        "checkedWitnessDeltaFrozen",
        "privateFreezePacket",
        "publicHoldPreserved",
        "runtimeBoundaryPreserved",
        "parkedNextBoundedIdentityBranchSelector",
        "parkedBoundedTrigFeasibility",
        "parkedHumanApprovedPublicCopyGate",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["freezeRowCount"] != 1:
        raise ValueError("expected one freeze row")
    if summary["guardCount"] != 0:
        raise ValueError("constant-coordinate witness should not add guards")
    if summary["frozenCaveatCount"] != 8:
        raise ValueError("unexpected caveat count")
    if summary["frozenBlockedPhraseCount"] != 10:
        raise ValueError("unexpected blocked phrase count")
    if summary["sourceD51RequiredCaveatCount"] != 8 or summary["sourceD51BlockedGlobalPhraseCount"] != 10:
        raise ValueError("D51 caveat/blocker counts drifted")
    if summary["runtimeLoweringControl"] != "standard_log_exp_and_arithmetic_remain_runtime_controls":
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
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
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
    if summary["nextAction"] != "EML-D54 select the next private post-pause action without public promotion.":
        raise ValueError("unexpected next action")
    if summary["claimFlagsFrozenOnly"] is not True:
        raise ValueError("claim flags must remain freeze-only")
    for row in payload["freezeRows"]:
        if row["machlibName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
            raise ValueError("unexpected freeze row witness")
        if row["sourceStatement"] != "eml 0 (exp 2) = -1":
            raise ValueError("unexpected row source statement")
        if row["checkedStatement"] != "eml 0 (exp (1 + 1)) = -1":
            raise ValueError("unexpected row checked statement")
        if row["guards"] != []:
            raise ValueError("constant-coordinate freeze row should have no guards")
        if row["existingConstantWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
            raise ValueError("row non-duplicate boundary drift")
        if row["duplicatesExistingConstantWitness"] is not False:
            raise ValueError("row must remain non-duplicate")
        if row["runtimeControl"] != "standard_log_exp_and_arithmetic_remain_runtime_controls":
            raise ValueError("row runtime control drift")
        if row["publicPromotionAllowed"] is not False:
            raise ValueError("freeze row must not allow public promotion")
    for key in ["branch_pause_started", "checked_witness_delta_frozen", "private_freeze_packet"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"branch_pause_started", "checked_witness_delta_frozen", "private_freeze_packet"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_constant_coordinate_branch_pause_freeze_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_constant_coordinate_checked_witness_delta_frozen_public_copy_held_no_new_proof",
        "source": f"python/results/eml_d53_constant_coordinate_branch_pause_freeze_packet/eml_d53_constant_coordinate_branch_pause_freeze_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d53_constant_coordinate_branch_pause_freeze_packet_feed",
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
        "# EML-D53 Constant-Coordinate Branch Pause Freeze Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D53 pauses the constant-coordinate branch and freezes the checked private witness delta.",
        "",
        "| Freeze row | Witness | Source statement | Checked Lean statement | Runtime control |",
        "|---|---|---|---|---|",
    ]
    for row in payload["freezeRows"]:
        lines.append(
            f"| `{row['freezeId']}` | `{row['machlibName']}` | `{row['sourceStatement']}` | `{row['checkedStatement']}` | {row['runtimeControl']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- branch pause started: `{payload['summary']['branchPauseStarted']}`",
            f"- checked witness delta frozen: `{payload['summary']['checkedWitnessDeltaFrozen']}`",
            f"- local spelling uses one plus one: `{payload['summary']['localSpellingUsesOnePlusOne']}`",
            f"- non-duplicate boundary: `{payload['summary']['existingConstantWitnessName']}`",
            f"- public hold preserved: `{payload['summary']['publicHoldPreserved']}`",
            f"- runtime boundary preserved: `{payload['summary']['runtimeBoundaryPreserved']}`",
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
    result_path = out_dir / f"eml_d53_constant_coordinate_branch_pause_freeze_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d53_constant_coordinate_branch_pause_freeze_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d53_constant_coordinate_branch_pause_freeze_packet.json"
    feed_path = command_feed_dir / f"eml_d53_constant_coordinate_branch_pause_freeze_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d53_constant_coordinate_branch_pause_freeze_packet")
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
    print("EML_D53_CONSTANT_COORDINATE_BRANCH_PAUSE_FREEZE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
