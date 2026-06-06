#!/usr/bin/env python3
"""EML-D109 private reviewer response availability guard."""

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

from scripts import eml_d108_post_static_topology_summary_next_selector as d108  # noqa: E402

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_private_reviewer_response_availability_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D109_PRIVATE_REVIEWER_RESPONSE_AVAILABILITY_GUARD_PASS"

TRUE_CLAIM_FLAGS = {
    "reviewer_response_availability_checked",
    "d108_selector_consumed",
    "no_response_hold_recorded",
    "d110_blocked_until_response_exists",
}

CLAIM_FLAGS = {
    "reviewer_response_availability_checked": True,
    "d108_selector_consumed": True,
    "no_response_hold_recorded": True,
    "d110_blocked_until_response_exists": True,
    "reviewer_response_supplied": False,
    "reviewer_response_consumed": False,
    "reviewer_decision_recorded": False,
    "reviewer_approval_recorded": False,
    "reviewer_rejection_recorded": False,
    "reviewer_hold_recorded": False,
    "private_summary_implementation_selected": False,
    "implementation_approved": False,
    "claim_topology_surface_created": False,
    "interactive_renderer_implemented": False,
    "renderer_implemented": False,
    "renderer_executed": False,
    "visualization_rendered": False,
    "visualization_quality_claim": False,
    "renderer_correctness_claim": False,
    "renderer_soundness_proved": False,
    "public_surface_updated": False,
    "public_page_created": False,
    "public_copy_approved": False,
    "public_ready": False,
    "human_approval_recorded": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "new_identity_candidate_selected": False,
    "next_bounded_identity_branch_selected": False,
    "next_public_witness_candidate_selected": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "runtime_performance_claim": False,
    "protected_expm1_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
    "theorem_discovery_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "catalog_completeness_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
}

NON_CLAIMS = [
    "EML-D109 records reviewer-response availability only; it does not consume or invent a reviewer response.",
    "D109 treats the absence of supplied reviewer-response content as a hold, not approval, rejection, or implementation permission.",
    "D109 does not implement, render, execute, or publish a Claim Topology surface; it does not approve public copy, edit MachLib, typecheck Lean, change runtime lowering, consume laptop artifacts, touch laptop-owned repos, or claim renderer correctness, visualization quality, public readiness, compiler correctness, formal equivalence, protected expm1 replacement, theorem discovery, or broad EML advantage.",
]


def response_availability_rows() -> list[dict[str, Any]]:
    return [
        {
            "checkId": "response_text_supplied",
            "status": "missing",
            "requiredFor": "reviewer_response_consumed",
            "holdReason": "No private reviewer-response text or artifact was supplied to this phase.",
        },
        {
            "checkId": "response_source_artifact_supplied",
            "status": "missing",
            "requiredFor": "reviewer_decision_recorded",
            "holdReason": "No source artifact path, pasted response, or reviewer note id was supplied.",
        },
        {
            "checkId": "response_decision_explicit",
            "status": "unavailable",
            "requiredFor": "approval_or_rejection_record",
            "holdReason": "No response exists from which to classify approval, rejection, hold, or revision request.",
        },
    ]


