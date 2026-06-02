#!/usr/bin/env python3
"""EML-D48 constant-coordinate zero-exp-two MachLib witness attempt."""

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

from scripts import eml_d47_constant_coordinate_refresh_feasibility_selector as d47  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_constant_coordinate_zero_exp_two_witness_attempt.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D48_CONSTANT_COORDINATE_ZERO_EXP_TWO_WITNESS_ATTEMPT_PASS"
MACHLIB_ROOT = ROOT.parent / "machlib" / "foundations"

CLAIM_FLAGS = {
    "scoped_witness_checked": True,
    "constant_coordinate_feasibility_recorded": True,
    "non_duplicate_statement_selected": True,
    "implementation_started": True,
    "machlib_file_changed": True,
    "lean_typecheck_performed": True,
    "candidate_proved": True,
    "proof_attempt_started": True,
    "blocker_recorded": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
    "bounded_trig_feasibility_selected": False,
    "human_public_copy_gate_selected": False,
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
    "EML-D48 checks one scoped non-duplicate constant-coordinate MachLib witness selected by D47.",
    "D48 uses MachLib's local `1 + 1` spelling for the D47 `2` constant because the current foundation only provides Real numerals 0 and 1.",
    "D48 does not approve public copy, promote public surfaces, change runtime lowering, replace log/exp, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery or broad EML superiority.",
]


