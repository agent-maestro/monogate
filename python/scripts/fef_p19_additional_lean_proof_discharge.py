#!/usr/bin/env python3
"""FEF-P19 additional selected Lean proof-discharge validator."""

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
FORGE_ROOT = MONOGATE_ROOT / "forge"
MACHLIB_BUILD_LIB = MONOGATE_ROOT / "machlib/foundations/.lake/build/lib"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.fef_p10_broader_generated_target_reingest import compile_target  # noqa: E402
from scripts.fef_p18_selected_lean_proof_discharge import CLAIM_FLAGS as BASE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p19_additional_lean_proof_discharge.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p19_additional_lean_proof_discharge_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P19_ADDITIONAL_LEAN_PROOF_DISCHARGE_PASS"

FEF_P18_PATH = ROOT / "reports/evidence_packets/fef_p18_selected_lean_proof_discharge.json"
SORRY_RE = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")
THEOREM_RE = re.compile(r"^\s*theorem\s+([A-Za-z_][A-Za-z0-9_']*)\b", re.MULTILINE)

CASES = [
    {
        "caseId": "mosfet_zero_overdrive_additional_proof_discharge_v0",
        "sourcePath": "examples/carriers/electronics/mosfet_iv.eml",
        "theoremName": "mosfet_zero_overdrive_zero_current",
        "generatedProofBody": "  unfold id_at_threshold\n  sorry  -- TODO: prove against MachLib foundations",
        "dischargedProofBody": "  unfold id_at_threshold\n  rfl",
        "remainingPlaceholderTheorems": ["mosfet_prefactor_positive"],
        "proofDependency": "Lean.rfl",
    },
]

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "additional_selected_lean_proof_claim": False,
    "lean_proof_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
}

