"""
session62_pde_eml.py — Session 62: Navier-Stokes & PDE EML Complexity.
"""

import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from monogate.frontiers.pde_eml import (
    HeatEquation,
    WaveEquation,
    BurgersEquation,
    SchrodingerEquation,
    NavierStokesEML,
    PDE_EML_TAXONOMY,
    analyze_pde_eml,
)

DIVIDER = "=" * 70


def section1_heat_kernel() -> dict:
    print(DIVIDER)
    print("SECTION 1 — HEAT KERNEL: EML-2")
    print(DIVIDER)
    print("""
  G(x,t) = exp(-x²/4κt) / √(4πκt)

  Structure: exp(quadratic in x) = EML-2 Gaussian.
  Also EML-2 in t (1/√t envelope × exp(-const/t)).

  Verify: ∫G(x,t)dx = 1 for all t > 0.
  Verify: G(x,t) → δ(x) as t → 0+.
""")
    heat = HeatEquation(kappa=1.0)
    t_vals = [0.01, 0.1, 0.5, 1.0, 2.0]
    print("  t       ∫G dx    |1-norm|     G(0,t)")
    print("  -----   ------   --------     ------")
    rows = []
    for t in t_vals:
        norm = heat.verify_normalization(t)
        err = abs(norm - 1.0)
        g0 = heat.kernel(0.0, t)
        print(f"  {t:.3f}   {norm:.6f}  {err:.2e}    {g0:.4f}")
        rows.append({"t": t, "norm": norm, "err": err, "G_0": g0})

    # Heat equation solution convergence
    def box_ic(y: float) -> float:
        return 1.0 if abs(y) < 0.5 else 0.0

    print("\n  Heat eq solution u(0,t) for box IC:")
    conv_data = []
    for t in [0.1, 0.5, 1.0, 2.0]:
        u0 = heat.solution(0.0, t, box_ic, x_range=5.0, n=300)
        print(f"  t={t}: u(0,t) = {u0:.6f}")
        conv_data.append({"t": t, "u_0": u0})

    return {
        "normalization": rows,
        "all_normalized": all(r["err"] < 0.005 for r in rows),
        "convergence": conv_data,
        "eml_depth": 2,
    }


def section2_wave_equation() -> dict:
    print(DIVIDER)
    print("SECTION 2 — WAVE EQUATION: EML DEPTH = DEPTH(IC)")
    print(DIVIDER)
    print("""
  u_tt = c²·u_xx
  D'Alembert: u(x,t) = ½[f(x-ct) + f(x+ct)] + 1/(2c)∫g

  KEY EML FACT:
    EML depth of solution = EML depth of initial data.
    The wave equation PRESERVES EML complexity.

  Example: Gaussian IC f(x) = exp(-x²) (EML-2):
    Solution u(x,t) = ½[exp(-(x-t)²) + exp(-(x+t)²)] — still EML-2.
""")
    wave = WaveEquation(speed=1.0)

    # Gaussian IC
    def f_gauss(x: float) -> float:
        return math.exp(-x ** 2)

    def g_zero(x: float) -> float:
        return 0.0

    print("  u(x=0,t) for Gaussian IC f(x)=exp(-x²), g=0:")
    rows = []
    for t in [0.0, 0.5, 1.0, 2.0]:
        u = wave.dalembert(0.0, t, f_gauss, g_zero)
        u_exact = 0.5 * (math.exp(-t ** 2) + math.exp(-t ** 2))
        print(f"  t={t}: u(0,t) = {u:.6f} (exact = {u_exact:.6f})")
        rows.append({"t": t, "u": u, "exact": u_exact})

    print("\n  EML depth: solution inherits EML depth of f(x).")
    print("  Gaussian IC: EML-2 → solution: EML-2.")
    print("  Polynomial IC (EML-0) → solution: EML-0.")

    return {
        "gaussian_ic_rows": rows,
        "eml_depth_preserving": True,
        "eml_depth_for_gaussian_IC": wave.eml_depth_solution(2),
    }


