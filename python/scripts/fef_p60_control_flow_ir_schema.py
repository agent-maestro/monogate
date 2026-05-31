#!/usr/bin/env python3
"""FEF-P60 control-flow IR schema checkpoint."""

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

from scripts import fef_p59_control_flow_ir_inventory as p59

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p60_control_flow_ir_schema.v0"
CONTROL_FLOW_IR_SCHEMA_VERSION = "monogate.control_flow_ir.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P60_CONTROL_FLOW_IR_SCHEMA_PASS"

P59_PACKET = ROOT / "reports/evidence_packets/fef_p59_control_flow_ir_inventory.json"

CLAIM_FLAGS = {
    "control_flow_ir_schema_claim": False,
    "control_flow_ir_implemented": False,
    "frontend_lowering_changed": False,
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
    "FEF-P60 records a control-flow IR schema checkpoint only.",
    "FEF-P60 does not implement the control-flow IR in Forge or eFrog.",
    "FEF-P60 does not add or widen frontend lowering.",
    "FEF-P60 does not claim general branch/control-flow support.",
    "FEF-P60 does not claim branch/control-flow re-ingest support.",
    "FEF-P60 does not claim full non-generated source roundtrip.",
    "FEF-P60 does not claim arbitrary C/Rust source-family support.",
    "FEF-P60 does not record reviewer approval or rejection.",
    "FEF-P60 does not publish a package.",
    "FEF-P60 does not enable checkout or commerce.",
    "FEF-P60 does not claim public readiness.",
    "FEF-P60 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P60 does not claim runtime performance.",
    "FEF-P60 does not claim hardware, silicon, proof, Pro-target, production, or all-target readiness.",
]

