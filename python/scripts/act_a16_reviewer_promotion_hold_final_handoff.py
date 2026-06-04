#!/usr/bin/env python3
"""ACT-A16 reviewer promotion hold final handoff packet."""

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

from scripts import act_a15_reviewer_promotion_hold_feed_guard as a15  # noqa: E402

DATE = "2026-06-04"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_reviewer_promotion_hold_final_handoff.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A16_REVIEWER_PROMOTION_HOLD_FINAL_HANDOFF_PASS"

CLAIM_FLAGS = {
    "reviewer_promotion_hold_final_handoff_recorded": True,
    "act_a15_reviewer_promotion_hold_feed_guard_consumed": True,
    "source_feed_rebuilt": True,
    "promotion_hold_chain_summary_recorded": True,
    "private_handoff_checklist_recorded": True,
    "private_reviewer_handoff_ready": True,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "concrete_artifact_accepted": False,
    "production_validator_implemented": False,
    "validator_soundness_proved": False,
    "soundness_proved": False,
    "full_galois_connection_claim": False,
    "abstract_interpretation_soundness_proved": False,
    "visualization_started": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "runtime_lowering_changed": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "proof_attempt_started": False,
    "candidate_proved": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "runtime_performance_claim": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "renderer_implemented": False,
    "renderer_executed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "ACT-A16 records a private reviewer promotion hold final handoff only; it does not promote ACT artifacts.",
    "ACT-A16 consumes ACT-A15 without recording reviewer approval or rejection, accepting a concrete artifact, implementing a production validator, or proving validator soundness.",
    "ACT-A16 does not prove a Galois connection, prove abstract interpretation soundness, update public surfaces, change runtime behavior, edit MachLib, consume laptop/electronics artifacts, or approve public copy.",
]

BLOCKED_STATEMENTS = [
    "A reviewer has accepted an ACT concrete artifact for promotion.",
    "A reviewer has approved ACT promotion.",
    "A reviewer has rejected ACT promotion.",
    "The ACT alpha/gamma validator is production-ready.",
    "The ACT validator is sound.",
    "A Galois connection or abstract interpretation soundness theorem has been proved.",
    "ACT artifacts are public-ready.",
    "Laptop or electronics artifacts have been consumed by this handoff.",
    "ACT promotion may update public copy or public surfaces.",
]


def build_chain_summary(source_payload: dict[str, Any], source_feed: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "phase": "ACT-A13",
            "artifactId": "act-a13-reviewer-promotion-hold-gate",
            "role": "records private reviewer promotion hold gate",
            "recordedCounts": {
                "promotionHoldGates": 9,
                "promotionHoldChecks": 9,
                "promotionHoldPasses": 9,
                "blockedStatements": 6,
            },
            "promotionAllowed": False,
        },
        {
            "phase": "ACT-A14",
            "artifactId": "act-a14-reviewer-promotion-hold-snapshot",
            "role": "records private reviewer promotion hold snapshot",
            "recordedCounts": {
                "snapshotChecks": 7,
                "snapshotPasses": 7,
            },
            "promotionAllowed": False,
        },
        {
            "phase": "ACT-A15",
            "artifactId": source_feed["feedId"],
            "role": "records private reviewer promotion hold feed guard",
            "recordedCounts": {
                "feedGuardRows": source_payload["summary"]["feedGuardRowCount"],
                "feedGuardPasses": source_payload["summary"]["feedGuardPassCount"],
                "allowedTrueSourceClaimFlags": source_payload["summary"]["allowedTrueSourceClaimFlagCount"],
                "blockedFalseSourceClaimFlags": source_payload["summary"]["blockedSourceClaimFlagCount"],
            },
            "promotionAllowed": False,
        },
    ]


def build_handoff_packet() -> dict[str, Any]:
    return {
        "handoffStatus": "ready_for_private_review",
        "reviewerDecisionStatus": "not_recorded",
        "reviewSurface": "private_only",
        "implementationStatus": "held_pending_reviewer_response",
        "chainRange": "ACT-A13-A15",
        "allowedPrivateOutcomes": [
            "accept_private_promotion_hold_chain",
            "request_copy_tightening",
            "request_additional_negative_claim_flags",
            "request_production_validator_design_before_acceptance",
            "request_formal_soundness_plan_before_acceptance",
            "request_public_copy_gate_hold",
            "request_reviewer_hold",
        ],
        "reviewerMustInspect": [
            "ACT-A13 promotion hold gates and blocked promotion statements.",
            "ACT-A14 baseline and observed promotion hold snapshot checks.",
            "ACT-A15 command feed guard rows and claim-flag boundary.",
            "No reviewer decision, artifact acceptance, public copy, or public surface update is recorded.",
            "No production validator, validator soundness, Galois connection, or abstract interpretation soundness is claimed.",
        ],
        "pivotCriteria": [
            "A real reviewer response is recorded before any promotion posture changes.",
            "A separate implementation phase exists before production validator work.",
            "A separate proof phase exists before soundness or Galois-connection claims.",
            "A separate public copy gate exists before public surfaces change.",
        ],
    }


