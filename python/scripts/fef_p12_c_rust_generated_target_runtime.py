#!/usr/bin/env python3
"""FEF-P12 selected C/Rust generated-target local runtime guard."""

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
EFROG_ROOT = MONOGATE_ROOT / "efrog"
FORGE_ROOT = MONOGATE_ROOT / "forge"
FORGE_C_RUNTIME = FORGE_ROOT / "software/runtime/c/libmonogate.c"
FORGE_C_INCLUDE = FORGE_ROOT / "software/runtime/c"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))
if str(EFROG_ROOT) not in sys.path:
    sys.path.insert(0, str(EFROG_ROOT))

from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts.fef_p10_broader_generated_target_reingest import (  # noqa: E402
    ATOL,
    RTOL,
    CASES as FEF_P10_CASES,
    CLAIM_FLAGS as BASE_CLAIM_FLAGS,
    call_generated_python,
    compare_values,
    compile_target,
    decompile_source_case,
)

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p12_c_rust_generated_target_runtime.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p12_generated_runtime_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P12_C_RUST_GENERATED_TARGET_RUNTIME_PASS"

FEF_P11_PATH = ROOT / "reports/evidence_packets/fef_p11_per_target_validation_policy.json"

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "target_all_ready_claim": False,
    "c_target_public_ready": False,
    "rust_target_public_ready": False,
}

NON_CLAIMS = [
    "FEF-P12 records bounded local-runtime checks for selected generated C and Rust outputs.",
    "FEF-P12 compares generated C/Rust local-runtime outputs to generated Python reference outputs over deterministic samples.",
    "FEF-P12 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P12 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P12 does not claim runtime performance, Verilog, Lean proofs, zkproof, silicon, or hardware output.",
    "FEF-P12 does not claim all Forge targets are ready.",
]

SELECTED_CASE_IDS = [
    "python_stable_sigmoid_broader_reingest_v0",
    "python_voltage_divider_broader_reingest_v0",
    "javascript_circle_area_broader_reingest_v0",
    "c_gaussian_broader_reingest_v0",
    "rust_sigmoid_broader_reingest_v0",
]


def selected_cases() -> list[dict[str, Any]]:
    by_id = {case["caseId"]: case for case in FEF_P10_CASES}
    return [by_id[case_id] for case_id in SELECTED_CASE_IDS]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def float_literal(value: float, suffix: str = "") -> str:
    text = repr(float(value))
    if "e" not in text and "." not in text:
        text += ".0"
    return f"{text}{suffix}"


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"required local tool is unavailable: {name}")
    return path


RUST_RUNTIME_COMPAT = """
mod monogate_sys {
    pub fn mg_abs(x: f64) -> f64 { x.abs() }
    pub fn mg_acos(x: f64) -> f64 { x.acos() }
    pub fn mg_acosh(x: f64) -> f64 { x.acosh() }
    pub fn mg_asin(x: f64) -> f64 { x.asin() }
    pub fn mg_asinh(x: f64) -> f64 { x.asinh() }
    pub fn mg_atan(x: f64) -> f64 { x.atan() }
    pub fn mg_atanh(x: f64) -> f64 { x.atanh() }
    pub fn mg_ceil(x: f64) -> f64 { x.ceil() }
    pub fn mg_cos(x: f64) -> f64 { x.cos() }
    pub fn mg_cosh(x: f64) -> f64 { x.cosh() }
    pub fn mg_exp(x: f64) -> f64 { x.exp() }
    pub fn mg_floor(x: f64) -> f64 { x.floor() }
    pub fn mg_ln(x: f64) -> f64 { x.ln() }
    pub fn mg_log(x: f64) -> f64 { x.ln() }
    pub fn mg_log10(x: f64) -> f64 { x.log10() }
    pub fn mg_log2(x: f64) -> f64 { x.log2() }
    pub fn mg_clamp(x: f64, lo: f64, hi: f64) -> f64 { x.max(lo).min(hi) }
    pub fn mg_max(x: f64, y: f64) -> f64 { x.max(y) }
    pub fn mg_min(x: f64, y: f64) -> f64 { x.min(y) }
    pub fn mg_pow(x: f64, y: f64) -> f64 { x.powf(y) }
    pub fn mg_round(x: f64) -> f64 { x.round() }
    pub fn mg_sin(x: f64) -> f64 { x.sin() }
    pub fn mg_sinh(x: f64) -> f64 { x.sinh() }
    pub fn mg_sqrt(x: f64) -> f64 { x.sqrt() }
    pub fn mg_tan(x: f64) -> f64 { x.tan() }
    pub fn mg_tanh(x: f64) -> f64 { x.tanh() }
}
"""

