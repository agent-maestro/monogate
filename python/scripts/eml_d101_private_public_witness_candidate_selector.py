#!/usr/bin/env python3
"""EML-D101 private public-witness candidate selector."""

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

from scripts import eml_d100_bounded_artifact_target_set_consolidation_review as d100  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_private_public_witness_candidate_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D101_PRIVATE_PUBLIC_WITNESS_CANDIDATE_SELECTOR_PASS"

CLAIM_FLAGS = {
    "public_witness_candidate_selected": True,
    "private_selector_only": True,
    "checked_witness_core_observed": True,
    "expm1_boundary_candidate_selected": True,
    "public_witness_copy_packet_recommended": True,
    "public_copy_drafted": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "public_page_created": False,
    "claim_topology_surface_created": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_log_replacement_claim": False,
    "protected_log1p_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
    "broad_log1p_family_claim": False,
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
    "catalog_completeness_claim": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D101 privately selects one checked witness as a candidate for later public-witness copy drafting; it does not draft, approve, publish, or promote public copy.",
    "D101 selects the expm1-boundary identity because it is narrow, already checked, and has prior private copy-review history; it does not claim broad EML advantage or expm1 replacement.",
    "D101 does not create a public page, update public surfaces, edit MachLib, typecheck Lean, start proof work, change runtime lowering, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime performance, compiler correctness, formal equivalence, catalog completeness, public readiness, or full EML semantics.",
]


