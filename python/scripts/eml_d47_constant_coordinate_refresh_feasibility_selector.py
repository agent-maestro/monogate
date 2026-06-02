#!/usr/bin/env python3
"""EML-D47 constant-coordinate refresh feasibility selector."""

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

from scripts import eml_d46_post_positive_log_exp_pause_next_selector as d46  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_constant_coordinate_refresh_feasibility_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D47_CONSTANT_COORDINATE_REFRESH_FEASIBILITY_SELECTOR_PASS"

CLAIM_FLAGS = {
    "feasibility_selector_started": True,
    "constant_coordinate_candidate_selected": True,
    "non_duplicate_statement_selected": True,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
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
    "EML-D47 is a feasibility selector for one non-duplicate constant-coordinate candidate; it does not edit MachLib, typecheck Lean, or prove the candidate.",
    "D47 does not reopen the checked D10 constants witness or claim a public Atlas promotion.",
    "D47 does not approve public copy, consume laptop artifacts, touch laptop-owned repos, change runtime lowering, replace log/exp, or claim theorem discovery or broad EML superiority.",
]

EXISTING_CONSTANT_WITNESS_STATEMENTS = [
    "eml 0 (exp 1) = 0",
    "eml 0 1 = 1",
    "eml 1 1 = exp 1",
]


