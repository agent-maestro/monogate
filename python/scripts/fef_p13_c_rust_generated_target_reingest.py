#!/usr/bin/env python3
"""FEF-P13 selected C/Rust generated-target re-ingest guard."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))
if str(EFROG_ROOT) not in sys.path:
    sys.path.insert(0, str(EFROG_ROOT))

from efrog.decompilers.c import decompile_c_file  # noqa: E402
from efrog.decompilers.rust import decompile_rust_file  # noqa: E402
from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts.fef_p10_broader_generated_target_reingest import (  # noqa: E402
    ATOL,
    RTOL,
    call_generated_python,
    compare_values,
    compile_target,
    decompile_source_case,
)
from scripts.fef_p12_c_rust_generated_target_runtime import (  # noqa: E402
    CLAIM_FLAGS as BASE_CLAIM_FLAGS,
    NON_CLAIMS as P12_NON_CLAIMS,
    SELECTED_CASE_IDS,
    call_generated_c,
    call_generated_rust,
    selected_cases,
)

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p13_c_rust_generated_target_reingest.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p13_generated_reingest_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P13_C_RUST_GENERATED_TARGET_REINGEST_PASS"

FEF_P12_PATH = ROOT / "reports/evidence_packets/fef_p12_c_rust_generated_target_runtime.json"

CLAIM_FLAGS = dict(BASE_CLAIM_FLAGS)

NON_CLAIMS = [
    "FEF-P13 records bounded generated C/Rust target re-ingest checks for selected outputs.",
    "FEF-P13 compares generated C/Rust runtime outputs to re-ingested-and-recompiled Python outputs over deterministic samples.",
    "FEF-P13 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P13 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P13 does not claim runtime performance, Verilog, Lean proofs, zkproof, silicon, or hardware output.",
    "FEF-P13 does not claim all Forge targets are ready.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reingest_generated_target(target: str, generated_path: Path):
    if target == "c":
        return decompile_c_file(str(generated_path))
    if target == "rust":
        return decompile_rust_file(str(generated_path))
    raise ValueError(f"unsupported FEF-P13 target: {target}")


def compare_case_target(case: dict[str, Any], target: str, tmp_path: Path) -> dict[str, Any]:
    source_mod = decompile_source_case(case)
    source_eml = source_mod.to_eml()
    source_eml_path = tmp_path / f"{case['caseId']}_source.eml"
    source_eml_path.write_text(source_eml, encoding="utf-8")

    target_ext = "c" if target == "c" else "rs"
    generated_path = tmp_path / f"{case['caseId']}_generated.{target_ext}"
    compile_target(source_eml_path, target, generated_path)

    reingested_mod = reingest_generated_target(target, generated_path)
    reingested_eml = reingested_mod.to_eml()
    reingested_eml_path = tmp_path / f"{case['caseId']}_{target}_reingested.eml"
    reingested_py_path = tmp_path / f"{case['caseId']}_{target}_reingested.py"
    reingested_eml_path.write_text(reingested_eml, encoding="utf-8")
    compile_target(reingested_eml_path, "python", reingested_py_path)

    samples = case["samples"]
    if target == "c":
        generated_values = call_generated_c(generated_path, case["functionName"], samples, tmp_path)
    elif target == "rust":
        generated_values = call_generated_rust(generated_path, case["functionName"], samples, tmp_path)
    else:
        raise ValueError(f"unsupported FEF-P13 target: {target}")
    reingested_values = call_generated_python(
        reingested_py_path,
        case["functionName"],
        samples,
        f"{case['caseId']}_{target}_reingested",
    )
    frames, max_abs, max_rel = compare_values(generated_values, reingested_values, samples)
    for frame in frames:
        frame["values"] = {
            "generatedTargetRuntime": frame["values"]["generatedTarget"],
            "reingestedRecompiledPython": frame["values"]["reingestedRecompiledPython"],
        }

    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p13_generated_reingest_packet_v0",
        "date": DATE,
        "caseId": f"{case['caseId']}_{target}_generated_reingest",
        "sourceCaseId": case["caseId"],
        "sourceLanguage": case["sourceLanguage"],
        "sourcePath": case["sourcePath"],
        "generatedTargetLanguage": target,
        "reingestedTargetLanguage": "eml",
        "recompiledTargetLanguage": "python",
        "functionName": case["functionName"],
        "sourceEmlHash": fingerprint_eml(source_eml),
        "reingestedEmlHash": fingerprint_eml(reingested_eml),
        "reingestedFunctionCount": len(reingested_mod.functions),
        "sampleCount": len(samples),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "reingestStatus": "pass" if max_abs <= ATOL or max_rel <= RTOL else "fail",
        "frames": frames,
        "bridgeFixesExercised": [
            "Forge C runtime mg_* math call mapping",
            "Forge Rust crate attribute stripping",
            "Forge Rust runtime mg_* math call mapping",
        ],
        "missingEvidence": [
            "larger generated C/Rust re-ingest fixture family",
            "generated C/Rust re-ingest for branch/control-flow targets",
            "formal compiler correctness proof",
            "public package publication decision",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "packetCount": len(packets),
        "passCount": sum(1 for packet in packets if packet["reingestStatus"] == "pass"),
        "failCount": sum(1 for packet in packets if packet["reingestStatus"] == "fail"),
        "caseCount": len({packet["sourceCaseId"] for packet in packets}),
        "sampleCount": sum(packet["sampleCount"] for packet in packets),
        "sourceLanguages": sorted({packet["sourceLanguage"] for packet in packets}),
        "generatedTargetLanguages": sorted({packet["generatedTargetLanguage"] for packet in packets}),
        "recompiledTargetLanguages": sorted({packet["recompiledTargetLanguage"] for packet in packets}),
        "maxAbsError": max(packet["maxAbsError"] for packet in packets),
        "maxRelError": max(packet["maxRelError"] for packet in packets),
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
    fef_p12 = read_json(FEF_P12_PATH)
    packets: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="fef_p13_c_rust_reingest_") as tmp:
        tmp_path = Path(tmp)
        for case in selected_cases():
            for target in ("c", "rust"):
                packets.append(compare_case_target(case, target, tmp_path))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p13-c-rust-generated-target-reingest",
        "decision": "selected_c_rust_generated_target_reingest_passed",
        "reingestPackets": packets,
        "summary": summarize(packets),
        "fefP12Link": {
            "path": str(FEF_P12_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p12["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_c_generated_target_reingest", "status": "pass"},
            {"id": "selected_rust_generated_target_reingest", "status": "pass"},
            {"id": "target_all_ready_claim", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Add structural validators for non-runtime targets where local tooling exists.",
            "Broaden generated C/Rust re-ingest beyond the selected scalar fixture set.",
            "Keep publication blocked unless an explicit release action is requested.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "p12NonClaimsInherited": list(P12_NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P13 C/Rust Generated-Target Re-ingest",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_c_rust_generated_target_reingest_sample_grid_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected generated C/Rust target re-ingest only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, silicon, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Generated C targets re-ingest through eFrog after Forge runtime mg_* call mapping.",
            "Generated Rust targets re-ingest through eFrog after generated attribute handling and Forge runtime mg_* call mapping.",
            "Re-ingested C/Rust outputs recompile to Python and agree with generated target runtimes over deterministic samples.",
            "The selected source family includes Python, JavaScript, C, and Rust sources.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p13_c_rust_generated_target_reingest.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p13_c_rust_generated_target_reingest.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p13_c_rust_generated_target_reingest.v0",
        "date": DATE,
        "title": "FEF-P13 C/Rust Generated-Target Re-ingest",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add structural validators for non-runtime targets where local tooling exists.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Source | Generated target | Samples | Status | Max abs error | Max rel error |",
        "|---|---|---|---:|---|---:|---:|",
    ]
    for packet in payload["reingestPackets"]:
        rows.append(
            f"| `{packet['sourceCaseId']}` | `{packet['sourceLanguage']}` | `{packet['generatedTargetLanguage']}` | {packet['sampleCount']} | `{packet['reingestStatus']}` | {packet['maxAbsError']:.3e} | {packet['maxRelError']:.3e} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P13 C/Rust Generated-Target Re-ingest",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P13 adds bounded re-ingest evidence for selected generated C and Rust targets.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Cases: `{summary['caseCount']}`",
            f"- Packets: `{summary['packetCount']}`",
            f"- Samples: `{summary['sampleCount']}`",
            f"- Passes: `{summary['passCount']}`",
            f"- Source languages: `{','.join(summary['sourceLanguages'])}`",
            f"- Generated targets: `{','.join(summary['generatedTargetLanguages'])}`",
            f"- Max abs error: `{summary['maxAbsError']:.3e}`",
            f"- Max rel error: `{summary['maxRelError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Selected generated C/Rust re-ingest sample-grid comparison only.",
            "- No package publication or checkout claim.",
            "- No all-target readiness, compiler correctness, or formal semantic equivalence claim.",
            "- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P13 packet schema")
    if packet["packetType"] != "fef_p13_generated_reingest_packet_v0":
        raise ValueError("invalid FEF-P13 packet type")
    if packet["generatedTargetLanguage"] not in {"c", "rust"}:
        raise ValueError("FEF-P13 generated target must be C or Rust")
    if packet["reingestStatus"] != "pass":
        raise ValueError(f"{packet['caseId']} re-ingest did not pass")
    if packet["reingestedFunctionCount"] != 1:
        raise ValueError(f"{packet['caseId']} must re-ingest exactly one function")
    for frame in packet["frames"]:
        if frame["withinTolerance"] is not True:
            raise ValueError(f"{packet['caseId']} frame outside tolerance")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P13 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P13 status")
    summary = payload["summary"]
    if summary["caseCount"] != len(SELECTED_CASE_IDS):
        raise ValueError("unexpected FEF-P13 selected case count")
    if summary["packetCount"] != len(SELECTED_CASE_IDS) * 2:
        raise ValueError("unexpected FEF-P13 packet count")
    if summary["passCount"] != summary["packetCount"]:
        raise ValueError("all FEF-P13 re-ingest packets must pass")
    if summary["sourceLanguages"] != ["c", "javascript", "python", "rust"]:
        raise ValueError("FEF-P13 must cover C, JavaScript, Python, and Rust sources")
    if summary["generatedTargetLanguages"] != ["c", "rust"]:
        raise ValueError("FEF-P13 must cover C and Rust generated targets")
    if summary["recompiledTargetLanguages"] != ["python"]:
        raise ValueError("FEF-P13 recompiled target must be Python")
    for key in [
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
    for packet in payload["reingestPackets"]:
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
    result_path = out_dir / f"fef_p13_c_rust_generated_target_reingest_{STAMP}.json"
    report_path = report_dir / f"fef_p13_c_rust_generated_target_reingest_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p13_c_rust_generated_target_reingest.json"
    feed_path = command_feed_dir / f"fef_p13_c_rust_generated_target_reingest_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["reingestPackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p13_c_rust_generated_target_reingest")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p13_generated_reingest_packets")
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
    print("FEF_P13_C_RUST_GENERATED_TARGET_REINGEST_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
