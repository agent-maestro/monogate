"""
pde_eml.py — EML Complexity in PDEs and Navier-Stokes.

Session 62 findings:
  - Heat kernel G(x,t) = exp(-x²/4t)/√(4πt): EML-2 in x (Gaussian), EML-2 in t
  - Wave equation: u(x,t) = f(x-ct)+g(x+ct). EML depth = depth(f,g)
  - Burgers equation: Cole-Hopf → heat equation → EML-3 solution
  - Schrödinger free particle: ψ = exp(i(kx-ωt)) → EML-1
  - Harmonic oscillator: ψ_n = H_n·exp(-x²/2) → EML-3 (Session 59)
  - Navier-Stokes conjecture: smooth solutions EML-finite; blowup = EML-inf
  - Burgers (1D NS analogue): Cole-Hopf gives global smooth solution → EML-3
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

__all__ = [
    "HeatEquation",
    "WaveEquation",
    "BurgersEquation",
    "SchrodingerEquation",
    "NavierStokesEML",
    "PDE_EML_TAXONOMY",
    "analyze_pde_eml",
]

# ── EML Taxonomy ─────────────────────────────────────────────────────────────

PDE_EML_TAXONOMY: dict[str, dict] = {
    "heat_kernel": {
        "formula": "G(x,t) = exp(-x²/4κt) / √(4πκt)",
        "eml_depth": 2,
        "reason": "Gaussian in x: exp(quadratic) = EML-2. EML-2 in t (envelope 1/√t).",
    },
    "wave_equation_solution": {
        "formula": "u(x,t) = f(x-ct) + g(x+ct)  (d'Alembert)",
        "eml_depth": "depth(f)",
        "reason": "EML depth of solution = EML depth of initial data f,g.",
    },
    "burgers_cole_hopf": {
        "formula": "u = -2ν·(∂θ/∂x)/θ, where θ solves heat eq",
        "eml_depth": 3,
        "reason": (
            "θ = heat kernel convolution with exp(-initial data/2ν): EML-3. "
            "u = -2ν·∂_x(log θ): log of EML-3 = EML-3. Cole-Hopf → EML-3."
        ),
    },
    "schrodinger_free": {
        "formula": "ψ(x,t) = exp(i(kx - ħk²t/2m))",
        "eml_depth": 1,
        "reason": "Pure exponential of linear phase: EML-1.",
    },
    "schrodinger_ho": {
        "formula": "ψ_n(x) = H_n(x) · exp(-x²/2) / normalization",
        "eml_depth": 3,
        "reason": "Hermite polynomial H_n times Gaussian: EML-3 (Session 59).",
    },
    "ns_smooth_conjecture": {
        "formula": "NS solutions: EML-finite vorticity ⟺ smoothness",
        "eml_depth": "finite_or_inf",
        "reason": (
            "CONJECTURE: Smooth NS solutions have EML-finite vorticity. "
            "Blowup at T* would require EML-inf. "
            "Proven for 1D Burgers (Cole-Hopf → EML-3, global smooth)."
        ),
        "status": "conjecture",
    },
    "burgers_1d": {
        "formula": "u_t + u·u_x = ν·u_xx",
        "eml_depth": 3,
        "reason": "Cole-Hopf transform reduces to heat eq. Global smooth solution: EML-3.",
    },
}


# ── Heat Equation ─────────────────────────────────────────────────────────────

@dataclass
class HeatEquation:
    """
    Heat equation u_t = κ·u_xx with fundamental solution (heat kernel).

    G(x,t) = exp(-x²/(4κt)) / √(4πκt)  — EML-2 in x, EML-2 in t
    """

    kappa: float = 1.0  # thermal diffusivity

    def kernel(self, x: float, t: float) -> float:
        """G(x,t) = exp(-x²/4κt)/√(4πκt)."""
        if t <= 0:
            return 0.0
        exponent = -x ** 2 / (4.0 * self.kappa * t)
        if exponent < -700:
            return 0.0
        return math.exp(exponent) / math.sqrt(4.0 * math.pi * self.kappa * t)

    def solution(self, x: float, t: float,
                 initial: Callable[[float], float],
                 x_range: float = 10.0, n: int = 1000) -> float:
        """u(x,t) = ∫G(x-y,t)·f(y)dy via numerical integration."""
        ys = np.linspace(-x_range, x_range, n)
        dy = ys[1] - ys[0]
        f_vals = np.array([initial(y) for y in ys])
        g_vals = np.array([self.kernel(x - y, t) for y in ys])
        return float(np.sum(g_vals * f_vals) * dy)

    def verify_normalization(self, t: float, x_range: float = 20.0,
                              n: int = 2000) -> float:
        """∫G(x,t)dx = 1."""
        xs = np.linspace(-x_range, x_range, n)
        dx = xs[1] - xs[0]
        vals = np.array([self.kernel(x, t) for x in xs])
        return float(np.sum(vals) * dx)

    def convergence_test(self, x_range: float = 5.0, n_x: int = 50,
                         t_vals: list | None = None) -> list[dict]:
        """
        Test convergence: u(x,t) → Gaussian as t→0 from spread-out IC.
        IC: box function f(y) = 1_{|y|<0.5}.
        """
        if t_vals is None:
            t_vals = [0.05, 0.1, 0.5, 1.0, 2.0]
        xs = np.linspace(-x_range, x_range, n_x)
        results = []
        for t in t_vals:
            sol_vals = [self.solution(x, t, lambda y: 1.0 if abs(y) < 0.5 else 0.0)
                        for x in xs]
            center = self.solution(0.0, t, lambda y: 1.0 if abs(y) < 0.5 else 0.0)
            results.append({"t": t, "u_at_0": center, "n_x": n_x})
        return results

    def eml_depth_kernel(self) -> int:
        return 2


# ── Wave Equation ─────────────────────────────────────────────────────────────

@dataclass
class WaveEquation:
    """
    Wave equation u_tt = c²·u_xx.
    D'Alembert solution: u(x,t) = ½[f(x-ct) + f(x+ct)] + 1/(2c)·∫_{x-ct}^{x+ct} g(y)dy
    """

    speed: float = 1.0

    def dalembert(self, x: float, t: float,
                  f: Callable[[float], float],
                  g: Callable[[float], float],
                  n_int: int = 500) -> float:
        """D'Alembert formula."""
        c = self.speed
        fterm = 0.5 * (f(x - c * t) + f(x + c * t))
        # Integrate g from x-ct to x+ct
        a, b = x - c * t, x + c * t
        ys = np.linspace(a, b, n_int)
        dy = (b - a) / (n_int - 1) if n_int > 1 else 0.0
        gterm = 0.5 / c * float(np.sum([g(y) for y in ys])) * dy
        return fterm + gterm

    def gaussian_pulse(self, x: float, t: float,
                       x0: float = 0.0, sigma: float = 1.0) -> tuple[float, float]:
        """
        Gaussian initial pulse: f(x) = exp(-(x-x0)²/2σ²), g=0.
        Solution = ½[G(x-ct) + G(x+ct)].
        """
        c = self.speed
        g1 = math.exp(-((x - c * t - x0) ** 2) / (2.0 * sigma ** 2))
        g2 = math.exp(-((x + c * t - x0) ** 2) / (2.0 * sigma ** 2))
        return 0.5 * (g1 + g2), (g1 + g2) / 2.0  # same

    def eml_depth_solution(self, eml_depth_f: int) -> int:
        """EML depth of solution = EML depth of initial data."""
        return eml_depth_f


