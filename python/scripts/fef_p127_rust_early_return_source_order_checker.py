#!/usr/bin/env python3
"""FEF-P127 Rust early-return source-order expected rows and checker."""

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

from scripts import fef_p121_source_preserving_roundtrip_fixture_gate as p121  # noqa: E402
from scripts import fef_p126_rust_source_preserving_fixture_checker as p126  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p127_rust_early_return_source_order_checker.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P127_RUST_EARLY_RETURN_SOURCE_ORDER_CHECKER_PASS"

P121_RESULT = ROOT / "python/results/fef_p121_source_preserving_roundtrip_fixture_gate/fef_p121_source_preserving_roundtrip_fixture_gate_2026_06_01.json"
P126_PACKET = ROOT / "reports/evidence_packets/fef_p126_rust_source_preserving_fixture_checker.json"
P126_RESULT = ROOT / "python/results/fef_p126_rust_source_preserving_fixture_checker/fef_p126_rust_source_preserving_fixture_checker_2026_06_01.json"
SELECTED_FIXTURE_ID = "rust_early_return_source_order_v0"

CLAIM_FLAGS = {
    "rust_early_return_source_order_checker_claim": False,
    "rust_source_preserving_fixture_checker_claim": False,
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
    "FEF-P127 records expected rows, checker rows, and negative controls for one Rust early-return fixture only.",
    "FEF-P127 does not parse non-generated Rust source.",
    "FEF-P127 does not re-emit non-generated Rust source.",
    "FEF-P127 does not run a preservation oracle.",
    "FEF-P127 does not execute source, generated, or re-ingested code.",
    "FEF-P127 does not validate token, whitespace, comment, formatting, or source-layout fidelity.",
    "FEF-P127 does not implement source-preserving roundtrip support.",
    "FEF-P127 does not widen Forge or eFrog frontend lowering.",
    "FEF-P127 preserves the P120-P126 private review hold boundary.",
    "FEF-P127 does not record reviewer approval or rejection.",
    "FEF-P127 does not claim general branch/control-flow support.",
    "FEF-P127 does not claim full non-generated source roundtrip.",
    "FEF-P127 does not claim arbitrary C/Rust source-family support.",
    "FEF-P127 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P127 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

EXPECTED_ROWS = [
    {"id": "if_guard_open_line", "category": "layout", "expectedKind": "exact_line_strict", "expectedValue": "if x < lo {", "rationale": "The early-return guard line anchors the source-order fixture."},
    {"id": "return_lo_statement", "category": "return_path", "expectedKind": "exact_line_strict", "expectedValue": "    return lo;", "rationale": "The early return statement must stay visible in the source sketch."},
    {"id": "guard_closing_brace", "category": "layout", "expectedKind": "exact_line_strict", "expectedValue": "}", "rationale": "The closing brace separates the guard from fallthrough source."},
    {"id": "fallthrough_comment", "category": "comment", "expectedKind": "exact_line_strict", "expectedValue": "// fall through", "rationale": "The fallthrough comment is an explicit source-preservation feature."},
    {"id": "fallthrough_tail_expr", "category": "expression_tail", "expectedKind": "exact_line_strict", "expectedValue": "x", "rationale": "The final line is a Rust tail expression, not a return statement."},
    {"id": "return_before_fallthrough_order", "category": "token_order", "expectedKind": "relative_order", "expectedValue": ["return lo;", "// fall through", "\nx"], "rationale": "The early return must precede the fallthrough comment and final tail expression."},
    {"id": "else_token_absent", "category": "token_absence", "expectedKind": "absence", "expectedValue": "else", "rationale": "The selected fixture is early return plus fallthrough, not explicit else."},
    {"id": "line_count", "category": "layout", "expectedKind": "line_count", "expectedValue": 5, "rationale": "The five-line sketch bounds the expected Rust source order surface."},
]

NEGATIVE_CONTROLS = [
    {
        "id": "missing_fallthrough_comment_negative_control_v0",
        "mutation": "remove_fallthrough_comment",
        "sourceSketch": "if x < lo {\n    return lo;\n}\nx",
        "expectedFailedRows": ["fallthrough_comment", "return_before_fallthrough_order", "line_count"],
    },
    {
        "id": "changed_return_negative_control_v0",
        "mutation": "change_early_return_statement",
        "sourceSketch": "if x < lo {\n    return low;\n}\n// fall through\nx",
        "expectedFailedRows": ["return_lo_statement", "return_before_fallthrough_order"],
    },
    {
        "id": "else_inserted_negative_control_v0",
        "mutation": "insert_else_branch",
        "sourceSketch": "if x < lo {\n    return lo;\n} else {\n    x\n}",
        "expectedFailedRows": ["fallthrough_comment", "fallthrough_tail_expr", "return_before_fallthrough_order", "else_token_absent"],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_fixture(p121_payload: dict[str, Any]) -> dict[str, Any]:
    for row in p121_payload["fixtureMatrix"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def expected_rows() -> list[dict[str, Any]]:
    return [
        {
            **copy.deepcopy(row),
            "selectedFixtureId": SELECTED_FIXTURE_ID,
            "sourceSemanticsOnly": True,
            "sourceParsePerformed": False,
            "sourceReemissionPerformed": False,
            "preservationOracleRun": False,
            "sourceFidelityValidated": False,
            "runtimeExecutionPerformed": False,
            "supportClaimAllowed": False,
        }
        for row in EXPECTED_ROWS
    ]


def check_row(source: str, row: dict[str, Any]) -> dict[str, Any]:
    lines = source.splitlines()
    kind = row["expectedKind"]
    if kind == "exact_line_strict":
        matched = row["expectedValue"] in lines
    elif kind == "relative_order":
        position = -1
        matched = True
        for token in row["expectedValue"]:
            next_position = source.find(token, position + 1)
            if next_position < 0:
                matched = False
                break
            position = next_position
    elif kind == "absence":
        matched = row["expectedValue"] not in source
    elif kind == "line_count":
        matched = len(lines) == row["expectedValue"]
    else:
        raise ValueError(f"unknown expected kind: {kind}")
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


def evaluate_control(control: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    checked_rows = checker_rows(control["sourceSketch"], rows)
    failed_rows = [row["rowId"] for row in checked_rows if row["checkStatus"] == "fail"]
    passed_rows = [row["rowId"] for row in checked_rows if row["checkStatus"] == "pass"]
    return {
        **copy.deepcopy(control),
        "selectedFixtureId": SELECTED_FIXTURE_ID,
        "checkerRows": checked_rows,
        "passedRows": passed_rows,
        "failedRows": failed_rows,
        "expectedFailedRowsMatched": failed_rows == control["expectedFailedRows"],
        "failClosed": len(failed_rows) > 0,
        "sourceSketchChecked": True,
        "sourceParsePerformed": False,
        "sourceReemissionPerformed": False,
        "preservationOracleRun": False,
        "sourceFidelityValidated": False,
        "runtimeExecutionPerformed": False,
        "supportClaimAllowed": False,
    }


def negative_control_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [evaluate_control(control, rows) for control in NEGATIVE_CONTROLS]


def false_summary_flags() -> dict[str, bool]:
    return {key: False for key in [
        "rustEarlyReturnSourceOrderCheckerClaim",
        "rustSourcePreservingFixtureCheckerClaim",
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
    ]}


def category_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    return dict(sorted(counts.items()))


def build_summary(p126_packet: dict[str, Any], p126_payload: dict[str, Any], fixture: dict[str, Any], rows: list[dict[str, Any]], checks: list[dict[str, Any]], controls: list[dict[str, Any]]) -> dict[str, Any]:
    check_passes = sum(1 for row in checks if row["checkStatus"] == "pass")
    control_failures = sum(len(control["failedRows"]) for control in controls)
    control_passes = sum(len(control["passedRows"]) for control in controls)
    return {
        "sourcePacketCount": 1,
        "p126ValidationPass": p126_packet["validationStatus"] == "pass",
        "p126ClaimFlagsAllFalse": all(value is False for value in p126_packet["claimFlags"].values()),
        "p126CheckerPassCount": p126_payload["summary"]["checkerPassCount"],
        "p126ReviewerDecisionRecorded": p126_payload["summary"]["reviewerDecisionRecorded"],
        "p126ImplementationHeldPendingReview": p126_payload["summary"]["p125ImplementationHeldPendingReview"],
        "selectedFixtureId": fixture["id"],
        "selectedFixtureLanguage": fixture["sourceLanguage"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "expectedRowCount": len(rows),
        "categoryCounts": category_counts(rows),
        "checkerRowCount": len(checks),
        "checkerPassCount": check_passes,
        "checkerFailCount": len(checks) - check_passes,
        "allExpectedRowsMatched": check_passes == len(checks),
        "negativeControlCount": len(controls),
        "negativeControlRowCheckCount": sum(len(control["checkerRows"]) for control in controls),
        "negativeControlExpectedFailureCount": control_failures,
        "negativeControlPassRowCount": control_passes,
        "allNegativeControlsFailClosed": all(control["failClosed"] is True for control in controls),
        "allExpectedFailuresMatched": all(control["expectedFailedRowsMatched"] is True for control in controls),
        "allRowsSourceSketchChecked": all(row["sourceSketchChecked"] is True for row in checks) and all(control["sourceSketchChecked"] is True for control in controls),
        "allSourceParseNotPerformed": all(row["sourceParsePerformed"] is False for row in checks) and all(control["sourceParsePerformed"] is False for control in controls),
        "allSourceReemissionNotPerformed": all(row["sourceReemissionPerformed"] is False for row in checks) and all(control["sourceReemissionPerformed"] is False for control in controls),
        "allPreservationOracleNotRun": all(row["preservationOracleRun"] is False for row in checks) and all(control["preservationOracleRun"] is False for control in controls),
        "allSourceFidelityNotValidated": all(row["sourceFidelityValidated"] is False for row in checks) and all(control["sourceFidelityValidated"] is False for control in controls),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in checks) and all(control["runtimeExecutionPerformed"] is False for control in controls),
        "allSupportClaimsBlocked": all(row["supportClaimAllowed"] is False for row in checks) and all(control["supportClaimAllowed"] is False for control in controls),
        **false_summary_flags(),
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p121_payload = read_json(P121_RESULT)
    p121.validate_payload(p121_payload)
    p126_packet = read_json(P126_PACKET)
    p126_payload = read_json(P126_RESULT)
    p126.validate_payload(p126_payload)
    fixture = selected_fixture(p121_payload)
    rows = expected_rows()
    checks = checker_rows(fixture["sourceSketch"], rows)
    controls = negative_control_results(rows)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p127-rust-early-return-source-order-checker",
        "decision": "rust_early_return_source_order_expected_rows_checker_negative_controls_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P126",
            "packetPath": str(P126_PACKET.relative_to(ROOT)),
            "resultPath": str(P126_RESULT.relative_to(ROOT)),
            "reviewDecision": p126_packet["reviewDecision"],
            "validationStatus": p126_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedRows": rows,
        "checkerRows": checks,
        "negativeControls": controls,
        "summary": build_summary(p126_packet, p126_payload, fixture, rows, checks, controls),
        "releaseGates": [
            {"id": "rust_early_return_source_order_checker", "status": "recorded"},
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
            "P127 records expected rows, checker rows, and negative controls for rust_early_return_source_order_v0.",
            "P127 matches all eight expected rows and all three negative controls fail closed.",
            "P127 keeps source parsing, source re-emission, preservation-oracle execution, and source fidelity validation blocked.",
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
            "Package the P121-P127 source-preserving fixture discipline as a private reviewer handoff hold.",
            "Record actual private reviewer response to P47-P127 if one exists.",
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
        "title": "FEF-P127 Rust Early-Return Source-Order Checker",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "rust_early_return_source_order_checker_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Rust early-return source-order expected rows/checker/negative controls only; no source parsing, source re-emission, preservation-oracle execution, token/comment/layout fidelity validation, source-preserving support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P127 selects rust_early_return_source_order_v0 as the Rust early-return source-order lane.",
            "Eight expected rows pass against the stored Rust source sketch.",
            "Three negative controls fail closed with expected failed rows.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p127_rust_early_return_source_order_checker.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p127_rust_early_return_source_order_checker.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p127_rust_early_return_source_order_checker.v0",
        "date": DATE,
        "title": "FEF-P127 Rust Early-Return Source-Order Checker",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Package P121-P127 as a private reviewer handoff hold for the source-preserving ladder.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Row | Category | Status |", "|---|---|---|"]
    for row in payload["checkerRows"]:
        rows.append(f"| `{row['rowId']}` | `{row['category']}` | `{row['checkStatus']}` |")
    controls = ["| Control | Failed rows | Fail closed |", "|---|---:|---|"]
    for control in payload["negativeControls"]:
        controls.append(f"| `{control['id']}` | {len(control['failedRows'])} | `{control['failClosed']}` |")
    return "\n".join([
        "# FEF-P127 Rust Early-Return Source-Order Checker",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P127 applies the source-preserving checker discipline to a Rust early-return/fallthrough fixture.",
        "",
        "## Summary",
        "",
        f"- Selected fixture: `{summary['selectedFixtureId']}`",
        f"- Expected rows: `{summary['expectedRowCount']}`",
        f"- Checker passes: `{summary['checkerPassCount']}`",
        f"- Checker failures: `{summary['checkerFailCount']}`",
        f"- Negative controls: `{summary['negativeControlCount']}`",
        f"- Negative-control expected failures: `{summary['negativeControlExpectedFailureCount']}`",
        f"- All negative controls fail closed: `{summary['allNegativeControlsFailClosed']}`",
        f"- Source parse performed: `{not summary['allSourceParseNotPerformed']}`",
        f"- Source re-emission performed: `{not summary['allSourceReemissionNotPerformed']}`",
        f"- Source fidelity validated: `{not summary['allSourceFidelityNotValidated']}`",
        f"- Source-preserving support claim: `{summary['sourcePreservingRoundtripSupportClaim']}`",
        "",
        "## Checker Rows",
        "",
        *rows,
        "",
        "## Negative Controls",
        "",
        *controls,
        "",
        "## Boundary",
        "",
        "- Source-sketch checks only; no source parser or re-emitter execution.",
        "- No preservation oracle or fidelity validation claim.",
        "- No source-preserving roundtrip support claim.",
        "- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.",
        "",
    ])


def validate_checked_row(row: dict[str, Any]) -> None:
    for key in ["sourceParsePerformed", "sourceReemissionPerformed", "preservationOracleRun", "sourceFidelityValidated", "runtimeExecutionPerformed", "supportClaimAllowed"]:
        if row[key] is not False:
            raise ValueError(f"{key} must remain false")
    if row["sourceSketchChecked"] is not True:
        raise ValueError("source sketch must be checked")


def validate_control(control: dict[str, Any]) -> None:
    if control["failClosed"] is not True or control["expectedFailedRowsMatched"] is not True:
        raise ValueError("negative control must fail closed with expected rows")
    for row in control["checkerRows"]:
        validate_checked_row(row)
    for key in ["sourceParsePerformed", "sourceReemissionPerformed", "preservationOracleRun", "sourceFidelityValidated", "runtimeExecutionPerformed", "supportClaimAllowed"]:
        if control[key] is not False:
            raise ValueError(f"{key} must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P127 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P127 status")
    p126.validate_payload(read_json(P126_RESULT))
    if payload["selectedFixture"]["id"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if len(payload["expectedRows"]) != 8 or len(payload["checkerRows"]) != 8:
        raise ValueError("expected eight rows")
    if len(payload["negativeControls"]) != 3:
        raise ValueError("expected three negative controls")
    for row in payload["checkerRows"]:
        validate_checked_row(row)
    for control in payload["negativeControls"]:
        validate_control(control)
    summary = payload["summary"]
    for key in [
        "p126ValidationPass",
        "p126ClaimFlagsAllFalse",
        "p126ImplementationHeldPendingReview",
        "selectedFixtureStillBlocked",
        "allExpectedRowsMatched",
        "allNegativeControlsFailClosed",
        "allExpectedFailuresMatched",
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
    if summary["p126ReviewerDecisionRecorded"] is not False:
        raise ValueError("P126 reviewer decision must remain not recorded")
    if summary["selectedFixtureLanguage"] != "rust":
        raise ValueError("selected fixture must be Rust")
    if summary["checkerPassCount"] != 8 or summary["checkerFailCount"] != 0:
        raise ValueError("unexpected checker counts")
    if summary["negativeControlCount"] != 3 or summary["negativeControlRowCheckCount"] != 24:
        raise ValueError("unexpected negative-control counts")
    if summary["negativeControlExpectedFailureCount"] != 9 or summary["negativeControlPassRowCount"] != 15:
        raise ValueError("unexpected negative-control pass/fail counts")
    for key, value in false_summary_flags().items():
        if summary[key] is not value:
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
    result_path = out_dir / f"fef_p127_rust_early_return_source_order_checker_{STAMP}.json"
    report_path = report_dir / f"fef_p127_rust_early_return_source_order_checker_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p127_rust_early_return_source_order_checker.json"
    feed_path = command_feed_dir / f"fef_p127_rust_early_return_source_order_checker_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p127_rust_early_return_source_order_checker")
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
    print("FEF_P127_RUST_EARLY_RETURN_SOURCE_ORDER_CHECKER_OK")
    print(f"selected_fixture={built['payload']['summary']['selectedFixtureId']}")
    print(f"checker_passes={built['payload']['summary']['checkerPassCount']}")
    print(f"negative_controls={built['payload']['summary']['negativeControlCount']}")
    print(f"source_parse_performed={not built['payload']['summary']['allSourceParseNotPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
