#!/usr/bin/env python3
"""EML-D56 expm1 boundary identity feasibility packet."""

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

from scripts import eml_d55_bounded_identity_branch_candidate_selector as d55  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_expm1_boundary_identity_feasibility.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D56_EXPM1_BOUNDARY_IDENTITY_FEASIBILITY_PASS"

CLAIM_FLAGS = {
    "witness_feasibility_recorded": True,
    "bounded_identity_candidate_selected": True,
    "expm1_boundary_candidate_selected": True,
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
    "EML-D56 records feasibility only; it does not edit MachLib, typecheck Lean, or start a proof attempt.",
    "D56 keeps protected expm1 as the runtime and numerical-stability control and makes no protected expm1 replacement claim.",
    "D56 does not approve public copy, promote public surfaces, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/exp replacement, or broad EML superiority.",
]

FEASIBILITY_ITEMS = [
    {
        "itemId": "selected_branch_matches_d55",
        "status": "satisfied",
        "evidence": "D55 selected expm1_boundary_identity as selected_next.",
        "reviewNote": "The feasibility packet stays inside the selected bounded identity candidate.",
    },
    {
        "itemId": "statement_shape_small",
        "status": "satisfied",
        "evidence": "The proposed statement is eml x (exp 1) = exp x - 1.",
        "reviewNote": "This is one scoped identity candidate, not a family theorem.",
    },
    {
        "itemId": "proof_shape_visible",
        "status": "satisfied",
        "evidence": "Unfolding eml gives exp x - log (exp 1); log_exp reduces log (exp 1) to 1.",
        "reviewNote": "The expected witness attempt should be a small definitional/log-exp rewrite, not a search result.",
    },
    {
        "itemId": "non_duplicate_boundary_preserved",
        "status": "satisfied",
        "evidence": "D55 records no duplicate checked witness and distinguishes the candidate from eml x 1 = exp x plus the D10 constants bundle.",
        "reviewNote": "The candidate uses argument exp 1, so it should not be treated as the checked eml x 1 witness.",
    },
    {
        "itemId": "protected_expm1_runtime_control_preserved",
        "status": "satisfied",
        "evidence": "The packet keeps protected_expm1_remains_runtime_control and makes no runtime lowering claim.",
        "reviewNote": "The identity may be proof-shape useful while protected expm1 remains the numerical runtime control.",
    },
]

BLOCKERS = [
    {
        "blockerId": "runtime_relabeling",
        "severity": "hard_blocker",
        "description": "The identity must not be relabeled as runtime lowering, protected expm1 replacement, or runtime advantage.",
    },
    {
        "blockerId": "duplicate_exp_branch_witness",
        "severity": "hard_blocker",
        "description": "Any future witness attempt must distinguish eml x (exp 1) from the already checked eml x 1 = exp x branch.",
    },
    {
        "blockerId": "broad_family_language",
        "severity": "hard_blocker",
        "description": "The packet must not broaden the single identity into all expm1-style, log/exp, or constant-coordinate identities.",
    },
    {
        "blockerId": "proof_or_typecheck_claim",
        "severity": "hard_blocker",
        "description": "D56 records feasibility only; any proof, Lean typecheck, or MachLib edit requires a separate D57 phase.",
    },
]