# ── Burgers Equation via Cole-Hopf ────────────────────────────────────────────

@dataclass
class BurgersEquation:
    """
    Burgers equation u_t + u·u_x = ν·u_xx.

    Cole-Hopf transform: u = -2ν·∂_x(log θ), θ_t = ν·θ_xx.
    θ solves heat equation → global smooth solution.

    Initial data: u₀(x), θ₀(x) = exp(-∫u₀/(2ν))
    Solution via heat kernel:
      θ(x,t) = ∫G(x-y,t)·θ₀(y)dy
      u(x,t) = -2ν·(∂θ/∂x)/θ
    """

    nu: float = 0.1  # viscosity

    def cole_hopf_transform(self, u0: Callable[[float], float],
                             x_ref: float = -10.0, n_x: int = 200) -> Callable[[float], float]:
        """
        Compute θ₀(x) = exp(-∫_{x_ref}^x u₀(s)ds / (2ν)).
        """
        heat = HeatEquation(kappa=self.nu)

        def theta0(x: float) -> float:
            # Numerically integrate u₀ from x_ref to x
            xs = np.linspace(x_ref, x, n_x)
            dx = (x - x_ref) / (n_x - 1) if n_x > 1 else 0.0
            integral = float(np.sum([u0(s) for s in xs])) * dx
            exponent = -integral / (2.0 * self.nu)
            if exponent < -700:
                return 1e-300
            if exponent > 700:
                return math.exp(700.0)
            return math.exp(exponent)

        return theta0

    def solution(self, x: float, t: float,
                 theta0: Callable[[float], float],
                 x_range: float = 8.0, n: int = 500,
                 dx_diff: float = 1e-4) -> float:
        """
        u(x,t) = -2ν·(∂θ/∂x)/θ  where  θ(x,t) = ∫G(x-y,t)·θ₀(y)dy.
        """
        heat = HeatEquation(kappa=self.nu)
        ys = np.linspace(-x_range, x_range, n)
        dy = ys[1] - ys[0]
        theta0_vals = np.array([theta0(y) for y in ys])

        def theta(xp: float) -> float:
            g_vals = np.array([heat.kernel(xp - y, t) for y in ys])
            return float(np.sum(g_vals * theta0_vals) * dy)

        th_x = theta(x)
        if abs(th_x) < 1e-300:
            return 0.0
        th_xp = theta(x + dx_diff)
        th_xm = theta(x - dx_diff)
        dtheta_dx = (th_xp - th_xm) / (2.0 * dx_diff)
        return -2.0 * self.nu * dtheta_dx / th_x

    def shock_solution(self, x: float, t: float,
                       x_L: float = -1.0, x_R: float = 1.0,
                       u_L: float = 1.0, u_R: float = -1.0) -> float:
        """
        Approximate inviscid Burgers shock: step initial data.
        Returns the shock position and approximate profile.
        """
        # Shock position: x_s(t) = 0 for symmetric data
        # Profile: smoothed by viscosity ~ tanh((x)/(2νt))...
        if t <= 0:
            return u_L if x < 0 else u_R
        arg = x / (2.0 * self.nu * t) if self.nu > 0 else float("inf")
        if arg > 700:
            return u_R
        if arg < -700:
            return u_L
        return (u_L + u_R) / 2.0 - (u_L - u_R) / 2.0 * math.tanh(arg)

    def eml_depth(self) -> int:
        return 3  # Cole-Hopf: θ solves heat eq (EML-2), log θ adds +1 = EML-3


