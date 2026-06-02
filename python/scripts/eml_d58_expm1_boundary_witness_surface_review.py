#!/usr/bin/env python3
"""EML-D58 expm1 boundary checked-witness private surface review."""

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

from scripts import eml_d57_expm1_boundary_identity_witness_attempt as d57  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_expm1_boundary_witness_surface_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D58_EXPM1_BOUNDARY_WITNESS_SURFACE_REVIEW_PASS"

CLAIM_FLAGS = {
    "surface_updated": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
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
    "EML-D58 is a private surface review over the checked D57 expm1-boundary witness; it does not update public pages or promote Atlas copy.",
    "The checked identity is one scoped proof/teaching-shape witness; protected expm1 remains the runtime and numerical-stability control.",
    "D58 does not edit MachLib, typecheck Lean, approve public copy, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, protected expm1 replacement, or broad EML superiority.",
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
    witness = d57.build_payload(atlas_gate_path)
    d57.validate_payload(witness)
    surface_rows = [
        surface_row(
            "machlib_witness_index_expm1_boundary",
            "machlib_private_index",
            "checked_witness_recorded_private",
            "scoped_machlib_expm1_boundary_identity_checked",
            "record_as_private_checked_witness",
            [
                "D57 checks MachLib.Real.expm1_boundary_identity_witness.",
                "The checked statement is eml x (exp 1) = exp x - 1.",
                "The witness is scoped to one identity and does not create an expm1 family theorem.",
            ],
            ["public readiness", "theorem discovery", "broad expm1 identity family"],
        ),
        surface_row(
            "expm1_runtime_control_guardrail",
            "runtime_control_guardrail",
            "protected_expm1_runtime_control_required",
            "protected_expm1_runtime_control_preserved",
            "keep_protected_expm1_as_runtime_control",
            [
                "D56 and D57 keep protected_expm1_remains_runtime_control.",
                "The identity may support proof/teaching shape but does not replace protected expm1.",
                "Future copy must block runtime advantage and protected expm1 replacement language.",
            ],
            ["protected expm1 replacement", "runtime advantage", "runtime lowering superiority"],
        ),
        surface_row(
            "expm1_non_duplicate_exp_branch_guardrail",
            "candidate_boundary",
            "non_duplicate_of_exp_branch_witness",
            "exp_one_argument_boundary_preserved",
            "keep_eml_x_exp_one_separate_from_eml_x_one",
            [
                "D57 checks eml x (exp 1), not eml x 1.",
                "MachLib.Real.atlas_exp_from_eml_witness already records eml x 1 = exp x.",
                "The D10 constants bundle remains separate from this universal x identity.",
            ],
            ["duplicate exp branch witness", "D10 relabeling", "broad constant-coordinate theorem"],
        ),
        surface_row(
            "advantage_lab_expm1_boundary",
            "advantage_lab",
            "runtime_control_remains_protected_expm1",
            "scoped_expm1_boundary_identity_witness_available",
            "do_not_add_runtime_advantage_row_without_new_runtime_evidence",
            [
                "The witness strengthens proof/teaching shape only.",
                "Protected expm1 remains the numerical runtime control.",
                "No Advantage Lab case should be added without separate runtime evidence.",
            ],
            ["runtime advantage", "protected expm1 replacement", "log/exp replacement"],
        ),
        surface_row(
            "public_atlas_expm1_boundary",
            "public_surface",
            "held_private",
            "checked_machlib_witness_available_private",
            "require_human_copy_review_before_public_change",
            [
                "D57 proof status is real but public wording has not been reviewed.",
                "No monogate.org or monogate.dev public route is changed by D58.",
                "Safe public wording must preserve runtime-control and non-duplicate caveats.",
            ],
            ["public readiness", "public theorem claim", "public Atlas promotion"],
        ),
    ]
    summary = {
        "sourceWitnessAttempt": witness["artifactId"],
        "selectedWitnessName": witness["summary"]["machlibName"],
        "sourceSelectedCandidateId": witness["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": witness["summary"]["sourceSelectedFamily"],
        "checkedStatement": witness["summary"]["checkedStatement"],
        "machlibFile": witness["summary"]["machlibFile"],
        "guardCount": witness["summary"]["guardCount"],
        "checkedWitnessRecordedPrivately": witness["summary"]["candidateProved"],
        "candidateProved": witness["summary"]["candidateProved"],
        "buildPassed": witness["summary"]["buildPassed"],
        "surfaceRowCount": len(surface_rows),
        "runtimeLoweringControl": witness["summary"]["runtimeLoweringControl"],
        "publicPromotionPerformed": False,
        "publicEducationCandidate": False,
        "publicCopyApproved": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
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
        "nextAction": "EML-D59 choose expm1-boundary checked-witness copy review, next bounded branch, or human-approved public copy gate without public promotion.",
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in row["claimFlags"].values()) for row in surface_rows),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_expm1_boundary_witness_surface_review_v0",
        "artifactId": "eml-d58-expm1-boundary-witness-surface-review",
        "status": STATUS,
        "decision": "surface_checked_expm1_boundary_witness_as_private_review_evidence_only",
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
    if payload["sourceWitnessAttempt"] != "eml-d57-expm1-boundary-identity-witness-attempt":
        raise ValueError("D58 must consume D57")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "protected_runtime_boundary_identity":
        raise ValueError("unexpected family")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    if summary["surfaceRowCount"] != 5:
        raise ValueError("expected five surface rows")
    for key in ["checkedWitnessRecordedPrivately", "candidateProved", "buildPassed"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 0:
        raise ValueError("expm1-boundary witness should not add guards")
    for key in [
        "publicPromotionPerformed",
        "publicEducationCandidate",
        "publicCopyApproved",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedExpm1ReplacementClaim",
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
    if summary["runtimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["nextAction"] != "EML-D59 choose expm1-boundary checked-witness copy review, next bounded branch, or human-approved public copy gate without public promotion.":
        raise ValueError("unexpected next action")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_expm1_boundary_witness_surface_review",
        "validationStatus": "pass",
        "semanticStrength": "checked_expm1_boundary_witness_private_surface_review_no_public_update",
        "source": f"python/results/eml_d58_expm1_boundary_witness_surface_review/eml_d58_expm1_boundary_witness_surface_review_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d58_expm1_boundary_witness_surface_review_feed",
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
        "# EML-D58 Expm1 Boundary Witness Surface Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D58 surfaces the checked expm1-boundary witness privately without public copy approval.",
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
            f"- checked statement: `{payload['summary']['checkedStatement']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
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
    result_path = out_dir / f"eml_d58_expm1_boundary_witness_surface_review_{STAMP}.json"
    report_path = report_dir / f"eml_d58_expm1_boundary_witness_surface_review_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d58_expm1_boundary_witness_surface_review.json"
    feed_path = command_feed_dir / f"eml_d58_expm1_boundary_witness_surface_review_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d58_expm1_boundary_witness_surface_review")
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
    print("EML_D58_EXPM1_BOUNDARY_WITNESS_SURFACE_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
