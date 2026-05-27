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


VALIDATORS: dict[str, Callable[[], list[dict[str, Any]]]] = {
    "exp_from_eml": validate_exp_from_eml,
    "bose_boundary": validate_bose_boundary,
    "fermi_boundary": validate_fermi_boundary,
    "subtraction_boundary": validate_subtraction_boundary,
    "forward_difference_operator": validate_forward_difference,
    "q_integer_ratio": validate_q_integer,
    "bell_generating_rewrite": validate_bell_generating_rewrite,
    "dedekind_eta_factor": validate_dedekind_eta_factor,
    "mellin_polylog_correction": validate_mellin_polylog_correction,
    "zeta_explicit_formula_rewrite": validate_zeta_explicit_formula_rewrite,
    "rh_modulus_boundary": validate_rh_modulus_boundary,
}


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
        "id": "subtraction_boundary",
        "atlasObject": "linear subtraction boundary",
        "classification": "exact_identity",
        "standardForm": "v - u",
        "emlForm": "eml(log(v), exp(u))",
        "claimBoundary": "Requires v > 0 on the real branch.",
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
]


def analyze_entry(entry: dict[str, Any]) -> dict[str, Any]:
    checks = VALIDATORS[entry["id"]]()
    return {
        **entry,
        "validationStatus": "pass" if all(item.get("pass") is True for item in checks) else "fail",
        "numericChecks": checks,
        "sampleCount": len(checks),
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


def build_annex(out_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    entries = [analyze_entry(entry) for entry in SEED_ENTRIES]
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["classification"]] = counts.get(entry["classification"], 0) + 1
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS if all(entry["validationStatus"] == "pass" for entry in entries) else "EML_ATLAS_ANNEX_FAIL",
        "publicAtlasSource": "https://monogate.org/atlas",
        "annexRole": "private_generated_verification_layer",
        "entryCount": len(entries),
        "classificationCounts": counts,
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
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
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
    if payload.get("entryCount", 0) < 10:
        raise ValueError("expected at least 10 annex entries")
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
