#!/usr/bin/env python3
"""EML-ADV-PCC4 noisy real-source holdout.

Extends PCC3 by perturbing the eFrog RC decay holdout. The experiment separates
model-to-model agreement from residual-to-noisy-observation so noisy data is not
misread as an EML runtime or prediction advantage.
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
SOURCE_PATH = EFROG_ROOT / "examples" / "rc_decay_stable.py"

if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_advantage_pcc4_noisy_real_source_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_pcc4_noisy_real_source_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC4_NOISY_REAL_SOURCE_HOLDOUT_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
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
    "PCC4 is one private noisy real-source holdout, not a broad noisy-data benchmark.",
    "PCC4 does not prove broad EML advantage, noise robustness, or prediction accuracy.",
    "PCC4 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "Noisy-observation residuals are reported as residuals only, not as a fit or forecasting claim.",
]

CRITERIA = {
    "profileCount": 4,
    "finiteRatioPass": 1.0,
    "modelAgreementMaxAbsPass": 1.0e-12,
    "modelAgreementMaxRelPass": 1.0e-12,
}


def source_digest(path: Path = SOURCE_PATH) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def standard_rc_decay(v0: np.ndarray, tau: np.ndarray, t: np.ndarray) -> np.ndarray:
    scale = tau * tau + 1.0
    inv_tau = 1.0 / scale
    exponent = -t * inv_tau
    return v0 * np.exp(exponent)


def eml_shaped_rc_decay(v0: np.ndarray, tau: np.ndarray, t: np.ndarray) -> np.ndarray:
    scale = tau * tau + 1.0
    inv_tau = 1.0 / scale
    exponent = -t * inv_tau
    return v0 * eml(exponent, 1.0)


def deterministic_noise(count: int, *, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=count).astype(np.float64)


def profile_specs() -> list[dict[str, Any]]:
    count = 2048
    base = {
        "v0": np.linspace(0.25, 5.0, count),
        "tau": np.linspace(0.2, 5.0, count),
        "t": np.linspace(0.0, 12.0, count),
    }
    long_tail = {
        "v0": np.linspace(1.0, 10.0, count),
        "tau": np.geomspace(0.1, 20.0, count),
        "t": np.geomspace(1.0e-9, 200.0, count),
    }
    noisy_inputs = {
        "v0": np.clip(base["v0"] + deterministic_noise(count, seed=4101, scale=0.02), 0.01, None),
        "tau": np.clip(base["tau"] + deterministic_noise(count, seed=4102, scale=0.015), 1.0e-4, None),
        "t": np.clip(base["t"] + deterministic_noise(count, seed=4103, scale=0.03), 0.0, None),
    }
    edge = {
        "v0": np.clip(np.linspace(0.1, 2.0, count) + deterministic_noise(count, seed=4104, scale=0.005), 0.01, None),
        "tau": np.clip(np.geomspace(1.0e-4, 0.25, count) + deterministic_noise(count, seed=4105, scale=0.0004), 1.0e-5, None),
        "t": np.clip(np.linspace(0.0, 2.0, count) + deterministic_noise(count, seed=4106, scale=0.01), 0.0, None),
    }
    return [
        {"profile": "clean_baseline", "noiseKind": "none", **base},
        {"profile": "noisy_input_grid", "noiseKind": "input_perturbation", **noisy_inputs},
        {"profile": "noisy_output_observation_grid", "noiseKind": "output_observation", **long_tail},
        {"profile": "small_tau_noisy_edge_grid", "noiseKind": "input_edge_perturbation", **edge},
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
    v0 = spec["v0"].astype(np.float64)
    tau = spec["tau"].astype(np.float64)
    t = spec["t"].astype(np.float64)
    source = standard_rc_decay(v0, tau, t)
    eml_observed = eml_shaped_rc_decay(v0, tau, t)
    agreement = agreement_metric(eml_observed, source)
    noisy_observation = source
    if spec["noiseKind"] == "output_observation":
        noisy_observation = source + deterministic_noise(source.size, seed=4110, scale=0.002)
    residual = residual_metric(eml_observed, noisy_observation)
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "sampleCount": int(v0.size),
        "inputRanges": {
            "v0": [float(v0.min()), float(v0.max())],
            "tau": [float(tau.min()), float(tau.max())],
            "t": [float(t.min()), float(t.max())],
        },
        "emlShapedVsSource": agreement,
        "emlShapedVsNoisyObservation": residual,
        "winner": "semantic_tie_under_noise" if agreement["pass"] else "blocked",
    }


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_specs()]
    pass_count = sum(1 for profile in profiles if profile["emlShapedVsSource"]["pass"])
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_pcc4_noisy_real_source_holdout_packet_v0",
        "date": DATE,
        "caseId": "efrog_rc_decay_stable_noisy_real_source_holdout_v0",
        "sourceRepo": "efrog",
        "sourcePath": "examples/rc_decay_stable.py",
        "sourceSha256": source_digest(),
        "standardForm": "v0 * exp(-t / (tau*tau + 1))",
        "emlForm": "v0 * eml(-t / (tau*tau + 1), 1)",
        "holdoutClass": "noisy_real_source_semantic_tie",
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "passingProfiles": pass_count,
            "blockedProfiles": len(profiles) - pass_count,
            "noisyOutputProfileCount": sum(1 for profile in profiles if profile["noiseKind"] == "output_observation"),
            "allProfilesPass": pass_count == len(profiles),
            "runtimePerformanceClaim": False,
            "broadEmlAdvantageClaim": False,
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
        "artifactId": "eml-adv-pcc4-noisy-real-source-holdout",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "gapResponseKind": "noisy_real_source_holdout",
        "selectedSource": "efrog/examples/rc_decay_stable.py",
        "holdoutPacket": packet,
        "summary": {
            "holdoutCount": 1,
            "profileCount": packet["summary"]["profileCount"],
            "passingProfiles": packet["summary"]["passingProfiles"],
            "noisyOutputProfileCount": packet["summary"]["noisyOutputProfileCount"],
            "allProfilesPass": packet["summary"]["allProfilesPass"],
            "sourceLinked": SOURCE_PATH.exists(),
            "broadEmlAdvantageClaim": False,
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
        "artifactId": "eml-adv-pcc4-noisy-real-source-holdout",
        "title": "EML-ADV-PCC4 Noisy Real-Source Holdout",
        "reviewDecision": "private_noisy_real_source_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_noisy_sample_grid",
        "semanticStrength": "noisy_real_source_semantic_tie_no_prediction_or_runtime_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private noisy real-source holdout for EML Advantage Lab contract only; no broad EML advantage, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Adds controlled input and output perturbations around the eFrog RC decay holdout.",
            "Separates model-to-model agreement from residual-to-noisy-observation.",
            "Keeps broad EML advantage, prediction, and runtime claims blocked.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc4_noisy_real_source_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc4_noisy_real_source_holdout.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc4.v0",
        "date": DATE,
        "title": "EML-ADV-PCC4 Noisy Real-Source Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC5: ingest a second eFrog source and compare source-family behavior.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-ADV-PCC4 Noisy Real-Source Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC4 adds controlled perturbations around the eFrog RC decay holdout.",
        "It reports semantic agreement separately from noisy-observation residuals.",
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
            f"- Profiles: `{summary['profileCount']}`",
            f"- Passing profiles: `{summary['passingProfiles']}`",
            f"- Noisy output profiles: `{summary['noisyOutputProfileCount']}`",
            f"- Broad EML advantage claim: `{summary['broadEmlAdvantageClaim']}`",
            f"- Prediction accuracy claim: `{summary['predictionAccuracyClaim']}`",
            f"- Runtime performance claim: `{summary['runtimePerformanceClaim']}`",
            "",
            "## Boundary",
            "",
            "- Private noisy real-source holdout only.",
            "- No broad EML advantage, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid PCC4 packet schema")
    if packet["summary"]["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected PCC4 profile count")
    if packet["summary"]["passingProfiles"] != packet["summary"]["profileCount"]:
        raise ValueError("expected all PCC4 profiles to preserve source agreement")
    if packet["summary"]["noisyOutputProfileCount"] < 1:
        raise ValueError("expected at least one noisy output profile")
    for key in ["runtimePerformanceClaim", "broadEmlAdvantageClaim", "noiseRobustnessGeneralClaim", "predictionAccuracyClaim"]:
        if packet["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC4 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC4 status")
    summary = payload["summary"]
    if summary["holdoutCount"] != 1:
        raise ValueError("expected exactly one noisy real-source holdout")
    if summary["sourceLinked"] is not True:
        raise ValueError("expected linked eFrog source")
    if summary["allProfilesPass"] is not True:
        raise ValueError("expected all PCC4 profiles to pass")
    for key in [
        "broadEmlAdvantageClaim",
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

    result_path = out_dir / f"eml_advantage_pcc4_noisy_real_source_holdout_{STAMP}.json"
    packet_path = packet_dir / f"{payload['holdoutPacket']['caseId']}_pcc4_noisy_real_source_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc4_noisy_real_source_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc4_noisy_real_source_holdout.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc4_noisy_real_source_holdout_feed_{STAMP}.json"

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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc4_noisy_real_source_holdout")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc4_noisy_real_source_holdout_packets")
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
    print("EML_ADV_PCC4_NOISY_REAL_SOURCE_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
