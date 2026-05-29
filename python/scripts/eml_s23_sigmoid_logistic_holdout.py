#!/usr/bin/env python3
"""EML-S23 sigmoid/logistic dedicated holdout.

S23 executes the S22-selected sigmoid/logistic source-family promotion. It
records stable-source evidence, Forge/eFrog linkage, and bounded-output stress
profiles. This is private research evidence only: no broad advantage, runtime
performance, compiler correctness, formal equivalence, or public-readiness
claim.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_s23_sigmoid_logistic_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_s23_sigmoid_logistic_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_S23_SIGMOID_LOGISTIC_HOLDOUT_PASS"

PATHS = {
    "s22": ROOT / "python/results/eml_s22_source_family_generalization_map/eml_s22_source_family_generalization_map_2026_05_29.json",
    "a13": ROOT / "python/results/eml_a13_forge_efrog_roundtrip_advantage/eml_a13_forge_efrog_roundtrip_advantage_2026_05_29.json",
    "a13_2": ROOT / "python/results/eml_a13_2_semantic_output_comparison/eml_a13_2_semantic_output_comparison_2026_05_29.json",
    "a14": ROOT / "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
    "s20": ROOT / "python/results/eml_s20_style_atlas/eml_s20_style_atlas_2026_05_29.json",
}

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "sigmoid_generalization_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "formal_proof_claim": False,
    "certified_safety_claim": False,
    "production_toolchain_claim": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "machlib_source_changed": False,
    "engine_behavior_changed": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "S23 is one dedicated sigmoid/logistic holdout, not a broad source-family benchmark.",
    "S23 does not prove broad EML advantage, sigmoid generalization, runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, or public readiness.",
    "S23 records stable-source and sample-grid evidence only.",
    "The stable sigmoid fixture is deterministic software evidence, not biological, ML, finance, hardware, or production evidence.",
]

CRITERIA = {
    "profileCount": 4,
    "finiteRatioPass": 1.0,
    "maxAbsErrorPass": 1.0e-12,
    "maxRelErrorPass": 1.0e-12,
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def clamp60(x: np.ndarray) -> np.ndarray:
    return (np.abs(x + 60.0) - np.abs(x - 60.0)) / 2.0


def stable_sigmoid_source(x: np.ndarray) -> np.ndarray:
    x_safe = clamp60(x)
    return 1.0 / (1.0 + np.exp(-x_safe))


def eml_sigmoid_form(x: np.ndarray) -> np.ndarray:
    x_safe = clamp60(x)
    return 1.0 / (1.0 + eml(-x_safe, 1.0))


def naive_sigmoid_or_nan(x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore"):
        return 1.0 / (1.0 + np.exp(-x))


def deterministic_noise(count: int, *, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=count).astype(np.float64)


def profile_specs() -> list[dict[str, Any]]:
    count = 2048
    safe = np.linspace(-40.0, 40.0, count)
    transition = np.linspace(-8.0, 8.0, count)
    noisy = transition + deterministic_noise(count, seed=2301, scale=0.025)
    boundary = np.concatenate([
        np.linspace(-1000.0, -60.0, count // 2),
        np.linspace(60.0, 1000.0, count // 2),
    ]).astype(np.float64)
    return [
        {"profile": "safe_sigmoid_grid", "noiseKind": "none", "x": safe},
        {"profile": "transition_sigmoid_grid", "noiseKind": "transition", "x": transition},
        {"profile": "noisy_input_sigmoid_grid", "noiseKind": "input_perturbation", "x": noisy},
        {"profile": "overflow_boundary_sigmoid_grid", "noiseKind": "overflow_boundary", "x": boundary},
    ]


def agreement_metric(observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(observed) & np.isfinite(reference)
    errors = np.abs(observed[finite] - reference[finite])
    rel = errors / np.maximum(np.abs(reference[finite]), 1.0e-300)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    finite_ratio = float(np.mean(np.isfinite(observed)))
    return {
        "finiteRatio": finite_ratio,
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "meanAbsError": float(np.mean(errors)) if errors.size else float("inf"),
        "pass": bool(
            finite_ratio >= CRITERIA["finiteRatioPass"]
            and max_abs <= CRITERIA["maxAbsErrorPass"]
            and max_rel <= CRITERIA["maxRelErrorPass"]
        ),
    }


def profile_result(spec: dict[str, Any]) -> dict[str, Any]:
    x = spec["x"].astype(np.float64)
    source = stable_sigmoid_source(x)
    eml_observed = eml_sigmoid_form(x)
    naive = naive_sigmoid_or_nan(x)
    agreement = agreement_metric(eml_observed, source)
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "sampleCount": int(x.size),
        "inputRanges": {"x": [float(np.min(x)), float(np.max(x))]},
        "clampRange": [-60.0, 60.0],
        "emlShapedVsSource": agreement,
        "sourceFiniteRatio": float(np.mean(np.isfinite(source))),
        "sourceOutputRange": [float(np.min(source)), float(np.max(source))],
        "naiveFiniteRatio": float(np.mean(np.isfinite(naive))),
        "boundedOutputValid": bool(np.all((source >= 0.0) & (source <= 1.0))),
        "overflowBoundaryProfile": spec["noiseKind"] == "overflow_boundary",
        "decision": "bounded_transition_semantic_tie" if agreement["pass"] else "blocked",
    }


def case_packets_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {packet["caseId"]: packet for packet in payload["casePackets"]}


def export_packets_by_case() -> dict[str, dict[str, Any]]:
    packet_dir = ROOT / "python/results/eml_forge_efrog_export_packets"
    out: dict[str, dict[str, Any]] = {}
    for path in packet_dir.glob(f"*_{STAMP}.json"):
        packet = read_json(path)
        out[packet["sourceCaseId"]] = packet
    return out


def style_packets_by_family() -> dict[str, dict[str, Any]]:
    packet_dir = ROOT / "python/results/eml_style_packets"
    out: dict[str, dict[str, Any]] = {}
    for path in packet_dir.glob(f"*_{STAMP}.json"):
        packet = read_json(path)
        out[packet["familyId"]] = packet
    return out


def stable_roundtrip_packets(a13: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        packet for packet in a13["casePackets"]
        if packet["sourceLanguage"] == "python_holdout_stable_sigmoid"
    ]


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_specs()]
    pass_count = sum(1 for profile in profiles if profile["emlShapedVsSource"]["pass"])
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_s23_sigmoid_logistic_holdout_packet_v0",
        "date": DATE,
        "caseId": "stable_sigmoid_logistic_holdout_v0",
        "sourceFamily": "stable_sigmoid",
        "sourcePath": "efrog/examples/stable_sigmoid.py",
        "standardForm": "1 / (1 + exp(-clamp60(x)))",
        "emlForm": "1 / (1 + eml(-clamp60(x), 1))",
        "clampFormula": "clamp60(x) = (abs(x + 60) - abs(x - 60)) / 2",
        "runtimeWitnesses": [
            "stable_sigmoid_finite_exp_clamp",
            "stable_sigmoid_bounded_output",
        ],
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "passingProfiles": pass_count,
            "blockedProfiles": len(profiles) - pass_count,
            "sampleCountTotal": sum(profile["sampleCount"] for profile in profiles),
            "overflowBoundaryProfileCount": sum(1 for profile in profiles if profile["overflowBoundaryProfile"]),
            "allProfilesPass": pass_count == len(profiles),
            "allProfilesBounded": all(profile["boundedOutputValid"] for profile in profiles),
            "runtimeWitnessedObligationCount": 2,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "runtimePerformanceClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_holdout_packet(packet)
    return packet


def build_payload() -> dict[str, Any]:
    s22 = read_json(PATHS["s22"])
    a13 = read_json(PATHS["a13"])
    a13_2 = read_json(PATHS["a13_2"])
    a14 = read_json(PATHS["a14"])
    s20 = read_json(PATHS["s20"])
    semantic_cases = case_packets_by_id(a13_2)
    exports = export_packets_by_case()
    styles = style_packets_by_family()
    roundtrips = stable_roundtrip_packets(a13)
    holdout = build_holdout_packet()
    semantic_case = semantic_cases["stable_sigmoid_holdout_semantic_compare_v0"]
    export_packet = exports["stable_sigmoid_holdout_semantic_compare_v0"]
    style_packet = styles["stable_sigmoid"]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-s23-sigmoid-logistic-holdout",
        "selectedFrom": "eml-s22-source-family-generalization-map",
        "sourceEvidence": [str(path.relative_to(ROOT)) for path in PATHS.values()],
        "s22SelectedPromotionFamily": s22["summary"]["selectedPromotionFamily"],
        "a13RoundtripPackets": [
            {
                "caseId": packet["caseId"],
                "targetLanguage": packet["targetLanguage"],
                "roundtripStatus": packet["roundtripStatus"],
                "canonicalEmlHash": packet["canonicalEmlHash"],
            }
            for packet in roundtrips
        ],
        "a13_2SemanticCase": {
            "caseId": semantic_case["caseId"],
            "sampleCount": semantic_case["sampleCount"],
            "comparisonStatus": semantic_case["comparisonStatus"],
            "maxAbsError": semantic_case["maxAbsError"],
            "maxRelError": semantic_case["maxRelError"],
        },
        "a14Export": {
            "exportId": export_packet["exportId"],
            "roundtripLinkStatus": export_packet["roundtripLinkStatus"],
            "familyId": export_packet["emlSurfaceSummary"]["familyId"],
            "runtimeRecommendation": export_packet["emlSurfaceSummary"]["runtimeRecommendation"],
        },
        "s20Style": {
            "stylePacketId": style_packet["stylePacketId"],
            "primaryStyle": style_packet["primaryStyle"],
            "styleTags": style_packet["styleTags"],
        },
        "holdoutPacket": holdout,
        "summary": {
            "sourceFamily": "stable_sigmoid",
            "profileCount": holdout["summary"]["profileCount"],
            "passingProfiles": holdout["summary"]["passingProfiles"],
            "sampleCountTotal": holdout["summary"]["sampleCountTotal"],
            "roundtripPacketCount": len(roundtrips),
            "roundtripPassCount": sum(1 for packet in roundtrips if packet["roundtripStatus"] == "pass"),
            "semanticComparisonPass": semantic_case["comparisonStatus"] == "pass",
            "exportRoundtripLinked": export_packet["roundtripLinkStatus"] == "linked_by_canonical_eml_hash",
            "s20PrimaryStyle": style_packet["primaryStyle"],
            "runtimeWitnessedObligationCount": holdout["summary"]["runtimeWitnessedObligationCount"],
            "publicReady": False,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "sigmoidGeneralizationClaim": False,
            "runtimePerformanceClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextResearchQuestion": "Compare stable sigmoid against protected sigmoid/logaddexp-style runtimes before any performance or production claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    _ = a14, s20
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-s23-sigmoid-logistic-holdout",
        "title": "EML-S23 Sigmoid/Logistic Dedicated Holdout",
        "reviewDecision": "private_sigmoid_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_sample_grid_and_existing_toolchain_artifacts",
        "semanticStrength": "single_sigmoid_holdout_no_generalization_or_runtime_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private sigmoid/logistic holdout only; no broad EML advantage, source-family generalization, runtime performance, compiler correctness, formal equivalence, proof, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Executes the S22-selected sigmoid/logistic promotion.",
            "Uses a stable clamp60 exponent input to keep exp finite.",
            "Links stable sigmoid to A13, A13.2, A14, and S20 evidence.",
        ],
        "validationCommands": [
            "python python/scripts/eml_s23_sigmoid_logistic_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_s23_sigmoid_logistic_holdout.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_s23_sigmoid_logistic_holdout.v0",
        "date": DATE,
        "title": "EML-S23 Sigmoid/Logistic Dedicated Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": payload["nextResearchQuestion"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-S23 Sigmoid/Logistic Dedicated Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "S23 executes the S22-selected sigmoid/logistic source-family promotion.",
        "It is private holdout evidence, not a proof, runtime benchmark, compiler correctness result, or public claim.",
        "",
        "## Toolchain Linkage",
        "",
        f"- A13 roundtrip packets: `{payload['summary']['roundtripPacketCount']}`",
        f"- A13 roundtrip passes: `{payload['summary']['roundtripPassCount']}`",
        f"- A13.2 semantic comparison pass: `{payload['summary']['semanticComparisonPass']}`",
        f"- A14 export linked: `{payload['summary']['exportRoundtripLinked']}`",
        f"- S20 primary style: `{payload['summary']['s20PrimaryStyle']}`",
        "",
        "## Profiles",
        "",
        "| Profile | Noise kind | Samples | Decision | Range | Max abs error |",
        "|---|---|---:|---|---|---:|",
    ]
    for profile in packet["profiles"]:
        agreement = profile["emlShapedVsSource"]
        lines.append(
            f"| `{profile['profile']}` | `{profile['noiseKind']}` | {profile['sampleCount']} | "
            f"`{profile['decision']}` | `{profile['sourceOutputRange'][0]:.3e}..{profile['sourceOutputRange'][1]:.3e}` | "
            f"`{agreement['maxAbsError']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No broad EML advantage claim.",
            "- No source-family or sigmoid generalization claim.",
            "- No runtime performance claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No proof, deployment, package publish, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_holdout_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid S23 packet schema")
    summary = packet["summary"]
    if summary["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected profile count")
    if summary["passingProfiles"] != summary["profileCount"]:
        raise ValueError("all profiles must pass")
    if summary["allProfilesBounded"] is not True:
        raise ValueError("stable sigmoid outputs must be bounded")
    if summary["runtimeWitnessedObligationCount"] != 2:
        raise ValueError("expected two runtime witnessed obligations")
    for profile in packet["profiles"]:
        agreement = profile["emlShapedVsSource"]
        if agreement["finiteRatio"] < CRITERIA["finiteRatioPass"]:
            raise ValueError("finite ratio below pass threshold")
        if agreement["maxAbsError"] > CRITERIA["maxAbsErrorPass"]:
            raise ValueError("max abs error above pass threshold")
        if agreement["maxRelError"] > CRITERIA["maxRelErrorPass"]:
            raise ValueError("max rel error above pass threshold")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid S23 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid S23 status")
    if payload["s22SelectedPromotionFamily"] != "sigmoid_logistic":
        raise ValueError("S23 must follow S22 sigmoid selection")
    validate_holdout_packet(payload["holdoutPacket"])
    summary = payload["summary"]
    if summary["roundtripPacketCount"] != 2 or summary["roundtripPassCount"] != 2:
        raise ValueError("stable sigmoid must have two passing A13 roundtrip packets")
    if summary["semanticComparisonPass"] is not True:
        raise ValueError("stable sigmoid semantic comparison must pass")
    if summary["exportRoundtripLinked"] is not True:
        raise ValueError("stable sigmoid export must link to roundtrip hash")
    if summary["s20PrimaryStyle"] != "eml_native":
        raise ValueError("stable sigmoid should be S20 EML-native")
    for key in [
        "publicReady",
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "sigmoidGeneralizationClaim",
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_s23_sigmoid_logistic_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_s23_sigmoid_logistic_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_s23_sigmoid_logistic_holdout.json"
    feed_path = command_feed_dir / f"eml_s23_sigmoid_logistic_holdout_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_s23_sigmoid_logistic_holdout")
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
    print("EML_S23_SIGMOID_LOGISTIC_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"roundtrip_passes={built['payload']['summary']['roundtripPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
