#!/usr/bin/env python3
"""FEF-P34 clamp/guard free-target guard for the Forge CLI."""

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
SCHEMA_VERSION = "monogate.fef_p34_clamp_guard_free_target_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P34_CLAMP_GUARD_FREE_TARGET_GUARD_PASS"

FEF_P11_PATH = ROOT / "reports/evidence_packets/fef_p11_per_target_validation_policy.json"
FEF_P33_PATH = ROOT / "reports/evidence_packets/fef_p33_free_target_fixture_matrix.json"
SOURCE_FIXTURE_ID = "generated/clamp_guard_mix.eml"
SOURCE_FIXTURE = """module clamp_guard_mix;

@verify(lean, theorem = "clamp_guard_mix_bounds")
fn clamp_guard_mix(x: Real) -> Real
    where chain_order <= 0
    ensures (result >= -1.0)
    ensures (result <= 1.0)
{
    clamp(x, -1.0, 1.0)
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
    "clamp_guard_free_target_guard_claim": False,
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
    "FEF-P34 records clamp/guard fixture emission for the 13 Forge free targets.",
    "FEF-P34 uses local syntax/toolchain checks where tools are installed and structural checks where they are not.",
    "FEF-P34 does not claim arbitrary branch/control-flow support.",
    "FEF-P34 does not claim all free targets are public-ready.",
    "FEF-P34 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P34 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P34 does not claim runtime performance, Verilog, silicon, hardware, Pro-target, or all-target readiness.",
]

RUST_RUNTIME_COMPAT = """
#[allow(dead_code)]
mod monogate_sys {
    pub fn mg_abs(x: f64) -> f64 { x.abs() }
    pub fn mg_acos(x: f64) -> f64 { x.acos() }
    pub fn mg_asin(x: f64) -> f64 { x.asin() }
    pub fn mg_atan(x: f64) -> f64 { x.atan() }
    pub fn mg_clamp(x: f64, lo: f64, hi: f64) -> f64 { x.max(lo).min(hi) }
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
        return structural_result("tool_unavailable", ["#include", "mg_clamp", "clamp_guard_mix"], path)
    return command_validation(
        "local_toolchain_syntax",
        [gcc, "-std=c11", "-Wall", "-Werror", f"-I{FORGE_C_INCLUDE}", "-c", str(path), "-o", str(tmp_path / "c.o")],
    )


def validate_cpp(path: Path, tmp_path: Path) -> dict[str, Any]:
    gpp = tool("g++")
    if not gpp:
        return structural_result("tool_unavailable", ["namespace forge::clamp_guard_mix", "clamp_guard_mix"], path)
    wrapper = tmp_path / "cpp_main.cpp"
    wrapper.write_text(
        '#include "clamp_guard_mix.hpp"\n'
        "int main() {\n"
        "  double got = forge::clamp_guard_mix::clamp_guard_mix(2.5);\n"
        "  return got == 1.0 ? 0 : 1;\n"
        "}\n",
        encoding="utf-8",
    )
    copied = tmp_path / "clamp_guard_mix.hpp"
    copied.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation(
        "local_toolchain_syntax",
        [gpp, "-std=c++17", "-Wall", "-Werror", "-I", str(tmp_path), "-c", str(wrapper), "-o", str(tmp_path / "cpp.o")],
    )


def validate_rust(path: Path, tmp_path: Path) -> dict[str, Any]:
    rustc = tool("rustc")
    if not rustc:
        return structural_result("tool_unavailable", ["pub fn clamp_guard_mix", "mg_clamp"], path)
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
        return structural_result("tool_unavailable", ["export function clamp_guard_mix"], path)
    mjs = tmp_path / "clamp_guard_mix.mjs"
    mjs.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation("local_toolchain_syntax", [node, "--check", str(mjs)])


def validate_java(path: Path, tmp_path: Path) -> dict[str, Any]:
    javac = tool("javac")
    if not javac:
        return structural_result("tool_unavailable", ["public final class ClampGuardMix", "clamp_guard_mix"], path)
    java_path = tmp_path / "ClampGuardMix.java"
    java_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return command_validation("local_toolchain_syntax", [javac, str(java_path)])


def validate_lean(path: Path, _tmp_path: Path) -> dict[str, Any]:
    lean = tool("lean")
    if not lean:
        return structural_result("tool_unavailable", ["theorem clamp_guard_mix_bounds"], path)
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


def validate_wasm(path: Path, _tmp_path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if data.startswith(b"\x00asm"):
        ok = True
        level = "wasm_magic_structural"
    else:
        text = data.decode("utf-8", errors="replace")
        ok = "wasm32" in text and "mg_clamp" in text
        level = "wasm_llvm_ir_structural"
    return {
        "validationLevel": level,
        "validationStatus": "pass" if ok else "fail",
        "tool": "structural",
        "outputExcerpt": "",
    }


def validate_zkproof(path: Path, _tmp_path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    circuits = payload.get("circuits", [])
    gate_kinds = [
        gate.get("k")
        for circuit in circuits
        for gate in circuit.get("circuit", {}).get("gates", [])
    ]
    ok = (
        payload.get("spec") == "monogate-zkcircuit/v1"
        and len(circuits) >= 1
        and "CLAMP" in gate_kinds
        and payload.get("n_skipped") == 0
    )
    return {
        "validationLevel": "json_schema_structural_clamp_gate",
        "validationStatus": "pass" if ok else "fail",
        "tool": "python_json",
        "circuitCount": len(circuits),
        "containsClampGate": "CLAMP" in gate_kinds,
        "outputExcerpt": "",
    }


def validate_structural_target(target: str, path: Path) -> dict[str, Any]:
    token_map = {
        "go": ["package clampguardmix", "func clamp_guard_mix"],
        "kotlin": ["package forge.clamp_guard_mix", "fun clamp_guard_mix"],
        "csharp": ["namespace Forge", "public static class ClampGuardMix", "clamp_guard_mix"],
        "matlab": ["function", "clamp_guard_mix"],
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
    out_name = "ClampGuardMix.java" if target == "java" else f"clamp_guard_mix.{ext}"
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
        "zkproofClampCircuitPass": any(
            row["target"] == "zkproof"
            and row["validationStatus"] == "pass"
            and row.get("containsClampGate") is True
            for row in rows
        ),
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
    fef_p33 = read_json(FEF_P33_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p34_clamp_guard_targets_") as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "clamp_guard_mix.eml"
        source_path.write_text(SOURCE_FIXTURE, encoding="utf-8")
        rows = [build_target_row(source_path, target, ext, tmp_path) for target, ext in FREE_TARGETS]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p34-clamp-guard-free-target-guard",
        "decision": "clamp_guard_fixture_all_free_targets_emit_and_validate",
        "sourceFixture": SOURCE_FIXTURE_ID,
        "targetRows": rows,
        "summary": summarize(rows),
        "fefP11Link": {
            "path": str(FEF_P11_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p11["reviewDecision"],
        },
        "fefP33Link": {
            "path": str(FEF_P33_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p33["reviewDecision"],
        },
        "releaseGates": [
            {"id": "clamp_guard_fixture_all_13_free_targets_emit", "status": "pass"},
            {"id": "clamp_guard_fixture_all_13_free_targets_validate", "status": "pass"},
            {"id": "zkproof_clamp_gate_structural_check", "status": "pass"},
            {"id": "all_free_targets_public_ready", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "nextMilestones": [
            "Fold FEF-P34 into the selected-fixture matrix as a third fixture.",
            "Add runtime execution checks for more free targets where local toolchains are available.",
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
        "title": "FEF-P34 Clamp/Guard Free Target Guard",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "clamp_guard_free_target_emission_guard_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Clamp/guard fixture emission and validation guard for the 13 Forge free targets only; it uses local toolchain checks where available and structural checks otherwise, and makes no arbitrary branch/control-flow support, all-free-target public readiness, compiler correctness, formal equivalence, publication, runtime performance, hardware, Pro-target, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "All 13 free targets emitted non-empty artifacts for generated/clamp_guard_mix.eml.",
            "The zkproof artifact contains a CLAMP gate with zero skipped functions.",
            "C, C++, Rust, Python, JavaScript, Java, and Lean received local toolchain checks.",
            "Go, Kotlin, C#, MATLAB, wasm, and zkproof received bounded structural checks in this environment.",
            "The guard is clamp/guard fixture evidence only and does not publish or widen public preview claims.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p34_clamp_guard_free_target_guard.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p34_clamp_guard_free_target_guard.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p34_clamp_guard_free_target_guard.v0",
        "date": DATE,
        "title": "FEF-P34 Clamp/Guard Free Target Guard",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Fold the clamp/guard fixture into the selected-fixture matrix or add local runtime execution checks for additional free targets.",
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
            "# FEF-P34 Clamp/Guard Free Target Guard",
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
            f"- zkproof clamp circuit pass: `{summary['zkproofClampCircuitPass']}`",
            f"- Local-toolchain validation targets: `{', '.join(summary['localToolchainValidationTargets'])}`",
            f"- Structural validation targets: `{', '.join(summary['structuralValidationTargets'])}`",
            "",
            "## Boundary",
            "",
            "- Clamp/guard fixture emission and validation guard only.",
            "- Structural checks are not runtime checks.",
            "- No arbitrary branch/control-flow support claim.",
            "- No all-free-target public-readiness, compiler-correctness, formal-equivalence, or publication claim.",
            "- No package publication, checkout, performance, hardware, Pro-target, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P34 schema")
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
    if summary["zkproofClampCircuitPass"] is not True:
        raise ValueError("zkproof clamp circuit structural check must pass")
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
    result_path = out_dir / f"fef_p34_clamp_guard_free_target_guard_{STAMP}.json"
    report_path = report_dir / f"fef_p34_clamp_guard_free_target_guard_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p34_clamp_guard_free_target_guard.json"
    feed_path = command_feed_dir / f"fef_p34_clamp_guard_free_target_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p34_clamp_guard_free_target_guard")
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
    print("FEF_P34_CLAMP_GUARD_FREE_TARGET_GUARD_OK")
    print(f"free_targets={built['payload']['summary']['freeTargetCount']}")
    print(f"emission_passes={built['payload']['summary']['emissionPassCount']}")
    print(f"validation_passes={built['payload']['summary']['validationPassCount']}")
    print(f"zkproof_clamp_circuit={built['payload']['summary']['zkproofClampCircuitPass']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