def candidate_row(
    candidate_id: str,
    family: str,
    proposed_statement: str,
    proposed_witness_name: str,
    guard_shape: list[str],
    duplicate_status: str,
    feasibility_status: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "candidateId": candidate_id,
        "family": family,
        "proposedStatement": proposed_statement,
        "proposedWitnessName": proposed_witness_name,
        "guardShape": guard_shape,
        "duplicateStatus": duplicate_status,
        "feasibilityStatus": feasibility_status,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def option_by_id(payload: dict[str, Any], option_id: str) -> dict[str, Any]:
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d46.build_payload(atlas_gate_path)
    d46.validate_payload(selector)
    selected = option_by_id(selector, "constant_coordinate_refresh_selector")
    candidates = [
        candidate_row(
            "zero_coordinate_exp_two_boundary",
            "constant_coordinate_refresh",
            "eml 0 (exp 2) = -1",
            "MachLib.Real.constant_coordinate_zero_exp_two_witness",
            [],
            "non_duplicate_of_constants_zero_one_e_boundary_witness",
            "selected_feasible_next_attempt",
            [
                "It keeps the first EML coordinate fixed at 0 while moving the second coordinate away from the already checked exp 1 and 1 cases.",
                "It is a single constant-coordinate statement and can be checked later by unfolding EML plus log_exp/arithmetic.",
                "It extends the constants lane without claiming a new runtime lowering or public Atlas row.",
            ],
            [
                "must not relabel D10 constants as new work",
                "must remain a feasibility selector before any MachLib edit",
                "requires a separate D48 witness attempt or blocker packet",
            ],
        )
    ]
    chosen = candidates[0]
    summary = {
        "sourceSelector": selector["artifactId"],
        "sourceSelectedOptionId": selector["summary"]["selectedOptionId"],
        "sourceSelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "d46ConstantCoordinateRefreshSelected": selector["summary"]["constantCoordinateRefreshSelected"],
        "d46FrozenWitnessName": selector["summary"]["frozenWitnessName"],
        "d46FrozenCheckedStatement": selector["summary"]["frozenCheckedStatement"],
        "d46PublicHoldPreserved": selector["summary"]["publicHoldPreserved"],
        "candidateCount": len(candidates),
        "selectedCandidateId": chosen["candidateId"],
        "selectedFamily": chosen["family"],
        "selectedProposedStatement": chosen["proposedStatement"],
        "selectedProposedWitnessName": chosen["proposedWitnessName"],
        "selectedDuplicateStatus": chosen["duplicateStatus"],
        "guardCount": len(chosen["guardShape"]),
        "existingConstantWitnessName": "MachLib.Real.constants_zero_one_e_boundary_witness",
        "existingConstantWitnessStatementCount": len(EXISTING_CONSTANT_WITNESS_STATEMENTS),
        "duplicatesExistingConstantWitness": chosen["proposedStatement"] in EXISTING_CONSTANT_WITNESS_STATEMENTS,
        "nonDuplicateStatementSelected": True,
        "feasibilitySelectorStarted": True,
        "constantCoordinateCandidateSelected": True,
        "boundedTrigFeasibilitySelected": False,
        "humanPublicCopyGateSelected": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": "standard_log_exp_and_arithmetic_remain_runtime_controls",
        "logExpReplacementClaim": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "selectedNextArtifact": "EML-D48 constant-coordinate zero-exp-two witness attempt or blocker packet",
        "claimFlagsFeasibilityOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "feasibility_selector_started",
                "constant_coordinate_candidate_selected",
                "non_duplicate_statement_selected",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "feasibility_selector_started",
                "constant_coordinate_candidate_selected",
                "non_duplicate_statement_selected",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_constant_coordinate_refresh_feasibility_selector_v0",
        "artifactId": "eml-d47-constant-coordinate-refresh-feasibility-selector",
        "status": STATUS,
        "decision": "select_zero_coordinate_exp_two_boundary_feasibility",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "existingConstantWitnessStatements": list(EXISTING_CONSTANT_WITNESS_STATEMENTS),
        "candidateRows": candidates,
        "selectedCandidate": chosen,
        "sourceSelectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d46-post-positive-log-exp-pause-next-selector":
        raise ValueError("D47 must consume D46")
    if summary["sourceSelectedOptionId"] != "constant_coordinate_refresh_selector":
        raise ValueError("D46 must select constant-coordinate refresh")
    if summary["d46ConstantCoordinateRefreshSelected"] is not True:
        raise ValueError("D46 constant-coordinate selection must be preserved")
    if summary["d46FrozenWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected D46 frozen witness")
    if summary["d46FrozenCheckedStatement"] != "0 < x -> exp (log x) = x":
        raise ValueError("unexpected D46 frozen statement")
    if summary["candidateCount"] != 1:
        raise ValueError("expected one candidate row")
    if summary["selectedCandidateId"] != "zero_coordinate_exp_two_boundary":
        raise ValueError("unexpected selected candidate")
    if summary["selectedFamily"] != "constant_coordinate_refresh":
        raise ValueError("unexpected family")
    if summary["selectedProposedStatement"] != "eml 0 (exp 2) = -1":
        raise ValueError("unexpected proposed statement")
    if summary["selectedProposedWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("unexpected proposed witness")
    if summary["existingConstantWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("unexpected existing witness name")
    if summary["existingConstantWitnessStatementCount"] != 3:
        raise ValueError("existing constants witness statement count drift")
    if summary["duplicatesExistingConstantWitness"] is not False:
        raise ValueError("D47 candidate must not duplicate D10 constants witness")
    for key in [
        "nonDuplicateStatementSelected",
        "feasibilitySelectorStarted",
        "constantCoordinateCandidateSelected",
        "d46PublicHoldPreserved",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 0:
        raise ValueError("constant exp-two candidate should not add a guard")
    for key in [
        "boundedTrigFeasibilitySelected",
        "humanPublicCopyGateSelected",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "advantageLabCaseAdded",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_log_exp_and_arithmetic_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["selectedNextArtifact"] != "EML-D48 constant-coordinate zero-exp-two witness attempt or blocker packet":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsFeasibilityOnly"] is not True:
        raise ValueError("claim flags must remain feasibility-only")
    for key in ["feasibility_selector_started", "constant_coordinate_candidate_selected", "non_duplicate_statement_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"feasibility_selector_started", "constant_coordinate_candidate_selected", "non_duplicate_statement_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_constant_coordinate_refresh_feasibility_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_feasibility_selector_non_duplicate_constant_coordinate_no_implementation",
        "source": f"python/results/eml_d47_constant_coordinate_refresh_feasibility_selector/eml_d47_constant_coordinate_refresh_feasibility_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d47_constant_coordinate_refresh_feasibility_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedProposedStatement": payload["summary"]["selectedProposedStatement"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D48 as a constant-coordinate zero-exp-two witness attempt or blocker packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D47 Constant-Coordinate Refresh Feasibility Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D47 selects one non-duplicate constant-coordinate candidate before any MachLib edit or proof attempt.",
        "",
        "| Candidate | Statement | Duplicate status | Next artifact |",
        "|---|---|---|---|",
    ]
    for row in payload["candidateRows"]:
        lines.append(
            f"| `{row['candidateId']}` | `{row['proposedStatement']}` | `{row['duplicateStatus']}` | {payload['summary']['selectedNextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Existing Constants Witness",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in payload["existingConstantWitnessStatements"])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected proposed witness: `{payload['summary']['selectedProposedWitnessName']}`",
            f"- duplicates existing constants witness: `{payload['summary']['duplicatesExistingConstantWitness']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- proof attempt started: `{payload['summary']['proofAttemptStarted']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
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
    result_path = out_dir / f"eml_d47_constant_coordinate_refresh_feasibility_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d47_constant_coordinate_refresh_feasibility_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d47_constant_coordinate_refresh_feasibility_selector.json"
    feed_path = command_feed_dir / f"eml_d47_constant_coordinate_refresh_feasibility_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d47_constant_coordinate_refresh_feasibility_selector")
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
    print("EML_D47_CONSTANT_COORDINATE_REFRESH_FEASIBILITY_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
