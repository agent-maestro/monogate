#!/usr/bin/env python3
"""EML-ADV-PCC2 gap response.

Adds one concrete protected-runtime negative control to the EML Advantage Lab
proof-carrying contract. The experiment checks the cancellation-sensitive
`exp(x)-1` lane and records that protected standard `expm1` is the correct
lowering there.
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
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_advantage_pcc2_gap_response.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_pcc2_negative_control_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC2_GAP_RESPONSE_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
    "protected_runtime_complete_claim": False,
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
    "PCC2 is one protected-runtime negative control, not an exhaustive holdout suite.",
    "PCC2 does not prove broad EML advantage or general EML superiority.",
    "PCC2 does not claim public runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, or public readiness.",
    "The result supports a local lowering rule: use protected expm1 near cancellation-sensitive exp(x)-1 regions.",
]

CRITERIA = {
    "standardWinImprovementFactor": 10.0,
    "finiteRatioPass": 1.0,
    "profileCount": 3,
}


def raw_eml_expm1(xs: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore"):
        return np.exp(xs) - 1.0


def reference_expm1(xs: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore"):
        return np.asarray(np.expm1(xs.astype(np.longdouble)), dtype=np.float64)


def metric(observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(observed) & np.isfinite(reference)
    errors = np.abs(observed[finite] - reference[finite])
    rel = errors / np.maximum(np.abs(reference[finite]), 1.0e-300)
    return {
        "finiteRatio": float(np.mean(np.isfinite(observed))),
        "maxAbsError": float(np.max(errors)) if errors.size else float("inf"),
        "maxRelError": float(np.max(rel)) if rel.size else float("inf"),
        "meanRelError": float(np.mean(rel)) if rel.size else float("inf"),
    }


def profile_grids() -> list[dict[str, Any]]:
    return [
        {
            "profile": "tiny_symmetric_holdout",
            "description": "values where exp(x)-1 suffers cancellation",
            "xs": np.concatenate(
                [
                    np.linspace(-1.0e-12, -1.0e-16, 1024),
                    np.linspace(1.0e-16, 1.0e-12, 1024),
                ]
            ),
        },
        {
            "profile": "small_symmetric_holdout",
            "description": "small but not microscopic cancellation region",
            "xs": np.concatenate(
                [
                    np.linspace(-1.0e-8, -1.0e-12, 1024),
                    np.linspace(1.0e-12, 1.0e-8, 1024),
                ]
            ),
        },
        {
            "profile": "one_sided_positive_edge",
            "description": "positive edge where protected lowering should remain safe",
            "xs": np.geomspace(1.0e-16, 1.0e-6, 2048),
        },
    ]


def profile_result(spec: dict[str, Any]) -> dict[str, Any]:
    xs = spec["xs"].astype(np.float64)
    reference = reference_expm1(xs)
    eml_observed = raw_eml_expm1(xs)
    standard_observed = np.expm1(xs)
    eml_metric = metric(eml_observed, reference)
    standard_metric = metric(standard_observed, reference)
    improvement = eml_metric["meanRelError"] / max(standard_metric["meanRelError"], 1.0e-300)
    winner = "standard" if improvement >= CRITERIA["standardWinImprovementFactor"] else "mixed"
    return {
        "profile": spec["profile"],
        "description": spec["description"],
        "inputMin": float(xs.min()),
        "inputMax": float(xs.max()),
        "sampleCount": int(xs.size),
        "emlRaw": eml_metric,
        "standardProtected": standard_metric,
        "meanRelativeErrorImprovementFactor": float(improvement),
        "winner": winner,
    }


def build_negative_control_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in profile_grids()]
    standard_wins = sum(1 for profile in profiles if profile["winner"] == "standard")
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_pcc2_negative_control_packet_v0",
        "date": DATE,
        "caseId": "protected_expm1_cancellation_negative_control_v0",
        "gapId": "eml-advantage-runtime-performance-non-claim",
        "emlForm": "eml(x,e) = exp(x) - 1",
        "standardForm": "expm1(x)",
        "expectedWinner": "standard",
        "negativeControlClass": "protected_runtime_cancellation",
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "standardWinProfiles": standard_wins,
            "emlWinProfiles": sum(1 for profile in profiles if profile["winner"] == "eml"),
            "allProfilesFavorProtectedStandard": standard_wins == len(profiles),
            "criteria": dict(CRITERIA),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_payload() -> dict[str, Any]:
    packet = build_negative_control_packet()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-adv-pcc2-gap-response",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "gapResponseKind": "protected_runtime_negative_control",
        "selectedGap": "runtime/performance non-claim needs explicit protected-runtime counterexample evidence",
        "negativeControlPacket": packet,
        "summary": {
            "negativeControlCount": 1,
            "profileCount": packet["summary"]["profileCount"],
            "standardWinProfiles": packet["summary"]["standardWinProfiles"],
            "allProfilesFavorProtectedStandard": packet["summary"]["allProfilesFavorProtectedStandard"],
            "broadEmlAdvantageClaim": False,
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
        "artifactId": "eml-adv-pcc2-gap-response",
        "title": "EML-ADV-PCC2 Gap Response",
        "reviewDecision": "private_gap_response_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_numeric_holdout",
        "semanticStrength": "protected_runtime_negative_control_no_broad_advantage_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private protected-runtime negative control for EML Advantage Lab contract only; no broad EML advantage, public runtime performance, compiler correctness, formal equivalence, proof, production, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Adds a concrete cancellation-sensitive negative control.",
            "Records protected expm1 as the correct lowering for exp(x)-1 near zero.",
            "Keeps broad EML advantage and runtime-performance claims blocked.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc2_gap_response.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc2_gap_response.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc2.v0",
        "date": DATE,
        "title": "EML-ADV-PCC2 Gap Response",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC3: add a non-cancellation holdout from the eFrog registry or a noisy-data source.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["negativeControlPacket"]
    lines = [
        "# EML-ADV-PCC2 Gap Response",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC2 responds to one EML Advantage Lab contract gap with a protected-runtime negative control.",
        "It checks the cancellation-sensitive lane where raw `eml(x,e) = exp(x)-1` should lose to protected `expm1(x)`.",
        "",
        "| Profile | Winner | Mean relative error improvement |",
        "|---|---|---:|",
    ]
    for profile in packet["profiles"]:
        lines.append(
            f"| `{profile['profile']}` | `{profile['winner']}` | "
            f"`{profile['meanRelativeErrorImprovementFactor']:.3e}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Negative controls: `{summary['negativeControlCount']}`",
            f"- Profiles: `{summary['profileCount']}`",
            f"- Standard-win profiles: `{summary['standardWinProfiles']}`",
            f"- All profiles favor protected standard: `{summary['allProfilesFavorProtectedStandard']}`",
            f"- Broad EML advantage claim: `{summary['broadEmlAdvantageClaim']}`",
            f"- Runtime performance claim: `{summary['runtimePerformanceClaim']}`",
            "",
            "## Boundary",
            "",
            "- Private gap response only.",
            "- No broad EML advantage, public runtime performance, compiler correctness, formal equivalence, proof, production, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC2 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC2 status")
    summary = payload["summary"]
    if summary["negativeControlCount"] != 1:
        raise ValueError("expected exactly one negative control")
    if summary["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected profile count")
    if summary["standardWinProfiles"] != summary["profileCount"]:
        raise ValueError("expected protected standard to win all PCC2 profiles")
    for key in ["broadEmlAdvantageClaim", "runtimePerformanceClaim", "publicReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    packet = payload["negativeControlPacket"]
    if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid negative-control packet schema")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def build_outputs(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)

    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)

    result_path = out_dir / f"eml_advantage_pcc2_gap_response_{STAMP}.json"
    packet_path = packet_dir / f"{payload['negativeControlPacket']['caseId']}_pcc2_negative_control_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc2_gap_response_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc2_gap_response.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc2_gap_response_feed_{STAMP}.json"

    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    packet_path.write_text(
        json.dumps(payload["negativeControlPacket"], indent=2, sort_keys=True, allow_nan=False) + "\n",
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc2_gap_response")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc2_negative_control_packets")
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
    print("EML_ADV_PCC2_GAP_RESPONSE_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
