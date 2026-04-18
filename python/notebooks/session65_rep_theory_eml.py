"""
session65_rep_theory_eml.py — Session 65: Representation Theory & EML.
"""

import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from monogate.frontiers.rep_theory_eml import (
    U1Representation,
    SU2Character,
    WeylFormula,
    PeterWeyl,
    WignerD,
    REP_THEORY_EML_TAXONOMY,
    analyze_rep_theory_eml,
)

DIVIDER = "=" * 70


def section1_u1() -> dict:
    print(DIVIDER)
    print("SECTION 1 — U(1) REPRESENTATIONS: EML-1 ATOMS")
    print(DIVIDER)
    print("""
  U(1) = {e^{iθ}: θ ∈ [0,2π)}

  Irreducible representations: χ_n(e^{iθ}) = e^{inθ}  (n ∈ ℤ)
  Each is a PURE EML-1 ATOM: exp(i·integer·θ).

  This is the MOST FUNDAMENTAL example of EML-1 in representation theory.
  Peter-Weyl: L²(U(1)) = ⊕ ℂ·e^{inθ} — the Fourier basis is EML-1.
""")
    u1 = U1Representation()
    theta_vals = [0.0, math.pi / 6, math.pi / 4, math.pi / 2, math.pi]
    n_vals = [1, 2, 3, -1, 5]

    print("  θ          χ_1(e^{iθ})=e^{iθ}  χ_2=e^{2iθ}   χ_3=e^{3iθ}")
    rows = []
    for theta in theta_vals:
        c1 = u1.character(1, theta)
        c2 = u1.character(2, theta)
        c3 = u1.character(3, theta)
        print(f"  {theta:.4f}   ({c1.real:.4f},{c1.imag:.4f})  ({c2.real:.4f},{c2.imag:.4f})  ({c3.real:.4f},{c3.imag:.4f})")
        rows.append({"theta": theta, "chi_1": [c1.real, c1.imag],
                     "chi_2": [c2.real, c2.imag], "chi_3": [c3.real, c3.imag]})

    # Orthogonality: ∫χ_n·χ̄_m dθ/(2π) = δ_{nm}
    n_pts = 1000
    thetas = np.linspace(0, 2 * math.pi, n_pts, endpoint=False)
    dtheta = 2 * math.pi / n_pts
    chi_1 = np.array([u1.character(1, t) for t in thetas])
    chi_2 = np.array([u1.character(2, t) for t in thetas])
    ortho_12 = abs(float(np.sum(chi_1 * np.conj(chi_2)) * dtheta / (2 * math.pi)))
    ortho_11 = abs(float(np.sum(chi_1 * np.conj(chi_1)) * dtheta / (2 * math.pi)))
    print(f"\n  ∫χ_1·χ̄_1 dθ/(2π) = {ortho_11:.6f} (expected 1.0)")
    print(f"  ∫χ_1·χ̄_2 dθ/(2π) = {ortho_12:.6f} (expected 0.0)")
    print(f"  EML depth: {u1.eml_depth_character()} (EML-1 atoms!)")

    return {
        "characters": rows,
        "orthogonality_11": ortho_11,
        "orthogonality_12": ortho_12,
        "eml_depth": u1.eml_depth_character(),
    }


def section2_su2() -> dict:
    print(DIVIDER)
    print("SECTION 2 — SU(2) CHARACTERS: EML-3")
    print(DIVIDER)
    print("""
  SU(2) irreps: V_j for j = 0, 1/2, 1, 3/2, 2, ...
  Character: χ_j(θ) = sin((2j+1)θ) / sin(θ)
  At θ=0: χ_j(0) = dim(V_j) = 2j+1.

  EML depth: sin((2j+1)θ)/sin(θ) — ratio of EML-3 functions = EML-3.

  Weyl integration formula (Peter-Weyl orthogonality):
    ∫₀^π χ_j(θ)·χ_{j'}(θ)·sin²(θ)·dθ/(π/2) = δ_{jj'}
""")
    su2 = SU2Character()
    j_vals = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
    theta = math.pi / 4

    print(f"  θ = π/4 = {theta:.4f}")
    print("  j     χ_j(π/4)   dim=2j+1   Casimir j(j+1)")
    print("  ---   --------   --------   --------------")
    rows = []
    for j in j_vals:
        chi = su2.character(j, theta)
        dim = su2.dimension(j)
        casimir = su2.casimir_eigenvalue(j)
        print(f"  {j:.1f}   {chi:8.4f}   {dim:8d}   {casimir:14.4f}")
        rows.append({"j": j, "chi": chi, "dim": dim, "casimir": casimir})

    # Orthogonality check
    print("\n  Weyl integration (orthonormality check):")
    print("  j      ∫|χ_j|²·sin²·dθ/(π/2) = 1?")
    norms = []
    for j in [0.0, 0.5, 1.0, 1.5, 2.0]:
        norm = su2.weyl_integration(j)
        print(f"  j={j}: {norm:.6f} (expected 1.0)")
        norms.append({"j": j, "norm": norm})

    # Tensor product decomposition
    print("\n  Clebsch-Gordan: V_{j1} ⊗ V_{j2} = ⊕ V_j:")
    print(f"  V_{{1/2}} ⊗ V_{{1/2}} = {su2.decompose_tensor_product(0.5, 0.5)}")
    print(f"  V_1 ⊗ V_1 = {su2.decompose_tensor_product(1.0, 1.0)}")
    print(f"  V_1 ⊗ V_2 = {su2.decompose_tensor_product(1.0, 2.0)}")

    return {
        "characters": rows,
        "norms": norms,
        "cg_half_x_half": su2.decompose_tensor_product(0.5, 0.5),
        "cg_1_x_1": su2.decompose_tensor_product(1.0, 1.0),
        "eml_depth": su2.eml_depth(),
    }


