#!/usr/bin/env python3
"""FEF-P87 guarded-div re-ingest boundary probe for the compound condition."""

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

from scripts import fef_p86_compound_condition_guarded_div_installation_candidate_probe as p86  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p87_compound_condition_guarded_div_reingest_boundary_probe.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P87_COMPOUND_CONDITION_GUARDED_DIV_REINGEST_BOUNDARY_PROBE_PASS"

P86_PACKET = ROOT / "reports/evidence_packets/fef_p86_compound_condition_guarded_div_installation_candidate_probe.json"
P86_RESULT = ROOT / "python/results/fef_p86_compound_condition_guarded_div_installation_candidate_probe/fef_p86_compound_condition_guarded_div_installation_candidate_probe_2026_05_31.json"

CLAIM_FLAGS = {
    "guarded_div_reingest_boundary_probe_claim": False,
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
    "FEF-P87 records a fail-closed re-ingest boundary probe only.",
    "FEF-P87 does not install the guarded-div primitive in eFrog or Forge.",
    "FEF-P87 does not change eFrog or Forge source code.",
    "FEF-P87 does not execute re-ingested code.",
    "FEF-P87 does not claim supported compound-condition re-ingest.",
    "FEF-P87 does not claim compiler-wide short-circuit semantics.",
    "FEF-P87 does not claim compound-condition support.",
    "FEF-P87 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P87 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def boundary_contract(p86_payload: dict[str, Any]) -> dict[str, Any]:
    candidate = p86_payload["installationCandidate"]
    return {
        "contractId": "selected_guarded_div_reingest_boundary_contract_v0",
        "candidateId": candidate["candidateId"],
        "scope": candidate["scope"],
        "status": "boundary_probe_pass_reingest_execution_blocked",
        "requiredHelperSurface": ["nonzero01", "guarded_div"],
        "requiredBoundaryProperties": [
            "candidate fixture id must match c_and_short_circuit_guard_v0",
            "guarded_div must carry an explicit guard argument",
            "zero-denominator rows must preserve division non-evaluation",
            "left-false rows must preserve right-side non-evaluation",
            "all selected rows must still match P77 expected values before any re-ingest execution is allowed",
            "candidate must remain uninstalled until an explicit implementation phase is approved",
        ],
        "actualReingestExecutionPerformed": False,
        "recompiledPythonExecuted": False,
        "installedInEfrog": False,
        "installedInForge": False,
        "compilerBehaviorChanged": False,
    }


def build_boundary_rows(p86_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in p86_payload["probeResult"]["rows"]:
        left_false = row["intermediates"]["lhs"] == 0.0
        zero_denominator = bool(row["zeroDenominator"])
        division_evaluated = bool(row["divisionEvaluated"])
        boundary_status = "pass"
        reasons = []
        if zero_denominator and division_evaluated:
            boundary_status = "fail"
            reasons.append("zero-denominator row evaluated division")
        if left_false and row["intermediates"]["rhsEvaluated"]:
            boundary_status = "fail"
            reasons.append("left-false row evaluated right-side guard")
        if row["pass"] is not True:
            boundary_status = "fail"
            reasons.append("candidate row did not match expected value")
        if not reasons:
            reasons.append("selected boundary preserved")
        rows.append(
            {
                "sampleId": row["sampleId"],
                "path": row["path"],
                "inputs": dict(row["inputs"]),
                "expected": row["expected"],
                "observed": row["observed"],
                "absError": row["absError"],
                "candidatePass": row["pass"],
                "zeroDenominator": zero_denominator,
                "leftFalse": left_false,
                "divisionEvaluated": division_evaluated,
                "rhsEvaluated": row["intermediates"]["rhsEvaluated"],
                "boundaryStatus": boundary_status,
                "reasons": reasons,
            }
        )
    return rows


def build_boundary_probe(contract: dict[str, Any], p86_payload: dict[str, Any]) -> dict[str, Any]:
    rows = build_boundary_rows(p86_payload)
    zero_rows = [row for row in rows if row["zeroDenominator"]]
    left_false_rows = [row for row in rows if row["leftFalse"]]
    return {
        "probeId": "selected_guarded_div_reingest_boundary_probe_v0",
        "contractId": contract["contractId"],
        "candidateId": contract["candidateId"],
        "scope": contract["scope"],
        "rowCount": len(rows),
        "boundaryPassCount": sum(1 for row in rows if row["boundaryStatus"] == "pass"),
        "boundaryFailCount": sum(1 for row in rows if row["boundaryStatus"] == "fail"),
        "zeroDenominatorRowCount": len(zero_rows),
        "zeroDenominatorRowsWithDivisionSkipped": sum(1 for row in zero_rows if row["divisionEvaluated"] is False),
        "leftFalseRowCount": len(left_false_rows),
        "leftFalseRowsWithRightSideSkipped": sum(1 for row in left_false_rows if row["rhsEvaluated"] is False),
        "allCandidateRowsPass": all(row["candidatePass"] is True for row in rows),
        "nonEvaluationBoundaryPreserved": all(row["boundaryStatus"] == "pass" for row in rows),
        "actualReingestExecutionPerformed": False,
        "recompiledPythonExecuted": False,
        "candidateInstalled": False,
        "rows": rows,
    }


def build_summary(p86_packet: dict[str, Any], p86_payload: dict[str, Any], contract: dict[str, Any], probe: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p86ValidationPass": p86_packet["validationStatus"] == "pass",
        "p86ClaimFlagsAllFalse": all(value is False for value in p86_packet["claimFlags"].values()),
        "selectedFixtureId": p86_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p86_payload["summary"]["selectedFixtureStillBlocked"],
        "contractId": contract["contractId"],
        "contractStatus": contract["status"],
        "probeId": probe["probeId"],
        "requiredHelperSurfaceCount": len(contract["requiredHelperSurface"]),
        "requiredBoundaryPropertyCount": len(contract["requiredBoundaryProperties"]),
        "rowCount": probe["rowCount"],
        "boundaryPassCount": probe["boundaryPassCount"],
        "boundaryFailCount": probe["boundaryFailCount"],
        "zeroDenominatorRowCount": probe["zeroDenominatorRowCount"],
        "zeroDenominatorRowsWithDivisionSkipped": probe["zeroDenominatorRowsWithDivisionSkipped"],
        "leftFalseRowCount": probe["leftFalseRowCount"],
        "leftFalseRowsWithRightSideSkipped": probe["leftFalseRowsWithRightSideSkipped"],
        "allCandidateRowsPass": probe["allCandidateRowsPass"],
        "nonEvaluationBoundaryPreserved": probe["nonEvaluationBoundaryPreserved"],
        "failClosedReingestBoundaryProbePerformed": True,
        "actualReingestExecutionPerformed": probe["actualReingestExecutionPerformed"],
        "recompiledPythonExecuted": probe["recompiledPythonExecuted"],
        "candidateInstalled": probe["candidateInstalled"],
        "sourcePrimitiveInstalled": False,
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
    p86_packet = read_json(P86_PACKET)
    p86_payload = read_json(P86_RESULT)
    p86.validate_payload(p86_payload)
    contract = boundary_contract(p86_payload)
    probe = build_boundary_probe(contract, p86_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p87-compound-condition-guarded-div-reingest-boundary-probe",
        "decision": "selected_guarded_div_reingest_boundary_probe_pass_execution_blocked",
        "sourcePacket": {
            "phase": "P86",
            "packetPath": str(P86_PACKET.relative_to(ROOT)),
            "resultPath": str(P86_RESULT.relative_to(ROOT)),
            "reviewDecision": p86_packet["reviewDecision"],
            "validationStatus": p86_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p86_payload["selectedFixture"]),
        "boundaryContract": contract,
        "boundaryProbe": probe,
        "summary": build_summary(p86_packet, p86_payload, contract, probe),
        "releaseGates": [
            {"id": "selected_guarded_div_reingest_boundary_probe", "status": "pass_execution_blocked"},
            {"id": "non_evaluation_boundary", "status": "preserved"},
            {"id": "actual_reingest_execution", "status": "blocked_not_performed"},
            {"id": "source_primitive_installation", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P87 records a fail-closed re-ingest boundary probe for the selected guarded-div candidate.",
            "The boundary probe preserves zero-denominator division skip and left-false right-side skip over the selected rows.",
            "P87 does not install the candidate or execute re-ingested code.",
            "Compound-condition re-ingest support remains blocked.",
        ],
        "blockedStatements": [
            "Re-ingested compound-condition code executed successfully.",
            "Compound-condition re-ingest is supported.",
            "The selected guarded-div primitive is installed in eFrog or Forge.",
            "The selected boundary probe proves compiler-wide short-circuit semantics.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Decide whether to stop at reviewer intake for P47-P87 or create an explicit implementation-change proposal.",
            "Keep actual re-ingest execution blocked until installation is intentionally approved.",
            "Record private reviewer response to the P47-P87 branch/control-flow bundle.",
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
        "title": "FEF-P87 Compound-Condition Guarded-Div Re-ingest Boundary Probe",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_guarded_div_reingest_boundary_probe_pass_execution_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected fail-closed re-ingest boundary probe only; no installed eFrog/Forge behavior change, actual re-ingest execution, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P87 checks the selected guarded-div candidate's re-ingest boundary.",
            "Zero-denominator and left-false non-evaluation boundaries are preserved in the probe.",
            "Actual re-ingest execution remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p87_compound_condition_guarded_div_reingest_boundary_probe.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p87_compound_condition_guarded_div_reingest_boundary_probe.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p87_compound_condition_guarded_div_reingest_boundary_probe.v0",
        "date": DATE,
        "title": "FEF-P87 Compound-Condition Guarded-Div Re-ingest Boundary Probe",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Choose private reviewer intake or explicit implementation-change proposal.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        f"- `{row['sampleId']}` `{row['boundaryStatus']}` div-eval `{row['divisionEvaluated']}` rhs-eval `{row['rhsEvaluated']}`"
        for row in payload["boundaryProbe"]["rows"]
    ]
    return "\n".join(
        [
            "# FEF-P87 Compound-Condition Guarded-Div Re-ingest Boundary Probe",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P87 records a fail-closed re-ingest boundary probe without executing re-ingested code.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Contract: `{summary['contractId']}`",
            f"- Probe: `{summary['probeId']}`",
            f"- Boundary pass count: `{summary['boundaryPassCount']}`",
            f"- Boundary fail count: `{summary['boundaryFailCount']}`",
            f"- Zero-denominator rows with division skipped: `{summary['zeroDenominatorRowsWithDivisionSkipped']}`",
            f"- Left-false rows with right side skipped: `{summary['leftFalseRowsWithRightSideSkipped']}`",
            f"- Actual re-ingest execution performed: `{summary['actualReingestExecutionPerformed']}`",
            f"- Candidate installed: `{summary['candidateInstalled']}`",
            "",
            "## Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected fail-closed boundary probe only.",
            "- No installed eFrog or Forge behavior change.",
            "- No actual re-ingest execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P87 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P87 status")
    p86.validate_payload(read_json(P86_RESULT))
    summary = payload["summary"]
    for key in [
        "p86ValidationPass",
        "p86ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allCandidateRowsPass",
        "nonEvaluationBoundaryPreserved",
        "failClosedReingestBoundaryProbePerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["contractStatus"] != "boundary_probe_pass_reingest_execution_blocked":
        raise ValueError("unexpected boundary contract status")
    if summary["rowCount"] != 7:
        raise ValueError("expected seven boundary rows")
    if summary["boundaryPassCount"] != 7 or summary["boundaryFailCount"] != 0:
        raise ValueError("expected all boundary checks to pass")
    if summary["zeroDenominatorRowCount"] != 2 or summary["zeroDenominatorRowsWithDivisionSkipped"] != 2:
        raise ValueError("expected zero-denominator rows to skip division")
    if summary["leftFalseRowCount"] != 3 or summary["leftFalseRowsWithRightSideSkipped"] != 3:
        raise ValueError("expected left-false rows to skip right-side guard")
    if summary["requiredHelperSurfaceCount"] != 2:
        raise ValueError("expected helper boundary surface count")
    if summary["requiredBoundaryPropertyCount"] != 6:
        raise ValueError("expected boundary property count")
    for key in [
        "actualReingestExecutionPerformed",
        "recompiledPythonExecuted",
        "candidateInstalled",
        "sourcePrimitiveInstalled",
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
    result_path = out_dir / f"fef_p87_compound_condition_guarded_div_reingest_boundary_probe_{STAMP}.json"
    report_path = report_dir / f"fef_p87_compound_condition_guarded_div_reingest_boundary_probe_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p87_compound_condition_guarded_div_reingest_boundary_probe.json"
    feed_path = command_feed_dir / f"fef_p87_compound_condition_guarded_div_reingest_boundary_probe_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p87_compound_condition_guarded_div_reingest_boundary_probe")
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
    print("FEF_P87_COMPOUND_CONDITION_GUARDED_DIV_REINGEST_BOUNDARY_PROBE_OK")
    print(f"boundary_pass_count={built['payload']['summary']['boundaryPassCount']}")
    print(f"actual_reingest_execution={built['payload']['summary']['actualReingestExecutionPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
