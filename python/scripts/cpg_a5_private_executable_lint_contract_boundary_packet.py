#!/usr/bin/env python3
"""CPG-A5 private executable lint contract boundary packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector as cpg_a4  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_executable_lint_contract_boundary_packet.v0"
STATUS = "CPG_A5_PRIVATE_EXECUTABLE_LINT_CONTRACT_BOUNDARY_PACKET_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A6 private lint contract boundary review or static test selector"

TRUE_CLAIM_FLAGS = {
    "cpg_a4_consumed",
    "lint_contract_boundary_packet_created",
    "contract_input_shape_recorded",
    "contract_output_shape_recorded",
    "contract_rejection_obligations_recorded",
    "execution_gate_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "cpg_a4_consumed": True,
    "lint_contract_boundary_packet_created": True,
    "contract_input_shape_recorded": True,
    "contract_output_shape_recorded": True,
    "contract_rejection_obligations_recorded": True,
    "execution_gate_recorded": True,
    "d109_hold_respected": True,
    "executable_lint_contract_created": False,
    "executable_lint_contract_executed": False,
    "lint_contract_implementation_created": False,
    "lint_contract_static_tests_created": False,
    "lint_contract_static_tests_executed": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "lint_engine_implemented": False,
    "lint_engine_executed": False,
    "fixture_runner_implemented": False,
    "fixture_runner_executed": False,
    "automatic_rewrite_enabled": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "automatic_lowering_safety_claim": False,
    "runtime_performance_claim": False,
    "code_generation_claim": False,
    "runtime_lowering_changed": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_package_release_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "scientific_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "ip_license_terms_finalized": False,
    "accelerator_card_ready": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "CPG-A5 is a private boundary packet for a possible executable lint contract; it is not the executable contract.",
    "CPG-A5 records input, output, rejection, and execution-gate obligations only.",
    "CPG-A5 does not implement or execute a compiler plugin, lint engine, lint contract, fixture runner, rewrite engine, code generator, or runtime lowering path.",
    "CPG-A5 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A5 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def input_shape() -> list[dict[str, str]]:
    return [
        {
            "field": "source_snippet",
            "requirement": "short source expression or statement under advisory review",
            "boundary": "the snippet is not compiled, rewritten, or executed by this packet",
        },
        {
            "field": "expression_family",
            "requirement": "bounded family label such as expm1_boundary or positive_log_exp_guard",
            "boundary": "family labels are hints, not completeness or theorem-discovery claims",
        },
        {
            "field": "evidence_pointer",
            "requirement": "optional private witness/evidence packet id when one is known",
            "boundary": "a pointer does not establish applicability to the snippet",
        },
        {
            "field": "guard_context",
            "requirement": "explicit domain or guard notes supplied by the reviewer or caller",
            "boundary": "the contract may report missing guards but does not prove guards",
        },
    ]


def output_shape() -> list[dict[str, str]]:
    return [
        {
            "output": "advisory_notice",
            "allowed": "human-readable lint/profile/review note",
            "blocked": "automatic rewrite, replacement, or lowering instruction",
        },
        {
            "output": "guard_checklist_item",
            "allowed": "explicit guard reminder tied to a bounded evidence pointer",
            "blocked": "claim that the guard is satisfied or mechanically proven",
        },
        {
            "output": "evidence_pointer",
            "allowed": "private packet id, witness id, or report path for reviewer follow-up",
            "blocked": "public readiness, library completeness, or SDK stability statement",
        },
        {
            "output": "blocked_claim_notice",
            "allowed": "notice that a requested compiler/performance/public claim is out of scope",
            "blocked": "soft approval wording for the blocked claim",
        },
    ]


def rejection_obligations() -> list[dict[str, Any]]:
    return [
        {
            "obligationId": "reject_automatic_rewrite_or_lowering",
            "mustReject": ["automatic_rewrite", "automatic_lowering", "replacement_patch"],
            "requiredReason": "The advisory lane has no semantic-preservation or lowering-safety proof.",
            "blockedClaims": ["semantic_preservation_claim", "automatic_lowering_safety_claim"],
        },
        {
            "obligationId": "reject_runtime_or_training_savings_claim",
            "mustReject": ["runtime_speedup", "training_savings", "benchmark_win"],
            "requiredReason": "The contract boundary records no measurement protocol or benchmark execution.",
            "blockedClaims": ["runtime_performance_claim", "training_savings_claim"],
        },
        {
            "obligationId": "reject_public_or_package_readiness_claim",
            "mustReject": ["public_docs_ready", "package_release_ready", "sdk_stable"],
            "requiredReason": "Public copy, package release, and SDK stability require separate approval.",
            "blockedClaims": ["public_readiness_claim", "public_package_release_claim", "sdk_stability_claim"],
        },
        {
            "obligationId": "reject_guard_proven_or_theorem_discovered_claim",
            "mustReject": ["guard_proven", "new_theorem_discovered", "applicability_proven"],
            "requiredReason": "A lint contract may surface guard notes but cannot prove guards or discover theorems.",
            "blockedClaims": ["compiler_correctness_claim", "broad_eml_advantage_claim"],
        },
    ]


def execution_gates() -> list[dict[str, str]]:
    return [
        {
            "gateId": "contract_boundary_review_required",
            "status": "required_before_static_tests",
            "reason": "The boundary packet must be reviewed before static executable-contract tests are drafted.",
        },
        {
            "gateId": "static_test_fixtures_required",
            "status": "required_before_implementation",
            "reason": "Executable behavior must be checked against accepted and rejection examples before implementation.",
        },
        {
            "gateId": "implementation_hold_gate_required",
            "status": "required_before_any_lint_engine",
            "reason": "A separate hold gate must explicitly approve implementation scope.",
        },
        {
            "gateId": "public_docs_gate_required",
            "status": "required_before_public_copy",
            "reason": "Public docs or package wording requires separate approval and readiness evidence.",
        },
    ]


def build_payload() -> dict[str, Any]:
    selector = cpg_a4.build_payload()
    cpg_a4.validate_payload(selector)
    inputs = input_shape()
    outputs = output_shape()
    rejections = rejection_obligations()
    gates = execution_gates()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "inputFieldCount": len(inputs),
        "outputFieldCount": len(outputs),
        "rejectionObligationCount": len(rejections),
        "executionGateCount": len(gates),
        "executableLintContractCreated": False,
        "executableLintContractExecuted": False,
        "lintContractImplementationCreated": False,
        "lintContractStaticTestsCreated": False,
        "lintContractStaticTestsExecuted": False,
        "compilerPluginImplemented": False,
        "compilerPluginExecuted": False,
        "lintEngineImplemented": False,
        "lintEngineExecuted": False,
        "fixtureRunnerImplemented": False,
        "fixtureRunnerExecuted": False,
        "compilerCorrectnessClaim": False,
        "semanticPreservationClaim": False,
        "automaticLoweringSafetyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="cpg-a5-private-executable-lint-contract-boundary-packet",
        artifact_type="private_executable_lint_contract_boundary_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "contractInputShape": inputs,
            "contractOutputShape": outputs,
            "contractRejectionObligations": rejections,
            "executionGates": gates,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "cpg-a4-private-compiler-plugin-static-fixture-review-or-lint-contract-selector":
        raise ValueError("CPG-A5 must consume CPG-A4")
    summary = payload["summary"]
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["inputFieldCount"] != len(payload["contractInputShape"]):
        raise ValueError("input count mismatch")
    if summary["outputFieldCount"] != len(payload["contractOutputShape"]):
        raise ValueError("output count mismatch")
    if summary["rejectionObligationCount"] != len(payload["contractRejectionObligations"]):
        raise ValueError("rejection obligation count mismatch")
    if summary["executionGateCount"] != len(payload["executionGates"]):
        raise ValueError("execution gate count mismatch")
    if {item["field"] for item in payload["contractInputShape"]} != {
        "source_snippet",
        "expression_family",
        "evidence_pointer",
        "guard_context",
    }:
        raise ValueError("unexpected contract input shape")
    if {item["output"] for item in payload["contractOutputShape"]} != {
        "advisory_notice",
        "guard_checklist_item",
        "evidence_pointer",
        "blocked_claim_notice",
    }:
        raise ValueError("unexpected contract output shape")
    gate_statuses = {gate["gateId"]: gate["status"] for gate in payload["executionGates"]}
    if gate_statuses["contract_boundary_review_required"] != "required_before_static_tests":
        raise ValueError("boundary review gate missing")
    if gate_statuses["implementation_hold_gate_required"] != "required_before_any_lint_engine":
        raise ValueError("implementation hold gate missing")
    for key in [
        "executableLintContractCreated",
        "executableLintContractExecuted",
        "lintContractImplementationCreated",
        "lintContractStaticTestsCreated",
        "lintContractStaticTestsExecuted",
        "compilerPluginImplemented",
        "compilerPluginExecuted",
        "lintEngineImplemented",
        "lintEngineExecuted",
        "fixtureRunnerImplemented",
        "fixtureRunnerExecuted",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "automaticLoweringSafetyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="private_lint_contract_boundary_no_execution",
        source=f"python/results/cpg_a5_private_executable_lint_contract_boundary_packet/cpg_a5_private_executable_lint_contract_boundary_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a5_private_executable_lint_contract_boundary_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "inputFieldCount": payload["summary"]["inputFieldCount"],
            "outputFieldCount": payload["summary"]["outputFieldCount"],
            "rejectionObligationCount": payload["summary"]["rejectionObligationCount"],
            "executionGateCount": payload["summary"]["executionGateCount"],
            "executableLintContractCreated": payload["summary"]["executableLintContractCreated"],
            "lintEngineImplemented": payload["summary"]["lintEngineImplemented"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A5 Private Executable Lint Contract Boundary Packet",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("input field count", payload["summary"]["inputFieldCount"]),
            ("output field count", payload["summary"]["outputFieldCount"]),
            ("rejection obligation count", payload["summary"]["rejectionObligationCount"]),
            ("execution gate count", payload["summary"]["executionGateCount"]),
            ("executable lint contract created", payload["summary"]["executableLintContractCreated"]),
            ("lint engine implemented", payload["summary"]["lintEngineImplemented"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Contract Input Shape",
                [f"- `{item['field']}`: {item['requirement']} Boundary: {item['boundary']}" for item in payload["contractInputShape"]],
            ),
            (
                "Contract Output Shape",
                [f"- `{item['output']}`: {item['allowed']} Blocked: {item['blocked']}" for item in payload["contractOutputShape"]],
            ),
            (
                "Rejection Obligations",
                [
                    f"- `{item['obligationId']}`: reject {', '.join(item['mustReject'])}. Reason: {item['requiredReason']}"
                    for item in payload["contractRejectionObligations"]
                ],
            ),
            (
                "Execution Gates",
                [f"- `{gate['gateId']}`: `{gate['status']}` - {gate['reason']}" for gate in payload["executionGates"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"cpg_a5_private_executable_lint_contract_boundary_packet_{STAMP}.json"
    report_path = report_dir / f"cpg_a5_private_executable_lint_contract_boundary_packet_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a5_private_executable_lint_contract_boundary_packet.json"
    feed_path = command_feed_dir / f"cpg_a5_private_executable_lint_contract_boundary_packet_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/cpg_a5_private_executable_lint_contract_boundary_packet",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("CPG_A5_PRIVATE_EXECUTABLE_LINT_CONTRACT_BOUNDARY_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
