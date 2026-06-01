#!/usr/bin/env python3
"""FEF-P122 expected preservation rows for one source-preserving fixture."""

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

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p122_source_preserving_expected_rows.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P122_SOURCE_PRESERVING_EXPECTED_ROWS_PASS"

P121_PACKET = ROOT / "reports/evidence_packets/fef_p121_source_preserving_roundtrip_fixture_gate.json"
P121_RESULT = ROOT / "python/results/fef_p121_source_preserving_roundtrip_fixture_gate/fef_p121_source_preserving_roundtrip_fixture_gate_2026_06_01.json"
SELECTED_FIXTURE_ID = "c_if_else_source_layout_v0"

CLAIM_FLAGS = {
    "source_preserving_expected_rows_claim": False,
    "source_preserving_roundtrip_fixture_gate_claim": False,
    "source_preserving_roundtrip_support_claim": False,
    "source_parse_execution_claim": False,
    "source_reemission_claim": False,
    "source_fidelity_claim": False,
    "source_fidelity_validation_claim": False,
    "local_preservation_oracle_claim": False,
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
    "FEF-P122 records expected preservation rows for one selected source-preserving fixture only.",
    "FEF-P122 does not parse non-generated source.",
    "FEF-P122 does not re-emit non-generated source.",
    "FEF-P122 does not run a preservation oracle or fidelity checker.",
    "FEF-P122 does not execute source, generated, or re-ingested code.",
    "FEF-P122 does not validate token, whitespace, comment, formatting, or source-layout fidelity.",
    "FEF-P122 does not implement source-preserving roundtrip support.",
    "FEF-P122 does not widen Forge or eFrog frontend lowering.",
    "FEF-P122 preserves the P120/P121 private review hold boundary.",
    "FEF-P122 does not record reviewer approval or rejection.",
    "FEF-P122 does not claim general branch/control-flow support.",
    "FEF-P122 does not claim full non-generated source roundtrip.",
    "FEF-P122 does not claim arbitrary C/Rust source-family support.",
    "FEF-P122 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P122 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

EXPECTED_ROWS = [
    {
        "id": "has_block_comment",
        "category": "comment",
        "expectedKind": "presence",
        "expectedValue": True,
        "sourceSlice": "/* clamp */",
        "rationale": "The selected source fixture carries a leading block comment that a source-preserving path would need to account for.",
    },
    {
        "id": "comment_text_clamp",
        "category": "comment",
        "expectedKind": "exact_text",
        "expectedValue": "/* clamp */",
        "sourceSlice": "/* clamp */",
        "rationale": "The exact block-comment text is part of the expected preservation surface.",
    },
    {
        "id": "if_before_else_order",
        "category": "token_order",
        "expectedKind": "relative_order",
        "expectedValue": ["if", "else"],
        "sourceSlice": "if (x < lo) ... else",
        "rationale": "The branch token order should remain explicit before any source-preserving support claim.",
    },
    {
        "id": "brace_layout_multiline",
        "category": "layout",
        "expectedKind": "multiline_brace_layout",
        "expectedValue": {
            "ifOpeningBraceLine": "if (x < lo) {",
            "elseOpeningBraceLine": "} else {",
            "closingBraceLine": "}",
        },
        "sourceSlice": "if (x < lo) {\n  return lo;\n} else {\n  return x;\n}",
        "rationale": "The fixture is intentionally format-sensitive around braces and the else boundary.",
    },
    {
        "id": "return_lo_path",
        "category": "return_path",
        "expectedKind": "exact_statement",
        "expectedValue": "return lo;",
        "sourceSlice": "return lo;",
        "rationale": "The low-clamp return path must be named as an expected source-preservation fact.",
    },
    {
        "id": "return_x_path",
        "category": "return_path",
        "expectedKind": "exact_statement",
        "expectedValue": "return x;",
        "sourceSlice": "return x;",
        "rationale": "The fallthrough-style else return path must be named as an expected source-preservation fact.",
    },
    {
        "id": "else_token_present",
        "category": "token_presence",
        "expectedKind": "presence",
        "expectedValue": True,
        "sourceSlice": "} else {",
        "rationale": "The selected fixture uses explicit if/else source shape, not a lowered selector-only source shape.",
    },
    {
        "id": "line_count",
        "category": "layout",
        "expectedKind": "line_count",
        "expectedValue": 6,
        "sourceSlice": "/* clamp */ ... }",
        "rationale": "The six-line source sketch gives a bounded expected layout surface for a later checker.",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_fixture(p121_result: dict[str, Any]) -> dict[str, Any]:
    for row in p121_result["fixtureMatrix"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def expected_preservation_rows() -> list[dict[str, Any]]:
    rows = []
    for row in EXPECTED_ROWS:
        rows.append(
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
        )
    return rows


def category_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    return dict(sorted(counts.items()))


def build_summary(p121_packet: dict[str, Any], p121_payload: dict[str, Any], fixture: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = category_counts(rows)
    return {
        "sourcePacketCount": 1,
        "p121ValidationPass": p121_packet["validationStatus"] == "pass",
        "p121ClaimFlagsAllFalse": all(value is False for value in p121_packet["claimFlags"].values()),
        "p121FixtureCount": p121_payload["summary"]["fixtureCount"],
        "p121ReviewerDecisionRecorded": p121_payload["summary"]["reviewerDecisionRecorded"],
        "p121ImplementationHeldPendingReview": p121_payload["summary"]["p120ImplementationHeldPendingReview"],
        "selectedFixtureId": fixture["id"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "selectedFixtureLanguage": fixture["sourceLanguage"],
        "selectedFixtureShape": fixture["shape"],
        "expectedRowCount": len(rows),
        "categoryCounts": counts,
        "commentExpectationCount": counts.get("comment", 0),
        "layoutExpectationCount": counts.get("layout", 0),
        "tokenExpectationCount": counts.get("token_order", 0) + counts.get("token_presence", 0),
        "returnPathExpectationCount": counts.get("return_path", 0),
        "allRowsSourceSemanticsOnly": all(row["sourceSemanticsOnly"] is True for row in rows),
        "allSourceParseNotPerformed": all(row["sourceParsePerformed"] is False for row in rows),
        "allSourceReemissionNotPerformed": all(row["sourceReemissionPerformed"] is False for row in rows),
        "allPreservationOracleNotRun": all(row["preservationOracleRun"] is False for row in rows),
        "allSourceFidelityNotValidated": all(row["sourceFidelityValidated"] is False for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "allSupportClaimsBlocked": all(row["supportClaimAllowed"] is False for row in rows),
        "sourcePreservingExpectedRowsClaim": False,
        "sourcePreservingRoundtripSupportClaim": False,
        "sourceParseExecutionClaim": False,
        "sourceReemissionClaim": False,
        "sourceFidelityClaim": False,
        "sourceFidelityValidationClaim": False,
        "localPreservationOracleClaim": False,
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
    p121_packet = read_json(P121_PACKET)
    p121_payload = read_json(P121_RESULT)
    p121.validate_payload(p121_payload)
    fixture = selected_fixture(p121_payload)
    rows = expected_preservation_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p122-source-preserving-expected-rows",
        "decision": "source_preserving_expected_rows_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P121",
            "packetPath": str(P121_PACKET.relative_to(ROOT)),
            "resultPath": str(P121_RESULT.relative_to(ROOT)),
            "reviewDecision": p121_packet["reviewDecision"],
            "validationStatus": p121_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedPreservationRows": rows,
        "summary": build_summary(p121_packet, p121_payload, fixture, rows),
        "releaseGates": [
            {"id": "source_preserving_expected_rows", "status": "recorded"},
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
            "P122 records expected preservation rows for the selected c_if_else_source_layout_v0 fixture.",
            "P122 gives a later checker explicit comment, token-order, layout, return-path, and line-count expectations.",
            "P122 keeps source parsing, source re-emission, preservation-oracle execution, and source fidelity validation blocked.",
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
            "Build a local preservation oracle/checker over the P122 expected rows without claiming source re-emission.",
            "Record actual private reviewer response to P47-P122 if one exists.",
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
        "title": "FEF-P122 Source-Preserving Expected Rows",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "source_preserving_expected_rows_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected preservation rows only; no source parsing, source re-emission, preservation-oracle execution, token/comment/layout fidelity validation, source-preserving support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P122 selects c_if_else_source_layout_v0 from the P121 fixture gate.",
            "Eight expected preservation rows cover comments, token order, layout, return paths, and line count.",
            "No source parse, source re-emission, preservation oracle, or fidelity validation is performed.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p122_source_preserving_expected_rows.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p122_source_preserving_expected_rows.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p122_source_preserving_expected_rows.v0",
        "date": DATE,
        "title": "FEF-P122 Source-Preserving Expected Rows",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Build a local preservation oracle/checker over expected rows without source re-emission.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Row | Category | Expected kind | Source parse | Fidelity validated |", "|---|---|---|---|---|"]
    for row in payload["expectedPreservationRows"]:
        rows.append(
            f"| `{row['id']}` | `{row['category']}` | `{row['expectedKind']}` | `{row['sourceParsePerformed']}` | `{row['sourceFidelityValidated']}` |"
        )
    return "\n".join(
        [
            "# FEF-P122 Source-Preserving Expected Rows",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P122 records expected preservation rows for one selected source-preserving fixture.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Expected rows: `{summary['expectedRowCount']}`",
            f"- Comment expectations: `{summary['commentExpectationCount']}`",
            f"- Layout expectations: `{summary['layoutExpectationCount']}`",
            f"- Token expectations: `{summary['tokenExpectationCount']}`",
            f"- Return-path expectations: `{summary['returnPathExpectationCount']}`",
            f"- Source parse performed: `{not summary['allSourceParseNotPerformed']}`",
            f"- Source re-emission performed: `{not summary['allSourceReemissionNotPerformed']}`",
            f"- Preservation oracle run: `{not summary['allPreservationOracleNotRun']}`",
            f"- Source fidelity validated: `{not summary['allSourceFidelityNotValidated']}`",
            f"- Source-preserving support claim: `{summary['sourcePreservingRoundtripSupportClaim']}`",
            "",
            "## Expected Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Expected-row metadata only; no source parser or re-emitter execution.",
            "- No preservation oracle or fidelity validation claim.",
            "- No source-preserving roundtrip support claim.",
            "- No frontend lowering change.",
            "- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_row(row: dict[str, Any]) -> None:
    if row["selectedFixtureId"] != SELECTED_FIXTURE_ID:
        raise ValueError("row fixture id mismatch")
    if not row["id"] or not row["category"] or not row["expectedKind"]:
        raise ValueError("row must carry id, category, and expected kind")
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
    if row["sourceSemanticsOnly"] is not True:
        raise ValueError("row must remain source semantics only")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P122 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P122 status")
    p121.validate_payload(read_json(P121_RESULT))
    if payload["selectedFixture"]["id"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if len(payload["expectedPreservationRows"]) != 8:
        raise ValueError("expected exactly eight preservation rows")
    for row in payload["expectedPreservationRows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p121ValidationPass",
        "p121ClaimFlagsAllFalse",
        "p121ImplementationHeldPendingReview",
        "selectedFixtureStillBlocked",
        "allRowsSourceSemanticsOnly",
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
    if summary["p121ReviewerDecisionRecorded"] is not False:
        raise ValueError("P121 reviewer decision must remain not recorded")
    if summary["expectedRowCount"] != 8:
        raise ValueError("unexpected expected-row count")
    if summary["commentExpectationCount"] != 2 or summary["layoutExpectationCount"] != 2:
        raise ValueError("unexpected preservation category counts")
    if summary["tokenExpectationCount"] != 2 or summary["returnPathExpectationCount"] != 2:
        raise ValueError("unexpected token/return category counts")
    for key in [
        "sourcePreservingExpectedRowsClaim",
        "sourcePreservingRoundtripSupportClaim",
        "sourceParseExecutionClaim",
        "sourceReemissionClaim",
        "sourceFidelityClaim",
        "sourceFidelityValidationClaim",
        "localPreservationOracleClaim",
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
    result_path = out_dir / f"fef_p122_source_preserving_expected_rows_{STAMP}.json"
    report_path = report_dir / f"fef_p122_source_preserving_expected_rows_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p122_source_preserving_expected_rows.json"
    feed_path = command_feed_dir / f"fef_p122_source_preserving_expected_rows_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p122_source_preserving_expected_rows")
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
    print("FEF_P122_SOURCE_PRESERVING_EXPECTED_ROWS_OK")
    print(f"selected_fixture={built['payload']['summary']['selectedFixtureId']}")
    print(f"expected_rows={built['payload']['summary']['expectedRowCount']}")
    print(f"source_parse_performed={not built['payload']['summary']['allSourceParseNotPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
