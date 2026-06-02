#!/usr/bin/env python3
"""EML-D60 expm1-boundary checked-witness copy review packet."""

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

from scripts import eml_d59_expm1_boundary_surface_next_selector as d59  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_expm1_boundary_checked_witness_copy_review_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D60_EXPM1_BOUNDARY_CHECKED_WITNESS_COPY_REVIEW_PACKET_PASS"

CLAIM_FLAGS = {
    "copy_review_started": True,
    "private_copy_review_only": True,
    "checked_witness_copy_review_only": True,
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
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
    "new_bounded_branch_selected": False,
    "bounded_trig_feasibility_selected": False,
    "human_public_copy_gate_selected": False,
    "human_approval_recorded": False,
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
    "EML-D60 is a private checked-witness copy review packet for the expm1-boundary identity; it does not approve or publish public copy.",
    "D60 reviews wording for one scoped MachLib witness and keeps protected expm1 as the runtime and numerical-stability control.",
    "D60 does not edit MachLib, typecheck Lean, start proof work, add Advantage Lab cases, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime advantage, protected expm1 replacement, or broad EML superiority.",
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
    selector = d59.build_payload(atlas_gate_path)
    d59.validate_payload(selector)
    row = witness_copy_row(
        "expm1_boundary_identity",
        "MachLib.Real.expm1_boundary_identity_witness",
        "A checked MachLib witness records the scoped identity eml x (exp 1) = exp x - 1; protected expm1 remains the runtime and numerical-stability control.",
        [
            "Always describe this as one scoped checked witness, not an expm1 replacement.",
            "Preserve the checked statement eml x (exp 1) = exp x - 1.",
            "Say protected expm1 remains the runtime and numerical-stability control.",
            "Distinguish this from MachLib.Real.atlas_exp_from_eml_witness, which records eml x 1 = exp x.",
            "Keep Advantage Lab and runtime-performance claims held for separate evidence.",
            "Keep public copy held for human review.",
        ],
        [
            "EML replaces expm1",
            "protected expm1 replacement",
            "log/exp replacement",
            "runtime advantage",
            "numerical stability advantage",
            "all expm1 identities",
            "duplicate exp branch witness",
            "public ready",
            "theorem discovery",
            "Advantage Lab proof",
        ],
        "protected expm1 remains runtime control",
    )
    required_caveats = [
        "This checked-witness copy review is private-only.",
        "The checked statement is eml x (exp 1) = exp x - 1.",
        "The witness name is MachLib.Real.expm1_boundary_identity_witness.",
        "Protected expm1 remains the runtime and numerical-stability control.",
        "The witness is non-duplicate with the existing eml x 1 = exp x branch.",
        "The witness is one scoped MachLib theorem name, not a broad expm1 theory.",
        "Advantage Lab and runtime-performance claims require separate evidence.",
        "Public Atlas and public education promotion remain false.",
    ]
    blocked_global_phrases = [
        "theorem discovery",
        "protected expm1 replacement",
        "runtime advantage",
        "numerical stability advantage",
        "public ready",
        "broad EML advantage",
        "compiler correctness",
        "formal equivalence",
        "full EML semantics",
        "all expm1 identities",
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
        "d58SurfaceRowCount": selector["summary"]["d58SurfaceRowCount"],
        "runtimeGuardrailStatus": selector["summary"]["runtimeGuardrailStatus"],
        "publicAtlasStatus": selector["summary"]["publicAtlasStatus"],
        "copyReviewStarted": True,
        "privateCopyReviewOnly": True,
        "checkedWitnessCopyReviewOnly": True,
        "witnessRowCount": 1,
        "requiredCaveatCount": len(required_caveats),
        "blockedGlobalPhraseCount": len(blocked_global_phrases),
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "publicCopyApproved": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
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
        "humanPublicCopyGateSelected": False,
        "humanApprovalRecorded": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D61 choose expm1-boundary pause/freeze, next bounded branch, or human-approved public copy gate.",
        "claimFlagsAllBounded": all(
            CLAIM_FLAGS[key] is True
            for key in ["copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_expm1_boundary_checked_witness_copy_review_packet_v0",
        "artifactId": "eml-d60-expm1-boundary-checked-witness-copy-review-packet",
        "status": STATUS,
        "decision": "expm1_boundary_checked_witness_copy_review_private_only_public_copy_held",
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
    if payload["sourceSelector"] != "eml-d59-expm1-boundary-surface-next-selector":
        raise ValueError("D60 must consume D59")
    if summary["selectedOptionId"] != "expm1_boundary_checked_witness_copy_review_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "expm1_boundary_identity":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "protected_runtime_boundary_identity":
        raise ValueError("unexpected family")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["machlibFile"] != "foundations/MachLib/EMLAtlasWitness.lean":
        raise ValueError("unexpected MachLib file")
    if summary["guardCount"] != 0:
        raise ValueError("expm1 copy review should not add guards")
    if summary["d58SurfaceRowCount"] != 5:
        raise ValueError("D58 row count drift")
    if summary["runtimeGuardrailStatus"] != "protected_expm1_runtime_control_required":
        raise ValueError("runtime guardrail drift")
    if summary["publicAtlasStatus"] != "held_private":
        raise ValueError("public hold drift")
    for key in ["copyReviewStarted", "privateCopyReviewOnly", "checkedWitnessCopyReviewOnly"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["witnessRowCount"] != 1:
        raise ValueError("expected one witness copy row")
    if summary["requiredCaveatCount"] != 8:
        raise ValueError("unexpected caveat count")
    if summary["blockedGlobalPhraseCount"] != 10:
        raise ValueError("unexpected blocked phrase count")
    for key in [
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "publicCopyApproved",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "protectedExpm1ReplacementClaim",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "newBoundedBranchSelected",
        "boundedTrigFeasibilitySelected",
        "humanPublicCopyGateSelected",
        "humanApprovalRecorded",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["nextAction"] != "EML-D61 choose expm1-boundary pause/freeze, next bounded branch, or human-approved public copy gate.":
        raise ValueError("unexpected next action")
    if summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in ["copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"} and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(row["publicPromotionAllowed"] for row in payload["witnessCopyRows"]):
        raise ValueError("copy row must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_expm1_boundary_checked_witness_copy_review_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_expm1_boundary_checked_witness_copy_review_public_copy_held",
        "source": f"python/results/eml_d60_expm1_boundary_checked_witness_copy_review_packet/eml_d60_expm1_boundary_checked_witness_copy_review_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d60_expm1_boundary_checked_witness_copy_review_packet_feed",
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
        "# EML-D60 Expm1 Boundary Checked-Witness Copy Review Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D60 reviews safe private wording for the checked expm1-boundary witness while holding all public copy.",
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
            f"- checked witness: `{payload['summary']['selectedWitnessName']}`",
            f"- private copy review only: `{payload['summary']['privateCopyReviewOnly']}`",
            f"- checked witness copy review only: `{payload['summary']['checkedWitnessCopyReviewOnly']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- runtime lowering changed: `{payload['summary']['runtimeLoweringChanged']}`",
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
    result_path = out_dir / f"eml_d60_expm1_boundary_checked_witness_copy_review_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d60_expm1_boundary_checked_witness_copy_review_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d60_expm1_boundary_checked_witness_copy_review_packet.json"
    feed_path = command_feed_dir / f"eml_d60_expm1_boundary_checked_witness_copy_review_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d60_expm1_boundary_checked_witness_copy_review_packet")
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
    print("EML_D60_EXPM1_BOUNDARY_CHECKED_WITNESS_COPY_REVIEW_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
