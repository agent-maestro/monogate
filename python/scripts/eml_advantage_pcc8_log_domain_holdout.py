#!/usr/bin/env python3
"""EML-ADV-PCC8 log-domain eFrog holdout.

Adds numpy_softplus.py as a log-domain source family. The experiment separates
EML-shaped representation from protected runtime lowering: raw log(1+exp(x))
and log(1+eml(x,1)) agree on safe ranges, but protected logaddexp(0,x) is the
runtime recommendation on overflow-prone ranges.
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
SOURCE_PATH = EFROG_ROOT / "examples" / "numpy_softplus.py"

if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_advantage_pcc8_log_domain_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_pcc8_log_domain_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC8_LOG_DOMAIN_HOLDOUT_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "log_domain_generalization_claim": False,
    "protected_lowering_correctness_claim": False,
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
    "PCC8 is one log-domain holdout, not a broad log-domain benchmark.",
    "PCC8 does not prove broad EML advantage, source-family generalization, protected-lowering correctness, noise robustness, or prediction accuracy.",
    "PCC8 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "Protected logaddexp is recorded as the runtime recommendation on overflow-prone ranges, not as a compiler-correctness proof.",
]

CRITERIA = {
    "profileCount": 5,
    "finiteRatioPass": 1.0,
    "safeAgreementMaxAbsPass": 1.0e-12,
    "safeAgreementMaxRelPass": 1.0e-12,
}


def source_digest(path: Path = SOURCE_PATH) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def source_softplus(x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore"):
        return np.log(1.0 + np.exp(x))


def eml_shaped_softplus(x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore"):
        return np.log(1.0 + eml(x, 1.0))


def protected_softplus(x: np.ndarray) -> np.ndarray:
    return np.logaddexp(0.0, x)


def deterministic_noise(count: int, *, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=count).astype(np.float64)


def profile_specs() -> list[dict[str, Any]]:
    count = 2048
    safe = np.linspace(-40.0, 40.0, count)
    centered = np.linspace(-8.0, 8.0, count)
    noisy_inputs = centered + deterministic_noise(count, seed=8101, scale=0.03)
    negative_tail = np.linspace(-1000.0, -50.0, count)
    overflow_tail = np.linspace(690.0, 760.0, count)
    return [
        {"profile": "safe_log_domain_grid", "noiseKind": "none", "x": safe, "expectProtectedLowering": False},
        {"profile": "centered_noisy_input_grid", "noiseKind": "input_perturbation", "x": noisy_inputs, "expectProtectedLowering": False},
        {"profile": "noisy_output_observation_grid", "noiseKind": "output_observation", "x": centered, "expectProtectedLowering": False},
        {"profile": "negative_tail_underflow_grid", "noiseKind": "negative_tail", "x": negative_tail, "expectProtectedLowering": False},
        {"profile": "positive_overflow_guard_grid", "noiseKind": "overflow_guard", "x": overflow_tail, "expectProtectedLowering": True},
    ]


def agreement_metric(observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(observed) & np.isfinite(reference)
    errors = np.abs(observed[finite] - reference[finite])
    rel = errors / np.maximum(np.abs(reference[finite]), 1.0e-300)
    finite_ratio = float(np.mean(np.isfinite(observed)))
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    return {
        "finiteRatio": finite_ratio,
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "meanAbsError": float(np.mean(errors)) if errors.size else float("inf"),
        "pass": bool(
            finite_ratio >= CRITERIA["finiteRatioPass"]
            and max_abs <= CRITERIA["safeAgreementMaxAbsPass"]
            and max_rel <= CRITERIA["safeAgreementMaxRelPass"]
        ),
    }


def finite_metric(observed: np.ndarray) -> dict[str, Any]:
    return {
        "finiteRatio": float(np.mean(np.isfinite(observed))),
        "finiteCount": int(np.sum(np.isfinite(observed))),
        "sampleCount": int(observed.size),
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
    x = spec["x"].astype(np.float64)
    source = source_softplus(x)
    eml_observed = eml_shaped_softplus(x)
    protected = protected_softplus(x)
    safe_agreement = agreement_metric(eml_observed, source)
    protected_agreement = agreement_metric(protected, protected)
    noisy_observation = protected
    if spec["noiseKind"] == "output_observation":
        noisy_observation = protected + deterministic_noise(protected.size, seed=8110, scale=0.001)
    residual = residual_metric(protected, noisy_observation)
    source_finite = finite_metric(source)
    eml_finite = finite_metric(eml_observed)
    protected_finite = finite_metric(protected)
    protected_needed = bool(spec["expectProtectedLowering"] or protected_finite["finiteRatio"] > source_finite["finiteRatio"])
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "sampleCount": int(x.size),
        "inputRanges": {"x": [float(x.min()), float(x.max())]},
        "emlShapedVsSource": safe_agreement,
        "protectedVsProtectedReference": protected_agreement,
        "protectedVsNoisyObservation": residual,
        "sourceFinite": source_finite,
        "emlFinite": eml_finite,
        "protectedFinite": protected_finite,
        "protectedLoweringRecommended": protected_needed,
        "winner": "protected_lowering_required" if protected_needed else "semantic_tie_log_domain_safe_range",
    }


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_specs()]
    safe_profiles = [profile for profile in profiles if not profile["protectedLoweringRecommended"]]
    protected_profiles = [profile for profile in profiles if profile["protectedLoweringRecommended"]]
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_pcc8_log_domain_holdout_packet_v0",
        "date": DATE,
        "caseId": "efrog_numpy_softplus_log_domain_holdout_v0",
        "sourceRepo": "efrog",
        "sourcePath": "examples/numpy_softplus.py",
        "sourceSha256": source_digest(),
        "sourceLineCount": len(source_text.splitlines()),
        "sourceForm": "log(1 + exp(x))",
        "emlForm": "log(1 + eml(x, 1))",
        "protectedForm": "logaddexp(0, x)",
        "holdoutClass": "log_domain_semantic_tie_with_protected_lowering_guard",
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "safeSemanticTieProfiles": len(safe_profiles),
            "protectedLoweringRecommendedProfiles": len(protected_profiles),
            "noisyOutputProfileCount": sum(1 for profile in profiles if profile["noiseKind"] == "output_observation"),
            "allProtectedProfilesFinite": all(profile["protectedFinite"]["finiteRatio"] == 1.0 for profile in profiles),
            "overflowGuardProfileCount": sum(1 for profile in profiles if profile["noiseKind"] == "overflow_guard"),
            "runtimePerformanceClaim": False,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "logDomainGeneralizationClaim": False,
            "protectedLoweringCorrectnessClaim": False,
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
        "artifactId": "eml-adv-pcc8-log-domain-holdout",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "gapResponseKind": "log_domain_source_family_holdout",
        "selectedSource": "efrog/examples/numpy_softplus.py",
        "holdoutPacket": packet,
        "summary": {
            "holdoutCount": 1,
            "sourceFamilyCount": 4,
            "sourceFamilies": ["rc_decay_stable", "gaussian_stable", "damped_wave", "numpy_softplus"],
            "profileCount": packet["summary"]["profileCount"],
            "safeSemanticTieProfiles": packet["summary"]["safeSemanticTieProfiles"],
            "protectedLoweringRecommendedProfiles": packet["summary"]["protectedLoweringRecommendedProfiles"],
            "allProtectedProfilesFinite": packet["summary"]["allProtectedProfilesFinite"],
            "sourceLinked": SOURCE_PATH.exists(),
            "runtimeRecommendation": "protected_logaddexp_for_overflow_prone_ranges",
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "logDomainGeneralizationClaim": False,
            "protectedLoweringCorrectnessClaim": False,
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
        "artifactId": "eml-adv-pcc8-log-domain-holdout",
        "title": "EML-ADV-PCC8 Log-Domain Holdout",
        "reviewDecision": "private_log_domain_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_overflow_guard_sample_grid",
        "semanticStrength": "log_domain_semantic_tie_with_protected_lowering_recommendation_no_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private log-domain holdout for EML Advantage Lab contract only; no broad EML advantage, source-family generalization, log-domain generalization, protected-lowering correctness, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Adds numpy_softplus.py as a fourth eFrog source family.",
            "Separates safe-range EML/source agreement from overflow-prone protected lowering.",
            "Records protected logaddexp as the runtime recommendation without claiming compiler correctness.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc8_log_domain_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc8_log_domain_holdout.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc8.v0",
        "date": DATE,
        "title": "EML-ADV-PCC8 Log-Domain Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC9: add a guarded/piecewise source family such as clamp_guard.py.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-ADV-PCC8 Log-Domain Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC8 adds `numpy_softplus.py` as a log-domain eFrog source family.",
        "It separates safe-range EML/source agreement from overflow-prone protected lowering.",
        "",
        "| Profile | Noise | Winner | Source finite | EML finite | Protected finite |",
        "|---|---|---|---:|---:|---:|",
    ]
    for profile in packet["profiles"]:
        lines.append(
            f"| `{profile['profile']}` | `{profile['noiseKind']}` | `{profile['winner']}` | "
            f"`{profile['sourceFinite']['finiteRatio']:.3f}` | `{profile['emlFinite']['finiteRatio']:.3f}` | "
            f"`{profile['protectedFinite']['finiteRatio']:.3f}` |"
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
            f"- Safe semantic tie profiles: `{summary['safeSemanticTieProfiles']}`",
            f"- Protected lowering recommended profiles: `{summary['protectedLoweringRecommendedProfiles']}`",
            f"- All protected profiles finite: `{summary['allProtectedProfilesFinite']}`",
            f"- Runtime recommendation: `{summary['runtimeRecommendation']}`",
            "",
            "## Boundary",
            "",
            "- Private log-domain holdout only.",
            "- No broad EML advantage, source-family generalization, log-domain generalization, protected-lowering correctness, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid PCC8 packet schema")
    summary = packet["summary"]
    if summary["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected PCC8 profile count")
    if summary["safeSemanticTieProfiles"] < 3:
        raise ValueError("expected at least three safe semantic tie profiles")
    if summary["protectedLoweringRecommendedProfiles"] < 1:
        raise ValueError("expected at least one protected lowering profile")
    if summary["allProtectedProfilesFinite"] is not True:
        raise ValueError("expected protected softplus to remain finite")
    for key in [
        "runtimePerformanceClaim",
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "logDomainGeneralizationClaim",
        "protectedLoweringCorrectnessClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for profile in packet["profiles"]:
        if profile["noiseKind"] == "overflow_guard" and profile["protectedLoweringRecommended"] is not True:
            raise ValueError("overflow guard must recommend protected lowering")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC8 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC8 status")
    summary = payload["summary"]
    if summary["holdoutCount"] != 1:
        raise ValueError("expected exactly one log-domain holdout")
    if summary["sourceFamilyCount"] < 4:
        raise ValueError("expected four source families after PCC8")
    if summary["sourceLinked"] is not True:
        raise ValueError("expected linked eFrog source")
    if summary["allProtectedProfilesFinite"] is not True:
        raise ValueError("expected protected profiles finite")
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "logDomainGeneralizationClaim",
        "protectedLoweringCorrectnessClaim",
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
    result_path = out_dir / f"eml_advantage_pcc8_log_domain_holdout_{STAMP}.json"
    packet_path = packet_dir / f"{payload['holdoutPacket']['caseId']}_pcc8_log_domain_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc8_log_domain_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc8_log_domain_holdout.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc8_log_domain_holdout_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc8_log_domain_holdout")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc8_log_domain_holdout_packets")
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
    print("EML_ADV_PCC8_LOG_DOMAIN_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
