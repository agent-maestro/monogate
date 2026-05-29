#!/usr/bin/env python3
"""EML-S20 style atlas.

Classifies existing Forge/eFrog export packets into bounded "EML style" lanes.
This is vocabulary and review plumbing over existing evidence, not a new
compiler, decompiler, proof, benchmark, or public claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_a14_forge_efrog_export_ux import build_payload as build_a14_payload  # noqa: E402
from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_s20_style_atlas.v0"
STYLE_PACKET_SCHEMA_VERSION = "monogate.eml_style_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_S20_STYLE_ATLAS_PASS"

PCC10_PATH = ROOT / "python/results/eml_advantage_pcc10_family_synthesis/eml_advantage_pcc10_family_synthesis_2026_05_29.json"
A17_PATH = ROOT / "python/results/eml_a17_private_review_dry_run/eml_a17_private_review_dry_run_2026_05_29.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "style_generalization_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "formal_proof_claim": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "engine_behavior_changed": False,
    "machlib_source_changed": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "S20 defines a private EML style vocabulary over existing A14/PCC10 evidence only.",
    "S20 does not claim broad EML advantage, runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, or public readiness.",
    "S20 does not change Forge, eFrog, MachLib, Monogate Engine, or public surfaces.",
    "S20 classifications are review aids; they are not mathematical proofs or source-family generalization claims.",
]

STYLE_DEFINITIONS = {
    "eml_native": {
        "meaning": "The core expression shape is directly represented by an EML exponential/log boundary.",
        "reviewRule": "Treat EML as the search/semantic representation; still require runtime and domain evidence before claiming performance or safety.",
    },
    "eml_partial": {
        "meaning": "EML captures a meaningful substructure, but another operator family remains essential.",
        "reviewRule": "Keep EML as an explanatory/search component and preserve the non-EML surface explicitly.",
    },
    "guard_owned": {
        "meaning": "Piecewise, branch, or boundary semantics dominate the artifact.",
        "reviewRule": "Route to guard grammar before any EML lowering or runtime claim.",
    },
    "standard_preferred": {
        "meaning": "Standard or protected math is currently the preferred runtime or source-facing form.",
        "reviewRule": "Use EML only as optional semantic annotation unless new evidence changes the decision.",
    },
    "semantic_only": {
        "meaning": "The case has sample-grid evidence but no canonical Forge/eFrog roundtrip link.",
        "reviewRule": "Do not use as roundtrip evidence; require linked hash evidence before toolchain claims.",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def style_for_packet(packet: dict[str, Any]) -> tuple[str, list[str], str]:
    family_id = packet["emlSurfaceSummary"]["familyId"]
    finding = packet["emlSurfaceSummary"]["finding"]
    role = packet["emlSurfaceSummary"]["emlRole"]
    runtime = packet["emlSurfaceSummary"]["runtimeRecommendation"]
    tags: list[str] = []

    if family_id in {"rc_decay", "gaussian"} and role.startswith("full_exponential"):
        primary = "eml_native"
        rationale = "The main surface is an exponential envelope/kernel already represented by the EML boundary."
    elif family_id in {"damped_wave", "numpy_softplus"} or "partial" in finding:
        primary = "eml_partial"
        rationale = "EML covers a useful substructure, but another surface or protected form remains required."
    elif family_id == "clamp_guard" or "guard" in finding or "guard" in role:
        primary = "guard_owned"
        rationale = "The meaningful behavior is the guarded branch/boundary, so guard grammar owns the case."
    else:
        primary = "standard_preferred"
        rationale = "No current family-level EML role is established; standard/protected form remains preferred."

    if "protected" in runtime or "standard" in runtime:
        tags.append("standard_preferred")
    if packet["roundtripLinkStatus"] == "semantic_comparison_only":
        tags.append("semantic_only")
    if primary not in tags:
        tags.insert(0, primary)

    return primary, tags, rationale


def style_packet(packet: dict[str, Any]) -> dict[str, Any]:
    primary, tags, rationale = style_for_packet(packet)
    row = {
        "schemaVersion": STYLE_PACKET_SCHEMA_VERSION,
        "packetType": "eml_style_packet_v0",
        "date": DATE,
        "stylePacketId": f"{packet['sourceCaseId']}_style_packet_v0",
        "sourceExportId": packet["exportId"],
        "sourceCaseId": packet["sourceCaseId"],
        "functionName": packet["functionName"],
        "sourcePath": packet["sourcePath"],
        "canonicalEmlHash": packet["canonicalEmlHash"],
        "familyId": packet["emlSurfaceSummary"]["familyId"],
        "surface": packet["emlSurfaceSummary"]["surface"],
        "finding": packet["emlSurfaceSummary"]["finding"],
        "emlRole": packet["emlSurfaceSummary"]["emlRole"],
        "runtimeRecommendation": packet["emlSurfaceSummary"]["runtimeRecommendation"],
        "roundtripLinkStatus": packet["roundtripLinkStatus"],
        "semanticSampleGridStatus": packet["semanticSampleGridStatus"],
        "semanticSampleCount": packet["semanticSampleCount"],
        "primaryStyle": primary,
        "styleTags": tags,
        "styleRationale": rationale,
        "reviewInstruction": STYLE_DEFINITIONS[primary]["reviewRule"],
        "blockedClaims": [
            "broad_eml_advantage",
            "runtime_performance",
            "compiler_correctness",
            "formal_equivalence",
            "style_generalization",
            "public_readiness",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_style_packet(row)
    return row


def build_payload(packet_dir: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    a14_payload, a14_packets = build_a14_payload()
    pcc10 = read_json(PCC10_PATH)
    a17 = read_json(A17_PATH)
    packets = [style_packet(packet) for packet in a14_packets]
    if packet_dir:
        packet_dir.mkdir(parents=True, exist_ok=True)
        for packet in packets:
            path = packet_dir / f"{packet['stylePacketId']}_{STAMP}.json"
            path.write_text(json.dumps(packet, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")

    primary_counts = {style: 0 for style in STYLE_DEFINITIONS}
    tag_counts = {style: 0 for style in STYLE_DEFINITIONS}
    for packet in packets:
        primary_counts[packet["primaryStyle"]] += 1
        for tag in packet["styleTags"]:
            tag_counts[tag] += 1

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-s20-style-atlas",
        "styleDefinitions": STYLE_DEFINITIONS,
        "sourceEvidence": [
            "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
            "python/results/eml_forge_efrog_export_packets/*_2026_05_29.json",
            str(PCC10_PATH.relative_to(ROOT)),
            str(A17_PATH.relative_to(ROOT)),
        ],
        "stylePacketIds": [packet["stylePacketId"] for packet in packets],
        "summary": {
            "stylePacketCount": len(packets),
            "sourceExportPacketCount": a14_payload["summary"]["exportPacketCount"],
            "pcc10SourceFamilyCount": pcc10["summary"]["sourceFamilyCount"],
            "a17CandidatePacketCount": a17["summary"]["candidateReviewPacketCount"],
            "primaryStyleCounts": primary_counts,
            "styleTagCounts": tag_counts,
            "emlNativePrimaryCount": primary_counts["eml_native"],
            "emlPartialPrimaryCount": primary_counts["eml_partial"],
            "guardOwnedPrimaryCount": primary_counts["guard_owned"],
            "standardPreferredPrimaryCount": primary_counts["standard_preferred"],
            "semanticOnlyTagCount": tag_counts["semantic_only"],
            "roundtripLinkedCount": sum(1 for packet in packets if packet["roundtripLinkStatus"] == "linked_by_canonical_eml_hash"),
            "semanticOnlyCount": sum(1 for packet in packets if packet["roundtripLinkStatus"] == "semantic_comparison_only"),
            "publicReady": False,
            "styleGeneralizationClaim": False,
            "broadEmlAdvantageClaim": False,
            "runtimePerformanceClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextResearchQuestion": "Use the style atlas to choose the next EML-native holdout instead of expanding every surface equally.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload, packets)
    return payload, packets


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-s20-style-atlas",
        "title": "EML-S20 Style Atlas",
        "reviewDecision": "private_review_vocabulary_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_classification_over_existing_a14_pcc10_evidence",
        "semanticStrength": "style_classifier_no_new_performance_or_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private EML style vocabulary only; no broad EML advantage, runtime performance, compiler correctness, formal equivalence, proof, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Separates EML-native, EML-partial, guard-owned, standard-preferred, and semantic-only cases.",
            "Classifies six existing Forge/eFrog export packets without changing the compiler or decompiler.",
            "Turns vague EML advantage language into reviewable style decisions.",
        ],
        "validationCommands": [
            "python python/scripts/eml_s20_style_atlas.py --build --strict",
            "python -m pytest -q python/tests/test_eml_s20_style_atlas.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_s20_style_atlas.v0",
        "date": DATE,
        "title": "EML-S20 Style Atlas",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Choose the next holdout from an EML-native lane and keep guard-owned cases in guard grammar.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any], packets: list[dict[str, Any]]) -> str:
    lines = [
        "# EML-S20 Style Atlas",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "S20 defines a practical vocabulary for the phrase \"EML style\" using existing A14/PCC10 evidence.",
        "It is a private review artifact, not a proof, benchmark, compiler change, deployment, or public claim.",
        "",
        "## Lay Of The Land",
        "",
        "- Evidence infrastructure is now stable enough to carry private candidate packets, saved drafts, and reviewer decisions.",
        "- Forge/eFrog have export packets and sample-grid evidence, but not compiler-correctness or formal-equivalence proof.",
        "- EML looks strongest as a compact semantic/search representation for exponential/log-shaped surfaces.",
        "- Standard or protected math still owns many runtime and stability decisions.",
        "- Guarded or piecewise behavior belongs in guard grammar before any EML lowering is considered.",
        "",
        "## Style Classes",
        "",
    ]
    for style, definition in payload["styleDefinitions"].items():
        lines.extend(
            [
                f"### `{style}`",
                "",
                definition["meaning"],
                "",
                f"Review rule: {definition['reviewRule']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Classified Packets",
            "",
            "| Source case | Family | Primary style | Tags | Link | Review instruction |",
            "|---|---|---|---|---|---|",
        ]
    )
    for packet in packets:
        lines.append(
            f"| `{packet['sourceCaseId']}` | `{packet['familyId']}` | `{packet['primaryStyle']}` | "
            f"`{', '.join(packet['styleTags'])}` | `{packet['roundtripLinkStatus']}` | {packet['reviewInstruction']} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Style packets: `{summary['stylePacketCount']}`",
            f"- EML-native primary cases: `{summary['emlNativePrimaryCount']}`",
            f"- EML-partial primary cases: `{summary['emlPartialPrimaryCount']}`",
            f"- Guard-owned primary cases: `{summary['guardOwnedPrimaryCount']}`",
            f"- Standard-preferred primary cases: `{summary['standardPreferredPrimaryCount']}`",
            f"- Semantic-only tagged cases: `{summary['semanticOnlyTagCount']}`",
            "",
            "## Boundary",
            "",
            "- No broad EML advantage claim.",
            "- No runtime performance claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No proof, deployment, package publish, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_style_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != STYLE_PACKET_SCHEMA_VERSION:
        raise ValueError("invalid style packet schema")
    if packet["primaryStyle"] not in STYLE_DEFINITIONS:
        raise ValueError("invalid primary style")
    if packet["primaryStyle"] not in packet["styleTags"]:
        raise ValueError("primary style must be included in style tags")
    if packet["semanticSampleGridStatus"] != "pass":
        raise ValueError("style packet requires passing semantic sample grid")
    if packet["roundtripLinkStatus"] not in {"linked_by_canonical_eml_hash", "semantic_comparison_only"}:
        raise ValueError("invalid roundtrip link status")
    for tag in packet["styleTags"]:
        if tag not in STYLE_DEFINITIONS:
            raise ValueError(f"unknown style tag: {tag}")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any], packets: list[dict[str, Any]]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["stylePacketCount"] != 6:
        raise ValueError("expected six style packets")
    if summary["sourceExportPacketCount"] != summary["stylePacketCount"]:
        raise ValueError("style packets must match source export packets")
    if summary["emlNativePrimaryCount"] < 2:
        raise ValueError("expected at least two EML-native cases from current evidence")
    if summary["guardOwnedPrimaryCount"] < 1:
        raise ValueError("expected at least one guard-owned case")
    if summary["semanticOnlyTagCount"] < 2:
        raise ValueError("expected at least two semantic-only tagged cases")
    for key in [
        "publicReady",
        "styleGeneralizationClaim",
        "broadEmlAdvantageClaim",
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    if len({packet["stylePacketId"] for packet in packets}) != len(packets):
        raise ValueError("style packet ids must be unique")
    for packet in packets:
        validate_style_packet(packet)
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload, packets = build_payload(packet_dir)
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_s20_style_atlas_{STAMP}.json"
    report_path = report_dir / f"eml_s20_style_atlas_{STAMP}.md"
    evidence_path = evidence_dir / "eml_s20_style_atlas.json"
    feed_path = command_feed_dir / f"eml_s20_style_atlas_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload, packets), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "packets": packets,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
        "packet_dir": str(packet_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_s20_style_atlas")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_style_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"], built["packets"])
    print("EML_S20_STYLE_ATLAS_OK")
    print(f"style_packets={built['payload']['summary']['stylePacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
