#!/usr/bin/env python3
"""EML-S22 source-family generalization map.

S22 compares three next-candidate EML source families with a fixed review rule:
sigmoid/logistic, damped oscillator, and softplus/log-sum-exp. It promotes one
private next-source-family candidate for follow-up work. This is research
triage only, not a proof, runtime benchmark, compiler-correctness result, or
broad EML advantage claim.
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
SCHEMA_VERSION = "monogate.eml_s22_source_family_generalization_map.v0"
PROMOTION_PACKET_SCHEMA_VERSION = "monogate.eml_s22_source_family_promotion_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_S22_SOURCE_FAMILY_MAP_PASS"

PATHS = {
    "a13_2": ROOT / "python/results/eml_a13_2_semantic_output_comparison/eml_a13_2_semantic_output_comparison_2026_05_29.json",
    "a14": ROOT / "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
    "s20": ROOT / "python/results/eml_s20_style_atlas/eml_s20_style_atlas_2026_05_29.json",
    "s21": ROOT / "python/results/eml_s21_native_holdout/eml_s21_native_holdout_2026_05_29.json",
    "pcc7": ROOT / "python/results/eml_advantage_pcc7_oscillatory_holdout/eml_advantage_pcc7_oscillatory_holdout_2026_05_29.json",
    "pcc8": ROOT / "python/results/eml_advantage_pcc8_log_domain_holdout/eml_advantage_pcc8_log_domain_holdout_2026_05_29.json",
    "pcc10": ROOT / "python/results/eml_advantage_pcc10_family_synthesis/eml_advantage_pcc10_family_synthesis_2026_05_29.json",
}

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "family_level_generalization_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "formal_proof_claim": False,
    "prediction_accuracy_claim": False,
    "production_toolchain_claim": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "machlib_source_changed": False,
    "engine_behavior_changed": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "S22 is a private source-family triage map over existing evidence.",
    "S22 does not prove broad EML advantage, source-family generalization, runtime performance, compiler correctness, or formal equivalence.",
    "S22 does not change Forge, eFrog, MachLib, Monogate Engine, or public surfaces.",
    "The promotion packet is a next-work candidate, not a public product or correctness claim.",
]

DECISION_RULE = {
    "scale": "0_to_5_each",
    "fields": [
        "representationCompactness",
        "searchFriendliness",
        "semanticPreservation",
        "runtimeStability",
        "lowGuardBurden",
        "decompilerReadability",
        "roundtripMaturity",
    ],
    "promotionScoreFormula": (
        "representationCompactness + searchFriendliness + semanticPreservation + "
        "runtimeStability + lowGuardBurden + decompilerReadability + roundtripMaturity"
    ),
    "promotionTieBreakers": [
        "higher semanticPreservation",
        "higher lowGuardBurden",
        "higher roundtripMaturity",
        "lexicographic familyId",
    ],
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def semantic_case_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {case["caseId"]: case for case in payload["casePackets"]}


def style_by_family(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    packet_dir = ROOT / "python/results/eml_style_packets"
    rows: dict[str, dict[str, Any]] = {}
    for packet_id in payload["stylePacketIds"]:
        path = packet_dir / f"{packet_id}_{STAMP}.json"
        if path.exists():
            packet = read_json(path)
            rows[packet["familyId"]] = packet
    return rows


def pcc10_family_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["familyId"]: row for row in payload["families"]}


def score_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    scores = candidate["scores"]
    score = sum(int(scores[field]) for field in DECISION_RULE["fields"])
    out = dict(candidate)
    out["promotionScore"] = score
    if score >= 29:
        out["decisionLane"] = "promote_next_source_family_holdout"
    elif score >= 24:
        out["decisionLane"] = "keep_as_review_candidate"
    elif score >= 18:
        out["decisionLane"] = "keep_as_partial_or_protected_lane"
    else:
        out["decisionLane"] = "defer"
    return out


def build_candidates() -> list[dict[str, Any]]:
    a13_2 = read_json(PATHS["a13_2"])
    s20 = read_json(PATHS["s20"])
    pcc7 = read_json(PATHS["pcc7"])
    pcc8 = read_json(PATHS["pcc8"])
    pcc10 = read_json(PATHS["pcc10"])
    cases = semantic_case_by_id(a13_2)
    styles = style_by_family(s20)
    pcc10_by_family = pcc10_family_by_id(pcc10)

    sigmoid_case = cases["sigmoid_semantic_compare_v0"]
    damped_summary = pcc7["summary"]
    softplus_summary = pcc8["summary"]

    candidates = [
        {
            "familyId": "sigmoid_logistic",
            "candidateKind": "bounded_transition",
            "sourceFamily": "sigmoid.py",
            "sourceEvidence": [
                "python/results/eml_a13_2_semantic_output_comparison/eml_a13_2_semantic_output_comparison_2026_05_29.json",
                "python/results/eml_forge_efrog_semantic_comparison_packets/sigmoid_semantic_compare_v0_2026_05_29.json",
            ],
            "semanticEvidence": {
                "caseId": sigmoid_case["caseId"],
                "sampleCount": sigmoid_case["sampleCount"],
                "comparisonStatus": sigmoid_case["comparisonStatus"],
                "maxAbsError": sigmoid_case["maxAbsError"],
                "maxRelError": sigmoid_case["maxRelError"],
            },
            "styleEvidence": {
                "currentStyle": "standard_preferred",
                "why": "The surface is compact and readable, but the existing S20 family mapping treats it as a standard/protected runtime case until a dedicated holdout exists.",
            },
            "scores": {
                "representationCompactness": 4,
                "searchFriendliness": 5,
                "semanticPreservation": 5,
                "runtimeStability": 4,
                "lowGuardBurden": 4,
                "decompilerReadability": 5,
                "roundtripMaturity": 3,
            },
            "emlRole": "bounded_exponential_transition_representation",
            "runtimeRecommendation": "standard_or_protected_sigmoid_runtime_until_large_range_benchmark",
            "nextAction": "promote_sigmoid_logistic_to_dedicated_source_holdout_with_overflow_guard_profile",
        },
        {
            "familyId": "damped_oscillator",
            "candidateKind": "oscillatory_envelope",
            "sourceFamily": "damped_wave.py",
            "sourceEvidence": [
                "python/results/eml_advantage_pcc7_oscillatory_holdout/eml_advantage_pcc7_oscillatory_holdout_2026_05_29.json",
            ],
            "semanticEvidence": {
                "profileCount": damped_summary["profileCount"],
                "allProfilesPass": damped_summary["allProfilesPass"],
                "noisyOutputProfileCount": damped_summary["noisyOutputProfileCount"],
            },
            "styleEvidence": {
                "currentStyle": styles.get("damped_wave", {}).get("primaryStyle", "eml_partial"),
                "pcc10Finding": pcc10_by_family["damped_wave"]["finding"],
            },
            "scores": {
                "representationCompactness": 3,
                "searchFriendliness": 3,
                "semanticPreservation": 5,
                "runtimeStability": 4,
                "lowGuardBurden": 4,
                "decompilerReadability": 4,
                "roundtripMaturity": 3,
            },
            "emlRole": "exponential_damping_envelope_only",
            "runtimeRecommendation": "keep_sine_surface_standard_and_use_eml_for_envelope_search",
            "nextAction": "keep_as_partial_eml_lane_until_oscillatory_grammar_is_explicit",
        },
        {
            "familyId": "softplus_logsumexp",
            "candidateKind": "log_domain_protected",
            "sourceFamily": "numpy_softplus.py",
            "sourceEvidence": [
                "python/results/eml_advantage_pcc8_log_domain_holdout/eml_advantage_pcc8_log_domain_holdout_2026_05_29.json",
            ],
            "semanticEvidence": {
                "profileCount": softplus_summary["profileCount"],
                "safeSemanticTieProfiles": softplus_summary["safeSemanticTieProfiles"],
                "protectedLoweringRecommendedProfiles": softplus_summary["protectedLoweringRecommendedProfiles"],
                "allProtectedProfilesFinite": softplus_summary["allProtectedProfilesFinite"],
            },
            "styleEvidence": {
                "currentStyle": styles.get("numpy_softplus", {}).get("primaryStyle", "eml_partial"),
                "pcc10Finding": pcc10_by_family["numpy_softplus"]["finding"],
            },
            "scores": {
                "representationCompactness": 4,
                "searchFriendliness": 4,
                "semanticPreservation": 4,
                "runtimeStability": 5,
                "lowGuardBurden": 2,
                "decompilerReadability": 4,
                "roundtripMaturity": 3,
            },
            "emlRole": "log_domain_semantic_representation_with_protected_runtime_requirement",
            "runtimeRecommendation": "protected_logaddexp_runtime_for_overflow_prone_ranges",
            "nextAction": "keep_as_protected_lowering_lane_not_primary_holdout_promotion",
        },
    ]
    return [score_candidate(candidate) for candidate in candidates]


def promotion_sort_key(candidate: dict[str, Any]) -> tuple[int, int, int, int, str]:
    scores = candidate["scores"]
    return (
        int(candidate["promotionScore"]),
        int(scores["semanticPreservation"]),
        int(scores["lowGuardBurden"]),
        int(scores["roundtripMaturity"]),
        candidate["familyId"],
    )


def build_promotion_packet(winner: dict[str, Any]) -> dict[str, Any]:
    packet = {
        "schemaVersion": PROMOTION_PACKET_SCHEMA_VERSION,
        "packetType": "eml_s22_source_family_promotion_packet_v0",
        "date": DATE,
        "promotionId": "sigmoid_logistic_next_holdout_candidate_v0",
        "familyId": winner["familyId"],
        "candidateKind": winner["candidateKind"],
        "decisionLane": winner["decisionLane"],
        "promotionScore": winner["promotionScore"],
        "scores": winner["scores"],
        "sourceFamily": winner["sourceFamily"],
        "emlRole": winner["emlRole"],
        "runtimeRecommendation": winner["runtimeRecommendation"],
        "nextAction": winner["nextAction"],
        "requiredNextEvidence": [
            "dedicated eFrog holdout trial for examples/sigmoid.py or stable_sigmoid.py",
            "large positive/negative range profile to expose overflow boundaries",
            "Forge/eFrog roundtrip hash link for the dedicated holdout fixture",
            "semantic sample-grid packet distinct from the existing basic sigmoid example",
            "claim guard that keeps runtime and generalization claims false",
        ],
        "blockedClaims": [
            "broad_eml_advantage",
            "source_family_generalization",
            "runtime_performance",
            "compiler_correctness",
            "formal_equivalence",
            "production_toolchain",
            "public_readiness",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_promotion_packet(packet)
    return packet


def build_payload() -> dict[str, Any]:
    candidates = build_candidates()
    winner = sorted(candidates, key=promotion_sort_key, reverse=True)[0]
    promotion_packet = build_promotion_packet(winner)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-s22-source-family-generalization-map",
        "decisionRule": DECISION_RULE,
        "sourceEvidence": [str(path.relative_to(ROOT)) for path in PATHS.values()],
        "candidateFamilies": candidates,
        "promotionPacket": promotion_packet,
        "summary": {
            "candidateFamilyCount": len(candidates),
            "selectedPromotionFamily": winner["familyId"],
            "selectedPromotionScore": winner["promotionScore"],
            "promotionPacketId": promotion_packet["promotionId"],
            "promoteNextSourceFamilyHoldoutCount": sum(
                1 for candidate in candidates if candidate["decisionLane"] == "promote_next_source_family_holdout"
            ),
            "reviewCandidateCount": sum(
                1 for candidate in candidates if candidate["decisionLane"] == "keep_as_review_candidate"
            ),
            "partialOrProtectedLaneCount": sum(
                1 for candidate in candidates if candidate["decisionLane"] == "keep_as_partial_or_protected_lane"
            ),
            "publicReady": False,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "familyLevelGeneralizationClaim": False,
            "runtimePerformanceClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextResearchQuestion": "Run the promoted sigmoid/logistic source-family holdout with explicit overflow-boundary evidence.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-s22-source-family-generalization-map",
        "title": "EML-S22 Source-Family Generalization Map",
        "reviewDecision": "private_source_family_triage_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_synthesis_over_existing_evidence",
        "semanticStrength": "three_family_decision_map_no_generalization_or_runtime_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private source-family triage only; no broad EML advantage, source-family generalization, runtime-performance, compiler-correctness, formal-equivalence, proof, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Compares sigmoid/logistic, damped oscillator, and softplus/log-sum-exp as next source-family candidates.",
            "Uses a fixed seven-field decision rule instead of narrative preference.",
            "Promotes sigmoid/logistic as the next private holdout candidate while keeping all public/runtime/proof claims blocked.",
        ],
        "validationCommands": [
            "python python/scripts/eml_s22_source_family_generalization_map.py --build --strict",
            "python -m pytest -q python/tests/test_eml_s22_source_family_generalization_map.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_s22_source_family_generalization_map.v0",
        "date": DATE,
        "title": "EML-S22 Source-Family Generalization Map",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": payload["nextResearchQuestion"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-S22 Source-Family Generalization Map",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "S22 turns the next EML research question into a deterministic source-family map.",
        "It is private triage over existing evidence, not a proof, benchmark, compiler change, or public claim.",
        "",
        "## Decision Rule",
        "",
        f"Formula: `{payload['decisionRule']['promotionScoreFormula']}`",
        "",
        "| Family | Kind | Score | Lane | EML role | Runtime recommendation |",
        "|---|---|---:|---|---|---|",
    ]
    for candidate in payload["candidateFamilies"]:
        lines.append(
            f"| `{candidate['familyId']}` | `{candidate['candidateKind']}` | "
            f"`{candidate['promotionScore']}` | `{candidate['decisionLane']}` | "
            f"`{candidate['emlRole']}` | `{candidate['runtimeRecommendation']}` |"
        )
    packet = payload["promotionPacket"]
    lines.extend(
        [
            "",
            "## Promoted Candidate",
            "",
            f"- Family: `{packet['familyId']}`",
            f"- Promotion id: `{packet['promotionId']}`",
            f"- Next action: `{packet['nextAction']}`",
            "",
            "Required next evidence:",
            "",
        ]
    )
    for item in packet["requiredNextEvidence"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No broad EML advantage claim.",
            "- No source-family generalization claim.",
            "- No runtime performance claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No proof, deployment, package publish, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_promotion_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PROMOTION_PACKET_SCHEMA_VERSION:
        raise ValueError("invalid S22 promotion packet schema")
    if packet["familyId"] != "sigmoid_logistic":
        raise ValueError("S22 currently expects sigmoid/logistic as selected promotion candidate")
    if packet["decisionLane"] != "promote_next_source_family_holdout":
        raise ValueError("selected packet must be in promotion lane")
    if packet["promotionScore"] < 29:
        raise ValueError("promotion score below threshold")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid S22 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid S22 status")
    summary = payload["summary"]
    if summary["candidateFamilyCount"] != 3:
        raise ValueError("S22 must compare exactly three candidate families")
    if summary["selectedPromotionFamily"] != "sigmoid_logistic":
        raise ValueError("unexpected S22 promotion family")
    if summary["promoteNextSourceFamilyHoldoutCount"] != 1:
        raise ValueError("S22 should promote exactly one family")
    validate_promotion_packet(payload["promotionPacket"])
    candidate_ids = {candidate["familyId"] for candidate in payload["candidateFamilies"]}
    if candidate_ids != {"sigmoid_logistic", "damped_oscillator", "softplus_logsumexp"}:
        raise ValueError("unexpected S22 candidate families")
    for key in [
        "publicReady",
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "familyLevelGeneralizationClaim",
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


def build_outputs(
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_s22_source_family_generalization_map_{STAMP}.json"
    packet_path = packet_dir / f"{payload['promotionPacket']['promotionId']}_{STAMP}.json"
    report_path = report_dir / f"eml_s22_source_family_generalization_map_{STAMP}.md"
    evidence_path = evidence_dir / "eml_s22_source_family_generalization_map.json"
    feed_path = command_feed_dir / f"eml_s22_source_family_generalization_map_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    packet_path.write_text(
        json.dumps(payload["promotionPacket"], indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_s22_source_family_generalization_map")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_s22_promotion_packets")
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
    print("EML_S22_SOURCE_FAMILY_MAP_OK")
    print(f"candidates={built['payload']['summary']['candidateFamilyCount']}")
    print(f"selected={built['payload']['summary']['selectedPromotionFamily']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
