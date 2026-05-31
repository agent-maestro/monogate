#!/usr/bin/env python3
"""FEF-P61 unsupported-construct blocker gate for control-flow IR."""

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
SCHEMA_VERSION = "monogate.fef_p61_unsupported_construct_blocker_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P61_UNSUPPORTED_CONSTRUCT_BLOCKER_GATE_PASS"

P60_PACKET = ROOT / "reports/evidence_packets/fef_p60_control_flow_ir_schema.json"
P60_RESULT = ROOT / "python/results/fef_p60_control_flow_ir_schema/fef_p60_control_flow_ir_schema_2026_05_31.json"
P60_SCHEMA = ROOT / "schemas/control_flow_ir_schema_v0.json"

CLAIM_FLAGS = {
    "unsupported_construct_blocker_gate_claim": False,
    "control_flow_ir_schema_claim": False,
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
    "FEF-P61 records a blocker gate for unsupported control-flow constructs only.",
    "FEF-P61 does not implement unsupported constructs.",
    "FEF-P61 does not widen Forge or eFrog frontend lowering.",
    "FEF-P61 does not claim general branch/control-flow support.",
    "FEF-P61 does not claim branch/control-flow re-ingest support.",
    "FEF-P61 does not claim full non-generated source roundtrip.",
    "FEF-P61 does not claim arbitrary C/Rust source-family support.",
    "FEF-P61 does not record reviewer approval or rejection.",
    "FEF-P61 does not publish a package.",
    "FEF-P61 does not enable checkout or commerce.",
    "FEF-P61 does not claim public readiness.",
    "FEF-P61 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P61 does not claim runtime performance.",
    "FEF-P61 does not claim hardware, silicon, proof, Pro-target, production, or all-target readiness.",
]

