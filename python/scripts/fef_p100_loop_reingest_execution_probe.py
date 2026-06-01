#!/usr/bin/env python3
"""FEF-P100 selected re-ingest execution probe for the generated loop fixture."""

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
from scripts import fef_p99_loop_reingest_policy as p99  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p100_loop_reingest_execution_probe.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P100_LOOP_REINGEST_EXECUTION_PROBE_PASS"

P99_PACKET = ROOT / "reports/evidence_packets/fef_p99_loop_reingest_policy.json"
P99_RESULT = ROOT / "python/results/fef_p99_loop_reingest_policy/fef_p99_loop_reingest_policy_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_reingest_execution_probe_claim": False,
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
    "FEF-P100 invokes the selected eFrog C re-ingest probe and records the fail-closed result.",
    "FEF-P100 does not claim successful re-ingest execution.",
    "FEF-P100 does not install loop lowering in Forge or eFrog.",
    "FEF-P100 does not change Forge or eFrog lowering behavior.",
    "FEF-P100 does not implement loop headers, latches, variants, or back-edge semantics in Forge or eFrog.",
    "FEF-P100 does not claim loop/back-edge support.",
    "FEF-P100 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P100 does not claim general branch/control-flow support.",
    "FEF-P100 does not claim branch/control-flow re-ingest support.",
    "FEF-P100 does not claim full non-generated source roundtrip.",
    "FEF-P100 does not claim arbitrary C/Rust source-family support.",
    "FEF-P100 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P100 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def run_reingest_probe(source: str) -> dict[str, Any]:
    try:
        module = decompile_c_source(source, source_path="c_while_accumulate_v0_generated_fixture.c")
    except EFrogError as exc:
        failure = classify_failure(str(exc))
        return {
            "probeId": "selected_generated_loop_c_fixture_efrog_reingest_probe",
            "sourceLanguage": "c",
            "decompiler": "efrog.decompilers.c.decompile_c_source",
            "invocationPerformed": True,
            "status": "blocked_expected_unsupported_surface",
            "reingestExecuted": False,
            "recompiledPythonExecuted": False,
            "runtimeComparisonExecuted": False,
            "errorType": type(exc).__name__,
            "errorMessage": str(exc),
            "failure": failure,
        }
    eml = module.to_eml()
    return {
        "probeId": "selected_generated_loop_c_fixture_efrog_reingest_probe",
        "sourceLanguage": "c",
        "decompiler": "efrog.decompilers.c.decompile_c_source",
        "invocationPerformed": True,
        "status": "unexpected_pass_policy_requires_review",
        "reingestExecuted": True,
        "recompiledPythonExecuted": False,
        "runtimeComparisonExecuted": False,
        "functionCount": len(module.functions),
        "emlPreview": eml[:500],
        "failure": {
            "failureClass": "none_unexpected_pass",
            "detectedBlockers": [],
            "message": "",
        },
    }


