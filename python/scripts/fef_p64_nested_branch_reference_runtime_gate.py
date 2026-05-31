#!/usr/bin/env python3
"""FEF-P64 reference-runtime gate for the selected nested-branch samples."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p63_nested_branch_expected_samples as p63

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p64_nested_branch_reference_runtime_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P64_NESTED_BRANCH_REFERENCE_RUNTIME_GATE_PASS"

P63_PACKET = ROOT / "reports/evidence_packets/fef_p63_nested_branch_expected_samples.json"
P63_RESULT = ROOT / "python/results/fef_p63_nested_branch_expected_samples/fef_p63_nested_branch_expected_samples_2026_05_31.json"

CLAIM_FLAGS = {
    "nested_branch_reference_runtime_gate_claim": False,
    "nested_branch_source_execution_claim": False,
    "nested_branch_generated_target_execution_claim": False,
    "nested_branch_reingest_execution_claim": False,
    "nested_branch_lowering_claim": False,
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
    "FEF-P64 executes a local Python reference evaluator for the P63 expected-sample table only.",
    "FEF-P64 does not execute the original C nested-branch source.",
    "FEF-P64 does not execute generated target code.",
    "FEF-P64 does not execute re-ingested code.",
    "FEF-P64 does not implement nested branch lowering.",
    "FEF-P64 does not widen Forge or eFrog frontend lowering.",
    "FEF-P64 does not claim nested branch support.",
    "FEF-P64 does not claim general branch/control-flow support.",
    "FEF-P64 does not claim branch/control-flow re-ingest support.",
    "FEF-P64 does not claim full non-generated source roundtrip.",
    "FEF-P64 does not claim arbitrary C/Rust source-family support.",
    "FEF-P64 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P64 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reference_runtime(x: float, y: float) -> float:
    """Reference-only mirror of the selected fixture's source semantics."""
    if x > 0.0:
        if y > 0.0:
            return x + y
    return 0.0


