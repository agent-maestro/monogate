#!/usr/bin/env python3
"""EML-D64 bounded identity branch candidate selector."""

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

from scripts import eml_d63_post_expm1_boundary_pause_next_selector as d63  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_bounded_identity_branch_candidate_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D64_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"

CLAIM_FLAGS = {
    "bounded_identity_candidate_selected": True,
    "probability_logit_boundary_candidate_selected": True,
    "witness_feasibility_recorded": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
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
    "EML-D64 selects one bounded identity candidate only; it does not record feasibility, edit MachLib, typecheck Lean, or start a proof attempt.",
    "D64 selects a guarded probability-logit boundary coordinate candidate while keeping protected logarithmic runtime controls in place.",
    "D64 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p replacement, protected expm1 replacement, or broad EML superiority.",
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
    selector = d63.build_payload(atlas_gate_path)
    d63.validate_payload(selector)
    candidates = [
        branch_candidate(
            "probability_logit_boundary_coordinate",
            "guarded_probability_log_coordinate",
            "probability_logit_boundary_v0",
            "0 < p and p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)",
            "eml (log p) (exp (log (1 - p)))",
            "p - log (1 - p)",
            ["0 < p", "p < 1"],
            "selected_next",
            73,
            "guarded_domain_coordinate_candidate",
            "EML-D65 probability logit boundary coordinate feasibility packet",
            [
                "It is the highest-priority parked guarded coordinate after the expm1 branch was frozen.",
                "It exercises domain-obligation visibility without touching protected runtime log/log1p controls.",
                "It can be reviewed as feasibility before any MachLib edit or Lean typecheck.",
            ],
            [
                "must distinguish coordinate feasibility from a logit replacement claim",
                "must keep protected logarithmic runtime controls in place",
                "must include domain-edge negative controls before any proof work",
                "must keep proof-attempt and implementation claims false in D65 unless separately selected",
            ],
            [],
            "protected_log_and_log1p_remain_runtime_controls",
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
            48,
            "speculative_frontier_probe",
            "Future bounded trig identity feasibility selector",
            [
                "A trigonometric probe may broaden EML research later.",
                "It remains more speculative and needs stronger negative controls before proof work.",
            ],
            [
                "requires exact statement",
                "requires bounded interval guard",
                "avoid broad EML advantage language",
            ],
            [],
            "standard_trig_remains_runtime_control",
        ),
        branch_candidate(
            "human_approved_expm1_public_copy_gate",
            "public_copy_gate_lane",
            "human_approved_public_copy_gate",
            "human-approved expm1-boundary public copy gate",
            "private copy boundary only",
            "public copy requires human approval",
            ["explicit human approval required"],
            "candidate_later_requires_human_approval",
            36,
            "public_copy_gate_not_research_candidate",
            "Future human-approved expm1-boundary public copy gate",
            [
                "D62 froze expm1 private copy boundaries, but no human approval is recorded.",
                "Public copy should remain behind a separate human gate.",
            ],
            [
                "requires explicit human approval",
                "must reuse D62 frozen caveats and blocked phrases",
                "must not imply protected expm1 replacement, runtime advantage, or public readiness",
            ],
            [],
            "protected_expm1_remains_runtime_control",
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
        "sourceNonDuplicateWitnessName": selector["summary"]["nonDuplicateWitnessName"],
        "sourceDuplicatesExistingExpBranchWitness": selector["summary"]["duplicatesExistingExpBranchWitness"],
        "sourceRuntimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "sourceRuntimeGuardrailStatus": selector["summary"]["runtimeGuardrailStatus"],
        "sourcePublicAtlasStatus": selector["summary"]["publicAtlasStatus"],
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
        "probabilityLogitBoundaryCandidateSelected": True,
        "witnessFeasibilityRecorded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
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
            for key in ["bounded_identity_candidate_selected", "probability_logit_boundary_candidate_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"bounded_identity_candidate_selected", "probability_logit_boundary_candidate_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_bounded_identity_branch_candidate_selector_v0",
        "artifactId": "eml-d64-bounded-identity-branch-candidate-selector",
        "status": STATUS,
        "decision": "select_probability_logit_boundary_coordinate_candidate",
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
    if payload["sourceSelector"] != "eml-d63-post-expm1-boundary-pause-next-selector":
        raise ValueError("D64 must consume D63")
    if summary["sourceSelectedOptionId"] != "next_bounded_identity_branch_selector":
        raise ValueError("D64 requires D63 bounded identity selection")
    if summary["sourceSelectedNextArtifact"] != "EML-D64 bounded identity branch candidate selector":
        raise ValueError("unexpected D63 next artifact")
    if summary["sourceFrozenWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected frozen source witness")
    if summary["sourceFrozenStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected frozen source statement")
    if summary["sourceFrozenCaveatCount"] != 8 or summary["sourceFrozenBlockedPhraseCount"] != 10:
        raise ValueError("D62 freeze caveat/blocker counts drifted")
    if summary["sourceNonDuplicateWitnessName"] != "MachLib.Real.atlas_exp_from_eml_witness":
        raise ValueError("D62 non-duplicate boundary drift")
    if summary["sourceDuplicatesExistingExpBranchWitness"] is not False:
        raise ValueError("D62 duplicate boundary drift")
    if summary["sourceRuntimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("D62 runtime control drift")
    if summary["sourceRuntimeGuardrailStatus"] != "protected_expm1_runtime_control_required":
        raise ValueError("D62 runtime guardrail drift")
    if summary["sourcePublicAtlasStatus"] != "held_private":
        raise ValueError("D62 public hold drift")
    if summary["candidateCount"] != 3:
        raise ValueError("expected three bounded candidates")
    if summary["selectedCandidateId"] != "probability_logit_boundary_coordinate":
        raise ValueError("unexpected selected candidate")
    if summary["selectedFamily"] != "guarded_probability_log_coordinate":
        raise ValueError("unexpected selected family")
    if summary["selectedSourceFrontierId"] != "probability_logit_boundary_v0":
        raise ValueError("unexpected source frontier id")
    if summary["selectedProposedStatement"] != "0 < p and p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected proposed statement")
    if summary["selectedNextArtifact"] != "EML-D65 probability logit boundary coordinate feasibility packet":
        raise ValueError("unexpected next artifact")
    if summary["selectedGuardCount"] != 2:
        raise ValueError("selected candidate should have two guards")
    if summary["selectedDuplicatesCheckedWitness"] is not False:
        raise ValueError("selected candidate must not duplicate a checked witness")
    if summary["selectedDuplicateCheckedWitnessCount"] != 0:
        raise ValueError("duplicate witness count drift")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime control drift")
    for key in [
        "boundedIdentityCandidateSelected",
        "probabilityLogitBoundaryCandidateSelected",
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
        "protectedLogReplacementClaim",
        "protectedLog1pReplacementClaim",
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
    for key in ["bounded_identity_candidate_selected", "probability_logit_boundary_candidate_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"bounded_identity_candidate_selected", "probability_logit_boundary_candidate_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_bounded_identity_branch_candidate_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_one_probability_logit_boundary_candidate_no_proof_no_runtime_claim",
        "source": f"python/results/eml_d64_bounded_identity_branch_candidate_selector/eml_d64_bounded_identity_branch_candidate_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d64_bounded_identity_branch_candidate_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedProposedStatement": payload["summary"]["selectedProposedStatement"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D65 as a probability logit boundary coordinate feasibility packet; do not edit MachLib yet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D64 Bounded Identity Branch Candidate Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected candidate: `{payload['summary']['selectedCandidateId']}`",
        "",
        "D64 selects one bounded identity candidate after the D63 post-pause selector.",
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
    result_path = out_dir / f"eml_d64_bounded_identity_branch_candidate_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d64_bounded_identity_branch_candidate_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d64_bounded_identity_branch_candidate_selector.json"
    feed_path = command_feed_dir / f"eml_d64_bounded_identity_branch_candidate_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d64_bounded_identity_branch_candidate_selector")
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
    print("EML_D64_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
