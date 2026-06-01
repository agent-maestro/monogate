#!/usr/bin/env python3
"""FEF-P102 parsed selected-loop EML/Python comparison gate."""

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

from scripts import fef_p101_loop_helper_adapter_probe as p101  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p102_loop_parsed_eml_python_comparison.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P102_LOOP_PARSED_EML_PYTHON_COMPARISON_PASS"

P101_PACKET = ROOT / "reports/evidence_packets/fef_p101_loop_helper_adapter_probe.json"
P101_RESULT = ROOT / "python/results/fef_p101_loop_helper_adapter_probe/fef_p101_loop_helper_adapter_probe_2026_05_31.json"
P98_RESULT = ROOT / "python/results/fef_p98_loop_generated_target_runtime_gate/fef_p98_loop_generated_target_runtime_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_parsed_eml_python_comparison_claim": False,
    "loop_reingest_parse_success_claim": False,
    "loop_reingest_execution_claim": False,
    "loop_reingest_supported": False,
    "loop_lowering_implemented": False,
    "loop_backedge_support_claim": False,
    "loop_backedge_semantics_implemented": False,
    "loop_boundedness_policy_general_claim": False,
    "selected_loop_helper_adapter_installed": False,
    "selected_codegen_fixture_installed": False,
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
    "FEF-P102 executes only a selected parsed-EML-shaped Python comparison for the P101 adapted loop fixture.",
    "FEF-P102 compares the parsed EML shape against the P98 selected generated C runtime rows.",
    "FEF-P102 does not execute a Forge-recompiled Python target.",
    "FEF-P102 does not change eFrog or Forge source code.",
    "FEF-P102 does not install the selected loop helper adapter in eFrog or Forge.",
    "FEF-P102 does not install loop lowering in Forge or eFrog.",
    "FEF-P102 does not implement loop headers, latches, variants, or back-edge semantics in Forge or eFrog.",
    "FEF-P102 does not claim loop/back-edge support.",
    "FEF-P102 does not claim general branch/control-flow support.",
    "FEF-P102 does not claim branch/control-flow re-ingest support.",
    "FEF-P102 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P102 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def step01(value: float) -> float:
    return max(0.0, min(1.0, value * 1.0e30))


def evaluate_p101_parsed_eml_shape(x: float, n: float) -> dict[str, float]:
    n_as_real = float(n)
    k = 0.0 + (n_as_real - 0.0) * step01(n_as_real - 0.0)
    observed = float(x) * k
    return {
        "step01Input": n_as_real - 0.0,
        "step01Value": step01(n_as_real - 0.0),
        "k": k,
        "observed": observed,
    }


def build_comparison_rows(p98_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in p98_payload["runtimeComparison"]["rows"]:
        inputs = row["inputs"]
        values = evaluate_p101_parsed_eml_shape(float(inputs["x"]), float(inputs["n"]))
        observed = values["observed"]
        expected = float(row["observed"])
        abs_error = abs(observed - expected)
        rows.append(
            {
                "sampleId": row["sampleId"],
                "path": row["path"],
                "inputs": dict(inputs),
                "effectiveIterationCount": row["effectiveIterationCount"],
                "p98GeneratedTargetObserved": expected,
                "p98Expected": float(row["expected"]),
                "parsedEmlPythonObserved": observed,
                "absError": abs_error,
                "pass": math.isfinite(observed) and abs_error <= 1.0e-12,
                "executionStatus": "executed_selected_parsed_eml_python_shape",
                "intermediates": values,
            }
        )
    return rows


def build_comparison_result(p101_payload: dict[str, Any], p98_payload: dict[str, Any]) -> dict[str, Any]:
    rows = build_comparison_rows(p98_payload)
    return {
        "harnessId": "selected_loop_parsed_eml_python_comparison_harness_v0",
        "scope": "p101_adapted_parsed_eml_shape_against_p98_generated_c_rows",
        "sourceEmlPreview": p101_payload["reingestProbe"]["emlPreview"],
        "comparisonKind": "selected_parsed_eml_python_against_generated_c_loop_runtime_rows",
        "rowCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"] is True),
        "failCount": sum(1 for row in rows if row["pass"] is False),
        "maxAbsError": max((row["absError"] for row in rows), default=0.0),
        "allRowsFinite": all(math.isfinite(float(row["parsedEmlPythonObserved"])) for row in rows),
        "allRowsPass": all(row["pass"] is True for row in rows),
        "parsedEmlPythonExecuted": True,
        "p98GeneratedTargetRowsConsumed": True,
        "recompiledPythonTargetExecuted": False,
        "installedAdapterUsed": False,
        "rows": rows,
    }


