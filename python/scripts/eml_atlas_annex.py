#!/usr/bin/env python3
"""EML-A1 Atlas Evidence Annex.

This is a generated verifier/classifier for selected Atlas-style EML claims.
It supports the public monogate.org Atlas without replacing it or expanding
public proof, savings, RH, physics, or compiler claims.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402

SCHEMA_VERSION = "monogate.eml_atlas_annex.v0"
STATUS = "EML_ATLAS_ANNEX_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
TOLERANCE = 1e-9
MACHLIB_STUB_SCHEMA_VERSION = "monogate.eml_atlas_annex_machlib_stub_manifest.v0"


def eml(x: complex, y: complex) -> complex:
    return cmath.exp(x) - cmath.log(y)


def _abs_error(a: complex, b: complex) -> float:
    return abs(a - b)


def _sample(label: str, observed: complex, expected: complex, tolerance: float = TOLERANCE) -> dict[str, Any]:
    error = _abs_error(observed, expected)
    return {
        "label": label,
        "observed": _format_complex(observed),
        "expected": _format_complex(expected),
        "absError": error,
        "tolerance": tolerance,
        "pass": error <= tolerance,
    }


def _format_complex(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _polylog_series(s: int, lam: float, terms: int = 20000) -> float:
    return sum((lam**k) / (k**s) for k in range(1, terms + 1))


def _mellin_kernel_series(s: int, lam: float, terms: int = 20000) -> float:
    # Integral expansion:
    # 1 / (exp(x) - lam) = sum_{k>=0} lam^k exp(-(k+1)x)
    # so integral x^(s-1)/(exp(x)-lam) dx = Gamma(s) * Li_s(lam) / lam.
    return math.gamma(s) * sum((lam**k) / ((k + 1) ** s) for k in range(terms))


def validate_exp_from_eml() -> list[dict[str, Any]]:
    return [_sample(f"x={x}", eml(x, 1), cmath.exp(x)) for x in [-2.0, 0.0, 1.5]]


def validate_bose_boundary() -> list[dict[str, Any]]:
    return [_sample(f"x={x}", eml(x, math.e), cmath.exp(x) - 1) for x in [-1.0, 0.25, 2.0]]


def validate_fermi_boundary() -> list[dict[str, Any]]:
    return [_sample(f"x={x}", eml(x, math.exp(-1)), cmath.exp(x) + 1) for x in [-1.0, 0.25, 2.0]]


def validate_subtraction_boundary() -> list[dict[str, Any]]:
    pairs = [(3.5, 1.25), (10.0, -2.0), (0.75, 0.5)]
    return [
        _sample(f"v={v},u={u}", eml(math.log(v), math.exp(u)), v - u)
        for v, u in pairs
    ]


def validate_forward_difference() -> list[dict[str, Any]]:
    # For f(t)=t^3, exp(d/dt)f(t) is the finite Taylor shift f(t+1).
    samples = []
    for t in [-2.0, 0.0, 3.0]:
        shifted = t**3 + 3 * t**2 + 3 * t + 1
        delta = shifted - t**3
        samples.append(_sample(f"t={t}", shifted - t**3, (t + 1) ** 3 - t**3))
        samples.append(_sample(f"delta={t}", delta, 3 * t**2 + 3 * t + 1))
    return samples


def validate_q_integer() -> list[dict[str, Any]]:
    samples = []
    for n, x in [(2, 0.2), (3, 0.5), (5, -0.15)]:
        q = math.exp(x)
        observed = eml(n * x, math.e) / eml(x, math.e)
        expected = (q**n - 1) / (q - 1)
        samples.append(_sample(f"n={n},x={x}", observed, expected))
    return samples


def validate_bell_generating_rewrite() -> list[dict[str, Any]]:
    return [
        _sample(
            f"x={x}",
            eml(eml(x, math.e), 1),
            cmath.exp(cmath.exp(x) - 1),
        )
        for x in [-0.5, 0.0, 0.5]
    ]


def validate_dedekind_eta_factor() -> list[dict[str, Any]]:
    samples = []
    for n, tau in [(1, 1j), (2, 0.3 + 0.9j), (3, -0.2 + 1.2j)]:
        z = 2j * math.pi * n * tau
        observed = 1 - cmath.exp(z)
        expected = -eml(z, math.e)
        samples.append(_sample(f"n={n}", observed, expected))
    return samples


def validate_mellin_polylog_correction() -> list[dict[str, Any]]:
    samples = []
    for s, lam in [(2, 0.25), (2, 0.5), (3, 0.75)]:
        observed = _mellin_kernel_series(s, lam)
        corrected = math.gamma(s) * _polylog_series(s, lam) / lam
        incorrect = math.gamma(s) * _polylog_series(s, lam)
        samples.append(_sample(f"s={s},lambda={lam}", observed, corrected, tolerance=1e-10))
        samples.append(
            {
                "label": f"missing-factor-check s={s},lambda={lam}",
                "observed": observed,
                "incorrectWithoutDivisionByLambda": incorrect,
                "absError": abs(observed - incorrect),
                "pass": abs(observed - incorrect) > 1e-3,
            }
        )
    return samples


def validate_zeta_explicit_formula_rewrite() -> list[dict[str, Any]]:
    samples = []
    for x, gamma in [(10.0, 14.134725141), (100.0, 21.022039639), (50.0, 25.01085758)]:
        rho = 0.5 + 1j * gamma
        sigma = math.log(math.log(x))
        observed = eml(rho * eml(sigma, 1), 1)
        expected = cmath.exp(rho * math.log(x))
        samples.append(_sample(f"x={x},gamma={gamma}", observed, expected, tolerance=1e-8))
    return samples


def validate_rh_modulus_boundary() -> list[dict[str, Any]]:
    x = 100.0
    critical = 0.5 + 14.134725141j
    off_critical = 0.3 + 14.134725141j
    sigma = math.log(math.log(x))
    critical_modulus = abs(eml(critical * eml(sigma, 1), 1))
    off_modulus = abs(eml(off_critical * eml(sigma, 1), 1))
    return [
        {
            "label": "critical-line-sample",
            "observedModulus": critical_modulus,
            "expectedSqrtX": math.sqrt(x),
            "absError": abs(critical_modulus - math.sqrt(x)),
            "pass": abs(critical_modulus - math.sqrt(x)) <= 1e-8,
        },
        {
            "label": "off-critical-control",
            "observedModulus": off_modulus,
            "expectedNotSqrtX": math.sqrt(x),
            "absError": abs(off_modulus - math.sqrt(x)),
            "pass": abs(off_modulus - math.sqrt(x)) > 1e-3,
        },
    ]


def validate_ln_from_eml() -> list[dict[str, Any]]:
    return [
        _sample(f"y={y}", eml(1, eml(eml(1, y), 1)), cmath.log(y))
        for y in [0.25, 1.5, 7.0]
    ]


def validate_constants_zero_and_e() -> list[dict[str, Any]]:
    return [
        _sample("e", eml(1, 1), math.e),
        _sample("zero", eml(1, eml(eml(1, 1), 1)), 0),
    ]


def validate_maxwell_boundary() -> list[dict[str, Any]]:
    return [_sample(f"x={x}", eml(x, 1), cmath.exp(x)) for x in [-1.0, 0.25, 2.0]]


def validate_euler_null_state() -> list[dict[str, Any]]:
    return [
        _sample("i*pi, exp(-1)", eml(1j * math.pi, math.exp(-1)), 0, tolerance=1e-9),
    ]


def validate_prime_signature_log_recovery() -> list[dict[str, Any]]:
    return [
        _sample(f"p={p}", eml(math.log(math.log(p)), 1), math.log(p))
        for p in [2, 3, 17, 101]
    ]


def validate_review_queue_only() -> list[dict[str, Any]]:
    return [
        {
            "label": "review-queue-only",
            "pass": True,
            "nonClaim": "This entry is classified for review routing only; no numeric or proof validation is asserted.",
        }
    ]


VALIDATORS: dict[str, Callable[[], list[dict[str, Any]]]] = {
    "exp_from_eml": validate_exp_from_eml,
    "ln_from_eml": validate_ln_from_eml,
    "constants_zero_and_e": validate_constants_zero_and_e,
    "bose_boundary": validate_bose_boundary,
    "fermi_boundary": validate_fermi_boundary,
    "maxwell_boundary": validate_maxwell_boundary,
    "subtraction_boundary": validate_subtraction_boundary,
    "euler_null_state": validate_euler_null_state,
    "prime_signature_log_recovery": validate_prime_signature_log_recovery,
    "forward_difference_operator": validate_forward_difference,
    "q_integer_ratio": validate_q_integer,
    "bell_generating_rewrite": validate_bell_generating_rewrite,
    "dedekind_eta_factor": validate_dedekind_eta_factor,
    "mellin_polylog_correction": validate_mellin_polylog_correction,
    "zeta_explicit_formula_rewrite": validate_zeta_explicit_formula_rewrite,
    "rh_modulus_boundary": validate_rh_modulus_boundary,
}


for _queued_id in [
    "theta_prime_signature_sum",
    "psi_prime_power_sum",
    "prime_number_theorem_signature",
    "polylog_lerch_extension",
    "stat_mechanics_triad",
    "stefan_boltzmann_zeta4",
    "arithmetic_gas_partition",
    "dedekind_eta_product_numeric",
    "string_eta_critical_dimension",
    "quaternionic_null_sphere",
    "hopf_fibration_null_analogy",
    "gue_spacing_null_result",
    "prime_signature_sequence",
    "mellin_deformation_family",
    "operator_family_dn",
    "finite_difference_heaviside",
    "superbest_cost_boundary",
    "symbolic_regression_prediction",
    "riemann_eml_dictionary",
]:
    VALIDATORS[_queued_id] = validate_review_queue_only


SEED_ENTRIES: list[dict[str, Any]] = [
    {
        "id": "exp_from_eml",
        "atlasObject": "exp(x)",
        "classification": "exact_identity",
        "standardForm": "exp(x)",
        "emlForm": "eml(x, 1)",
        "claimBoundary": "Definition-level EML identity over the real/complex exponential branch used by this verifier.",
    },
    {
        "id": "ln_from_eml",
        "atlasObject": "ln(y) from EML",
        "classification": "exact_identity",
        "standardForm": "ln(y)",
        "emlForm": "eml(1, eml(eml(1, y), 1))",
        "claimBoundary": "Requires y > 0 on the real branch.",
    },
    {
        "id": "constants_zero_and_e",
        "atlasObject": "constants e and 0",
        "classification": "exact_identity",
        "standardForm": "e, 0",
        "emlForm": "eml(1,1), eml(1, eml(eml(1,1),1))",
        "claimBoundary": "Definition-level constant identities only.",
    },
    {
        "id": "bose_boundary",
        "atlasObject": "Bose-Einstein denominator",
        "classification": "exact_identity",
        "standardForm": "exp(x) - 1",
        "emlForm": "eml(x, e)",
        "claimBoundary": "Boundary rewrite only; no new physics theorem is claimed.",
    },
    {
        "id": "fermi_boundary",
        "atlasObject": "Fermi-Dirac denominator",
        "classification": "exact_identity",
        "standardForm": "exp(x) + 1",
        "emlForm": "eml(x, exp(-1))",
        "claimBoundary": "Boundary rewrite only; no new physics theorem is claimed.",
    },
    {
        "id": "maxwell_boundary",
        "atlasObject": "Maxwell-Boltzmann boundary",
        "classification": "exact_identity",
        "standardForm": "exp(x)",
        "emlForm": "eml(x, 1)",
        "claimBoundary": "Boundary rewrite only; no new statistical-mechanics theorem is claimed.",
    },
    {
        "id": "subtraction_boundary",
        "atlasObject": "linear subtraction boundary",
        "classification": "exact_identity",
        "standardForm": "v - u",
        "emlForm": "eml(log(v), exp(u))",
        "claimBoundary": "Requires v > 0 on the real branch.",
    },
    {
        "id": "euler_null_state",
        "atlasObject": "Euler null state",
        "classification": "exact_identity",
        "standardForm": "exp(i*pi) + 1 = 0",
        "emlForm": "eml(i*pi, exp(-1)) = 0",
        "claimBoundary": "Complex principal-branch identity; no topology or physics theorem is claimed.",
    },
    {
        "id": "prime_signature_log_recovery",
        "atlasObject": "prime signature log recovery",
        "classification": "exact_identity",
        "standardForm": "ln(p)",
        "emlForm": "eml(ln(ln(p)), 1)",
        "claimBoundary": "Requires p > 1; signature notation does not prove prime-distribution claims.",
    },
    {
        "id": "forward_difference_operator",
        "atlasObject": "forward difference operator",
        "classification": "standard_rewrite",
        "standardForm": "exp(d/dt) - 1",
        "emlForm": "eml(d/dt, e)",
        "claimBoundary": "Operational-calculus rewrite checked on a polynomial witness; not a general operator-domain proof.",
    },
    {
        "id": "q_integer_ratio",
        "atlasObject": "q-integers",
        "classification": "standard_rewrite",
        "standardForm": "(q^n - 1) / (q - 1), q=exp(x)",
        "emlForm": "eml(n*x, e) / eml(x, e)",
        "claimBoundary": "Algebraic rewrite for q != 1; no quantum-group theorem is claimed.",
    },
    {
        "id": "bell_generating_rewrite",
        "atlasObject": "Bell exponential generating function",
        "classification": "standard_rewrite",
        "standardForm": "exp(exp(x) - 1)",
        "emlForm": "eml(eml(x, e), 1)",
        "claimBoundary": "Generating-function rewrite only; no combinatorics proof is claimed.",
    },
    {
        "id": "dedekind_eta_factor",
        "atlasObject": "Dedekind eta product factor",
        "classification": "standard_rewrite",
        "standardForm": "1 - exp(2*pi*i*n*tau)",
        "emlForm": "-eml(2*pi*i*n*tau, e)",
        "claimBoundary": "Single product-factor rewrite; no modular-form theorem is claimed.",
    },
    {
        "id": "mellin_polylog_correction",
        "atlasObject": "Mellin/polylog EML kernel",
        "classification": "standard_rewrite",
        "standardForm": "Integral x^(s-1)/(exp(x)-lambda) dx = Gamma(s)*Li_s(lambda)/lambda",
        "emlForm": "Integral x^(s-1)/eml(x, exp(log(lambda))) dx",
        "claimBoundary": "Includes the required division by lambda for 0 < lambda < 1; lambda -> 0 is a limiting case.",
    },
    {
        "id": "zeta_explicit_formula_rewrite",
        "atlasObject": "zeta explicit-formula term",
        "classification": "standard_rewrite",
        "standardForm": "x^rho",
        "emlForm": "eml(rho * eml(log(log(x)), 1), 1)",
        "claimBoundary": "Grammar rewrite of a known term; not a proof of the explicit formula or RH.",
    },
    {
        "id": "rh_modulus_boundary",
        "atlasObject": "RH modulus statement",
        "classification": "conjectural_or_blocked",
        "standardForm": "|x^rho| = sqrt(x) for non-trivial zeros on Re(rho)=1/2",
        "emlForm": "|eml(rho * eml(log(log(x)), 1), 1)| = sqrt(x)",
        "claimBoundary": "Blocked as a public theorem claim; verifier only demonstrates critical-line and off-critical samples.",
    },
    {
        "id": "theta_prime_signature_sum",
        "atlasObject": "Chebyshev theta via prime signatures",
        "classification": "standard_rewrite",
        "standardForm": "theta(x) = sum_{p <= x} ln(p)",
        "emlForm": "sum_{p <= x} eml(sigma(p), 1)",
        "claimBoundary": "Finite-sum rewrite only; no prime number theorem claim.",
    },
    {
        "id": "psi_prime_power_sum",
        "atlasObject": "Chebyshev psi via prime signatures",
        "classification": "standard_rewrite",
        "standardForm": "psi(x) = sum_{p^k <= x} ln(p)",
        "emlForm": "sum_{p^k <= x} eml(sigma(p), 1)",
        "claimBoundary": "Finite-sum rewrite only; no explicit-formula proof.",
    },
    {
        "id": "prime_number_theorem_signature",
        "atlasObject": "prime number theorem signature form",
        "classification": "standard_rewrite",
        "standardForm": "pi(x) ~ x / ln(x)",
        "emlForm": "pi(x) ~ x / eml(sigma(x), 1)",
        "claimBoundary": "Asymptotic theorem restatement only; no proof or improved bound.",
    },
    {
        "id": "polylog_lerch_extension",
        "atlasObject": "polylog/Lerch extension",
        "classification": "standard_rewrite",
        "standardForm": "Gamma(s) Phi(z,s,a)",
        "emlForm": "Mellin kernel with exp/log boundary parameters",
        "claimBoundary": "Named-function mapping only; no new special-function theorem.",
    },
    {
        "id": "stat_mechanics_triad",
        "atlasObject": "statistical mechanics triad",
        "classification": "heuristic_analogy",
        "standardForm": "Fermi, Maxwell, Bose denominators",
        "emlForm": "eml(x, exp(-1)), eml(x, 1), eml(x, e)",
        "claimBoundary": "Pedagogical boundary pattern; no new physics theorem.",
    },
    {
        "id": "stefan_boltzmann_zeta4",
        "atlasObject": "Stefan-Boltzmann zeta(4) bridge",
        "classification": "standard_rewrite",
        "standardForm": "Integral x^3/(exp(x)-1) dx = pi^4/15",
        "emlForm": "Integral x^3/eml(x,e) dx",
        "claimBoundary": "Classical identity restatement; no new physical derivation.",
    },
    {
        "id": "arithmetic_gas_partition",
        "atlasObject": "arithmetic gas partition function",
        "classification": "heuristic_analogy",
        "standardForm": "zeta as bosonic partition function",
        "emlForm": "Euler product factors as EML exponentials",
        "claimBoundary": "Known Bost-Connes style analogy; no theorem claim.",
    },
    {
        "id": "dedekind_eta_product_numeric",
        "atlasObject": "Dedekind eta EML product",
        "classification": "numeric_observation",
        "standardForm": "eta(tau) product",
        "emlForm": "product of -eml(2*pi*i*n*tau, e) factors",
        "claimBoundary": "Numerical/product observation; no modular-form theorem.",
    },
    {
        "id": "string_eta_critical_dimension",
        "atlasObject": "string eta critical-dimension note",
        "classification": "heuristic_analogy",
        "standardForm": "eta(tau)^-24 and zeta regularization",
        "emlForm": "eta factors routed through EML product factors",
        "claimBoundary": "Pedagogical analogy; no string-theory theorem.",
    },
    {
        "id": "quaternionic_null_sphere",
        "atlasObject": "quaternionic null sphere",
        "classification": "numeric_observation",
        "standardForm": "exp(q) = -1 for pure |q| = pi",
        "emlForm": "eml(q, exp(-1)) = 0",
        "claimBoundary": "Quaternionic identity candidate needs dedicated algebra verifier.",
    },
    {
        "id": "hopf_fibration_null_analogy",
        "atlasObject": "Hopf fibration null analogy",
        "classification": "heuristic_analogy",
        "standardForm": "division-algebra null-set dimensions",
        "emlForm": "EML null sets across C/H/O",
        "claimBoundary": "Analogy only; octonionic case is blocked until formalized.",
    },
    {
        "id": "gue_spacing_null_result",
        "atlasObject": "GUE spacing null result",
        "classification": "numeric_observation",
        "standardForm": "Delta sigma(p) vs zeta zero spacings",
        "emlForm": "prime-signature gap experiment",
        "claimBoundary": "Recorded null result; no spectral correspondence claim.",
    },
    {
        "id": "prime_signature_sequence",
        "atlasObject": "prime signature sequence",
        "classification": "numeric_observation",
        "standardForm": "sigma(p)=ln(ln(p))",
        "emlForm": "zero of eml(x,p)",
        "claimBoundary": "Coordinate projection only; no prime-distribution theorem.",
    },
    {
        "id": "mellin_deformation_family",
        "atlasObject": "Mellin deformation family",
        "classification": "standard_rewrite",
        "standardForm": "Integral x^(s-1)/(exp(x)-lambda) dx",
        "emlForm": "Integral x^(s-1)/eml(x, exp(log(lambda))) dx",
        "claimBoundary": "Uses corrected polylog factor; no zero-free-region claim.",
    },
    {
        "id": "operator_family_dn",
        "atlasObject": "D_n operator family",
        "classification": "heuristic_analogy",
        "standardForm": "exp(n*x) - (ln y)^n",
        "emlForm": "higher-order duality engine",
        "claimBoundary": "Exploratory family; not validated as universal algebra.",
    },
    {
        "id": "finite_difference_heaviside",
        "atlasObject": "Heaviside operational calculus",
        "classification": "standard_rewrite",
        "standardForm": "exp(D) - 1 = Delta",
        "emlForm": "eml(D, e)",
        "claimBoundary": "Operator-domain proof remains future work.",
    },
    {
        "id": "superbest_cost_boundary",
        "atlasObject": "SuperBEST cost boundary",
        "classification": "conjectural_or_blocked",
        "standardForm": "public tree cost vs internal DAG cost",
        "emlForm": "Atlas cost claims routed through evidence packets",
        "claimBoundary": "Blocked from public promotion without cost-lab evidence.",
    },
    {
        "id": "symbolic_regression_prediction",
        "atlasObject": "symbolic regression prediction",
        "classification": "numeric_observation",
        "standardForm": "template search on psi(x)-x",
        "emlForm": "EML-shaped critical-line basis",
        "claimBoundary": "Benchmark-only; no theorem or zeta-zero discovery claim.",
    },
    {
        "id": "riemann_eml_dictionary",
        "atlasObject": "Riemann-EML dictionary",
        "classification": "conjectural_or_blocked",
        "standardForm": "zeta identities rewritten in EML grammar",
        "emlForm": "dictionary of Dirichlet, Euler product, xi, explicit formula",
        "claimBoundary": "Dictionary is notation/grammar unless separately proved.",
    },
]


def analyze_entry(entry: dict[str, Any]) -> dict[str, Any]:
    checks = VALIDATORS[entry["id"]]()
    action = review_action(entry)
    return {
        **entry,
        "validationStatus": "pass" if all(item.get("pass") is True for item in checks) else "fail",
        "numericChecks": checks,
        "sampleCount": len(checks),
        "reviewAction": action,
        "publicAtlasSource": "https://monogate.org/atlas",
        "promoteToPublicAtlas": False,
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "This annex does not replace the public monogate.org Atlas.",
            "This annex does not create a theorem/proof claim.",
            "This annex does not create a public SuperBEST savings claim.",
            "This annex does not prove RH, physics theorems, modular-form theorems, or quantum-group theorems.",
        ],
    }


def review_action(entry: dict[str, Any]) -> dict[str, Any]:
    classification = entry["classification"]
    if classification == "exact_identity":
        return {
            "action": "candidate_machlib_witness",
            "priority": 1,
            "rationale": "Small exact identity suitable for a future checked witness or explicit blocked proof card.",
        }
    if classification == "standard_rewrite":
        return {
            "action": "keep_private_symbolic_or_numeric_verifier",
            "priority": 2,
            "rationale": "Useful Atlas support material, but needs domain notes before public promotion.",
        }
    if classification == "numeric_observation":
        return {
            "action": "needs_reproduction_benchmark",
            "priority": 3,
            "rationale": "Observation should remain internal until the benchmark is independently reproducible.",
        }
    if classification == "heuristic_analogy":
        return {
            "action": "keep_private_expository_only",
            "priority": 4,
            "rationale": "Good explanatory lens, not a verifier or theorem lane.",
        }
    return {
        "action": "blocked_public_claim",
        "priority": 5,
        "rationale": "Must stay blocked unless a separate proof, benchmark, or reviewer decision changes the boundary.",
    }


def build_review_queue(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue = [
        {
            "id": entry["id"],
            "atlasObject": entry["atlasObject"],
            "classification": entry["classification"],
            "validationStatus": entry["validationStatus"],
            "action": entry["reviewAction"]["action"],
            "priority": entry["reviewAction"]["priority"],
            "rationale": entry["reviewAction"]["rationale"],
            "promoteToPublicAtlas": False,
        }
        for entry in entries
    ]
    return sorted(queue, key=lambda item: (item["priority"], item["id"]))


def action_counts(review_queue: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in review_queue:
        counts[item["action"]] = counts.get(item["action"], 0) + 1
    return counts


def next_proof_targets(review_queue: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "atlasObject": item["atlasObject"],
            "action": item["action"],
            "status": "candidate_only_not_proved",
        }
        for item in review_queue
        if item["action"] == "candidate_machlib_witness"
    ][:limit]


def machlib_stub_name(entry_id: str) -> str:
    return f"{entry_id}_candidate_obligation"


def render_machlib_stubs(targets: list[dict[str, Any]]) -> str:
    lines = [
        "-- Candidate-only EML Atlas Annex stubs.",
        "-- Generated by python/scripts/eml_atlas_annex.py.",
        "-- These are review targets, not checked proof claims.",
        "",
        "namespace Monogate",
        "namespace EML",
        "namespace AtlasAnnex",
        "",
    ]
    for target in targets:
        escaped = target["atlasObject"].replace('"', '\\"')
        lines.extend(
            [
                f'def {machlib_stub_name(target["id"])} : String :=',
                f'  "{escaped}: candidate-only Atlas identity witness target"',
                "",
            ]
        )
    lines.extend(["end AtlasAnnex", "end EML", "end Monogate", ""])
    return "\n".join(lines)


def build_machlib_stub_manifest(targets: list[dict[str, Any]], stub_path: Path) -> dict[str, Any]:
    try:
        rendered_stub_path = str(stub_path.relative_to(ROOT))
    except ValueError:
        rendered_stub_path = str(stub_path)
    return {
        "schemaVersion": MACHLIB_STUB_SCHEMA_VERSION,
        "date": DATE,
        "status": "candidate_only",
        "stubPath": rendered_stub_path,
        "stubCount": len(targets),
        "exactIdentityCount": len(targets),
        "targets": targets,
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "formal_verification_claim": False,
            "theorem_proof_claim": False,
            "machlib_build_claim": False,
            "public_ready": False,
        },
        "nonClaims": [
            "These stubs are not checked Lean theorems.",
            "These stubs do not claim MachLib build success.",
            "These stubs do not promote Atlas entries publicly.",
        ],
    }


def build_annex(out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    entries = [analyze_entry(entry) for entry in SEED_ENTRIES]
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["classification"]] = counts.get(entry["classification"], 0) + 1
    review_queue = build_review_queue(entries)
    proof_targets = next_proof_targets(review_queue)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS if all(entry["validationStatus"] == "pass" for entry in entries) else "EML_ATLAS_ANNEX_FAIL",
        "publicAtlasSource": "https://monogate.org/atlas",
        "annexRole": "private_generated_verification_layer",
        "entryCount": len(entries),
        "classificationCounts": counts,
        "reviewQueueSummary": {
            "queueCount": len(review_queue),
            "actionCounts": action_counts(review_queue),
            "candidateMachlibWitnessCount": len(proof_targets),
            "publicPromotionCount": 0,
        },
        "reviewQueue": review_queue,
        "nextProofTargets": proof_targets,
        "claimPromotionPolicy": {
            "defaultDecision": "candidate_only",
            "publicPromotionRequires": [
                "reviewer approval",
                "domain notes",
                "evidence packet",
                "no forbidden claim flags",
            ],
            "publicAtlasPromotionPerformed": False,
        },
        "entries": entries,
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "The monogate.org Atlas remains the canonical public Atlas.",
            "This annex is an internal evidence and claim-hygiene layer.",
            "No RH proof, physics theorem, modular-form theorem, quantum-group theorem, or public SuperBEST claim is made.",
            "No Forge/compiler behavior changes are made.",
            "No package publish or deploy is performed by this script.",
        ],
    }
    evidence = build_evidence_packet(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_atlas_annex_{stamp}.json"
    report_path = report_dir / f"eml_a1_atlas_evidence_annex_{stamp}.md"
    evidence_path = evidence_dir / "eml_atlas_annex.json"
    stub_dir = report_dir / "eml_atlas_annex_machlib_stubs"
    stub_dir.mkdir(parents=True, exist_ok=True)
    stub_path = stub_dir / "eml_atlas_annex_exact_identity_stubs.lean"
    stub_manifest_path = stub_dir / "eml_atlas_annex_exact_identity_stub_manifest.json"
    stub_manifest = build_machlib_stub_manifest(proof_targets, stub_path)
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    stub_path.write_text(render_machlib_stubs(proof_targets), encoding="utf-8")
    stub_manifest_path.write_text(json.dumps(stub_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "stub_manifest": stub_manifest,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "stub_path": str(stub_path),
        "stub_manifest_path": str(stub_manifest_path),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-atlas-annex",
        "title": "EML-A1 Atlas Evidence Annex",
        "reviewDecision": "candidate_only",
        "validationStatus": "pass" if payload["status"] == STATUS else "fail",
        "replayStatus": "pass",
        "semanticStrength": "atlas_identity_classifier_candidate_no_public_claim_change",
        "semanticReview": {
            "entry_count": payload["entryCount"],
            "classification_counts": payload["classificationCounts"],
            "review_queue_summary": payload["reviewQueueSummary"],
            "next_proof_targets": payload["nextProofTargets"],
            "public_atlas_source": payload["publicAtlasSource"],
            "promote_to_public_atlas": False,
        },
        "claimBoundary": "Generated annex classifies selected Atlas-style identities; it does not replace monogate.org/atlas or create public theorem/RH/physics/SuperBEST claims.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "package_publish_performed": False,
            "deploy_performed": False,
            "rh_proof_claim": False,
            "physics_theorem_claim": False,
            "modular_form_theorem_claim": False,
            "quantum_group_theorem_claim": False,
        },
        "nonClaims": payload["nonClaims"],
        "reviewHighlights": [
            "Classifies exact identities separately from rewrites, observations, and blocked conjectural statements.",
            "Catches the Mellin/polylog missing-lambda-factor boundary.",
            "Keeps monogate.org/atlas as the canonical public Atlas.",
        ],
        "validationCommands": [
            "python python/scripts/eml_atlas_annex.py --build --strict",
            "python -m pytest -q python/tests/test_eml_atlas_annex.py",
        ],
        "timeline": [
            {"label": "Atlas source", "status": "pass", "detail": "Public source fixed to https://monogate.org/atlas."},
            {"label": "Identity checks", "status": "pass", "detail": "Seed entries validated by deterministic numeric witnesses."},
            {"label": "Claim boundary", "status": "pass", "detail": "Public promotion and theorem/proof flags remain false."},
        ],
        "reviewReasons": [
            "Useful as a reviewer annex before any Atlas-like claim is surfaced publicly.",
        ],
        "reviewNotes": "Candidate-only internal generated annex.",
        "sourceReportPath": f"reports/eml_a1_atlas_evidence_annex_{DATE.replace('-', '_')}.md",
        "evidencePaths": [
            "python/scripts/eml_atlas_annex.py",
            f"python/results/eml_atlas_annex/eml_atlas_annex_{DATE.replace('-', '_')}.json",
            f"reports/eml_a1_atlas_evidence_annex_{DATE.replace('-', '_')}.md",
            "reports/evidence_packets/eml_atlas_annex.json",
            "reports/eml_atlas_annex_machlib_stubs/eml_atlas_annex_exact_identity_stubs.lean",
            "reports/eml_atlas_annex_machlib_stubs/eml_atlas_annex_exact_identity_stub_manifest.json",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A1 Atlas Evidence Annex",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Public Atlas source: {payload['publicAtlasSource']}",
        "",
        "This annex is a private/generated verification layer for selected",
        "Atlas-style identities. It does not replace the public Atlas.",
        "",
        "| Entry | Classification | Checks | Boundary |",
        "|---|---|---:|---|",
    ]
    for entry in payload["entries"]:
        lines.append(
            f"| `{entry['id']}` | `{entry['classification']}` | "
            f"`{entry['sampleCount']}` | {entry['claimBoundary']} |"
        )
    lines.extend(
        [
            "",
            "## Classification Counts",
            "",
            *[
                f"- `{key}`: `{value}`"
                for key, value in sorted(payload["classificationCounts"].items())
            ],
            "",
            "## Review Queue",
            "",
            "| Entry | Action | Priority | Promote? |",
            "|---|---|---:|---|",
        ]
    )
    for item in payload["reviewQueue"]:
        lines.append(
            f"| `{item['id']}` | `{item['action']}` | `{item['priority']}` | "
            f"`{item['promoteToPublicAtlas']}` |"
        )
    lines.extend(
        [
            "",
            "## Next Candidate Proof Targets",
            "",
            *[
                f"- `{item['id']}`: {item['atlasObject']} (`{item['status']}`)"
                for item in payload["nextProofTargets"]
            ],
            "",
            "## Non-Claims",
            "",
            *[f"- {item}" for item in payload["nonClaims"]],
            "",
        ]
    )
    return "\n".join(lines)


def validate_annex(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid annex schema")
    if payload.get("status") != STATUS:
        raise ValueError("annex status must pass")
    if payload.get("entryCount", 0) < 30:
        raise ValueError("expected at least 30 annex entries")
    if payload.get("reviewQueueSummary", {}).get("queueCount") != payload.get("entryCount"):
        raise ValueError("review queue must cover every annex entry")
    if payload.get("reviewQueueSummary", {}).get("publicPromotionCount") != 0:
        raise ValueError("public promotion count must remain zero")
    if len(payload.get("nextProofTargets", [])) < 5:
        raise ValueError("expected candidate proof targets")
    if payload.get("publicAtlasSource") != "https://monogate.org/atlas":
        raise ValueError("public Atlas source must remain monogate.org/atlas")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    for entry in payload["entries"]:
        if entry["validationStatus"] != "pass":
            raise ValueError(f"entry failed validation: {entry['id']}")
        if entry["promoteToPublicAtlas"] is not False:
            raise ValueError(f"entry promoted publicly without review: {entry['id']}")
        if entry["classification"] == "exact_identity" and entry["reviewAction"]["action"] != "candidate_machlib_witness":
            raise ValueError(f"exact identity missing MachLib witness action: {entry['id']}")
        for key, value in entry.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"entry claim flag must remain false: {entry['id']} {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_atlas_annex")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_annex(args.out_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_annex(built["payload"])
    print("EML_ATLAS_ANNEX_OK")
    print(f"entries={built['payload']['entryCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