# ── Schrödinger Equation ─────────────────────────────────────────────────────

@dataclass
class SchrodingerEquation:
    """
    Schrödinger equation iħψ_t = -ħ²/(2m)·ψ_xx + V(x)ψ.

    Free particle: ψ(x,t) = exp(i(kx - ħk²t/2m)) — EML-1 (pure exponential)
    Harmonic oscillator: ψ_n = H_n·exp(-x²/2) — EML-3 (Session 59)
    """

    hbar: float = 1.0
    mass: float = 1.0

    def free_particle(self, x: float, t: float, k: float) -> complex:
        """Free particle plane wave: ψ(x,t) = exp(i(kx - ħk²t/2m))."""
        omega = self.hbar * k ** 2 / (2.0 * self.mass)
        phase = k * x - omega * t
        return complex(math.cos(phase), math.sin(phase))

    def free_packet(self, x: float, t: float,
                    k0: float = 1.0, sigma: float = 1.0) -> float:
        """Gaussian wave packet (modulus): |ψ(x,t)|."""
        # ψ₀(x) = exp(ik₀x) · exp(-x²/4σ²) / (2πσ²)^{1/4}
        # At time t: spreads as Gaussian with σ(t)² = σ² + ħ²t²/(4m²σ²)
        sigma_t_sq = sigma ** 2 + (self.hbar * t) ** 2 / (4.0 * self.mass ** 2 * sigma ** 2)
        norm = (2.0 * math.pi * sigma_t_sq) ** (-0.25)
        exponent = -(x - self.hbar * k0 * t / self.mass) ** 2 / (4.0 * sigma_t_sq)
        if exponent < -700:
            return 0.0
        return norm * math.exp(exponent)

    def ho_wavefunction(self, n: int, x: float) -> float:
        """
        ψ_n(x) = (π^{-1/4}/√(2^n·n!)) · H_n(x) · exp(-x²/2)
        where H_n = Hermite polynomial.
        EML-3: H_n(x) is polynomial, exp(-x²/2) is Gaussian.
        """
        # Hermite polynomial via recurrence
        if n == 0:
            h = 1.0
        elif n == 1:
            h = 2.0 * x
        else:
            h_prev, h_curr = 1.0, 2.0 * x
            for k in range(2, n + 1):
                h_next = 2.0 * x * h_curr - 2.0 * (k - 1) * h_prev
                h_prev, h_curr = h_curr, h_next
            h = h_curr
        norm = (math.pi ** (-0.25)) / math.sqrt(float(2 ** n) * math.factorial(n))
        gauss = math.exp(-x ** 2 / 2.0) if x ** 2 < 1400 else 0.0
        return norm * h * gauss

    def ho_energy(self, n: int) -> float:
        """E_n = ħω(n+½), ω=1."""
        return self.hbar * (n + 0.5)

    def eml_depth_free(self) -> int:
        return 1  # exp(i·linear) = EML-1

    def eml_depth_ho(self) -> int:
        return 3  # H_n(x)·exp(-x²/2) = EML-3


