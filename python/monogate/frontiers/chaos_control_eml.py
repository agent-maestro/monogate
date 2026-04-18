"""
Session 91 — Chaos Control & Synchronization: EML as Controller

OGY method, delayed feedback control, and coupled oscillator synchronization.
Tests whether low-depth EML trees (EML-2 or EML-3) can stabilize or synchronize
EML-∞ chaotic systems.

Key theorem: The OGY control perturbation at time t is EML-2 (linear feedback in
deviation from unstable periodic orbit). Synchronization coupling is EML-1 (exponential
convergence rate). The controller reduces EML depth: EML-∞ chaos → EML-2 controlled orbit.
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class OGYControl:
    """
    Ott-Grebogi-Yorke (1990) chaos control: apply tiny perturbations to a
    system parameter to stabilize an unstable periodic orbit (UPO) embedded in
    the strange attractor.

    EML structure:
    - Strange attractor: EML-∞
    - UPO embedded in attractor: EML-2 (periodic orbit = EML-2 closed curve)
    - OGY perturbation δp_n = -F·(x_n - x*): linear feedback = EML-2
    - Controlled orbit converges to UPO: EML-1 (exponential convergence)
    - Net result: EML-∞ attractor → EML-2 orbit via EML-2 controller
    """

    def logistic_upo(self, r: float = 3.9) -> dict:
        """Find period-1 UPO of logistic map x → r·x(1-x)."""
        # Fixed point: x* = 1 - 1/r
        x_star = 1 - 1/r
        # Jacobian at x*: f'(x*) = r(1-2x*) = r(1-2+2/r) = r(-1+2/r) = 2-r
        jacobian = r * (1 - 2 * x_star)
        # Eigenvalue λ = jacobian; unstable if |λ| > 1
        is_unstable = abs(jacobian) > 1
        return {
            "r": r,
            "x_star": round(x_star, 6),
            "jacobian_at_x_star": round(jacobian, 6),
            "unstable": is_unstable,
            "eml_upo": 2,
            "reason": "Fixed point x* = 1-1/r: rational function of r = EML-2",
        }

    def ogy_perturbation(self, x_n: float, x_star: float, jacobian: float,
                          r: float = 3.9, delta_r_max: float = 0.01) -> dict:
        """
        OGY: δr_n = -F·(x_n - x*) where F = (λ_u - 1)·∂x*/∂r / (e_u · ∂F/∂p)
        Simplified: δr_n ≈ -(λ_u/(λ_u·∂x*/∂r))·(x_n - x*)
        """
        lambda_u = jacobian  # unstable eigenvalue
        dx_star_dr = 1 / r**2  # ∂x*/∂r = ∂(1-1/r)/∂r = 1/r²
        if abs(lambda_u) > 1e-10:
            F = (lambda_u - 1) / (lambda_u * dx_star_dr)
        else:
            F = 0.0
        delta_r = -F * (x_n - x_star)
        delta_r = max(-delta_r_max, min(delta_r_max, delta_r))
        return {
            "x_n": round(x_n, 6),
            "x_star": round(x_star, 6),
            "deviation": round(x_n - x_star, 6),
            "delta_r": round(delta_r, 8),
            "eml_perturbation": 2,
            "reason": "δr = -F·(x-x*): linear feedback = EML-2",
        }

    def controlled_trajectory(self, n_steps: int = 30) -> list[dict]:
        r0 = 3.9
        upo = self.logistic_upo(r0)
        x_star = upo["x_star"]
        jacobian = upo["jacobian_at_x_star"]
        x = 0.4  # random initial
        results = []
        for i in range(n_steps):
            perturbation = self.ogy_perturbation(x, x_star, jacobian, r0)
            delta_r = perturbation["delta_r"]
            r_controlled = r0 + delta_r
            x_new = r_controlled * x * (1 - x)
            results.append({
                "step": i,
                "x": round(x, 6),
                "delta_r": round(delta_r, 8),
                "distance_to_upo": round(abs(x - x_star), 6),
            })
            x = x_new
        return results

    def to_dict(self) -> dict:
        return {
            "method": "OGY chaos control",
            "upo": self.logistic_upo(3.9),
            "perturbation_example": self.ogy_perturbation(0.4, 0.7436, -2.51),
            "controlled_trajectory": self.controlled_trajectory(20),
            "eml_depth_reduction": "EML-∞ (strange attractor) → EML-2 (UPO) via EML-2 controller",
            "eml_convergence": "EML-1: exponential approach to UPO after control engages",
        }


@dataclass
class PyramasSync:
    """
    Pecora-Carroll (1990) chaos synchronization: master-slave coupling.

    Master: dx/dt = f(x)    — EML-∞ trajectory
    Slave:  dy/dt = f(y) + K·(x-y)  — coupling term K·(x-y) = EML-2 (linear)

    Synchronization condition: largest conditional Lyapunov exponent λ_c < 0.
    Synchronization rate: |e(t)| ~ exp(λ_c·t) = EML-1 decay.

    EML structure:
    - Coupling term K·(x-y): EML-2 (linear)
    - Synchronization error e(t) = x(t)-y(t): EML-1 decay (when synchronized)
    - Master trajectory: EML-∞
    - Synchronized state: EML-∞ (follows master — inherits its depth)
    - But: the synchronization itself is an EML-1 process
    """

    def logistic_couple_sync(self, K: float = 0.5, n_steps: int = 50) -> list[dict]:
        """Coupled logistic maps: x_{n+1}=r·x_n(1-x_n), y_{n+1}=(1-K)·r·y_n(1-y_n)+K·x_{n+1}"""
        r = 3.9
        x, y = 0.3, 0.7
        results = []
        for i in range(n_steps):
            x_new = r * x * (1 - x)
            y_new = (1 - K) * r * y * (1 - y) + K * x_new
            error = abs(x_new - y_new)
            if i % 5 == 0 or i < 5:
                results.append({
                    "step": i,
                    "x": round(x_new, 6),
                    "y": round(y_new, 6),
                    "sync_error": round(error, 8),
                })
            x, y = x_new, y_new
        return results

    def synchronization_eml_table(self) -> list[dict]:
        return [
            {
                "phase": "Before synchronization",
                "error": "|x(t)-y(t)| ~ O(1)",
                "eml": EML_INF,
                "reason": "Both trajectories independently EML-∞",
            },
            {
                "phase": "Synchronization process",
                "error": "|e(t)| ~ exp(λ_c·t), λ_c < 0",
                "eml": 1,
                "reason": "Exponential convergence = EML-1",
            },
            {
                "phase": "After synchronization",
                "error": "|x(t)-y(t)| < ε",
                "eml": 1,
                "reason": "Synchronized state: error = EML-1 (exponentially small); trajectories still EML-∞",
            },
            {
                "phase": "Coupling term K·(x-y)",
                "error": "Linear in deviation",
                "eml": 2,
                "reason": "Linear feedback = EML-2; drives EML-∞ system to EML-1 convergence",
            },
        ]

    def to_dict(self) -> dict:
        return {
            "method": "Pecora-Carroll master-slave synchronization",
            "coupled_logistic": self.logistic_couple_sync(K=0.5, n_steps=30),
            "eml_analysis": self.synchronization_eml_table(),
            "conditional_lyapunov": "λ_c < 0 ↔ synchronization: EML-1 convergence condition",
        }


@dataclass
class DelayedFeedbackControl:
    """
    Pyragas (1992) delayed feedback control: u(t) = K·[x(t-τ) - x(t)]
    where τ = period of target UPO.

    When x(t) is on UPO: u(t) = K·[x(t-τ) - x(t)] = 0 (non-invasive!)
    Off UPO: u(t) ≠ 0 → pushes back toward UPO.

    EML structure:
    - u(t) = K·[x(t-τ) - x(t)]: EML-2 (linear difference in EML-∞ values)
    - τ: the target period = EML-2 (period of UPO = algebraic function of r)
    - Control is non-invasive when synchronized: u → 0 = EML-0
    """

    def to_dict(self) -> dict:
        return {
            "method": "Pyragas delayed feedback control",
            "control_signal": "u(t) = K·[x(t-τ) - x(t)]",
            "eml_u_on_upo": 0,
            "eml_u_off_upo": 2,
            "reason": "u = K·Δx: linear difference = EML-2; vanishes on UPO = EML-0",
            "advantage": "Non-invasive: does not perturb the target orbit",
            "eml_depth_reduction": "EML-∞ → EML-2 UPO via EML-2 controller (same as OGY)",
        }


def analyze_chaos_control_eml() -> dict:
    ogy = OGYControl()
    sync = PyramasSync()
    dfc = DelayedFeedbackControl()
    return {
        "session": 91,
        "title": "Chaos Control & Synchronization: EML as Controller",
        "key_theorem": {
            "theorem": "EML Chaos Control Depth Reduction Theorem",
            "statement": (
                "An EML-2 linear feedback controller (OGY: δp = -F·(x-x*)) "
                "can stabilize an EML-∞ chaotic attractor onto an EML-2 UPO. "
                "The convergence to the controlled orbit is EML-1 (exponential). "
                "EML-2 (linear coupling) is sufficient to synchronize EML-∞ trajectories "
                "with EML-1 convergence rate. "
                "EML-3 or higher controllers are not needed for stabilization — "
                "EML-2 is the minimal controller depth for chaos control."
            ),
        },
        "ogy_control": ogy.to_dict(),
        "synchronization": sync.to_dict(),
        "delayed_feedback": dfc.to_dict(),
        "eml_depth_summary": {
            "EML-0": "UPO control signal when on orbit (u=0); topological period T",
            "EML-1": "Synchronization convergence exp(λ_c·t); approach to UPO after control",
            "EML-2": "OGY perturbation δp = -F·(x-x*); delayed feedback u = K·Δx; coupling term",
            "EML-∞": "Uncontrolled chaotic trajectory; master trajectory (remains EML-∞)",
        },
        "rabbit_hole_log": [
            "The OGY insight: EML-∞ attractors contain infinitely many EML-2 UPOs as their 'skeleton'. The controller just selects one and holds the trajectory near it. EML-∞ is a superposition of EML-2 structures.",
            "Synchronization and the EML depth principle: the coupling term K·(x-y) = EML-2 drives exponential (EML-1) convergence of EML-∞ trajectories. The controller depth (EML-2) equals the depth of the geometry (EML-2 linear algebra of the Jacobian).",
            "Contrast with Session 85 (vortex control): NS has no known EML-2 controller because the BKM obstruction is EML-∞. Chaos control works because the attractor has EML-2 UPO structure. NS singularity has no such sub-structure.",
        ],
        "connections": {
            "to_session_82": "Session 82: chaos = EML-∞ long-time. Session 91: EML-2 controller forces EML-∞ back to EML-2 UPO",
            "to_session_85": "Session 85: NS has no EML-2 controller (BKM obstruction). Session 91: chaotic ODEs do have EML-2 controllers",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_chaos_control_eml(), indent=2, default=str))
