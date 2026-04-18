"""
session63_riemannian_eml.py — Session 63: Riemannian Geometry & GR EML.
"""

import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from monogate.frontiers.riemannian_eml import (
    SchwarzschildMetric,
    GeodesicEML,
    HawkingRadiation,
    GravitationalWaves,
    RiemannianEMLAnalysis,
    GR_EML_TAXONOMY,
    analyze_riemannian_eml,
)

DIVIDER = "=" * 70


def section1_schwarzschild() -> dict:
    print(DIVIDER)
    print("SECTION 1 — SCHWARZSCHILD METRIC: EML-2")
    print(DIVIDER)
    print("""
  ds² = -(1-2M/r)dt² + (1-2M/r)^{-1}dr² + r²dΩ²

  Components are RATIONAL functions of r → EML-2.
  Special radii (M=1, G=c=1):
    r_s = 2M = 2  (Schwarzschild radius / event horizon)
    r_ps = 3M = 3 (photon sphere)
    r_ISCO = 6M = 6 (innermost stable circular orbit)
""")
    metric = SchwarzschildMetric(mass=1.0)
    r_vals = [2.5, 3.0, 4.0, 6.0, 10.0, 20.0, 100.0]

    print(f"  r_s = {metric.schwarzschild_radius}")
    print(f"  Photon sphere r_ps = {metric.photon_sphere_radius()}")
    print(f"  ISCO r_ISCO = {metric.innermost_stable_orbit()}")

    print("\n  r       g_{tt}          g_{rr}")
    print("  -----   -----------     -----------")
    rows = []
    for r in r_vals:
        gtt = metric.g_tt(r)
        grr = metric.g_rr(r)
        print(f"  {r:5.1f}   {gtt:11.6f}   {grr:11.6f}")
        rows.append({"r": r, "g_tt": gtt, "g_rr": grr})

    return {
        "r_s": metric.schwarzschild_radius,
        "r_photon_sphere": metric.photon_sphere_radius(),
        "r_isco": metric.innermost_stable_orbit(),
        "metric_table": rows,
        "eml_depth": metric.eml_depth_metric(),
    }


def section2_christoffel() -> dict:
    print(DIVIDER)
    print("SECTION 2 — CHRISTOFFEL SYMBOLS: EML-2")
    print(DIVIDER)
    print("""
  Γ^ρ_{μν} = ½g^{ρσ}(∂_μg_{νσ}+∂_νg_{μσ}-∂_σg_{μν})

  For Schwarzschild:
    Γ^r_{tt} = M(r-2M)/r³   — rational in r → EML-2
    Γ^t_{tr} = M/(r(r-2M))  — rational in r → EML-2
    Γ^r_{rr} = -M/(r(r-2M)) — rational in r → EML-2

  Kretschner scalar K = 48M²/r⁶ → EML-inf at r=0.
""")
    metric = SchwarzschildMetric(mass=1.0)
    r_vals = [3.0, 4.0, 5.0, 6.0, 10.0]

    print("  r     Γ^r_tt      Γ^t_tr      Γ^r_rr      K=48/r⁶")
    print("  ---   ---------   ---------   ---------   --------")
    rows = []
    for r in r_vals:
        gr_tt = metric.christoffel_r_tt(r)
        gt_tr = metric.christoffel_t_tr(r)
        gr_rr = metric.christoffel_r_rr(r)
        K = metric.kretschner_scalar(r)
        print(f"  {r:3.0f}   {gr_tt:9.6f}   {gt_tr:9.6f}   {gr_rr:9.6f}   {K:.4f}")
        rows.append({"r": r, "Gamma_r_tt": gr_tt, "Gamma_t_tr": gt_tr,
                     "Gamma_r_rr": gr_rr, "K": K})

    # Show K → inf as r → 0
    print("\n  Kretschner scalar K(r) → ∞ as r → 0 (singularity, EML-inf):")
    sing_rows = []
    for r in [1.0, 0.5, 0.1, 0.05]:
        K = metric.kretschner_scalar(r)
        print(f"  r={r}: K = {K:.2e}")
        sing_rows.append({"r": r, "K": K})

    return {
        "christoffel_table": rows,
        "singularity": sing_rows,
        "eml_depth": 2,
        "eml_depth_singularity": "inf",
    }


