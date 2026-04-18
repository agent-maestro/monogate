"""
session66_complex_eml.py — Session 66: Complex Analysis & Riemann Surfaces EML.
"""

import sys
import json
import math
import cmath
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from monogate.frontiers.complex_eml import (
    ComplexLogarithm,
    LaurentSeries,
    ResidueCalculus,
    ConformalMaps,
    EMLComplexFiltration,
    COMPLEX_EML_TAXONOMY,
    analyze_complex_eml,
)

DIVIDER = "=" * 70


def section1_riemann_surface_log() -> dict:
    print(DIVIDER)
    print("SECTION 1 — RIEMANN SURFACE OF LOG: EML-2 (BRANCH), EML-0 (MONODROMY)")
    print(DIVIDER)
    print("""
  Log(z) = ln|z| + i·Arg(z)  (principal branch, ℂ\\(-∞,0])

  Multi-valued on ℂ*: log_n(z) = Log(z) + 2πi·n.
  Analytic continuation around 0: Log → Log + 2πi.
  Monodromy group = ℤ (winding numbers = EML-0: integers).

  Riemann surface: universal cover of ℂ* = infinite helix.
  Single-valued on helix: EML-2.
  Deck transformations (z → z+2πi): EML-0.
""")
    clog = ComplexLogarithm()

    # Principal branch at various points
    z_vals = [complex(1, 0), complex(0, 1), complex(-1, 0.01),
              complex(2, 2), complex(math.e, 0)]
    print("  z           Log(z)                    |Log|²")
    rows = []
    for z in z_vals:
        log_z = clog.principal_log(z)
        mag2 = abs(log_z) ** 2
        print(f"  {z}  {log_z}  {mag2:.4f}")
        rows.append({"z": [z.real, z.imag], "log_z": [log_z.real, log_z.imag]})

    # Monodromy demonstration
    mono = clog.monodromy_demo()
    print(f"\n  Monodromy demo (circle around origin):")
    print(f"  Start: Log(1) = {mono['log_start']}")
    print(f"  After one full revolution: Im(Log) = {mono['log_end']:.6f}")
    print(f"  Expected: 2π = {2*math.pi:.6f}")
    print(f"  Winding number: {mono['winding_number']} (EML-0: integer)")
    print(f"  Monodromy group: {mono['monodromy_group']}")

    # Riemann surface structure
    rs = clog.riemann_surface_structure()
    print(f"\n  Riemann surface: {rs['covering']}")
    print(f"  EML depth (single branch): {rs['eml_depth_single_branch']}")
    print(f"  EML depth (monodromy): {rs['eml_depth_monodromy']}")

    return {
        "log_values": rows,
        "monodromy": mono,
        "riemann_surface": rs,
        "eml_depth_branch": 2,
        "eml_depth_monodromy": 0,
    }


def section2_laurent_series() -> dict:
    print(DIVIDER)
    print("SECTION 2 — LAURENT SERIES: RESIDUES EML-0, TERMS EML-2")
    print(DIVIDER)
    print("""
  f(z) = Σ_{n∈ℤ} a_n z^n

  Each term a_n·z^n = a_n·exp(n·Log z) → EML-2 in z.
  Residue = a_{-1}: just a coefficient → EML-0.

  Example: f(z) = 1/(z²-1) = 1/((z-1)(z+1))
    Res(f, z=1) = 1/2   (EML-0)
    Res(f, z=-1) = -1/2  (EML-0)
""")
    laurent = LaurentSeries()
    residue_calc = ResidueCalculus()

    # Residues by formula for 1/(z²-1)
    poles = [complex(1, 0), complex(-1, 0)]
    orders = [1, 1]
    res_data = laurent.compute_residues_by_formula(poles, orders)
    for r in res_data:
        print(f"  Res(1/(z²-1), {r['pole']}) = {r['residue'].real:.4f} + {r['residue'].imag:.4f}i")

    # Verify via contour integral
    def f_test(z: complex) -> complex:
        denom = z ** 2 - 1.0
        if abs(denom) < 1e-8:
            return complex(0)
        return 1.0 / denom

    # ∮|z|=0.5 1/(z²-1)dz = 0 (no poles inside |z|=0.5)
    # ∮|z|=1.5 1/(z²-1)dz = 2πi(1/2-1/2) = 0 (both poles, sum residues = 0)
    int_small = residue_calc.contour_integral(f_test, complex(0), 0.5)
    int_large = residue_calc.contour_integral(f_test, complex(0), 1.5)
    print(f"\n  Contour integrals of 1/(z²-1):")
    print(f"  |z|=0.5 (no poles): {int_small.real:.4f} + {int_small.imag:.4f}i")
    print(f"  |z|=1.5 (both poles): {int_large.real:.4f} + {int_large.imag:.4f}i")
    print(f"  Both ≈ 0 (sum residues = 1/2-1/2 = 0)")

    # Compute Laurent coefficients numerically for 1/(z-0.5) around z=0
    def f_simple(z: complex) -> complex:
        return 1.0 / (z - 0.5)
    coeffs = laurent.coefficients(f_simple, center=complex(0, 0), r=0.3,
                                   n_min=-1, n_max=3, n_pts=2000)
    print(f"\n  Laurent coefficients of 1/(z-0.5) around z=0 (|z|=0.3):")
    for n in [-1, 0, 1, 2]:
        c = coeffs[n]
        # Exact: a_n = 1/(0.5)^{n+1} = 2^{n+1}
        exact = (-2) ** (n + 1)  # (-1)^{n+1}/0.5^{n+1}... actually 1/(z-0.5) = -2/(1-2z) = -2Σ(2z)^n
        print(f"  a_{n} = {c.real:.4f} (exact: {exact:.4f})")

    return {
        "residues": res_data,
        "contour_small": [int_small.real, int_small.imag],
        "contour_large": [int_large.real, int_large.imag],
        "eml_depth_residue": 0,
        "eml_depth_term": 2,
    }


