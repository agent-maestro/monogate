#!/usr/bin/env python3
"""FEF-P109 original C stubbed-runtime gate for selected side-effect samples."""

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

from scripts import fef_p108_side_effect_reference_runtime_gate as p108  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p109_side_effect_original_c_stubbed_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P109_SIDE_EFFECT_ORIGINAL_C_STUBBED_RUNTIME_GATE_PASS"

P108_PACKET = ROOT / "reports/evidence_packets/fef_p108_side_effect_reference_runtime_gate.json"
P108_RESULT = ROOT / "python/results/fef_p108_side_effect_reference_runtime_gate/fef_p108_side_effect_reference_runtime_gate_2026_06_01.json"

CLAIM_FLAGS = {
    "side_effect_original_c_stubbed_runtime_gate_claim": False,
    "live_external_call_claim": False,
    "unbounded_memory_mutation_claim": False,
    "generated_target_execution_claim": False,
    "reingest_execution_claim": False,
    "side_effect_lowering_implemented": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
    "side_effect_memory_support_claim": False,
    "loop_backedge_support_claim": False,
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
    "FEF-P109 compiles and runs one selected original C side-effect fixture locally with a deterministic stubbed external call.",
    "FEF-P109 captures bounded harness-local state for the selected fixture only.",
    "FEF-P109 does not perform live external calls.",
    "FEF-P109 does not perform unbounded memory mutation or aliasing.",
    "FEF-P109 does not execute generated target code.",
    "FEF-P109 does not execute re-ingested code.",
    "FEF-P109 does not implement effect ordering, external-call, aliasing, or memory-state policy in Forge or eFrog.",
    "FEF-P109 does not implement side-effect/call/memory lowering.",
    "FEF-P109 does not widen Forge or eFrog frontend lowering.",
    "FEF-P109 does not claim side-effect/call/memory support.",
    "FEF-P109 does not claim loop/back-edge, assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P109 does not record reviewer approval or rejection.",
    "FEF-P109 does not claim general branch/control-flow support.",
    "FEF-P109 does not claim branch/control-flow re-ingest support.",
    "FEF-P109 does not claim full non-generated source roundtrip.",
    "FEF-P109 does not claim arbitrary C/Rust source-family support.",
    "FEF-P109 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P109 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def c_harness_source(rows: list[dict[str, Any]]) -> str:
    calls = []
    for row in rows:
        inputs = row["inputs"]
        x = inputs["x"]
        initial_state = inputs["initialState"]
        stub_return = inputs["externalCallReturn"]
        stub = 0.0 if stub_return is None else stub_return
        calls.append(
            "  run_sample(\"{sample_id}\", {x}, {initial_state}, {stub});".format(
                sample_id=row["sampleId"],
                x=x,
                initial_state=initial_state,
                stub=stub,
            )
        )
    return "\n".join(
        [
            "#include <stdio.h>",
            "",
            "static double state = 0.0;",
            "static double deterministic_update_return = 0.0;",
            "static int update_state_call_count = 0;",
            "static int state_write_count = 0;",
            "",
            "static double update_state(double x) {",
            "  (void)x;",
            "  update_state_call_count = update_state_call_count + 1;",
            "  return deterministic_update_return;",
            "}",
            "",
            "static double selected_global_state_update(double x) {",
            "  if (x > 0.0) {",
            "    state = update_state(x);",
            "    state_write_count = state_write_count + 1;",
            "  }",
            "  return state;",
            "}",
            "",
            "static void run_sample(const char *sample_id, double x, double initial_state, double stub_return) {",
            "  state = initial_state;",
            "  deterministic_update_return = stub_return;",
            "  update_state_call_count = 0;",
            "  state_write_count = 0;",
            "  double observed = selected_global_state_update(x);",
            "  printf(\"%s %.17g %.17g %d %d\\n\", sample_id, observed, state, update_state_call_count, state_write_count);",
            "}",
            "",
            "int main(void) {",
            *calls,
            "  return 0;",
            "}",
            "",
        ]
    )


def compile_and_run_c(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gcc = shutil.which("gcc")
    if not gcc:
        raise RuntimeError("gcc is required for FEF-P109")
    with tempfile.TemporaryDirectory(prefix="fef_p109_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "selected_global_state_update_stubbed.c"
        exe_path = tmp_path / "selected_global_state_update_stubbed"
        source_path.write_text(c_harness_source(rows), encoding="utf-8")
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


def parse_runtime_output(stdout: str) -> dict[str, dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for line in stdout.splitlines():
        sample_id, value, final_state, call_count, write_count = line.split()
        observed[sample_id] = {
            "observed": float(value),
            "capturedFinalState": float(final_state),
            "stubbedCallCount": int(call_count),
            "boundedStateWriteCount": int(write_count),
        }
    return observed


def comparison_rows(p108_payload: dict[str, Any], observed: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for reference_row in p108_payload["runtimeComparison"]["rows"]:
        sample_id = reference_row["sampleId"]
        actual = observed[sample_id]
        expected = float(reference_row["expected"])
        observed_value = float(actual["observed"])
        abs_error = abs(observed_value - expected)
        expected_call_count = 1 if reference_row["modeledCallExpected"] else 0
        expected_write_count = 1 if reference_row["modeledStateWriteExpected"] else 0
        rows.append(
            {
                "sampleId": sample_id,
                "inputs": copy.deepcopy(reference_row["inputs"]),
                "path": reference_row["path"],
                "expected": expected,
                "observed": observed_value,
                "capturedFinalState": actual["capturedFinalState"],
                "absError": abs_error,
                "pass": (
                    math.isfinite(observed_value)
                    and abs_error == 0.0
                    and actual["capturedFinalState"] == observed_value
                    and actual["stubbedCallCount"] == expected_call_count
                    and actual["boundedStateWriteCount"] == expected_write_count
                ),
                "guardTrue": reference_row["guardTrue"],
                "expectedStubbedCallCount": expected_call_count,
                "stubbedCallCount": actual["stubbedCallCount"],
                "expectedBoundedStateWriteCount": expected_write_count,
                "boundedStateWriteCount": actual["boundedStateWriteCount"],
                "referenceObserved": reference_row["observed"],
                "stubbedOriginalCSourceExecuted": True,
                "liveExternalCallPerformed": False,
                "boundedHarnessStateCaptured": True,
                "unboundedMemoryMutationPerformed": False,
                "generatedTargetExecuted": False,
                "reingestedTargetExecuted": False,
            }
        )
    return rows


def build_summary(p108_packet: dict[str, Any], p108_payload: dict[str, Any], rows: list[dict[str, Any]], c_runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p108ValidationPass": p108_packet["validationStatus"] == "pass",
        "p108ClaimFlagsAllFalse": all(value is False for value in p108_packet["claimFlags"].values()),
        "selectedFixtureId": p108_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p108_payload["summary"]["selectedFixtureStillBlocked"],
        "p108ComparisonCount": p108_payload["summary"]["comparisonCount"],
        "p108PassCount": p108_payload["summary"]["passCount"],
        "compilerAvailable": bool(c_runtime["compiler"]),
        "compileReturnCode": c_runtime["compileReturnCode"],
        "runReturnCode": c_runtime["runReturnCode"],
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "guardTrueCount": sum(1 for row in rows if row["guardTrue"]),
        "guardFalseCount": sum(1 for row in rows if not row["guardTrue"]),
        "stubbedCallCount": sum(row["stubbedCallCount"] for row in rows),
        "boundedStateWriteCount": sum(row["boundedStateWriteCount"] for row in rows),
        "maxAbsError": max(row["absError"] for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "allStubbedOriginalCSourceExecuted": all(row["stubbedOriginalCSourceExecuted"] is True for row in rows),
        "allLiveExternalCallsNotPerformed": all(row["liveExternalCallPerformed"] is False for row in rows),
        "allBoundedHarnessStateCaptured": all(row["boundedHarnessStateCaptured"] is True for row in rows),
        "allUnboundedMemoryMutationNotPerformed": all(row["unboundedMemoryMutationPerformed"] is False for row in rows),
        "generatedTargetExecuted": any(row["generatedTargetExecuted"] for row in rows),
        "reingestedTargetExecuted": any(row["reingestedTargetExecuted"] for row in rows),
        "selectedOriginalCStubbedRuntimeEvidenceRecorded": True,
        "sideEffectLoweringImplemented": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "sideEffectMemorySupportClaim": False,
        "loopBackedgeSupportClaim": False,
        "assignmentPhiSupportClaim": False,
        "compoundConditionSupportClaim": False,
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
    p108_packet = read_json(P108_PACKET)
    p108_payload = read_json(P108_RESULT)
    p108.validate_payload(p108_payload)
    reference_rows = p108_payload["runtimeComparison"]["rows"]
    c_runtime = compile_and_run_c(reference_rows)
    observed = parse_runtime_output(c_runtime["runStdout"])
    rows = comparison_rows(p108_payload, observed)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p109-side-effect-original-c-stubbed-runtime-gate",
        "decision": "side_effect_original_c_stubbed_runtime_gate_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P108",
            "packetPath": str(P108_PACKET.relative_to(ROOT)),
            "resultPath": str(P108_RESULT.relative_to(ROOT)),
            "reviewDecision": p108_packet["reviewDecision"],
            "validationStatus": p108_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p108_payload["selectedFixture"]),
        "stubbedExternalCallPolicy": {
            "externalFunction": "update_state",
            "stubKind": "deterministic_sample_supplied_return_value",
            "liveExternalCallPerformed": False,
            "allowedBy": "FEF-P107 external_call_return_injection_v0",
        },
        "boundedStateCapture": {
            "stateCell": "state",
            "captureKind": "harness_local_global_state_cell",
            "unboundedMemoryMutationPerformed": False,
            "allowedBy": "FEF-P107 single_state_cell_no_alias_escape_v0",
        },
        "originalCSourceExecution": {
            "sourceLanguage": "c",
            "compiler": c_runtime["compiler"],
            "compileReturnCode": c_runtime["compileReturnCode"],
            "compileStderr": c_runtime["compileStderr"],
            "runReturnCode": c_runtime["runReturnCode"],
            "sampleCount": len(reference_rows),
            "stubbedOriginalCSourceExecuted": True,
            "liveExternalCallPerformed": False,
            "boundedHarnessStateCaptured": True,
            "generatedTargetExecuted": False,
            "reingestedTargetExecuted": False,
            "rows": rows,
        },
        "summary": build_summary(p108_packet, p108_payload, rows, c_runtime),
        "releaseGates": [
            {"id": "side_effect_original_c_stubbed_runtime_gate", "status": "recorded"},
            {"id": "live_external_call_execution", "status": "not_performed"},
            {"id": "bounded_harness_state_capture", "status": "recorded"},
            {"id": "unbounded_memory_mutation", "status": "not_performed"},
            {"id": "generated_target_runtime_execution", "status": "not_performed"},
            {"id": "side_effect_reingest_execution", "status": "not_performed"},
            {"id": "effect_order_policy", "status": "used_as_harness_precondition_not_implemented"},
            {"id": "external_call_policy", "status": "used_as_harness_precondition_not_implemented"},
            {"id": "memory_alias_policy", "status": "used_as_harness_precondition_not_implemented"},
            {"id": "side_effect_lowering", "status": "blocked"},
            {"id": "side_effect_memory_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P109 compiles and runs the selected original C side-effect fixture with deterministic local external-call stubbing.",
            "All seven selected comparisons pass against the P108 modeled reference table with zero absolute error.",
            "P109 records bounded harness-local state capture only; live external calls, generated targets, and re-ingest remain blocked.",
        ],
        "blockedStatements": [
            "A live external call was performed.",
            "Unbounded memory mutation or aliasing was supported.",
            "Generated side-effect target code was executed.",
            "Re-ingested side-effect code was executed.",
            "Effect-order, external-call, or memory-alias policy was implemented in Forge or eFrog.",
            "Side-effect/call/memory lowering is implemented.",
            "Side-effecting calls or memory operations are generally supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Record generated-target runtime status as blocked until side-effect lowering and codegen policy exists.",
            "Define a selected side-effect lowering proposal only after reviewer acceptance of the P105-P109 evidence ladder.",
            "Record a real private reviewer response if one exists before installing any adapter or lowering.",
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
        "title": "FEF-P109 Side-Effect Original C Stubbed Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "side_effect_original_c_stubbed_runtime_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected original-C stubbed runtime gate only; no live external call, unbounded memory mutation, generated-target execution, re-ingest execution, side-effect lowering, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P109 compiles and runs the selected C fixture with deterministic update_state stubbing.",
            "All seven rows pass against P108 with zero absolute error.",
            "Generated targets and re-ingest remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p109_side_effect_original_c_stubbed_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p109_side_effect_original_c_stubbed_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p109_side_effect_original_c_stubbed_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P109 Side-Effect Original C Stubbed Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record generated-target runtime status as blocked until selected side-effect lowering and codegen policy exists.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Expected | Observed | Stub calls | State writes | Pass |", "|---|---:|---:|---:|---:|---|"]
    for row in payload["originalCSourceExecution"]["rows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['expected']}` | `{row['observed']}` | "
            f"`{row['stubbedCallCount']}` | `{row['boundedStateWriteCount']}` | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P109 Side-Effect Original C Stubbed Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P109 compiles and runs a selected original C side-effect fixture with deterministic local stubbing.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Comparison count: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Guard true count: `{summary['guardTrueCount']}`",
            f"- Guard false count: `{summary['guardFalseCount']}`",
            f"- Stubbed call count: `{summary['stubbedCallCount']}`",
            f"- Bounded state write count: `{summary['boundedStateWriteCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Live external calls performed: `{summary['allLiveExternalCallsNotPerformed'] is False}`",
            f"- Unbounded memory mutation performed: `{summary['allUnboundedMemoryMutationNotPerformed'] is False}`",
            f"- Generated target executed: `{summary['generatedTargetExecuted']}`",
            f"- Re-ingested target executed: `{summary['reingestedTargetExecuted']}`",
            "",
            "## Comparisons",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected original C fixture with deterministic local stubbing only.",
            "- No live external calls performed.",
            "- Bounded harness-local state capture only.",
            "- No generated-target or re-ingested execution.",
            "- No side-effect/call/memory support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P109 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P109 status")
    p108.validate_payload(read_json(P108_RESULT))
    summary = payload["summary"]
    for key in [
        "p108ValidationPass",
        "p108ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "compilerAvailable",
        "allObservedFinite",
        "allStubbedOriginalCSourceExecuted",
        "allLiveExternalCallsNotPerformed",
        "allBoundedHarnessStateCaptured",
        "allUnboundedMemoryMutationNotPerformed",
        "selectedOriginalCStubbedRuntimeEvidenceRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["compileReturnCode"] != 0 or summary["runReturnCode"] != 0:
        raise ValueError("C compile/run must pass")
    if summary["comparisonCount"] != 7:
        raise ValueError("expected seven comparisons")
    if summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("expected seven passing comparisons")
    if summary["guardTrueCount"] != 4 or summary["guardFalseCount"] != 3:
        raise ValueError("unexpected guard distribution")
    if summary["stubbedCallCount"] != 4 or summary["boundedStateWriteCount"] != 4:
        raise ValueError("unexpected stub/write distribution")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("expected zero max abs error")
    for key in [
        "generatedTargetExecuted",
        "reingestedTargetExecuted",
        "sideEffectLoweringImplemented",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "sideEffectMemorySupportClaim",
        "loopBackedgeSupportClaim",
        "assignmentPhiSupportClaim",
        "compoundConditionSupportClaim",
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
    result_path = out_dir / f"fef_p109_side_effect_original_c_stubbed_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p109_side_effect_original_c_stubbed_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p109_side_effect_original_c_stubbed_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p109_side_effect_original_c_stubbed_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p109_side_effect_original_c_stubbed_runtime_gate")
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
    print("FEF_P109_SIDE_EFFECT_ORIGINAL_C_STUBBED_RUNTIME_GATE_OK")
    print(f"comparisons={built['payload']['summary']['comparisonCount']}")
    print(f"pass={built['payload']['summary']['passCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
