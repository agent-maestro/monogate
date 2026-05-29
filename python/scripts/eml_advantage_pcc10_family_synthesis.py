#!/usr/bin/env python3
"""EML-ADV-PCC10 family-level synthesis.

Summarizes the current EML Advantage source-family run across smooth,
log-domain, oscillatory, and guarded holdouts. This is a private synthesis
artifact, not a broad EML advantage claim.
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
SCHEMA_VERSION = "monogate.eml_advantage_pcc10_family_synthesis.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC10_FAMILY_SYNTHESIS_PASS"

PATHS = {
    "rc_decay": ROOT / "python/results/eml_advantage_pcc4_noisy_real_source_holdout/eml_advantage_pcc4_noisy_real_source_holdout_2026_05_29.json",
    "gaussian": ROOT / "python/results/eml_advantage_pcc5_second_source_family_holdout/eml_advantage_pcc5_second_source_family_holdout_2026_05_29.json",
    "damped_wave": ROOT / "python/results/eml_advantage_pcc7_oscillatory_holdout/eml_advantage_pcc7_oscillatory_holdout_2026_05_29.json",
    "numpy_softplus": ROOT / "python/results/eml_advantage_pcc8_log_domain_holdout/eml_advantage_pcc8_log_domain_holdout_2026_05_29.json",
    "clamp_guard": ROOT / "python/results/eml_advantage_pcc9_guarded_piecewise_holdout/eml_advantage_pcc9_guarded_piecewise_holdout_2026_05_29.json",
}

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "family_level_generalization_claim": False,
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
    "PCC10 is a private synthesis over five holdout families, not a broad EML advantage benchmark.",
    "PCC10 does not prove source-family generalization, compiler correctness, formal equivalence, proof strength, runtime performance, or production readiness.",
    "PCC10 does not claim EML is generally superior to standard/protected mathematics.",
    "The synthesis identifies where EML helps representation and where protected or guarded standard forms remain required.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def family_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "familyId": "rc_decay",
            "source": "rc_decay_stable.py",
            "surface": "smooth_exponential_decay",
            "finding": "semantic_search_representation_tie",
            "emlRole": "full_exponential_envelope_representation",
            "runtimeRecommendation": "standard_or_protected_runtime_until_benchmarked",
            "payload": read_json(PATHS["rc_decay"]),
        },
        {
            "familyId": "gaussian",
            "source": "gaussian_stable.py",
            "surface": "quadratic_exponent_gaussian",
            "finding": "semantic_search_representation_tie",
            "emlRole": "full_exponential_kernel_representation",
            "runtimeRecommendation": "standard_or_protected_runtime_until_benchmarked",
            "payload": read_json(PATHS["gaussian"]),
        },
        {
            "familyId": "damped_wave",
            "source": "damped_wave.py",
            "surface": "oscillatory_with_decay",
            "finding": "partial_eml_coverage",
            "emlRole": "damping_envelope_only",
            "runtimeRecommendation": "standard_sine_surface_still_required",
            "payload": read_json(PATHS["damped_wave"]),
        },
        {
            "familyId": "numpy_softplus",
            "source": "numpy_softplus.py",
            "surface": "log_domain_softplus",
            "finding": "semantic_tie_with_protected_lowering_guard",
            "emlRole": "safe_range_representation",
            "runtimeRecommendation": "protected_logaddexp_for_overflow_prone_ranges",
            "payload": read_json(PATHS["numpy_softplus"]),
        },
        {
            "familyId": "clamp_guard",
            "source": "clamp_guard.py",
            "surface": "guarded_piecewise_branching",
            "finding": "guard_semantics_not_eml_operator_win",
            "emlRole": "none_guard_grammar_role",
            "runtimeRecommendation": "preserve_guard_domains_before_lowering",
            "payload": read_json(PATHS["clamp_guard"]),
        },
    ]
    for row in rows:
        summary = row["payload"]["summary"]
        row["profileCount"] = int(summary.get("profileCount", 0))
        row["sourceFamilyCountAtTime"] = int(summary.get("sourceFamilyCount", 0))
        row["publicReady"] = bool(summary.get("publicReady", False))
        row.pop("payload")
    return rows


def build_payload() -> dict[str, Any]:
    families = family_rows()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-adv-pcc10-family-synthesis",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "sourceEvidence": [str(path.relative_to(ROOT)) for path in PATHS.values()],
        "families": families,
        "decisionMap": {
            "representationHelpful": ["rc_decay", "gaussian", "damped_wave", "numpy_softplus"],
            "fullEmlCoverage": ["rc_decay", "gaussian"],
            "partialEmlCoverage": ["damped_wave", "numpy_softplus"],
            "protectedRuntimeRequired": ["numpy_softplus"],
            "guardGrammarRequired": ["clamp_guard"],
            "runtimeWinsClaimed": [],
            "publicClaimsAllowed": [],
        },
        "summary": {
            "sourceFamilyCount": len(families),
            "profileCount": sum(row["profileCount"] for row in families),
            "representationHelpfulFamilies": 4,
            "fullEmlCoverageFamilies": 2,
            "partialEmlCoverageFamilies": 2,
            "protectedRuntimeRequiredFamilies": 1,
            "guardGrammarRequiredFamilies": 1,
            "runtimeWinFamilies": 0,
            "publicClaimAllowedFamilies": 0,
            "recommendedPausePoint": True,
            "nextProductLanes": ["forge_efrog_productization", "monogate_engine_glassbox", "machlib_small_witness"],
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "familyLevelGeneralizationClaim": False,
            "runtimePerformanceClaim": False,
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
        "artifactId": "eml-adv-pcc10-family-synthesis",
        "title": "EML-ADV-PCC10 Family-Level Synthesis",
        "reviewDecision": "private_family_synthesis_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_synthesis_over_existing_holdouts",
        "semanticStrength": "five_family_synthesis_no_generalization_or_runtime_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private family-level synthesis only; no broad EML advantage, source-family generalization, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Summarizes five EML Advantage source families.",
            "Separates representation help, partial EML coverage, protected runtime need, and guard grammar need.",
            "Marks the source-family phase as a clean private pause point.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc10_family_synthesis.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc10_family_synthesis.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc10.v0",
        "date": DATE,
        "title": "EML-ADV-PCC10 Family-Level Synthesis",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Decide which product lane gets the research: Forge/eFrog, Monogate Engine, or MachLib.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-ADV-PCC10 Family-Level Synthesis",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC10 summarizes the current EML Advantage source-family phase.",
        "It is a private synthesis artifact, not a broad EML advantage claim.",
        "",
        "| Family | Surface | Finding | EML role | Runtime recommendation | Profiles |",
        "|---|---|---|---|---|---:|",
    ]
    for row in payload["families"]:
        lines.append(
            f"| `{row['familyId']}` | `{row['surface']}` | `{row['finding']}` | "
            f"`{row['emlRole']}` | `{row['runtimeRecommendation']}` | `{row['profileCount']}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Source families: `{summary['sourceFamilyCount']}`",
            f"- Profiles: `{summary['profileCount']}`",
            f"- Representation helpful families: `{summary['representationHelpfulFamilies']}`",
            f"- Full EML coverage families: `{summary['fullEmlCoverageFamilies']}`",
            f"- Partial EML coverage families: `{summary['partialEmlCoverageFamilies']}`",
            f"- Protected runtime required families: `{summary['protectedRuntimeRequiredFamilies']}`",
            f"- Guard grammar required families: `{summary['guardGrammarRequiredFamilies']}`",
            f"- Runtime win families: `{summary['runtimeWinFamilies']}`",
            f"- Recommended pause point: `{summary['recommendedPausePoint']}`",
            "",
            "## Boundary",
            "",
            "- Private family-level synthesis only.",
            "- No broad EML advantage, source-family generalization, runtime-performance, compiler-correctness, formal-equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC10 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC10 status")
    summary = payload["summary"]
    if summary["sourceFamilyCount"] != 5:
        raise ValueError("expected five source families")
    if summary["profileCount"] < 22:
        raise ValueError("expected at least 22 profiles")
    if summary["runtimeWinFamilies"] != 0:
        raise ValueError("PCC10 must not claim runtime wins")
    if summary["recommendedPausePoint"] is not True:
        raise ValueError("PCC10 should mark a pause point")
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "familyLevelGeneralizationClaim",
        "runtimePerformanceClaim",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    if payload["decisionMap"]["runtimeWinsClaimed"]:
        raise ValueError("runtimeWinsClaimed must be empty")
    if payload["decisionMap"]["publicClaimsAllowed"]:
        raise ValueError("publicClaimsAllowed must be empty")
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
    result_path = out_dir / f"eml_advantage_pcc10_family_synthesis_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc10_family_synthesis_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc10_family_synthesis.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc10_family_synthesis_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc10_family_synthesis")
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
    print("EML_ADV_PCC10_FAMILY_SYNTHESIS_OK")
    print(f"families={built['payload']['summary']['sourceFamilyCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
