#!/usr/bin/env python3
"""EML-A13.2 semantic output comparison for selected Forge/eFrog kernels.

Compiles selected Python-source kernels through eFrog -> EML -> Forge Python
and JavaScript, executes fixed sample grids, and compares target outputs with
the original source. This is executable sample evidence only; it is not a
compiler-correctness proof or formal equivalence claim.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
FORGE_ROOT = MONOGATE_ROOT / "forge"
FORGE_CLI = FORGE_ROOT / "tools" / "cli" / "main.py"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))
if str(EFROG_ROOT) not in sys.path:
    sys.path.insert(0, str(EFROG_ROOT))

from efrog.decompilers.python import decompile_python_file  # noqa: E402
from efrog.fingerprint import fingerprint_eml  # noqa: E402
from efrog.verify import _load_callables_from_source  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_a13_2_semantic_output_comparison.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_forge_efrog_semantic_comparison_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A13_2_SEMANTIC_OUTPUT_COMPARISON_PASS"
ATOL = 1.0e-9
RTOL = 1.0e-9

CLAIM_FLAGS = {
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "production_toolchain_claim": False,
    "proof_claim": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "A13.2 records bounded sample-grid semantic comparisons only.",
    "A13.2 does not change Forge or eFrog behavior.",
    "A13.2 does not prove compiler correctness or formal semantic equivalence.",
    "A13.2 does not claim broad EML advantage, runtime performance, production readiness, or public safety.",
]

CASES = [
    {
        "caseId": "gaussian_semantic_compare_v0",
        "sourcePath": "examples/gaussian.py",
        "functionName": "gaussian",
        "samples": [
            {"mu": 0.0, "sigma": 1.0, "x": -1.0},
            {"mu": 0.5, "sigma": 2.0, "x": 1.5},
            {"mu": -1.0, "sigma": 0.75, "x": 0.25},
            {"mu": 2.0, "sigma": 3.0, "x": -2.0},
        ],
    },
    {
        "caseId": "sigmoid_semantic_compare_v0",
        "sourcePath": "examples/sigmoid.py",
        "functionName": "sigmoid",
        "samples": [{"x": x} for x in [-8.0, -2.0, 0.0, 2.0, 8.0]],
    },
    {
        "caseId": "poly_quadratic_semantic_compare_v0",
        "sourcePath": "examples/poly_quadratic.py",
        "functionName": "poly_quadratic",
        "samples": [
            {"x": -2.0, "c0": 1.0, "c1": -0.5, "c2": 2.0},
            {"x": 0.0, "c0": -1.0, "c1": 3.0, "c2": 0.25},
            {"x": 1.5, "c0": 0.5, "c1": 1.25, "c2": -0.75},
            {"x": 3.0, "c0": 2.0, "c1": -1.0, "c2": 0.1},
        ],
    },
    {
        "caseId": "gaussian_stable_holdout_semantic_compare_v0",
        "sourcePath": "examples/gaussian_stable.py",
        "functionName": "gaussian_stable",
        "samples": [
            {"mu": 0.0, "sigma": 1.0, "x": 0.0},
            {"mu": 1.0, "sigma": 2.5, "x": -1.0},
            {"mu": -2.0, "sigma": 0.8, "x": 1.0},
            {"mu": 0.25, "sigma": 4.0, "x": 3.0},
        ],
    },
    {
        "caseId": "rc_decay_holdout_semantic_compare_v0",
        "sourcePath": "examples/rc_decay_stable.py",
        "functionName": "rc_decay_stable",
        "samples": [
            {"v0": 1.0, "tau": 0.5, "t": 0.0},
            {"v0": 5.0, "tau": 2.0, "t": 1.0},
            {"v0": -3.0, "tau": 1.25, "t": 4.0},
            {"v0": 10.0, "tau": 5.0, "t": 8.0},
        ],
    },
    {
        "caseId": "stretched_exponential_holdout_semantic_compare_v0",
        "sourcePath": "examples/stretched_exponential.py",
        "functionName": "stretched_exponential",
        "samples": [
            {"amplitude": 1.0, "scale": 1.0, "shape": 0.75, "t": 0.0},
            {"amplitude": 2.0, "scale": 3.0, "shape": 1.5, "t": 4.0},
            {"amplitude": 0.5, "scale": 0.75, "shape": 2.5, "t": 1.25},
            {"amplitude": 1.0, "scale": 0.0, "shape": 1.0, "t": 1.0},
            {"amplitude": 1.0, "scale": 1.0, "shape": 0.5, "t": -1.0},
        ],
    },
    {
        "caseId": "voltage_divider_holdout_semantic_compare_v0",
        "sourcePath": "examples/voltage_divider.py",
        "functionName": "voltage_divider",
        "samples": [
            {"vin": 5.0, "r_top": 1000.0, "r_bottom": 1000.0},
            {"vin": 3.3, "r_top": 2200.0, "r_bottom": 4700.0},
            {"vin": 12.0, "r_top": 10000.0, "r_bottom": 2000.0},
            {"vin": -5.0, "r_top": 330.0, "r_bottom": 680.0},
        ],
    },
]


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


def call_js(module_path: Path, function_name: str, samples: list[dict[str, float]]) -> list[float]:
    runner = f"""