RUST_INNER_ATTRIBUTE_RE = re.compile(r"^\s*#!\[[^\n]*\]\s*$", re.MULTILINE)


def call_generated_c(generated_path: Path, function_name: str, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    gcc = require_tool("gcc")
    work = tmp_path / f"{generated_path.stem}_c_runtime"
    work.mkdir(parents=True, exist_ok=True)
    main_path = work / "main.c"
    exe_path = work / "runner"
    calls = []
    for sample in samples:
        args = ", ".join(float_literal(arg) for arg in sample["args"])
        calls.append(f'    printf("%.17g\\n", {function_name}({args}));')
    main_path.write_text(
        "\n".join(
            [
                "#include <stdio.h>",
                f'#include "{generated_path.as_posix()}"',
                "int main(void) {",
                *calls,
                "    return 0;",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            gcc,
            "-O2",
            "-std=c11",
            "-Wall",
            "-Wno-unused-function",
            "-Wno-unused-variable",
            f"-I{FORGE_C_INCLUDE}",
            str(main_path),
            str(FORGE_C_RUNTIME),
            "-lm",
            "-o",
            str(exe_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    run = subprocess.run([str(exe_path)], capture_output=True, text=True, timeout=30, check=False)
    if run.returncode != 0:
        raise RuntimeError((run.stderr or run.stdout).strip())
    return [float(line) for line in run.stdout.splitlines() if line.strip()]


def call_generated_rust(generated_path: Path, function_name: str, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    cargo = require_tool("cargo")
    rustc = require_tool("rustc")
    work = tmp_path / f"{generated_path.stem}_rust_runtime"
    src = work / "src"
    src.mkdir(parents=True, exist_ok=True)
    (work / "Cargo.toml").write_text(
        "\n".join(
            [
                "[package]",
                'name = "fef_p12_target_runtime"',
                'version = "0.0.0"',
                'edition = "2021"',
                "",
                "[lib]",
                'name = "fef_p12_target_runtime"',
                'path = "src/lib.rs"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    generated_source = RUST_INNER_ATTRIBUTE_RE.sub("", generated_path.read_text(encoding="utf-8"))
    (src / "lib.rs").write_text(RUST_RUNTIME_COMPAT + "\n" + generated_source, encoding="utf-8")
    calls = []
    for sample in samples:
        args = ", ".join(float_literal(arg, "_f64") for arg in sample["args"])
        calls.append(f'    println!("{{:.17e}}", fef_p12_target_runtime::{function_name}({args}));')
    (src / "main.rs").write_text(
        "\n".join(
            [
                "fn main() {",
                *calls,
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [cargo, "run", "--quiet", "--release"],
        cwd=str(work),
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    _ = rustc
    return [float(line) for line in proc.stdout.splitlines() if line.strip()]


def compare_case_target(case: dict[str, Any], target: str, tmp_path: Path) -> dict[str, Any]:
    source_mod = decompile_source_case(case)
    source_eml = source_mod.to_eml()
    source_eml_path = tmp_path / f"{case['caseId']}_source.eml"
    source_eml_path.write_text(source_eml, encoding="utf-8")

    reference_path = tmp_path / f"{case['caseId']}_reference.py"
    compile_target(source_eml_path, "python", reference_path)
    target_ext = "c" if target == "c" else "rs"
    generated_path = tmp_path / f"{case['caseId']}_generated.{target_ext}"
    compile_target(source_eml_path, target, generated_path)

    samples = case["samples"]
    reference_values = call_generated_python(
        reference_path,
        case["functionName"],
        samples,
        f"{case['caseId']}_reference",
    )
    if target == "c":
        runtime_values = call_generated_c(generated_path, case["functionName"], samples, tmp_path)
    elif target == "rust":
        runtime_values = call_generated_rust(generated_path, case["functionName"], samples, tmp_path)
    else:
        raise ValueError(f"unsupported FEF-P12 target: {target}")

    frames, max_abs, max_rel = compare_values(runtime_values, reference_values, samples)
    for frame in frames:
        frame["values"] = {
            "generatedTargetRuntime": frame["values"]["generatedTarget"],
            "pythonReference": frame["values"]["reingestedRecompiledPython"],
        }

    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p12_generated_runtime_packet_v0",
        "date": DATE,
        "caseId": f"{case['caseId']}_{target}_runtime",
        "sourceCaseId": case["caseId"],
        "sourceLanguage": case["sourceLanguage"],
        "sourcePath": case["sourcePath"],
        "generatedTargetLanguage": target,
        "referenceTargetLanguage": "python",
        "functionName": case["functionName"],
        "sourceEmlHash": fingerprint_eml(source_eml),
        "sampleCount": len(samples),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "runtimeStatus": "pass" if max_abs <= ATOL or max_rel <= RTOL else "fail",
        "toolchain": {
            "gcc": shutil.which("gcc"),
            "cargo": shutil.which("cargo"),
            "rustc": shutil.which("rustc"),
        },
        "frames": frames,
        "missingEvidence": [
            "larger generated C/Rust runtime fixture family",
            "C/Rust generated-target decompilation and re-ingest path",
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
        "passCount": sum(1 for packet in packets if packet["runtimeStatus"] == "pass"),
        "failCount": sum(1 for packet in packets if packet["runtimeStatus"] == "fail"),
        "caseCount": len({packet["sourceCaseId"] for packet in packets}),
        "sampleCount": sum(packet["sampleCount"] for packet in packets),
        "sourceLanguages": sorted({packet["sourceLanguage"] for packet in packets}),
        "generatedTargetLanguages": sorted({packet["generatedTargetLanguage"] for packet in packets}),
        "referenceTargetLanguages": sorted({packet["referenceTargetLanguage"] for packet in packets}),
        "maxAbsError": max(packet["maxAbsError"] for packet in packets),
        "maxRelError": max(packet["maxRelError"] for packet in packets),
        "localGccAvailable": shutil.which("gcc") is not None,
        "localCargoAvailable": shutil.which("cargo") is not None,
        "localRustcAvailable": shutil.which("rustc") is not None,
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
    fef_p11 = read_json(FEF_P11_PATH)
    packets: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="fef_p12_c_rust_runtime_") as tmp:
        tmp_path = Path(tmp)
        for case in selected_cases():
            for target in ("c", "rust"):
                packets.append(compare_case_target(case, target, tmp_path))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p12-c-rust-generated-target-runtime",
        "decision": "selected_c_rust_generated_target_runtime_passed",
        "runtimePackets": packets,
        "summary": summarize(packets),
        "fefP11Link": {
            "path": str(FEF_P11_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p11["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_c_generated_target_runtime", "status": "pass"},
            {"id": "selected_rust_generated_target_runtime", "status": "pass"},
            {"id": "target_all_ready_claim", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Add selected C/Rust generated-target decompilation and re-ingest checks.",
            "Add structural or syntax-only validators for non-runtime target families where local tooling exists.",
            "Keep publication blocked unless an explicit release action is requested.",
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
        "title": "FEF-P12 C/Rust Generated-Target Runtime",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_c_rust_generated_target_local_runtime_sample_grid_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected generated C/Rust local-runtime sample-grid comparison only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, silicon, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selected generated C outputs compile with local gcc and Forge C runtime.",
            "Selected generated Rust outputs compile/run with local Cargo and a local compatibility shim for Forge runtime math calls.",
            "Generated C/Rust local-runtime outputs agree with generated Python reference outputs over deterministic samples.",
            "The selected source family includes Python, JavaScript, C, and Rust sources.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p12_c_rust_generated_target_runtime.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p12_c_rust_generated_target_runtime.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p12_c_rust_generated_target_runtime.v0",
        "date": DATE,
        "title": "FEF-P12 C/Rust Generated-Target Runtime",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add selected C/Rust generated-target decompilation and re-ingest checks.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Source | Generated target | Samples | Status | Max abs error | Max rel error |",
        "|---|---|---|---:|---|---:|---:|",
    ]
    for packet in payload["runtimePackets"]:
        rows.append(
            f"| `{packet['sourceCaseId']}` | `{packet['sourceLanguage']}` | `{packet['generatedTargetLanguage']}` | {packet['sampleCount']} | `{packet['runtimeStatus']}` | {packet['maxAbsError']:.3e} | {packet['maxRelError']:.3e} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P12 C/Rust Generated-Target Runtime",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P12 turns selected C and Rust generated targets from policy-defined evidence-open",
            "into bounded local-runtime sample-grid evidence.",
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
            "- Selected generated C/Rust local-runtime sample-grid comparison only.",
            "- Rust runtime execution uses a local compatibility shim for Forge runtime math calls to keep the guard offline-reproducible.",
            "- No package publication or checkout claim.",
            "- No all-target readiness, compiler correctness, or formal semantic equivalence claim.",
            "- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P12 packet schema")
    if packet["packetType"] != "fef_p12_generated_runtime_packet_v0":
        raise ValueError("invalid FEF-P12 packet type")
    if packet["generatedTargetLanguage"] not in {"c", "rust"}:
        raise ValueError("FEF-P12 generated target must be C or Rust")
    if packet["runtimeStatus"] != "pass":
        raise ValueError(f"{packet['caseId']} runtime did not pass")
    for frame in packet["frames"]:
        if frame["withinTolerance"] is not True:
            raise ValueError(f"{packet['caseId']} frame outside tolerance")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P12 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P12 status")
    summary = payload["summary"]
    if summary["caseCount"] != len(SELECTED_CASE_IDS):
        raise ValueError("unexpected FEF-P12 selected case count")
    if summary["packetCount"] != len(SELECTED_CASE_IDS) * 2:
        raise ValueError("unexpected FEF-P12 packet count")
    if summary["passCount"] != summary["packetCount"]:
        raise ValueError("all FEF-P12 runtime packets must pass")
    if summary["sourceLanguages"] != ["c", "javascript", "python", "rust"]:
        raise ValueError("FEF-P12 must cover C, JavaScript, Python, and Rust sources")
    if summary["generatedTargetLanguages"] != ["c", "rust"]:
        raise ValueError("FEF-P12 must cover C and Rust generated targets")
    if summary["referenceTargetLanguages"] != ["python"]:
        raise ValueError("FEF-P12 reference target must be Python")
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
    for packet in payload["runtimePackets"]:
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
    result_path = out_dir / f"fef_p12_c_rust_generated_target_runtime_{STAMP}.json"
    report_path = report_dir / f"fef_p12_c_rust_generated_target_runtime_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p12_c_rust_generated_target_runtime.json"
    feed_path = command_feed_dir / f"fef_p12_c_rust_generated_target_runtime_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["runtimePackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p12_c_rust_generated_target_runtime")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p12_generated_runtime_packets")
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
    print("FEF_P12_C_RUST_GENERATED_TARGET_RUNTIME_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