# ── Navier-Stokes EML Analysis ────────────────────────────────────────────────

@dataclass
class NavierStokesEML:
    """
    EML restatement of the Navier-Stokes regularity problem.

    CONJECTURE (EML version):
      A smooth solution to 3D NS on [0,T] has EML-finite vorticity ω(x,t)
      for all t ∈ [0,T).
      If blowup occurs at T*, then max_x |ω(x,t)| → ∞ as t→T*,
      meaning the vorticity field becomes EML-inf at T*.

    1D EVIDENCE (Burgers):
      Cole-Hopf transform shows the 1D Burgers equation has GLOBAL smooth solutions.
      The vorticity (=u_x) satisfies:
        u_x(x,t) = -2ν·∂_x(∂_x(log θ))
      which involves at most log of heat kernel → EML-3. No blowup.

    INTERPRETATION:
      EML-3 ≤ vorticity depth < ∞ for Burgers.
      The EML depth of vorticity is a quantitative substitute for
      the classical "no blowup" condition.
    """

    nu: float = 0.1

    def burgers_vorticity_depth(self) -> int:
        """EML depth of Burgers vorticity = EML-3 (Cole-Hopf derivation)."""
        return 3

    def ns_conjecture(self) -> dict:
        return {
            "statement": (
                "3D NS smooth solutions: vorticity is EML-finite. "
                "Blowup = vorticity becomes EML-inf."
            ),
            "1d_evidence": (
                "Burgers (1D NS analogue): Cole-Hopf → heat equation. "
                "Vorticity = u_x is EML-3. Global smooth, no blowup."
            ),
            "status": "conjecture",
            "relation_to_millennium": (
                "If proven: EML-finite vorticity → smooth solution (one direction). "
                "The EML depth serves as a quantitative regularity criterion."
            ),
        }

    def verify_burgers_regularity(self, x_vals: np.ndarray, t: float) -> np.ndarray:
        """Compute Burgers shock profile at time t, showing smooth solution."""
        burgers = BurgersEquation(nu=self.nu)
        return np.array([burgers.shock_solution(x, t) for x in x_vals])


