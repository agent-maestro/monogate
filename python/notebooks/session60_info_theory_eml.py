"""
session60_info_theory_eml.py — Session 60: Information Theory & EML Complexity.
"""

import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from monogate.frontiers.info_theory_eml import (
    ShannonEntropy,
    KLDivergence,
    FisherInformation,
    MutualInformation,
    ExponentialFamily,
    RateDistortion,
    INFO_THEORY_EML_TAXONOMY,
    analyze_info_theory_eml,
)

DIVIDER = "=" * 70


def section1_entropy() -> dict:
    print(DIVIDER)
    print("SECTION 1 — SHANNON ENTROPY: EML-2")
    print(DIVIDER)
    print("""
  H(X) = -Σ p·log p
  Each term p·log(p) contains log (EML-2 atom) → H is EML-2.

  Key entropies:
    Gaussian  N(μ,σ²): h = ½·log(2πeσ²)     — EML-2
    Bernoulli Ber(p):  H = -p·log p - (1-p)·log(1-p) — EML-2
    Poisson   Pois(λ): H ≈ ½·log(2πeλ) for large λ  — EML-2
    Exponential Exp(λ): h = 1 - log(λ)       — EML-2
""")
    se = ShannonEntropy()
    h_gauss_1 = se.entropy_gaussian(1.0)
    h_gauss_2 = se.entropy_gaussian(2.0)
    h_bern_half = se.entropy_bernoulli(0.5)
    h_pois_1 = se.entropy_poisson(1.0)
    h_pois_5 = se.entropy_poisson(5.0)
    h_exp_1 = se.entropy_exponential(1.0)

    print(f"  h(N(0,1))    = {h_gauss_1:.6f}  (expected {0.5*math.log(2*math.pi*math.e):.6f})")
    print(f"  h(N(0,4))    = {h_gauss_2:.6f}")
    print(f"  H(Ber(0.5))  = {h_bern_half:.6f}  (expected {math.log(2):.6f})")
    print(f"  H(Pois(1))   ≈ {h_pois_1:.6f}")
    print(f"  H(Pois(5))   ≈ {h_pois_5:.6f}")
    print(f"  h(Exp(1))    = {h_exp_1:.6f}  (expected 1.0)")
    print(f"  EML depth = {se.eml_depth()}")

    return {
        "h_gaussian_sigma1": h_gauss_1,
        "h_gaussian_sigma2": h_gauss_2,
        "h_bernoulli_half": h_bern_half,
        "h_bernoulli_half_expected": math.log(2),
        "h_poisson_lam1": h_pois_1,
        "h_poisson_lam5": h_pois_5,
        "h_exponential_lam1": h_exp_1,
        "eml_depth": 2,
    }


def section2_kl_divergence() -> dict:
    print(DIVIDER)
    print("SECTION 2 — KL DIVERGENCE: EML-2")
    print(DIVIDER)
    print("""
  D_KL(P‖Q) = Σ p·log(p/q) = Σ p·(log p - log q)
  Both log p and log q are EML-2 → KL is EML-2.

  KEY VERIFICATION:
    KL(N(0,1)‖N(μ,1)) = μ²/2  (exact closed form, EML-2 in μ)
""")
    kl = KLDivergence()
    mu_vals = [0.5, 1.0, 2.0, 3.0]
    print("  μ      KL (computed)   μ²/2 (formula)   match")
    print("  ----   ------------   --------------   -----")
    all_match = True
    rows = []
    for mu in mu_vals:
        computed = kl.kl_gaussian_standard(mu)
        formula = mu ** 2 / 2.0
        match = abs(computed - formula) < 1e-12
        if not match:
            all_match = False
        print(f"  {mu:.1f}    {computed:.8f}   {formula:.8f}   {match}")
        rows.append({"mu": mu, "computed": computed, "formula": formula, "match": match})

    # Discrete KL
    p = np.array([0.5, 0.3, 0.2])
    q = np.array([0.4, 0.4, 0.2])
    kl_disc = kl.kl_discrete(p, q)
    print(f"\n  KL([0.5,0.3,0.2]‖[0.4,0.4,0.2]) = {kl_disc:.6f}")
    print(f"  All Gaussian KL matches: {all_match}")

    return {
        "gaussian_kl_rows": rows,
        "all_gaussian_match": all_match,
        "discrete_kl_example": kl_disc,
        "eml_depth": 2,
    }


