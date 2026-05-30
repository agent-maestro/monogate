#!/usr/bin/env python3
"""FEF-P10 broader generated-target re-ingest fixture family."""

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
from efrog.decompilers.javascript import decompile_javascript_file  # noqa: E402
from efrog.decompilers.python import decompile_python_source  # noqa: E402
from efrog.decompilers.rust import decompile_rust_file  # noqa: E402
from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts.fef_p8_generated_target_reingest import (  # noqa: E402
    ATOL,
    RTOL,
    CLAIM_FLAGS as BASE_CLAIM_FLAGS,
    call_generated_js,
    call_generated_python,
    compare_values,
    compile_target,
    reingest_target,
)

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p10_broader_generated_target_reingest.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p10_reingest_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P10_BROADER_GENERATED_TARGET_REINGEST_PASS"

FEF_P9_PATH = ROOT / "reports/evidence_packets/fef_p9_pow_spelling_reingest_guard.json"

CLAIM_FLAGS = dict(BASE_CLAIM_FLAGS)

NON_CLAIMS = [
    "FEF-P10 records a broader but still bounded generated-target re-ingest fixture family.",
    "FEF-P10 compares generated target outputs to re-ingested-and-recompiled Python outputs over deterministic samples.",
    "FEF-P10 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P10 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P10 does not claim runtime performance, Verilog, Lean proofs, zkproof, silicon, or hardware output.",
]

