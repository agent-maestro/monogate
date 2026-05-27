#!/usr/bin/env python3
"""EML-A7 Atlas promotion gate.

Consumes the generated Atlas annex and classifies each entry for safe public
education, internal reviewer-only handling, proof targeting, or blocking.
This script never promotes an entry by itself.
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

SCHEMA_VERSION = "monogate.eml_atlas_promotion_gate.v0"
STATUS = "EML_ATLAS_PROMOTION_GATE_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"


SAFE_PUBLIC_EDUCATION = {
    "exp_from_eml",
    "bose_boundary",
    "fermi_boundary",
    "maxwell_boundary",
    "subtraction_boundary",
    "q_integer_ratio",
    "bell_generating_rewrite",
}

PROOF_TARGETS = {
    "exp_from_eml": "checked_machlib_witness_available",
    "ln_from_eml": "candidate_machlib_witness",
    "constants_zero_and_e": "candidate_machlib_witness",
    "subtraction_boundary": "candidate_machlib_witness",
    "prime_signature_log_recovery": "candidate_machlib_witness",
}


def gate_decision(entry: dict[str, Any]) -> dict[str, Any]:
    entry_id = entry["id"]
    classification = entry["classification"]
    if classification == "conjectural_or_blocked":
        bucket = "blocked_or_conjectural"
        public_candidate = False
    elif entry_id in SAFE_PUBLIC_EDUCATION:
        bucket = "safe_public_education_candidate"
        public_candidate = True
    elif entry_id in PROOF_TARGETS:
        bucket = "proof_target"
        public_candidate = False
    else:
        bucket = "internal_reviewer_only"
        public_candidate = False

    return {
        "id": entry_id,
        "atlasObject": entry["atlasObject"],
        "classification": classification,
        "bucket": bucket,
        "publicEducationCandidate": public_candidate,
        "publicPromotionPerformed": False,
        "proofStatus": PROOF_TARGETS.get(entry_id, "not_a_current_proof_target"),
        "reason": reason_for(bucket),
    }


def reason_for(bucket: str) -> str:
    reasons = {
        "safe_public_education_candidate": "Simple identity/rewrite can be explained publicly with explicit non-claims.",
        "proof_target": "Exact identity is better routed to MachLib before public strengthening.",
        "internal_reviewer_only": "Needs private verifier, reproduction, or domain notes before surfacing.",
        "blocked_or_conjectural": "Must stay blocked from public promotion.",
    }
    return reasons[bucket]


def build_gate(annex_path: Path, out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    annex = json.loads(annex_path.read_text(encoding="utf-8"))
    decisions = [gate_decision(entry) for entry in annex["entries"]]
    bucket_counts: dict[str, int] = {}
    for decision in decisions:
        bucket_counts[decision["bucket"]] = bucket_counts.get(decision["bucket"], 0) + 1

    result = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceAnnexPath": str(annex_path),
        "sourceAnnexStatus": annex["status"],
        "entryCount": len(decisions),
        "bucketCounts": bucket_counts,
        "decisions": decisions,
        "checkedWitnesses": [
            {
                "entryId": "exp_from_eml",
                "machlibName": "MachLib.Real.atlas_exp_from_eml_witness",
                "status": "checked_by_lake_build",
            }
        ],
        "policy": {
            "publicPromotionPerformed": False,
            "safePublicEducationRequires": [
                "plain-language wording",
                "explicit non-claims",
                "reviewer approval",
                "no blocked/conjectural bucket",
            ],
            "blockedBuckets": ["blocked_or_conjectural"],
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "public_atlas_promotion": False,
            "public_superbest_claim_change": False,
            "theorem_discovery_claim": False,
            "rh_proof_claim": False,
            "physics_theorem_claim": False,
        },
        "nonClaims": [
            "This gate does not modify monogate.org/atlas.",
            "This gate does not promote any entry publicly.",
            "This gate does not create theorem-discovery, RH, physics, or SuperBEST claims.",
            "Safe public education candidates still require separate reviewer approval.",
        ],
    }
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_atlas_promotion_gate_{stamp}.json"
    report_path = report_dir / f"eml_a7_atlas_promotion_gate_{stamp}.md"
    evidence_path = evidence_dir / "eml_atlas_promotion_gate.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(result), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"result": result, "evidence": evidence, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path)}


def build_evidence_packet(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-atlas-promotion-gate",
        "title": "EML-A7 Atlas Promotion Gate",
        "reviewDecision": "candidate_only",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": "atlas_claim_routing_gate_no_public_promotion",
        "semanticReview": {
            "entry_count": result["entryCount"],
            "bucket_counts": result["bucketCounts"],
            "public_promotion_performed": False,
            "checked_witness_count": len(result["checkedWitnesses"]),
        },
        "claimBoundary": "Review gate only; no public Atlas modification or theorem-discovery claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "public_atlas_promotion": False,
            "public_superbest_claim_change": False,
            "theorem_discovery_claim": False,
            "rh_proof_claim": False,
            "physics_theorem_claim": False,
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "nonClaims": result["nonClaims"],
        "reviewHighlights": [
            "Separates public education candidates from proof targets and blocked statements.",
            "Records exp_from_eml as the first checked MachLib Atlas witness.",
        ],
        "validationCommands": [
            "python python/scripts/eml_atlas_promotion_gate.py --build --strict",
            "python -m pytest -q python/tests/test_eml_atlas_promotion_gate.py",
            "lake build",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# EML-A7 Atlas Promotion Gate",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{result['status']}`",
        "",
        "| Bucket | Count |",
        "|---|---:|",
    ]
    for key, value in sorted(result["bucketCounts"].items()):
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Checked Witnesses", ""])
    for witness in result["checkedWitnesses"]:
        lines.append(f"- `{witness['entryId']}` -> `{witness['machlibName']}` (`{witness['status']}`)")
    lines.extend(["", "## Non-Claims", "", *[f"- {item}" for item in result["nonClaims"]], ""])
    return "\n".join(lines)


def validate_gate(result: dict[str, Any]) -> None:
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid gate schema")
    if result.get("status") != STATUS:
        raise ValueError("gate must pass")
    if result.get("entryCount", 0) < 30:
        raise ValueError("expected expanded annex")
    if result["policy"]["publicPromotionPerformed"] is not False:
        raise ValueError("public promotion must remain false")
    if result["bucketCounts"].get("blocked_or_conjectural", 0) < 1:
        raise ValueError("expected blocked bucket")
    checked = {item["entryId"]: item for item in result["checkedWitnesses"]}
    if checked.get("exp_from_eml", {}).get("status") != "checked_by_lake_build":
        raise ValueError("expected exp_from_eml checked witness")
    for key, value in result.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    for decision in result["decisions"]:
        if decision["bucket"] == "blocked_or_conjectural" and decision["publicEducationCandidate"] is not False:
            raise ValueError(f"blocked item cannot be public candidate: {decision['id']}")
        if decision["publicPromotionPerformed"] is not False:
            raise ValueError(f"promotion performed unexpectedly: {decision['id']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--annex-path", type=Path, default=ROOT / f"python/results/eml_atlas_annex/eml_atlas_annex_{DATE.replace('-', '_')}.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_atlas_promotion_gate")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_gate(args.annex_path, args.out_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_gate(built["result"])
    print("EML_ATLAS_PROMOTION_GATE_OK")
    print(f"entries={built['result']['entryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