def section3_geodesic() -> dict:
    print(DIVIDER)
    print("SECTION 3 — GEODESIC EQUATION: EML-2")
    print(DIVIDER)
    print("""
  ẍ^ρ + Γ^ρ_{μν}ẋ^μẋ^ν = 0

  EML depth = depth(Γ) = EML-2 for Schwarzschild.

  Key circular orbits (M=1):
    Photon sphere: r = 3M = 3
    ISCO (massive): r = 6M = 6

  Orbital period T = 2π√(r³/M) (Kepler-like).
""")
    metric = SchwarzschildMetric(mass=1.0)
    geodesic = GeodesicEML(metric=metric)

    r_ps = metric.photon_sphere_radius()
    r_isco = metric.innermost_stable_orbit()

    print(f"  Photon sphere: r_ps = {r_ps:.4f} M")
    print(f"  ISCO: r_ISCO = {r_isco:.4f} M")

    T_isco = geodesic.orbital_period(r_isco)
    T_r10 = geodesic.orbital_period(10.0)
    print(f"\n  Orbital periods:")
    print(f"  T(r=ISCO=6M) = {T_isco:.4f}")
    print(f"  T(r=10M) = {T_r10:.4f}")

    # Effective potential
    L_vals = [3.0, 3.46, 4.0, 5.0]
    r_range = np.linspace(3.0, 20.0, 50)
    print(f"\n  Effective potential V_eff(r) for L=3.46 (near ISCO):")
    veff_data = []
    for r in [4.0, 6.0, 8.0, 10.0, 15.0]:
        veff = geodesic.effective_potential(r, L=3.46)
        print(f"  r={r}: V_eff = {veff:.6f}")
        veff_data.append({"r": r, "V_eff": veff})

    return {
        "photon_sphere": r_ps,
        "isco": r_isco,
        "orbital_period_isco": T_isco,
        "orbital_period_r10": T_r10,
        "effective_potential": veff_data,
        "eml_depth": geodesic.eml_depth(),
    }


def section4_hawking() -> dict:
    print(DIVIDER)
    print("SECTION 4 — HAWKING TEMPERATURE: EML-1 (FORMULA) / EML-3 (DERIVATION)")
    print(DIVIDER)
    print("""
  T_H = ħc³/(8πGMk_B)  [SI units]
  T_H = 1/(8πM)          [geometric units G=c=ħ=k_B=1]

  FORMULA: T_H ∝ 1/M → EML-1 (rational in M)
  DERIVATION: Bogoliubov transformation near horizon involves
    thermal Green's functions similar to erf → EML-3.

  KEY EML INSIGHT: The final result can have LOWER EML depth than
  the derivation (cancellations and simplifications occur).
  T_H formula is EML-1; derivation is EML-3.
""")
    mass_vals = [0.5, 1.0, 2.0, 5.0, 10.0, 100.0]
    print("  M       T_H (geometric)  S_BH = 4πM²  t_evap/M³")
    print("  -----   --------------   -----------  ---------")
    rows = []
    for M in mass_vals:
        hw = HawkingRadiation(mass=M)
        T = hw.temperature()
        S = hw.entropy()
        t_ev = hw.evaporation_time()
        print(f"  {M:5.1f}   {T:.8f}   {S:11.4f}  {t_ev/M**3:.4f}")
        rows.append({"M": M, "T_H": T, "S_BH": S, "t_evap": t_ev})

    # Verify T_H = 1/(8πM)
    match = all(abs(r["T_H"] - 1.0/(8*math.pi*r["M"])) < 1e-14 for r in rows)
    print(f"\n  All T_H match 1/(8πM): {match}")

    # Solar mass black hole in SI
    M_sun = 2e30
    hw_si = HawkingRadiation(mass=1.0)
    T_sun_si = hw_si.temperature_si(M_sun)
    print(f"\n  Solar mass BH T_H (SI) ≈ {T_sun_si:.2e} K")

    return {
        "table": rows,
        "all_match_formula": match,
        "T_sun_si": T_sun_si,
        "eml_depth_formula": 1,
        "eml_depth_derivation": 3,
    }


