#!/usr/bin/env python3
"""FEF-P73 original C runtime gate for the selected compound-condition fixture."""

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

from scripts import fef_p72_compound_condition_reference_runtime_gate as p72

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p73_compound_condition_original_c_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P73_COMPOUND_CONDITION_ORIGINAL_C_RUNTIME_GATE_PASS"

P72_PACKET = ROOT / "reports/evidence_packets/fef_p72_compound_condition_reference_runtime_gate.json"
P72_RESULT = ROOT / "python/results/fef_p72_compound_condition_reference_runtime_gate/fef_p72_compound_condition_reference_runtime_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_original_c_runtime_gate_claim": False,
    "selected_original_c_compound_condition_source_execution_recorded": False,
    "compound_condition_generated_target_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_lowering_claim": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
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
    "FEF-P73 compiles and runs one selected original C compound-condition fixture locally.",
    "FEF-P73 does not execute generated target code.",
    "FEF-P73 does not execute re-ingested code.",
    "FEF-P73 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P73 does not implement compound-condition lowering.",
    "FEF-P73 does not widen Forge or eFrog frontend lowering.",
    "FEF-P73 does not claim compound-condition support.",
    "FEF-P73 does not claim assignment/phi or nested branch support.",
    "FEF-P73 does not claim general branch/control-flow support.",
    "FEF-P73 does not claim branch/control-flow re-ingest support.",
    "FEF-P73 does not claim full non-generated source roundtrip.",
    "FEF-P73 does not claim arbitrary C/Rust source-family support.",
    "FEF-P73 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P73 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def c_harness_source(samples: list[dict[str, Any]]) -> str:
    rows = []
    for sample in samples:
        rows.append(f'  printf("{sample["sampleId"]} %.17g\\n", selected_compound_condition({sample["inputs"]["x"]}, {sample["inputs"]["y"]}));')
    return "\n".join(
        [
            "#include <stdio.h>",
            "",
            "static double selected_compound_condition(double x, double y) {",
            "  if (x > 0.0 && y != 0.0) {",
            "    return x / y;",
            "  }",
            "  return 0.0;",
            "}",
            "",
            "int main(void) {",
            *rows,
            "  return 0;",
            "}",
            "",
        ]
    )


