#!/usr/bin/env python3
"""EML-A14 Forge/eFrog evidence export UX.

Builds private developer-facing export packets from existing A13/A13.2/PCC10
evidence. This is export plumbing only: it does not change Forge or eFrog.
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

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_a14_forge_efrog_export_ux.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_forge_efrog_export_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A14_FORGE_EFROG_EXPORT_UX_PASS"

PATHS = {
    "a13": ROOT / "python/results/eml_a13_forge_efrog_roundtrip_advantage/eml_a13_forge_efrog_roundtrip_advantage_2026_05_29.json",
    "a13_2": ROOT / "python/results/eml_a13_2_semantic_output_comparison/eml_a13_2_semantic_output_comparison_2026_05_29.json",
    "pcc10": ROOT / "python/results/eml_advantage_pcc10_family_synthesis/eml_advantage_pcc10_family_synthesis_2026_05_29.json",
    "sprint_closure": ROOT / "python/results/eml_advantage_product_sprint_closure/eml_advantage_product_sprint_closure_2026_05_29.json",
}

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
    "proof_claim": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "A14 exports existing evidence into developer-facing packets only.",
    "A14 does not change Forge or eFrog compiler/decompiler behavior.",
    "A14 does not prove compiler correctness or formal semantic equivalence.",
    "A14 does not claim broad EML advantage, runtime performance, production readiness, certified safety, or public safety.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def family_for_case(case_id: str, pcc10: dict[str, Any]) -> dict[str, Any] | None:
    family_map = {
        "rc_decay_holdout_semantic_compare_v0": "rc_decay",
        "gaussian_stable_holdout_semantic_compare_v0": "gaussian",
        "gaussian_semantic_compare_v0": "gaussian",
        "stretched_exponential_holdout_semantic_compare_v0": "stretched_exponential",
        "stable_sigmoid_holdout_semantic_compare_v0": "stable_sigmoid",
        "sigmoid_semantic_compare_v0": "numpy_softplus",
        "voltage_divider_holdout_semantic_compare_v0": "clamp_guard",
    }
    family_id = family_map.get(case_id)
    if not family_id:
        return None
    for row in pcc10["families"]:
        if row["familyId"] == family_id:
            return row
    if family_id == "stretched_exponential":
        return {
            "familyId": "stretched_exponential",
            "surface": "stable_stretched_exponential",
            "finding": "semantic_search_representation_tie",
            "emlRole": "full_exponential_stretched_kernel_representation",
            "runtimeRecommendation": "standard_or_protected_runtime_until_benchmarked",
        }
    if family_id == "stable_sigmoid":
        return {
            "familyId": "stable_sigmoid",
            "surface": "stable_sigmoid_logistic",
            "finding": "bounded_transition_semantic_search_representation",
            "emlRole": "bounded_exponential_transition_representation",
            "runtimeRecommendation": "protected_branch_stable_runtime_for_large_ranges",
        }
    return None


def roundtrip_index(a13: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = {}
    for packet in a13["casePackets"]:
        rows.setdefault(packet["canonicalEmlHash"], []).append(packet)
    return rows


def export_packet(semantic_case: dict[str, Any], matching_roundtrips: list[dict[str, Any]], pcc10: dict[str, Any]) -> dict[str, Any]:
    family = family_for_case(semantic_case["caseId"], pcc10)
    sample_count = len(semantic_case["frames"])
    roundtrip_targets = sorted({row["targetLanguage"] for row in matching_roundtrips})
    target_hint = roundtrip_targets or ["javascript", "python"]
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_forge_efrog_export_packet_v0",
        "date": DATE,
        "exportId": f"{semantic_case['caseId']}_export_packet_v0",
        "sourceCaseId": semantic_case["caseId"],
        "functionName": semantic_case["functionName"],
        "sourcePath": semantic_case["sourcePath"],
        "canonicalEmlHash": semantic_case["canonicalEmlHash"],
        "efrogDecompileStatus": "existing_a13_2_input",
        "forgeTargets": target_hint,
        "roundtripCaseCount": len(matching_roundtrips),
        "roundtripPassCount": sum(1 for row in matching_roundtrips if row["roundtripStatus"] == "pass"),
        "roundtripLinkStatus": "linked_by_canonical_eml_hash" if matching_roundtrips else "semantic_comparison_only",
        "semanticSampleGridStatus": semantic_case["comparisonStatus"],
        "semanticSampleCount": sample_count,
        "maxAbsError": semantic_case["maxAbsError"],
        "maxRelError": semantic_case["maxRelError"],
        "emlSurfaceSummary": {
            "familyId": family["familyId"] if family else "unmapped",
            "surface": family["surface"] if family else "unmapped_semantic_case",
            "finding": family["finding"] if family else "semantic_export_only",
            "emlRole": family["emlRole"] if family else "case_level_export",
            "runtimeRecommendation": family["runtimeRecommendation"] if family else "standard_or_protected_runtime_until_benchmarked",
        },
        "machlibWitnessReferences": [
            {
                "name": "atlas_subtraction_boundary_witness",
                "path": "../machlib/foundations/MachLib/EMLAtlasWitness.lean",
                "appliesTo": "available_reference_only_not_required_for_this_export",
            },
            {
                "name": "eml_log_exp_subtraction_boundary",
                "path": "../machlib/foundations/MachLib/EML.lean",
                "appliesTo": "available_reference_only_not_required_for_this_export",
            },
        ],
        "exportActions": [
            "open_source_fixture",
            "inspect_eml_hash",
            "inspect_roundtrip_targets",
            "inspect_semantic_sample_frames",
            "copy_candidate_evidence_packet",
        ],
        "reviewerDecision": "private_export_packet_candidate",
        "blockedClaims": [
            "compiler_correctness",
            "formal_equivalence",
            "broad_eml_advantage",
            "runtime_performance",
            "production_toolchain",
            "certified_safety",
            "public_readiness",
        ],
        "missingEvidence": [
            "larger semantic sample grid",
            "non-Python source semantic comparison",
            "formal compiler correctness proof",
            "runtime benchmark before performance claims",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_export_packet(packet)
    return packet


def build_payload(packet_dir: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    a13 = read_json(PATHS["a13"])
    a13_2 = read_json(PATHS["a13_2"])
    pcc10 = read_json(PATHS["pcc10"])
    sprint_closure = read_json(PATHS["sprint_closure"])
    by_hash = roundtrip_index(a13)
    packets = [
        export_packet(case, by_hash.get(case["canonicalEmlHash"], []), pcc10)
        for case in a13_2["casePackets"]
    ]
    if packet_dir:
        packet_dir.mkdir(parents=True, exist_ok=True)
        for packet in packets:
            path = packet_dir / f"{packet['exportId']}_{STAMP}.json"
            path.write_text(json.dumps(packet, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-a14-forge-efrog-export-ux",
        "sourceEvidence": [str(path.relative_to(ROOT)) for path in PATHS.values()],
        "exportPacketIds": [packet["exportId"] for packet in packets],
        "builderPreset": {
            "artifactType": "compiler_decompiler",
            "packetType": PACKET_SCHEMA_VERSION,
            "defaultReviewerAction": "Keep private; inspect source, EML hash, roundtrip targets, sample frames, and blocked claims.",
            "defaultNextStep": "Expand the sample grid or attach this export packet to a private Glass Box evidence mount.",
        },
        "summary": {
            "exportPacketCount": len(packets),
            "semanticCaseCount": a13_2["summary"]["caseCount"],
            "semanticPassCount": a13_2["summary"]["passCount"],
            "roundtripCaseCount": a13["summary"]["caseCount"],
            "roundtripPassCount": a13["summary"]["roundtripPassCount"],
            "roundtripLinkedExportCount": sum(1 for packet in packets if packet["roundtripLinkStatus"] == "linked_by_canonical_eml_hash"),
            "semanticOnlyExportCount": sum(1 for packet in packets if packet["roundtripLinkStatus"] == "semantic_comparison_only"),
            "targetLanguageCount": len(a13["summary"]["targetLanguages"]),
            "familySynthesisSourceCount": pcc10["summary"]["sourceFamilyCount"],
            "sprintClosureHandoffReadyCount": sprint_closure["summary"]["handoffReadyCount"],
            "forgeBehaviorChanged": False,
            "efrogBehaviorChanged": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "broadEmlAdvantageClaim": False,
            "runtimePerformanceClaim": False,
            "publicReady": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload, packets)
    return payload, packets


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a14-forge-efrog-export-ux",
        "title": "EML-A14 Forge/eFrog Evidence Export UX",
        "reviewDecision": "private_export_workflow_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_export_over_existing_a13_evidence",
        "semanticStrength": "developer_export_packets_no_compiler_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private export UX only; no Forge/eFrog behavior change, compiler correctness, formal equivalence, broad EML advantage, runtime performance, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Exports eight semantic sample-grid cases into developer-facing packets.",
            "Links each export to matching roundtrip target evidence by canonical EML hash.",
            "Carries PCC10 family interpretation and blocked claims into the UX layer.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a14_forge_efrog_export_ux.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a14_forge_efrog_export_ux.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a14_forge_efrog_export_ux.v0",
        "date": DATE,
        "title": "EML-A14 Forge/eFrog Evidence Export UX",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Mount selected A14 export packets into Glass Box after the engine worktree is coordinated.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any], packets: list[dict[str, Any]]) -> str:
    lines = [
        "# EML-A14 Forge/eFrog Evidence Export UX",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A14 turns existing A13/A13.2/PCC10 evidence into private developer-facing export packets.",
        "It is not a compiler, decompiler, proof, runtime, or public product claim.",
        "",
        "| Export | Function | Family | Semantic status | Samples | Roundtrip targets |",
        "|---|---|---|---|---:|---|",
    ]
    for packet in packets:
        lines.append(
            f"| `{packet['exportId']}` | `{packet['functionName']}` | "
            f"`{packet['emlSurfaceSummary']['familyId']}` | `{packet['semanticSampleGridStatus']}` | "
            f"{packet['semanticSampleCount']} | `{','.join(packet['forgeTargets'])}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Export packets: `{summary['exportPacketCount']}`",
            f"- Semantic cases: `{summary['semanticCaseCount']}`",
            f"- Semantic passes: `{summary['semanticPassCount']}`",
            f"- Roundtrip cases available: `{summary['roundtripCaseCount']}`",
            f"- Roundtrip passes available: `{summary['roundtripPassCount']}`",
            "",
            "## Boundary",
            "",
            "- No Forge/eFrog behavior change.",
            "- No compiler correctness or formal equivalence claim.",
            "- No broad EML advantage or runtime performance claim.",
            "- No deployment or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_export_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid export packet schema")
    if packet["semanticSampleGridStatus"] != "pass":
        raise ValueError("export packet requires passing semantic sample-grid status")
    if packet["roundtripPassCount"] != packet["roundtripCaseCount"]:
        raise ValueError("all linked roundtrip rows must pass")
    if packet["roundtripLinkStatus"] not in {"linked_by_canonical_eml_hash", "semantic_comparison_only"}:
        raise ValueError("invalid roundtrip link status")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any], packets: list[dict[str, Any]]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["exportPacketCount"] != 8:
        raise ValueError("expected eight export packets")
    if summary["semanticPassCount"] != summary["semanticCaseCount"]:
        raise ValueError("all semantic cases must pass")
    if summary["roundtripPassCount"] != summary["roundtripCaseCount"]:
        raise ValueError("all A13 roundtrip cases must pass")
    for key in [
        "forgeBehaviorChanged",
        "efrogBehaviorChanged",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "broadEmlAdvantageClaim",
        "runtimePerformanceClaim",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    if len({packet["exportId"] for packet in packets}) != len(packets):
        raise ValueError("export ids must be unique")
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
    result_path = out_dir / f"eml_a14_forge_efrog_export_ux_{STAMP}.json"
    report_path = report_dir / f"eml_a14_forge_efrog_export_ux_{STAMP}.md"
    evidence_path = evidence_dir / "eml_a14_forge_efrog_export_ux.json"
    feed_path = command_feed_dir / f"eml_a14_forge_efrog_export_ux_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a14_forge_efrog_export_ux")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_forge_efrog_export_packets")
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
    print("EML_A14_FORGE_EFROG_EXPORT_UX_OK")
    print(f"exports={built['payload']['summary']['exportPacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
