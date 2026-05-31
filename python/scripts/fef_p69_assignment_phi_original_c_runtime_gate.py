#!/usr/bin/env python3
"""FEF-P69 original C runtime gate for the selected assignment/phi fixture."""

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

from scripts import fef_p68_assignment_phi_reference_runtime_gate as p68

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p69_assignment_phi_original_c_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P69_ASSIGNMENT_PHI_ORIGINAL_C_RUNTIME_GATE_PASS"

P68_PACKET = ROOT / "reports/evidence_packets/fef_p68_assignment_phi_reference_runtime_gate.json"
P68_RESULT = ROOT / "python/results/fef_p68_assignment_phi_reference_runtime_gate/fef_p68_assignment_phi_reference_runtime_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "assignment_phi_original_c_runtime_gate_claim": False,
    "selected_original_c_assignment_phi_source_execution_recorded": False,
    "assignment_phi_generated_target_execution_claim": False,
    "assignment_phi_reingest_execution_claim": False,
    "assignment_phi_lowering_claim": False,
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
    "FEF-P69 compiles and runs one selected original C assignment/phi fixture locally.",
    "FEF-P69 does not execute generated target code.",
    "FEF-P69 does not execute re-ingested code.",
    "FEF-P69 does not implement mutable assignment lowering.",
    "FEF-P69 does not implement phi/select lowering.",
    "FEF-P69 does not widen Forge or eFrog frontend lowering.",
    "FEF-P69 does not claim assignment/phi support.",
    "FEF-P69 does not claim general branch/control-flow support.",
    "FEF-P69 does not claim branch/control-flow re-ingest support.",
    "FEF-P69 does not claim full non-generated source roundtrip.",
    "FEF-P69 does not claim arbitrary C/Rust source-family support.",
    "FEF-P69 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P69 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def c_harness_source(samples: list[dict[str, Any]]) -> str:
    rows = []
    for sample in samples:
        rows.append(f'  printf("{sample["sampleId"]} %.17g\\n", selected_assignment_phi({sample["inputs"]["x"]}, {sample["inputs"]["y"]}));')
    return "\n".join(
        [
            "#include <stdio.h>",
            "",
            "static double selected_assignment_phi(double x, double y) {",
            "  double z = x;",
            "  if (x > 0.0) {",
            "    z = y;",
            "  }",
            "  return z;",
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
        raise RuntimeError("gcc is required for FEF-P69")
    with tempfile.TemporaryDirectory(prefix="fef_p69_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "selected_assignment_phi.c"
        exe_path = tmp_path / "selected_assignment_phi"
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


def comparison_rows(p68_payload: dict[str, Any], observed: dict[str, float]) -> list[dict[str, Any]]:
    rows = []
    for reference_row in p68_payload["runtimeComparison"]["rows"]:
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
                "assignmentTaken": reference_row["assignmentTaken"],
                "originalCSourceExecuted": True,
                "generatedTargetExecuted": False,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p68_packet: dict[str, Any], p68_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p68ValidationPass": p68_packet["validationStatus"] == "pass",
        "p68ClaimFlagsAllFalse": all(value is False for value in p68_packet["claimFlags"].values()),
        "selectedFixtureId": p68_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p68_payload["summary"]["selectedFixtureStillBlocked"],
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "assignmentTakenCount": sum(1 for row in rows if row["assignmentTaken"] is True),
        "fallthroughCount": sum(1 for row in rows if row["assignmentTaken"] is False),
        "maxAbsError": max(row["absError"] for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "allOriginalCSourceExecuted": all(row["originalCSourceExecuted"] is True for row in rows),
        "generatedTargetExecuted": any(row["generatedTargetExecuted"] for row in rows),
        "reingestedTargetExecuted": any(row["reingestedTargetExecuted"] for row in rows),
        "selectedOriginalCRuntimeEvidenceRecorded": True,
        "assignmentPhiGeneratedTargetExecutionClaim": False,
        "assignmentPhiReingestExecutionClaim": False,
        "assignmentPhiLoweringClaim": False,
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
    p68_packet = read_json(P68_PACKET)
    p68_payload = read_json(P68_RESULT)
    p68.validate_payload(p68_payload)
    samples = [
        {"sampleId": row["sampleId"], "inputs": row["inputs"]}
        for row in p68_payload["runtimeComparison"]["rows"]
    ]
    execution = compile_and_run_c(samples)
    observed = parse_runtime_output(execution["runStdout"])
    rows = comparison_rows(p68_payload, observed)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p69-assignment-phi-original-c-runtime-gate",
        "decision": "assignment_phi_original_c_runtime_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P68",
            "packetPath": str(P68_PACKET.relative_to(ROOT)),
            "resultPath": str(P68_RESULT.relative_to(ROOT)),
            "reviewDecision": p68_packet["reviewDecision"],
            "validationStatus": p68_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p68_payload["selectedFixture"]),
        "runtimeComparison": {
            "comparisonKind": "local_original_c_source_runtime_against_assignment_phi_expected_samples",
            "sourceLanguage": "c",
            "compiler": execution["compiler"],
            "compileReturnCode": execution["compileReturnCode"],
            "runReturnCode": execution["runReturnCode"],
            "originalSourceExecuted": True,
            "generatedTargetExecuted": False,
            "reingestedTargetExecuted": False,
            "rows": rows,
        },
        "summary": build_summary(p68_packet, p68_payload, rows),
        "releaseGates": [
            {"id": "original_c_assignment_phi_runtime_execution", "status": "recorded"},
            {"id": "generated_target_runtime_execution", "status": "not_performed"},
            {"id": "assignment_phi_reingest_execution", "status": "not_performed"},
            {"id": "assignment_phi_lowering", "status": "blocked"},
            {"id": "assignment_phi_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P69 compiles and runs the selected original C assignment/phi fixture locally.",
            "The selected fixture matches all seven expected samples with zero absolute error.",
            "P69 is original-source runtime evidence, not generated target or lowering evidence.",
        ],
        "blockedStatements": [
            "Generated assignment/phi target code was executed.",
            "Re-ingested assignment/phi code was executed.",
            "Assignment/phi lowering is implemented.",
            "Mutable assignments across branches are supported.",
            "Phi/select lowering is supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Build generated-target runtime comparison for the selected fixture only after lowering exists.",
            "Build a compound-condition semantics gate for short-circuit shape.",
            "Keep assignment/phi support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P69 Assignment/Phi Original C Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_assignment_phi_original_c_runtime_evidence_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected original C runtime evidence only; no generated target execution, re-ingest execution, assignment/phi lowering, assignment/phi support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P69 compiles and runs the selected original C assignment/phi fixture locally.",
            "All seven comparisons pass with zero absolute error.",
            "The selected assignment/phi fixture remains blocked for implementation/support claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p69_assignment_phi_original_c_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p69_assignment_phi_original_c_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p69_assignment_phi_original_c_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P69 Assignment/Phi Original C Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Build compound-condition semantics gate or generated-target evidence only after a lowering exists.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | y | Expected | Observed | Abs Error | Pass |", "|---|---:|---:|---:|---:|---:|---|"]
    for row in payload["runtimeComparison"]["rows"]:
        rows.append(
            f"| `{row['sampleId']}` | {row['inputs']['x']} | {row['inputs']['y']} | {row['expected']} | {row['observed']} | {row['absError']} | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P69 Assignment/Phi Original C Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P69 compiles and runs the selected original C assignment/phi fixture against the P67 expected samples.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- Comparisons: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Assignment taken samples: `{summary['assignmentTakenCount']}`",
            f"- Fallthrough samples: `{summary['fallthroughCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Original C source executed: `{summary['allOriginalCSourceExecuted']}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            f"- Assignment/phi lowering claim: `{summary['assignmentPhiLoweringClaim']}`",
            f"- Assignment/phi support claim: `{summary['assignmentPhiSupportClaim']}`",
            "",
            "## Comparisons",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected original C runtime evidence only.",
            "- No generated target or re-ingested target execution.",
            "- No assignment/phi lowering or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_row(row: dict[str, Any]) -> None:
    if row["expected"] != p68.reference_runtime(float(row["inputs"]["x"]), float(row["inputs"]["y"])):
        raise ValueError("expected value does not match selected source semantics")
    if row["observed"] != row["expected"]:
        raise ValueError("observed value must match expected value")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("original C runtime comparison must pass exactly")
    if row["originalCSourceExecuted"] is not True:
        raise ValueError("row must record original C source execution")
    if row["generatedTargetExecuted"] is not False or row["reingestedTargetExecuted"] is not False:
        raise ValueError("row must not record generated or re-ingested execution")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P69 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P69 status")
    p68.validate_payload(read_json(P68_RESULT))
    runtime = payload["runtimeComparison"]
    if runtime["originalSourceExecuted"] is not True:
        raise ValueError("original source execution must be recorded")
    if runtime["generatedTargetExecuted"] is not False or runtime["reingestedTargetExecuted"] is not False:
        raise ValueError("generated and re-ingested execution must remain false")
    for row in runtime["rows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p68ValidationPass",
        "p68ClaimFlagsAllFalse",
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
    if summary["assignmentTakenCount"] != 3 or summary["fallthroughCount"] != 4:
        raise ValueError("unexpected assignment/fallthrough counts")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("maxAbsError must be zero")
    for key in [
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "assignmentPhiGeneratedTargetExecutionClaim",
        "assignmentPhiReingestExecutionClaim",
        "assignmentPhiLoweringClaim",
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
    result_path = out_dir / f"fef_p69_assignment_phi_original_c_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p69_assignment_phi_original_c_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p69_assignment_phi_original_c_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p69_assignment_phi_original_c_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p69_assignment_phi_original_c_runtime_gate")
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
    print("FEF_P69_ASSIGNMENT_PHI_ORIGINAL_C_RUNTIME_GATE_OK")
    print(f"comparisons={built['payload']['summary']['comparisonCount']}")
    print(f"pass_count={built['payload']['summary']['passCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
