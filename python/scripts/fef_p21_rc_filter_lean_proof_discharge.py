#!/usr/bin/env python3
"""FEF-P21 selected rc_filter Lean proof-discharge validator."""

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
from scripts.fef_p20_lean_proof_candidate_scanner import CLAIM_FLAGS as BASE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p21_rc_filter_lean_proof_discharge.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p21_rc_filter_lean_proof_discharge_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P21_RC_FILTER_LEAN_PROOF_DISCHARGE_PASS"

FEF_P20_PATH = ROOT / "reports/evidence_packets/fef_p20_lean_proof_candidate_scanner.json"
SORRY_RE = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")
THEOREM_RE = re.compile(r"^\s*theorem\s+([A-Za-z_][A-Za-z0-9_']*)\b", re.MULTILINE)

CASE = {
    "caseId": "rc_filter_candidate_reviewed_proof_discharge_v0",
    "sourcePath": "examples/rc_filter.eml",
    "selectedTheorems": [
        "rc_time_constant_def",
        "rc_steady_state_equals_input",
        "rc_initial_output_zero",
        "rc_step_response_form",
    ],
    "remainingPlaceholderTheorems": ["rc_step_response_at_zero"],
    "proofBody": "  rfl",
    "proofDependency": "Lean.rfl",
}

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "candidate_reviewed_proof_claim": False,
    "lean_proof_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
}