def section3_fisher_information() -> dict:
    print(DIVIDER)
    print("SECTION 3 — FISHER INFORMATION: EML-2")
    print(DIVIDER)
    print("""
  I(θ) = E[(∂log p/∂θ)²] = -E[∂²log p/∂θ²]
  Since log p is EML-2, ∂log p/∂θ is EML-2, squaring preserves depth.

  KEY: Fisher info for Gaussian location: I(μ) = 1/σ²
  Cramér-Rao: Var(μ̂) ≥ σ² (any unbiased estimator)
""")
    fi = FisherInformation()
    sigma_vals = [0.5, 1.0, 2.0, 3.0]
    print("  σ      I(μ) computed   1/σ² formula   match")
    print("  ----   ------------   ------------   -----")
    rows = []
    for s in sigma_vals:
        computed = fi.fisher_gaussian_mu(s)
        formula = 1.0 / s ** 2
        match = abs(computed - formula) < 1e-14
        print(f"  {s:.1f}    {computed:.8f}   {formula:.8f}   {match}")
        rows.append({"sigma": s, "I_mu": computed, "formula_1_over_sigma2": formula, "match": match})

    cr_sigma1 = fi.cramer_rao_bound(fi.fisher_gaussian_mu(1.0))
    print(f"\n  Cramér-Rao bound (σ=1): Var ≥ {cr_sigma1:.6f} = 1/I(μ) = σ²")
    print(f"  EML depth = {fi.eml_depth()}")

    return {
        "fisher_rows": rows,
        "cramer_rao_sigma1": cr_sigma1,
        "fisher_bernoulli_half": fi.fisher_bernoulli(0.5),
        "fisher_poisson_lam1": fi.fisher_poisson(1.0),
        "eml_depth": 2,
    }


def section4_mutual_information() -> dict:
    print(DIVIDER)
    print("SECTION 4 — MUTUAL INFORMATION: EML-2")
    print(DIVIDER)
    print("""
  I(X;Y) = H(X) + H(Y) - H(X,Y) = EML-2 - EML-2 = EML-2
  For bivariate Gaussian with correlation ρ:
    I(X;Y) = -½·log(1-ρ²)  — EML-2 in ρ
""")
    mi = MutualInformation()
    rho_vals = [0.0, 0.3, 0.5, 0.7, 0.9, 0.99]
    print("  ρ       I(X;Y)")
    print("  -----   -------")
    rows = []
    for rho in rho_vals:
        val = mi.mi_gaussian(rho)
        print(f"  {rho:.2f}    {val:.6f}")
        rows.append({"rho": rho, "mi": val})

    # Joint distribution example
    joint = np.array([[0.3, 0.1], [0.1, 0.5]])
    mi_joint = mi.mi_from_joint(joint)
    print(f"\n  MI from joint [[0.3,0.1],[0.1,0.5]]: {mi_joint:.6f}")

    bsc = mi.channel_capacity_bsc(0.1)
    print(f"  BSC capacity (p=0.1) = {bsc:.6f} bits")

    return {
        "gaussian_mi": rows,
        "joint_mi_example": mi_joint,
        "bsc_capacity_p01": mi.channel_capacity_bsc(0.01),
        "bsc_capacity_p10": bsc,
        "eml_depth": 2,
    }


def section5_max_entropy_theorem() -> dict:
    print(DIVIDER)
    print("SECTION 5 — MAX ENTROPY THEOREM: EML-1 KERNEL")
    print(DIVIDER)
    print("""
  THEOREM: Max entropy distribution with linear constraints
    E[T_k(X)] = η_k  (EML-0 constraints)
  is EXACTLY the exponential family:
    p*(x|θ) = h(x) · exp(θᵀT(x) - A(θ))

  The kernel exp(θᵀT(x)) = Π_k exp(θ_k · T_k(x))
  is a PRODUCT of EML-1 atoms.

  UNIFICATION with Session 57 (Statistical Mechanics):
    Boltzmann: p(state) ∝ exp(-βE(state)) = exp(θ·E)
    Same structure as max entropy with T=Energy, θ=-β.

  Examples:
    Gaussian:   T=(x, x²), h=1, θ=(μ/σ², -1/2σ²)
    Poisson:    T=x,       h=1/k!, θ=log λ
    Bernoulli:  T=x,       h=1,    θ=log(p/(1-p)) (logit)
    Boltzmann:  T=E,       h=g(E), θ=-β (inverse temperature)
""")
    ef = ExponentialFamily()
    theta1, theta2 = ef.gaussian_natural_params(0.0, 1.0)
    log_part = ef.gaussian_log_partition(theta1, theta2)
    expected_lp = math.log(math.sqrt(2 * math.pi))

    print(f"  Gaussian N(0,1) natural params: θ₁={theta1}, θ₂={theta2}")
    print(f"  Log partition A(θ) = {log_part:.8f}")
    print(f"  Expected ½·log(2π) = {expected_lp:.8f}")
    print(f"  Match: {abs(log_part - expected_lp) < 1e-10}")
    print(f"\n  EML depth of exp(θᵀT(x)) kernel: {ef.eml_depth_kernel()} (EML-1!)")

    # Max entropy discrete with fixed mean
    n, target_mean = 10, 3.0
    p_maxent = ef.max_entropy_discrete(n, {1: target_mean})
    actual_mean = float(np.dot(np.arange(n), p_maxent))
    print(f"\n  Max entropy on {{0,...,9}} with E[X]={target_mean}:")
    print(f"  Achieved mean: {actual_mean:.6f}")
    print(f"  Distribution: {np.round(p_maxent, 4)}")

    return {
        "gaussian_natural_theta1": theta1,
        "gaussian_natural_theta2": theta2,
        "log_partition": log_part,
        "log_partition_expected": expected_lp,
        "match": abs(log_part - expected_lp) < 1e-10,
        "eml_depth_kernel": ef.eml_depth_kernel(),
        "max_entropy_mean_achieved": actual_mean,
        "max_entropy_mean_target": target_mean,
    }


