"""
Session 231 — Direction D: EML-1 Class Characterization

EML operator: eml(x,y) = exp(x) - ln(y)
Direction D: Complete Stratum Characterization Theorem.
Core thesis: EML-1 = single exp-layer without paired normalization.
Every EML-1 object is an exponential function that has NOT been normalized/logged.
Contrast with EML-2 = exp + log paired = integration.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class EML1CatalogEML:
    """Complete catalog of EML-1 objects with primitive analysis."""

    def eml1_instances(self) -> dict[str, Any]:
        return {
            "partition_function_Z": {
                "expression": "Z = Σ exp(-βE_i)",
                "primitive": "exp (single)",
                "normalization": "NONE — Z itself is the unnormalized sum",
                "why_eml1": "Sum of exp terms; no log taken; not yet normalized to probability",
                "contrast": "F = -log(Z)/β is EML-2: here the log appears"
            },
            "ground_state_energy": {
                "expression": "E_0 ~ exp(-1/g) (non-perturbative)",
                "primitive": "exp (single)",
                "normalization": "NONE",
                "why_eml1": "Single exponential suppression; no log factor"
            },
            "bcs_gap": {
                "expression": "Δ ~ exp(-1/(N₀V))",
                "primitive": "exp (single)",
                "normalization": "NONE",
                "why_eml1": "Exponential gap; the Cooper pair binding energy"
            },
            "birkhoff_convergence": {
                "expression": "|time_avg - space_avg| ~ exp(-λN)",
                "primitive": "exp (single, with decay rate λ)",
                "normalization": "NONE — rate of approach, not a normalized quantity",
                "why_eml1": "Exponential convergence rate; no log"
            },
            "qec_threshold": {
                "expression": "P_logical ~ (p/p_th)^{2^k} exp-suppression",
                "primitive": "exp (single)",
                "normalization": "NONE",
                "why_eml1": "Exponential suppression of error below threshold"
            },
            "decoherence_factor": {
                "expression": "exp(-γt) coherence decay",
                "primitive": "exp (single)",
                "normalization": "NONE",
                "why_eml1": "Pure exponential decay; not yet integrated/logged"
            },
            "resolvent_decay": {
                "expression": "|(A-λ)^{-1}| ~ exp(-d(λ, spec(A)))",
                "primitive": "exp (single, of spectral distance)",
                "normalization": "NONE",
                "why_eml1": "Exponential decay away from spectrum"
            },
            "wigner_surmise": {
                "expression": "P(s) = (π/2)s exp(-πs²/4)",
                "primitive": "exp (single Gaussian)",
                "normalization": "PARTIAL — but the characteristic feature is the exp factor",
                "why_eml1": "Level-spacing distribution: exp factor dominates EML depth"
            }
        }

    def primitive_test(self) -> dict[str, Any]:
        """
        Formal test: an expression is EML-1 iff it contains exp as its OUTERMOST
        depth-increasing primitive, and does NOT contain log as an outer layer.
        EML-0: algebraic (no transcendentals).
        EML-1: exp(...) where ... is EML-0 or EML-1.
        EML-2: log(exp(...)) or exp(...)·normalization → log enters as paired partner.
        """
        test_cases = {
            "exp(-x)": {"depth": 1, "has_exp": True, "has_log": False, "result": "EML-1"},
            "exp(-x²)": {"depth": 1, "has_exp": True, "has_log": False, "result": "EML-1"},
            "-log(Z)/β": {"depth": 2, "has_exp": False, "has_log": True, "result": "EML-2"},
            "x²": {"depth": 0, "has_exp": False, "has_log": False, "result": "EML-0"},
            "cos(x)": {"depth": 3, "has_exp": True, "has_log": False, "result": "EML-3 (exp(ix) form)"},
            "log(∫exp(f)dμ)": {"depth": 2, "has_exp": True, "has_log": True, "result": "EML-2 (paired)"},
            "Σ exp(-βE_i)": {"depth": 1, "has_exp": True, "has_log": False, "result": "EML-1"},
        }
        return {
            "test_cases": test_cases,
            "rule": "EML-1 = exp without log; EML-2 = exp + log paired; EML-3 = exp(imaginary)",
            "key_distinction": "The log partner is what elevates EML-1 to EML-2"
        }

    def analyze(self) -> dict[str, Any]:
        inst = self.eml1_instances()
        test = self.primitive_test()
        return {
            "model": "EML1CatalogEML",
            "instances": inst,
            "primitive_test": test,
            "instance_count": len(inst),
            "common_property": "All EML-1 objects = single exp without normalization/log partner",
            "key_insight": "EML-1 = exp-only class; Z=EML-1 because log(Z) is taken to get F=EML-2"
        }


def analyze_eml1_class_eml() -> dict[str, Any]:
    catalog = EML1CatalogEML()
    return {
        "session": 231,
        "title": "Direction D: EML-1 Class Characterization",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "eml1_analysis": catalog.analyze(),
        "eml_depth_summary": {
            "EML-1_definition": "exp without log partner = single exponential primitive",
            "contrast_eml2": "EML-2 = exp + log paired (= integration = normalization)",
            "contrast_eml3": "EML-3 = exp(imaginary) = oscillatory extension"
        },
        "key_theorem": (
            "The EML-1 Class Theorem (S231, Direction D): "
            "EML-1 = the single exponential class: objects of the form exp(f) "
            "where f is EML-0 or EML-1, and no outer logarithm is applied. "
            "The KEY distinction from EML-2: in EML-2, exp and log appear TOGETHER "
            "(paired as ∫ = exp-sum + log-normalization). "
            "In EML-1, exp appears ALONE — no normalization, no log partner. "
            "Partition function Z = EML-1 precisely because log(Z) hasn't been taken yet. "
            "The moment you write F = -log(Z)/β, you're at EML-2. "
            "The transition Z → F is the canonical EML-1 → EML-2 step: adding the log partner."
        ),
        "rabbit_hole_log": [
            "Z=EML-1, F=EML-2: the partition function is the clearest EML-1→2 example",
            "EML-1 = exp alone; EML-2 = exp+log; the log partner is what creates the integration layer",
            "All exponential decays/growths without normalization = EML-1"
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_eml1_class_eml(), indent=2, default=str))
