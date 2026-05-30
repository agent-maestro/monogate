#!/usr/bin/env python3
"""FEF-P11 per-target validation policy for the broad Forge surface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
FORGE_ROOT = MONOGATE_ROOT / "forge"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))
if str(FORGE_ROOT) not in sys.path:
    sys.path.insert(0, str(FORGE_ROOT))

from tools.cli.main import ORDERED_TARGETS  # noqa: E402
from tools.license.verifier import FREE_TARGETS, PRO_TARGETS  # noqa: E402
from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p11_per_target_validation_policy.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P11_PER_TARGET_VALIDATION_POLICY_PASS"

FEF_P10_PATH = ROOT / "reports/evidence_packets/fef_p10_broader_generated_target_reingest.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "proof_claim": False,
    "package_published": False,
    "public_compiler_package_available": False,
    "public_checkout_enabled": False,
    "target_all_ready_claim": False,
    "verilog_claim": False,
    "lean_proof_claim": False,
    "zkproof_claim": False,
    "silicon_claim": False,
}

NON_CLAIMS = [
    "FEF-P11 records a per-target validation policy for the broad Forge target surface.",
    "FEF-P11 does not execute or validate all targets.",
    "FEF-P11 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P11 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P11 does not claim runtime performance, Verilog readiness, Lean proofs, zkproof readiness, silicon, or hardware output.",
]

SAMPLE_GRID_TARGETS = {"python", "javascript"}
LOCAL_RUNTIME_CANDIDATES = {"c", "cpp", "rust", "go", "java", "kotlin", "csharp", "swift", "matlab", "luau", "gdscript", "solidity"}
IR_OR_BYTECODE_TARGETS = {"llvm", "wasm"}
SHADER_TARGETS = {"hlsl", "glsl", "glsles", "wgsl", "metal"}
HARDWARE_TARGETS = {"verilog", "systemverilog", "vhdl", "chisel"}
FORMAL_TARGETS = {"lean", "coq", "isabelle"}
ZK_TARGETS = {"zkproof"}
SAFETY_TARGETS = {"ada", "autosar", "aadl", "ros2"}
MANUFACTURING_TARGETS = {"spice", "kicad", "jlcpcb"}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def target_tier(target: str) -> str:
    if target in FREE_TARGETS:
        return "free"
    if target in PRO_TARGETS:
        return "pro"
    return "unknown"


def policy_for(target: str) -> dict[str, Any]:
    if target in SAMPLE_GRID_TARGETS:
        level = "runtime_reingest_sample_grid"
        status = "selected_fixture_pass"
        next_validator = "broaden fixture family and keep runtime/re-ingest sample-grid checks"
        allowed_copy = "Selected fixture runtime/re-ingest evidence exists; no broad target readiness claim."
    elif target in LOCAL_RUNTIME_CANDIDATES:
        level = "local_toolchain_runtime_candidate"
        status = "policy_defined_evidence_open"
        next_validator = "compile selected generated target with local toolchain and compare deterministic samples"
        allowed_copy = "Target emission may be described as policy-mapped only until target-specific runtime evidence exists."
    elif target in IR_OR_BYTECODE_TARGETS:
        level = "ir_or_bytecode_syntax_candidate"
        status = "policy_defined_evidence_open"
        next_validator = "emit artifact and run available parser/assembler/object-level smoke where installed"
        allowed_copy = "IR/bytecode emission may be described as candidate artifact only."
    elif target in SHADER_TARGETS:
        level = "shader_syntax_lint_candidate"
        status = "policy_defined_evidence_open"
        next_validator = "emit shader and run target shader compiler/linter when available"
        allowed_copy = "Shader target may be described as candidate source emission only."
    elif target in HARDWARE_TARGETS:
        level = "hardware_syntax_lint_candidate"
        status = "policy_defined_evidence_open"
        next_validator = "emit RTL/source and run syntax lint/simulation where local tools are available"
        allowed_copy = "Hardware target may be described as candidate artifact only; no silicon or hardware-observed claim."
    elif target in FORMAL_TARGETS:
        level = "formal_artifact_structural_only"
        status = "policy_defined_evidence_open"
        next_validator = "check generated theorem/stub structure and separately record any discharged proof"
        allowed_copy = "Formal target may be described as obligation/stub artifact only unless proofs are discharged."
    elif target in ZK_TARGETS:
        level = "zk_ir_structural_only"
        status = "policy_defined_evidence_open"
        next_validator = "check circuit JSON/schema and separately record proof-system execution if added"
        allowed_copy = "ZK target may be described as circuit/IR artifact only, not a working proof system."
    elif target in SAFETY_TARGETS:
        level = "safety_bundle_structural_only"
        status = "policy_defined_evidence_open"
        next_validator = "emit bundle and run schema/build-system smoke where local tooling exists"
        allowed_copy = "Safety/robotics target may be described as candidate bundle only."
    elif target in MANUFACTURING_TARGETS:
        level = "manufacturing_artifact_structural_only"
        status = "policy_defined_evidence_open"
        next_validator = "emit netlist/schematic/BOM bundle and run schema/manufacturing consistency checks"
        allowed_copy = "Manufacturing target may be described as candidate artifact only; no fabrication claim."
    else:
        level = "held_out_unclassified"
        status = "blocked"
        next_validator = "classify target before any validation or public copy"
        allowed_copy = "No public copy beyond held-out target."

    return {
        "target": target,
        "tier": target_tier(target),
        "validationLevel": level,
        "currentEvidenceStatus": status,
        "allowedPublicCopy": allowed_copy,
        "blockedClaims": [
            "compiler_correctness",
            "formal_equivalence",
            "runtime_performance",
            "production_readiness",
            "public_readiness",
            "target_all_readiness",
        ],
        "nextValidator": next_validator,
    }


def summarize(policies: list[dict[str, Any]]) -> dict[str, Any]:
    level_counts: dict[str, int] = {}
    tier_counts: dict[str, int] = {}
    for policy in policies:
        level_counts[policy["validationLevel"]] = level_counts.get(policy["validationLevel"], 0) + 1
        tier_counts[policy["tier"]] = tier_counts.get(policy["tier"], 0) + 1
    return {
        "targetCount": len(policies),
        "freeTargetCount": tier_counts.get("free", 0),
        "proTargetCount": tier_counts.get("pro", 0),
        "unknownTierCount": tier_counts.get("unknown", 0),
        "validationLevelCounts": dict(sorted(level_counts.items())),
        "sampleGridValidatedTargets": sorted(SAMPLE_GRID_TARGETS),
        "policyOnlyTargetCount": sum(1 for p in policies if p["currentEvidenceStatus"] == "policy_defined_evidence_open"),
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "targetAllReadyClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    fef_p10 = read_json(FEF_P10_PATH)
    policies = [policy_for(target) for target in ORDERED_TARGETS]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p11-per-target-validation-policy",
        "decision": "per_target_validation_policy_recorded",
        "targetOrder": list(ORDERED_TARGETS),
        "targetPolicies": policies,
        "summary": summarize(policies),
        "fefP10Link": {
            "path": str(FEF_P10_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p10["reviewDecision"],
        },
        "releaseGates": [
            {"id": "all_cli_targets_classified", "status": "pass"},
            {"id": "python_javascript_sample_grid_evidence_attached", "status": "pass"},
            {"id": "non_python_javascript_targets_policy_only", "status": "required"},
            {"id": "public_package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "nextMilestones": [
            "Run FEF-P12 local toolchain runtime checks for selected C/Rust generated targets.",
            "Add shader/RTL syntax-lint packets only when local tools are available.",
            "Keep publication blocked unless an explicit release action is requested.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P11 Per-Target Validation Policy",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "policy_classification_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Per-target validation policy only; no all-target execution, public package publication, compiler correctness, formal equivalence, runtime performance, production readiness, checkout, Verilog readiness, Lean proof, zkproof readiness, silicon, or hardware claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "All 36 CLI targets are classified into explicit validation levels.",
            "Only Python and JavaScript carry selected runtime/re-ingest sample-grid evidence from FEF-P10.",
            "Every non-Python/JavaScript target remains policy-defined evidence-open until its own validator runs.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p11_per_target_validation_policy.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p11_per_target_validation_policy.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p11_per_target_validation_policy.v0",
        "date": DATE,
        "title": "FEF-P11 Per-Target Validation Policy",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run selected local toolchain runtime checks for C/Rust generated targets.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Target | Tier | Validation level | Evidence status |",
        "|---|---|---|---|",
    ]
    for policy in payload["targetPolicies"]:
        rows.append(
            f"| `{policy['target']}` | `{policy['tier']}` | `{policy['validationLevel']}` | `{policy['currentEvidenceStatus']}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P11 Per-Target Validation Policy",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P11 classifies each Forge CLI target into an allowed validation",
            "level. It is a policy packet, not all-target execution evidence.",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Targets classified: `{summary['targetCount']}`",
            f"- Free targets: `{summary['freeTargetCount']}`",
            f"- Pro targets: `{summary['proTargetCount']}`",
            f"- Sample-grid validated targets: `{','.join(summary['sampleGridValidatedTargets'])}`",
            f"- Policy-only targets: `{summary['policyOnlyTargetCount']}`",
            "",
            "## Boundary",
            "",
            "- Per-target validation policy only.",
            "- No all-target execution or broad readiness claim.",
            "- No package publication or checkout claim.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No runtime performance, production, Verilog readiness, Lean proof, zkproof readiness, silicon, or hardware claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P11 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P11 status")
    if payload["targetOrder"] != list(ORDERED_TARGETS):
        raise ValueError("target order must mirror Forge CLI ORDERED_TARGETS")
    summary = payload["summary"]
    if summary["targetCount"] != 36:
        raise ValueError("FEF-P11 must classify all 36 CLI targets")
    if summary["freeTargetCount"] != 13:
        raise ValueError("expected 13 free targets")
    if summary["proTargetCount"] != 23:
        raise ValueError("expected 23 pro targets")
    if summary["unknownTierCount"] != 0:
        raise ValueError("all targets must have known tier")
    if summary["sampleGridValidatedTargets"] != ["javascript", "python"]:
        raise ValueError("only Python/JavaScript may carry sample-grid validation in FEF-P11")
    if summary["policyOnlyTargetCount"] != 34:
        raise ValueError("non-Python/JavaScript targets must remain policy-only in FEF-P11")
    for key in [
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
        "targetAllReadyClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for policy in payload["targetPolicies"]:
        if policy["target"] not in ORDERED_TARGETS:
            raise ValueError("unknown target in policy")
        if policy["target"] in SAMPLE_GRID_TARGETS:
            if policy["currentEvidenceStatus"] != "selected_fixture_pass":
                raise ValueError("Python/JavaScript must attach selected fixture pass")
        elif policy["currentEvidenceStatus"] != "policy_defined_evidence_open":
            raise ValueError("non-Python/JavaScript targets must remain policy-only")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p11_per_target_validation_policy_{STAMP}.json"
    report_path = report_dir / f"fef_p11_per_target_validation_policy_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p11_per_target_validation_policy.json"
    feed_path = command_feed_dir / f"fef_p11_per_target_validation_policy_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p11_per_target_validation_policy")
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
    print("FEF_P11_PER_TARGET_VALIDATION_POLICY_OK")
    print(f"targets={built['payload']['summary']['targetCount']}")
    print(f"policy_only={built['payload']['summary']['policyOnlyTargetCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
