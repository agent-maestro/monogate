#!/usr/bin/env python3
"""FEF-P28 zero-division MachLib proof-surface guard."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
MACHLIB_BUILD_LIB = MONOGATE_ROOT / "machlib/foundations/.lake/build/lib"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p28_zero_division_surface_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P28_ZERO_DIVISION_SURFACE_GUARD_PASS"

FEF_P27_PATH = ROOT / "reports/evidence_packets/fef_p27_rc_step_machlib_surface_inventory.json"

GENERATED_IMPORTS = [
    "import MachLib.EML",
    "import MachLib.Trig",
    "import MachLib.Forge",
]

HELPER_IDENTIFIERS = [
    "zero_div_of_ne_zero",
    "zero_div_of_pos",
]

CLAIM_FLAGS = {
    "new_machlib_axiom_claim": False,
    "rc_step_response_proved_claim": False,
    "lean_proof_claim": False,
    "all_generated_lean_files_proved_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "target_all_ready_claim": False,
    "package_published": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
}

NON_CLAIMS = [
    "FEF-P28 records a narrow zero-division proof-surface guard for Forge-generated Lean imports.",
    "FEF-P28 adds no MachLib axiom; the helper is derived from div_def, ne_of_gt, and zero_mul.",
    "FEF-P28 does not discharge rc_step_response_at_zero.",
    "FEF-P28 does not claim broad Lean proof readiness or all generated Lean proofs are discharged.",
    "FEF-P28 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P28 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P28 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def lean_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("LEAN_PATH", "")
    env["LEAN_PATH"] = f"{MACHLIB_BUILD_LIB}:{existing}" if existing else str(MACHLIB_BUILD_LIB)
    return env


def run_lean(source: str, tmp_path: Path, name: str) -> dict[str, Any]:
    lean = shutil.which("lean")
    if not lean:
        return {
            "attempted": False,
            "status": "tool_unavailable",
            "returnCode": None,
            "outputExcerpt": "",
        }
    lean_path = tmp_path / f"{name}.lean"
    lean_path.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [lean, str(lean_path)],
        cwd=str(ROOT),
        env=lean_env(),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    output = (proc.stdout or proc.stderr).strip()
    return {
        "attempted": True,
        "status": "lean_check_pass" if proc.returncode == 0 else "lean_check_fail",
        "returnCode": proc.returncode,
        "outputExcerpt": output[:900],
    }


def identifier_probe(identifier: str, tmp_path: Path) -> dict[str, Any]:
    source = "\n".join([
        *GENERATED_IMPORTS,
        "",
        "open MachLib",
        "open MachLib.Real",
        f"#check {identifier}",
        "",
    ])
    result = run_lean(source, tmp_path, f"probe_{identifier}")
    result["identifier"] = identifier
    result["available"] = result["status"] == "lean_check_pass"
    return result


def proof_chain_probe(tmp_path: Path) -> dict[str, Any]:
    source = "\n".join([
        *GENERATED_IMPORTS,
        "",
        "open MachLib",
        "open MachLib.Real",
        "",
        "noncomputable def vout_charging_at_zero_probe (vin : Real) (tau_val : Real) : Real :=",
        "  (vin * ((1 : Real) - (Real.exp ((0 : Real) / tau_val))))",
        "",
        "theorem rc_step_zero_division_surface_probe (vin : Real) (tau_val : Real)",
        "    (h1 : (tau_val > (0 : Real))) :",
        "    ((vout_charging_at_zero_probe vin tau_val) = (0 : Real)) := by",
        "  unfold vout_charging_at_zero_probe",
        "  rw [zero_div_of_pos h1, exp_zero, sub_def, add_neg, mul_zero]",
        "",
    ])
    result = run_lean(source, tmp_path, "rc_step_zero_division_surface_probe")
    result["probeName"] = "rc_step_zero_division_surface_probe"
    return result


def build_payload() -> dict[str, Any]:
    fef_p27 = read_json(FEF_P27_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p28_zero_division_surface_") as tmp:
        tmp_path = Path(tmp)
        identifier_results = [identifier_probe(identifier, tmp_path) for identifier in HELPER_IDENTIFIERS]
        proof_result = proof_chain_probe(tmp_path)
    available_count = sum(1 for result in identifier_results if result["available"])
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p28-zero-division-surface-guard",
        "decision": "zero_division_surface_guard_closed",
        "generatedImports": list(GENERATED_IMPORTS),
        "helperIdentifiers": identifier_results,
        "proofChainProbe": proof_result,
        "summary": {
            "helperIdentifierCount": len(identifier_results),
            "helperIdentifierAvailableCount": available_count,
            "zeroDivOfNeZeroAvailable": any(
                result["identifier"] == "zero_div_of_ne_zero" and result["available"]
                for result in identifier_results
            ),
            "zeroDivOfPosAvailable": any(
                result["identifier"] == "zero_div_of_pos" and result["available"]
                for result in identifier_results
            ),
            "rcStepZeroDivisionSurfaceProbePass": proof_result["status"] == "lean_check_pass",
            "newMachlibAxiomClaim": False,
            "rcStepResponseProvedClaim": False,
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
        },
        "fefP27Link": {
            "path": str(FEF_P27_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p27["reviewDecision"],
        },
        "releaseGates": [
            {"id": "zero_division_helper_surface_available", "status": "pass"},
            {"id": "zero_division_proof_chain_probe_typechecks", "status": "pass"},
            {"id": "rc_step_response_at_zero_discharged", "status": "blocked"},
            {"id": "all_generated_lean_files_zero_sorry", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Retry rc_step_response_at_zero as a scoped proof-discharge packet using zero_div_of_pos.",
            "Keep generated Lean imports bounded to MachLib.Forge unless a Ring dependency is explicitly justified.",
            "Keep broad compiler, proof, and publication claims blocked.",
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
        "title": "FEF-P28 Zero-Division MachLib Surface Guard",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "narrow_machlib_helper_surface_guard_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Narrow zero-division proof-surface guard only; the helper is derived, rc_step_response_at_zero is not discharged here, and there is no all-generated-file proof, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Generated imports expose zero_div_of_ne_zero and zero_div_of_pos.",
            "The zero-time rc-filter proof-chain probe typechecks using zero_div_of_pos, exp_zero, sub_def, add_neg, and mul_zero.",
            "The packet records surface readiness only; rc_step_response_at_zero remains a follow-up target.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p28_zero_division_surface_guard.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p28_zero_division_surface_guard.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p28_zero_division_surface_guard.v0",
        "date": DATE,
        "title": "FEF-P28 Zero-Division MachLib Surface Guard",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Retry rc_step_response_at_zero as a scoped proof-discharge packet using zero_div_of_pos.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Identifier | Status |",
        "|---|---:|",
    ]
    for result in payload["helperIdentifiers"]:
        rows.append(f"| `{result['identifier']}` | `{result['status']}` |")
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P28 Zero-Division MachLib Surface Guard",
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
            f"- Helper identifiers available: `{summary['helperIdentifierAvailableCount']}` / `{summary['helperIdentifierCount']}`",
            f"- `zero_div_of_ne_zero` available: `{summary['zeroDivOfNeZeroAvailable']}`",
            f"- `zero_div_of_pos` available: `{summary['zeroDivOfPosAvailable']}`",
            f"- Zero-time proof-chain probe passes: `{summary['rcStepZeroDivisionSurfaceProbePass']}`",
            "",
            "## Boundary",
            "",
            "- Narrow derived-helper surface guard only; no new MachLib axiom.",
            "- `rc_step_response_at_zero` remains a follow-up discharge target.",
            "- No all-generated-file proof, compiler-correctness, formal-equivalence, or public-readiness claim.",
            "- No package publication, checkout, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P28 schema")
    summary = payload["summary"]
    if summary["helperIdentifierCount"] != len(HELPER_IDENTIFIERS):
        raise ValueError("unexpected helper identifier count")
    if summary["helperIdentifierAvailableCount"] != len(HELPER_IDENTIFIERS):
        raise ValueError("helper identifiers must all be available")
    if summary["zeroDivOfNeZeroAvailable"] is not True:
        raise ValueError("zero_div_of_ne_zero must be available")
    if summary["zeroDivOfPosAvailable"] is not True:
        raise ValueError("zero_div_of_pos must be available")
    if summary["rcStepZeroDivisionSurfaceProbePass"] is not True:
        raise ValueError("zero-division proof-chain probe must pass")
    for key in [
        "newMachlibAxiomClaim",
        "rcStepResponseProvedClaim",
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
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p28_zero_division_surface_guard_{STAMP}.json"
    report_path = report_dir / f"fef_p28_zero_division_surface_guard_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p28_zero_division_surface_guard.json"
    feed_path = command_feed_dir / f"fef_p28_zero_division_surface_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p28_zero_division_surface_guard")
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
    print("FEF_P28_ZERO_DIVISION_SURFACE_GUARD_OK")
    print(f"helpers_available={built['payload']['summary']['helperIdentifierAvailableCount']}")
    print(f"proof_chain_probe={built['payload']['summary']['rcStepZeroDivisionSurfaceProbePass']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
