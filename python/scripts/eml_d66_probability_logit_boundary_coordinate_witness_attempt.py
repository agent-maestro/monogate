#!/usr/bin/env python3
"""EML-D66 probability logit boundary coordinate MachLib witness attempt."""

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

from scripts import eml_d65_probability_logit_boundary_coordinate_feasibility_packet as d65  # noqa: E402

DATE = "2026-06-03"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_probability_logit_boundary_coordinate_witness_attempt.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D66_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_WITNESS_ATTEMPT_PASS"

CLAIM_FLAGS = {
    "witness_feasibility_recorded": True,
    "bounded_identity_candidate_selected": True,
    "probability_logit_boundary_candidate_selected": True,
    "guarded_domain_obligations_recorded": True,
    "negative_controls_recorded": True,
    "implementation_started": True,
    "machlib_file_changed": True,
    "lean_typecheck_performed": True,
    "candidate_proved": True,
    "proof_attempt_started": True,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_log_replacement_claim": False,
    "protected_log1p_replacement_claim": False,
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
    "EML-D66 checks one scoped guarded MachLib witness only; it does not claim theorem discovery, broad probability/logit theory, or broad EML advantage.",
    "D66 keeps protected log/log1p controls as runtime controls and makes no log, log1p, logit, or runtime replacement claim.",
    "D66 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim runtime performance, compiler correctness, formal equivalence, full EML semantics, or public readiness.",
]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    feasibility = d65.build_payload(atlas_gate_path)
    d65.validate_payload(feasibility)
    witness = feasibility["proposedWitness"]
    checked_witness = {
        "candidateId": witness["candidateId"],
        "family": witness["family"],
        "machlibName": witness["proposedMachlibName"],
        "machlibFile": "foundations/MachLib/EMLAtlasWitness.lean",
        "checkedStatement": witness["proposedStatement"],
        "guardShape": witness["guardShape"],
        "derivedDomainObligations": witness["derivedDomainObligations"],
        "proofShape": [
            "retain p < 1 as explicit domain guard",
            "unfold eml",
            "rewrite exp (log p) to p using 0 < p",
            "rewrite log (exp (log (1 - p))) to log (1 - p)",
        ],
        "buildCommand": "cd foundations && lake build",
        "buildStatus": "passed",
        "knownUnrelatedWarnings": [
            "MachLib.ForgeTest declaration uses sorry",
            "MachLib.HighDimensional declaration uses sorry at line 377",
            "MachLib.HighDimensional declaration uses sorry at line 394",
        ],
        "runtimeControl": witness["runtimeControl"],
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }
    summary = {
        "sourceFeasibilityPacket": feasibility["artifactId"],
        "sourceSelectedCandidateId": feasibility["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": feasibility["summary"]["sourceSelectedFamily"],
        "sourceSelectedSourceFrontierId": feasibility["summary"]["sourceSelectedSourceFrontierId"],
        "sourceProposedMachlibName": feasibility["summary"]["proposedMachlibName"],
        "sourceProposedStatement": feasibility["summary"]["proposedStatement"],
        "sourceFeasibilityStatus": feasibility["summary"]["feasibilityStatus"],
        "sourceGuardCount": feasibility["summary"]["guardCount"],
        "sourceDerivedDomainObligationCount": feasibility["summary"]["derivedDomainObligationCount"],
        "sourceNegativeControlCount": feasibility["summary"]["negativeControlCount"],
        "sourceBlockerCount": feasibility["summary"]["blockerCount"],
        "sourceRuntimeLoweringControl": feasibility["summary"]["runtimeLoweringControl"],
        "machlibName": checked_witness["machlibName"],
        "machlibFile": checked_witness["machlibFile"],
        "checkedStatement": checked_witness["checkedStatement"],
        "guardCount": len(checked_witness["guardShape"]),
        "derivedDomainObligationCount": len(checked_witness["derivedDomainObligations"]),
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
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
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
        "nextArtifact": "EML-D67 probability logit checked-witness private surface review",
        "claimFlagsCheckedOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "witness_feasibility_recorded",
                "bounded_identity_candidate_selected",
                "probability_logit_boundary_candidate_selected",
                "guarded_domain_obligations_recorded",
                "negative_controls_recorded",
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
                "probability_logit_boundary_candidate_selected",
                "guarded_domain_obligations_recorded",
                "negative_controls_recorded",
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
        "attemptType": "eml_probability_logit_boundary_coordinate_witness_attempt_v0",
        "artifactId": "eml-d66-probability-logit-boundary-coordinate-witness-attempt",
        "status": STATUS,
        "decision": "checked_probability_logit_boundary_coordinate_witness",
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
    if payload["sourceFeasibilityPacket"] != "eml-d65-probability-logit-boundary-coordinate-feasibility-packet":
        raise ValueError("D66 must consume D65")
    if summary["sourceSelectedCandidateId"] != "probability_logit_boundary_coordinate":
        raise ValueError("unexpected source candidate")
    if summary["sourceSelectedFamily"] != "guarded_probability_log_coordinate":
        raise ValueError("unexpected source family")
    if summary["sourceSelectedSourceFrontierId"] != "probability_logit_boundary_v0":
        raise ValueError("unexpected source frontier id")
    if summary["sourceProposedMachlibName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
        raise ValueError("unexpected source witness name")
    if summary["sourceProposedStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected source statement")
    if summary["sourceFeasibilityStatus"] != "feasible_for_guarded_scoped_witness_attempt":
        raise ValueError("unexpected feasibility status")
    if summary["sourceGuardCount"] != 2 or summary["sourceDerivedDomainObligationCount"] != 2:
        raise ValueError("source guard counts drifted")
    if summary["sourceNegativeControlCount"] != 4 or summary["sourceBlockerCount"] != 4:
        raise ValueError("source control/blocker counts drifted")
    if summary["sourceRuntimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("source runtime control drift")
    if summary["machlibName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
        raise ValueError("unexpected checked witness name")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    if summary["checkedStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected checked statement")
    if witness["guardShape"] != ["0 < p", "p < 1"]:
        raise ValueError("unexpected guard shape")
    if witness["derivedDomainObligations"] != ["0 < p", "0 < 1 - p"]:
        raise ValueError("unexpected derived obligations")
    if summary["guardCount"] != 2:
        raise ValueError("unexpected guard count")
    if summary["derivedDomainObligationCount"] != 2:
        raise ValueError("unexpected derived obligation count")
    if summary["proofStepCount"] != 4:
        raise ValueError("unexpected proof step count")
    if summary["knownUnrelatedWarningCount"] != 3:
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
        "protectedLogReplacementClaim",
        "protectedLog1pReplacementClaim",
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
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime control drift")
    if summary["nextArtifact"] != "EML-D67 probability logit checked-witness private surface review":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsCheckedOnly"] is not True:
        raise ValueError("claim flags must remain checked-only")
    for key in [
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "probability_logit_boundary_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
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
            "witness_feasibility_recorded",
            "bounded_identity_candidate_selected",
            "probability_logit_boundary_candidate_selected",
            "guarded_domain_obligations_recorded",
            "negative_controls_recorded",
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
        "artifactType": "eml_probability_logit_boundary_coordinate_witness_attempt",
        "validationStatus": "pass",
        "semanticStrength": "private_checked_guarded_machlib_witness_no_runtime_or_public_claim",
        "source": f"python/results/eml_d66_probability_logit_boundary_coordinate_witness_attempt/eml_d66_probability_logit_boundary_coordinate_witness_attempt_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d66_probability_logit_boundary_coordinate_witness_attempt_feed",
        "date": DATE,
        "status": payload["status"],
        "machlibName": payload["summary"]["machlibName"],
        "checkedStatement": payload["summary"]["checkedStatement"],
        "buildStatus": payload["checkedWitness"]["buildStatus"],
        "nextAction": "Run EML-D67 as a private checked-witness surface review; do not promote public copy.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D66 Probability Logit Boundary Coordinate Witness Attempt",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Checked witness: `{payload['summary']['machlibName']}`",
        "",
        f"Statement: `{payload['summary']['checkedStatement']}`",
        "",
        "D66 checks one guarded MachLib witness after the D65 feasibility packet.",
        "",
        "## Summary",
        "",
        f"- source feasibility: `{payload['summary']['sourceFeasibilityPacket']}`",
        f"- guard count: `{payload['summary']['guardCount']}`",
        f"- proof step count: `{payload['summary']['proofStepCount']}`",
        f"- build passed: `{payload['summary']['buildPassed']}`",
        f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
        f"- public ready: `{payload['summary']['publicReady']}`",
        "",
        "## Known Unrelated Warnings",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["checkedWitness"]["knownUnrelatedWarnings"])
    lines.extend(
        [
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
    result_path = out_dir / f"eml_d66_probability_logit_boundary_coordinate_witness_attempt_{STAMP}.json"
    report_path = report_dir / f"eml_d66_probability_logit_boundary_coordinate_witness_attempt_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d66_probability_logit_boundary_coordinate_witness_attempt.json"
    feed_path = command_feed_dir / f"eml_d66_probability_logit_boundary_coordinate_witness_attempt_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d66_probability_logit_boundary_coordinate_witness_attempt")
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
    print("EML_D66_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_WITNESS_ATTEMPT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
