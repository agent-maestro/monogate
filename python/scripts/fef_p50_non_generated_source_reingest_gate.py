#!/usr/bin/env python3
"""FEF-P50 selected non-generated source-derived C/Rust re-ingest gate."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from efrog.fingerprint import fingerprint_eml  # noqa: E402
from scripts import fef_p6_broader_original_runtime_semantic_comparison as p6  # noqa: E402
from scripts import fef_p49_non_generated_c_rust_fixture_gate as p49  # noqa: E402
from scripts.fef_p10_broader_generated_target_reingest import (  # noqa: E402
    ATOL,
    RTOL,
    call_generated_python,
    compare_values,
    compile_target,
)
from scripts.fef_p12_c_rust_generated_target_runtime import (  # noqa: E402
    call_generated_c,
    call_generated_rust,
)
from scripts.fef_p13_c_rust_generated_target_reingest import (  # noqa: E402
    reingest_generated_target,
)

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p50_non_generated_source_reingest_gate.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p50_source_derived_reingest_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P50_NON_GENERATED_SOURCE_REINGEST_GATE_PASS"

P49_PACKET = ROOT / "reports/evidence_packets/fef_p49_non_generated_c_rust_fixture_gate.json"

CLAIM_FLAGS = {
    "selected_non_generated_source_derived_reingest_claim": False,
    "full_non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "arbitrary_source_family_claim": False,
    "all_free_targets_roundtrip_claim": False,
    "all_free_targets_runtime_execution_claim": False,
    "all_target_readiness_claim": False,
    "private_reviewer_decision_recorded": False,
    "public_preview_release_claim": False,
    "package_published": False,
    "checkout_enabled": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
}

NON_CLAIMS = [
    "FEF-P50 records selected non-generated source-derived generated C/Rust target re-ingest checks.",
    "FEF-P50 compares generated C/Rust runtime outputs to re-ingested-and-recompiled Python outputs over deterministic samples.",
    "FEF-P50 does not claim full non-generated source roundtrip.",
    "FEF-P50 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P50 does not record reviewer approval or rejection.",
    "FEF-P50 does not publish a package.",
    "FEF-P50 does not enable checkout or commerce.",
    "FEF-P50 does not claim public readiness.",
    "FEF-P50 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P50 does not claim runtime performance.",
    "FEF-P50 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P50 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_case_target(case: dict[str, Any], target: str, tmp_path: Path) -> dict[str, Any]:
    source_mod = p6.decompile_case(case)
    source_eml = source_mod.to_eml()
    source_eml_path = tmp_path / f"{case['caseId']}_source.eml"
    source_eml_path.write_text(source_eml, encoding="utf-8")

    target_ext = "c" if target == "c" else "rs"
    generated_path = tmp_path / f"{case['caseId']}_generated.{target_ext}"
    compile_target(source_eml_path, target, generated_path)

    reingested_mod = reingest_generated_target(target, generated_path)
    reingested_eml = reingested_mod.to_eml()
    reingested_eml_path = tmp_path / f"{case['caseId']}_{target}_reingested.eml"
    reingested_py_path = tmp_path / f"{case['caseId']}_{target}_reingested.py"
    reingested_eml_path.write_text(reingested_eml, encoding="utf-8")
    compile_target(reingested_eml_path, "python", reingested_py_path)

    samples = case["samples"]
    if target == "c":
        generated_values = call_generated_c(generated_path, case["functionName"], samples, tmp_path)
    elif target == "rust":
        generated_values = call_generated_rust(generated_path, case["functionName"], samples, tmp_path)
    else:
        raise ValueError(f"unsupported FEF-P50 target: {target}")
    reingested_values = call_generated_python(
        reingested_py_path,
        case["functionName"],
        samples,
        f"{case['caseId']}_{target}_source_derived_reingested",
    )
    frames, max_abs, max_rel = compare_values(generated_values, reingested_values, samples)
    for frame in frames:
        frame["values"] = {
            "sourceDerivedGeneratedTargetRuntime": frame["values"]["generatedTarget"],
            "reingestedRecompiledPython": frame["values"]["reingestedRecompiledPython"],
        }

    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p50_source_derived_reingest_packet_v0",
        "date": DATE,
        "caseId": f"{case['caseId']}_{target}_source_derived_reingest",
        "sourceCaseId": case["caseId"],
        "sourceLanguage": case["sourceLanguage"],
        "sourcePath": case["sourcePath"],
        "generatedTargetLanguage": target,
        "reingestedTargetLanguage": "eml",
        "recompiledTargetLanguage": "python",
        "functionName": case["functionName"],
        "sourceEmlHash": fingerprint_eml(source_eml),
        "reingestedEmlHash": fingerprint_eml(reingested_eml),
        "sourceFunctionCount": len(source_mod.functions),
        "reingestedFunctionCount": len(reingested_mod.functions),
        "sampleCount": len(samples),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "reingestStatus": "pass" if max_abs <= ATOL or max_rel <= RTOL else "fail",
        "frames": frames,
        "evidenceKind": "selected_non_generated_source_derived_generated_target_reingest",
        "missingEvidence": [
            "larger non-generated C/Rust source fixture family",
            "non-generated source-derived re-ingest for branch/control-flow targets",
            "direct arbitrary source-to-source roundtrip",
            "formal compiler correctness proof",
            "public package publication decision",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def summarize(packets: list[dict[str, Any]], p49_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "packetCount": len(packets),
        "passCount": sum(1 for packet in packets if packet["reingestStatus"] == "pass"),
        "failCount": sum(1 for packet in packets if packet["reingestStatus"] == "fail"),
        "sourceCaseCount": len({packet["sourceCaseId"] for packet in packets}),
        "sourceSampleCount": p49_summary["nonGeneratedSourceSampleCount"],
        "packetSampleCount": sum(packet["sampleCount"] for packet in packets),
        "sourceLanguages": sorted({packet["sourceLanguage"] for packet in packets}),
        "generatedTargetLanguages": sorted({packet["generatedTargetLanguage"] for packet in packets}),
        "recompiledTargetLanguages": sorted({packet["recompiledTargetLanguage"] for packet in packets}),
        "maxAbsError": max(packet["maxAbsError"] for packet in packets),
        "maxRelError": max(packet["maxRelError"] for packet in packets),
        "p49SemanticEvidenceAttached": p49_summary["nonGeneratedCRustSemanticEvidenceAttached"],
        "selectedNonGeneratedSourceDerivedReingest": True,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "fullCRustRoundtripClaim": False,
        "arbitrarySourceFamilyClaim": False,
        "reviewerDecisionRecorded": False,
        "packagePublished": False,
        "checkoutEnabled": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "allFreeTargetsRuntimeExecutionClaim": False,
        "allFreeTargetsRoundtripClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p49_packet = read_json(P49_PACKET)
    p49_summary = p49_packet["semanticReview"]
    packets: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="fef_p50_source_reingest_") as tmp:
        tmp_path = Path(tmp)
        for case in p6.CASES:
            for target in ("c", "rust"):
                packets.append(compare_case_target(case, target, tmp_path))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p50-non-generated-source-reingest-gate",
        "decision": "selected_non_generated_source_derived_reingest_passed_full_roundtrip_blocked",
        "reingestPackets": packets,
        "summary": summarize(packets, p49_summary),
        "fefP49Link": {
            "path": str(P49_PACKET.relative_to(ROOT)),
            "reviewDecision": p49_packet["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_non_generated_source_derived_reingest", "status": "pass"},
            {"id": "full_non_generated_source_roundtrip_claim", "status": "blocked"},
            {"id": "full_c_rust_roundtrip_claim", "status": "blocked"},
            {"id": "arbitrary_source_family_claim", "status": "blocked"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "public_readiness", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivateClaims": [
            "Selected non-generated C/Rust source fixtures produce source-derived generated C/Rust targets that re-ingest through eFrog.",
            "The selected source-derived re-ingest gate covers 5 source cases, 10 generated-target packets, and 46 packet-sample comparisons.",
            "Generated C/Rust target runtimes match re-ingested-and-recompiled Python outputs over deterministic samples.",
            "This is private selected-fixture evidence only, not full arbitrary C/Rust source roundtrip.",
        ],
        "blockedClaims": [
            "full non-generated source roundtrip is supported",
            "full arbitrary C/Rust source roundtrip is supported",
            "arbitrary C/Rust source-family support is established",
            "Forge/eFrog is public-ready",
            "a package has been published",
            "checkout is enabled",
            "compiler correctness has been proved",
            "formal semantic equivalence has been proved",
            "runtime performance has been established",
            "all 13 free targets runtime-execute",
            "all 13 free targets roundtrip",
            "hardware, silicon, Lean-proof, zkproof, Pro-target, production, or all-target readiness is established",
        ],
        "nextMilestones": [
            "Record private reviewer response over P47/P48/P49/P50.",
            "If reviewer requests broader C/Rust confidence, add branch/control-flow non-generated fixtures under a separate gate.",
            "Do not relabel P50 as full source roundtrip without direct arbitrary source-family evidence.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "p49NonClaimsInherited": list(p49.NON_CLAIMS),
    }
    validate_payload(payload)
    return copy.deepcopy(payload)


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P50 Non-Generated Source Re-ingest Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_non_generated_source_derived_generated_target_reingest_full_roundtrip_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected non-generated source-derived generated C/Rust target re-ingest only; no full non-generated source roundtrip, arbitrary C/Rust source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P50 runs source-derived re-ingest checks over the selected P6 non-generated C/Rust source fixtures.",
            "The gate covers 5 source cases, 10 generated C/Rust target packets, and 46 packet-sample comparisons.",
            "Generated target runtimes match re-ingested-and-recompiled Python outputs over deterministic samples.",
            "Full arbitrary C/Rust source roundtrip remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p50_non_generated_source_reingest_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p50_non_generated_source_reingest_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p50_non_generated_source_reingest_gate.v0",
        "date": DATE,
        "title": "FEF-P50 Non-Generated Source Re-ingest Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record a private reviewer response over P47/P48/P49/P50 or add branch/control-flow non-generated fixtures under a separate gate.",
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
            "# FEF-P50 Non-Generated Source Re-ingest Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P50 runs selected non-generated C/Rust source-derived re-ingest checks.",
            "The source fixtures decompile through eFrog, compile through Forge to C/Rust,",
            "re-ingest through eFrog, recompile to Python, and compare generated target runtime",
            "outputs against the re-ingested Python outputs over deterministic samples.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Source cases: `{summary['sourceCaseCount']}`",
            f"- Re-ingest packets: `{summary['packetCount']}`",
            f"- Packet samples: `{summary['packetSampleCount']}`",
            f"- Passes: `{summary['passCount']}`",
            f"- Source languages: `{', '.join(summary['sourceLanguages'])}`",
            f"- Generated targets: `{', '.join(summary['generatedTargetLanguages'])}`",
            f"- Recompiled targets: `{', '.join(summary['recompiledTargetLanguages'])}`",
            f"- Max abs error: `{summary['maxAbsError']:.3e}`",
            f"- Max rel error: `{summary['maxRelError']:.3e}`",
            "",
            "## Allowed Private Claims",
            "",
            *[f"- {claim}" for claim in payload["allowedPrivateClaims"]],
            "",
            "## Blocked Claims",
            "",
            *[f"- {claim}" for claim in payload["blockedClaims"]],
            "",
            "## Boundary",
            "",
            "- Selected non-generated source-derived generated C/Rust target re-ingest only.",
            "- No full non-generated source roundtrip claim.",
            "- No arbitrary C/Rust source-family claim.",
            "- No reviewer decision, package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "- No all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P50 packet schema")
    if packet["packetType"] != "fef_p50_source_derived_reingest_packet_v0":
        raise ValueError("invalid FEF-P50 packet type")
    if packet["sourceLanguage"] not in {"c", "rust"}:
        raise ValueError("FEF-P50 source language must be C or Rust")
    if packet["generatedTargetLanguage"] not in {"c", "rust"}:
        raise ValueError("FEF-P50 generated target must be C or Rust")
    if packet["recompiledTargetLanguage"] != "python":
        raise ValueError("FEF-P50 recompiled target must be Python")
    if packet["sourceFunctionCount"] != 1:
        raise ValueError("FEF-P50 source fixture must have one function")
    if packet["reingestedFunctionCount"] != 1:
        raise ValueError("FEF-P50 re-ingested target must have one function")
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
        raise ValueError("invalid FEF-P50 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P50 status")
    summary = payload["summary"]
    if summary["sourceCaseCount"] != 5:
        raise ValueError("expected five selected non-generated source cases")
    if summary["packetCount"] != 10:
        raise ValueError("expected ten source-derived re-ingest packets")
    if summary["passCount"] != summary["packetCount"]:
        raise ValueError("all FEF-P50 re-ingest packets must pass")
    if summary["sourceSampleCount"] != 23:
        raise ValueError("unexpected source sample count")
    if summary["packetSampleCount"] != 46:
        raise ValueError("unexpected packet sample count")
    if summary["sourceLanguages"] != ["c", "rust"]:
        raise ValueError("expected C/Rust source languages")
    if summary["generatedTargetLanguages"] != ["c", "rust"]:
        raise ValueError("expected C/Rust generated targets")
    if summary["recompiledTargetLanguages"] != ["python"]:
        raise ValueError("expected Python recompiled target")
    if summary["p49SemanticEvidenceAttached"] is not True:
        raise ValueError("P49 semantic evidence must be attached")
    if summary["selectedNonGeneratedSourceDerivedReingest"] is not True:
        raise ValueError("selected source-derived re-ingest should pass")
    for key in [
        "fullNonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "arbitrarySourceFamilyClaim",
        "reviewerDecisionRecorded",
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "allFreeTargetsRuntimeExecutionClaim",
        "allFreeTargetsRoundtripClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["reingestPackets"]:
        validate_packet(packet)
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p50_non_generated_source_reingest_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p50_non_generated_source_reingest_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p50_non_generated_source_reingest_gate.json"
    feed_path = command_feed_dir / f"fef_p50_non_generated_source_reingest_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p50_non_generated_source_reingest_gate")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p50_source_derived_reingest_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(
        args.out_dir,
        args.packet_dir,
        args.report_dir,
        args.evidence_dir,
        args.command_feed_dir,
    )
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P50_NON_GENERATED_SOURCE_REINGEST_GATE_OK")
    print(f"source_cases={built['payload']['summary']['sourceCaseCount']}")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"packet_samples={built['payload']['summary']['packetSampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