def comparison_rows(p63_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for sample in p63_payload["expectedSamples"]:
        x = float(sample["inputs"]["x"])
        y = float(sample["inputs"]["y"])
        observed = reference_runtime(x, y)
        expected = float(sample["expected"])
        abs_error = abs(observed - expected)
        rows.append(
            {
                "sampleId": sample["sampleId"],
                "inputs": copy.deepcopy(sample["inputs"]),
                "expected": expected,
                "observed": observed,
                "absError": abs_error,
                "pass": math.isfinite(observed) and abs_error == 0.0,
                "path": sample["path"],
                "referenceRuntimeOnly": True,
                "sourceOrGeneratedCodeExecuted": False,
            }
        )
    return rows


def build_summary(p63_packet: dict[str, Any], p63_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p63ValidationPass": p63_packet["validationStatus"] == "pass",
        "p63ClaimFlagsAllFalse": all(value is False for value in p63_packet["claimFlags"].values()),
        "selectedFixtureId": p63_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p63_payload["summary"]["selectedFixtureStillBlocked"],
        "comparisonCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"]),
        "failCount": sum(1 for row in rows if not row["pass"]),
        "maxAbsError": max(row["absError"] for row in rows),
        "allObservedFinite": all(math.isfinite(row["observed"]) for row in rows),
        "allReferenceRuntimeOnly": all(row["referenceRuntimeOnly"] is True for row in rows),
        "sourceOrGeneratedCodeExecuted": any(row["sourceOrGeneratedCodeExecuted"] for row in rows),
        "nestedBranchSourceExecutionClaim": False,
        "nestedBranchGeneratedTargetExecutionClaim": False,
        "nestedBranchReingestExecutionClaim": False,
        "nestedBranchLoweringClaim": False,
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
    p63_packet = read_json(P63_PACKET)
    p63_payload = read_json(P63_RESULT)
    p63.validate_payload(p63_payload)
    rows = comparison_rows(p63_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p64-nested-branch-reference-runtime-gate",
        "decision": "nested_branch_reference_runtime_gate_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P63",
            "packetPath": str(P63_PACKET.relative_to(ROOT)),
            "resultPath": str(P63_RESULT.relative_to(ROOT)),
            "reviewDecision": p63_packet["reviewDecision"],
            "validationStatus": p63_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p63_payload["selectedFixture"]),
        "runtimeComparison": {
            "comparisonKind": "local_python_reference_runtime_against_expected_samples",
            "sourceLanguage": "python_reference_harness",
            "originalSourceExecuted": False,
            "generatedTargetExecuted": False,
            "reingestedTargetExecuted": False,
            "rows": rows,
        },
        "summary": build_summary(p63_packet, p63_payload, rows),
        "releaseGates": [
            {"id": "nested_branch_reference_runtime_gate", "status": "recorded"},
            {"id": "original_c_nested_branch_runtime_execution", "status": "not_performed"},
            {"id": "generated_target_runtime_execution", "status": "not_performed"},
            {"id": "nested_branch_reingest_execution", "status": "not_performed"},
            {"id": "nested_branch_lowering", "status": "blocked"},
            {"id": "nested_branch_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P64 runs a local Python reference evaluator over the P63 expected samples.",
            "The selected nested branch fixture still remains blocked for lowering and support.",
            "P64 is a runtime-table consistency gate, not generated target evidence.",
        ],
        "blockedStatements": [
            "The original C nested branch source was executed.",
            "Generated nested branch target code was executed.",
            "Re-ingested nested branch code was executed.",
            "Nested branch lowering is implemented.",
            "Nested branches are supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Replace the reference harness with original-source execution for the selected fixture.",
            "Build an assignment/phi fixture gate for dominance and merge semantics.",
            "Keep nested branch support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P64 Nested Branch Reference Runtime Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "reference_runtime_table_consistency_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Reference-runtime table consistency only; no original C execution, generated target execution, re-ingest execution, nested branch lowering, nested branch support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P64 compares a local Python reference evaluator against all P63 expected samples.",
            "All seven comparisons pass with zero absolute error.",
            "The selected nested branch fixture remains blocked for implementation/support claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p64_nested_branch_reference_runtime_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p64_nested_branch_reference_runtime_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p64_nested_branch_reference_runtime_gate.v0",
        "date": DATE,
        "title": "FEF-P64 Nested Branch Reference Runtime Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Replace the reference harness with original-source execution for the selected fixture.",
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
            "# FEF-P64 Nested Branch Reference Runtime Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P64 compares the P63 expected samples against a local Python reference evaluator.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- Comparisons: `{summary['comparisonCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Reference runtime only: `{summary['allReferenceRuntimeOnly']}`",
            f"- Original/generated code executed: `{summary['sourceOrGeneratedCodeExecuted']}`",
            f"- Nested branch source execution claim: `{summary['nestedBranchSourceExecutionClaim']}`",
            f"- Nested branch lowering claim: `{summary['nestedBranchLoweringClaim']}`",
            f"- Nested branch support claim: `{summary['nestedBranchSupportClaim']}`",
            "",
            "## Comparisons",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Reference-runtime table consistency only.",
            "- No original C nested branch source execution.",
            "- No generated target or re-ingested target execution.",
            "- No nested branch lowering or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_row(row: dict[str, Any]) -> None:
    observed = reference_runtime(float(row["inputs"]["x"]), float(row["inputs"]["y"]))
    if row["observed"] != observed:
        raise ValueError("observed value does not match reference runtime")
    if row["expected"] != observed:
        raise ValueError("expected value does not match reference runtime")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("reference runtime comparison must pass exactly")
    if row["referenceRuntimeOnly"] is not True:
        raise ValueError("row must remain reference-runtime-only")
    if row["sourceOrGeneratedCodeExecuted"] is not False:
        raise ValueError("row must not execute source or generated code")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P64 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P64 status")
    p63.validate_payload(read_json(P63_RESULT))
    for row in payload["runtimeComparison"]["rows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p63ValidationPass",
        "p63ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allObservedFinite",
        "allReferenceRuntimeOnly",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["comparisonCount"] != 7 or summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("unexpected comparison counts")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("maxAbsError must be zero")
    for key in [
        "sourceOrGeneratedCodeExecuted",
        "nestedBranchSourceExecutionClaim",
        "nestedBranchGeneratedTargetExecutionClaim",
        "nestedBranchReingestExecutionClaim",
        "nestedBranchLoweringClaim",
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
    result_path = out_dir / f"fef_p64_nested_branch_reference_runtime_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p64_nested_branch_reference_runtime_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p64_nested_branch_reference_runtime_gate.json"
    feed_path = command_feed_dir / f"fef_p64_nested_branch_reference_runtime_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p64_nested_branch_reference_runtime_gate")
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
    print("FEF_P64_NESTED_BRANCH_REFERENCE_RUNTIME_GATE_OK")
    print(f"comparisons={built['payload']['summary']['comparisonCount']}")
    print(f"pass_count={built['payload']['summary']['passCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
