#!/usr/bin/env python3
"""EML-D45 positive log-exp branch pause and checked-witness freeze packet."""

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

from scripts import eml_d44_positive_log_exp_review_next_selector as d44  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_positive_log_exp_branch_pause_freeze_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D45_POSITIVE_LOG_EXP_BRANCH_PAUSE_FREEZE_PACKET_PASS"

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
    "EML-D45 pauses the positive log-exp branch and freezes the checked private delta only; it does not approve or publish public copy.",
    "D45 records no new proof attempt, no MachLib edit, no Lean typecheck, no implementation work, and no runtime lowering change.",
    "D45 does not claim theorem discovery, log/exp replacement, runtime advantage, broad EML superiority, public readiness, course work, laptop intake, or electronics repo changes.",
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
    selector = d44.build_payload(atlas_gate_path)
    d44.validate_payload(selector)
    frozen_caveats = [
        "Always name the 0 < x guard.",
        "Say positive-domain or positive real input.",
        "Describe this as one scoped checked witness, not theorem discovery.",
        "Keep standard log/exp as the semantic and runtime controls.",
        "Keep public copy held for human review.",
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
    ]
    freeze_rows = [
        freeze_row(
            "positive_log_exp_roundtrip_checked_delta",
            "MachLib.Real.positive_log_exp_roundtrip_witness",
            "0 < x -> exp (log x) = x",
            ["0 < x"],
            frozen_caveats,
            frozen_blocked_phrases,
            "standard_log_exp_remains_runtime_control",
        )
    ]
    parked_options = [
        parked_option(
            "constant_coordinate_refresh_selector",
            "private_bounded_identity_lane",
            "parked_after_positive_log_exp_pause",
            "Available only through a later selector after the checked positive log-exp delta is frozen.",
        ),
        parked_option(
            "bounded_trig_identity_feasibility_selector",
            "private_frontier_probe_lane",
            "parked_after_positive_log_exp_pause",
            "Requires a separate guarded feasibility selector and negative controls.",
        ),
        parked_option(
            "human_approved_public_copy_gate",
            "public_copy_gate_lane",
            "parked_requires_explicit_human_approval",
            "D45 freezes private copy boundaries but records no human approval for public use.",
        ),
    ]
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "sourceSelectedCandidateId": selector["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["sourceSelectedFamily"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "branchPauseStarted": True,
        "checkedWitnessDeltaFrozen": True,
        "privateFreezePacket": True,
        "freezeRowCount": len(freeze_rows),
        "guardCount": 1,
        "frozenCaveatCount": len(frozen_caveats),
        "frozenBlockedPhraseCount": len(frozen_blocked_phrases),
        "positiveDomainGuardRequired": selector["summary"]["positiveDomainGuardRequired"],
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
        "humanApprovedPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "parkedConstantCoordinateRefresh": True,
        "parkedBoundedTrigFeasibility": True,
        "parkedHumanApprovedPublicCopyGate": True,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D46 select the next private post-pause action without public promotion.",
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
        "packetType": "eml_positive_log_exp_branch_pause_freeze_packet_v0",
        "artifactId": "eml-d45-positive-log-exp-branch-pause-freeze-packet",
        "status": STATUS,
        "decision": "pause_positive_log_exp_branch_and_freeze_checked_witness_delta",
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
    if payload["sourceSelector"] != "eml-d44-positive-log-exp-review-next-selector":
        raise ValueError("D45 must consume D44")
    if summary["selectedOptionId"] != "positive_log_exp_branch_pause_freeze_packet":
        raise ValueError("unexpected D44 selected option")
    if summary["sourceSelectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "positive_domain_log_exp_roundtrip":
        raise ValueError("unexpected family")
    if summary["selectedWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected witness")
    for key in [
        "branchPauseStarted",
        "checkedWitnessDeltaFrozen",
        "privateFreezePacket",
        "positiveDomainGuardRequired",
        "publicHoldPreserved",
        "runtimeBoundaryPreserved",
        "parkedConstantCoordinateRefresh",
        "parkedBoundedTrigFeasibility",
        "parkedHumanApprovedPublicCopyGate",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["freezeRowCount"] != 1:
        raise ValueError("expected one freeze row")
    if summary["guardCount"] != 1:
        raise ValueError("guard count drift")
    if summary["frozenCaveatCount"] != 5:
        raise ValueError("unexpected caveat count")
    if summary["frozenBlockedPhraseCount"] != 8:
        raise ValueError("unexpected blocked phrase count")
    if summary["runtimeLoweringControl"] != "standard_log_exp_remains_runtime_control":
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
        "humanApprovedPublicCopyGateSelected",
        "humanApprovalRecorded",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["nextAction"] != "EML-D46 select the next private post-pause action without public promotion.":
        raise ValueError("unexpected next action")
    if summary["claimFlagsFrozenOnly"] is not True:
        raise ValueError("claim flags must remain freeze-only")
    for row in payload["freezeRows"]:
        if row["machlibName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
            raise ValueError("unexpected freeze row witness")
        if row["checkedStatement"] != "0 < x -> exp (log x) = x":
            raise ValueError("unexpected checked statement")
        if row["guards"] != ["0 < x"]:
            raise ValueError("guard must be frozen exactly")
        if row["runtimeControl"] != "standard_log_exp_remains_runtime_control":
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
        "artifactType": "eml_positive_log_exp_branch_pause_freeze_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_checked_witness_delta_frozen_public_copy_held_no_new_proof",
        "source": f"python/results/eml_d45_positive_log_exp_branch_pause_freeze_packet/eml_d45_positive_log_exp_branch_pause_freeze_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d45_positive_log_exp_branch_pause_freeze_packet_feed",
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
        "# EML-D45 Positive Log-Exp Branch Pause Freeze Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D45 pauses the positive log-exp branch and freezes the checked private witness delta.",
        "",
        "| Freeze row | Witness | Statement | Runtime control |",
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
            f"- checked witness delta frozen: `{payload['summary']['checkedWitnessDeltaFrozen']}`",
            f"- positive-domain guard required: `{payload['summary']['positiveDomainGuardRequired']}`",
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
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d45_positive_log_exp_branch_pause_freeze_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d45_positive_log_exp_branch_pause_freeze_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d45_positive_log_exp_branch_pause_freeze_packet.json"
    feed_path = command_feed_dir / f"eml_d45_positive_log_exp_branch_pause_freeze_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d45_positive_log_exp_branch_pause_freeze_packet")
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
    print("EML_D45_POSITIVE_LOG_EXP_BRANCH_PAUSE_FREEZE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