def section5_gravitational_waves() -> dict:
    print(DIVIDER)
    print("SECTION 5 — GRAVITATIONAL WAVES: EML-2")
    print(DIVIDER)
    print("""
  h_{μν}(t,r) ∝ exp(iω(t-r/c)) / r

  Structure:
    exp(iωt): EML-1 carrier (pure exponential)
    1/r:      EML-2 (rational decay)
    Overall:  EML-2

  GW150914 parameters:
    M_chirp ≈ 30 M_sun, r ≈ 410 Mpc
    h ≈ 10^{-21} (dimensionless strain)
""")
    gw = GravitationalWaves(frequency=100.0)

    print("  h(t=0, r) — strain amplitude profile:")
    print("  r       |h| (arb. units)")
    rows = []
    for r in [1.0, 2.0, 5.0, 10.0]:
        h = abs(gw.strain(0.0, r, amplitude=1.0))
        print(f"  r={r}: {h:.6f}")
        rows.append({"r": r, "strain": h})

    # Verify 1/r decay
    h1 = abs(gw.strain(0.0, 1.0, 1.0))
    h2 = abs(gw.strain(0.0, 2.0, 1.0))
    ratio = h1 / h2
    print(f"\n  h(r=1)/h(r=2) = {ratio:.4f} (expected 2.0)")
    print(f"  Confirms 1/r decay: {abs(ratio - 2.0) < 0.01}")

    h_gw150914 = gw.strain_amplitude(0.0, 0.0, M_chirp=30.0, r_Mpc=410.0)
    print(f"\n  GW150914 strain estimate: h ≈ {h_gw150914:.2e}")

    # Chirp frequency evolution
    print("\n  Chirp frequency f(t) near merger (t_merger=10):")
    for dt in [5.0, 2.0, 1.0, 0.5, 0.1]:
        f = gw.chirp_frequency(10.0 - dt, 10.0)
        print(f"  Δt={dt}: f = {f:.4f}")

    return {
        "strain_profile": rows,
        "ratio_r1_r2": h1 / h2,
        "one_over_r_confirmed": abs(h1 / h2 - 2.0) < 0.01,
        "gw150914_strain": h_gw150914,
        "eml_depth": gw.eml_depth(),
    }


def main() -> None:
    print("\n" + DIVIDER)
    print("SESSION 63 — RIEMANNIAN GEOMETRY & GR EML COMPLEXITY")
    print(DIVIDER + "\n")

    results: dict = {"session": 63, "title": "Riemannian Geometry & GR EML Complexity"}

    results["section1_schwarzschild"] = section1_schwarzschild()
    results["section2_christoffel"] = section2_christoffel()
    results["section3_geodesic"] = section3_geodesic()
    results["section4_hawking"] = section4_hawking()
    results["section5_gravitational_waves"] = section5_gravitational_waves()

    full = analyze_riemannian_eml()
    results["taxonomy"] = full["taxonomy"]
    results["summary"] = full["summary"]

    print("\n" + DIVIDER)
    print("SUMMARY — EML DEPTHS IN GR")
    print(DIVIDER)
    print("""
  Flat metric (Minkowski):         EML-0  (constants)
  Schwarzschild metric:            EML-2  (rational in r)
  Christoffel symbols:             EML-2  (rational in r)
  Geodesic equation:               EML-2  (depth of Γ)
  Hawking T_H = 1/(8πM):          EML-1  (formula, inverse in M)
  Hawking derivation:              EML-3  (thermal Green's function)
  Gravitational waves:             EML-2  (exp-carrier × 1/r)
  Singularity at r=0:              EML-∞  (K=48M²/r⁶ diverges)
  Event horizon r_s = 2M:         EML-0  (coordinate value)

  KEY INSIGHT:
    GR curvature is EML-2 for smooth solutions.
    Physical singularities (r=0) are EML-inf.
    The Penrose singularity theorem predicts EML-inf formation
    under generic initial conditions with trapped surfaces.
""")

    out_path = Path(__file__).parent.parent / "results" / "session63_riemannian_eml.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
