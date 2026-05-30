#!/usr/bin/env python3
"""FEF-P6 broader original-runtime semantic comparison for C/Rust fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
FORGE_ROOT = MONOGATE_ROOT / "forge"
FORGE_CLI = FORGE_ROOT / "tools" / "cli" / "main.py"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))
if str(EFROG_ROOT) not in sys.path:
    sys.path.insert(0, str(EFROG_ROOT))

from efrog.decompilers.c import decompile_c_file  # noqa: E402
from efrog.decompilers.rust import decompile_rust_file  # noqa: E402
from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p6_broader_original_runtime_semantic_comparison.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p6_original_runtime_semantic_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P6_BROADER_ORIGINAL_RUNTIME_SEMANTIC_COMPARISON_PASS"
ATOL = 1.0e-9
RTOL = 1.0e-9

FEF_P5_PATH = ROOT / "reports/evidence_packets/fef_p5_publication_copy_review.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "proof_claim": False,
    "package_published": False,
    "public_compiler_package_available": False,
    "public_checkout_enabled": False,
    "verilog_claim": False,
    "lean_proof_claim": False,
    "zkproof_claim": False,
    "silicon_claim": False,
}

NON_CLAIMS = [
    "FEF-P6 records bounded original-runtime sample comparisons for selected C and Rust fixtures.",
    "FEF-P6 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P6 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P6 does not claim runtime performance, Verilog, Lean proofs, zkproof, silicon, or hardware output.",
    "MATLAB/Octave original-runtime comparison is recorded as unavailable when no local runtime is present.",
]

Case = dict[str, Any]
Decompiler = Callable[[str], Any]

CASES: list[Case] = [
    {
        "caseId": "c_gaussian_original_runtime_semantic_compare_v0",
        "sourceLanguage": "c",
        "sourcePath": "examples/gaussian.c",
        "functionName": "gaussian",
        "samples": [
            {"args": [0.0, 1.0, -1.0], "labels": ["mu", "sigma", "x"]},
            {"args": [0.5, 2.0, 1.5], "labels": ["mu", "sigma", "x"]},
            {"args": [-1.0, 0.75, 0.25], "labels": ["mu", "sigma", "x"]},
            {"args": [2.0, 3.0, -2.0], "labels": ["mu", "sigma", "x"]},
        ],
    },
    {
        "caseId": "c_circle_area_original_runtime_semantic_compare_v0",
        "sourceLanguage": "c",
        "sourcePath": "examples/circle_area.c",
        "functionName": "area",
        "samples": [{"args": [r], "labels": ["r"]} for r in [0.0, 0.5, 1.0, 2.5, 10.0]],
    },
    {
        "caseId": "rust_gaussian_original_runtime_semantic_compare_v0",
        "sourceLanguage": "rust",
        "sourcePath": "examples/gaussian.rs",
        "functionName": "gaussian",
        "samples": [
            {"args": [-1.0, 0.0, 1.0], "labels": ["x", "mu", "sigma"]},
            {"args": [1.5, 0.5, 2.0], "labels": ["x", "mu", "sigma"]},
            {"args": [0.25, -1.0, 0.75], "labels": ["x", "mu", "sigma"]},
            {"args": [-2.0, 2.0, 3.0], "labels": ["x", "mu", "sigma"]},
        ],
    },
    {
        "caseId": "rust_sigmoid_original_runtime_semantic_compare_v0",
        "sourceLanguage": "rust",
        "sourcePath": "examples/sigmoid.rs",
        "functionName": "sigmoid",
        "samples": [{"args": [x], "labels": ["x"]} for x in [-8.0, -2.0, 0.0, 2.0, 8.0]],
    },
    {
        "caseId": "rust_circle_area_original_runtime_semantic_compare_v0",
        "sourceLanguage": "rust",
        "sourcePath": "examples/circle_area.rs",
        "functionName": "area",
        "samples": [{"args": [r], "labels": ["r"]} for r in [0.0, 0.5, 1.0, 2.5, 10.0]],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_python_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compile_target(eml_path: Path, target: str, out_path: Path) -> str:
    proc = subprocess.run(
        [sys.executable, str(FORGE_CLI), str(eml_path), "--target", target, "-o", str(out_path)],
        cwd=str(FORGE_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    return (proc.stderr or proc.stdout).strip()


def call_generated_js(module_path: Path, function_name: str, samples: list[dict[str, Any]]) -> list[float]:
    runner = """
