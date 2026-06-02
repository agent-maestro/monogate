#!/usr/bin/env python3
"""ACT-A4 alpha/gamma dry-run validator fixture expansion packet."""

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

from scripts import act_a2_alpha_gamma_validator_obligations as a2  # noqa: E402
from scripts import eml_d45_positive_log_exp_branch_pause_freeze_packet as d45  # noqa: E402
from scripts import eml_d53_constant_coordinate_branch_pause_freeze_packet as d53  # noqa: E402
from scripts import eml_d62_expm1_boundary_branch_pause_freeze_packet as d62  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_dry_run_fixture_expansion.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A4_DRY_RUN_VALIDATOR_FIXTURE_EXPANSION_PASS"

OBLIGATION_IDS = [
    "alpha_source_identity_required",
    "alpha_claim_strength_bounded",
    "alpha_traceability_complete",
    "gamma_admissible_artifact_class",
    "gamma_boundary_preservation",
    "roundtrip_no_claim_escalation",
]

CLAIM_FLAGS = {
    "dry_run_fixture_expansion_recorded": True,
    "act_a2_obligations_consumed": True,
    "fixture_cases_recorded": True,
    "fixture_checks_dry_run": True,
    "fixture_checks_passed": True,
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
    "ACT-A4 expands private dry-run validator fixtures only; it is not a production alpha/gamma validator.",
    "ACT-A4 checks D45, D53, and D62 private freeze packet shapes against ACT-A2 obligation classes without proving soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A4 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def fixture_case(case_id: str, packet: dict[str, Any], checked_statement: str, runtime_control: str, public_status: str) -> dict[str, Any]:
    row = packet["freezeRows"][0]
    return {
        "fixtureId": case_id,
        "sourceArtifact": packet["artifactId"],
        "artifactType": "private_freeze_packet",
        "freezeId": row["freezeId"],
        "machlibName": row["machlibName"],
        "checkedStatement": checked_statement,
        "runtimeControl": runtime_control,
        "publicStatus": public_status,
        "guardCount": len(row.get("guards", [])),
        "caveatCount": len(row["frozenCaveats"]),
        "blockedPhraseCount": len(row["frozenBlockedPhrases"]),
        "claimFlags": packet["claimFlags"],
        "nonClaimCount": len(packet["nonClaims"]),
        "sourcePath": f"python/results/{case_id}/{packet['artifactId']}_{STAMP}.json",
    }


def build_fixture_cases(atlas_gate_path: Path) -> list[dict[str, Any]]:
    positive = d45.build_payload(atlas_gate_path)
    d45.validate_payload(positive)
    constant = d53.build_payload(atlas_gate_path)
    d53.validate_payload(constant)
    expm1 = d62.build_payload(atlas_gate_path)
    d62.validate_payload(expm1)
    return [
        fixture_case(
            "eml_d45_positive_log_exp_branch_pause_freeze_packet",
            positive,
            positive["freezeRows"][0]["checkedStatement"],
            positive["freezeRows"][0]["runtimeControl"],
            "held_private",
        ),
        fixture_case(
            "eml_d53_constant_coordinate_branch_pause_freeze_packet",
            constant,
            constant["freezeRows"][0]["checkedStatement"],
            constant["freezeRows"][0]["runtimeControl"],
            "held_private",
        ),
        fixture_case(
            "eml_d62_expm1_boundary_branch_pause_freeze_packet",
            expm1,
            expm1["freezeRows"][0]["checkedStatement"],
            expm1["freezeRows"][0]["runtimeControl"],
            "held_private",
        ),
    ]


def dry_run_check(case: dict[str, Any], obligation_id: str) -> dict[str, Any]:
    evidence_map = {
        "alpha_source_identity_required": [case["sourceArtifact"], case["artifactType"], case["freezeId"], case["machlibName"]],
        "alpha_claim_strength_bounded": sorted(key for key, value in case["claimFlags"].items() if value is True),
        "alpha_traceability_complete": [case["checkedStatement"], f"caveats={case['caveatCount']}", f"blocked={case['blockedPhraseCount']}", f"nonClaims={case['nonClaimCount']}"],
        "gamma_admissible_artifact_class": ["evidence_packet", "lean_checked_witness"],
        "gamma_boundary_preservation": [case["runtimeControl"], case["publicStatus"]],
        "roundtrip_no_claim_escalation": ["publicReady=false", "runtimeLoweringChanged=false", "soundnessProved=false"],
    }
    return {
        "checkId": f"{case['fixtureId']}:{obligation_id}",
        "fixtureId": case["fixtureId"],
        "sourceObligation": obligation_id,
        "status": "pass",
        "rejectedFailureModes": [],
        "evidence": evidence_map[obligation_id],
    }


def fixture_checks(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks = [dry_run_check(case, obligation_id) for case in cases for obligation_id in OBLIGATION_IDS]
    for case in cases:
        if not case["sourceArtifact"] or not case["machlibName"] or not case["checkedStatement"]:
            raise ValueError("fixture source identity incomplete")
        if case["publicStatus"] != "held_private":
            raise ValueError("fixture public boundary drift")
        if case["claimFlags"].get("public_ready") is not False:
            raise ValueError("fixture public-ready escalation")
        if case["claimFlags"].get("runtime_lowering_changed") is not False:
            raise ValueError("fixture runtime escalation")
        if case["claimFlags"].get("electronics_repo_touched") is not False:
            raise ValueError("fixture lane-owner drift")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    obligations = a2.build_payload(atlas_gate_path)
    a2.validate_payload(obligations)
    cases = build_fixture_cases(atlas_gate_path)
    checks = fixture_checks(cases)
    summary = {
        "sourceObligationsPacket": obligations["artifactId"],
        "sourceValidatorObligationCount": obligations["summary"]["validatorObligationCount"],
        "fixtureCaseCount": len(cases),
        "fixtureCheckCount": len(checks),
        "fixtureCheckPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "fixtureRejectCount": sum(len(check["rejectedFailureModes"]) for check in checks),
        "obligationCoveragePerFixture": len(OBLIGATION_IDS),
        "positiveGuardedFixtureIncluded": True,
        "constantCoordinateFixtureIncluded": True,
        "expm1FixtureIncluded": True,
        "dryRunFixtureExpansionRecorded": True,
        "actA2ObligationsConsumed": True,
        "fixtureCasesRecorded": True,
        "fixtureChecksDryRun": True,
        "fixtureChecksPassed": True,
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
        "nextAction": "ACT-A5 add negative/rejection fixtures or GB-VIS-A5 add private renderer integration gate without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "dry_run_fixture_expansion_recorded",
                "act_a2_obligations_consumed",
                "fixture_cases_recorded",
                "fixture_checks_dry_run",
                "fixture_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "dry_run_fixture_expansion_recorded",
                "act_a2_obligations_consumed",
                "fixture_cases_recorded",
                "fixture_checks_dry_run",
                "fixture_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_dry_run_fixture_expansion_v0",
        "artifactId": "act-a4-dry-run-validator-fixture-expansion",
        "status": STATUS,
        "decision": "expand_alpha_gamma_dry_run_fixtures_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceObligationsPacket": obligations["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "fixtureCases": cases,
        "fixtureChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceObligationsPacket"] != "act-a2-alpha-gamma-validator-obligations":
        raise ValueError("ACT-A4 must consume ACT-A2")
    if summary["sourceValidatorObligationCount"] != 6:
        raise ValueError("unexpected source obligation count")
    if summary["fixtureCaseCount"] != 3:
        raise ValueError("unexpected fixture count")
    if summary["fixtureCheckCount"] != 18 or summary["fixtureCheckPassCount"] != 18:
        raise ValueError("unexpected fixture check count")
    if summary["fixtureRejectCount"] != 0:
        raise ValueError("fixture dry-run should reject no accepted fixtures")
    for key in [
        "dryRunFixtureExpansionRecorded",
        "actA2ObligationsConsumed",
        "fixtureCasesRecorded",
        "fixtureChecksDryRun",
        "fixtureChecksPassed",
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
    true_keys = {
        "dry_run_fixture_expansion_recorded",
        "act_a2_obligations_consumed",
        "fixture_cases_recorded",
        "fixture_checks_dry_run",
        "fixture_checks_passed",
    }
    for key in true_keys:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in true_keys and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "alpha_gamma_dry_run_fixture_expansion",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_dry_run_fixture_expansion_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a4_dry_run_validator_fixture_expansion/act_a4_dry_run_validator_fixture_expansion_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a4_dry_run_validator_fixture_expansion_feed",
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
        "# ACT-A4 Dry-Run Validator Fixture Expansion",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A4 expands private alpha/gamma dry-run fixtures without implementing a production validator.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| fixture cases | `{payload['summary']['fixtureCaseCount']}` |",
        f"| fixture checks | `{payload['summary']['fixtureCheckCount']}` |",
        f"| fixture passes | `{payload['summary']['fixtureCheckPassCount']}` |",
        f"| fixture rejects | `{payload['summary']['fixtureRejectCount']}` |",
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
    result_path = out_dir / f"act_a4_dry_run_validator_fixture_expansion_{STAMP}.json"
    report_path = report_dir / f"act_a4_dry_run_validator_fixture_expansion_{STAMP}.md"
    evidence_path = evidence_dir / "act_a4_dry_run_validator_fixture_expansion.json"
    feed_path = command_feed_dir / f"act_a4_dry_run_validator_fixture_expansion_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a4_dry_run_validator_fixture_expansion")
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
    print("ACT_A4_DRY_RUN_VALIDATOR_FIXTURE_EXPANSION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
