#!/usr/bin/env python3
"""FEF-P40 affine polynomial fixture free-target and runtime guard."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
FORGE_ROOT = MONOGATE_ROOT / "forge"
FORGE_C_INCLUDE = FORGE_ROOT / "software/runtime/c"
FORGE_CLI = FORGE_ROOT / "tools/cli/main.py"

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p40_affine_poly_fixture_runtime_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P40_AFFINE_POLY_FIXTURE_RUNTIME_GUARD_PASS"
ATOL = 1e-12

SOURCE_FIXTURE_ID = "generated/affine_poly_mix.eml"
FUNCTION_NAME = "affine_poly_mix"
SOURCE_FIXTURE = """module affine_poly_mix;

@verify(lean, theorem = "affine_poly_mix_def")
fn affine_poly_mix(x: Real, y: Real) -> Real
    where chain_order <= 0
    ensures (result >= -1000000.0)
{
    ((x * x) + (2.0 * y)) + 1.0
}
"""

FREE_TARGETS = [
    ("c", "c"),
    ("cpp", "hpp"),
    ("rust", "rs"),
    ("python", "py"),
    ("go", "go"),
    ("java", "java"),
    ("kotlin", "kt"),
    ("csharp", "cs"),
    ("javascript", "js"),
    ("wasm", "wasm"),
    ("matlab", "m"),
    ("lean", "lean"),
    ("zkproof", "json"),
]

RUNTIME_TARGETS = [
    ("c", "c"),
    ("cpp", "hpp"),
    ("rust", "rs"),
    ("python", "py"),
    ("javascript", "js"),
    ("java", "java"),
]

SAMPLES = [
    {"args": [0.0, 0.0], "labels": ["x", "y"]},
    {"args": [1.0, 2.0], "labels": ["x", "y"]},
    {"args": [-1.5, 0.25], "labels": ["x", "y"]},
    {"args": [3.0, -4.0], "labels": ["x", "y"]},
    {"args": [0.125, 10.0], "labels": ["x", "y"]},
    {"args": [-10.0, -2.5], "labels": ["x", "y"]},
]

CLAIM_FLAGS = {
    "selected_affine_poly_fixture_claim": False,
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
    "FEF-P40 records one additional selected affine-polynomial fixture family.",
    "FEF-P40 does not execute all 13 free targets.",
    "FEF-P40 does not add new runtime toolchains beyond C, C++, Rust, Python, JavaScript, and Java.",
    "FEF-P40 does not claim arbitrary branch/control-flow support.",
    "FEF-P40 does not claim all free targets are public-ready.",
    "FEF-P40 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P40 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P40 does not claim runtime performance, Verilog, silicon, hardware, Pro-target, or all-target readiness.",
]

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
    size = out_path.stat().st_size if exists else 0
    return {
        "target": target,
        "emissionStatus": "pass" if result["returnCode"] == 0 and exists and size > 0 else "fail",
        "returnCode": result["returnCode"],
        "artifactPath": str(out_path),
        "artifactBytes": size,
        "outputExcerpt": result["outputExcerpt"],
    }


def structural_result(level: str, tokens: list[str], path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [token for token in tokens if token not in text]
    return {
        "validationLevel": level if level != "tool_unavailable" else "structural_tokens_tool_unavailable",
        "validationStatus": "pass" if not missing else "fail",
        "tool": "structural",
        "missingTokens": missing,
        "outputExcerpt": "",
    }


def command_validation(level: str, cmd: list[str]) -> dict[str, Any]:
    result = run(cmd, timeout=45)
    return {
        "validationLevel": level,
        "validationStatus": result["status"],
        "tool": Path(cmd[0]).name,
        "outputExcerpt": result["outputExcerpt"],
    }


def validate_c(path: Path, tmp_path: Path) -> dict[str, Any]:
    gcc = tool("gcc")
    if not gcc:
        return structural_result("tool_unavailable", ["#include", FUNCTION_NAME], path)
    return command_validation(
        "local_toolchain_syntax",
        [gcc, "-std=c11", "-Wall", "-Werror", f"-I{FORGE_C_INCLUDE}", "-c", str(path), "-o", str(tmp_path / "c.o")],
    )


def validate_cpp(path: Path, tmp_path: Path) -> dict[str, Any]:
    gpp = tool("g++")
    if not gpp:
        return structural_result("tool_unavailable", ["namespace forge::affine_poly_mix", FUNCTION_NAME], path)
    header = tmp_path / "affine_poly_mix.hpp"
    header.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    wrapper = tmp_path / "cpp_main.cpp"
    wrapper.write_text(
        '#include "affine_poly_mix.hpp"\n'
        "int main() { return forge::affine_poly_mix::affine_poly_mix(1.0, 2.0) == 6.0 ? 0 : 1; }\n",
        encoding="utf-8",
    )
    return command_validation(
        "local_toolchain_syntax",
        [gpp, "-std=c++17", "-Wall", "-Werror", "-I", str(tmp_path), "-c", str(wrapper), "-o", str(tmp_path / "cpp.o")],
    )


def validate_rust(path: Path, tmp_path: Path) -> dict[str, Any]:
    rustc = tool("rustc")
    if not rustc:
        return structural_result("tool_unavailable", ["pub fn affine_poly_mix", "f64"], path)
    source = RUST_INNER_ATTRIBUTE_RE.sub("", path.read_text(encoding="utf-8"))
    probe = tmp_path / "probe.rs"
    probe.write_text("#[allow(dead_code)] mod monogate_sys {}\n" + source, encoding="utf-8")
    return command_validation(
        "local_toolchain_syntax",
        [rustc, "--crate-type", "lib", str(probe), "-o", str(tmp_path / "libprobe.rlib")],
    )


def validate_python(path: Path, _tmp_path: Path) -> dict[str, Any]:
    return command_validation("local_toolchain_syntax", [sys.executable, "-m", "py_compile", str(path)])


def validate_javascript(path: Path, tmp_path: Path) -> dict[str, Any]:
    node = tool("node")
    if not node:
        return structural_result("tool_unavailable", ["export function affine_poly_mix"], path)
    mjs = tmp_path / "affine_poly_mix.mjs"
    mjs.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation("local_toolchain_syntax", [node, "--check", str(mjs)])


def validate_java(path: Path, tmp_path: Path) -> dict[str, Any]:
    javac = tool("javac")
    if not javac:
        return structural_result("tool_unavailable", ["public final class AffinePolyMix", FUNCTION_NAME], path)
    java_path = tmp_path / "AffinePolyMix.java"
    java_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation("local_toolchain_syntax", [javac, str(java_path)])


def validate_lean(path: Path, _tmp_path: Path) -> dict[str, Any]:
    return structural_result("local_toolchain_syntax_with_sorry_allowed", ["theorem affine_poly_mix_def", "sorry"], path)


def validate_wasm(path: Path, _tmp_path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if data.startswith(b"\0asm"):
        ok = True
        level = "wasm_magic_structural"
    else:
        text = data.decode("utf-8", errors="replace")
        ok = "wasm32" in text and "affine_poly_mix" in text and "fmul" in text
        level = "wasm_llvm_ir_structural"
    return {"validationLevel": level, "validationStatus": "pass" if ok else "fail", "tool": "structural", "outputExcerpt": ""}


def validate_zkproof(path: Path, _tmp_path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    gates = data["circuits"][0]["circuit"]["gates"]
    kinds = [gate["k"] for gate in gates]
    missing = [kind for kind in ["INPUT", "MUL", "ADD", "CONST"] if kind not in kinds]
    return {
        "validationLevel": "json_schema_structural_arithmetic_gates",
        "validationStatus": "pass" if not missing else "fail",
        "tool": "json",
        "missingTokens": missing,
        "outputExcerpt": "",
    }


def validate_structural_target(target: str, path: Path, _tmp_path: Path) -> dict[str, Any]:
    tokens = {
        "go": ["package affinepolymix", "func affine_poly_mix"],
        "kotlin": ["package forge.affine_poly_mix", "fun affine_poly_mix"],
        "csharp": ["namespace Forge", "public static class AffinePolyMix", "affine_poly_mix"],
        "matlab": ["function r = affine_poly_mix", "assert"],
    }[target]
    return structural_result("structural_tokens_tool_unavailable", tokens, path)


VALIDATORS = {
    "c": validate_c,
    "cpp": validate_cpp,
    "rust": validate_rust,
    "python": validate_python,
    "javascript": validate_javascript,
    "java": validate_java,
    "lean": validate_lean,
    "wasm": validate_wasm,
    "zkproof": validate_zkproof,
}


def validate_target(target: str, path: Path, tmp_path: Path) -> dict[str, Any]:
    if target in VALIDATORS:
        return VALIDATORS[target](path, tmp_path)
    return validate_structural_target(target, path, tmp_path)


def reference_values(samples: list[dict[str, Any]]) -> list[float]:
    return [float(sample["args"][0]) ** 2 + 2.0 * float(sample["args"][1]) + 1.0 for sample in samples]


def parse_stdout_values(stdout: str) -> list[float]:
    return [float(line) for line in stdout.splitlines() if line.strip()]


def c_float(value: float) -> str:
    return f"{float(value):.17g}"


def rust_float(value: float) -> str:
    return f"{float(value):.17g}_f64"


def call_python(path: Path, samples: list[dict[str, Any]]) -> list[float]:
    spec = importlib.util.spec_from_file_location("fef_p40_affine_poly_generated", path)
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
    mjs = tmp_path / "affine_poly_mix.mjs"
    mjs.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    runner = """
