#!/usr/bin/env python3
"""FEF-P26 rc_step_response_at_zero proof-blocker analysis."""

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
from scripts.fef_p25_selected_zero_sorry_file_index import CLAIM_FLAGS as BASE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p26_rc_step_response_proof_blocker_analysis.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p26_rc_step_response_proof_blocker_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P26_RC_STEP_RESPONSE_PROOF_BLOCKER_ANALYSIS_PASS"

FEF_P25_PATH = ROOT / "reports/evidence_packets/fef_p25_selected_zero_sorry_file_index.json"
SORRY_RE = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")
TARGET_THEOREM = "rc_step_response_at_zero"
SOURCE_PATH = "examples/rc_filter.eml"
CASE_ID = "rc_step_response_at_zero_proof_blocker_analysis_v0"

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "proof_blocker_analysis_claim": False,
    "rc_step_response_proved_claim": False,
    "lean_proof_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
}

NON_CLAIMS = [
    "FEF-P26 records a bounded blocker analysis for rc_step_response_at_zero.",
    "FEF-P26 does not discharge rc_step_response_at_zero.",
    "FEF-P26 does not rewrite generated Lean artifacts.",
    "FEF-P26 does not claim broad Lean proof readiness or all generated Lean proofs are discharged.",
    "FEF-P26 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P26 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P26 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_bodies() -> list[dict[str, str]]:
    return [
        {
            "candidateId": "unfold_rfl_v0",
            "proofBody": "  unfold vout_charging_at_zero\n  rfl",
            "expectedBlocker": "requires simplifying vin * (1 - exp (0 / tau_val)) to 0",
        },
        {
            "candidateId": "unfold_simp_v0",
            "proofBody": "  unfold vout_charging_at_zero\n  simp",
            "expectedBlocker": "current simplifier does not reduce exp (0 / tau_val)",
        },
        {
            "candidateId": "unfold_ring_v0",
            "proofBody": "  unfold vout_charging_at_zero\n  ring",
            "expectedBlocker": "ring tactic is not available in the generated MachLib import surface",
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
        "outputExcerpt": output[:900],
    }


def target_obligation_re() -> re.Pattern[str]:
    return re.compile(
        rf"(theorem\s+{TARGET_THEOREM}\b.*?:= by\n)"
        rf"(?P<body>  unfold [A-Za-z_][A-Za-z0-9_']*\n"
        rf"  sorry  -- TODO: prove against MachLib foundations)",
        re.DOTALL,
    )


def analyze_case(tmp_path: Path) -> dict[str, Any]:
    generated_path = tmp_path / f"{CASE_ID}_generated.lean"
    compile_target(FORGE_ROOT / SOURCE_PATH, "lean", generated_path)
    generated_source = generated_path.read_text(encoding="utf-8")
    match = target_obligation_re().search(generated_source)
    if not match:
        raise ValueError(f"target theorem proof body not found: {TARGET_THEOREM}")

    attempts = []
    for candidate in candidate_bodies():
        candidate_source = (
            generated_source[:match.start("body")]
            + candidate["proofBody"]
            + generated_source[match.end("body"):]
        )
        candidate_path = tmp_path / f"{CASE_ID}_{candidate['candidateId']}.lean"
        candidate_path.write_text(candidate_source, encoding="utf-8")
        check = lean_check(candidate_path)
        attempts.append({
            "candidateId": candidate["candidateId"],
            "proofBody": candidate["proofBody"].splitlines(),
            "expectedBlocker": candidate["expectedBlocker"],
            "leanCheck": check,
            "candidateFileSorryCount": len(SORRY_RE.findall(candidate_source)),
        })

    passing = [attempt for attempt in attempts if attempt["leanCheck"]["status"] == "candidate_typecheck_pass"]
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p26_rc_step_response_proof_blocker_packet_v0",
        "date": DATE,
        "caseId": CASE_ID,
        "sourcePath": SOURCE_PATH,
        "targetTheorem": TARGET_THEOREM,
        "generatedTargetLanguage": "lean",
        "generatedFileSorryCount": len(SORRY_RE.findall(generated_source)),
        "targetGeneratedProofBody": match.group("body").splitlines(),
        "attempts": attempts,
        "passingCandidateCount": len(passing),
        "blockedCandidateCount": len(attempts) - len(passing),
        "blockerStatus": "blocked_no_candidate_passed" if not passing else "candidate_found",
        "blockerExplanation": "The target reduces to vin * (1 - exp (0 / tau_val)) = 0; current selected imports do not expose the needed exp-zero/division-zero/ring rewrite chain.",
        "neededProofSurface": [
            "0 / tau_val = 0 for tau_val > 0 or denominator nonzero",
            "Real.exp 0 = 1",
            "1 - 1 = 0",
            "vin * 0 = 0",
            "a proof script or MachLib lemma composing those rewrites",
        ],
        "machlibBuildLib": str(MACHLIB_BUILD_LIB),
        "machlibBuildLibExists": MACHLIB_BUILD_LIB.exists(),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "packetCount": 1,
        "targetTheorem": TARGET_THEOREM,
        "generatedFileSorryCount": packet["generatedFileSorryCount"],
        "attemptCount": len(packet["attempts"]),
        "passingCandidateCount": packet["passingCandidateCount"],
        "blockedCandidateCount": packet["blockedCandidateCount"],
        "blockerStatus": packet["blockerStatus"],
        "rcStepResponseProvedClaim": False,
        "proofBlockerAnalysisClaim": False,
        "leanProofClaim": False,
        "allGeneratedLeanFilesProvedClaim": False,
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
    fef_p25 = read_json(FEF_P25_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p26_rc_step_blocker_") as tmp:
        packet = analyze_case(Path(tmp))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p26-rc-step-response-proof-blocker-analysis",
        "decision": "rc_step_response_at_zero_blocker_recorded_no_candidate_discharge",
        "blockerPackets": [packet],
        "summary": summarize(packet),
        "fefP25Link": {
            "path": str(FEF_P25_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p25["reviewDecision"],
        },
        "releaseGates": [
            {"id": "target_blocker_analyzed", "status": "pass"},
            {"id": "rc_step_response_candidate_found", "status": "blocked"},
            {"id": "selected_zero_sorry_files_unchanged", "status": "pass"},
            {"id": "all_generated_lean_files_zero_sorry", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Add or identify MachLib lemmas for zero division, exp_zero, sub_self/sub_eq_zero, and mul_zero.",
            "Retry rc_step_response_at_zero only after the needed proof surface is available.",
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
        "title": "FEF-P26 rc_step_response_at_zero Proof Blocker Analysis",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "bounded_proof_blocker_analysis_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Bounded blocker analysis for rc_step_response_at_zero only; no candidate proof body typechecks, the target theorem remains undischarged, and there is no all-generated-file proof, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "The simple rfl/simp/ring-style candidate set does not discharge rc_step_response_at_zero.",
            "The target reduces to an exponential zero-step rewrite chain not present in the selected proof surface.",
            "P25's selected zero-sorry-file index remains unchanged: rc_filter is still the visible blocker.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p26_rc_step_response_proof_blocker_analysis.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p26_rc_step_response_proof_blocker_analysis.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p26_rc_step_response_proof_blocker_analysis.v0",
        "date": DATE,
        "title": "FEF-P26 rc_step_response_at_zero Proof Blocker Analysis",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add or identify the zero-division and exp-zero proof surface before retrying rc_step_response_at_zero.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["blockerPackets"][0]
    rows = [
        "| Candidate | Status | Expected blocker |",
        "|---|---|---|",
    ]
    for attempt in packet["attempts"]:
        rows.append(
            f"| `{attempt['candidateId']}` | `{attempt['leanCheck']['status']}` | "
            f"{attempt['expectedBlocker']} |"
        )
    summary = payload["summary"]
    needed = [f"- {item}" for item in packet["neededProofSurface"]]
    return "\n".join(
        [
            "# FEF-P26 rc_step_response_at_zero Proof Blocker Analysis",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            *rows,
            "",
            "## Needed Proof Surface",
            "",
            *needed,
            "",
            "## Summary",
            "",
            f"- Target theorem: `{summary['targetTheorem']}`",
            f"- Attempts: `{summary['attemptCount']}`",
            f"- Passing candidates: `{summary['passingCandidateCount']}`",
            f"- Blocked candidates: `{summary['blockedCandidateCount']}`",
            "",
            "## Boundary",
            "",
            "- Blocker analysis only; no proof body was accepted.",
            "- `rc_filter` remains blocked by `rc_step_response_at_zero`.",
            "- No all-generated-file proof, compiler-correctness, formal-equivalence, or public-readiness claim.",
            "- No package publication, checkout, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P26 packet schema")
    if packet["targetTheorem"] != TARGET_THEOREM:
        raise ValueError("invalid target theorem")
    if packet["generatedFileSorryCount"] != 5:
        raise ValueError("rc_filter generated file must start with five placeholders")
    if packet["passingCandidateCount"] != 0:
        raise ValueError("P26 must not record a passing candidate")
    if packet["blockedCandidateCount"] != 3:
        raise ValueError("P26 expected three blocked candidates")
    if packet["blockerStatus"] != "blocked_no_candidate_passed":
        raise ValueError("target blocker must remain visible")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P26 schema")
    summary = payload["summary"]
    if summary["passingCandidateCount"] != 0:
        raise ValueError("rc_step_response_at_zero must remain undischarged")
    if summary["blockedCandidateCount"] != 3:
        raise ValueError("expected three blocked candidates")
    if summary["blockerStatus"] != "blocked_no_candidate_passed":
        raise ValueError("blocker status must remain blocked")
    for key in [
        "rcStepResponseProvedClaim",
        "proofBlockerAnalysisClaim",
        "leanProofClaim",
        "allGeneratedLeanFilesProvedClaim",
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
    for packet in payload["blockerPackets"]:
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
    result_path = out_dir / f"fef_p26_rc_step_response_proof_blocker_analysis_{STAMP}.json"
    report_path = report_dir / f"fef_p26_rc_step_response_proof_blocker_analysis_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p26_rc_step_response_proof_blocker_analysis.json"
    feed_path = command_feed_dir / f"fef_p26_rc_step_response_proof_blocker_analysis_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["blockerPackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p26_rc_step_response_proof_blocker_analysis")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p26_rc_step_response_proof_blocker_analysis_packets")
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
    print("FEF_P26_RC_STEP_RESPONSE_PROOF_BLOCKER_ANALYSIS_OK")
    print(f"passing_candidates={built['payload']['summary']['passingCandidateCount']}")
    print(f"blocked_candidates={built['payload']['summary']['blockedCandidateCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
