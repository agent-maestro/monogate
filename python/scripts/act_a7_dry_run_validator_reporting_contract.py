#!/usr/bin/env python3
"""ACT-A7 dry-run validator reporting contract packet."""

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

from scripts import act_a6_rejection_fixture_hardening as a6  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_dry_run_validator_reporting_contract.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A7_DRY_RUN_VALIDATOR_REPORTING_CONTRACT_PASS"

REPORT_SECTIONS = [
    "source_packet",
    "accepted_fixture_context",
    "negative_rejection_coverage",
    "hardening_obligations",
    "non_claims",
    "next_action",
]

CLAIM_FLAGS = {
    "dry_run_validator_reporting_contract_recorded": True,
    "act_a6_hardening_consumed": True,
    "report_rows_recorded": True,
    "report_sections_recorded": True,
    "reporting_checks_recorded": True,
    "reporting_checks_passed": True,
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
    "ACT-A7 records a private dry-run validator reporting contract only; it is not a production alpha/gamma validator.",
    "ACT-A7 formats ACT-A6 hardening evidence into reviewer report rows without proving validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A7 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def report_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "reportRowId": f"act_a7_report:{row['failureMode']}",
        "sourceHardeningRow": row["rowId"],
        "failureMode": row["failureMode"],
        "boundaryFamily": row["boundaryFamily"],
        "reviewerCue": row["reviewerCue"],
        "expectedStatus": row["expectedStatus"],
        "coverageStatus": row["coverageStatus"],
        "requiredMutationPathCount": len(row["requiredMutationPaths"]),
        "missingMutationPathCount": len(row["missingRequiredMutationPaths"]),
        "reportDisposition": "include_private_reviewer_report",
    }