def blocker_requirements(probe: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = set(probe["failure"]["detectedBlockers"])
    return [
        {
            "requirementId": "support_selected_loop_effective_iteration_helper",
            "status": "required_before_reingest_execution",
            "linkedBlockerDetected": "selected_loop_helper_call_unsupported" in blockers,
        },
        {
            "requirementId": "support_selected_closed_form_loop_return",
            "status": "required_before_reingest_execution",
            "linkedBlockerDetected": True,
        },
        {
            "requirementId": "reject_unbounded_or_data_dependent_loop_surfaces",
            "status": "must_remain_fail_closed",
            "linkedBlockerDetected": True,
        },
        {
            "requirementId": "compile_reingested_eml_to_python_and_compare_p98_rows",
            "status": "blocked_until_reingest_parse_passes",
            "linkedBlockerDetected": True,
        },
    ]


def build_summary(p99_packet: dict[str, Any], p99_payload: dict[str, Any], probe: dict[str, Any], requirements: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = probe["status"] == "blocked_expected_unsupported_surface"
    return {
        "sourcePacketCount": 1,
        "p99ValidationPass": p99_packet["validationStatus"] == "pass",
        "p99ClaimFlagsAllFalse": all(value is False for value in p99_packet["claimFlags"].values()),
        "selectedFixtureId": p99_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p99_payload["summary"]["selectedFixtureStillBlocked"],
        "p99PolicyRecorded": p99_payload["summary"]["reingestPolicyRecorded"],
        "p99RequiredComparisonRowCount": p99_payload["summary"]["requiredComparisonRowCount"],
        "probeInvocationPerformed": probe["invocationPerformed"],
        "probeStatus": probe["status"],
        "probeBlockedExpectedUnsupportedSurface": blocked,
        "detectedBlockerCount": len(probe["failure"]["detectedBlockers"]),
        "requirementCount": len(requirements),
        "linkedRequirementCount": sum(1 for item in requirements if item["linkedBlockerDetected"]),
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
    p99_packet = read_json(P99_PACKET)
    p99_payload = read_json(P99_RESULT)
    p99.validate_payload(p99_payload)
    source = p99_payload["selectedCodegenFixture"]["source"]
    probe = run_reingest_probe(source)
    requirements = blocker_requirements(probe)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p100-loop-reingest-execution-probe",
        "decision": "selected_loop_reingest_probe_blocked_expected_surface",
        "sourcePacket": {
            "phase": "P99",
            "packetPath": str(P99_PACKET.relative_to(ROOT)),
            "resultPath": str(P99_RESULT.relative_to(ROOT)),
            "reviewDecision": p99_packet["reviewDecision"],
            "validationStatus": p99_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p99_payload["selectedFixture"]),
        "selectedCodegenFixture": copy.deepcopy(p99_payload["selectedCodegenFixture"]),
        "reingestPolicy": copy.deepcopy(p99_payload["reingestPolicy"]),
        "reingestProbe": probe,
        "blockerRequirements": requirements,
        "summary": build_summary(p99_packet, p99_payload, probe, requirements),
        "releaseGates": [
            {"id": "selected_loop_reingest_probe_invocation", "status": "performed_blocked_expected_surface"},
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
            "P100 invokes the selected eFrog C re-ingest probe and records the fail-closed blocker.",
            "The selected generated loop fixture is not re-ingested successfully yet.",
            "P100 identifies concrete blocker requirements before a selected re-ingest pass can be recorded.",
        ],
        "blockedStatements": [
            "Re-ingested loop code was executed successfully.",
            "Re-ingested Python comparison rows were executed.",
            "Loop re-ingest is supported.",
            "Generated loop runtime support is installed in Forge or eFrog.",
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
            "Teach eFrog the selected loop effective-iteration helper surface, or add a selected re-ingest adapter.",
            "Re-run the selected generated loop re-ingest gate after the parse blocker is cleared.",
            "Record private reviewer response to the P47-P100 branch/control-flow bundle.",
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
        "title": "FEF-P100 Loop Re-ingest Execution Probe",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_loop_reingest_probe_invoked_blocked_expected_surface",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected loop re-ingest execution probe only; eFrog re-ingest remains blocked, with no successful re-ingest execution, loop lowering installation, Forge/eFrog behavior change, loop/back-edge support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P100 invokes the selected eFrog C re-ingest probe.",
            "The probe blocks on the selected generated loop helper surface.",
            "The next step is an eFrog selected-surface adapter or parser support before execution evidence can pass.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p100_loop_reingest_execution_probe.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p100_loop_reingest_execution_probe.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p100_loop_reingest_execution_probe.v0",
        "date": DATE,
        "title": "FEF-P100 Loop Re-ingest Execution Probe",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add selected loop helper adapter or eFrog support before re-ingest execution can pass.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    requirements = ["| Requirement | Status | Linked Blocker |", "|---|---|---|"]
    for item in payload["blockerRequirements"]:
        requirements.append(
            f"| `{item['requirementId']}` | `{item['status']}` | `{item['linkedBlockerDetected']}` |"
        )
    blockers = ", ".join(f"`{item}`" for item in payload["reingestProbe"]["failure"]["detectedBlockers"])
    return "\n".join(
        [
            "# FEF-P100 Loop Re-ingest Execution Probe",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P100 invokes the selected eFrog C re-ingest probe and records the fail-closed result.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Probe status: `{summary['probeStatus']}`",
            f"- Probe invocation performed: `{summary['probeInvocationPerformed']}`",
            f"- Blocked expected unsupported surface: `{summary['probeBlockedExpectedUnsupportedSurface']}`",
            f"- Detected blocker count: `{summary['detectedBlockerCount']}`",
            f"- Detected blockers: {blockers}",
            f"- Re-ingest executed: `{summary['reingestExecuted']}`",
            f"- Recompiled Python executed: `{summary['recompiledPythonExecuted']}`",
            f"- Runtime comparison executed: `{summary['runtimeComparisonExecuted']}`",
            f"- Loop re-ingest supported: `{summary['loopReingestSupported']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Probe Error",
            "",
            "```text",
            payload["reingestProbe"].get("errorMessage", ""),
            "```",
            "",
            "## Blocker Requirements",
            "",
            *requirements,
            "",
            "## Boundary",
            "",
            "- Selected re-ingest execution probe only.",
            "- No successful eFrog re-ingest execution.",
            "- No recompiled Python execution or runtime comparison.",
            "- No Forge/eFrog behavior change or loop lowering installation.",
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_probe(probe: dict[str, Any]) -> None:
    if probe["invocationPerformed"] is not True:
        raise ValueError("probe invocation must be recorded")
    if probe["status"] != "blocked_expected_unsupported_surface":
        raise ValueError("P100 expects the selected loop helper surface to remain blocked")
    if probe["reingestExecuted"] is not False:
        raise ValueError("P100 must not record successful re-ingest execution")
    if probe["recompiledPythonExecuted"] is not False or probe["runtimeComparisonExecuted"] is not False:
        raise ValueError("P100 must not execute recompiled Python or runtime comparison")
    if "selected_loop_helper_call_unsupported" not in probe["failure"]["detectedBlockers"]:
        raise ValueError("selected loop helper blocker must be detected")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P100 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P100 status")
    p99.validate_payload(read_json(P99_RESULT))
    validate_probe(payload["reingestProbe"])
    summary = payload["summary"]
    for key in [
        "p99ValidationPass",
        "p99ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "p99PolicyRecorded",
        "probeInvocationPerformed",
        "probeBlockedExpectedUnsupportedSurface",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["p99RequiredComparisonRowCount"] != 7:
        raise ValueError("expected seven required comparison rows from P99")
    if summary["detectedBlockerCount"] < 1 or summary["linkedRequirementCount"] < 3:
        raise ValueError("expected linked blocker requirements")
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
    result_path = out_dir / f"fef_p100_loop_reingest_execution_probe_{STAMP}.json"
    report_path = report_dir / f"fef_p100_loop_reingest_execution_probe_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p100_loop_reingest_execution_probe.json"
    feed_path = command_feed_dir / f"fef_p100_loop_reingest_execution_probe_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p100_loop_reingest_execution_probe")
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
    print("FEF_P100_LOOP_REINGEST_EXECUTION_PROBE_OK")
    print(f"probe_status={built['payload']['summary']['probeStatus']}")
    print(f"detected_blockers={built['payload']['summary']['detectedBlockerCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