def candidate_option(
    option_id: str,
    witness_id: str,
    machlib_name: str,
    family: str,
    statement: str,
    guard_summary: str,
    runtime_control: str,
    status: str,
    priority_score: int,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "witnessId": witness_id,
        "machlibName": machlib_name,
        "family": family,
        "checkedStatement": statement,
        "guardSummary": guard_summary,
        "runtimeControl": runtime_control,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_candidate_options() -> list[dict[str, Any]]:
    return [
        candidate_option(
            "expm1_boundary_identity_public_witness_candidate",
            "expm1_boundary_identity",
            "MachLib.Real.expm1_boundary_identity_witness",
            "expm1_boundary",
            "eml x (exp 1) = exp x - 1",
            "no extra real-domain guard recorded",
            "protected_expm1_remains_runtime_control",
            "selected_next",
            96,
            "EML-D102 expm1 boundary public-witness copy packet",
            [
                "The witness is one compact equality with no extra real-domain guard recorded.",
                "Prior D60/D61/D62 packets already preserved the protected-expm1 runtime-control boundary.",
                "The statement can be explained humbly as one checked MachLib witness without claiming replacement, performance, or public readiness.",
            ],
            [
                "must remain private until a later copy packet is reviewed",
                "must not imply protected expm1 replacement",
                "must not imply runtime or numerical-stability advantage",
            ],
        ),
        candidate_option(
            "positive_log_exp_roundtrip_public_witness_candidate",
            "positive_log_exp_roundtrip",
            "MachLib.Real.positive_log_exp_roundtrip_witness",
            "positive_log_exp",
            "0 < x -> eml (log x) (exp 1) = x",
            "0 < x",
            "standard_log_exp_remains_runtime_control",
            "candidate_later",
            83,
            "Future positive log-exp public-witness copy packet",
            [
                "This witness is also strong and human-readable.",
                "Its positive-domain guard makes it slightly more guard-heavy than the selected expm1 boundary for a first public-witness candidate.",
            ],
            [
                "must preserve 0 < x guard",
                "must not claim log/exp replacement",
                "must not imply broad log-exp coverage",
            ],
        ),
        candidate_option(
            "subtraction_boundary_affine_offset_public_witness_candidate",
            "subtraction_boundary_affine_offset",
            "MachLib.Real.subtraction_boundary_affine_offset_witness",
            "subtraction_boundary",
            "checked affine-offset subtraction boundary witness",
            "0 < x + y",
            "standard_subtraction_remains_runtime_control",
            "candidate_later",
            78,
            "Future subtraction-boundary public-witness copy packet",
            [
                "The subtraction boundary family is strong and useful.",
                "It is better suited to a family-facing artifact after the first single-witness public-copy lane is stabilized.",
            ],
            [
                "must preserve positivity guard",
                "must not claim broad subtraction-family coverage",
                "must not imply arbitrary-depth support",
            ],
        ),
        candidate_option(
            "log1p_affine_scaled_boundary_public_witness_candidate",
            "log1p_affine_scaled_boundary_coordinate",
            "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness",
            "log1p_affine_scaled_boundary",
            "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x",
            "0 < 1 + a * x",
            "protected_log_and_log1p_remain_runtime_controls",
            "candidate_later_after_affine_branch_rest",
            64,
            "Future affine log1p public-witness copy packet",
            [
                "The affine log1p witness is fresh and high-quality.",
                "D98 intentionally froze that branch, so it should rest before becoming the first public-witness candidate.",
            ],
            [
                "respect D98 branch freeze",
                "must not claim broad log1p-family coverage",
                "must preserve protected log/log1p runtime controls",
            ],
        ),
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    review = d100.build_payload(atlas_gate_path)
    d100.validate_payload(review)
    options = build_candidate_options()
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceReview": review["artifactId"],
        "sourceRecommendedNextOptionId": review["summary"]["recommendedNextOptionId"],
        "sourceRecommendedNextArtifact": review["summary"]["recommendedNextArtifact"],
        "sourceCheckedWitnessCoreCount": review["summary"]["checkedWitnessCoreCount"],
        "sourceTargetMin": review["summary"]["targetMin"],
        "sourceTargetMax": review["summary"]["targetMax"],
        "sourceAdditionalArtifactsNeededForLowerBound": review["summary"]["additionalArtifactsNeededForLowerBound"],
        "sourceRemainingSlotsBeforeUpperBound": review["summary"]["remainingSlotsBeforeUpperBound"],
        "sourceSelectorOnlyPacketsCountedAsFinalArtifacts": review["summary"][
            "selectorOnlyPacketsCountedAsFinalArtifacts"
        ],
        "sourceAffineLog1pBranchFrozenObserved": review["summary"]["affineLog1pBranchFrozenObserved"],
        "candidateOptionCount": len(options),
        "publicWitnessCandidateSelected": True,
        "privateSelectorOnly": True,
        "checkedWitnessCoreObserved": True,
        "selectedOptionId": selected["optionId"],
        "selectedCandidateId": selected["witnessId"],
        "selectedWitnessName": selected["machlibName"],
        "selectedFamily": selected["family"],
        "selectedCheckedStatement": selected["checkedStatement"],
        "selectedGuardSummary": selected["guardSummary"],
        "selectedRuntimeControl": selected["runtimeControl"],
        "selectedNextArtifact": selected["nextArtifact"],
        "expm1BoundaryCandidateSelected": True,
        "publicWitnessCopyPacketRecommended": True,
        "publicCopyDrafted": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "publicPageCreated": False,
        "claimTopologySurfaceCreated": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "newIdentityCandidateSelected": False,
        "nextBoundedIdentityBranchSelected": False,
        "boundedTrigFeasibilitySelected": False,
        "advantageLabCaseAdded": False,
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
        "runtimePerformanceClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "fullEmlSemanticsClaim": False,
        "catalogCompletenessClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsSelectorOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "public_witness_candidate_selected",
                "private_selector_only",
                "checked_witness_core_observed",
                "expm1_boundary_candidate_selected",
                "public_witness_copy_packet_recommended",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "public_witness_candidate_selected",
                "private_selector_only",
                "checked_witness_core_observed",
                "expm1_boundary_candidate_selected",
                "public_witness_copy_packet_recommended",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_private_public_witness_candidate_selector_v0",
        "artifactId": "eml-d101-private-public-witness-candidate-selector",
        "status": STATUS,
        "decision": "select_expm1_boundary_identity_as_private_public_witness_candidate",
        "date": DATE,
        "sourceReview": review["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "candidateOptions": options,
        "selectedCandidate": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceReview"] != "eml-d100-bounded-artifact-target-set-consolidation-review":
        raise ValueError("D101 must consume D100")
    if summary["sourceRecommendedNextOptionId"] != "private_public_witness_candidate_selector":
        raise ValueError("unexpected D100 recommended option")
    if summary["sourceRecommendedNextArtifact"] != "EML-D101 private public-witness candidate selector":
        raise ValueError("unexpected D100 recommended artifact")
    if summary["sourceCheckedWitnessCoreCount"] != 13:
        raise ValueError("checked witness core count drift")
    if summary["sourceTargetMin"] != 15 or summary["sourceTargetMax"] != 25:
        raise ValueError("target range drift")
    if summary["sourceAdditionalArtifactsNeededForLowerBound"] != 2:
        raise ValueError("lower-bound gap drift")
    if summary["sourceRemainingSlotsBeforeUpperBound"] != 12:
        raise ValueError("upper-bound slot drift")
    if summary["sourceSelectorOnlyPacketsCountedAsFinalArtifacts"] is not False:
        raise ValueError("selector-only packets must not count as final artifacts")
    if summary["sourceAffineLog1pBranchFrozenObserved"] is not True:
        raise ValueError("D98 affine log1p freeze must remain observed")
    if summary["candidateOptionCount"] != 4:
        raise ValueError("expected four candidate options")
    selected_options = [
        option for option in payload["candidateOptions"] if option["selectionStatus"] == "selected_next"
    ]
    if len(selected_options) != 1:
        raise ValueError("D101 must select exactly one candidate")
    if payload["selectedCandidate"] != selected_options[0]:
        raise ValueError("selected candidate mismatch")
    for key in [
        "publicWitnessCandidateSelected",
        "privateSelectorOnly",
        "checkedWitnessCoreObserved",
        "expm1BoundaryCandidateSelected",
        "publicWitnessCopyPacketRecommended",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedOptionId"] != "expm1_boundary_identity_public_witness_candidate":
        raise ValueError("unexpected selected option")
    if summary["selectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("unexpected selected candidate")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected selected witness")
    if summary["selectedFamily"] != "expm1_boundary":
        raise ValueError("unexpected selected family")
    if summary["selectedCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["selectedGuardSummary"] != "no extra real-domain guard recorded":
        raise ValueError("unexpected guard summary")
    if summary["selectedRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("unexpected runtime control")
    if summary["selectedNextArtifact"] != "EML-D102 expm1 boundary public-witness copy packet":
        raise ValueError("unexpected next artifact")
    for key in [
        "publicCopyDrafted",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "claimTopologySurfaceCreated",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "boundedTrigFeasibilitySelected",
        "advantageLabCaseAdded",
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
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "fullEmlSemanticsClaim",
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsSelectorOnly"] is not True:
        raise ValueError("claim flags must remain selector-only")
    allowed_true = {
        "public_witness_candidate_selected",
        "private_selector_only",
        "checked_witness_core_observed",
        "expm1_boundary_candidate_selected",
        "public_witness_copy_packet_recommended",
    }
    for key in allowed_true:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(option["publicPromotionAllowed"] for option in payload["candidateOptions"]):
        raise ValueError("candidate options must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_private_public_witness_candidate_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_selects_one_checked_expm1_boundary_public_witness_candidate_no_public_copy_no_new_proof",
        "source": f"python/results/eml_d101_private_public_witness_candidate_selector/eml_d101_private_public_witness_candidate_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d101_private_public_witness_candidate_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D102 as a private expm1-boundary public-witness copy packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D101 Private Public-Witness Candidate Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D101 privately selects exactly one checked witness as the candidate for a later public-witness copy packet.",
        "",
        "## Selected Candidate",
        "",
        f"- witness: `{payload['summary']['selectedWitnessName']}`",
        f"- statement: `{payload['summary']['selectedCheckedStatement']}`",
        f"- guard summary: `{payload['summary']['selectedGuardSummary']}`",
        f"- runtime control: `{payload['summary']['selectedRuntimeControl']}`",
        f"- next artifact: `{payload['summary']['selectedNextArtifact']}`",
        f"- public copy drafted: `{payload['summary']['publicCopyDrafted']}`",
        f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
        "",
        "## Candidate Options",
        "",
        "| Option | Witness | Status | Next artifact |",
        "|---|---|---|---|",
    ]
    for option in payload["candidateOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['witnessId']}` | `{option['selectionStatus']}` | {option['nextArtifact']} |"
        )
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    atlas_gate_path: Path,
) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d101_private_public_witness_candidate_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d101_private_public_witness_candidate_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d101_private_public_witness_candidate_selector.json"
    feed_path = command_feed_dir / f"eml_d101_private_public_witness_candidate_selector_feed_{STAMP}.json"
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
    parser.add_argument(
        "--atlas-gate-path",
        type=Path,
        default=ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d101_private_public_witness_candidate_selector")
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
    print("EML_D101_PRIVATE_PUBLIC_WITNESS_CANDIDATE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
