#!/usr/bin/env python3
"""EML-R10E formal compiler proof skeleton.

Builds the proof-obligation skeleton for a future EML lowering correctness
proof. This records what is covered by R10C scoped certificates and what remains
open. It does not prove compiler correctness.
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

SCHEMA_VERSION = "monogate.eml_r10e_formal_compiler_proof_skeleton.v0"
SKELETON_SCHEMA_VERSION = "monogate.eml_formal_compiler_proof_skeleton.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_R10E_FORMAL_COMPILER_PROOF_SKELETON_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
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
    "R10E is a formal proof skeleton, not a completed compiler proof.",
    "R10E does not claim compiler correctness or full EML semantics.",
    "R10E does not change Forge/compiler behavior.",
    "R10E does not deploy or publish packages.",
]

COMPILER_OBLIGATIONS = [
    {
        "obligationId": "syntax-preservation",
        "title": "Lowering preserves well-formed expression structure.",
        "status": "open",
        "requiredForCompilerCorrectness": True,
        "neededArtifact": "formal AST/lowering relation",
    },
    {
        "obligationId": "domain-guard-preservation",
        "title": "Lowering preserves required domain guards.",
        "status": "open",
        "requiredForCompilerCorrectness": True,
        "neededArtifact": "guard calculus and proof assistant model",
    },
    {
        "obligationId": "per-case-semantic-preservation",
        "title": "Each lowered case preserves semantics under its guards.",
        "status": "covered_by_scoped_certificate",
        "requiredForCompilerCorrectness": True,
        "neededArtifact": "R10C scoped certificates for currently covered cases",
    },
    {
        "obligationId": "unsupported-case-routing",
        "title": "Unsupported lowerings are rejected or routed to candidate-only review.",
        "status": "open",
        "requiredForCompilerCorrectness": True,
        "neededArtifact": "total decision procedure over lowering cases",
    },
    {
        "obligationId": "runtime-implementation-correspondence",
        "title": "Generated runtime stubs correspond to the formal lowered expression.",
        "status": "open",
        "requiredForCompilerCorrectness": True,
        "neededArtifact": "codegen semantics for Python/Rust/C fixtures",
    },
    {
        "obligationId": "compiler-wide-induction",
        "title": "The lowering proof composes over arbitrary supported expression trees.",
        "status": "open",
        "requiredForCompilerCorrectness": True,
        "neededArtifact": "structural induction over EML AST",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def covered_cases(r10c: dict[str, Any]) -> list[dict[str, Any]]:
    cases = []
    for packet in r10c["proofPackets"]:
        cases.append(
            {
                "caseId": packet["caseId"],
                "proofStatus": packet["proofStatus"],
                "domainGuards": packet["domainGuards"],
                "rewriteStepCount": len(packet["rewriteSteps"]),
                "scopeBoundary": packet["scopeBoundary"],
            }
        )
    return cases


def build_skeleton_payload(r10c_path: Path, r10c: dict[str, Any]) -> dict[str, Any]:
    cases = covered_cases(r10c)
    obligations = [dict(item) for item in COMPILER_OBLIGATIONS]
    open_obligations = [item for item in obligations if item["status"] != "covered_by_scoped_certificate"]
    return {
        "schemaVersion": SKELETON_SCHEMA_VERSION,
        "skeletonType": "eml_formal_compiler_proof_skeleton_v0",
        "date": DATE,
        "sourceR10CPath": str(r10c_path),
        "obligations": obligations,
        "coveredCases": cases,
        "openObligations": open_obligations,
        "summary": {
            "obligationCount": len(obligations),
            "coveredObligationCount": len(obligations) - len(open_obligations),
            "openObligationCount": len(open_obligations),
            "coveredCaseCount": len(cases),
            "compilerCorrectnessProved": False,
            "formalCompilerProofComplete": False,
            "compilerBehaviorChanged": False,
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-r10e-formal-compiler-proof-skeleton",
        "title": "EML-R10E Formal Compiler Proof Skeleton",
        "reviewDecision": "formal_compiler_proof_skeleton_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "proof_skeleton_open_obligations_no_compiler_correctness_claim",
        "semanticReview": {
            "obligationCount": payload["summary"]["obligationCount"],
            "coveredObligationCount": payload["summary"]["coveredObligationCount"],
            "openObligationCount": payload["summary"]["openObligationCount"],
            "coveredCaseCount": payload["summary"]["coveredCaseCount"],
            "compilerCorrectnessProved": False,
            "formalCompilerProofComplete": False,
        },
        "claimBoundary": "Formal compiler proof skeleton only; open obligations remain and compiler correctness is not proved.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Maps R10C scoped certificates into a compiler proof skeleton.",
            "Separates covered per-case semantics from open compiler-wide obligations.",
            "Keeps compiler correctness blocked until open obligations are discharged.",
        ],
        "validationCommands": [
            "python python/scripts/eml_r10e_formal_compiler_proof_skeleton.py --build --strict",
            "python -m pytest -q python/tests/test_eml_r10e_formal_compiler_proof_skeleton.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_r10e.v0",
        "date": DATE,
        "title": "EML-R10E Formal Compiler Proof Skeleton",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "R10F proof-assistant AST and guard model",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-R10E Formal Compiler Proof Skeleton",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "R10E records the proof skeleton required for future EML lowering",
        "correctness. It maps R10C scoped certificates into one obligation lane",
        "and leaves compiler-wide obligations open.",
        "",
        "## Obligations",
        "",
        "| Obligation | Status | Needed artifact |",
        "|---|---|---|",
    ]
    for obligation in payload["skeleton"]["obligations"]:
        lines.append(
            f"| `{obligation['obligationId']}` | `{obligation['status']}` | {obligation['neededArtifact']} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Obligations: `{summary['obligationCount']}`",
            f"- Covered obligations: `{summary['coveredObligationCount']}`",
            f"- Open obligations: `{summary['openObligationCount']}`",
            f"- Covered cases: `{summary['coveredCaseCount']}`",
            f"- Compiler correctness proved: `{summary['compilerCorrectnessProved']}`",
            f"- Formal compiler proof complete: `{summary['formalCompilerProofComplete']}`",
            "",
            "## Boundary",
            "",
            "- Proof skeleton only.",
            "- No compiler correctness claim.",
            "- No full EML semantics claim.",
            "- No compiler behavior change.",
            "- No deployment or production lowering claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid R10E schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid R10E status")
    skeleton = payload["skeleton"]
    if skeleton.get("schemaVersion") != SKELETON_SCHEMA_VERSION:
        raise ValueError("invalid skeleton schema")
    summary = payload["summary"]
    if summary["obligationCount"] < 6:
        raise ValueError("expected at least 6 compiler proof obligations")
    if summary["coveredCaseCount"] < 4:
        raise ValueError("expected at least 4 covered scoped cases")
    if summary["openObligationCount"] <= 0:
        raise ValueError("skeleton must preserve open obligations")
    for key in ["compilerCorrectnessProved", "formalCompilerProofComplete", "compilerBehaviorChanged"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")
    for key, value in skeleton.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"skeleton claim flag must remain false: {key}")


def build_skeleton(
    r10c_path: Path,
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    r10c = load_json(r10c_path)
    skeleton = build_skeleton_payload(r10c_path, r10c)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceR10CPath": str(r10c_path),
        "skeleton": skeleton,
        "summary": skeleton["summary"],
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
    result_path = out_dir / f"eml_r10e_formal_compiler_proof_skeleton_{stamp}.json"
    skeleton_path = out_dir / f"eml_formal_compiler_proof_skeleton_{stamp}.json"
    report_path = report_dir / f"eml_r10e_formal_compiler_proof_skeleton_{stamp}.md"
    evidence_path = evidence_dir / "eml_r10e_formal_compiler_proof_skeleton.json"
    feed_path = command_feed_dir / f"eml_r10e_formal_compiler_proof_skeleton_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    skeleton_path.write_text(json.dumps(skeleton, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "skeleton": skeleton,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "skeleton_path": str(skeleton_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--r10c-path",
        type=Path,
        default=ROOT / f"python/results/eml_r10c_scoped_semantic_proof/eml_r10c_scoped_semantic_proof_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_r10e_formal_compiler_proof_skeleton")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_skeleton(args.r10c_path, args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_R10E_FORMAL_COMPILER_PROOF_SKELETON_OK")
    print(f"obligations={built['payload']['summary']['obligationCount']}")
    print(f"open_obligations={built['payload']['summary']['openObligationCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