def hold_actions() -> list[dict[str, Any]]:
    return [
        {
            "actionId": "wait_for_actual_private_reviewer_response",
            "status": "selected_hold",
            "nextArtifact": "EML-D110 private reviewer response intake packet only after response content exists",
        },
        {
            "actionId": "private_summary_implementation_packet",
            "status": "blocked_requires_explicit_approval",
            "nextArtifact": "Future separately approved private summary implementation packet",
        },
        {
            "actionId": "public_copy_gate",
            "status": "blocked_requires_explicit_human_approval",
            "nextArtifact": "Future human-approved public copy gate",
        },
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d108.build_payload(atlas_gate_path)
    d108.validate_payload(selector)
    checks = response_availability_rows()
    actions = hold_actions()
    d108_summary = selector["summary"]
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedWitnessName": d108_summary["selectedWitnessName"],
        "checkedStatement": d108_summary["checkedStatement"],
        "guardSummary": d108_summary["guardSummary"],
        "runtimeControl": d108_summary["runtimeControl"],
        "d108SelectedOptionId": d108_summary["selectedOptionId"],
        "d108SelectedNextArtifact": d108_summary["selectedNextArtifact"],
        "availabilityCheckCount": len(checks),
        "missingResponseCheckCount": sum(1 for item in checks if item["status"] == "missing"),
        "holdActionCount": len(actions),
        "reviewerResponseAvailabilityChecked": True,
        "d108SelectorConsumed": True,
        "noResponseHoldRecorded": True,
        "d110BlockedUntilResponseExists": True,
        "reviewerResponseSupplied": False,
        "reviewerResponseConsumed": False,
        "reviewerDecisionRecorded": False,
        "reviewerApprovalRecorded": False,
        "reviewerRejectionRecorded": False,
        "reviewerHoldRecorded": False,
        "privateSummaryImplementationSelected": False,
        "implementationApproved": False,
        "claimTopologySurfaceCreated": False,
        "interactiveRendererImplemented": False,
        "rendererImplemented": False,
        "rendererExecuted": False,
        "visualizationRendered": False,
        "visualizationQualityClaim": False,
        "rendererCorrectnessClaim": False,
        "rendererSoundnessProved": False,
        "publicSurfaceUpdated": False,
        "publicPageCreated": False,
        "publicCopyApproved": False,
        "publicReady": False,
        "humanApprovalRecorded": False,
        "sdkCompilerDocsCreated": False,
        "courseMaterialCreated": False,
        "newIdentityCandidateSelected": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "runtimeLoweringChanged": False,
        "runtimePerformanceClaim": False,
        "protectedExpm1ReplacementClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "fullEmlSemanticsClaim": False,
        "catalogCompletenessClaim": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "claimFlagsBounded": all(CLAIM_FLAGS[key] is True for key in TRUE_CLAIM_FLAGS)
        and all(value is False for key, value in CLAIM_FLAGS.items() if key not in TRUE_CLAIM_FLAGS),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "guardType": "eml_private_reviewer_response_availability_guard_v0",
        "artifactId": "eml-d109-private-reviewer-response-availability-guard",
        "status": STATUS,
        "decision": "record_no_response_hold_after_d108_no_reviewer_response_consumed",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "responseAvailabilityChecks": checks,
        "holdActions": actions,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d108-post-static-topology-summary-next-selector":
        raise ValueError("D109 must consume D108")
    if summary["d108SelectedOptionId"] != "private_reviewer_response_intake":
        raise ValueError("D108 selected option drift")
    if summary["d108SelectedNextArtifact"] != "EML-D109 private reviewer response intake packet":
        raise ValueError("D108 next artifact drift")
    if summary["selectedWitnessName"] != "MachLib.Real.expm1_boundary_identity_witness":
        raise ValueError("unexpected witness")
    if summary["checkedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("unexpected checked statement")
    if summary["guardSummary"] != "no extra real-domain guard recorded":
        raise ValueError("unexpected guard summary")
    if summary["runtimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("unexpected runtime control")
    if summary["availabilityCheckCount"] != 3 or summary["missingResponseCheckCount"] != 2:
        raise ValueError("availability check drift")
    if summary["holdActionCount"] != 3:
        raise ValueError("hold action drift")
    for key in [
        "reviewerResponseAvailabilityChecked",
        "d108SelectorConsumed",
        "noResponseHoldRecorded",
        "d110BlockedUntilResponseExists",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "reviewerResponseSupplied",
        "reviewerResponseConsumed",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "reviewerHoldRecorded",
        "privateSummaryImplementationSelected",
        "implementationApproved",
        "claimTopologySurfaceCreated",
        "interactiveRendererImplemented",
        "rendererImplemented",
        "rendererExecuted",
        "visualizationRendered",
        "visualizationQualityClaim",
        "rendererCorrectnessClaim",
        "rendererSoundnessProved",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "publicCopyApproved",
        "publicReady",
        "humanApprovalRecorded",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "newIdentityCandidateSelected",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "runtimeLoweringChanged",
        "runtimePerformanceClaim",
        "protectedExpm1ReplacementClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "fullEmlSemanticsClaim",
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags are not bounded")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_private_reviewer_response_availability_guard",
        "validationStatus": "pass",
        "semanticStrength": "private_reviewer_response_availability_guard_no_response_consumed_no_public_update",
        "source": f"python/results/eml_d109_private_reviewer_response_availability_guard/eml_d109_private_reviewer_response_availability_guard_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d109_private_reviewer_response_availability_guard_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceSelector": payload["sourceSelector"],
        "reviewerResponseSupplied": payload["summary"]["reviewerResponseSupplied"],
        "reviewerResponseConsumed": payload["summary"]["reviewerResponseConsumed"],
        "d110BlockedUntilResponseExists": payload["summary"]["d110BlockedUntilResponseExists"],
        "rendererImplemented": payload["summary"]["rendererImplemented"],
        "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
        "nextAction": "Hold until an actual private reviewer response exists; then run the real response intake packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D109 Private Reviewer Response Availability Guard",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D109 records that no private reviewer response was supplied. It is a hold guard, not a response intake.",
        "",
        "## Summary",
        "",
        f"- source selector: `{payload['sourceSelector']}`",
        f"- reviewer response supplied: `{payload['summary']['reviewerResponseSupplied']}`",
        f"- reviewer response consumed: `{payload['summary']['reviewerResponseConsumed']}`",
        f"- reviewer decision recorded: `{payload['summary']['reviewerDecisionRecorded']}`",
        f"- D110 blocked until response exists: `{payload['summary']['d110BlockedUntilResponseExists']}`",
        f"- renderer implemented: `{payload['summary']['rendererImplemented']}`",
        f"- public surface updated: `{payload['summary']['publicSurfaceUpdated']}`",
        "",
        "## Availability Checks",
        "",
        "| Check | Status | Required for |",
        "|---|---|---|",
    ]
    for check in payload["responseAvailabilityChecks"]:
        lines.append(f"| `{check['checkId']}` | `{check['status']}` | `{check['requiredFor']}` |")
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
    result_path = out_dir / f"eml_d109_private_reviewer_response_availability_guard_{STAMP}.json"
    report_path = report_dir / f"eml_d109_private_reviewer_response_availability_guard_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d109_private_reviewer_response_availability_guard.json"
    feed_path = command_feed_dir / f"eml_d109_private_reviewer_response_availability_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d109_private_reviewer_response_availability_guard")
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
    print("EML_D109_PRIVATE_REVIEWER_RESPONSE_AVAILABILITY_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
