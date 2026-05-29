#!/usr/bin/env python3
"""EML-ADV-PCC7 oscillatory eFrog holdout.

Adds damped_wave.py as a non-pure-exponential source family. EML represents the
decay envelope, while the sine component remains standard/protected math.
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
SOURCE_PATH = EFROG_ROOT / "examples" / "damped_wave.py"

if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_advantage_pcc7_oscillatory_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_pcc7_oscillatory_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC7_OSCILLATORY_HOLDOUT_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "oscillatory_generalization_claim": False,
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
    "PCC7 is one oscillatory holdout, not a broad oscillatory-source benchmark.",
    "PCC7 does not prove broad EML advantage, source-family generalization, oscillatory generalization, noise robustness, or prediction accuracy.",
    "PCC7 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "The sine component remains standard math; EML only represents the exponential damping envelope in this holdout.",
]

CRITERIA = {
    "profileCount": 4,
    "finiteRatioPass": 1.0,
    "modelAgreementMaxAbsPass": 1.0e-12,
    "modelAgreementMaxRelPass": 1.0e-12,
}


def source_digest(path: Path = SOURCE_PATH) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def standard_damped_wave(zeta: np.ndarray, omega: np.ndarray, t: np.ndarray) -> np.ndarray:
    return np.exp(-zeta * t) * np.sin(omega * t)


def eml_shaped_damped_wave(zeta: np.ndarray, omega: np.ndarray, t: np.ndarray) -> np.ndarray:
    return eml(-zeta * t, 1.0) * np.sin(omega * t)


def deterministic_noise(count: int, *, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=count).astype(np.float64)


def profile_specs() -> list[dict[str, Any]]:
    count = 2048
    clean = {
        "zeta": np.linspace(0.01, 1.5, count),
        "omega": np.linspace(0.25, 8.0, count),
        "t": np.linspace(0.0, 20.0, count),
    }
    phase = {
        "zeta": np.geomspace(0.005, 2.0, count),
        "omega": np.linspace(1.0, 40.0, count),
        "t": np.linspace(0.0, 12.0, count),
    }
    noisy_inputs = {
        "zeta": np.clip(clean["zeta"] + deterministic_noise(count, seed=7101, scale=0.002), 0.0, None),
        "omega": np.clip(clean["omega"] + deterministic_noise(count, seed=7102, scale=0.02), 0.0, None),
        "t": np.clip(clean["t"] + deterministic_noise(count, seed=7103, scale=0.01), 0.0, None),
    }
    near_zero = {
        "zeta": np.linspace(0.0, 0.05, count),
        "omega": np.linspace(0.1, 4.0, count),
        "t": np.linspace(0.0, 5.0, count) + deterministic_noise(count, seed=7104, scale=0.001),
    }
    return [
        {"profile": "clean_damped_wave_grid", "noiseKind": "none", **clean},
        {"profile": "high_frequency_phase_grid", "noiseKind": "phase_sweep", **phase},
        {"profile": "noisy_input_damped_wave_grid", "noiseKind": "input_perturbation", **noisy_inputs},
        {"profile": "noisy_output_damped_wave_observation_grid", "noiseKind": "output_observation", **near_zero},
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
    zeta = spec["zeta"].astype(np.float64)
    omega = spec["omega"].astype(np.float64)
    t = spec["t"].astype(np.float64)
    source = standard_damped_wave(zeta, omega, t)
    eml_observed = eml_shaped_damped_wave(zeta, omega, t)
    agreement = agreement_metric(eml_observed, source)
    noisy_observation = source
    if spec["noiseKind"] == "output_observation":
        noisy_observation = source + deterministic_noise(source.size, seed=7110, scale=0.0015)
    residual = residual_metric(eml_observed, noisy_observation)
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "sampleCount": int(zeta.size),
        "inputRanges": {
            "zeta": [float(zeta.min()), float(zeta.max())],
            "omega": [float(omega.min()), float(omega.max())],
            "t": [float(t.min()), float(t.max())],
        },
        "emlShapedVsSource": agreement,
        "emlShapedVsNoisyObservation": residual,
        "winner": "partial_eml_envelope_semantic_tie" if agreement["pass"] else "blocked",
    }


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_specs()]
    pass_count = sum(1 for profile in profiles if profile["emlShapedVsSource"]["pass"])
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_pcc7_oscillatory_holdout_packet_v0",
        "date": DATE,
        "caseId": "efrog_damped_wave_oscillatory_holdout_v0",
        "sourceRepo": "efrog",
        "sourcePath": "examples/damped_wave.py",
        "sourceSha256": source_digest(),
        "sourceLineCount": len(source_text.splitlines()),
        "standardForm": "exp(-zeta * t) * sin(omega * t)",
        "emlForm": "eml(-zeta * t, 1) * sin(omega * t)",
        "holdoutClass": "oscillatory_partial_eml_envelope_semantic_tie",
        "emlCoverage": "exponential_damping_envelope_only",
        "standardCoverage": "sine_oscillation_and_runtime_surface",
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
            "oscillatoryGeneralizationClaim": False,
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
        "artifactId": "eml-adv-pcc7-oscillatory-holdout",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "gapResponseKind": "oscillatory_source_family_holdout",
        "selectedSource": "efrog/examples/damped_wave.py",
        "holdoutPacket": packet,
        "summary": {
            "holdoutCount": 1,
            "sourceFamilyCount": 3,
            "sourceFamilies": ["rc_decay_stable", "gaussian_stable", "damped_wave"],
            "profileCount": packet["summary"]["profileCount"],
            "passingProfiles": packet["summary"]["passingProfiles"],
            "noisyOutputProfileCount": packet["summary"]["noisyOutputProfileCount"],
            "allProfilesPass": packet["summary"]["allProfilesPass"],
            "sourceLinked": SOURCE_PATH.exists(),
            "partialEmlCoverage": "exponential_damping_envelope_only",
            "standardRuntimeSurfaceStillRequired": True,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "oscillatoryGeneralizationClaim": False,
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
        "artifactId": "eml-adv-pcc7-oscillatory-holdout",
        "title": "EML-ADV-PCC7 Oscillatory Holdout",
        "reviewDecision": "private_oscillatory_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_noisy_sample_grid",
        "semanticStrength": "partial_eml_envelope_semantic_tie_no_runtime_or_generalization_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private oscillatory holdout for EML Advantage Lab contract only; no broad EML advantage, source-family generalization, oscillatory generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Adds damped_wave.py as a third eFrog source family.",
            "Shows EML can represent the exponential damping envelope while sine remains standard math.",
            "Records partial EML coverage instead of claiming a full EML or runtime win.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc7_oscillatory_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc7_oscillatory_holdout.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc7.v0",
        "date": DATE,
        "title": "EML-ADV-PCC7 Oscillatory Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC8: add a log-domain or guarded/piecewise source family before any stronger EML advantage synthesis.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-ADV-PCC7 Oscillatory Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC7 adds `damped_wave.py` as a non-pure-exponential eFrog source family.",
        "EML represents the damping envelope; sine remains standard math.",
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
            f"- Partial EML coverage: `{summary['partialEmlCoverage']}`",
            f"- Standard runtime surface still required: `{summary['standardRuntimeSurfaceStillRequired']}`",
            f"- Runtime performance claim: `{summary['runtimePerformanceClaim']}`",
            "",
            "## Boundary",
            "",
            "- Private oscillatory holdout only.",
            "- No broad EML advantage, source-family generalization, oscillatory generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid PCC7 packet schema")
    if packet["summary"]["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected PCC7 profile count")
    if packet["summary"]["passingProfiles"] != packet["summary"]["profileCount"]:
        raise ValueError("expected all PCC7 profiles to preserve source agreement")
    if packet["emlCoverage"] != "exponential_damping_envelope_only":
        raise ValueError("PCC7 must record partial EML coverage")
    for key in [
        "runtimePerformanceClaim",
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "oscillatoryGeneralizationClaim",
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
        raise ValueError("invalid PCC7 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC7 status")
    summary = payload["summary"]
    if summary["holdoutCount"] != 1:
        raise ValueError("expected exactly one oscillatory holdout")
    if summary["sourceFamilyCount"] < 3:
        raise ValueError("expected three source families after PCC7")
    if summary["sourceLinked"] is not True:
        raise ValueError("expected linked eFrog source")
    if summary["allProfilesPass"] is not True:
        raise ValueError("expected all PCC7 profiles to pass")
    if summary["standardRuntimeSurfaceStillRequired"] is not True:
        raise ValueError("PCC7 must keep standard runtime surface required")
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "oscillatoryGeneralizationClaim",
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
    result_path = out_dir / f"eml_advantage_pcc7_oscillatory_holdout_{STAMP}.json"
    packet_path = packet_dir / f"{payload['holdoutPacket']['caseId']}_pcc7_oscillatory_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc7_oscillatory_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc7_oscillatory_holdout.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc7_oscillatory_holdout_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc7_oscillatory_holdout")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc7_oscillatory_holdout_packets")
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
    print("EML_ADV_PCC7_OSCILLATORY_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
