#!/usr/bin/env python3
"""FEF-P58 branch gap private-review addendum."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p58_branch_gap_private_review_addendum.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P58_BRANCH_GAP_PRIVATE_REVIEW_ADDENDUM_PASS"

SOURCE_PACKETS = {
    "P47": ROOT / "reports/evidence_packets/fef_p47_private_reviewer_bundle_index.json",
    "P48": ROOT / "reports/evidence_packets/fef_p48_private_reviewer_intake_packet.json",
    "P49": ROOT / "reports/evidence_packets/fef_p49_non_generated_c_rust_fixture_gate.json",
    "P50": ROOT / "reports/evidence_packets/fef_p50_non_generated_source_reingest_gate.json",
    "P51": ROOT / "reports/evidence_packets/fef_p51_branch_control_flow_blocker_gate.json",
    "P57": ROOT / "reports/evidence_packets/fef_p57_selected_branch_closure_matrix.json",
}

CLAIM_FLAGS = {
    "private_review_addendum_claim": False,
    "private_reviewer_decision_recorded": False,
    "general_branch_control_flow_claim": False,
    "branch_control_flow_reingest_claim": False,
    "full_non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "arbitrary_source_family_claim": False,
    "all_free_targets_roundtrip_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_target_readiness_claim": False,
    "public_preview_release_claim": False,
    "package_published": False,
    "checkout_enabled": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
}

NON_CLAIMS = [
    "FEF-P58 records a private-review addendum and gap analysis only.",
    "FEF-P58 does not add a new frontend lowering implementation.",
    "FEF-P58 does not record reviewer approval or rejection.",
    "FEF-P58 does not claim general branch/control-flow support.",
    "FEF-P58 does not claim branch/control-flow re-ingest support.",
    "FEF-P58 does not claim full non-generated source roundtrip.",
    "FEF-P58 does not claim arbitrary C/Rust source-family support.",
    "FEF-P58 does not publish a package.",
    "FEF-P58 does not enable checkout or commerce.",
    "FEF-P58 does not claim public readiness.",
    "FEF-P58 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P58 does not claim runtime performance.",
    "FEF-P58 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P58 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]

GAP_ROWS = [
    {
        "id": "grammar_surface_breadth",
        "status": "blocked",
        "selectedEvidence": "P52-P57 cover five selected branch forms only.",
        "missingEvidence": "arbitrary C/Rust branch syntax, nested statements, boolean combinations, and source-family corpus breadth",
        "nextValidator": "fixture_family_matrix",
    },
    {
        "id": "control_flow_normalization",
        "status": "blocked",
        "selectedEvidence": "Selected branches lower to guarded affine EML selectors using step01.",
        "missingEvidence": "general control-flow graph normalization with explicit dominance, fallthrough, merge, and return semantics",
        "nextValidator": "control_flow_ir_inventory",
    },
    {
        "id": "side_effect_and_state_model",
        "status": "blocked",
        "selectedEvidence": "Current selected branch fixtures are scalar and side-effect free.",
        "missingEvidence": "assignments, mutable locals, loops, function calls with effects, and memory/model boundaries",
        "nextValidator": "unsupported_constructs_blocker_gate",
    },
    {
        "id": "source_roundtrip_semantics",
        "status": "blocked",
        "selectedEvidence": "P50 and P57 re-ingest generated C/Rust targets and recompile to Python.",
        "missingEvidence": "source-preserving non-generated C/Rust roundtrip with branch/control-flow AST equivalence",
        "nextValidator": "non_generated_branch_roundtrip_gate",
    },
    {
        "id": "formal_correctness_surface",
        "status": "blocked",
        "selectedEvidence": "Evidence packets compare deterministic runtime samples.",
        "missingEvidence": "formal source semantics, lowering relation, proof obligations, and discharged proof artifacts",
        "nextValidator": "formal_obligation_inventory",
    },
    {
        "id": "release_readiness_surface",
        "status": "blocked",
        "selectedEvidence": "P47/P48 define private-review bundle and intake; P57 adds branch closure matrix.",
        "missingEvidence": "recorded reviewer decision, copy approval, package policy, checkout policy, and public-support plan",
        "nextValidator": "private_reviewer_response_packet",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_summaries() -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for phase, path in SOURCE_PACKETS.items():
        packet = read_json(path)
        summaries[phase] = {
            "artifactId": packet.get("artifactId"),
            "title": packet.get("title"),
            "packetPath": str(path.relative_to(ROOT)),
            "reviewDecision": packet.get("reviewDecision"),
            "validationStatus": packet.get("validationStatus"),
            "semanticStrength": packet.get("semanticStrength"),
            "semanticReview": packet.get("semanticReview", {}),
            "claimFlagsAllFalse": all(value is False for value in packet.get("claimFlags", {}).values()),
        }
    return summaries


def build_summary(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    p47 = sources["P47"]["semanticReview"]
    p48 = sources["P48"]["semanticReview"]
    p49 = sources["P49"]["semanticReview"]
    p50 = sources["P50"]["semanticReview"]
    p51 = sources["P51"]["semanticReview"]
    p57 = sources["P57"]["semanticReview"]
    return {
        "sourcePacketCount": len(sources),
        "allSourcePacketsValidationPass": all(item["validationStatus"] == "pass" for item in sources.values()),
        "allSourcePacketClaimFlagsFalse": all(item["claimFlagsAllFalse"] for item in sources.values()),
        "privateReviewBundleReady": p47["privatePreviewReleaseActionApproved"] is True,
        "privateReviewerIntakeReady": p48["intakeReady"] is True,
        "reviewerDecisionRecorded": False,
        "nonGeneratedSemanticSourceCaseCount": p49["nonGeneratedSourceCaseCount"],
        "nonGeneratedSemanticSourceSampleCount": p49["nonGeneratedSourceSampleCount"],
        "sourceDerivedReingestPacketCount": p50["packetCount"],
        "sourceDerivedReingestSampleCount": p50["packetSampleCount"],
        "selectedBranchCaseCount": p57["selectedBranchCaseCount"],
        "selectedBranchClosureCount": p57["selectedBranchClosureCount"],
        "selectedBranchReingestPacketCount": p57["totalReingestPacketCount"],
        "selectedBranchPacketSampleComparisons": p57["totalPacketSampleComparisons"],
        "p51SelectedBlockedCount": p51["blockedCount"],
        "gapCount": len(GAP_ROWS),
        "blockedGapCount": sum(1 for row in GAP_ROWS if row["status"] == "blocked"),
        "recommendedNextPhase": "private_reviewer_response_or_branch_gap_validator",
        "generalBranchControlFlowClaim": False,
        "branchControlFlowReingestClaim": False,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "fullCRustRoundtripClaim": False,
        "arbitrarySourceFamilyClaim": False,
        "packagePublished": False,
        "checkoutEnabled": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "allFreeTargetsRuntimeExecutionClaim": False,
        "allFreeTargetsRoundtripClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    sources = source_summaries()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p58-branch-gap-private-review-addendum",
        "decision": "private_review_addendum_ready_general_branch_gap_blocked",
        "sourcePackets": sources,
        "summary": build_summary(sources),
        "gapRows": copy.deepcopy(GAP_ROWS),
        "reviewerAddendum": {
            "addendumStatus": "ready_for_private_review",
            "reviewerDecisionStatus": "not_recorded",
            "reviewSurface": "private_only",
            "reviewerShouldInspect": [
                "P47/P48 for private-review bundle and intake boundaries.",
                "P49/P50 for selected non-generated C/Rust semantic and re-ingest evidence.",
                "P51/P57 for the selected branch blocker inventory and closure matrix.",
                "The six remaining gap rows before any general branch/control-flow claim changes.",
            ],
            "reviewerQuestions": [
                "Is the selected branch closure matrix enough to close the current private-review concern?",
                "Which remaining gap should be implemented first: grammar breadth, control-flow IR, source roundtrip, or formal semantics?",
                "Which blocked claim is most likely to be misunderstood by a private reviewer?",
                "Should the next phase record reviewer response or build the next gap validator?",
            ],
            "allowedReviewerOutcomes": [
                "accept_selected_branch_closure_scope",
                "request_branch_gap_validator",
                "request_copy_tightening",
                "request_broader_fixture_family",
                "hold_private_preview",
            ],
        },
        "allowedPrivateReviewerStatements": [
            "P57 closes all five selected P51 branch blockers under selected-fixture evidence.",
            "P58 identifies six remaining blocked gaps before any general branch/control-flow claim.",
            "P47-P58 are ready to send as a private-review packet set.",
        ],
        "blockedStatements": [
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Arbitrary C/Rust source-family support is established.",
            "A reviewer has approved the bundle.",
            "Forge/eFrog is public-ready.",
            "A package has been published.",
            "Checkout is enabled.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "releaseGates": [
            {"id": "private_reviewer_addendum", "status": "ready"},
            {"id": "selected_branch_closure_matrix", "status": "pass"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "full_non_generated_source_roundtrip", "status": "blocked"},
            {"id": "arbitrary_source_family_support", "status": "blocked"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "public_release", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "nextMilestones": [
            "Send P47-P58 to private review and record the reviewer response.",
            "If implementation continues, choose one blocked gap and build a narrow validator.",
            "Do not widen public/package/readiness/correctness/performance claims from selected evidence alone.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return copy.deepcopy(payload)


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P58 Branch Gap Private-Review Addendum",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "private_review_addendum_ready_general_branch_gap_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private-review addendum and gap analysis only; no reviewer decision, general branch/control-flow support, branch re-ingest, full source roundtrip, arbitrary source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P58 links P47/P48/P49/P50/P51/P57 into a private-review addendum.",
            "P57 closes all five selected P51 branch blockers under selected-fixture evidence.",
            "Six remaining gaps are explicitly blocked before general branch/control-flow support.",
            "No reviewer decision or public-release posture change is recorded.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p58_branch_gap_private_review_addendum.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p58_branch_gap_private_review_addendum.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p58_branch_gap_private_review_addendum.v0",
        "date": DATE,
        "title": "FEF-P58 Branch Gap Private-Review Addendum",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Send P47-P58 to private review or pick one blocked gap for a narrow validator.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Gap | Status | Selected Evidence | Missing Evidence | Next Validator |",
        "|---|---|---|---|---|",
    ]
    for row in payload["gapRows"]:
        rows.append(
            f"| `{row['id']}` | `{row['status']}` | {row['selectedEvidence']} | {row['missingEvidence']} | `{row['nextValidator']}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P58 Branch Gap Private-Review Addendum",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P58 turns the P57 selected branch closure matrix into a private-review addendum and gap map.",
            "",
            "## Summary",
            "",
            f"- Source packets: `{summary['sourcePacketCount']}`",
            f"- Private review bundle ready: `{summary['privateReviewBundleReady']}`",
            f"- Private reviewer intake ready: `{summary['privateReviewerIntakeReady']}`",
            f"- Reviewer decision recorded: `{summary['reviewerDecisionRecorded']}`",
            f"- Selected branch closures: `{summary['selectedBranchClosureCount']}`",
            f"- Selected branch re-ingest packets: `{summary['selectedBranchReingestPacketCount']}`",
            f"- Selected branch packet-sample comparisons: `{summary['selectedBranchPacketSampleComparisons']}`",
            f"- P51 selected blockers remaining: `{summary['p51SelectedBlockedCount']}`",
            f"- Blocked gap rows: `{summary['blockedGapCount']}`",
            "",
            "## Gap Rows",
            "",
            *rows,
            "",
            "## Allowed Private Reviewer Statements",
            "",
            *[f"- {statement}" for statement in payload["allowedPrivateReviewerStatements"]],
            "",
            "## Blocked Statements",
            "",
            *[f"- {statement}" for statement in payload["blockedStatements"]],
            "",
            "## Boundary",
            "",
            "- Private-review addendum and gap analysis only.",
            "- No reviewer approval or public-release posture change.",
            "- No general branch/control-flow, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P58 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P58 status")
    summary = payload["summary"]
    if summary["sourcePacketCount"] != 6:
        raise ValueError("expected six source packets")
    if summary["allSourcePacketsValidationPass"] is not True:
        raise ValueError("all source packets must validate")
    if summary["allSourcePacketClaimFlagsFalse"] is not True:
        raise ValueError("source packet claim flags must remain false")
    if summary["privateReviewBundleReady"] is not True:
        raise ValueError("P47 private bundle should be ready")
    if summary["privateReviewerIntakeReady"] is not True:
        raise ValueError("P48 private intake should be ready")
    if summary["reviewerDecisionRecorded"] is not False:
        raise ValueError("P58 must not record reviewer decision")
    if summary["nonGeneratedSemanticSourceCaseCount"] != 5:
        raise ValueError("expected five selected non-generated source cases")
    if summary["sourceDerivedReingestPacketCount"] != 10:
        raise ValueError("expected ten source-derived re-ingest packets")
    if summary["sourceDerivedReingestSampleCount"] != 46:
        raise ValueError("unexpected source-derived sample total")
    if summary["selectedBranchCaseCount"] != 5:
        raise ValueError("expected five selected branch cases")
    if summary["selectedBranchClosureCount"] != 5:
        raise ValueError("expected five selected branch closures")
    if summary["selectedBranchReingestPacketCount"] != 10:
        raise ValueError("expected ten selected branch packets")
    if summary["selectedBranchPacketSampleComparisons"] != 58:
        raise ValueError("unexpected selected branch sample total")
    if summary["p51SelectedBlockedCount"] != 0:
        raise ValueError("P51 selected blockers should remain zero")
    if summary["gapCount"] != 6 or summary["blockedGapCount"] != 6:
        raise ValueError("expected six blocked gap rows")
    for row in payload["gapRows"]:
        if row["status"] != "blocked":
            raise ValueError(f"gap row must remain blocked: {row['id']}")
    for key in [
        "generalBranchControlFlowClaim",
        "branchControlFlowReingestClaim",
        "fullNonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "arbitrarySourceFamilyClaim",
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsRoundtripClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p58_branch_gap_private_review_addendum_{STAMP}.json"
    report_path = report_dir / f"fef_p58_branch_gap_private_review_addendum_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p58_branch_gap_private_review_addendum.json"
    feed_path = command_feed_dir / f"fef_p58_branch_gap_private_review_addendum_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p58_branch_gap_private_review_addendum")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P58_BRANCH_GAP_PRIVATE_REVIEW_ADDENDUM_OK")
    print(f"source_packets={built['payload']['summary']['sourcePacketCount']}")
    print(f"blocked_gaps={built['payload']['summary']['blockedGapCount']}")
    print(f"selected_branch_closures={built['payload']['summary']['selectedBranchClosureCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
