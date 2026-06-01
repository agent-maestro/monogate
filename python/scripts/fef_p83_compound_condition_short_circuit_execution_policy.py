#!/usr/bin/env python3
"""FEF-P83 selected short-circuit-safe execution policy for parsed P82 EML."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p82_compound_condition_if_assignment_normalization_probe as p82  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p83_compound_condition_short_circuit_execution_policy.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P83_COMPOUND_CONDITION_SHORT_CIRCUIT_EXECUTION_POLICY_PASS"

P82_PACKET = ROOT / "reports/evidence_packets/fef_p82_compound_condition_if_assignment_normalization_probe.json"
P82_RESULT = ROOT / "python/results/fef_p82_compound_condition_if_assignment_normalization_probe/fef_p82_compound_condition_if_assignment_normalization_probe_2026_05_31.json"
P77_RESULT = ROOT / "python/results/fef_p77_compound_condition_generated_target_runtime_gate/fef_p77_compound_condition_generated_target_runtime_gate_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_short_circuit_execution_policy_claim": False,
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
    "FEF-P83 records a selected short-circuit-safe execution policy only.",
    "FEF-P83 does not execute re-ingested Python or compare parsed EML rows.",
    "FEF-P83 does not change eFrog or Forge source code.",
    "FEF-P83 does not claim supported compound-condition re-ingest.",
    "FEF-P83 does not claim the normalized eager-division shape preserves all C short-circuit semantics.",
    "FEF-P83 does not install helper functions in Forge or eFrog.",
    "FEF-P83 does not claim compound-condition support.",
    "FEF-P83 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P83 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_policy_row(row: dict[str, Any]) -> dict[str, Any]:
    y = float(row["inputs"]["y"])
    eager_division_safe = y != 0.0
    if eager_division_safe:
        status = "eligible_for_future_eager_eml_comparison"
        reason = "denominator is nonzero, so the parsed eager division is finite on this row"
    else:
        status = "blocked_by_short_circuit_eager_division"
        reason = "denominator is zero, so parsed eager x / y would not preserve the original C short-circuit guard"
    return {
        "sampleId": row["sampleId"],
        "path": row["path"],
        "inputs": dict(row["inputs"]),
        "expected": row["expected"],
        "p77Observed": row["observed"],
        "p77Pass": row["pass"],
        "rhsEvaluatedInOriginalShape": row["rhsEvaluated"],
        "eagerDivisionSafe": eager_division_safe,
        "policyStatus": status,
        "reason": reason,
        "futureComparisonAllowed": eager_division_safe,
        "futureComparisonBlocked": not eager_division_safe,
    }


def build_execution_policy(p82_payload: dict[str, Any], p77_payload: dict[str, Any]) -> dict[str, Any]:
    rows = [classify_policy_row(row) for row in p77_payload["runtimeComparison"]["rows"]]
    allowed = [row for row in rows if row["futureComparisonAllowed"]]
    blocked = [row for row in rows if row["futureComparisonBlocked"]]
    return {
        "policyId": "selected_short_circuit_safe_eager_eml_execution_policy_v0",
        "scope": "selected_p82_parsed_eml_against_p77_rows",
        "status": "recorded_execution_still_blocked",
        "sourceObligation": p82_payload["adapterProbe"]["semanticCaveats"][0]["id"],
        "rowCount": len(rows),
        "futureComparisonAllowedRowCount": len(allowed),
        "futureComparisonBlockedRowCount": len(blocked),
        "allowedSampleIds": [row["sampleId"] for row in allowed],
        "blockedSampleIds": [row["sampleId"] for row in blocked],
        "blockedPaths": sorted({row["path"] for row in blocked}),
        "executionPolicyRows": rows,
        "executionPerformed": False,
        "runtimeComparisonPerformed": False,
    }


def build_summary(p82_packet: dict[str, Any], p82_payload: dict[str, Any], p77_payload: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 2,
        "p82ValidationPass": p82_packet["validationStatus"] == "pass",
        "p82ClaimFlagsAllFalse": all(value is False for value in p82_packet["claimFlags"].values()),
        "p82ParseSucceeded": p82_payload["summary"]["reingestParseSucceeded"],
        "p82SemanticExecutionBlocked": p82_payload["summary"]["semanticExecutionBlocked"],
        "p77GeneratedTargetExecuted": p77_payload["summary"]["generatedTargetRuntimeExecuted"],
        "p77ComparisonPassCount": p77_payload["summary"]["passCount"],
        "selectedFixtureId": p82_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p82_payload["summary"]["selectedFixtureStillBlocked"],
        "policyId": policy["policyId"],
        "policyStatus": policy["status"],
        "rowCount": policy["rowCount"],
        "futureComparisonAllowedRowCount": policy["futureComparisonAllowedRowCount"],
        "futureComparisonBlockedRowCount": policy["futureComparisonBlockedRowCount"],
        "blockedByShortCircuitEagerDivisionCount": policy["futureComparisonBlockedRowCount"],
        "hasBlockedRows": policy["futureComparisonBlockedRowCount"] > 0,
        "executionPolicyRecorded": True,
        "executionPerformed": False,
        "runtimeComparisonPerformed": False,
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
    p82_packet = read_json(P82_PACKET)
    p82_payload = read_json(P82_RESULT)
    p77_payload = read_json(P77_RESULT)
    p82.validate_payload(p82_payload)
    policy = build_execution_policy(p82_payload, p77_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p83-compound-condition-short-circuit-execution-policy",
        "decision": "selected_short_circuit_safe_execution_policy_recorded_execution_blocked",
        "sourcePackets": [
            {
                "phase": "P82",
                "packetPath": str(P82_PACKET.relative_to(ROOT)),
                "resultPath": str(P82_RESULT.relative_to(ROOT)),
                "reviewDecision": p82_packet["reviewDecision"],
                "validationStatus": p82_packet["validationStatus"],
            },
            {
                "phase": "P77",
                "resultPath": str(P77_RESULT.relative_to(ROOT)),
                "comparisonKind": p77_payload["runtimeComparison"]["comparisonKind"],
            },
        ],
        "selectedFixture": copy.deepcopy(p82_payload["selectedFixture"]),
        "executionPolicy": policy,
        "summary": build_summary(p82_packet, p82_payload, p77_payload, policy),
        "releaseGates": [
            {"id": "selected_short_circuit_safe_execution_policy", "status": "recorded"},
            {"id": "selected_reingest_parse", "status": "selected_probe_pass_from_p82"},
            {"id": "selected_reingest_execution", "status": "blocked_not_executed"},
            {"id": "blocked_zero_denominator_rows", "status": "requires_guarded_division_or_review_only_policy"},
            {"id": "helper_runtime_installation", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P83 records a selected short-circuit-safe execution policy for the parsed P82 EML.",
            "Five P77 rows are eligible for future eager parsed-EML comparison because their denominator is nonzero.",
            "Two P77 rows remain blocked because eager x / y would cross the original short-circuit boundary.",
            "No parsed-EML execution or runtime comparison is performed in P83.",
        ],
        "blockedStatements": [
            "Re-ingested compound-condition code was executed successfully.",
            "All P77 rows are safe for eager parsed-EML comparison.",
            "Compound-condition re-ingest is supported.",
            "The selected policy is installed in eFrog or Forge.",
            "The normalized branch-free source is semantically equivalent to the original C short-circuit source.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Add a selected guarded_div source primitive or row-filtered execution harness before comparing parsed P82 EML.",
            "Keep zero-denominator short-circuit rows blocked unless the source primitive preserves non-evaluation.",
            "Record private reviewer response to the P47-P83 branch/control-flow bundle.",
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
        "title": "FEF-P83 Compound-Condition Short-Circuit Execution Policy",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_execution_policy_recorded_runtime_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected execution policy only; no parsed-EML execution, installed eFrog/Forge behavior change, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P83 classifies P77 rows against the P82 short-circuit/eager-division obligation.",
            "Five rows are eligible for a future eager parsed-EML comparison.",
            "Two zero-denominator rows remain blocked until guarded division or review-only policy is chosen.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p83_compound_condition_short_circuit_execution_policy.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p83_compound_condition_short_circuit_execution_policy.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p83_compound_condition_short_circuit_execution_policy.v0",
        "date": DATE,
        "title": "FEF-P83 Compound-Condition Short-Circuit Execution Policy",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add selected guarded_div source primitive or row-filtered parsed-EML execution harness.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        f"- `{row['sampleId']}` `{row['policyStatus']}`: {row['reason']}"
        for row in payload["executionPolicy"]["executionPolicyRows"]
    ]
    return "\n".join(
        [
            "# FEF-P83 Compound-Condition Short-Circuit Execution Policy",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P83 records the selected execution policy needed before any parsed P82 EML runtime comparison.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Policy: `{summary['policyId']}`",
            f"- Row count: `{summary['rowCount']}`",
            f"- Future comparison allowed rows: `{summary['futureComparisonAllowedRowCount']}`",
            f"- Future comparison blocked rows: `{summary['futureComparisonBlockedRowCount']}`",
            f"- Execution performed: `{summary['executionPerformed']}`",
            f"- Runtime comparison performed: `{summary['runtimeComparisonPerformed']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Row Policy",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected execution policy only.",
            "- No parsed-EML execution or runtime comparison.",
            "- No installed eFrog or Forge behavior change.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P83 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P83 status")
    p82.validate_payload(read_json(P82_RESULT))
    summary = payload["summary"]
    for key in [
        "p82ValidationPass",
        "p82ClaimFlagsAllFalse",
        "p82ParseSucceeded",
        "p82SemanticExecutionBlocked",
        "p77GeneratedTargetExecuted",
        "selectedFixtureStillBlocked",
        "hasBlockedRows",
        "executionPolicyRecorded",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["rowCount"] != 7:
        raise ValueError("expected seven P77 rows")
    if summary["futureComparisonAllowedRowCount"] != 5:
        raise ValueError("expected five future-comparison-eligible rows")
    if summary["futureComparisonBlockedRowCount"] != 2:
        raise ValueError("expected two blocked zero-denominator rows")
    if payload["executionPolicy"]["blockedSampleIds"] != ["sample_01", "sample_03"]:
        raise ValueError("expected sample_01 and sample_03 to remain blocked")
    for key in [
        "executionPerformed",
        "runtimeComparisonPerformed",
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
    result_path = out_dir / f"fef_p83_compound_condition_short_circuit_execution_policy_{STAMP}.json"
    report_path = report_dir / f"fef_p83_compound_condition_short_circuit_execution_policy_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p83_compound_condition_short_circuit_execution_policy.json"
    feed_path = command_feed_dir / f"fef_p83_compound_condition_short_circuit_execution_policy_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p83_compound_condition_short_circuit_execution_policy")
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
    print("FEF_P83_COMPOUND_CONDITION_SHORT_CIRCUIT_EXECUTION_POLICY_OK")
    print(f"allowed_rows={built['payload']['summary']['futureComparisonAllowedRowCount']}")
    print(f"blocked_rows={built['payload']['summary']['futureComparisonBlockedRowCount']}")
    print(f"execution_performed={built['payload']['summary']['executionPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
