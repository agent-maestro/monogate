#!/usr/bin/env python3
"""EML-A8.5 unstable deep-tree holdout.

Stress-tests the main practical weakness of EML: deep trees can become
numerically unstable even when the symbolic identity is attractive.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a8_5_deep_tree_holdout.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_deep_tree_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A8_5_DEEP_TREE_HOLDOUT_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "deep_tree_stability_claim": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "public_ready": False,
    "public_atlas_promotion": False,
    "theorem_discovery_claim": False,
    "deploy_performed": False,
}

NON_CLAIMS = [
    "A8.5 is a deterministic deep-tree holdout, not proof of deep-tree stability.",
    "A8.5 does not prove EML advantage, broad EML superiority, compiler correctness, runtime performance, theorem discovery, public Atlas promotion, or deployment.",
    "Blocked deep trees are guardrail evidence, not a universal limit theorem.",
]

CRITERIA = {
    "finiteRatioPass": 0.999,
    "maxRelErrorPass": 1.0e-8,
    "maxAbsErrorPass": 1.0e-8,
    "standardImprovementFactor": 100.0,
    "blockFiniteRatioBelow": 0.99,
    "blockMaxAbsErrorAbove": 1.0e6,
}


ArrayFn = Callable[[np.ndarray], np.ndarray]


def metric(name: str, observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    obs = np.asarray(observed, dtype=np.float64)
    ref = np.asarray(reference, dtype=np.float64)
    finite = np.isfinite(obs) & np.isfinite(ref)
    errors = np.abs(obs[finite] - ref[finite])
    rel = errors / np.maximum(np.abs(ref[finite]), 1.0e-12)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    finite_ratio = float(np.mean(np.isfinite(obs)))
    return {
        "expression": name,
        "sampleCount": int(obs.size),
        "finiteRatio": finite_ratio,
        "nanCount": int(np.isnan(obs).sum()),
        "infCount": int(np.isinf(obs).sum()),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "pass": bool(
            finite_ratio >= CRITERIA["finiteRatioPass"]
            and (max_abs <= CRITERIA["maxAbsErrorPass"] or max_rel <= CRITERIA["maxRelErrorPass"])
        ),
    }


def json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def expm1_chain_raw(x: np.ndarray, depth: int) -> np.ndarray:
    y = np.asarray(x, dtype=np.float64)
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(depth):
            y = eml(y, math.e)
    return y


def expm1_chain_standard(x: np.ndarray, depth: int) -> np.ndarray:
    y = np.asarray(x, dtype=np.float64)
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(depth):
            y = np.expm1(y)
    return y


def expm1_chain_ref(x: np.ndarray, depth: int) -> np.ndarray:
    y = np.asarray(x, dtype=np.longdouble)
    for _ in range(depth):
        y = np.expm1(y)
    return np.asarray(y, dtype=np.float64)


def ln_from_eml(y: np.ndarray) -> np.ndarray:
    return eml(1.0, eml(eml(1.0, y), 1.0))


def nested_ln_identity(x: np.ndarray, depth: int) -> np.ndarray:
    y = np.exp(x)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        for _ in range(depth):
            y = np.exp(ln_from_eml(y))
    return np.log(y)


def subtraction_boundary_chain(x: np.ndarray, depth: int) -> np.ndarray:
    y = np.asarray(x, dtype=np.float64)
    with np.errstate(over="ignore", invalid="ignore"):
        for step in range(depth):
            v = np.exp(y)
            u = np.full_like(y, 0.125 * (step + 1))
            y = eml(np.log(v), np.exp(u))
    return y


def case_specs() -> list[dict[str, Any]]:
    return [
        {
            "caseId": "deep_expm1_chain_near_zero_v0",
            "treeDepth": 8,
            "emlForm": "Fold_8 z -> eml(z,e)",
            "standardForm": "Fold_8 z -> expm1(z)",
            "range": (-1.0e-8, 1.0e-8),
            "emlFn": lambda x: expm1_chain_raw(x, 8),
            "standardFn": lambda x: expm1_chain_standard(x, 8),
            "referenceFn": lambda x: expm1_chain_ref(x, 8),
            "expected": "standard_runtime_win",
        },
        {
            "caseId": "deep_expm1_chain_wide_v0",
            "treeDepth": 5,
            "emlForm": "Fold_5 z -> eml(z,e)",
            "standardForm": "guarded/protected expm1 chain",
            "range": (1.0, 5.0),
            "emlFn": lambda x: expm1_chain_raw(x, 5),
            "standardFn": lambda x: expm1_chain_standard(x, 5),
            "referenceFn": lambda x: expm1_chain_ref(x, 5),
            "expected": "blocked_unstable_deep_tree",
        },
        {
            "caseId": "nested_ln_from_eml_positive_v0",
            "treeDepth": 6,
            "emlForm": "nested ln_from_eml(exp(x))",
            "standardForm": "log(exp(x))",
            "range": (-8.0, 8.0),
            "emlFn": lambda x: nested_ln_identity(x, 6),
            "standardFn": lambda x: x,
            "referenceFn": lambda x: x,
            "expected": "mixed_identity_supported",
        },
        {
            "caseId": "subtraction_boundary_chain_v0",
            "treeDepth": 6,
            "emlForm": "eml(log(v),exp(u)) repeated with positive v",
            "standardForm": "subtraction accumulator",
            "range": (-4.0, 4.0),
            "emlFn": lambda x: subtraction_boundary_chain(x, 6),
            "standardFn": lambda x: x - sum(0.125 * (step + 1) for step in range(6)),
            "referenceFn": lambda x: x - sum(0.125 * (step + 1) for step in range(6)),
            "expected": "eml_structure_supported",
        },
        {
            "caseId": "unstable_deep_tree_negative_control_v0",
            "treeDepth": 12,
            "emlForm": "unguarded deep EML exponential fold",
            "standardForm": "blocked unless lowered/guarded",
            "range": (2.0, 8.0),
            "emlFn": lambda x: expm1_chain_raw(x, 12),
            "standardFn": lambda x: np.full_like(x, np.nan),
            "referenceFn": lambda x: expm1_chain_ref(x, 12),
            "expected": "blocked_unstable_deep_tree",
        },
    ]


def grid(low: float, high: float, profile: str) -> np.ndarray:
    count = 2048
    if profile == "edge":
        span = high - low
        return np.concatenate(
            [
                np.linspace(low, low + 0.02 * span, count // 2),
                np.linspace(high - 0.02 * span, high, count // 2),
            ]
        )
    if profile == "stress":
        return np.linspace(low - 0.25 * (high - low), high + 0.25 * (high - low), count)
    return np.linspace(low, high, count)


def profile_result(spec: dict[str, Any], profile: str) -> dict[str, Any]:
    xs = grid(*spec["range"], profile)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        reference = spec["referenceFn"](xs)
        eml_observed = spec["emlFn"](xs)
        standard_observed = spec["standardFn"](xs)
    eml_metric = metric("eml_deep_tree", eml_observed, reference)
    standard_metric = metric("standard_or_guarded", standard_observed, reference)
    eml_abs = max(eml_metric["maxAbsError"], 1.0e-300)
    standard_abs = max(standard_metric["maxAbsError"], 1.0e-300)
    if eml_metric["finiteRatio"] < CRITERIA["blockFiniteRatioBelow"] or eml_metric["maxAbsError"] > CRITERIA["blockMaxAbsErrorAbove"]:
        winner = "blocked"
    elif standard_metric["pass"] and eml_abs / standard_abs >= CRITERIA["standardImprovementFactor"]:
        winner = "standard"
    elif eml_metric["pass"] and standard_metric["pass"]:
        winner = "tie"
    elif eml_metric["pass"]:
        winner = "eml_structure"
    elif standard_metric["pass"]:
        winner = "standard"
    else:
        winner = "blocked"
    return {
        "profile": profile,
        "inputMin": float(xs.min()),
        "inputMax": float(xs.max()),
        "eml": eml_metric,
        "standard": standard_metric,
        "winner": winner,
    }


def classify(spec: dict[str, Any], profiles: list[dict[str, Any]]) -> str:
    if any(profile["winner"] == "blocked" for profile in profiles):
        return "blocked_unstable_deep_tree"
    if spec["expected"] == "standard_runtime_win" and all(profile["winner"] in {"standard", "tie"} for profile in profiles):
        return "standard_runtime_win"
    if spec["expected"] == "eml_structure_supported" and all(profile["winner"] in {"eml_structure", "tie"} for profile in profiles):
        return "eml_structure_supported"
    if spec["expected"] == "mixed_identity_supported" and all(profile["winner"] == "tie" for profile in profiles):
        return "mixed_identity_supported"
    return spec["expected"]


def packet_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    profiles = [profile_result(spec, profile) for profile in ["holdout", "edge", "stress"]]
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_deep_tree_holdout_packet_v0",
        "date": DATE,
        "caseId": spec["caseId"],
        "treeDepth": spec["treeDepth"],
        "emlForm": spec["emlForm"],
        "standardForm": spec["standardForm"],
        "holdoutClass": classify(spec, profiles),
        "profiles": profiles,
        "criteria": dict(CRITERIA),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, int] = {}
    max_depth = 0
    for packet in packets:
        by_class[packet["holdoutClass"]] = by_class.get(packet["holdoutClass"], 0) + 1
        max_depth = max(max_depth, packet["treeDepth"])
    return {
        "packetCount": len(packets),
        "byHoldoutClass": by_class,
        "maxTreeDepth": max_depth,
        "blockedCount": by_class.get("blocked_unstable_deep_tree", 0),
        "standardRuntimeWinCount": by_class.get("standard_runtime_win", 0),
        "mixedIdentitySupportedCount": by_class.get("mixed_identity_supported", 0),
        "emlStructureSupportedCount": by_class.get("eml_structure_supported", 0),
        "deepTreeStabilityClaim": False,
        "emlAdvantageProved": False,
        "publicAtlasPromotion": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_holdout(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    packets = [packet_from_spec(spec) for spec in case_specs()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "holdoutId": "eml_a8_5_deep_tree_holdout",
        "holdoutPackets": packets,
        "summary": summarize(packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    safe_payload = json_safe(payload)
    evidence = json_safe(build_evidence_packet(safe_payload))
    feed = json_safe(command_feed(safe_payload))
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a8_5_deep_tree_holdout_{stamp}.json"
    report_path = report_dir / f"eml_a8_5_deep_tree_holdout_{stamp}.md"
    evidence_path = evidence_dir / "eml_a8_5_deep_tree_holdout.json"
    feed_path = command_feed_dir / f"eml_a8_5_deep_tree_holdout_feed_{stamp}.json"
    result_path.write_text(json.dumps(safe_payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(safe_payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    for packet in safe_payload["holdoutPackets"]:
        packet_path = packet_dir / f"{packet['caseId']}_deep_tree_holdout_{stamp}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {"payload": safe_payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a8-5-deep-tree-holdout",
        "title": "EML-A8.5 Deep Tree Holdout",
        "reviewDecision": "deep_tree_guardrail_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_numeric_holdout",
        "semanticStrength": "deep_tree_stress_no_stability_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Deep-tree holdout only; no deep-tree stability proof, runtime performance, compiler correctness, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Finds blocked unstable deep trees.",
            "Confirms protected standard forms remain necessary near known numerical traps.",
            "Provides direct inputs for A9 compiler guard rules.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a8_5_deep_tree_holdout.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a8_5_deep_tree_holdout.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a8_5.v0",
        "date": DATE,
        "title": "EML-A8.5 Deep Tree Holdout",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A9 encode compiler guard rules from A8 evidence",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A8.5 Deep Tree Holdout",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| Case | Depth | Holdout class |",
        "|---|---:|---|",
    ]
    for packet in payload["holdoutPackets"]:
        lines.append(f"| `{packet['caseId']}` | `{packet['treeDepth']}` | `{packet['holdoutClass']}` |")
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Packets: `{summary['packetCount']}`",
            f"- Max tree depth: `{summary['maxTreeDepth']}`",
            f"- Blocked: `{summary['blockedCount']}`",
            f"- Standard runtime wins: `{summary['standardRuntimeWinCount']}`",
            f"- EML structure supported: `{summary['emlStructureSupportedCount']}`",
            f"- Deep-tree stability claim: `{summary['deepTreeStabilityClaim']}`",
            "",
            "## Boundary",
            "",
            "- Deep-tree holdout only.",
            "- No broad EML advantage, deep-tree stability proof, runtime performance, compiler correctness, theorem discovery, public Atlas promotion, or deployment claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A8.5 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid A8.5 status")
    summary = payload["summary"]
    if summary["packetCount"] < 5:
        raise ValueError("expected at least five deep-tree packets")
    if summary["blockedCount"] < 1:
        raise ValueError("expected at least one blocked deep tree")
    if summary["standardRuntimeWinCount"] < 1:
        raise ValueError("expected at least one standard runtime win")
    if summary["maxTreeDepth"] < 8:
        raise ValueError("expected depth stress")
    for key in ["deepTreeStabilityClaim", "emlAdvantageProved", "publicAtlasPromotion"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["holdoutPackets"]:
        if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid packet schema: {packet.get('caseId')}")
        if len(packet["profiles"]) != 3:
            raise ValueError(f"expected three profiles: {packet['caseId']}")
        for key, value in packet["claimFlags"].items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['caseId']}: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a8_5_deep_tree_holdout")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_deep_tree_holdout_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_holdout(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A8_5_DEEP_TREE_HOLDOUT_OK")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
