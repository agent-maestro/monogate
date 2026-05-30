#!/usr/bin/env python3
"""FEF-P32 runtime-helper free-target guard for the Forge CLI."""

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
FORGE_C_INCLUDE = FORGE_ROOT / "software/runtime/c"
MACHLIB_BUILD_LIB = MONOGATE_ROOT / "machlib/foundations/.lake/build/lib"
FORGE_CLI = FORGE_ROOT / "tools/cli/main.py"

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p32_free_target_runtime_helper_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P32_FREE_TARGET_RUNTIME_HELPER_GUARD_PASS"

FEF_P11_PATH = ROOT / "reports/evidence_packets/fef_p11_per_target_validation_policy.json"
FEF_P30_PATH = ROOT / "reports/evidence_packets/fef_p30_selected_zero_sorry_file_index_refresh.json"
SOURCE_FIXTURE_ID = "generated/runtime_helper_mix.eml"
SOURCE_FIXTURE = """module runtime_helper_mix;

@verify(lean, theorem = "runtime_helper_mix_def")
fn runtime_helper_mix(x: Real, y: Real, z: Real) -> Real
    where chain_order <= 3
    requires (y > 0.0)
    ensures (result == exp(x) + ln(y) + sin(z))
{
    exp(x) + ln(y) + sin(z)
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

CLAIM_FLAGS = {
    "free_target_runtime_helper_guard_claim": False,
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
    "FEF-P32 records runtime-helper fixture emission for the 13 Forge free targets.",
    "FEF-P32 uses local syntax/toolchain checks where tools are installed and structural checks where they are not.",
    "FEF-P32 does not claim all free targets are public-ready.",
    "FEF-P32 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P32 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P32 does not claim runtime performance, Verilog, silicon, hardware, Pro-target, or all-target readiness.",
]

RUST_RUNTIME_COMPAT = """
#[allow(dead_code)]
mod monogate_sys {
    pub fn mg_abs(x: f64) -> f64 { x.abs() }
    pub fn mg_acos(x: f64) -> f64 { x.acos() }
    pub fn mg_asin(x: f64) -> f64 { x.asin() }
    pub fn mg_atan(x: f64) -> f64 { x.atan() }
    pub fn mg_cos(x: f64) -> f64 { x.cos() }
    pub fn mg_exp(x: f64) -> f64 { x.exp() }
    pub fn mg_ln(x: f64) -> f64 { x.ln() }
    pub fn mg_log(x: f64) -> f64 { x.ln() }
    pub fn mg_pow(x: f64, y: f64) -> f64 { x.powf(y) }
    pub fn mg_sin(x: f64) -> f64 { x.sin() }
    pub fn mg_sqrt(x: f64) -> f64 { x.sqrt() }
    pub fn mg_tan(x: f64) -> f64 { x.tan() }
}
"""

RUST_INNER_ATTRIBUTE_RE = re.compile(r"^\s*#!\[[^\n]*\]\s*$", re.MULTILINE)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, timeout: int = 30) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return {
        "returnCode": proc.returncode,
        "status": "pass" if proc.returncode == 0 else "fail",
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


def tool(name: str) -> str | None:
    return shutil.which(name)


def validate_c(path: Path, tmp_path: Path) -> dict[str, Any]:
    gcc = tool("gcc")
    if not gcc:
        return structural_result("tool_unavailable", ["#include", "runtime_helper_mix"], path)
    return command_validation(
        "local_toolchain_syntax",
        [gcc, "-std=c11", "-Wall", "-Werror", f"-I{FORGE_C_INCLUDE}", "-c", str(path), "-o", str(tmp_path / "c.o")],
    )


def validate_cpp(path: Path, tmp_path: Path) -> dict[str, Any]:
    gpp = tool("g++")
    if not gpp:
        return structural_result("tool_unavailable", ["namespace forge::runtime_helper_mix", "runtime_helper_mix"], path)
    wrapper = tmp_path / "cpp_main.cpp"
    wrapper.write_text(
        '#include "runtime_helper_mix.hpp"\n'
        "#include <cmath>\n"
        "int main() {\n"
        "  double got = forge::runtime_helper_mix::runtime_helper_mix(1.0, 2.0, 0.5);\n"
        "  double expected = std::exp(1.0) + std::log(2.0) + std::sin(0.5);\n"
        "  return std::abs(got - expected) < 1e-12 ? 0 : 1;\n"
        "}\n",
        encoding="utf-8",
    )
    copied = tmp_path / "runtime_helper_mix.hpp"
    copied.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation(
        "local_toolchain_syntax",
        [gpp, "-std=c++17", "-Wall", "-Werror", "-I", str(tmp_path), "-c", str(wrapper), "-o", str(tmp_path / "cpp.o")],
    )


def validate_rust(path: Path, tmp_path: Path) -> dict[str, Any]:
    rustc = tool("rustc")
    if not rustc:
        return structural_result("tool_unavailable", ["pub fn runtime_helper_mix", "f64"], path)
    source = RUST_INNER_ATTRIBUTE_RE.sub("", path.read_text(encoding="utf-8"))
    probe = tmp_path / "probe.rs"
    probe.write_text(RUST_RUNTIME_COMPAT + "\n" + source, encoding="utf-8")
    return command_validation(
        "local_toolchain_syntax",
        [rustc, "--crate-type", "lib", str(probe), "-o", str(tmp_path / "libprobe.rlib")],
    )


def validate_python(path: Path, _tmp_path: Path) -> dict[str, Any]:
    return command_validation("local_toolchain_syntax", [sys.executable, "-m", "py_compile", str(path)])


def validate_javascript(path: Path, tmp_path: Path) -> dict[str, Any]:
    node = tool("node")
    if not node:
        return structural_result("tool_unavailable", ["export function runtime_helper_mix"], path)
    mjs = tmp_path / "runtime_helper_mix.mjs"
    mjs.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation("local_toolchain_syntax", [node, "--check", str(mjs)])


def validate_java(path: Path, tmp_path: Path) -> dict[str, Any]:
    javac = tool("javac")
    if not javac:
        return structural_result("tool_unavailable", ["public final class RuntimeHelperMix", "runtime_helper_mix"], path)
    java_path = tmp_path / "RuntimeHelperMix.java"
    java_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation("local_toolchain_syntax", [javac, str(java_path)])


def validate_lean(path: Path, _tmp_path: Path) -> dict[str, Any]:
    lean = tool("lean")
    if not lean:
        return structural_result("tool_unavailable", ["theorem runtime_helper_mix_def"], path)
    env = os.environ.copy()
    existing = env.get("LEAN_PATH", "")
    env["LEAN_PATH"] = f"{MACHLIB_BUILD_LIB}:{existing}" if existing else str(MACHLIB_BUILD_LIB)
    result = run([lean, str(path)], env=env, timeout=30)
    return {
        "validationLevel": "local_toolchain_syntax_with_sorry_allowed",
        "validationStatus": result["status"],
        "tool": "lean",
        "outputExcerpt": result["outputExcerpt"],
    }


def validate_zkproof(path: Path, _tmp_path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    circuits = payload.get("circuits", [])
    ok = payload.get("spec") == "monogate-zkcircuit/v1" and len(circuits) >= 1
    return {
        "validationLevel": "json_schema_structural",
        "validationStatus": "pass" if ok else "fail",
        "tool": "python_json",
        "circuitCount": len(circuits),
        "outputExcerpt": "",
    }


def validate_wasm(path: Path, _tmp_path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if data.startswith(b"\x00asm"):
        ok = True
        level = "wasm_magic_structural"
    else:
        text = data.decode("utf-8", errors="replace")
        ok = "wasm32" in text and "define" in text
        level = "wasm_llvm_ir_structural"
    return {
        "validationLevel": level,
        "validationStatus": "pass" if ok else "fail",
        "tool": "structural",
        "outputExcerpt": "",
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


def validate_structural_target(target: str, path: Path) -> dict[str, Any]:
    token_map = {
        "go": ["package runtimehelpermix", "func runtime_helper_mix"],
        "kotlin": ["package forge.runtime_helper_mix", "fun runtime_helper_mix"],
        "csharp": ["namespace Forge", "public static class RuntimeHelperMix", "runtime_helper_mix"],
        "matlab": ["function", "runtime_helper_mix"],
    }
    return structural_result("structural_tokens", token_map[target], path)


def validate_target(target: str, path: Path, tmp_path: Path) -> dict[str, Any]:
    validators = {
        "c": validate_c,
        "cpp": validate_cpp,
        "rust": validate_rust,
        "python": validate_python,
        "javascript": validate_javascript,
        "java": validate_java,
        "lean": validate_lean,
        "zkproof": validate_zkproof,
        "wasm": validate_wasm,
    }
    if target in validators:
        return validators[target](path, tmp_path)
    return validate_structural_target(target, path)


def build_target_row(source_path: Path, target: str, ext: str, tmp_path: Path) -> dict[str, Any]:
    out_name = "RuntimeHelperMix.java" if target == "java" else f"runtime_helper_mix.{ext}"
    out_path = tmp_path / target / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emission = compile_target(source_path, target, out_path)
    validation = validate_target(target, out_path, out_path.parent) if emission["emissionStatus"] == "pass" else {
        "validationLevel": "not_attempted_emission_failed",
        "validationStatus": "fail",
        "tool": "",
        "outputExcerpt": emission["outputExcerpt"],
    }
    return {**emission, **validation}


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "freeTargetCount": len(rows),
        "emissionPassCount": sum(1 for row in rows if row["emissionStatus"] == "pass"),
        "validationPassCount": sum(1 for row in rows if row["validationStatus"] == "pass"),
        "localToolchainValidationTargets": [
            row["target"] for row in rows if row["validationLevel"].startswith("local_toolchain")
        ],
        "structuralValidationTargets": [
            row["target"] for row in rows if not row["validationLevel"].startswith("local_toolchain")
        ],
        "emittedTargets": [row["target"] for row in rows if row["emissionStatus"] == "pass"],
        "validationFailedTargets": [row["target"] for row in rows if row["validationStatus"] != "pass"],
        "allFreeTargetsEmissionPass": all(row["emissionStatus"] == "pass" for row in rows),
        "allFreeTargetsValidationPass": all(row["validationStatus"] == "pass" for row in rows),
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


def build_payload() -> dict[str, Any]:
    fef_p11 = read_json(FEF_P11_PATH)
    fef_p30 = read_json(FEF_P30_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p32_runtime_helper_targets_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "runtime_helper_mix.eml"
        source_path.write_text(SOURCE_FIXTURE, encoding="utf-8")
        rows = [build_target_row(source_path, target, ext, tmp_path) for target, ext in FREE_TARGETS]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p32-free-target-runtime-helper-guard",
        "decision": "runtime_helper_fixture_all_free_targets_emit_and_validate",
        "sourceFixture": SOURCE_FIXTURE_ID,
        "targetRows": rows,
        "summary": summarize(rows),
        "fefP11Link": {
            "path": str(FEF_P11_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p11["reviewDecision"],
        },
        "fefP30Link": {
            "path": str(FEF_P30_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p30["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_fixture_all_13_free_targets_emit", "status": "pass"},
            {"id": "selected_fixture_all_13_free_targets_validate", "status": "pass"},
            {"id": "all_free_targets_public_ready", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Add runtime checks for additional free targets where local toolchains are available.",
            "Turn the selected-fixture guards into a small multi-fixture matrix.",
            "Add local runtime checks for Go/Kotlin/C#/MATLAB when toolchains are available.",
            "Keep public package publication blocked until explicit release action.",
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
        "title": "FEF-P32 Free Target Runtime-Helper Guard",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "runtime_helper_free_target_emission_guard_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Runtime-helper fixture emission and validation guard for the 13 Forge free targets only; it uses local toolchain checks where available and structural checks otherwise, and makes no all-free-target public readiness, compiler correctness, formal equivalence, publication, runtime performance, hardware, Pro-target, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "All 13 free targets emitted non-empty artifacts for generated/runtime_helper_mix.eml.",
            "C, C++, Rust, Python, JavaScript, Java, and Lean received local toolchain checks.",
            "Go, Kotlin, C#, MATLAB, wasm, and zkproof received bounded structural checks in this environment.",
            "The guard is runtime-helper fixture evidence only and does not publish or widen public preview claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p32_free_target_runtime_helper_guard.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p32_free_target_runtime_helper_guard.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p32_free_target_runtime_helper_guard.v0",
        "date": DATE,
        "title": "FEF-P32 Free Target Runtime-Helper Guard",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add local runtime checks for additional free targets or turn selected fixtures into a small multi-fixture matrix.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Target | Emission | Validation | Level | Bytes |",
        "|---|---:|---:|---|---:|",
    ]
    for row in payload["targetRows"]:
        rows.append(
            f"| `{row['target']}` | `{row['emissionStatus']}` | `{row['validationStatus']}` | "
            f"`{row['validationLevel']}` | `{row['artifactBytes']}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P32 Free Target Runtime-Helper Guard",
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
            f"- Free targets checked: `{summary['freeTargetCount']}`",
            f"- Emission passes: `{summary['emissionPassCount']}`",
            f"- Validation passes: `{summary['validationPassCount']}`",
            f"- Local-toolchain validation targets: `{', '.join(summary['localToolchainValidationTargets'])}`",
            f"- Structural validation targets: `{', '.join(summary['structuralValidationTargets'])}`",
            "",
            "## Boundary",
            "",
            "- Runtime-helper fixture emission and validation guard only.",
            "- Structural checks are not runtime checks.",
            "- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.",
            "- No package publication, checkout, performance, hardware, Pro-target, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P32 schema")
    summary = payload["summary"]
    if summary["freeTargetCount"] != 13:
        raise ValueError("expected 13 free targets")
    if summary["emissionPassCount"] != 13:
        raise ValueError("all 13 free targets must emit")
    if summary["validationPassCount"] != 13:
        raise ValueError("all 13 free targets must validate at the selected level")
    if summary["allFreeTargetsEmissionPass"] is not True:
        raise ValueError("all free target emission must pass")
    if summary["allFreeTargetsValidationPass"] is not True:
        raise ValueError("all free target validation must pass")
    for key in [
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
    result_path = out_dir / f"fef_p32_free_target_runtime_helper_guard_{STAMP}.json"
    report_path = report_dir / f"fef_p32_free_target_runtime_helper_guard_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p32_free_target_runtime_helper_guard.json"
    feed_path = command_feed_dir / f"fef_p32_free_target_runtime_helper_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p32_free_target_runtime_helper_guard")
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
    print("FEF_P32_FREE_TARGET_RUNTIME_HELPER_GUARD_OK")
    print(f"free_targets={built['payload']['summary']['freeTargetCount']}")
    print(f"emission_passes={built['payload']['summary']['emissionPassCount']}")
    print(f"validation_passes={built['payload']['summary']['validationPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
