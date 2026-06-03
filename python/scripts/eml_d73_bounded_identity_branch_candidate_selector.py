#!/usr/bin/env python3
"""EML-D73 bounded identity branch candidate selector."""

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

from scripts import eml_d72_post_probability_logit_pause_next_selector as d72  # noqa: E402

DATE = "2026-06-03"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_bounded_identity_branch_candidate_selector.d73.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D73_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_PASS"

CLAIM_FLAGS = {
    "bounded_identity_candidate_selected": True,
    "log1p_shifted_boundary_candidate_selected": True,
    "witness_feasibility_recorded": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_log_replacement_claim": False,
    "protected_log1p_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
    "bounded_trig_feasibility_selected": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
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
    "EML-D73 selects one bounded identity candidate only; it does not record feasibility, edit MachLib, typecheck Lean, or start a proof attempt.",
    "D73 selects a guarded log1p-shifted boundary coordinate candidate while keeping protected log/log1p runtime controls in place.",
    "D73 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p replacement, protected expm1 replacement, or broad EML superiority.",
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
    selector = d72.build_payload(atlas_gate_path)
    d72.validate_payload(selector)
    candidates = [
        branch_candidate(
            "log1p_shifted_boundary_coordinate",
            "guarded_log1p_shifted_coordinate",
            "post_probability_logit_pause_identity_lane",
            "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x",
            "eml (log (1 + x)) (exp 1)",
            "x",
            ["0 < 1 + x"],
            "selected_next",
            76,
            "guarded_domain_coordinate_candidate",
            "EML-D74 log1p shifted boundary coordinate feasibility packet",
            [
                "It is a fresh guarded bounded identity candidate after the probability-logit branch was frozen.",
                "It exercises log1p-style domain-obligation visibility without claiming protected log/log1p replacement.",
                "It can be reviewed as feasibility before any MachLib edit, Lean typecheck, or proof attempt.",
            ],
            [
                "must distinguish coordinate feasibility from a log/log1p replacement claim",
                "must keep protected logarithmic runtime controls in place",
                "must include domain-edge negative controls before any proof work",
                "must keep proof-attempt and implementation claims false in D74 unless separately selected",
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
            58,
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
            "human_approved_probability_logit_public_copy_gate",
            "public_copy_gate_lane",
            "human_approved_public_copy_gate",
            "human-approved probability-logit public copy gate",
            "private copy boundary only",
            "public copy requires human approval",
            ["explicit human approval required"],
            "candidate_later_requires_human_approval",
            37,
            "public_copy_gate_not_research_candidate",
            "Future human-approved probability-logit public copy gate",
            [
                "D71 froze probability-logit private copy boundaries, but no human approval is recorded.",
                "Public copy should remain behind a separate human gate.",
            ],
            [
                "requires explicit human approval",
                "must reuse D71 frozen caveats and blocked phrases",
                "must not imply log/log1p/logit replacement, runtime advantage, or public readiness",
            ],
            [],
            "protected_log_and_log1p_remain_runtime_controls",
        ),
    ]
    selected = next(candidate for candidate in candidates if candidate["selectionStatus"] == "selected_next")
    summary = {
        "sourceSelector": selector["artifactId"],
        "sourceSelectedOptionId": selector["summary"]["selectedOptionId"],
        "sourceSelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "sourceFrozenWitnessName": selector["summary"]["frozenWitnessName"],
        "sourceFrozenStatement": selector["summary"]["frozenCheckedStatement"],
        "sourceFrozenGuardCount": selector["summary"]["frozenGuardCount"],
        "sourceFrozenGuards": selector["summary"]["frozenGuards"],
        "sourceFrozenCaveatCount": selector["summary"]["frozenCaveatCount"],
        "sourceFrozenBlockedPhraseCount": selector["summary"]["frozenBlockedPhraseCount"],
        "sourceNegativeControlCount": selector["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": selector["summary"]["sourceBlockerCount"],
        "sourceRuntimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "sourceRuntimeGuardrailStatus": selector["summary"]["runtimeGuardrailStatus"],
        "sourceGuardBoundaryStatus": selector["summary"]["guardBoundaryStatus"],
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
        "log1pShiftedBoundaryCandidateSelected": True,
        "witnessFeasibilityRecorded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "candidateProvedThisPhase": False,
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
            for key in ["bounded_identity_candidate_selected", "log1p_shifted_boundary_candidate_selected"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"bounded_identity_candidate_selected", "log1p_shifted_boundary_candidate_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_bounded_identity_branch_candidate_selector_d73_v0",
        "artifactId": "eml-d73-bounded-identity-branch-candidate-selector",
        "status": STATUS,
        "decision": "select_log1p_shifted_boundary_coordinate_candidate",
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
    if payload["sourceSelector"] != "eml-d72-post-probability-logit-pause-next-selector":
        raise ValueError("D73 must consume D72")
    if summary["sourceSelectedOptionId"] != "next_bounded_identity_branch_selector":
        raise ValueError("D73 requires D72 bounded identity selection")
    if summary["sourceSelectedNextArtifact"] != "EML-D73 bounded identity branch candidate selector":
        raise ValueError("unexpected D72 next artifact")
    if summary["sourceFrozenWitnessName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
        raise ValueError("unexpected frozen source witness")
    if summary["sourceFrozenStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected frozen source statement")
    if summary["sourceFrozenGuardCount"] != 2 or summary["sourceFrozenGuards"] != ["0 < p", "p < 1"]:
        raise ValueError("D71 frozen guard boundary drift")
    if summary["sourceFrozenCaveatCount"] != 9 or summary["sourceFrozenBlockedPhraseCount"] != 12:
        raise ValueError("D71 freeze caveat/blocker counts drifted")
    if summary["sourceNegativeControlCount"] != 4 or summary["sourceBlockerCount"] != 4:
        raise ValueError("D71 source negative control/blocker counts drifted")
    if summary["sourceRuntimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("D71 runtime control drift")
    if summary["sourceRuntimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("D71 runtime guardrail drift")
    if summary["sourceGuardBoundaryStatus"] != "guarded_domain_boundary_required":
        raise ValueError("D71 guard boundary status drift")
    if summary["sourcePublicAtlasStatus"] != "held_private":
        raise ValueError("D71 public hold drift")
    if summary["candidateCount"] != 3:
        raise ValueError("expected three bounded candidates")
    if summary["selectedCandidateId"] != "log1p_shifted_boundary_coordinate":
        raise ValueError("unexpected selected candidate")
    if summary["selectedFamily"] != "guarded_log1p_shifted_coordinate":
        raise ValueError("unexpected selected family")
    if summary["selectedSourceFrontierId"] != "post_probability_logit_pause_identity_lane":
        raise ValueError("unexpected source frontier id")
    if summary["selectedProposedStatement"] != "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x":
        raise ValueError("unexpected proposed statement")
    if summary["selectedNextArtifact"] != "EML-D74 log1p shifted boundary coordinate feasibility packet":
        raise ValueError("unexpected next artifact")
    if summary["selectedGuardCount"] != 1:
        raise ValueError("selected candidate should have one guard")
    if summary["selectedDuplicatesCheckedWitness"] is not False:
        raise ValueError("selected candidate must not duplicate a checked witness")
    if summary["selectedDuplicateCheckedWitnessCount"] != 0:
        raise ValueError("duplicate witness count drift")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime control drift")
    for key in [
        "boundedIdentityCandidateSelected",
        "log1pShiftedBoundaryCandidateSelected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "witnessFeasibilityRecorded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "candidateProvedThisPhase",
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
    for key in ["bounded_identity_candidate_selected", "log1p_shifted_boundary_candidate_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"bounded_identity_candidate_selected", "log1p_shifted_boundary_candidate_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_bounded_identity_branch_candidate_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_one_log1p_shifted_boundary_candidate_no_proof_no_runtime_claim",
        "source": f"python/results/eml_d73_bounded_identity_branch_candidate_selector/eml_d73_bounded_identity_branch_candidate_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d73_bounded_identity_branch_candidate_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedProposedStatement": payload["summary"]["selectedProposedStatement"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D74 as a log1p shifted boundary coordinate feasibility packet; do not edit MachLib yet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D73 Bounded Identity Branch Candidate Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected candidate: `{payload['summary']['selectedCandidateId']}`",
        "",
        "D73 selects one bounded identity candidate after the D72 post-pause selector.",
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
    result_path = out_dir / f"eml_d73_bounded_identity_branch_candidate_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d73_bounded_identity_branch_candidate_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d73_bounded_identity_branch_candidate_selector.json"
    feed_path = command_feed_dir / f"eml_d73_bounded_identity_branch_candidate_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d73_bounded_identity_branch_candidate_selector")
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
    print("EML_D73_BOUNDED_IDENTITY_BRANCH_CANDIDATE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
