#!/usr/bin/env python3
"""EML-D102 expm1-boundary public-witness copy packet."""

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

from scripts import eml_d101_private_public_witness_candidate_selector as d101  # noqa: E402

DATE = "2026-06-05"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_expm1_boundary_public_witness_copy_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D102_EXPM1_BOUNDARY_PUBLIC_WITNESS_COPY_PACKET_PASS"

CLAIM_FLAGS = {
    "public_witness_copy_packet_created": True,
    "private_copy_review_only": True,
    "public_copy_drafted_for_review": True,
    "expm1_boundary_candidate_preserved": True,
    "claim_boundaries_box_included": True,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "public_page_created": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "claim_topology_surface_created": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
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
    "EML-D102 drafts a private review packet for one checked witness; it does not approve, publish, or create public copy.",
    "D102 preserves protected expm1 as the runtime and numerical-stability control; it does not claim EML replaces expm1.",
    "D102 does not edit MachLib, typecheck Lean, start proof work, change runtime lowering, add Advantage Lab cases, create SDK/compiler docs, create course material, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime performance, compiler correctness, formal equivalence, catalog completeness, public readiness, full EML semantics, or broad EML advantage.",
]

PUBLIC_DRAFT_MARKDOWN = """# One Checked MachLib Witness: expm1 Boundary

This private draft describes one narrow checked witness from MachLib. It is not a
public announcement, not a library overview, and not an approval to publish.

## Original EML-Shaped Statement

```text
eml x (exp 1) = exp x - 1
```

## Checked Lean / MachLib Witness

```text
MachLib.Real.expm1_boundary_identity_witness
```

Checked statement:

```text
eml x (exp 1) = exp x - 1
```

## Guards / Domain Conditions

```text
no extra real-domain guard recorded
```

## Plain-English Reading

This witness records that, inside this scoped MachLib statement, the EML-shaped
expression `eml x (exp 1)` matches the boundary identity `exp x - 1`.

The artifact is useful because it gives reviewers one exact theorem name, one
exact statement, and one exact runtime boundary to inspect. Protected `expm1`
remains the runtime and numerical-stability control.

## Claim Boundaries

What is being claimed:

- One named MachLib witness exists for the statement above.
- This packet preserves the exact checked statement and the recorded guard
  summary.
- The packet is suitable for private review as a candidate public-witness page.

What is not being claimed:

- No public copy is approved.
- No public page or Atlas row has been published.
- No EML advantage is claimed.
- No runtime performance claim is made.
- No compiler correctness claim is made.
- No formal equivalence claim is made.
- No full EML semantics claim is made.
- No claim is made that EML replaces protected `expm1`.
- No claim is made that this witness covers all expm1 identities.
- No public readiness claim is made.
"""


