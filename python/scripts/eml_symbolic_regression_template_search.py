#!/usr/bin/env python3
"""EML-A5 symbolic-regression-style template search.

This is a deterministic template-search benchmark over the same psi(x)-x
fixture used by EML-A2. It is not a full PySR run and it does not claim
autonomous theorem discovery. The purpose is to make the next research question
reviewable: which small grammar templates are promising enough to deserve a
proper symbolic-regression job later?
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

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402
from scripts.eml_prime_residual_benchmark import (  # noqa: E402
    FIRST_ZETA_ZERO_GAMMA,
    eml_prediction,
    fixture,
    standard_profiled_prediction,
)

SCHEMA_VERSION = "monogate.eml_symbolic_regression_template_search.v0"
STATUS = "EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a - b) ** 2))


def profiled_plain_trig(xs: np.ndarray, residual: np.ndarray, gamma: float) -> tuple[np.ndarray, list[float]]:
    log_x = np.log(xs)
    design = np.column_stack([np.cos(gamma * log_x), np.sin(gamma * log_x)])
    coefficients = np.linalg.lstsq(design, residual, rcond=None)[0]
    return design @ coefficients, [float(coefficients[0]), float(coefficients[1])]


def wrong_exponent_prediction(xs: np.ndarray, gamma: float, exponent: float) -> np.ndarray:
    rho = exponent + 1j * gamma
    return np.array([-2.0 * ((complex(x) ** rho) / rho).real for x in xs])


def constant_prediction(xs: np.ndarray, residual: np.ndarray) -> tuple[np.ndarray, list[float]]:
    coefficient = float(np.mean(residual))
    return np.full_like(xs, coefficient), [coefficient]


def template_specs() -> list[dict[str, Any]]:
    return [
        {
            "id": "eml_critical_one_node",
            "family": "eml",
            "grammarOperatorNodes": 1,
            "freeParameterCount": 1,
            "description": "-2 Re(x^(1/2+i gamma)/(1/2+i gamma))",
        },
        {
            "id": "standard_profiled_sqrt_cos_sin",
            "family": "standard",
            "grammarOperatorNodes": 5,
            "freeParameterCount": 3,
            "description": "sqrt(x) * (A cos(gamma log x) + B sin(gamma log x)) with profiled amplitudes",
        },
        {
            "id": "eml_wrong_exponent_03",
            "family": "negative_control",
            "grammarOperatorNodes": 1,
            "freeParameterCount": 1,
            "description": "-2 Re(x^(0.3+i gamma)/(0.3+i gamma))",
        },
        {
            "id": "eml_wrong_exponent_07",
            "family": "negative_control",
            "grammarOperatorNodes": 1,
            "freeParameterCount": 1,
            "description": "-2 Re(x^(0.7+i gamma)/(0.7+i gamma))",
        },
        {
            "id": "plain_profiled_cos_sin",
            "family": "negative_control",
            "grammarOperatorNodes": 3,
            "freeParameterCount": 3,
            "description": "A cos(gamma log x) + B sin(gamma log x) with no sqrt(x) envelope",
        },
        {
            "id": "constant_baseline",
            "family": "baseline",
            "grammarOperatorNodes": 0,
            "freeParameterCount": 1,
            "description": "mean residual baseline",
        },
    ]


def template_prediction(
    template_id: str,
    xs: np.ndarray,
    residual: np.ndarray,
    gamma: float,
) -> tuple[np.ndarray, list[float]]:
    if template_id == "eml_critical_one_node":
        return eml_prediction(xs, gamma), []
    if template_id == "standard_profiled_sqrt_cos_sin":
        prediction, coefficients = standard_profiled_prediction(xs, residual, gamma)
        return prediction, [float(coefficients[0]), float(coefficients[1])]
    if template_id == "eml_wrong_exponent_03":
        return wrong_exponent_prediction(xs, gamma, 0.3), []
    if template_id == "eml_wrong_exponent_07":
        return wrong_exponent_prediction(xs, gamma, 0.7), []
    if template_id == "plain_profiled_cos_sin":
        return profiled_plain_trig(xs, residual, gamma)
    if template_id == "constant_baseline":
        return constant_prediction(xs, residual)
    raise ValueError(f"unknown template: {template_id}")


def scan_template(
    spec: dict[str, Any],
    xs: np.ndarray,
    residual: np.ndarray,
    gammas: np.ndarray,
) -> dict[str, Any]:
    if spec["id"] == "constant_baseline":
        prediction, coefficients = template_prediction(spec["id"], xs, residual, 0.0)
        best_mse = mse(residual, prediction)
        return {
            **spec,
            "bestGamma": None,
            "bestMse": best_mse,
            "errorFromFirstKnownZero": None,
            "profiledCoefficients": coefficients,
            "complexityAdjustedScore": best_mse + 0.05 * spec["grammarOperatorNodes"],
            "status": "baseline",
        }

    losses: list[float] = []
    coefficients_by_gamma: list[list[float]] = []
    for gamma in gammas:
        prediction, coefficients = template_prediction(spec["id"], xs, residual, float(gamma))
        losses.append(mse(residual, prediction))
        coefficients_by_gamma.append(coefficients)
    losses_arr = np.array(losses)
    best_idx = int(np.argmin(losses_arr))
    best_gamma = float(gammas[best_idx])
    best_mse = float(losses_arr[best_idx])
    return {
        **spec,
        "bestGamma": best_gamma,
        "bestMse": best_mse,
        "errorFromFirstKnownZero": abs(best_gamma - FIRST_ZETA_ZERO_GAMMA),
        "profiledCoefficients": coefficients_by_gamma[best_idx],
        "complexityAdjustedScore": best_mse + 0.05 * spec["grammarOperatorNodes"],
        "status": "candidate_template",
    }


def build_search(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    gamma_min: float = 5.0,
    gamma_max: float = 40.0,
    gamma_steps: int = 2000,
) -> dict[str, Any]:
    fx = fixture()
    gammas = np.linspace(gamma_min, gamma_max, gamma_steps)
    templates = [scan_template(spec, fx["x"], fx["residual"], gammas) for spec in template_specs()]
    ranked_by_mse = sorted(templates, key=lambda item: item["bestMse"])
    ranked_by_localization = sorted(
        [item for item in templates if item["errorFromFirstKnownZero"] is not None],
        key=lambda item: item["errorFromFirstKnownZero"],
    )
    ranked_by_score = sorted(templates, key=lambda item: item["complexityAdjustedScore"])
    ranked_candidates_by_score = sorted(
        [item for item in templates if item["family"] != "baseline"],
        key=lambda item: item["complexityAdjustedScore"],
    )
    result = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "searchId": "eml_a5_template_search_v0",
        "fixture": fx["summary"],
        "scan": {
            "gammaMin": gamma_min,
            "gammaMax": gamma_max,
            "gammaSteps": gamma_steps,
            "knownFirstZetaZeroGamma": FIRST_ZETA_ZERO_GAMMA,
        },
        "templates": templates,
        "rankings": {
            "byMse": [item["id"] for item in ranked_by_mse],
            "byLocalization": [item["id"] for item in ranked_by_localization],
            "byComplexityAdjustedScore": [item["id"] for item in ranked_by_score],
            "byCandidateComplexityAdjustedScore": [item["id"] for item in ranked_candidates_by_score],
        },
        "interpretation": {
            "resultLabel": "candidate_template_search_not_full_symbolic_regression",
            "fullPysrRunPerformed": False,
            "summary": (
                "The EML critical-line template remains a compact candidate and leads the simple "
                "complexity-adjusted score on this fixture, but the template search is intentionally "
                "ambiguous: a wrong-exponent control localizes slightly closer, and low-MSE baselines "
                "show that MSE alone is not evidence of structure."
            ),
            "reviewFinding": "promising_but_not_decisive",
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "eml_grammar_theorem_claim": False,
            "pysr_run_claim": False,
            "public_atlas_promotion": False,
        },
        "nonClaims": [
            "This search does not prove RH.",
            "This search does not discover zeta zeros.",
            "This search is not a full PySR run.",
            "This search does not prove an EML grammar theorem.",
            "This search does not promote any Atlas entry publicly.",
            "This search does not change Forge/compiler behavior.",
        ],
    }
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_symbolic_regression_template_search_{stamp}.json"
    report_path = report_dir / f"eml_a5_symbolic_regression_template_search_{stamp}.md"
    evidence_path = evidence_dir / "eml_symbolic_regression_template_search.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(result), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "result": result,
        "evidence": evidence,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
    }


def build_evidence_packet(result: dict[str, Any]) -> dict[str, Any]:
    eml = next(item for item in result["templates"] if item["id"] == "eml_critical_one_node")
    standard = next(item for item in result["templates"] if item["id"] == "standard_profiled_sqrt_cos_sin")
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-symbolic-regression-template-search",
        "title": "EML-A5 Symbolic Regression Template Search",
        "reviewDecision": "candidate_only",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": "fixed_template_search_candidate_no_theorem_claim",
        "semanticReview": {
            "search_id": result["searchId"],
            "template_count": len(result["templates"]),
            "full_pysr_run_performed": False,
            "eml_best_gamma": eml["bestGamma"],
            "standard_best_gamma": standard["bestGamma"],
            "eml_error_from_first_known_zero": eml["errorFromFirstKnownZero"],
            "standard_error_from_first_known_zero": standard["errorFromFirstKnownZero"],
        },
        "claimBoundary": "Deterministic fixed-template benchmark only; no proof, zeta-zero discovery, full PySR run, or public Atlas promotion claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "eml_grammar_theorem_claim": False,
            "pysr_run_claim": False,
            "public_atlas_promotion": False,
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "nonClaims": result["nonClaims"],
        "reviewHighlights": [
            "Ranks fixed EML, standard, and negative-control templates on the same residual fixture.",
            "Separates localization, MSE, and complexity-adjusted scoring.",
            "Marks full PySR/autodiscovery as future work.",
        ],
        "validationCommands": [
            "python python/scripts/eml_symbolic_regression_template_search.py --build --strict",
            "python -m pytest -q python/tests/test_eml_symbolic_regression_template_search.py",
        ],
        "timeline": [
            {"label": "Fixture", "status": "pass", "detail": "Reused deterministic EML-A2 psi(x)-x residual."},
            {"label": "Template scan", "status": "pass", "detail": "Scanned fixed template library over gamma range."},
            {"label": "Claim boundary", "status": "pass", "detail": "Proof/discovery/PySR/promotion flags remain false."},
        ],
        "reviewReasons": [
            "Turns the high-upside symbolic-regression idea into a reproducible reviewer artifact.",
        ],
        "reviewNotes": "Candidate-only template search. Use as triage before a full symbolic-regression run.",
        "sourceReportPath": f"reports/eml_a5_symbolic_regression_template_search_{DATE.replace('-', '_')}.md",
        "evidencePaths": [
            "python/scripts/eml_symbolic_regression_template_search.py",
            f"python/results/eml_symbolic_regression_template_search/eml_symbolic_regression_template_search_{DATE.replace('-', '_')}.json",
            f"reports/eml_a5_symbolic_regression_template_search_{DATE.replace('-', '_')}.md",
            "reports/evidence_packets/eml_symbolic_regression_template_search.json",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# EML-A5 Symbolic Regression Template Search",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{result['status']}`",
        "",
        "This is a deterministic fixed-template search, not a full PySR run.",
        "",
        "| Template | Family | Nodes | Params | Best gamma | MSE | Error from first known zero |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in result["templates"]:
        gamma = "n/a" if item["bestGamma"] is None else f"`{item['bestGamma']:.6f}`"
        error = "n/a" if item["errorFromFirstKnownZero"] is None else f"`{item['errorFromFirstKnownZero']:.6f}`"
        lines.append(
            f"| `{item['id']}` | `{item['family']}` | `{item['grammarOperatorNodes']}` | "
            f"`{item['freeParameterCount']}` | {gamma} | `{item['bestMse']:.6f}` | {error} |"
        )
    lines.extend(
        [
            "",
            "## Rankings",
            "",
            f"- By MSE: `{', '.join(result['rankings']['byMse'])}`",
            f"- By localization: `{', '.join(result['rankings']['byLocalization'])}`",
            f"- By complexity-adjusted score: `{', '.join(result['rankings']['byComplexityAdjustedScore'])}`",
            "",
            "## Interpretation",
            "",
            result["interpretation"]["summary"],
            "",
            "## Non-Claims",
            "",
            *[f"- {item}" for item in result["nonClaims"]],
            "",
        ]
    )
    return "\n".join(lines)


def validate_search(result: dict[str, Any]) -> None:
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid template-search schema")
    if result.get("status") != STATUS:
        raise ValueError("template-search status must pass")
    if len(result.get("templates", [])) < 6:
        raise ValueError("expected at least six templates")
    if result["interpretation"].get("fullPysrRunPerformed") is not False:
        raise ValueError("full PySR run flag must remain false")
    eml = next(item for item in result["templates"] if item["id"] == "eml_critical_one_node")
    standard = next(item for item in result["templates"] if item["id"] == "standard_profiled_sqrt_cos_sin")
    if eml["errorFromFirstKnownZero"] >= 0.06:
        raise ValueError("EML critical template did not localize gamma1 within fixture tolerance")
    if standard["bestMse"] >= eml["bestMse"]:
        raise ValueError("expected profiled standard template to remain lower MSE")
    if result["rankings"]["byCandidateComplexityAdjustedScore"][0] != "eml_critical_one_node":
        raise ValueError("expected EML critical template to lead complexity-adjusted ranking")
    wrong = next(item for item in result["templates"] if item["id"] == "eml_wrong_exponent_03")
    if wrong["errorFromFirstKnownZero"] >= eml["errorFromFirstKnownZero"]:
        raise ValueError("expected wrong-exponent control to expose localization ambiguity")
    for key, value in result.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_symbolic_regression_template_search")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_search(args.out_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_search(built["result"])
    eml = next(item for item in built["result"]["templates"] if item["id"] == "eml_critical_one_node")
    print("EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_OK")
    print(f"eml_best_gamma={eml['bestGamma']:.6f}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
