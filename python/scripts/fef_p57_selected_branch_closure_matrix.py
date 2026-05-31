#!/usr/bin/env python3
"""FEF-P57 selected branch closure matrix."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p57_selected_branch_closure_matrix.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P57_SELECTED_BRANCH_CLOSURE_MATRIX_PASS"

P51_PACKET = ROOT / "reports/evidence_packets/fef_p51_branch_control_flow_blocker_gate.json"

BRANCH_PHASES = [
    {
        "phase": "FEF-P52",
        "caseId": "c_ternary_select_v0",
        "sourceLanguage": "c",
        "feature": "ternary_select",
        "packetPath": ROOT / "reports/evidence_packets/fef_p52_c_ternary_branch_lowering_gate.json",
        "summaryPassKey": "selectedCTernaryLoweringPass",
        "closureKey": "cTernaryBlockerClosed",
        "expectedPacketCount": 2,
        "expectedPacketSampleCount": 10,
    },
    {
        "phase": "FEF-P53",
        "caseId": "c_if_early_return_relu_v0",
        "sourceLanguage": "c",
        "feature": "if_early_return",
        "packetPath": ROOT / "reports/evidence_packets/fef_p53_c_if_early_return_branch_lowering_gate.json",
        "summaryPassKey": "selectedCIfEarlyReturnLoweringPass",
        "closureKey": "cIfEarlyReturnBlockerClosed",
        "expectedPacketCount": 2,
        "expectedPacketSampleCount": 10,
    },
    {
        "phase": "FEF-P54",
        "caseId": "c_if_else_clamp_v0",
        "sourceLanguage": "c",
        "feature": "if_else_clamp",
        "packetPath": ROOT / "reports/evidence_packets/fef_p54_c_if_else_clamp_branch_lowering_gate.json",
        "summaryPassKey": "selectedCIfElseClampLoweringPass",
        "closureKey": "cIfElseClampBlockerClosed",
        "expectedPacketCount": 2,
        "expectedPacketSampleCount": 14,
    },
    {
        "phase": "FEF-P55",
        "caseId": "rust_if_expr_relu_v0",
        "sourceLanguage": "rust",
        "feature": "if_expression",
        "packetPath": ROOT / "reports/evidence_packets/fef_p55_rust_if_expression_branch_lowering_gate.json",
        "summaryPassKey": "selectedRustIfExpressionLoweringPass",
        "closureKey": "rustIfExpressionBlockerClosed",
        "expectedPacketCount": 2,
        "expectedPacketSampleCount": 10,
    },
    {
        "phase": "FEF-P56",
        "caseId": "rust_if_return_clamp_v0",
        "sourceLanguage": "rust",
        "feature": "if_return_clamp",
        "packetPath": ROOT / "reports/evidence_packets/fef_p56_rust_if_return_branch_lowering_gate.json",
        "summaryPassKey": "selectedRustIfReturnLoweringPass",
        "closureKey": "rustIfReturnBlockerClosed",
        "expectedPacketCount": 2,
        "expectedPacketSampleCount": 14,
    },
]

CLAIM_FLAGS = {
    "all_selected_branch_closure_matrix_claim": False,
    "general_branch_control_flow_claim": False,
    "full_non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "arbitrary_source_family_claim": False,
    "all_free_targets_roundtrip_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_target_readiness_claim": False,
    "private_reviewer_decision_recorded": False,
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
    "FEF-P57 records a selected branch closure matrix over P51-P56 only.",
    "FEF-P57 does not add a new frontend lowering implementation.",
    "FEF-P57 does not claim general branch/control-flow support.",
    "FEF-P57 does not claim full non-generated source roundtrip.",
    "FEF-P57 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P57 does not claim arbitrary C/Rust source-family support.",
    "FEF-P57 does not record reviewer approval or rejection.",
    "FEF-P57 does not publish a package.",
    "FEF-P57 does not enable checkout or commerce.",
    "FEF-P57 does not claim public readiness.",
    "FEF-P57 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P57 does not claim runtime performance.",
    "FEF-P57 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P57 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_closure_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in BRANCH_PHASES:
        packet = read_json(spec["packetPath"])
        summary = packet["semanticReview"]
        row = {
            "phase": spec["phase"],
            "caseId": spec["caseId"],
            "sourceLanguage": spec["sourceLanguage"],
            "feature": spec["feature"],
            "packetPath": str(spec["packetPath"].relative_to(ROOT)),
            "packetReviewDecision": packet["reviewDecision"],
            "selectedLoweringPass": summary[spec["summaryPassKey"]],
            "p51BlockerClosed": summary[spec["closureKey"]],
            "packetCount": summary["packetCount"],
            "packetSampleCount": summary["packetSampleCount"],
            "generatedTargetLanguages": summary["generatedTargetLanguages"],
            "recompiledTargetLanguages": summary["recompiledTargetLanguages"],
            "maxAbsError": summary["maxAbsError"],
            "maxRelError": summary["maxRelError"],
            "claimFlags": dict(CLAIM_FLAGS),
        }
        rows.append(row)
    return rows


def summarize(rows: list[dict[str, Any]], p51_summary: dict[str, Any]) -> dict[str, Any]:
    total_packets = sum(row["packetCount"] for row in rows)
    total_samples = sum(row["packetSampleCount"] for row in rows)
    return {
        "selectedBranchCaseCount": len(rows),
        "selectedBranchClosureCount": sum(1 for row in rows if row["p51BlockerClosed"] is True),
        "selectedLoweringPassCount": sum(1 for row in rows if row["selectedLoweringPass"] is True),
        "totalReingestPacketCount": total_packets,
        "totalPacketSampleComparisons": total_samples,
        "sourceLanguages": sorted({row["sourceLanguage"] for row in rows}),
        "generatedTargetLanguages": sorted({lang for row in rows for lang in row["generatedTargetLanguages"]}),
        "recompiledTargetLanguages": sorted({lang for row in rows for lang in row["recompiledTargetLanguages"]}),
        "maxAbsError": max(row["maxAbsError"] for row in rows),
        "maxRelError": max(row["maxRelError"] for row in rows),
        "p51FixtureCount": p51_summary["fixtureCount"],
        "p51BlockedCount": p51_summary["blockedCount"],
        "p51LaterPhasePassCount": p51_summary["laterPhasePassCount"],
        "p51LaterPhasePassCaseIds": p51_summary["laterPhasePassCaseIds"],
        "generalBranchControlFlowClaim": False,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "fullCRustRoundtripClaim": False,
        "arbitrarySourceFamilyClaim": False,
        "reviewerDecisionRecorded": False,
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
    p51_packet = read_json(P51_PACKET)
    rows = build_closure_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p57-selected-branch-closure-matrix",
        "decision": "all_selected_branch_closures_recorded_general_branch_blocked",
        "closureRows": rows,
        "summary": summarize(rows, p51_packet["semanticReview"]),
        "fefP51Link": {
            "path": str(P51_PACKET.relative_to(ROOT)),
            "reviewDecision": p51_packet["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_branch_closure_matrix", "status": "pass"},
            {"id": "p51_selected_branch_blockers_remaining", "status": "zero_selected_blockers"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "full_non_generated_source_roundtrip_claim", "status": "blocked"},
            {"id": "arbitrary_source_family_claim", "status": "blocked"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivateClaims": [
            "All five selected P51 branch fixtures now have later-phase closure evidence in P52-P56.",
            "The selected branch closures cover C ternary, C if early-return, C if/else clamp, Rust if-expression, and Rust if-return clamp fixtures.",
            "The selected closures contain 10 generated C/Rust re-ingest packets and 58 packet-sample comparisons.",
            "P51 now records zero selected branch blockers while general branch/control-flow support remains blocked.",
        ],
        "blockedClaims": [
            "general C/Rust branch/control-flow support is established",
            "full non-generated source roundtrip is supported",
            "full arbitrary C/Rust source roundtrip is supported",
            "arbitrary C/Rust source-family support is established",
            "Forge/eFrog is public-ready",
            "a package has been published",
            "checkout is enabled",
            "compiler correctness has been proved",
            "formal semantic equivalence has been proved",
            "runtime performance has been established",
        ],
        "nextMilestones": [
            "Send P47-P57 to private review before changing release posture.",
            "If implementation continues, add broader branch fixtures only under new selected gates.",
            "Keep public/package/readiness/correctness/performance claims blocked until explicit review.",
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
        "title": "FEF-P57 Selected Branch Closure Matrix",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "all_selected_branch_closures_recorded_general_branch_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected branch closure matrix only; no general branch/control-flow support, full source roundtrip, arbitrary source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P57 consolidates P52-P56 selected branch closure evidence.",
            "All five selected P51 branch fixtures are now later-phase closures.",
            "The matrix contains 10 generated C/Rust re-ingest packets and 58 packet-sample comparisons.",
            "General branch/control-flow support remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p57_selected_branch_closure_matrix.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p57_selected_branch_closure_matrix.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p57_selected_branch_closure_matrix.v0",
        "date": DATE,
        "title": "FEF-P57 Selected Branch Closure Matrix",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Send P47-P57 to private review before changing release posture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Phase | Case | Source | Feature | Packets | Samples | Max abs error |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in payload["closureRows"]:
        rows.append(
            f"| `{row['phase']}` | `{row['caseId']}` | `{row['sourceLanguage']}` | `{row['feature']}` | {row['packetCount']} | {row['packetSampleCount']} | {row['maxAbsError']:.3e} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P57 Selected Branch Closure Matrix",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P57 consolidates the selected branch closure evidence from P52-P56.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Selected branch cases: `{summary['selectedBranchCaseCount']}`",
            f"- Selected branch closures: `{summary['selectedBranchClosureCount']}`",
            f"- Re-ingest packets: `{summary['totalReingestPacketCount']}`",
            f"- Packet-sample comparisons: `{summary['totalPacketSampleComparisons']}`",
            f"- Source languages: `{', '.join(summary['sourceLanguages'])}`",
            f"- Generated targets: `{', '.join(summary['generatedTargetLanguages'])}`",
            f"- Recompiled targets: `{', '.join(summary['recompiledTargetLanguages'])}`",
            f"- Max abs error: `{summary['maxAbsError']:.3e}`",
            f"- Max rel error: `{summary['maxRelError']:.3e}`",
            f"- P51 selected blockers remaining: `{summary['p51BlockedCount']}`",
            "",
            "## Allowed Private Claims",
            "",
            *[f"- {claim}" for claim in payload["allowedPrivateClaims"]],
            "",
            "## Blocked Claims",
            "",
            *[f"- {claim}" for claim in payload["blockedClaims"]],
            "",
            "## Boundary",
            "",
            "- Selected branch closure matrix only.",
            "- No general branch/control-flow support claim.",
            "- No full non-generated source roundtrip or arbitrary source-family claim.",
            "- No reviewer decision, package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P57 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P57 status")
    summary = payload["summary"]
    expected_case_ids = {spec["caseId"] for spec in BRANCH_PHASES}
    observed_case_ids = {row["caseId"] for row in payload["closureRows"]}
    if observed_case_ids != expected_case_ids:
        raise ValueError("unexpected selected branch case set")
    if summary["selectedBranchCaseCount"] != 5:
        raise ValueError("expected five selected branch cases")
    if summary["selectedBranchClosureCount"] != 5:
        raise ValueError("all selected branch cases should be closed")
    if summary["selectedLoweringPassCount"] != 5:
        raise ValueError("all selected branch lowerings should pass")
    if summary["totalReingestPacketCount"] != 10:
        raise ValueError("expected ten generated C/Rust re-ingest packets")
    if summary["totalPacketSampleComparisons"] != 58:
        raise ValueError("unexpected selected branch sample total")
    if summary["sourceLanguages"] != ["c", "rust"]:
        raise ValueError("expected C/Rust selected branch sources")
    if summary["generatedTargetLanguages"] != ["c", "rust"]:
        raise ValueError("expected C/Rust generated targets")
    if summary["recompiledTargetLanguages"] != ["python"]:
        raise ValueError("expected Python recompiled target")
    if summary["maxAbsError"] != 0.0 or summary["maxRelError"] != 0.0:
        raise ValueError("selected branch matrix should have zero observed error")
    if summary["p51BlockedCount"] != 0:
        raise ValueError("P51 selected blockers should be zero after P56")
    if set(summary["p51LaterPhasePassCaseIds"]) != expected_case_ids:
        raise ValueError("P51 later-phase closures should match selected branch cases")
    for row in payload["closureRows"]:
        if row["selectedLoweringPass"] is not True:
            raise ValueError(f"{row['caseId']} selected lowering did not pass")
        if row["p51BlockerClosed"] is not True:
            raise ValueError(f"{row['caseId']} P51 blocker not closed")
        if row["packetCount"] != 2:
            raise ValueError(f"{row['caseId']} should have generated C/Rust packets")
        for key, value in row["claimFlags"].items():
            if value is not False:
                raise ValueError(f"row claim flag must remain false: {key}")
    for key in [
        "generalBranchControlFlowClaim",
        "fullNonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "arbitrarySourceFamilyClaim",
        "reviewerDecisionRecorded",
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
    result_path = out_dir / f"fef_p57_selected_branch_closure_matrix_{STAMP}.json"
    report_path = report_dir / f"fef_p57_selected_branch_closure_matrix_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p57_selected_branch_closure_matrix.json"
    feed_path = command_feed_dir / f"fef_p57_selected_branch_closure_matrix_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p57_selected_branch_closure_matrix")
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
    print("FEF_P57_SELECTED_BRANCH_CLOSURE_MATRIX_OK")
    print(f"selected_cases={built['payload']['summary']['selectedBranchCaseCount']}")
    print(f"selected_closures={built['payload']['summary']['selectedBranchClosureCount']}")
    print(f"packet_samples={built['payload']['summary']['totalPacketSampleComparisons']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