PROBE_SURFACES = {
    "nested_statement_branches": {
        "sourceLanguage": "c",
        "sourceSketch": "if (x > 0.0) { if (y > 0.0) { return x + y; } } return 0.0;",
        "blockedBy": "nested_branch_fixture_matrix",
        "blockerCategory": "grammar_breadth",
    },
    "boolean_compound_conditions": {
        "sourceLanguage": "rust",
        "sourceSketch": "if x > 0.0 && y > 0.0 { x } else { 0.0 }",
        "blockedBy": "compound_condition_semantics_gate",
        "blockerCategory": "condition_semantics",
    },
    "mutable_assignments_across_branches": {
        "sourceLanguage": "c",
        "sourceSketch": "double z = x; if (x > 0.0) { z = y; } return z;",
        "blockedBy": "assignment_phi_fixture_gate",
        "blockerCategory": "state_and_merge",
    },
    "loops_and_back_edges": {
        "sourceLanguage": "rust",
        "sourceSketch": "while i < n { acc = acc + x; i = i + 1; }",
        "blockedBy": "loop_construct_blocker_gate",
        "blockerCategory": "loops_and_back_edges",
    },
    "side_effecting_calls_or_memory": {
        "sourceLanguage": "c",
        "sourceSketch": "if (x > 0.0) { state[0] = update(x); } return state[0];",
        "blockedBy": "side_effect_boundary_inventory",
        "blockerCategory": "effects_calls_memory",
    },
    "source_preserving_roundtrip": {
        "sourceLanguage": "rust",
        "sourceSketch": "non-generated source branch AST -> source-preserving re-emission",
        "blockedBy": "non_generated_branch_roundtrip_gate",
        "blockerCategory": "source_roundtrip_semantics",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def blocker_probe(unsupported_form: dict[str, Any]) -> dict[str, Any]:
    construct_id = unsupported_form["id"]
    surface = PROBE_SURFACES[construct_id]
    ordered_unsupported_forms = [copy.deepcopy(unsupported_form)] + [
        copy.deepcopy(item) for item in p59.UNSUPPORTED_FORMS if item["id"] != construct_id
    ]
    statement = {
        "kind": "unsupported_construct",
        "constructId": construct_id,
        "expr": surface["sourceSketch"],
        "blockerCategory": surface["blockerCategory"],
        "blockedBy": surface["blockedBy"],
        "reason": unsupported_form["reason"],
    }
    fragment = {
        "schemaVersion": p60.CONTROL_FLOW_IR_SCHEMA_VERSION,
        "programId": f"{construct_id}_blocker_probe_v0",
        "sourceLanguage": surface["sourceLanguage"],
        "functionName": f"{construct_id}_blocker_probe",
        "feature": construct_id,
        "entryBlockId": "entry",
        "exitBlockId": "exit",
        "blocks": [
            {
                "id": "entry",
                "kind": "cfg_entry",
                "statements": [statement],
                "terminator": {"kind": "unreachable"},
            },
            {
                "id": "exit",
                "kind": "cfg_exit",
                "statements": [],
                "terminator": {"kind": "unreachable"},
            },
        ],
        "unsupportedConstructs": ordered_unsupported_forms,
        "semanticObligations": copy.deepcopy(p59.SEMANTIC_OBLIGATIONS),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    return {
        "constructId": construct_id,
        "status": "blocked_fail_closed",
        "sourceLanguage": surface["sourceLanguage"],
        "blockerCategory": surface["blockerCategory"],
        "blockedBy": surface["blockedBy"],
        "sourceSketch": surface["sourceSketch"],
        "schemaFragment": fragment,
        "requiredNextValidator": unsupported_form["nextValidator"],
        "supportClaimAllowed": False,
    }


def blocker_probes() -> list[dict[str, Any]]:
    return [blocker_probe(item) for item in p59.UNSUPPORTED_FORMS]


def build_summary(p60_packet: dict[str, Any], p60_result: dict[str, Any], probes: list[dict[str, Any]]) -> dict[str, Any]:
    construct_ids = {probe["constructId"] for probe in probes}
    p59_ids = {item["id"] for item in p59.UNSUPPORTED_FORMS}
    schema_ids = {
        item["id"]
        for fragment in p60_result["selectedIrFragments"]
        for item in fragment["unsupportedConstructs"]
    }
    return {
        "sourcePacketCount": 1,
        "p60ValidationPass": p60_packet["validationStatus"] == "pass",
        "p60ClaimFlagsAllFalse": all(value is False for value in p60_packet["claimFlags"].values()),
        "p60SchemaId": p60_result["controlFlowIrSchema"]["$id"],
        "p60SelectedIrFragmentCount": p60_result["summary"]["selectedIrFragmentCount"],
        "p60ControlFlowIrImplemented": p60_result["summary"]["controlFlowIrImplemented"],
        "p60FrontendLoweringChanged": p60_result["summary"]["frontendLoweringChanged"],
        "unsupportedConstructProbeCount": len(probes),
        "p59UnsupportedFormCount": len(p59.UNSUPPORTED_FORMS),
        "allP59UnsupportedFormsCovered": construct_ids == p59_ids,
        "allP60SchemaUnsupportedFormsCovered": construct_ids == schema_ids,
        "allUnsupportedProbesBlocked": all(probe["status"] == "blocked_fail_closed" for probe in probes),
        "schemaFragmentsValidate": True,
        "unsupportedConstructsSupported": False,
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
    p60_packet = read_json(P60_PACKET)
    p60_result = read_json(P60_RESULT)
    p60_schema = read_json(P60_SCHEMA)
    probes = blocker_probes()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p61-unsupported-construct-blocker-gate",
        "decision": "unsupported_construct_blocker_gate_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P60",
            "packetPath": str(P60_PACKET.relative_to(ROOT)),
            "resultPath": str(P60_RESULT.relative_to(ROOT)),
            "schemaPath": str(P60_SCHEMA.relative_to(ROOT)),
            "reviewDecision": p60_packet["reviewDecision"],
            "validationStatus": p60_packet["validationStatus"],
        },
        "controlFlowIrSchemaId": p60_schema["$id"],
        "unsupportedConstructProbes": probes,
        "summary": build_summary(p60_packet, p60_result, probes),
        "releaseGates": [
            {"id": "unsupported_construct_blocker_gate", "status": "recorded"},
            {"id": "unsupported_construct_support", "status": "blocked"},
            {"id": "control_flow_ir_implementation", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "branch_control_flow_reingest", "status": "blocked"},
            {"id": "non_generated_branch_roundtrip", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P61 records a fail-closed unsupported-construct blocker gate against the P60 schema.",
            "All six P59/P60 unsupported forms are represented as blocked schema-shaped probes.",
            "P61 can be used to keep unsupported constructs from being mistaken for implemented branch support.",
        ],
        "blockedStatements": [
            "Unsupported constructs are implemented.",
            "Loops, effects, calls, memory, labels, nested branches, and source-preserving roundtrip are supported.",
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
            "Build a nested-branch fixture matrix for grammar breadth.",
            "Build an assignment/phi fixture gate for dominance and merge semantics.",
            "Only after those gates, consider a narrow schema-backed frontend adapter.",
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
        "title": "FEF-P61 Unsupported Construct Blocker Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "unsupported_construct_blocker_gate_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Unsupported-construct blocker gate only; no unsupported construct implementation, frontend widening, general branch/control-flow support, branch re-ingest, full source roundtrip, arbitrary source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P61 covers all six P59/P60 unsupported forms.",
            "Each unsupported construct is represented as a P60-schema-shaped blocked probe.",
            "All probes remain fail-closed and support claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p61_unsupported_construct_blocker_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p61_unsupported_construct_blocker_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p61_unsupported_construct_blocker_gate.v0",
        "date": DATE,
        "title": "FEF-P61 Unsupported Construct Blocker Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Build a nested-branch fixture matrix against the P60 schema.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        "| Construct | Source | Category | Status | Next Validator |",
        "|---|---|---|---|---|",
    ]
    for probe in payload["unsupportedConstructProbes"]:
        rows.append(
            f"| `{probe['constructId']}` | `{probe['sourceLanguage']}` | `{probe['blockerCategory']}` | `{probe['status']}` | `{probe['blockedBy']}` |"
        )
    return "\n".join(
        [
            "# FEF-P61 Unsupported Construct Blocker Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P61 makes the P60 control-flow IR schema fail closed for unsupported constructs.",
            "",
            "## Summary",
            "",
            f"- P60 schema id: `{summary['p60SchemaId']}`",
            f"- P60 selected IR fragments: `{summary['p60SelectedIrFragmentCount']}`",
            f"- Unsupported construct probes: `{summary['unsupportedConstructProbeCount']}`",
            f"- P59 unsupported forms: `{summary['p59UnsupportedFormCount']}`",
            f"- All P59 unsupported forms covered: `{summary['allP59UnsupportedFormsCovered']}`",
            f"- All P60 schema unsupported forms covered: `{summary['allP60SchemaUnsupportedFormsCovered']}`",
            f"- All unsupported probes blocked: `{summary['allUnsupportedProbesBlocked']}`",
            f"- Schema fragments validate: `{summary['schemaFragmentsValidate']}`",
            f"- Unsupported constructs supported: `{summary['unsupportedConstructsSupported']}`",
            f"- Control-flow IR implemented: `{summary['controlFlowIrImplemented']}`",
            f"- Frontend lowering changed: `{summary['frontendLoweringChanged']}`",
            "",
            "## Blocked Probes",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Blocker gate only; no unsupported construct implementation.",
            "- No frontend lowering change.",
            "- No general branch/control-flow support claim.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_probe(probe: dict[str, Any]) -> None:
    if probe["status"] != "blocked_fail_closed":
        raise ValueError("unsupported probe must remain blocked")
    if probe["supportClaimAllowed"] is not False:
        raise ValueError("support claim must remain blocked")
    fragment = probe["schemaFragment"]
    required = set(p60.CONTROL_FLOW_IR_SCHEMA["required"])
    missing = required - set(fragment)
    if missing:
        raise ValueError(f"probe fragment missing required fields: {sorted(missing)}")
    if len(fragment["unsupportedConstructs"]) != 6:
        raise ValueError("probe must carry the full unsupported construct boundary set")
    if fragment["unsupportedConstructs"][0]["id"] != probe["constructId"]:
        raise ValueError("probe must put the focused unsupported construct first")
    p60.validate_fragment(fragment)
    statements = [statement for block in fragment["blocks"] for statement in block["statements"]]
    if not any(statement["kind"] == "unsupported_construct" for statement in statements):
        raise ValueError("probe must include unsupported_construct statement")
    if not all(value is False for value in fragment["claimFlags"].values()):
        raise ValueError("probe fragment claim flags must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P61 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P61 status")
    if payload["controlFlowIrSchemaId"] != p60.CONTROL_FLOW_IR_SCHEMA_VERSION:
        raise ValueError("unexpected P60 schema id")
    for probe in payload["unsupportedConstructProbes"]:
        validate_probe(probe)
    summary = payload["summary"]
    expected_true = [
        "p60ValidationPass",
        "p60ClaimFlagsAllFalse",
        "allP59UnsupportedFormsCovered",
        "allP60SchemaUnsupportedFormsCovered",
        "allUnsupportedProbesBlocked",
        "schemaFragmentsValidate",
        "claimFlagsAllFalse",
    ]
    for key in expected_true:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["unsupportedConstructProbeCount"] != 6:
        raise ValueError("expected six unsupported construct probes")
    if summary["p59UnsupportedFormCount"] != 6:
        raise ValueError("expected six P59 unsupported forms")
    if summary["p60SelectedIrFragmentCount"] != 5:
        raise ValueError("expected five P60 selected fragments")
    for key in [
        "p60ControlFlowIrImplemented",
        "p60FrontendLoweringChanged",
        "unsupportedConstructsSupported",
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
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p61_unsupported_construct_blocker_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p61_unsupported_construct_blocker_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p61_unsupported_construct_blocker_gate.json"
    feed_path = command_feed_dir / f"fef_p61_unsupported_construct_blocker_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p61_unsupported_construct_blocker_gate")
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
    print("FEF_P61_UNSUPPORTED_CONSTRUCT_BLOCKER_GATE_OK")
    print(f"unsupported_probes={built['payload']['summary']['unsupportedConstructProbeCount']}")
    print(f"all_blocked={built['payload']['summary']['allUnsupportedProbesBlocked']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
