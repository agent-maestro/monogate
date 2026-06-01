#!/usr/bin/env python3
"""FEF-P97 selected loop codegen fixture."""

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

from scripts import fef_p96_loop_lowering_rule_packet as p96  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p97_loop_codegen_fixture.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P97_LOOP_CODEGEN_FIXTURE_PASS"

P96_PACKET = ROOT / "reports/evidence_packets/fef_p96_loop_lowering_rule_packet.json"
P96_RESULT = ROOT / "python/results/fef_p96_loop_lowering_rule_packet/fef_p96_loop_lowering_rule_packet_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_codegen_fixture_claim": False,
    "loop_lowering_implemented": False,
    "loop_generated_target_execution_claim": False,
    "loop_reingest_execution_claim": False,
    "loop_backedge_support_claim": False,
    "loop_backedge_semantics_implemented": False,
    "loop_boundedness_policy_general_claim": False,
    "selected_codegen_fixture_recorded": False,
    "assignment_phi_support_claim": False,
    "compound_condition_support_claim": False,
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
    "FEF-P97 records selected loop codegen fixture text only.",
    "FEF-P97 does not change Forge or eFrog lowering behavior.",
    "FEF-P97 does not compile or execute generated target code.",
    "FEF-P97 does not execute re-ingested code.",
    "FEF-P97 does not install loop lowering in Forge or eFrog.",
    "FEF-P97 does not implement loop headers, latches, variants, or back-edge semantics in Forge or eFrog.",
    "FEF-P97 does not implement a general loop boundedness policy.",
    "FEF-P97 does not claim loop/back-edge support.",
    "FEF-P97 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P97 does not claim general branch/control-flow support.",
    "FEF-P97 does not claim branch/control-flow re-ingest support.",
    "FEF-P97 does not claim full non-generated source roundtrip.",
    "FEF-P97 does not claim arbitrary C/Rust source-family support.",
    "FEF-P97 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P97 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_codegen_fixture() -> dict[str, Any]:
    c_source = "\n".join(
        [
            "static int mg_loop_effective_iterations(int n) {",
            "  return n > 0 ? n : 0;",
            "}",
            "",
            "double c_while_accumulate_v0_generated_fixture(double x, int n) {",
            "  int k = mg_loop_effective_iterations(n);",
            "  return x * (double)k;",
            "}",
        ]
    )
    return {
        "fixtureId": "c_while_accumulate_v0_generated_codegen_fixture",
        "selectedFixtureId": "c_while_accumulate_v0",
        "targetLanguage": "c",
        "status": "codegen_fixture_recorded_runtime_not_executed",
        "source": c_source,
        "usesHelpers": ["loop_effective_iterations"],
        "requiresPolicyGate": "selected_c_while_accumulate_boundedness_policy_v0",
        "generatedTargetCompiled": False,
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
        "installedInForge": False,
    }


def codegen_fixture_value(x: float, n: int) -> dict[str, Any]:
    k = n if n > 0 else 0
    return {
        "value": x * float(k),
        "effectiveIterationCount": k,
    }


