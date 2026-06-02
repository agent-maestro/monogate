#!/usr/bin/env python3
"""ACT-A1 abstract/concrete trace contract seed packet."""

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

from scripts import eml_d62_expm1_boundary_branch_pause_freeze_packet as d62  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.abstract_concrete_trace_contract.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "ACT_A1_ABSTRACT_CONCRETE_TRACE_CONTRACT_PASS"

CLAIM_FLAGS = {
    "contract_seed_recorded": True,
    "alpha_operator_defined": True,
    "gamma_operator_defined": True,
    "d62_example_bound": True,
    "visualization_started": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "runtime_lowering_changed": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "proof_attempt_started": False,
    "candidate_proved": False,
    "full_galois_connection_claim": False,
    "abstract_interpretation_soundness_proved": False,
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
    "ACT-A1 records a seed contract for abstract/concrete trace semantics; it does not prove a Galois connection or full abstract interpretation soundness.",
    "ACT-A1 defines operator roles, admissible artifact classes, and preservation obligations only; it does not implement visualization, runtime lowering, compiler behavior, or public copy.",
    "ACT-A1 uses the D57-D62 expm1-boundary chain as a worked private example without editing MachLib, typechecking Lean, consuming laptop artifacts, touching laptop-owned repos, or claiming theorem discovery or broad EML superiority.",
]


def operator_definitions() -> list[dict[str, Any]]:
    return [
        {
            "operator": "alpha",
            "spelling": "alpha : ConcreteArtifact -> AbstractClaimObject",
            "role": "abstraction",
            "description": "Maps a concrete artifact into a bounded abstract claim object with evidence, guards, caveats, blocked phrases, and non-claims.",
            "mustPreserve": [
                "artifact identity and source path",
                "claim flags and non-claims",
                "guards and domain restrictions",
                "verification status and reviewer outcome",
                "blocked phrases and public/private status",
            ],
        },
        {
            "operator": "gamma",
            "spelling": "gamma : AbstractClaimObject -> AdmissibleConcreteArtifacts",
            "role": "concretion",
            "description": "Maps an abstract claim object to the concrete artifacts allowed to count as evidence or realization for that claim.",
            "mustPreserve": [
                "allowed artifact classes",
                "required fields and guard obligations",
                "maximum claim strength",
                "traceability back to evidence packets",
                "public-copy and runtime-control boundaries",
            ],
        },
    ]


def artifact_classes() -> list[dict[str, Any]]:
    return [
        {
            "classId": "lean_checked_witness",
            "examples": ["MachLib theorem", "Lean build result"],
            "alphaOutput": "checked_witness_claim_object",
            "gammaAdmits": ["Lean theorem reference", "build log", "proof-source path"],
        },
        {
            "classId": "evidence_packet",
            "examples": ["D57-D62 JSON", "Command Center feed", "review report"],
            "alphaOutput": "claim_boundary_packet",
            "gammaAdmits": ["result JSON", "evidence packet", "feed", "report"],
        },
        {
            "classId": "runtime_trace",
            "examples": ["future bounded runtime trace", "comparison packet"],
            "alphaOutput": "bounded_runtime_observation",
            "gammaAdmits": ["trace rows", "comparison method", "error bound"],
        },
        {
            "classId": "lesson_or_hardware_artifact",
            "examples": ["course packet", "simulated lesson", "future live capture"],
            "alphaOutput": "reviewable_teaching_or_capture_claim",
            "gammaAdmits": ["laptop-agent packet only after intake validation"],
        },
    ]