CONTROL_FLOW_IR_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": CONTROL_FLOW_IR_SCHEMA_VERSION,
    "title": "Monogate Control-Flow IR v0",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schemaVersion",
        "programId",
        "sourceLanguage",
        "functionName",
        "entryBlockId",
        "exitBlockId",
        "blocks",
        "unsupportedConstructs",
        "semanticObligations",
        "claimFlags",
        "nonClaims",
    ],
    "properties": {
        "schemaVersion": {"const": CONTROL_FLOW_IR_SCHEMA_VERSION},
        "programId": {"type": "string", "minLength": 1},
        "sourceLanguage": {"enum": ["c", "rust"]},
        "functionName": {"type": "string", "minLength": 1},
        "feature": {"type": "string", "minLength": 1},
        "entryBlockId": {"type": "string", "minLength": 1},
        "exitBlockId": {"type": "string", "minLength": 1},
        "blocks": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/block"}},
        "unsupportedConstructs": {"type": "array", "items": {"$ref": "#/$defs/unsupportedConstruct"}},
        "semanticObligations": {"type": "array", "items": {"$ref": "#/$defs/semanticObligation"}},
        "claimFlags": {"type": "object", "additionalProperties": {"const": False}},
        "nonClaims": {"type": "array", "items": {"type": "string"}},
    },
    "$defs": {
        "block": {
            "type": "object",
            "additionalProperties": False,
            "required": ["id", "kind", "statements", "terminator"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "kind": {"enum": ["cfg_entry", "basic_block", "merge", "cfg_exit"]},
                "statements": {"type": "array", "items": {"$ref": "#/$defs/statement"}},
                "terminator": {"$ref": "#/$defs/terminator"},
            },
        },
        "statement": {
            "type": "object",
            "additionalProperties": True,
            "required": ["kind"],
            "properties": {
                "kind": {"enum": ["assignment", "phi_or_select", "unsupported_construct"]},
                "target": {"type": "string"},
                "expr": {"type": "string"},
                "condition": {"type": "string"},
                "trueExpr": {"type": "string"},
                "falseExpr": {"type": "string"},
                "constructId": {"type": "string"},
            },
        },
        "terminator": {
            "type": "object",
            "additionalProperties": False,
            "required": ["kind"],
            "properties": {
                "kind": {"enum": ["branch", "return_value", "jump", "unreachable"]},
                "condition": {"type": "string"},
                "trueBlock": {"type": "string"},
                "falseBlock": {"type": "string"},
                "targetBlock": {"type": "string"},
                "value": {"type": "string"},
            },
        },
        "unsupportedConstruct": {
            "type": "object",
            "additionalProperties": False,
            "required": ["id", "status", "reason", "nextValidator"],
            "properties": {
                "id": {"type": "string"},
                "status": {"const": "blocked"},
                "reason": {"type": "string"},
                "nextValidator": {"type": "string"},
            },
        },
        "semanticObligation": {
            "type": "object",
            "additionalProperties": False,
            "required": ["id", "status", "description"],
            "properties": {
                "id": {"type": "string"},
                "status": {"const": "open"},
                "description": {"type": "string"},
            },
        },
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def branch_fragment(case_id: str, source_language: str, feature: str, blocks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": CONTROL_FLOW_IR_SCHEMA_VERSION,
        "programId": case_id,
        "sourceLanguage": source_language,
        "functionName": case_id.replace("_v0", ""),
        "feature": feature,
        "entryBlockId": "entry",
        "exitBlockId": "exit",
        "blocks": blocks,
        "unsupportedConstructs": copy.deepcopy(p59.UNSUPPORTED_FORMS),
        "semanticObligations": copy.deepcopy(p59.SEMANTIC_OBLIGATIONS),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def selected_ir_fragments() -> list[dict[str, Any]]:
    return [
        branch_fragment(
            "c_ternary_select_v0",
            "c",
            "ternary_select",
            [
                {
                    "id": "entry",
                    "kind": "cfg_entry",
                    "statements": [
                        {
                            "kind": "phi_or_select",
                            "target": "result",
                            "condition": "x > 0.0",
                            "trueExpr": "x",
                            "falseExpr": "0.0",
                        }
                    ],
                    "terminator": {"kind": "return_value", "value": "result"},
                },
                {"id": "exit", "kind": "cfg_exit", "statements": [], "terminator": {"kind": "unreachable"}},
            ],
        ),
        branch_fragment(
            "c_if_early_return_relu_v0",
            "c",
            "if_early_return",
            [
                {"id": "entry", "kind": "cfg_entry", "statements": [], "terminator": {"kind": "branch", "condition": "x > 0.0", "trueBlock": "then_return", "falseBlock": "fallthrough"}},
                {"id": "then_return", "kind": "basic_block", "statements": [], "terminator": {"kind": "return_value", "value": "x"}},
                {"id": "fallthrough", "kind": "basic_block", "statements": [], "terminator": {"kind": "return_value", "value": "0.0"}},
                {"id": "exit", "kind": "cfg_exit", "statements": [], "terminator": {"kind": "unreachable"}},
            ],
        ),
        branch_fragment(
            "c_if_else_clamp_v0",
            "c",
            "if_else_clamp",
            [
                {"id": "entry", "kind": "cfg_entry", "statements": [], "terminator": {"kind": "branch", "condition": "x < lo", "trueBlock": "lo_return", "falseBlock": "check_hi"}},
                {"id": "lo_return", "kind": "basic_block", "statements": [], "terminator": {"kind": "return_value", "value": "lo"}},
                {"id": "check_hi", "kind": "basic_block", "statements": [], "terminator": {"kind": "branch", "condition": "x > hi", "trueBlock": "hi_return", "falseBlock": "mid_return"}},
                {"id": "hi_return", "kind": "basic_block", "statements": [], "terminator": {"kind": "return_value", "value": "hi"}},
                {"id": "mid_return", "kind": "basic_block", "statements": [], "terminator": {"kind": "return_value", "value": "x"}},
                {"id": "exit", "kind": "cfg_exit", "statements": [], "terminator": {"kind": "unreachable"}},
            ],
        ),
        branch_fragment(
            "rust_if_expr_relu_v0",
            "rust",
            "if_expression",
            [
                {
                    "id": "entry",
                    "kind": "cfg_entry",
                    "statements": [
                        {
                            "kind": "phi_or_select",
                            "target": "result",
                            "condition": "x > 0.0",
                            "trueExpr": "x",
                            "falseExpr": "0.0",
                        }
                    ],
                    "terminator": {"kind": "return_value", "value": "result"},
                },
                {"id": "exit", "kind": "cfg_exit", "statements": [], "terminator": {"kind": "unreachable"}},
            ],
        ),
        branch_fragment(
            "rust_if_return_clamp_v0",
            "rust",
            "if_return_clamp",
            [
                {"id": "entry", "kind": "cfg_entry", "statements": [], "terminator": {"kind": "branch", "condition": "x < lo", "trueBlock": "lo_return", "falseBlock": "check_hi"}},
                {"id": "lo_return", "kind": "basic_block", "statements": [], "terminator": {"kind": "return_value", "value": "lo"}},
                {"id": "check_hi", "kind": "basic_block", "statements": [], "terminator": {"kind": "branch", "condition": "x > hi", "trueBlock": "hi_return", "falseBlock": "fallthrough"}},
                {"id": "hi_return", "kind": "basic_block", "statements": [], "terminator": {"kind": "return_value", "value": "hi"}},
                {"id": "fallthrough", "kind": "merge", "statements": [], "terminator": {"kind": "return_value", "value": "x"}},
                {"id": "exit", "kind": "cfg_exit", "statements": [], "terminator": {"kind": "unreachable"}},
            ],
        ),
    ]


def validate_schema_object(schema: dict[str, Any]) -> None:
    if schema["$id"] != CONTROL_FLOW_IR_SCHEMA_VERSION:
        raise ValueError("invalid control-flow IR schema id")
    required = set(schema["required"])
    for key in [
        "schemaVersion",
        "programId",
        "sourceLanguage",
        "functionName",
        "entryBlockId",
        "exitBlockId",
        "blocks",
        "unsupportedConstructs",
        "semanticObligations",
        "claimFlags",
        "nonClaims",
    ]:
        if key not in required:
            raise ValueError(f"missing required schema key: {key}")
    block_kinds = set(schema["$defs"]["block"]["properties"]["kind"]["enum"])
    if block_kinds != {"cfg_entry", "basic_block", "merge", "cfg_exit"}:
        raise ValueError("unexpected block kind set")
    statement_kinds = set(schema["$defs"]["statement"]["properties"]["kind"]["enum"])
    if statement_kinds != {"assignment", "phi_or_select", "unsupported_construct"}:
        raise ValueError("unexpected statement kind set")
    terminator_kinds = set(schema["$defs"]["terminator"]["properties"]["kind"]["enum"])
    if terminator_kinds != {"branch", "return_value", "jump", "unreachable"}:
        raise ValueError("unexpected terminator kind set")


def validate_fragment(fragment: dict[str, Any]) -> None:
    required = CONTROL_FLOW_IR_SCHEMA["required"]
    for key in required:
        if key not in fragment:
            raise ValueError(f"fragment missing required key: {key}")
    if fragment["schemaVersion"] != CONTROL_FLOW_IR_SCHEMA_VERSION:
        raise ValueError("fragment has wrong schema version")
    if fragment["sourceLanguage"] not in {"c", "rust"}:
        raise ValueError("unexpected source language")
    blocks = fragment["blocks"]
    block_ids = {block["id"] for block in blocks}
    if fragment["entryBlockId"] not in block_ids or fragment["exitBlockId"] not in block_ids:
        raise ValueError("entry/exit block ids must exist")
    if not any(block["kind"] == "cfg_entry" for block in blocks):
        raise ValueError("fragment needs cfg_entry block")
    if not any(block["kind"] == "cfg_exit" for block in blocks):
        raise ValueError("fragment needs cfg_exit block")
    terminator_kinds = {"branch", "return_value", "jump", "unreachable"}
    statement_kinds = {"assignment", "phi_or_select", "unsupported_construct"}
    for block in blocks:
        if block["kind"] not in {"cfg_entry", "basic_block", "merge", "cfg_exit"}:
            raise ValueError(f"unexpected block kind: {block['kind']}")
        if block["terminator"]["kind"] not in terminator_kinds:
            raise ValueError(f"unexpected terminator kind: {block['terminator']['kind']}")
        terminator = block["terminator"]
        for edge_key in ["trueBlock", "falseBlock", "targetBlock"]:
            if edge_key in terminator and terminator[edge_key] not in block_ids:
                raise ValueError(f"terminator edge points to missing block: {edge_key}")
        for statement in block["statements"]:
            if statement["kind"] not in statement_kinds:
                raise ValueError(f"unexpected statement kind: {statement['kind']}")
    if len(fragment["unsupportedConstructs"]) != 6:
        raise ValueError("expected six unsupported constructs")
    if len(fragment["semanticObligations"]) != 6:
        raise ValueError("expected six semantic obligations")
    if not all(value is False for value in fragment["claimFlags"].values()):
        raise ValueError("fragment claim flags must remain false")


def build_summary(p59_packet: dict[str, Any], fragments: list[dict[str, Any]]) -> dict[str, Any]:
    p59_summary = p59_packet["semanticReview"]
    return {
        "sourcePacketCount": 1,
        "p59ValidationPass": p59_packet["validationStatus"] == "pass",
        "p59ClaimFlagsAllFalse": all(value is False for value in p59_packet["claimFlags"].values()),
        "schemaRequiredFieldCount": len(CONTROL_FLOW_IR_SCHEMA["required"]),
        "schemaBlockKindCount": len(CONTROL_FLOW_IR_SCHEMA["$defs"]["block"]["properties"]["kind"]["enum"]),
        "schemaStatementKindCount": len(CONTROL_FLOW_IR_SCHEMA["$defs"]["statement"]["properties"]["kind"]["enum"]),
        "schemaTerminatorKindCount": len(CONTROL_FLOW_IR_SCHEMA["$defs"]["terminator"]["properties"]["kind"]["enum"]),
        "selectedIrFragmentCount": len(fragments),
        "selectedBranchClosureCount": p59_summary["selectedBranchClosureCount"],
        "p59IrNodeCount": p59_summary["irNodeCount"],
        "p59UnsupportedFormCount": p59_summary["unsupportedFormCount"],
        "p59OpenSemanticObligationCount": p59_summary["openSemanticObligationCount"],
        "controlFlowIrSchemaWritten": True,
        "controlFlowIrImplemented": False,
        "frontendLoweringChanged": False,
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
    p59_packet = read_json(P59_PACKET)
    fragments = selected_ir_fragments()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p60-control-flow-ir-schema",
        "decision": "control_flow_ir_schema_recorded_implementation_blocked",
        "sourcePacket": {
            "phase": "P59",
            "packetPath": str(P59_PACKET.relative_to(ROOT)),
            "reviewDecision": p59_packet["reviewDecision"],
            "validationStatus": p59_packet["validationStatus"],
        },
        "controlFlowIrSchema": copy.deepcopy(CONTROL_FLOW_IR_SCHEMA),
        "selectedIrFragments": fragments,
        "summary": build_summary(p59_packet, fragments),
        "releaseGates": [
            {"id": "control_flow_ir_schema", "status": "recorded"},
            {"id": "control_flow_ir_implementation", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "branch_control_flow_reingest", "status": "blocked"},
            {"id": "non_generated_branch_roundtrip", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P60 records a machine-readable control-flow IR schema for private review.",
            "The five selected P57 branch closures can be expressed as schema-conforming fragments.",
            "P60 keeps implementation, general support, roundtrip, correctness, equivalence, and performance claims blocked.",
        ],
        "blockedStatements": [
            "The control-flow IR is implemented in Forge/eFrog.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Arbitrary C/Rust source-family support is established.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Build an unsupported constructs blocker gate against the P60 schema.",
            "Build a nested branch fixture matrix against the P60 schema.",
            "Only after those gates, consider implementing a narrow schema-backed frontend adapter.",
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
        "title": "FEF-P60 Control-Flow IR Schema",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "control_flow_ir_schema_recorded_implementation_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Control-flow IR schema checkpoint only; no IR implementation, new frontend lowering, general branch/control-flow support, branch re-ingest, full source roundtrip, arbitrary source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P60 writes a machine-readable control-flow IR schema.",
            "Five selected branch closures are represented as schema-conforming fragments.",
            "The schema includes block, statement, terminator, unsupported-construct, and semantic-obligation surfaces.",
            "Implementation and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p60_control_flow_ir_schema.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p60_control_flow_ir_schema.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p60_control_flow_ir_schema.v0",
        "date": DATE,
        "title": "FEF-P60 Control-Flow IR Schema",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Build an unsupported constructs blocker gate against the P60 schema.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    fragments = [
        "| Fragment | Source | Blocks | Branch Terminators | Return Terminators |",
        "|---|---|---:|---:|---:|",
    ]
    for fragment in payload["selectedIrFragments"]:
        terminators = [block["terminator"]["kind"] for block in fragment["blocks"]]
        fragments.append(
            f"| `{fragment['programId']}` | `{fragment['sourceLanguage']}` | {len(fragment['blocks'])} | {terminators.count('branch')} | {terminators.count('return_value')} |"
        )
    return "\n".join(
        [
            "# FEF-P60 Control-Flow IR Schema",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P60 turns the P59 inventory into a machine-readable schema checkpoint.",
            "",
            "## Summary",
            "",
            f"- Schema version: `{CONTROL_FLOW_IR_SCHEMA_VERSION}`",
            f"- Required fields: `{summary['schemaRequiredFieldCount']}`",
            f"- Block kinds: `{summary['schemaBlockKindCount']}`",
            f"- Statement kinds: `{summary['schemaStatementKindCount']}`",
            f"- Terminator kinds: `{summary['schemaTerminatorKindCount']}`",
            f"- Selected IR fragments: `{summary['selectedIrFragmentCount']}`",
            f"- P59 IR nodes: `{summary['p59IrNodeCount']}`",
            f"- P59 unsupported forms: `{summary['p59UnsupportedFormCount']}`",
            f"- P59 open semantic obligations: `{summary['p59OpenSemanticObligationCount']}`",
            f"- Control-flow IR implemented: `{summary['controlFlowIrImplemented']}`",
            f"- Frontend lowering changed: `{summary['frontendLoweringChanged']}`",
            "",
            "## Selected IR Fragments",
            "",
            *fragments,
            "",
            "## Schema Surface",
            "",
            "- top-level program metadata",
            "- blocks with entry/basic/merge/exit roles",
            "- statements for assignment, phi/select, and unsupported constructs",
            "- terminators for branch, return, jump, and unreachable",
            "- unsupported constructs and semantic obligations",
            "- claim flags locked false",
            "",
            "## Boundary",
            "",
            "- Schema checkpoint only; no new IR implementation.",
            "- No frontend lowering change.",
            "- No general branch/control-flow support claim.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P60 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P60 status")
    validate_schema_object(payload["controlFlowIrSchema"])
    for fragment in payload["selectedIrFragments"]:
        validate_fragment(fragment)
    summary = payload["summary"]
    if summary["sourcePacketCount"] != 1 or summary["p59ValidationPass"] is not True:
        raise ValueError("P59 source packet must validate")
    if summary["p59ClaimFlagsAllFalse"] is not True:
        raise ValueError("P59 claim flags must remain false")
    if summary["schemaRequiredFieldCount"] != 11:
        raise ValueError("unexpected required field count")
    if summary["schemaBlockKindCount"] != 4:
        raise ValueError("unexpected block kind count")
    if summary["schemaStatementKindCount"] != 3:
        raise ValueError("unexpected statement kind count")
    if summary["schemaTerminatorKindCount"] != 4:
        raise ValueError("unexpected terminator kind count")
    if summary["selectedIrFragmentCount"] != 5:
        raise ValueError("expected five selected IR fragments")
    if summary["selectedBranchClosureCount"] != 5:
        raise ValueError("expected five selected branch closures from P59")
    if summary["p59IrNodeCount"] != 10:
        raise ValueError("expected ten P59 IR nodes")
    if summary["p59UnsupportedFormCount"] != 6:
        raise ValueError("expected six P59 unsupported forms")
    if summary["p59OpenSemanticObligationCount"] != 6:
        raise ValueError("expected six P59 open semantic obligations")
    for key in [
        "controlFlowIrImplemented",
        "frontendLoweringChanged",
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


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    schema_dir: Path,
) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    schema_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p60_control_flow_ir_schema_{STAMP}.json"
    report_path = report_dir / f"fef_p60_control_flow_ir_schema_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p60_control_flow_ir_schema.json"
    feed_path = command_feed_dir / f"fef_p60_control_flow_ir_schema_feed_{STAMP}.json"
    schema_path = schema_dir / "control_flow_ir_schema_v0.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    schema_path.write_text(json.dumps(CONTROL_FLOW_IR_SCHEMA, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
        "schema_path": str(schema_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p60_control_flow_ir_schema")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--schema-dir", type=Path, default=ROOT / "schemas")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.schema_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P60_CONTROL_FLOW_IR_SCHEMA_OK")
    print(f"selected_fragments={built['payload']['summary']['selectedIrFragmentCount']}")
    print(f"schema={built['schema_path']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
