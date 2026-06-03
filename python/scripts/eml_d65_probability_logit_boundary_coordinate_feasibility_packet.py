#!/usr/bin/env python3
"""EML-D65 probability logit boundary coordinate feasibility packet."""

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

from scripts import eml_d64_bounded_identity_branch_candidate_selector as d64  # noqa: E402

DATE = "2026-06-03"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_probability_logit_boundary_coordinate_feasibility.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D65_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_FEASIBILITY_PASS"

CLAIM_FLAGS = {
    "witness_feasibility_recorded": True,
    "bounded_identity_candidate_selected": True,
    "probability_logit_boundary_candidate_selected": True,
    "guarded_domain_obligations_recorded": True,
    "negative_controls_recorded": True,
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
    "EML-D65 records guarded feasibility only; it does not edit MachLib, typecheck Lean, or start a proof attempt.",
    "D65 keeps protected log/log1p controls as runtime controls and makes no log, log1p, or logit replacement claim.",
    "D65 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, formal equivalence, or broad EML superiority.",
]

FEASIBILITY_ITEMS = [
    {
        "itemId": "selected_branch_matches_d64",
        "status": "satisfied",
        "evidence": "D64 selected probability_logit_boundary_coordinate as selected_next.",
        "reviewNote": "The feasibility packet stays inside the selected bounded identity candidate.",
    },
    {
        "itemId": "domain_obligations_visible",
        "status": "satisfied",
        "evidence": "The statement carries guards 0 < p and p < 1, giving 0 < p and 0 < 1 - p for logarithmic rewrites.",
        "reviewNote": "The coordinate is feasible only as a guarded-domain statement.",
    },
    {
        "itemId": "proof_shape_visible",
        "status": "satisfied",
        "evidence": "Unfolding eml gives exp (log p) - log (exp (log (1 - p))); guarded exp-log/log-exp rewrites reduce this to p - log (1 - p).",
        "reviewNote": "The expected witness attempt should be a small guarded rewrite, not a search or runtime claim.",
    },
    {
        "itemId": "negative_controls_required",
        "status": "satisfied",
        "evidence": "Boundary controls for p <= 0, p >= 1, and unguarded statements are recorded as blockers.",
        "reviewNote": "Any future proof attempt must preserve the two domain guards.",
    },
    {
        "itemId": "protected_log_runtime_control_preserved",
        "status": "satisfied",
        "evidence": "The packet keeps protected_log_and_log1p_remain_runtime_controls and records no runtime lowering change.",
        "reviewNote": "The identity may be proof-shape useful while protected logarithmic routines remain runtime controls.",
    },
    {
        "itemId": "non_duplicate_boundary_preserved",
        "status": "satisfied",
        "evidence": "D64 records no duplicate checked witness for the selected probability-logit coordinate.",
        "reviewNote": "The candidate is a new guarded coordinate, not a relabeling of an existing checked witness.",
    },
]

NEGATIVE_CONTROLS = [
    {
        "controlId": "p_zero_boundary_blocked",
        "status": "blocked_by_guard",
        "blockedCondition": "p = 0",
        "reason": "log p is outside the guarded real-log rewrite domain.",
    },
    {
        "controlId": "p_one_boundary_blocked",
        "status": "blocked_by_guard",
        "blockedCondition": "p = 1",
        "reason": "log (1 - p) is outside the guarded real-log rewrite domain.",
    },
    {
        "controlId": "ungarded_probability_coordinate_blocked",
        "status": "blocked_by_guard",
        "blockedCondition": "missing either 0 < p or p < 1",
        "reason": "The feasibility argument depends on both positive logarithm arguments.",
    },
    {
        "controlId": "runtime_logit_replacement_blocked",
        "status": "blocked_by_claim_boundary",
        "blockedCondition": "claiming log/log1p/logit runtime replacement",
        "reason": "D65 records proof-shape feasibility only and keeps protected log/log1p runtime controls.",
    },
]

BLOCKERS = [
    {
        "blockerId": "domain_edge_loss",
        "severity": "hard_blocker",
        "description": "Any future witness attempt must carry both guards and derive the 0 < 1 - p obligation before rewriting log (1 - p).",
    },
    {
        "blockerId": "runtime_relabeling",
        "severity": "hard_blocker",
        "description": "The identity must not be relabeled as runtime lowering, log/log1p replacement, logit replacement, or runtime advantage.",
    },
    {
        "blockerId": "proof_or_typecheck_claim",
        "severity": "hard_blocker",
        "description": "D65 records feasibility only; any proof, Lean typecheck, or MachLib edit requires a separate D66 phase.",
    },
    {
        "blockerId": "broad_probability_language",
        "severity": "hard_blocker",
        "description": "The packet must not broaden the single guarded coordinate into all logit, probability, entropy, or logistic identities.",
    },
]


