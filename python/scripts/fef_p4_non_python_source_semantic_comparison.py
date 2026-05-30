#!/usr/bin/env python3
"""FEF-P4 non-Python source semantic comparison packet."""

from __future__ import annotations

import argparse
import importlib.util
import json
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

from efrog.decompilers.javascript import decompile_javascript_file  # noqa: E402
from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p4_non_python_source_semantic_comparison.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p4_non_python_source_semantic_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P4_NON_PYTHON_SOURCE_SEMANTIC_COMPARISON_PASS"
ATOL = 1.0e-9
RTOL = 1.0e-9

FEF_P3_PATH = ROOT / "reports/evidence_packets/fef_p3_javascript_bridge_guard.json"

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
    "FEF-P4 records bounded non-Python source semantic sample comparisons.",
    "FEF-P4 uses selected JavaScript source fixtures only.",
    "FEF-P4 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P4 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P4 does not claim runtime performance, Verilog, Lean proofs, zkproof, or silicon output.",
]

CASES = [
    {
        "caseId": "javascript_gaussian_semantic_compare_v0",
        "sourceLanguage": "javascript",
        "sourcePath": "examples/gaussian.js",
        "functionName": "gaussian",
        "samples": [
            {"args": [-1.0, 0.0, 1.0], "labels": ["x", "mu", "sigma"]},
            {"args": [1.5, 0.5, 2.0], "labels": ["x", "mu", "sigma"]},
            {"args": [0.25, -1.0, 0.75], "labels": ["x", "mu", "sigma"]},
            {"args": [-2.0, 2.0, 3.0], "labels": ["x", "mu", "sigma"]},
        ],
    },
    {
        "caseId": "javascript_sigmoid_semantic_compare_v0",
        "sourceLanguage": "javascript",
        "sourcePath": "examples/sigmoid.js",
        "functionName": "sigmoid",
        "samples": [{"args": [x], "labels": ["x"]} for x in [-8.0, -2.0, 0.0, 2.0, 8.0]],
    },
    {
        "caseId": "javascript_circle_area_semantic_compare_v0",
        "sourceLanguage": "javascript",
        "sourcePath": "examples/circle_area.js",
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


def call_original_js(source_path: Path, function_name: str, samples: list[dict[str, Any]]) -> list[float]:
    runner = """
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const functionName = process.argv[2];
const samples = JSON.parse(process.argv[3]);
const context = { Math };
vm.createContext(context);
vm.runInContext(source, context);
const out = [];
for (const sample of samples) {
  context.__args = sample.args;
  const value = vm.runInContext(functionName + "(...__args)", context);
  if (!Number.isFinite(Number(value))) throw new Error('non-finite original output');
  out.push(Number(value));
}
console.log(JSON.stringify(out));
"""
    proc = subprocess.run(
        ["node", "-e", runner, str(source_path), function_name, json.dumps(samples)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    return [float(value) for value in json.loads(proc.stdout)]


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


def compare_case(case: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    source_path = EFROG_ROOT / case["sourcePath"]
    mod = decompile_javascript_file(str(source_path))
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
    original_values = call_original_js(source_path, case["functionName"], samples)
    python_values = [float(forge_py_fn(*sample["args"])) for sample in samples]
    javascript_values = call_generated_js(js_path, case["functionName"], samples)

    frames = []
    max_abs = 0.0
    max_rel = 0.0
    for index, sample in enumerate(samples):
        values = {
            "originalJavaScript": original_values[index],
            "forgePython": python_values[index],
            "forgeJavaScript": javascript_values[index],
        }
        abs_errors = {
            "pythonVsOriginalJavaScript": abs(values["forgePython"] - values["originalJavaScript"]),
            "javascriptVsOriginalJavaScript": abs(values["forgeJavaScript"] - values["originalJavaScript"]),
            "javascriptVsPython": abs(values["forgeJavaScript"] - values["forgePython"]),
        }
        rel_errors = {
            "pythonVsOriginalJavaScript": rel_error(values["forgePython"], values["originalJavaScript"]),
            "javascriptVsOriginalJavaScript": rel_error(values["forgeJavaScript"], values["originalJavaScript"]),
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
        "packetType": "fef_p4_non_python_source_semantic_packet_v0",
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
            "C/Rust/MATLAB original-runtime semantic comparison",
            "larger semantic sample grid",
            "formal compiler correctness proof",
            "public package publication decision",
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
        "sourceLanguages": sorted({packet["sourceLanguage"] for packet in case_packets}),
        "targetLanguages": ["python", "javascript"],
        "maxAbsError": max(packet["maxAbsError"] for packet in case_packets),
        "maxRelError": max(packet["maxRelError"] for packet in case_packets),
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    fef_p3 = read_json(FEF_P3_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p4_non_python_semantic_") as tmp:
        tmp_path = Path(tmp)
        case_packets = [compare_case(case, tmp_path) for case in CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p4-non-python-source-semantic-comparison",
        "decision": "javascript_source_semantic_comparison_passed",
        "casePackets": case_packets,
        "summary": summarize(case_packets),
        "fefP3Link": {
            "path": str(FEF_P3_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p3["reviewDecision"],
        },
        "releaseGates": [
            {"id": "non_python_source_runtime_comparison_passed", "status": "pass"},
            {"id": "javascript_source_to_forge_python_passed", "status": "pass"},
            {"id": "javascript_source_to_forge_javascript_passed", "status": "pass"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "FEF-P5 publication decision and public copy update only after claim review",
            "C/Rust/MATLAB original-runtime semantic comparison",
            "generated target re-ingest for Python/JavaScript outputs",
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
        "title": "FEF-P4 Non-Python Source Semantic Comparison",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "javascript_source_sample_grid_semantic_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected JavaScript-source sample-grid semantic comparison only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, or silicon claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Three JavaScript source fixtures execute under Node and compare against Forge Python and Forge JavaScript outputs.",
            "The comparison covers gaussian, sigmoid, and circle area fixtures over deterministic sample grids.",
            "This closes the first non-Python source semantic-comparison blocker while leaving broader language/runtime coverage open.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p4_non_python_source_semantic_comparison.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p4_non_python_source_semantic_comparison.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p4_non_python_source_semantic_comparison.v0",
        "date": DATE,
        "title": "FEF-P4 Non-Python Source Semantic Comparison",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run a publication/copy decision only after claim review, or expand original-runtime comparison to C/Rust/MATLAB.",
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
        "# FEF-P4 Non-Python Source Semantic Comparison",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P4 runs selected JavaScript source fixtures through eFrog and Forge,",
        "then compares original JavaScript runtime output with generated Python",
        "and JavaScript target outputs over fixed sample grids.",
        "",
        *rows,
        "",
        "## Summary",
        "",
        f"- Cases: `{summary['caseCount']}`",
        f"- Samples: `{summary['sampleCount']}`",
        f"- Passes: `{summary['passCount']}`",
        f"- Max abs error: `{summary['maxAbsError']:.3e}`",
        f"- Max rel error: `{summary['maxRelError']:.3e}`",
        "",
        "## Boundary",
        "",
        "- JavaScript-source sample-grid comparison only.",
        "- No package publication or checkout claim.",
        "- No compiler correctness or formal semantic equivalence claim.",
        "- No runtime performance, production, Verilog, Lean proof, zkproof, or silicon claim.",
        "",
    ]
    return "\n".join(lines)


def validate_case_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P4 case packet schema")
    if packet["packetType"] != "fef_p4_non_python_source_semantic_packet_v0":
        raise ValueError("invalid FEF-P4 packet type")
    if packet["sourceLanguage"] == "python":
        raise ValueError("FEF-P4 requires non-Python source cases")
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
        raise ValueError("invalid FEF-P4 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P4 status")
    summary = payload["summary"]
    if summary["caseCount"] < 3:
        raise ValueError("expected at least three non-Python semantic comparison cases")
    if summary["passCount"] != summary["caseCount"]:
        raise ValueError("all semantic comparisons must pass")
    if summary["sourceLanguages"] != ["javascript"]:
        raise ValueError("FEF-P4 currently records selected JavaScript source cases")
    if summary["sampleCount"] < 12:
        raise ValueError("expected at least 12 sample frames")
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
    result_path = out_dir / f"fef_p4_non_python_source_semantic_comparison_{STAMP}.json"
    report_path = report_dir / f"fef_p4_non_python_source_semantic_comparison_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p4_non_python_source_semantic_comparison.json"
    feed_path = command_feed_dir / f"fef_p4_non_python_source_semantic_comparison_feed_{STAMP}.json"
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
        default=ROOT / "python/results/fef_p4_non_python_source_semantic_comparison",
    )
    parser.add_argument(
        "--packet-dir",
        type=Path,
        default=ROOT / "python/results/fef_p4_non_python_source_semantic_packets",
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
    print("FEF_P4_NON_PYTHON_SOURCE_SEMANTIC_COMPARISON_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
