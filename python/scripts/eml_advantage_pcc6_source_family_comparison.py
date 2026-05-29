#!/usr/bin/env python3
"""EML-ADV-PCC6 source-family comparison report.

Compares the RC decay and Gaussian EML Advantage holdouts. PCC6 is a synthesis
artifact over existing evidence; it does not add a new mathematical proof,
runtime benchmark, or source-family generalization claim.
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
SCHEMA_VERSION = "monogate.eml_advantage_pcc6_source_family_comparison.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC6_SOURCE_FAMILY_COMPARISON_PASS"

PCC4_PATH = ROOT / "python/results/eml_advantage_pcc4_noisy_real_source_holdout/eml_advantage_pcc4_noisy_real_source_holdout_2026_05_29.json"
PCC5_PATH = ROOT / "python/results/eml_advantage_pcc5_second_source_family_holdout/eml_advantage_pcc5_second_source_family_holdout_2026_05_29.json"

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
    "PCC6 compares two private source-family holdouts; it is not a broad source-family benchmark.",
    "PCC6 does not prove broad EML advantage, source-family generalization, noise robustness, or prediction accuracy.",
    "PCC6 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "PCC6 is a synthesis artifact over existing PCC4/PCC5 evidence, not a new proof or live runtime measurement.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def family_record(payload: dict[str, Any], *, family_id: str, source_family: str, shape: str) -> dict[str, Any]:
    packet = payload["holdoutPacket"]
    profiles = packet["profiles"]
    max_abs = max(profile["emlShapedVsSource"]["maxAbsError"] for profile in profiles)
    max_rel = max(profile["emlShapedVsSource"]["maxRelError"] for profile in profiles)
    noisy_profiles = [profile for profile in profiles if profile["noiseKind"] == "output_observation"]
    max_noisy_rmse = max((profile["emlShapedVsNoisyObservation"]["rmse"] for profile in noisy_profiles), default=0.0)
    return {
        "familyId": family_id,
        "sourceFamily": source_family,
        "sourcePath": packet["sourcePath"],
        "shape": shape,
        "standardForm": packet["standardForm"],
        "emlForm": packet["emlForm"],
        "profileCount": packet["summary"]["profileCount"],
        "passingProfiles": packet["summary"]["passingProfiles"],
        "noisyOutputProfileCount": packet["summary"]["noisyOutputProfileCount"],
        "maxAgreementAbsError": max_abs,
        "maxAgreementRelError": max_rel,
        "maxNoisyObservationRmse": max_noisy_rmse,
        "classification": "semantic_search_representation_tie_not_runtime_win",
        "runtimeRecommendation": "prefer_standard_or_protected_runtime_form_until_runtime_benchmarks_exist",
    }


def build_payload() -> dict[str, Any]:
    pcc4 = read_json(PCC4_PATH)
    pcc5 = read_json(PCC5_PATH)
    families = [
        family_record(pcc4, family_id="rc_decay", source_family="rc_decay_stable", shape="single exponential decay envelope"),
        family_record(pcc5, family_id="gaussian", source_family="gaussian_stable", shape="quadratic exponent with sigma normalization"),
    ]
    profile_count = sum(family["profileCount"] for family in families)
    passing_profiles = sum(family["passingProfiles"] for family in families)
    noisy_output_profiles = sum(family["noisyOutputProfileCount"] for family in families)
    max_abs = max(family["maxAgreementAbsError"] for family in families)
    max_rel = max(family["maxAgreementRelError"] for family in families)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-adv-pcc6-source-family-comparison",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "comparisonKind": "rc_decay_vs_gaussian_source_family_synthesis",
        "sourceEvidence": [
            "reports/evidence_packets/eml_advantage_pcc4_noisy_real_source_holdout.json",
            "reports/evidence_packets/eml_advantage_pcc5_second_source_family_holdout.json",
        ],
        "families": families,
        "summary": {
            "sourceFamilyCount": len(families),
            "profileCount": profile_count,
            "passingProfiles": passing_profiles,
            "noisyOutputProfileCount": noisy_output_profiles,
            "allProfilesPass": passing_profiles == profile_count,
            "maxAgreementAbsError": max_abs,
            "maxAgreementRelError": max_rel,
            "semanticRepresentationTieFamilies": len(families),
            "runtimeWinFamilies": 0,
            "standardRuntimeRecommendedFamilies": len(families),
            "nextHoldoutFamily": "oscillatory_damped_wave",
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
        "artifactId": "eml-adv-pcc6-source-family-comparison",
        "title": "EML-ADV-PCC6 Source-Family Comparison",
        "reviewDecision": "private_source_family_comparison_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_synthesis_over_existing_holdouts",
        "semanticStrength": "two_family_semantic_search_representation_synthesis_no_generalization_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private source-family comparison over RC decay and Gaussian holdouts only; no broad EML advantage, source-family generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Compares RC decay and Gaussian stable source families side by side.",
            "Records EML as a semantic/search representation tie across both families.",
            "Keeps standard/protected runtime forms as the runtime recommendation.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc6_source_family_comparison.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc6_source_family_comparison.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc6.v0",
        "date": DATE,
        "title": "EML-ADV-PCC6 Source-Family Comparison",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC7: add an oscillatory eFrog holdout using damped_wave.py.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-ADV-PCC6 Source-Family Comparison",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC6 compares the RC decay and Gaussian stable eFrog holdouts.",
        "It is a private synthesis artifact, not a broad EML advantage claim.",
        "",
        "| Family | Shape | Profiles | Passing | Max abs agreement error | Noisy RMSE max | Classification |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for family in payload["families"]:
        lines.append(
            f"| `{family['sourceFamily']}` | {family['shape']} | `{family['profileCount']}` | "
            f"`{family['passingProfiles']}` | `{family['maxAgreementAbsError']:.3e}` | "
            f"`{family['maxNoisyObservationRmse']:.3e}` | `{family['classification']}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Source families: `{summary['sourceFamilyCount']}`",
            f"- Profiles: `{summary['profileCount']}`",
            f"- Passing profiles: `{summary['passingProfiles']}`",
            f"- Semantic/search representation tie families: `{summary['semanticRepresentationTieFamilies']}`",
            f"- Runtime win families: `{summary['runtimeWinFamilies']}`",
            f"- Standard/protected runtime recommended families: `{summary['standardRuntimeRecommendedFamilies']}`",
            f"- Next holdout family: `{summary['nextHoldoutFamily']}`",
            "",
            "## Boundary",
            "",
            "- Private two-family comparison only.",
            "- No broad EML advantage, source-family generalization, noise-robustness, prediction-accuracy, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC6 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC6 status")
    summary = payload["summary"]
    if summary["sourceFamilyCount"] != 2:
        raise ValueError("expected exactly two compared source families")
    if summary["profileCount"] < 8:
        raise ValueError("expected at least eight comparison profiles")
    if summary["passingProfiles"] != summary["profileCount"]:
        raise ValueError("expected all compared profiles to pass")
    if summary["runtimeWinFamilies"] != 0:
        raise ValueError("PCC6 must not report runtime wins")
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
    for family in payload["families"]:
        if family["classification"] != "semantic_search_representation_tie_not_runtime_win":
            raise ValueError("unexpected family classification")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_advantage_pcc6_source_family_comparison_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc6_source_family_comparison_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc6_source_family_comparison.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc6_source_family_comparison_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc6_source_family_comparison")
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
    print("EML_ADV_PCC6_SOURCE_FAMILY_COMPARISON_OK")
    print(f"families={built['payload']['summary']['sourceFamilyCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
