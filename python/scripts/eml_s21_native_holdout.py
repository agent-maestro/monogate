#!/usr/bin/env python3
"""EML-S21 native-style holdout.

Uses the S20 style atlas to choose an EML-native lane, then tests a new
stretched-exponential source family. This is a private semantic holdout only:
it does not claim runtime advantage, compiler correctness, or broad EML
superiority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_s21_native_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_s21_native_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_S21_NATIVE_HOLDOUT_PASS"

S20_PATH = ROOT / "python/results/eml_s20_style_atlas/eml_s20_style_atlas_2026_05_29.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "broad_eml_advantage_claim": False,
    "eml_native_generalization_claim": False,
    "source_family_generalization_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "formal_proof_claim": False,
    "prediction_accuracy_claim": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "machlib_source_changed": False,
    "engine_behavior_changed": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "S21 is one private EML-native holdout selected from the S20 style atlas.",
    "S21 does not prove EML-native source-family generalization or broad EML advantage.",
    "S21 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "The stretched-exponential source family is a deterministic semantic fixture, not live hardware, biology, reliability, or production evidence.",
]

CRITERIA = {
    "profileCount": 4,
    "finiteRatioPass": 1.0,
    "maxAbsErrorPass": 1.0e-12,
    "maxRelErrorPass": 1.0e-12,
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def deterministic_noise(count: int, *, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=count).astype(np.float64)


def standard_stretched_exponential(amplitude: np.ndarray, scale: np.ndarray, shape: np.ndarray, t: np.ndarray) -> np.ndarray:
    ratio = np.maximum(t, 0.0) / scale
    exponent = -(ratio**shape)
    return amplitude * np.exp(exponent)


def eml_stretched_exponential(amplitude: np.ndarray, scale: np.ndarray, shape: np.ndarray, t: np.ndarray) -> np.ndarray:
    ratio = np.maximum(t, 0.0) / scale
    exponent = -(ratio**shape)
    return amplitude * eml(exponent, 1.0)


def profile_specs() -> list[dict[str, Any]]:
    count = 2048
    clean = {
        "amplitude": np.linspace(0.2, 3.0, count),
        "scale": np.linspace(0.35, 5.0, count),
        "shape": np.linspace(0.55, 2.75, count),
        "t": np.linspace(0.0, 8.0, count),
    }
    noisy_inputs = {
        "amplitude": np.clip(clean["amplitude"] + deterministic_noise(count, seed=2101, scale=0.01), 1.0e-6, None),
        "scale": np.clip(clean["scale"] + deterministic_noise(count, seed=2102, scale=0.02), 1.0e-6, None),
        "shape": np.clip(clean["shape"] + deterministic_noise(count, seed=2103, scale=0.015), 0.05, None),
        "t": np.clip(clean["t"] + deterministic_noise(count, seed=2104, scale=0.025), 0.0, None),
    }
    long_tail = {
        "amplitude": np.linspace(0.5, 1.5, count),
        "scale": np.geomspace(0.2, 8.0, count),
        "shape": np.linspace(0.3, 1.2, count),
        "t": np.geomspace(1.0e-6, 40.0, count),
    }
    shape_sweep = {
        "amplitude": np.ones(count),
        "scale": np.linspace(0.5, 2.5, count),
        "shape": np.geomspace(0.25, 4.0, count),
        "t": np.linspace(0.0, 6.0, count),
    }
    return [
        {"profile": "clean_stretched_exponential_grid", "noiseKind": "none", **clean},
        {"profile": "noisy_input_stretched_exponential_grid", "noiseKind": "input_perturbation", **noisy_inputs},
        {"profile": "long_tail_stretched_exponential_grid", "noiseKind": "tail_sweep", **long_tail},
        {"profile": "shape_sweep_stretched_exponential_grid", "noiseKind": "shape_sweep", **shape_sweep},
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
    amplitude = spec["amplitude"].astype(np.float64)
    scale = spec["scale"].astype(np.float64)
    shape = spec["shape"].astype(np.float64)
    t = spec["t"].astype(np.float64)
    source = standard_stretched_exponential(amplitude, scale, shape, t)
    eml_observed = eml_stretched_exponential(amplitude, scale, shape, t)
    agreement = agreement_metric(eml_observed, source)
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "sampleCount": int(t.size),
        "inputRanges": {
            "amplitude": [float(amplitude.min()), float(amplitude.max())],
            "scale": [float(scale.min()), float(scale.max())],
            "shape": [float(shape.min()), float(shape.max())],
            "t": [float(t.min()), float(t.max())],
        },
        "domainRequirements": [
            "scale > 0",
            "shape > 0",
            "t is clamped to nonnegative semantic domain before fractional powers",
        ],
        "emlShapedVsSource": agreement,
        "styleDecision": "eml_native_semantic_tie" if agreement["pass"] else "blocked",
    }


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_specs()]
    pass_count = sum(1 for profile in profiles if profile["emlShapedVsSource"]["pass"])
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_s21_native_holdout_packet_v0",
        "date": DATE,
        "caseId": "stretched_exponential_eml_native_holdout_v0",
        "selectedFromStyleAtlas": "eml_native",
        "sourceFamily": "stretched_exponential",
        "surface": "amplitude * exp(-((max(t, 0) / scale)^shape))",
        "standardForm": "amplitude * exp(-((max(t, 0) / scale)^shape))",
        "emlForm": "amplitude * eml(-((max(t, 0) / scale)^shape), 1)",
        "whyThisHoldout": [
            "It stays in the S20 EML-native lane.",
            "It is not a repeat of Gaussian or RC decay.",
            "It stresses fractional powers, positive-domain guards, and long tails.",
        ],
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "passingProfiles": pass_count,
            "blockedProfiles": len(profiles) - pass_count,
            "allProfilesPass": pass_count == len(profiles),
            "sampleCountTotal": sum(profile["sampleCount"] for profile in profiles),
            "emlNativeSemanticTie": pass_count == len(profiles),
            "broadEmlAdvantageClaim": False,
            "emlNativeGeneralizationClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "runtimePerformanceClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def build_payload() -> dict[str, Any]:
    s20 = read_json(S20_PATH)
    packet = build_holdout_packet()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-s21-native-holdout",
        "sourceEvidence": [str(S20_PATH.relative_to(ROOT))],
        "selectedStyleLane": "eml_native",
        "s20NativePrimaryCount": s20["summary"]["emlNativePrimaryCount"],
        "holdoutPacket": packet,
        "summary": {
            "holdoutCount": 1,
            "sourceFamily": "stretched_exponential",
            "profileCount": packet["summary"]["profileCount"],
            "passingProfiles": packet["summary"]["passingProfiles"],
            "sampleCountTotal": packet["summary"]["sampleCountTotal"],
            "allProfilesPass": packet["summary"]["allProfilesPass"],
            "emlNativeSemanticTie": packet["summary"]["emlNativeSemanticTie"],
            "s20NativePrimaryCount": s20["summary"]["emlNativePrimaryCount"],
            "publicReady": False,
            "broadEmlAdvantageClaim": False,
            "emlNativeGeneralizationClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "runtimePerformanceClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextResearchQuestion": "Promote stretched exponential into Forge/eFrog export flow only after a source fixture and roundtrip hash exist.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-s21-native-holdout",
        "title": "EML-S21 Native Holdout",
        "reviewDecision": "private_eml_native_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_sample_grid",
        "semanticStrength": "single_new_eml_native_holdout_no_generalization_or_runtime_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private EML-native holdout only; no broad EML advantage, EML-native generalization, runtime performance, compiler correctness, formal equivalence, proof, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Uses S20 to select the EML-native lane instead of expanding randomly.",
            "Adds a stretched-exponential surface distinct from RC decay and Gaussian.",
            "Records domain requirements for positive scale/shape and nonnegative time before fractional powers.",
        ],
        "validationCommands": [
            "python python/scripts/eml_s21_native_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_s21_native_holdout.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_s21_native_holdout.v0",
        "date": DATE,
        "title": "EML-S21 Native Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": payload["nextResearchQuestion"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-S21 Native Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "S21 uses the S20 style atlas to select the EML-native lane and tests a new stretched-exponential surface.",
        "It is a private semantic holdout, not a broad advantage, runtime, proof, compiler, or public claim.",
        "",
        "## Holdout",
        "",
        f"- Source family: `{packet['sourceFamily']}`",
        f"- Standard form: `{packet['standardForm']}`",
        f"- EML form: `{packet['emlForm']}`",
        "",
        "| Profile | Noise kind | Samples | Decision | Max abs error | Max rel error |",
        "|---|---|---:|---|---:|---:|",
    ]
    for profile in packet["profiles"]:
        agreement = profile["emlShapedVsSource"]
        lines.append(
            f"| `{profile['profile']}` | `{profile['noiseKind']}` | {profile['sampleCount']} | "
            f"`{profile['styleDecision']}` | `{agreement['maxAbsError']:.3e}` | `{agreement['maxRelError']:.3e}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Profiles: `{summary['profileCount']}`",
            f"- Passing profiles: `{summary['passingProfiles']}`",
            f"- Total samples: `{summary['sampleCountTotal']}`",
            f"- EML-native semantic tie: `{summary['emlNativeSemanticTie']}`",
            "",
            "## Boundary",
            "",
            "- No broad EML advantage claim.",
            "- No EML-native generalization claim.",
            "- No runtime performance claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No proof, deployment, package publish, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid packet schema")
    summary = packet["summary"]
    if summary["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected profile count")
    if summary["passingProfiles"] != summary["profileCount"]:
        raise ValueError("all profiles must pass for S21")
    for profile in packet["profiles"]:
        agreement = profile["emlShapedVsSource"]
        if agreement["finiteRatio"] < CRITERIA["finiteRatioPass"]:
            raise ValueError("finite ratio below pass threshold")
        if agreement["maxAbsError"] > CRITERIA["maxAbsErrorPass"]:
            raise ValueError("max abs error above pass threshold")
        if agreement["maxRelError"] > CRITERIA["maxRelErrorPass"]:
            raise ValueError("max rel error above pass threshold")
    for key in [
        "broadEmlAdvantageClaim",
        "emlNativeGeneralizationClaim",
        "sourceFamilyGeneralizationClaim",
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    if payload["selectedStyleLane"] != "eml_native":
        raise ValueError("S21 must select the EML-native lane")
    validate_packet(payload["holdoutPacket"])
    summary = payload["summary"]
    if summary["s20NativePrimaryCount"] < 2:
        raise ValueError("S20 must expose at least two EML-native cases before S21")
    for key in [
        "publicReady",
        "broadEmlAdvantageClaim",
        "emlNativeGeneralizationClaim",
        "sourceFamilyGeneralizationClaim",
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
    result_path = out_dir / f"eml_s21_native_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_s21_native_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_s21_native_holdout.json"
    feed_path = command_feed_dir / f"eml_s21_native_holdout_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_s21_native_holdout")
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
    print("EML_S21_NATIVE_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
