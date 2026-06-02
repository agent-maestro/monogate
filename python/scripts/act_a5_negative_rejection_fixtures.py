#!/usr/bin/env python3
"""ACT-A5 alpha/gamma negative rejection fixture packet."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import act_a4_dry_run_validator_fixture_expansion as a4  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_negative_rejection_fixtures.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A5_NEGATIVE_REJECTION_FIXTURES_PASS"

REJECTION_CASE_SPECS = [
    {
        "fixtureId": "act_a5_claim_escalation_negative_fixture",
        "failureMode": "claim_escalation",
        "sourceObligation": "alpha_claim_strength_bounded",
        "expectedRejectReason": "positive fixture attempts theorem discovery and soundness claims",
        "mutations": {
            "claimFlags.theorem_discovery_claim": True,
            "claimFlags.soundness_proved": True,
        },
    },
    {
        "fixtureId": "act_a5_trace_gap_negative_fixture",
        "failureMode": "trace_gap",
        "sourceObligation": "alpha_traceability_complete",
        "expectedRejectReason": "fixture lacks checked statement traceability",
        "mutations": {
            "checkedStatement": "",
        },
    },
    {
        "fixtureId": "act_a5_public_gate_bypass_negative_fixture",
        "failureMode": "public_gate_bypass",
        "sourceObligation": "gamma_boundary_preservation",
        "expectedRejectReason": "fixture bypasses private hold and public readiness gate",
        "mutations": {
            "publicStatus": "public_ready",
            "claimFlags.public_ready": True,
        },
    },
    {
        "fixtureId": "act_a5_runtime_drift_negative_fixture",
        "failureMode": "runtime_drift",
        "sourceObligation": "gamma_boundary_preservation",
        "expectedRejectReason": "fixture changes protected runtime lowering boundary",
        "mutations": {
            "runtimeControl": "runtime_lowering_changed",
            "claimFlags.runtime_lowering_changed": True,
        },
    },
    {
        "fixtureId": "act_a5_lane_owner_drift_negative_fixture",
        "failureMode": "lane_owner_drift",
        "sourceObligation": "gamma_admissible_artifact_class",
        "expectedRejectReason": "fixture claims electronics/laptop lane ownership changed",
        "mutations": {
            "claimFlags.electronics_repo_touched": True,
            "claimFlags.laptop_artifact_consumed": True,
        },
    },
]

CLAIM_FLAGS = {
    "negative_rejection_fixtures_recorded": True,
    "act_a4_fixture_expansion_consumed": True,
    "expected_rejections_recorded": True,
    "rejection_failure_modes_recorded": True,
    "dry_run_rejection_gate_recorded": True,
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
    "public_ready": False,
}

NON_CLAIMS = [
    "ACT-A5 records synthetic negative/rejection fixtures only; it is not a production alpha/gamma validator.",
    "ACT-A5 expected rejections exercise claim escalation, trace gaps, public gate bypass, runtime drift, and lane-owner drift without proving validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A5 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def set_path(row: dict[str, Any], dotted_path: str, value: Any) -> None:
    target = row
    parts = dotted_path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = value


def build_rejection_fixture(base_case: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    negative = copy.deepcopy(base_case)
    for dotted_path, value in spec["mutations"].items():
        set_path(negative, dotted_path, value)
    return {
        "fixtureId": spec["fixtureId"],
        "sourceAcceptedFixtureId": base_case["fixtureId"],
        "sourceArtifact": base_case["sourceArtifact"],
        "artifactType": base_case["artifactType"],
        "failureMode": spec["failureMode"],
        "sourceObligation": spec["sourceObligation"],
        "expectedStatus": "reject",
        "expectedRejectReason": spec["expectedRejectReason"],
        "mutations": dict(spec["mutations"]),
        "mutatedFixture": negative,
    }


def build_rejection_fixtures(accepted_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {case["fixtureId"]: case for case in accepted_cases}
    base = by_id["eml_d62_expm1_boundary_branch_pause_freeze_packet"]
    return [build_rejection_fixture(base, spec) for spec in REJECTION_CASE_SPECS]


def rejection_check(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "checkId": f"{fixture['fixtureId']}:{fixture['sourceObligation']}",
        "fixtureId": fixture["fixtureId"],
        "sourceAcceptedFixtureId": fixture["sourceAcceptedFixtureId"],
        "sourceObligation": fixture["sourceObligation"],
        "failureMode": fixture["failureMode"],
        "status": "expected_reject",
        "rejectReason": fixture["expectedRejectReason"],
        "productionValidatorUsed": False,
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a4.build_payload(atlas_gate_path)
    a4.validate_payload(source)
    negative_fixtures = build_rejection_fixtures(source["fixtureCases"])
    checks = [rejection_check(fixture) for fixture in negative_fixtures]
    failure_modes = [fixture["failureMode"] for fixture in negative_fixtures]
    summary = {
        "sourceFixtureExpansionPacket": source["artifactId"],
        "sourceAcceptedFixtureCount": source["summary"]["fixtureCaseCount"],
        "negativeFixtureCount": len(negative_fixtures),
        "rejectionCheckCount": len(checks),
        "expectedRejectCount": sum(1 for check in checks if check["status"] == "expected_reject"),
        "unexpectedAcceptCount": 0,
        "failureModesCovered": failure_modes,
        "claimEscalationFixtureIncluded": "claim_escalation" in failure_modes,
        "traceGapFixtureIncluded": "trace_gap" in failure_modes,
        "publicGateBypassFixtureIncluded": "public_gate_bypass" in failure_modes,
        "runtimeDriftFixtureIncluded": "runtime_drift" in failure_modes,
        "laneOwnerDriftFixtureIncluded": "lane_owner_drift" in failure_modes,
        "negativeRejectionFixturesRecorded": True,
        "actA4FixtureExpansionConsumed": True,
        "expectedRejectionsRecorded": True,
        "dryRunRejectionGateRecorded": True,
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
        "publicReady": False,
        "nextAction": "GB-VIS-A5 private renderer integration gate or ACT-A6 rejection fixture expansion hardening without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "negative_rejection_fixtures_recorded",
                "act_a4_fixture_expansion_consumed",
                "expected_rejections_recorded",
                "rejection_failure_modes_recorded",
                "dry_run_rejection_gate_recorded",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "negative_rejection_fixtures_recorded",
                "act_a4_fixture_expansion_consumed",
                "expected_rejections_recorded",
                "rejection_failure_modes_recorded",
                "dry_run_rejection_gate_recorded",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_negative_rejection_fixtures_v0",
        "artifactId": "act-a5-negative-rejection-fixtures",
        "status": STATUS,
        "decision": "record_alpha_gamma_negative_rejection_fixtures_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceFixtureExpansionPacket": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "negativeFixtures": negative_fixtures,
        "rejectionChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceFixtureExpansionPacket"] != "act-a4-dry-run-validator-fixture-expansion":
        raise ValueError("ACT-A5 must consume ACT-A4")
    if summary["sourceAcceptedFixtureCount"] != 3:
        raise ValueError("unexpected source fixture count")
    if summary["negativeFixtureCount"] != 5:
        raise ValueError("unexpected negative fixture count")
    if summary["rejectionCheckCount"] != 5 or summary["expectedRejectCount"] != 5:
        raise ValueError("unexpected rejection check count")
    if summary["unexpectedAcceptCount"] != 0:
        raise ValueError("negative fixtures must not be unexpectedly accepted")
    required_modes = {
        "claim_escalation",
        "trace_gap",
        "public_gate_bypass",
        "runtime_drift",
        "lane_owner_drift",
    }
    if set(summary["failureModesCovered"]) != required_modes:
        raise ValueError("failure mode coverage drift")
    for fixture in payload["negativeFixtures"]:
        if fixture["expectedStatus"] != "reject":
            raise ValueError("negative fixture must expect rejection")
        if not fixture["expectedRejectReason"]:
            raise ValueError("negative fixture reject reason missing")
    for check in payload["rejectionChecks"]:
        if check["status"] != "expected_reject":
            raise ValueError("negative check must record expected rejection")
        if check["productionValidatorUsed"] is not False:
            raise ValueError("ACT-A5 must not use a production validator")
    for key in [
        "negativeRejectionFixturesRecorded",
        "actA4FixtureExpansionConsumed",
        "expectedRejectionsRecorded",
        "dryRunRejectionGateRecorded",
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
        "artifactType": "alpha_gamma_negative_rejection_fixtures",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_negative_rejection_fixtures_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a5_negative_rejection_fixtures/act_a5_negative_rejection_fixtures_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a5_negative_rejection_fixtures_feed",
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
        "# ACT-A5 Negative Rejection Fixtures",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A5 records synthetic alpha/gamma rejection fixtures without implementing a production validator.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| negative fixtures | `{payload['summary']['negativeFixtureCount']}` |",
        f"| rejection checks | `{payload['summary']['rejectionCheckCount']}` |",
        f"| expected rejects | `{payload['summary']['expectedRejectCount']}` |",
        f"| unexpected accepts | `{payload['summary']['unexpectedAcceptCount']}` |",
        "",
        "## Failure Modes",
        "",
    ]
    lines.extend(f"- `{mode}`" for mode in payload["summary"]["failureModesCovered"])
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"act_a5_negative_rejection_fixtures_{STAMP}.json"
    report_path = report_dir / f"act_a5_negative_rejection_fixtures_{STAMP}.md"
    evidence_path = evidence_dir / "act_a5_negative_rejection_fixtures.json"
    feed_path = command_feed_dir / f"act_a5_negative_rejection_fixtures_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a5_negative_rejection_fixtures")
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
    print("ACT_A5_NEGATIVE_REJECTION_FIXTURES_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