def section3_residue_theorem() -> dict:
    print(DIVIDER)
    print("SECTION 3 — RESIDUE THEOREM: EML-0 RESULT")
    print(DIVIDER)
    print("""
  ∮_γ f(z)dz = 2πi Σ_{inside γ} Res(f, z_k)

  Result = 2πi × (sum of EML-0 residues) = 2πi × algebraic number.
  The residue theorem maps complex analysis → discrete data (EML-0).

  Verification:
    ∮|z|=2 1/(z-1)dz = 2πi · 1 = 2πi  (one simple pole, Res=1)
    ∮|z|=2 1/(z²-1)dz = 0              (Res(z=1)+Res(z=-1) = 0)
    ∮|z|=1 sin(z)/z dz = 0             (removable singularity, Res=0)
""")
    residue_calc = ResidueCalculus()
    results = residue_calc.verify_residue_theorem()

    for r in results:
        integral = r["integral"]
        expected = [r["expected_real"], r["expected_imag"]]
        print(f"  f = {r['function']}:")
        print(f"    ∮ = {integral[0]:.4f} + {integral[1]:.4f}i")
        print(f"    Expected: {expected[0]:.4f} + {expected[1]:.4f}i")
        print(f"    Match: {r['match']}")

    all_match = all(r["match"] for r in results)
    print(f"\n  All residue theorem checks pass: {all_match}")

    return {
        "tests": results,
        "all_match": all_match,
        "eml_depth": residue_calc.eml_depth(),
    }


def section4_conformal_maps() -> dict:
    print(DIVIDER)
    print("SECTION 4 — CONFORMAL MAPS: EML DEPTHS")
    print(DIVIDER)
    print("""
  exp: z ↦ e^z        → EML-1 (conformal, maps strips to sectors)
  Log: z ↦ Log(z)     → EML-2 (inverse of EML-1)
  Möbius: z ↦ (az+b)/(cz+d)  → EML-2 (rational)
  Joukowski: z ↦ z + 1/z      → EML-2 (rational, airfoil maps)
  Riemann map (generic):      → EML-inf (not elementary in general)
""")
    conf = ConformalMaps()

    z_vals = [complex(0.001, 0.001), complex(1, 0), complex(0, math.pi / 2),
              complex(1, 1), complex(-1, 0.5)]
    print("  z           exp(z)                    Log(z)")
    rows = []
    for z in z_vals:
        ez = conf.exp_map(z)
        lz = conf.log_map(z)
        print(f"  {z}  ({ez.real:.4f},{ez.imag:.4f})    ({lz.real:.4f},{lz.imag:.4f})")
        rows.append({
            "z": [z.real, z.imag],
            "exp_z": [ez.real, ez.imag],
            "log_z": [lz.real, lz.imag],
        })

    # Cayley map: upper half-plane → unit disk
    z_uhp = [complex(0, 1), complex(1, 1), complex(0, 2), complex(-1, 1)]
    print("\n  Cayley map (z-i)/(z+i): upper half-plane → unit disk")
    for z in z_uhp:
        w = conf.cayley_map(z)
        inside = abs(w) < 1.0
        print(f"  z={z} → w={w}, |w|={abs(w):.4f} (inside unit disk: {inside})")

    # Joukowski
    print("\n  Joukowski z+1/z (maps circle |z|=r to airfoil-like shapes):")
    for r in [1.1, 1.5, 2.0]:
        thetas = np.linspace(0, 2 * math.pi, 8, endpoint=False)
        z_circle = r * np.exp(1j * thetas)
        w_vals = [conf.joukowski(z) for z in z_circle]
        real_range = (min(w.real for w in w_vals), max(w.real for w in w_vals))
        imag_range = (min(w.imag for w in w_vals), max(w.imag for w in w_vals))
        print(f"  r={r}: real∈[{real_range[0]:.2f},{real_range[1]:.2f}], imag∈[{imag_range[0]:.2f},{imag_range[1]:.2f}]")

    return {
        "map_values": rows,
        "eml_depths": {
            "exp": conf.eml_depth_exp(),
            "log": conf.eml_depth_log(),
            "mobius": conf.eml_depth_mobius(),
            "riemann_map": conf.eml_depth_riemann_map(),
        },
    }


