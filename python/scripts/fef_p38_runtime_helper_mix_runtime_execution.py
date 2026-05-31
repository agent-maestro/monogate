#!/usr/bin/env python3
"""FEF-P38 runtime execution guard for generated runtime_helper_mix targets."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p32_free_target_runtime_helper_guard as p32

MONOGATE_ROOT = ROOT.parent
FORGE_ROOT = MONOGATE_ROOT / "forge"
FORGE_C_INCLUDE = FORGE_ROOT / "software/runtime/c"
FORGE_CLI = FORGE_ROOT / "tools/cli/main.py"

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p38_runtime_helper_mix_runtime_execution.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P38_RUNTIME_HELPER_MIX_RUNTIME_EXECUTION_PASS"
ATOL = 1e-12

FEF_P37_PATH = ROOT / "reports/evidence_packets/fef_p37_verified_add_runtime_execution.json"
SOURCE_FIXTURE_ID = p32.SOURCE_FIXTURE_ID
FUNCTION_NAME = "runtime_helper_mix"
SAMPLES = [
    {"args": [0.0, 1.0, 0.0], "labels": ["x", "y", "z"]},
    {"args": [1.0, 2.0, 0.5], "labels": ["x", "y", "z"]},
    {"args": [-0.5, 0.25, -1.0], "labels": ["x", "y", "z"]},
    {"args": [0.25, 10.0, 3.0], "labels": ["x", "y", "z"]},
    {"args": [2.0, 4.0, -0.25], "labels": ["x", "y", "z"]},
]

RUNTIME_TARGETS = [
    ("c", "c"),
    ("cpp", "hpp"),
    ("rust", "rs"),
    ("python", "py"),
    ("javascript", "js"),
    ("java", "java"),
]

CLAIM_FLAGS = {
    "selected_runtime_execution_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_free_targets_public_ready_claim": False,
    "target_all_ready_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "package_published": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
}

NON_CLAIMS = [
    "FEF-P38 records runtime execution for installed toolchains over one selected runtime_helper_mix fixture.",
    "FEF-P38 does not execute all 13 free targets.",
    "FEF-P38 does not claim all free targets are public-ready.",
    "FEF-P38 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P38 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P38 does not claim runtime performance, Verilog, silicon, hardware, Pro-target, or all-target readiness.",
]

RUST_RUNTIME_COMPAT = """
#[allow(dead_code)]
mod monogate_sys {
    pub fn mg_exp(x: f64) -> f64 { x.exp() }
    pub fn mg_ln(x: f64) -> f64 { x.ln() }
    pub fn mg_sin(x: f64) -> f64 { x.sin() }
}
"""

RUST_INNER_ATTRIBUTE_RE = re.compile(r"^\s*#!\[[^\n]*\]\s*$", re.MULTILINE)


def tool(name: str) -> str | None:
    return shutil.which(name)


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 30) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return {
        "returnCode": proc.returncode,
        "status": "pass" if proc.returncode == 0 else "fail",
        "stdout": proc.stdout,
        "outputExcerpt": output[:900],
    }


def compile_target(source_path: Path, target: str, out_path: Path) -> dict[str, Any]:
    result = run(
        [sys.executable, str(FORGE_CLI), str(source_path), "--target", target, "-o", str(out_path)],
        cwd=FORGE_ROOT,
        timeout=45,
    )
    exists = out_path.exists()
    return {
        "target": target,
        "emissionStatus": "pass" if result["returnCode"] == 0 and exists and out_path.stat().st_size > 0 else "fail",
        "returnCode": result["returnCode"],
        "artifactPath": str(out_path),
        "artifactBytes": out_path.stat().st_size if exists else 0,
        "outputExcerpt": result["outputExcerpt"],
    }


def reference_values(samples: list[dict[str, Any]]) -> list[float]:
    return [
        math.exp(float(sample["args"][0])) + math.log(float(sample["args"][1])) + math.sin(float(sample["args"][2]))
        for sample in samples
    ]


def parse_stdout_values(stdout: str) -> list[float]:
    return [float(line) for line in stdout.splitlines() if line.strip()]


def c_float(value: float) -> str:
    return f"{float(value):.17g}"


def rust_float(value: float) -> str:
    return f"{float(value):.17g}_f64"


def call_python(path: Path, samples: list[dict[str, Any]]) -> list[float]:
    spec = importlib.util.spec_from_file_location("fef_p38_runtime_helper_generated", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load generated Python module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, FUNCTION_NAME)
    return [float(fn(*sample["args"])) for sample in samples]


def call_javascript(path: Path, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    node = tool("node")
    if not node:
        raise RuntimeError("node unavailable")
    mjs = tmp_path / "runtime_helper_mix.mjs"
    mjs.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    runner = """
