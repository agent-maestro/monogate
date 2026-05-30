#!/usr/bin/env python3
"""FEF-P14 selected Lean structural validator."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
FORGE_ROOT = MONOGATE_ROOT / "forge"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.fef_p10_broader_generated_target_reingest import compile_target  # noqa: E402
from scripts.fef_p13_c_rust_generated_target_reingest import CLAIM_FLAGS as BASE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p14_lean_structural_validator.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p14_lean_structural_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P14_LEAN_STRUCTURAL_VALIDATOR_PASS"

FEF_P13_PATH = ROOT / "reports/evidence_packets/fef_p13_c_rust_generated_target_reingest.json"

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "lean_structural_ready": False,
    "lean_typecheck_claim": False,
    "lean_proof_claim": False,
}

NON_CLAIMS = [
    "FEF-P14 records bounded structural validation for selected generated Lean artifacts.",
    "FEF-P14 checks theorem names, MachLib imports, and proof-placeholder counts.",
    "FEF-P14 does not claim Lean proofs are discharged.",
    "FEF-P14 does not claim generated Lean files typecheck in a configured MachLib project.",
    "FEF-P14 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P14 does not claim compiler correctness, formal semantic equivalence, runtime performance, Verilog, zkproof, silicon, or hardware output.",
]

CASES = [
    {
        "caseId": "verified_add_lean_structural_v0",
        "sourcePath": "examples/verified_add.eml",
        "expectedTheorems": ["add_nonneg_is_nonneg"],
    },
    {
        "caseId": "clamp_bounded_lean_structural_v0",
        "sourcePath": "examples/clamp_bounded.eml",
        "expectedTheorems": ["clamp_in_unit_interval"],
    },
    {
        "caseId": "voltage_divider_lean_structural_v0",
        "sourcePath": "examples/voltage_divider.eml",
        "expectedTheorems": [
            "voltage_divider_law",
            "voltage_divider_denom_pos",
            "voltage_divider_symmetric_half",
        ],
    },
]

THEOREM_RE = re.compile(r"^\s*theorem\s+([A-Za-z_][A-Za-z0-9_']*)\b", re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*import\s+(MachLib\.[A-Za-z0-9_.']+)\s*$", re.MULTILINE)
SORRY_RE = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_lean_check(lean_path: Path) -> dict[str, Any]:
    lean = shutil.which("lean")
    if not lean:
        return {
            "attempted": False,
            "status": "tool_unavailable",
            "returnCode": None,
            "stderrExcerpt": "",
        }
    proc = subprocess.run(
        [lean, str(lean_path)],
        cwd=str(FORGE_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    output = (proc.stderr or proc.stdout).strip()
    if proc.returncode == 0:
        status = "pass"
    elif "unknown module prefix 'MachLib'" in output:
        status = "blocked_machlib_import_unresolved"
    else:
        status = "failed"
    return {
        "attempted": True,
        "status": status,
        "returnCode": proc.returncode,
        "stderrExcerpt": output[:500],
    }


def validate_case(case: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    source_path = FORGE_ROOT / case["sourcePath"]
    generated_path = tmp_path / f"{case['caseId']}.lean"
    compile_target(source_path, "lean", generated_path)
    source = generated_path.read_text(encoding="utf-8")
    imports = IMPORT_RE.findall(source)
    theorem_names = THEOREM_RE.findall(source)
    sorry_count = len(SORRY_RE.findall(source))
    expected = list(case["expectedTheorems"])
    missing = [name for name in expected if name not in theorem_names]
    unexpected = [name for name in theorem_names if name not in expected]
    lean_check = run_lean_check(generated_path)
    structural_status = (
        "pass"
        if not missing and len(imports) >= 1 and sorry_count >= len(expected)
        else "fail"
    )
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p14_lean_structural_packet_v0",
        "date": DATE,
        "caseId": case["caseId"],
        "sourcePath": case["sourcePath"],
        "generatedTargetLanguage": "lean",
        "expectedTheorems": expected,
        "declaredTheorems": theorem_names,
        "missingTheorems": missing,
        "unexpectedTheorems": unexpected,
        "machlibImports": imports,
        "sorryCount": sorry_count,
        "generatedLineCount": source.count("\n") + 1,
        "generatedByteCount": len(source.encode("utf-8")),
        "structuralStatus": structural_status,
        "leanToolchainCheck": lean_check,
        "proofStatus": "placeholder_sorry_present",
        "missingEvidence": [
            "MachLib import path configured for standalone Lean typecheck",
            "discharged Lean proofs replacing sorry placeholders",
            "larger Lean structural fixture family",
            "formal compiler correctness proof",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    lean_statuses = sorted({packet["leanToolchainCheck"]["status"] for packet in packets})
    return {
        "packetCount": len(packets),
        "passCount": sum(1 for packet in packets if packet["structuralStatus"] == "pass"),
        "failCount": sum(1 for packet in packets if packet["structuralStatus"] == "fail"),
        "caseCount": len(packets),
        "generatedTargetLanguages": ["lean"],
        "declaredTheoremCount": sum(len(packet["declaredTheorems"]) for packet in packets),
        "expectedTheoremCount": sum(len(packet["expectedTheorems"]) for packet in packets),
        "sorryCount": sum(packet["sorryCount"] for packet in packets),
        "leanBinaryAvailable": shutil.which("lean") is not None,
        "leanToolchainStatuses": lean_statuses,
        "leanTypecheckClaim": False,
        "leanProofClaim": False,
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "targetAllReadyClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    fef_p13 = read_json(FEF_P13_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p14_lean_structural_") as tmp:
        packets = [validate_case(case, Path(tmp)) for case in CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p14-lean-structural-validator",
        "decision": "selected_lean_structural_validation_passed_typecheck_blocked",
        "structuralPackets": packets,
        "summary": summarize(packets),
        "fefP13Link": {
            "path": str(FEF_P13_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p13["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_lean_structural_validation", "status": "pass"},
            {"id": "lean_typecheck_in_configured_machlib_project", "status": "blocked"},
            {"id": "lean_proofs_discharged", "status": "blocked"},
            {"id": "target_all_ready_claim", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Configure standalone Lean/MachLib import path or Lake project for generated Lean typecheck.",
            "Replace selected sorry placeholders with discharged proofs only when proven.",
            "Add structural validators for other non-runtime target families where local tooling exists.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P14 Lean Structural Validator",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_lean_structural_validation_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected generated Lean structural validation only; no Lean typecheck claim, discharged-proof claim, public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, zkproof, silicon, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selected Lean outputs declare the expected theorem names.",
            "Generated Lean outputs carry MachLib imports.",
            "Proof bodies still contain sorry placeholders and are counted explicitly.",
            "Standalone Lean typecheck remains blocked until MachLib imports are configured for this environment.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p14_lean_structural_validator.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p14_lean_structural_validator.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p14_lean_structural_validator.v0",
        "date": DATE,
        "title": "FEF-P14 Lean Structural Validator",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Configure a Lean/MachLib typecheck environment before any Lean proof or typecheck claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Expected theorem count | Declared theorem count | Sorry count | Structural status | Lean check |",
        "|---|---:|---:|---:|---|---|",
    ]
    for packet in payload["structuralPackets"]:
        rows.append(
            f"| `{packet['caseId']}` | {len(packet['expectedTheorems'])} | {len(packet['declaredTheorems'])} | {packet['sorryCount']} | `{packet['structuralStatus']}` | `{packet['leanToolchainCheck']['status']}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P14 Lean Structural Validator",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P14 adds bounded structural validation for selected generated Lean artifacts.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Cases: `{summary['caseCount']}`",
            f"- Packets: `{summary['packetCount']}`",
            f"- Structural passes: `{summary['passCount']}`",
            f"- Expected theorem declarations: `{summary['expectedTheoremCount']}`",
            f"- Declared theorem declarations: `{summary['declaredTheoremCount']}`",
            f"- Sorry placeholders: `{summary['sorryCount']}`",
            f"- Lean toolchain statuses: `{','.join(summary['leanToolchainStatuses'])}`",
            "",
            "## Boundary",
            "",
            "- Selected generated Lean structural validation only.",
            "- No Lean typecheck or discharged-proof claim.",
            "- No package publication or checkout claim.",
            "- No all-target readiness, compiler correctness, or formal semantic equivalence claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P14 packet schema")
    if packet["packetType"] != "fef_p14_lean_structural_packet_v0":
        raise ValueError("invalid FEF-P14 packet type")
    if packet["generatedTargetLanguage"] != "lean":
        raise ValueError("FEF-P14 target must be Lean")
    if packet["structuralStatus"] != "pass":
        raise ValueError(f"{packet['caseId']} structural validation did not pass")
    if packet["missingTheorems"]:
        raise ValueError(f"{packet['caseId']} missing expected theorem declarations")
    if packet["sorryCount"] < len(packet["expectedTheorems"]):
        raise ValueError(f"{packet['caseId']} must count proof placeholders")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P14 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P14 status")
    summary = payload["summary"]
    if summary["caseCount"] != len(CASES):
        raise ValueError("unexpected FEF-P14 case count")
    if summary["passCount"] != summary["packetCount"]:
        raise ValueError("all FEF-P14 structural packets must pass")
    if summary["expectedTheoremCount"] != summary["declaredTheoremCount"]:
        raise ValueError("expected theorem count must match declared theorem count")
    if summary["sorryCount"] < summary["expectedTheoremCount"]:
        raise ValueError("sorry placeholders must be counted")
    for key in [
        "leanTypecheckClaim",
        "leanProofClaim",
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "targetAllReadyClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["structuralPackets"]:
        validate_packet(packet)


def build_outputs(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p14_lean_structural_validator_{STAMP}.json"
    report_path = report_dir / f"fef_p14_lean_structural_validator_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p14_lean_structural_validator.json"
    feed_path = command_feed_dir / f"fef_p14_lean_structural_validator_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["structuralPackets"]:
        packet_path = packet_dir / f"{packet['caseId']}_{STAMP}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p14_lean_structural_validator")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p14_lean_structural_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P14_LEAN_STRUCTURAL_VALIDATOR_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"theorems={built['payload']['summary']['declaredTheoremCount']}")
    print(f"sorry={built['payload']['summary']['sorryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