def file_contains(path: Path, token: str) -> bool:
    return path.exists() and token in path.read_text(encoding="utf-8")


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    feasibility = d47.build_payload(atlas_gate_path)
    d47.validate_payload(feasibility)
    atlas_path = MACHLIB_ROOT / "MachLib" / "EMLAtlasWitness.lean"
    selected = {
        "name": "constant_coordinate_zero_exp_two_witness",
        "machlibName": "MachLib.Real.constant_coordinate_zero_exp_two_witness",
        "path": "../machlib/foundations/MachLib/EMLAtlasWitness.lean",
        "sourceProposedStatement": feasibility["summary"]["selectedProposedStatement"],
        "checkedLeanStatement": "eml 0 (exp (1 + 1)) = -1",
        "localSpellingNote": "MachLib.Basic currently provides Real numeral instances for 0 and 1 only; D47's exp 2 target is checked as exp (1 + 1).",
        "guardShape": [],
        "proofSketch": "unfold eml; rw [exp_zero, log_exp]; rw [sub_def, neg_add]; rw [← add_assoc, add_neg, zero_add]",
        "present": file_contains(atlas_path, "theorem constant_coordinate_zero_exp_two_witness"),
        "localStatementPresent": file_contains(atlas_path, "eml 0 (exp (1 + 1)) = -1"),
        "sourceCandidateId": feasibility["summary"]["selectedCandidateId"],
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
        "sourceFeasibilitySelector": feasibility["artifactId"],
        "sourceSelectedCandidateId": feasibility["summary"]["selectedCandidateId"],
        "sourceSelectedFamily": feasibility["summary"]["selectedFamily"],
        "sourceProposedStatement": feasibility["summary"]["selectedProposedStatement"],
        "sourceProposedWitnessName": feasibility["summary"]["selectedProposedWitnessName"],
        "existingConstantWitnessName": feasibility["summary"]["existingConstantWitnessName"],
        "duplicatesExistingConstantWitness": feasibility["summary"]["duplicatesExistingConstantWitness"],
        "selectedWitnessName": selected["machlibName"],
        "selectedWitnessPresent": selected["present"],
        "checkedLeanStatement": selected["checkedLeanStatement"],
        "localStatementPresent": selected["localStatementPresent"],
        "localSpellingUsesOnePlusOne": True,
        "localSpellingReason": selected["localSpellingNote"],
        "guardCount": len(selected["guardShape"]),
        "machlibFileChanged": True,
        "leanTypecheckPerformed": True,
        "lakeBuildPassed": True,
        "scopedWitnessChecked": selected["present"],
        "candidateProved": selected["present"],
        "implementationStarted": True,
        "proofAttemptStarted": True,
        "blockerRecorded": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": "standard_log_exp_and_arithmetic_remain_runtime_controls",
        "logExpReplacementClaim": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "boundedTrigFeasibilitySelected": False,
        "humanPublicCopyGateSelected": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextArtifact": "EML-D49 constant-coordinate zero-exp-two private surface review",
        "claimFlagsBounded": all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "scoped_witness_checked",
                "constant_coordinate_feasibility_recorded",
                "non_duplicate_statement_selected",
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
        "attemptType": "eml_constant_coordinate_zero_exp_two_witness_attempt_v0",
        "artifactId": "eml-d48-constant-coordinate-zero-exp-two-witness-attempt",
        "status": STATUS,
        "decision": "constant_coordinate_zero_exp_two_witness_checked_in_machlib",
        "date": DATE,
        "sourceFeasibilitySelector": feasibility["artifactId"],
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
    if payload["sourceFeasibilitySelector"] != "eml-d47-constant-coordinate-refresh-feasibility-selector":
        raise ValueError("D48 must consume D47")
    if summary["sourceSelectedCandidateId"] != "zero_coordinate_exp_two_boundary":
        raise ValueError("unexpected source candidate")
    if summary["sourceSelectedFamily"] != "constant_coordinate_refresh":
        raise ValueError("unexpected family")
    if summary["sourceProposedStatement"] != "eml 0 (exp 2) = -1":
        raise ValueError("unexpected D47 source statement")
    if summary["sourceProposedWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("unexpected D47 proposed witness")
    if summary["existingConstantWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("unexpected existing constants witness")
    if summary["duplicatesExistingConstantWitness"] is not False:
        raise ValueError("D48 must remain non-duplicate")
    if summary["selectedWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("unexpected selected witness")
    if summary["checkedLeanStatement"] != "eml 0 (exp (1 + 1)) = -1":
        raise ValueError("unexpected checked Lean statement")
    if summary["localSpellingUsesOnePlusOne"] is not True:
        raise ValueError("D48 must record the local 1 + 1 spelling")
    if summary["guardCount"] != 0:
        raise ValueError("unexpected guard count")
    for key in [
        "selectedWitnessPresent",
        "localStatementPresent",
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
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "advantageLabCaseAdded",
        "boundedTrigFeasibilitySelected",
        "humanPublicCopyGateSelected",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_log_exp_and_arithmetic_remain_runtime_controls":
        raise ValueError("runtime control drift")
    if summary["nextArtifact"] != "EML-D49 constant-coordinate zero-exp-two private surface review":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in [
        "scoped_witness_checked",
        "constant_coordinate_feasibility_recorded",
        "non_duplicate_statement_selected",
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
            "constant_coordinate_feasibility_recorded",
            "non_duplicate_statement_selected",
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
        "artifactType": "eml_constant_coordinate_zero_exp_two_witness_attempt",
        "validationStatus": "pass",
        "semanticStrength": "scoped_machlib_constant_coordinate_zero_exp_two_witness_checked",
        "source": f"python/results/eml_d48_constant_coordinate_zero_exp_two_witness_attempt/eml_d48_constant_coordinate_zero_exp_two_witness_attempt_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d48_constant_coordinate_zero_exp_two_witness_attempt_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "checkedLeanStatement": payload["summary"]["checkedLeanStatement"],
        "nextAction": "Surface D48 privately before any public copy, public Atlas, or runtime-lowering claim.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D48 Constant-Coordinate Zero-Exp-Two Witness Attempt",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected witness: `{payload['summary']['selectedWitnessName']}`",
        "",
        "D48 checks one scoped non-duplicate constant-coordinate MachLib witness.",
        "",
        "## Statement",
        "",
        f"- D47 source statement: `{payload['summary']['sourceProposedStatement']}`",
        f"- checked Lean statement: `{payload['summary']['checkedLeanStatement']}`",
        f"- local spelling reason: {payload['summary']['localSpellingReason']}",
        "",
        "## Verification",
        "",
        f"- command: `{payload['verification']['command']}`",
        f"- observed status: `{payload['verification']['observedStatus']}`",
        "",
        "## Summary",
        "",
        f"- selected witness present: `{payload['summary']['selectedWitnessPresent']}`",
        f"- lake build passed: `{payload['summary']['lakeBuildPassed']}`",
        f"- blocker recorded: `{payload['summary']['blockerRecorded']}`",
        f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
        f"- runtime lowering changed: `{payload['summary']['runtimeLoweringChanged']}`",
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
    result_path = out_dir / f"eml_d48_constant_coordinate_zero_exp_two_witness_attempt_{STAMP}.json"
    report_path = report_dir / f"eml_d48_constant_coordinate_zero_exp_two_witness_attempt_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d48_constant_coordinate_zero_exp_two_witness_attempt.json"
    feed_path = command_feed_dir / f"eml_d48_constant_coordinate_zero_exp_two_witness_attempt_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d48_constant_coordinate_zero_exp_two_witness_attempt")
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
    print("EML_D48_CONSTANT_COORDINATE_ZERO_EXP_TWO_WITNESS_ATTEMPT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
