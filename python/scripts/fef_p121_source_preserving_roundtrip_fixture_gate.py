#!/usr/bin/env python3
"""FEF-P121 source-preserving roundtrip fixture gate for control-flow IR."""

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

from scripts import fef_p59_control_flow_ir_inventory as p59  # noqa: E402
from scripts import fef_p60_control_flow_ir_schema as p60  # noqa: E402
from scripts import fef_p120_compound_condition_private_reviewer_handoff_hold_gate as p120  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p121_source_preserving_roundtrip_fixture_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P121_SOURCE_PRESERVING_ROUNDTRIP_FIXTURE_GATE_PASS"

P61_PACKET = ROOT / "reports/evidence_packets/fef_p61_unsupported_construct_blocker_gate.json"
P120_PACKET = ROOT / "reports/evidence_packets/fef_p120_compound_condition_private_reviewer_handoff_hold_gate.json"
P120_RESULT = ROOT / "python/results/fef_p120_compound_condition_private_reviewer_handoff_hold_gate/fef_p120_compound_condition_private_reviewer_handoff_hold_gate_2026_06_01.json"

CLAIM_FLAGS = {
    "source_preserving_roundtrip_fixture_gate_claim": False,
    "source_preserving_roundtrip_support_claim": False,
    "source_parse_execution_claim": False,
    "source_reemission_claim": False,
    "source_fidelity_claim": False,
    "non_generated_source_roundtrip_claim": False,
    "compound_condition_support_claim": False,
    "loop_backedge_support_claim": False,
    "assignment_phi_support_claim": False,
    "side_effect_memory_support_claim": False,
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
    "FEF-P121 records source-preserving roundtrip fixtures only.",
    "FEF-P121 does not parse or re-emit non-generated source.",
    "FEF-P121 does not execute source-preserving roundtrip fixtures.",
    "FEF-P121 does not claim token, whitespace, comment, or formatting fidelity.",
    "FEF-P121 does not implement source-preserving roundtrip support.",
    "FEF-P121 does not widen Forge or eFrog frontend lowering.",
    "FEF-P121 preserves the P120 private reviewer handoff hold status.",
    "FEF-P121 does not record reviewer approval or rejection.",
    "FEF-P121 does not claim general branch/control-flow support.",
    "FEF-P121 does not claim branch/control-flow re-ingest support.",
    "FEF-P121 does not claim full non-generated source roundtrip.",
    "FEF-P121 does not claim arbitrary C/Rust source-family support.",
    "FEF-P121 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P121 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

FIXTURES = [
    {
        "id": "c_if_else_source_layout_v0",
        "sourceLanguage": "c",
        "shape": "if_else_with_layout_and_comment",
        "sourceSketch": "/* clamp */\nif (x < lo) {\n  return lo;\n} else {\n  return x;\n}",
        "sourceFidelityFeatures": ["block_comment", "brace_layout", "else_token", "return_spacing"],
        "branchConstructCount": 1,
        "tokenBoundaryCount": 6,
        "commentCount": 1,
        "formatSensitive": True,
        "blockedBy": "non_generated_branch_roundtrip_gate",
        "requiredSemanticObligations": ["source_ast_roundtrip_boundary", "condition_truth_semantics"],
    },
    {
        "id": "c_nested_source_order_v0",
        "sourceLanguage": "c",
        "shape": "nested_if_source_order",
        "sourceSketch": "if (x > 0.0) {\n  if (y > 0.0) return x + y;\n}\nreturn 0.0;",
        "sourceFidelityFeatures": ["nested_if_order", "single_line_inner_return", "fallthrough_return"],
        "branchConstructCount": 2,
        "tokenBoundaryCount": 7,
        "commentCount": 0,
        "formatSensitive": True,
        "blockedBy": "non_generated_branch_roundtrip_gate",
        "requiredSemanticObligations": ["source_ast_roundtrip_boundary", "dominance_and_merge_preservation"],
    },
    {
        "id": "rust_if_expr_source_layout_v0",
        "sourceLanguage": "rust",
        "shape": "rust_if_expression_layout",
        "sourceSketch": "if x > 0.0 {\n    x\n} else {\n    0.0\n}",
        "sourceFidelityFeatures": ["expression_tail_position", "brace_layout", "indentation"],
        "branchConstructCount": 1,
        "tokenBoundaryCount": 5,
        "commentCount": 0,
        "formatSensitive": True,
        "blockedBy": "non_generated_branch_roundtrip_gate",
        "requiredSemanticObligations": ["source_ast_roundtrip_boundary", "dominance_and_merge_preservation"],
    },
    {
        "id": "rust_early_return_source_order_v0",
        "sourceLanguage": "rust",
        "shape": "rust_early_return_source_order",
        "sourceSketch": "if x < lo {\n    return lo;\n}\n// fall through\nx",
        "sourceFidelityFeatures": ["early_return_order", "line_comment", "fallthrough_expression"],
        "branchConstructCount": 1,
        "tokenBoundaryCount": 5,
        "commentCount": 1,
        "formatSensitive": True,
        "blockedBy": "non_generated_branch_roundtrip_gate",
        "requiredSemanticObligations": ["source_ast_roundtrip_boundary", "return_and_fallthrough_preservation"],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_fragment(fixture: dict[str, Any]) -> dict[str, Any]:
    obligations = [
        copy.deepcopy(item)
        for item in p59.SEMANTIC_OBLIGATIONS
        if item["id"] in fixture["requiredSemanticObligations"] or item["id"] == "unsupported_construct_fail_closed"
    ]
    while len(obligations) < 6:
        existing = {item["id"] for item in obligations}
        next_item = next(item for item in p59.SEMANTIC_OBLIGATIONS if item["id"] not in existing)
        obligations.append(copy.deepcopy(next_item))
    return {
        "schemaVersion": p60.CONTROL_FLOW_IR_SCHEMA_VERSION,
        "programId": fixture["id"],
        "sourceLanguage": fixture["sourceLanguage"],
        "functionName": fixture["id"].replace("_v0", ""),
        "feature": fixture["shape"],
        "entryBlockId": "entry",
        "exitBlockId": "exit",
        "blocks": [
            {
                "id": "entry",
                "kind": "cfg_entry",
                "statements": [
                    {
                        "kind": "unsupported_construct",
                        "constructId": "source_preserving_roundtrip",
                        "expr": fixture["sourceSketch"],
                        "blockedBy": fixture["blockedBy"],
                    }
                ],
                "terminator": {"kind": "unreachable"},
            },
            {"id": "exit", "kind": "cfg_exit", "statements": [], "terminator": {"kind": "unreachable"}},
        ],
        "unsupportedConstructs": copy.deepcopy(p59.UNSUPPORTED_FORMS),
        "semanticObligations": obligations[:6],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def matrix_rows() -> list[dict[str, Any]]:
    rows = []
    for fixture in FIXTURES:
        rows.append(
            {
                **copy.deepcopy(fixture),
                "status": "blocked_fixture_defined",
                "constructId": "source_preserving_roundtrip",
                "schemaFragment": fixture_fragment(fixture),
                "supportClaimAllowed": False,
                "sourceParsePerformed": False,
                "sourceReemissionPerformed": False,
                "runtimeExecutionPerformed": False,
                "roundtripFidelityClaim": False,
            }
        )
    return rows


def build_summary(p61_packet: dict[str, Any], p120_packet: dict[str, Any], p120_payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    fidelity_features = sorted({feature for row in rows for feature in row["sourceFidelityFeatures"]})
    return {
        "sourcePacketCount": 2,
        "p61ValidationPass": p61_packet["validationStatus"] == "pass",
        "p61ClaimFlagsAllFalse": all(value is False for value in p61_packet["claimFlags"].values()),
        "p120ValidationPass": p120_packet["validationStatus"] == "pass",
        "p120ClaimFlagsAllFalse": all(value is False for value in p120_packet["claimFlags"].values()),
        "p120ReviewerDecisionRecorded": p120_payload["summary"]["reviewerDecisionRecorded"],
        "p120ImplementationHeldPendingReview": p120_payload["summary"]["implementationHeldPendingReview"],
        "fixtureCount": len(rows),
        "cFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "c"),
        "rustFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "rust"),
        "sourceFidelityFeatureCount": len(fidelity_features),
        "sourceFidelityFeatures": fidelity_features,
        "totalBranchConstructCount": sum(row["branchConstructCount"] for row in rows),
        "totalTokenBoundaryCount": sum(row["tokenBoundaryCount"] for row in rows),
        "totalCommentCount": sum(row["commentCount"] for row in rows),
        "formatSensitiveFixtureCount": sum(1 for row in rows if row["formatSensitive"]),
        "allFixturesBlocked": all(row["status"] == "blocked_fixture_defined" for row in rows),
        "allSourceParseNotPerformed": all(row["sourceParsePerformed"] is False for row in rows),
        "allSourceReemissionNotPerformed": all(row["sourceReemissionPerformed"] is False for row in rows),
        "allRuntimeExecutionNotPerformed": all(row["runtimeExecutionPerformed"] is False for row in rows),
        "schemaFragmentsValidate": True,
        "sourcePreservingRoundtripSupportClaim": False,
        "sourceParseExecutionClaim": False,
        "sourceReemissionClaim": False,
        "sourceFidelityClaim": False,
        "nonGeneratedSourceRoundtripClaim": False,
        "compoundConditionSupportClaim": False,
        "loopBackedgeSupportClaim": False,
        "assignmentPhiSupportClaim": False,
        "sideEffectMemorySupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "frontendLoweringChanged": False,
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
    p61_packet = read_json(P61_PACKET)
    p120_packet = read_json(P120_PACKET)
    p120_payload = read_json(P120_RESULT)
    p120.validate_payload(p120_payload)
    rows = matrix_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p121-source-preserving-roundtrip-fixture-gate",
        "decision": "source_preserving_roundtrip_fixture_gate_recorded_support_blocked_review_hold_preserved",
        "sourcePackets": [
            {
                "phase": "P61",
                "packetPath": str(P61_PACKET.relative_to(ROOT)),
                "reviewDecision": p61_packet["reviewDecision"],
                "validationStatus": p61_packet["validationStatus"],
            },
            {
                "phase": "P120",
                "packetPath": str(P120_PACKET.relative_to(ROOT)),
                "resultPath": str(P120_RESULT.relative_to(ROOT)),
                "reviewDecision": p120_packet["reviewDecision"],
                "validationStatus": p120_packet["validationStatus"],
            },
        ],
        "fixtureMatrix": rows,
        "summary": build_summary(p61_packet, p120_packet, p120_payload, rows),
        "releaseGates": [
            {"id": "source_preserving_roundtrip_fixture_gate", "status": "recorded"},
            {"id": "source_preserving_roundtrip_support", "status": "blocked"},
            {"id": "source_parse_execution", "status": "not_performed"},
            {"id": "source_reemission", "status": "not_performed"},
            {"id": "source_fidelity_claim", "status": "blocked"},
            {"id": "non_generated_source_roundtrip", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P121 records selected source-preserving roundtrip fixture shapes for private review.",
            "P121 keeps source parsing, source re-emission, and fidelity claims blocked.",
            "P121 preserves the P120 reviewer handoff hold status.",
        ],
        "blockedStatements": [
            "Non-generated source was parsed for source-preserving roundtrip.",
            "Non-generated source was re-emitted.",
            "Token, whitespace, comment, or formatting fidelity has been established.",
            "Source-preserving roundtrip is supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Attach expected preservation rows for one selected source-preserving fixture before any parser/re-emitter claim.",
            "Record actual private reviewer response to P47-P121 if one exists.",
            "Keep held proposals P111 and P119 unapplied without reviewer approval.",
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
        "title": "FEF-P121 Source-Preserving Roundtrip Fixture Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "source_preserving_roundtrip_fixtures_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Source-preserving roundtrip fixture gate only; no source parsing, source re-emission, token/format fidelity, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P121 records four source-preserving roundtrip fixture shapes.",
            "P120 reviewer handoff hold remains not recorded/held.",
            "No source-preserving roundtrip execution or fidelity claim is made.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p121_source_preserving_roundtrip_fixture_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p121_source_preserving_roundtrip_fixture_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p121_source_preserving_roundtrip_fixture_gate.v0",
        "date": DATE,
        "title": "FEF-P121 Source-Preserving Roundtrip Fixture Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach expected preservation rows before any source parser/re-emitter claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Fixture | Language | Shape | Branches | Comments | Status |", "|---|---|---|---:|---:|---|"]
    for row in payload["fixtureMatrix"]:
        rows.append(
            f"| `{row['id']}` | `{row['sourceLanguage']}` | `{row['shape']}` | {row['branchConstructCount']} | {row['commentCount']} | `{row['status']}` |"
        )
    return "\n".join(
        [
            "# FEF-P121 Source-Preserving Roundtrip Fixture Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P121 records blocked fixture shapes for non-generated source-preserving branch roundtrip.",
            "",
            "## Summary",
            "",
            f"- Fixture count: `{summary['fixtureCount']}`",
            f"- C fixtures: `{summary['cFixtureCount']}`",
            f"- Rust fixtures: `{summary['rustFixtureCount']}`",
            f"- Source fidelity feature count: `{summary['sourceFidelityFeatureCount']}`",
            f"- Total branch constructs: `{summary['totalBranchConstructCount']}`",
            f"- Total comment count: `{summary['totalCommentCount']}`",
            f"- Format-sensitive fixtures: `{summary['formatSensitiveFixtureCount']}`",
            f"- All fixtures blocked: `{summary['allFixturesBlocked']}`",
            f"- Source parse performed: `{not summary['allSourceParseNotPerformed']}`",
            f"- Source re-emission performed: `{not summary['allSourceReemissionNotPerformed']}`",
            f"- Source fidelity claim: `{summary['sourceFidelityClaim']}`",
            f"- Full non-generated source roundtrip claim: `{summary['fullNonGeneratedSourceRoundtripClaim']}`",
            "",
            "## Fixture Matrix",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Fixture gate only; no source parser or re-emitter execution.",
            "- No token, whitespace, comment, or formatting fidelity claim.",
            "- No source-preserving roundtrip support claim.",
            "- No frontend lowering change.",
            "- No full source roundtrip, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_fragment(fragment: dict[str, Any], fixture_id: str) -> None:
    if fragment["schemaVersion"] != p60.CONTROL_FLOW_IR_SCHEMA_VERSION:
        raise ValueError("invalid control-flow IR schema version")
    if fragment["programId"] != fixture_id:
        raise ValueError("fragment program id mismatch")
    statements = fragment["blocks"][0]["statements"]
    if not any(statement["kind"] == "unsupported_construct" for statement in statements):
        raise ValueError("fragment must include unsupported_construct statement")
    if statements[0]["constructId"] != "source_preserving_roundtrip":
        raise ValueError("fragment must focus source_preserving_roundtrip")
    if len(fragment["semanticObligations"]) != 6:
        raise ValueError("fragment must carry six semantic obligations")
    if not any(item["id"] == "source_ast_roundtrip_boundary" for item in fragment["semanticObligations"]):
        raise ValueError("fragment must carry source roundtrip obligation")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P121 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P121 status")
    p120.validate_payload(read_json(P120_RESULT))
    for row in payload["fixtureMatrix"]:
        validate_fragment(row["schemaFragment"], row["id"])
        for key in [
            "supportClaimAllowed",
            "sourceParsePerformed",
            "sourceReemissionPerformed",
            "runtimeExecutionPerformed",
            "roundtripFidelityClaim",
        ]:
            if row[key] is not False:
                raise ValueError(f"{key} must remain false")
    summary = payload["summary"]
    for key in [
        "p61ValidationPass",
        "p61ClaimFlagsAllFalse",
        "p120ValidationPass",
        "p120ClaimFlagsAllFalse",
        "p120ImplementationHeldPendingReview",
        "allFixturesBlocked",
        "allSourceParseNotPerformed",
        "allSourceReemissionNotPerformed",
        "allRuntimeExecutionNotPerformed",
        "schemaFragmentsValidate",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["p120ReviewerDecisionRecorded"] is not False:
        raise ValueError("P120 reviewer decision must remain not recorded")
    if summary["fixtureCount"] != 4 or summary["cFixtureCount"] != 2 or summary["rustFixtureCount"] != 2:
        raise ValueError("unexpected fixture counts")
    if summary["totalBranchConstructCount"] != 5 or summary["totalCommentCount"] != 2:
        raise ValueError("unexpected source fixture feature counts")
    for key in [
        "sourcePreservingRoundtripSupportClaim",
        "sourceParseExecutionClaim",
        "sourceReemissionClaim",
        "sourceFidelityClaim",
        "nonGeneratedSourceRoundtripClaim",
        "compoundConditionSupportClaim",
        "loopBackedgeSupportClaim",
        "assignmentPhiSupportClaim",
        "sideEffectMemorySupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "frontendLoweringChanged",
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
    result_path = out_dir / f"fef_p121_source_preserving_roundtrip_fixture_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p121_source_preserving_roundtrip_fixture_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p121_source_preserving_roundtrip_fixture_gate.json"
    feed_path = command_feed_dir / f"fef_p121_source_preserving_roundtrip_fixture_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p121_source_preserving_roundtrip_fixture_gate")
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
    print("FEF_P121_SOURCE_PRESERVING_ROUNDTRIP_FIXTURE_GATE_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"source_parse_performed={not built['payload']['summary']['allSourceParseNotPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
