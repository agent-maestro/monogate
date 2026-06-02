#!/usr/bin/env python3
"""ACT-A9 reviewer report feed guard packet."""

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

from scripts import act_a8_reviewer_report_snapshot as a8  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_reviewer_report_feed_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A9_REVIEWER_REPORT_FEED_GUARD_PASS"

EXPECTED_SOURCE_FEED_ID = "act_a8_reviewer_report_snapshot_feed"
EXPECTED_SOURCE_STATUS = "ACT_A8_REVIEWER_REPORT_SNAPSHOT_PASS"
EXPECTED_SOURCE_DECISION = "record_reviewer_report_snapshot_no_production_validator_no_soundness_claim"

ALLOWED_TRUE_SOURCE_CLAIM_FLAGS = {
    "reviewer_report_snapshot_recorded",
    "act_a7_reporting_contract_consumed",
    "baseline_snapshot_recorded",
    "observed_snapshot_recorded",
    "snapshot_checks_recorded",
    "snapshot_checks_passed",
}

BLOCKED_SOURCE_CLAIM_FLAGS = {
    "production_validator_implemented",
    "validator_soundness_proved",
    "soundness_proved",
    "full_galois_connection_claim",
    "abstract_interpretation_soundness_proved",
    "public_surface_updated",
    "public_copy_approved",
    "runtime_lowering_changed",
    "machlib_file_changed",
    "lean_typecheck_performed",
    "proof_attempt_started",
    "electronics_repo_touched",
    "laptop_artifact_consumed",
    "renderer_implemented",
    "renderer_executed",
    "public_ready",
}