def section3_weyl_formula() -> dict:
    print(DIVIDER)
    print("SECTION 3 — WEYL CHARACTER FORMULA: EML-1 NUMERATOR")
    print(DIVIDER)
    print("""
  χ_λ = Σ_{w∈W} (-1)^{ℓ(w)} e^{w(λ+ρ)} / Π_{α>0}(e^{α/2}-e^{-α/2})

  For SU(2): χ_j = (e^{i(j+1/2)·2θ} - e^{-i(j+1/2)·2θ}) / (e^{iθ}-e^{-iθ})
  = sin((2j+1)θ)/sin(θ)

  NUMERATOR: sum of EML-1 atoms (e^{iλ·θ} terms) → EML-1
  DENOMINATOR: single EML-1 expression (e^{iθ}-e^{-iθ} = 2i·sin θ)
  RATIO: EML-1/EML-1 → EML-1 (or EML-2 if non-trivial cancellation)
  But sin expression is EML-3, so the trig form appears EML-3.

  KEY INSIGHT:
    The Weyl formula shows that SU(2) characters are RATIOS of EML-1 sums.
    The EML-3 appearance (sin/sin) is the simplified trig form.
""")
    weyl = WeylFormula()
    su2 = SU2Character()

    # Compare Weyl formula character with direct character
    theta_vals = [0.1, math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2]
    j_vals = [0.5, 1.0, 1.5, 2.0]

    print("  j     θ         χ_j (Weyl)  χ_j (direct)  match")
    print("  ---   -------   ----------  ------------  -----")
    rows = []
    for j in j_vals:
        for theta in [math.pi / 4, math.pi / 3]:
            chi_weyl = weyl.character_su2(j, theta)
            chi_direct = su2.character(j, theta)
            match = abs(chi_weyl - chi_direct) < 1e-10
            print(f"  {j:.1f}   {theta:.4f}   {chi_weyl:.6f}  {chi_direct:.6f}  {match}")
            rows.append({"j": j, "theta": theta, "weyl": chi_weyl,
                         "direct": chi_direct, "match": match})

    print(f"\n  Weyl numerator EML depth: {weyl.eml_depth_numerator()} (EML-1)")
    print(f"  Character (trig form) EML depth: {weyl.eml_depth_character()} (EML-3)")

    return {
        "comparison": rows,
        "all_match": all(r["match"] for r in rows),
        "eml_depth_numerator": weyl.eml_depth_numerator(),
        "eml_depth_character": weyl.eml_depth_character(),
    }


def section4_peter_weyl() -> dict:
    print(DIVIDER)
    print("SECTION 4 — PETER-WEYL & PARSEVAL: EML-1 BASIS, EML-2 NORMS")
    print(DIVIDER)
    print("""
  Peter-Weyl: L²(G) = ⊕_λ V_λ ⊗ V_λ*
  For U(1): L²(U(1)) = ⊕_{n∈ℤ} ℂ·e^{inθ}  — EML-1 Fourier basis

  Parseval's theorem: ‖f‖²_{L²} = Σ_n |f̂(n)|²
  Both sides involve L² norms → EML-2.

  Test: step function f(θ) = 1 if θ<π, -1 if θ≥π.
  Fourier series: f̂(n) = 0 for even n, 2i/(nπ) for odd n → EML-1 coefficients.
""")
    pw = PeterWeyl()

    # Parseval check with step function
    f_step = lambda t: 1.0 if t < math.pi else -1.0
    parseval = pw.parseval_check(f_step, n_max=50)
    print(f"  Parseval check (step function, N_max=50):")
    print(f"  ‖f‖²_L² = {parseval['l2_norm_sq']:.6f}")
    print(f"  Σ|f̂(n)|² = {parseval['parseval_sum']:.6f}")
    print(f"  Relative error: {parseval['relative_error']:.4e}")
    print(f"  Match (< 0.01): {parseval['relative_error'] < 0.01}")

    # Fourier convergence
    f_smooth = lambda t: math.cos(t) + 0.5 * math.sin(2 * t)
    exact_val = f_smooth(math.pi / 4)
    conv = pw.fourier_convergence(f_smooth, math.pi / 4, [2, 5, 10, 20])
    print(f"\n  Fourier convergence for f(θ) = cos(θ) + ½sin(2θ) at θ=π/4:")
    print(f"  Exact value: {exact_val:.8f}")
    print("  N_max   Approximation  Error")
    for row in conv:
        print(f"  {row['n_max']:5d}   {row['approximation']:.8f}  {row['error']:.2e}")

    return {
        "parseval": parseval,
        "parseval_match": parseval["relative_error"] < 0.01,
        "fourier_convergence": conv,
        "eml_depth_basis": pw.eml_depth_basis(),
    }


