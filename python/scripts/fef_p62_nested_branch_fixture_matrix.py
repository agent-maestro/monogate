#!/usr/bin/env python3
"""FEF-P62 nested-branch fixture matrix for control-flow IR."""

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
from scripts import fef_p60_control_flow_ir_schema as p60

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p62_nested_branch_fixture_matrix.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P62_NESTED_BRANCH_FIXTURE_MATRIX_PASS"

P61_PACKET = ROOT / "reports/evidence_packets/fef_p61_unsupported_construct_blocker_gate.json"

CLAIM_FLAGS = {
    "nested_branch_fixture_matrix_claim": False,
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
    "FEF-P62 records a nested-branch fixture matrix only.",
    "FEF-P62 does not implement nested branch lowering.",
    "FEF-P62 does not widen Forge or eFrog frontend lowering.",
    "FEF-P62 does not claim nested branch support.",
    "FEF-P62 does not claim general branch/control-flow support.",
    "FEF-P62 does not claim branch/control-flow re-ingest support.",
    "FEF-P62 does not claim full non-generated source roundtrip.",
    "FEF-P62 does not claim arbitrary C/Rust source-family support.",
    "FEF-P62 does not record reviewer approval or rejection.",
    "FEF-P62 does not publish a package.",
    "FEF-P62 does not enable checkout or commerce.",
    "FEF-P62 does not claim public readiness.",
    "FEF-P62 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P62 does not claim runtime performance.",
]

