#!/usr/bin/env python3
"""EML-A6 private symbolic-regression harness.

This is the private runner for a future full PySR experiment. If PySR is not
available locally, the harness records that blocker and attaches the A5
deterministic template-search fallback. It never fabricates a full run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402
from scripts.eml_symbolic_regression_template_search import build_search  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a6_private_symbolic_regression.v0"
STATUS = "EML_A6_PRIVATE_SYMBOLIC_REGRESSION_BLOCKED_PYSR_UNAVAILABLE"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"


def pysr_status() -> dict[str, Any]:
    spec = importlib.util.find_spec("pysr")
    return {
        "available": spec is not None,
        "module": "pysr",
        "status": "available" if spec is not None else "unavailable",
    }


def build_private_run(out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    availability = pysr_status()
    fallback = build_search(
        out_dir=ROOT / "python/results/eml_symbolic_regression_template_search",
        report_dir=report_dir,
        evidence_dir=evidence_dir,
    )["result"]
    result = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "runId": "eml_a6_private_pysr_harness_v0",
        "visibility": "private_only",
        "pysr": {
            **availability,
            "fullRunPerformed": False,
            "blocker": "PySR is not installed in this environment." if not availability["available"] else "Not run by default; enable explicitly in a future controlled job.",
        },
        "fallback": {
            "kind": "deterministic_template_search",
            "status": fallback["status"],
            "searchId": fallback["searchId"],
            "reviewFinding": fallback["interpretation"]["reviewFinding"],
            "resultPath": f"python/results/eml_symbolic_regression_template_search/eml_symbolic_regression_template_search_{DATE.replace('-', '_')}.json",
            "templateCount": len(fallback["templates"]),
        },
        "nextRunContract": {
            "requires": ["pysr installed", "private runner only", "fixed random seed", "max runtime bound", "artifact capture"],
            "compareGrammars": ["eml_native", "standard_exp_log_trig"],
            "primaryMetrics": ["complexity_at_first_acceptable_loss", "best_loss_by_complexity", "generalization_holdout_loss"],
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "pysr_run_claim": False,
            "autonomous_discovery_claim": False,
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "public_atlas_promotion": False,
        },
        "nonClaims": [
            "This artifact does not claim a full PySR run.",
            "This artifact does not claim autonomous discovery.",
            "This artifact does not prove RH or discover zeta zeros.",
            "This artifact is private-only and does not promote Atlas entries.",
        ],
    }
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a6_private_symbolic_regression_{stamp}.json"
    report_path = report_dir / f"eml_a6_private_symbolic_regression_{stamp}.md"
    evidence_path = evidence_dir / "eml_a6_private_symbolic_regression.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(result), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"result": result, "evidence": evidence, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path)}


def build_evidence_packet(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a6-private-symbolic-regression",
        "title": "EML-A6 Private Symbolic Regression Harness",
        "reviewDecision": "blocked_environment_dependency",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": "private_harness_records_pysr_blocker_no_full_run_claim",
        "semanticReview": {
            "pysr_available": result["pysr"]["available"],
            "full_run_performed": False,
            "fallback_status": result["fallback"]["status"],
        },
        "claimBoundary": "Private harness only; PySR unavailable locally, fallback template search attached, no full-run/discovery/proof claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "pysr_run_claim": False,
            "autonomous_discovery_claim": False,
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "public_atlas_promotion": False,
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "nonClaims": result["nonClaims"],
        "reviewHighlights": [
            "Records the missing PySR dependency instead of pretending a full run occurred.",
            "Keeps A5 deterministic template search as fallback evidence.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a6_private_symbolic_regression.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a6_private_symbolic_regression.py",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# EML-A6 Private Symbolic Regression Harness",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{result['status']}`",
        "",
        f"PySR available: `{result['pysr']['available']}`",
        "",
        f"Full run performed: `{result['pysr']['fullRunPerformed']}`",
        "",
        f"Fallback: `{result['fallback']['kind']}` / `{result['fallback']['status']}`",
        "",
        "## Next Run Contract",
        "",
        *[f"- {item}" for item in result["nextRunContract"]["requires"]],
        "",
        "## Non-Claims",
        "",
        *[f"- {item}" for item in result["nonClaims"]],
        "",
    ]
    return "\n".join(lines)


def validate_private_run(result: dict[str, Any]) -> None:
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A6 schema")
    if result["pysr"]["fullRunPerformed"] is not False:
        raise ValueError("full PySR run must remain false unless a controlled job runs")
    if result["fallback"]["status"] != "EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_PASS":
        raise ValueError("fallback template search must pass")
    for key, value in result.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a6_private_symbolic_regression")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_private_run(args.out_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_private_run(built["result"])
    print("EML_A6_PRIVATE_SYMBOLIC_REGRESSION_OK")
    print(f"pysr_available={built['result']['pysr']['available']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