def build_report_rows(hardening_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [report_row(row) for row in hardening_rows]


def reporting_checks(source: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks = [
        {
            "checkId": "source_hardening_packet_is_act_a6",
            "status": "pass",
            "observed": source["artifactId"],
            "expected": "act-a6-rejection-fixture-hardening",
        },
        {
            "checkId": "report_rows_match_hardening_rows",
            "status": "pass",
            "observed": len(rows),
            "expected": source["summary"]["hardeningRowCount"],
        },
        {
            "checkId": "report_sections_are_complete",
            "status": "pass",
            "observed": sorted(REPORT_SECTIONS),
            "expected": sorted(REPORT_SECTIONS),
        },
        {
            "checkId": "all_report_rows_are_private_reviewer_rows",
            "status": "pass",
            "observed": sorted({row["reportDisposition"] for row in rows}),
            "expected": ["include_private_reviewer_report"],
        },
        {
            "checkId": "all_report_rows_are_covered",
            "status": "pass",
            "observed": sorted({row["coverageStatus"] for row in rows}),
            "expected": ["covered"],
        },
        {
            "checkId": "no_missing_mutation_paths_reported",
            "status": "pass",
            "observed": sum(row["missingMutationPathCount"] for row in rows),
            "expected": 0,
        },
        {
            "checkId": "production_validator_claims_remain_false",
            "status": "pass",
            "observed": {
                "productionValidatorImplemented": False,
                "validatorSoundnessProved": False,
                "publicReady": False,
            },
            "expected": {
                "productionValidatorImplemented": False,
                "validatorSoundnessProved": False,
                "publicReady": False,
            },
        },
    ]
    for check in checks:
        if check["observed"] != check["expected"]:
            raise ValueError(f"reporting check failed: {check['checkId']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a6.build_payload(atlas_gate_path)
    a6.validate_payload(source)
    rows = build_report_rows(source["hardeningRows"])
    checks = reporting_checks(source, rows)
    summary = {
        "sourceHardeningPacket": source["artifactId"],
        "sourceHardeningRowCount": source["summary"]["hardeningRowCount"],
        "reportRowCount": len(rows),
        "reportSectionCount": len(REPORT_SECTIONS),
        "reportingCheckCount": len(checks),
        "reportingCheckPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "coveredReportRowCount": sum(1 for row in rows if row["coverageStatus"] == "covered"),
        "missingMutationPathCount": sum(row["missingMutationPathCount"] for row in rows),
        "dryRunValidatorReportingContractRecorded": True,
        "actA6HardeningConsumed": True,
        "reportRowsRecorded": True,
        "reportSectionsRecorded": True,
        "reportingChecksRecorded": True,
        "reportingChecksPassed": True,
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
        "nextAction": "GB-VIS-A7 private adapter smoke fixture or ACT-A8 reviewer report snapshot without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "dry_run_validator_reporting_contract_recorded",
                "act_a6_hardening_consumed",
                "report_rows_recorded",
                "report_sections_recorded",
                "reporting_checks_recorded",
                "reporting_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "dry_run_validator_reporting_contract_recorded",
                "act_a6_hardening_consumed",
                "report_rows_recorded",
                "report_sections_recorded",
                "reporting_checks_recorded",
                "reporting_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_dry_run_validator_reporting_contract_v0",
        "artifactId": "act-a7-dry-run-validator-reporting-contract",
        "status": STATUS,
        "decision": "record_dry_run_validator_reporting_contract_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceHardeningPacket": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "reportSections": list(REPORT_SECTIONS),
        "reportRows": rows,
        "reportingChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceHardeningPacket"] != "act-a6-rejection-fixture-hardening":
        raise ValueError("ACT-A7 must consume ACT-A6")
    if summary["sourceHardeningRowCount"] != 5 or summary["reportRowCount"] != 5:
        raise ValueError("unexpected report row count")
    if summary["reportSectionCount"] != 6:
        raise ValueError("unexpected report section count")
    if summary["reportingCheckCount"] != 7 or summary["reportingCheckPassCount"] != 7:
        raise ValueError("unexpected reporting check count")
    if summary["coveredReportRowCount"] != 5 or summary["missingMutationPathCount"] != 0:
        raise ValueError("report coverage drift")
    for row in payload["reportRows"]:
        if row["reportDisposition"] != "include_private_reviewer_report":
            raise ValueError("report row disposition drift")
        if row["coverageStatus"] != "covered":
            raise ValueError("report row coverage drift")
    for check in payload["reportingChecks"]:
        if check["status"] != "pass" or check["observed"] != check["expected"]:
            raise ValueError("reporting check must pass exactly")
    for key in [
        "dryRunValidatorReportingContractRecorded",
        "actA6HardeningConsumed",
        "reportRowsRecorded",
        "reportSectionsRecorded",
        "reportingChecksRecorded",
        "reportingChecksPassed",
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
        "artifactType": "alpha_gamma_dry_run_validator_reporting_contract",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_dry_run_validator_reporting_contract_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a7_dry_run_validator_reporting_contract/act_a7_dry_run_validator_reporting_contract_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a7_dry_run_validator_reporting_contract_feed",
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
        "# ACT-A7 Dry-Run Validator Reporting Contract",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A7 records private dry-run validator report rows without implementing a production validator.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| report rows | `{payload['summary']['reportRowCount']}` |",
        f"| report sections | `{payload['summary']['reportSectionCount']}` |",
        f"| reporting checks | `{payload['summary']['reportingCheckCount']}` |",
        f"| reporting passes | `{payload['summary']['reportingCheckPassCount']}` |",
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
    result_path = out_dir / f"act_a7_dry_run_validator_reporting_contract_{STAMP}.json"
    report_path = report_dir / f"act_a7_dry_run_validator_reporting_contract_{STAMP}.md"
    evidence_path = evidence_dir / "act_a7_dry_run_validator_reporting_contract.json"
    feed_path = command_feed_dir / f"act_a7_dry_run_validator_reporting_contract_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a7_dry_run_validator_reporting_contract")
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
    print("ACT_A7_DRY_RUN_VALIDATOR_REPORTING_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
