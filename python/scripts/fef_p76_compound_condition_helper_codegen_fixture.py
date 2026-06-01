#!/usr/bin/env python3
"""FEF-P76 guarded helper/codegen fixture for the selected compound condition."""

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

from scripts import fef_p75_compound_condition_lowering_rule_packet as p75

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p76_compound_condition_helper_codegen_fixture.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P76_COMPOUND_CONDITION_HELPER_CODEGEN_FIXTURE_PASS"

P75_PACKET = ROOT / "reports/evidence_packets/fef_p75_compound_condition_lowering_rule_packet.json"
P75_RESULT = ROOT / "python/results/fef_p75_compound_condition_lowering_rule_packet/fef_p75_compound_condition_lowering_rule_packet_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_helper_codegen_fixture_claim": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_generated_target_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
    "guarded_division_runtime_helper_implemented": False,
    "nonzero_predicate_runtime_helper_implemented": False,
    "selected_codegen_fixture_recorded": False,
    "assignment_phi_support_claim": False,
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
    "FEF-P76 records guarded helper and selected codegen fixture text only.",
    "FEF-P76 does not change Forge or eFrog lowering behavior.",
    "FEF-P76 does not execute generated target code.",
    "FEF-P76 does not execute re-ingested code.",
    "FEF-P76 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P76 does not install guarded division or nonzero predicate helpers in a runtime package.",
    "FEF-P76 does not claim compound-condition support.",
    "FEF-P76 does not claim assignment/phi or nested branch support.",
    "FEF-P76 does not claim general branch/control-flow support.",
    "FEF-P76 does not claim branch/control-flow re-ingest support.",
    "FEF-P76 does not claim full non-generated source roundtrip.",
    "FEF-P76 does not claim arbitrary C/Rust source-family support.",
    "FEF-P76 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P76 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def helper_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "helperId": "step01",
            "signature": "double mg_step01(double value)",
            "cBody": "return value > 0.0 ? 1.0 : 0.0;",
            "purpose": "selected positive-threshold guard",
            "installedInRuntime": False,
        },
        {
            "helperId": "nonzero01",
            "signature": "double mg_nonzero01(double value)",
            "cBody": "return value != 0.0 ? 1.0 : 0.0;",
            "purpose": "selected nonzero-denominator guard",
            "installedInRuntime": False,
        },
        {
            "helperId": "guarded_div",
            "signature": "double mg_guarded_div(double numerator, double denominator, double default_value, double guard)",
            "cBody": "return guard != 0.0 ? numerator / denominator : default_value;",
            "purpose": "selected guarded division value helper",
            "installedInRuntime": False,
        },
    ]


def selected_codegen_fixture() -> dict[str, Any]:
    c_source = "\n".join(
        [
            "static double mg_step01(double value) { return value > 0.0 ? 1.0 : 0.0; }",
            "static double mg_nonzero01(double value) { return value != 0.0 ? 1.0 : 0.0; }",
            "static double mg_guarded_div(double numerator, double denominator, double default_value, double guard) {",
            "  return guard != 0.0 ? numerator / denominator : default_value;",
            "}",
            "",
            "double c_and_short_circuit_guard_v0_generated_fixture(double x, double y) {",
            "  double lhs = mg_step01(x);",
            "  double rhs = 0.0;",
            "  double selected = 0.0;",
            "  if (lhs != 0.0) {",
            "    rhs = mg_nonzero01(y);",
            "    selected = mg_guarded_div(x, y, 0.0, rhs);",
            "  }",
            "  return lhs * rhs * selected;",
            "}",
        ]
    )
    return {
        "fixtureId": "c_and_short_circuit_guard_v0_generated_codegen_fixture",
        "selectedFixtureId": "c_and_short_circuit_guard_v0",
        "targetLanguage": "c",
        "status": "codegen_fixture_recorded_runtime_not_executed",
        "source": c_source,
        "usesHelpers": ["step01", "nonzero01", "guarded_div"],
        "preservesShortCircuitSkipInCodeShape": True,
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "installedInForge": False,
    }


