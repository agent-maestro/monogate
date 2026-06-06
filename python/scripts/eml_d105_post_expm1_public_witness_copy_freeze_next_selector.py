#!/usr/bin/env python3
"""EML-D105 post expm1 public-witness copy freeze next-action selector."""

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

from scripts import eml_d104_expm1_public_witness_copy_freeze_packet as d104  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_post_expm1_public_witness_copy_freeze_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D105_POST_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_NEXT_SELECTOR_PASS"

CLAIM_FLAGS = {
    "next_action_selected": True,
    "private_claim_topology_surface_selected": True,
    "d104_copy_boundary_observed": True,
    "claim_topology_surface_created": False,
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
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "next_public_witness_candidate_selected": False,
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
    "renderer_correctness_claim": False,
    "visualization_quality_claim": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D105 selects the next private action after D104; it does not create the Claim Topology Surface.",
    "D105 chooses a private reviewer-visibility lane because the first public-witness copy boundary is frozen and D research should consolidate rather than expand indefinitely.",
    "D105 does not approve public copy, publish a public page, create renderer artifacts, claim renderer correctness or visualization quality, edit MachLib, typecheck Lean, start proof work, change runtime lowering, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime performance, compiler correctness, formal equivalence, public readiness, protected expm1 replacement, catalog completeness, or broad EML advantage.",
]