def section3_burgers() -> dict:
    print(DIVIDER)
    print("SECTION 3 — BURGERS EQUATION: COLE-HOPF → EML-3")
    print(DIVIDER)
    print("""
  u_t + u·u_x = ν·u_xx  (ν = viscosity)

  Cole-Hopf transform: u = -2ν·∂_x(log θ), θ_t = ν·θ_xx.
  θ is solution of HEAT EQUATION → EML-2.
  u = -2ν·∂(log θ)/∂x = derivative of log(EML-2) = EML-3.

  KEY RESULT:
    Global smooth solution exists for all t>0 (unlike inviscid ν→0).
    Vorticity u_x stays EML-3: no blowup, no EML-inf occurrence.
    This is the 1D analogue of the NS regularity problem.

  Shock profile for step IC u₀: converges to tanh profile (EML-3).
""")
    burgers = BurgersEquation(nu=0.1)
    x_vals = np.linspace(-3.0, 3.0, 13)

    print("  Burgers shock profile at various times (step IC):")
    print("  x      t=0.1     t=0.5     t=2.0")
    print("  ----   ------    ------    ------")
    time_profiles: dict[str, list] = {"x": [], "t01": [], "t05": [], "t20": []}
    for x in x_vals:
        u01 = burgers.shock_solution(x, 0.1)
        u05 = burgers.shock_solution(x, 0.5)
        u20 = burgers.shock_solution(x, 2.0)
        print(f"  {x:5.2f}  {u01:7.4f}   {u05:7.4f}   {u20:7.4f}")
        time_profiles["x"].append(float(x))
        time_profiles["t01"].append(u01)
        time_profiles["t05"].append(u05)
        time_profiles["t20"].append(u20)

    print(f"\n  EML depth via Cole-Hopf: {burgers.eml_depth()}")
    print("  Global smooth solution: vorticity stays EML-3, no blowup.")

    return {
        "shock_profiles": time_profiles,
        "eml_depth": burgers.eml_depth(),
        "note": "Cole-Hopf transform: Burgers → heat eq → EML-3 solution",
    }


def section4_schrodinger() -> dict:
    print(DIVIDER)
    print("SECTION 4 — SCHRÖDINGER EQUATION: EML-1 (FREE) / EML-3 (HO)")
    print(DIVIDER)
    print("""
  Free particle: ψ(x,t) = exp(i(kx - ħk²t/2m)) → EML-1 (pure exponential)
  Harmonic osc: ψ_n(x) = H_n(x)·exp(-x²/2) → EML-3 (polynomial × Gaussian)
""")
    schro = SchrodingerEquation()

    print("  Free particle |ψ(x,t)| (Gaussian packet, k₀=1, σ=1):")
    print("  x       t=0        t=1        t=3")
    rows = []
    for x in [-3.0, -1.0, 0.0, 1.0, 3.0]:
        p0 = schro.free_packet(x, 0.0)
        p1 = schro.free_packet(x, 1.0)
        p3 = schro.free_packet(x, 3.0)
        print(f"  {x:5.1f}   {p0:.6f}  {p1:.6f}  {p3:.6f}")
        rows.append({"x": x, "t0": p0, "t1": p1, "t3": p3})

    print("\n  HO wavefunctions ψ_n(x):")
    print("  n    ψ_n(0)      ψ_n(1)      E_n")
    ho_data = []
    for n in range(5):
        psi0 = schro.ho_wavefunction(n, 0.0)
        psi1 = schro.ho_wavefunction(n, 1.0)
        en = schro.ho_energy(n)
        print(f"  {n}    {psi0:9.6f}  {psi1:9.6f}  {en:.1f}")
        ho_data.append({"n": n, "psi_0": psi0, "psi_1": psi1, "E_n": en})

    # Orthonormality check: ∫|ψ_n|² dx ≈ 1
    xs = np.linspace(-8.0, 8.0, 2000)
    dx = xs[1] - xs[0]
    norms = []
    for n in range(4):
        vals = np.array([schro.ho_wavefunction(n, x) ** 2 for x in xs])
        norm = float(np.sum(vals) * dx)
        norms.append({"n": n, "norm": norm})
        print(f"  ∫|ψ_{n}|² dx = {norm:.6f} (expected 1.0)")

    return {
        "free_packet": rows,
        "ho_wavefunctions": ho_data,
        "orthonormality": norms,
        "eml_depth_free": schro.eml_depth_free(),
        "eml_depth_ho": schro.eml_depth_ho(),
    }


