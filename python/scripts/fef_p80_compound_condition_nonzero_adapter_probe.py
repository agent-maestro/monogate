#!/usr/bin/env python3
"""FEF-P80 selected nonzero-predicate adapter probe for compound-condition re-ingest."""

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
from scripts import fef_p79_compound_condition_reingest_execution_probe as p79  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p80_compound_condition_nonzero_adapter_probe.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P80_COMPOUND_CONDITION_NONZERO_ADAPTER_PROBE_PASS"

P79_PACKET = ROOT / "reports/evidence_packets/fef_p79_compound_condition_reingest_execution_probe.json"
P79_RESULT = ROOT / "python/results/fef_p79_compound_condition_reingest_execution_probe/fef_p79_compound_condition_reingest_execution_probe_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_nonzero_adapter_probe_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_reingest_supported": False,
    "compound_condition_lowering_implemented": False,
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
    "FEF-P80 records a selected nonzero-predicate source adapter probe only.",
    "FEF-P80 does not change eFrog or Forge source code.",
    "FEF-P80 does not claim successful re-ingest execution.",
    "FEF-P80 does not install helper functions in Forge or eFrog.",
    "FEF-P80 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P80 does not claim compound-condition support.",
    "FEF-P80 does not claim branch/control-flow re-ingest support.",
    "FEF-P80 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P80 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def adapt_selected_nonzero_predicates(source: str) -> dict[str, Any]:
    adapted = source
    replacements = [
        (
            "return value != 0.0 ? 1.0 : 0.0;",
            "return step01(value * value);",
            "nonzero01_helper_condition",
        ),
        (
            "return guard != 0.0 ? numerator / denominator : default_value;",
            "return default_value + (numerator / denominator - (default_value)) * step01(guard * guard);",
            "guarded_div_helper_condition",
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
        "adapterId": "selected_nonzero_predicate_branch_free_adapter_v0",
        "scope": "selected_generated_c_fixture_only",
        "status": "adapter_probe_applied",
        "sourceChanged": adapted != source,
        "replacements": applied,
        "adaptedSource": adapted,
    }


def classify_failure(message: str) -> dict[str, Any]:
    detected = []
    if "unsupported as C branch condition" in message and "BinaryOp" in message:
        detected.append("nonzero_comparison_condition_unsupported")
    if "call to non-math function" in message:
        detected.append("selected_guard_helper_call_unsupported")
    if "if/for/while go to E3+" in message or "C if statement form not supported" in message:
        detected.append("statement_level_if_assignment_shape_unsupported")
    if not detected:
        detected.append("unclassified_reingest_blocker")
    return {
        "failureClass": "efrog_selected_generated_compound_condition_surface_blocked",
        "detectedBlockers": detected,
        "message": message,
    }


def run_adapted_probe(source: str) -> dict[str, Any]:
    try:
        module = decompile_c_source(source, source_path="c_and_short_circuit_guard_v0_adapted_generated_fixture.c")
    except EFrogError as exc:
        failure = classify_failure(str(exc))
        return {
            "probeId": "selected_nonzero_adapted_c_fixture_efrog_probe",
            "decompiler": "efrog.decompilers.c.decompile_c_source",
            "invocationPerformed": True,
            "status": "blocked_expected_next_surface",
            "reingestExecuted": False,
            "recompiledPythonExecuted": False,
            "errorType": type(exc).__name__,
            "errorMessage": str(exc),
            "failure": failure,
        }
    return {
        "probeId": "selected_nonzero_adapted_c_fixture_efrog_probe",
        "decompiler": "efrog.decompilers.c.decompile_c_source",
        "invocationPerformed": True,
        "status": "unexpected_pass_policy_requires_review",
        "reingestExecuted": True,
        "recompiledPythonExecuted": False,
        "functionCount": len(module.functions),
        "emlPreview": module.to_eml()[:500],
        "failure": {
            "failureClass": "none_unexpected_pass",
            "detectedBlockers": [],
            "message": "",
        },
    }


def build_summary(p79_packet: dict[str, Any], p79_payload: dict[str, Any], adapter: dict[str, Any], probe: dict[str, Any]) -> dict[str, Any]:
    detected = set(probe["failure"]["detectedBlockers"])
    previous_detected = set(p79_payload["reingestProbe"]["failure"]["detectedBlockers"])
    return {
        "sourcePacketCount": 1,
        "p79ValidationPass": p79_packet["validationStatus"] == "pass",
        "p79ClaimFlagsAllFalse": all(value is False for value in p79_packet["claimFlags"].values()),
        "selectedFixtureId": p79_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p79_payload["summary"]["selectedFixtureStillBlocked"],
        "adapterId": adapter["adapterId"],
        "adapterStatus": adapter["status"],
        "adapterSourceChanged": adapter["sourceChanged"],
        "replacementCount": len(adapter["replacements"]),
        "replacementAppliedCount": sum(1 for item in adapter["replacements"] if item["applied"]),
        "previousBlockerCleared": "nonzero_comparison_condition_unsupported" in previous_detected
        and "nonzero_comparison_condition_unsupported" not in detected,
        "nextBlockerDetected": "selected_guard_helper_call_unsupported" in detected,
        "probeStatus": probe["status"],
        "probeInvocationPerformed": probe["invocationPerformed"],
        "detectedBlockerCount": len(probe["failure"]["detectedBlockers"]),
        "reingestExecuted": False,
        "recompiledPythonExecuted": False,
        "runtimeComparisonExecuted": False,
        "compoundConditionReingestSupported": False,
        "helperRuntimeInstalled": False,
        "codegenFixtureInstalledInForge": False,
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "compoundConditionLoweringImplemented": False,
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
    p79_packet = read_json(P79_PACKET)
    p79_payload = read_json(P79_RESULT)
    p79.validate_payload(p79_payload)
    source = p79_payload["selectedCodegenFixture"]["source"]
    adapter = adapt_selected_nonzero_predicates(source)
    probe = run_adapted_probe(adapter["adaptedSource"])
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p80-compound-condition-nonzero-adapter-probe",
        "decision": "selected_nonzero_predicate_adapter_clears_first_blocker_next_surface_blocked",
        "sourcePacket": {
            "phase": "P79",
            "packetPath": str(P79_PACKET.relative_to(ROOT)),
            "resultPath": str(P79_RESULT.relative_to(ROOT)),
            "reviewDecision": p79_packet["reviewDecision"],
            "validationStatus": p79_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p79_payload["selectedFixture"]),
        "adapterProbe": {key: value for key, value in adapter.items() if key != "adaptedSource"},
        "reingestProbe": probe,
        "summary": build_summary(p79_packet, p79_payload, adapter, probe),
        "releaseGates": [
            {"id": "selected_nonzero_predicate_adapter_probe", "status": "recorded"},
            {"id": "selected_reingest_execution", "status": "blocked_not_executed"},
            {"id": "selected_guard_helper_call_surface", "status": "blocked"},
            {"id": "helper_runtime_installation", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P80 applies a selected nonzero-predicate adapter probe to the generated compound-condition fixture.",
            "The P79 nonzero comparison blocker is cleared in the adapted probe.",
            "The adapted probe still fails closed on the selected guard-helper call surface.",
        ],
        "blockedStatements": [
            "Re-ingested compound-condition code was executed successfully.",
            "Compound-condition re-ingest is supported.",
            "The selected adapter is installed in eFrog or Forge.",
            "Guard helper calls are supported by eFrog re-ingest.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "General C/Rust branch/control-flow support is established.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Add selected guard-helper call mapping or adapter for mg_step01, mg_nonzero01, and mg_guarded_div.",
            "Re-run the selected generated compound-condition re-ingest gate after the helper-call blocker is cleared.",
            "Record private reviewer response to the P47-P80 branch/control-flow bundle.",
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
        "title": "FEF-P80 Compound-Condition Nonzero Adapter Probe",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_nonzero_adapter_probe_clears_first_blocker_next_surface_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected adapter probe only; no successful re-ingest execution, installed eFrog/Forge behavior change, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P80 clears the P79 nonzero comparison blocker in a selected adapted source probe.",
            "The adapted probe exposes the next blocker: selected guard-helper calls.",
            "No re-ingest execution pass or installed behavior change is claimed.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p80_compound_condition_nonzero_adapter_probe.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p80_compound_condition_nonzero_adapter_probe.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p80_compound_condition_nonzero_adapter_probe.v0",
        "date": DATE,
        "title": "FEF-P80 Compound-Condition Nonzero Adapter Probe",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add selected guard-helper call mapping or adapter.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    replacements = [
        f"- `{item['replacementId']}`: applied `{item['applied']}`"
        for item in payload["adapterProbe"]["replacements"]
    ]
    blockers = [f"- `{item}`" for item in payload["reingestProbe"]["failure"]["detectedBlockers"]]
    return "\n".join(
        [
            "# FEF-P80 Compound-Condition Nonzero Adapter Probe",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P80 clears the selected nonzero-predicate blocker in an adapter probe and records the next blocker.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Adapter status: `{summary['adapterStatus']}`",
            f"- Replacement applied count: `{summary['replacementAppliedCount']}`",
            f"- Previous blocker cleared: `{summary['previousBlockerCleared']}`",
            f"- Next blocker detected: `{summary['nextBlockerDetected']}`",
            f"- Probe status: `{summary['probeStatus']}`",
            f"- Re-ingest executed: `{summary['reingestExecuted']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Replacements",
            "",
            *replacements,
            "",
            "## Detected Blockers",
            "",
            *blockers,
            "",
            "## Boundary",
            "",
            "- Selected adapter probe only.",
            "- No installed eFrog or Forge behavior change.",
            "- No successful re-ingest execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P80 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P80 status")
    p79.validate_payload(read_json(P79_RESULT))
    summary = payload["summary"]
    for key in [
        "p79ValidationPass",
        "p79ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "adapterSourceChanged",
        "previousBlockerCleared",
        "nextBlockerDetected",
        "probeInvocationPerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["replacementCount"] != 2 or summary["replacementAppliedCount"] != 2:
        raise ValueError("expected both selected nonzero replacements")
    if summary["probeStatus"] != "blocked_expected_next_surface":
        raise ValueError("expected adapted probe to expose next blocker")
    for key in [
        "reingestExecuted",
        "recompiledPythonExecuted",
        "runtimeComparisonExecuted",
        "compoundConditionReingestSupported",
        "helperRuntimeInstalled",
        "codegenFixtureInstalledInForge",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "compoundConditionLoweringImplemented",
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
    result_path = out_dir / f"fef_p80_compound_condition_nonzero_adapter_probe_{STAMP}.json"
    report_path = report_dir / f"fef_p80_compound_condition_nonzero_adapter_probe_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p80_compound_condition_nonzero_adapter_probe.json"
    feed_path = command_feed_dir / f"fef_p80_compound_condition_nonzero_adapter_probe_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p80_compound_condition_nonzero_adapter_probe")
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
    print("FEF_P80_COMPOUND_CONDITION_NONZERO_ADAPTER_PROBE_OK")
    print(f"previous_blocker_cleared={built['payload']['summary']['previousBlockerCleared']}")
    print(f"next_blocker_detected={built['payload']['summary']['nextBlockerDetected']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