def fixture_validation_rows(p96_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in p96_payload["ruleValidationRows"]:
        x = float(row["inputs"]["x"])
        n = int(row["inputs"]["n"])
        reference = codegen_fixture_value(x, n)
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
                "effectiveIterationCount": reference["effectiveIterationCount"],
                "generatedTargetCompiled": False,
                "generatedTargetExecuted": False,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p96_packet: dict[str, Any], p96_payload: dict[str, Any], codegen: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p96ValidationPass": p96_packet["validationStatus"] == "pass",
        "p96ClaimFlagsAllFalse": all(value is False for value in p96_packet["claimFlags"].values()),
        "selectedFixtureId": p96_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p96_payload["summary"]["selectedFixtureStillBlocked"],
        "codegenFixtureStatus": codegen["status"],
        "codegenFixtureRecorded": codegen["status"] == "codegen_fixture_recorded_runtime_not_executed",
        "codegenFixtureInstalledInForge": codegen["installedInForge"],
        "codegenRequiresPolicyGate": codegen["requiresPolicyGate"],
        "fixtureValidationSampleCount": len(rows),
        "fixtureValidationPassCount": sum(1 for row in rows if row["pass"]),
        "fixtureValidationFailCount": sum(1 for row in rows if not row["pass"]),
        "fixtureValidationMaxAbsError": max(row["absError"] for row in rows),
        "zeroIterationCount": sum(1 for row in rows if row["effectiveIterationCount"] == 0),
        "singleIterationCount": sum(1 for row in rows if row["effectiveIterationCount"] == 1),
        "multiIterationCount": sum(1 for row in rows if row["effectiveIterationCount"] > 1),
        "maxEffectiveIterationCount": max(row["effectiveIterationCount"] for row in rows),
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "loopLoweringImplemented": False,
        "loopGeneratedTargetCompiled": False,
        "loopGeneratedTargetExecuted": False,
        "loopReingestExecuted": False,
        "loopBackedgeSupportClaim": False,
        "loopBackedgeSemanticsImplemented": False,
        "loopBoundednessPolicyGeneralClaim": False,
        "selectedCodegenFixtureInstalled": False,
        "assignmentPhiSupportClaim": False,
        "compoundConditionSupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
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
    p96_packet = read_json(P96_PACKET)
    p96_payload = read_json(P96_RESULT)
    p96.validate_payload(p96_payload)
    codegen = selected_codegen_fixture()
    rows = fixture_validation_rows(p96_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p97-loop-codegen-fixture",
        "decision": "selected_loop_codegen_fixture_recorded_runtime_blocked",
        "sourcePacket": {
            "phase": "P96",
            "packetPath": str(P96_PACKET.relative_to(ROOT)),
            "resultPath": str(P96_RESULT.relative_to(ROOT)),
            "reviewDecision": p96_packet["reviewDecision"],
            "validationStatus": p96_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p96_payload["selectedFixture"]),
        "selectedCodegenFixture": codegen,
        "fixtureValidationRows": rows,
        "summary": build_summary(p96_packet, p96_payload, codegen, rows),
        "releaseGates": [
            {"id": "selected_loop_codegen_fixture", "status": "recorded_runtime_blocked"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "loop_reingest_execution", "status": "not_performed"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "loop_backedge_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P97 records selected loop codegen fixture text for review.",
            "The fixture validates against the existing seven selected loop samples.",
            "P97 does not compile, execute, install, or re-ingest the generated fixture.",
        ],
        "blockedStatements": [
            "Loop lowering is implemented in Forge or eFrog.",
            "Generated loop target code was compiled or executed.",
            "Re-ingested loop code was executed.",
            "Loop header, latch, variant, or back-edge semantics are implemented in Forge or eFrog.",
            "Loop/back-edge constructs are supported.",
            "The P92 boundedness policy is a general loop policy.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Run the selected loop codegen fixture in a generated-target runtime gate.",
            "Record private reviewer response to the P47-P97 branch/control-flow bundle.",
            "Keep loop/back-edge support blocked until generated-target and re-ingest evidence exist.",
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
        "title": "FEF-P97 Loop Codegen Fixture",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_loop_codegen_fixture_recorded_runtime_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected loop codegen fixture only; no Forge/eFrog behavior change, generated target compile/run, re-ingest execution, loop/back-edge support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P97 records C fixture text for the selected loop lowering.",
            "The fixture validates against seven existing selected loop samples without compiling or running generated code.",
            "Generated-target runtime remains blocked for a separate gate.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p97_loop_codegen_fixture.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p97_loop_codegen_fixture.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p97_loop_codegen_fixture.v0",
        "date": DATE,
        "title": "FEF-P97 Loop Codegen Fixture",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run the selected loop codegen fixture in a generated-target runtime gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Path | Effective Iterations | Expected | Fixture Value | Abs Error | Pass |", "|---|---|---:|---:|---:|---:|---|"]
    for row in payload["fixtureValidationRows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['path']}` | {row['effectiveIterationCount']} | {row['expected']} | {row['codegenFixtureValue']} | {row['absError']} | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P97 Loop Codegen Fixture",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P97 records selected loop codegen fixture text without compiling or executing generated target code.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Codegen fixture status: `{summary['codegenFixtureStatus']}`",
            f"- Requires policy gate: `{summary['codegenRequiresPolicyGate']}`",
            f"- Fixture validation samples: `{summary['fixtureValidationSampleCount']}`",
            f"- Fixture validation pass count: `{summary['fixtureValidationPassCount']}`",
            f"- Fixture validation fail count: `{summary['fixtureValidationFailCount']}`",
            f"- Fixture validation max absolute error: `{summary['fixtureValidationMaxAbsError']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            f"- Frontend lowering changed: `{summary['frontendLoweringChanged']}`",
            f"- Loop lowering implemented: `{summary['loopLoweringImplemented']}`",
            f"- Generated target compiled: `{summary['loopGeneratedTargetCompiled']}`",
            f"- Generated target executed: `{summary['loopGeneratedTargetExecuted']}`",
            "",
            "## Codegen Fixture",
            "",
            "```c",
            payload["selectedCodegenFixture"]["source"],
            "```",
            "",
            "## Fixture Validation",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected codegen fixture text only.",
            "- No Forge/eFrog behavior change.",
            "- No generated target compile/run or re-ingested target execution.",
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_codegen(codegen: dict[str, Any]) -> None:
    if codegen["status"] != "codegen_fixture_recorded_runtime_not_executed":
        raise ValueError("codegen fixture must remain runtime-not-executed")
    if codegen["selectedFixtureId"] != "c_while_accumulate_v0":
        raise ValueError("unexpected codegen fixture")
    if codegen["requiresPolicyGate"] != "selected_c_while_accumulate_boundedness_policy_v0":
        raise ValueError("codegen fixture must retain selected policy gate")
    for token in ["mg_loop_effective_iterations", "return x * (double)k;"]:
        if token not in codegen["source"]:
            raise ValueError(f"missing codegen token: {token}")
    for key in ["generatedTargetCompiled", "generatedTargetExecuted", "reingestedTargetExecuted", "installedInForge"]:
        if codegen[key] is not False:
            raise ValueError(f"{key} must remain false")


def validate_row(row: dict[str, Any]) -> None:
    if row["codegenFixtureValue"] != row["expected"]:
        raise ValueError("codegen fixture value must match expected")
    if row["absError"] != abs(row["codegenFixtureValue"] - row["expected"]):
        raise ValueError("absolute error mismatch")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("selected rows must pass with zero error")
    if row["effectiveIterationCount"] != max(0, int(row["inputs"]["n"])):
        raise ValueError("effective iteration count mismatch")
    for key in ["generatedTargetCompiled", "generatedTargetExecuted", "reingestedTargetExecuted"]:
        if row[key] is not False:
            raise ValueError(f"{key} must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P97 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P97 status")
    p96.validate_payload(read_json(P96_RESULT))
    validate_codegen(payload["selectedCodegenFixture"])
    for row in payload["fixtureValidationRows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p96ValidationPass",
        "p96ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "codegenFixtureRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedFixtureId"] != "c_while_accumulate_v0":
        raise ValueError("unexpected selected fixture")
    if summary["fixtureValidationSampleCount"] != 7 or summary["fixtureValidationPassCount"] != 7:
        raise ValueError("expected seven passing fixture validation samples")
    if summary["fixtureValidationFailCount"] != 0 or summary["fixtureValidationMaxAbsError"] != 0.0:
        raise ValueError("expected zero fixture validation error")
    if summary["zeroIterationCount"] != 2 or summary["singleIterationCount"] != 1 or summary["multiIterationCount"] != 4:
        raise ValueError("unexpected iteration distribution")
    for key in [
        "codegenFixtureInstalledInForge",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "loopLoweringImplemented",
        "loopGeneratedTargetCompiled",
        "loopGeneratedTargetExecuted",
        "loopReingestExecuted",
        "loopBackedgeSupportClaim",
        "loopBackedgeSemanticsImplemented",
        "loopBoundednessPolicyGeneralClaim",
        "selectedCodegenFixtureInstalled",
        "assignmentPhiSupportClaim",
        "compoundConditionSupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
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
    result_path = out_dir / f"fef_p97_loop_codegen_fixture_{STAMP}.json"
    report_path = report_dir / f"fef_p97_loop_codegen_fixture_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p97_loop_codegen_fixture.json"
    feed_path = command_feed_dir / f"fef_p97_loop_codegen_fixture_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p97_loop_codegen_fixture")
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
    print("FEF_P97_LOOP_CODEGEN_FIXTURE_OK")
    print(f"pass_count={built['payload']['summary']['fixtureValidationPassCount']}")
    print(f"max_abs_error={built['payload']['summary']['fixtureValidationMaxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
