#!/usr/bin/env python3
"""FEF-P20 Lean proof-discharge candidate scanner."""

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
from scripts.fef_p17_broader_lean_typecheck_with_sorry import CASES as P17_CASES  # noqa: E402
from scripts.fef_p19_additional_lean_proof_discharge import CLAIM_FLAGS as BASE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p20_lean_proof_candidate_scanner.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p20_lean_proof_candidate_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P20_LEAN_PROOF_CANDIDATE_SCANNER_PASS"

FEF_P19_PATH = ROOT / "reports/evidence_packets/fef_p19_additional_lean_proof_discharge.json"
SORRY_RE = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")
PROOF_OBLIGATION_RE = re.compile(
    r"theorem\s+(?P<theorem>[A-Za-z_][A-Za-z0-9_']*)\b"
    r"(?P<header>.*?)"
    r":= by\n"
    r"(?P<body>  unfold (?P<function>[A-Za-z_][A-Za-z0-9_']*)\n"
    r"  sorry  -- TODO: prove against MachLib foundations)",
    re.DOTALL,
)

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "candidate_scanner_proof_claim": False,
    "lean_proof_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
}

NON_CLAIMS = [
    "FEF-P20 scans selected generated Lean proof obligations for small no-sorry candidate proof bodies.",
    "FEF-P20 reports candidate closure and blockers; it does not automatically discharge the generated source artifacts.",
    "FEF-P20 does not claim broad Lean proof readiness or all generated Lean proofs are discharged.",
    "FEF-P20 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P20 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P20 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
    "FEF-P20 relies on the current MachLib axiomatic foundation surface and does not audit MachLib foundational soundness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_bodies(function_name: str) -> list[dict[str, str]]:
    return [
        {
            "candidateId": "rfl_v0",
            "proofBody": "  rfl",
        },
        {
            "candidateId": "unfold_rfl_v0",
            "proofBody": f"  unfold {function_name}\n  rfl",
        },
        {
            "candidateId": "unfold_simp_v0",
            "proofBody": f"  unfold {function_name}\n  simp",
        },
        {
            "candidateId": "unfold_add_nonneg_v0",
            "proofBody": f"  unfold {function_name}\n  exact add_nonneg h1 h2",
        },
    ]


def lean_check(lean_path: Path) -> dict[str, Any]:
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
    status = "candidate_typecheck_pass" if proc.returncode == 0 else "candidate_typecheck_fail"
    if "unknown module prefix 'MachLib'" in output:
        status = "blocked_machlib_import_unresolved"
    return {
        "attempted": True,
        "status": status,
        "returnCode": proc.returncode,
        "outputExcerpt": output[:700],
    }


def scan_obligation(source: str, match: re.Match[str], path_base: Path, index: int) -> dict[str, Any]:
    theorem_name = match.group("theorem")
    function_name = match.group("function")
    generated_body = match.group("body")
    attempts = []
    selected = None
    for candidate in candidate_bodies(function_name):
        if "sorry" in candidate["proofBody"]:
            raise ValueError("candidate proof bodies must not contain sorry")
        candidate_source = source[:match.start("body")] + candidate["proofBody"] + source[match.end("body"):]
        candidate_path = path_base.with_name(f"{path_base.stem}_{index}_{candidate['candidateId']}.lean")
        candidate_path.write_text(candidate_source, encoding="utf-8")
        check = lean_check(candidate_path)
        attempt = {
            "candidateId": candidate["candidateId"],
            "proofBody": candidate["proofBody"].splitlines(),
            "leanCheck": check,
            "candidateFileSorryCount": len(SORRY_RE.findall(candidate_source)),
        }
        attempts.append(attempt)
        if selected is None and check["status"] == "candidate_typecheck_pass":
            selected = attempt
    packet = {
        "theoremName": theorem_name,
        "functionName": function_name,
        "generatedProofBody": generated_body.splitlines(),
        "generatedFileSorryCount": len(SORRY_RE.findall(source)),
        "attempts": attempts,
        "candidateStatus": "candidate_found" if selected else "blocked_no_candidate_passed",
        "selectedCandidate": selected,
    }
    return packet


def validate_case(case: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    lean_path = tmp_path / f"{case['caseId']}.lean"
    compile_target(FORGE_ROOT / case["sourcePath"], "lean", lean_path)
    source = lean_path.read_text(encoding="utf-8")
    obligations = [
        scan_obligation(source, match, lean_path, index)
        for index, match in enumerate(PROOF_OBLIGATION_RE.finditer(source), start=1)
    ]
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p20_lean_proof_candidate_packet_v0",
        "date": DATE,
        "caseId": case["caseId"].replace("broader_lean_typecheck", "proof_candidate_scan"),
        "sourcePath": case["sourcePath"],
        "generatedTargetLanguage": "lean",
        "generatedFileSorryCount": len(SORRY_RE.findall(source)),
        "proofObligationCount": len(obligations),
        "candidateFoundCount": sum(1 for obligation in obligations if obligation["candidateStatus"] == "candidate_found"),
        "blockedCandidateCount": sum(1 for obligation in obligations if obligation["candidateStatus"] != "candidate_found"),
        "obligations": obligations,
        "machlibBuildLib": str(MACHLIB_BUILD_LIB),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "proofDischargePolicy": "scan_only_no_generated_source_rewrite",
        "missingEvidence": [
            "review and intentional discharge for candidate-found theorems",
            "new MachLib lemmas or proof scripts for blocked obligations",
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
    obligation_count = sum(packet["proofObligationCount"] for packet in packets)
    candidate_found = sum(packet["candidateFoundCount"] for packet in packets)
    blocked = sum(packet["blockedCandidateCount"] for packet in packets)
    return {
        "packetCount": len(packets),
        "caseCount": len(packets),
        "proofObligationCount": obligation_count,
        "candidateFoundCount": candidate_found,
        "blockedCandidateCount": blocked,
        "candidateCoverageRatio": candidate_found / obligation_count if obligation_count else 0.0,
        "generatedFileSorryCount": sum(packet["generatedFileSorryCount"] for packet in packets),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "candidateScannerProofClaim": False,
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
    fef_p19 = read_json(FEF_P19_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p20_lean_candidate_scan_") as tmp:
        packets = [validate_case(case, Path(tmp)) for case in P17_CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p20-lean-proof-candidate-scanner",
        "decision": "selected_lean_proof_candidate_scan_recorded",
        "candidatePackets": packets,
        "summary": summarize(packets),
        "fefP19Link": {
            "path": str(FEF_P19_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p19["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_candidate_scan_completed", "status": "pass"},
            {"id": "candidate_found_theorems_reviewed_and_discharged", "status": "blocked"},
            {"id": "blocked_obligations_have_machlib_proofs", "status": "blocked"},
            {"id": "machlib_foundational_audit", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Review candidate-found obligations before adding additional discharge packets.",
            "For blocked obligations, add targeted MachLib lemmas or keep the blockers visible.",
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
        "title": "FEF-P20 Lean Proof Candidate Scanner",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_generated_lean_candidate_scan_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected generated Lean proof-candidate scan only; candidate-found obligations are not automatically promoted to discharged proofs, blockers remain visible, and there is no broad Lean proof readiness, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "The scanner compiles the FEF-P17 selected generated Lean family.",
            "Each generated `unfold ...; sorry` obligation is tested against a fixed no-sorry candidate set.",
            "Candidate-found obligations and blocked obligations are reported separately.",
            "The scanner does not rewrite generated source artifacts or make proof-readiness claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p20_lean_proof_candidate_scanner.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p20_lean_proof_candidate_scanner.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p20_lean_proof_candidate_scanner.v0",
        "date": DATE,
        "title": "FEF-P20 Lean Proof Candidate Scanner",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Review candidate-found obligations before adding more discharge packets.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Obligations | Candidate found | Blocked |",
        "|---|---:|---:|---:|",
    ]
    for packet in payload["candidatePackets"]:
        rows.append(
            f"| `{packet['caseId']}` | {packet['proofObligationCount']} | {packet['candidateFoundCount']} | {packet['blockedCandidateCount']} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P20 Lean Proof Candidate Scanner",
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
            f"- Proof obligations scanned: `{summary['proofObligationCount']}`",
            f"- Candidate found: `{summary['candidateFoundCount']}`",
            f"- Blocked candidates: `{summary['blockedCandidateCount']}`",
            f"- Candidate coverage ratio: `{summary['candidateCoverageRatio']:.3f}`",
            "",
            "## Boundary",
            "",
            "- Candidate scanner only; no generated source rewrite.",
            "- Candidate-found obligations are not automatically proof-readiness claims.",
            "- Blocked obligations remain visible.",
            "- No compiler-correctness, formal-equivalence, public-readiness, package, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P20 packet schema")
    if packet["packetType"] != "fef_p20_lean_proof_candidate_packet_v0":
        raise ValueError("invalid FEF-P20 packet type")
    if not packet["machlibBuildLibExists"]:
        raise ValueError("MachLib build lib must exist for FEF-P20")
    if packet["proofObligationCount"] != packet["generatedFileSorryCount"]:
        raise ValueError("each selected generated sorry must map to an obligation")
    for obligation in packet["obligations"]:
        for attempt in obligation["attempts"]:
            if any("sorry" in line for line in attempt["proofBody"]):
                raise ValueError("candidate proof body must not contain sorry")
        if obligation["candidateStatus"] == "candidate_found":
            if obligation["selectedCandidate"] is None:
                raise ValueError("candidate_found obligations must record selectedCandidate")
        else:
            if obligation["selectedCandidate"] is not None:
                raise ValueError("blocked obligations must not record selectedCandidate")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P20 schema")
    summary = payload["summary"]
    if summary["caseCount"] != len(P17_CASES):
        raise ValueError("unexpected FEF-P20 case count")
    if summary["proofObligationCount"] != 15:
        raise ValueError("unexpected selected proof obligation count")
    if summary["candidateFoundCount"] < 1:
        raise ValueError("expected at least one candidate-found obligation")
    if summary["blockedCandidateCount"] < 1:
        raise ValueError("expected at least one blocker to remain visible")
    for key in [
        "candidateScannerProofClaim",
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
    for packet in payload["candidatePackets"]:
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
    result_path = out_dir / f"fef_p20_lean_proof_candidate_scanner_{STAMP}.json"
    report_path = report_dir / f"fef_p20_lean_proof_candidate_scanner_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p20_lean_proof_candidate_scanner.json"
    feed_path = command_feed_dir / f"fef_p20_lean_proof_candidate_scanner_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["candidatePackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p20_lean_proof_candidate_scanner")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p20_lean_proof_candidate_packets")
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
    print("FEF_P20_LEAN_PROOF_CANDIDATE_SCANNER_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"obligations={built['payload']['summary']['proofObligationCount']}")
    print(f"candidate_found={built['payload']['summary']['candidateFoundCount']}")
    print(f"blocked={built['payload']['summary']['blockedCandidateCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
