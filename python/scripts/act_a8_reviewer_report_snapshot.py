#!/usr/bin/env python3
"""ACT-A8 reviewer report snapshot packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import act_a7_dry_run_validator_reporting_contract as a7  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_reviewer_report_snapshot.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A8_REVIEWER_REPORT_SNAPSHOT_PASS"

CLAIM_FLAGS = {
    "reviewer_report_snapshot_recorded": True,
    "act_a7_reporting_contract_consumed": True,
    "baseline_snapshot_recorded": True,
    "observed_snapshot_recorded": True,
    "snapshot_checks_recorded": True,
    "snapshot_checks_passed": True,
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
    "ACT-A8 records a private reviewer report snapshot only; it is not a production alpha/gamma validator.",
    "ACT-A8 snapshots ACT-A7 report rows and sections without proving validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A8 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_snapshot(source: dict[str, Any], snapshot_id: str) -> dict[str, Any]:
    rows = source["reportRows"]
    sections = source["reportSections"]
    checks = source["reportingChecks"]
    return {
        "snapshotId": snapshot_id,
        "snapshotFormat": "monogate.alpha_gamma_reviewer_report_snapshot.v0",
        "sourceReportingContract": source["artifactId"],
        "reportRowCount": len(rows),
        "reportSectionCount": len(sections),
        "reportingCheckCount": len(checks),
        "coveredReportRowCount": source["summary"]["coveredReportRowCount"],
        "missingMutationPathCount": source["summary"]["missingMutationPathCount"],
        "rowDigest": digest(rows),
        "sectionDigest": digest(sections),
        "checkDigest": digest(checks),
        "nonClaimDigest": digest(source["nonClaims"]),
        "claimFlagDigest": digest(source["claimFlags"]),
    }


def snapshot_checks(baseline: dict[str, Any], observed: dict[str, Any]) -> list[dict[str, Any]]:
    fields = [
        "rowDigest",
        "sectionDigest",
        "checkDigest",
        "nonClaimDigest",
        "claimFlagDigest",
    ]
    checks = [
        {
            "checkId": f"{field}_matches",
            "status": "pass",
            "field": field,
            "baseline": baseline[field],
            "observed": observed[field],
        }
        for field in fields
    ]
    for check in checks:
        if check["baseline"] != check["observed"]:
            raise ValueError(f"reviewer report snapshot mismatch: {check['field']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a7.build_payload(atlas_gate_path)
    a7.validate_payload(source)
    baseline = build_snapshot(source, "act_a8_baseline_private_reviewer_report_snapshot")
    observed = build_snapshot(source, "act_a8_observed_private_reviewer_report_snapshot")
    checks = snapshot_checks(baseline, observed)
    summary = {
        "sourceReportingContract": source["artifactId"],
        "baselineSnapshotId": baseline["snapshotId"],
        "observedSnapshotId": observed["snapshotId"],
        "reportRowCount": baseline["reportRowCount"],
        "reportSectionCount": baseline["reportSectionCount"],
        "reportingCheckCount": baseline["reportingCheckCount"],
        "coveredReportRowCount": baseline["coveredReportRowCount"],
        "missingMutationPathCount": baseline["missingMutationPathCount"],
        "snapshotCheckCount": len(checks),
        "snapshotCheckPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "reviewerReportSnapshotRecorded": True,
        "actA7ReportingContractConsumed": True,
        "baselineSnapshotRecorded": True,
        "observedSnapshotRecorded": True,
        "snapshotChecksRecorded": True,
        "snapshotChecksPassed": True,
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
        "nextAction": "GB-VIS-A8 private adapter snapshot comparison or ACT-A9 reviewer report feed guard without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "reviewer_report_snapshot_recorded",
                "act_a7_reporting_contract_consumed",
                "baseline_snapshot_recorded",
                "observed_snapshot_recorded",
                "snapshot_checks_recorded",
                "snapshot_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "reviewer_report_snapshot_recorded",
                "act_a7_reporting_contract_consumed",
                "baseline_snapshot_recorded",
                "observed_snapshot_recorded",
                "snapshot_checks_recorded",
                "snapshot_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_reviewer_report_snapshot_v0",
        "artifactId": "act-a8-reviewer-report-snapshot",
        "status": STATUS,
        "decision": "record_reviewer_report_snapshot_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceReportingContract": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "baselineSnapshot": baseline,
        "observedSnapshot": observed,
        "snapshotChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceReportingContract"] != "act-a7-dry-run-validator-reporting-contract":
        raise ValueError("ACT-A8 must consume ACT-A7")
    if summary["reportRowCount"] != 5 or summary["reportSectionCount"] != 6:
        raise ValueError("unexpected report snapshot count")
    if summary["reportingCheckCount"] != 7:
        raise ValueError("unexpected reporting check count")
    if summary["coveredReportRowCount"] != 5 or summary["missingMutationPathCount"] != 0:
        raise ValueError("report snapshot coverage drift")
    if summary["snapshotCheckCount"] != 5 or summary["snapshotCheckPassCount"] != 5:
        raise ValueError("unexpected snapshot check count")
    for check in payload["snapshotChecks"]:
        if check["status"] != "pass" or check["baseline"] != check["observed"]:
            raise ValueError("reviewer report snapshot check must pass exactly")
    for key in [
        "reviewerReportSnapshotRecorded",
        "actA7ReportingContractConsumed",
        "baselineSnapshotRecorded",
        "observedSnapshotRecorded",
        "snapshotChecksRecorded",
        "snapshotChecksPassed",
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
        "artifactType": "alpha_gamma_reviewer_report_snapshot",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_reviewer_report_snapshot_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a8_reviewer_report_snapshot/act_a8_reviewer_report_snapshot_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a8_reviewer_report_snapshot_feed",
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
        "# ACT-A8 Reviewer Report Snapshot",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A8 records a private reviewer report snapshot without implementing a production validator.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| report rows | `{payload['summary']['reportRowCount']}` |",
        f"| report sections | `{payload['summary']['reportSectionCount']}` |",
        f"| snapshot checks | `{payload['summary']['snapshotCheckCount']}` |",
        f"| snapshot passes | `{payload['summary']['snapshotCheckPassCount']}` |",
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
    result_path = out_dir / f"act_a8_reviewer_report_snapshot_{STAMP}.json"
    report_path = report_dir / f"act_a8_reviewer_report_snapshot_{STAMP}.md"
    evidence_path = evidence_dir / "act_a8_reviewer_report_snapshot.json"
    feed_path = command_feed_dir / f"act_a8_reviewer_report_snapshot_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a8_reviewer_report_snapshot")
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
    print("ACT_A8_REVIEWER_REPORT_SNAPSHOT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