def compile_and_run_c(samples: list[dict[str, Any]]) -> dict[str, Any]:
    gcc = shutil.which("gcc")
    if not gcc:
        raise RuntimeError("gcc is required for FEF-P73")
    with tempfile.TemporaryDirectory(prefix="fef_p73_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "selected_compound_condition.c"
        exe_path = tmp_path / "selected_compound_condition"
        source_path.write_text(c_harness_source(samples), encoding="utf-8")
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


def comparison_rows(p72_payload: dict[str, Any], observed: dict[str, float]) -> list[dict[str, Any]]:
    rows = []
    for reference_row in p72_payload["runtimeComparison"]["rows"]:
        sample_id = reference_row["sampleId"]
        expected = float(reference_row["expected"])
        actual = observed[sample_id]
        abs_error = abs(actual - expected)
        rows.append(
            {
                "sampleId": sample_id,
                "inputs": copy.deepcopy(reference_row["inputs"]),
                "expected": expected,
                "observed": actual,
                "absError": abs_error,
                "pass": math.isfinite(actual) and abs_error == 0.0,
                "path": reference_row["path"],
                "leftCondition": reference_row["leftCondition"],
                "rightConditionEvaluated": reference_row["rightConditionEvaluated"],
                "rightCondition": reference_row["rightCondition"],
                "divisionPerformed": reference_row["divisionPerformed"],
                "originalCSourceExecuted": True,
                "generatedTargetExecuted": False,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p72_packet: dict[str, Any], p72_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p72ValidationPass": p72_packet["validationStatus"] == "pass",
        "p72ClaimFlagsAllFalse": all(value is False for value in p72_packet["claimFlags"].values()),
        "selectedFixtureId": p72_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p72_payload["summary"]["selectedFixtureStillBlocked"],
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "andTrueDivisionCount": sum(1 for row in rows if row["path"] == "and_true_division"),
        "leftFalseShortCircuitCount": sum(1 for row in rows if row["path"] == "left_false_short_circuit"),
        "rightFalseGuardCount": sum(1 for row in rows if row["path"] == "right_false_zero_denominator_guard"),
        "rightConditionEvaluationCount": sum(1 for row in rows if row["rightConditionEvaluated"] is True),
        "divisionPerformedCount": sum(1 for row in rows if row["divisionPerformed"] is True),
        "maxAbsError": max(row["absError"] for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "allOriginalCSourceExecuted": all(row["originalCSourceExecuted"] is True for row in rows),
        "generatedTargetExecuted": any(row["generatedTargetExecuted"] for row in rows),
        "reingestedTargetExecuted": any(row["reingestedTargetExecuted"] for row in rows),
        "selectedOriginalCRuntimeEvidenceRecorded": True,
        "compoundConditionGeneratedTargetExecutionClaim": False,
        "compoundConditionReingestExecutionClaim": False,
        "compoundConditionLoweringClaim": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
        "assignmentPhiSupportClaim": False,
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
    p72_packet = read_json(P72_PACKET)
    p72_payload = read_json(P72_RESULT)
    p72.validate_payload(p72_payload)
    samples = [
        {"sampleId": row["sampleId"], "inputs": row["inputs"]}
        for row in p72_payload["runtimeComparison"]["rows"]
    ]
    execution = compile_and_run_c(samples)
    observed = parse_runtime_output(execution["runStdout"])
    rows = comparison_rows(p72_payload, observed)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p73-compound-condition-original-c-runtime-gate",
        "decision": "compound_condition_original_c_runtime_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P72",
            "packetPath": str(P72_PACKET.relative_to(ROOT)),
            "resultPath": str(P72_RESULT.relative_to(ROOT)),
            "reviewDecision": p72_packet["reviewDecision"],
            "validationStatus": p72_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p72_payload["selectedFixture"]),
        "runtimeComparison": {
            "comparisonKind": "local_original_c_source_runtime_against_compound_condition_expected_samples",
            "sourceLanguage": "c",
            "compiler": execution["compiler"],
            "compileReturnCode": execution["compileReturnCode"],
            "runReturnCode": execution["runReturnCode"],
            "originalSourceExecuted": True,
            "generatedTargetExecuted": False,
            "reingestedTargetExecuted": False,
            "rows": rows,
        },
        "summary": build_summary(p72_packet, p72_payload, rows),
        "releaseGates": [
            {"id": "original_c_compound_condition_runtime_execution", "status": "recorded"},
            {"id": "generated_target_runtime_execution", "status": "not_performed"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "short_circuit_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P73 compiles and runs the selected original C compound-condition fixture locally.",
            "The selected fixture matches all seven expected samples with zero absolute error.",
            "P73 is original-source runtime evidence, not generated target or lowering evidence.",
        ],
        "blockedStatements": [
            "Generated compound-condition target code was executed.",
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
            "Build generated-target runtime comparison for the selected fixture only after compound-condition lowering exists.",
            "Keep compound-condition support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P73 Compound-Condition Original C Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_compound_condition_original_c_runtime_evidence_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected original C runtime evidence only; no generated target execution, re-ingest execution, compound-condition lowering, compound-condition support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P73 compiles and runs the selected original C compound-condition fixture locally.",
            "All seven comparisons pass with zero absolute error.",
            "The selected compound-condition fixture remains blocked for implementation/support claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p73_compound_condition_original_c_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p73_compound_condition_original_c_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p73_compound_condition_original_c_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P73 Compound-Condition Original C Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Build generated-target evidence only after compound-condition lowering exists.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | y | Path | Expected | Observed | Abs Error | Pass |", "|---|---:|---:|---|---:|---:|---:|---|"]
    for row in payload["runtimeComparison"]["rows"]:
        rows.append(
            f"| `{row['sampleId']}` | {row['inputs']['x']} | {row['inputs']['y']} | `{row['path']}` | {row['expected']} | {row['observed']} | {row['absError']} | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P73 Compound-Condition Original C Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P73 compiles and runs the selected original C compound-condition fixture against the P71 expected samples.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- Comparisons: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- True-division samples: `{summary['andTrueDivisionCount']}`",
            f"- Left-false short-circuit samples: `{summary['leftFalseShortCircuitCount']}`",
            f"- Right-false guard samples: `{summary['rightFalseGuardCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Original C source executed: `{summary['allOriginalCSourceExecuted']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Compound-condition lowering claim: `{summary['compoundConditionLoweringClaim']}`",
            f"- Compound-condition support claim: `{summary['compoundConditionSupportClaim']}`",
            "",
            "## Comparisons",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected original C runtime evidence only.",
            "- No generated target or re-ingested target execution.",
            "- No short-circuit implementation, compound-condition lowering, or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_row(row: dict[str, Any]) -> None:
    runtime = p72.reference_runtime(float(row["inputs"]["x"]), float(row["inputs"]["y"]))
    if row["expected"] != runtime["observed"]:
        raise ValueError("expected value does not match selected source semantics")
    if row["observed"] != row["expected"]:
        raise ValueError("observed value must match expected value")
    for key in ["leftCondition", "rightConditionEvaluated", "rightCondition", "divisionPerformed"]:
        if row[key] != runtime[key]:
            raise ValueError(f"{key} does not match selected source semantics")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("original C runtime comparison must pass exactly")
    if row["originalCSourceExecuted"] is not True:
        raise ValueError("row must record original C source execution")
    if row["generatedTargetExecuted"] is not False or row["reingestedTargetExecuted"] is not False:
        raise ValueError("row must not record generated or re-ingested execution")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P73 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P73 status")
    p72.validate_payload(read_json(P72_RESULT))
    runtime = payload["runtimeComparison"]
    if runtime["originalSourceExecuted"] is not True:
        raise ValueError("original source execution must be recorded")
    if runtime["generatedTargetExecuted"] is not False or runtime["reingestedTargetExecuted"] is not False:
        raise ValueError("generated and re-ingested execution must remain false")
    for row in runtime["rows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p72ValidationPass",
        "p72ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allObservedFinite",
        "allOriginalCSourceExecuted",
        "selectedOriginalCRuntimeEvidenceRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["comparisonCount"] != 7 or summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("unexpected comparison counts")
    if summary["andTrueDivisionCount"] != 3:
        raise ValueError("expected three true-division samples")
    if summary["leftFalseShortCircuitCount"] != 3:
        raise ValueError("expected three left-false short-circuit samples")
    if summary["rightFalseGuardCount"] != 1:
        raise ValueError("expected one right-false guard sample")
    if summary["rightConditionEvaluationCount"] != 4 or summary["divisionPerformedCount"] != 3:
        raise ValueError("unexpected short-circuit path counts")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("maxAbsError must be zero")
    for key in [
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "compoundConditionGeneratedTargetExecutionClaim",
        "compoundConditionReingestExecutionClaim",
        "compoundConditionLoweringClaim",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
        "assignmentPhiSupportClaim",
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
    result_path = out_dir / f"fef_p73_compound_condition_original_c_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p73_compound_condition_original_c_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p73_compound_condition_original_c_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p73_compound_condition_original_c_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p73_compound_condition_original_c_runtime_gate")
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
    print("FEF_P73_COMPOUND_CONDITION_ORIGINAL_C_RUNTIME_GATE_OK")
    print(f"comparisons={built['payload']['summary']['comparisonCount']}")
    print(f"pass_count={built['payload']['summary']['passCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
