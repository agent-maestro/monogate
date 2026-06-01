#!/usr/bin/env python3
"""FEF-P86 guarded-div installation candidate probe for the compound condition."""

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

from scripts import fef_p85_compound_condition_guarded_div_source_primitive_execution as p85  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p86_compound_condition_guarded_div_installation_candidate_probe.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P86_COMPOUND_CONDITION_GUARDED_DIV_INSTALLATION_CANDIDATE_PROBE_PASS"

P85_PACKET = ROOT / "reports/evidence_packets/fef_p85_compound_condition_guarded_div_source_primitive_execution.json"
P85_RESULT = ROOT / "python/results/fef_p85_compound_condition_guarded_div_source_primitive_execution/fef_p85_compound_condition_guarded_div_source_primitive_execution_2026_05_31.json"

CLAIM_FLAGS = {
    "guarded_div_installation_candidate_probe_claim": False,
    "guarded_div_source_primitive_installed": False,
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
    "FEF-P86 records a local installation-candidate probe only.",
    "FEF-P86 does not install the guarded-div primitive in eFrog or Forge.",
    "FEF-P86 does not change eFrog or Forge source code.",
    "FEF-P86 does not execute re-ingested code.",
    "FEF-P86 does not claim supported compound-condition re-ingest.",
    "FEF-P86 does not claim compiler-wide short-circuit semantics.",
    "FEF-P86 does not claim compound-condition support.",
    "FEF-P86 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P86 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def installation_candidate() -> dict[str, Any]:
    return {
        "candidateId": "selected_guarded_div_local_adapter_installation_candidate_v0",
        "sourcePrimitiveId": "selected_guarded_div_non_evaluation_source_primitive_v0",
        "status": "candidate_probe_recorded_not_installed",
        "scope": "selected_c_and_short_circuit_guard_v0_only",
        "intendedPipelineHooks": [
            {
                "hookId": "rewrite_selected_nonzero_condition",
                "source": "y != 0.0",
                "candidateLowering": "nonzero01(y)",
                "previousEvidence": "FEF-P80",
            },
            {
                "hookId": "rewrite_selected_guarded_division",
                "source": "x / y under y != 0.0 guard",
                "candidateLowering": "guarded_div(x, y, default=0.0, guard=nonzero01(y))",
                "previousEvidence": "FEF-P85",
            },
            {
                "hookId": "preserve_short_circuit_non_evaluation",
                "source": "left-false or y-zero path",
                "candidateLowering": "skip division when guard is 0.0",
                "previousEvidence": "FEF-P85",
            },
        ],
        "requiredFailClosedChecks": [
            "candidate fixture id must match c_and_short_circuit_guard_v0",
            "zero-denominator rows must not evaluate division",
            "all seven selected rows must match P77 expected values",
            "candidate must remain uninstalled until a separate explicit implementation phase",
            "re-ingest execution must remain blocked until a separate fail-closed probe exists",
        ],
        "installedInEfrog": False,
        "installedInForge": False,
        "compilerBehaviorChanged": False,
    }


def build_probe_rows(p85_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in p85_payload["executionResult"]["rows"]:
        values = p85.evaluate_guarded_div_source_primitive(float(row["inputs"]["x"]), float(row["inputs"]["y"]))
        expected = float(row["expected"])
        observed = values["observed"]
        abs_error = abs(observed - expected)
        rows.append(
            {
                "sampleId": row["sampleId"],
                "path": row["path"],
                "inputs": dict(row["inputs"]),
                "expected": expected,
                "observed": observed,
                "absError": abs_error,
                "pass": math.isfinite(observed) and abs_error <= 1.0e-12,
                "probeStatus": "candidate_probe_executed_not_installed",
                "wasP84BlockedRow": row["wasBlockedInP84"],
                "zeroDenominator": row["zeroDenominator"],
                "divisionEvaluated": values["divisionEvaluated"],
                "nonEvaluationPreserved": not values["divisionEvaluated"] if row["zeroDenominator"] else True,
                "intermediates": values,
            }
        )
    return rows


def build_probe_result(candidate: dict[str, Any], p85_payload: dict[str, Any]) -> dict[str, Any]:
    rows = build_probe_rows(p85_payload)
    zero_rows = [row for row in rows if row["zeroDenominator"]]
    return {
        "probeId": "selected_guarded_div_installation_candidate_probe_v0",
        "candidateId": candidate["candidateId"],
        "sourcePrimitiveId": candidate["sourcePrimitiveId"],
        "scope": candidate["scope"],
        "rowCount": len(rows),
        "executedRowCount": len(rows),
        "passCount": sum(1 for row in rows if row["pass"] is True),
        "failCount": sum(1 for row in rows if row["pass"] is False),
        "maxAbsError": max((row["absError"] for row in rows), default=0.0),
        "zeroDenominatorRowCount": len(zero_rows),
        "zeroDenominatorRowsWithDivisionSkipped": sum(1 for row in zero_rows if row["divisionEvaluated"] is False),
        "nonEvaluationBoundaryPreserved": all(row["nonEvaluationPreserved"] for row in rows),
        "allRowsFinite": all(math.isfinite(float(row["observed"])) for row in rows),
        "allRowsPass": all(row["pass"] is True for row in rows),
        "candidateInstalled": False,
        "reingestProbePerformed": False,
        "rows": rows,
    }


def build_summary(p85_packet: dict[str, Any], p85_payload: dict[str, Any], candidate: dict[str, Any], probe: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p85ValidationPass": p85_packet["validationStatus"] == "pass",
        "p85ClaimFlagsAllFalse": all(value is False for value in p85_packet["claimFlags"].values()),
        "selectedFixtureId": p85_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p85_payload["summary"]["selectedFixtureStillBlocked"],
        "candidateId": candidate["candidateId"],
        "candidateStatus": candidate["status"],
        "probeId": probe["probeId"],
        "intendedPipelineHookCount": len(candidate["intendedPipelineHooks"]),
        "requiredFailClosedCheckCount": len(candidate["requiredFailClosedChecks"]),
        "rowCount": probe["rowCount"],
        "executedRowCount": probe["executedRowCount"],
        "passCount": probe["passCount"],
        "failCount": probe["failCount"],
        "maxAbsError": probe["maxAbsError"],
        "zeroDenominatorRowCount": probe["zeroDenominatorRowCount"],
        "zeroDenominatorRowsWithDivisionSkipped": probe["zeroDenominatorRowsWithDivisionSkipped"],
        "nonEvaluationBoundaryPreserved": probe["nonEvaluationBoundaryPreserved"],
        "allRowsFinite": probe["allRowsFinite"],
        "allRowsPass": probe["allRowsPass"],
        "candidateProbePerformed": True,
        "candidateInstalled": probe["candidateInstalled"],
        "sourcePrimitiveInstalled": False,
        "reingestProbePerformed": probe["reingestProbePerformed"],
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
    p85_packet = read_json(P85_PACKET)
    p85_payload = read_json(P85_RESULT)
    p85.validate_payload(p85_payload)
    candidate = installation_candidate()
    probe = build_probe_result(candidate, p85_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p86-compound-condition-guarded-div-installation-candidate-probe",
        "decision": "selected_guarded_div_installation_candidate_probe_pass_not_installed",
        "sourcePacket": {
            "phase": "P85",
            "packetPath": str(P85_PACKET.relative_to(ROOT)),
            "resultPath": str(P85_RESULT.relative_to(ROOT)),
            "reviewDecision": p85_packet["reviewDecision"],
            "validationStatus": p85_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p85_payload["selectedFixture"]),
        "installationCandidate": candidate,
        "probeResult": probe,
        "summary": build_summary(p85_packet, p85_payload, candidate, probe),
        "releaseGates": [
            {"id": "selected_guarded_div_installation_candidate", "status": "candidate_probe_pass_not_installed"},
            {"id": "non_evaluation_boundary", "status": "preserved_in_candidate_probe"},
            {"id": "source_primitive_installation", "status": "not_performed"},
            {"id": "reingest_probe", "status": "blocked_not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P86 records a selected local installation candidate for the guarded-div primitive.",
            "The candidate probe replays all seven P77 rows and preserves the zero-denominator non-evaluation boundary.",
            "The selected candidate is not installed in eFrog or Forge.",
            "P86 does not perform re-ingest execution.",
        ],
        "blockedStatements": [
            "The selected guarded-div primitive is installed in eFrog or Forge.",
            "Compound-condition re-ingest is supported.",
            "Re-ingested compound-condition code executed successfully.",
            "The selected candidate proves compiler-wide short-circuit semantics.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Add a fail-closed re-ingest boundary probe for the selected guarded-div candidate.",
            "Keep the candidate uninstalled until an explicit implementation phase is approved.",
            "Record private reviewer response to the P47-P86 branch/control-flow bundle.",
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
        "title": "FEF-P86 Compound-Condition Guarded-Div Installation Candidate Probe",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_guarded_div_installation_candidate_probe_pass_not_installed",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected installation-candidate probe only; no installed eFrog/Forge behavior change, re-ingest execution, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P86 identifies the selected local adapter hooks for guarded-div primitive installation.",
            "The candidate probe preserves the zero-denominator non-evaluation boundary.",
            "The candidate remains uninstalled and re-ingest execution remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p86_compound_condition_guarded_div_installation_candidate_probe.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p86_compound_condition_guarded_div_installation_candidate_probe.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p86_compound_condition_guarded_div_installation_candidate_probe.v0",
        "date": DATE,
        "title": "FEF-P86 Compound-Condition Guarded-Div Installation Candidate Probe",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add fail-closed re-ingest boundary probe for the guarded-div candidate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        f"- `{row['sampleId']}` `{row['probeStatus']}` observed `{row['observed']}` pass `{row['pass']}` non-eval `{row['nonEvaluationPreserved']}`"
        for row in payload["probeResult"]["rows"]
    ]
    hooks = [
        f"- `{hook['hookId']}`: `{hook['candidateLowering']}`"
        for hook in payload["installationCandidate"]["intendedPipelineHooks"]
    ]
    return "\n".join(
        [
            "# FEF-P86 Compound-Condition Guarded-Div Installation Candidate Probe",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P86 records a selected installation candidate without installing it.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Candidate: `{summary['candidateId']}`",
            f"- Probe: `{summary['probeId']}`",
            f"- Executed rows: `{summary['executedRowCount']}`",
            f"- Zero-denominator rows with division skipped: `{summary['zeroDenominatorRowsWithDivisionSkipped']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Candidate installed: `{summary['candidateInstalled']}`",
            f"- Re-ingest probe performed: `{summary['reingestProbePerformed']}`",
            "",
            "## Intended Hooks",
            "",
            *hooks,
            "",
            "## Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected installation-candidate probe only.",
            "- No installed eFrog or Forge behavior change.",
            "- No re-ingest execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P86 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P86 status")
    p85.validate_payload(read_json(P85_RESULT))
    summary = payload["summary"]
    for key in [
        "p85ValidationPass",
        "p85ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "nonEvaluationBoundaryPreserved",
        "allRowsFinite",
        "allRowsPass",
        "candidateProbePerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["candidateStatus"] != "candidate_probe_recorded_not_installed":
        raise ValueError("candidate must remain uninstalled")
    if summary["rowCount"] != 7 or summary["executedRowCount"] != 7:
        raise ValueError("expected seven executed candidate rows")
    if summary["zeroDenominatorRowCount"] != 2 or summary["zeroDenominatorRowsWithDivisionSkipped"] != 2:
        raise ValueError("expected zero-denominator rows to skip division")
    if summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("expected all candidate rows to pass")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("expected exact candidate agreement")
    if summary["intendedPipelineHookCount"] != 3:
        raise ValueError("expected three candidate pipeline hooks")
    if summary["requiredFailClosedCheckCount"] != 5:
        raise ValueError("expected five fail-closed checks")
    for key in [
        "candidateInstalled",
        "sourcePrimitiveInstalled",
        "reingestProbePerformed",
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
    result_path = out_dir / f"fef_p86_compound_condition_guarded_div_installation_candidate_probe_{STAMP}.json"
    report_path = report_dir / f"fef_p86_compound_condition_guarded_div_installation_candidate_probe_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p86_compound_condition_guarded_div_installation_candidate_probe.json"
    feed_path = command_feed_dir / f"fef_p86_compound_condition_guarded_div_installation_candidate_probe_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p86_compound_condition_guarded_div_installation_candidate_probe")
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
    print("FEF_P86_COMPOUND_CONDITION_GUARDED_DIV_INSTALLATION_CANDIDATE_PROBE_OK")
    print(f"executed_rows={built['payload']['summary']['executedRowCount']}")
    print(f"candidate_installed={built['payload']['summary']['candidateInstalled']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
