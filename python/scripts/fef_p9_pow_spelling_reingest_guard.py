#!/usr/bin/env python3
"""FEF-P9 pow-spelling compatibility guard for generated-target re-ingest."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))
if str(MONOGATE_ROOT / "efrog") not in sys.path:
    sys.path.insert(0, str(MONOGATE_ROOT / "efrog"))

from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts.fef_p8_generated_target_reingest import (  # noqa: E402
    ATOL,
    RTOL,
    CLAIM_FLAGS as BASE_CLAIM_FLAGS,
    call_generated_js,
    call_generated_python,
    compare_values,
    compile_target,
    decompile_source_case,
    reingest_target,
)

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p9_pow_spelling_reingest_guard.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p9_pow_spelling_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P9_POW_SPELLING_REINGEST_GUARD_PASS"

FEF_P8_PATH = ROOT / "reports/evidence_packets/fef_p8_generated_target_reingest.json"

CLAIM_FLAGS = dict(BASE_CLAIM_FLAGS)

NON_CLAIMS = [
    "FEF-P9 records a bounded pow-spelling compatibility guard for selected generated-target re-ingest cases.",
    "FEF-P9 verifies that selected power-shaped generated Python targets re-ingest to Forge-parseable `pow(...)` EML.",
    "FEF-P9 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P9 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P9 does not claim runtime performance, Verilog, Lean proofs, zkproof, silicon, or hardware output.",
]

CASES: list[dict[str, Any]] = [
    {
        "caseId": "javascript_gaussian_pow_spelling_reingest_v0",
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
        "caseId": "javascript_circle_area_pow_spelling_reingest_v0",
        "sourceLanguage": "javascript",
        "sourcePath": "examples/circle_area.js",
        "functionName": "area",
        "samples": [{"args": [r], "labels": ["r"]} for r in [0.0, 0.5, 1.0, 2.5, 10.0]],
    },
    {
        "caseId": "c_circle_area_pow_spelling_reingest_v0",
        "sourceLanguage": "c",
        "sourcePath": "examples/circle_area.c",
        "functionName": "area",
        "samples": [{"args": [r], "labels": ["r"]} for r in [0.0, 0.5, 1.0, 2.5, 10.0]],
    },
    {
        "caseId": "rust_circle_area_pow_spelling_reingest_v0",
        "sourceLanguage": "rust",
        "sourcePath": "examples/circle_area.rs",
        "functionName": "area",
        "samples": [{"args": [r], "labels": ["r"]} for r in [0.0, 0.5, 1.0, 2.5, 10.0]],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pow_spelling_guard(reingested_eml: str, target: str) -> dict[str, Any]:
    has_caret_power = " ^ " in reingested_eml
    has_pow_call = "pow(" in reingested_eml
    return {
        "hasCaretPowerToken": has_caret_power,
        "hasPowCall": has_pow_call,
        "pythonGeneratedPowerCase": target == "python",
        "status": "pass" if not has_caret_power and (target != "python" or has_pow_call) else "fail",
    }


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
    spelling = pow_spelling_guard(reingested_eml, target)
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
        "packetType": "fef_p9_pow_spelling_packet_v0",
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
        "powSpellingGuard": spelling,
        "reingestedFunctionCount": len(reingested_mod.functions),
        "sampleCount": len(samples),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "reingestStatus": "pass" if max_abs <= ATOL or max_rel <= RTOL else "fail",
        "frames": frames,
        "missingEvidence": [
            "larger power-expression generated-target fixture family",
            "formal compiler correctness proof",
            "public package publication decision",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    python_packets = [p for p in packets if p["generatedTargetLanguage"] == "python"]
    return {
        "packetCount": len(packets),
        "passCount": sum(1 for packet in packets if packet["reingestStatus"] == "pass"),
        "failCount": sum(1 for packet in packets if packet["reingestStatus"] == "fail"),
        "sampleCount": sum(packet["sampleCount"] for packet in packets),
        "sourceLanguages": sorted({packet["sourceLanguage"] for packet in packets}),
        "generatedTargetLanguages": sorted({packet["generatedTargetLanguage"] for packet in packets}),
        "powSpellingGuardPass": all(packet["powSpellingGuard"]["status"] == "pass" for packet in packets),
        "pythonGeneratedPowerPowCallPass": all(packet["powSpellingGuard"]["hasPowCall"] is True for packet in python_packets),
        "caretPowerTokenCount": sum(1 for packet in packets if packet["powSpellingGuard"]["hasCaretPowerToken"]),
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
    fef_p8 = read_json(FEF_P8_PATH)
    packets: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="fef_p9_pow_spelling_") as tmp:
        tmp_path = Path(tmp)
        for case in CASES:
            for target in ("python", "javascript"):
                packets.append(compare_case_target(case, target, tmp_path))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p9-pow-spelling-reingest-guard",
        "decision": "pow_spelling_reingest_guard_passed",
        "powSpellingPackets": packets,
        "summary": summarize(packets),
        "fefP8Link": {
            "path": str(FEF_P8_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p8["reviewDecision"],
            "heldOutGapClosed": "power-expression generated-target re-ingest for selected fixtures",
        },
        "releaseGates": [
            {"id": "python_power_generated_target_reingest", "status": "pass"},
            {"id": "javascript_generated_target_reingest_still_passes", "status": "pass"},
            {"id": "caret_power_token_absent_from_reingested_eml", "status": "pass"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Broaden generated-target re-ingest fixtures beyond selected power cases.",
            "Add per-target validation policy for the broad target surface.",
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
        "title": "FEF-P9 Pow-Spelling Re-ingest Guard",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_power_generated_target_reingest_sample_grid_agreement",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected pow-spelling generated-target re-ingest only; no public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selected power-shaped generated Python targets re-ingest to `pow(...)` EML rather than caret power.",
            "The re-ingested EML recompiles through Forge Python for selected power-shaped cases.",
            "Generated target outputs and re-ingested/recompiled Python outputs agree over deterministic samples for the selected cases.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p9_pow_spelling_reingest_guard.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p9_pow_spelling_reingest_guard.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p9_pow_spelling_reingest_guard.v0",
        "date": DATE,
        "title": "FEF-P9 Pow-Spelling Re-ingest Guard",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Broaden generated-target re-ingest fixtures beyond selected power cases.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Source | Generated target | Samples | Pow guard | Status | Max abs error |",
        "|---|---|---|---:|---|---|---:|",
    ]
    for packet in payload["powSpellingPackets"]:
        rows.append(
            f"| `{packet['sourceCaseId']}` | `{packet['sourceLanguage']}` | `{packet['generatedTargetLanguage']}` | {packet['sampleCount']} | `{packet['powSpellingGuard']['status']}` | `{packet['reingestStatus']}` | {packet['maxAbsError']:.3e} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P9 Pow-Spelling Re-ingest Guard",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P9 closes the selected power-expression generated-target",
            "re-ingest holdout from FEF-P8 by requiring re-ingested EML to use",
            "`pow(...)` rather than caret power.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Packets: `{summary['packetCount']}`",
            f"- Samples: `{summary['sampleCount']}`",
            f"- Passes: `{summary['passCount']}`",
            f"- Pow spelling guard pass: `{summary['powSpellingGuardPass']}`",
            f"- Caret power token count: `{summary['caretPowerTokenCount']}`",
            f"- Max abs error: `{summary['maxAbsError']:.3e}`",
            f"- Max rel error: `{summary['maxRelError']:.3e}`",
            "",
            "## Boundary",
            "",
            "- Selected power-shaped generated-target re-ingest only.",
            "- No package publication or checkout claim.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No runtime performance, production, Verilog, Lean proof, zkproof, silicon, or hardware claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P9 packet schema")
    if packet["packetType"] != "fef_p9_pow_spelling_packet_v0":
        raise ValueError("invalid FEF-P9 packet type")
    if packet["powSpellingGuard"]["status"] != "pass":
        raise ValueError(f"{packet['caseId']} pow-spelling guard did not pass")
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
        raise ValueError("invalid FEF-P9 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P9 status")
    summary = payload["summary"]
    if summary["packetCount"] != 8:
        raise ValueError("expected eight pow-spelling re-ingest packets")
    if summary["passCount"] != summary["packetCount"]:
        raise ValueError("all pow-spelling re-ingest packets must pass")
    if summary["powSpellingGuardPass"] is not True:
        raise ValueError("pow-spelling guard must pass")
    if summary["pythonGeneratedPowerPowCallPass"] is not True:
        raise ValueError("selected generated Python power cases must re-ingest to pow(...)")
    if summary["caretPowerTokenCount"] != 0:
        raise ValueError("re-ingested EML must not include caret power tokens")
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
    for packet in payload["powSpellingPackets"]:
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
    result_path = out_dir / f"fef_p9_pow_spelling_reingest_guard_{STAMP}.json"
    report_path = report_dir / f"fef_p9_pow_spelling_reingest_guard_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p9_pow_spelling_reingest_guard.json"
    feed_path = command_feed_dir / f"fef_p9_pow_spelling_reingest_guard_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in payload["powSpellingPackets"]:
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p9_pow_spelling_reingest_guard")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p9_pow_spelling_packets")
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
    print("FEF_P9_POW_SPELLING_REINGEST_GUARD_OK")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
