#!/usr/bin/env python3
"""ACT-A15 reviewer promotion hold feed guard packet."""

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

from scripts import act_a14_reviewer_promotion_hold_snapshot as a14  # noqa: E402

DATE = "2026-06-03"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_reviewer_promotion_hold_feed_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A15_REVIEWER_PROMOTION_HOLD_FEED_GUARD_PASS"

EXPECTED_SOURCE_FEED_ID = "act_a14_reviewer_promotion_hold_snapshot_feed"
EXPECTED_SOURCE_STATUS = "ACT_A14_REVIEWER_PROMOTION_HOLD_SNAPSHOT_PASS"
EXPECTED_SOURCE_DECISION = "record_reviewer_promotion_hold_snapshot_no_artifact_acceptance_no_public_promotion"

ALLOWED_TRUE_SOURCE_CLAIM_FLAGS = {
    "reviewer_promotion_hold_snapshot_recorded",
    "act_a13_reviewer_promotion_hold_gate_consumed",
    "baseline_snapshot_recorded",
    "observed_snapshot_recorded",
    "snapshot_checks_recorded",
    "snapshot_checks_passed",
}

BLOCKED_SOURCE_CLAIM_FLAGS = {
    "reviewer_decision_recorded",
    "concrete_artifact_accepted",
    "production_validator_implemented",
    "validator_soundness_proved",
    "soundness_proved",
    "full_galois_connection_claim",
    "abstract_interpretation_soundness_proved",
    "visualization_started",
    "public_surface_updated",
    "public_copy_approved",
    "runtime_lowering_changed",
    "machlib_file_changed",
    "lean_typecheck_performed",
    "proof_attempt_started",
    "candidate_proved",
    "compiler_correctness_claim",
    "formal_equivalence_claim",
    "full_eml_semantics_claim",
    "theorem_discovery_claim",
    "general_eml_superiority_claim",
    "runtime_performance_claim",
    "electronics_repo_touched",
    "laptop_artifact_consumed",
    "renderer_implemented",
    "renderer_executed",
    "public_ready",
}

CLAIM_FLAGS = {
    "reviewer_promotion_hold_feed_guard_recorded": True,
    "act_a14_reviewer_promotion_hold_snapshot_consumed": True,
    "source_feed_rebuilt": True,
    "feed_guard_rows_recorded": True,
    "feed_guard_checks_recorded": True,
    "feed_guard_checks_passed": True,
    "reviewer_decision_recorded": False,
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
    "ACT-A15 records a private reviewer promotion hold feed guard only; it does not promote ACT artifacts.",
    "ACT-A15 rebuilds and guards the ACT-A14 command feed without recording reviewer acceptance, accepting a concrete artifact, implementing a production validator, or proving validator soundness.",
    "ACT-A15 does not prove a Galois connection, prove abstract interpretation soundness, update public surfaces, change runtime behavior, edit MachLib, consume laptop/electronics artifacts, or approve public copy.",
]