CLAIM_FLAGS = {
    "reviewer_report_feed_guard_recorded": True,
    "act_a8_reviewer_report_snapshot_consumed": True,
    "source_feed_rebuilt": True,
    "feed_guard_rows_recorded": True,
    "feed_guard_checks_recorded": True,
    "feed_guard_checks_passed": True,
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
    "ACT-A9 records a private reviewer report feed guard only; it is not a production alpha/gamma validator.",
    "ACT-A9 rebuilds and guards the ACT-A8 command feed without proving validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A9 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def feed_guard_rows(source_feed: dict[str, Any]) -> list[dict[str, Any]]:
    true_flags = sorted(key for key, value in source_feed["claimFlags"].items() if value is True)
    blocked_false_flags = sorted(
        key for key in BLOCKED_SOURCE_CLAIM_FLAGS if source_feed["claimFlags"].get(key) is False
    )
    return [
        {
            "guardRowId": "act_a9_feed_guard:feed_id",
            "observed": source_feed["feedId"],
            "expected": EXPECTED_SOURCE_FEED_ID,
            "status": "pass",
        },
        {
            "guardRowId": "act_a9_feed_guard:status",
            "observed": source_feed["status"],
            "expected": EXPECTED_SOURCE_STATUS,
            "status": "pass",
        },
        {
            "guardRowId": "act_a9_feed_guard:decision",
            "observed": source_feed["decision"],
            "expected": EXPECTED_SOURCE_DECISION,
            "status": "pass",
        },
        {
            "guardRowId": "act_a9_feed_guard:next_action_is_private",
            "observed": "without public promotion" in source_feed["nextAction"],
            "expected": True,
            "status": "pass",
        },
        {
            "guardRowId": "act_a9_feed_guard:allowed_true_claim_flags",
            "observed": true_flags,
            "expected": sorted(ALLOWED_TRUE_SOURCE_CLAIM_FLAGS),
            "status": "pass",
        },
        {
            "guardRowId": "act_a9_feed_guard:blocked_claim_flags_false",
            "observed": blocked_false_flags,
            "expected": sorted(BLOCKED_SOURCE_CLAIM_FLAGS),
            "status": "pass",
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a8.build_payload(atlas_gate_path)
    a8.validate_payload(source)
    source_feed = a8.build_feed(source)
    rows = feed_guard_rows(source_feed)
    for row in rows:
        if row["observed"] != row["expected"]:
            raise ValueError(f"feed guard row failed: {row['guardRowId']}")
    summary = {
        "sourceReviewerReportSnapshot": source["artifactId"],
        "sourceFeedId": source_feed["feedId"],
        "sourceFeedStatus": source_feed["status"],
        "sourceFeedDecision": source_feed["decision"],
        "sourceFeedNextAction": source_feed["nextAction"],
        "sourceClaimFlagCount": len(source_feed["claimFlags"]),
        "allowedTrueSourceClaimFlagCount": len(ALLOWED_TRUE_SOURCE_CLAIM_FLAGS),
        "blockedSourceClaimFlagCount": len(BLOCKED_SOURCE_CLAIM_FLAGS),
        "feedGuardRowCount": len(rows),
        "feedGuardPassCount": sum(1 for row in rows if row["status"] == "pass"),
        "reviewerReportFeedGuardRecorded": True,
        "actA8ReviewerReportSnapshotConsumed": True,
        "sourceFeedRebuilt": True,
        "feedGuardRowsRecorded": True,
        "feedGuardChecksRecorded": True,
        "feedGuardChecksPassed": True,
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
        "nextAction": "GB-VIS-A9 private adapter feed guard or ACT-A10 reviewer intake guard without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "reviewer_report_feed_guard_recorded",
                "act_a8_reviewer_report_snapshot_consumed",
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
                "reviewer_report_feed_guard_recorded",
                "act_a8_reviewer_report_snapshot_consumed",
                "source_feed_rebuilt",
                "feed_guard_rows_recorded",
                "feed_guard_checks_recorded",
                "feed_guard_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_reviewer_report_feed_guard_v0",
        "artifactId": "act-a9-reviewer-report-feed-guard",
        "status": STATUS,
        "decision": "record_reviewer_report_feed_guard_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceReviewerReportSnapshot": source["artifactId"],
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
    if payload["sourceReviewerReportSnapshot"] != "act-a8-reviewer-report-snapshot":
        raise ValueError("ACT-A9 must consume ACT-A8")
    if summary["sourceFeedId"] != EXPECTED_SOURCE_FEED_ID:
        raise ValueError("unexpected source feed id")
    if summary["sourceFeedStatus"] != EXPECTED_SOURCE_STATUS:
        raise ValueError("unexpected source feed status")
    if summary["sourceFeedDecision"] != EXPECTED_SOURCE_DECISION:
        raise ValueError("unexpected source feed decision")
    if summary["feedGuardRowCount"] != 6 or summary["feedGuardPassCount"] != 6:
        raise ValueError("unexpected feed guard count")
    if summary["allowedTrueSourceClaimFlagCount"] != 6:
        raise ValueError("unexpected allowed true claim flag count")
    if summary["blockedSourceClaimFlagCount"] != len(BLOCKED_SOURCE_CLAIM_FLAGS):
        raise ValueError("unexpected blocked claim flag count")
    for row in payload["feedGuardRows"]:
        if row["status"] != "pass" or row["observed"] != row["expected"]:
            raise ValueError("feed guard row must pass exactly")
    for key in [
        "reviewerReportFeedGuardRecorded",
        "actA8ReviewerReportSnapshotConsumed",
        "sourceFeedRebuilt",
        "feedGuardRowsRecorded",
        "feedGuardChecksRecorded",
        "feedGuardChecksPassed",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
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
        "artifactType": "alpha_gamma_reviewer_report_feed_guard",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_reviewer_report_feed_guard_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a9_reviewer_report_feed_guard/act_a9_reviewer_report_feed_guard_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a9_reviewer_report_feed_guard_feed",
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
        "# ACT-A9 Reviewer Report Feed Guard",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A9 records a private reviewer report feed guard without implementing a production validator.",
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


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"act_a9_reviewer_report_feed_guard_{STAMP}.json"
    report_path = report_dir / f"act_a9_reviewer_report_feed_guard_{STAMP}.md"
    evidence_path = evidence_dir / "act_a9_reviewer_report_feed_guard.json"
    feed_path = command_feed_dir / f"act_a9_reviewer_report_feed_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a9_reviewer_report_feed_guard")
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
    print("ACT_A9_REVIEWER_REPORT_FEED_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
