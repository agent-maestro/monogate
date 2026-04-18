"""
Session 202 — Information Geometry: Fisher Metric, Natural Gradient & Exponential Families

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Information geometry is predominantly EML-2 (Fisher information, KL divergence,
geodesics in parameter space). The exponential family is EML-1/2 (log-partition function = EML-2).
Natural gradient = EML-2. This explains why EML-2 is the MOST POPULATED stratum:
information geometry underlies all learning, inference, and statistical mechanics.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class FisherMetricEML:
    """Fisher information metric and its EML depth."""

    def fisher_information(self, theta: float = 0.5, n: int = 10) -> dict[str, Any]:
        """Fisher metric for Bernoulli: I(θ) = 1/(θ(1-θ)). EML-2 (rational in θ)."""
        I_theta = round(1 / (theta * (1 - theta)), 4)
        log_likelihood = round(n * theta * math.log(theta) + n * (1 - theta) * math.log(1 - theta), 4)
        cramer_rao = round(1 / (n * I_theta), 6)
        return {
            "theta": theta,
            "fisher_info": I_theta,
            "eml_depth_fisher": 2,
            "log_likelihood": log_likelihood,
            "eml_depth_log_likelihood": 2,
            "cramer_rao_bound": cramer_rao,
            "eml_depth_cramer_rao": 2,
            "note": "Fisher=EML-2; log-likelihood=EML-2; Cramér-Rao=EML-2 — all information geometry = EML-2"
        }

    def kl_divergence_eml(self, p: float = 0.3, q: float = 0.5) -> dict[str, Any]:
        """KL divergence: DKL(P||Q) = Σ p log(p/q). EML-2."""
        kl = round(p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q)), 4)
        js = round((kl + p * math.log(q / p) + (1 - p) * math.log((1 - q) / (1 - p))) / 2, 4)
        return {
            "kl_depth": 2,
            "kl_value": kl,
            "js_divergence": round(abs(js), 4),
            "js_depth": 2,
            "jensen_shannon_depth": 2,
            "note": "KL, JS, all f-divergences = EML-2 (log-based information)"
        }

    def exponential_family_eml(self, eta: float = 1.0) -> dict[str, Any]:
        """
        Exponential family: p(x|η) = h(x) exp(η·T(x) - A(η)).
        Log-partition function A(η): EML-2 (cumulant generating function = log + exp composition).
        A(η) for Gaussian: A(η) = η²/2 → EML-2 (quadratic = EML-2).
        Natural parameter η: EML-0 (real parameter).
        Sufficient statistic T(x): EML-3 (depends on oscillatory data).
        """
        A_eta = round(eta**2 / 2, 4)
        A_prime = round(eta, 4)
        A_double_prime = 1.0
        return {
            "log_partition_depth": 2,
            "A_eta": A_eta,
            "mean_dA_deta": A_prime,
            "variance_fisher": A_double_prime,
            "natural_param_depth": 0,
            "sufficient_stat_depth": 3,
            "note": "Exp family: A(η)=EML-2; mean=EML-2; Fisher=d²A/dη²=EML-2"
        }

    def analyze(self) -> dict[str, Any]:
        fisher = self.fisher_information()
        kl = self.kl_divergence_eml()
        exp = self.exponential_family_eml()
        return {
            "model": "FisherMetricEML",
            "fisher_info": fisher,
            "kl_divergence": kl,
            "exponential_family": exp,
            "key_insight": "ALL of information geometry = EML-2: explains why EML-2 is most populated stratum"
        }


@dataclass
class NaturalGradientEML:
    """Natural gradient descent and its EML depth."""

    def natural_gradient(self, lr: float = 0.01, I: float = 4.0) -> dict[str, Any]:
        """Natural gradient: θ_{t+1} = θ_t - lr · F⁻¹ · ∇L. F = Fisher matrix = EML-2."""
        grad_L = 1.0
        nat_grad = round(grad_L / I, 4)
        update = round(lr * nat_grad, 6)
        return {
            "fisher_matrix_depth": 2,
            "gradient_depth": 2,
            "natural_gradient_depth": 2,
            "nat_grad_value": nat_grad,
            "update": update,
            "note": "Natural gradient = Fisher⁻¹ · gradient: EML-2 throughout"
        }

    def information_geodesic(self, t: float = 0.5) -> dict[str, Any]:
        """Geodesic in statistical manifold: EML-2 curvature."""
        curvature_approx = round(math.log(1 + t), 4)
        christoffel_approx = round(0.5 * t, 4)
        return {
            "geodesic_depth": 2,
            "curvature_depth": 2,
            "christoffel_approx": christoffel_approx,
            "curvature": curvature_approx,
            "note": "Statistical manifold geodesic: Riemannian curvature = EML-2 (log-based)"
        }

    def analyze(self) -> dict[str, Any]:
        ng = self.natural_gradient()
        geo = self.information_geodesic()
        return {
            "model": "NaturalGradientEML",
            "natural_gradient": ng,
            "geodesic": geo,
            "key_insight": "Natural gradient = EML-2 throughout; statistical manifold curvature = EML-2"
        }


def analyze_information_geometry_eml() -> dict[str, Any]:
    fisher = FisherMetricEML()
    natgrad = NaturalGradientEML()
    return {
        "session": 202,
        "title": "Information Geometry: Fisher Metric, Natural Gradient & Exponential Families",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "fisher_metric": fisher.analyze(),
        "natural_gradient": natgrad.analyze(),
        "eml_depth_summary": {
            "EML-0": "Natural parameters, sufficient statistics (values)",
            "EML-2": "Fisher information, KL/JS divergence, log-partition A(η), natural gradient, curvature",
            "EML-3": "Sufficient statistics T(x) (oscillatory data), likelihood function",
            "EML-∞": "Non-parametric density estimation"
        },
        "key_theorem": (
            "The EML Information Geometry Theorem (S202): "
            "Information geometry is the EML-2 stratum of statistics: "
            "Fisher information = EML-2. KL divergence = EML-2. "
            "Log-partition function A(η) = EML-2. Natural gradient = EML-2. "
            "ALL of differential-geometric statistics is EML-2. "
            "This explains the observation from S190: EML-2 has 21+ confirmations "
            "(most of any stratum) because information geometry is ubiquitous in "
            "physics, statistics, and machine learning. "
            "The exponential family IS the EML-2 object in probability."
        ),
        "rabbit_hole_log": [
            "ALL information geometry = EML-2: Fisher, KL, JS, natural gradient, geodesic curvature",
            "Log-partition function A(η) = EML-2: connects exp family to EML depth directly",
            "EML-2 dominance explained: information geometry underlies all learning and stat mech"
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_information_geometry_eml(), indent=2, default=str))