CASES: list[dict[str, Any]] = [
    {
        "caseId": "python_gaussian_broader_reingest_v0",
        "sourceLanguage": "python",
        "sourcePath": "examples/gaussian.py",
        "functionName": "gaussian",
        "samples": [
            {"args": [0.0, 1.0, -1.0], "labels": ["mu", "sigma", "x"]},
            {"args": [0.5, 2.0, 1.5], "labels": ["mu", "sigma", "x"]},
            {"args": [-1.0, 0.75, 0.25], "labels": ["mu", "sigma", "x"]},
        ],
    },
    {
        "caseId": "python_stable_sigmoid_broader_reingest_v0",
        "sourceLanguage": "python",
        "sourcePath": "examples/stable_sigmoid.py",
        "functionName": "stable_sigmoid",
        "samples": [{"args": [x], "labels": ["x"]} for x in [-8.0, -2.0, 0.0, 2.0, 8.0]],
    },
    {
        "caseId": "python_voltage_divider_broader_reingest_v0",
        "sourceLanguage": "python",
        "sourcePath": "examples/voltage_divider.py",
        "functionName": "voltage_divider",
        "samples": [
            {"args": [5.0, 1000.0, 1000.0], "labels": ["vin", "r_top", "r_bottom"]},
            {"args": [3.3, 220.0, 470.0], "labels": ["vin", "r_top", "r_bottom"]},
            {"args": [12.0, 3300.0, 680.0], "labels": ["vin", "r_top", "r_bottom"]},
        ],
    },
    {
        "caseId": "python_rc_decay_stable_broader_reingest_v0",
        "sourceLanguage": "python",
        "sourcePath": "examples/rc_decay_stable.py",
        "functionName": "rc_decay_stable",
        "samples": [
            {"args": [5.0, 2.0, 0.5], "labels": ["v0", "tau", "t"]},
            {"args": [3.3, 4.0, 1.2], "labels": ["v0", "tau", "t"]},
            {"args": [1.8, 0.75, 0.1], "labels": ["v0", "tau", "t"]},
        ],
    },
    {
        "caseId": "python_stretched_exponential_broader_reingest_v0",
        "sourceLanguage": "python",
        "sourcePath": "examples/stretched_exponential.py",
        "functionName": "stretched_exponential",
        "samples": [
            {"args": [2.0, 1.5, 0.5, 1.2], "labels": ["a", "tau", "beta", "t"]},
            {"args": [1.0, 2.0, 0.25, 0.75], "labels": ["a", "tau", "beta", "t"]},
            {"args": [4.0, 3.0, 1.0, 2.5], "labels": ["a", "tau", "beta", "t"]},
        ],
    },
    {
        "caseId": "javascript_gaussian_broader_reingest_v0",
        "sourceLanguage": "javascript",
        "sourcePath": "examples/gaussian.js",
        "functionName": "gaussian",
        "samples": [
            {"args": [-1.0, 0.0, 1.0], "labels": ["x", "mu", "sigma"]},
            {"args": [1.5, 0.5, 2.0], "labels": ["x", "mu", "sigma"]},
            {"args": [0.25, -1.0, 0.75], "labels": ["x", "mu", "sigma"]},
        ],
    },
    {
        "caseId": "javascript_circle_area_broader_reingest_v0",
        "sourceLanguage": "javascript",
        "sourcePath": "examples/circle_area.js",
        "functionName": "area",
        "samples": [{"args": [r], "labels": ["r"]} for r in [0.0, 0.5, 2.5]],
    },
    {
        "caseId": "c_gaussian_broader_reingest_v0",
        "sourceLanguage": "c",
        "sourcePath": "examples/gaussian.c",
        "functionName": "gaussian",
        "samples": [
            {"args": [0.0, 1.0, -1.0], "labels": ["mu", "sigma", "x"]},
            {"args": [0.5, 2.0, 1.5], "labels": ["mu", "sigma", "x"]},
            {"args": [-1.0, 0.75, 0.25], "labels": ["mu", "sigma", "x"]},
        ],
    },
    {
        "caseId": "rust_sigmoid_broader_reingest_v0",
        "sourceLanguage": "rust",
        "sourcePath": "examples/sigmoid.rs",
        "functionName": "sigmoid",
        "samples": [{"args": [x], "labels": ["x"]} for x in [-2.0, 0.0, 2.0]],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def decompile_source_case(case: dict[str, Any]):
    source_path = EFROG_ROOT / case["sourcePath"]
    if case["sourceLanguage"] == "python":
        return decompile_python_source(
            source_path.read_text(encoding="utf-8"),
            source_path=str(source_path),
        )
    if case["sourceLanguage"] == "javascript":
        return decompile_javascript_file(str(source_path))
    if case["sourceLanguage"] == "c":
        return decompile_c_file(str(source_path))
    if case["sourceLanguage"] == "rust":
        return decompile_rust_file(str(source_path))
    raise ValueError(f"unsupported FEF-P10 source language: {case['sourceLanguage']}")


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
        generated_values = call_generated_python(
            generated_path,
            case["functionName"],
            samples,
            f"{case['caseId']}_generated",
        )
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
        "packetType": "fef_p10_reingest_packet_v0",
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
            "larger generated-target fixture family",
            "per-target validation policy for non-Python/JavaScript outputs",
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
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    fef_p9 = read_json(FEF_P9_PATH)
    packets: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="fef_p10_broader_reingest_") as tmp:
        tmp_path = Path(tmp)
        for case in CASES:
            for target in ("python", "javascript"):
                packets.append(compare_case_target(case, target, tmp_path))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p10-broader-generated-target-reingest",
        "decision": "broader_selected_generated_target_reingest_passed",
        "reingestPackets": packets,
        "summary": summarize(packets),
        "fefP9Link": {
            "path": str(FEF_P9_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p9["reviewDecision"],
        },
        "releaseGates": [
            {"id": "broader_python_generated_target_reingest", "status": "pass"},
            {"id": "broader_javascript_generated_target_reingest", "status": "pass"},
            {"id": "source_language_family_expanded", "status": "pass"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Add per-target validation policy for non-Python/JavaScript outputs.",
            "Create a private release-readiness checklist before any explicit publication action.",
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
        "title": "FEF-P10 Broader Generated-Target Re-ingest",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "broader_selected_generated_target_reingest_sample_grid_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Broader selected generated Python/JavaScript target re-ingest only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Generated Python outputs re-ingest through eFrog and recompile to Python for the selected broader fixture family.",
            "Generated JavaScript outputs re-ingest through eFrog and recompile to Python for the selected broader fixture family.",
            "The selected source family now includes Python, JavaScript, C, and Rust sources.",
            "Generated target outputs and re-ingested/recompiled Python outputs agree over deterministic samples for the selected cases.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p10_broader_generated_target_reingest.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p10_broader_generated_target_reingest.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p10_broader_generated_target_reingest.v0",
        "date": DATE,
        "title": "FEF-P10 Broader Generated-Target Re-ingest",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add per-target validation policy for non-Python/JavaScript outputs.",
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
            "# FEF-P10 Broader Generated-Target Re-ingest",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P10 broadens the generated-target re-ingest fixture family while",
            "keeping the evidence private, deterministic, and bounded.",
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
            "- Broader selected generated Python/JavaScript target re-ingest only.",
            "- No package publication or checkout claim.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P10 packet schema")
    if packet["packetType"] != "fef_p10_reingest_packet_v0":
        raise ValueError("invalid FEF-P10 packet type")
    if packet["generatedTargetLanguage"] not in {"python", "javascript"}:
        raise ValueError("FEF-P10 generated target must be Python or JavaScript")
    if packet["reingestStatus"] != "pass":
        raise ValueError(f"{packet['caseId']} re-ingest did not pass")
    for frame in packet["frames"]:
        if frame["withinTolerance"] is not True:
            raise ValueError(f"{packet['caseId']} frame outside tolerance")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P10 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P10 status")
    summary = payload["summary"]
    if summary["caseCount"] != 9:
        raise ValueError("expected nine broader re-ingest cases")
    if summary["packetCount"] != 18:
        raise ValueError("expected eighteen broader re-ingest packets")
    if summary["passCount"] != summary["packetCount"]:
        raise ValueError("all broader re-ingest packets must pass")
    if summary["sourceLanguages"] != ["c", "javascript", "python", "rust"]:
        raise ValueError("FEF-P10 must cover C, JavaScript, Python, and Rust sources")
    if summary["generatedTargetLanguages"] != ["javascript", "python"]:
        raise ValueError("FEF-P10 must cover Python and JavaScript generated targets")
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
    result_path = out_dir / f"fef_p10_broader_generated_target_reingest_{STAMP}.json"
    report_path = report_dir / f"fef_p10_broader_generated_target_reingest_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p10_broader_generated_target_reingest.json"
    feed_path = command_feed_dir / f"fef_p10_broader_generated_target_reingest_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p10_broader_generated_target_reingest")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p10_reingest_packets")
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
    print("FEF_P10_BROADER_GENERATED_TARGET_REINGEST_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