def selected_candidate_by_id(payload: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in payload["branchCandidates"] if item["candidateId"] == candidate_id)


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d55.build_payload(atlas_gate_path)
    d55.validate_payload(selector)
    selected = selected_candidate_by_id(selector, "expm1_boundary_identity")
    proposed_witness = {
        "candidateId": selected["candidateId"],
        "family": selected["family"],
        "sourceFrontierId": selected["sourceFrontierId"],
        "proposedMachlibName": "MachLib.Real.expm1_boundary_identity_witness",
        "statementKind": "unguarded_real_identity",
        "emlShape": selected["emlShape"],
        "standardShape": selected["standardShape"],
        "proposedStatement": selected["proposedStatement"],
        "guardShape": selected["guardShape"],
        "guardPolicy": "no_domain_guard_required_for_log_exp_one",
        "semanticControl": "standard_real_exp_log_exp_one_control",
        "runtimeControl": selected["runtimeControl"],
        "expectedProofShape": [
            "unfold eml",
            "rewrite log (exp 1) to 1",
            "normalize subtraction expression without changing runtime lowering",
        ],
        "nextArtifact": "EML-D57 expm1 boundary identity MachLib witness attempt or blocker",
    }
    summary = {
        "sourceCandidateSelector": selector["artifactId"],
        "sourceSelectedCandidateId": selector["summary"]["selectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["selectedFamily"],
        "sourceSelectedSourceFrontierId": selector["summary"]["selectedSourceFrontierId"],
        "sourceSelectedProposedStatement": selector["summary"]["selectedProposedStatement"],
        "sourceRuntimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "sourceFrozenWitnessName": selector["summary"]["sourceFrozenWitnessName"],
        "sourceFrozenStatement": selector["summary"]["sourceFrozenStatement"],
        "sourceFrozenCaveatCount": selector["summary"]["sourceFrozenCaveatCount"],
        "sourceFrozenBlockedPhraseCount": selector["summary"]["sourceFrozenBlockedPhraseCount"],
        "feasibilityRecorded": True,
        "feasibilityStatus": "feasible_for_scoped_witness_attempt",
        "proposedMachlibName": proposed_witness["proposedMachlibName"],
        "proposedStatement": proposed_witness["proposedStatement"],
        "guardCount": len(proposed_witness["guardShape"]),
        "noDomainGuardRequired": True,
        "expectedProofStepCount": len(proposed_witness["expectedProofShape"]),
        "feasibilityItemCount": len(FEASIBILITY_ITEMS),
        "blockerCount": len(BLOCKERS),
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
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
        "claimFlagsAllBounded": all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "witness_feasibility_recorded",
                "bounded_identity_candidate_selected",
                "expm1_boundary_candidate_selected",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_expm1_boundary_identity_feasibility_v0",
        "artifactId": "eml-d56-expm1-boundary-identity-feasibility-packet",
        "status": STATUS,
        "decision": "record_expm1_boundary_identity_feasibility",
        "date": DATE,
        "sourceCandidateSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "proposedWitness": proposed_witness,
        "feasibilityItems": list(FEASIBILITY_ITEMS),
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
    if payload["sourceCandidateSelector"] != "eml-d55-bounded-identity-branch-candidate-selector":
        raise ValueError("D56 must consume D55")
    if summary["sourceSelectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("D56 must preserve the D55 selected candidate")
    if summary["sourceSelectedFamily"] != "protected_runtime_boundary_identity":
        raise ValueError("D56 must preserve the D55 selected family")
    if summary["sourceSelectedSourceFrontierId"] != "expm1_failure_boundary_v1":
        raise ValueError("unexpected source frontier id")
    if summary["sourceSelectedProposedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected source proposed statement")
    if summary["sourceRuntimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("D55 runtime control drift")
    if summary["sourceFrozenWitnessName"] != "MachLib.Real.constant_coordinate_zero_exp_two_witness":
        raise ValueError("D53 frozen witness drift")
    if summary["sourceFrozenStatement"] != "eml 0 (exp (1 + 1)) = -1":
        raise ValueError("D53 frozen statement drift")
    if summary["sourceFrozenCaveatCount"] != 8 or summary["sourceFrozenBlockedPhraseCount"] != 10:
        raise ValueError("D53 frozen caveat/blocker counts drifted")
    if witness["proposedMachlibName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected proposed MachLib name")
    if witness["proposedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected proposed statement")
    if witness["guardShape"] != []:
        raise ValueError("unexpected guard shape")
    if summary["guardCount"] != 0:
        raise ValueError("expected no guards")
    if summary["noDomainGuardRequired"] is not True:
        raise ValueError("no-domain guard policy must be explicit")
    if summary["feasibilityRecorded"] is not True:
        raise ValueError("feasibility must be recorded")
    if summary["feasibilityStatus"] != "feasible_for_scoped_witness_attempt":
        raise ValueError("unexpected feasibility status")
    if summary["expectedProofStepCount"] != 3:
        raise ValueError("expected three proof-shape notes")
    if summary["feasibilityItemCount"] != 5:
        raise ValueError("expected five feasibility items")
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
        raise ValueError("runtime lowering control drift")
    if summary["nextArtifact"] != "EML-D57 expm1 boundary identity MachLib witness attempt or blocker":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in [
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "expm1_boundary_candidate_selected",
    ]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {
            "witness_feasibility_recorded",
            "bounded_identity_candidate_selected",
            "expm1_boundary_candidate_selected",
        } and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(item["status"] != "satisfied" for item in payload["feasibilityItems"]):
        raise ValueError("all feasibility items must be satisfied")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_expm1_boundary_identity_feasibility_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_feasibility_packet_no_machlib_edit_no_typecheck_no_runtime_claim",
        "source": f"python/results/eml_d56_expm1_boundary_identity_feasibility_packet/eml_d56_expm1_boundary_identity_feasibility_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d56_expm1_boundary_identity_feasibility_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "proposedMachlibName": payload["summary"]["proposedMachlibName"],
        "proposedStatement": payload["summary"]["proposedStatement"],
        "nextAction": "Run EML-D57 only as a scoped MachLib witness attempt or precise blocker.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D56 Expm1 Boundary Identity Feasibility Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Proposed witness: `{payload['summary']['proposedMachlibName']}`",
        "",
        f"Statement: `{payload['summary']['proposedStatement']}`",
        "",
        "D56 records feasibility for one expm1-boundary identity before any MachLib edit.",
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
            "## Blockers",
            "",
            "| Blocker | Severity | Description |",
            "|---|---|---|",
        ]
    )
    for blocker in payload["blockers"]:
        lines.append(f"| `{blocker['blockerId']}` | `{blocker['severity']}` | {blocker['description']} |")
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
    result_path = out_dir / f"eml_d56_expm1_boundary_identity_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d56_expm1_boundary_identity_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d56_expm1_boundary_identity_feasibility_packet.json"
    feed_path = command_feed_dir / f"eml_d56_expm1_boundary_identity_feasibility_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d56_expm1_boundary_identity_feasibility_packet")
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
    print("EML_D56_EXPM1_BOUNDARY_IDENTITY_FEASIBILITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