def build_summary(
    p101_packet: dict[str, Any],
    p101_payload: dict[str, Any],
    p98_payload: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    return {
        "sourcePacketCount": 2,
        "p101ValidationPass": p101_packet["validationStatus"] == "pass",
        "p101ClaimFlagsAllFalse": all(value is False for value in p101_packet["claimFlags"].values()),
        "p101ReingestParseSucceeded": p101_payload["summary"]["reingestParseSucceeded"],
        "p101PreviousBlockerCleared": p101_payload["summary"]["previousBlockerCleared"],
        "p98RuntimeRowsPass": p98_payload["summary"]["passCount"] == p98_payload["summary"]["comparisonCount"]
        and p98_payload["summary"]["failCount"] == 0,
        "selectedFixtureId": p101_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p101_payload["summary"]["selectedFixtureStillBlocked"],
        "harnessId": comparison["harnessId"],
        "comparisonKind": comparison["comparisonKind"],
        "rowCount": comparison["rowCount"],
        "passCount": comparison["passCount"],
        "failCount": comparison["failCount"],
        "maxAbsError": comparison["maxAbsError"],
        "allRowsFinite": comparison["allRowsFinite"],
        "allRowsPass": comparison["allRowsPass"],
        "parsedEmlPythonComparisonPerformed": True,
        "runtimeComparisonPerformed": True,
        "recompiledPythonTargetExecuted": False,
        "loopReingestSupported": False,
        "selectedLoopHelperAdapterInstalled": False,
        "selectedCodegenFixtureInstalled": False,
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "loopLoweringImplemented": False,
        "loopBackedgeSupportClaim": False,
        "loopBackedgeSemanticsImplemented": False,
        "loopBoundednessPolicyGeneralClaim": False,
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
    p101_packet = read_json(P101_PACKET)
    p101_payload = read_json(P101_RESULT)
    p98_payload = read_json(P98_RESULT)
    p101.validate_payload(p101_payload)
    comparison = build_comparison_result(p101_payload, p98_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p102-loop-parsed-eml-python-comparison",
        "decision": "selected_loop_parsed_eml_python_comparison_recorded_installed_support_blocked",
        "sourcePackets": [
            {
                "phase": "P101",
                "packetPath": str(P101_PACKET.relative_to(ROOT)),
                "resultPath": str(P101_RESULT.relative_to(ROOT)),
                "reviewDecision": p101_packet["reviewDecision"],
                "validationStatus": p101_packet["validationStatus"],
            },
            {
                "phase": "P98",
                "resultPath": str(P98_RESULT.relative_to(ROOT)),
                "reviewDecision": p98_payload["decision"],
                "status": p98_payload["status"],
            },
        ],
        "selectedFixture": copy.deepcopy(p101_payload["selectedFixture"]),
        "adapterProbe": copy.deepcopy(p101_payload["adapterProbe"]),
        "reingestProbe": copy.deepcopy(p101_payload["reingestProbe"]),
        "comparisonResult": comparison,
        "summary": build_summary(p101_packet, p101_payload, p98_payload, comparison),
        "releaseGates": [
            {"id": "selected_loop_reingest_parse", "status": "recorded_by_p101"},
            {"id": "selected_parsed_eml_python_comparison", "status": "recorded"},
            {"id": "recompiled_python_target_execution", "status": "not_performed"},
            {"id": "loop_helper_adapter_installation", "status": "not_performed"},
            {"id": "loop_lowering_installation", "status": "not_performed"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "loop_backedge_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P102 executes the selected parsed-EML-shaped Python comparison for the P101 adapted loop fixture.",
            "All seven P98 generated C runtime rows match the parsed EML shape with max absolute error 0.0.",
            "P102 preserves the boundary that no selected loop helper adapter is installed in eFrog or Forge.",
        ],
        "blockedStatements": [
            "A Forge-recompiled Python target was executed.",
            "Loop re-ingest is supported.",
            "The selected loop helper adapter is installed in eFrog or Forge.",
            "Loop header, latch, variant, or back-edge semantics are implemented in Forge or eFrog.",
            "Loop lowering is implemented.",
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
            "Record a selected loop helper adapter installation candidate before any behavior change.",
            "Keep loop/back-edge support blocked until installed lowering and re-ingest execution evidence exist.",
            "Record private reviewer response to the P47-P102 branch/control-flow bundle.",
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
        "title": "FEF-P102 Loop Parsed-EML Python Comparison",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_loop_parsed_eml_python_comparison_pass_installed_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected parsed-EML-shaped Python comparison only; no Forge-recompiled Python target execution, installed adapter, Forge/eFrog behavior change, loop/back-edge support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P102 consumes the P101 parsed loop EML shape.",
            "All seven P98 generated C runtime rows match with zero observed error.",
            "Installed loop adapter and general loop support remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p102_loop_parsed_eml_python_comparison.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p102_loop_parsed_eml_python_comparison.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p102_loop_parsed_eml_python_comparison.v0",
        "date": DATE,
        "title": "FEF-P102 Loop Parsed-EML Python Comparison",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record a selected loop helper adapter installation candidate before any behavior change.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        "| Sample | n | x | P98 observed | Parsed EML observed | abs error | pass |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["comparisonResult"]["rows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['inputs']['n']}` | `{row['inputs']['x']}` | "
            f"`{row['p98GeneratedTargetObserved']}` | `{row['parsedEmlPythonObserved']}` | "
            f"`{row['absError']}` | `{row['pass']}` |"
        )
    return "\n".join(
        [
            "# FEF-P102 Loop Parsed-EML Python Comparison",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P102 executes the selected parsed-EML-shaped Python comparison after the P101 parse pass.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Harness: `{summary['harnessId']}`",
            f"- Rows compared: `{summary['rowCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- P101 parse succeeded: `{summary['p101ReingestParseSucceeded']}`",
            f"- Parsed EML/Python comparison performed: `{summary['parsedEmlPythonComparisonPerformed']}`",
            f"- Forge-recompiled Python target executed: `{summary['recompiledPythonTargetExecuted']}`",
            f"- Selected adapter installed: `{summary['selectedLoopHelperAdapterInstalled']}`",
            f"- Loop re-ingest supported: `{summary['loopReingestSupported']}`",
            "",
            "## Rows",
            "",
            *rows,
            "",
            "## Parsed EML Shape",
            "",
            "```text",
            payload["comparisonResult"]["sourceEmlPreview"],
            "```",
            "",
            "## Boundary",
            "",
            "- Selected parsed-EML-shaped Python comparison only.",
            "- No Forge-recompiled Python target execution.",
            "- No installed eFrog or Forge adapter.",
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P102 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P102 status")
    p101.validate_payload(read_json(P101_RESULT))
    summary = payload["summary"]
    for key in [
        "p101ValidationPass",
        "p101ClaimFlagsAllFalse",
        "p101ReingestParseSucceeded",
        "p101PreviousBlockerCleared",
        "p98RuntimeRowsPass",
        "selectedFixtureStillBlocked",
        "allRowsFinite",
        "allRowsPass",
        "parsedEmlPythonComparisonPerformed",
        "runtimeComparisonPerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["rowCount"] != 7:
        raise ValueError("expected seven selected loop comparison rows")
    if summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("expected all selected loop comparison rows to pass")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("expected exact selected loop parsed-EML agreement")
    if payload["comparisonResult"]["comparisonKind"] != "selected_parsed_eml_python_against_generated_c_loop_runtime_rows":
        raise ValueError("unexpected comparison kind")
    if "let k = 0.0 + (n - (0.0)) * step01((n) - (0.0));" not in payload["comparisonResult"]["sourceEmlPreview"]:
        raise ValueError("expected P101 parsed loop EML shape")
    for key in [
        "recompiledPythonTargetExecuted",
        "loopReingestSupported",
        "selectedLoopHelperAdapterInstalled",
        "selectedCodegenFixtureInstalled",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "loopLoweringImplemented",
        "loopBackedgeSupportClaim",
        "loopBackedgeSemanticsImplemented",
        "loopBoundednessPolicyGeneralClaim",
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
    result_path = out_dir / f"fef_p102_loop_parsed_eml_python_comparison_{STAMP}.json"
    report_path = report_dir / f"fef_p102_loop_parsed_eml_python_comparison_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p102_loop_parsed_eml_python_comparison.json"
    feed_path = command_feed_dir / f"fef_p102_loop_parsed_eml_python_comparison_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p102_loop_parsed_eml_python_comparison")
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
    print("FEF_P102_LOOP_PARSED_EML_PYTHON_COMPARISON_OK")
    print(f"rows={built['payload']['summary']['rowCount']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