FIXTURES = [
    {
        "id": "c_nested_if_return_v0",
        "sourceLanguage": "c",
        "shape": "nested_if_return",
        "sourceSketch": "if (x > 0.0) { if (y > 0.0) return x + y; } return 0.0;",
        "branchDepth": 2,
        "returnCount": 2,
        "blockedBy": "nested_branch_fixture_matrix_runtime_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "return_and_fallthrough_preservation"],
    },
    {
        "id": "c_nested_if_else_value_v0",
        "sourceLanguage": "c",
        "shape": "nested_if_else_value",
        "sourceSketch": "if (x > 0.0) { if (y > 0.0) return hi; else return mid; } return lo;",
        "branchDepth": 2,
        "returnCount": 3,
        "blockedBy": "dominance_merge_fixture_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "dominance_and_merge_preservation"],
    },
    {
        "id": "rust_nested_if_expr_v0",
        "sourceLanguage": "rust",
        "shape": "nested_if_expression",
        "sourceSketch": "if x > 0.0 { if y > 0.0 { x + y } else { x } } else { 0.0 }",
        "branchDepth": 2,
        "returnCount": 1,
        "blockedBy": "rust_block_expression_boundary_gate",
        "requiredSemanticObligations": ["condition_truth_semantics", "dominance_and_merge_preservation"],
    },
    {
        "id": "rust_nested_if_return_v0",
        "sourceLanguage": "rust",
        "shape": "nested_if_return",
        "sourceSketch": "if x > hi { if y > 0.0 { return hi; } } if x < lo { return lo; } x",
        "branchDepth": 2,
        "returnCount": 3,
        "blockedBy": "early_return_fallthrough_gate",
        "requiredSemanticObligations": ["return_and_fallthrough_preservation", "source_ast_roundtrip_boundary"],
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
                        "constructId": "nested_statement_branches",
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
        fragment = fixture_fragment(fixture)
        rows.append(
            {
                **copy.deepcopy(fixture),
                "status": "blocked_fixture_defined",
                "schemaFragment": fragment,
                "supportClaimAllowed": False,
            }
        )
    return rows


def build_summary(p61_packet: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p61ValidationPass": p61_packet["validationStatus"] == "pass",
        "p61ClaimFlagsAllFalse": all(value is False for value in p61_packet["claimFlags"].values()),
        "fixtureCount": len(rows),
        "cFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "c"),
        "rustFixtureCount": sum(1 for row in rows if row["sourceLanguage"] == "rust"),
        "maxBranchDepth": max(row["branchDepth"] for row in rows),
        "totalReturnCount": sum(row["returnCount"] for row in rows),
        "allFixturesBlocked": all(row["status"] == "blocked_fixture_defined" for row in rows),
        "schemaFragmentsValidate": True,
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
    rows = matrix_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p62-nested-branch-fixture-matrix",
        "decision": "nested_branch_fixture_matrix_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P61",
            "packetPath": str(P61_PACKET.relative_to(ROOT)),
            "reviewDecision": p61_packet["reviewDecision"],
            "validationStatus": p61_packet["validationStatus"],
        },
        "nestedBranchFixtures": rows,
        "summary": build_summary(p61_packet, rows),
        "releaseGates": [
            {"id": "nested_branch_fixture_matrix", "status": "recorded"},
            {"id": "nested_branch_support", "status": "blocked"},
            {"id": "control_flow_ir_implementation", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "branch_control_flow_reingest", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P62 records a nested-branch fixture matrix for private review.",
            "The matrix covers selected C and Rust nested branch shapes as blocked fixtures.",
            "P62 does not implement or claim nested branch support.",
        ],
        "blockedStatements": [
            "Nested branch lowering is implemented.",
            "Nested branches are supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Add deterministic expected-outcome samples for one nested fixture.",
            "Build an assignment/phi fixture gate for dominance and merge semantics.",
            "Only after a runtime/re-ingest gate, consider narrow nested branch lowering.",
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
        "title": "FEF-P62 Nested Branch Fixture Matrix",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "nested_branch_fixture_matrix_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Nested branch fixture matrix only; no nested branch implementation, frontend widening, general branch/control-flow support, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P62 defines four nested branch fixtures across C and Rust.",
            "Every fixture is schema-shaped and blocked pending a later validator.",
            "Nested branch support and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p62_nested_branch_fixture_matrix.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p62_nested_branch_fixture_matrix.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p62_nested_branch_fixture_matrix.v0",
        "date": DATE,
        "title": "FEF-P62 Nested Branch Fixture Matrix",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add deterministic expected-outcome samples for one nested branch fixture.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Fixture | Source | Shape | Depth | Returns | Status |", "|---|---|---|---:|---:|---|"]
    for row in payload["nestedBranchFixtures"]:
        rows.append(
            f"| `{row['id']}` | `{row['sourceLanguage']}` | `{row['shape']}` | {row['branchDepth']} | {row['returnCount']} | `{row['status']}` |"
        )
    return "\n".join(
        [
            "# FEF-P62 Nested Branch Fixture Matrix",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P62 defines blocked nested-branch fixture shapes against the P60/P61 surfaces.",
            "",
            "## Summary",
            "",
            f"- Fixtures: `{summary['fixtureCount']}`",
            f"- C fixtures: `{summary['cFixtureCount']}`",
            f"- Rust fixtures: `{summary['rustFixtureCount']}`",
            f"- Max branch depth: `{summary['maxBranchDepth']}`",
            f"- Total return sites: `{summary['totalReturnCount']}`",
            f"- All fixtures blocked: `{summary['allFixturesBlocked']}`",
            f"- Schema fragments validate: `{summary['schemaFragmentsValidate']}`",
            f"- Nested branch support claim: `{summary['nestedBranchSupportClaim']}`",
            f"- Control-flow IR implemented: `{summary['controlFlowIrImplemented']}`",
            f"- Frontend lowering changed: `{summary['frontendLoweringChanged']}`",
            "",
            "## Matrix",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Fixture matrix only; no nested branch implementation.",
            "- No frontend lowering change.",
            "- No general branch/control-flow support claim.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_fixture(row: dict[str, Any]) -> None:
    if row["status"] != "blocked_fixture_defined":
        raise ValueError("nested branch fixture must remain blocked")
    if row["supportClaimAllowed"] is not False:
        raise ValueError("nested branch support claim must remain false")
    if row["branchDepth"] < 2:
        raise ValueError("nested branch fixture must have depth >= 2")
    p60.validate_fragment(row["schemaFragment"])
    if row["schemaFragment"]["feature"] != row["shape"]:
        raise ValueError("fixture feature must match shape")
    if not all(value is False for value in row["schemaFragment"]["claimFlags"].values()):
        raise ValueError("fixture claim flags must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P62 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P62 status")
    for row in payload["nestedBranchFixtures"]:
        validate_fixture(row)
    summary = payload["summary"]
    for key in ["p61ValidationPass", "p61ClaimFlagsAllFalse", "allFixturesBlocked", "schemaFragmentsValidate", "claimFlagsAllFalse"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["fixtureCount"] != 4 or summary["cFixtureCount"] != 2 or summary["rustFixtureCount"] != 2:
        raise ValueError("unexpected fixture matrix shape")
    if summary["maxBranchDepth"] != 2:
        raise ValueError("unexpected max branch depth")
    for key in [
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
    result_path = out_dir / f"fef_p62_nested_branch_fixture_matrix_{STAMP}.json"
    report_path = report_dir / f"fef_p62_nested_branch_fixture_matrix_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p62_nested_branch_fixture_matrix.json"
    feed_path = command_feed_dir / f"fef_p62_nested_branch_fixture_matrix_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p62_nested_branch_fixture_matrix")
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
    print("FEF_P62_NESTED_BRANCH_FIXTURE_MATRIX_OK")
    print(f"fixtures={built['payload']['summary']['fixtureCount']}")
    print(f"all_blocked={built['payload']['summary']['allFixturesBlocked']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