def selector_option(
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
    freeze = d104.build_payload(atlas_gate_path)
    d104.validate_payload(freeze)
    options = [
        selector_option(
            "private_claim_topology_surface_seed",
            "private_claim_topology_lane",
            "selected_next",
            89,
            "EML-D106 private Claim Topology Surface seed packet",
            [
                "D104 froze the first public-witness copy boundary, so reviewer tooling can now show it as a stable private node.",
                "A private Claim Topology seed can make accepted fixtures, blocked claims, dependencies, and next reviewer actions visible without public UI claims.",
                "This consolidates the D100-D104 public-witness lane instead of expanding the bounded witness catalog.",
            ],
            [
                "must remain private",
                "must not claim renderer correctness or visualization quality",
                "must distinguish frozen private copy from public approval",
            ],
        ),
        selector_option(
            "human_public_copy_gate",
            "public_copy_gate_lane",
            "candidate_later_requires_explicit_human_approval",
            67,
            "Future human-approved expm1 public-witness copy gate",
            [
                "D104 froze the private copy boundary, but no human approval has been recorded.",
                "A public gate remains necessary before any public page or Atlas promotion.",
            ],
            [
                "requires explicit human approval",
                "requires reviewer decision record",
                "must preserve D104 frozen caveats and blocked phrases",
            ],
        ),
        selector_option(
            "sdk_compiler_guard_note_excerpt",
            "private_sdk_compiler_docs_lane",
            "candidate_later",
            61,
            "Future SDK/compiler guard-note excerpt packet",
            [
                "The frozen witness copy can inform guard documentation later.",
                "Docs should wait until topology/reviewer visibility clarifies claim boundaries.",
            ],
            [
                "must not claim compiler correctness",
                "must not claim runtime lowering",
                "must not imply public readiness",
            ],
        ),
        selector_option(
            "next_public_witness_candidate_selector",
            "private_public_witness_lane",
            "candidate_later_after_topology_seed",
            48,
            "Future next public-witness candidate selector",
            [
                "A second candidate may be useful later.",
                "Selecting another witness now would expand the lane before reviewer topology exists.",
            ],
            [
                "requires D106 or equivalent private topology seed",
                "must not count selector-only packets as final artifacts",
                "must avoid broad EML advantage language",
            ],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceFreezePacket": freeze["artifactId"],
        "selectedWitnessName": freeze["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": freeze["summary"]["sourceSelectedCandidateId"],
        "selectedFamily": freeze["summary"]["selectedFamily"],
        "checkedStatement": freeze["summary"]["checkedStatement"],
        "guardSummary": freeze["summary"]["guardSummary"],
        "runtimeControl": freeze["summary"]["runtimeControl"],
        "d104PrivateCopyFreezeStarted": freeze["summary"]["privateCopyFreezeStarted"],
        "d104PublicWitnessCopyFrozen": freeze["summary"]["publicWitnessCopyFrozen"],
        "d104CopyBoundaryPreserved": freeze["summary"]["d102CopyBoundaryPreserved"],
        "d104ClaimBoundariesFrozen": freeze["summary"]["claimBoundariesFrozen"],
        "d104FreezeRowCount": freeze["summary"]["freezeRowCount"],
        "d104FrozenSectionCount": freeze["summary"]["frozenSectionCount"],
        "d104FrozenCaveatCount": freeze["summary"]["frozenCaveatCount"],
        "d104FrozenBlockedPhraseCount": freeze["summary"]["frozenBlockedPhraseCount"],
        "optionCount": len(options),
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "nextActionSelected": True,
        "privateClaimTopologySurfaceSelected": True,
        "claimTopologySurfaceCreated": False,
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
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "newIdentityCandidateSelected": False,
        "nextBoundedIdentityBranchSelected": False,
        "nextPublicWitnessCandidateSelected": False,
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
        "rendererCorrectnessClaim": False,
        "visualizationQualityClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsSelectorOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "next_action_selected",
                "private_claim_topology_surface_selected",
                "d104_copy_boundary_observed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "next_action_selected",
                "private_claim_topology_surface_selected",
                "d104_copy_boundary_observed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_post_expm1_public_witness_copy_freeze_next_selector_v0",
        "artifactId": "eml-d105-post-expm1-public-witness-copy-freeze-next-selector",
        "status": STATUS,
        "decision": "select_private_claim_topology_surface_seed_after_public_witness_copy_freeze",
        "date": DATE,
        "sourceFreezePacket": freeze["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "selectorOptions": options,
        "selectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceFreezePacket"] != "eml-d104-expm1-public-witness-copy-freeze-packet":
        raise ValueError("D105 must consume D104")
    for key in [
        "d104PrivateCopyFreezeStarted",
        "d104PublicWitnessCopyFrozen",
        "d104CopyBoundaryPreserved",
        "d104ClaimBoundariesFrozen",
        "nextActionSelected",
        "privateClaimTopologySurfaceSelected",
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
    if summary["d104FreezeRowCount"] != 1:
        raise ValueError("freeze row count drift")
    if summary["d104FrozenSectionCount"] != 5:
        raise ValueError("frozen section count drift")
    if summary["d104FrozenCaveatCount"] != 7 or summary["d104FrozenBlockedPhraseCount"] != 11:
        raise ValueError("frozen caveat/blocker count drift")
    if summary["optionCount"] != 4:
        raise ValueError("expected four selector options")
    if summary["selectedOptionId"] != "private_claim_topology_surface_seed":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D106 private Claim Topology Surface seed packet":
        raise ValueError("unexpected next artifact")
    for key in [
        "claimTopologySurfaceCreated",
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
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "nextPublicWitnessCandidateSelected",
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
        "rendererCorrectnessClaim",
        "visualizationQualityClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsSelectorOnly"] is not True:
        raise ValueError("claim flags must remain selector-only")
    allowed_true = {
        "next_action_selected",
        "private_claim_topology_surface_selected",
        "d104_copy_boundary_observed",
    }
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
        "artifactType": "eml_post_expm1_public_witness_copy_freeze_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_selects_claim_topology_seed_after_expm1_copy_freeze_no_public_approval_no_renderer_claim",
        "source": f"python/results/eml_d105_post_expm1_public_witness_copy_freeze_next_selector/eml_d105_post_expm1_public_witness_copy_freeze_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d105_post_expm1_public_witness_copy_freeze_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "publicCopyApproved": payload["summary"]["publicCopyApproved"],
        "claimTopologySurfaceCreated": payload["summary"]["claimTopologySurfaceCreated"],
        "nextAction": "Run EML-D106 as a private Claim Topology Surface seed packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D105 Post Expm1 Public-Witness Copy Freeze Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D105 selects the next private action after the D104 expm1 public-witness copy freeze.",
        "",
        "## Summary",
        "",
        f"- selected option: `{payload['summary']['selectedOptionId']}`",
        f"- next artifact: `{payload['summary']['selectedNextArtifact']}`",
        f"- witness: `{payload['summary']['selectedWitnessName']}`",
        f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
        f"- topology surface created: `{payload['summary']['claimTopologySurfaceCreated']}`",
        "",
        "## Options",
        "",
        "| Option | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for option in payload["selectorOptions"]:
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
    result_path = out_dir / f"eml_d105_post_expm1_public_witness_copy_freeze_next_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d105_post_expm1_public_witness_copy_freeze_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d105_post_expm1_public_witness_copy_freeze_next_selector.json"
    feed_path = command_feed_dir / f"eml_d105_post_expm1_public_witness_copy_freeze_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d105_post_expm1_public_witness_copy_freeze_next_selector")
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
    print("EML_D105_POST_EXPM1_PUBLIC_WITNESS_COPY_FREEZE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
