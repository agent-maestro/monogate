#!/usr/bin/env python3
"""FEF-P77 generated-target runtime gate for the selected compound condition."""

from __future__ import annotations

import argparse
import copy
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p76_compound_condition_helper_codegen_fixture as p76

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p77_compound_condition_generated_target_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P77_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_GATE_PASS"

P76_PACKET = ROOT / "reports/evidence_packets/fef_p76_compound_condition_helper_codegen_fixture.json"
P76_RESULT = ROOT / "python/results/fef_p76_compound_condition_helper_codegen_fixture/fef_p76_compound_condition_helper_codegen_fixture_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_generated_target_runtime_gate_claim": False,
    "selected_generated_target_runtime_execution_recorded": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
    "guarded_division_runtime_helper_installed": False,
    "nonzero_predicate_runtime_helper_installed": False,
    "selected_codegen_fixture_installed_in_forge": False,
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
    "FEF-P77 compiles and runs one selected generated C fixture locally.",
    "FEF-P77 does not install helper functions in Forge or eFrog.",
    "FEF-P77 does not change Forge or eFrog lowering behavior.",
    "FEF-P77 does not execute re-ingested code.",
    "FEF-P77 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P77 does not claim compound-condition support.",
    "FEF-P77 does not claim assignment/phi or nested branch support.",
    "FEF-P77 does not claim general branch/control-flow support.",
    "FEF-P77 does not claim branch/control-flow re-ingest support.",
    "FEF-P77 does not claim full non-generated source roundtrip.",
    "FEF-P77 does not claim arbitrary C/Rust source-family support.",
    "FEF-P77 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P77 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def c_harness_source(codegen_source: str, rows: list[dict[str, Any]]) -> str:
    calls = []
    for row in rows:
        x = row["inputs"]["x"]
        y = row["inputs"]["y"]
        calls.append(
            f'  printf("{row["sampleId"]} %.17g\\n", c_and_short_circuit_guard_v0_generated_fixture({x}, {y}));'
        )
    return "\n".join(
        [
            "#include <stdio.h>",
            "",
            codegen_source,
            "",
            "int main(void) {",
            *calls,
            "  return 0;",
            "}",
            "",
        ]
    )


