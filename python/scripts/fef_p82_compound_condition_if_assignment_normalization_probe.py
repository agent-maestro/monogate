#!/usr/bin/env python3
"""FEF-P82 selected if-assignment normalization probe for compound-condition re-ingest."""

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
from scripts import fef_p81_compound_condition_guard_helper_adapter_probe as p81  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p82_compound_condition_if_assignment_normalization_probe.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P82_COMPOUND_CONDITION_IF_ASSIGNMENT_NORMALIZATION_PROBE_PASS"

P81_PACKET = ROOT / "reports/evidence_packets/fef_p81_compound_condition_guard_helper_adapter_probe.json"
P81_RESULT = ROOT / "python/results/fef_p81_compound_condition_guard_helper_adapter_probe/fef_p81_compound_condition_guard_helper_adapter_probe_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_if_assignment_normalization_probe_claim": False,
    "compound_condition_reingest_parse_success_claim": False,
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
    "FEF-P82 records a selected if-assignment normalization probe only.",
    "FEF-P82 does not change eFrog or Forge source code.",
    "FEF-P82 does not claim supported compound-condition re-ingest.",
    "FEF-P82 does not execute re-ingested Python or compare runtime rows.",
    "FEF-P82 does not claim the normalized eager-division shape preserves C short-circuit semantics.",
    "FEF-P82 does not install helper functions in Forge or eFrog.",
    "FEF-P82 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P82 does not claim compound-condition support.",
    "FEF-P82 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P82 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def adapt_selected_if_assignment_shape(source: str) -> dict[str, Any]:
    base = p81.adapt_selected_guard_helper_calls(source)
    adapted = base["adaptedSource"]
    before = "\n".join(
        [
            "double c_and_short_circuit_guard_v0_generated_fixture(double x, double y) {",
            "  double lhs = step01(x);",
            "  double rhs = 0.0;",
            "  double selected = 0.0;",
            "  if (lhs > 0.0) {",
            "    rhs = step01(y * y);",
            "    selected = 0.0 + (x / y - (0.0)) * step01(rhs * rhs);",
            "  }",
            "  return lhs * rhs * selected;",
            "}",
        ]
    )
    after = "\n".join(
        [
            "double c_and_short_circuit_guard_v0_generated_fixture(double x, double y) {",
            "  double lhs = step01(x);",
            "  double rhs_candidate = step01(y * y);",
            "  double rhs = lhs * rhs_candidate;",
            "  double selected_candidate = 0.0 + (x / y - (0.0)) * step01(rhs_candidate * rhs_candidate);",
            "  double selected = lhs * selected_candidate;",
            "  return lhs * rhs * selected;",
            "}",
        ]
    )
    replacement = {
        "replacementId": "selected_if_assignment_to_branch_free_candidate_bindings",
        "before": before,
        "after": after,
        "applied": before in adapted,
    }
    if replacement["applied"]:
        adapted = adapted.replace(before, after, 1)
    return {
        "adapterId": "selected_if_assignment_normalization_probe_v0",
        "scope": "selected_generated_c_fixture_only",
        "status": "adapter_probe_applied" if replacement["applied"] else "adapter_probe_not_applied",
        "composesPriorAdapter": base["adapterId"],
        "priorReplacementCount": len(base["replacements"]),
        "priorReplacementAppliedCount": sum(1 for item in base["replacements"] if item["applied"]),
        "sourceChanged": adapted != source,
        "replacements": [replacement],
        "semanticCaveats": [
            {
                "id": "short_circuit_eager_division_semantic_obligation",
                "status": "open_execution_blocker",
                "reason": "The selected branch-free normalized source may evaluate x / y eagerly where the original C short-circuits.",
            }
        ],
        "adaptedSource": adapted,
    }


def classify_failure(message: str) -> dict[str, Any]:
    detected = []
    if "unsupported as C branch condition" in message and "BinaryOp" in message:
        detected.append("nonzero_comparison_condition_unsupported")
    if "call to non-math function" in message:
        detected.append("selected_guard_helper_call_unsupported")
    if "C if statement form not supported" in message or "if/for/while go to E3+" in message:
        detected.append("statement_level_if_assignment_shape_unsupported")
    if not detected:
        detected.append("unclassified_reingest_blocker")
    return {
        "failureClass": "efrog_selected_generated_compound_condition_surface_blocked",
        "detectedBlockers": detected,
        "message": message,
    }


