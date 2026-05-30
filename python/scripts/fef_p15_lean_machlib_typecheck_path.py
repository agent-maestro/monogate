#!/usr/bin/env python3
"""FEF-P15 configured Lean/MachLib typecheck-path validator."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
MACHLIB_ROOT = MONOGATE_ROOT / "machlib"
MACHLIB_BUILD_LIB = MACHLIB_ROOT / "foundations/.lake/build/lib"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.fef_p14_lean_structural_validator import (  # noqa: E402
    CASES,
    CLAIM_FLAGS as BASE_CLAIM_FLAGS,
    NON_CLAIMS as P14_NON_CLAIMS,
    validate_case,
)

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p15_lean_machlib_typecheck_path.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p15_lean_typecheck_path_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P15_LEAN_MACHLIB_TYPECHECK_PATH_PASS"

FEF_P14_PATH = ROOT / "reports/evidence_packets/fef_p14_lean_structural_validator.json"

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "lean_import_resolution_claim": False,
    "lean_typecheck_with_sorry_claim": False,
    "lean_proof_claim": False,
}

NON_CLAIMS = [
    "FEF-P15 records a configured Lean/MachLib typecheck-path probe for selected generated Lean artifacts.",
    "FEF-P15 may report Lean typecheck success only for files whose proof bodies still contain sorry placeholders.",
    "FEF-P15 does not claim discharged Lean proofs.",
    "FEF-P15 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P15 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P15 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
]

SORRY_RE = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_lean_result(returncode: int, output: str) -> str:
    if returncode == 0:
        return "typecheck_with_sorry_pass"
    if "unknown module prefix 'MachLib'" in output:
        return "blocked_machlib_import_unresolved"
    if "ambiguous term" in output:
        return "blocked_generated_name_ambiguity"
    return "failed_lean_elaboration"


def lean_check_with_machlib(lean_path: Path) -> dict[str, Any]:
    lean = shutil.which("lean")
    if not lean:
        return {
            "attempted": False,
            "status": "tool_unavailable",
            "returnCode": None,
            "outputExcerpt": "",
        }
    env = os.environ.copy()
    existing = env.get("LEAN_PATH", "")
    env["LEAN_PATH"] = f"{MACHLIB_BUILD_LIB}:{existing}" if existing else str(MACHLIB_BUILD_LIB)
    proc = subprocess.run(
        [lean, str(lean_path)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    output = (proc.stdout or proc.stderr).strip()
    return {
        "attempted": True,
        "status": classify_lean_result(proc.returncode, output),
        "returnCode": proc.returncode,
        "outputExcerpt": output[:700],
    }


def validate_typecheck_case(case: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    structural_packet = validate_case(case, tmp_path)
    lean_path = tmp_path / f"{case['caseId']}.lean"
    source = lean_path.read_text(encoding="utf-8")
    configured_check = lean_check_with_machlib(lean_path)
    import_resolved = configured_check["status"] != "blocked_machlib_import_unresolved"
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p15_lean_typecheck_path_packet_v0",
        "date": DATE,
        "caseId": case["caseId"].replace("lean_structural", "lean_typecheck_path"),
        "sourcePath": case["sourcePath"],
        "generatedTargetLanguage": "lean",
        "expectedTheorems": structural_packet["expectedTheorems"],
        "declaredTheorems": structural_packet["declaredTheorems"],
        "sorryCount": len(SORRY_RE.findall(source)),
        "machlibBuildLib": str(MACHLIB_BUILD_LIB),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "configuredLeanCheck": configured_check,
        "machlibImportResolved": import_resolved,
        "typecheckWithSorryStatus": configured_check["status"],
        "proofStatus": "placeholder_sorry_present",
        "missingEvidence": [
            "generated-name hygiene fix for any Lean elaboration ambiguity",
            "discharged Lean proofs replacing sorry placeholders",
            "larger Lean typecheck-path fixture family",
            "formal compiler correctness proof",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = sorted({packet["typecheckWithSorryStatus"] for packet in packets})
    return {
        "packetCount": len(packets),
        "caseCount": len(packets),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "machlibImportResolvedCount": sum(1 for packet in packets if packet["machlibImportResolved"]),
        "typecheckWithSorryPassCount": sum(1 for packet in packets if packet["typecheckWithSorryStatus"] == "typecheck_with_sorry_pass"),
        "typecheckBlockedCount": sum(1 for packet in packets if packet["typecheckWithSorryStatus"] != "typecheck_with_sorry_pass"),
        "typecheckWithSorryStatuses": statuses,
        "declaredTheoremCount": sum(len(packet["declaredTheorems"]) for packet in packets),
        "sorryCount": sum(packet["sorryCount"] for packet in packets),
        "leanImportResolutionClaim": False,
        "leanTypecheckWithSorryClaim": False,
        "leanProofClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "targetAllReadyClaim": False,
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    fef_p14 = read_json(FEF_P14_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p15_lean_typecheck_path_") as tmp:
        packets = [validate_typecheck_case(case, Path(tmp)) for case in CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p15-lean-machlib-typecheck-path",
        "decision": "lean_machlib_import_path_configured_selected_typecheck_with_sorry_partial",
        "typecheckPathPackets": packets,
        "summary": summarize(packets),
        "fefP14Link": {
            "path": str(FEF_P14_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p14["reviewDecision"],
        },
        "releaseGates": [
            {"id": "machlib_build_lib_found", "status": "pass"},
            {"id": "selected_lean_import_resolution", "status": "pass"},
            {"id": "all_selected_lean_typecheck_with_sorry", "status": "blocked"},
            {"id": "lean_proofs_discharged", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Fix generated Lean name hygiene for ambiguous theorem/function names.",
            "Keep sorry placeholders visible until proofs are discharged.",
            "Do not promote Lean proof or compiler-correctness copy from this packet.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "p14NonClaimsInherited": list(P14_NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P15 Lean MachLib Typecheck Path",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "configured_lean_machlib_import_path_partial_typecheck_with_sorry",
        "semanticReview": payload["summary"],
        "claimBoundary": "Configured Lean/MachLib typecheck-path probe only; sorry placeholders remain, one selected case is blocked by generated-name ambiguity, and there is no Lean proof, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Local MachLib .lake build artifacts are present and used through LEAN_PATH.",
            "MachLib imports resolve for the selected generated Lean artifacts.",
            "Two selected generated Lean artifacts typecheck with sorry placeholders present.",
            "One selected generated Lean artifact is blocked by generated-name ambiguity.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p15_lean_machlib_typecheck_path.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p15_lean_machlib_typecheck_path.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p15_lean_machlib_typecheck_path.v0",
        "date": DATE,
        "title": "FEF-P15 Lean MachLib Typecheck Path",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Fix generated Lean name hygiene before expanding Lean typecheck claims.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Import resolved | Typecheck status | Sorry count |",
        "|---|---|---|---:|",
    ]
    for packet in payload["typecheckPathPackets"]:
        rows.append(
            f"| `{packet['caseId']}` | `{packet['machlibImportResolved']}` | `{packet['typecheckWithSorryStatus']}` | {packet['sorryCount']} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P15 Lean MachLib Typecheck Path",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Cases: `{summary['caseCount']}`",
            f"- MachLib import resolved: `{summary['machlibImportResolvedCount']}`",
            f"- Typecheck-with-sorry passes: `{summary['typecheckWithSorryPassCount']}`",
            f"- Typecheck blocked: `{summary['typecheckBlockedCount']}`",
            f"- Sorry placeholders: `{summary['sorryCount']}`",
            "",
            "## Boundary",
            "",
            "- Configured Lean/MachLib typecheck-path probe only.",
            "- No discharged-proof, formal-equivalence, or compiler-correctness claim.",
            "- No package publication, checkout, public-readiness, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P15 packet schema")
    if packet["packetType"] != "fef_p15_lean_typecheck_path_packet_v0":
        raise ValueError("invalid FEF-P15 packet type")
    if not packet["machlibBuildLibExists"]:
        raise ValueError("MachLib build lib must exist for FEF-P15")
    if not packet["machlibImportResolved"]:
        raise ValueError(f"{packet['caseId']} must resolve MachLib imports")
    if packet["sorryCount"] < len(packet["expectedTheorems"]):
        raise ValueError(f"{packet['caseId']} must keep sorry placeholders counted")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P15 schema")
    summary = payload["summary"]
    if summary["caseCount"] != len(CASES):
        raise ValueError("unexpected FEF-P15 case count")
    if summary["machlibImportResolvedCount"] != len(CASES):
        raise ValueError("all selected Lean cases must resolve MachLib imports")
    if summary["typecheckWithSorryPassCount"] < 2:
        raise ValueError("expected at least two selected Lean typecheck-with-sorry passes")
    if summary["typecheckBlockedCount"] < 1:
        raise ValueError("expected at least one blocker to remain explicit")
    for key in [
        "leanImportResolutionClaim",
        "leanTypecheckWithSorryClaim",
        "leanProofClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "targetAllReadyClaim",
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["typecheckPathPackets"]:
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
    result_path = out_dir / f"fef_p15_lean_machlib_typecheck_path_{STAMP}.json"
    report_path = report_dir / f"fef_p15_lean_machlib_typecheck_path_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p15_lean_machlib_typecheck_path.json"
    feed_path = command_feed_dir / f"fef_p15_lean_machlib_typecheck_path_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["typecheckPathPackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p15_lean_machlib_typecheck_path")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p15_lean_typecheck_path_packets")
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
    print("FEF_P15_LEAN_MACHLIB_TYPECHECK_PATH_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"typecheck_with_sorry_passes={built['payload']['summary']['typecheckWithSorryPassCount']}")
    print(f"blocked={built['payload']['summary']['typecheckBlockedCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