def compile_and_run_generated_c(codegen_source: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    gcc = shutil.which("gcc")
    if not gcc:
        raise RuntimeError("gcc is required for FEF-P77")
    with tempfile.TemporaryDirectory(prefix="fef_p77_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "selected_generated_compound_condition.c"
        exe_path = tmp_path / "selected_generated_compound_condition"
        source_path.write_text(c_harness_source(codegen_source, rows), encoding="utf-8")
        compile_proc = subprocess.run(
            [gcc, "-std=c99", "-O0", "-Wall", "-Wextra", str(source_path), "-o", str(exe_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if compile_proc.returncode != 0:
            raise RuntimeError(compile_proc.stderr)
        run_proc = subprocess.run([str(exe_path)], check=False, capture_output=True, text=True)
        if run_proc.returncode != 0:
            raise RuntimeError(run_proc.stderr)
        return {
            "compiler": gcc,
            "compileReturnCode": compile_proc.returncode,
            "compileStderr": compile_proc.stderr.strip(),
            "runReturnCode": run_proc.returncode,
            "runStdout": run_proc.stdout,
        }


def parse_runtime_output(stdout: str) -> dict[str, float]:
    observed: dict[str, float] = {}
    for line in stdout.splitlines():
        sample_id, value = line.split()
        observed[sample_id] = float(value)
    return observed


def runtime_rows(p76_payload: dict[str, Any], observed: dict[str, float]) -> list[dict[str, Any]]:
    rows = []
    for source_row in p76_payload["fixtureValidationRows"]:
        sample_id = source_row["sampleId"]
        expected = float(source_row["expected"])
        actual = observed[sample_id]
        abs_error = abs(actual - expected)
        rows.append(
            {
                "sampleId": sample_id,
                "inputs": copy.deepcopy(source_row["inputs"]),
                "path": source_row["path"],
                "expected": expected,
                "observed": actual,
                "absError": abs_error,
                "pass": math.isfinite(actual) and abs_error == 0.0,
                "lhs": source_row["lhs"],
                "rhsEvaluated": source_row["rhsEvaluated"],
                "rhs": source_row["rhs"],
                "selected": source_row["selected"],
                "generatedTargetExecuted": True,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p76_packet: dict[str, Any], p76_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p76ValidationPass": p76_packet["validationStatus"] == "pass",
        "p76ClaimFlagsAllFalse": all(value is False for value in p76_packet["claimFlags"].values()),
        "selectedFixtureId": p76_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p76_payload["summary"]["selectedFixtureStillBlocked"],
        "runtimeComparisonKind": "local_generated_c_fixture_against_compound_condition_expected_samples",
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "maxAbsError": max(row["absError"] for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "generatedTargetRuntimeExecuted": all(row["generatedTargetExecuted"] is True for row in rows),
        "selectedGeneratedTargetRuntimeEvidenceRecorded": True,
        "reingestedTargetExecuted": any(row["reingestedTargetExecuted"] for row in rows),
        "leftFalseShortCircuitCount": sum(1 for row in rows if row["path"] == "left_false_short_circuit"),
        "rightFalseGuardCount": sum(1 for row in rows if row["path"] == "right_false_zero_denominator_guard"),
        "helperRuntimeInstalled": False,
        "codegenFixtureInstalledInForge": False,
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "compoundConditionLoweringImplemented": False,
        "compoundConditionGeneratedTargetRuntimeClaim": False,
        "compoundConditionReingestExecuted": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
        "guardedDivisionRuntimeHelperInstalled": False,
        "nonzeroPredicateRuntimeHelperInstalled": False,
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
    p76_packet = read_json(P76_PACKET)
    p76_payload = read_json(P76_RESULT)
    p76.validate_payload(p76_payload)
    codegen = copy.deepcopy(p76_payload["selectedCodegenFixture"])
    execution = compile_and_run_generated_c(codegen["source"], p76_payload["fixtureValidationRows"])
    observed = parse_runtime_output(execution["runStdout"])
    rows = runtime_rows(p76_payload, observed)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p77-compound-condition-generated-target-runtime-gate",
        "decision": "selected_generated_c_fixture_runtime_recorded_reingest_blocked",
        "sourcePacket": {
            "phase": "P76",
            "packetPath": str(P76_PACKET.relative_to(ROOT)),
            "resultPath": str(P76_RESULT.relative_to(ROOT)),
            "reviewDecision": p76_packet["reviewDecision"],
            "validationStatus": p76_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p76_payload["selectedFixture"]),
        "selectedCodegenFixture": codegen,
        "runtimeComparison": {
            "comparisonKind": "local_generated_c_fixture_against_compound_condition_expected_samples",
            "targetLanguage": "c",
            "compiler": execution["compiler"],
            "compileReturnCode": execution["compileReturnCode"],
            "runReturnCode": execution["runReturnCode"],
            "generatedTargetExecuted": True,
            "reingestedTargetExecuted": False,
            "installedInForge": False,
            "rows": rows,
        },
        "summary": build_summary(p76_packet, p76_payload, rows),
        "releaseGates": [
            {"id": "selected_generated_c_fixture_runtime_execution", "status": "recorded"},
            {"id": "helper_runtime_installation", "status": "not_performed"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "short_circuit_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P77 compiles and runs the selected generated C fixture locally.",
            "The selected generated fixture matches all seven expected samples with zero absolute error.",
            "P77 is selected generated-fixture runtime evidence, not installed Forge/eFrog lowering or support evidence.",
        ],
        "blockedStatements": [
            "Generated compound-condition runtime support is installed in Forge or eFrog.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit condition semantics are implemented in Forge or eFrog.",
            "Compound-condition lowering is implemented.",
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
            "Add selected re-ingest policy for the generated compound-condition fixture.",
            "Record private reviewer response to the P47-P77 branch/control-flow bundle.",
            "Keep compound-condition support blocked until installed lowering and re-ingest evidence exists.",
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
        "title": "FEF-P77 Compound-Condition Generated Target Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_generated_c_fixture_runtime_evidence_reingest_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected generated C fixture runtime evidence only; no Forge/eFrog behavior change, helper installation, re-ingest execution, compound-condition support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P77 compiles and runs the selected generated C fixture locally.",
            "All seven comparisons pass with zero absolute error.",
            "Re-ingest and installed lowering remain blocked for separate gates.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p77_compound_condition_generated_target_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p77_compound_condition_generated_target_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p77_compound_condition_generated_target_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P77 Compound-Condition Generated Target Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add selected re-ingest policy for the generated compound-condition fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Path | Expected | Observed | Abs Error | Pass |", "|---|---|---:|---:|---:|---|"]
    for row in payload["runtimeComparison"]["rows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['path']}` | {row['expected']} | {row['observed']} | {row['absError']} | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P77 Compound-Condition Generated Target Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P77 compiles and runs the selected generated C fixture without installing compound-condition lowering.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Runtime comparison kind: `{summary['runtimeComparisonKind']}`",
            f"- Comparison count: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Generated target runtime executed: `{summary['generatedTargetRuntimeExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Helper runtime installed: `{summary['helperRuntimeInstalled']}`",
            f"- Codegen fixture installed in Forge: `{summary['codegenFixtureInstalledInForge']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            f"- Compound-condition lowering implemented: `{summary['compoundConditionLoweringImplemented']}`",
            "",
            "## Runtime Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected generated C fixture runtime evidence only.",
            "- No Forge/eFrog behavior change or helper installation.",
            "- No re-ingested target execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_row(row: dict[str, Any]) -> None:
    if row["observed"] != row["expected"]:
        raise ValueError("generated runtime row must match expected sample")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("generated runtime row must pass exactly")
    if row["generatedTargetExecuted"] is not True:
        raise ValueError("generated target must be executed in P77")
    if row["reingestedTargetExecuted"] is not False:
        raise ValueError("re-ingested target must not execute in P77")
    if row["path"] == "left_false_short_circuit" and row["rhsEvaluated"] is not False:
        raise ValueError("left-false short circuit must skip rhs")
    if row["path"] == "right_false_zero_denominator_guard" and row["selected"] != 0.0:
        raise ValueError("zero-denominator guard must avoid selected division value")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P77 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P77 status")
    p76.validate_payload(read_json(P76_RESULT))
    runtime = payload["runtimeComparison"]
    if runtime["comparisonKind"] != "local_generated_c_fixture_against_compound_condition_expected_samples":
        raise ValueError("unexpected runtime comparison kind")
    if runtime["generatedTargetExecuted"] is not True:
        raise ValueError("P77 must execute the selected generated target fixture")
    if runtime["reingestedTargetExecuted"] is not False or runtime["installedInForge"] is not False:
        raise ValueError("P77 must not execute re-ingest or install Forge lowering")
    for row in runtime["rows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p76ValidationPass",
        "p76ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allObservedFinite",
        "generatedTargetRuntimeExecuted",
        "selectedGeneratedTargetRuntimeEvidenceRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["comparisonCount"] != 7 or summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("unexpected runtime comparison counts")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("unexpected generated runtime max error")
    for key in [
        "reingestedTargetExecuted",
        "helperRuntimeInstalled",
        "codegenFixtureInstalledInForge",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "compoundConditionLoweringImplemented",
        "compoundConditionGeneratedTargetRuntimeClaim",
        "compoundConditionReingestExecuted",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
        "guardedDivisionRuntimeHelperInstalled",
        "nonzeroPredicateRuntimeHelperInstalled",
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
    result_path = out_dir / f"fef_p77_compound_condition_generated_target_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p77_compound_condition_generated_target_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p77_compound_condition_generated_target_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p77_compound_condition_generated_target_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p77_compound_condition_generated_target_runtime_gate")
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
    print("FEF_P77_COMPOUND_CONDITION_GENERATED_TARGET_RUNTIME_GATE_OK")
    print(f"runtime_status={built['payload']['summary']['runtimeComparisonKind']}")
    print(f"pass_count={built['payload']['summary']['passCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
