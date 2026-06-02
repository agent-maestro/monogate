#!/usr/bin/env python3
"""EML-D49 constant-coordinate zero-exp-two private surface review."""

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

from scripts import eml_d48_constant_coordinate_zero_exp_two_witness_attempt as d48  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_constant_coordinate_zero_exp_two_surface_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D49_CONSTANT_COORDINATE_ZERO_EXP_TWO_SURFACE_REVIEW_PASS"

CLAIM_FLAGS = {
    "surface_updated": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
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
    "EML-D49 is a private surface review over the checked D48 constant-coordinate witness; it does not update public pages or promote Atlas copy.",
    "The checked identity is one scoped proof/teaching-shape witness using MachLib's local `1 + 1` spelling; it is not a new runtime lowering or log/exp replacement.",
    "D49 does not edit MachLib, typecheck Lean, approve public copy, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery or broad EML superiority.",
]


def surface_row(
    surface_id: str,
    surface_kind: str,
    status: str,
    evidence_strength: str,
    action: str,
    rationale: list[str],
    blocked_claims: list[str],
) -> dict[str, Any]:
    return {
        "surfaceId": surface_id,
        "surfaceKind": surface_kind,
        "surfaceStatus": status,
        "evidenceStrength": evidence_strength,
        "recommendedAction": action,
        "rationale": rationale,
        "blockedClaims": blocked_claims,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    witness = d48.build_payload(atlas_gate_path)
    d48.validate_payload(witness)
    surface_rows = [
        surface_row(
            "machlib_witness_index_constant_coordinate_zero_exp_two",
            "machlib_private_index",
            "checked_witness_recorded_private",
            "scoped_machlib_constant_coordinate_zero_exp_two_witness_checked",
            "record_as_private_checked_witness",
            [
                "D48 checks MachLib.Real.constant_coordinate_zero_exp_two_witness.",
                "The checked Lean statement is eml 0 (exp (1 + 1)) = -1.",
                "The D47 source statement remains eml 0 (exp 2) = -1.",
            ],
            ["public readiness", "theorem discovery", "duplicate D10 constants witness"],
        ),
        surface_row(
            "constant_coordinate_local_spelling_guardrail",
            "local_spelling_guardrail",
            "one_plus_one_spelling_required",
            "local_real_numeral_boundary_recorded",
            "preserve_exp_two_to_exp_one_plus_one_note",
            [
                "MachLib.Basic currently provides Real numeral instances for 0 and 1 only.",
                "D49 must preserve the note that exp 2 is checked locally as exp (1 + 1).",
                "Future copy should not hide the local spelling difference when citing the checked Lean theorem.",
            ],
            ["ambiguous numeral 2 claim", "unchecked exp 2 Lean spelling", "public copy without caveat"],
        ),
        surface_row(
            "constant_coordinate_non_duplicate_guardrail",
            "candidate_boundary",
            "non_duplicate_of_d10_constants_bundle",
            "d10_constants_boundary_preserved",
            "keep_d10_bundle_and_d48_witness_separate",
            [
                "D47 selected a non-duplicate target instead of relabeling the D10 constants bundle.",
                "The existing D10 bundle remains eml 0 (exp 1) = 0, eml 0 1 = 1, and eml 1 1 = exp 1.",
                "D48 adds one separate constant-coordinate identity only.",
            ],
            ["D10 relabeling", "new constants family theorem", "broad constant-coordinate theorem"],
        ),
        surface_row(
            "advantage_lab_constant_coordinate_zero_exp_two",
            "advantage_lab",
            "runtime_control_remains_standard_log_exp_and_arithmetic",
            "scoped_constant_coordinate_identity_witness_available",
            "do_not_add_runtime_advantage_row_without_new_runtime_evidence",
            [
                "The witness strengthens proof/teaching shape only.",
                "Standard log/exp and arithmetic remain the semantic and runtime controls.",
                "No Advantage Lab case should be added without separate runtime evidence.",
            ],
            ["runtime advantage", "runtime lowering superiority", "log/exp replacement"],
        ),
        surface_row(
            "public_atlas_constant_coordinate_zero_exp_two",
            "public_surface",
            "held_private",
            "checked_machlib_witness_available_private",
            "require_human_copy_review_before_public_change",
            [
                "D48 proof status is real but public wording has not been reviewed.",
                "No monogate.org or monogate.dev public route is changed by D49.",
                "Safe public wording must preserve the local spelling and non-duplicate caveats.",
            ],
            ["public readiness", "public theorem claim", "public Atlas promotion"],
        ),
    ]
    summary = {
        "sourceWitnessAttempt": witness["artifactId"],
        "selectedWitnessName": witness["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": witness["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": witness["summary"]["sourceSelectedFamily"],
        "sourceProposedStatement": witness["summary"]["sourceProposedStatement"],
        "checkedLeanStatement": witness["summary"]["checkedLeanStatement"],
        "localSpellingUsesOnePlusOne": witness["summary"]["localSpellingUsesOnePlusOne"],
        "localSpellingReason": witness["summary"]["localSpellingReason"],
        "existingConstantWitnessName": witness["summary"]["existingConstantWitnessName"],
        "duplicatesExistingConstantWitness": witness["summary"]["duplicatesExistingConstantWitness"],
        "surfaceRowCount": len(surface_rows),
        "checkedWitnessRecordedPrivately": witness["summary"]["scopedWitnessChecked"],
        "candidateProved": witness["summary"]["candidateProved"],
        "guardCount": witness["summary"]["guardCount"],
        "publicPromotionPerformed": False,
        "publicEducationCandidate": False,
        "publicCopyApproved": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "runtimeLoweringControl": witness["summary"]["runtimeLoweringControl"],
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "surfaceUpdated": False,
        "boundedTrigFeasibilitySelected": False,
        "humanPublicCopyGateSelected": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D50 choose checked-witness copy review, next bounded branch, or human-approved public copy gate without public promotion.",
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in row["claimFlags"].values()) for row in surface_rows),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_constant_coordinate_zero_exp_two_surface_review_v0",
        "artifactId": "eml-d49-constant-coordinate-zero-exp-two-surface-review",
        "status": STATUS,
        "decision": "surface_checked_constant_coordinate_zero_exp_two_witness_as_private_review_evidence_only",
        "date": DATE,
        "sourceWitnessAttempt": witness["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "surfaceRows": surface_rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceWitnessAttempt"] != "eml-d48-constant-coordinate-zero-exp-two-witness-attempt":
        raise ValueError("D49 must consume D48")
    if summary["selectedWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "zero_coordinate_exp_two_boundary":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "constant_coordinate_refresh":
        raise ValueError("unexpected family")
    if summary["sourceProposedStatement"] != "eml 0 (exp 2) = -1":
        raise ValueError("unexpected source statement")
    if summary["checkedLeanStatement"] != "eml 0 (exp (1 + 1)) = -1":
        raise ValueError("unexpected checked Lean statement")
    if summary["localSpellingUsesOnePlusOne"] is not True:
        raise ValueError("local spelling note must be preserved")
    if summary["existingConstantWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("unexpected existing constants witness")
    if summary["duplicatesExistingConstantWitness"] is not False:
        raise ValueError("D49 must preserve non-duplicate boundary")
    if summary["surfaceRowCount"] != 5:
        raise ValueError("expected five surface rows")
    for key in ["checkedWitnessRecordedPrivately", "candidateProved"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 0:
        raise ValueError("constant-coordinate witness should not add guards")
    for key in [
        "publicPromotionPerformed",
        "publicEducationCandidate",
        "publicCopyApproved",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "surfaceUpdated",
        "boundedTrigFeasibilitySelected",
        "humanPublicCopyGateSelected",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_log_exp_and_arithmetic_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["nextAction"] != "EML-D50 choose checked-witness copy review, next bounded branch, or human-approved public copy gate without public promotion.":
        raise ValueError("unexpected next action")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_constant_coordinate_zero_exp_two_surface_review",
        "validationStatus": "pass",
        "semanticStrength": "checked_constant_coordinate_zero_exp_two_private_surface_review_no_public_update",
        "source": f"python/results/eml_d49_constant_coordinate_zero_exp_two_surface_review/eml_d49_constant_coordinate_zero_exp_two_surface_review_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d49_constant_coordinate_zero_exp_two_surface_review_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D49 Constant-Coordinate Zero-Exp-Two Surface Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D49 surfaces the checked constant-coordinate witness privately without public copy approval.",
        "",
        "| Surface | Status | Action |",
        "|---|---|---|",
    ]
    for row in payload["surfaceRows"]:
        lines.append(f"| `{row['surfaceId']}` | `{row['surfaceStatus']}` | {row['recommendedAction']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected witness: `{payload['summary']['selectedWitnessName']}`",
            f"- source statement: `{payload['summary']['sourceProposedStatement']}`",
            f"- checked Lean statement: `{payload['summary']['checkedLeanStatement']}`",
            f"- local spelling preserved: `{payload['summary']['localSpellingUsesOnePlusOne']}`",
            f"- duplicates existing constants witness: `{payload['summary']['duplicatesExistingConstantWitness']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- surface updated: `{payload['summary']['surfaceUpdated']}`",
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
    result_path = out_dir / f"eml_d49_constant_coordinate_zero_exp_two_surface_review_{STAMP}.json"
    report_path = report_dir / f"eml_d49_constant_coordinate_zero_exp_two_surface_review_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d49_constant_coordinate_zero_exp_two_surface_review.json"
    feed_path = command_feed_dir / f"eml_d49_constant_coordinate_zero_exp_two_surface_review_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d49_constant_coordinate_zero_exp_two_surface_review")
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
    print("EML_D49_CONSTANT_COORDINATE_ZERO_EXP_TWO_SURFACE_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