def build_copy_sections(selected: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "sectionId": "original_eml_shaped_statement",
            "title": "Original EML-Shaped Statement",
            "body": selected["checkedStatement"],
            "reviewStatus": "private_reviewable",
        },
        {
            "sectionId": "checked_lean_machlib_witness",
            "title": "Checked Lean / MachLib Witness",
            "body": selected["machlibName"],
            "reviewStatus": "private_reviewable",
        },
        {
            "sectionId": "guards_domain_conditions",
            "title": "Guards / Domain Conditions",
            "body": selected["guardSummary"],
            "reviewStatus": "private_reviewable",
        },
        {
            "sectionId": "plain_english_reading",
            "title": "Plain-English Reading",
            "body": (
                "This witness records that, inside this scoped MachLib statement, "
                "the EML-shaped expression eml x (exp 1) matches exp x - 1 while "
                "protected expm1 remains the runtime and numerical-stability control."
            ),
            "reviewStatus": "private_reviewable",
        },
        {
            "sectionId": "claim_boundaries",
            "title": "Claim Boundaries",
            "body": "one checked witness; no approval, publication, runtime advantage, compiler correctness, or expm1 replacement claim",
            "reviewStatus": "private_reviewable",
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d101.build_payload(atlas_gate_path)
    d101.validate_payload(selector)
    selected = selector["selectedCandidate"]
    sections = build_copy_sections(selected)
    required_caveats = [
        "This is a private review draft, not approved public copy.",
        "The exact checked statement is eml x (exp 1) = exp x - 1.",
        "The exact witness name is MachLib.Real.expm1_boundary_identity_witness.",
        "The recorded guard summary is: no extra real-domain guard recorded.",
        "Protected expm1 remains the runtime and numerical-stability control.",
        "Do not describe this as EML replacing expm1.",
        "Do not claim runtime performance, numerical-stability advantage, compiler correctness, formal equivalence, public readiness, or broad EML advantage.",
    ]
    blocked_phrases = [
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
    summary = {
        "sourceSelector": selector["artifactId"],
        "sourceSelectedOptionId": selector["summary"]["selectedOptionId"],
        "sourceSelectedCandidateId": selector["summary"]["selectedCandidateId"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "selectedFamily": selector["summary"]["selectedFamily"],
        "checkedStatement": selector["summary"]["selectedCheckedStatement"],
        "guardSummary": selector["summary"]["selectedGuardSummary"],
        "runtimeControl": selector["summary"]["selectedRuntimeControl"],
        "sourceNextArtifact": selector["summary"]["selectedNextArtifact"],
        "publicWitnessCopyPacketCreated": True,
        "privateCopyReviewOnly": True,
        "publicCopyDraftedForReview": True,
        "copySectionCount": len(sections),
        "requiredCaveatCount": len(required_caveats),
        "blockedPhraseCount": len(blocked_phrases),
        "claimBoundariesBoxIncluded": True,
        "publicCopyApproved": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "publicPageCreated": False,
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "newIdentityCandidateSelected": False,
        "nextBoundedIdentityBranchSelected": False,
        "boundedTrigFeasibilitySelected": False,
        "claimTopologySurfaceCreated": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
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
        "nextAction": "EML-D103 private public-witness copy review next-action selector or private reviewer response intake.",
        "claimFlagsCopyDraftOnly": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "public_witness_copy_packet_created",
                "private_copy_review_only",
                "public_copy_drafted_for_review",
                "expm1_boundary_candidate_preserved",
                "claim_boundaries_box_included",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "public_witness_copy_packet_created",
                "private_copy_review_only",
                "public_copy_drafted_for_review",
                "expm1_boundary_candidate_preserved",
                "claim_boundaries_box_included",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_expm1_boundary_public_witness_copy_packet_v0",
        "artifactId": "eml-d102-expm1-boundary-public-witness-copy-packet",
        "status": STATUS,
        "decision": "draft_private_expm1_boundary_public_witness_copy_packet_public_copy_unapproved",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "copySections": sections,
        "requiredCaveats": required_caveats,
        "blockedPhrases": blocked_phrases,
        "privateDraftMarkdown": PUBLIC_DRAFT_MARKDOWN,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d101-private-public-witness-candidate-selector":
        raise ValueError("D102 must consume D101")
    if summary["sourceSelectedOptionId"] != "expm1_boundary_identity_public_witness_candidate":
        raise ValueError("unexpected D101 selected option")
    if summary["sourceSelectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("unexpected selected candidate")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["guardSummary"] != "no extra real-domain guard recorded":
        raise ValueError("unexpected guard summary")
    if summary["runtimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("unexpected runtime control")
    if summary["sourceNextArtifact"] != "EML-D102 expm1 boundary public-witness copy packet":
        raise ValueError("unexpected D101 next artifact")
    for key in [
        "publicWitnessCopyPacketCreated",
        "privateCopyReviewOnly",
        "publicCopyDraftedForReview",
        "claimBoundariesBoxIncluded",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["copySectionCount"] != 5:
        raise ValueError("expected five copy sections")
    if summary["requiredCaveatCount"] != 7:
        raise ValueError("unexpected caveat count")
    if summary["blockedPhraseCount"] != 11:
        raise ValueError("unexpected blocked phrase count")
    if "## Claim Boundaries" not in payload["privateDraftMarkdown"]:
        raise ValueError("claim boundaries section missing")
    if "No EML advantage is claimed." not in payload["privateDraftMarkdown"]:
        raise ValueError("non-claim missing from draft")
    for key in [
        "publicCopyApproved",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "newIdentityCandidateSelected",
        "nextBoundedIdentityBranchSelected",
        "boundedTrigFeasibilitySelected",
        "claimTopologySurfaceCreated",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
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
    if summary["claimFlagsCopyDraftOnly"] is not True:
        raise ValueError("claim flags must remain copy-draft-only")
    allowed_true = {
        "public_witness_copy_packet_created",
        "private_copy_review_only",
        "public_copy_drafted_for_review",
        "expm1_boundary_candidate_preserved",
        "claim_boundaries_box_included",
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
        "artifactType": "eml_expm1_boundary_public_witness_copy_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_expm1_boundary_public_witness_copy_packet_drafted_for_review_no_approval_no_public_surface",
        "source": f"python/results/eml_d102_expm1_boundary_public_witness_copy_packet/eml_d102_expm1_boundary_public_witness_copy_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d102_expm1_boundary_public_witness_copy_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "publicCopyDraftedForReview": payload["summary"]["publicCopyDraftedForReview"],
        "publicCopyApproved": payload["summary"]["publicCopyApproved"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D102 Expm1 Boundary Public-Witness Copy Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D102 drafts private review copy for one checked expm1-boundary witness and keeps publication blocked.",
        "",
        "## Summary",
        "",
        f"- witness: `{payload['summary']['selectedWitnessName']}`",
        f"- statement: `{payload['summary']['checkedStatement']}`",
        f"- guard summary: `{payload['summary']['guardSummary']}`",
        f"- runtime control: `{payload['summary']['runtimeControl']}`",
        f"- public copy drafted for review: `{payload['summary']['publicCopyDraftedForReview']}`",
        f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
        f"- public page created: `{payload['summary']['publicPageCreated']}`",
        "",
        "## Private Draft Markdown",
        "",
        payload["privateDraftMarkdown"],
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
    result_path = out_dir / f"eml_d102_expm1_boundary_public_witness_copy_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d102_expm1_boundary_public_witness_copy_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d102_expm1_boundary_public_witness_copy_packet.json"
    feed_path = command_feed_dir / f"eml_d102_expm1_boundary_public_witness_copy_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d102_expm1_boundary_public_witness_copy_packet")
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
    print("EML_D102_EXPM1_BOUNDARY_PUBLIC_WITNESS_COPY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