def section5_wigner_d() -> dict:
    print(DIVIDER)
    print("SECTION 5 — WIGNER D-MATRICES: EML-3")
    print(DIVIDER)
    print("""
  D^j_{mm'}(α,β,γ) = e^{-imα} · d^j_{mm'}(β) · e^{-im'γ}

  Small-d matrix d^j_{mm'}(β): involves cos(β/2), sin(β/2) → EML-3.
  Full D-matrix: EML-1 (e^{imα}) × EML-3 (d^j) × EML-1 (e^{im'γ}) = EML-3.

  Physical role: rotation matrices for quantum angular momentum.
  SO(3): rotation by Euler angles (α,β,γ).
""")
    wd = WignerD()

    beta_vals = [0.0, math.pi / 6, math.pi / 4, math.pi / 2, math.pi]

    print("  Spin-1/2 d^{1/2}(β):")
    print("  β           [0,0]      [0,1]      [1,0]      [1,1]")
    d_rows = []
    for beta in [0.0, math.pi / 4, math.pi / 2, math.pi]:
        d = wd.d_half_spin(beta)
        print(f"  {beta:.4f}   {d[0,0]:9.4f}  {d[0,1]:9.4f}  {d[1,0]:9.4f}  {d[1,1]:9.4f}")
        d_rows.append({"beta": beta, "d_matrix": d.tolist()})

    # Verify unitarity
    print("\n  Unitarity check D†D = I:")
    for j, beta in [(0.5, math.pi/3), (0.5, math.pi/2), (1.0, math.pi/4)]:
        err = wd.unitarity_check(j, beta)
        print(f"  j={j}, β={beta:.3f}: max|D†D - I| = {err:.2e}")

    print(f"\n  EML depth: {wd.eml_depth()} (trig polynomials in β)")

    return {
        "d_half_matrices": d_rows,
        "unitarity_j_half_pi3": wd.unitarity_check(0.5, math.pi / 3),
        "unitarity_j_1_pi4": wd.unitarity_check(1.0, math.pi / 4),
        "eml_depth": wd.eml_depth(),
    }


def main() -> None:
    print("\n" + DIVIDER)
    print("SESSION 65 — REPRESENTATION THEORY & EML COMPLEXITY")
    print(DIVIDER + "\n")

    results: dict = {"session": 65, "title": "Representation Theory EML Complexity"}

    results["section1_u1"] = section1_u1()
    results["section2_su2"] = section2_su2()
    results["section3_weyl"] = section3_weyl_formula()
    results["section4_peter_weyl"] = section4_peter_weyl()
    results["section5_wigner_d"] = section5_wigner_d()

    full = analyze_rep_theory_eml()
    results["taxonomy"] = full["taxonomy"]
    results["summary"] = full["summary"]

    print("\n" + DIVIDER)
    print("SUMMARY — EML DEPTHS IN REPRESENTATION THEORY")
    print(DIVIDER)
    print("""
  U(1) characters χ_n = e^{inθ}:     EML-1  (pure EML-1 atoms!)
  SU(2) characters sin/sin:           EML-3  (trig ratio)
  Weyl formula numerator:             EML-1  (sum of EML-1 atoms)
  Wigner D-matrices:                  EML-3  (trig polynomials)
  Casimir eigenvalue j(j+1):          EML-0  (integer/algebraic)
  Weight lattice P:                   EML-0  (discrete)
  Peter-Weyl basis e^{inθ}:           EML-1
  Plancherel ‖f‖²=Σd_λ‖f̂‖²:         EML-2  (L² norms)

  KEY INSIGHT:
    Compact Lie group characters are built from EML-1 atoms (e^{iλ·θ}).
    The U(1) case shows Fourier analysis = EML-1 expansion.
    SU(2) characters sin/sin are EML-3 (trig simplification of EML-1 ratio).
    Representation theory = the algebraic structure that organizes EML-1 atoms.
""")

    out_path = Path(__file__).parent.parent / "results" / "session65_rep_theory_eml.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