def feed_guard_rows(source_feed: dict[str, Any]) -> list[dict[str, Any]]:
    true_flags = sorted(key for key, value in source_feed["claimFlags"].items() if value is True)
    blocked_false_flags = sorted(
        key for key in BLOCKED_SOURCE_CLAIM_FLAGS if source_feed["claimFlags"].get(key) is False
    )
    return [
        {
            "guardRowId": "act_a15_feed_guard:feed_id",
            "observed": source_feed["feedId"],
            "expected": EXPECTED_SOURCE_FEED_ID,
            "status": "pass",
        },
        {
            "guardRowId": "act_a15_feed_guard:status",
            "observed": source_feed["status"],
            "expected": EXPECTED_SOURCE_STATUS,
            "status": "pass",
        },
        {
            "guardRowId": "act_a15_feed_guard:decision",
            "observed": source_feed["decision"],
            "expected": EXPECTED_SOURCE_DECISION,
            "status": "pass",
        },
        {
            "guardRowId": "act_a15_feed_guard:next_action_is_private",
            "observed": "without public promotion" in source_feed["nextAction"],
            "expected": True,
            "status": "pass",
        },
        {
            "guardRowId": "act_a15_feed_guard:allowed_true_claim_flags",
            "observed": true_flags,
            "expected": sorted(ALLOWED_TRUE_SOURCE_CLAIM_FLAGS),
            "status": "pass",
        },
        {
            "guardRowId": "act_a15_feed_guard:blocked_claim_flags_false",
            "observed": blocked_false_flags,
            "expected": sorted(BLOCKED_SOURCE_CLAIM_FLAGS),
            "status": "pass",
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a14.build_payload(atlas_gate_path)
    a14.validate_payload(source)
    source_feed = a14.build_feed(source)
    rows = feed_guard_rows(source_feed)
    for row in rows:
        if row["observed"] != row["expected"]:
            raise ValueError(f"promotion hold feed guard row failed: {row['guardRowId']}")
    summary = {
        "sourceReviewerPromotionHoldSnapshot": source["artifactId"],
        "sourceFeedId": source_feed["feedId"],
        "sourceFeedStatus": source_feed["status"],
        "sourceFeedDecision": source_feed["decision"],
        "sourceFeedNextAction": source_feed["nextAction"],
        "sourceClaimFlagCount": len(source_feed["claimFlags"]),
        "allowedTrueSourceClaimFlagCount": len(ALLOWED_TRUE_SOURCE_CLAIM_FLAGS),
        "blockedSourceClaimFlagCount": len(BLOCKED_SOURCE_CLAIM_FLAGS),
        "feedGuardRowCount": len(rows),
        "feedGuardPassCount": sum(1 for row in rows if row["status"] == "pass"),
        "reviewerPromotionHoldFeedGuardRecorded": True,
        "actA14ReviewerPromotionHoldSnapshotConsumed": True,
        "sourceFeedRebuilt": True,
        "feedGuardRowsRecorded": True,
        "feedGuardChecksRecorded": True,
        "feedGuardChecksPassed": True,
        "reviewerDecisionRecorded": False,
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
        "nextAction": "EML-D81 post-log1p-shifted-pause selector or ACT-A16 reviewer promotion hold final handoff without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "reviewer_promotion_hold_feed_guard_recorded",
                "act_a14_reviewer_promotion_hold_snapshot_consumed",
                "source_feed_rebuilt",
                "feed_guard_rows_recorded",
                "feed_guard_checks_recorded",
                "feed_guard_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "reviewer_promotion_hold_feed_guard_recorded",
                "act_a14_reviewer_promotion_hold_snapshot_consumed",
                "source_feed_rebuilt",
                "feed_guard_rows_recorded",
                "feed_guard_checks_recorded",
                "feed_guard_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_reviewer_promotion_hold_feed_guard_v0",
        "artifactId": "act-a15-reviewer-promotion-hold-feed-guard",
        "status": STATUS,
        "decision": "record_reviewer_promotion_hold_feed_guard_no_artifact_acceptance_no_public_promotion",
        "date": DATE,
        "sourceReviewerPromotionHoldSnapshot": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "sourceFeed": source_feed,
        "feedGuardRows": rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceReviewerPromotionHoldSnapshot"] != "act-a14-reviewer-promotion-hold-snapshot":
        raise ValueError("ACT-A15 must consume ACT-A14")
    if summary["sourceFeedId"] != EXPECTED_SOURCE_FEED_ID:
        raise ValueError("unexpected source feed id")
    if summary["sourceFeedStatus"] != EXPECTED_SOURCE_STATUS:
        raise ValueError("unexpected source feed status")
    if summary["sourceFeedDecision"] != EXPECTED_SOURCE_DECISION:
        raise ValueError("unexpected source feed decision")
    if summary["feedGuardRowCount"] != 6 or summary["feedGuardPassCount"] != 6:
        raise ValueError("unexpected feed guard count")
    if summary["sourceClaimFlagCount"] != len(a14.CLAIM_FLAGS):
        raise ValueError("unexpected source claim flag count")
    if summary["allowedTrueSourceClaimFlagCount"] != 6:
        raise ValueError("unexpected allowed true claim flag count")
    if summary["blockedSourceClaimFlagCount"] != len(BLOCKED_SOURCE_CLAIM_FLAGS):
        raise ValueError("unexpected blocked claim flag count")
    for row in payload["feedGuardRows"]:
        if row["status"] != "pass" or row["observed"] != row["expected"]:
            raise ValueError("promotion hold feed guard row must pass exactly")
    for key in [
        "reviewerPromotionHoldFeedGuardRecorded",
        "actA14ReviewerPromotionHoldSnapshotConsumed",
        "sourceFeedRebuilt",
        "feedGuardRowsRecorded",
        "feedGuardChecksRecorded",
        "feedGuardChecksPassed",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "reviewerDecisionRecorded",
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
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "alpha_gamma_reviewer_promotion_hold_feed_guard",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_reviewer_promotion_hold_feed_guard_no_artifact_acceptance_no_public_promotion",
        "source": f"python/results/act_a15_reviewer_promotion_hold_feed_guard/act_a15_reviewer_promotion_hold_feed_guard_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a15_reviewer_promotion_hold_feed_guard_feed",
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
        "# ACT-A15 Reviewer Promotion Hold Feed Guard",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A15 records a private reviewer promotion hold feed guard without accepting artifacts or promoting public claims.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| source claim flags | `{payload['summary']['sourceClaimFlagCount']}` |",
        f"| allowed true source flags | `{payload['summary']['allowedTrueSourceClaimFlagCount']}` |",
        f"| blocked source flags | `{payload['summary']['blockedSourceClaimFlagCount']}` |",
        f"| feed guard rows | `{payload['summary']['feedGuardRowCount']}` |",
        f"| feed guard passes | `{payload['summary']['feedGuardPassCount']}` |",
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
    result_path = out_dir / f"act_a15_reviewer_promotion_hold_feed_guard_{STAMP}.json"
    report_path = report_dir / f"act_a15_reviewer_promotion_hold_feed_guard_{STAMP}.md"
    evidence_path = evidence_dir / "act_a15_reviewer_promotion_hold_feed_guard.json"
    feed_path = command_feed_dir / f"act_a15_reviewer_promotion_hold_feed_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a15_reviewer_promotion_hold_feed_guard")
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
    print("ACT_A15_REVIEWER_PROMOTION_HOLD_FEED_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