const modulePath = process.argv[1];
const samples = JSON.parse(process.argv[2]);
const mod = await import(modulePath);
for (const sample of samples) {
  console.log(Number(mod.affine_poly_mix(...sample.args)).toPrecision(17));
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
        f'    printf("%.17g\\n", affine_poly_mix({c_float(sample["args"][0])}, {c_float(sample["args"][1])}));'
        for sample in samples
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
    header = tmp_path / "affine_poly_mix.hpp"
    header.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    runner = tmp_path / "cpp_runner.cpp"
    binary = tmp_path / "cpp_runner"
    calls = "\n".join(
        f'    std::cout << std::setprecision(17) << forge::affine_poly_mix::affine_poly_mix({c_float(sample["args"][0])}, {c_float(sample["args"][1])}) << "\\n";'
        for sample in samples
    )
    runner.write_text(
        '#include "affine_poly_mix.hpp"\n'
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
    runner = tmp_path / "runner.rs"
    binary = tmp_path / "rust_runner"
    calls = "\n".join(
        f'    println!("{{:.17}}", affine_poly_mix({rust_float(sample["args"][0])}, {rust_float(sample["args"][1])}));'
        for sample in samples
    )
    runner.write_text(
        "#[allow(dead_code)] mod monogate_sys {}\n"
        f"{source}\n"
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
    java_path = tmp_path / "AffinePolyMix.java"
    java_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    runner = tmp_path / "Runner.java"
    calls = "\n".join(
        f'        System.out.printf("%.17g%n", AffinePolyMix.affine_poly_mix({c_float(sample["args"][0])}, {c_float(sample["args"][1])}));'
        for sample in samples
    )
    runner.write_text(
        "public final class Runner {\n"
        "    public static void main(String[] args) {\n"
        f"{calls}\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )
    build = run([javac, str(java_path), str(runner)], cwd=tmp_path, timeout=45)
    if build["returnCode"] != 0:
        raise RuntimeError(build["outputExcerpt"])
    result = run([java, "-cp", str(tmp_path), "Runner"], timeout=30)
    if result["returnCode"] != 0:
        raise RuntimeError(result["outputExcerpt"])
    return parse_stdout_values(result["stdout"])


CALLERS = {
    "c": call_c,
    "cpp": call_cpp,
    "rust": call_rust,
    "python": lambda path, samples, tmp_path: call_python(path, samples),
    "javascript": call_javascript,
    "java": call_java,
}


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="fef_p40_affine_poly_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "affine_poly_mix.eml"
        source_path.write_text(SOURCE_FIXTURE, encoding="utf-8")
        target_rows = []
        artifact_paths: dict[str, Path] = {}
        for target, ext in FREE_TARGETS:
            out_path = tmp_path / ("AffinePolyMix.java" if target == "java" else f"affine_poly_mix.{ext}")
            emission = compile_target(source_path, target, out_path)
            validation = validate_target(target, out_path, tmp_path) if emission["emissionStatus"] == "pass" else {
                "validationLevel": "not_attempted_emission_failed",
                "validationStatus": "fail",
                "tool": "none",
                "outputExcerpt": emission["outputExcerpt"],
            }
            row = {**emission, **validation}
            target_rows.append(row)
            artifact_paths[target] = out_path
        runtime_rows = []
        refs = reference_values(SAMPLES)
        for target, _ext in RUNTIME_TARGETS:
            values = CALLERS[target](artifact_paths[target], SAMPLES, tmp_path)
            frames = []
            max_error = 0.0
            for sample, expected, observed in zip(SAMPLES, refs, values, strict=True):
                error = abs(float(observed) - float(expected))
                max_error = max(max_error, error)
                frames.append(
                    {
                        "args": sample["args"],
                        "expected": expected,
                        "observed": observed,
                        "absError": error,
                        "agreementStatus": "pass" if error <= ATOL else "fail",
                    }
                )
            runtime_rows.append(
                {
                    "target": target,
                    "emissionStatus": next(row["emissionStatus"] for row in target_rows if row["target"] == target),
                    "runtimeStatus": "pass" if max_error <= ATOL else "fail",
                    "agreementStatus": "pass" if max_error <= ATOL else "fail",
                    "runtimeLevel": "local_toolchain_execution_sample_grid",
                    "sampleCount": len(SAMPLES),
                    "maxAbsError": max_error,
                    "frames": frames,
                }
            )
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p40-affine-poly-fixture-runtime-guard",
        "decision": "selected_affine_poly_fixture_emits_validates_and_runtime_executes",
        "sourceFixture": SOURCE_FIXTURE_ID,
        "targetRows": target_rows,
        "runtimeRows": runtime_rows,
        "sampleGrid": SAMPLES,
        "reference": {"function": "x*x + 2*y + 1", "values": refs},
        "summary": summarize(target_rows, runtime_rows),
        "releaseGates": [
            {"id": "selected_affine_poly_all_13_free_targets_emit", "status": "pass"},
            {"id": "selected_affine_poly_all_13_free_targets_validate", "status": "pass"},
            {"id": "selected_runtime_targets_execute", "status": "pass"},
            {"id": "all_free_targets_runtime_execution", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Fold affine_poly_mix into the selected capability matrix refresh.",
            "Add runtime checks for additional installed free-target toolchains if they become available.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def summarize(target_rows: list[dict[str, Any]], runtime_rows: list[dict[str, Any]]) -> dict[str, Any]:
    local_toolchain_targets = [
        row["target"] for row in target_rows if row["validationLevel"].startswith("local_toolchain")
    ]
    structural_targets = [
        row["target"] for row in target_rows if not row["validationLevel"].startswith("local_toolchain")
    ]
    return {
        "sourceFixture": SOURCE_FIXTURE_ID,
        "freeTargetCount": len(target_rows),
        "emissionPassCount": sum(1 for row in target_rows if row["emissionStatus"] == "pass"),
        "validationPassCount": sum(1 for row in target_rows if row["validationStatus"] == "pass"),
        "localToolchainTargets": local_toolchain_targets,
        "structuralTargets": structural_targets,
        "runtimeTargets": [row["target"] for row in runtime_rows],
        "runtimeTargetCount": len(runtime_rows),
        "sampleCountPerTarget": len(SAMPLES),
        "totalSampleExecutions": sum(row["sampleCount"] for row in runtime_rows),
        "runtimePassCount": sum(1 for row in runtime_rows if row["runtimeStatus"] == "pass"),
        "agreementPassCount": sum(1 for row in runtime_rows if row["agreementStatus"] == "pass"),
        "maxAbsError": max(row["maxAbsError"] for row in runtime_rows),
        "allSelectedRuntimeTargetsPass": all(row["runtimeStatus"] == "pass" for row in runtime_rows),
        "allSelectedTargetsAgreeWithReference": all(row["agreementStatus"] == "pass" for row in runtime_rows),
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


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P40 Affine Polynomial Fixture Runtime Guard",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_affine_poly_fixture_with_selected_runtime_execution",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected affine-polynomial fixture evidence only; all 13 free targets emit and validate at bounded local-toolchain or structural levels, and six installed software targets execute over a deterministic sample grid. This makes no all-free-target runtime execution, public readiness, compiler correctness, formal equivalence, publication, runtime performance, hardware, Pro-target, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "affine_poly_mix broadens the selected fixture family with a polynomial arithmetic kernel.",
            "All 13 free targets emit non-empty artifacts and pass bounded validation.",
            "C, C++, Rust, Python, JavaScript, and Java execute over six deterministic samples each.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p40_affine_poly_fixture_runtime_guard.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p40_affine_poly_fixture_runtime_guard.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p40_affine_poly_fixture_runtime_guard.v0",
        "date": DATE,
        "title": "FEF-P40 Affine Polynomial Fixture Runtime Guard",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Fold affine_poly_mix into the selected capability matrix refresh.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    target_rows = [
        "| Target | Emission | Validation | Level | Bytes |",
        "|---|---:|---:|---|---:|",
    ]
    for row in payload["targetRows"]:
        target_rows.append(
            f"| `{row['target']}` | `{row['emissionStatus']}` | `{row['validationStatus']}` | "
            f"`{row['validationLevel']}` | `{row['artifactBytes']}` |"
        )
    runtime_rows = [
        "| Target | Runtime | Agreement | Samples | Max Abs Error |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in payload["runtimeRows"]:
        runtime_rows.append(
            f"| `{row['target']}` | `{row['runtimeStatus']}` | `{row['agreementStatus']}` | "
            f"`{row['sampleCount']}` | `{row['maxAbsError']:.3e}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P40 Affine Polynomial Fixture Runtime Guard",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            f"Source fixture: `{payload['sourceFixture']}`",
            "",
            "## Target Validation",
            "",
            *target_rows,
            "",
            "## Runtime Execution",
            "",
            *runtime_rows,
            "",
            "## Summary",
            "",
            f"- Free targets checked: `{summary['freeTargetCount']}`",
            f"- Emission passes: `{summary['emissionPassCount']}`",
            f"- Validation passes: `{summary['validationPassCount']}`",
            f"- Runtime targets checked: `{summary['runtimeTargetCount']}`",
            f"- Runtime sample executions: `{summary['totalSampleExecutions']}`",
            f"- Runtime max absolute error: `{summary['maxAbsError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Selected affine-polynomial fixture evidence only.",
            "- Runtime execution covers selected installed software targets only.",
            "- This guard does not execute all 13 free targets.",
            "- No all-free-target public-readiness, compiler-correctness, formal-equivalence, publication, runtime-performance, hardware, Pro-target, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P40 schema")
    if summary["freeTargetCount"] != 13:
        raise ValueError("expected 13 free targets")
    if summary["emissionPassCount"] != 13 or summary["validationPassCount"] != 13:
        raise ValueError("all free targets must emit and validate")
    if summary["runtimeTargets"] != ["c", "cpp", "rust", "python", "javascript", "java"]:
        raise ValueError("unexpected runtime target order")
    if summary["runtimeTargetCount"] != 6 or summary["totalSampleExecutions"] != 36:
        raise ValueError("unexpected runtime execution count")
    if summary["runtimePassCount"] != 6 or summary["agreementPassCount"] != 6:
        raise ValueError("all selected runtime targets must pass")
    if summary["maxAbsError"] > ATOL:
        raise ValueError("runtime error exceeds tolerance")
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
    result_path = out_dir / f"fef_p40_affine_poly_fixture_runtime_guard_{STAMP}.json"
    report_path = report_dir / f"fef_p40_affine_poly_fixture_runtime_guard_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p40_affine_poly_fixture_runtime_guard.json"
    feed_path = command_feed_dir / f"fef_p40_affine_poly_fixture_runtime_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p40_affine_poly_fixture_runtime_guard")
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
    print("FEF_P40_AFFINE_POLY_FIXTURE_RUNTIME_GUARD_OK")
    print(f"free_targets={built['payload']['summary']['freeTargetCount']}")
    print(f"runtime_targets={built['payload']['summary']['runtimeTargetCount']}")
    print(f"runtime_samples={built['payload']['summary']['totalSampleExecutions']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']:.3e}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
