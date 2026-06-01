#!/usr/bin/env python3
"""FEF-P123 local expected-row checker for one source-preserving fixture."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p122_source_preserving_expected_rows as p122  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p123_source_preserving_expected_row_checker.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P123_SOURCE_PRESERVING_EXPECTED_ROW_CHECKER_PASS"

P122_PACKET = ROOT / "reports/evidence_packets/fef_p122_source_preserving_expected_rows.json"
P122_RESULT = ROOT / "python/results/fef_p122_source_preserving_expected_rows/fef_p122_source_preserving_expected_rows_2026_06_01.json"
SELECTED_FIXTURE_ID = p122.SELECTED_FIXTURE_ID

CLAIM_FLAGS = {
    "source_preserving_expected_row_checker_claim": False,
    "source_preserving_expected_rows_claim": False,
    "source_preserving_roundtrip_support_claim": False,
    "source_parse_execution_claim": False,
    "source_reemission_claim": False,
    "source_fidelity_claim": False,
    "source_fidelity_validation_claim": False,
    "preservation_oracle_claim": False,
    "non_generated_source_roundtrip_claim": False,
    "compound_condition_support_claim": False,
    "loop_backedge_support_claim": False,
    "assignment_phi_support_claim": False,
    "side_effect_memory_support_claim": False,
    "nested_branch_support_claim": False,
    "control_flow_ir_implemented": False,
    "frontend_lowering_changed": False,
    "unsupported_constructs_supported": False,
    "general_branch_control_flow_claim": False,
    "branch_control_flow_reingest_claim": False,
    "full_non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "arbitrary_source_family_claim": False,
    "private_reviewer_decision_recorded": False,
    "implementation_change_approved": False,
    "implementation_change_applied": False,
    "public_preview_release_claim": False,
    "package_published": False,
    "checkout_enabled": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "production_ready": False,
}

NON_CLAIMS = [
    "FEF-P123 runs a local expected-row checker against the P122 source sketch only.",
    "FEF-P123 does not parse non-generated source.",
    "FEF-P123 does not re-emit non-generated source.",
    "FEF-P123 does not run a preservation oracle.",
    "FEF-P123 does not execute source, generated, or re-ingested code.",
    "FEF-P123 does not validate token, whitespace, comment, formatting, or source-layout fidelity.",
    "FEF-P123 does not implement source-preserving roundtrip support.",
    "FEF-P123 does not widen Forge or eFrog frontend lowering.",
    "FEF-P123 preserves the P120/P121/P122 private review hold boundary.",
    "FEF-P123 does not record reviewer approval or rejection.",
    "FEF-P123 does not claim general branch/control-flow support.",
    "FEF-P123 does not claim full non-generated source roundtrip.",
    "FEF-P123 does not claim arbitrary C/Rust source-family support.",
    "FEF-P123 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P123 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_presence(source: str, row: dict[str, Any]) -> bool:
    if row["expectedValue"] is True:
        return str(row["sourceSlice"]) in source
    return str(row["sourceSlice"]) not in source


def check_exact_text(source: str, row: dict[str, Any]) -> bool:
    return row["expectedValue"] == row["sourceSlice"] and str(row["expectedValue"]) in source


def check_relative_order(source: str, row: dict[str, Any]) -> bool:
    position = -1
    for token in row["expectedValue"]:
        next_position = source.find(token, position + 1)
        if next_position < 0:
            return False
        position = next_position
    return True


def check_multiline_brace_layout(source: str, row: dict[str, Any]) -> bool:
    lines = source.splitlines()
    expected = row["expectedValue"]
    return (
        expected["ifOpeningBraceLine"] in lines
        and expected["elseOpeningBraceLine"] in lines
        and expected["closingBraceLine"] == lines[-1]
    )


def check_exact_statement(source: str, row: dict[str, Any]) -> bool:
    return row["expectedValue"] in [line.strip() for line in source.splitlines()]


def check_line_count(source: str, row: dict[str, Any]) -> bool:
    return len(source.splitlines()) == row["expectedValue"]


def check_row(source: str, row: dict[str, Any]) -> dict[str, Any]:
    checkers = {
        "presence": check_presence,
        "exact_text": check_exact_text,
        "relative_order": check_relative_order,
        "multiline_brace_layout": check_multiline_brace_layout,
        "exact_statement": check_exact_statement,
        "line_count": check_line_count,
    }
    if row["expectedKind"] not in checkers:
        raise ValueError(f"unknown expected kind: {row['expectedKind']}")
    matched = checkers[row["expectedKind"]](source, row)
    return {
        "rowId": row["id"],
        "category": row["category"],
        "expectedKind": row["expectedKind"],
        "checkStatus": "pass" if matched else "fail",
        "matchedExpectedRow": matched,
        "sourceSketchChecked": True,
        "sourceParsePerformed": False,
        "sourceReemissionPerformed": False,
        "preservationOracleRun": False,
        "sourceFidelityValidated": False,
        "runtimeExecutionPerformed": False,
        "supportClaimAllowed": False,
    }


def checker_rows(source: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [check_row(source, row) for row in rows]


def build_summary(p122_packet: dict[str, Any], p122_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    pass_count = sum(1 for row in rows if row["checkStatus"] == "pass")
    fail_count = len(rows) - pass_count
    return {
        "sourcePacketCount": 1,
        "p122ValidationPass": p122_packet["validationStatus"] == "pass",
        "p122ClaimFlagsAllFalse": all(value is False for value in p122_packet["claimFlags"].values()),
        "p122ExpectedRowCount": p122_payload["summary"]["expectedRowCount"],
        "p122ReviewerDecisionRecorded": p122_payload["summary"]["reviewerDecisionRecorded"],
        "p122ImplementationHeldPendingReview": p122_payload["summary"]["p121ImplementationHeldPendingReview"],
        "selectedFixtureId": p122_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p122_payload["summary"]["selectedFixtureStillBlocked"],
        "checkerRowCount": len(rows),
        "checkerPassCount": pass_count,
        "checkerFailCount": fail_count,
        "allExpectedRowsMatched": fail_count == 0,
        "allRowsSourceSketchChecked": all(row["sourceSketchChecked"] is True for row in rows),
        "allSourceParseNotPerformed": all(row["sourceParsePerformed"] is False for row in rows),
        "allSourceReemissionNotPerformed": all(row["sourceReemissionPerformed"] is False for row in rows),
        "allPreservationOracleNotRun": all(row["preservationOracleRun"] is False for row in rows),
        "allSourceFidelityNotValidated": all(row["sourceFidelityValidated"] is False for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "allSupportClaimsBlocked": all(row["supportClaimAllowed"] is False for row in rows),
        "sourcePreservingExpectedRowCheckerClaim": False,
        "sourcePreservingExpectedRowsClaim": False,
        "sourcePreservingRoundtripSupportClaim": False,
        "sourceParseExecutionClaim": False,
        "sourceReemissionClaim": False,
        "sourceFidelityClaim": False,
        "sourceFidelityValidationClaim": False,
        "preservationOracleClaim": False,
        "nonGeneratedSourceRoundtripClaim": False,
        "compoundConditionSupportClaim": False,
        "loopBackedgeSupportClaim": False,
        "assignmentPhiSupportClaim": False,
        "sideEffectMemorySupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "frontendLoweringChanged": False,
        "unsupportedConstructsSupported": False,
        "generalBranchControlFlowClaim": False,
        "branchControlFlowReingestClaim": False,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "fullCRustRoundtripClaim": False,
        "arbitrarySourceFamilyClaim": False,
        "reviewerDecisionRecorded": False,
        "implementationChangeApproved": False,
        "implementationChangeApplied": False,
        "packagePublished": False,
        "checkoutEnabled": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p122_packet = read_json(P122_PACKET)
    p122_payload = read_json(P122_RESULT)
    p122.validate_payload(p122_payload)
    source = p122_payload["selectedFixture"]["sourceSketch"]
    rows = checker_rows(source, p122_payload["expectedPreservationRows"])
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p123-source-preserving-expected-row-checker",
        "decision": "source_preserving_expected_row_checker_pass_support_blocked",
        "sourcePacket": {
            "phase": "P122",
            "packetPath": str(P122_PACKET.relative_to(ROOT)),
            "resultPath": str(P122_RESULT.relative_to(ROOT)),
            "reviewDecision": p122_packet["reviewDecision"],
            "validationStatus": p122_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p122_payload["selectedFixture"]),
        "sourceSketch": source,
        "checkerRows": rows,
        "summary": build_summary(p122_packet, p122_payload, rows),
        "releaseGates": [
            {"id": "source_preserving_expected_row_checker", "status": "pass"},
            {"id": "source_parse_execution", "status": "not_performed"},
            {"id": "source_reemission", "status": "not_performed"},
            {"id": "preservation_oracle", "status": "not_run"},
            {"id": "source_fidelity_validation", "status": "not_performed"},
            {"id": "source_preserving_roundtrip_support", "status": "blocked"},
            {"id": "full_non_generated_source_roundtrip", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P123 runs a local expected-row checker over the P122 source sketch.",
            "P123 matched all eight P122 expected rows against the selected fixture sketch.",
            "P123 keeps source parsing, source re-emission, preservation-oracle execution, and source fidelity validation blocked.",
        ],
        "blockedStatements": [
            "Non-generated source was parsed for source-preserving roundtrip.",
            "Non-generated source was re-emitted.",
            "A preservation oracle checked source fidelity.",
            "Token, whitespace, comment, or formatting fidelity has been validated.",
            "Source-preserving roundtrip is supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Add a mismatch/negative-control checker fixture before broadening the source-preserving ladder.",
            "Record actual private reviewer response to P47-P123 if one exists.",
            "Keep held proposals P111 and P119 unapplied without reviewer approval.",
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
        "title": "FEF-P123 Source-Preserving Expected Row Checker",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "source_preserving_expected_row_checker_pass_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected-row checker over stored source sketch only; no source parsing, source re-emission, preservation-oracle execution, token/comment/layout fidelity validation, source-preserving support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P123 checks the eight P122 expected rows against the stored c_if_else_source_layout_v0 source sketch.",
            "All eight expected rows match the stored source sketch.",
            "No source parse, source re-emission, preservation oracle, or fidelity validation is performed.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p123_source_preserving_expected_row_checker.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p123_source_preserving_expected_row_checker.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p123_source_preserving_expected_row_checker.v0",
        "date": DATE,
        "title": "FEF-P123 Source-Preserving Expected Row Checker",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add a mismatch/negative-control checker fixture before broadening source-preserving claims.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Row | Category | Status | Parse | Fidelity |", "|---|---|---|---|---|"]
    for row in payload["checkerRows"]:
        rows.append(
            f"| `{row['rowId']}` | `{row['category']}` | `{row['checkStatus']}` | `{row['sourceParsePerformed']}` | `{row['sourceFidelityValidated']}` |"
        )
    return "\n".join(
        [
            "# FEF-P123 Source-Preserving Expected Row Checker",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P123 checks P122 expected rows against the stored source sketch only.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Checker rows: `{summary['checkerRowCount']}`",
            f"- Checker passes: `{summary['checkerPassCount']}`",
            f"- Checker failures: `{summary['checkerFailCount']}`",
            f"- All expected rows matched: `{summary['allExpectedRowsMatched']}`",
            f"- Source parse performed: `{not summary['allSourceParseNotPerformed']}`",
            f"- Source re-emission performed: `{not summary['allSourceReemissionNotPerformed']}`",
            f"- Preservation oracle run: `{not summary['allPreservationOracleNotRun']}`",
            f"- Source fidelity validated: `{not summary['allSourceFidelityNotValidated']}`",
            f"- Source-preserving support claim: `{summary['sourcePreservingRoundtripSupportClaim']}`",
            "",
            "## Checker Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Stored-source-sketch checker only; no source parser or re-emitter execution.",
            "- No preservation oracle or fidelity validation claim.",
            "- No source-preserving roundtrip support claim.",
            "- No frontend lowering change.",
            "- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_checker_row(row: dict[str, Any]) -> None:
    if row["checkStatus"] not in {"pass", "fail"}:
        raise ValueError("invalid check status")
    for key in [
        "sourceParsePerformed",
        "sourceReemissionPerformed",
        "preservationOracleRun",
        "sourceFidelityValidated",
        "runtimeExecutionPerformed",
        "supportClaimAllowed",
    ]:
        if row[key] is not False:
            raise ValueError(f"{key} must remain false")
    if row["sourceSketchChecked"] is not True:
        raise ValueError("row must record source sketch check")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P123 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P123 status")
    p122.validate_payload(read_json(P122_RESULT))
    if payload["selectedFixture"]["id"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if len(payload["checkerRows"]) != 8:
        raise ValueError("expected exactly eight checker rows")
    for row in payload["checkerRows"]:
        validate_checker_row(row)
    summary = payload["summary"]
    for key in [
        "p122ValidationPass",
        "p122ClaimFlagsAllFalse",
        "p122ImplementationHeldPendingReview",
        "selectedFixtureStillBlocked",
        "allExpectedRowsMatched",
        "allRowsSourceSketchChecked",
        "allSourceParseNotPerformed",
        "allSourceReemissionNotPerformed",
        "allPreservationOracleNotRun",
        "allSourceFidelityNotValidated",
        "allRuntimeExecutionNotPerformed",
        "allSupportClaimsBlocked",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["p122ReviewerDecisionRecorded"] is not False:
        raise ValueError("P122 reviewer decision must remain not recorded")
    if summary["checkerRowCount"] != 8 or summary["checkerPassCount"] != 8 or summary["checkerFailCount"] != 0:
        raise ValueError("unexpected checker counts")
    for key in [
        "sourcePreservingExpectedRowCheckerClaim",
        "sourcePreservingExpectedRowsClaim",
        "sourcePreservingRoundtripSupportClaim",
        "sourceParseExecutionClaim",
        "sourceReemissionClaim",
        "sourceFidelityClaim",
        "sourceFidelityValidationClaim",
        "preservationOracleClaim",
        "nonGeneratedSourceRoundtripClaim",
        "compoundConditionSupportClaim",
        "loopBackedgeSupportClaim",
        "assignmentPhiSupportClaim",
        "sideEffectMemorySupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "frontendLoweringChanged",
        "unsupportedConstructsSupported",
        "generalBranchControlFlowClaim",
        "branchControlFlowReingestClaim",
        "fullNonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "arbitrarySourceFamilyClaim",
        "reviewerDecisionRecorded",
        "implementationChangeApproved",
        "implementationChangeApplied",
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "productionReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flags must remain false")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p123_source_preserving_expected_row_checker_{STAMP}.json"
    report_path = report_dir / f"fef_p123_source_preserving_expected_row_checker_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p123_source_preserving_expected_row_checker.json"
    feed_path = command_feed_dir / f"fef_p123_source_preserving_expected_row_checker_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p123_source_preserving_expected_row_checker")
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
    print("FEF_P123_SOURCE_PRESERVING_EXPECTED_ROW_CHECKER_OK")
    print(f"selected_fixture={built['payload']['summary']['selectedFixtureId']}")
    print(f"checker_passes={built['payload']['summary']['checkerPassCount']}")
    print(f"source_parse_performed={not built['payload']['summary']['allSourceParseNotPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