def selected_candidate_by_id(payload: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in payload["branchCandidates"] if item["candidateId"] == candidate_id)


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d64.build_payload(atlas_gate_path)
    d64.validate_payload(selector)
    selected = selected_candidate_by_id(selector, "probability_logit_boundary_coordinate")
    proposed_witness = {
        "candidateId": selected["candidateId"],
        "family": selected["family"],
        "sourceFrontierId": selected["sourceFrontierId"],
        "proposedMachlibName": "MachLib.Real.probability_logit_boundary_coordinate_witness",
        "statementKind": "guarded_real_identity",
        "emlShape": selected["emlShape"],
        "standardShape": selected["standardShape"],
        "sourceProposedStatement": selected["proposedStatement"],
        "proposedStatement": "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)",
        "guardShape": selected["guardShape"],
        "derivedDomainObligations": ["0 < p", "0 < 1 - p"],
        "guardPolicy": "both_probability_interval_guards_required",
        "semanticControl": "guarded_real_exp_log_rewrite_control",
        "runtimeControl": selected["runtimeControl"],
        "expectedProofShape": [
            "introduce guards 0 < p and p < 1",
            "derive 0 < 1 - p from p < 1",
            "unfold eml",
            "rewrite exp (log p) to p under 0 < p",
            "rewrite log (exp (log (1 - p))) to log (1 - p)",
            "normalize subtraction expression without changing runtime lowering",
        ],
        "nextArtifact": "EML-D66 probability logit boundary coordinate MachLib witness attempt or blocker",
    }
    summary = {
        "sourceCandidateSelector": selector["artifactId"],
        "sourceSelectedCandidateId": selector["summary"]["selectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["selectedFamily"],
        "sourceSelectedSourceFrontierId": selector["summary"]["selectedSourceFrontierId"],
        "sourceSelectedProposedStatement": selector["summary"]["selectedProposedStatement"],
        "sourceSelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "sourceRuntimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "sourceFrozenWitnessName": selector["summary"]["sourceFrozenWitnessName"],
        "sourceFrozenStatement": selector["summary"]["sourceFrozenStatement"],
        "sourceFrozenCaveatCount": selector["summary"]["sourceFrozenCaveatCount"],
        "sourceFrozenBlockedPhraseCount": selector["summary"]["sourceFrozenBlockedPhraseCount"],
        "feasibilityRecorded": True,
        "feasibilityStatus": "feasible_for_guarded_scoped_witness_attempt",
        "proposedMachlibName": proposed_witness["proposedMachlibName"],
        "proposedStatement": proposed_witness["proposedStatement"],
        "guardCount": len(proposed_witness["guardShape"]),
        "derivedDomainObligationCount": len(proposed_witness["derivedDomainObligations"]),
        "expectedProofStepCount": len(proposed_witness["expectedProofShape"]),
        "feasibilityItemCount": len(FEASIBILITY_ITEMS),
        "negativeControlCount": len(NEGATIVE_CONTROLS),
        "blockerCount": len(BLOCKERS),
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
        "runtimeLoweringControl": selected["runtimeControl"],
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
        "nextArtifact": proposed_witness["nextArtifact"],
        "claimFlagsFeasibilityOnly": all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "witness_feasibility_recorded",
                "bounded_identity_candidate_selected",
                "probability_logit_boundary_candidate_selected",
                "guarded_domain_obligations_recorded",
                "negative_controls_recorded",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_probability_logit_boundary_coordinate_feasibility_v0",
        "artifactId": "eml-d65-probability-logit-boundary-coordinate-feasibility-packet",
        "status": STATUS,
        "decision": "record_probability_logit_boundary_coordinate_feasibility",
        "date": DATE,
        "sourceCandidateSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "proposedWitness": proposed_witness,
        "feasibilityItems": list(FEASIBILITY_ITEMS),
        "negativeControls": list(NEGATIVE_CONTROLS),
        "blockers": list(BLOCKERS),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    witness = payload["proposedWitness"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceCandidateSelector"] != "eml-d64-bounded-identity-branch-candidate-selector":
        raise ValueError("D65 must consume D64")
    if summary["sourceSelectedCandidateId"] != "probability_logit_boundary_coordinate":
        raise ValueError("D65 must preserve the D64 selected candidate")
    if summary["sourceSelectedFamily"] != "guarded_probability_log_coordinate":
        raise ValueError("D65 must preserve the D64 selected family")
    if summary["sourceSelectedSourceFrontierId"] != "probability_logit_boundary_v0":
        raise ValueError("unexpected source frontier id")
    if summary["sourceSelectedProposedStatement"] != "0 < p and p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected source proposed statement")
    if summary["sourceSelectedNextArtifact"] != "EML-D65 probability logit boundary coordinate feasibility packet":
        raise ValueError("unexpected D64 next artifact")
    if summary["sourceRuntimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("D64 runtime control drift")
    if summary["sourceFrozenWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("D62 frozen witness drift")
    if summary["sourceFrozenStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("D62 frozen statement drift")
    if summary["sourceFrozenCaveatCount"] != 8 or summary["sourceFrozenBlockedPhraseCount"] != 10:
        raise ValueError("D62 frozen caveat/blocker counts drifted")
    if witness["proposedMachlibName"] != "MachLib.Real.probability_logit_boundary_coordinate_witness":
        raise ValueError("unexpected proposed MachLib name")
    if witness["proposedStatement"] != "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)":
        raise ValueError("unexpected proposed statement")
    if witness["guardShape"] != ["0 < p", "p < 1"]:
        raise ValueError("unexpected guard shape")
    if witness["derivedDomainObligations"] != ["0 < p", "0 < 1 - p"]:
        raise ValueError("unexpected derived domain obligations")
    if summary["guardCount"] != 2:
        raise ValueError("expected two guards")
    if summary["derivedDomainObligationCount"] != 2:
        raise ValueError("expected two derived domain obligations")
    if summary["feasibilityRecorded"] is not True:
        raise ValueError("feasibility must be recorded")
    if summary["feasibilityStatus"] != "feasible_for_guarded_scoped_witness_attempt":
        raise ValueError("unexpected feasibility status")
    if summary["expectedProofStepCount"] != 6:
        raise ValueError("expected six proof-shape notes")
    if summary["feasibilityItemCount"] != 6:
        raise ValueError("expected six feasibility items")
    if summary["negativeControlCount"] != 4:
        raise ValueError("expected four negative controls")
    if summary["blockerCount"] != 4:
        raise ValueError("expected four blockers")
    for key in [
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
        raise ValueError("runtime lowering control drift")
    if summary["nextArtifact"] != "EML-D66 probability logit boundary coordinate MachLib witness attempt or blocker":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsFeasibilityOnly"] is not True:
        raise ValueError("claim flags must remain feasibility-only")
    for key in [
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "probability_logit_boundary_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
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
        } and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(item["status"] != "satisfied" for item in payload["feasibilityItems"]):
        raise ValueError("all feasibility items must be satisfied")
    if any(item["status"] not in {"blocked_by_guard", "blocked_by_claim_boundary"} for item in payload["negativeControls"]):
        raise ValueError("negative controls must be blocked")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_probability_logit_boundary_coordinate_feasibility_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_guarded_feasibility_packet_no_machlib_edit_no_typecheck_no_runtime_claim",
        "source": f"python/results/eml_d65_probability_logit_boundary_coordinate_feasibility_packet/eml_d65_probability_logit_boundary_coordinate_feasibility_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d65_probability_logit_boundary_coordinate_feasibility_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "proposedMachlibName": payload["summary"]["proposedMachlibName"],
        "proposedStatement": payload["summary"]["proposedStatement"],
        "guardCount": payload["summary"]["guardCount"],
        "negativeControlCount": payload["summary"]["negativeControlCount"],
        "nextAction": "Run EML-D66 only as a scoped guarded MachLib witness attempt or precise blocker.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D65 Probability Logit Boundary Coordinate Feasibility Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Proposed witness: `{payload['summary']['proposedMachlibName']}`",
        "",
        f"Statement: `{payload['summary']['proposedStatement']}`",
        "",
        "D65 records guarded feasibility before any MachLib edit, Lean typecheck, or proof attempt.",
        "",
        "## Feasibility Items",
        "",
        "| Item | Status | Review note |",
        "|---|---|---|",
    ]
    for item in payload["feasibilityItems"]:
        lines.append(f"| `{item['itemId']}` | `{item['status']}` | {item['reviewNote']} |")
    lines.extend(
        [
            "",
            "## Negative Controls",
            "",
            "| Control | Status | Reason |",
            "|---|---|---|",
        ]
    )
    for item in payload["negativeControls"]:
        lines.append(f"| `{item['controlId']}` | `{item['status']}` | {item['reason']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- source candidate: `{payload['summary']['sourceSelectedCandidateId']}`",
            f"- guard count: `{payload['summary']['guardCount']}`",
            f"- derived domain obligation count: `{payload['summary']['derivedDomainObligationCount']}`",
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
    result_path = out_dir / f"eml_d65_probability_logit_boundary_coordinate_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d65_probability_logit_boundary_coordinate_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d65_probability_logit_boundary_coordinate_feasibility_packet.json"
    feed_path = command_feed_dir / f"eml_d65_probability_logit_boundary_coordinate_feasibility_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d65_probability_logit_boundary_coordinate_feasibility_packet")
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
    print("EML_D65_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_FEASIBILITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