NON_CLAIMS = [
    "FEF-P19 records one additional selected generated Lean theorem whose proof body typechecks without sorry.",
    "FEF-P19 leaves remaining generated Lean placeholders explicit when the containing file has other proof obligations.",
    "FEF-P19 does not claim broad Lean proof readiness or all generated Lean proofs are discharged.",
    "FEF-P19 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P19 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P19 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
    "FEF-P19 relies on the current MachLib axiomatic foundation surface and does not audit MachLib foundational soundness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    if proc.returncode == 0:
        status = "typecheck_selected_proof_with_remaining_sorry_pass"
    elif "unknown module prefix 'MachLib'" in output:
        status = "blocked_machlib_import_unresolved"
    else:
        status = "failed_lean_elaboration"
    return {
        "attempted": True,
        "status": status,
        "returnCode": proc.returncode,
        "outputExcerpt": output[:700],
    }


def validate_case(case: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    generated_path = tmp_path / f"{case['caseId']}_generated.lean"
    discharged_path = tmp_path / f"{case['caseId']}_discharged.lean"
    compile_target(FORGE_ROOT / case["sourcePath"], "lean", generated_path)
    generated_source = generated_path.read_text(encoding="utf-8")
    theorem_names = THEOREM_RE.findall(generated_source)
    if case["theoremName"] not in theorem_names:
        raise ValueError(f"missing theorem {case['theoremName']}")
    if case["generatedProofBody"] not in generated_source:
        raise ValueError(f"expected generated proof placeholder missing for {case['caseId']}")
    discharged_source = generated_source.replace(
        case["generatedProofBody"],
        case["dischargedProofBody"],
        1,
    )
    discharged_path.write_text(discharged_source, encoding="utf-8")
    lean_check = lean_check_with_machlib(discharged_path)
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p19_additional_lean_proof_discharge_packet_v0",
        "date": DATE,
        "caseId": case["caseId"],
        "sourcePath": case["sourcePath"],
        "generatedTargetLanguage": "lean",
        "theoremName": case["theoremName"],
        "declaredTheorems": theorem_names,
        "proofDependency": case["proofDependency"],
        "generatedFileSorryCount": len(SORRY_RE.findall(generated_source)),
        "dischargedFileSorryCount": len(SORRY_RE.findall(discharged_source)),
        "selectedTheoremDischarged": True,
        "remainingPlaceholderTheorems": list(case["remainingPlaceholderTheorems"]),
        "dischargedProofBody": case["dischargedProofBody"].splitlines(),
        "machlibBuildLib": str(MACHLIB_BUILD_LIB),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "configuredLeanCheck": lean_check,
        "proofDischargeStatus": "additional_selected_theorem_typechecks_remaining_sorry_present",
        "missingEvidence": [
            "proof discharge for the remaining theorem in the same generated file",
            "proof discharge for the remaining generated Lean theorem stubs",
            "broader proof-discharge automation policy",
            "formal compiler correctness proof",
            "audit of MachLib foundational axioms",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = sorted({packet["configuredLeanCheck"]["status"] for packet in packets})
    return {
        "packetCount": len(packets),
        "caseCount": len(packets),
        "additionalSelectedProofPassCount": sum(
            1 for packet in packets
            if packet["configuredLeanCheck"]["status"] == "typecheck_selected_proof_with_remaining_sorry_pass"
            and packet["selectedTheoremDischarged"] is True
        ),
        "additionalSelectedProofBlockedCount": sum(
            1 for packet in packets
            if packet["configuredLeanCheck"]["status"] != "typecheck_selected_proof_with_remaining_sorry_pass"
            or packet["selectedTheoremDischarged"] is not True
        ),
        "leanCheckStatuses": statuses,
        "generatedFileSorryCount": sum(packet["generatedFileSorryCount"] for packet in packets),
        "dischargedFileSorryCount": sum(packet["dischargedFileSorryCount"] for packet in packets),
        "remainingPlaceholderTheoremCount": sum(len(packet["remainingPlaceholderTheorems"]) for packet in packets),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "additionalSelectedLeanProofClaim": False,
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
    fef_p18 = read_json(FEF_P18_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p19_additional_lean_proof_") as tmp:
        packets = [validate_case(case, Path(tmp)) for case in CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p19-additional-lean-proof-discharge",
        "decision": "one_additional_selected_generated_lean_theorem_typechecks_with_remaining_sorry_visible",
        "additionalProofPackets": packets,
        "summary": summarize(packets),
        "fefP18Link": {
            "path": str(FEF_P18_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p18["reviewDecision"],
        },
        "releaseGates": [
            {"id": "machlib_build_lib_found", "status": "pass"},
            {"id": "one_additional_selected_theorem_typechecks", "status": "pass"},
            {"id": "same_file_remaining_placeholder_visible", "status": "pass"},
            {"id": "remaining_generated_lean_proofs_discharged", "status": "blocked"},
            {"id": "machlib_foundational_audit", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Attempt proof discharge for the remaining mosfet prefactor theorem only if it can close without sorry.",
            "Add a proof-discharge candidate scanner before increasing manual proof attempts.",
            "Keep broad Lean proof-readiness and compiler-correctness claims blocked.",
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
        "title": "FEF-P19 Additional Lean Proof Discharge",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "one_additional_selected_generated_lean_theorem_typechecks_with_remaining_sorry_visible",
        "semanticReview": payload["summary"],
        "claimBoundary": "One additional selected generated Lean theorem proof body typechecks against the current MachLib surface while another theorem in the same file still has a sorry placeholder; no broad Lean proof readiness, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "The generated mosfet_iv Lean file initially contains two sorry placeholders.",
            "The selected proof replaces the zero-overdrive theorem placeholder with `unfold id_at_threshold; rfl`.",
            "The discharged selected Lean file typechecks through the configured MachLib path.",
            "The same generated file still contains one remaining sorry placeholder for mosfet_prefactor_positive.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p19_additional_lean_proof_discharge.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p19_additional_lean_proof_discharge.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p19_additional_lean_proof_discharge.v0",
        "date": DATE,
        "title": "FEF-P19 Additional Lean Proof Discharge",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add a proof-discharge candidate scanner before scaling manual proof attempts.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Theorem | Lean status | Generated file sorry | Discharged file sorry | Remaining theorem placeholders |",
        "|---|---|---|---:|---:|---:|",
    ]
    for packet in payload["additionalProofPackets"]:
        rows.append(
            f"| `{packet['caseId']}` | `{packet['theoremName']}` | `{packet['configuredLeanCheck']['status']}` | {packet['generatedFileSorryCount']} | {packet['dischargedFileSorryCount']} | {len(packet['remainingPlaceholderTheorems'])} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P19 Additional Lean Proof Discharge",
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
            f"- Additional selected proof passes: `{summary['additionalSelectedProofPassCount']}`",
            f"- Additional selected proof blocked: `{summary['additionalSelectedProofBlockedCount']}`",
            f"- Generated file sorry placeholders: `{summary['generatedFileSorryCount']}`",
            f"- Discharged file sorry placeholders: `{summary['dischargedFileSorryCount']}`",
            f"- Remaining placeholder theorem count: `{summary['remainingPlaceholderTheoremCount']}`",
            "",
            "## Boundary",
            "",
            "- One additional selected generated Lean theorem is discharged.",
            "- The containing generated file still has a remaining `sorry` placeholder.",
            "- No broad Lean-proof, compiler-correctness, formal-equivalence, or public-readiness claim.",
            "- No package publication, checkout, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P19 packet schema")
    if packet["packetType"] != "fef_p19_additional_lean_proof_discharge_packet_v0":
        raise ValueError("invalid FEF-P19 packet type")
    if not packet["machlibBuildLibExists"]:
        raise ValueError("MachLib build lib must exist for FEF-P19")
    if packet["generatedFileSorryCount"] != 2:
        raise ValueError("selected generated file must start with two sorry placeholders")
    if packet["dischargedFileSorryCount"] != 1:
        raise ValueError("selected discharged file must leave exactly one sorry placeholder")
    if packet["selectedTheoremDischarged"] is not True:
        raise ValueError("selected theorem must be marked discharged")
    if packet["configuredLeanCheck"]["status"] != "typecheck_selected_proof_with_remaining_sorry_pass":
        raise ValueError("selected discharged file must typecheck")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P19 schema")
    summary = payload["summary"]
    if summary["caseCount"] != len(CASES):
        raise ValueError("unexpected FEF-P19 case count")
    if summary["additionalSelectedProofPassCount"] != len(CASES):
        raise ValueError("all selected additional proof-discharge cases must pass")
    if summary["additionalSelectedProofBlockedCount"] != 0:
        raise ValueError("no selected additional proof-discharge blockers may remain")
    if summary["remainingPlaceholderTheoremCount"] != 1:
        raise ValueError("FEF-P19 must keep the same-file remaining placeholder visible")
    for key in [
        "additionalSelectedLeanProofClaim",
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
    for packet in payload["additionalProofPackets"]:
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
    result_path = out_dir / f"fef_p19_additional_lean_proof_discharge_{STAMP}.json"
    report_path = report_dir / f"fef_p19_additional_lean_proof_discharge_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p19_additional_lean_proof_discharge.json"
    feed_path = command_feed_dir / f"fef_p19_additional_lean_proof_discharge_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["additionalProofPackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p19_additional_lean_proof_discharge")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p19_additional_lean_proof_discharge_packets")
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
    print("FEF_P19_ADDITIONAL_LEAN_PROOF_DISCHARGE_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"additional_selected_proof_passes={built['payload']['summary']['additionalSelectedProofPassCount']}")
    print(f"remaining_file_sorry={built['payload']['summary']['dischargedFileSorryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
