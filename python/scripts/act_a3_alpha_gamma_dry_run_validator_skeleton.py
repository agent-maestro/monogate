#!/usr/bin/env python3
"""ACT-A3 alpha/gamma dry-run validator skeleton packet."""

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

from scripts import act_a1_abstract_concrete_trace_contract as a1  # noqa: E402
from scripts import act_a2_alpha_gamma_validator_obligations as a2  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_dry_run_validator_skeleton.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A3_ALPHA_GAMMA_DRY_RUN_VALIDATOR_SKELETON_PASS"

ALLOWED_TRUE_SOURCE_FLAGS = {
    "validator_obligations_recorded",
    "alpha_validator_requirements_defined",
    "gamma_validator_requirements_defined",
    "failure_modes_defined",
}

EXPECTED_ARTIFACT_CLASSES = {
    "lean_checked_witness",
    "evidence_packet",
    "runtime_trace",
    "lesson_or_hardware_artifact",
}

CLAIM_FLAGS = {
    "dry_run_validator_skeleton_recorded": True,
    "act_a2_obligations_consumed": True,
    "alpha_checks_dry_run": True,
    "gamma_checks_dry_run": True,
    "roundtrip_checks_dry_run": True,
    "validator_skeleton_implemented": True,
    "dry_run_executed": True,
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
    "ACT-A3 implements and executes a dry-run validator skeleton only; it is not a production alpha/gamma validator.",
    "ACT-A3 checks the ACT-A2 obligation shape against the ACT-A1/D62 worked example without proving soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A3 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def _pass_check(check_id: str, operator: str, obligation_id: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "checkId": check_id,
        "operator": operator,
        "sourceObligation": obligation_id,
        "status": "pass",
        "rejectedFailureModes": [],
        "evidence": evidence,
    }


