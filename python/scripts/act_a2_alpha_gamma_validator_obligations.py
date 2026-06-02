#!/usr/bin/env python3
"""ACT-A2 alpha/gamma validator obligations packet."""

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

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.alpha_gamma_validator_obligations.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A2_ALPHA_GAMMA_VALIDATOR_OBLIGATIONS_PASS"

CLAIM_FLAGS = {
    "validator_obligations_recorded": True,
    "alpha_validator_requirements_defined": True,
    "gamma_validator_requirements_defined": True,
    "failure_modes_defined": True,
    "validator_implemented": False,
    "validator_executed": False,
    "soundness_proved": False,
    "full_galois_connection_claim": False,
    "abstract_interpretation_soundness_proved": False,
    "visualization_started": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "runtime_lowering_changed": False,
    "implementation_started": False,
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
    "ACT-A2 records validator obligations and failure modes only; it does not implement or execute an alpha/gamma validator.",
    "ACT-A2 does not prove soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "ACT-A2 does not update public surfaces, runtime behavior, MachLib, visualization tooling, laptop-owned repos, or electronics repos.",
]


def validator_obligations() -> list[dict[str, Any]]:
    return [
        {
            "obligationId": "alpha_source_identity_required",
            "operator": "alpha",
            "requirement": "A concrete artifact must expose artifactId, artifactType, source path, validation status, and claim flags before alpha may map it.",
            "rejectIf": ["missing_artifact_id", "missing_source_path", "missing_claim_flags", "unknown_artifact_type"],
        },
        {
            "obligationId": "alpha_claim_strength_bounded",
            "operator": "alpha",
            "requirement": "The abstract claim object must not raise claim strength beyond the source concrete artifact and frozen caveats.",
            "rejectIf": ["claim_flag_escalation", "public_ready_without_gate", "runtime_claim_without_control"],
        },
        {
            "obligationId": "alpha_traceability_complete",
            "operator": "alpha",
            "requirement": "The abstract claim object must retain evidence links, guards, caveats, blocked phrases, non-claims, and reviewer status.",
            "rejectIf": ["missing_evidence_link", "missing_caveats", "missing_blocked_phrases", "missing_non_claims"],
        },
        {
            "obligationId": "gamma_admissible_artifact_class",
            "operator": "gamma",
            "requirement": "Every admitted concrete artifact must belong to an ACT-A1 artifact class and satisfy that class's required fields.",
            "rejectIf": ["unknown_gamma_artifact_class", "required_field_missing", "wrong_lane_owner"],
        },
        {
            "obligationId": "gamma_boundary_preservation",
            "operator": "gamma",
            "requirement": "Concretions must preserve public/private status, runtime-control boundary, guard obligations, and blocked phrases.",
            "rejectIf": ["public_status_drift", "runtime_control_drift", "guard_drift", "blocked_phrase_drift"],
        },
        {
            "obligationId": "roundtrip_no_claim_escalation",
            "operator": "alpha_gamma_roundtrip",
            "requirement": "For a future validator, alpha(gamma(a)) may be weaker than a but must not be stronger than a.",
            "rejectIf": ["roundtrip_claim_escalation", "roundtrip_public_promotion", "roundtrip_runtime_advantage"],
        },
    ]


