#!/usr/bin/env python3
"""FEF-P53 selected C if early-return branch lowering gate."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))
if str(EFROG_ROOT) not in sys.path:
    sys.path.insert(0, str(EFROG_ROOT))

from efrog.decompilers.c import decompile_c_source  # noqa: E402
from efrog.fingerprint import fingerprint_eml  # noqa: E402
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
SCHEMA_VERSION = "monogate.fef_p53_c_if_early_return_branch_lowering_gate.v0"
PACKET_SCHEMA_VERSION = "monogate.fef_p53_c_if_early_return_reingest_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P53_C_IF_EARLY_RETURN_BRANCH_LOWERING_GATE_PASS"

P51_PACKET = ROOT / "reports/evidence_packets/fef_p51_branch_control_flow_blocker_gate.json"

SOURCE = "double relu(double x) { if (x > 0.0) return x; return 0.0; }"
CASE_ID = "c_if_early_return_relu_v0"
SAMPLES = [{"args": [x], "labels": ["x"]} for x in [-2.0, -1.0e-12, 0.0, 1.0e-12, 2.0]]

CLAIM_FLAGS = {
    "selected_c_if_early_return_lowering_claim": False,
    "general_c_branch_support_claim": False,
    "c_if_statement_support_claim": False,
    "rust_if_support_claim": False,
    "branch_control_flow_general_claim": False,
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
    "FEF-P53 records a selected C if early-return lowering and re-ingest gate only.",
    "FEF-P53 does not claim general C branch/control-flow support.",
    "FEF-P53 does not claim C if-statement support.",
    "FEF-P53 does not claim Rust if support.",
    "FEF-P53 does not claim full non-generated source roundtrip.",
    "FEF-P53 does not claim full arbitrary C/Rust source roundtrip.",
    "FEF-P53 does not record reviewer approval or rejection.",
    "FEF-P53 does not publish a package.",
    "FEF-P53 does not enable checkout or commerce.",
    "FEF-P53 does not claim public readiness.",
    "FEF-P53 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P53 does not claim runtime performance.",
    "FEF-P53 does not claim all-free-target runtime execution or all-free-target roundtrip.",
    "FEF-P53 does not claim Verilog, Lean proof, zkproof, silicon, hardware, Pro-target, production, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_value(x: float) -> float:
    return x if x > 0.0 else 0.0


def compare_target(target: str, eml_path: Path, source_eml: str, tmp_path: Path) -> dict[str, Any]:
    target_ext = "c" if target == "c" else "rs"
    generated_path = tmp_path / f"{CASE_ID}_generated.{target_ext}"
    compile_target(eml_path, target, generated_path)

    reingested_mod = reingest_generated_target(target, generated_path)
    reingested_eml = reingested_mod.to_eml()
    reingested_eml_path = tmp_path / f"{CASE_ID}_{target}_reingested.eml"
    reingested_py_path = tmp_path / f"{CASE_ID}_{target}_reingested.py"
    reingested_eml_path.write_text(reingested_eml, encoding="utf-8")
    compile_target(reingested_eml_path, "python", reingested_py_path)

    if target == "c":
        generated_values = call_generated_c(generated_path, "relu", SAMPLES, tmp_path)
    elif target == "rust":
        generated_values = call_generated_rust(generated_path, "relu", SAMPLES, tmp_path)
    else:
        raise ValueError(f"unsupported FEF-P53 target: {target}")
    reingested_values = call_generated_python(
        reingested_py_path,
        "relu",
        SAMPLES,
        f"{CASE_ID}_{target}_reingested",
    )
    frames, max_abs, max_rel = compare_values(generated_values, reingested_values, SAMPLES)
    for frame in frames:
        x = frame["sample"]["args"][0]
        frame["values"] = {
            "sourceDerivedGeneratedTargetRuntime": frame["values"]["generatedTarget"],
            "reingestedRecompiledPython": frame["values"]["reingestedRecompiledPython"],
            "expectedIfEarlyReturnReference": expected_value(x),
        }
        frame["absErrorGeneratedVsExpectedReference"] = abs(
            frame["values"]["sourceDerivedGeneratedTargetRuntime"]
            - frame["values"]["expectedIfEarlyReturnReference"]
        )
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "fef_p53_c_if_early_return_reingest_packet_v0",
        "date": DATE,
        "caseId": f"{CASE_ID}_{target}_reingest",
        "sourceCaseId": CASE_ID,
        "sourceLanguage": "c",
        "sourceFeature": "if_early_return",
        "generatedTargetLanguage": target,
        "reingestedTargetLanguage": "eml",
        "recompiledTargetLanguage": "python",
        "functionName": "relu",
        "sourceEmlHash": fingerprint_eml(source_eml),
        "reingestedEmlHash": fingerprint_eml(reingested_eml),
        "sourceFunctionCount": 2,
        "reingestedFunctionCount": len(reingested_mod.functions),
        "sampleCount": len(SAMPLES),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "reingestStatus": "pass" if max_abs <= ATOL or max_rel <= RTOL else "fail",
        "frames": frames,
        "evidenceKind": "selected_c_if_early_return_source_derived_generated_target_reingest",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def build_payload() -> dict[str, Any]:
    p51_packet = read_json(P51_PACKET)
    with tempfile.TemporaryDirectory(prefix="fef_p53_c_if_early_return_") as tmp:
        tmp_path = Path(tmp)
        source_mod = decompile_c_source(SOURCE, source_path=f"{CASE_ID}.c")
        source_eml = source_mod.to_eml()
        source_eml_path = tmp_path / f"{CASE_ID}.eml"
        source_eml_path.write_text(source_eml, encoding="utf-8")
        packets = [
            compare_target("c", source_eml_path, source_eml, tmp_path),
            compare_target("rust", source_eml_path, source_eml, tmp_path),
        ]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p53-c-if-early-return-branch-lowering-gate",
        "decision": "selected_c_if_early_return_lowering_reingest_passed_general_branch_blocked",
        "sourceFixture": {
            "caseId": CASE_ID,
            "sourceLanguage": "c",
            "feature": "if_early_return",
            "source": SOURCE,
            "loweringForm": "affine_selector_with_step01_guard",
            "sourceEmlContains": ["fn step01", "clamp(", "step01(", "relu"],
        },
        "reingestPackets": packets,
        "summary": summarize(packets, p51_packet["semanticReview"]),
        "fefP51Link": {
            "path": str(P51_PACKET.relative_to(ROOT)),
            "reviewDecision": p51_packet["reviewDecision"],
        },
        "releaseGates": [
            {"id": "selected_c_if_early_return_lowering", "status": "pass"},
            {"id": "selected_c_if_early_return_generated_c_reingest", "status": "pass"},
            {"id": "selected_c_if_early_return_generated_rust_reingest", "status": "pass"},
            {"id": "c_if_statement_support", "status": "blocked"},
            {"id": "rust_if_support", "status": "blocked"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "full_non_generated_source_roundtrip_claim", "status": "blocked"},
            {"id": "private_reviewer_decision", "status": "not_recorded"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "compiler_correctness_proved", "status": "blocked"},
        ],
        "allowedPrivateClaims": [
            "One selected C if early-return fixture now lowers to a guarded affine selector.",
            "The selected C if early-return fixture emits generated C/Rust targets that re-ingest through eFrog and recompile to Python.",
            "The selected C/Rust generated target runtimes match re-ingested Python outputs over 10 packet-sample comparisons.",
            "P53 closes the P51 selected C if early-return blocker only; broader C if-statement forms and Rust if remain blocked.",
        ],
        "blockedClaims": [
            "general C branch/control-flow support is established",
            "C if-statement support is established",
            "Rust if support is established",
            "branch/control-flow re-ingest is generally supported",
            "full non-generated source roundtrip is supported",
            "full arbitrary C/Rust source roundtrip is supported",
            "arbitrary C/Rust source-family support is established",
            "Forge/eFrog is public-ready",
            "a package has been published",
            "checkout is enabled",
            "compiler correctness has been proved",
            "formal semantic equivalence has been proved",
            "runtime performance has been established",
        ],
        "nextMilestones": [
            "Add C if/else clamp lowering or Rust if-expression lowering under a separate gate.",
            "Regenerate a branch blocker inventory after the next frontend slice.",
            "Record private reviewer response over P47-P53 before changing release posture.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return copy.deepcopy(payload)


def summarize(packets: list[dict[str, Any]], p51_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "selectedCIfEarlyReturnLoweringPass": True,
        "sourceCaseCount": 1,
        "packetCount": len(packets),
        "passCount": sum(1 for packet in packets if packet["reingestStatus"] == "pass"),
        "failCount": sum(1 for packet in packets if packet["reingestStatus"] == "fail"),
        "packetSampleCount": sum(packet["sampleCount"] for packet in packets),
        "sourceLanguages": ["c"],
        "generatedTargetLanguages": sorted({packet["generatedTargetLanguage"] for packet in packets}),
        "recompiledTargetLanguages": sorted({packet["recompiledTargetLanguage"] for packet in packets}),
        "maxAbsError": max(packet["maxAbsError"] for packet in packets),
        "maxRelError": max(packet["maxRelError"] for packet in packets),
        "p51CurrentBlockedFixtureCount": p51_summary["blockedCount"],
        "p51CurrentLaterPhasePassCaseIds": p51_summary.get("laterPhasePassCaseIds", []),
        "p51CurrentBlockerClasses": p51_summary["blockerClasses"],
        "cIfEarlyReturnBlockerClosed": True,
        "cIfStatementSupportClaim": False,
        "rustIfSupportClaim": False,
        "generalBranchControlFlowSupportClaim": False,
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


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P53 C If Early-Return Branch Lowering Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_c_if_early_return_lowering_reingest_general_branch_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected C if early-return lowering and re-ingest only; no general C branch/control-flow support, C if-statement support, Rust if support, full source roundtrip, arbitrary source-family, package publication, checkout, public readiness, compiler correctness, formal equivalence, runtime performance, all-free-target runtime, all-free-target roundtrip, hardware, silicon, or proof claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P53 closes the selected P51 C if early-return blocker with an affine selector plus step01 lowering.",
            "Generated C and Rust targets re-ingest through eFrog and recompile to Python.",
            "Generated target runtimes match re-ingested Python outputs over 10 packet-sample comparisons.",
            "Broader C if-statement forms and Rust if remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p53_c_if_early_return_branch_lowering_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p53_c_if_early_return_branch_lowering_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p53_c_if_early_return_branch_lowering_gate.v0",
        "date": DATE,
        "title": "FEF-P53 C If Early-Return Branch Lowering Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Implement C if/else clamp lowering or Rust if-expression lowering under a separate gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Case | Generated target | Samples | Status | Max abs error | Max rel error |",
        "|---|---|---:|---|---:|---:|",
    ]
    for packet in payload["reingestPackets"]:
        rows.append(
            f"| `{packet['sourceCaseId']}` | `{packet['generatedTargetLanguage']}` | {packet['sampleCount']} | `{packet['reingestStatus']}` | {packet['maxAbsError']:.3e} | {packet['maxRelError']:.3e} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P53 C If Early-Return Branch Lowering Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P53 closes one narrow branch blocker: selected C if early-return expressions.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Selected C if early-return lowering pass: `{summary['selectedCIfEarlyReturnLoweringPass']}`",
            f"- Source cases: `{summary['sourceCaseCount']}`",
            f"- Re-ingest packets: `{summary['packetCount']}`",
            f"- Packet samples: `{summary['packetSampleCount']}`",
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
            "- Selected C if early-return lowering and re-ingest only.",
            "- No general C branch/control-flow support claim.",
            "- No C if-statement or Rust if support claim.",
            "- No full non-generated source roundtrip or arbitrary source-family claim.",
            "- No reviewer decision, package publication, checkout, or public-readiness claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid FEF-P53 packet schema")
    if packet["packetType"] != "fef_p53_c_if_early_return_reingest_packet_v0":
        raise ValueError("invalid FEF-P53 packet type")
    if packet["sourceLanguage"] != "c":
        raise ValueError("FEF-P53 source language must be C")
    if packet["sourceFeature"] != "if_early_return":
        raise ValueError("FEF-P53 source feature must be if_early_return")
    if packet["generatedTargetLanguage"] not in {"c", "rust"}:
        raise ValueError("FEF-P53 generated target must be C or Rust")
    if packet["recompiledTargetLanguage"] != "python":
        raise ValueError("FEF-P53 recompiled target must be Python")
    if packet["sourceFunctionCount"] != 2:
        raise ValueError("FEF-P53 source EML should include relu and step01")
    if packet["reingestedFunctionCount"] != 2:
        raise ValueError("FEF-P53 re-ingested target should include relu and step01")
    if packet["reingestStatus"] != "pass":
        raise ValueError(f"{packet['caseId']} re-ingest did not pass")
    for frame in packet["frames"]:
        if frame["withinTolerance"] is not True:
            raise ValueError(f"{packet['caseId']} frame outside tolerance")
        if frame["absErrorGeneratedVsExpectedReference"] > ATOL:
            raise ValueError(f"{packet['caseId']} frame missed if early-return reference")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P53 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P53 status")
    summary = payload["summary"]
    if summary["selectedCIfEarlyReturnLoweringPass"] is not True:
        raise ValueError("selected C if early-return lowering should pass")
    if summary["sourceCaseCount"] != 1:
        raise ValueError("expected one selected C if early-return source case")
    if summary["packetCount"] != 2:
        raise ValueError("expected generated C and Rust re-ingest packets")
    if summary["passCount"] != 2:
        raise ValueError("all P53 packets must pass")
    if summary["packetSampleCount"] != 10:
        raise ValueError("unexpected P53 packet sample count")
    if summary["generatedTargetLanguages"] != ["c", "rust"]:
        raise ValueError("expected C/Rust generated targets")
    if summary["recompiledTargetLanguages"] != ["python"]:
        raise ValueError("expected Python recompiled target")
    if summary["cIfEarlyReturnBlockerClosed"] is not True:
        raise ValueError("C if early-return blocker should be closed")
    for key in [
        "cIfStatementSupportClaim",
        "rustIfSupportClaim",
        "generalBranchControlFlowSupportClaim",
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
    result_path = out_dir / f"fef_p53_c_if_early_return_branch_lowering_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p53_c_if_early_return_branch_lowering_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p53_c_if_early_return_branch_lowering_gate.json"
    feed_path = command_feed_dir / f"fef_p53_c_if_early_return_branch_lowering_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p53_c_if_early_return_branch_lowering_gate")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/fef_p53_c_if_early_return_reingest_packets")
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
    print("FEF_P53_C_IF_EARLY_RETURN_BRANCH_LOWERING_GATE_OK")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"packet_samples={built['payload']['summary']['packetSampleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
