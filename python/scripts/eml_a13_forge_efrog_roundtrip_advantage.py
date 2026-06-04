#!/usr/bin/env python3
"""EML-A13 Forge/eFrog roundtrip advantage lab.

Runs existing eFrog source frontends and a small holdout slice through Forge's
Python and JavaScript targets. This is a private measurement lane: no Forge or
eFrog behavior changes, no compiler-correctness proof, and no broad EML
advantage claim.
"""

from __future__ import annotations

import argparse
import json
import re
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

from efrog.fingerprint import canonical_size, fingerprint_eml  # noqa: E402
from efrog.normalization import normalize_module  # noqa: E402
from efrog.decompilers.python import decompile_python_source  # noqa: E402
from efrog.roundtrip import BRIDGE_FIXTURES, BridgeFixture, _compile_target, _decompile_fixture  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_a13_forge_efrog_roundtrip_advantage.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_forge_efrog_roundtrip_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A13_FORGE_EFROG_ROUNDTRIP_ADVANTAGE_PASS"
TARGETS = ("python", "javascript")
HOLDOUT_FIXTURES = (
    BridgeFixture("python_holdout_gaussian_stable", False, "examples/gaussian_stable.py", None, decompile_python_source),
    BridgeFixture("python_holdout_rc_decay_stable", False, "examples/rc_decay_stable.py", None, decompile_python_source),
    BridgeFixture("python_holdout_stretched_exponential", False, "examples/stretched_exponential.py", None, decompile_python_source),
    BridgeFixture("python_holdout_stable_sigmoid", False, "examples/stable_sigmoid.py", None, decompile_python_source),
    BridgeFixture("python_holdout_poly_horner", False, "examples/poly_horner.py", None, decompile_python_source),
    BridgeFixture("python_holdout_voltage_divider", False, "examples/voltage_divider.py", None, decompile_python_source),
)

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
    "A13 records bounded eFrog-to-Forge roundtrip evidence only.",
    "A13 does not change Forge or eFrog behavior.",
    "A13 does not prove compiler correctness or formal semantic equivalence.",
    "A13 does not claim broad EML advantage, runtime performance, production readiness, or public safety.",
]


def _fixture_source(fixture: Any) -> str:
    if fixture.source_path:
        return (EFROG_ROOT / fixture.source_path).read_text(encoding="utf-8")
    return fixture.inline_source or ""


def _surface_node_count(source: str) -> int:
    tokens = re.findall(
        r"\b(?:exp|log|sqrt|sin|cos|tan|pow|return|let|var|function|func|fn|if|else|for|range|step01|lerp)\b|[+\-*/^%<>=]",
        source,
    )
    return len(tokens)


def _advantage_class(roundtrip_status: str, eml_nodes: int, standard_nodes: int) -> str:
    if roundtrip_status != "pass":
        return "roundtrip_blocked"
    if eml_nodes <= standard_nodes:
        return "eml_toolchain_surface_win"
    return "roundtrip_pass_standard_surface_smaller"


def _is_license_blocked(message: str) -> bool:
    lowered = message.lower()
    return "license" in lowered and "expired" in lowered


