#!/usr/bin/env python3
"""EML-ADV-PCC5 second source-family holdout.

Adds the eFrog Gaussian holdout as a second real-source family for the EML
Advantage proof-carrying contract. The experiment checks source-vs-EML-shaped
agreement across clean and noisy deterministic profiles. It does not claim a
runtime win or broad EML advantage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
EFROG_ROOT = MONOGATE_ROOT / "efrog"
SOURCE_PATH = EFROG_ROOT / "examples" / "gaussian_stable.py"

if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_advantage_pcc5_second_source_family_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_pcc5_second_source_family_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC5_SECOND_SOURCE_FAMILY_HOLDOUT_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "real_world_generalization_claim": False,
    "noise_robustness_general_claim": False,
    "prediction_accuracy_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "proof_claim": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "deploy_performed": False,
}

NON_CLAIMS = [
    "PCC5 is one second-source-family holdout, not a broad source-family benchmark.",
    "PCC5 does not prove broad EML advantage, source-family generalization, noise robustness, or prediction accuracy.",
    "PCC5 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "The Gaussian source link is to an eFrog holdout fixture, not a live hardware or production trace.",
]

CRITERIA = {
    "profileCount": 4,
    "finiteRatioPass": 1.0,
    "modelAgreementMaxAbsPass": 1.0e-12,
    "modelAgreementMaxRelPass": 1.0e-12,
}


def source_digest(path: Path = SOURCE_PATH) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def standard_gaussian(mu: np.ndarray, sigma: np.ndarray, x: np.ndarray) -> np.ndarray:
    dx = x - mu
    inv_sigma = 1.0 / sigma
    z = dx * inv_sigma
    exponent = -0.5 * z * z
    return np.exp(exponent) * inv_sigma


def eml_shaped_gaussian(mu: np.ndarray, sigma: np.ndarray, x: np.ndarray) -> np.ndarray:
    dx = x - mu
    inv_sigma = 1.0 / sigma
    z = dx * inv_sigma
    exponent = -0.5 * z * z
    return eml(exponent, 1.0) * inv_sigma


def deterministic_noise(count: int, *, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=count).astype(np.float64)


def profile_specs() -> list[dict[str, Any]]:
    count = 2048
    clean = {
        "mu": np.linspace(-2.0, 2.0, count),
        "sigma": np.linspace(0.25, 4.0, count),
        "x": np.linspace(-6.0, 6.0, count),
    }
    tail = {
        "mu": np.linspace(-1.0, 1.0, count),
        "sigma": np.geomspace(0.15, 3.0, count),
        "x": np.concatenate([np.linspace(-9.0, -3.0, count // 2), np.linspace(3.0, 9.0, count // 2)]),
    }
    noisy_inputs = {
        "mu": clean["mu"] + deterministic_noise(count, seed=5101, scale=0.02),
        "sigma": np.clip(clean["sigma"] + deterministic_noise(count, seed=5102, scale=0.015), 1.0e-4, None),
        "x": clean["x"] + deterministic_noise(count, seed=5103, scale=0.03),
    }
    narrow_sigma = {
        "mu": np.linspace(-0.5, 0.5, count),
        "sigma": np.geomspace(0.02, 0.25, count),
        "x": np.linspace(-1.5, 1.5, count) + deterministic_noise(count, seed=5104, scale=0.002),
    }
    return [
        {"profile": "clean_gaussian_grid", "noiseKind": "none", **clean},
        {"profile": "noisy_input_gaussian_grid", "noiseKind": "input_perturbation", **noisy_inputs},
        {"profile": "noisy_output_gaussian_observation_grid", "noiseKind": "output_observation", **tail},
        {"profile": "narrow_sigma_noisy_edge_grid", "noiseKind": "input_edge_perturbation", **narrow_sigma},
    ]


def agreement_metric(observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(observed) & np.isfinite(reference)
    errors = np.abs(observed[finite] - reference[finite])
    rel = errors / np.maximum(np.abs(reference[finite]), 1.0e-300)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    return {
        "finiteRatio": float(np.mean(np.isfinite(observed))),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "meanAbsError": float(np.mean(errors)) if errors.size else float("inf"),
        "pass": bool(
            float(np.mean(np.isfinite(observed))) >= CRITERIA["finiteRatioPass"]
            and max_abs <= CRITERIA["modelAgreementMaxAbsPass"]
            and max_rel <= CRITERIA["modelAgreementMaxRelPass"]
        ),
    }


def residual_metric(observed: np.ndarray, noisy_observation: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(observed) & np.isfinite(noisy_observation)
    errors = observed[finite] - noisy_observation[finite]
    return {
        "finiteRatio": float(np.mean(np.isfinite(observed))),
        "rmse": float(np.sqrt(np.mean(errors * errors))) if errors.size else float("inf"),
        "mae": float(np.mean(np.abs(errors))) if errors.size else float("inf"),
        "reportedAsClaim": False,
    }


def profile_result(spec: dict[str, Any]) -> dict[str, Any]:
    mu = spec["mu"].astype(np.float64)
    sigma = spec["sigma"].astype(np.float64)
    x = spec["x"].astype(np.float64)
    source = standard_gaussian(mu, sigma, x)
    eml_observed = eml_shaped_gaussian(mu, sigma, x)
    agreement = agreement_metric(eml_observed, source)
    noisy_observation = source
    if spec["noiseKind"] == "output_observation":
        noisy_observation = source + deterministic_noise(source.size, seed=5110, scale=0.001)
    residual = residual_metric(eml_observed, noisy_observation)
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "sampleCount": int(mu.size),
        "inputRanges": {
            "mu": [float(mu.min()), float(mu.max())],
            "sigma": [float(sigma.min()), float(sigma.max())],
            "x": [float(x.min()), float(x.max())],
        },
        "emlShapedVsSource": agreement,
        "emlShapedVsNoisyObservation": residual,
        "winner": "semantic_tie_for_second_source_family" if agreement["pass"] else "blocked",
    }


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_specs()]
    pass_count = sum(1 for profile in profiles if profile["emlShapedVsSource"]["pass"])
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_pcc5_second_source_family_holdout_packet_v0",
        "date": DATE,
        "caseId": "efrog_gaussian_stable_second_source_family_holdout_v0",
        "sourceRepo": "efrog",
        "sourcePath": "examples/gaussian_stable.py",
        "sourceSha256": source_digest(),
        "sourceLineCount": len(source_text.splitlines()),
        "standardForm": "exp(-0.5 * ((x - mu) / sigma)^2) / sigma",
        "emlForm": "eml(-0.5 * ((x - mu) / sigma)^2, 1) / sigma",
        "holdoutClass": "second_source_family_semantic_tie",
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "passingProfiles": pass_count,
            "blockedProfiles": len(profiles) - pass_count,
            "noisyOutputProfileCount": sum(1 for profile in profiles if profile["noiseKind"] == "output_observation"),
            "allProfilesPass": pass_count == len(profiles),
            "runtimePerformanceClaim": False,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "noiseRobustnessGeneralClaim": False,
            "predictionAccuracyClaim": False,
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def build_payload() -> dict[str, Any]:
    packet = build_holdout_packet()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-adv-pcc5-second-source-family-holdout",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "gapResponseKind": "second_source_family_holdout",
        "selectedSource": "efrog/examples/gaussian_stable.py",
        "holdoutPacket": packet,
        "summary": {
            "holdoutCount": 1,
            "sourceFamilyCount": 2,
            "sourceFamilies": ["rc_decay_stable", "gaussian_stable"],
            "profileCount": packet["summary"]["profileCount"],
            "passingProfiles": packet["summary"]["passingProfiles"],
            "noisyOutputProfileCount": packet["summary"]["noisyOutputProfileCount"],
            "allProfilesPass": packet["summary"]["allProfilesPass"],
            "sourceLinked": SOURCE_PATH.exists(),
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "runtimePerformanceClaim": False,
            "noiseRobustnessGeneralClaim": False,
            "predictionAccuracyClaim": False,
            "publicReady": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-adv-pcc5-second-source-family-holdout",
        "title": "EML-ADV-PCC5 Second Source-Family Holdout",
        "reviewDecision": "private_second_source_family_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_noisy_sample_grid",
        "semanticStrength": "second_source_family_semantic_tie_no_runtime_or_generalization_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private second-source-family holdout for EML Advantage Lab contract only; no broad EML advantage, source-family generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Adds gaussian_stable.py as the second eFrog source family after RC decay.",
            "Checks clean, noisy-input, noisy-output, and narrow-sigma edge profiles.",
            "Records EML as semantic/search representation evidence, not a runtime win.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc5_second_source_family_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc5_second_source_family_holdout.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc5.v0",
        "date": DATE,
        "title": "EML-ADV-PCC5 Second Source-Family Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC6: add a source-family comparison report across RC decay and Gaussian holdouts.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-ADV-PCC5 Second Source-Family Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC5 adds `gaussian_stable.py` as a second eFrog source family for the EML Advantage contract.",
        "It reports source agreement separately from noisy-observation residuals.",
        "",
        "| Profile | Noise | Winner | Max abs agreement error | Observation RMSE |",
        "|---|---|---|---:|---:|",
    ]
    for profile in packet["profiles"]:
        agreement = profile["emlShapedVsSource"]
        residual = profile["emlShapedVsNoisyObservation"]
        lines.append(
            f"| `{profile['profile']}` | `{profile['noiseKind']}` | `{profile['winner']}` | "
            f"`{agreement['maxAbsError']:.3e}` | `{residual['rmse']:.3e}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Holdouts: `{summary['holdoutCount']}`",
            f"- Source families now referenced: `{summary['sourceFamilyCount']}`",
            f"- Profiles: `{summary['profileCount']}`",
            f"- Passing profiles: `{summary['passingProfiles']}`",
            f"- Noisy output profiles: `{summary['noisyOutputProfileCount']}`",
            f"- Broad EML advantage claim: `{summary['broadEmlAdvantageClaim']}`",
            f"- Source-family generalization claim: `{summary['sourceFamilyGeneralizationClaim']}`",
            f"- Runtime performance claim: `{summary['runtimePerformanceClaim']}`",
            "",
            "## Boundary",
            "",
            "- Private second-source-family holdout only.",
            "- No broad EML advantage, source-family generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid PCC5 packet schema")
    if packet["summary"]["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected PCC5 profile count")
    if packet["summary"]["passingProfiles"] != packet["summary"]["profileCount"]:
        raise ValueError("expected all PCC5 profiles to preserve source agreement")
    if packet["summary"]["noisyOutputProfileCount"] < 1:
        raise ValueError("expected at least one noisy output profile")
    for key in [
        "runtimePerformanceClaim",
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
    ]:
        if packet["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC5 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC5 status")
    summary = payload["summary"]
    if summary["holdoutCount"] != 1:
        raise ValueError("expected exactly one second-source-family holdout")
    if summary["sourceFamilyCount"] < 2:
        raise ValueError("expected two source families after PCC5")
    if summary["sourceLinked"] is not True:
        raise ValueError("expected linked eFrog source")
    if summary["allProfilesPass"] is not True:
        raise ValueError("expected all PCC5 profiles to pass")
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "runtimePerformanceClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    validate_packet(payload["holdoutPacket"])
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)

    result_path = out_dir / f"eml_advantage_pcc5_second_source_family_holdout_{STAMP}.json"
    packet_path = packet_dir / f"{payload['holdoutPacket']['caseId']}_pcc5_second_source_family_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc5_second_source_family_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc5_second_source_family_holdout.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc5_second_source_family_holdout_feed_{STAMP}.json"

    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    packet_path.write_text(json.dumps(payload["holdoutPacket"], indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "packet_path": str(packet_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc5_second_source_family_holdout")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc5_second_source_family_holdout_packets")
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
    print("EML_ADV_PCC5_SECOND_SOURCE_FAMILY_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