def preservation_obligations() -> list[dict[str, Any]]:
    return [
        {
            "obligationId": "soundness_of_claim_strength",
            "rule": "alpha(c) may not support a claim stronger than the concrete artifact c records.",
            "blockedIf": ["missing evidence source", "claim flag overreach", "unreviewed public copy"],
        },
        {
            "obligationId": "traceability",
            "rule": "Every abstract claim must point to concrete evidence, guard/caveat records, non-claims, and blocked phrases.",
            "blockedIf": ["missing artifact id", "missing source path", "missing caveat list"],
        },
        {
            "obligationId": "concretion_admissibility",
            "rule": "gamma(a) admits only concrete artifacts that satisfy the frozen caveats and required fields of a.",
            "blockedIf": ["wrong artifact class", "missing guard", "runtime/public boundary drift"],
        },
        {
            "obligationId": "bounded_error_or_guard_record",
            "rule": "Numeric or runtime claims require explicit guard, error, comparison, or control records.",
            "blockedIf": ["runtime advantage phrase without evidence", "missing error bound", "missing control"],
        },
        {
            "obligationId": "public_copy_gate",
            "rule": "Public copy remains inadmissible unless a separate human-approved public gate records approval.",
            "blockedIf": ["public_ready true", "public surface update", "missing human approval"],
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    freeze = d62.build_payload(atlas_gate_path)
    d62.validate_payload(freeze)
    example = {
        "exampleId": "d57_d62_expm1_boundary_private_chain",
        "sourceFreezePacket": freeze["artifactId"],
        "concreteArtifacts": [
            "MachLib.Real.expm1_boundary_identity_witness",
            "python/results/eml_d62_expm1_boundary_branch_pause_freeze_packet/eml_d62_expm1_boundary_branch_pause_freeze_packet_2026_06_02.json",
            "reports/evidence_packets/eml_d62_expm1_boundary_branch_pause_freeze_packet.json",
            "command_center_feeds/eml_d62_expm1_boundary_branch_pause_freeze_packet_feed_2026_06_02.json",
        ],
        "alphaResult": {
            "abstractClaimObjectId": "expm1_boundary_checked_witness_private_claim",
            "checkedStatement": freeze["summary"]["checkedStatement"],
            "claimStrength": "private_checked_witness_copy_frozen",
            "runtimeControl": freeze["summary"]["runtimeLoweringControl"],
            "publicStatus": freeze["summary"]["publicAtlasStatus"],
        },
        "gammaAdmissibleConcrete": [
            "private evidence packet with D60 caveats and blockers preserved",
            "Lean witness reference with checked statement unchanged",
            "future public copy gate only with explicit human approval",
        ],
    }
    summary = {
        "operatorCount": 2,
        "artifactClassCount": len(artifact_classes()),
        "preservationObligationCount": len(preservation_obligations()),
        "workedExampleCount": 1,
        "sourceFreezePacket": freeze["artifactId"],
        "sourceCheckedStatement": freeze["summary"]["checkedStatement"],
        "sourceRuntimeControl": freeze["summary"]["runtimeLoweringControl"],
        "sourcePublicStatus": freeze["summary"]["publicAtlasStatus"],
        "contractSeedRecorded": True,
        "alphaOperatorDefined": True,
        "gammaOperatorDefined": True,
        "d62ExampleBound": True,
        "visualizationStarted": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "runtimeLoweringChanged": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "proofAttemptStarted": False,
        "fullGaloisConnectionClaim": False,
        "abstractInterpretationSoundnessProved": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "ACT-A2 define first alpha/gamma validator obligations or GB-VIS-A1 claim topology renderer seed without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in ["contract_seed_recorded", "alpha_operator_defined", "gamma_operator_defined", "d62_example_bound"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"contract_seed_recorded", "alpha_operator_defined", "gamma_operator_defined", "d62_example_bound"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "contractType": "abstract_concrete_trace_contract_v0",
        "artifactId": "act-a1-abstract-concrete-trace-contract",
        "status": STATUS,
        "decision": "record_alpha_gamma_trace_contract_seed_private_only",
        "date": DATE,
        "sourceFreezePacket": freeze["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "operators": operator_definitions(),
        "artifactClasses": artifact_classes(),
        "preservationObligations": preservation_obligations(),
        "workedExamples": [example],
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceFreezePacket"] != "eml-d62-expm1-boundary-branch-pause-freeze-packet":
        raise ValueError("ACT-A1 must consume D62")
    if summary["operatorCount"] != 2:
        raise ValueError("expected alpha and gamma")
    if summary["artifactClassCount"] != 4:
        raise ValueError("unexpected artifact class count")
    if summary["preservationObligationCount"] != 5:
        raise ValueError("unexpected preservation obligation count")
    if summary["sourceCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected source statement")
    if summary["sourceRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime control drift")
    if summary["sourcePublicStatus"] != "held_private":
        raise ValueError("public status drift")
    for key in ["contractSeedRecorded", "alphaOperatorDefined", "gammaOperatorDefined", "d62ExampleBound"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "visualizationStarted",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "runtimeLoweringChanged",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "proofAttemptStarted",
        "fullGaloisConnectionClaim",
        "abstractInterpretationSoundnessProved",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in ["contract_seed_recorded", "alpha_operator_defined", "gamma_operator_defined", "d62_example_bound"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"contract_seed_recorded", "alpha_operator_defined", "gamma_operator_defined", "d62_example_bound"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "abstract_concrete_trace_contract",
        "validationStatus": "pass",
        "semanticStrength": "private_alpha_gamma_trace_contract_seed_no_soundness_proof_no_public_update",
        "source": f"python/results/act_a1_abstract_concrete_trace_contract/act_a1_abstract_concrete_trace_contract_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "act_a1_abstract_concrete_trace_contract_feed",
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
        "# ACT-A1 Abstract Concrete Trace Contract",
        "",
        f"Status: `{payload['status']}`",
        "",
        "ACT-A1 records a private alpha/gamma trace contract seed for proof-carrying artifacts.",
        "",
        "| Operator | Role |",
        "|---|---|",
    ]
    for operator in payload["operators"]:
        lines.append(f"| `{operator['operator']}` | {operator['role']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- operators: `{payload['summary']['operatorCount']}`",
            f"- artifact classes: `{payload['summary']['artifactClassCount']}`",
            f"- preservation obligations: `{payload['summary']['preservationObligationCount']}`",
            f"- source checked statement: `{payload['summary']['sourceCheckedStatement']}`",
            f"- runtime control: `{payload['summary']['sourceRuntimeControl']}`",
            f"- public status: `{payload['summary']['sourcePublicStatus']}`",
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
    result_path = out_dir / f"act_a1_abstract_concrete_trace_contract_{STAMP}.json"
    report_path = report_dir / f"act_a1_abstract_concrete_trace_contract_{STAMP}.md"
    evidence_path = evidence_dir / "act_a1_abstract_concrete_trace_contract.json"
    feed_path = command_feed_dir / f"act_a1_abstract_concrete_trace_contract_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/act_a1_abstract_concrete_trace_contract")
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
    print("ACT_A1_ABSTRACT_CONCRETE_TRACE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
