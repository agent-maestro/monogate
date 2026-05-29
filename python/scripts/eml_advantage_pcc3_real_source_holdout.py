#!/usr/bin/env python3
"""EML-ADV-PCC3 real-source holdout.

Connects the EML Advantage Lab contract to one non-cancellation eFrog holdout
source. The selected kernel is `examples/rc_decay_stable.py`, and the check is
a deterministic sample-grid comparison between the source formula and an
EML-shaped exponential expression.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
SCHEMA_VERSION = "monogate.eml_advantage_pcc3_real_source_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_pcc3_real_source_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADV_PCC3_REAL_SOURCE_HOLDOUT_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "broad_eml_advantage_claim": False,
    "real_world_generalization_claim": False,
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
    "PCC3 is one private real-source holdout, not a broad real-world benchmark.",
    "PCC3 does not prove broad EML advantage or general EML superiority.",
    "PCC3 does not claim runtime performance, compiler correctness, formal equivalence, proof strength, production readiness, public readiness, or deployment.",
    "The source link is to an eFrog holdout fixture; it is not a live hardware or production trace.",
]

CRITERIA = {
    "profileCount": 3,
    "maxAbsErrorPass": 1.0e-12,
    "maxRelErrorPass": 1.0e-12,
    "finiteRatioPass": 1.0,
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


def grids() -> list[dict[str, Any]]:
    count = 2048
    return [
        {
            "profile": "nominal_decay_grid",
            "v0": np.linspace(0.25, 5.0, count),
            "tau": np.linspace(0.2, 5.0, count),
            "t": np.linspace(0.0, 12.0, count),
        },
        {
            "profile": "long_tail_decay_grid",
            "v0": np.linspace(1.0, 10.0, count),
            "tau": np.geomspace(0.1, 20.0, count),
            "t": np.geomspace(1.0e-9, 200.0, count),
        },
        {
            "profile": "small_tau_edge_grid",
            "v0": np.linspace(0.1, 2.0, count),
            "tau": np.geomspace(1.0e-4, 0.25, count),
            "t": np.linspace(0.0, 2.0, count),
        },
    ]


def metric(observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
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
            and max_abs <= CRITERIA["maxAbsErrorPass"]
            and max_rel <= CRITERIA["maxRelErrorPass"]
        ),
    }


def profile_result(spec: dict[str, Any]) -> dict[str, Any]:
    v0 = spec["v0"].astype(np.float64)
    tau = spec["tau"].astype(np.float64)
    t = spec["t"].astype(np.float64)
    reference = standard_rc_decay(v0, tau, t)
    eml_observed = eml_shaped_rc_decay(v0, tau, t)
    eml_metric = metric(eml_observed, reference)
    return {
        "profile": spec["profile"],
        "sampleCount": int(v0.size),
        "inputRanges": {
            "v0": [float(v0.min()), float(v0.max())],
            "tau": [float(tau.min()), float(tau.max())],
            "t": [float(t.min()), float(t.max())],
        },
        "emlShapedVsSource": eml_metric,
        "winner": "semantic_tie" if eml_metric["pass"] else "blocked",
    }


def build_holdout_packet() -> dict[str, Any]:
    profiles = [profile_result(spec) for spec in grids()]
    pass_count = sum(1 for profile in profiles if profile["emlShapedVsSource"]["pass"])
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_pcc3_real_source_holdout_packet_v0",
        "date": DATE,
        "caseId": "efrog_rc_decay_stable_real_source_holdout_v0",
        "sourceRepo": "efrog",
        "sourcePath": "examples/rc_decay_stable.py",
        "sourceSha256": source_digest(),
        "sourceLineCount": len(source_text.splitlines()),
        "standardForm": "v0 * exp(-t / (tau*tau + 1))",
        "emlForm": "v0 * eml(-t / (tau*tau + 1), 1)",
        "holdoutClass": "real_source_semantic_tie",
        "profiles": profiles,
        "summary": {
            "profileCount": len(profiles),
            "passingProfiles": pass_count,
            "blockedProfiles": len(profiles) - pass_count,
            "allProfilesPass": pass_count == len(profiles),
            "runtimePerformanceClaim": False,
            "broadEmlAdvantageClaim": False,
            "realWorldGeneralizationClaim": False,
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
        "artifactId": "eml-adv-pcc3-real-source-holdout",
        "contractId": "eml-advantage-lab-proof-carrying-artifact-contract",
        "gapResponseKind": "real_source_non_cancellation_holdout",
        "selectedSource": "efrog/examples/rc_decay_stable.py",
        "holdoutPacket": packet,
        "summary": {
            "holdoutCount": 1,
            "profileCount": packet["summary"]["profileCount"],
            "passingProfiles": packet["summary"]["passingProfiles"],
            "allProfilesPass": packet["summary"]["allProfilesPass"],
            "sourceLinked": SOURCE_PATH.exists(),
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
        "artifactId": "eml-adv-pcc3-real-source-holdout",
        "title": "EML-ADV-PCC3 Real-Source Holdout",
        "reviewDecision": "private_real_source_holdout_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_sample_grid",
        "semanticStrength": "real_source_semantic_tie_no_runtime_or_broad_advantage_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private real-source holdout for EML Advantage Lab contract only; no broad EML advantage, runtime performance, compiler correctness, formal equivalence, proof, production, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Links the EML Advantage contract to an actual eFrog holdout source.",
            "Checks the non-cancellation RC decay kernel on three deterministic sample grids.",
            "Records EML as a semantic/search representation, not a runtime-performance win.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_pcc3_real_source_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_pcc3_real_source_holdout.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_adv_pcc3.v0",
        "date": DATE,
        "title": "EML-ADV-PCC3 Real-Source Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-ADV-PCC4: add noisy-data perturbation around the real-source holdout or ingest a second eFrog source.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    packet = payload["holdoutPacket"]
    lines = [
        "# EML-ADV-PCC3 Real-Source Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC3 links the EML Advantage proof-carrying contract to a real eFrog holdout source.",
        "The selected source is `examples/rc_decay_stable.py`.",
        "",
        "| Profile | Winner | Max abs error | Max rel error |",
        "|---|---|---:|---:|",
    ]
    for profile in packet["profiles"]:
        metric_row = profile["emlShapedVsSource"]
        lines.append(
            f"| `{profile['profile']}` | `{profile['winner']}` | "
            f"`{metric_row['maxAbsError']:.3e}` | `{metric_row['maxRelError']:.3e}` |"
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
            f"- Source linked: `{summary['sourceLinked']}`",
            f"- Broad EML advantage claim: `{summary['broadEmlAdvantageClaim']}`",
            f"- Runtime performance claim: `{summary['runtimePerformanceClaim']}`",
            "",
            "## Boundary",
            "",
            "- Private real-source holdout only.",
            "- No broad EML advantage, runtime performance, compiler correctness, formal equivalence, proof, production, deployment, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid PCC3 packet schema")
    if packet["summary"]["profileCount"] != CRITERIA["profileCount"]:
        raise ValueError("unexpected PCC3 profile count")
    if packet["summary"]["passingProfiles"] != packet["summary"]["profileCount"]:
        raise ValueError("expected all PCC3 profiles to pass")
    if not packet["sourceSha256"].startswith("sha256:"):
        raise ValueError("source digest must be sha256")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid PCC3 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid PCC3 status")
    summary = payload["summary"]
    if summary["holdoutCount"] != 1:
        raise ValueError("expected exactly one real-source holdout")
    if summary["sourceLinked"] is not True:
        raise ValueError("expected linked eFrog source")
    if summary["allProfilesPass"] is not True:
        raise ValueError("expected all PCC3 profiles to pass")
    for key in ["broadEmlAdvantageClaim", "runtimePerformanceClaim", "publicReady"]:
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

    result_path = out_dir / f"eml_advantage_pcc3_real_source_holdout_{STAMP}.json"
    packet_path = packet_dir / f"{payload['holdoutPacket']['caseId']}_pcc3_real_source_holdout_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_pcc3_real_source_holdout_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_pcc3_real_source_holdout.json"
    feed_path = command_feed_dir / f"eml_advantage_pcc3_real_source_holdout_feed_{STAMP}.json"

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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc3_real_source_holdout")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_pcc3_real_source_holdout_packets")
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
    print("EML_ADV_PCC3_REAL_SOURCE_HOLDOUT_OK")
    print(f"profiles={built['payload']['summary']['profileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