const mod = await import(process.argv[1]);
const samples = JSON.parse(process.argv[2]);
const fn = mod[process.argv[3]];
if (typeof fn !== 'function') throw new Error('missing function ' + process.argv[3]);
const out = samples.map(sample => fn(...Object.values(sample)));
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


def compare_case(case: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    source_path = EFROG_ROOT / case["sourcePath"]
    source = source_path.read_text(encoding="utf-8")
    mod = decompile_python_file(str(source_path))
    eml = mod.to_eml()
    eml_path = tmp_path / f"{case['caseId']}.eml"
    py_path = tmp_path / f"{case['caseId']}.py"
    js_path = tmp_path / f"{case['caseId']}.mjs"
    eml_path.write_text(eml, encoding="utf-8")
    compile_target(eml_path, "python", py_path)
    compile_target(eml_path, "javascript", js_path)

    original_funcs = _load_callables_from_source(source, namespace=f"{case['caseId']}_orig")
    py_module = load_python_module(py_path)
    original_fn = original_funcs[case["functionName"]]
    forge_py_fn = getattr(py_module, case["functionName"])
    samples = case["samples"]
    original_values = [float(original_fn(**sample)) for sample in samples]
    python_values = [float(forge_py_fn(**sample)) for sample in samples]
    javascript_values = call_js(js_path, case["functionName"], samples)

    frames = []
    max_abs = 0.0
    max_rel = 0.0
    for index, sample in enumerate(samples):
        values = {
            "original": original_values[index],
            "forgePython": python_values[index],
            "forgeJavaScript": javascript_values[index],
        }
        abs_errors = {
            "pythonVsOriginal": abs(values["forgePython"] - values["original"]),
            "javascriptVsOriginal": abs(values["forgeJavaScript"] - values["original"]),
            "javascriptVsPython": abs(values["forgeJavaScript"] - values["forgePython"]),
        }
        rel_errors = {
            "pythonVsOriginal": rel_error(values["forgePython"], values["original"]),
            "javascriptVsOriginal": rel_error(values["forgeJavaScript"], values["original"]),
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
        "packetType": "eml_forge_efrog_semantic_comparison_packet_v0",
        "date": DATE,
        "caseId": case["caseId"],
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
            "larger semantic sample grid",
            "non-Python source semantic comparison",
            "formal compiler correctness proof",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_case_packet(packet)
    return packet


def summarize(case_packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "caseCount": len(case_packets),
        "passCount": sum(1 for packet in case_packets if packet["comparisonStatus"] == "pass"),
        "failCount": sum(1 for packet in case_packets if packet["comparisonStatus"] == "fail"),
        "sampleCount": sum(packet["sampleCount"] for packet in case_packets),
        "targetLanguages": ["python", "javascript"],
        "maxAbsError": max(packet["maxAbsError"] for packet in case_packets),
        "maxRelError": max(packet["maxRelError"] for packet in case_packets),
        "forgeBehaviorChanged": False,
        "efrogBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "broadEmlAdvantageClaim": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a13-2-semantic-output-comparison",
        "title": "EML-A13.2 Semantic Output Comparison",
        "reviewDecision": "private_semantic_sample_evidence_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_sample_grid_target_comparison",
        "semanticStrength": "sample_grid_semantic_agreement_no_compiler_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private sample-grid semantic comparison only; no compiler correctness, formal equivalence, broad EML advantage, runtime performance, production readiness, or public safety claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a13_2_semantic_output_comparison.v0",
        "date": DATE,
        "title": "EML-A13.2 Semantic Output Comparison",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A13.3 add non-Python source semantic comparison or generated target re-ingest",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Samples | Status | Max abs error | Max rel error |",
        "|---|---:|---|---:|---:|",
    ]
    for packet in payload["casePackets"]:
        rows.append(
            f"| `{packet['caseId']}` | {packet['sampleCount']} | `{packet['comparisonStatus']}` | {packet['maxAbsError']:.3e} | {packet['maxRelError']:.3e} |"
        )
    return "\n".join(
        [
            "# EML-A13.2 Semantic Output Comparison",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            "A13.2 executes selected Python-source kernels after eFrog decompilation",
            "and Forge Python/JavaScript emission, then compares fixed sample grids.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Cases: `{payload['summary']['caseCount']}`",
            f"- Samples: `{payload['summary']['sampleCount']}`",
            f"- Passes: `{payload['summary']['passCount']}`",
            f"- Max abs error: `{payload['summary']['maxAbsError']:.3e}`",
            f"- Max rel error: `{payload['summary']['maxRelError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Sample-grid semantic comparison only.",
            "- No Forge or eFrog behavior change.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No broad EML advantage, runtime performance, production readiness, or public safety claim.",
            "",
        ]
    )


def validate_case_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid A13.2 case packet schema")
    if packet["packetType"] != "eml_forge_efrog_semantic_comparison_packet_v0":
        raise ValueError("invalid A13.2 packet type")
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
        raise ValueError("invalid A13.2 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid A13.2 status")
    summary = payload["summary"]
    if summary["caseCount"] < 6:
        raise ValueError("expected at least six semantic comparison cases")
    if summary["passCount"] != summary["caseCount"]:
        raise ValueError("all semantic comparisons must pass")
    if summary["sampleCount"] < 20:
        raise ValueError("expected at least 20 sample frames")
    for key in [
        "forgeBehaviorChanged",
        "efrogBehaviorChanged",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "broadEmlAdvantageClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for packet in payload["casePackets"]:
        validate_case_packet(packet)


def build_lab(
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eml_a13_2_semantic_") as tmp:
        tmp_path = Path(tmp)
        case_packets = [compare_case(case, tmp_path) for case in CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "labId": "eml_a13_2_semantic_output_comparison",
        "casePackets": case_packets,
        "summary": summarize(case_packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_a13_2_semantic_output_comparison_{STAMP}.json"
    report_path = report_dir / f"eml_a13_2_semantic_output_comparison_{STAMP}.md"
    evidence_path = evidence_dir / "eml_a13_2_semantic_output_comparison.json"
    feed_path = command_feed_dir / f"eml_a13_2_semantic_output_comparison_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in case_packets:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a13_2_semantic_output_comparison")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_forge_efrog_semantic_comparison_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_lab(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A13_2_SEMANTIC_OUTPUT_COMPARISON_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
