#!/usr/bin/env python3
"""FEF-P51 branch/control-flow blocker gate for non-generated C/Rust fixtures."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))
if str(EFROG_ROOT) not in sys.path:
    sys.path.insert(0, str(EFROG_ROOT))

from efrog.decompilers.c import decompile_c_source  # noqa: E402
from efrog.decompilers.rust import decompile_rust_source  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p51_branch_control_flow_blocker_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P51_BRANCH_CONTROL_FLOW_BLOCKER_GATE_PASS"
LATER_PHASE_PASS_CASE_IDS = {
    "c_ternary_select_v0",
    "c_if_early_return_relu_v0",
    "c_if_else_clamp_v0",
    "rust_if_expr_relu_v0",
}
MIN_EXPECTED_BLOCKED_FIXTURES = 1
MAX_EXPECTED_LATER_PHASE_PASSES = len(LATER_PHASE_PASS_CASE_IDS)

P50_PACKET = ROOT / "reports/evidence_packets/fef_p50_non_generated_source_reingest_gate.json"

CLAIM_FLAGS = {
    "branch_control_flow_supported": False,
    "branch_control_flow_reingest_claim": False,
    "selected_branch_fixture_pass_claim": False,
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
    "FEF-P51 records branch/control-flow blockers for selected non-generated C/Rust fixtures.",
    "FEF-P51 does not implement C/Rust branch/control-flow decompilation.",
    "FEF-P51 does not claim selected branch fixtures pass.",
    "FEF-P51 does not claim branch/control-flow re-ingest.",
    "FEF-P51 does not claim full non-generated source roundtrip.",
    "FEF-P51 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P51 does not record reviewer approval or rejection.",
    "FEF-P51 does not publish a package.",
    "FEF-P51 does not enable checkout or commerce.",
    "FEF-P51 does not claim public readiness.",
    "FEF-P51 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P51 does not claim runtime performance.",
    "FEF-P51 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P51 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]

BRANCH_FIXTURES = [
    {
        "caseId": "c_if_early_return_relu_v0",
        "sourceLanguage": "c",
        "feature": "if_early_return",
        "expectedStatus": "blocked_or_later_phase_pass",
        "source": "double relu(double x) { if (x > 0.0) return x; return 0.0; }",
    },
    {
        "caseId": "c_if_else_clamp_v0",
        "sourceLanguage": "c",
        "feature": "if_else_clamp",
        "expectedStatus": "blocked",
        "source": (
            "double clamp(double x, double lo, double hi) { "
            "if (x < lo) return lo; else if (x > hi) return hi; else return x; }"
        ),
    },
    {
        "caseId": "c_ternary_select_v0",
        "sourceLanguage": "c",
        "feature": "ternary_select",
        "expectedStatus": "blocked_or_later_phase_pass",
        "source": "double select_pos(double x) { return x > 0.0 ? x : 0.0; }",
    },
    {
        "caseId": "rust_if_expr_relu_v0",
        "sourceLanguage": "rust",
        "feature": "if_expression",
        "expectedStatus": "blocked",
        "source": "fn relu(x: f64) -> f64 { if x > 0.0 { x } else { 0.0 } }",
    },
    {
        "caseId": "rust_if_return_clamp_v0",
        "sourceLanguage": "rust",
        "feature": "if_return_clamp",
        "expectedStatus": "blocked",
        "source": (
            "fn clamp(x: f64, lo: f64, hi: f64) -> f64 { "
            "if x < lo { return lo; } if x > hi { return hi; } return x; }"
        ),
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def attempt_fixture(fixture: dict[str, str]) -> dict[str, Any]:
    try:
        if fixture["sourceLanguage"] == "c":
            mod = decompile_c_source(fixture["source"], source_path=f"{fixture['caseId']}.c")
        elif fixture["sourceLanguage"] == "rust":
            mod = decompile_rust_source(fixture["source"], source_path=f"{fixture['caseId']}.rs")
        else:
            raise ValueError(f"unsupported source language: {fixture['sourceLanguage']}")
        eml = mod.to_eml()
        status = "unexpected_pass"
        error_type = None
        error_message = None
        emitted_eml = eml
    except Exception as exc:  # Blocker inventory intentionally records local frontend errors.
        status = "blocked"
        error_type = type(exc).__name__
        error_message = str(exc)
        emitted_eml = None
    return {
        "caseId": fixture["caseId"],
        "sourceLanguage": fixture["sourceLanguage"],
        "feature": fixture["feature"],
        "expectedStatus": fixture["expectedStatus"],
        "observedStatus": status,
        "errorType": error_type,
        "errorMessage": error_message,
        "emittedEml": emitted_eml,
        "sourceSnippet": fixture["source"],
        "blockerClass": classify_blocker(fixture, error_message),
        "claimFlags": dict(CLAIM_FLAGS),
    }


def classify_blocker(fixture: dict[str, str], error_message: str | None) -> str:
    if not error_message:
        return "unexpected_pass"
    if fixture["sourceLanguage"] == "c" and fixture["feature"].startswith("if"):
        return "c_statement_control_flow_unsupported"
    if fixture["sourceLanguage"] == "c" and fixture["feature"] == "ternary_select":
        return "c_conditional_expression_unsupported"
    if fixture["sourceLanguage"] == "rust" and fixture["feature"].startswith("if"):
        return "rust_if_expression_unsupported"
    return "unclassified_frontend_blocker"


def summarize(rows: list[dict[str, Any]], p50_summary: dict[str, Any]) -> dict[str, Any]:
    blocker_classes = sorted(
        {row["blockerClass"] for row in rows if row["observedStatus"] == "blocked"}
    )
    later_phase_passes = [
        row["caseId"]
        for row in rows
        if row["caseId"] in LATER_PHASE_PASS_CASE_IDS
        and row["observedStatus"] == "unexpected_pass"
    ]
    return {
        "fixtureCount": len(rows),
        "blockedCount": sum(1 for row in rows if row["observedStatus"] == "blocked"),
        "unexpectedPassCount": sum(1 for row in rows if row["observedStatus"] == "unexpected_pass"),
        "laterPhasePassCount": len(later_phase_passes),
        "laterPhasePassCaseIds": later_phase_passes,
        "minimumExpectedBlockedFixtures": MIN_EXPECTED_BLOCKED_FIXTURES,
        "sourceLanguages": sorted({row["sourceLanguage"] for row in rows}),
        "features": [row["feature"] for row in rows],
        "blockerClasses": blocker_classes,
        "p50SourceDerivedReingestPass": p50_summary["selectedNonGeneratedSourceDerivedReingest"],
        "p50SourceCaseCount": p50_summary["sourceCaseCount"],
        "p50PacketCount": p50_summary["packetCount"],
        "branchControlFlowSupported": False,
        "branchControlFlowReingestClaim": False,
        "selectedBranchFixturePassClaim": False,
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
    p50_packet = read_json(P50_PACKET)
    rows = [attempt_fixture(fixture) for fixture in BRANCH_FIXTURES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p51-branch-control-flow-blocker-gate",
        "decision": "branch_control_flow_non_generated_c_rust_blockers_recorded",
        "fixtureRows": rows,
        "summary": summarize(rows, p50_packet["semanticReview"]),
        "fefP50Link": {
            "path": str(P50_PACKET.relative_to(ROOT)),
            "reviewDecision": p50_packet["reviewDecision"],
        },
        "releaseGates": [
            {"id": "branch_control_flow_fixture_attempted", "status": "pass"},
            {"id": "branch_control_flow_supported", "status": "blocked"},
            {"id": "branch_control_flow_reingest", "status": "blocked"},
            {"id": "full_non_generated_source_roundtrip_claim", "status": "blocked"},
            {"id": "arbitrary_source_family_claim", "status": "blocked"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "implementationRequirements": [
            "Keep C branch lowering evidence in later selected P52/P53/P54 gates, not in P51 blocker evidence.",
            "Keep selected Rust `if` expression evidence in the later FEF-P55 gate, not in P51 blocker evidence.",
            "Add Rust `if return` parsing/lowering before branch re-ingest can cover the remaining selected Rust branch blocker.",
            "Add deterministic boundary samples around branch thresholds after frontend support exists.",
            "Keep the new branch gate separate from P50 scalar source-derived re-ingest evidence.",
        ],
        "allowedPrivateClaims": [
            "Selected branch/control-flow C/Rust fixtures were attempted and current frontend blockers are recorded.",
            "After FEF-P52/FEF-P53/FEF-P54/FEF-P55, selected C branch cases and the selected Rust if-expression case may pass as later-phase closures while P51 remains a blocker inventory.",
            "P50 scalar source-derived re-ingest evidence remains valid but does not cover branch/control-flow fixtures.",
            "The next branch work is implementation work, not a release-action task.",
        ],
        "blockedClaims": [
            "C/Rust branch/control-flow source fixtures pass",
            "branch/control-flow re-ingest is supported",
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
            "Implement the narrow C/Rust branch frontends or keep branch fixtures as blocked review evidence.",
            "After each frontend slice exists, add a separate branch fixture runtime/re-ingest gate.",
            "Record private reviewer response over P47-P55 before changing release posture.",
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
        "title": "FEF-P51 Branch/Control-Flow Blocker Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "branch_control_flow_blocker_inventory_no_support_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Branch/control-flow blocker inventory only; selected non-generated C/Rust branch fixtures are attempted and blocked at the frontend boundary. No branch support, branch re-ingest, full source roundtrip, arbitrary source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P51 attempts selected C/Rust branch/control-flow fixtures and records their blockers.",
            "After FEF-P52/FEF-P53/FEF-P54/FEF-P55, selected C branch cases and the selected Rust if-expression case may pass as later-phase closures; Rust `if return` remains a frontend blocker.",
            "P50 scalar source-derived re-ingest evidence remains separate and does not cover branch/control-flow.",
            "No branch/control-flow support claim is made.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p51_branch_control_flow_blocker_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p51_branch_control_flow_blocker_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p51_branch_control_flow_blocker_gate.v0",
        "date": DATE,
        "title": "FEF-P51 Branch/Control-Flow Blocker Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Implement narrow Rust if-return frontend lowering or record private reviewer response over P47-P55.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Source | Feature | Observed | Blocker class | Error |",
        "|---|---|---|---|---|---|",
    ]
    for row in payload["fixtureRows"]:
        error = (row["errorMessage"] or "").replace("|", "\\|")
        rows.append(
            f"| `{row['caseId']}` | `{row['sourceLanguage']}` | `{row['feature']}` | `{row['observedStatus']}` | `{row['blockerClass']}` | {error} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P51 Branch/Control-Flow Blocker Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P51 attempts selected non-generated C/Rust branch/control-flow fixtures.",
            "The goal is blocker inventory, not branch support.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Fixtures attempted: `{summary['fixtureCount']}`",
            f"- Blocked fixtures: `{summary['blockedCount']}`",
            f"- Unexpected passes: `{summary['unexpectedPassCount']}`",
            f"- Later-phase pass cases: `{', '.join(summary['laterPhasePassCaseIds']) or 'none'}`",
            f"- Source languages: `{', '.join(summary['sourceLanguages'])}`",
            f"- Blocker classes: `{', '.join(summary['blockerClasses'])}`",
            f"- P50 source-derived re-ingest pass: `{summary['p50SourceDerivedReingestPass']}`",
            "",
            "## Implementation Requirements",
            "",
            *[f"- {item}" for item in payload["implementationRequirements"]],
            "",
            "## Boundary",
            "",
            "- Branch/control-flow blocker inventory only.",
            "- No C/Rust branch/control-flow support claim.",
            "- No branch/control-flow re-ingest claim.",
            "- No full non-generated source roundtrip or arbitrary source-family claim.",
            "- No reviewer decision, package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P51 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P51 status")
    summary = payload["summary"]
    if summary["fixtureCount"] != len(BRANCH_FIXTURES):
        raise ValueError("unexpected branch fixture count")
    if summary["blockedCount"] < MIN_EXPECTED_BLOCKED_FIXTURES:
        raise ValueError("too few P51 fixtures remain blocked")
    if summary["unexpectedPassCount"] > MAX_EXPECTED_LATER_PHASE_PASSES:
        raise ValueError("too many later-phase branch fixture passes")
    if summary["laterPhasePassCount"] != summary["unexpectedPassCount"]:
        raise ValueError("unexpected pass must be recorded as a later-phase pass")
    if set(summary["laterPhasePassCaseIds"]) - LATER_PHASE_PASS_CASE_IDS:
        raise ValueError("only recorded later-phase cases may pass in P51")
    if summary["sourceLanguages"] != ["c", "rust"]:
        raise ValueError("expected C/Rust branch fixture languages")
    if summary["p50SourceDerivedReingestPass"] is not True:
        raise ValueError("P50 source-derived re-ingest should remain linked")
    expected_classes = {
        "rust_if_expression_unsupported",
    }
    if not expected_classes.issubset(set(summary["blockerClasses"])):
        raise ValueError("unexpected branch blocker class set")
    for row in payload["fixtureRows"]:
        if row["caseId"] in LATER_PHASE_PASS_CASE_IDS and row["observedStatus"] == "unexpected_pass":
            if not row["emittedEml"] or "step01" not in row["emittedEml"]:
                raise ValueError("later-phase branch pass must emit guarded EML")
            continue
        if row["observedStatus"] != "blocked":
            raise ValueError(f"{row['caseId']} must be blocked")
        if not row["errorMessage"]:
            raise ValueError(f"{row['caseId']} must record an error message")
        for key, value in row["claimFlags"].items():
            if value is not False:
                raise ValueError(f"row claim flag must remain false: {key}")
    for key in [
        "branchControlFlowSupported",
        "branchControlFlowReingestClaim",
        "selectedBranchFixturePassClaim",
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
    result_path = out_dir / f"fef_p51_branch_control_flow_blocker_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p51_branch_control_flow_blocker_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p51_branch_control_flow_blocker_gate.json"
    feed_path = command_feed_dir / f"fef_p51_branch_control_flow_blocker_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p51_branch_control_flow_blocker_gate")
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
    print("FEF_P51_BRANCH_CONTROL_FLOW_BLOCKER_GATE_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"blocked={built['payload']['summary']['blockedCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
