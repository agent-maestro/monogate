#!/usr/bin/env python3
"""FEF-P124 negative-control checker for source-preserving expected rows."""

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
from scripts import fef_p123_source_preserving_expected_row_checker as p123  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p124_source_preserving_negative_control_checker.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P124_SOURCE_PRESERVING_NEGATIVE_CONTROL_CHECKER_PASS"

P123_PACKET = ROOT / "reports/evidence_packets/fef_p123_source_preserving_expected_row_checker.json"
P123_RESULT = ROOT / "python/results/fef_p123_source_preserving_expected_row_checker/fef_p123_source_preserving_expected_row_checker_2026_06_01.json"
SELECTED_FIXTURE_ID = p122.SELECTED_FIXTURE_ID

CLAIM_FLAGS = {
    "source_preserving_negative_control_checker_claim": False,
    "source_preserving_expected_row_checker_claim": False,
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
    "FEF-P124 runs negative controls against the P123 expected-row checker only.",
    "FEF-P124 does not parse non-generated source.",
    "FEF-P124 does not re-emit non-generated source.",
    "FEF-P124 does not run a preservation oracle.",
    "FEF-P124 does not execute source, generated, or re-ingested code.",
    "FEF-P124 does not validate token, whitespace, comment, formatting, or source-layout fidelity.",
    "FEF-P124 does not implement source-preserving roundtrip support.",
    "FEF-P124 does not widen Forge or eFrog frontend lowering.",
    "FEF-P124 preserves the P120/P121/P122/P123 private review hold boundary.",
    "FEF-P124 does not record reviewer approval or rejection.",
    "FEF-P124 does not claim general branch/control-flow support.",
    "FEF-P124 does not claim full non-generated source roundtrip.",
    "FEF-P124 does not claim arbitrary C/Rust source-family support.",
    "FEF-P124 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P124 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

NEGATIVE_CONTROLS = [
    {
        "id": "missing_comment_negative_control_v0",
        "mutation": "remove_leading_block_comment",
        "sourceSketch": "if (x < lo) {\n  return lo;\n} else {\n  return x;\n}",
        "expectedFailedRows": ["has_block_comment", "comment_text_clamp", "line_count"],
    },
    {
        "id": "missing_else_negative_control_v0",
        "mutation": "remove_else_token_and_block_layout",
        "sourceSketch": "/* clamp */\nif (x < lo) {\n  return lo;\n}\nreturn x;",
        "expectedFailedRows": ["if_before_else_order", "brace_layout_multiline", "else_token_present", "line_count"],
    },
    {
        "id": "changed_return_path_negative_control_v0",
        "mutation": "change_low_return_statement",
        "sourceSketch": "/* clamp */\nif (x < lo) {\n  return low;\n} else {\n  return x;\n}",
        "expectedFailedRows": ["return_lo_path"],
    },
    {
        "id": "single_line_layout_negative_control_v0",
        "mutation": "collapse_multiline_layout",
        "sourceSketch": "/* clamp */\nif (x < lo) { return lo; } else { return x; }",
        "expectedFailedRows": ["brace_layout_multiline", "return_lo_path", "return_x_path", "line_count"],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_control(control: dict[str, Any], expected_rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = p123.checker_rows(control["sourceSketch"], expected_rows)
    failed_rows = [row["rowId"] for row in rows if row["checkStatus"] == "fail"]
    passed_rows = [row["rowId"] for row in rows if row["checkStatus"] == "pass"]
    return {
        **copy.deepcopy(control),
        "selectedFixtureId": SELECTED_FIXTURE_ID,
        "checkerRows": rows,
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


def negative_control_results() -> list[dict[str, Any]]:
    return [evaluate_control(control, p122.expected_preservation_rows()) for control in NEGATIVE_CONTROLS]


def build_summary(p123_packet: dict[str, Any], p123_payload: dict[str, Any], controls: list[dict[str, Any]]) -> dict[str, Any]:
    total_rows = sum(len(control["checkerRows"]) for control in controls)
    total_failures = sum(len(control["failedRows"]) for control in controls)
    total_passes = sum(len(control["passedRows"]) for control in controls)
    return {
        "sourcePacketCount": 1,
        "p123ValidationPass": p123_packet["validationStatus"] == "pass",
        "p123ClaimFlagsAllFalse": all(value is False for value in p123_packet["claimFlags"].values()),
        "p123CheckerPassCount": p123_payload["summary"]["checkerPassCount"],
        "p123ReviewerDecisionRecorded": p123_payload["summary"]["reviewerDecisionRecorded"],
        "p123ImplementationHeldPendingReview": p123_payload["summary"]["p122ImplementationHeldPendingReview"],
        "selectedFixtureId": p123_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p123_payload["summary"]["selectedFixtureStillBlocked"],
        "negativeControlCount": len(controls),
        "negativeControlRowCheckCount": total_rows,
        "negativeControlExpectedFailureCount": total_failures,
        "negativeControlPassRowCount": total_passes,
        "allNegativeControlsFailClosed": all(control["failClosed"] is True for control in controls),
        "allExpectedFailuresMatched": all(control["expectedFailedRowsMatched"] is True for control in controls),
        "allRowsSourceSketchChecked": all(control["sourceSketchChecked"] is True for control in controls),
        "allSourceParseNotPerformed": all(control["sourceParsePerformed"] is False for control in controls),
        "allSourceReemissionNotPerformed": all(control["sourceReemissionPerformed"] is False for control in controls),
        "allPreservationOracleNotRun": all(control["preservationOracleRun"] is False for control in controls),
        "allSourceFidelityNotValidated": all(control["sourceFidelityValidated"] is False for control in controls),
        "allRuntimeExecutionNotPerformed": all(control["runtimeExecutionPerformed"] is False for control in controls),
        "allSupportClaimsBlocked": all(control["supportClaimAllowed"] is False for control in controls),
        "sourcePreservingNegativeControlCheckerClaim": False,
        "sourcePreservingExpectedRowCheckerClaim": False,
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
    p123_packet = read_json(P123_PACKET)
    p123_payload = read_json(P123_RESULT)
    p123.validate_payload(p123_payload)
    controls = negative_control_results()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p124-source-preserving-negative-control-checker",
        "decision": "source_preserving_negative_controls_fail_closed_support_blocked",
        "sourcePacket": {
            "phase": "P123",
            "packetPath": str(P123_PACKET.relative_to(ROOT)),
            "resultPath": str(P123_RESULT.relative_to(ROOT)),
            "reviewDecision": p123_packet["reviewDecision"],
            "validationStatus": p123_packet["validationStatus"],
        },
        "selectedFixtureId": SELECTED_FIXTURE_ID,
        "negativeControls": controls,
        "summary": build_summary(p123_packet, p123_payload, controls),
        "releaseGates": [
            {"id": "source_preserving_negative_controls", "status": "fail_closed_pass"},
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
            "P124 runs four negative controls against the P123 expected-row checker.",
            "Each negative control fails closed with the expected failed rows.",
            "P124 keeps source parsing, source re-emission, preservation-oracle execution, and source fidelity validation blocked.",
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
            "Add a second selected source-preserving fixture only as another expected-row/checker/negative-control lane.",
            "Record actual private reviewer response to P47-P124 if one exists.",
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
        "title": "FEF-P124 Source-Preserving Negative-Control Checker",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "source_preserving_negative_controls_fail_closed_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Negative controls over stored source sketches only; no source parsing, source re-emission, preservation-oracle execution, token/comment/layout fidelity validation, source-preserving support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P124 runs four negative controls against the P123 expected-row checker.",
            "All four negative controls fail closed with expected failed rows.",
            "No source parse, source re-emission, preservation oracle, or fidelity validation is performed.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p124_source_preserving_negative_control_checker.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p124_source_preserving_negative_control_checker.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p124_source_preserving_negative_control_checker.v0",
        "date": DATE,
        "title": "FEF-P124 Source-Preserving Negative-Control Checker",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add a second source-preserving fixture through the same expected-row/checker/negative-control discipline.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Control | Mutation | Failed rows | Fail closed |", "|---|---|---:|---|"]
    for control in payload["negativeControls"]:
        rows.append(
            f"| `{control['id']}` | `{control['mutation']}` | {len(control['failedRows'])} | `{control['failClosed']}` |"
        )
    return "\n".join(
        [
            "# FEF-P124 Source-Preserving Negative-Control Checker",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P124 runs negative controls against the P123 expected-row checker.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Negative controls: `{summary['negativeControlCount']}`",
            f"- Row checks: `{summary['negativeControlRowCheckCount']}`",
            f"- Expected failures: `{summary['negativeControlExpectedFailureCount']}`",
            f"- Passing rows inside controls: `{summary['negativeControlPassRowCount']}`",
            f"- All controls fail closed: `{summary['allNegativeControlsFailClosed']}`",
            f"- All expected failures matched: `{summary['allExpectedFailuresMatched']}`",
            f"- Source parse performed: `{not summary['allSourceParseNotPerformed']}`",
            f"- Source re-emission performed: `{not summary['allSourceReemissionNotPerformed']}`",
            f"- Preservation oracle run: `{not summary['allPreservationOracleNotRun']}`",
            f"- Source fidelity validated: `{not summary['allSourceFidelityNotValidated']}`",
            f"- Source-preserving support claim: `{summary['sourcePreservingRoundtripSupportClaim']}`",
            "",
            "## Negative Controls",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Negative-control source-sketch checks only; no source parser or re-emitter execution.",
            "- No preservation oracle or fidelity validation claim.",
            "- No source-preserving roundtrip support claim.",
            "- No frontend lowering change.",
            "- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_control(control: dict[str, Any]) -> None:
    if not control["failClosed"]:
        raise ValueError("negative control must fail closed")
    if control["failedRows"] != control["expectedFailedRows"]:
        raise ValueError("negative control failed rows must match expected failed rows")
    for row in control["checkerRows"]:
        p123.validate_checker_row(row)
    for key in [
        "sourceParsePerformed",
        "sourceReemissionPerformed",
        "preservationOracleRun",
        "sourceFidelityValidated",
        "runtimeExecutionPerformed",
        "supportClaimAllowed",
    ]:
        if control[key] is not False:
            raise ValueError(f"{key} must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P124 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P124 status")
    p123.validate_payload(read_json(P123_RESULT))
    if payload["selectedFixtureId"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if len(payload["negativeControls"]) != 4:
        raise ValueError("expected four negative controls")
    for control in payload["negativeControls"]:
        validate_control(control)
    summary = payload["summary"]
    for key in [
        "p123ValidationPass",
        "p123ClaimFlagsAllFalse",
        "p123ImplementationHeldPendingReview",
        "selectedFixtureStillBlocked",
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
    if summary["p123ReviewerDecisionRecorded"] is not False:
        raise ValueError("P123 reviewer decision must remain not recorded")
    if summary["negativeControlCount"] != 4 or summary["negativeControlRowCheckCount"] != 32:
        raise ValueError("unexpected negative-control counts")
    if summary["negativeControlExpectedFailureCount"] != 12 or summary["negativeControlPassRowCount"] != 20:
        raise ValueError("unexpected negative-control pass/fail counts")
    for key in [
        "sourcePreservingNegativeControlCheckerClaim",
        "sourcePreservingExpectedRowCheckerClaim",
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
    result_path = out_dir / f"fef_p124_source_preserving_negative_control_checker_{STAMP}.json"
    report_path = report_dir / f"fef_p124_source_preserving_negative_control_checker_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p124_source_preserving_negative_control_checker.json"
    feed_path = command_feed_dir / f"fef_p124_source_preserving_negative_control_checker_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p124_source_preserving_negative_control_checker")
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
    print("FEF_P124_SOURCE_PRESERVING_NEGATIVE_CONTROL_CHECKER_OK")
    print(f"negative_controls={built['payload']['summary']['negativeControlCount']}")
    print(f"expected_failures={built['payload']['summary']['negativeControlExpectedFailureCount']}")
    print(f"source_parse_performed={not built['payload']['summary']['allSourceParseNotPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
