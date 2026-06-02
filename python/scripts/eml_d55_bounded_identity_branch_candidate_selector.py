#!/usr/bin/env python3
"""EML-D55 bounded identity branch candidate selector."""

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

from scripts import eml_d54_post_constant_coordinate_pause_next_selector as d54  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_bounded_identity_branch_candidate_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D55_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"

CLAIM_FLAGS = {
    "bounded_identity_candidate_selected": True,
    "expm1_boundary_candidate_selected": True,
    "witness_feasibility_recorded": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
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
    "EML-D55 selects one bounded identity candidate only; it does not record feasibility, edit MachLib, typecheck Lean, or start a proof attempt.",
    "D55 selects an expm1-boundary identity candidate while keeping protected expm1 as the runtime and numerical-stability control.",
    "D55 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/exp replacement, protected expm1 replacement, or broad EML superiority.",
]


def branch_candidate(
    candidate_id: str,
    family: str,
    source_frontier_id: str,
    proposed_statement: str,
    eml_shape: str,
    standard_shape: str,
    guard_shape: list[str],
    status: str,
    priority_score: int,
    estimated_difficulty: str,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
    duplicate_checked_witnesses: list[str],
    runtime_control: str,
) -> dict[str, Any]:
    return {
        "candidateId": candidate_id,
        "family": family,
        "sourceFrontierId": source_frontier_id,
        "proposedStatement": proposed_statement,
        "emlShape": eml_shape,
        "standardShape": standard_shape,
        "guardShape": guard_shape,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "estimatedDifficulty": estimated_difficulty,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "duplicateCheckedWitnesses": duplicate_checked_witnesses,
        "duplicatesCheckedWitness": bool(duplicate_checked_witnesses),
        "runtimeControl": runtime_control,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d54.build_payload(atlas_gate_path)
    d54.validate_payload(selector)
    candidates = [
        branch_candidate(
            "expm1_boundary_identity",
            "protected_runtime_boundary_identity",
            "expm1_failure_boundary_v1",
            "eml x (exp 1) = exp x - 1",
            "eml x (exp 1)",
            "exp x - 1",
            [],
            "selected_next",
            76,
            "small_universal_identity_with_runtime_control",
            "EML-D56 expm1 boundary identity feasibility packet",
            [
                "It is one precise non-duplicate bounded identity candidate after the D53 constant-coordinate freeze.",
                "It connects to the D1 expm1 protected-runtime boundary while preserving protected expm1 as the numerical control.",
                "It can be reviewed as feasibility before any MachLib edit or Lean typecheck.",
            ],
            [
                "must distinguish identity feasibility from protected expm1 runtime replacement",
                "must not duplicate MachLib.Real.atlas_exp_from_eml_witness or the D10 constants bundle",
                "must keep proof-attempt and implementation claims false in D56 unless separately selected",
            ],
            [],
            "protected_expm1_remains_runtime_control",
        ),
        branch_candidate(
            "probability_logit_boundary_coordinate",
            "probability_log_domain_coordinate",
            "probability_logit_boundary_v0",
            "guarded probability-logit EML coordinate candidate",
            "EML subtraction-coordinate view of log p - log (1 - p)",
            "log p - log1p (-p)",
            ["0 < p", "p < 1"],
            "candidate_later",
            59,
            "guarded_domain_probe",
            "Future probability logit boundary feasibility selector",
            [
                "It remains a useful domain-obligation candidate.",
                "It requires stronger edge guards and protected standard-control handling than the expm1 boundary identity.",
            ],
            [
                "requires exact EML statement",
                "requires edge-domain negative controls",
                "protected logit/log1p controls must remain runtime controls",
            ],
            [],
            "protected_logit_and_log1p_remain_runtime_controls",
        ),
        branch_candidate(
            "bounded_trig_eml_probe_selector",
            "bounded_trig_identity_probe",
            "bounded_trig_identity_feasibility_selector",
            "single bounded trig identity candidate",
            "guarded sin/cos EML coordinate candidate",
            "standard bounded trig identity",
            ["bounded interval guard required"],
            "candidate_later",
            44,
            "speculative_frontier_probe",
            "Future bounded trig identity feasibility selector",
            [
                "A trigonometric probe may broaden EML research later.",
                "It is more speculative and needs negative controls before proof work.",
            ],
            [
                "requires exact statement",
                "requires bounded interval guard",
                "avoid broad EML advantage language",
            ],
            [],
            "standard_trig_remains_runtime_control",
        ),
    ]
    selected = next(candidate for candidate in candidates if candidate["selectionStatus"] == "selected_next")
    summary = {
        "sourceSelector": selector["artifactId"],
        "sourceSelectedOptionId": selector["summary"]["selectedOptionId"],
        "sourceSelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "sourceFrozenWitnessName": selector["summary"]["frozenWitnessName"],
        "sourceFrozenStatement": selector["summary"]["frozenCheckedStatement"],
        "sourceFrozenCaveatCount": selector["summary"]["frozenCaveatCount"],
        "sourceFrozenBlockedPhraseCount": selector["summary"]["frozenBlockedPhraseCount"],
        "sourceLocalSpellingUsesOnePlusOne": selector["summary"]["localSpellingUsesOnePlusOne"],
        "sourceExistingConstantWitnessName": selector["summary"]["existingConstantWitnessName"],
        "sourceDuplicatesExistingConstantWitness": selector["summary"]["duplicatesExistingConstantWitness"],
        "candidateCount": len(candidates),
        "selectedCandidateId": selected["candidateId"],
        "selectedFamily": selected["family"],
        "selectedSourceFrontierId": selected["sourceFrontierId"],
        "selectedProposedStatement": selected["proposedStatement"],
        "selectedNextArtifact": selected["nextArtifact"],
        "selectedGuardCount": len(selected["guardShape"]),
        "selectedDuplicatesCheckedWitness": selected["duplicatesCheckedWitness"],
        "selectedDuplicateCheckedWitnessCount": len(selected["duplicateCheckedWitnesses"]),
        "runtimeLoweringControl": selected["runtimeControl"],
        "boundedIdentityCandidateSelected": True,
        "expm1BoundaryCandidateSelected": True,
        "witnessFeasibilityRecorded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "boundedTrigFeasibilitySelected": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsCandidateOnly": all(
            CLAIM_FLAGS[key] is True
            for key in ["bounded_identity_candidate_selected", "expm1_boundary_candidate_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"bounded_identity_candidate_selected", "expm1_boundary_candidate_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_bounded_identity_branch_candidate_selector_v0",
        "artifactId": "eml-d55-bounded-identity-branch-candidate-selector",
        "status": STATUS,
        "decision": "select_expm1_boundary_identity_candidate",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "branchCandidates": candidates,
        "selectedCandidate": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d54-post-constant-coordinate-pause-next-selector":
        raise ValueError("D55 must consume D54")
    if summary["sourceSelectedOptionId"] != "next_bounded_identity_branch_selector":
        raise ValueError("D55 requires D54 bounded identity selection")
    if summary["sourceSelectedNextArtifact"] != "EML-D55 bounded identity branch candidate selector":
        raise ValueError("unexpected D54 next artifact")
    if summary["sourceFrozenWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("unexpected frozen source witness")
    if summary["sourceFrozenStatement"] != "eml 0 (exp (1 + 1)) = -1":
        raise ValueError("unexpected frozen source statement")
    if summary["sourceFrozenCaveatCount"] != 8 or summary["sourceFrozenBlockedPhraseCount"] != 10:
        raise ValueError("D53 freeze caveat/blocker counts drifted")
    if summary["sourceLocalSpellingUsesOnePlusOne"] is not True:
        raise ValueError("D53 local spelling note must be preserved")
    if summary["sourceExistingConstantWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("D53 non-duplicate boundary drift")
    if summary["sourceDuplicatesExistingConstantWitness"] is not False:
        raise ValueError("D53 duplicate boundary drift")
    if summary["candidateCount"] != 3:
        raise ValueError("expected three bounded candidates")
    if summary["selectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("unexpected selected candidate")
    if summary["selectedFamily"] != "protected_runtime_boundary_identity":
        raise ValueError("unexpected selected family")
    if summary["selectedSourceFrontierId"] != "expm1_failure_boundary_v1":
        raise ValueError("unexpected source frontier id")
    if summary["selectedProposedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected proposed statement")
    if summary["selectedNextArtifact"] != "EML-D56 expm1 boundary identity feasibility packet":
        raise ValueError("unexpected next artifact")
    if summary["selectedGuardCount"] != 0:
        raise ValueError("selected candidate should be unguarded")
    if summary["selectedDuplicatesCheckedWitness"] is not False:
        raise ValueError("selected candidate must not duplicate a checked witness")
    if summary["selectedDuplicateCheckedWitnessCount"] != 0:
        raise ValueError("duplicate witness count drift")
    if summary["runtimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime control drift")
    for key in [
        "boundedIdentityCandidateSelected",
        "expm1BoundaryCandidateSelected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "witnessFeasibilityRecorded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "boundedTrigFeasibilitySelected",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
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
    if summary["claimFlagsCandidateOnly"] is not True:
        raise ValueError("claim flags must remain candidate-only")
    for key in ["bounded_identity_candidate_selected", "expm1_boundary_candidate_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"bounded_identity_candidate_selected", "expm1_boundary_candidate_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_bounded_identity_branch_candidate_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_one_expm1_boundary_candidate_no_proof_no_runtime_claim",
        "source": f"python/results/eml_d55_bounded_identity_branch_candidate_selector/eml_d55_bounded_identity_branch_candidate_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d55_bounded_identity_branch_candidate_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedProposedStatement": payload["summary"]["selectedProposedStatement"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D56 as an expm1 boundary identity feasibility packet; do not edit MachLib yet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D55 Bounded Identity Branch Candidate Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected candidate: `{payload['summary']['selectedCandidateId']}`",
        "",
        "D55 selects one bounded identity candidate after the D54 post-pause selector.",
        "",
        "| Candidate | Status | Score | Proposed statement | Next artifact |",
        "|---|---|---:|---|---|",
    ]
    for candidate in payload["branchCandidates"]:
        lines.append(
            f"| `{candidate['candidateId']}` | `{candidate['selectionStatus']}` | {candidate['priorityScore']} | `{candidate['proposedStatement']}` | {candidate['nextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected family: `{payload['summary']['selectedFamily']}`",
            f"- selected proposed statement: `{payload['summary']['selectedProposedStatement']}`",
            f"- runtime control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- candidate proved: `{payload['summary']['candidateProved']}`",
            f"- public ready: `{payload['summary']['publicReady']}`",
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
    result_path = out_dir / f"eml_d55_bounded_identity_branch_candidate_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d55_bounded_identity_branch_candidate_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d55_bounded_identity_branch_candidate_selector.json"
    feed_path = command_feed_dir / f"eml_d55_bounded_identity_branch_candidate_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d55_bounded_identity_branch_candidate_selector")
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
    print("EML_D55_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
