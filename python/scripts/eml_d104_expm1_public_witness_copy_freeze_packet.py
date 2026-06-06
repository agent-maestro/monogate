#!/usr/bin/env python3
"""EML-D104 expm1 public-witness copy freeze packet."""

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

from scripts import eml_d103_public_witness_copy_review_next_selector as d103  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_expm1_public_witness_copy_freeze_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D104_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_PACKET_PASS"

CLAIM_FLAGS = {
    "private_copy_freeze_started": True,
    "public_witness_copy_frozen": True,
    "d102_copy_boundary_preserved": True,
    "claim_boundaries_frozen": True,
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
    "EML-D104 freezes the private expm1 public-witness copy boundary; it does not approve, publish, or create public copy.",
    "D104 preserves the D102 private draft, exact checked statement, guard summary, claim-boundaries section, caveats, blocked phrases, and protected expm1 runtime-control boundary.",
    "D104 does not edit MachLib, typecheck Lean, start proof work, change runtime lowering, create public pages or docs, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime performance, compiler correctness, formal equivalence, public readiness, protected expm1 replacement, or broad EML advantage.",
]


def freeze_row(
    freeze_id: str,
    machlib_name: str,
    checked_statement: str,
    guard_summary: str,
    runtime_control: str,
    frozen_section_ids: list[str],
    frozen_caveats: list[str],
    frozen_blocked_phrases: list[str],
) -> dict[str, Any]:
    return {
        "freezeId": freeze_id,
        "machlibName": machlib_name,
        "checkedStatement": checked_statement,
        "guardSummary": guard_summary,
        "runtimeControl": runtime_control,
        "frozenSectionIds": frozen_section_ids,
        "frozenCaveats": frozen_caveats,
        "frozenBlockedPhrases": frozen_blocked_phrases,
        "freezeStatus": "private_public_witness_copy_boundary_frozen",
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def parked_option(option_id: str, lane: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "lane": lane,
        "status": status,
        "reason": reason,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d103.build_payload(atlas_gate_path)
    d103.validate_payload(selector)
    frozen_section_ids = [
        "original_eml_shaped_statement",
        "checked_lean_machlib_witness",
        "guards_domain_conditions",
        "plain_english_reading",
        "claim_boundaries",
    ]
    frozen_caveats = [
        "This frozen copy boundary is private-only.",
        "The exact checked statement is eml x (exp 1) = exp x - 1.",
        "The exact witness name is MachLib.Real.expm1_boundary_identity_witness.",
        "The recorded guard summary is: no extra real-domain guard recorded.",
        "Protected expm1 remains the runtime and numerical-stability control.",
        "Do not describe this as EML replacing expm1.",
        "Do not claim runtime performance, numerical-stability advantage, compiler correctness, formal equivalence, public readiness, or broad EML advantage.",
    ]
    frozen_blocked_phrases = [
        "EML replaces expm1",
        "protected expm1 replacement",
        "runtime advantage",
        "numerical stability advantage",
        "compiler correctness",
        "formal equivalence",
        "full EML semantics",
        "public ready",
        "theorem discovery",
        "all expm1 identities",
        "broad EML advantage",
    ]
    freeze_rows = [
        freeze_row(
            "expm1_public_witness_copy_boundary",
            selector["summary"]["selectedWitnessName"],
            selector["summary"]["checkedStatement"],
            selector["summary"]["guardSummary"],
            selector["summary"]["runtimeControl"],
            frozen_section_ids,
            frozen_caveats,
            frozen_blocked_phrases,
        )
    ]
    parked_options = [
        parked_option(
            "human_public_copy_gate",
            "public_copy_gate_lane",
            "parked_requires_explicit_human_approval",
            "D104 freezes the private copy boundary but records no human approval.",
        ),
        parked_option(
            "private_claim_topology_surface_mvp",
            "private_claim_topology_lane",
            "parked_after_copy_freeze",
            "A private topology surface can consume the frozen boundary later without claiming public readiness.",
        ),
        parked_option(
            "next_public_witness_candidate_selector",
            "private_public_witness_lane",
            "parked_after_copy_freeze",
            "A second candidate should be selected only through a later selector.",
        ),
    ]
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "selectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": selector["summary"]["sourceSelectedCandidateId"],
        "selectedFamily": selector["summary"]["selectedFamily"],
        "checkedStatement": selector["summary"]["checkedStatement"],
        "guardSummary": selector["summary"]["guardSummary"],
        "runtimeControl": selector["summary"]["runtimeControl"],
        "d102CopySectionCount": selector["summary"]["d102CopySectionCount"],
        "d102RequiredCaveatCount": selector["summary"]["d102RequiredCaveatCount"],
        "d102BlockedPhraseCount": selector["summary"]["d102BlockedPhraseCount"],
        "d102ClaimBoundariesBoxIncluded": selector["summary"]["d102ClaimBoundariesBoxIncluded"],
        "privateCopyFreezeStarted": True,
        "publicWitnessCopyFrozen": True,
        "d102CopyBoundaryPreserved": True,
        "claimBoundariesFrozen": True,
        "freezeRowCount": len(freeze_rows),
        "frozenSectionCount": len(frozen_section_ids),
        "frozenCaveatCount": len(frozen_caveats),
        "frozenBlockedPhraseCount": len(frozen_blocked_phrases),
        "parkedOptionCount": len(parked_options),
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
        "nextAction": "EML-D105 post-expm1 public-witness copy freeze next-action selector or private reviewer response intake.",
        "claimFlagsFrozenOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "private_copy_freeze_started",
                "public_witness_copy_frozen",
                "d102_copy_boundary_preserved",
                "claim_boundaries_frozen",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "private_copy_freeze_started",
                "public_witness_copy_frozen",
                "d102_copy_boundary_preserved",
                "claim_boundaries_frozen",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_expm1_public_witness_copy_freeze_packet_v0",
        "artifactId": "eml-d104-expm1-public-witness-copy-freeze-packet",
        "status": STATUS,
        "decision": "freeze_private_expm1_public_witness_copy_boundary_public_copy_unapproved",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "freezeRows": freeze_rows,
        "parkedOptions": parked_options,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d103-public-witness-copy-review-next-selector":
        raise ValueError("D104 must consume D103")
    if summary["selectedOptionId"] != "expm1_public_witness_copy_freeze_packet":
        raise ValueError("unexpected D103 selected option")
    if summary["selectedNextArtifact"] != "EML-D104 expm1 public-witness copy freeze packet":
        raise ValueError("unexpected D103 next artifact")
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
    if summary["d102CopySectionCount"] != 5 or summary["frozenSectionCount"] != 5:
        raise ValueError("copy section count drift")
    if summary["d102RequiredCaveatCount"] != 7 or summary["frozenCaveatCount"] != 7:
        raise ValueError("caveat count drift")
    if summary["d102BlockedPhraseCount"] != 11 or summary["frozenBlockedPhraseCount"] != 11:
        raise ValueError("blocked phrase count drift")
    for key in [
        "d102ClaimBoundariesBoxIncluded",
        "privateCopyFreezeStarted",
        "publicWitnessCopyFrozen",
        "d102CopyBoundaryPreserved",
        "claimBoundariesFrozen",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["freezeRowCount"] != 1:
        raise ValueError("expected one freeze row")
    if summary["parkedOptionCount"] != 3:
        raise ValueError("expected three parked options")
    for key in [
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
    if summary["claimFlagsFrozenOnly"] is not True:
        raise ValueError("claim flags must remain frozen-only")
    allowed_true = {
        "private_copy_freeze_started",
        "public_witness_copy_frozen",
        "d102_copy_boundary_preserved",
        "claim_boundaries_frozen",
    }
    for key in allowed_true:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(row["publicPromotionAllowed"] for row in payload["freezeRows"]):
        raise ValueError("freeze rows must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_expm1_public_witness_copy_freeze_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_freeze_of_expm1_public_witness_copy_boundary_no_approval_no_public_surface",
        "source": f"python/results/eml_d104_expm1_public_witness_copy_freeze_packet/eml_d104_expm1_public_witness_copy_freeze_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d104_expm1_public_witness_copy_freeze_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "publicWitnessCopyFrozen": payload["summary"]["publicWitnessCopyFrozen"],
        "publicCopyApproved": payload["summary"]["publicCopyApproved"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D104 Expm1 Public-Witness Copy Freeze Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D104 freezes the private expm1 public-witness copy boundary and keeps public approval blocked.",
        "",
        "## Summary",
        "",
        f"- witness: `{payload['summary']['selectedWitnessName']}`",
        f"- statement: `{payload['summary']['checkedStatement']}`",
        f"- guard summary: `{payload['summary']['guardSummary']}`",
        f"- runtime control: `{payload['summary']['runtimeControl']}`",
        f"- frozen sections: `{payload['summary']['frozenSectionCount']}`",
        f"- frozen caveats: `{payload['summary']['frozenCaveatCount']}`",
        f"- frozen blocked phrases: `{payload['summary']['frozenBlockedPhraseCount']}`",
        f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
        "",
        "## Non-Claims",
        "",
    ]
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
    result_path = out_dir / f"eml_d104_expm1_public_witness_copy_freeze_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d104_expm1_public_witness_copy_freeze_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d104_expm1_public_witness_copy_freeze_packet.json"
    feed_path = command_feed_dir / f"eml_d104_expm1_public_witness_copy_freeze_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d104_expm1_public_witness_copy_freeze_packet")
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
    print("EML_D104_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
