#!/usr/bin/env python3
"""Draft safe public-education copy for selected Atlas entries.

This consumes the A7 promotion gate and writes draft copy only. It does not
modify monogate.org/atlas and does not mark anything as publicly promoted.
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
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402

SCHEMA_VERSION = "monogate.eml_atlas_safe_education_draft.v0"
STATUS = "EML_ATLAS_SAFE_EDUCATION_DRAFT_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"

COPY: dict[str, dict[str, str]] = {
    "exp_from_eml": {
        "title": "Exponential As One EML Call",
        "plainLanguage": "When the second input is 1, EML returns the ordinary exponential because ln(1) is 0.",
        "formula": "eml(x, 1) = exp(x)",
    },
    "bose_boundary": {
        "title": "The exp(x) - 1 Boundary",
        "plainLanguage": "When the second input is e, EML produces exp(x) - 1. This is a familiar denominator shape in classical formulas, but here it is only being shown as a rewrite.",
        "formula": "eml(x, e) = exp(x) - 1",
    },
    "fermi_boundary": {
        "title": "The exp(x) + 1 Boundary",
        "plainLanguage": "When the second input is exp(-1), EML produces exp(x) + 1. The draft may mention the familiar denominator shape, but must not claim new physics.",
        "formula": "eml(x, exp(-1)) = exp(x) + 1",
    },
    "maxwell_boundary": {
        "title": "The Classical exp(x) Boundary",
        "plainLanguage": "When the second input is 1, EML lands on exp(x). This overlaps with exp_from_eml and should be kept short if surfaced.",
        "formula": "eml(x, 1) = exp(x)",
    },
    "subtraction_boundary": {
        "title": "Subtraction As A Boundary",
        "plainLanguage": "If v is positive, feeding log(v) and exp(u) into EML collapses back to v - u.",
        "formula": "eml(log(v), exp(u)) = v - u, for v > 0",
    },
    "q_integer_ratio": {
        "title": "Q-Integers As An EML Ratio",
        "plainLanguage": "With q = exp(x), a q-integer can be written as a ratio of two EML boundary evaluations.",
        "formula": "[n]_q = eml(n*x, e) / eml(x, e), q = exp(x)",
    },
    "bell_generating_rewrite": {
        "title": "Bell Generating Function Shape",
        "plainLanguage": "A nested EML expression reproduces the exponential generating function shape for Bell numbers.",
        "formula": "eml(eml(x, e), 1) = exp(exp(x) - 1)",
    },
}


def build_draft(gate_path: Path, out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    safe = [
        decision for decision in gate["decisions"]
        if decision["bucket"] == "safe_public_education_candidate"
    ]
    drafts = []
    for decision in safe:
        copy = COPY[decision["id"]]
        drafts.append(
            {
                "id": decision["id"],
                "title": copy["title"],
                "plainLanguage": copy["plainLanguage"],
                "formula": copy["formula"],
                "sourceBucket": decision["bucket"],
                "proofStatus": decision["proofStatus"],
                "publicPromotionPerformed": False,
                "reviewStatus": "draft_needs_human_review",
                "nonClaims": [
                    "This draft does not modify monogate.org/atlas.",
                    "This draft does not claim a new theorem.",
                    "This draft does not claim physics, RH, zeta-zero, or public SuperBEST results.",
                ],
            }
        )
    result = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceGatePath": str(gate_path),
        "draftCount": len(drafts),
        "drafts": drafts,
        "policy": {
            "publicPromotionPerformed": False,
            "requiresMuseOrReviewerReview": True,
            "allowedUse": "draft_copy_for_review_only",
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "public_atlas_promotion": False,
            "theorem_discovery_claim": False,
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "physics_theorem_claim": False,
            "public_superbest_claim_change": False,
        },
        "nonClaims": [
            "This artifact is draft copy only.",
            "This artifact does not modify or deploy monogate.org/atlas.",
            "This artifact does not make theorem, RH, physics, or SuperBEST claims.",
            "Every draft still needs human review before publication.",
        ],
    }
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_atlas_safe_education_draft_{stamp}.json"
    report_path = report_dir / f"eml_a9_atlas_safe_education_draft_{stamp}.md"
    evidence_path = evidence_dir / "eml_atlas_safe_education_draft.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(result), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"result": result, "evidence": evidence, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path)}


def build_evidence_packet(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-atlas-safe-education-draft",
        "title": "EML Atlas Safe Education Draft",
        "reviewDecision": "draft_needs_human_review",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": "draft_copy_no_public_promotion",
        "semanticReview": {
            "draft_count": result["draftCount"],
            "public_promotion_performed": False,
            "requires_muse_or_reviewer_review": True,
        },
        "claimBoundary": "Draft copy only; no public Atlas modification or theorem claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "public_atlas_promotion": False,
            "theorem_discovery_claim": False,
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "physics_theorem_claim": False,
            "public_superbest_claim_change": False,
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "nonClaims": result["nonClaims"],
        "reviewHighlights": [
            "Drafts only the A7 safe public education candidates.",
            "Keeps public promotion false for every item.",
        ],
        "validationCommands": [
            "python python/scripts/eml_atlas_safe_education_draft.py --build --strict",
            "python -m pytest -q python/tests/test_eml_atlas_safe_education_draft.py",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# EML-A9 Atlas Safe Education Draft",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{result['status']}`",
        "",
        "Draft copy only. No public Atlas modification is performed.",
        "",
    ]
    for draft in result["drafts"]:
        lines.extend(
            [
                f"## {draft['title']}",
                "",
                f"- Entry: `{draft['id']}`",
                f"- Formula: `{draft['formula']}`",
                f"- Proof status: `{draft['proofStatus']}`",
                f"- Public promotion performed: `{draft['publicPromotionPerformed']}`",
                "",
                draft["plainLanguage"],
                "",
            ]
        )
    lines.extend(["## Non-Claims", "", *[f"- {item}" for item in result["nonClaims"]], ""])
    return "\n".join(lines)


def validate_draft(result: dict[str, Any]) -> None:
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid draft schema")
    if result.get("status") != STATUS:
        raise ValueError("draft status must pass")
    if result.get("draftCount") != 7:
        raise ValueError("expected exactly seven safe education drafts")
    if result["policy"]["publicPromotionPerformed"] is not False:
        raise ValueError("public promotion must remain false")
    for key, value in result.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    for draft in result["drafts"]:
        if draft["publicPromotionPerformed"] is not False:
            raise ValueError(f"draft promoted unexpectedly: {draft['id']}")
        if not draft["plainLanguage"]:
            raise ValueError(f"draft missing copy: {draft['id']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--gate-path", type=Path, default=ROOT / f"python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_{DATE.replace('-', '_')}.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_atlas_safe_education_draft")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_draft(args.gate_path, args.out_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_draft(built["result"])
    print("EML_ATLAS_SAFE_EDUCATION_DRAFT_OK")
    print(f"drafts={built['result']['draftCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
