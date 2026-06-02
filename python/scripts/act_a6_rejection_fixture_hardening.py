#!/usr/bin/env python3
"""ACT-A6 alpha/gamma rejection fixture hardening packet."""

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

from scripts import act_a5_negative_rejection_fixtures as a5  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_rejection_fixture_hardening.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A6_REJECTION_FIXTURE_HARDENING_PASS"

EXPECTED_HARDENING = {
    "claim_escalation": {
        "boundaryFamily": "claim_strength",
        "requiredMutationPaths": ["claimFlags.soundness_proved", "claimFlags.theorem_discovery_claim"],
        "reviewerCue": "escalates_private_claim_strength",
    },
    "trace_gap": {
        "boundaryFamily": "traceability",
        "requiredMutationPaths": ["checkedStatement"],
        "reviewerCue": "removes_checked_statement_trace",
    },
    "public_gate_bypass": {
        "boundaryFamily": "public_boundary",
        "requiredMutationPaths": ["claimFlags.public_ready", "publicStatus"],
        "reviewerCue": "bypasses_private_public_gate",
    },
    "runtime_drift": {
        "boundaryFamily": "runtime_boundary",
        "requiredMutationPaths": ["claimFlags.runtime_lowering_changed", "runtimeControl"],
        "reviewerCue": "changes_runtime_lowering_boundary",
    },
    "lane_owner_drift": {
        "boundaryFamily": "lane_ownership",
        "requiredMutationPaths": ["claimFlags.electronics_repo_touched", "claimFlags.laptop_artifact_consumed"],
        "reviewerCue": "crosses_laptop_electronics_lane_boundary",
    },
}

