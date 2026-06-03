#!/usr/bin/env python3
"""ACT-A10 reviewer intake guard packet."""

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

from scripts import act_a9_reviewer_report_feed_guard as a9  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_reviewer_intake_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A10_REVIEWER_INTAKE_GUARD_PASS"

EXPECTED_SOURCE_ARTIFACT = "act-a9-reviewer-report-feed-guard"
EXPECTED_SOURCE_STATUS = "ACT_A9_REVIEWER_REPORT_FEED_GUARD_PASS"
EXPECTED_SOURCE_FEED_ID = "act_a9_reviewer_report_feed_guard_feed"

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
    "reviewer_intake_guard_recorded": True,
    "act_a9_reviewer_feed_guard_consumed": True,
    "source_feed_guard_rows_consumed": True,
    "intake_guard_rows_recorded": True,
    "intake_guard_checks_recorded": True,
    "intake_guard_checks_passed": True,
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
    "ACT-A10 records a private reviewer intake guard only; it is not a production alpha/gamma validator.",
    "ACT-A10 consumes ACT-A9 feed-guard evidence without accepting a laptop artifact, proving validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A10 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, electronics repos, or course artifacts.",
]


def intake_guard_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    source_feed = a9.build_feed(source)
    blocked_false_flags = sorted(
        key for key in BLOCKED_SOURCE_CLAIM_FLAGS if source["claimFlags"].get(key) is False
    )
    return [
        {
            "guardRowId": "act_a10_intake_guard:source_artifact",
            "observed": source["artifactId"],
            "expected": EXPECTED_SOURCE_ARTIFACT,
            "status": "pass",
        },
        {
            "guardRowId": "act_a10_intake_guard:source_status",
            "observed": source["status"],
            "expected": EXPECTED_SOURCE_STATUS,
            "status": "pass",
        },
        {
            "guardRowId": "act_a10_intake_guard:source_feed_id",
            "observed": source_feed["feedId"],
            "expected": EXPECTED_SOURCE_FEED_ID,
            "status": "pass",
        },
        {
            "guardRowId": "act_a10_intake_guard:source_feed_guard_rows_passed",
            "observed": source["summary"]["feedGuardPassCount"],
            "expected": source["summary"]["feedGuardRowCount"],
            "status": "pass",
        },
        {
            "guardRowId": "act_a10_intake_guard:source_next_action_is_private",
            "observed": "without public promotion" in source["summary"]["nextAction"],
            "expected": True,
            "status": "pass",
        },
        {
            "guardRowId": "act_a10_intake_guard:blocked_claim_flags_false",
            "observed": blocked_false_flags,
            "expected": sorted(BLOCKED_SOURCE_CLAIM_FLAGS),
            "status": "pass",
        },
        {
            "guardRowId": "act_a10_intake_guard:no_laptop_or_course_artifact_accepted",
            "observed": {
                "laptopArtifactConsumed": source["summary"]["laptopArtifactConsumed"],
                "publicReady": source["summary"]["publicReady"],
            },
            "expected": {
                "laptopArtifactConsumed": False,
                "publicReady": False,
            },
            "status": "pass",
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a9.build_payload(atlas_gate_path)
    a9.validate_payload(source)
    rows = intake_guard_rows(source)
    for row in rows:
        if row["observed"] != row["expected"]:
            raise ValueError(f"reviewer intake guard row failed: {row['guardRowId']}")
    summary = {
        "sourceReviewerFeedGuard": source["artifactId"],
        "sourceFeedId": a9.build_feed(source)["feedId"],
        "sourceFeedGuardRowCount": source["summary"]["feedGuardRowCount"],
        "sourceFeedGuardPassCount": source["summary"]["feedGuardPassCount"],
        "sourceClaimFlagCount": len(source["claimFlags"]),
        "blockedSourceClaimFlagCount": len(BLOCKED_SOURCE_CLAIM_FLAGS),
        "intakeGuardRowCount": len(rows),
        "intakeGuardPassCount": sum(1 for row in rows if row["status"] == "pass"),
        "reviewerIntakeGuardRecorded": True,
        "actA9ReviewerFeedGuardConsumed": True,
        "sourceFeedGuardRowsConsumed": True,
        "intakeGuardRowsRecorded": True,
        "intakeGuardChecksRecorded": True,
        "intakeGuardChecksPassed": True,
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
        "nextAction": "GB-VIS-A10 private adapter intake guard or ACT-A11 reviewer intake snapshot without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "reviewer_intake_guard_recorded",
                "act_a9_reviewer_feed_guard_consumed",
                "source_feed_guard_rows_consumed",
                "intake_guard_rows_recorded",
                "intake_guard_checks_recorded",
                "intake_guard_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "reviewer_intake_guard_recorded",
                "act_a9_reviewer_feed_guard_consumed",
                "source_feed_guard_rows_consumed",
                "intake_guard_rows_recorded",
                "intake_guard_checks_recorded",
                "intake_guard_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_reviewer_intake_guard_v0",
        "artifactId": "act-a10-reviewer-intake-guard",
        "status": STATUS,
        "decision": "record_reviewer_intake_guard_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceReviewerFeedGuard": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "sourceFeedGuardRows": source["feedGuardRows"],
        "intakeGuardRows": rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceReviewerFeedGuard"] != EXPECTED_SOURCE_ARTIFACT:
        raise ValueError("ACT-A10 must consume ACT-A9")
    if summary["sourceFeedId"] != EXPECTED_SOURCE_FEED_ID:
        raise ValueError("unexpected source feed id")
    if summary["sourceFeedGuardRowCount"] != 6 or summary["sourceFeedGuardPassCount"] != 6:
        raise ValueError("unexpected source feed guard count")
    if summary["sourceClaimFlagCount"] != 30:
        raise ValueError("unexpected source claim flag count")
    if summary["blockedSourceClaimFlagCount"] != len(BLOCKED_SOURCE_CLAIM_FLAGS):
        raise ValueError("unexpected blocked source claim flag count")
    if summary["intakeGuardRowCount"] != 7 or summary["intakeGuardPassCount"] != 7:
        raise ValueError("unexpected intake guard count")
    for row in payload["intakeGuardRows"]:
        if row["status"] != "pass" or row["observed"] != row["expected"]:
            raise ValueError("reviewer intake guard row must pass exactly")
    for key in [
        "reviewerIntakeGuardRecorded",
        "actA9ReviewerFeedGuardConsumed",
        "sourceFeedGuardRowsConsumed",
        "intakeGuardRowsRecorded",
        "intakeGuardChecksRecorded",
        "intakeGuardChecksPassed",
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
        "artifactType": "alpha_gamma_reviewer_intake_guard",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_reviewer_intake_guard_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a10_reviewer_intake_guard/act_a10_reviewer_intake_guard_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a10_reviewer_intake_guard_feed",
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
        "# ACT-A10 Reviewer Intake Guard",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A10 records a private reviewer intake guard without implementing a production validator.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| source feed guard rows | `{payload['summary']['sourceFeedGuardRowCount']}` |",
        f"| source feed guard passes | `{payload['summary']['sourceFeedGuardPassCount']}` |",
        f"| source claim flags | `{payload['summary']['sourceClaimFlagCount']}` |",
        f"| blocked source flags | `{payload['summary']['blockedSourceClaimFlagCount']}` |",
        f"| intake guard rows | `{payload['summary']['intakeGuardRowCount']}` |",
        f"| intake guard passes | `{payload['summary']['intakeGuardPassCount']}` |",
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
    result_path = out_dir / f"act_a10_reviewer_intake_guard_{STAMP}.json"
    report_path = report_dir / f"act_a10_reviewer_intake_guard_{STAMP}.md"
    evidence_path = evidence_dir / "act_a10_reviewer_intake_guard.json"
    feed_path = command_feed_dir / f"act_a10_reviewer_intake_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a10_reviewer_intake_guard")
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
    print("ACT_A10_REVIEWER_INTAKE_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