const modulePath = process.argv[1];
const samples = JSON.parse(process.argv[2]);
const mod = await import(modulePath);
const fn = mod.runtime_helper_mix;
for (const sample of samples) {
  console.log(Number(fn(...sample.args)).toPrecision(17));
}
"""
    result = run([node, "--input-type=module", "-e", runner, mjs.as_uri(), json.dumps(samples)], timeout=30)
    if result["returnCode"] != 0:
        raise RuntimeError(result["outputExcerpt"])
    return parse_stdout_values(result["stdout"])


def call_c(path: Path, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    gcc = tool("gcc")
    if not gcc:
        raise RuntimeError("gcc unavailable")
    runner = tmp_path / "c_runner.c"
    binary = tmp_path / "c_runner"
    calls = "\n".join(
        f'    printf("%.17g\\n", runtime_helper_mix({c_float(s["args"][0])}, {c_float(s["args"][1])}, {c_float(s["args"][2])}));'
        for s in samples
    )
    runner.write_text(
        "#include <stdio.h>\n"
        "#include <math.h>\n"
        f'#include "{path}"\n\n'
        "int main(void) {\n"
        f"{calls}\n"
        "    return 0;\n"
        "}\n",
        encoding="utf-8",
    )
    build = run([gcc, "-std=c11", f"-I{FORGE_C_INCLUDE}", str(runner), "-lm", "-o", str(binary)], timeout=45)
    if build["returnCode"] != 0:
        raise RuntimeError(build["outputExcerpt"])
    result = run([str(binary)], timeout=30)
    if result["returnCode"] != 0:
        raise RuntimeError(result["outputExcerpt"])
    return parse_stdout_values(result["stdout"])


def call_cpp(path: Path, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    gpp = tool("g++")
    if not gpp:
        raise RuntimeError("g++ unavailable")
    header = tmp_path / "runtime_helper_mix.hpp"
    header.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    runner = tmp_path / "cpp_runner.cpp"
    binary = tmp_path / "cpp_runner"
    calls = "\n".join(
        f'    std::cout << std::setprecision(17) << forge::runtime_helper_mix::runtime_helper_mix({c_float(s["args"][0])}, {c_float(s["args"][1])}, {c_float(s["args"][2])}) << "\\n";'
        for s in samples
    )
    runner.write_text(
        '#include "runtime_helper_mix.hpp"\n'
        "#include <iomanip>\n"
        "#include <iostream>\n\n"
        "int main() {\n"
        f"{calls}\n"
        "    return 0;\n"
        "}\n",
        encoding="utf-8",
    )
    build = run([gpp, "-std=c++17", "-I", str(tmp_path), str(runner), "-o", str(binary)], timeout=45)
    if build["returnCode"] != 0:
        raise RuntimeError(build["outputExcerpt"])
    result = run([str(binary)], timeout=30)
    if result["returnCode"] != 0:
        raise RuntimeError(result["outputExcerpt"])
    return parse_stdout_values(result["stdout"])


def call_rust(path: Path, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    rustc = tool("rustc")
    if not rustc:
        raise RuntimeError("rustc unavailable")
    source = RUST_INNER_ATTRIBUTE_RE.sub("", path.read_text(encoding="utf-8"))
    generated = tmp_path / "generated.rs"
    generated.write_text(RUST_RUNTIME_COMPAT + "\n" + source, encoding="utf-8")
    runner = tmp_path / "rust_runner.rs"
    binary = tmp_path / "rust_runner"
    calls = "\n".join(
        f'    println!("{{:.17e}}", runtime_helper_mix({rust_float(s["args"][0])}, {rust_float(s["args"][1])}, {rust_float(s["args"][2])}));'
        for s in samples
    )
    runner.write_text(
        f'include!(r#"{generated}"#);\n\n'
        "fn main() {\n"
        f"{calls}\n"
        "}\n",
        encoding="utf-8",
    )
    build = run([rustc, str(runner), "-o", str(binary)], timeout=45)
    if build["returnCode"] != 0:
        raise RuntimeError(build["outputExcerpt"])
    result = run([str(binary)], timeout=30)
    if result["returnCode"] != 0:
        raise RuntimeError(result["outputExcerpt"])
    return parse_stdout_values(result["stdout"])


def call_java(path: Path, samples: list[dict[str, Any]], tmp_path: Path) -> list[float]:
    javac = tool("javac")
    java = tool("java")
    if not javac or not java:
        raise RuntimeError("javac/java unavailable")
    generated = tmp_path / "RuntimeHelperMix.java"
    generated.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    runner = tmp_path / "RuntimeHelperMixRunner.java"
    calls = "\n".join(
        f'        System.out.printf("%.17g%n", RuntimeHelperMix.runtime_helper_mix({c_float(s["args"][0])}, {c_float(s["args"][1])}, {c_float(s["args"][2])}));'
        for s in samples
    )
    runner.write_text(
        "public final class RuntimeHelperMixRunner {\n"
        "    public static void main(String[] args) {\n"
        f"{calls}\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )
    build = run([javac, str(generated), str(runner)], cwd=tmp_path, timeout=45)
    if build["returnCode"] != 0:
        raise RuntimeError(build["outputExcerpt"])
    result = run([java, "-cp", str(tmp_path), "RuntimeHelperMixRunner"], timeout=30)
    if result["returnCode"] != 0:
        raise RuntimeError(result["outputExcerpt"])
    return parse_stdout_values(result["stdout"])


def compare_values(target: str, observed: list[float], expected: list[float], samples: list[dict[str, Any]]) -> dict[str, Any]:
    frames = []
    max_abs = 0.0
    for index, (got, exp) in enumerate(zip(observed, expected)):
        abs_error = abs(got - exp)
        max_abs = max(max_abs, abs_error)
        frames.append({"index": index, "sample": samples[index], "expected": exp, "observed": got, "absError": abs_error})
    return {
        "target": target,
        "sampleCount": len(samples),
        "maxAbsError": max_abs,
        "agreementStatus": "pass" if len(observed) == len(expected) and max_abs <= ATOL else "fail",
        "frames": frames,
    }


def execute_target(target: str, path: Path, samples: list[dict[str, Any]], tmp_path: Path) -> dict[str, Any]:
    callers = {
        "c": call_c,
        "cpp": call_cpp,
        "rust": call_rust,
        "python": lambda p, s, _t: call_python(p, s),
        "javascript": call_javascript,
        "java": call_java,
    }
    try:
        observed = callers[target](path, samples, tmp_path)
        comparison = compare_values(target, observed, reference_values(samples), samples)
        return {
            "runtimeStatus": "pass" if comparison["agreementStatus"] == "pass" else "fail",
            "runtimeLevel": "local_toolchain_execution_sample_grid",
            "runtimeTool": target,
            **comparison,
            "outputExcerpt": "",
        }
    except Exception as exc:
        return {
            "target": target,
            "runtimeStatus": "fail",
            "runtimeLevel": "local_toolchain_execution_sample_grid",
            "runtimeTool": target,
            "sampleCount": len(samples),
            "maxAbsError": math.inf,
            "agreementStatus": "fail",
            "frames": [],
            "outputExcerpt": str(exc)[:900],
        }


def build_runtime_row(source_path: Path, target: str, ext: str, tmp_path: Path) -> dict[str, Any]:
    out_name = "RuntimeHelperMix.java" if target == "java" else f"runtime_helper_mix.{ext}"
    out_path = tmp_path / target / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emission = compile_target(source_path, target, out_path)
    runtime = execute_target(target, out_path, SAMPLES, out_path.parent) if emission["emissionStatus"] == "pass" else {
        "target": target,
        "runtimeStatus": "fail",
        "runtimeLevel": "not_attempted_emission_failed",
        "runtimeTool": target,
        "sampleCount": len(SAMPLES),
        "maxAbsError": math.inf,
        "agreementStatus": "fail",
        "frames": [],
        "outputExcerpt": emission["outputExcerpt"],
    }
    return {**emission, **runtime}


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourceFixture": SOURCE_FIXTURE_ID,
        "runtimeTargetCount": len(rows),
        "runtimeTargets": [row["target"] for row in rows],
        "sampleCountPerTarget": len(SAMPLES),
        "totalSampleExecutions": sum(row["sampleCount"] for row in rows),
        "emissionPassCount": sum(1 for row in rows if row["emissionStatus"] == "pass"),
        "runtimePassCount": sum(1 for row in rows if row["runtimeStatus"] == "pass"),
        "agreementPassCount": sum(1 for row in rows if row["agreementStatus"] == "pass"),
        "runtimeFailedTargets": [row["target"] for row in rows if row["runtimeStatus"] != "pass"],
        "maxAbsError": max(row["maxAbsError"] for row in rows),
        "allSelectedRuntimeTargetsPass": all(row["runtimeStatus"] == "pass" for row in rows),
        "allSelectedTargetsAgreeWithReference": all(row["agreementStatus"] == "pass" for row in rows),
        "allFreeTargetsRuntimeExecutionClaim": False,
        "allFreeTargetsPublicReadyClaim": False,
        "targetAllReadyClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


@lru_cache(maxsize=1)
def _build_payload_cached() -> dict[str, Any]:
    fef_p37 = json.loads(FEF_P37_PATH.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="fef_p38_runtime_helper_runtime_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "runtime_helper_mix.eml"
        source_path.write_text(p32.SOURCE_FIXTURE, encoding="utf-8")
        rows = [build_runtime_row(source_path, target, ext, tmp_path) for target, ext in RUNTIME_TARGETS]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p38-runtime-helper-mix-runtime-execution",
        "decision": "selected_runtime_helper_mix_generated_targets_execute_and_match_reference",
        "sourceFixture": SOURCE_FIXTURE_ID,
        "sampleGrid": SAMPLES,
        "reference": {"function": "exp(x) + ln(y) + sin(z)", "values": reference_values(SAMPLES)},
        "runtimeRows": rows,
        "summary": summarize(rows),
        "fefP37Link": {
            "path": str(FEF_P37_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p37["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_runtime_targets_emit", "status": "pass"},
            {"id": "selected_runtime_targets_execute", "status": "pass"},
            {"id": "selected_runtime_targets_match_reference", "status": "pass"},
            {"id": "all_free_targets_runtime_execution", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Fold runtime_helper_mix runtime execution rows into the selected capability matrix view.",
            "Add runtime execution checks for additional free targets when local toolchains are available.",
            "Keep public package publication blocked until explicit release action.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_payload() -> dict[str, Any]:
    return copy.deepcopy(_build_payload_cached())


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P38 Runtime Helper Mix Runtime Execution",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_generated_targets_runtime_sample_grid_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Runtime execution over installed local toolchains for one selected runtime_helper_mix fixture only; it compares generated C, C++, Rust, Python, JavaScript, and Java outputs to a deterministic reference grid and makes no all-free-target runtime execution, public readiness, compiler correctness, formal equivalence, publication, runtime performance, hardware, Pro-target, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Generated C, C++, Rust, Python, JavaScript, and Java runtime_helper_mix targets execute locally.",
            "All selected runtime targets match the exp/ln/sin reference over five domain-valid samples.",
            "Go, Kotlin, C#, MATLAB, wasm, Lean, and zkproof are not runtime-executed by this guard.",
            "The guard is selected runtime evidence only and does not publish or widen public preview claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p38_runtime_helper_mix_runtime_execution.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p38_runtime_helper_mix_runtime_execution.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p38_runtime_helper_mix_runtime_execution.v0",
        "date": DATE,
        "title": "FEF-P38 Runtime Helper Mix Runtime Execution",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Fold runtime_helper_mix runtime rows into the capability matrix.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = ["| Target | Emission | Runtime | Agreement | Samples | Max Abs Error |", "|---|---:|---:|---:|---:|---:|"]
    for row in payload["runtimeRows"]:
        rows.append(
            f"| `{row['target']}` | `{row['emissionStatus']}` | `{row['runtimeStatus']}` | "
            f"`{row['agreementStatus']}` | `{row['sampleCount']}` | `{row['maxAbsError']:.3e}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P38 Runtime Helper Mix Runtime Execution",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            f"Source fixture: `{payload['sourceFixture']}`",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Runtime targets checked: `{summary['runtimeTargetCount']}`",
            f"- Samples per target: `{summary['sampleCountPerTarget']}`",
            f"- Total sample executions: `{summary['totalSampleExecutions']}`",
            f"- Runtime passes: `{summary['runtimePassCount']}`",
            f"- Agreement passes: `{summary['agreementPassCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Selected generated-target runtime execution only.",
            "- This guard does not execute all 13 free targets.",
            "- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.",
            "- No runtime performance, package publication, checkout, hardware, Pro-target, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P38 schema")
    summary = payload["summary"]
    if summary["runtimeTargetCount"] != len(RUNTIME_TARGETS):
        raise ValueError("unexpected runtime target count")
    if summary["sampleCountPerTarget"] != len(SAMPLES):
        raise ValueError("unexpected sample count")
    if summary["emissionPassCount"] != len(RUNTIME_TARGETS):
        raise ValueError("all selected runtime targets must emit")
    if summary["runtimePassCount"] != len(RUNTIME_TARGETS):
        raise ValueError("all selected runtime targets must execute")
    if summary["agreementPassCount"] != len(RUNTIME_TARGETS):
        raise ValueError("all selected runtime targets must match reference")
    if summary["runtimeFailedTargets"]:
        raise ValueError("runtime failed targets must remain empty")
    if summary["maxAbsError"] > ATOL:
        raise ValueError("sample-grid error exceeds tolerance")
    for key in [
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsPublicReadyClaim",
        "targetAllReadyClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
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
    result_path = out_dir / f"fef_p38_runtime_helper_mix_runtime_execution_{STAMP}.json"
    report_path = report_dir / f"fef_p38_runtime_helper_mix_runtime_execution_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p38_runtime_helper_mix_runtime_execution.json"
    feed_path = command_feed_dir / f"fef_p38_runtime_helper_mix_runtime_execution_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p38_runtime_helper_mix_runtime_execution")
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
    print("FEF_P38_RUNTIME_HELPER_MIX_RUNTIME_EXECUTION_OK")
    print(f"runtime_targets={built['payload']['summary']['runtimeTargetCount']}")
    print(f"samples_per_target={built['payload']['summary']['sampleCountPerTarget']}")
    print(f"runtime_passes={built['payload']['summary']['runtimePassCount']}")
    print(f"agreement_passes={built['payload']['summary']['agreementPassCount']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']:.3e}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
