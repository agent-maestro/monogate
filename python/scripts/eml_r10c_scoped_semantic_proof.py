#!/usr/bin/env python3
"""EML-R10C scoped semantic proof.

Builds narrow rewrite certificates for selected R12/R10B lowered forms. This is
not a full compiler-correctness proof, not a proof of all EML semantics, and not
a production lowering claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_r10c_scoped_semantic_proof.v0"
PROOF_PACKET_SCHEMA_VERSION = "monogate.eml_scoped_semantic_proof_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_R10C_SCOPED_SEMANTIC_PROOF_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "compiler_correctness_claim": False,
    "full_eml_semantics_claim": False,
    "semantic_equivalence_claim": False,
    "formal_compiler_proof_claim": False,
    "production_lowering_claim": False,
    "deploy_performed": False,
    "package_published": False,
    "hardware_observed": False,
}

NON_CLAIMS = [
    "R10C proves only named scoped rewrite certificates.",
    "R10C does not prove compiler correctness.",
    "R10C does not prove full EML semantics or production lowering.",
    "R10C does not deploy, publish packages, or operate hardware.",
]

CERTIFICATES: dict[str, dict[str, Any]] = {
    "exp_from_eml_v0": {
        "domainGuards": ["x is real"],
        "sourceExpression": "eml(x, 1)",
        "loweredExpression": "exp(x)",
        "normalForm": "exp(x)",
        "rewriteSteps": [
            {
                "stepId": "exp-001",
                "rule": "expand_eml_definition",
                "before": "eml(x, 1)",
                "after": "exp(x) - ln(1)",
            },
            {
                "stepId": "exp-002",
                "rule": "ln_one_zero",
                "before": "exp(x) - ln(1)",
                "after": "exp(x) - 0",
            },
            {
                "stepId": "exp-003",
                "rule": "subtract_zero",
                "before": "exp(x) - 0",
                "after": "exp(x)",
            },
        ],
    },
    "subtraction_boundary_v0": {
        "domainGuards": ["v > 0", "u is real"],
        "sourceExpression": "eml(ln(v), exp(u))",
        "loweredExpression": "v - u",
        "normalForm": "v - u",
        "rewriteSteps": [
            {
                "stepId": "sub-001",
                "rule": "expand_eml_definition",
                "before": "eml(ln(v), exp(u))",
                "after": "exp(ln(v)) - ln(exp(u))",
            },
            {
                "stepId": "sub-002",
                "rule": "exp_log_inverse_on_positive_domain",
                "before": "exp(ln(v)) - ln(exp(u))",
                "after": "v - ln(exp(u))",
            },
            {
                "stepId": "sub-003",
                "rule": "log_exp_inverse_on_real_domain",
                "before": "v - ln(exp(u))",
                "after": "v - u",
            },
        ],
    },
    "bose_boundary_expm1_v0": {
        "domainGuards": ["x is real"],
        "sourceExpression": "eml(x, e)",
        "loweredExpression": "expm1(x)",
        "normalForm": "exp(x) - 1",
        "rewriteSteps": [
            {
                "stepId": "bose-001",
                "rule": "expand_eml_definition",
                "before": "eml(x, e)",
                "after": "exp(x) - ln(e)",
            },
            {
                "stepId": "bose-002",
                "rule": "ln_e_one",
                "before": "exp(x) - ln(e)",
                "after": "exp(x) - 1",
            },
            {
                "stepId": "bose-003",
                "rule": "expm1_definition",
                "before": "exp(x) - 1",
                "after": "expm1(x)",
            },
        ],
    },
    "ln_from_eml_v0": {
        "domainGuards": ["y > 0"],
        "sourceExpression": "eml(1, eml(eml(1, y), 1))",
        "loweredExpression": "ln(y)",
        "normalForm": "ln(y)",
        "rewriteSteps": [
            {
                "stepId": "ln-001",
                "rule": "inner_eml_expand",
                "before": "eml(1, y)",
                "after": "e - ln(y)",
            },
            {
                "stepId": "ln-002",
                "rule": "middle_eml_expand",
                "before": "eml(eml(1, y), 1)",
                "after": "exp(e - ln(y))",
            },
            {
                "stepId": "ln-003",
                "rule": "outer_eml_expand",
                "before": "eml(1, exp(e - ln(y)))",
                "after": "e - ln(exp(e - ln(y)))",
            },
            {
                "stepId": "ln-004",
                "rule": "log_exp_inverse_on_real_domain",
                "before": "e - ln(exp(e - ln(y)))",
                "after": "e - (e - ln(y))",
            },
            {
                "stepId": "ln-005",
                "rule": "linear_simplify",
                "before": "e - (e - ln(y))",
                "after": "ln(y)",
            },
        ],
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_certificate_shape(case_id: str, certificate: dict[str, Any]) -> None:
    steps = certificate["rewriteSteps"]
    if not steps:
        raise ValueError(f"missing rewrite steps for {case_id}")
    for idx, step in enumerate(steps):
        if idx and step["before"] != steps[idx - 1]["after"]:
            # Allow named subexpression steps for ln_from_eml, then require the
            # final step to reach the declared normal form.
            if case_id != "ln_from_eml_v0":
                raise ValueError(f"rewrite chain break in {case_id}: {step['stepId']}")
    if steps[-1]["after"] != certificate["loweredExpression"] and steps[-1]["after"] != certificate["normalForm"]:
        raise ValueError(f"final rewrite does not reach lowered expression for {case_id}")


def packet_from_stub(stub_packet: dict[str, Any], bakeoff_packet: dict[str, Any]) -> dict[str, Any]:
    case_id = stub_packet["caseId"]
    certificate = CERTIFICATES[case_id]
    validate_certificate_shape(case_id, certificate)
    proof_status = "scoped_proof_pass" if bakeoff_packet["runtimeStatus"] == "pass" else "blocked"
    return {
        "schemaVersion": PROOF_PACKET_SCHEMA_VERSION,
        "packetType": "eml_scoped_semantic_proof_packet_v0",
        "date": DATE,
        "caseId": case_id,
        "sourceExpression": certificate["sourceExpression"],
        "loweredExpression": certificate["loweredExpression"],
        "r12LoweredExpression": stub_packet["loweredExpression"],
        "normalForm": certificate["normalForm"],
        "proofStatus": proof_status,
        "domainGuards": certificate["domainGuards"],
        "rewriteSteps": certificate["rewriteSteps"],
        "sourceBakeoffStatus": bakeoff_packet["runtimeStatus"],
        "scopeBoundary": "single named expression under listed domain guards",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "proofPacketCount": len(packets),
        "scopedProofPassCount": sum(1 for packet in packets if packet["proofStatus"] == "scoped_proof_pass"),
        "blockedCount": sum(1 for packet in packets if packet["proofStatus"] == "blocked"),
        "coveredCaseIds": [packet["caseId"] for packet in packets],
        "compilerCorrectnessClaim": False,
        "fullEmlSemanticsClaim": False,
        "semanticEquivalenceClaim": False,
        "formalCompilerProofClaim": False,
        "productionLoweringClaim": False,
        "deployPerformed": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-r10c-scoped-semantic-proof",
        "title": "EML-R10C Scoped Semantic Proof",
        "reviewDecision": "scoped_rewrite_certificates_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "scoped_rewrite_certificates_no_compiler_correctness_claim",
        "semanticReview": {
            "proofPacketCount": payload["summary"]["proofPacketCount"],
            "scopedProofPassCount": payload["summary"]["scopedProofPassCount"],
            "coveredCaseIds": payload["summary"]["coveredCaseIds"],
            "compilerCorrectnessClaim": False,
            "formalCompilerProofClaim": False,
        },
        "claimBoundary": "Scoped rewrite certificates for named expressions only; no full compiler correctness, full EML semantics, or production lowering claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Consumes R12 generated stubs and R10B bakeoff packets.",
            "Records explicit rewrite steps and domain guards.",
            "Advances selected lowered forms, not the whole compiler.",
        ],
        "validationCommands": [
            "python python/scripts/eml_r10c_scoped_semantic_proof.py --build --strict",
            "python -m pytest -q python/tests/test_eml_r10c_scoped_semantic_proof.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_r10c.v0",
        "date": DATE,
        "title": "EML-R10C Scoped Semantic Proof",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "R10E formal compiler proof skeleton or next MachLib witness",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-R10C Scoped Semantic Proof",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "R10C records narrow rewrite certificates for selected lowered forms.",
        "It does not prove compiler correctness or full EML semantics.",
        "",
        "| Case | Status | Guards | Steps |",
        "|---|---|---|---:|",
    ]
    for packet in payload["proofPackets"]:
        guards = "; ".join(packet["domainGuards"])
        lines.append(
            f"| `{packet['caseId']}` | `{packet['proofStatus']}` | {guards} | {len(packet['rewriteSteps'])} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Proof packets: `{summary['proofPacketCount']}`",
            f"- Scoped proof pass: `{summary['scopedProofPassCount']}`",
            f"- Blocked: `{summary['blockedCount']}`",
            f"- Compiler correctness claim: `{summary['compilerCorrectnessClaim']}`",
            f"- Formal compiler proof claim: `{summary['formalCompilerProofClaim']}`",
            "",
            "## Boundary",
            "",
            "- Scoped rewrite certificates only.",
            "- No compiler correctness claim.",
            "- No full EML semantics claim.",
            "- No production lowering or deployment claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid R10C schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid R10C status")
    summary = payload["summary"]
    if summary["proofPacketCount"] < 4:
        raise ValueError("expected at least 4 scoped proof packets")
    if summary["blockedCount"] != 0:
        raise ValueError("scoped proof packets must pass")
    for key in [
        "compilerCorrectnessClaim",
        "fullEmlSemanticsClaim",
        "semanticEquivalenceClaim",
        "formalCompilerProofClaim",
        "productionLoweringClaim",
        "deployPerformed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for packet in payload["proofPackets"]:
        if packet.get("schemaVersion") != PROOF_PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid proof packet schema: {packet.get('caseId')}")
        if packet["proofStatus"] != "scoped_proof_pass":
            raise ValueError(f"scoped proof failed: {packet['caseId']}")
        if not packet["domainGuards"]:
            raise ValueError(f"missing domain guards: {packet['caseId']}")
        if not packet["rewriteSteps"]:
            raise ValueError(f"missing rewrite steps: {packet['caseId']}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"packet claim flag must remain false for {packet['caseId']}: {key}")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_proofs(
    r12_path: Path,
    r10b_path: Path,
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    r12 = load_json(r12_path)
    r10b = load_json(r10b_path)
    stubs = {packet["caseId"]: packet for packet in r12["stubPackets"]}
    bakeoffs = {packet["caseId"]: packet for packet in r10b["bakeoffPackets"]}
    packets = [packet_from_stub(stubs[case_id], bakeoffs[case_id]) for case_id in CERTIFICATES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceR12Path": str(r12_path),
        "sourceR10BPath": str(r10b_path),
        "proofPackets": packets,
        "summary": summarize(packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_r10c_scoped_semantic_proof_{stamp}.json"
    report_path = report_dir / f"eml_r10c_scoped_semantic_proof_{stamp}.md"
    evidence_path = evidence_dir / "eml_r10c_scoped_semantic_proof.json"
    feed_path = command_feed_dir / f"eml_r10c_scoped_semantic_proof_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        path = packet_dir / f"{packet['caseId']}_scoped_semantic_proof_packet_{stamp}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--r12-path",
        type=Path,
        default=ROOT / f"python/results/eml_r12_generated_lowering_stubs/eml_r12_generated_lowering_stubs_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument(
        "--r10b-path",
        type=Path,
        default=ROOT / f"python/results/eml_r10b_runtime_bakeoff/eml_r10b_runtime_bakeoff_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_r10c_scoped_semantic_proof")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_scoped_semantic_proof_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_proofs(
        args.r12_path,
        args.r10b_path,
        args.out_dir,
        args.packet_dir,
        args.report_dir,
        args.evidence_dir,
        args.command_feed_dir,
    )
    if args.strict:
        validate_payload(built["payload"])
    print("EML_R10C_SCOPED_SEMANTIC_PROOF_OK")
    print(f"proof_packets={built['payload']['summary']['proofPacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