def dry_run_checks(contract: dict[str, Any], obligations: dict[str, Any]) -> list[dict[str, Any]]:
    obligation_ids = {item["obligationId"] for item in obligations["validatorObligations"]}
    artifact_classes = {item["classId"] for item in contract["artifactClasses"]}
    worked_example = contract["workedExamples"][0]
    source_flags = obligations["claimFlags"]
    source_true_flags = {key for key, value in source_flags.items() if value is True}

    checks = [
        _pass_check(
            "alpha_source_identity_required_dry_run",
            "alpha",
            "alpha_source_identity_required",
            [
                obligations["artifactId"],
                obligations["packetType"],
                obligations["sourceAtlasGatePath"],
                obligations["status"],
                "claimFlags",
            ],
        ),
        _pass_check(
            "alpha_claim_strength_bounded_dry_run",
            "alpha",
            "alpha_claim_strength_bounded",
            sorted(source_true_flags),
        ),
        _pass_check(
            "alpha_traceability_complete_dry_run",
            "alpha",
            "alpha_traceability_complete",
            [
                worked_example["sourceFreezePacket"],
                worked_example["alphaResult"]["checkedStatement"],
                worked_example["alphaResult"]["runtimeControl"],
                worked_example["alphaResult"]["publicStatus"],
                "nonClaims",
            ],
        ),
        _pass_check(
            "gamma_admissible_artifact_class_dry_run",
            "gamma",
            "gamma_admissible_artifact_class",
            sorted(artifact_classes),
        ),
        _pass_check(
            "gamma_boundary_preservation_dry_run",
            "gamma",
            "gamma_boundary_preservation",
            [
                contract["summary"]["sourceRuntimeControl"],
                contract["summary"]["sourcePublicStatus"],
                obligations["summary"]["sourceRuntimeControl"],
                obligations["summary"]["sourcePublicStatus"],
            ],
        ),
        _pass_check(
            "roundtrip_no_claim_escalation_dry_run",
            "alpha_gamma_roundtrip",
            "roundtrip_no_claim_escalation",
            [
                f"source_true_flags={','.join(sorted(source_true_flags))}",
                "publicReady=false",
                "runtimeLoweringChanged=false",
                "soundnessProved=false",
            ],
        ),
    ]

    if obligation_ids != {check["sourceObligation"] for check in checks}:
        raise ValueError("dry-run checks do not cover ACT-A2 obligations")
    if source_true_flags != ALLOWED_TRUE_SOURCE_FLAGS:
        raise ValueError("source claim flags are not bounded to ACT-A2 allowed true flags")
    if artifact_classes != EXPECTED_ARTIFACT_CLASSES:
        raise ValueError("ACT-A1 artifact class drift")
    if contract["summary"]["sourceRuntimeControl"] != obligations["summary"]["sourceRuntimeControl"]:
        raise ValueError("runtime control boundary drift")
    if contract["summary"]["sourcePublicStatus"] != obligations["summary"]["sourcePublicStatus"]:
        raise ValueError("public status drift")
    if obligations["summary"]["soundnessProved"] is not False:
        raise ValueError("source soundness claim escalation")
    if obligations["summary"]["publicReady"] is not False:
        raise ValueError("source public-ready claim escalation")
    if obligations["summary"]["runtimeLoweringChanged"] is not False:
        raise ValueError("source runtime claim escalation")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    contract = a1.build_payload(atlas_gate_path)
    a1.validate_payload(contract)
    obligations = a2.build_payload(atlas_gate_path)
    a2.validate_payload(obligations)
    checks = dry_run_checks(contract, obligations)
    summary = {
        "sourceContract": contract["artifactId"],
        "sourceObligationsPacket": obligations["artifactId"],
        "sourceValidatorObligationCount": obligations["summary"]["validatorObligationCount"],
        "sourceFailureModeCount": obligations["summary"]["failureModeCount"],
        "dryRunCheckCount": len(checks),
        "dryRunPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "dryRunRejectCount": sum(len(check["rejectedFailureModes"]) for check in checks),
        "alphaDryRunCheckCount": sum(1 for check in checks if check["operator"] == "alpha"),
        "gammaDryRunCheckCount": sum(1 for check in checks if check["operator"] == "gamma"),
        "roundtripDryRunCheckCount": sum(1 for check in checks if check["operator"] == "alpha_gamma_roundtrip"),
        "sourceCheckedStatement": contract["summary"]["sourceCheckedStatement"],
        "sourceRuntimeControl": contract["summary"]["sourceRuntimeControl"],
        "sourcePublicStatus": contract["summary"]["sourcePublicStatus"],
        "dryRunValidatorSkeletonRecorded": True,
        "actA2ObligationsConsumed": True,
        "alphaChecksDryRun": True,
        "gammaChecksDryRun": True,
        "roundtripChecksDryRun": True,
        "validatorSkeletonImplemented": True,
        "dryRunExecuted": True,
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
        "nextAction": "GB-VIS-A1 seed claim topology renderer or ACT-A4 expand dry-run validator fixtures without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "dry_run_validator_skeleton_recorded",
                "act_a2_obligations_consumed",
                "alpha_checks_dry_run",
                "gamma_checks_dry_run",
                "roundtrip_checks_dry_run",
                "validator_skeleton_implemented",
                "dry_run_executed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "dry_run_validator_skeleton_recorded",
                "act_a2_obligations_consumed",
                "alpha_checks_dry_run",
                "gamma_checks_dry_run",
                "roundtrip_checks_dry_run",
                "validator_skeleton_implemented",
                "dry_run_executed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_dry_run_validator_skeleton_v0",
        "artifactId": "act-a3-alpha-gamma-dry-run-validator-skeleton",
        "status": STATUS,
        "decision": "execute_alpha_gamma_dry_run_validator_skeleton_no_production_validator_no_soundness_claim",
        "date": DATE,
        "sourceContract": contract["artifactId"],
        "sourceObligationsPacket": obligations["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "dryRunChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceContract"] != "act-a1-abstract-concrete-trace-contract":
        raise ValueError("ACT-A3 must retain ACT-A1 source contract")
    if payload["sourceObligationsPacket"] != "act-a2-alpha-gamma-validator-obligations":
        raise ValueError("ACT-A3 must consume ACT-A2")
    if summary["sourceValidatorObligationCount"] != 6:
        raise ValueError("unexpected source obligation count")
    if summary["sourceFailureModeCount"] != 5:
        raise ValueError("unexpected source failure mode count")
    if summary["dryRunCheckCount"] != 6:
        raise ValueError("unexpected dry-run check count")
    if summary["dryRunPassCount"] != 6:
        raise ValueError("unexpected dry-run pass count")
    if summary["dryRunRejectCount"] != 0:
        raise ValueError("dry-run should not reject the ACT-A2/A1 seed fixture")
    if summary["alphaDryRunCheckCount"] != 3:
        raise ValueError("unexpected alpha dry-run count")
    if summary["gammaDryRunCheckCount"] != 2:
        raise ValueError("unexpected gamma dry-run count")
    if summary["roundtripDryRunCheckCount"] != 1:
        raise ValueError("unexpected roundtrip dry-run count")
    if summary["sourceCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("source checked statement drift")
    if summary["sourceRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("source runtime drift")
    if summary["sourcePublicStatus"] != "held_private":
        raise ValueError("source public status drift")
    for key in [
        "dryRunValidatorSkeletonRecorded",
        "actA2ObligationsConsumed",
        "alphaChecksDryRun",
        "gammaChecksDryRun",
        "roundtripChecksDryRun",
        "validatorSkeletonImplemented",
        "dryRunExecuted",
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
        "dry_run_validator_skeleton_recorded",
        "act_a2_obligations_consumed",
        "alpha_checks_dry_run",
        "gamma_checks_dry_run",
        "roundtrip_checks_dry_run",
        "validator_skeleton_implemented",
        "dry_run_executed",
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
        "artifactType": "alpha_gamma_dry_run_validator_skeleton",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_dry_run_validator_skeleton_no_production_validator_no_soundness_proof",
        "source": f"python/results/act_a3_alpha_gamma_dry_run_validator_skeleton/act_a3_alpha_gamma_dry_run_validator_skeleton_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a3_alpha_gamma_dry_run_validator_skeleton_feed",
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
        "# ACT-A3 Alpha Gamma Dry-Run Validator Skeleton",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A3 executes a private dry-run validator skeleton over the ACT-A2 obligations and ACT-A1 worked example.",
        "",
        "| Check | Operator | Status |",
        "|---|---|---|",
    ]
    for check in payload["dryRunChecks"]:
        lines.append(f"| `{check['checkId']}` | `{check['operator']}` | `{check['status']}` |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- source validator obligations: `{payload['summary']['sourceValidatorObligationCount']}`",
            f"- dry-run checks: `{payload['summary']['dryRunCheckCount']}`",
            f"- dry-run passes: `{payload['summary']['dryRunPassCount']}`",
            f"- dry-run rejects: `{payload['summary']['dryRunRejectCount']}`",
            f"- production validator implemented: `{payload['summary']['productionValidatorImplemented']}`",
            f"- validator soundness proved: `{payload['summary']['validatorSoundnessProved']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"act_a3_alpha_gamma_dry_run_validator_skeleton_{STAMP}.json"
    report_path = report_dir / f"act_a3_alpha_gamma_dry_run_validator_skeleton_{STAMP}.md"
    evidence_path = evidence_dir / "act_a3_alpha_gamma_dry_run_validator_skeleton.json"
    feed_path = command_feed_dir / f"act_a3_alpha_gamma_dry_run_validator_skeleton_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a3_alpha_gamma_dry_run_validator_skeleton")
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
    print("ACT_A3_ALPHA_GAMMA_DRY_RUN_VALIDATOR_SKELETON_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
