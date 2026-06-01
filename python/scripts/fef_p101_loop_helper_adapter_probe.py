#!/usr/bin/env python3
"""FEF-P101 selected loop helper adapter probe for loop re-ingest."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))
if str(EFROG_ROOT) not in sys.path:
    sys.path.insert(0, str(EFROG_ROOT))

from efrog.decompilers.c import decompile_c_source  # noqa: E402
from efrog.decompilers.python import EFrogError  # noqa: E402
from scripts import fef_p100_loop_reingest_execution_probe as p100  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p101_loop_helper_adapter_probe.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P101_LOOP_HELPER_ADAPTER_PROBE_PASS"

P100_PACKET = ROOT / "reports/evidence_packets/fef_p100_loop_reingest_execution_probe.json"
P100_RESULT = ROOT / "python/results/fef_p100_loop_reingest_execution_probe/fef_p100_loop_reingest_execution_probe_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_helper_adapter_probe_claim": False,
    "loop_reingest_parse_success_claim": False,
    "loop_reingest_execution_claim": False,
    "loop_reingest_supported": False,
    "loop_lowering_implemented": False,
    "loop_backedge_support_claim": False,
    "loop_backedge_semantics_implemented": False,
    "loop_boundedness_policy_general_claim": False,
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
    "FEF-P101 records a selected loop helper adapter probe only.",
    "FEF-P101 does not change eFrog or Forge source code.",
    "FEF-P101 does not claim successful re-ingest execution.",
    "FEF-P101 does not execute recompiled Python or compare runtime rows.",
    "FEF-P101 does not install loop lowering in Forge or eFrog.",
    "FEF-P101 does not implement loop headers, latches, variants, or back-edge semantics in Forge or eFrog.",
    "FEF-P101 does not claim loop/back-edge support.",
    "FEF-P101 does not claim general branch/control-flow support.",
    "FEF-P101 does not claim branch/control-flow re-ingest support.",
    "FEF-P101 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P101 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def adapt_selected_loop_helper(source: str) -> dict[str, Any]:
    adapted = source
    replacements = [
        (
            "\n".join(
                [
                    "static int mg_loop_effective_iterations(int n) {",
                    "  return n > 0 ? n : 0;",
                    "}",
                    "",
                    "",
                ]
            ),
            "",
            "remove_selected_loop_helper_definition",
        ),
        (
            "int k = mg_loop_effective_iterations(n);",
            "int k = n > 0 ? n : 0;",
            "inline_selected_loop_effective_iterations_call",
        ),
    ]
    applied = []
    for before, after, replacement_id in replacements:
        if before in adapted:
            adapted = adapted.replace(before, after, 1)
            applied.append(
                {
                    "replacementId": replacement_id,
                    "before": before,
                    "after": after,
                    "applied": True,
                }
            )
        else:
            applied.append(
                {
                    "replacementId": replacement_id,
                    "before": before,
                    "after": after,
                    "applied": False,
                }
            )
    return {
        "adapterId": "selected_loop_helper_inline_adapter_v0",
        "scope": "selected_generated_c_loop_fixture_only",
        "status": "adapter_probe_applied",
        "sourceChanged": adapted != source,
        "replacements": applied,
        "adaptedSource": adapted,
    }


def classify_failure(message: str) -> dict[str, Any]:
    detected = []
    if "call to non-math function" in message and "mg_loop_effective_iterations" in message:
        detected.append("selected_loop_helper_call_unsupported")
    if "if/for/while go to E3+" in message or "C while statement form not supported" in message:
        detected.append("statement_level_loop_shape_unsupported")
    if "unsupported as C branch condition" in message:
        detected.append("loop_condition_unsupported")
    if not detected:
        detected.append("unclassified_reingest_blocker")
    return {
        "failureClass": "efrog_selected_generated_loop_surface_blocked",
        "detectedBlockers": detected,
        "message": message,
    }


def run_adapted_probe(source: str) -> dict[str, Any]:
    try:
        module = decompile_c_source(source, source_path="c_while_accumulate_v0_helper_adapted.c")
    except EFrogError as exc:
        failure = classify_failure(str(exc))
        return {
            "probeId": "selected_loop_helper_adapted_c_fixture_efrog_probe",
            "decompiler": "efrog.decompilers.c.decompile_c_source",
            "invocationPerformed": True,
            "status": "blocked_unexpected_surface",
            "reingestParseSucceeded": False,
            "recompiledPythonExecuted": False,
            "runtimeComparisonExecuted": False,
            "errorType": type(exc).__name__,
            "errorMessage": str(exc),
            "failure": failure,
        }
    eml = module.to_eml()
    return {
        "probeId": "selected_loop_helper_adapted_c_fixture_efrog_probe",
        "decompiler": "efrog.decompilers.c.decompile_c_source",
        "invocationPerformed": True,
        "status": "parse_pass_execution_blocked",
        "reingestParseSucceeded": True,
        "recompiledPythonExecuted": False,
        "runtimeComparisonExecuted": False,
        "functionCount": len(module.functions),
        "emlPreview": eml[:900],
        "failure": {
            "failureClass": "none_parse_pass",
            "detectedBlockers": [],
            "message": "",
        },
    }


def build_summary(p100_packet: dict[str, Any], p100_payload: dict[str, Any], adapter: dict[str, Any], probe: dict[str, Any]) -> dict[str, Any]:
    detected = set(probe["failure"]["detectedBlockers"])
    previous_detected = set(p100_payload["reingestProbe"]["failure"]["detectedBlockers"])
    return {
        "sourcePacketCount": 1,
        "p100ValidationPass": p100_packet["validationStatus"] == "pass",
        "p100ClaimFlagsAllFalse": all(value is False for value in p100_packet["claimFlags"].values()),
        "selectedFixtureId": p100_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p100_payload["summary"]["selectedFixtureStillBlocked"],
        "adapterId": adapter["adapterId"],
        "adapterStatus": adapter["status"],
        "adapterSourceChanged": adapter["sourceChanged"],
        "replacementCount": len(adapter["replacements"]),
        "replacementAppliedCount": sum(1 for item in adapter["replacements"] if item["applied"]),
        "previousBlockerCleared": "selected_loop_helper_call_unsupported" in previous_detected
        and "selected_loop_helper_call_unsupported" not in detected,
        "reingestParseSucceeded": probe["reingestParseSucceeded"],
        "probeStatus": probe["status"],
        "probeInvocationPerformed": probe["invocationPerformed"],
        "detectedBlockerCount": len(probe["failure"]["detectedBlockers"]),
        "reingestExecuted": False,
        "recompiledPythonExecuted": False,
        "runtimeComparisonExecuted": False,
        "loopReingestSupported": False,
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
    p100_packet = read_json(P100_PACKET)
    p100_payload = read_json(P100_RESULT)
    p100.validate_payload(p100_payload)
    source = p100_payload["selectedCodegenFixture"]["source"]
    adapter = adapt_selected_loop_helper(source)
    probe = run_adapted_probe(adapter["adaptedSource"])
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p101-loop-helper-adapter-probe",
        "decision": "selected_loop_helper_adapter_clears_blocker_parse_pass_execution_blocked",
        "sourcePacket": {
            "phase": "P100",
            "packetPath": str(P100_PACKET.relative_to(ROOT)),
            "resultPath": str(P100_RESULT.relative_to(ROOT)),
            "reviewDecision": p100_packet["reviewDecision"],
            "validationStatus": p100_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p100_payload["selectedFixture"]),
        "selectedCodegenFixture": copy.deepcopy(p100_payload["selectedCodegenFixture"]),
        "adapterProbe": {key: value for key, value in adapter.items() if key != "adaptedSource"},
        "reingestProbe": probe,
        "summary": build_summary(p100_packet, p100_payload, adapter, probe),
        "releaseGates": [
            {"id": "selected_loop_helper_adapter_probe", "status": "recorded_parse_pass"},
            {"id": "selected_loop_reingest_execution", "status": "blocked_not_executed"},
            {"id": "recompiled_python_execution", "status": "blocked_not_executed"},
            {"id": "loop_lowering_installation", "status": "not_performed"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "loop_backedge_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P101 records a selected loop helper adapter probe that clears the P100 helper-call blocker locally.",
            "The adapted selected generated loop fixture parses through eFrog.",
            "P101 does not execute recompiled Python or compare runtime rows.",
        ],
        "blockedStatements": [
            "Re-ingested loop code was executed successfully.",
            "Re-ingested Python comparison rows were executed.",
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
            "Execute the parsed selected loop EML/Python comparison gate.",
            "Compare recompiled Python rows against P98 generated C runtime rows.",
            "Record private reviewer response to the P47-P101 branch/control-flow bundle.",
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
        "title": "FEF-P101 Loop Helper Adapter Probe",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_loop_helper_adapter_parse_pass_execution_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected loop helper adapter probe only; no recompiled Python execution, runtime comparison, installed adapter, Forge/eFrog behavior change, loop/back-edge support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P101 locally inlines the selected loop effective-iteration helper.",
            "The adapted selected generated loop fixture parses through eFrog.",
            "Execution and runtime comparison remain blocked for a separate gate.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p101_loop_helper_adapter_probe.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p101_loop_helper_adapter_probe.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p101_loop_helper_adapter_probe.v0",
        "date": DATE,
        "title": "FEF-P101 Loop Helper Adapter Probe",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Execute the parsed selected loop EML/Python comparison gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    replacements = ["| Replacement | Applied |", "|---|---|"]
    for item in payload["adapterProbe"]["replacements"]:
        replacements.append(f"| `{item['replacementId']}` | `{item['applied']}` |")
    return "\n".join(
        [
            "# FEF-P101 Loop Helper Adapter Probe",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P101 records a selected loop helper adapter probe without executing recompiled Python.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Adapter id: `{summary['adapterId']}`",
            f"- Adapter status: `{summary['adapterStatus']}`",
            f"- Adapter source changed: `{summary['adapterSourceChanged']}`",
            f"- Replacement applied count: `{summary['replacementAppliedCount']}`",
            f"- Previous blocker cleared: `{summary['previousBlockerCleared']}`",
            f"- Re-ingest parse succeeded: `{summary['reingestParseSucceeded']}`",
            f"- Probe status: `{summary['probeStatus']}`",
            f"- Recompiled Python executed: `{summary['recompiledPythonExecuted']}`",
            f"- Runtime comparison executed: `{summary['runtimeComparisonExecuted']}`",
            f"- Loop re-ingest supported: `{summary['loopReingestSupported']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Adapter Replacements",
            "",
            *replacements,
            "",
            "## EML Preview",
            "",
            "```text",
            payload["reingestProbe"].get("emlPreview", ""),
            "```",
            "",
            "## Boundary",
            "",
            "- Selected loop helper adapter probe only.",
            "- No installed adapter or Forge/eFrog behavior change.",
            "- No recompiled Python execution or runtime comparison.",
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_adapter(adapter: dict[str, Any]) -> None:
    if adapter["status"] != "adapter_probe_applied":
        raise ValueError("adapter must be applied")
    if adapter["scope"] != "selected_generated_c_loop_fixture_only":
        raise ValueError("adapter scope must remain selected-only")
    if adapter["sourceChanged"] is not True:
        raise ValueError("adapter must change selected source")
    if len(adapter["replacements"]) != 2:
        raise ValueError("unexpected replacement count")
    if sum(1 for item in adapter["replacements"] if item["applied"]) != 2:
        raise ValueError("all selected helper replacements must apply")


def validate_probe(probe: dict[str, Any]) -> None:
    if probe["invocationPerformed"] is not True:
        raise ValueError("probe invocation must be recorded")
    if probe["status"] != "parse_pass_execution_blocked":
        raise ValueError("adapted selected loop fixture should parse while execution remains blocked")
    if probe["reingestParseSucceeded"] is not True:
        raise ValueError("P101 must clear the helper blocker enough to parse")
    if probe["recompiledPythonExecuted"] is not False or probe["runtimeComparisonExecuted"] is not False:
        raise ValueError("P101 must not execute recompiled Python or runtime comparison")
    if probe["failure"]["detectedBlockers"]:
        raise ValueError("adapted helper probe should not retain detected blockers")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P101 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P101 status")
    p100.validate_payload(read_json(P100_RESULT))
    validate_adapter(payload["adapterProbe"])
    validate_probe(payload["reingestProbe"])
    summary = payload["summary"]
    for key in [
        "p100ValidationPass",
        "p100ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "adapterSourceChanged",
        "previousBlockerCleared",
        "reingestParseSucceeded",
        "probeInvocationPerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["replacementAppliedCount"] != 2:
        raise ValueError("expected two applied replacements")
    if summary["detectedBlockerCount"] != 0:
        raise ValueError("helper blocker should be cleared in P101")
    for key in [
        "reingestExecuted",
        "recompiledPythonExecuted",
        "runtimeComparisonExecuted",
        "loopReingestSupported",
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
    result_path = out_dir / f"fef_p101_loop_helper_adapter_probe_{STAMP}.json"
    report_path = report_dir / f"fef_p101_loop_helper_adapter_probe_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p101_loop_helper_adapter_probe.json"
    feed_path = command_feed_dir / f"fef_p101_loop_helper_adapter_probe_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p101_loop_helper_adapter_probe")
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
    print("FEF_P101_LOOP_HELPER_ADAPTER_PROBE_OK")
    print(f"probe_status={built['payload']['summary']['probeStatus']}")
    print(f"parse_succeeded={built['payload']['summary']['reingestParseSucceeded']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
