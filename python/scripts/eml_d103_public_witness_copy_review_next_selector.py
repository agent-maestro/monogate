#!/usr/bin/env python3
"""EML-D103 public-witness copy-review next-action selector."""

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

from scripts import eml_d102_expm1_boundary_public_witness_copy_packet as d102  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_public_witness_copy_review_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D103_PUBLIC_WITNESS_COPY_REVIEW_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "private_copy_freeze_selected": True,
    "d102_copy_boundary_observed": True,
    "copy_freeze_started": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "public_page_created": False,
    "claim_topology_surface_created": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "protected_expm1_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "candidate_proved_this_phase": False,
    "proof_attempt_started": False,
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
    "EML-D103 selects the next private action after the D102 private copy packet; it does not start the freeze packet or approve public copy.",
    "D103 preserves the D102 draft, claim-boundaries section, checked statement, guard summary, and protected expm1 runtime-control boundary.",
    "D103 does not publish copy, create a public page, promote public surfaces, edit MachLib, typecheck Lean, start proof work, change runtime lowering, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime performance, compiler correctness, formal equivalence, public readiness, protected expm1 replacement, or broad EML advantage.",
]


def decision_option(
    option_id: str,
    lane: str,
    status: str,
    priority_score: int,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "lane": lane,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    packet = d102.build_payload(atlas_gate_path)
    d102.validate_payload(packet)
    options = [
        decision_option(
            "expm1_public_witness_copy_freeze_packet",
            "private_public_witness_copy_freeze_lane",
            "selected_next",
            91,
            "EML-D104 expm1 public-witness copy freeze packet",
            [
                "D102 created reviewable private copy but did not approve or publish it.",
                "A freeze packet can stabilize the exact statement, guard summary, draft sections, caveats, blocked phrases, and non-claims before any reviewer gate.",
                "Freezing the copy boundary keeps the first public-witness candidate useful without treating the private draft as public-ready.",
            ],
            [
                "must preserve D102 private draft and claim-boundaries text",
                "must keep public copy approval false",
                "must not treat copy freeze as human approval",
            ],
        ),
        decision_option(
            "human_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_explicit_human_approval",
            68,
            "Future human-approved expm1 public-witness copy gate",
            [
                "A human approval gate is necessary before publication.",
                "No explicit reviewer approval has been recorded yet, so it remains parked.",
            ],
            [
                "requires explicit human approval",
                "requires frozen D102 copy boundary or equivalent reviewer record",
                "must preserve protected expm1 runtime-control non-claims",
            ],
        ),
        decision_option(
            "private_claim_topology_surface_mvp",
            "private_claim_topology_lane",
            "candidate_later",
            63,
            "Future private Claim Topology / Evidence Surface MVP",
            [
                "The D100-D102 consolidation chain creates a good input for a private topology surface.",
                "It should wait until the first public-witness copy boundary is frozen.",
            ],
            [
                "must not claim renderer correctness",
                "must remain private",
                "must preserve approved versus blocked claim distinctions",
            ],
        ),
        decision_option(
            "next_public_witness_candidate_selector",
            "private_public_witness_lane",
            "candidate_later_after_freeze",
            52,
            "Future next public-witness candidate selector",
            [
                "A second witness may be useful after the first copy boundary is stable.",
                "Starting another candidate now would dilute the review path for the first public-witness packet.",
            ],
            [
                "requires D104 or equivalent boundary freeze",
                "must not inflate the bounded artifact target set with selector-only packets",
                "must avoid public-readiness language",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourcePacket": packet["artifactId"],
        "selectedWitnessName": packet["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": packet["summary"]["sourceSelectedCandidateId"],
        "selectedFamily": packet["summary"]["selectedFamily"],
        "checkedStatement": packet["summary"]["checkedStatement"],
        "guardSummary": packet["summary"]["guardSummary"],
        "runtimeControl": packet["summary"]["runtimeControl"],
        "d102PublicWitnessCopyPacketCreated": packet["summary"]["publicWitnessCopyPacketCreated"],
        "d102PrivateCopyReviewOnly": packet["summary"]["privateCopyReviewOnly"],
        "d102PublicCopyDraftedForReview": packet["summary"]["publicCopyDraftedForReview"],
        "d102ClaimBoundariesBoxIncluded": packet["summary"]["claimBoundariesBoxIncluded"],
        "d102CopySectionCount": packet["summary"]["copySectionCount"],
        "d102RequiredCaveatCount": packet["summary"]["requiredCaveatCount"],
        "d102BlockedPhraseCount": packet["summary"]["blockedPhraseCount"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "nextActionSelected": True,
        "privateCopyFreezeSelected": True,
        "copyFreezeStarted": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "publicPageCreated": False,
        "claimTopologySurfaceCreated": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
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
        "protectedExpm1ReplacementClaim": False,
        "runtimePerformanceClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "fullEmlSemanticsClaim": False,
        "catalogCompletenessClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in ["next_action_selected", "private_copy_freeze_selected", "d102_copy_boundary_observed"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"next_action_selected", "private_copy_freeze_selected", "d102_copy_boundary_observed"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_public_witness_copy_review_next_selector_v0",
        "artifactId": "eml-d103-public-witness-copy-review-next-selector",
        "status": STATUS,
        "decision": "select_expm1_public_witness_copy_freeze_packet_public_copy_unapproved",
        "date": DATE,
        "sourcePacket": packet["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "decisionOptions": options,
        "selectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourcePacket"] != "eml-d102-expm1-boundary-public-witness-copy-packet":
        raise ValueError("D103 must consume D102")
    for key in [
        "d102PublicWitnessCopyPacketCreated",
        "d102PrivateCopyReviewOnly",
        "d102PublicCopyDraftedForReview",
        "d102ClaimBoundariesBoxIncluded",
        "nextActionSelected",
        "privateCopyFreezeSelected",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("unexpected selected candidate")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["guardSummary"] != "no extra real-domain guard recorded":
        raise ValueError("unexpected guard summary")
    if summary["runtimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("unexpected runtime control")
    if summary["d102CopySectionCount"] != 5:
        raise ValueError("D102 section count drift")
    if summary["d102RequiredCaveatCount"] != 7 or summary["d102BlockedPhraseCount"] != 11:
        raise ValueError("D102 caveat/blocker count drift")
    if summary["selectedOptionId"] != "expm1_public_witness_copy_freeze_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D104 expm1 public-witness copy freeze packet":
        raise ValueError("unexpected next artifact")
    if summary["optionCount"] != 4:
        raise ValueError("expected four decision options")
    for key in [
        "copyFreezeStarted",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "claimTopologySurfaceCreated",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
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
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    allowed_true = {"next_action_selected", "private_copy_freeze_selected", "d102_copy_boundary_observed"}
    for key in allowed_true:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_public_witness_copy_review_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_selects_expm1_public_witness_copy_freeze_no_approval_no_public_surface",
        "source": f"python/results/eml_d103_public_witness_copy_review_next_selector/eml_d103_public_witness_copy_review_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d103_public_witness_copy_review_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "publicCopyApproved": payload["summary"]["publicCopyApproved"],
        "nextAction": "Run EML-D104 as a private expm1 public-witness copy freeze packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D103 Public-Witness Copy Review Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D103 selects the next private action after the D102 expm1 public-witness copy packet.",
        "",
        "## Summary",
        "",
        f"- selected option: `{payload['summary']['selectedOptionId']}`",
        f"- next artifact: `{payload['summary']['selectedNextArtifact']}`",
        f"- witness: `{payload['summary']['selectedWitnessName']}`",
        f"- copy freeze started: `{payload['summary']['copyFreezeStarted']}`",
        f"- human approval recorded: `{payload['summary']['humanApprovalRecorded']}`",
        f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
        "",
        "## Options",
        "",
        "| Option | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for option in payload["decisionOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | {option['priorityScore']} | {option['nextArtifact']} |"
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
    result_path = out_dir / f"eml_d103_public_witness_copy_review_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d103_public_witness_copy_review_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d103_public_witness_copy_review_next_selector.json"
    feed_path = command_feed_dir / f"eml_d103_public_witness_copy_review_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d103_public_witness_copy_review_next_selector")
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
    print("EML_D103_PUBLIC_WITNESS_COPY_REVIEW_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
