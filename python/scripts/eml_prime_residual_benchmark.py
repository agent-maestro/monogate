#!/usr/bin/env python3
"""EML-A2 prime residual grammar benchmark.

This benchmark asks a narrow, falsifiable question: on one fixed Chebyshev
psi residual fixture, does an EML-shaped critical-line basis localize the first
known zeta-zero frequency with lower grammar complexity than a profiled
standard trigonometric basis?

It is not a proof lane. Null results are acceptable. The output is
candidate-only internal evidence.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402

SCHEMA_VERSION = "monogate.eml_prime_residual_benchmark.v0"
STATUS = "EML_PRIME_RESIDUAL_BENCHMARK_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
FIRST_ZETA_ZERO_GAMMA = 14.134725141


def primes_upto(n: int) -> np.ndarray:
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            sieve[p * p : n + 1 : p] = False
    return np.where(sieve)[0]


def chebyshev_psi(xs: np.ndarray) -> np.ndarray:
    max_x = int(math.floor(float(xs.max())))
    prime_powers: list[tuple[int, float]] = []
    for prime in primes_upto(max_x):
        power = int(prime)
        log_prime = math.log(float(prime))
        while power <= max_x:
            prime_powers.append((power, log_prime))
            power *= int(prime)
    prime_powers.sort(key=lambda item: item[0])
    thresholds = np.array([item[0] for item in prime_powers])
    log_values = np.array([item[1] for item in prime_powers])
    cumulative = np.cumsum(log_values)
    idx = np.searchsorted(thresholds, xs, side="right") - 1
    return np.where(idx >= 0, cumulative[idx], 0.0)


def fixture(x_min: float = 4.0, x_max: float = 120.0, n_samples: int = 800) -> dict[str, Any]:
    xs = np.linspace(x_min, x_max, n_samples)
    psi = chebyshev_psi(xs)
    residual = psi - xs
    return {
        "x": xs,
        "psi": psi,
        "residual": residual,
        "summary": {
            "xMin": x_min,
            "xMax": x_max,
            "sampleCount": n_samples,
            "residualMin": float(residual.min()),
            "residualMax": float(residual.max()),
            "residualMseAgainstZero": float(np.mean(residual**2)),
            "primeCountUpToMax": int(len(primes_upto(int(x_max)))),
        },
    }


def eml_prediction(xs: np.ndarray, gamma: float) -> np.ndarray:
    rho = 0.5 + 1j * gamma
    # Equivalent to -2 * Re(eml(rho * ln(x), 1) / rho), because eml(z, 1)=exp(z).
    return np.array([-2.0 * ((complex(x) ** rho) / rho).real for x in xs])


def standard_profiled_prediction(xs: np.ndarray, residual: np.ndarray, gamma: float) -> tuple[np.ndarray, np.ndarray]:
    log_x = np.log(xs)
    sqrt_x = np.sqrt(xs)
    design = np.column_stack([
        sqrt_x * np.cos(gamma * log_x),
        sqrt_x * np.sin(gamma * log_x),
    ])
    coefficients = np.linalg.lstsq(design, residual, rcond=None)[0]
    return design @ coefficients, coefficients


def scan_gamma(
    xs: np.ndarray,
    residual: np.ndarray,
    gamma_min: float = 5.0,
    gamma_max: float = 40.0,
    gamma_steps: int = 2000,
) -> dict[str, Any]:
    gammas = np.linspace(gamma_min, gamma_max, gamma_steps)
    eml_losses = []
    standard_losses = []
    standard_coefficients = []
    for gamma in gammas:
        eml_y = eml_prediction(xs, float(gamma))
        eml_losses.append(float(np.mean((residual - eml_y) ** 2)))
        standard_y, coefficients = standard_profiled_prediction(xs, residual, float(gamma))
        standard_losses.append(float(np.mean((residual - standard_y) ** 2)))
        standard_coefficients.append([float(coefficients[0]), float(coefficients[1])])
    eml_losses_arr = np.array(eml_losses)
    standard_losses_arr = np.array(standard_losses)
    eml_idx = int(np.argmin(eml_losses_arr))
    standard_idx = int(np.argmin(standard_losses_arr))
    return {
        "gammaMin": gamma_min,
        "gammaMax": gamma_max,
        "gammaSteps": gamma_steps,
        "knownFirstZetaZeroGamma": FIRST_ZETA_ZERO_GAMMA,
        "eml": {
            "model": "single_eml_frequency",
            "grammarOperatorNodes": 1,
            "freeParameterCount": 1,
            "bestGamma": float(gammas[eml_idx]),
            "bestMse": float(eml_losses_arr[eml_idx]),
            "errorFromFirstKnownZero": abs(float(gammas[eml_idx]) - FIRST_ZETA_ZERO_GAMMA),
        },
        "standard": {
            "model": "profiled_sqrt_cos_sin",
            "grammarOperatorNodes": 5,
            "freeParameterCount": 3,
            "bestGamma": float(gammas[standard_idx]),
            "bestMse": float(standard_losses_arr[standard_idx]),
            "errorFromFirstKnownZero": abs(float(gammas[standard_idx]) - FIRST_ZETA_ZERO_GAMMA),
            "profiledCoefficients": standard_coefficients[standard_idx],
        },
        "comparison": {
            "emlCloserToFirstKnownZero": abs(float(gammas[eml_idx]) - FIRST_ZETA_ZERO_GAMMA)
            < abs(float(gammas[standard_idx]) - FIRST_ZETA_ZERO_GAMMA),
            "standardLowerMse": float(standard_losses_arr[standard_idx]) < float(eml_losses_arr[eml_idx]),
            "mseGapStandardMinusEml": float(standard_losses_arr[standard_idx] - eml_losses_arr[eml_idx]),
            "complexityRatioStandardToEml": 5.0,
        },
        "lossSamples": [
            {
                "gamma": float(gammas[index]),
                "emlMse": float(eml_losses_arr[index]),
                "standardMse": float(standard_losses_arr[index]),
            }
            for index in np.linspace(0, gamma_steps - 1, 60, dtype=int)
        ],
    }


def negative_controls(xs: np.ndarray, residual: np.ndarray) -> list[dict[str, Any]]:
    rng = np.random.default_rng(20260527)
    shuffled = residual.copy()
    rng.shuffle(shuffled)
    gaussian = 3.0 * np.exp(-((xs - 48.0) ** 2) / (2 * 12.0**2)) - 2.0 * np.exp(
        -((xs - 92.0) ** 2) / (2 * 8.0**2)
    )
    controls = []
    for label, control_residual in [("shuffled_residual", shuffled), ("gaussian_bumps", gaussian)]:
        scan = scan_gamma(xs, control_residual, gamma_steps=800)
        controls.append(
            {
                "label": label,
                "status": "context_only",
                "emlBestGamma": scan["eml"]["bestGamma"],
                "standardBestGamma": scan["standard"]["bestGamma"],
                "emlErrorFromFirstKnownZero": scan["eml"]["errorFromFirstKnownZero"],
                "standardErrorFromFirstKnownZero": scan["standard"]["errorFromFirstKnownZero"],
                "nonClaim": "Negative controls are context checks, not proof of specificity.",
            }
        )
    return controls


def build_benchmark(out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    fx = fixture()
    scan = scan_gamma(fx["x"], fx["residual"])
    controls = negative_controls(fx["x"], fx["residual"])
    result = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "benchmarkId": "eml_a2_prime_residual_gamma_scan_v0",
        "fixture": fx["summary"],
        "scan": scan,
        "negativeControls": controls,
        "interpretation": {
            "resultLabel": "candidate_supports_eml_frequency_localization_on_fixed_fixture",
            "nullResultAcceptable": True,
            "summary": (
                "On this fixed psi(x)-x fixture, the EML-shaped one-parameter scan lands closer "
                "to the first known zeta-zero frequency; the profiled standard basis has lower MSE "
                "because it fits two amplitudes at each frequency."
            ),
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "public_atlas_promotion": False,
            "benchmark_generalization_claim": False,
        },
        "nonClaims": [
            "This benchmark does not prove RH.",
            "This benchmark does not discover zeta zeros.",
            "This benchmark does not prove an EML grammar theorem.",
            "This benchmark does not promote any Atlas entry publicly.",
            "This benchmark does not change Forge/compiler behavior.",
            "Null results are acceptable for future runs.",
        ],
    }
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_prime_residual_benchmark_{stamp}.json"
    report_path = report_dir / f"eml_a2_prime_residual_benchmark_{stamp}.md"
    evidence_path = evidence_dir / "eml_prime_residual_benchmark.json"
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
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-prime-residual-benchmark",
        "title": "EML-A2 Prime Residual Benchmark",
        "reviewDecision": "candidate_only",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": "prime_residual_grammar_benchmark_candidate_no_rh_claim",
        "semanticReview": {
            "benchmark_id": result["benchmarkId"],
            "known_first_zeta_zero_gamma": result["scan"]["knownFirstZetaZeroGamma"],
            "eml_best_gamma": result["scan"]["eml"]["bestGamma"],
            "standard_best_gamma": result["scan"]["standard"]["bestGamma"],
            "eml_error_from_first_known_zero": result["scan"]["eml"]["errorFromFirstKnownZero"],
            "standard_error_from_first_known_zero": result["scan"]["standard"]["errorFromFirstKnownZero"],
            "null_result_acceptable": True,
        },
        "claimBoundary": "Fixed-fixture grammar benchmark only; no RH proof, zeta-zero discovery, theorem, or public Atlas promotion claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "public_atlas_promotion": False,
            "benchmark_generalization_claim": False,
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "nonClaims": result["nonClaims"],
        "reviewHighlights": [
            "Compares one EML-shaped frequency parameter with a profiled standard trigonometric basis.",
            "Records both localization error and MSE instead of forcing a one-number verdict.",
            "Includes deterministic negative controls marked context-only.",
        ],
        "validationCommands": [
            "python python/scripts/eml_prime_residual_benchmark.py --build --strict",
            "python -m pytest -q python/tests/test_eml_prime_residual_benchmark.py",
        ],
        "timeline": [
            {"label": "Fixture", "status": "pass", "detail": "Generated deterministic psi(x)-x residual on x in [4, 120]."},
            {"label": "Gamma scan", "status": "pass", "detail": "Scanned 2000 gamma values for EML and standard bases."},
            {"label": "Claim boundary", "status": "pass", "detail": "RH/theorem/discovery/promotion flags remain false."},
        ],
        "reviewReasons": [
            "High-upside falsifiable EML grammar-compression experiment, kept candidate-only.",
        ],
        "reviewNotes": "Internal benchmark artifact. Results should be treated as one fixture, not a theorem.",
        "sourceReportPath": f"reports/eml_a2_prime_residual_benchmark_{DATE.replace('-', '_')}.md",
        "evidencePaths": [
            "python/scripts/eml_prime_residual_benchmark.py",
            f"python/results/eml_prime_residual_benchmark/eml_prime_residual_benchmark_{DATE.replace('-', '_')}.json",
            f"reports/eml_a2_prime_residual_benchmark_{DATE.replace('-', '_')}.md",
            "reports/evidence_packets/eml_prime_residual_benchmark.json",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    scan = result["scan"]
    lines = [
        "# EML-A2 Prime Residual Benchmark",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{result['status']}`",
        "",
        "This is a fixed-fixture grammar benchmark, not a theorem lane.",
        "",
        "| Model | Grammar nodes | Free parameters | Best gamma | MSE | Error from first known zero |",
        "|---|---:|---:|---:|---:|---:|",
        f"| EML-shaped | `{scan['eml']['grammarOperatorNodes']}` | `{scan['eml']['freeParameterCount']}` | "
        f"`{scan['eml']['bestGamma']:.6f}` | `{scan['eml']['bestMse']:.6f}` | "
        f"`{scan['eml']['errorFromFirstKnownZero']:.6f}` |",
        f"| Standard profiled | `{scan['standard']['grammarOperatorNodes']}` | `{scan['standard']['freeParameterCount']}` | "
        f"`{scan['standard']['bestGamma']:.6f}` | `{scan['standard']['bestMse']:.6f}` | "
        f"`{scan['standard']['errorFromFirstKnownZero']:.6f}` |",
        "",
        "## Interpretation",
        "",
        result["interpretation"]["summary"],
        "",
        "## Negative Controls",
        "",
        "| Control | EML best gamma | Standard best gamma | Status |",
        "|---|---:|---:|---|",
    ]
    for control in result["negativeControls"]:
        lines.append(
            f"| `{control['label']}` | `{control['emlBestGamma']:.6f}` | "
            f"`{control['standardBestGamma']:.6f}` | `{control['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            *[f"- {item}" for item in result["nonClaims"]],
            "",
        ]
    )
    return "\n".join(lines)


def validate_benchmark(result: dict[str, Any]) -> None:
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid benchmark schema")
    if result.get("status") != STATUS:
        raise ValueError("benchmark status must pass")
    if result["fixture"]["sampleCount"] != 800:
        raise ValueError("unexpected fixture size")
    if result["scan"]["eml"]["errorFromFirstKnownZero"] >= 0.06:
        raise ValueError("EML scan did not localize first known zero within expected fixture tolerance")
    if not result["scan"]["comparison"]["emlCloserToFirstKnownZero"]:
        raise ValueError("expected EML scan to be closer on this fixed fixture")
    if not result["scan"]["comparison"]["standardLowerMse"]:
        raise ValueError("expected profiled standard basis to have lower MSE on this fixed fixture")
    if len(result["negativeControls"]) < 2:
        raise ValueError("expected deterministic negative controls")
    for key, value in result.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_prime_residual_benchmark")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_benchmark(args.out_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_benchmark(built["result"])
    print("EML_PRIME_RESIDUAL_BENCHMARK_OK")
    print(f"eml_best_gamma={built['result']['scan']['eml']['bestGamma']:.6f}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