def section6_rate_distortion() -> dict:
    print(DIVIDER)
    print("SECTION 6 — RATE-DISTORTION: EML-2")
    print(DIVIDER)
    print("""
  R(D) = min_{p(x̂|x): E[d]≤D} I(X;X̂)
  For Gaussian source N(0,σ²):
    R(D) = ½·log(σ²/D)  for D ≤ σ²  — EML-2 in D (contains log)
  AWGN channel capacity: C = ½·log(1+SNR) — EML-2 in SNR
""")
    rd = RateDistortion()
    sigma = 1.0
    d_vals = [0.1, 0.25, 0.5, 0.75, 1.0]
    print("  D       R(D)      ½·log(1/D)  match")
    print("  -----   -------   ----------  -----")
    rows = []
    for d in d_vals:
        r = rd.rate_gaussian(sigma, d)
        formula = max(0.0, 0.5 * math.log(1.0 / d))
        match = abs(r - formula) < 1e-12
        print(f"  {d:.2f}    {r:.6f}  {formula:.6f}    {match}")
        rows.append({"D": d, "R": r, "formula": formula, "match": match})

    snr_vals = [1.0, 10.0, 100.0]
    cap = {f"snr_{snr}": rd.channel_capacity_awgn(snr) for snr in snr_vals}
    print(f"\n  AWGN capacities: {cap}")

    return {
        "rate_distortion_rows": rows,
        "awgn_capacity": cap,
        "eml_depth": 2,
    }


def main() -> None:
    print("\n" + DIVIDER)
    print("SESSION 60 — INFORMATION THEORY & EML COMPLEXITY")
    print(DIVIDER + "\n")

    results: dict = {"session": 60, "title": "Information Theory EML Complexity"}

    results["section1_entropy"] = section1_entropy()
    results["section2_kl_divergence"] = section2_kl_divergence()
    results["section3_fisher_information"] = section3_fisher_information()
    results["section4_mutual_information"] = section4_mutual_information()
    results["section5_max_entropy_theorem"] = section5_max_entropy_theorem()
    results["section6_rate_distortion"] = section6_rate_distortion()

    # Full analysis
    full = analyze_info_theory_eml()
    results["full_analysis"] = full["summary"]
    results["taxonomy"] = full["taxonomy"]

    print("\n" + DIVIDER)
    print("SUMMARY — EML DEPTHS IN INFORMATION THEORY")
    print(DIVIDER)
    print("""
  Shannon entropy H(X):           EML-2  (contains -Σ p·log p)
  KL divergence D_KL(P‖Q):        EML-2  (contains Σ p·log(p/q))
  Fisher information I(θ):        EML-2  (contains E[(∂log p/∂θ)²])
  Mutual information I(X;Y):      EML-2  (linear combo of entropies)
  Max entropy kernel exp(θᵀT(x)): EML-1  (pure exponential family!)
  Rate-distortion R(D):           EML-2  (½·log(σ²/D) in D)
  Cramér-Rao bound 1/I(θ):        EML-2  (rational in EML-2)

  KEY INSIGHT:
    ALL fundamental info-theoretic quantities are EML-2.
    The MAX ENTROPY solution (exponential family) is EML-1 —
    the simplest non-trivial EML class.
    This is the SAME as Boltzmann (Session 57): both arise from
    maximizing entropy with linear constraints → EML-1 atoms.
    The EML framework unifies statistical mechanics and information
    theory at the level of function complexity.
""")

    out_path = Path(__file__).parent.parent / "results" / "session60_info_theory_eml.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