CLAIM_FLAGS = {
    "rejection_fixture_hardening_recorded": True,
    "act_a5_rejection_fixtures_consumed": True,
    "hardening_rows_recorded": True,
    "coverage_obligations_recorded": True,
    "hardening_checks_recorded": True,
    "hardening_checks_passed": True,
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
    "ACT-A6 records private rejection-fixture coverage hardening only; it is not a production alpha/gamma validator.",
    "ACT-A6 hardening rows require source obligations, mutation-path coverage, reviewer cues, and boundary-family labels without proving validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A6 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def build_hardening_row(fixture: dict[str, Any]) -> dict[str, Any]:
    mode = fixture["failureMode"]
    expected = EXPECTED_HARDENING[mode]
    mutation_paths = sorted(fixture["mutations"])
    required_paths = sorted(expected["requiredMutationPaths"])
    missing_paths = sorted(set(required_paths) - set(mutation_paths))
    return {
        "rowId": f"act_a6_hardening:{mode}",
        "sourceFixture": fixture["fixtureId"],
        "sourceObligation": fixture["sourceObligation"],
        "failureMode": mode,
        "boundaryFamily": expected["boundaryFamily"],
        "reviewerCue": expected["reviewerCue"],
        "mutationPaths": mutation_paths,
        "requiredMutationPaths": required_paths,
        "missingRequiredMutationPaths": missing_paths,
        "expectedStatus": fixture["expectedStatus"],
        "expectedRejectReason": fixture["expectedRejectReason"],
        "coverageStatus": "covered" if not missing_paths and fixture["expectedStatus"] == "reject" else "gap",
    }


def build_hardening_rows(rejection_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [build_hardening_row(fixture) for fixture in rejection_packet["negativeFixtures"]]


def hardening_checks(source: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    modes = sorted(row["failureMode"] for row in rows)
    families = sorted(row["boundaryFamily"] for row in rows)
    required_modes = sorted(EXPECTED_HARDENING)
    required_families = sorted({item["boundaryFamily"] for item in EXPECTED_HARDENING.values()})
    missing_paths = [row for row in rows if row["missingRequiredMutationPaths"]]
    checks = [
        {
            "checkId": "act_a5_source_consumed",
            "status": "pass",
            "observed": source["artifactId"],
            "expected": "act-a5-negative-rejection-fixtures",
        },
        {
            "checkId": "all_rejection_modes_have_hardening_rows",
            "status": "pass",
            "observed": modes,
            "expected": required_modes,
        },
        {
            "checkId": "boundary_families_are_complete",
            "status": "pass",
            "observed": families,
            "expected": required_families,
        },
        {
            "checkId": "required_mutation_paths_are_present",
            "status": "pass",
            "observed": len(missing_paths),
            "expected": 0,
        },
        {
            "checkId": "all_rows_remain_expected_reject",
            "status": "pass",
            "observed": sorted(row["expectedStatus"] for row in rows),
            "expected": ["reject"] * len(EXPECTED_HARDENING),
        },
        {
            "checkId": "reviewer_cues_are_unique",
            "status": "pass",
            "observed": len({row["reviewerCue"] for row in rows}),
            "expected": len(EXPECTED_HARDENING),
        },
        {
            "checkId": "coverage_statuses_are_covered",
            "status": "pass",
            "observed": sorted({row["coverageStatus"] for row in rows}),
            "expected": ["covered"],
        },
    ]
    for check in checks:
        if check["observed"] != check["expected"]:
            raise ValueError(f"hardening check failed: {check['checkId']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a5.build_payload(atlas_gate_path)
    a5.validate_payload(source)
    rows = build_hardening_rows(source)
    checks = hardening_checks(source, rows)
    summary = {
        "sourceRejectionPacket": source["artifactId"],
        "sourceNegativeFixtureCount": source["summary"]["negativeFixtureCount"],
        "hardeningRowCount": len(rows),
        "coverageObligationCount": sum(len(row["requiredMutationPaths"]) for row in rows),
        "hardeningCheckCount": len(checks),
        "hardeningCheckPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "missingMutationPathCount": sum(len(row["missingRequiredMutationPaths"]) for row in rows),
        "boundaryFamilyCount": len({row["boundaryFamily"] for row in rows}),
        "reviewerCueCount": len({row["reviewerCue"] for row in rows}),
        "unexpectedAcceptCount": source["summary"]["unexpectedAcceptCount"],
        "rejectionFixtureHardeningRecorded": True,
        "actA5RejectionFixturesConsumed": True,
        "hardeningRowsRecorded": True,
        "coverageObligationsRecorded": True,
        "hardeningChecksRecorded": True,
        "hardeningChecksPassed": True,
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
        "nextAction": "GB-VIS-A6 private renderer adapter contract or ACT-A7 dry-run validator reporting contract without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "rejection_fixture_hardening_recorded",
                "act_a5_rejection_fixtures_consumed",
                "hardening_rows_recorded",
                "coverage_obligations_recorded",
                "hardening_checks_recorded",
                "hardening_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "rejection_fixture_hardening_recorded",
                "act_a5_rejection_fixtures_consumed",
                "hardening_rows_recorded",
                "coverage_obligations_recorded",
                "hardening_checks_recorded",
                "hardening_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_rejection_fixture_hardening_v0",
        "artifactId": "act-a6-rejection-fixture-hardening",
        "status": STATUS,
        "decision": "record_alpha_gamma_rejection_fixture_hardening_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceRejectionPacket": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "hardeningRows": rows,
        "hardeningChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceRejectionPacket"] != "act-a5-negative-rejection-fixtures":
        raise ValueError("ACT-A6 must consume ACT-A5")
    if summary["sourceNegativeFixtureCount"] != 5:
        raise ValueError("unexpected source negative fixture count")
    if summary["hardeningRowCount"] != 5:
        raise ValueError("unexpected hardening row count")
    if summary["coverageObligationCount"] != 9:
        raise ValueError("unexpected coverage obligation count")
    if summary["hardeningCheckCount"] != 7 or summary["hardeningCheckPassCount"] != 7:
        raise ValueError("unexpected hardening check count")
    if summary["missingMutationPathCount"] != 0:
        raise ValueError("hardening rows must have no missing mutation paths")
    if summary["boundaryFamilyCount"] != 5 or summary["reviewerCueCount"] != 5:
        raise ValueError("hardening coverage drift")
    if summary["unexpectedAcceptCount"] != 0:
        raise ValueError("unexpected accept drift")
    for row in payload["hardeningRows"]:
        if row["coverageStatus"] != "covered":
            raise ValueError("hardening row must be covered")
        if row["expectedStatus"] != "reject":
            raise ValueError("hardening row must preserve expected rejection")
        if row["missingRequiredMutationPaths"]:
            raise ValueError("hardening row missing mutation paths")
    for check in payload["hardeningChecks"]:
        if check["status"] != "pass" or check["observed"] != check["expected"]:
            raise ValueError("hardening check must pass exactly")
    for key in [
        "rejectionFixtureHardeningRecorded",
        "actA5RejectionFixturesConsumed",
        "hardeningRowsRecorded",
        "coverageObligationsRecorded",
        "hardeningChecksRecorded",
        "hardeningChecksPassed",
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
        "artifactType": "alpha_gamma_rejection_fixture_hardening",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_rejection_fixture_hardening_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a6_rejection_fixture_hardening/act_a6_rejection_fixture_hardening_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a6_rejection_fixture_hardening_feed",
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
        "# ACT-A6 Rejection Fixture Hardening",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A6 records private rejection-fixture hardening without implementing a production validator.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| hardening rows | `{payload['summary']['hardeningRowCount']}` |",
        f"| coverage obligations | `{payload['summary']['coverageObligationCount']}` |",
        f"| hardening checks | `{payload['summary']['hardeningCheckCount']}` |",
        f"| hardening passes | `{payload['summary']['hardeningCheckPassCount']}` |",
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
    result_path = out_dir / f"act_a6_rejection_fixture_hardening_{STAMP}.json"
    report_path = report_dir / f"act_a6_rejection_fixture_hardening_{STAMP}.md"
    evidence_path = evidence_dir / "act_a6_rejection_fixture_hardening.json"
    feed_path = command_feed_dir / f"act_a6_rejection_fixture_hardening_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a6_rejection_fixture_hardening")
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
    print("ACT_A6_REJECTION_FIXTURE_HARDENING_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
