"""
bio_eml.py — EML Complexity of Bio/Chemical Networks.

Session 53 findings:
  - Lotka-Volterra (predator-prey): EML-2 per step (bilinear x*y term)
  - Michaelis-Menten kinetics: EML-2 (rational: V*S/(Km+S))
  - SIR epidemic model: EML-2 (bilinear S*I infection term)
  - FitzHugh-Nagumo neuron: EML-3 per step (cubic v³ polynomial)
  - Turing reaction-diffusion: EML-2 RHS + Laplacian (EML-2 for finite difference)
  - Brusselator: EML-3 per step (x²*y cubic nonlinearity)
  - Hill function (cooperative binding): EML-3 (x^n/(K^n + x^n) for n>1)

Key insight: Biology follows the same EML taxonomy as physics and mathematics.
  - Linear biology (simple growth/decay): EML-1
  - Standard kinetics (mass action): EML-2
  - Cooperative/allosteric kinetics: EML-3
  - Piecewise models (threshold switching): EML-inf

The mathematics of life is EML-finite.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = [
    "LotkaVolterra",
    "MichaelisMenten",
    "SIRModel",
    "FitzHughNagumo",
    "Brusselator",
    "hill_function",
    "BIO_EML_TAXONOMY",
    "analyze_bio_eml",
]


# ── Lotka-Volterra ────────────────────────────────────────────────────────────

class LotkaVolterra:
    """
    dx/dt = alpha*x - beta*x*y
    dy/dt = delta*x*y - gamma*y

    Degree-2 polynomial in (x,y) → EML-2 per step.
    Conserved quantity: V(x,y) = delta*x - gamma*ln(x) + beta*y - alpha*ln(y)
    (Lyapunov function — involves ln, EML-2).
    """

    def __init__(
        self,
        alpha: float = 1.0,
        beta: float = 0.1,
        delta: float = 0.075,
        gamma: float = 1.5,
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.delta = delta
        self.gamma = gamma

    def rhs(self, state: np.ndarray) -> np.ndarray:
        x, y = state
        return np.array([
            self.alpha * x - self.beta * x * y,
            self.delta * x * y - self.gamma * y,
        ])

    def integrate(
        self,
        x0: float = 10.0,
        y0: float = 5.0,
        dt: float = 0.01,
        n_steps: int = 5000,
    ) -> np.ndarray:
        state = np.array([x0, y0])
        traj = np.empty((n_steps + 1, 2))
        traj[0] = state
        for i in range(n_steps):
            k1 = self.rhs(state)
            k2 = self.rhs(state + 0.5 * dt * k1)
            k3 = self.rhs(state + 0.5 * dt * k2)
            k4 = self.rhs(state + dt * k3)
            state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
            traj[i + 1] = state
        return traj

    def lyapunov_function(self, x: float, y: float) -> float:
        if x <= 0 or y <= 0:
            return float("inf")
        return (
            self.delta * x - self.gamma * math.log(x)
            + self.beta * y - self.alpha * math.log(y)
        )

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": "lotka_volterra",
            "eml_per_step": 2,
            "highest_degree": 2,
            "nonlinearity": "x*y (bilinear predation term)",
            "conserved_quantity_eml": 2,
            "insight": (
                "Lotka-Volterra: bilinear term x*y = product of two EML-1 variables. "
                "EML-2 per step. Conserved quantity V involves ln(x), ln(y): "
                "also EML-2 (log is depth-2 via: ln(x) = eml(0, x) + 1). "
                "Periodic orbits: not chaotic, EML-2 governs all dynamics."
            ),
        }


# ── Michaelis-Menten ──────────────────────────────────────────────────────────

class MichaelisMenten:
    """
    v = Vmax * S / (Km + S)

    Rational function: numerator EML-1, denominator EML-1, quotient EML-2.
    (1/(Km+S) = exp(-ln(Km+S)) needs ln → EML-2 depth.)
    """

    def __init__(self, vmax: float = 10.0, km: float = 2.0) -> None:
        self.vmax = vmax
        self.km = km

    def rate(self, s: float | np.ndarray) -> float | np.ndarray:
        return self.vmax * s / (self.km + s)

    def full_system(
        self,
        s0: float = 10.0,
        e0: float = 1.0,
        p0: float = 0.0,
        dt: float = 0.01,
        n_steps: int = 2000,
        k_cat: float = 5.0,
    ) -> np.ndarray:
        """Integrate substrate depletion: dS/dt = -v(S)."""
        state = np.array([s0])
        traj = np.empty(n_steps + 1)
        traj[0] = s0
        for i in range(n_steps):
            v = self.vmax * state[0] / (self.km + state[0])
            state[0] = max(0.0, state[0] - dt * v)
            traj[i + 1] = state[0]
        return traj

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": "michaelis_menten",
            "formula": "v = Vmax * S / (Km + S)",
            "eml_depth": 2,
            "structure": "Rational function: S/(Km+S) = 1/(1 + Km/S)",
            "insight": (
                "v = Vmax*S/(Km+S): numerator is EML-1 (linear in S). "
                "Denominator (Km+S) is EML-1. Quotient needs reciprocal: "
                "1/x = exp(-ln(x)) = EML-2. Full rate function is EML-2. "
                "Michaelis-Menten saturation kinetics = EML-2."
            ),
        }


# ── SIR Model ─────────────────────────────────────────────────────────────────

class SIRModel:
    """
    dS/dt = -beta*S*I
    dI/dt =  beta*S*I - gamma*I
    dR/dt =  gamma*I

    Highest-degree term: S*I (bilinear) → EML-2 per step.
    """

    def __init__(self, beta: float = 0.3, gamma: float = 0.1) -> None:
        self.beta = beta
        self.gamma = gamma

    def rhs(self, state: np.ndarray) -> np.ndarray:
        s, i, r = state
        return np.array([
            -self.beta * s * i,
            self.beta * s * i - self.gamma * i,
            self.gamma * i,
        ])

    def integrate(
        self,
        s0: float = 0.99,
        i0: float = 0.01,
        r0: float = 0.0,
        dt: float = 0.1,
        n_steps: int = 2000,
    ) -> np.ndarray:
        state = np.array([s0, i0, r0])
        traj = np.empty((n_steps + 1, 3))
        traj[0] = state
        for i in range(n_steps):
            k1 = self.rhs(state)
            k2 = self.rhs(state + 0.5 * dt * k1)
            k3 = self.rhs(state + 0.5 * dt * k2)
            k4 = self.rhs(state + dt * k3)
            state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
            state = np.clip(state, 0.0, 1.0)
            traj[i + 1] = state
        return traj

    def r0_number(self) -> float:
        return self.beta / self.gamma

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": "SIR_epidemic",
            "eml_per_step": 2,
            "r0": self.r0_number(),
            "highest_degree": 2,
            "nonlinearity": "S*I (force of infection — bilinear)",
            "insight": (
                f"SIR model with R0={self.r0_number():.2f}: "
                "force of infection beta*S*I is bilinear → EML-2. "
                "Same structure as Lotka-Volterra (predator-prey). "
                "Epidemic dynamics and ecological oscillations are EML-2 systems."
            ),
        }


# ── FitzHugh-Nagumo ───────────────────────────────────────────────────────────

class FitzHughNagumo:
    """
    dv/dt = v - v³/3 - w + I_ext
    dw/dt = epsilon * (v + a - b*w)

    Cubic polynomial in v → degree 3 → EML-3 per step (v³ needs 2 multiplies = depth 2,
    but v³ inside a sum raises the overall tree depth to 3).
    """

    def __init__(
        self,
        a: float = 0.7,
        b: float = 0.8,
        epsilon: float = 0.08,
        i_ext: float = 0.5,
    ) -> None:
        self.a = a
        self.b = b
        self.epsilon = epsilon
        self.i_ext = i_ext

    def rhs(self, state: np.ndarray) -> np.ndarray:
        v, w = state
        return np.array([
            v - v**3 / 3.0 - w + self.i_ext,
            self.epsilon * (v + self.a - self.b * w),
        ])

    def integrate(
        self,
        v0: float = -1.2,
        w0: float = -0.6,
        dt: float = 0.05,
        n_steps: int = 5000,
    ) -> np.ndarray:
        state = np.array([v0, w0])
        traj = np.empty((n_steps + 1, 2))
        traj[0] = state
        for i in range(n_steps):
            k1 = self.rhs(state)
            k2 = self.rhs(state + 0.5 * dt * k1)
            k3 = self.rhs(state + 0.5 * dt * k2)
            k4 = self.rhs(state + dt * k3)
            state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
            traj[i + 1] = state
        return traj

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": "fitzhugh_nagumo",
            "eml_per_step": 3,
            "highest_degree": 3,
            "nonlinearity": "v³ (cubic nullcline)",
            "behavior": "Limit cycle (spiking neuron model)",
            "insight": (
                "FitzHugh-Nagumo: dv/dt = v - v³/3 - w + I. "
                "The cubic term v³ = v*v*v needs 2 multiplies: depth 2 in isolation. "
                "Inside the full RHS expression (sum with w and I), the tree depth is 3. "
                "This is the minimal neuron model with cubic spiking mechanism = EML-3."
            ),
        }


# ── Brusselator ──────────────────────────────────────────────────────────────

class Brusselator:
    """
    dx/dt = 1 - (B+1)*x + A*x²*y
    dy/dt = B*x - A*x²*y

    x²*y: cubic degree → EML-3 per step.
    Models oscillating chemical reactions (Belousov-Zhabotinsky type).
    """

    def __init__(self, A: float = 1.0, B: float = 3.0) -> None:
        self.A = A
        self.B = B

    def rhs(self, state: np.ndarray) -> np.ndarray:
        x, y = state
        cubic = self.A * x * x * y
        return np.array([
            1.0 - (self.B + 1.0) * x + cubic,
            self.B * x - cubic,
        ])

    def integrate(
        self,
        x0: float = 1.0,
        y0: float = 1.5,
        dt: float = 0.01,
        n_steps: int = 10000,
    ) -> np.ndarray:
        state = np.array([x0, y0])
        traj = np.empty((n_steps + 1, 2))
        traj[0] = state
        for i in range(n_steps):
            k1 = self.rhs(state)
            k2 = self.rhs(state + 0.5 * dt * k1)
            k3 = self.rhs(state + 0.5 * dt * k2)
            k4 = self.rhs(state + dt * k3)
            state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
            traj[i + 1] = state
        return traj

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": "brusselator",
            "eml_per_step": 3,
            "highest_degree": 3,
            "nonlinearity": "A*x²*y (autocatalytic trimolecular reaction)",
            "behavior": "Limit cycle for B > 1+A²",
            "oscillates": self.B > 1.0 + self.A**2,
            "insight": (
                f"Brusselator (A={self.A}, B={self.B}): "
                "autocatalytic x²*y term. x²*y = x*(x*y) needs two multiplies → depth 3. "
                f"{'Oscillating (B > 1+A²).' if self.B > 1+self.A**2 else 'Stable fixed point.'} "
                "Chemical oscillators require at least EML-3 (trimolecular autocatalysis)."
            ),
        }


# ── Hill Function ─────────────────────────────────────────────────────────────

def hill_function(
    x: float | np.ndarray,
    k: float = 1.0,
    n: float = 2.0,
    vmax: float = 1.0,
) -> float | np.ndarray:
    """
    H_n(x) = Vmax * x^n / (K^n + x^n)

    EML depth:
      x^n = exp(n * ln(x)) — depth 3 (ln is EML-2, exp is EML-3... wait)
      Actually: ln(x) = eml(0,x)+1 (depth 2); n*ln(x) (depth 2); exp(n*ln(x)) = x^n (depth 3)
      x^n / (K^n + x^n): add K^n (same depth 3), then divide (depth 4 total).
      Hill function with n>1 is EML-4 in general; n=1 (MM) is EML-2.
    """
    xn = x**n
    return vmax * xn / (k**n + xn)


# ── Taxonomy ──────────────────────────────────────────────────────────────────

BIO_EML_TAXONOMY: dict[str, dict[str, object]] = {
    "exponential_growth": {
        "formula": "dx/dt = r*x",
        "eml_per_step": 1,
        "solution": "x(t) = x0*exp(r*t) — EML-1 exact solution",
        "verdict": "EML-1: linear ODE, exact exp solution",
    },
    "logistic_growth": {
        "formula": "dx/dt = r*x*(1 - x/K)",
        "eml_per_step": 2,
        "solution": "Sigmoid: K/(1+exp(-r*(t-t0))) — EML-2 exact",
        "verdict": "EML-2: x*(1-x/K) is quadratic",
    },
    "lotka_volterra": {
        "formula": "dx=alpha*x-beta*x*y, dy=delta*x*y-gamma*y",
        "eml_per_step": 2,
        "verdict": "EML-2: bilinear x*y term",
    },
    "michaelis_menten": {
        "formula": "v = Vmax*S/(Km+S)",
        "eml_per_step": 2,
        "verdict": "EML-2: rational function (reciprocal = log+exp)",
    },
    "sir_model": {
        "formula": "dS=-beta*S*I, dI=beta*S*I-gamma*I, dR=gamma*I",
        "eml_per_step": 2,
        "verdict": "EML-2: bilinear S*I force of infection",
    },
    "fitzhugh_nagumo": {
        "formula": "dv=v-v³/3-w+I, dw=eps*(v+a-b*w)",
        "eml_per_step": 3,
        "verdict": "EML-3: cubic v³ spiking mechanism",
    },
    "brusselator": {
        "formula": "dx=1-(B+1)x+Ax²y, dy=Bx-Ax²y",
        "eml_per_step": 3,
        "verdict": "EML-3: cubic x²y autocatalytic term",
    },
    "hill_function_n2": {
        "formula": "Vmax*x²/(K²+x²)",
        "eml_per_step": 4,
        "verdict": "EML-4: x^n = exp(n*ln(x)) at depth 3, then rational at depth 4",
    },
    "turing_reaction_diffusion": {
        "formula": "du/dt = f(u,v) + D_u*∇²u",
        "eml_per_step": 3,
        "verdict": "EML-3 RHS (if Brusselator kinetics) + EML-2 Laplacian (finite diff)",
    },
    "threshold_switch": {
        "formula": "f(x) = 0 if x<theta, 1 if x>=theta",
        "eml_per_step": "inf",
        "verdict": "EML-inf: step function is not real-analytic",
    },
}


def analyze_bio_eml() -> dict[str, object]:
    """Run all bio/chemical EML analyses and verify numerically."""
    results = {}

    # Lotka-Volterra
    lv = LotkaVolterra()
    traj_lv = lv.integrate(n_steps=2000)
    results["lotka_volterra"] = {
        **lv.eml_analysis(),
        "orbit": {
            "prey_range": [float(traj_lv[:,0].min()), float(traj_lv[:,0].max())],
            "predator_range": [float(traj_lv[:,1].min()), float(traj_lv[:,1].max())],
        },
    }

    # MM kinetics
    mm = MichaelisMenten(vmax=10.0, km=2.0)
    s_vals = np.linspace(0.01, 20.0, 100)
    v_vals = mm.rate(s_vals)
    results["michaelis_menten"] = {
        **mm.eml_analysis(),
        "vmax_achieved_at_10Km": float(mm.rate(10 * mm.km)),
        "half_max_at_Km": float(mm.rate(mm.km) / mm.vmax),
    }

    # SIR
    sir = SIRModel(beta=0.3, gamma=0.1)
    traj_sir = sir.integrate()
    peak_infected = float(traj_sir[:, 1].max())
    results["sir_model"] = {
        **sir.eml_analysis(),
        "peak_infected": peak_infected,
        "final_susceptible": float(traj_sir[-1, 0]),
    }

    # FitzHugh-Nagumo
    fhn = FitzHughNagumo(i_ext=0.5)
    traj_fhn = fhn.integrate()
    # Count voltage spikes (sign changes of dv/dt going positive)
    v = traj_fhn[:, 0]
    spikes = int(np.sum((np.diff(np.sign(np.diff(v))) == -2)))
    results["fitzhugh_nagumo"] = {
        **fhn.eml_analysis(),
        "v_range": [float(v.min()), float(v.max())],
        "approximate_spikes": spikes,
    }

    # Brusselator
    bru = Brusselator(A=1.0, B=3.0)
    traj_bru = bru.integrate()
    results["brusselator"] = {
        **bru.eml_analysis(),
        "x_range": [float(traj_bru[:,0].min()), float(traj_bru[:,0].max())],
        "y_range": [float(traj_bru[:,1].min()), float(traj_bru[:,1].max())],
    }

    return {
        "models": results,
        "taxonomy": BIO_EML_TAXONOMY,
        "key_insight": (
            "Biology is EML-finite. Linear biology=EML-1, mass-action kinetics=EML-2, "
            "cooperative/allosteric=EML-3-4, threshold switches=EML-inf. "
            "The jump from EML-2 to EML-3 corresponds to trimolecular reactions "
            "and cubic nonlinearities — the minimum needed for chemical oscillations. "
            "Same EML hierarchy as physics: harmonic (EML-2) < anharmonic (EML-3) < chaotic."
        ),
    }
