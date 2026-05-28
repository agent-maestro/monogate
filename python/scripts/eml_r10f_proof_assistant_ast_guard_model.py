#!/usr/bin/env python3
"""EML-R10F proof-assistant AST and guard model.

Freezes a small proof-assistant-facing AST, guard vocabulary, and lowering
relation model after R10E. This is a model stub for future proof work, not a
completed formalization or compiler correctness proof.
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

from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_r10f_proof_assistant_ast_guard_model.v0"
MODEL_SCHEMA_VERSION = "monogate.eml_proof_assistant_ast_guard_model.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_R10F_PROOF_ASSISTANT_AST_GUARD_MODEL_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "proof_assistant_formalization_complete": False,
    "compiler_correctness_claim": False,
    "formal_compiler_proof_claim": False,
    "full_eml_semantics_claim": False,
    "semantic_equivalence_claim": False,
    "production_lowering_claim": False,
    "forge_behavior_changed": False,
    "compiler_behavior_changed": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "R10F is a proof-assistant-facing AST and guard model stub.",
    "R10F does not complete a Lean/Coq proof-assistant formalization.",
    "R10F does not claim compiler correctness, formal compiler proof, full EML semantics, or semantic equivalence.",
    "R10F does not change Forge/compiler behavior, deploy, or publish packages.",
]

AST_NODES = [
    {"node": "Var", "arity": 0, "description": "Named input variable."},
    {"node": "Const", "arity": 0, "description": "Literal numeric constant."},
    {"node": "Exp", "arity": 1, "description": "Protected or mathematical exponential node."},
    {"node": "Log", "arity": 1, "description": "Natural logarithm; requires positive argument guard."},
    {"node": "Add", "arity": 2, "description": "Binary addition."},
    {"node": "Sub", "arity": 2, "description": "Binary subtraction."},
    {"node": "Mul", "arity": 2, "description": "Binary multiplication."},
    {"node": "Eml", "arity": 2, "description": "Primitive eml(x,y) = exp(x) - log(y)."},
    {"node": "ProtectedExpm1", "arity": 1, "description": "Protected runtime lowering for exp(x)-1."},
    {"node": "ProtectedLogSumExp", "arity": "n>=1", "description": "Protected max-shifted log-sum-exp lowering."},
]

GUARDS = [
    {"guardId": "finite-inputs", "predicate": "all variables evaluate to finite real values", "formalStatus": "stub"},
    {"guardId": "positive-log-argument", "predicate": "argument(Log) > 0", "formalStatus": "stub"},
    {"guardId": "nonempty-vector", "predicate": "ProtectedLogSumExp input list has length >= 1", "formalStatus": "stub"},
    {"guardId": "near-zero-cancellation-risk", "predicate": "source shape exp(x)-1 may lose precision near zero", "formalStatus": "stub"},
    {"guardId": "blocked-unsupported-tree", "predicate": "unsupported or unstable trees route to blocked review", "formalStatus": "stub"},
]

LOWERING_RULES = [
    {
        "ruleId": "lower-exp-minus-one-to-expm1",
        "sourceAst": "Sub(Exp(x), Const(1))",
        "targetAst": "ProtectedExpm1(x)",
        "requiredGuards": ["finite-inputs", "near-zero-cancellation-risk"],
        "coveredBy": ["A11.2 protected-lowering benchmark", "A12 protected-lowering interpreter"],
        "proofStatus": "model_stub_not_formalized",
    },
    {
        "ruleId": "lower-log-sum-exp-to-protected",
        "sourceAst": "Log(Sum(map Exp xs))",
        "targetAst": "ProtectedLogSumExp(xs)",
        "requiredGuards": ["finite-inputs", "nonempty-vector"],
        "coveredBy": ["A11.2 protected-lowering benchmark", "A12 protected-lowering interpreter"],
        "proofStatus": "model_stub_not_formalized",
    },
    {
        "ruleId": "preserve-eml-proof-shape",
        "sourceAst": "Eml(x,y)",
        "targetAst": "Eml(x,y)",
        "requiredGuards": ["finite-inputs", "positive-log-argument"],
        "coveredBy": ["R10C scoped certificates for selected cases"],
        "proofStatus": "model_stub_not_formalized",
    },
    {
        "ruleId": "block-unsupported-lowering",
        "sourceAst": "UnsupportedOrUnstableTree",
        "targetAst": "BlockedReview",
        "requiredGuards": ["blocked-unsupported-tree"],
        "coveredBy": ["A9/A10 guard decision packets"],
        "proofStatus": "routing_stub_not_formalized",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_model_payload(r10e_path: Path, r10e: dict[str, Any], a12_path: Path | None, a12: dict[str, Any] | None) -> dict[str, Any]:
    open_obligations = [item["obligationId"] for item in r10e["skeleton"]["openObligations"]]
    a12_summary = a12["summary"] if a12 else None
    model = {
        "schemaVersion": MODEL_SCHEMA_VERSION,
        "modelType": "eml_proof_assistant_ast_guard_model_v0",
        "date": DATE,
        "sourceR10EPath": str(r10e_path),
        "sourceA12Path": str(a12_path) if a12_path else None,
        "astNodes": list(AST_NODES),
        "guards": list(GUARDS),
        "loweringRules": list(LOWERING_RULES),
        "openCompilerObligationsFromR10E": open_obligations,
        "a12InterpreterSummary": a12_summary,
        "summary": {
            "astNodeCount": len(AST_NODES),
            "guardCount": len(GUARDS),
            "loweringRuleCount": len(LOWERING_RULES),
            "openCompilerObligationCount": len(open_obligations),
            "a12InterpreterLinked": a12 is not None,
            "proofAssistantFormalizationComplete": False,
            "compilerCorrectnessProved": False,
            "compilerBehaviorChanged": False,
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_model(model)
    return model


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-r10f-proof-assistant-ast-guard-model",
        "title": "EML-R10F Proof-Assistant AST and Guard Model",
        "reviewDecision": "proof_assistant_ast_guard_model_stub_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "formalization_model_stub_open_obligations_no_compiler_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Proof-assistant AST and guard model stub only; no complete formalization, compiler correctness proof, full EML semantics, or production lowering claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_r10f.v0",
        "date": DATE,
        "title": "EML-R10F Proof-Assistant AST and Guard Model",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Pause EML infrastructure or begin Monogate Engine pivot with EML substrate handoff",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-R10F Proof-Assistant AST and Guard Model",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "R10F freezes a small AST, guard vocabulary, and lowering relation",
        "model for future proof-assistant work.",
        "",
        "## Model Counts",
        "",
        f"- AST nodes: `{payload['summary']['astNodeCount']}`",
        f"- Guards: `{payload['summary']['guardCount']}`",
        f"- Lowering rules: `{payload['summary']['loweringRuleCount']}`",
        f"- Open compiler obligations inherited from R10E: `{payload['summary']['openCompilerObligationCount']}`",
        f"- A12 interpreter linked: `{payload['summary']['a12InterpreterLinked']}`",
        "",
        "## Lowering Rules",
        "",
        "| Rule | Source | Target | Status |",
        "|---|---|---|---|",
    ]
    for rule in payload["model"]["loweringRules"]:
        lines.append(f"| `{rule['ruleId']}` | `{rule['sourceAst']}` | `{rule['targetAst']}` | `{rule['proofStatus']}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Model stub only.",
            "- No complete proof-assistant formalization.",
            "- No compiler correctness or full EML semantics claim.",
            "- No Forge/compiler behavior change.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_model(model: dict[str, Any]) -> None:
    if model["schemaVersion"] != MODEL_SCHEMA_VERSION:
        raise ValueError("invalid R10F model schema")
    if model["summary"]["astNodeCount"] < 8:
        raise ValueError("expected proof model AST vocabulary")
    if model["summary"]["guardCount"] < 4:
        raise ValueError("expected guard vocabulary")
    if model["summary"]["loweringRuleCount"] < 4:
        raise ValueError("expected lowering relation rules")
    if "compiler-wide-induction" not in model["openCompilerObligationsFromR10E"]:
        raise ValueError("R10F must inherit compiler-wide induction as open")
    for key in ["proofAssistantFormalizationComplete", "compilerCorrectnessProved", "compilerBehaviorChanged"]:
        if model["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in model["claimFlags"].items():
        if value is not False:
            raise ValueError(f"model claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid R10F schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid R10F status")
    validate_model(payload["model"])
    summary = payload["summary"]
    for key in ["proofAssistantFormalizationComplete", "compilerCorrectnessProved", "compilerBehaviorChanged"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_model(
    r10e_path: Path,
    a12_path: Path | None,
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    r10e = load_json(r10e_path)
    a12 = load_json(a12_path) if a12_path and a12_path.exists() else None
    model = build_model_payload(r10e_path, r10e, a12_path, a12)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "modelId": "eml_r10f_proof_assistant_ast_guard_model",
        "sourceR10EPath": str(r10e_path),
        "sourceA12Path": str(a12_path) if a12_path else None,
        "model": model,
        "summary": model["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_r10f_proof_assistant_ast_guard_model_{stamp}.json"
    model_path = out_dir / f"eml_proof_assistant_ast_guard_model_{stamp}.json"
    report_path = report_dir / f"eml_r10f_proof_assistant_ast_guard_model_{stamp}.md"
    evidence_path = evidence_dir / "eml_r10f_proof_assistant_ast_guard_model.json"
    feed_path = command_feed_dir / f"eml_r10f_proof_assistant_ast_guard_model_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    model_path.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "model": model,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "model_path": str(model_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    stamp = DATE.replace("-", "_")
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--r10e-path",
        type=Path,
        default=ROOT / f"python/results/eml_r10e_formal_compiler_proof_skeleton/eml_r10e_formal_compiler_proof_skeleton_{stamp}.json",
    )
    parser.add_argument(
        "--a12-path",
        type=Path,
        default=ROOT / f"python/results/eml_a12_protected_lowering_interpreter/eml_a12_protected_lowering_interpreter_{stamp}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_r10f_proof_assistant_ast_guard_model")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_model(args.r10e_path, args.a12_path, args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_R10F_PROOF_ASSISTANT_AST_GUARD_MODEL_OK")
    print(f"ast_nodes={built['payload']['summary']['astNodeCount']}")
    print(f"guards={built['payload']['summary']['guardCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
