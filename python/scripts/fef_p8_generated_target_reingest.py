#!/usr/bin/env python3
"""FEF-P8 generated-target re-ingest guard for Python/JavaScript outputs."""

from __future__ import annotations

import argparse
import importlib.util
import json
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
from efrog.decompilers.javascript import decompile_javascript_file, decompile_javascript_source  # noqa: E402
from efrog.decompilers.python import decompile_python_source  # noqa: E402
from efrog.decompilers.rust import decompile_rust_file  # noqa: E402
from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p8_generated_target_reingest.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p8_reingest_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P8_GENERATED_TARGET_REINGEST_PASS"
ATOL = 1.0e-9
RTOL = 1.0e-9

FEF_P7_PATH = ROOT / "reports/evidence_packets/fef_p7_compound_reassignment_javascript_guard.json"

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
    "FEF-P8 records bounded generated-target re-ingest checks for selected Python/JavaScript outputs.",
    "FEF-P8 compares generated target runtime outputs to re-ingested-and-recompiled Python outputs over deterministic samples.",
    "FEF-P8 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P8 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P8 does not claim runtime performance, Verilog, Lean proofs, zkproof, silicon, or hardware output.",
]

Decompiler = Callable[[str], Any]

CASES: list[dict[str, Any]] = [
    {
        "caseId": "javascript_sigmoid_generated_target_reingest_v0",
        "sourceLanguage": "javascript",
        "sourcePath": "examples/sigmoid.js",
        "functionName": "sigmoid",
        "samples": [{"args": [x], "labels": ["x"]} for x in [-8.0, -2.0, 0.0, 2.0, 8.0]],
    },
    {
        "caseId": "c_poly_horner_generated_target_reingest_v0",
        "sourceLanguage": "c",
        "sourcePath": "examples/poly_horner.c",
        "functionName": "quad",
        "samples": [
            {"args": [2.0, 3.0, 5.0, 7.0], "labels": ["a", "b", "c", "x"]},
            {"args": [1.0, -2.0, 0.5, 3.0], "labels": ["a", "b", "c", "x"]},
            {"args": [-1.5, 4.0, -0.25, -2.0], "labels": ["a", "b", "c", "x"]},
            {"args": [0.125, 0.5, -1.0, 8.0], "labels": ["a", "b", "c", "x"]},
        ],
    },
    {
        "caseId": "rust_poly_horner_generated_target_reingest_v0",
        "sourceLanguage": "rust",
        "sourcePath": "examples/poly_horner.rs",
        "functionName": "quad",
        "samples": [
            {"args": [2.0, 3.0, 5.0, 7.0], "labels": ["a", "b", "c", "x"]},
            {"args": [1.0, -2.0, 0.5, 3.0], "labels": ["a", "b", "c", "x"]},
            {"args": [-1.5, 4.0, -0.25, -2.0], "labels": ["a", "b", "c", "x"]},
            {"args": [0.125, 0.5, -1.0, 8.0], "labels": ["a", "b", "c", "x"]},
        ],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_python_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
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


def call_generated_python(module_path: Path, function_name: str, samples: list[dict[str, Any]], module_name: str) -> list[float]:
    module = load_python_module(module_path, module_name)
    fn = getattr(module, function_name)
    return [float(fn(*sample["args"])) for sample in samples]


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


def rel_error(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), ATOL)


def decompile_source_case(case: dict[str, Any]):
    source_path = EFROG_ROOT / case["sourcePath"]
    if case["sourceLanguage"] == "javascript":
        return decompile_javascript_file(str(source_path))
    if case["sourceLanguage"] == "c":
        return decompile_c_file(str(source_path))
    if case["sourceLanguage"] == "rust":
        return decompile_rust_file(str(source_path))
    raise ValueError(f"unsupported FEF-P8 source language: {case['sourceLanguage']}")


def sanitize_generated_javascript(source: str) -> str:
    return source.replace("export function ", "function ")


def reingest_target(target: str, target_path: Path):
    source = target_path.read_text(encoding="utf-8")
    if target == "python":
        return decompile_python_source(source, source_path=str(target_path))
    if target == "javascript":
        return decompile_javascript_source(
            sanitize_generated_javascript(source),
            source_path=str(target_path),
        )
    raise ValueError(f"unsupported FEF-P8 target: {target}")


def compare_values(generated_values: list[float], reingested_values: list[float], samples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float, float]:
    frames = []
    max_abs = 0.0
    max_rel = 0.0
    for index, sample in enumerate(samples):
        generated = generated_values[index]
        reingested = reingested_values[index]
        abs_error = abs(reingested - generated)
        rel = rel_error(reingested, generated)
        max_abs = max(max_abs, abs_error)
        max_rel = max(max_rel, rel)
        frames.append(
            {
                "frameIndex": index,
                "sample": sample,
                "values": {
                    "generatedTarget": generated,
                    "reingestedRecompiledPython": reingested,
                },
                "absError": abs_error,
                "relError": rel,
                "withinTolerance": abs_error <= ATOL or rel <= RTOL,
            }
        )
    return frames, max_abs, max_rel


def compare_case_target(case: dict[str, Any], target: str, tmp_path: Path) -> dict[str, Any]:
    source_mod = decompile_source_case(case)
    source_eml = source_mod.to_eml()
    source_eml_path = tmp_path / f"{case['caseId']}_source.eml"
    source_eml_path.write_text(source_eml, encoding="utf-8")

    target_ext = "py" if target == "python" else "mjs"
    generated_path = tmp_path / f"{case['caseId']}_generated.{target_ext}"
    compile_target(source_eml_path, target, generated_path)

    reingested_mod = reingest_target(target, generated_path)
    reingested_eml = reingested_mod.to_eml()
    reingested_eml_path = tmp_path / f"{case['caseId']}_{target}_reingested.eml"
    reingested_py_path = tmp_path / f"{case['caseId']}_{target}_reingested.py"
    reingested_eml_path.write_text(reingested_eml, encoding="utf-8")
    compile_target(reingested_eml_path, "python", reingested_py_path)

    samples = case["samples"]
    if target == "python":
        generated_values = call_generated_python(generated_path, case["functionName"], samples, f"{case['caseId']}_generated")
    else:
        generated_values = call_generated_js(generated_path, case["functionName"], samples)
    reingested_values = call_generated_python(
        reingested_py_path,
        case["functionName"],
        samples,
        f"{case['caseId']}_{target}_reingested",
    )
    frames, max_abs, max_rel = compare_values(generated_values, reingested_values, samples)
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p8_reingest_packet_v0",
        "date": DATE,
        "caseId": f"{case['caseId']}_{target}",
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
        "missingEvidence": [
            "generated target re-ingest for power-expression cases that currently print `^` from eFrog Python/JavaScript decompilers",
            "larger generated-target fixture family",
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
        "sampleCount": sum(packet["sampleCount"] for packet in packets),
        "sourceLanguages": sorted({packet["sourceLanguage"] for packet in packets}),
        "generatedTargetLanguages": sorted({packet["generatedTargetLanguage"] for packet in packets}),
        "recompiledTargetLanguages": sorted({packet["recompiledTargetLanguage"] for packet in packets}),
        "maxAbsError": max(packet["maxAbsError"] for packet in packets),
        "maxRelError": max(packet["maxRelError"] for packet in packets),
        "heldOutGeneratedTargetShapes": [
            "power-expression generated Python/JavaScript re-ingest where eFrog emits `^`, which Forge reserves for unit expressions"
        ],
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    fef_p7 = read_json(FEF_P7_PATH)
    packets: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="fef_p8_reingest_") as tmp:
        tmp_path = Path(tmp)
        for case in CASES:
            for target in ("python", "javascript"):
                packets.append(compare_case_target(case, target, tmp_path))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p8-generated-target-reingest",
        "decision": "selected_generated_target_reingest_passed",
        "reingestPackets": packets,
        "summary": summarize(packets),
        "fefP7Link": {
            "path": str(FEF_P7_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p7["reviewDecision"],
        },
        "releaseGates": [
            {"id": "python_generated_target_reingest", "status": "pass"},
            {"id": "javascript_generated_target_reingest", "status": "pass"},
            {"id": "power_expression_generated_target_reingest", "status": "held_out"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Add a pow-spelling compatibility guard for generated target re-ingest.",
            "Broaden generated-target re-ingest fixtures after pow-spelling compatibility is handled.",
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
        "title": "FEF-P8 Generated-Target Re-ingest",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_generated_target_reingest_sample_grid_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected generated Python/JavaScript target re-ingest only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selected generated Python outputs re-ingest through eFrog Python and recompile to Python.",
            "Selected generated JavaScript outputs re-ingest through eFrog JavaScript and recompile to Python.",
            "Generated target outputs and re-ingested/recompiled Python outputs agree over deterministic samples for the selected cases.",
            "Power-expression generated-target re-ingest remains held out because eFrog currently prints `^`, which Forge reserves for unit expressions.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p8_generated_target_reingest.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p8_generated_target_reingest.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p8_generated_target_reingest.v0",
        "date": DATE,
        "title": "FEF-P8 Generated-Target Re-ingest",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add a pow-spelling compatibility guard for generated target re-ingest.",
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
            "# FEF-P8 Generated-Target Re-ingest",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P8 re-ingests selected generated Python and JavaScript outputs",
            "through eFrog, recompiles the re-ingested EML to Python, and compares",
            "those outputs against the generated target outputs over fixed samples.",
            "",
            *rows,
            "",
            "## Summary",
            "",
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
            "- Selected generated Python/JavaScript target re-ingest only.",
            "- Power-expression generated target re-ingest remains held out.",
            "- No package publication or checkout claim.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P8 packet schema")
    if packet["packetType"] != "fef_p8_reingest_packet_v0":
        raise ValueError("invalid FEF-P8 packet type")
    if packet["generatedTargetLanguage"] not in {"python", "javascript"}:
        raise ValueError("FEF-P8 generated target must be Python or JavaScript")
    if packet["reingestStatus"] != "pass":
        raise ValueError(f"{packet['caseId']} re-ingest did not pass")
    if packet["sampleCount"] <= 0:
        raise ValueError("re-ingest packet needs samples")
    for frame in packet["frames"]:
        if frame["withinTolerance"] is not True:
            raise ValueError(f"{packet['caseId']} frame outside tolerance")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P8 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P8 status")
    summary = payload["summary"]
    if summary["packetCount"] != 6:
        raise ValueError("expected six generated-target re-ingest packets")
    if summary["passCount"] != summary["packetCount"]:
        raise ValueError("all generated-target re-ingest packets must pass")
    if summary["generatedTargetLanguages"] != ["javascript", "python"]:
        raise ValueError("FEF-P8 must cover Python and JavaScript generated targets")
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
    result_path = out_dir / f"fef_p8_generated_target_reingest_{STAMP}.json"
    report_path = report_dir / f"fef_p8_generated_target_reingest_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p8_generated_target_reingest.json"
    feed_path = command_feed_dir / f"fef_p8_generated_target_reingest_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p8_generated_target_reingest")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p8_reingest_packets")
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
    print("FEF_P8_GENERATED_TARGET_REINGEST_OK")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