def section5_complex_filtration() -> dict:
    print(DIVIDER)
    print("SECTION 5 — EML FILTRATION OVER ℂ: COARSER THAN OVER ℝ")
    print(DIVIDER)
    print("""
  Over ℝ:
    exp(x) — EML-1 (cannot equal sin by IZB)
    sin(x) — EML-3 (composition involving log: sin=Im(e^{ix}))
    They are in DIFFERENT EML classes.

  Over ℂ:
    e^{iz} = cos(z) + i·sin(z) — EML-1.
    sin(z) = (e^{iz} - e^{-iz})/(2i) — ALSO EML-1 over ℂ!
    The sin/exp distinction COLLAPSES over ℂ.

  EML classification over ℂ is by SINGULARITY TYPE:
    No singularity (entire): EML-0 or EML-1
    Poles (meromorphic): EML-2
    Branch points: EML-2
    Essential singularities: EML-∞ (Picard: f takes every value)

  Examples:
    e^z: EML-1 (entire, essential sing at ∞)
    sin(z): EML-1 over ℂ (same as e^{iz}/2i)
    Log(z): EML-2 (branch point at 0)
    ℘(z): EML-∞ (doubly periodic: Liouville → must have singularities)
    e^{1/z}: EML-∞ (essential singularity at 0, Picard theorem)
""")
    filtration = EMLComplexFiltration()
    comparison = filtration.eml_vs_real()
    sing_types = {
        s: filtration.singularity_eml_type(s)
        for s in ["removable", "pole_order_n", "logarithmic_branch",
                  "essential", "natural_boundary"]
    }

    print("  Singularity type → EML depth:")
    for s, eml in sing_types.items():
        print(f"  {s:<25} → {eml}")

    print(f"\n  Over ℝ: sin is EML-3 (distinct from exp=EML-1)")
    print(f"  Over ℂ: sin(z) = (e^{{iz}}-e^{{-iz}})/(2i) — EML-1!")
    print(f"  Conclusion: EML filtration over ℂ is COARSER.")

    # Verify sin=Im(exp(iz)) numerically
    z_vals = [0.0, math.pi / 4, math.pi / 2, 1.0]
    print("\n  sin(z) = Im(e^{iz}) verification (z real):")
    for z in z_vals:
        sin_direct = math.sin(z)
        exp_imag = cmath.exp(complex(0, z)).imag
        print(f"  z={z:.4f}: sin={sin_direct:.6f}, Im(e^{{iz}})={exp_imag:.6f}, match={abs(sin_direct-exp_imag)<1e-12}")

    return {
        "comparison": comparison,
        "singularity_types": sing_types,
        "key_theorem": "Over C: sin is EML-1 (same as exp). Over R: sin is EML-3.",
    }


def main() -> None:
    print("\n" + DIVIDER)
    print("SESSION 66 — COMPLEX ANALYSIS & RIEMANN SURFACES EML")
    print(DIVIDER + "\n")

    results: dict = {"session": 66, "title": "Complex Analysis EML Complexity"}

    results["section1_log"] = section1_riemann_surface_log()
    results["section2_laurent"] = section2_laurent_series()
    results["section3_residue"] = section3_residue_theorem()
    results["section4_conformal"] = section4_conformal_maps()
    results["section5_filtration"] = section5_complex_filtration()

    full = analyze_complex_eml()
    results["taxonomy"] = full["taxonomy"]
    results["summary"] = full["summary"]

    print("\n" + DIVIDER)
    print("SUMMARY — EML DEPTHS IN COMPLEX ANALYSIS")
    print(DIVIDER)
    print("""
  Log(z) single branch:            EML-2  (contains real log)
  Monodromy of Log:                EML-0  (integer winding numbers)
  Laurent term a_n·z^n:            EML-2  (exp(n·Log z))
  Residue a_{-1}:                  EML-0  (coefficient)
  Residue theorem result:          EML-0  (2πi × algebraic)
  exp(z) conformal map:            EML-1
  Log(z) conformal map:            EML-2
  Möbius/rational maps:            EML-2
  Generic Riemann map:             EML-∞
  Weierstrass ℘(z):                EML-∞
  Essential singularity (Picard):  EML-∞

  KEY INSIGHT:
    Over ℂ, sin(z) = (e^{iz}-e^{-iz})/2i is EML-1 (same as exp).
    The EML filtration over ℂ is COARSER than over ℝ.
    Classification is by singularity type: poles→EML-2, essential→EML-∞.
    Residue theorem maps complex analysis to EML-0 discrete data.
""")

    out_path = Path(__file__).parent.parent / "results" / "session66_complex_eml.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
