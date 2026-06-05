#!/usr/bin/env python3
"""EML-D96 log1p affine-scaled checked-witness copy review packet."""

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

from scripts import eml_d95_log1p_affine_scaled_surface_next_selector as d95  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_log1p_affine_scaled_checked_witness_copy_review_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D96_LOG1P_AFFINE_SCALED_CHECKED_WITNESS_COPY_REVIEW_PACKET_PASS"

CLAIM_FLAGS = {
    "copy_review_started": True,
    "private_copy_review_only": True,
    "checked_witness_copy_review_only": True,
    "duplicate_shifted_blocks_preserved": True,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
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
    "new_bounded_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "private_reviewer_response_intake_selected": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
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
    "EML-D96 is a private checked-witness copy review packet for the log1p affine-scaled coordinate; it does not approve or publish public copy.",
    "D96 reviews wording for one scoped guarded MachLib witness and keeps protected log and log1p as runtime controls.",
    "D96 preserves the D91/D92 duplicate shifted-coordinate blocks and does not reopen the checked log1p-shifted or log1m-shifted lanes as fresh work.",
    "D96 does not edit MachLib, typecheck Lean, start proof work, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, log/log1p replacement, formal equivalence, or broad EML superiority.",
]


def witness_copy_row(
    witness_id: str,
    machlib_name: str,
    safe_private_phrase: str,
    required_caveats: list[str],
    blocked_phrases: list[str],
    runtime_control: str,
) -> dict[str, Any]:
    return {
        "witnessId": witness_id,
        "machlibName": machlib_name,
        "safePrivatePhrase": safe_private_phrase,
        "requiredCaveats": required_caveats,
        "blockedPhrases": blocked_phrases,
        "runtimeControl": runtime_control,
        "copyStatus": "private_checked_witness_copy_reviewable",
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d95.build_payload(atlas_gate_path)
    d95.validate_payload(selector)
    row_caveats = [
        "Always describe this as one scoped guarded checked witness, not a log1p, affine-logarithm, or logarithm theory.",
        "Preserve the checked statement with the affine positive-domain guard: 0 < 1 + a * x.",
        "Say protected log and log1p remain the runtime controls.",
        "Keep D92 boundary controls visible: 1 + a * x <= 0, missing affine guard, duplicate shifted-coordinate reuse, and broad log1p-family statements remain blocked.",
        "Keep the D91/D92 duplicate shifted-coordinate blocks visible; the checked log1p-shifted and log1m-shifted lanes are not fresh work.",
        "Keep Advantage Lab and runtime-performance claims held for separate evidence.",
        "Keep public copy held for human review.",
    ]
    row_blocked_phrases = [
        "EML replaces log",
        "EML replaces log1p",
        "log replacement",
        "log1p replacement",
        "protected log replacement",
        "protected log1p replacement",
        "runtime advantage",
        "log1p affine theory",
        "logarithm theory",
        "unguarded affine logarithm identity",
        "broad log1p family",
        "public ready",
        "theorem discovery",
    ]
    row = witness_copy_row(
        "log1p_affine_scaled_boundary_coordinate",
        "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness",
        "A checked MachLib witness records the scoped guarded identity 0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x; protected log and log1p remain runtime controls.",
        row_caveats,
        row_blocked_phrases,
        "protected log and log1p remain runtime controls",
    )
    required_caveats = [
        "This checked-witness copy review is private-only.",
        "The checked statement is 0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x.",
        "The witness name is MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness.",
        "The affine positive-domain guard, 0 < 1 + a * x, must remain visible.",
        "Protected log and log1p remain the runtime controls.",
        "D92 negative controls for missing guard, invalid affine domain, duplicate shifted-coordinate reuse, and broad-family wording remain blocked.",
        "The D91/D92 duplicate shifted-coordinate blocks remain preserved.",
        "The witness is one scoped MachLib theorem name, not a broad log1p, affine-logarithm, or logarithm theory.",
        "Advantage Lab and runtime-performance claims require separate evidence.",
        "Public Atlas and public education promotion remain false.",
    ]
    blocked_global_phrases = [
        "theorem discovery",
        "log replacement",
        "log1p replacement",
        "runtime advantage",
        "log1p affine theory",
        "log1p theory",
        "logarithm theory",
        "unguarded affine logarithm identity",
        "broad log1p family",
        "public ready",
        "broad EML advantage",
        "compiler correctness",
        "formal equivalence",
        "full EML semantics",
    ]
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": selector["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["sourceSelectedFamily"],
        "checkedStatement": selector["summary"]["checkedStatement"],
        "machlibFile": selector["summary"]["machlibFile"],
        "guardCount": selector["summary"]["guardCount"],
        "sourceDerivedDomainObligationCount": selector["summary"]["sourceDerivedDomainObligationCount"],
        "sourceNegativeControlCount": selector["summary"]["sourceNegativeControlCount"],
        "sourceBlockerCount": selector["summary"]["sourceBlockerCount"],
        "sourceDuplicateShiftedBlocksPreserved": selector["summary"]["sourceDuplicateShiftedBlocksPreserved"],
        "duplicateShiftedBlocksPreserved": selector["summary"]["duplicateShiftedBlocksPreserved"],
        "d94SurfaceRowCount": selector["summary"]["d94SurfaceRowCount"],
        "guardBoundaryStatus": selector["summary"]["guardBoundaryStatus"],
        "runtimeGuardrailStatus": selector["summary"]["runtimeGuardrailStatus"],
        "publicAtlasStatus": selector["summary"]["publicAtlasStatus"],
        "copyReviewStarted": True,
        "privateCopyReviewOnly": True,
        "checkedWitnessCopyReviewOnly": True,
        "witnessRowCount": 1,
        "requiredCaveatCount": len(required_caveats),
        "blockedGlobalPhraseCount": len(blocked_global_phrases),
        "rowRequiredCaveatCount": len(row_caveats),
        "rowBlockedPhraseCount": len(row_blocked_phrases),
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "publicCopyApproved": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "protectedLogReplacementClaim": False,
        "protectedLog1pReplacementClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "runtimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "newBoundedBranchSelected": False,
        "boundedTrigFeasibilitySelected": False,
        "privateReviewerResponseIntakeSelected": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D97 choose log1p affine-scaled branch pause/freeze, next bounded branch, private reviewer response intake, or human-approved public copy gate.",
        "claimFlagsAllBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "copy_review_started",
                "private_copy_review_only",
                "checked_witness_copy_review_only",
                "duplicate_shifted_blocks_preserved",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "copy_review_started",
                "private_copy_review_only",
                "checked_witness_copy_review_only",
                "duplicate_shifted_blocks_preserved",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_log1p_affine_scaled_checked_witness_copy_review_packet_v0",
        "artifactId": "eml-d96-log1p-affine-scaled-checked-witness-copy-review-packet",
        "status": STATUS,
        "decision": "log1p_affine_scaled_checked_witness_copy_review_private_only_public_copy_held",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "witnessCopyRows": [row],
        "requiredCaveats": required_caveats,
        "blockedGlobalPhrases": blocked_global_phrases,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d95-log1p-affine-scaled-surface-next-selector":
        raise ValueError("D96 must consume D95")
    if summary["selectedOptionId"] != "log1p_affine_scaled_checked_witness_copy_review_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedWitnessName"] != "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "log1p_affine_scaled_boundary_coordinate":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "guarded_log1p_affine_scaled_coordinate":
        raise ValueError("unexpected family")
    if summary["checkedStatement"] != "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x":
        raise ValueError("unexpected checked statement")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    if summary["guardCount"] != 1:
        raise ValueError("log1p affine-scaled copy review should preserve one guard")
    if summary["sourceDerivedDomainObligationCount"] != 2:
        raise ValueError("derived domain obligation count drift")
    if summary["sourceNegativeControlCount"] != 5 or summary["sourceBlockerCount"] != 5:
        raise ValueError("negative control/blocker counts drift")
    if summary["sourceDuplicateShiftedBlocksPreserved"] is not True or summary["duplicateShiftedBlocksPreserved"] is not True:
        raise ValueError("duplicate shifted-coordinate block drift")
    if summary["d94SurfaceRowCount"] != 5:
        raise ValueError("D94 row count drift")
    if summary["guardBoundaryStatus"] != "affine_scaled_positive_domain_boundary_required":
        raise ValueError("guard boundary drift")
    if summary["runtimeGuardrailStatus"] != "protected_log_and_log1p_runtime_controls_required":
        raise ValueError("runtime guardrail drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    for key in ["copyReviewStarted", "privateCopyReviewOnly", "checkedWitnessCopyReviewOnly"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["witnessRowCount"] != 1:
        raise ValueError("expected one witness copy row")
    if summary["requiredCaveatCount"] != 10:
        raise ValueError("unexpected caveat count")
    if summary["blockedGlobalPhraseCount"] != 14:
        raise ValueError("unexpected blocked phrase count")
    if summary["rowRequiredCaveatCount"] != 7 or summary["rowBlockedPhraseCount"] != 13:
        raise ValueError("unexpected row copy boundary count")
    for key in [
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicCopyApproved",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedLogReplacementClaim",
        "protectedLog1pReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "newBoundedBranchSelected",
        "boundedTrigFeasibilitySelected",
        "privateReviewerResponseIntakeSelected",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "protected_log_and_log1p_remain_runtime_controls":
        raise ValueError("runtime lowering control drift")
    if summary["nextAction"] != (
        "EML-D97 choose log1p affine-scaled branch pause/freeze, next bounded branch, private reviewer response intake, or human-approved public copy gate."
    ):
        raise ValueError("unexpected next action")
    if summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    allowed_true = {
        "copy_review_started",
        "private_copy_review_only",
        "checked_witness_copy_review_only",
        "duplicate_shifted_blocks_preserved",
    }
    for key in allowed_true:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(row["publicPromotionAllowed"] for row in payload["witnessCopyRows"]):
        raise ValueError("copy row must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_log1p_affine_scaled_checked_witness_copy_review_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_log1p_affine_scaled_checked_witness_copy_review_public_copy_held",
        "source": f"python/results/eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet/eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "witnessRowCount": payload["summary"]["witnessRowCount"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D96 Log1p Affine-Scaled Checked-Witness Copy Review Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D96 reviews safe private wording for the checked log1p affine-scaled witness while holding all public copy.",
        "",
        "| Witness | Copy status | Runtime control |",
        "|---|---|---|",
    ]
    for row in payload["witnessCopyRows"]:
        lines.append(f"| `{row['witnessId']}` | `{row['copyStatus']}` | {row['runtimeControl']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- checked statement: `{payload['summary']['checkedStatement']}`",
            f"- guard count: `{payload['summary']['guardCount']}`",
            f"- duplicate shifted blocks preserved: `{payload['summary']['duplicateShiftedBlocksPreserved']}`",
            f"- required caveats: `{payload['summary']['requiredCaveatCount']}`",
            f"- blocked global phrases: `{payload['summary']['blockedGlobalPhraseCount']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
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
    result_path = out_dir / f"eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet.json"
    feed_path = command_feed_dir / f"eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet_feed_{STAMP}.json"
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet",
    )
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
    print("EML_D96_LOG1P_AFFINE_SCALED_CHECKED_WITNESS_COPY_REVIEW_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
