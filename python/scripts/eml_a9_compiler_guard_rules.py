#!/usr/bin/env python3
"""EML-A9 compiler guard rules.

Turns A8 evidence into conservative compiler/runtime policy. This is a rule
registry for future fixtures, not a compiler implementation or correctness
proof.
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
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a9_compiler_guard_rules.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_compiler_guard_rule_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A9_COMPILER_GUARD_RULES_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "compiler_behavior_changed": False,
    "compiler_correctness_claim": False,
    "guard_rules_complete": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "runtime_performance_claim": False,
    "public_ready": False,
    "public_atlas_promotion": False,
    "theorem_discovery_claim": False,
    "deploy_performed": False,
}

NON_CLAIMS = [
    "A9 records compiler guard rules only; it does not modify compiler behavior.",
    "A9 does not prove compiler correctness, EML advantage, broad EML superiority, runtime performance, theorem discovery, public Atlas promotion, or deployment.",
    "A9 guard rules are conservative and incomplete until implemented and tested in compiler fixtures.",
]


def rule_specs() -> list[dict[str, Any]]:
    return [
        {
            "ruleId": "prefer_eml_for_proof_shape_v0",
            "ruleClass": "proof_shape_preference",
            "trigger": "candidate axis is proof_shape or generator_identity and domain guards are explicit",
            "guardAction": "allow EML representation for proof/search/teaching surfaces; do not infer runtime win",
            "evidenceStatus": "ready_for_compiler_fixture",
            "sourceEvidence": [
                "reports/eml_a8_3_candidate_trial_runner_2026_05_27.md",
                "MachLib/EML.lean::eml_log_exp_subtraction_boundary",
            ],
            "rationale": "A8.3 supports proof-shape and identity lanes while keeping claims bounded.",
        },
        {
            "ruleId": "lower_expm1_near_zero_v0",
            "ruleClass": "protected_runtime_lowering",
            "trigger": "expression shape exp(x)-1 or eml(x,e) with near-zero runtime profile",
            "guardAction": "lower runtime code to protected expm1; keep EML only as boundary/proof notation",
            "evidenceStatus": "ready_for_compiler_fixture",
            "sourceEvidence": [
                "reports/eml_a8_3_candidate_trial_runner_2026_05_27.md",
                "reports/eml_a8_5_deep_tree_holdout_2026_05_27.md",
            ],
            "rationale": "A8.3 and A8.5 confirm standard/protected expm1 wins near zero.",
        },
        {
            "ruleId": "lower_logaddexp_softplus_v0",
            "ruleClass": "protected_runtime_lowering",
            "trigger": "expression shape ln(exp(a)+exp(b)) or softplus/log-sum-exp",
            "guardAction": "lower runtime code to protected logaddexp/softplus implementation",
            "evidenceStatus": "ready_for_compiler_fixture",
            "sourceEvidence": [
                "reports/eml_a8_1_holdout_advantage_benchmark_2026_05_27.md",
                "reports/eml_a8_4_negative_control_discipline_2026_05_27.md",
            ],
            "rationale": "A8.1/A8.4 keep logaddexp as a protected runtime negative control.",
        },
        {
            "ruleId": "require_positive_log_domain_guard_v0",
            "ruleClass": "domain_guard",
            "trigger": "any EML lowering introduces log(y), ln(y), or y argument interpreted as logarithmic domain",
            "guardAction": "require positive-domain obligation or log-domain lift before surfacing claim",
            "evidenceStatus": "ready_for_compiler_fixture",
            "sourceEvidence": [
                "reports/eml_a8_3_candidate_trial_runner_2026_05_27.md",
                "reports/eml_a8_5_deep_tree_holdout_2026_05_27.md",
            ],
            "rationale": "Safe log-domain lift is useful only when the positive coordinate obligation is explicit.",
        },
        {
            "ruleId": "block_unstable_deep_tree_v0",
            "ruleClass": "deep_tree_block",
            "trigger": "EML tree depth exceeds holdout-backed depth or finite/error metrics are missing",
            "guardAction": "block public advantage claims and require deep-tree holdout packet before runtime lowering",
            "evidenceStatus": "ready_for_compiler_fixture",
            "sourceEvidence": [
                "reports/eml_a8_5_deep_tree_holdout_2026_05_27.md",
                "reports/eml_a8_4_negative_control_discipline_2026_05_27.md",
            ],
            "rationale": "A8.5 blocked three deep-tree cases and found no EML-structure win under depth stress.",
        },
        {
            "ruleId": "require_trial_packet_before_advantage_claim_v0",
            "ruleClass": "claim_gate",
            "trigger": "any artifact attempts an EML advantage, runtime, compiler, or public Atlas claim",
            "guardAction": "require candidate packet, holdout/trial packet, negative-control check, and reviewer decision",
            "evidenceStatus": "documentation_rule_only",
            "sourceEvidence": [
                "reports/eml_a8_2_discovery_candidate_queue_2026_05_27.md",
                "reports/eml_a8_3_candidate_trial_runner_2026_05_27.md",
                "reports/eml_a8_4_negative_control_discipline_2026_05_27.md",
            ],
            "rationale": "A8 established the queue -> trial -> control flow for claim discipline.",
        },
    ]


def packet_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_compiler_guard_rule_packet_v0",
        "date": DATE,
        **spec,
        "compilerBehaviorChanged": False,
        "implementedInCompiler": False,
        "publicClaimAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for packet in packets:
        by_class[packet["ruleClass"]] = by_class.get(packet["ruleClass"], 0) + 1
        by_status[packet["evidenceStatus"]] = by_status.get(packet["evidenceStatus"], 0) + 1
    return {
        "ruleCount": len(packets),
        "byRuleClass": by_class,
        "byEvidenceStatus": by_status,
        "readyForCompilerFixtureCount": by_status.get("ready_for_compiler_fixture", 0),
        "compilerBehaviorChanged": False,
        "compilerCorrectnessClaim": False,
        "guardRulesComplete": False,
        "emlAdvantageProved": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_rules(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    packets = [packet_from_spec(spec) for spec in rule_specs()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "ruleSetId": "eml_a9_compiler_guard_rules",
        "rulePackets": packets,
        "summary": summarize(packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a9_compiler_guard_rules_{stamp}.json"
    report_path = report_dir / f"eml_a9_compiler_guard_rules_{stamp}.md"
    evidence_path = evidence_dir / "eml_a9_compiler_guard_rules.json"
    feed_path = command_feed_dir / f"eml_a9_compiler_guard_rules_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{packet['ruleId']}_guard_rule_{stamp}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a9-compiler-guard-rules",
        "title": "EML-A9 Compiler Guard Rules",
        "reviewDecision": "compiler_guard_rules_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "guard_rule_registry_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Guard rule registry only; no compiler behavior change, compiler correctness proof, runtime performance, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Converts A8 evidence into conservative compiler/runtime policy.",
            "Separates proof/search notation from runtime lowering.",
            "Blocks unstable deep trees until holdout evidence exists.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a9_compiler_guard_rules.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a9_compiler_guard_rules.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a9.v0",
        "date": DATE,
        "title": "EML-A9 Compiler Guard Rules",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A9.1 implement guard-rule fixtures without changing compiler behavior",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A9 Compiler Guard Rules",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| Rule | Class | Evidence status |",
        "|---|---|---|",
    ]
    for packet in payload["rulePackets"]:
        lines.append(f"| `{packet['ruleId']}` | `{packet['ruleClass']}` | `{packet['evidenceStatus']}` |")
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Rules: `{summary['ruleCount']}`",
            f"- Ready for compiler fixtures: `{summary['readyForCompilerFixtureCount']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            f"- Compiler correctness claim: `{summary['compilerCorrectnessClaim']}`",
            f"- Guard rules complete: `{summary['guardRulesComplete']}`",
            "",
            "## Boundary",
            "",
            "- Guard-rule registry only.",
            "- No compiler behavior change, compiler correctness proof, runtime performance, EML advantage proof, broad EML superiority, public Atlas promotion, or deployment claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A9 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid A9 status")
    summary = payload["summary"]
    if summary["ruleCount"] < 6:
        raise ValueError("expected at least six guard rules")
    if summary["readyForCompilerFixtureCount"] < 4:
        raise ValueError("expected fixture-ready rules")
    for key in ["compilerBehaviorChanged", "compilerCorrectnessClaim", "guardRulesComplete", "emlAdvantageProved"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["rulePackets"]:
        if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid rule packet schema: {packet.get('ruleId')}")
        if packet["compilerBehaviorChanged"] is not False or packet["implementedInCompiler"] is not False:
            raise ValueError(f"rule must not be implemented yet: {packet['ruleId']}")
        for key, value in packet["claimFlags"].items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['ruleId']}: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a9_compiler_guard_rules")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_compiler_guard_rule_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_rules(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A9_COMPILER_GUARD_RULES_OK")
    print(f"rules={built['payload']['summary']['ruleCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
