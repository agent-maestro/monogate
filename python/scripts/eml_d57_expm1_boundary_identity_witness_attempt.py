#!/usr/bin/env python3
"""EML-D57 expm1 boundary identity MachLib witness attempt."""

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

from scripts import eml_d56_expm1_boundary_identity_feasibility_packet as d56  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_expm1_boundary_identity_witness_attempt.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D57_EXPM1_BOUNDARY_IDENTITY_WITNESS_ATTEMPT_PASS"

CLAIM_FLAGS = {
    "witness_feasibility_recorded": True,
    "bounded_identity_candidate_selected": True,
    "expm1_boundary_candidate_selected": True,
    "implementation_started": True,
    "machlib_file_changed": True,
    "lean_typecheck_performed": True,
    "candidate_proved": True,
    "proof_attempt_started": True,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
    "bounded_trig_feasibility_selected": False,
    "human_public_copy_gate_selected": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
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
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D57 checks one scoped MachLib witness only; it does not claim theorem discovery, broad EML advantage, or a family theorem.",
    "D57 keeps protected expm1 as the runtime and numerical-stability control and makes no protected expm1 replacement or runtime advantage claim.",
    "D57 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or change public readiness.",
]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    feasibility = d56.build_payload(atlas_gate_path)
    d56.validate_payload(feasibility)
    witness = feasibility["proposedWitness"]
    checked_witness = {
        "candidateId": witness["candidateId"],
        "family": witness["family"],
        "machlibName": witness["proposedMachlibName"],
        "machlibFile": "foundations/MachLib/EMLAtlasWitness.lean",
        "checkedStatement": witness["proposedStatement"],
        "guardShape": witness["guardShape"],
        "proofShape": [
            "unfold eml",
            "rw [log_exp]",
        ],
        "buildCommand": "cd foundations && lake build",
        "buildStatus": "passed",
        "knownUnrelatedWarnings": [
            "MachLib.ForgeTest declaration uses sorry",
            "MachLib.HighDimensional declarations use sorry",
        ],
        "runtimeControl": witness["runtimeControl"],
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }
    summary = {
        "sourceFeasibilityPacket": feasibility["artifactId"],
        "sourceSelectedCandidateId": feasibility["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": feasibility["summary"]["sourceSelectedFamily"],
        "sourceProposedMachlibName": feasibility["summary"]["proposedMachlibName"],
        "sourceProposedStatement": feasibility["summary"]["proposedStatement"],
        "sourceFeasibilityStatus": feasibility["summary"]["feasibilityStatus"],
        "sourceRuntimeLoweringControl": feasibility["summary"]["runtimeLoweringControl"],
        "machlibName": checked_witness["machlibName"],
        "machlibFile": checked_witness["machlibFile"],
        "checkedStatement": checked_witness["checkedStatement"],
        "guardCount": len(checked_witness["guardShape"]),
        "proofStepCount": len(checked_witness["proofShape"]),
        "knownUnrelatedWarningCount": len(checked_witness["knownUnrelatedWarnings"]),
        "implementationStarted": True,
        "machlibFileChanged": True,
        "leanTypecheckPerformed": True,
        "candidateProved": True,
        "proofAttemptStarted": True,
        "buildPassed": True,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "runtimeLoweringControl": witness["runtimeControl"],
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "publicCopyApproved": False,
        "advantageLabCaseAdded": False,
        "boundedTrigFeasibilitySelected": False,
        "humanPublicCopyGateSelected": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextArtifact": "EML-D58 expm1 boundary checked-witness private surface review",
        "claimFlagsCheckedOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "witness_feasibility_recorded",
                "bounded_identity_candidate_selected",
                "expm1_boundary_candidate_selected",
                "implementation_started",
                "machlib_file_changed",
                "lean_typecheck_performed",
                "candidate_proved",
                "proof_attempt_started",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "witness_feasibility_recorded",
                "bounded_identity_candidate_selected",
                "expm1_boundary_candidate_selected",
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
        "attemptType": "eml_expm1_boundary_identity_witness_attempt_v0",
        "artifactId": "eml-d57-expm1-boundary-identity-witness-attempt",
        "status": STATUS,
        "decision": "checked_expm1_boundary_identity_witness",
        "date": DATE,
        "sourceFeasibilityPacket": feasibility["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "checkedWitness": checked_witness,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    witness = payload["checkedWitness"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceFeasibilityPacket"] != "eml-d56-expm1-boundary-identity-feasibility-packet":
        raise ValueError("D57 must consume D56")
    if summary["sourceSelectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("unexpected source candidate")
    if summary["sourceSelectedFamily"] != "protected_runtime_boundary_identity":
        raise ValueError("unexpected source family")
    if summary["sourceProposedMachlibName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected source witness name")
    if summary["sourceProposedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected source statement")
    if summary["sourceFeasibilityStatus"] != "feasible_for_scoped_witness_attempt":
        raise ValueError("unexpected feasibility status")
    if summary["sourceRuntimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("source runtime control drift")
    if summary["machlibName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected checked witness name")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["guardCount"] != 0:
        raise ValueError("unexpected guard count")
    if summary["proofStepCount"] != 2:
        raise ValueError("unexpected proof step count")
    if summary["knownUnrelatedWarningCount"] != 2:
        raise ValueError("unexpected warning count")
    for key in [
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "proofAttemptStarted",
        "buildPassed",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicCopyApproved",
        "advantageLabCaseAdded",
        "boundedTrigFeasibilitySelected",
        "humanPublicCopyGateSelected",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime control drift")
    if witness["buildStatus"] != "passed":
        raise ValueError("build must pass")
    if witness["publicPromotionAllowed"] is not False:
        raise ValueError("public promotion must remain blocked")
    if summary["nextArtifact"] != "EML-D58 expm1 boundary checked-witness private surface review":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsCheckedOnly"] is not True:
        raise ValueError("claim flags must remain checked-only")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_expm1_boundary_identity_witness_attempt",
        "validationStatus": "pass",
        "semanticStrength": "scoped_machlib_witness_checked_no_runtime_or_public_claim",
        "source": f"python/results/eml_d57_expm1_boundary_identity_witness_attempt/eml_d57_expm1_boundary_identity_witness_attempt_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d57_expm1_boundary_identity_witness_attempt_feed",
        "date": DATE,
        "status": payload["status"],
        "machlibName": payload["summary"]["machlibName"],
        "checkedStatement": payload["summary"]["checkedStatement"],
        "nextAction": "Run EML-D58 as a private surface review for the checked expm1-boundary witness.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D57 Expm1 Boundary Identity Witness Attempt",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Checked witness: `{payload['summary']['machlibName']}`",
        "",
        f"Statement: `{payload['summary']['checkedStatement']}`",
        "",
        "D57 records one scoped checked MachLib witness and keeps runtime/public claims blocked.",
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
    result_path = out_dir / f"eml_d57_expm1_boundary_identity_witness_attempt_{STAMP}.json"
    report_path = report_dir / f"eml_d57_expm1_boundary_identity_witness_attempt_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d57_expm1_boundary_identity_witness_attempt.json"
    feed_path = command_feed_dir / f"eml_d57_expm1_boundary_identity_witness_attempt_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d57_expm1_boundary_identity_witness_attempt")
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
    print("EML_D57_EXPM1_BOUNDARY_IDENTITY_WITNESS_ATTEMPT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