NON_CLAIMS = [
    "FEF-P21 records reviewed discharge for selected rc_filter generated Lean theorem candidates.",
    "FEF-P21 leaves the same file's remaining generated Lean placeholder explicit.",
    "FEF-P21 does not claim broad Lean proof readiness or all generated Lean proofs are discharged.",
    "FEF-P21 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P21 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P21 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
    "FEF-P21 relies on the current MachLib axiomatic foundation surface and does not audit MachLib foundational soundness.",
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
        status = "typecheck_selected_proofs_with_remaining_sorry_pass"
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


def replace_selected_proofs(source: str) -> tuple[str, list[dict[str, Any]]]:
    discharged = []
    updated = source
    for theorem in CASE["selectedTheorems"]:
        pattern = re.compile(
            rf"(theorem\s+{re.escape(theorem)}\b.*?:= by\n)"
            rf"(?P<body>  unfold [A-Za-z_][A-Za-z0-9_']*\n"
            rf"  sorry  -- TODO: prove against MachLib foundations)",
            re.DOTALL,
        )
        match = pattern.search(updated)
        if not match:
            raise ValueError(f"selected theorem proof body not found: {theorem}")
        generated_body = match.group("body")
        updated = updated[:match.start("body")] + CASE["proofBody"] + updated[match.end("body"):]
        discharged.append({
            "theoremName": theorem,
            "generatedProofBody": generated_body.splitlines(),
            "dischargedProofBody": CASE["proofBody"].splitlines(),
            "proofDependency": CASE["proofDependency"],
        })
    return updated, discharged


def validate_case(tmp_path: Path) -> dict[str, Any]:
    generated_path = tmp_path / f"{CASE['caseId']}_generated.lean"
    discharged_path = tmp_path / f"{CASE['caseId']}_discharged.lean"
    compile_target(FORGE_ROOT / CASE["sourcePath"], "lean", generated_path)
    generated_source = generated_path.read_text(encoding="utf-8")
    theorem_names = THEOREM_RE.findall(generated_source)
    missing = [
        theorem for theorem in CASE["selectedTheorems"] + CASE["remainingPlaceholderTheorems"]
        if theorem not in theorem_names
    ]
    if missing:
        raise ValueError(f"missing theorem declarations: {missing}")
    discharged_source, discharged_theorems = replace_selected_proofs(generated_source)
    discharged_path.write_text(discharged_source, encoding="utf-8")
    lean_check = lean_check_with_machlib(discharged_path)
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p21_rc_filter_lean_proof_discharge_packet_v0",
        "date": DATE,
        "caseId": CASE["caseId"],
        "sourcePath": CASE["sourcePath"],
        "generatedTargetLanguage": "lean",
        "declaredTheorems": theorem_names,
        "selectedDischargedTheorems": discharged_theorems,
        "remainingPlaceholderTheorems": list(CASE["remainingPlaceholderTheorems"]),
        "generatedFileSorryCount": len(SORRY_RE.findall(generated_source)),
        "dischargedFileSorryCount": len(SORRY_RE.findall(discharged_source)),
        "machlibBuildLib": str(MACHLIB_BUILD_LIB),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "configuredLeanCheck": lean_check,
        "proofDischargeStatus": "selected_rc_filter_theorems_typecheck_remaining_sorry_present",
        "missingEvidence": [
            "proof discharge for rc_step_response_at_zero",
            "proof discharge for the remaining generated Lean theorem stubs",
            "targeted MachLib lemmas or proof scripts for blocked obligations",
            "formal compiler correctness proof",
            "audit of MachLib foundational axioms",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    discharged_count = sum(len(packet["selectedDischargedTheorems"]) for packet in packets)
    remaining_count = sum(len(packet["remainingPlaceholderTheorems"]) for packet in packets)
    return {
        "packetCount": len(packets),
        "caseCount": len(packets),
        "selectedDischargedTheoremCount": discharged_count,
        "remainingPlaceholderTheoremCount": remaining_count,
        "generatedFileSorryCount": sum(packet["generatedFileSorryCount"] for packet in packets),
        "dischargedFileSorryCount": sum(packet["dischargedFileSorryCount"] for packet in packets),
        "leanCheckStatuses": sorted({packet["configuredLeanCheck"]["status"] for packet in packets}),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "candidateReviewedProofClaim": False,
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
    fef_p20 = read_json(FEF_P20_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p21_rc_filter_proof_") as tmp:
        packets = [validate_case(Path(tmp))]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p21-rc-filter-lean-proof-discharge",
        "decision": "rc_filter_candidate_found_theorems_reviewed_and_discharged_with_remaining_placeholder_visible",
        "rcFilterProofPackets": packets,
        "summary": summarize(packets),
        "fefP20Link": {
            "path": str(FEF_P20_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p20["reviewDecision"],
        },
        "releaseGates": [
            {"id": "candidate_found_obligations_reviewed", "status": "pass"},
            {"id": "selected_rc_filter_theorems_typecheck", "status": "pass"},
            {"id": "same_file_remaining_placeholder_visible", "status": "pass"},
            {"id": "remaining_generated_lean_proofs_discharged", "status": "blocked"},
            {"id": "machlib_foundational_audit", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Target rc_step_response_at_zero only after a valid MachLib proof path exists.",
            "Review remaining candidate-found obligations before adding more discharge packets.",
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
        "title": "FEF-P21 rc_filter Lean Proof Discharge",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_rc_filter_generated_lean_theorems_typecheck_with_remaining_placeholder_visible",
        "semanticReview": payload["summary"],
        "claimBoundary": "Reviewed discharge for selected rc_filter generated Lean theorem candidates only; one same-file placeholder remains visible, and there is no broad Lean proof readiness, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P20 identified four rc_filter candidate-found obligations.",
            "FEF-P21 replaces those four selected placeholders with `rfl` proof bodies.",
            "The discharged rc_filter generated Lean file typechecks through the configured MachLib path.",
            "The same generated file still contains one visible placeholder for rc_step_response_at_zero.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p21_rc_filter_lean_proof_discharge.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p21_rc_filter_lean_proof_discharge.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p21_rc_filter_lean_proof_discharge.v0",
        "date": DATE,
        "title": "FEF-P21 rc_filter Lean Proof Discharge",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Target rc_step_response_at_zero only after a valid MachLib proof path exists.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["rcFilterProofPackets"][0]
    rows = [
        "| Theorem | Proof body |",
        "|---|---|",
    ]
    for theorem in packet["selectedDischargedTheorems"]:
        rows.append(
            f"| `{theorem['theoremName']}` | `{' '.join(line.strip() for line in theorem['dischargedProofBody'])}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P21 rc_filter Lean Proof Discharge",
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
            f"- Selected discharged theorems: `{summary['selectedDischargedTheoremCount']}`",
            f"- Remaining placeholder theorems: `{summary['remainingPlaceholderTheoremCount']}`",
            f"- Generated file sorry placeholders: `{summary['generatedFileSorryCount']}`",
            f"- Discharged file sorry placeholders: `{summary['dischargedFileSorryCount']}`",
            "",
            "## Boundary",
            "",
            "- Reviewed discharge for selected rc_filter candidates only.",
            "- The same generated file still has one visible `sorry` placeholder.",
            "- No broad Lean-proof, compiler-correctness, formal-equivalence, or public-readiness claim.",
            "- No package publication, checkout, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P21 packet schema")
    if packet["packetType"] != "fef_p21_rc_filter_lean_proof_discharge_packet_v0":
        raise ValueError("invalid FEF-P21 packet type")
    if not packet["machlibBuildLibExists"]:
        raise ValueError("MachLib build lib must exist for FEF-P21")
    if packet["generatedFileSorryCount"] != 5:
        raise ValueError("rc_filter generated file must start with five placeholders")
    if packet["dischargedFileSorryCount"] != 1:
        raise ValueError("rc_filter discharged file must leave exactly one placeholder")
    if len(packet["selectedDischargedTheorems"]) != 4:
        raise ValueError("expected four selected rc_filter theorem discharges")
    if packet["configuredLeanCheck"]["status"] != "typecheck_selected_proofs_with_remaining_sorry_pass":
        raise ValueError("selected rc_filter discharged file must typecheck")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P21 schema")
    summary = payload["summary"]
    if summary["selectedDischargedTheoremCount"] != 4:
        raise ValueError("expected four selected rc_filter discharges")
    if summary["remainingPlaceholderTheoremCount"] != 1:
        raise ValueError("expected one rc_filter placeholder to remain visible")
    for key in [
        "candidateReviewedProofClaim",
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
    for packet in payload["rcFilterProofPackets"]:
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
    result_path = out_dir / f"fef_p21_rc_filter_lean_proof_discharge_{STAMP}.json"
    report_path = report_dir / f"fef_p21_rc_filter_lean_proof_discharge_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p21_rc_filter_lean_proof_discharge.json"
    feed_path = command_feed_dir / f"fef_p21_rc_filter_lean_proof_discharge_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["rcFilterProofPackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p21_rc_filter_lean_proof_discharge")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p21_rc_filter_lean_proof_discharge_packets")
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
    print("FEF_P21_RC_FILTER_LEAN_PROOF_DISCHARGE_OK")
    print(f"selected_discharged={built['payload']['summary']['selectedDischargedTheoremCount']}")
    print(f"remaining_placeholders={built['payload']['summary']['remainingPlaceholderTheoremCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