def codegen_reference_value(x: float, y: float) -> dict[str, Any]:
    lhs = 1.0 if x > 0.0 else 0.0
    rhs_evaluated = lhs != 0.0
    rhs = 1.0 if rhs_evaluated and y != 0.0 else 0.0
    selected = x / y if rhs != 0.0 else 0.0
    return {
        "value": lhs * rhs * selected,
        "lhs": lhs,
        "rhsEvaluated": rhs_evaluated,
        "rhs": rhs,
        "selected": selected,
    }


def fixture_validation_rows(p75_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in p75_payload["ruleValidationRows"]:
        x = float(row["inputs"]["x"])
        y = float(row["inputs"]["y"])
        reference = codegen_reference_value(x, y)
        expected = float(row["expected"])
        observed = float(reference["value"])
        rows.append(
            {
                "sampleId": row["sampleId"],
                "inputs": copy.deepcopy(row["inputs"]),
                "path": row["path"],
                "expected": expected,
                "codegenFixtureValue": observed,
                "absError": abs(observed - expected),
                "pass": observed == expected,
                "lhs": reference["lhs"],
                "rhsEvaluated": reference["rhsEvaluated"],
                "rhs": reference["rhs"],
                "selected": reference["selected"],
                "generatedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p75_packet: dict[str, Any], p75_payload: dict[str, Any], helpers: list[dict[str, Any]], codegen: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p75ValidationPass": p75_packet["validationStatus"] == "pass",
        "p75ClaimFlagsAllFalse": all(value is False for value in p75_packet["claimFlags"].values()),
        "selectedFixtureId": p75_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p75_payload["summary"]["selectedFixtureStillBlocked"],
        "helperFixtureCount": len(helpers),
        "helpersInstalledInRuntime": any(helper["installedInRuntime"] for helper in helpers),
        "codegenFixtureStatus": codegen["status"],
        "codegenFixtureRecorded": codegen["status"] == "codegen_fixture_recorded_runtime_not_executed",
        "codegenFixtureInstalledInForge": codegen["installedInForge"],
        "codegenFixturePreservesShortCircuitSkip": codegen["preservesShortCircuitSkipInCodeShape"],
        "fixtureValidationSampleCount": len(rows),
        "fixtureValidationPassCount": sum(1 for row in rows if row["pass"]),
        "fixtureValidationFailCount": sum(1 for row in rows if not row["pass"]),
        "fixtureValidationMaxAbsError": max(row["absError"] for row in rows),
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "compoundConditionLoweringImplemented": False,
        "compoundConditionGeneratedTargetExecuted": False,
        "compoundConditionReingestExecuted": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
        "guardedDivisionRuntimeHelperImplemented": False,
        "nonzeroPredicateRuntimeHelperImplemented": False,
        "assignmentPhiSupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "unsupportedConstructsSupported": False,
        "generalBranchControlFlowClaim": False,
        "branchControlFlowReingestClaim": False,
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
        "productionReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p75_packet = read_json(P75_PACKET)
    p75_payload = read_json(P75_RESULT)
    p75.validate_payload(p75_payload)
    helpers = helper_fixtures()
    codegen = selected_codegen_fixture()
    rows = fixture_validation_rows(p75_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p76-compound-condition-helper-codegen-fixture",
        "decision": "selected_helper_codegen_fixture_recorded_runtime_blocked",
        "sourcePacket": {
            "phase": "P75",
            "packetPath": str(P75_PACKET.relative_to(ROOT)),
            "resultPath": str(P75_RESULT.relative_to(ROOT)),
            "reviewDecision": p75_packet["reviewDecision"],
            "validationStatus": p75_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p75_payload["selectedFixture"]),
        "helperFixtures": helpers,
        "selectedCodegenFixture": codegen,
        "fixtureValidationRows": rows,
        "summary": build_summary(p75_packet, p75_payload, helpers, codegen, rows),
        "releaseGates": [
            {"id": "selected_helper_codegen_fixture", "status": "recorded_runtime_blocked"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "short_circuit_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P76 records guarded helper and selected codegen fixture text for review.",
            "The fixture validates against the existing seven-sample semantics table.",
            "P76 does not install helpers, change Forge/eFrog behavior, or execute generated targets.",
        ],
        "blockedStatements": [
            "Compound-condition lowering is implemented in Forge or eFrog.",
            "Guarded helpers are installed in a Forge/eFrog runtime.",
            "Generated compound-condition target code was executed.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit condition semantics are implemented in Forge or eFrog.",
            "Short-circuit boolean conditions are supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Run the selected codegen fixture in a generated-target runtime gate.",
            "Add a re-ingest policy for the selected generated compound-condition fixture.",
            "Record private reviewer response to the P47-P76 branch/control-flow bundle.",
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
        "title": "FEF-P76 Compound-Condition Helper Codegen Fixture",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_helper_codegen_fixture_recorded_runtime_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected helper/codegen fixture only; no Forge/eFrog behavior change, helper installation, generated target execution, re-ingest execution, compound-condition support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P76 records helper and codegen fixture text for the selected compound-condition fixture.",
            "The fixture validates against seven existing semantic samples.",
            "Generated-target runtime remains blocked for a separate gate.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p76_compound_condition_helper_codegen_fixture.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p76_compound_condition_helper_codegen_fixture.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p76_compound_condition_helper_codegen_fixture.v0",
        "date": DATE,
        "title": "FEF-P76 Compound-Condition Helper Codegen Fixture",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run the selected codegen fixture in a generated-target runtime gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Path | Expected | Fixture Value | Abs Error | Pass |", "|---|---|---:|---:|---:|---|"]
    for row in payload["fixtureValidationRows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['path']}` | {row['expected']} | {row['codegenFixtureValue']} | {row['absError']} | `{row['pass']}` |"
        )
    helpers = [f"- `{helper['helperId']}`: {helper['signature']}" for helper in payload["helperFixtures"]]
    return "\n".join(
        [
            "# FEF-P76 Compound-Condition Helper Codegen Fixture",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P76 records guarded helper and selected codegen fixture text without changing compiler behavior.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Helper fixture count: `{summary['helperFixtureCount']}`",
            f"- Helpers installed in runtime: `{summary['helpersInstalledInRuntime']}`",
            f"- Codegen fixture status: `{summary['codegenFixtureStatus']}`",
            f"- Codegen fixture installed in Forge: `{summary['codegenFixtureInstalledInForge']}`",
            f"- Preserves short-circuit skip in code shape: `{summary['codegenFixturePreservesShortCircuitSkip']}`",
            f"- Fixture validation samples: `{summary['fixtureValidationSampleCount']}`",
            f"- Fixture validation pass count: `{summary['fixtureValidationPassCount']}`",
            f"- Fixture validation fail count: `{summary['fixtureValidationFailCount']}`",
            f"- Fixture validation max absolute error: `{summary['fixtureValidationMaxAbsError']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            f"- Compound-condition lowering implemented: `{summary['compoundConditionLoweringImplemented']}`",
            f"- Generated target executed: `{summary['compoundConditionGeneratedTargetExecuted']}`",
            "",
            "## Helpers",
            "",
            *helpers,
            "",
            "## Validation Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected helper/codegen fixture text only.",
            "- No Forge/eFrog behavior change or helper installation.",
            "- No generated target or re-ingested target execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_helpers(helpers: list[dict[str, Any]]) -> None:
    ids = [helper["helperId"] for helper in helpers]
    if ids != ["step01", "nonzero01", "guarded_div"]:
        raise ValueError("unexpected helper fixture ids")
    if any(helper["installedInRuntime"] is not False for helper in helpers):
        raise ValueError("helpers must not be installed in runtime")


def validate_codegen(codegen: dict[str, Any]) -> None:
    if codegen["status"] != "codegen_fixture_recorded_runtime_not_executed":
        raise ValueError("codegen fixture must remain runtime-not-executed")
    if codegen["usesHelpers"] != ["step01", "nonzero01", "guarded_div"]:
        raise ValueError("codegen fixture must use expected helpers")
    if codegen["preservesShortCircuitSkipInCodeShape"] is not True:
        raise ValueError("codegen fixture must preserve selected short-circuit skip")
    if codegen["generatedTargetExecuted"] is not False or codegen["reingestedTargetExecuted"] is not False:
        raise ValueError("codegen fixture must not execute generated or re-ingested targets")
    if codegen["installedInForge"] is not False:
        raise ValueError("codegen fixture must not be installed in Forge")
    for token in ["mg_step01", "mg_nonzero01", "mg_guarded_div", "if (lhs != 0.0)"]:
        if token not in codegen["source"]:
            raise ValueError(f"missing expected codegen token: {token}")


def validate_row(row: dict[str, Any]) -> None:
    if row["codegenFixtureValue"] != row["expected"]:
        raise ValueError("codegen fixture value must match expected sample")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("codegen fixture validation row must pass exactly")
    if row["generatedTargetExecuted"] is not False:
        raise ValueError("codegen validation must not execute generated target")
    if row["path"] == "left_false_short_circuit" and row["rhsEvaluated"] is not False:
        raise ValueError("left-false short circuit must skip rhs")
    if row["path"] == "right_false_zero_denominator_guard" and row["selected"] != 0.0:
        raise ValueError("zero-denominator guard must avoid selected division value")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P76 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P76 status")
    p75.validate_payload(read_json(P75_RESULT))
    validate_helpers(payload["helperFixtures"])
    validate_codegen(payload["selectedCodegenFixture"])
    for row in payload["fixtureValidationRows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p75ValidationPass",
        "p75ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "codegenFixtureRecorded",
        "codegenFixturePreservesShortCircuitSkip",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["helperFixtureCount"] != 3:
        raise ValueError("expected three helper fixtures")
    if summary["fixtureValidationSampleCount"] != 7 or summary["fixtureValidationPassCount"] != 7 or summary["fixtureValidationFailCount"] != 0:
        raise ValueError("unexpected fixture validation counts")
    if summary["fixtureValidationMaxAbsError"] != 0.0:
        raise ValueError("unexpected fixture validation max error")
    for key in [
        "helpersInstalledInRuntime",
        "codegenFixtureInstalledInForge",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "compoundConditionLoweringImplemented",
        "compoundConditionGeneratedTargetExecuted",
        "compoundConditionReingestExecuted",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
        "guardedDivisionRuntimeHelperImplemented",
        "nonzeroPredicateRuntimeHelperImplemented",
        "assignmentPhiSupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "unsupportedConstructsSupported",
        "generalBranchControlFlowClaim",
        "branchControlFlowReingestClaim",
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
    result_path = out_dir / f"fef_p76_compound_condition_helper_codegen_fixture_{STAMP}.json"
    report_path = report_dir / f"fef_p76_compound_condition_helper_codegen_fixture_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p76_compound_condition_helper_codegen_fixture.json"
    feed_path = command_feed_dir / f"fef_p76_compound_condition_helper_codegen_fixture_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p76_compound_condition_helper_codegen_fixture")
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
    print("FEF_P76_COMPOUND_CONDITION_HELPER_CODEGEN_FIXTURE_OK")
    print(f"fixture_status={built['payload']['summary']['codegenFixtureStatus']}")
    print(f"validation_pass_count={built['payload']['summary']['fixtureValidationPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