def run_normalized_probe(source: str) -> dict[str, Any]:
    try:
        module = decompile_c_source(source, source_path="c_and_short_circuit_guard_v0_if_assignment_normalized.c")
    except EFrogError as exc:
        failure = classify_failure(str(exc))
        return {
            "probeId": "selected_if_assignment_normalized_c_fixture_efrog_probe",
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
        "probeId": "selected_if_assignment_normalized_c_fixture_efrog_probe",
        "decompiler": "efrog.decompilers.c.decompile_c_source",
        "invocationPerformed": True,
        "status": "parse_pass_execution_blocked_by_semantic_obligation",
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


def build_summary(p81_packet: dict[str, Any], p81_payload: dict[str, Any], adapter: dict[str, Any], probe: dict[str, Any]) -> dict[str, Any]:
    detected = set(probe["failure"]["detectedBlockers"])
    previous_detected = set(p81_payload["reingestProbe"]["failure"]["detectedBlockers"])
    return {
        "sourcePacketCount": 1,
        "p81ValidationPass": p81_packet["validationStatus"] == "pass",
        "p81ClaimFlagsAllFalse": all(value is False for value in p81_packet["claimFlags"].values()),
        "selectedFixtureId": p81_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p81_payload["summary"]["selectedFixtureStillBlocked"],
        "adapterId": adapter["adapterId"],
        "adapterStatus": adapter["status"],
        "adapterSourceChanged": adapter["sourceChanged"],
        "priorAdapterId": adapter["composesPriorAdapter"],
        "priorReplacementCount": adapter["priorReplacementCount"],
        "priorReplacementAppliedCount": adapter["priorReplacementAppliedCount"],
        "replacementCount": len(adapter["replacements"]),
        "replacementAppliedCount": sum(1 for item in adapter["replacements"] if item["applied"]),
        "previousBlockerCleared": "statement_level_if_assignment_shape_unsupported" in previous_detected
        and "statement_level_if_assignment_shape_unsupported" not in detected,
        "guardHelperBlockerStillCleared": "selected_guard_helper_call_unsupported" not in detected,
        "nonzeroComparisonBlockerStillCleared": "nonzero_comparison_condition_unsupported" not in detected,
        "reingestParseSucceeded": probe["reingestParseSucceeded"],
        "probeStatus": probe["status"],
        "probeInvocationPerformed": probe["invocationPerformed"],
        "detectedBlockerCount": len(probe["failure"]["detectedBlockers"]),
        "semanticObligationCount": len(adapter["semanticCaveats"]),
        "semanticExecutionBlocked": True,
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
    p81_packet = read_json(P81_PACKET)
    p81_payload = read_json(P81_RESULT)
    p81.validate_payload(p81_payload)
    p79_payload = p81.p80.read_json(p81.p80.P79_RESULT)
    source = p79_payload["selectedCodegenFixture"]["source"]
    adapter = adapt_selected_if_assignment_shape(source)
    probe = run_normalized_probe(adapter["adaptedSource"])
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p82-compound-condition-if-assignment-normalization-probe",
        "decision": "selected_if_assignment_normalization_parse_pass_execution_blocked",
        "sourcePacket": {
            "phase": "P81",
            "packetPath": str(P81_PACKET.relative_to(ROOT)),
            "resultPath": str(P81_RESULT.relative_to(ROOT)),
            "reviewDecision": p81_packet["reviewDecision"],
            "validationStatus": p81_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p81_payload["selectedFixture"]),
        "adapterProbe": {key: value for key, value in adapter.items() if key != "adaptedSource"},
        "reingestProbe": probe,
        "summary": build_summary(p81_packet, p81_payload, adapter, probe),
        "releaseGates": [
            {"id": "selected_if_assignment_normalization_probe", "status": "recorded"},
            {"id": "selected_reingest_parse", "status": "selected_probe_pass"},
            {"id": "selected_reingest_execution", "status": "blocked_not_executed"},
            {"id": "short_circuit_eager_division_semantic_obligation", "status": "open_execution_blocker"},
            {"id": "helper_runtime_installation", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P82 applies a selected if-assignment normalization probe to the generated compound-condition fixture.",
            "The P81 statement-level if assignment blocker is cleared in the adapted probe.",
            "The selected normalized source parses through eFrog into EML.",
            "Execution and comparison remain blocked by an explicit short-circuit/eager-division semantic obligation.",
        ],
        "blockedStatements": [
            "Re-ingested compound-condition code was executed successfully.",
            "Compound-condition re-ingest is supported.",
            "The selected adapter is installed in eFrog or Forge.",
            "The normalized branch-free source is semantically equivalent to the original C short-circuit source.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "General C/Rust branch/control-flow support is established.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Add a selected short-circuit-safe execution policy for the parsed P82 EML before comparing P77 rows.",
            "Decide whether the eager-division normalized source is review-only or needs a guarded_div source primitive.",
            "Record private reviewer response to the P47-P82 branch/control-flow bundle.",
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
        "title": "FEF-P82 Compound-Condition If-Assignment Normalization Probe",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_if_assignment_normalization_parse_pass_execution_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected parse probe only; no re-ingested execution, installed eFrog/Forge behavior change, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P82 clears the P81 statement-level if assignment blocker in an adapted source probe.",
            "The selected adapted source parses through eFrog into EML.",
            "Execution and comparison remain blocked by an explicit short-circuit/eager-division semantic obligation.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p82_compound_condition_if_assignment_normalization_probe.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p82_compound_condition_if_assignment_normalization_probe.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p82_compound_condition_if_assignment_normalization_probe.v0",
        "date": DATE,
        "title": "FEF-P82 Compound-Condition If-Assignment Normalization Probe",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add selected short-circuit-safe execution policy before runtime comparison.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    replacements = [
        f"- `{item['replacementId']}`: applied `{item['applied']}`"
        for item in payload["adapterProbe"]["replacements"]
    ]
    obligations = [
        f"- `{item['id']}`: `{item['status']}`"
        for item in payload["adapterProbe"]["semanticCaveats"]
    ]
    return "\n".join(
        [
            "# FEF-P82 Compound-Condition If-Assignment Normalization Probe",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P82 clears the selected statement-level if assignment blocker in an adapter probe and blocks execution on a semantic obligation.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Adapter status: `{summary['adapterStatus']}`",
            f"- Prior adapter: `{summary['priorAdapterId']}`",
            f"- Replacement applied count: `{summary['replacementAppliedCount']}`",
            f"- Previous blocker cleared: `{summary['previousBlockerCleared']}`",
            f"- Guard-helper blocker still cleared: `{summary['guardHelperBlockerStillCleared']}`",
            f"- Nonzero blocker still cleared: `{summary['nonzeroComparisonBlockerStillCleared']}`",
            f"- Re-ingest parse succeeded: `{summary['reingestParseSucceeded']}`",
            f"- Probe status: `{summary['probeStatus']}`",
            f"- Semantic execution blocked: `{summary['semanticExecutionBlocked']}`",
            f"- Recompiled Python executed: `{summary['recompiledPythonExecuted']}`",
            f"- Runtime comparison executed: `{summary['runtimeComparisonExecuted']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Replacements",
            "",
            *replacements,
            "",
            "## Open Semantic Obligations",
            "",
            *obligations,
            "",
            "## Boundary",
            "",
            "- Selected adapter parse probe only.",
            "- No installed eFrog or Forge behavior change.",
            "- No re-ingested execution or runtime comparison.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P82 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P82 status")
    p81.validate_payload(read_json(P81_RESULT))
    summary = payload["summary"]
    for key in [
        "p81ValidationPass",
        "p81ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "adapterSourceChanged",
        "previousBlockerCleared",
        "guardHelperBlockerStillCleared",
        "nonzeroComparisonBlockerStillCleared",
        "reingestParseSucceeded",
        "probeInvocationPerformed",
        "semanticExecutionBlocked",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["priorReplacementCount"] != 4 or summary["priorReplacementAppliedCount"] != 4:
        raise ValueError("expected P81 adapter composition")
    if summary["replacementCount"] != 1 or summary["replacementAppliedCount"] != 1:
        raise ValueError("expected selected if-assignment replacement")
    if summary["semanticObligationCount"] != 1:
        raise ValueError("expected one execution-blocking semantic obligation")
    if summary["probeStatus"] != "parse_pass_execution_blocked_by_semantic_obligation":
        raise ValueError("expected parse pass with execution blocked")
    if summary["detectedBlockerCount"] != 0:
        raise ValueError("expected no remaining parser blocker in P82 probe")
    for key in [
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
    result_path = out_dir / f"fef_p82_compound_condition_if_assignment_normalization_probe_{STAMP}.json"
    report_path = report_dir / f"fef_p82_compound_condition_if_assignment_normalization_probe_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p82_compound_condition_if_assignment_normalization_probe.json"
    feed_path = command_feed_dir / f"fef_p82_compound_condition_if_assignment_normalization_probe_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p82_compound_condition_if_assignment_normalization_probe")
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
    print("FEF_P82_COMPOUND_CONDITION_IF_ASSIGNMENT_NORMALIZATION_PROBE_OK")
    print(f"previous_blocker_cleared={built['payload']['summary']['previousBlockerCleared']}")
    print(f"reingest_parse_succeeded={built['payload']['summary']['reingestParseSucceeded']}")
    print(f"semantic_execution_blocked={built['payload']['summary']['semanticExecutionBlocked']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