def build_handoff_checklist() -> list[dict[str, str]]:
    return [
        {"id": "act_a13_hold_gate_reviewed", "status": "ready"},
        {"id": "act_a14_hold_snapshot_reviewed", "status": "ready"},
        {"id": "act_a15_feed_guard_reviewed", "status": "ready"},
        {"id": "promotion_allowed_false_reviewed", "status": "ready"},
        {"id": "reviewer_decision_not_recorded_reviewed", "status": "ready"},
        {"id": "public_promotion_blocked_reviewed", "status": "ready"},
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a15.build_payload(atlas_gate_path)
    a15.validate_payload(source)
    source_feed = a15.build_feed(source)
    chain = build_chain_summary(source, source_feed)
    handoff = build_handoff_packet()
    checklist = build_handoff_checklist()
    summary = {
        "sourceReviewerPromotionHoldFeedGuard": source["artifactId"],
        "sourceFeedId": source_feed["feedId"],
        "sourceFeedStatus": source_feed["status"],
        "sourceFeedDecision": source_feed["decision"],
        "sourceFeedNextAction": source_feed["nextAction"],
        "sourceFeedGuardRowCount": source["summary"]["feedGuardRowCount"],
        "sourceFeedGuardPassCount": source["summary"]["feedGuardPassCount"],
        "sourceAllowedTrueClaimFlagCount": source["summary"]["allowedTrueSourceClaimFlagCount"],
        "sourceBlockedClaimFlagCount": source["summary"]["blockedSourceClaimFlagCount"],
        "chainRange": handoff["chainRange"],
        "chainEntryCount": len(chain),
        "handoffChecklistCount": len(checklist),
        "allowedPrivateOutcomeCount": len(handoff["allowedPrivateOutcomes"]),
        "reviewerMustInspectCount": len(handoff["reviewerMustInspect"]),
        "pivotCriteriaCount": len(handoff["pivotCriteria"]),
        "blockedStatementCount": len(BLOCKED_STATEMENTS),
        "reviewerPromotionHoldFinalHandoffRecorded": True,
        "actA15ReviewerPromotionHoldFeedGuardConsumed": True,
        "sourceFeedRebuilt": True,
        "promotionHoldChainSummaryRecorded": True,
        "privateHandoffChecklistRecorded": True,
        "privateReviewerHandoffReady": True,
        "promotionAllowed": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "reviewerDecisionStatus": handoff["reviewerDecisionStatus"],
        "concreteArtifactAccepted": False,
        "productionValidatorImplemented": False,
        "validatorSoundnessProved": False,
        "soundnessProved": False,
        "fullGaloisConnectionClaim": False,
        "abstractInterpretationSoundnessProved": False,
        "visualizationStarted": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "runtimeLoweringChanged": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "proofAttemptStarted": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "rendererImplemented": False,
        "rendererExecuted": False,
        "publicReady": False,
        "nextAction": "EML-D81 post-log1p-shifted-pause selector or private reviewer response intake without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "reviewer_promotion_hold_final_handoff_recorded",
                "act_a15_reviewer_promotion_hold_feed_guard_consumed",
                "source_feed_rebuilt",
                "promotion_hold_chain_summary_recorded",
                "private_handoff_checklist_recorded",
                "private_reviewer_handoff_ready",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "reviewer_promotion_hold_final_handoff_recorded",
                "act_a15_reviewer_promotion_hold_feed_guard_consumed",
                "source_feed_rebuilt",
                "promotion_hold_chain_summary_recorded",
                "private_handoff_checklist_recorded",
                "private_reviewer_handoff_ready",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_reviewer_promotion_hold_final_handoff_v0",
        "artifactId": "act-a16-reviewer-promotion-hold-final-handoff",
        "status": STATUS,
        "decision": "record_reviewer_promotion_hold_final_handoff_no_artifact_acceptance_no_public_promotion",
        "date": DATE,
        "sourceReviewerPromotionHoldFeedGuard": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "sourceFeed": source_feed,
        "promotionHoldChain": chain,
        "reviewerHandoffPacket": handoff,
        "handoffChecklist": checklist,
        "blockedStatements": list(BLOCKED_STATEMENTS),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceReviewerPromotionHoldFeedGuard"] != "act-a15-reviewer-promotion-hold-feed-guard":
        raise ValueError("ACT-A16 must consume ACT-A15")
    if summary["sourceFeedId"] != "act_a15_reviewer_promotion_hold_feed_guard_feed":
        raise ValueError("unexpected source feed id")
    if summary["sourceFeedStatus"] != "ACT_A15_REVIEWER_PROMOTION_HOLD_FEED_GUARD_PASS":
        raise ValueError("unexpected source feed status")
    if summary["sourceFeedDecision"] != "record_reviewer_promotion_hold_feed_guard_no_artifact_acceptance_no_public_promotion":
        raise ValueError("unexpected source feed decision")
    if summary["sourceFeedGuardRowCount"] != 6 or summary["sourceFeedGuardPassCount"] != 6:
        raise ValueError("unexpected source feed guard count")
    if summary["sourceAllowedTrueClaimFlagCount"] != 6 or summary["sourceBlockedClaimFlagCount"] != 26:
        raise ValueError("unexpected source claim flag boundary count")
    if summary["chainRange"] != "ACT-A13-A15" or summary["chainEntryCount"] != 3:
        raise ValueError("unexpected chain summary")
    if summary["handoffChecklistCount"] != 6:
        raise ValueError("unexpected handoff checklist count")
    if summary["allowedPrivateOutcomeCount"] != 7:
        raise ValueError("unexpected allowed outcome count")
    if summary["reviewerMustInspectCount"] != 5:
        raise ValueError("unexpected reviewer inspection count")
    if summary["pivotCriteriaCount"] != 4:
        raise ValueError("unexpected pivot criteria count")
    if summary["blockedStatementCount"] != len(BLOCKED_STATEMENTS):
        raise ValueError("unexpected blocked statement count")
    for key in [
        "reviewerPromotionHoldFinalHandoffRecorded",
        "actA15ReviewerPromotionHoldFeedGuardConsumed",
        "sourceFeedRebuilt",
        "promotionHoldChainSummaryRecorded",
        "privateHandoffChecklistRecorded",
        "privateReviewerHandoffReady",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "promotionAllowed",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "concreteArtifactAccepted",
        "productionValidatorImplemented",
        "validatorSoundnessProved",
        "soundnessProved",
        "fullGaloisConnectionClaim",
        "abstractInterpretationSoundnessProved",
        "visualizationStarted",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "runtimeLoweringChanged",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "proofAttemptStarted",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "rendererImplemented",
        "rendererExecuted",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["reviewerDecisionStatus"] != "not_recorded":
        raise ValueError("reviewer decision must remain unrecorded")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for item in payload["promotionHoldChain"]:
        if item["promotionAllowed"] is not False:
            raise ValueError("all chain entries must keep promotion held")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "alpha_gamma_reviewer_promotion_hold_final_handoff",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_reviewer_promotion_hold_final_handoff_no_artifact_acceptance_no_public_promotion",
        "source": f"python/results/act_a16_reviewer_promotion_hold_final_handoff/act_a16_reviewer_promotion_hold_final_handoff_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a16_reviewer_promotion_hold_final_handoff_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# ACT-A16 Reviewer Promotion Hold Final Handoff",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A16 records a private reviewer promotion hold final handoff without accepting artifacts or promoting public claims.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| chain entries | `{payload['summary']['chainEntryCount']}` |",
        f"| handoff checklist rows | `{payload['summary']['handoffChecklistCount']}` |",
        f"| allowed private outcomes | `{payload['summary']['allowedPrivateOutcomeCount']}` |",
        f"| reviewer inspection items | `{payload['summary']['reviewerMustInspectCount']}` |",
        f"| blocked statements | `{payload['summary']['blockedStatementCount']}` |",
        "",
        "## Non-Claims",
        "",
    ]
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
    result_path = out_dir / f"act_a16_reviewer_promotion_hold_final_handoff_{STAMP}.json"
    report_path = report_dir / f"act_a16_reviewer_promotion_hold_final_handoff_{STAMP}.md"
    evidence_path = evidence_dir / "act_a16_reviewer_promotion_hold_final_handoff.json"
    feed_path = command_feed_dir / f"act_a16_reviewer_promotion_hold_final_handoff_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a16_reviewer_promotion_hold_final_handoff")
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
    print("ACT_A16_REVIEWER_PROMOTION_HOLD_FINAL_HANDOFF_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