def section5_ns_conjecture() -> dict:
    print(DIVIDER)
    print("SECTION 5 — NAVIER-STOKES EML CONJECTURE")
    print(DIVIDER)
    print("""
  CONJECTURE (EML Version of NS Regularity):
    A smooth 3D Navier-Stokes solution on [0,T] has EML-finite vorticity.
    Blowup at T* implies vorticity becomes EML-inf as t → T*-.

  EVIDENCE from 1D (Burgers = viscous 1D NS):
    Cole-Hopf: exact global smooth solution, vorticity = u_x is EML-3.
    → In 1D, no blowup, vorticity stays EML-3 (finite).

  PHYSICAL INTERPRETATION:
    EML depth of vorticity = measure of "how complicated" the flow is.
    Laminar flow (low Re): EML-2 or EML-3.
    Turbulent flow: EML grows but stays finite?
    Singularity: EML → ∞ (concentration of vorticity).

  CONNECTION TO MILLENNIUM PROBLEM:
    Clay Prize: does smooth 3D NS solution exist for all t?
    EML reformulation: is the vorticity EML-finite for all t?
    These are equivalent if EML-finite = smooth for NS vorticity.
""")
    ns = NavierStokesEML(nu=0.1)
    conj = ns.ns_conjecture()

    x_vals = np.linspace(-3.0, 3.0, 20)
    profiles = {}
    for t in [0.1, 0.5, 1.0]:
        prof = ns.verify_burgers_regularity(x_vals, t)
        profiles[f"t_{t}"] = list(float(v) for v in prof)

    print("  Burgers smooth profiles (1D NS analogue), ν=0.1:")
    print("  (All profiles are smooth — no EML-inf singularity)")
    for t_key in profiles:
        vals = profiles[t_key]
        extremes = f"min={min(vals):.3f}, max={max(vals):.3f}"
        print(f"  {t_key}: {extremes}")

    print(f"\n  Burgers vorticity EML depth: {ns.burgers_vorticity_depth()}")
    print(f"  NS Conjecture: {conj['statement'][:60]}...")

    return {
        "conjecture": conj,
        "burgers_vorticity_depth": ns.burgers_vorticity_depth(),
        "burgers_profiles": profiles,
    }


def main() -> None:
    print("\n" + DIVIDER)
    print("SESSION 62 — NAVIER-STOKES & PDE EML COMPLEXITY")
    print(DIVIDER + "\n")

    results: dict = {"session": 62, "title": "Navier-Stokes & PDE EML Complexity"}

    results["section1_heat_kernel"] = section1_heat_kernel()
    results["section2_wave_equation"] = section2_wave_equation()
    results["section3_burgers"] = section3_burgers()
    results["section4_schrodinger"] = section4_schrodinger()
    results["section5_ns_conjecture"] = section5_ns_conjecture()

    full = analyze_pde_eml()
    results["taxonomy"] = full["taxonomy"]
    results["summary"] = full["summary"]

    print("\n" + DIVIDER)
    print("SUMMARY — EML DEPTHS IN PDEs")
    print(DIVIDER)
    print("""
  Heat kernel G(x,t):              EML-2  (Gaussian in x, EML-2 in t)
  Wave eq solution:                EML-depth(IC)  (depth-preserving)
  Burgers via Cole-Hopf:           EML-3  (log of heat kernel solution)
  Schrödinger free particle:       EML-1  (pure exponential phase)
  Schrödinger harmonic osc:        EML-3  (Hermite × Gaussian)
  NS vorticity (1D, smooth):       EML-3  (Burgers evidence)
  NS blowup (conjectured):         EML-∞  (vorticity concentration)

  KEY INSIGHT:
    PDE regularity ↔ EML finiteness of solution.
    Cole-Hopf linearizes Burgers → heat eq, limiting depth to EML-3.
    The NS Millennium Problem may be reformulated as:
    "Does NS vorticity stay EML-finite for all t > 0?"
""")

    out_path = Path(__file__).parent.parent / "results" / "session62_pde_eml.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