def failure_modes() -> list[dict[str, Any]]:
    return [
        {
            "failureModeId": "claim_flag_escalation",
            "severity": "block",
            "description": "A mapped abstract object or admitted concretion turns a false claim flag true without a selected gate.",
        },
        {
            "failureModeId": "trace_gap",
            "severity": "block",
            "description": "A claim object lacks concrete evidence links, caveats, guards, blocked phrases, or non-claims.",
        },
        {
            "failureModeId": "public_gate_bypass",
            "severity": "block",
            "description": "A public-ready or public-copy claim appears without an explicit human-approved public gate.",
        },
        {
            "failureModeId": "runtime_control_drift",
            "severity": "block",
            "description": "A concretion changes the runtime-control boundary or implies runtime advantage without separate evidence.",
        },
        {
            "failureModeId": "lane_owner_drift",
            "severity": "block",
            "description": "An admitted concrete artifact touches a laptop-owned or electronics-owned lane without explicit intake.",
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    contract = a1.build_payload(atlas_gate_path)
    a1.validate_payload(contract)
    obligations = validator_obligations()
    modes = failure_modes()
    summary = {
        "sourceContract": contract["artifactId"],
        "sourceOperatorCount": contract["summary"]["operatorCount"],
        "sourceArtifactClassCount": contract["summary"]["artifactClassCount"],
        "sourcePreservationObligationCount": contract["summary"]["preservationObligationCount"],
        "validatorObligationCount": len(obligations),
        "failureModeCount": len(modes),
        "alphaValidatorRequirementCount": sum(1 for item in obligations if item["operator"] == "alpha"),
        "gammaValidatorRequirementCount": sum(1 for item in obligations if item["operator"] == "gamma"),
        "roundtripRequirementCount": sum(1 for item in obligations if item["operator"] == "alpha_gamma_roundtrip"),
        "sourceCheckedStatement": contract["summary"]["sourceCheckedStatement"],
        "sourceRuntimeControl": contract["summary"]["sourceRuntimeControl"],
        "sourcePublicStatus": contract["summary"]["sourcePublicStatus"],
        "validatorObligationsRecorded": True,
        "alphaValidatorRequirementsDefined": True,
        "gammaValidatorRequirementsDefined": True,
        "failureModesDefined": True,
        "validatorImplemented": False,
        "validatorExecuted": False,
        "soundnessProved": False,
        "fullGaloisConnectionClaim": False,
        "abstractInterpretationSoundnessProved": False,
        "visualizationStarted": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "runtimeLoweringChanged": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "proofAttemptStarted": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "ACT-A3 implement a dry-run alpha/gamma validator skeleton or GB-VIS-A1 claim topology renderer seed without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "validator_obligations_recorded",
                "alpha_validator_requirements_defined",
                "gamma_validator_requirements_defined",
                "failure_modes_defined",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "validator_obligations_recorded",
                "alpha_validator_requirements_defined",
                "gamma_validator_requirements_defined",
                "failure_modes_defined",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "alpha_gamma_validator_obligations_v0",
        "artifactId": "act-a2-alpha-gamma-validator-obligations",
        "status": STATUS,
        "decision": "record_alpha_gamma_validator_obligations_no_validator_execution",
        "date": DATE,
        "sourceContract": contract["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "validatorObligations": obligations,
        "failureModes": modes,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceContract"] != "act-a1-abstract-concrete-trace-contract":
        raise ValueError("ACT-A2 must consume ACT-A1")
    if summary["sourceOperatorCount"] != 2:
        raise ValueError("source operator count drift")
    if summary["sourceArtifactClassCount"] != 4:
        raise ValueError("source artifact class count drift")
    if summary["sourcePreservationObligationCount"] != 5:
        raise ValueError("source preservation obligation count drift")
    if summary["validatorObligationCount"] != 6:
        raise ValueError("unexpected validator obligation count")
    if summary["failureModeCount"] != 5:
        raise ValueError("unexpected failure mode count")
    if summary["alphaValidatorRequirementCount"] != 3:
        raise ValueError("unexpected alpha requirement count")
    if summary["gammaValidatorRequirementCount"] != 2:
        raise ValueError("unexpected gamma requirement count")
    if summary["roundtripRequirementCount"] != 1:
        raise ValueError("unexpected roundtrip requirement count")
    if summary["sourceCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("source statement drift")
    if summary["sourceRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("source runtime drift")
    if summary["sourcePublicStatus"] != "held_private":
        raise ValueError("source public status drift")
    for key in [
        "validatorObligationsRecorded",
        "alphaValidatorRequirementsDefined",
        "gammaValidatorRequirementsDefined",
        "failureModesDefined",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "validatorImplemented",
        "validatorExecuted",
        "soundnessProved",
        "fullGaloisConnectionClaim",
        "abstractInterpretationSoundnessProved",
        "visualizationStarted",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "runtimeLoweringChanged",
        "implementationStarted",
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
    for key in [
        "validator_obligations_recorded",
        "alpha_validator_requirements_defined",
        "gamma_validator_requirements_defined",
        "failure_modes_defined",
    ]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {
            "validator_obligations_recorded",
            "alpha_validator_requirements_defined",
            "gamma_validator_requirements_defined",
            "failure_modes_defined",
        } and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "alpha_gamma_validator_obligations",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_validator_obligations_no_validator_execution_no_soundness_proof",
        "source": f"python/results/act_a2_alpha_gamma_validator_obligations/act_a2_alpha_gamma_validator_obligations_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a2_alpha_gamma_validator_obligations_feed",
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
        "# ACT-A2 Alpha Gamma Validator Obligations",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A2 records first validator obligations for the ACT alpha/gamma contract without implementing or executing a validator.",
        "",
        "| Obligation | Operator |",
        "|---|---|",
    ]
    for obligation in payload["validatorObligations"]:
        lines.append(f"| `{obligation['obligationId']}` | `{obligation['operator']}` |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- validator obligations: `{payload['summary']['validatorObligationCount']}`",
            f"- failure modes: `{payload['summary']['failureModeCount']}`",
            f"- alpha requirements: `{payload['summary']['alphaValidatorRequirementCount']}`",
            f"- gamma requirements: `{payload['summary']['gammaValidatorRequirementCount']}`",
            f"- validator implemented: `{payload['summary']['validatorImplemented']}`",
            f"- soundness proved: `{payload['summary']['soundnessProved']}`",
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
    result_path = out_dir / f"act_a2_alpha_gamma_validator_obligations_{STAMP}.json"
    report_path = report_dir / f"act_a2_alpha_gamma_validator_obligations_{STAMP}.md"
    evidence_path = evidence_dir / "act_a2_alpha_gamma_validator_obligations.json"
    feed_path = command_feed_dir / f"act_a2_alpha_gamma_validator_obligations_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a2_alpha_gamma_validator_obligations")
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
    print("ACT_A2_ALPHA_GAMMA_VALIDATOR_OBLIGATIONS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
