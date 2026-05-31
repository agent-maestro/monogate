#!/usr/bin/env python3
"""FEF-P59 control-flow IR inventory."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p59_control_flow_ir_inventory.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P59_CONTROL_FLOW_IR_INVENTORY_PASS"

SOURCE_PACKETS = {
    "P51": ROOT / "reports/evidence_packets/fef_p51_branch_control_flow_blocker_gate.json",
    "P57": ROOT / "reports/evidence_packets/fef_p57_selected_branch_closure_matrix.json",
    "P58": ROOT / "reports/evidence_packets/fef_p58_branch_gap_private_review_addendum.json",
}

CLAIM_FLAGS = {
    "control_flow_ir_inventory_claim": False,
    "control_flow_ir_implemented": False,
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
    "FEF-P59 records a control-flow IR inventory only.",
    "FEF-P59 does not implement a new IR in Forge or eFrog.",
    "FEF-P59 does not add a new frontend lowering.",
    "FEF-P59 does not claim general branch/control-flow support.",
    "FEF-P59 does not claim branch/control-flow re-ingest support.",
    "FEF-P59 does not claim full non-generated source roundtrip.",
    "FEF-P59 does not claim arbitrary C/Rust source-family support.",
    "FEF-P59 does not record reviewer approval or rejection.",
    "FEF-P59 does not publish a package.",
    "FEF-P59 does not enable checkout or commerce.",
    "FEF-P59 does not claim public readiness.",
    "FEF-P59 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P59 does not claim runtime performance.",
    "FEF-P59 does not claim hardware, silicon, proof, Pro-target, production, or all-target readiness.",
]

IR_NODES = [
    {
        "id": "cfg_entry",
        "category": "structure",
        "purpose": "single entry point for a lifted function body",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "cfg_exit",
        "category": "structure",
        "purpose": "single normalized exit for return-value comparison and source roundtrip",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "basic_block",
        "category": "structure",
        "purpose": "ordered side-effect-aware statement container",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "condition_expr",
        "category": "predicate",
        "purpose": "typed boolean expression with explicit numeric comparison semantics",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "branch",
        "category": "control",
        "purpose": "conditional edge from one block to true/false successors",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "merge",
        "category": "control",
        "purpose": "join point for branch outcomes, fallthrough, and else-if chains",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "return_value",
        "category": "control",
        "purpose": "explicit return edge and returned expression",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "assignment",
        "category": "state",
        "purpose": "mutable local update needed before general branches or loops",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "phi_or_select",
        "category": "state",
        "purpose": "merged scalar value after branch alternatives",
        "requiredForGeneralSupport": True,
    },
    {
        "id": "unsupported_construct",
        "category": "boundary",
        "purpose": "fail-closed marker for loops, effects, calls, memory, labels, and unsupported branch forms",
        "requiredForGeneralSupport": True,
    },
]

SELECTED_MAPPINGS = [
    {
        "caseId": "c_ternary_select_v0",
        "sourceLanguage": "c",
        "selectedFeature": "ternary_select",
        "currentLowering": "guarded_affine_selector_step01",
        "candidateIrPath": ["condition_expr", "phi_or_select", "return_value"],
        "missingForGeneralization": ["typed condition semantics", "source roundtrip AST shape"],
    },
    {
        "caseId": "c_if_early_return_relu_v0",
        "sourceLanguage": "c",
        "selectedFeature": "if_early_return",
        "currentLowering": "guarded_affine_selector_step01",
        "candidateIrPath": ["cfg_entry", "condition_expr", "branch", "return_value", "cfg_exit"],
        "missingForGeneralization": ["fallthrough normalization", "multiple return normalization"],
    },
    {
        "caseId": "c_if_else_clamp_v0",
        "sourceLanguage": "c",
        "selectedFeature": "if_else_clamp",
        "currentLowering": "nested_guarded_affine_selector_step01",
        "candidateIrPath": ["condition_expr", "branch", "merge", "phi_or_select", "return_value"],
        "missingForGeneralization": ["else-if chain normalization", "dominance and merge proof obligations"],
    },
    {
        "caseId": "rust_if_expr_relu_v0",
        "sourceLanguage": "rust",
        "selectedFeature": "if_expression",
        "currentLowering": "guarded_affine_selector_step01",
        "candidateIrPath": ["condition_expr", "phi_or_select", "return_value"],
        "missingForGeneralization": ["expression-valued branch typing", "Rust block expression boundaries"],
    },
    {
        "caseId": "rust_if_return_clamp_v0",
        "sourceLanguage": "rust",
        "selectedFeature": "if_return_clamp",
        "currentLowering": "nested_guarded_affine_selector_step01",
        "candidateIrPath": ["cfg_entry", "condition_expr", "branch", "return_value", "merge", "cfg_exit"],
        "missingForGeneralization": ["early-return normalization", "fallthrough and merge semantics"],
    },
]

UNSUPPORTED_FORMS = [
    {
        "id": "nested_statement_branches",
        "status": "blocked",
        "reason": "selected closures do not cover arbitrary nested statement bodies",
        "nextValidator": "nested_branch_fixture_matrix",
    },
    {
        "id": "boolean_compound_conditions",
        "status": "blocked",
        "reason": "selected closures do not cover short-circuit and/or condition semantics",
        "nextValidator": "compound_condition_semantics_gate",
    },
    {
        "id": "mutable_assignments_across_branches",
        "status": "blocked",
        "reason": "selected closures are scalar return-only or expression-valued cases",
        "nextValidator": "assignment_phi_fixture_gate",
    },
    {
        "id": "loops_and_back_edges",
        "status": "blocked",
        "reason": "candidate IR needs loop headers, latches, variants, and boundedness policy",
        "nextValidator": "loop_construct_blocker_gate",
    },
    {
        "id": "side_effecting_calls_or_memory",
        "status": "blocked",
        "reason": "current selected branch evidence is side-effect free",
        "nextValidator": "side_effect_boundary_inventory",
    },
    {
        "id": "source_preserving_roundtrip",
        "status": "blocked",
        "reason": "generated-target re-ingest exists, but non-generated source-preserving branch roundtrip does not",
        "nextValidator": "non_generated_branch_roundtrip_gate",
    },
]

SEMANTIC_OBLIGATIONS = [
    {
        "id": "condition_truth_semantics",
        "status": "open",
        "description": "C/Rust comparison and boolean semantics must be explicit before branch equivalence claims.",
    },
    {
        "id": "dominance_and_merge_preservation",
        "status": "open",
        "description": "Each selected value must come from a dominating definition or explicit phi/select merge.",
    },
    {
        "id": "return_and_fallthrough_preservation",
        "status": "open",
        "description": "Early returns and fallthrough returns must normalize to equivalent exit behavior.",
    },
    {
        "id": "assignment_order_preservation",
        "status": "open",
        "description": "Mutable updates must preserve statement order and branch-local state.",
    },
    {
        "id": "unsupported_construct_fail_closed",
        "status": "open",
        "description": "Loops, labels, effects, calls, and memory must fail closed until separately validated.",
    },
    {
        "id": "source_ast_roundtrip_boundary",
        "status": "open",
        "description": "Non-generated source branches need a source AST boundary before full roundtrip claims.",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_summaries() -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for phase, path in SOURCE_PACKETS.items():
        packet = read_json(path)
        summaries[phase] = {
            "artifactId": packet.get("artifactId"),
            "title": packet.get("title"),
            "packetPath": str(path.relative_to(ROOT)),
            "reviewDecision": packet.get("reviewDecision"),
            "validationStatus": packet.get("validationStatus"),
            "semanticStrength": packet.get("semanticStrength"),
            "semanticReview": packet.get("semanticReview", {}),
            "claimFlagsAllFalse": all(value is False for value in packet.get("claimFlags", {}).values()),
        }
    return summaries


def build_summary(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    p51 = sources["P51"]["semanticReview"]
    p57 = sources["P57"]["semanticReview"]
    p58 = sources["P58"]["semanticReview"]
    return {
        "sourcePacketCount": len(sources),
        "allSourcePacketsValidationPass": all(item["validationStatus"] == "pass" for item in sources.values()),
        "allSourcePacketClaimFlagsFalse": all(item["claimFlagsAllFalse"] for item in sources.values()),
        "selectedBranchCaseCount": p57["selectedBranchCaseCount"],
        "selectedBranchClosureCount": p57["selectedBranchClosureCount"],
        "selectedBranchReingestPacketCount": p57["totalReingestPacketCount"],
        "selectedBranchPacketSampleComparisons": p57["totalPacketSampleComparisons"],
        "p51SelectedBlockedCount": p51["blockedCount"],
        "p58BlockedGapCount": p58["blockedGapCount"],
        "irNodeCount": len(IR_NODES),
        "requiredIrNodeCount": sum(1 for node in IR_NODES if node["requiredForGeneralSupport"] is True),
        "selectedMappingCount": len(SELECTED_MAPPINGS),
        "unsupportedFormCount": len(UNSUPPORTED_FORMS),
        "semanticObligationCount": len(SEMANTIC_OBLIGATIONS),
        "openSemanticObligationCount": sum(1 for item in SEMANTIC_OBLIGATIONS if item["status"] == "open"),
        "controlFlowIrImplemented": False,
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
    sources = source_summaries()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p59-control-flow-ir-inventory",
        "decision": "control_flow_ir_inventory_recorded_general_support_blocked",
        "sourcePackets": sources,
        "summary": build_summary(sources),
        "irNodes": copy.deepcopy(IR_NODES),
        "selectedClosureMappings": copy.deepcopy(SELECTED_MAPPINGS),
        "unsupportedForms": copy.deepcopy(UNSUPPORTED_FORMS),
        "semanticObligations": copy.deepcopy(SEMANTIC_OBLIGATIONS),
        "requiredValidators": [
            "control_flow_ir_schema",
            "nested_branch_fixture_matrix",
            "assignment_phi_fixture_gate",
            "compound_condition_semantics_gate",
            "unsupported_constructs_blocker_gate",
            "non_generated_branch_roundtrip_gate",
            "formal_obligation_inventory",
        ],
        "allowedPrivateReviewerStatements": [
            "P59 records a candidate control-flow IR inventory for review.",
            "The five selected P57 branch closures can be described using the candidate IR vocabulary.",
            "P59 names unsupported forms and semantic obligations before any general branch/control-flow support claim.",
        ],
        "blockedStatements": [
            "The control-flow IR is implemented.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Arbitrary C/Rust source-family support is established.",
            "A reviewer has approved the bundle.",
            "Forge/eFrog is public-ready.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "releaseGates": [
            {"id": "control_flow_ir_inventory", "status": "recorded"},
            {"id": "control_flow_ir_implementation", "status": "not_started"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "unsupported_constructs_policy", "status": "blocked"},
            {"id": "non_generated_branch_roundtrip", "status": "blocked"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "public_release", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "nextMilestones": [
            "Define a machine-readable control-flow IR schema without enabling support claims.",
            "Build a nested branch fixture matrix against the IR inventory.",
            "Build an unsupported constructs blocker gate for loops, effects, calls, memory, and labels.",
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
        "title": "FEF-P59 Control-Flow IR Inventory",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "control_flow_ir_inventory_recorded_general_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Control-flow IR inventory only; no IR implementation, new frontend lowering, general branch/control-flow support, branch re-ingest, full source roundtrip, arbitrary source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P59 defines the candidate IR vocabulary needed beyond selected branch fixtures.",
            "The five selected P57 closures are mapped to candidate IR paths.",
            "Unsupported branch/control-flow forms and semantic obligations remain explicitly blocked.",
            "General branch/control-flow support remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p59_control_flow_ir_inventory.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p59_control_flow_ir_inventory.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p59_control_flow_ir_inventory.v0",
        "date": DATE,
        "title": "FEF-P59 Control-Flow IR Inventory",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Define a machine-readable control-flow IR schema or build the unsupported constructs blocker gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    node_rows = [
        "| Node | Category | Purpose | Required |",
        "|---|---|---|---:|",
    ]
    for node in payload["irNodes"]:
        node_rows.append(
            f"| `{node['id']}` | `{node['category']}` | {node['purpose']} | `{node['requiredForGeneralSupport']}` |"
        )
    mapping_rows = [
        "| Case | Source | Feature | Current Lowering | Candidate IR Path |",
        "|---|---|---|---|---|",
    ]
    for row in payload["selectedClosureMappings"]:
        mapping_rows.append(
            f"| `{row['caseId']}` | `{row['sourceLanguage']}` | `{row['selectedFeature']}` | `{row['currentLowering']}` | `{', '.join(row['candidateIrPath'])}` |"
        )
    unsupported_rows = [
        "| Unsupported Form | Status | Reason | Next Validator |",
        "|---|---|---|---|",
    ]
    for row in payload["unsupportedForms"]:
        unsupported_rows.append(
            f"| `{row['id']}` | `{row['status']}` | {row['reason']} | `{row['nextValidator']}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P59 Control-Flow IR Inventory",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P59 maps the gap between selected branch closures and real branch/control-flow support.",
            "",
            "## Summary",
            "",
            f"- Source packets: `{summary['sourcePacketCount']}`",
            f"- Selected branch closures: `{summary['selectedBranchClosureCount']}`",
            f"- P51 selected blockers remaining: `{summary['p51SelectedBlockedCount']}`",
            f"- Candidate IR nodes: `{summary['irNodeCount']}`",
            f"- Selected closure mappings: `{summary['selectedMappingCount']}`",
            f"- Unsupported forms: `{summary['unsupportedFormCount']}`",
            f"- Open semantic obligations: `{summary['openSemanticObligationCount']}`",
            f"- Control-flow IR implemented: `{summary['controlFlowIrImplemented']}`",
            "",
            "## Candidate IR Nodes",
            "",
            *node_rows,
            "",
            "## Selected Closure Mappings",
            "",
            *mapping_rows,
            "",
            "## Unsupported Forms",
            "",
            *unsupported_rows,
            "",
            "## Semantic Obligations",
            "",
            *[f"- `{item['id']}`: {item['description']} ({item['status']})" for item in payload["semanticObligations"]],
            "",
            "## Boundary",
            "",
            "- Inventory only; no new IR implementation.",
            "- No general branch/control-flow support claim.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P59 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P59 status")
    summary = payload["summary"]
    if summary["sourcePacketCount"] != 3:
        raise ValueError("expected three source packets")
    if summary["allSourcePacketsValidationPass"] is not True:
        raise ValueError("all source packets must validate")
    if summary["allSourcePacketClaimFlagsFalse"] is not True:
        raise ValueError("source packet claim flags must remain false")
    if summary["selectedBranchCaseCount"] != 5 or summary["selectedBranchClosureCount"] != 5:
        raise ValueError("expected five selected branch closures")
    if summary["selectedBranchReingestPacketCount"] != 10:
        raise ValueError("expected ten selected branch re-ingest packets")
    if summary["selectedBranchPacketSampleComparisons"] != 58:
        raise ValueError("unexpected selected branch sample total")
    if summary["p51SelectedBlockedCount"] != 0:
        raise ValueError("P51 selected blockers should remain zero")
    if summary["p58BlockedGapCount"] != 6:
        raise ValueError("P58 should keep six blocked gaps")
    if summary["irNodeCount"] != 10 or summary["requiredIrNodeCount"] != 10:
        raise ValueError("expected ten required candidate IR nodes")
    if summary["selectedMappingCount"] != 5:
        raise ValueError("expected five selected closure mappings")
    if summary["unsupportedFormCount"] != 6:
        raise ValueError("expected six unsupported forms")
    if summary["semanticObligationCount"] != 6 or summary["openSemanticObligationCount"] != 6:
        raise ValueError("expected six open semantic obligations")
    expected_cases = {
        "c_ternary_select_v0",
        "c_if_early_return_relu_v0",
        "c_if_else_clamp_v0",
        "rust_if_expr_relu_v0",
        "rust_if_return_clamp_v0",
    }
    if {row["caseId"] for row in payload["selectedClosureMappings"]} != expected_cases:
        raise ValueError("unexpected selected closure mapping set")
    for row in payload["unsupportedForms"]:
        if row["status"] != "blocked":
            raise ValueError(f"unsupported form must remain blocked: {row['id']}")
    for item in payload["semanticObligations"]:
        if item["status"] != "open":
            raise ValueError(f"semantic obligation must remain open: {item['id']}")
    for key in [
        "controlFlowIrImplemented",
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
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p59_control_flow_ir_inventory_{STAMP}.json"
    report_path = report_dir / f"fef_p59_control_flow_ir_inventory_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p59_control_flow_ir_inventory.json"
    feed_path = command_feed_dir / f"fef_p59_control_flow_ir_inventory_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p59_control_flow_ir_inventory")
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
    print("FEF_P59_CONTROL_FLOW_IR_INVENTORY_OK")
    print(f"ir_nodes={built['payload']['summary']['irNodeCount']}")
    print(f"unsupported_forms={built['payload']['summary']['unsupportedFormCount']}")
    print(f"open_obligations={built['payload']['summary']['openSemanticObligationCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