const mod = await import(process.argv[1]);
const samples = JSON.parse(process.argv[2]);
const fn = mod[process.argv[3]];
if (typeof fn !== 'function') throw new Error('missing function ' + process.argv[3]);
const out = samples.map(sample => Number(fn(...sample.args)));
if (out.some(value => !Number.isFinite(value))) throw new Error('non-finite generated output');
console.log(JSON.stringify(out));
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", runner, module_path.as_uri(), json.dumps(samples), function_name],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    return [float(value) for value in json.loads(proc.stdout)]


def call_original_c(source_path: Path, function_name: str, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    runner = tmp_path / f"{source_path.stem}_{function_name}_runner.c"
    binary = tmp_path / f"{source_path.stem}_{function_name}_runner"
    calls = "\n".join(
        f'    printf("%.17g\\n", {function_name}({", ".join(_c_float(v) for v in sample["args"])}));'
        for sample in samples
    )
    runner.write_text(
        "#include <stdio.h>\n"
        "#include <math.h>\n"
        f'#include "{source_path}"\n\n'
        "int main(void) {\n"
        f"{calls}\n"
        "    return 0;\n"
        "}\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["gcc", str(runner), "-lm", "-o", str(binary)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=30, check=False)
    if run.returncode != 0:
        raise RuntimeError((run.stderr or run.stdout).strip())
    return [float(line) for line in run.stdout.splitlines() if line.strip()]


def call_original_rust(source_path: Path, function_name: str, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    runner = tmp_path / f"{source_path.stem}_{function_name}_runner.rs"
    binary = tmp_path / f"{source_path.stem}_{function_name}_runner"
    calls = "\n".join(
        f'    println!("{{:.17e}}", {function_name}({", ".join(_rust_float(v) for v in sample["args"])}));'
        for sample in samples
    )
    runner.write_text(
        f'include!(r#"{source_path}"#);\n\n'
        "fn main() {\n"
        f"{calls}\n"
        "}\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["rustc", str(runner), "-o", str(binary)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=30, check=False)
    if run.returncode != 0:
        raise RuntimeError((run.stderr or run.stdout).strip())
    return [float(line) for line in run.stdout.splitlines() if line.strip()]


def _c_float(value: float) -> str:
    return f"{float(value):.17g}"


def _rust_float(value: float) -> str:
    return f"{float(value):.17g}_f64"


def rel_error(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), ATOL)


def decompile_case(case: Case):
    source_path = EFROG_ROOT / case["sourcePath"]
    if case["sourceLanguage"] == "c":
        return decompile_c_file(str(source_path))
    if case["sourceLanguage"] == "rust":
        return decompile_rust_file(str(source_path))
    raise ValueError(f"unsupported FEF-P6 source language: {case['sourceLanguage']}")


def call_original(case: Case, source_path: Path, tmp_path: Path) -> list[float]:
    if case["sourceLanguage"] == "c":
        return call_original_c(source_path, case["functionName"], case["samples"], tmp_path)
    if case["sourceLanguage"] == "rust":
        return call_original_rust(source_path, case["functionName"], case["samples"], tmp_path)
    raise ValueError(f"unsupported original runtime: {case['sourceLanguage']}")


def compare_case(case: Case, tmp_path: Path) -> dict[str, Any]:
    source_path = EFROG_ROOT / case["sourcePath"]
    mod = decompile_case(case)
    eml = mod.to_eml()
    eml_path = tmp_path / f"{case['caseId']}.eml"
    py_path = tmp_path / f"{case['caseId']}.py"
    js_path = tmp_path / f"{case['caseId']}.mjs"
    eml_path.write_text(eml, encoding="utf-8")
    compile_target(eml_path, "python", py_path)
    compile_target(eml_path, "javascript", js_path)

    samples = case["samples"]
    py_module = load_python_module(py_path)
    forge_py_fn = getattr(py_module, case["functionName"])
    original_values = call_original(case, source_path, tmp_path)
    python_values = [float(forge_py_fn(*sample["args"])) for sample in samples]
    javascript_values = call_generated_js(js_path, case["functionName"], samples)

    frames = []
    max_abs = 0.0
    max_rel = 0.0
    for index, sample in enumerate(samples):
        values = {
            "originalRuntime": original_values[index],
            "forgePython": python_values[index],
            "forgeJavaScript": javascript_values[index],
        }
        abs_errors = {
            "pythonVsOriginalRuntime": abs(values["forgePython"] - values["originalRuntime"]),
            "javascriptVsOriginalRuntime": abs(values["forgeJavaScript"] - values["originalRuntime"]),
            "javascriptVsPython": abs(values["forgeJavaScript"] - values["forgePython"]),
        }
        rel_errors = {
            "pythonVsOriginalRuntime": rel_error(values["forgePython"], values["originalRuntime"]),
            "javascriptVsOriginalRuntime": rel_error(values["forgeJavaScript"], values["originalRuntime"]),
            "javascriptVsPython": rel_error(values["forgeJavaScript"], values["forgePython"]),
        }
        max_abs = max(max_abs, *abs_errors.values())
        max_rel = max(max_rel, *rel_errors.values())
        frames.append(
            {
                "frameIndex": index,
                "sample": sample,
                "values": values,
                "absErrors": abs_errors,
                "relErrors": rel_errors,
                "withinTolerance": max(abs_errors.values()) <= ATOL or max(rel_errors.values()) <= RTOL,
            }
        )
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p6_original_runtime_semantic_packet_v0",
        "date": DATE,
        "caseId": case["caseId"],
        "sourceLanguage": case["sourceLanguage"],
        "sourcePath": case["sourcePath"],
        "functionName": case["functionName"],
        "targetLanguages": ["python", "javascript"],
        "canonicalEmlHash": fingerprint_eml(eml),
        "sampleCount": len(samples),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "comparisonStatus": "pass" if max_abs <= ATOL or max_rel <= RTOL else "fail",
        "frames": frames,
        "missingEvidence": [
            "MATLAB/Octave original-runtime semantic comparison",
            "compound-reassignment generated JavaScript comparison",
            "larger semantic sample grid",
            "formal compiler correctness proof",
            "public package publication decision",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_case_packet(packet)
    return packet


def toolchain_status() -> dict[str, Any]:
    return {
        "gcc": {"available": shutil.which("gcc") is not None, "path": shutil.which("gcc")},
        "rustc": {"available": shutil.which("rustc") is not None, "path": shutil.which("rustc")},
        "octave": {"available": shutil.which("octave") is not None, "path": shutil.which("octave")},
        "matlab": {"available": shutil.which("matlab") is not None, "path": shutil.which("matlab")},
    }


def unavailable_runtime_notes(tools: dict[str, Any]) -> list[dict[str, str]]:
    notes = []
    if not tools["octave"]["available"] and not tools["matlab"]["available"]:
        notes.append(
            {
                "sourceLanguage": "matlab",
                "status": "not_executed",
                "reason": "No local octave or matlab runtime found on PATH.",
            }
        )
    return notes


def summarize(case_packets: list[dict[str, Any]], tools: dict[str, Any]) -> dict[str, Any]:
    return {
        "caseCount": len(case_packets),
        "passCount": sum(1 for packet in case_packets if packet["comparisonStatus"] == "pass"),
        "failCount": sum(1 for packet in case_packets if packet["comparisonStatus"] == "fail"),
        "sampleCount": sum(packet["sampleCount"] for packet in case_packets),
        "sourceLanguages": sorted({packet["sourceLanguage"] for packet in case_packets}),
        "targetLanguages": ["python", "javascript"],
        "maxAbsError": max(packet["maxAbsError"] for packet in case_packets),
        "maxRelError": max(packet["maxRelError"] for packet in case_packets),
        "toolchains": tools,
        "unavailableOriginalRuntimes": unavailable_runtime_notes(tools),
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    fef_p5 = read_json(FEF_P5_PATH)
    tools = toolchain_status()
    if not tools["gcc"]["available"]:
        raise RuntimeError("FEF-P6 requires gcc for selected C original-runtime cases")
    if not tools["rustc"]["available"]:
        raise RuntimeError("FEF-P6 requires rustc for selected Rust original-runtime cases")
    with tempfile.TemporaryDirectory(prefix="fef_p6_original_runtime_") as tmp:
        tmp_path = Path(tmp)
        case_packets = [compare_case(case, tmp_path) for case in CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p6-broader-original-runtime-semantic-comparison",
        "decision": "c_rust_original_runtime_semantic_comparison_passed",
        "casePackets": case_packets,
        "summary": summarize(case_packets, tools),
        "fefP5Link": {
            "path": str(FEF_P5_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p5["reviewDecision"],
        },
        "releaseGates": [
            {"id": "c_original_runtime_comparison_passed", "status": "pass"},
            {"id": "rust_original_runtime_comparison_passed", "status": "pass"},
            {"id": "matlab_original_runtime_available", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Add MATLAB/Octave original-runtime comparison when a local runtime is available.",
            "Fix or gate compound-reassignment generated JavaScript before adding poly_horner cases.",
            "Build generated target re-ingest for Python/JavaScript outputs.",
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
        "title": "FEF-P6 Broader Original-Runtime Semantic Comparison",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "c_rust_original_runtime_sample_grid_semantic_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected C/Rust original-runtime sample-grid semantic comparison only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selected C fixtures execute through gcc-built original runners and compare against Forge Python/JavaScript outputs.",
            "Selected Rust fixtures execute through rustc-built original runners and compare against Forge Python/JavaScript outputs.",
            "MATLAB/Octave original-runtime comparison is recorded as unavailable because no local runtime is on PATH.",
            "Compound-reassignment poly_horner fixtures are left out because generated JavaScript rebind handling needs a separate guard.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p6_broader_original_runtime_semantic_comparison.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p6_broader_original_runtime_semantic_comparison.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p6_broader_original_runtime_semantic_comparison.v0",
        "date": DATE,
        "title": "FEF-P6 Broader Original-Runtime Semantic Comparison",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add MATLAB/Octave original-runtime comparison only when a local runtime is available.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Source | Samples | Status | Max abs error | Max rel error |",
        "|---|---|---:|---|---:|---:|",
    ]
    for packet in payload["casePackets"]:
        rows.append(
            f"| `{packet['caseId']}` | `{packet['sourceLanguage']}` | {packet['sampleCount']} | `{packet['comparisonStatus']}` | {packet['maxAbsError']:.3e} | {packet['maxRelError']:.3e} |"
        )
    summary = payload["summary"]
    lines = [
        "# FEF-P6 Broader Original-Runtime Semantic Comparison",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P6 executes selected C and Rust source fixtures through their local",
        "original runtimes, then compares those outputs with Forge Python and",
        "Forge JavaScript targets over fixed sample grids.",
        "",
        *rows,
        "",
        "## Summary",
        "",
        f"- Cases: `{summary['caseCount']}`",
        f"- Samples: `{summary['sampleCount']}`",
        f"- Passes: `{summary['passCount']}`",
        f"- Source languages: `{','.join(summary['sourceLanguages'])}`",
        f"- Max abs error: `{summary['maxAbsError']:.3e}`",
        f"- Max rel error: `{summary['maxRelError']:.3e}`",
        f"- MATLAB/Octave original runtime: `{summary['unavailableOriginalRuntimes'][0]['status'] if summary['unavailableOriginalRuntimes'] else 'available'}`",
        "",
        "## Boundary",
        "",
        "- C/Rust original-runtime sample-grid comparison only.",
        "- MATLAB/Octave was not executed because no local runtime is available.",
        "- No package publication or checkout claim.",
        "- No compiler correctness or formal semantic equivalence claim.",
        "- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
        "",
    ]
    return "\n".join(lines)


def validate_case_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P6 case packet schema")
    if packet["packetType"] != "fef_p6_original_runtime_semantic_packet_v0":
        raise ValueError("invalid FEF-P6 packet type")
    if packet["sourceLanguage"] not in {"c", "rust"}:
        raise ValueError("FEF-P6 currently supports C/Rust original-runtime cases")
    if packet["comparisonStatus"] != "pass":
        raise ValueError(f"{packet['caseId']} semantic comparison did not pass")
    if packet["sampleCount"] <= 0:
        raise ValueError("semantic packet needs samples")
    for frame in packet["frames"]:
        if frame["withinTolerance"] is not True:
            raise ValueError(f"{packet['caseId']} frame outside tolerance")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"case packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P6 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P6 status")
    summary = payload["summary"]
    if summary["caseCount"] < 5:
        raise ValueError("expected at least five C/Rust semantic comparison cases")
    if summary["passCount"] != summary["caseCount"]:
        raise ValueError("all semantic comparisons must pass")
    if summary["sourceLanguages"] != ["c", "rust"]:
        raise ValueError("FEF-P6 must cover C and Rust source runtimes")
    if summary["sampleCount"] < 20:
        raise ValueError("expected at least 20 sample frames")
    if not summary["unavailableOriginalRuntimes"]:
        raise ValueError("MATLAB/Octave availability status must be recorded")
    for key in [
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["casePackets"]:
        validate_case_packet(packet)


def build_outputs(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p6_broader_original_runtime_semantic_comparison_{STAMP}.json"
    report_path = report_dir / f"fef_p6_broader_original_runtime_semantic_comparison_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p6_broader_original_runtime_semantic_comparison.json"
    feed_path = command_feed_dir / f"fef_p6_broader_original_runtime_semantic_comparison_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["casePackets"]:
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/fef_p6_broader_original_runtime_semantic_comparison",
    )
    parser.add_argument(
        "--packet-dir",
        type=Path,
        default=ROOT / "python/results/fef_p6_original_runtime_semantic_packets",
    )
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
    print("FEF_P6_BROADER_ORIGINAL_RUNTIME_SEMANTIC_COMPARISON_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
