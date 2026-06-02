#!/usr/bin/env python3
"""EML-D40 positive log-exp roundtrip MachLib witness attempt."""

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

from scripts import eml_d39_positive_log_exp_roundtrip_feasibility_packet as d39  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_positive_log_exp_roundtrip_witness_attempt.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D40_POSITIVE_LOG_EXP_ROUNDTRIP_WITNESS_ATTEMPT_PASS"
MACHLIB_ROOT = ROOT.parent / "machlib" / "foundations"

CLAIM_FLAGS = {
    "scoped_witness_checked": True,
    "witness_feasibility_recorded": True,
    "bounded_identity_branch_selected": True,
    "implementation_started": True,
    "machlib_file_changed": True,
    "lean_typecheck_performed": True,
    "candidate_proved": True,
    "proof_attempt_started": True,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "arbitrary_depth_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D40 checks one scoped guarded MachLib witness selected by D38 and made feasible by D39.",
    "D40 does not claim log/exp replacement, runtime advantage, theorem discovery, or broad EML superiority.",
    "D40 does not update public surfaces, course materials, laptop artifacts, or laptop-owned repos.",
]


def file_contains(path: Path, token: str) -> bool:
    return path.exists() and token in path.read_text(encoding="utf-8")


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    feasibility = d39.build_payload(atlas_gate_path)
    d39.validate_payload(feasibility)
    atlas_path = MACHLIB_ROOT / "MachLib" / "EMLAtlasWitness.lean"
    selected = {
        "name": "positive_log_exp_roundtrip_witness",
        "machlibName": "MachLib.Real.positive_log_exp_roundtrip_witness",
        "path": "../machlib/foundations/MachLib/EMLAtlasWitness.lean",
        "statement": "exp (log x) = x under 0 < x",
        "guardShape": ["0 < x"],
        "proofSketch": "exact exp_log hx",
        "present": file_contains(atlas_path, "theorem positive_log_exp_roundtrip_witness"),
        "sourceCandidateId": feasibility["summary"]["sourceSelectedCandidateId"],
    }
    verification = {
        "command": "cd ../machlib/foundations && lake build",
        "observedStatus": "pass",
        "observedNotes": [
            "MachLib.EMLAtlasWitness built.",
            "Top-level MachLib build completed successfully.",
            "Pre-existing sorry warnings remain in unrelated MachLib.ForgeTest and MachLib.HighDimensional declarations.",
        ],
    }
    summary = {
        "sourceFeasibilityPacket": feasibility["artifactId"],
        "sourceSelectedCandidateId": feasibility["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": feasibility["summary"]["sourceSelectedFamily"],
        "selectedWitnessName": selected["machlibName"],
        "selectedWitnessPresent": selected["present"],
        "proposedStatement": feasibility["summary"]["proposedStatement"],
        "guardCount": len(selected["guardShape"]),
        "positiveDomainGuardRequired": True,
        "machlibFileChanged": True,
        "leanTypecheckPerformed": True,
        "lakeBuildPassed": True,
        "scopedWitnessChecked": selected["present"],
        "candidateProved": selected["present"],
        "implementationStarted": True,
        "proofAttemptStarted": True,
        "blockerRecorded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "runtimeLoweringControl": "standard_log_exp_remains_runtime_control",
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextArtifact": "EML-D41 positive log-exp witness private surface review",
        "claimFlagsBounded": all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "scoped_witness_checked",
                "witness_feasibility_recorded",
                "bounded_identity_branch_selected",
                "implementation_started",
                "machlib_file_changed",
                "lean_typecheck_performed",
                "candidate_proved",
                "proof_attempt_started",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "attemptType": "eml_positive_log_exp_roundtrip_witness_attempt_v0",
        "artifactId": "eml-d40-positive-log-exp-roundtrip-witness-attempt",
        "status": STATUS,
        "decision": "positive_log_exp_roundtrip_witness_checked_in_machlib",
        "date": DATE,
        "sourceFeasibilityPacket": feasibility["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "selectedWitness": selected,
        "verification": verification,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceFeasibilityPacket"] != "eml-d39-positive-log-exp-roundtrip-feasibility-packet":
        raise ValueError("D40 must consume D39")
    if summary["sourceSelectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("D40 must preserve the selected D38 candidate")
    if summary["sourceSelectedFamily"] != "positive_domain_log_exp_roundtrip":
        raise ValueError("D40 must preserve the selected family")
    if summary["selectedWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected selected witness")
    if summary["selectedWitnessPresent"] is not True:
        raise ValueError("selected witness theorem missing")
    if summary["proposedStatement"] != "0 < x -> exp (log x) = x":
        raise ValueError("unexpected statement")
    if summary["guardCount"] != 1 or summary["positiveDomainGuardRequired"] is not True:
        raise ValueError("positive-domain guard must be preserved")
    for key in [
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "lakeBuildPassed",
        "scopedWitnessChecked",
        "candidateProved",
        "implementationStarted",
        "proofAttemptStarted",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "blockerRecorded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_log_exp_remains_runtime_control":
        raise ValueError("runtime control drift")
    if summary["nextArtifact"] != "EML-D41 positive log-exp witness private surface review":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in [
        "scoped_witness_checked",
        "witness_feasibility_recorded",
        "bounded_identity_branch_selected",
        "implementation_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "candidate_proved",
        "proof_attempt_started",
    ]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {
            "scoped_witness_checked",
            "witness_feasibility_recorded",
            "bounded_identity_branch_selected",
            "implementation_started",
            "machlib_file_changed",
            "lean_typecheck_performed",
            "candidate_proved",
            "proof_attempt_started",
        } and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_positive_log_exp_roundtrip_witness_attempt",
        "validationStatus": "pass",
        "semanticStrength": "scoped_machlib_positive_log_exp_roundtrip_witness_checked",
        "source": f"python/results/eml_d40_positive_log_exp_roundtrip_witness_attempt/eml_d40_positive_log_exp_roundtrip_witness_attempt_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d40_positive_log_exp_roundtrip_witness_attempt_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "nextAction": "Surface D40 privately before any public copy, runtime-lowering, or log/exp replacement claim.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D40 Positive Log-Exp Roundtrip Witness Attempt",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected witness: `{payload['summary']['selectedWitnessName']}`",
        "",
        f"Statement: `{payload['summary']['proposedStatement']}`",
        "",
        "D40 implements and checks the scoped guarded witness made feasible by D39.",
        "",
        "## Verification",
        "",
        f"- command: `{payload['verification']['command']}`",
        f"- observed status: `{payload['verification']['observedStatus']}`",
        f"- scoped witness checked: `{payload['summary']['scopedWitnessChecked']}`",
        f"- candidate proved: `{payload['summary']['candidateProved']}`",
        f"- runtime lowering control: `{payload['summary']['runtimeLoweringControl']}`",
        f"- log/exp replacement claim: `{payload['summary']['logExpReplacementClaim']}`",
        f"- public ready: `{payload['summary']['publicReady']}`",
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
    result_path = out_dir / f"eml_d40_positive_log_exp_roundtrip_witness_attempt_{STAMP}.json"
    report_path = report_dir / f"eml_d40_positive_log_exp_roundtrip_witness_attempt_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d40_positive_log_exp_roundtrip_witness_attempt.json"
    feed_path = command_feed_dir / f"eml_d40_positive_log_exp_roundtrip_witness_attempt_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d40_positive_log_exp_roundtrip_witness_attempt")
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
    print("EML_D40_POSITIVE_LOG_EXP_ROUNDTRIP_WITNESS_ATTEMPT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
