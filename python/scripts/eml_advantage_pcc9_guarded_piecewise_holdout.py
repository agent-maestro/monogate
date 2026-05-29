#!/usr/bin/env python3
"""EML-ADV-PCC9 guarded/piecewise eFrog holdout.

Adds clamp_guard.py as a branch-heavy source family. This is a guard semantics
holdout rather than an EML operator win: it checks that source branches and a
clamp-style guarded representation agree on deterministic sample grids, while
invalid bounds stay blocked.
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
SOURCE_PATH = EFROG_ROOT / "examples" / "clamp_guard.py"

if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_advantage_pcc9_guarded_piecewise_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_pcc9_guarded_piecewise_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC9_GUARDED_PIECEWISE_HOLDOUT_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "guard_semantics_generalization_claim": False,
    "branch_correctness_claim": False,
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
    "PCC9 is one guarded/piecewise holdout, not a broad guard-semantics benchmark.",
    "PCC9 does not prove broad EML advantage, source-family generalization, branch correctness, protected-lowering correctness, noise robustness, or prediction accuracy.",
    "PCC9 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "Invalid-bound cases are blocked as guard-domain failures, not rescued or treated as valid clamp behavior.",
]

CRITERIA = {
    "profileCount": 5,
    "validProfileCount": 4,
    "invalidProfileCount": 1,
    "maxAbsPass": 0.0,
}


def source_digest(path: Path = SOURCE_PATH) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def source_clamp_guard(x: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    return np.where(x < lo, lo, np.where(x > hi, hi, x))


def guarded_clamp_representation(x: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    return np.minimum(np.maximum(x, lo), hi)


def deterministic_noise(count: int, *, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=count).astype(np.float64)


def profile_specs() -> list[dict[str, Any]]:
    count = 2048
    baseline_lo = np.full(count, -1.0)
    baseline_hi = np.full(count, 1.0)
    variable_lo = np.linspace(-4.0, -0.25, count)
    variable_hi = np.linspace(0.25, 4.0, count)
    boundary_lo = np.linspace(-2.0, -0.5, count)
    boundary_hi = np.linspace(0.5, 2.0, count)
    boundary_x = np.where(np.arange(count) % 2 == 0, boundary_lo, boundary_hi)
    noisy_lo = np.full(count, -1.5)
    noisy_hi = np.full(count, 1.5)
    noisy_x = np.linspace(-2.5, 2.5, count) + deterministic_noise(count, seed=9101, scale=0.02)
    invalid_lo = np.linspace(1.0, 2.0, count)
    invalid_hi = np.linspace(-2.0, -1.0, count)
    return [
        {"profile": "baseline_guard_grid", "noiseKind": "none", "x": np.linspace(-3.0, 3.0, count), "lo": baseline_lo, "hi": baseline_hi, "validBounds": True},
        {"profile": "variable_bounds_grid", "noiseKind": "variable_bounds", "x": np.linspace(-5.0, 5.0, count), "lo": variable_lo, "hi": variable_hi, "validBounds": True},
        {"profile": "boundary_equality_grid", "noiseKind": "boundary_exact", "x": boundary_x, "lo": boundary_lo, "hi": boundary_hi, "validBounds": True},
        {"profile": "noisy_input_guard_grid", "noiseKind": "input_perturbation", "x": noisy_x, "lo": noisy_lo, "hi": noisy_hi, "validBounds": True},
        {"profile": "invalid_reversed_bounds_grid", "noiseKind": "invalid_bounds", "x": np.linspace(-3.0, 3.0, count), "lo": invalid_lo, "hi": invalid_hi, "validBounds": False},
    ]


def agreement_metric(observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    errors = np.abs(observed - reference)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    return {
        "finiteRatio": float(np.mean(np.isfinite(observed))),
        "maxAbsError": max_abs,
        "meanAbsError": float(np.mean(errors)) if errors.size else float("inf"),
        "pass": bool(max_abs <= CRITERIA["maxAbsPass"] and float(np.mean(np.isfinite(observed))) == 1.0),
    }


def transition_counts(source: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> dict[str, int]:
    return {
        "lowerClampCount": int(np.sum(source == lo)),
        "upperClampCount": int(np.sum(source == hi)),
        "passThroughCount": int(np.sum((source > lo) & (source < hi))),
        "boundaryEqualityCount": int(np.sum((source == lo) | (source == hi))),
    }


def profile_result(spec: dict[str, Any]) -> dict[str, Any]:
    x = spec["x"].astype(np.float64)
    lo = spec["lo"].astype(np.float64)
    hi = spec["hi"].astype(np.float64)
    valid_bounds = bool(spec["validBounds"] and np.all(lo <= hi))
    if not valid_bounds:
        return {
            "profile": spec["profile"],
            "noiseKind": spec["noiseKind"],
            "sampleCount": int(x.size),
            "inputRanges": {"x": [float(x.min()), float(x.max())], "lo": [float(lo.min()), float(lo.max())], "hi": [float(hi.min()), float(hi.max())]},
            "validBounds": False,
            "blocked": True,
            "blockReason": "lo_must_be_less_than_or_equal_to_hi",
            "winner": "blocked_invalid_guard_domain",
        }
    source = source_clamp_guard(x, lo, hi)
    guarded = guarded_clamp_representation(x, lo, hi)
    agreement = agreement_metric(guarded, source)
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "sampleCount": int(x.size),
        "inputRanges": {"x": [float(x.min()), float(x.max())], "lo": [float(lo.min()), float(lo.max())], "hi": [float(hi.min()), float(hi.max())]},
        "validBounds": True,
        "blocked": False,
        "guardedVsSource": agreement,
        "transitionCounts": transition_counts(source, lo, hi),
        "winner": "guarded_piecewise_semantic_tie" if agreement["pass"] else "blocked",
    }


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_specs()]
    valid_profiles = [profile for profile in profiles if not profile["blocked"]]
    invalid_profiles = [profile for profile in profiles if profile["blocked"]]
    passing_profiles = [profile for profile in valid_profiles if profile["guardedVsSource"]["pass"]]
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_pcc9_guarded_piecewise_holdout_packet_v0",
        "date": DATE,
        "caseId": "efrog_clamp_guard_guarded_piecewise_holdout_v0",
        "sourceRepo": "efrog",
        "sourcePath": "examples/clamp_guard.py",
        "sourceSha256": source_digest(),
        "sourceLineCount": len(source_text.splitlines()),
        "sourceForm": "if x < lo: lo; elif x > hi: hi; else: x",
        "guardedForm": "min(max(x, lo), hi) under lo <= hi",
        "holdoutClass": "guarded_piecewise_semantic_tie_with_invalid_domain_block",
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "validProfileCount": len(valid_profiles),
            "invalidProfileCount": len(invalid_profiles),
            "passingValidProfiles": len(passing_profiles),
            "invalidBoundsBlockedProfiles": len(invalid_profiles),
            "boundaryProfileCount": sum(1 for profile in profiles if profile["noiseKind"] == "boundary_exact"),
            "runtimePerformanceClaim": False,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "guardSemanticsGeneralizationClaim": False,
            "branchCorrectnessClaim": False,
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
        "artifactId": "eml-adv-pcc9-guarded-piecewise-holdout",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "gapResponseKind": "guarded_piecewise_source_family_holdout",
        "selectedSource": "efrog/examples/clamp_guard.py",
        "holdoutPacket": packet,
        "summary": {
            "holdoutCount": 1,
            "sourceFamilyCount": 5,
            "sourceFamilies": ["rc_decay_stable", "gaussian_stable", "damped_wave", "numpy_softplus", "clamp_guard"],
            "profileCount": packet["summary"]["profileCount"],
            "validProfileCount": packet["summary"]["validProfileCount"],
            "passingValidProfiles": packet["summary"]["passingValidProfiles"],
            "invalidBoundsBlockedProfiles": packet["summary"]["invalidBoundsBlockedProfiles"],
            "sourceLinked": SOURCE_PATH.exists(),
            "guardDomainRequirement": "lo <= hi",
            "runtimeRecommendation": "preserve_guard_domains_before_lowering_to_clamp_style_form",
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "guardSemanticsGeneralizationClaim": False,
            "branchCorrectnessClaim": False,
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
        "artifactId": "eml-adv-pcc9-guarded-piecewise-holdout",
        "title": "EML-ADV-PCC9 Guarded/Piecewise Holdout",
        "reviewDecision": "private_guarded_piecewise_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_guard_sample_grid",
        "semanticStrength": "guarded_piecewise_sample_grid_agreement_with_invalid_domain_block_no_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private guarded/piecewise holdout for EML Advantage Lab contract only; no broad EML advantage, source-family generalization, guard-semantics generalization, branch correctness, protected-lowering correctness, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Adds clamp_guard.py as a fifth eFrog source family.",
            "Checks source branches against a clamp-style guarded representation under lo <= hi.",
            "Blocks reversed-bound cases as invalid guard domains.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc9_guarded_piecewise_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc9_guarded_piecewise_holdout.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc9.v0",
        "date": DATE,
        "title": "EML-ADV-PCC9 Guarded/Piecewise Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC10: add a family-level synthesis across smooth, log-domain, oscillatory, and guarded holdouts.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-ADV-PCC9 Guarded/Piecewise Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC9 adds `clamp_guard.py` as a guarded/piecewise eFrog source family.",
        "It compares source branches with a clamp-style guarded representation and blocks invalid bounds.",
        "",
        "| Profile | Noise | Winner | Valid bounds | Max abs error |",
        "|---|---|---|---:|---:|",
    ]
    for profile in packet["profiles"]:
        max_abs = profile.get("guardedVsSource", {}).get("maxAbsError", 0.0)
        lines.append(
            f"| `{profile['profile']}` | `{profile['noiseKind']}` | `{profile['winner']}` | "
            f"`{profile['validBounds']}` | `{max_abs:.3e}` |"
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
            f"- Valid profiles: `{summary['validProfileCount']}`",
            f"- Passing valid profiles: `{summary['passingValidProfiles']}`",
            f"- Invalid bounds blocked profiles: `{summary['invalidBoundsBlockedProfiles']}`",
            f"- Guard domain requirement: `{summary['guardDomainRequirement']}`",
            "",
            "## Boundary",
            "",
            "- Private guarded/piecewise holdout only.",
            "- No broad EML advantage, source-family generalization, guard-semantics generalization, branch correctness, protected-lowering correctness, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid PCC9 packet schema")
    summary = packet["summary"]
    if summary["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected PCC9 profile count")
    if summary["validProfileCount"] != CRITERIA["validProfileCount"]:
        raise ValueError("unexpected PCC9 valid profile count")
    if summary["invalidProfileCount"] != CRITERIA["invalidProfileCount"]:
        raise ValueError("unexpected PCC9 invalid profile count")
    if summary["passingValidProfiles"] != summary["validProfileCount"]:
        raise ValueError("expected all valid PCC9 profiles to pass")
    if summary["invalidBoundsBlockedProfiles"] != 1:
        raise ValueError("expected exactly one invalid bounds block")
    for key in [
        "runtimePerformanceClaim",
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "guardSemanticsGeneralizationClaim",
        "branchCorrectnessClaim",
        "protectedLoweringCorrectnessClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC9 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC9 status")
    summary = payload["summary"]
    if summary["holdoutCount"] != 1:
        raise ValueError("expected exactly one guarded/piecewise holdout")
    if summary["sourceFamilyCount"] < 5:
        raise ValueError("expected five source families after PCC9")
    if summary["sourceLinked"] is not True:
        raise ValueError("expected linked eFrog source")
    if summary["passingValidProfiles"] != summary["validProfileCount"]:
        raise ValueError("expected valid profiles to pass")
    if summary["invalidBoundsBlockedProfiles"] != 1:
        raise ValueError("expected one invalid bounds block")
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "guardSemanticsGeneralizationClaim",
        "branchCorrectnessClaim",
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
    result_path = out_dir / f"eml_advantage_pcc9_guarded_piecewise_holdout_{STAMP}.json"
    packet_path = packet_dir / f"{payload['holdoutPacket']['caseId']}_pcc9_guarded_piecewise_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc9_guarded_piecewise_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc9_guarded_piecewise_holdout.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc9_guarded_piecewise_holdout_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc9_guarded_piecewise_holdout")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc9_guarded_piecewise_holdout_packets")
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
    print("EML_ADV_PCC9_GUARDED_PIECEWISE_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