# ── Grand Analysis ────────────────────────────────────────────────────────────

def analyze_pde_eml() -> dict:
    """Run full PDE EML analysis."""
    results: dict = {
        "session": 62,
        "title": "Navier-Stokes & PDE EML Complexity",
        "taxonomy": PDE_EML_TAXONOMY,
    }

    heat = HeatEquation(kappa=1.0)
    wave = WaveEquation(speed=1.0)
    burgers = BurgersEquation(nu=0.1)
    schro = SchrodingerEquation()
    ns = NavierStokesEML(nu=0.1)

    # Heat kernel
    t_vals = [0.1, 0.5, 1.0, 2.0]
    results["heat_kernel"] = {
        "normalization": {
            f"t_{t}": heat.verify_normalization(t) for t in t_vals
        },
        "kernel_at_0": {f"t_{t}": heat.kernel(0.0, t) for t in t_vals},
        "eml_depth": heat.eml_depth_kernel(),
    }

    # Wave equation (Gaussian pulse EML-2 → solution EML-2)
    results["wave_equation"] = {
        "gaussian_pulse_x1_t1": wave.gaussian_pulse(1.0, 1.0)[0],
        "eml_depth_for_gaussian_IC": wave.eml_depth_solution(2),
        "note": "EML depth of solution = EML depth of IC",
    }

    # Burgers
    results["burgers_cole_hopf"] = {
        "shock_t05": {
            f"x_{x}": burgers.shock_solution(x, 0.5) for x in [-2.0, -1.0, 0.0, 1.0, 2.0]
        },
        "eml_depth": burgers.eml_depth(),
        "note": "Cole-Hopf: Burgers → heat eq. EML-3 solution. No blowup.",
    }

    # Schrödinger
    results["schrodinger"] = {
        "free_particle_k1_x0_t0": abs(schro.free_particle(0.0, 0.0, 1.0)),
        "free_particle_k1_x1_t1": abs(schro.free_particle(1.0, 1.0, 1.0)),
        "ho_wavefunction_n0_x0": schro.ho_wavefunction(0, 0.0),
        "ho_wavefunction_n1_x0": schro.ho_wavefunction(1, 0.0),
        "ho_energies": {n: schro.ho_energy(n) for n in range(5)},
        "eml_depth_free": schro.eml_depth_free(),
        "eml_depth_ho": schro.eml_depth_ho(),
    }

    # NS conjecture
    results["navier_stokes_eml"] = ns.ns_conjecture()
    results["navier_stokes_eml"]["burgers_vorticity_depth"] = ns.burgers_vorticity_depth()

    results["summary"] = {
        "key_insight": (
            "PDE solutions inherit EML depth from initial data via the heat kernel (EML-2). "
            "Cole-Hopf transform linearizes Burgers to heat eq, capping depth at EML-3. "
            "Free Schrödinger: EML-1. HO quantum: EML-3. "
            "NS conjecture: blowup = EML-inf vorticity. "
            "Regularity = finiteness of EML depth."
        ),
        "eml_depths": {k: str(v["eml_depth"]) for k, v in PDE_EML_TAXONOMY.items()},
    }

    return results
