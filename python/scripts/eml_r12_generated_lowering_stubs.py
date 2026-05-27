#!/usr/bin/env python3
"""EML-R12 generated lowering stubs.

Consumes R11 lowering plans, emits generated Python stub packets, and validates
them on deterministic fixture grids. This does not claim compiler correctness,
formal semantic equivalence, production lowering, deployment, or performance.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import case_specs, deterministic_inputs, stable_sigmoid  # noqa: E402

SCHEMA_VERSION = "monogate.eml_r12_generated_lowering_stubs.v0"
STUB_SCHEMA_VERSION = "monogate.eml_generated_stub_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_R12_GENERATED_LOWERING_STUBS_PASS"

CLAIM_FLAGS = {
    **dict(DEFAULT_CLAIM_FLAGS),
    "compiler_correctness_claim": False,
    "semantic_equivalence_claim": False,
    "production_lowering_claim": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "R12 emits fixture stubs, not compiler output.",
    "R12 validates generated Python stubs on deterministic grids only.",
    "R12 does not claim compiler correctness, formal equivalence, production lowering, deployment, or performance.",
]

LOWERING_EXPRESSIONS = {
    "exp_from_eml_v0": "np.exp(x)",
    "subtraction_boundary_v0": "v - u",
    "bose_boundary_expm1_v0": "np.expm1(x)",
    "ln_from_eml_v0": "np.log(y)",
    "softplus_pair_v0": "np.logaddexp(a, b)",
    "sigmoid_derivative_v0": "stable_sigmoid(x) * (1.0 - stable_sigmoid(x))",
    "gaussian_energy_v0": "2.0 * np.exp(-(x * x))",
}

ARGUMENTS = {
    "exp_from_eml_v0": ["x"],
    "subtraction_boundary_v0": ["u", "v"],
    "bose_boundary_expm1_v0": ["x"],
    "ln_from_eml_v0": ["y"],
    "softplus_pair_v0": ["a", "b"],
    "sigmoid_derivative_v0": ["x"],
    "gaussian_energy_v0": ["x"],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def function_name(case_id: str) -> str:
    return f"lower_{case_id}".replace("-", "_")


def stub_source(case_id: str, lowered_expression: str) -> str:
    args = ", ".join(ARGUMENTS[case_id])
    return "\n".join(
        [
            f"def {function_name(case_id)}({args}):",
            f"    return {lowered_expression}",
            "",
        ]
    )


def compile_stub(case_id: str, source: str) -> Callable[..., np.ndarray]:
    namespace: dict[str, Any] = {"np": np, "math": math, "stable_sigmoid": stable_sigmoid}
    exec(source, namespace)
    return namespace[function_name(case_id)]


def plan_by_case(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {plan["caseId"]: plan for plan in payload["plans"]}


def case_spec_by_id() -> dict[str, Any]:
    return {spec.case_id: spec for spec in case_specs()}


def validate_stub(case_id: str, fn: Callable[..., np.ndarray]) -> dict[str, Any]:
    spec = case_spec_by_id()[case_id]
    values = deterministic_inputs(spec)
    args = [values[name] for name in ARGUMENTS[case_id]]
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        observed = np.asarray(fn(*args), dtype=np.float64)
        reference = np.asarray(spec.reference_fn(values), dtype=np.float64)
    finite = np.isfinite(observed)
    comparable = finite & np.isfinite(reference)
    errors = np.abs(observed[comparable] - reference[comparable])
    denominators = np.maximum(np.abs(reference[comparable]), 1.0e-12)
    rel_errors = errors / denominators
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel_errors)) if rel_errors.size else float("inf")
    status = "pass" if bool(np.all(finite)) and max_abs <= 1.0e-9 and max_rel <= 1.0e-9 else "fail"
    return {
        "status": status,
        "sampleCount": int(observed.size),
        "finiteRatio": float(np.mean(finite)),
        "nanOrInfCount": int(observed.size - np.count_nonzero(finite)),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "tolerances": {
            "maxAbsError": 1.0e-9,
            "maxRelError": 1.0e-9,
        },
    }


def rust_fixture(case_id: str, lowered: str) -> str:
    args = ", ".join(f"{name}: f64" for name in ARGUMENTS[case_id])
    expr = (
        lowered.replace("np.exp", "f64::exp")
        .replace("np.expm1", "f64::exp_m1")
        .replace("np.log", "f64::ln")
        .replace("np.logaddexp(a, b)", "a.max(b) + (a.min(b) - a.max(b)).exp().ln_1p()")
        .replace("stable_sigmoid(x)", "stable_sigmoid(x)")
    )
    return f"fn {function_name(case_id)}({args}) -> f64 {{ {expr} }}"


def c_fixture(case_id: str, lowered: str) -> str:
    args = ", ".join(f"double {name}" for name in ARGUMENTS[case_id])
    expr = (
        lowered.replace("np.exp", "exp")
        .replace("np.expm1", "expm1")
        .replace("np.log", "log")
        .replace("np.logaddexp(a, b)", "fmax(a,b) + log1p(exp(fmin(a,b) - fmax(a,b)))")
        .replace("stable_sigmoid(x)", "stable_sigmoid(x)")
    )
    return f"double {function_name(case_id)}({args}) {{ return {expr}; }}"


def packet_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    case_id = plan["caseId"]
    lowered = LOWERING_EXPRESSIONS[case_id]
    source = stub_source(case_id, lowered)
    fn = compile_stub(case_id, source)
    validation = validate_stub(case_id, fn)
    return {
        "schemaVersion": STUB_SCHEMA_VERSION,
        "packetType": "eml_generated_stub_packet_v0",
        "date": DATE,
        "caseId": case_id,
        "sourceExpression": plan["sourceExpression"],
        "r11SelectedImplementation": plan["selectedImplementation"],
        "loweringDecision": plan["loweringDecision"],
        "loweredExpression": lowered,
        "pythonFunctionName": function_name(case_id),
        "pythonSource": source,
        "rustFixture": rust_fixture(case_id, lowered),
        "cFixture": c_fixture(case_id, lowered),
        "requiredGuards": plan["requiredGuards"],
        "precisionCaveats": plan["precisionCaveats"],
        "validation": validation,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-r12-generated-lowering-stubs",
        "title": "EML-R12 Generated Lowering Stubs",
        "reviewDecision": "generated_stub_fixtures_validated",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "generated_python_fixture_validation_no_compiler_correctness_claim",
        "semanticReview": {
            "stubPacketCount": payload["summary"]["stubPacketCount"],
            "validationPassCount": payload["summary"]["validationPassCount"],
            "validationFailCount": payload["summary"]["validationFailCount"],
            "compilerBehaviorChanged": False,
            "productionLoweringClaim": False,
        },
        "claimBoundary": "Generated fixture stubs validated on deterministic grids only; no compiler correctness, formal equivalence, production lowering, or performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Consumes R11 lowering plans.",
            "Generates Python stub packets plus Rust/C text fixtures.",
            "Validates generated Python stubs against R10 reference functions on deterministic grids.",
        ],
        "validationCommands": [
            "python python/scripts/eml_r12_generated_lowering_stubs.py --build --strict",
            "python -m pytest -q python/tests/test_eml_r12_generated_lowering_stubs.py",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-R12 Generated Lowering Stubs",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "R12 turns R11 candidate lowering plans into generated fixture stubs and",
        "validates the generated Python stubs on deterministic grids.",
        "",
        "## Stub Packets",
        "",
        "| Case | Decision | Lowered expression | Validation | Max abs error | Max rel error |",
        "|---|---|---|---|---:|---:|",
    ]
    for packet in payload["stubPackets"]:
        validation = packet["validation"]
        lines.append(
            f"| `{packet['caseId']}` | `{packet['loweringDecision']}` | `{packet['loweredExpression']}` | "
            f"`{validation['status']}` | {validation['maxAbsError']:.3e} | {validation['maxRelError']:.3e} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Stub packets: `{payload['summary']['stubPacketCount']}`",
            f"- Validation pass: `{payload['summary']['validationPassCount']}`",
            f"- Validation fail: `{payload['summary']['validationFailCount']}`",
            f"- Compiler behavior changed: `{payload['summary']['compilerBehaviorChanged']}`",
            f"- Production lowering claim: `{payload['summary']['productionLoweringClaim']}`",
            "",
            "## Boundary",
            "",
            "- Generated fixture stubs only.",
            "- No compiler correctness claim.",
            "- No formal semantic equivalence claim.",
            "- No deployment or production lowering claim.",
            "",
        ]
    )
    return "\n".join(lines)


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_r12.v0",
        "date": DATE,
        "title": "EML-R12 Generated Lowering Stubs",
        "status": payload["status"],
        "stubPacketCount": payload["summary"]["stubPacketCount"],
        "validationPassCount": payload["summary"]["validationPassCount"],
        "validationFailCount": payload["summary"]["validationFailCount"],
        "topFollowup": "R10B runtime bakeoff or formal scoped semantic proof",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid R12 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid R12 status")
    if payload["summary"]["stubPacketCount"] < 7:
        raise ValueError("expected at least 7 stub packets")
    if payload["summary"]["validationFailCount"] != 0:
        raise ValueError("all generated stubs must validate in R12")
    for key in [
        "compilerBehaviorChanged",
        "forgeBehaviorChanged",
        "productionLoweringClaim",
        "semanticEquivalenceClaim",
        "deployPerformed",
        "packagePublished",
    ]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    for packet in payload["stubPackets"]:
        if packet["schemaVersion"] != STUB_SCHEMA_VERSION:
            raise ValueError(f"invalid stub schema: {packet.get('caseId')}")
        if packet["validation"]["status"] != "pass":
            raise ValueError(f"stub validation failed: {packet['caseId']}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['caseId']}: {key}")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_stubs(
    r11_path: Path,
    out_dir: Path,
    stub_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    r11 = load_json(r11_path)
    packets = [packet_from_plan(plan) for plan in r11["plans"]]
    pass_count = sum(1 for packet in packets if packet["validation"]["status"] == "pass")
    fail_count = len(packets) - pass_count
    summary = {
        "stubPacketCount": len(packets),
        "validationPassCount": pass_count,
        "validationFailCount": fail_count,
        "sourceR11Path": str(r11_path),
        "compilerBehaviorChanged": False,
        "forgeBehaviorChanged": False,
        "productionLoweringClaim": False,
        "semanticEquivalenceClaim": False,
        "deployPerformed": False,
        "packagePublished": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceR11Path": str(r11_path),
        "stubPackets": packets,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    stub_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_r12_generated_lowering_stubs_{stamp}.json"
    report_path = report_dir / f"eml_r12_generated_lowering_stubs_{stamp}.md"
    evidence_path = evidence_dir / "eml_r12_generated_lowering_stubs.json"
    feed_path = command_feed_dir / f"eml_r12_generated_lowering_stubs_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        path = stub_dir / f"{packet['caseId']}_generated_stub_{stamp}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    parser.add_argument(
        "--r11-path",
        type=Path,
        default=ROOT / f"python/results/eml_r11_hybrid_lowering_planner/eml_r11_hybrid_lowering_planner_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_r12_generated_lowering_stubs")
    parser.add_argument("--stub-dir", type=Path, default=ROOT / "python/results/eml_generated_stub_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_stubs(args.r11_path, args.out_dir, args.stub_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_R12_GENERATED_LOWERING_STUBS_OK")
    print(f"stub_packets={built['payload']['summary']['stubPacketCount']}")
    print(f"validation_pass={built['payload']['summary']['validationPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