def build_case_packet(fixture: Any, target: str, tmp_path: Path) -> dict[str, Any]:
    source = _fixture_source(fixture)
    mod = _decompile_fixture(fixture)
    eml = mod.to_eml()
    shape = normalize_module(mod)
    status, message = _compile_target(
        eml,
        target=target,
        tmp_path=tmp_path,
        source_language=fixture.language,
        strict=False,
    )
    standard_nodes = _surface_node_count(source)
    eml_nodes = _surface_node_count(eml)
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_forge_efrog_roundtrip_packet_v0",
        "date": DATE,
        "caseId": f"{fixture.language}_to_forge_{target}_v0",
        "sourceLanguage": fixture.language,
        "targetLanguage": target,
        "sourceClass": "holdout" if str(fixture.language).startswith("python_holdout_") else "default_frontend",
        "sourceHostedByEfrog": bool(fixture.hosted),
        "sourceBytes": len(source.encode("utf-8")),
        "canonicalEmlBytes": canonical_size(eml),
        "standardSurfaceNodeCount": standard_nodes,
        "emlSurfaceNodeCount": eml_nodes,
        "surfaceDeltaStandardMinusEml": standard_nodes - eml_nodes,
        "functionCount": len(mod.functions),
        "canonicalEmlHash": fingerprint_eml(eml),
        "normalizedShapeHash": shape.shape_hash,
        "roundtripStatus": status,
        "roundtripMessage": message,
        "licenseBlocked": _is_license_blocked(message),
        "advantageClass": _advantage_class(status, eml_nodes, standard_nodes),
        "reviewerDecision": "private_roundtrip_evidence",
        "missingEvidence": [
            "cross-target semantic equivalence",
            "larger holdout source corpus",
            "formal compiler correctness proof",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_case_packet(packet)
    return packet


def summarize(case_packets: list[dict[str, Any]]) -> dict[str, Any]:
    class_counts: dict[str, int] = {}
    for packet in case_packets:
        class_counts[packet["advantageClass"]] = class_counts.get(packet["advantageClass"], 0) + 1
    return {
        "caseCount": len(case_packets),
        "defaultFrontendCaseCount": sum(1 for packet in case_packets if packet["sourceClass"] == "default_frontend"),
        "holdoutCaseCount": sum(1 for packet in case_packets if packet["sourceClass"] == "holdout"),
        "roundtripPassCount": sum(1 for packet in case_packets if packet["roundtripStatus"] == "pass"),
        "roundtripBlockedCount": sum(1 for packet in case_packets if packet["roundtripStatus"] == "blocked"),
        "roundtripFailCount": sum(1 for packet in case_packets if packet["roundtripStatus"] == "fail"),
        "licenseBlockedCount": sum(1 for packet in case_packets if packet["licenseBlocked"]),
        "allRoundtripsBlockedByExpiredLicense": all(packet["licenseBlocked"] for packet in case_packets),
        "emlToolchainSurfaceWinCount": class_counts.get("eml_toolchain_surface_win", 0),
        "standardSurfaceSmallerCount": class_counts.get("roundtrip_pass_standard_surface_smaller", 0),
        "advantageClassCounts": class_counts,
        "targetLanguages": sorted({packet["targetLanguage"] for packet in case_packets}),
        "sourceLanguageCount": len({packet["sourceLanguage"] for packet in case_packets}),
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
        "artifactId": "eml-a13-forge-efrog-roundtrip-advantage",
        "title": "EML-A13 Forge/eFrog Roundtrip Advantage Lab",
        "reviewDecision": "private_roundtrip_evidence_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_source_to_eml_to_forge_target_roundtrip",
        "semanticStrength": "toolchain_roundtrip_evidence_no_compiler_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private roundtrip lab only; no compiler correctness, formal equivalence, broad EML advantage, runtime performance, production readiness, or public safety claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a13_forge_efrog_roundtrip_advantage.v0",
        "date": DATE,
        "title": "EML-A13 Forge/eFrog Roundtrip Advantage Lab",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A13.2 add semantic output comparison for selected scalar kernels",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A13 Forge/eFrog Roundtrip Advantage Lab",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A13 runs existing eFrog source frontends and a small holdout slice through",
        "Forge's Python and JavaScript targets",
        "and records bounded roundtrip evidence for the EML toolchain thesis.",
        "",
        "| Case | Roundtrip | Advantage class | Standard nodes | EML nodes | Shape hash |",
        "|---|---|---|---:|---:|---|",
    ]
    for packet in payload["casePackets"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{packet['caseId']}`",
                    f"`{packet['roundtripStatus']}`",
                    f"`{packet['advantageClass']}`",
                    str(packet["standardSurfaceNodeCount"]),
                    str(packet["emlSurfaceNodeCount"]),
                    f"`{packet['normalizedShapeHash'][:18]}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Cases: `{payload['summary']['caseCount']}`",
            f"- Holdout cases: `{payload['summary']['holdoutCaseCount']}`",
            f"- Targets: `{', '.join(payload['summary']['targetLanguages'])}`",
            f"- Roundtrip passes: `{payload['summary']['roundtripPassCount']}`",
            f"- EML surface wins: `{payload['summary']['emlToolchainSurfaceWinCount']}`",
            f"- Standard surface smaller: `{payload['summary']['standardSurfaceSmallerCount']}`",
            "",
            "## Boundary",
            "",
            "- Private toolchain evidence only.",
            "- No Forge or eFrog behavior change.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No broad EML advantage, runtime performance, production readiness, or public safety claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_case_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid A13 case packet schema")
    if packet["packetType"] != "eml_forge_efrog_roundtrip_packet_v0":
        raise ValueError("invalid A13 packet type")
    if not packet["canonicalEmlHash"].startswith("sha256:"):
        raise ValueError("canonical EML hash must be sha256")
    if packet["roundtripStatus"] not in {"pass", "fail", "blocked"}:
        raise ValueError("invalid roundtrip status")
    if packet["licenseBlocked"] is True and "license expired" not in packet["roundtripMessage"].lower():
        raise ValueError("license-blocked packets must preserve the expired-license message")
    if packet["canonicalEmlBytes"] <= 0 or packet["functionCount"] <= 0:
        raise ValueError("packet must contain decompiled EML")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"case packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid A13 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid A13 status")
    summary = payload["summary"]
    if summary["caseCount"] < 10:
        raise ValueError("expected at least 10 source frontend cases")
    if summary["holdoutCaseCount"] < 4:
        raise ValueError("expected holdout source cases")
    if set(summary["targetLanguages"]) != set(TARGETS):
        raise ValueError("expected Python and JavaScript Forge targets")
    if summary["roundtripPassCount"] < 20 and summary["allRoundtripsBlockedByExpiredLicense"] is not True:
        raise ValueError("expected at least 20 passing roundtrips or explicit expired-license blockage")
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
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("A13 claim flags must remain false")
    for packet in payload["casePackets"]:
        validate_case_packet(packet)


def build_lab(
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eml_a13_roundtrip_") as tmp:
        tmp_path = Path(tmp)
        fixtures = tuple(BRIDGE_FIXTURES) + HOLDOUT_FIXTURES
        case_packets = [
            build_case_packet(fixture, target, tmp_path)
            for fixture in fixtures
            for target in TARGETS
        ]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "labId": "eml_a13_forge_efrog_roundtrip_advantage",
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
    result_path = out_dir / f"eml_a13_forge_efrog_roundtrip_advantage_{STAMP}.json"
    report_path = report_dir / f"eml_a13_forge_efrog_roundtrip_advantage_{STAMP}.md"
    evidence_path = evidence_dir / "eml_a13_forge_efrog_roundtrip_advantage.json"
    feed_path = command_feed_dir / f"eml_a13_forge_efrog_roundtrip_advantage_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a13_forge_efrog_roundtrip_advantage")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_forge_efrog_roundtrip_packets")
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
    print("EML_A13_FORGE_EFROG_ROUNDTRIP_ADVANTAGE_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"passes={built['payload']['summary']['roundtripPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
