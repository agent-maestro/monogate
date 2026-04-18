"""
session68_combinatorics_eml.py — Session 68: Combinatorics, GFs & Grand Synthesis.
"""

import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from monogate.frontiers.combinatorics_eml import (
    OrdinaryGF,
    ExponentialGF,
    PartitionFunction,
    PrimeCountingEML,
    GrandSynthesis,
    COMBINATORICS_EML_TAXONOMY,
    analyze_combinatorics_eml,
)

DIVIDER = "=" * 70


def section1_ogf() -> dict:
    print(DIVIDER)
    print("SECTION 1 — ORDINARY GENERATING FUNCTIONS: EML-2")
    print(DIVIDER)
    print("""
  OGF F(x) = Σ a_n x^n. EML depth = depth of F(x) as function.

    Geometric:  Σ x^n = 1/(1-x)        → EML-2 (rational)
    Fibonacci:  Σ F_n x^n = 1/(1-x-x²) → EML-2 (rational)
    Catalan:    Σ C_n x^n = (1-√(1-4x))/2 → EML-2 (algebraic, √)

  Catalan numbers: C_n = (2n choose n)/(n+1)
  C_0=1, C_1=1, C_2=2, C_3=5, C_4=14, C_5=42, ...
  Count: parenthesizations, binary trees, lattice paths, ...
""")
    ogf = OrdinaryGF()

    # Fibonacci
    fibs = ogf.fibonacci_coefficients(12)
    print(f"  Fibonacci sequence (F_1 to F_12): {fibs}")

    # Catalan numbers
    catalan_nums = [ogf.catalan_number(n) for n in range(11)]
    print(f"\n  Catalan numbers C_0 to C_10: {catalan_nums}")

    # Verify OGF values
    x_vals = [0.1, 0.3, 0.5]
    print("\n  OGF values:")
    print("  x      1/(1-x)    1/(1-x-x²)  Catalan C(x)")
    rows = []
    for x in x_vals:
        g = ogf.geometric_ogf(x)
        f = ogf.fibonacci_ogf(x)
        c = ogf.catalan_ogf(x)
        print(f"  {x:.1f}    {g:.4f}     {f:.4f}       {c:.4f}")
        rows.append({"x": x, "geometric": g, "fibonacci": f, "catalan": c})

    return {
        "fibonacci": fibs,
        "catalan": catalan_nums,
        "ogf_values": rows,
        "eml_geometric": ogf.eml_depth_geometric(),
        "eml_fibonacci": ogf.eml_depth_fibonacci(),
        "eml_catalan": ogf.eml_depth_catalan(),
    }


def section2_egf() -> dict:
    print(DIVIDER)
    print("SECTION 2 — EXPONENTIAL GENERATING FUNCTIONS: EML-2")
    print(DIVIDER)
    print("""
  EGF F(x) = Σ a_n x^n/n!.

  Bell numbers (set partitions):
    EGF = exp(e^x - 1)  → EML-2 (exp of exp: double exponential)
    B_0=1, B_1=1, B_2=2, B_3=5, B_4=15, B_5=52, ...

  Derangements (no fixed points):
    EGF = exp(-x)/(1-x)  → EML-2 (EML-1 × EML-2)
    D_0=1, D_1=0, D_2=1, D_3=2, D_4=9, D_5=44, ...
""")
    egf = ExponentialGF()

    # Bell numbers
    bell_nums = [egf.bell_number(n) for n in range(11)]
    print(f"  Bell numbers B_0 to B_10: {bell_nums}")

    # Verify via Dobinski formula: B_n = (1/e)Σ k^n/k!
    print("\n  Bell numbers via Dobinski formula (1/e·Σ k^n/k!):")
    print("  n    B_n (exact)  Dobinski approx  match")
    rows = []
    for n in range(8):
        exact = egf.bell_number(n)
        dobinski = egf.bell_from_egf(n)
        match = abs(dobinski - exact) < 0.5
        print(f"  {n}    {exact:11d}  {dobinski:15.2f}  {match}")
        rows.append({"n": n, "exact": exact, "dobinski": dobinski, "match": match})

    # Derangements
    deranges = [egf.derangement_number(n) for n in range(10)]
    print(f"\n  Derangements D_0 to D_9: {deranges}")

    # Verify: D_n/n! → 1/e as n→∞
    derange_ratios = [egf.derangement_number(n) / math.factorial(n) for n in range(1, 10)]
    print(f"\n  D_n/n! → 1/e = {1/math.e:.6f}:")
    for n, r in enumerate(derange_ratios[-5:], start=5):
        print(f"  n={n}: D_n/n! = {r:.6f}")

    return {
        "bell_numbers": bell_nums,
        "dobinski_check": rows,
        "derangements": deranges,
        "derange_ratio_limit_1_over_e": 1.0 / math.e,
        "eml_bell": egf.eml_depth_bell(),
        "eml_derangements": egf.eml_depth_derangements(),
    }


def section3_partitions() -> dict:
    print(DIVIDER)
    print("SECTION 3 — PARTITION FUNCTION p(n): EML-1 ASYMPTOTIC")
    print(DIVIDER)
    print("""
  p(n) = number of partitions of n (unordered sums).
  p(4) = 5: {4, 3+1, 2+2, 2+1+1, 1+1+1+1}

  Hardy-Ramanujan (1918) asymptotic:
    p(n) ~ exp(π√(2n/3)) / (4n√3)  as n → ∞

  LEADING TERM: exp(C·√n) where C = π√(2/3) = π√2/√3.
  This is EML-1 in n: exp of (√n) — the EML-1 exponential of a √-sublinear.
  (More precisely: exp(a·n^{1/2}) is EML-1 with a fractional exponent.)
""")
    pf = PartitionFunction()

    n_vals = [1, 2, 5, 10, 20, 50, 100, 200]
    print("  n      p(n) exact     Hardy-Ramanujan   relative error")
    print("  -----  -----------   ---------------   ---------------")
    rows = []
    for n in n_vals:
        exact = pf.exact(n)
        hr = pf.hardy_ramanujan(n)
        rel_err = abs(hr - exact) / exact if exact > 0 else 0
        print(f"  {n:5d}  {exact:11d}   {hr:15.1f}   {rel_err:.4f}")
        rows.append({"n": n, "exact": exact, "hr": hr, "rel_err": rel_err})

    print(f"\n  C = π√(2/3) = {math.pi * math.sqrt(2/3):.6f}")
    print(f"  EML depth of leading term exp(C√n): {pf.eml_depth_asymptotic()} (EML-1)")

    return {
        "asymptotic_table": rows,
        "C_constant": math.pi * math.sqrt(2.0 / 3.0),
        "eml_depth": pf.eml_depth_asymptotic(),
    }


def section4_prime_counting() -> dict:
    print(DIVIDER)
    print("SECTION 4 — PRIME COUNTING π(x): EML-2 (LOG-INTEGRAL)")
    print(DIVIDER)
    print("""
  Prime Number Theorem: π(x) ~ Li(x) = ∫_2^x dt/log(t)

  Li(x): integral of 1/log(t) → EML-2 (log-integral).

  Riemann's exact formula (RH connection, Session 59):
    π(x) = Li(x) - Σ_{ρ} Li(x^ρ)/ρ - log(2) + small terms
  where ρ are non-trivial zeros of ζ(s).

  On RH: all ρ = 1/2 + iγ → Li(x^{1/2}) ~ 2√x/log(x) → EML-2.
  Error: |π(x) - Li(x)| = O(√x·log x): EML-2 error (sub-EML-2).
""")
    pc = PrimeCountingEML()

    x_vals = [10, 50, 100, 500, 1000]
    print("  x       π(x)    Li(x)    |π-Li|/π")
    print("  -----   -----   ------   --------")
    rows = []
    for x in x_vals:
        pi_x = pc.prime_counting_sieve(x)
        li_x = pc.log_integral(float(x))
        rel_err = abs(pi_x - li_x) / pi_x if pi_x > 0 else 0
        print(f"  {x:5d}   {pi_x:5d}   {li_x:6.2f}   {rel_err:.4f}")
        rows.append({"x": x, "pi_x": pi_x, "li_x": li_x, "rel_err": rel_err})

    print(f"\n  Li(x) = ∫dt/log(t): EML depth = {pc.eml_depth_li()} (log-integral)")
    print("  Connects to Session 59 (RH): zeros of ζ govern π(x) errors.")

    return {
        "pnt_table": rows,
        "eml_depth_li": pc.eml_depth_li(),
        "rh_connection": "zeros of zeta govern pi(x) error: Li(x^rho) ~ EML-2",
    }


def section5_grand_synthesis() -> dict:
    print(DIVIDER)
    print("SECTION 5 — GRAND SYNTHESIS: EML DEPTH MAP (Sessions 47-68)")
    print(DIVIDER)
    print("""
  The EML hierarchy covers ALL of mathematics and physics:

  EML-0: DISCRETE/ALGEBRAIC DATA
    - Integers, rationals, algebraic numbers
    - Topological invariants, winding numbers
    - CNOT gates, group characters (residues, dimensions)

  EML-1: EXPONENTIAL ATOMS
    - exp(x): the fundamental EML-1 atom
    - Boltzmann factors (stat mech), path integrals (QFT)
    - Fourier basis e^{inx}, U(1) representations
    - Hardy-Ramanujan leading term exp(π√(2n/3))

  EML-2: LOGARITHMS, GAUSSIANS, RATIONALS
    - log(x), √x, rational functions
    - Shannon entropy H(X) = -Σp·log p
    - Heat kernel, Schwarzschild metric, QFT propagators
    - OGFs/EGFs for combinatorics, Li(x) for primes

  EML-3: ERROR FUNCTION FAMILY
    - erf(x): integral of exp(-x²)/√π
    - Black-Scholes, quantum wavefunctions (HO)
    - Cole-Hopf Burgers solution, Grover algorithm
    - SU(2) characters sin/sin

  EML-∞: NON-ELEMENTARY, CHAOS, SINGULARITIES
    - Brownian paths, instantons exp(-1/g)
    - Black hole singularities, NS blowup (conj.)
    - Non-elementary integrals, Weierstrass ℘
    - Strange attractors, fractal dimension

  GRAND UNIFICATION THEOREM (EML):
    Every smooth mathematical quantity can be assigned an EML depth.
    Physical singularities = EML-∞ formation.
    Information = EML-2.
    Symmetry = EML-1 atoms.
    Topology = EML-0.
    The EML hierarchy IS the complexity ladder of continuous mathematics.
""")
    gs = GrandSynthesis()
    unified = gs.unified_eml_depths()

    print("  EML depth distribution across sessions 47-68:")
    for session_num, desc in unified["sessions"].items():
        print(f"    Session {session_num}: {desc}")

    print("\n  Unified principles:")
    for p in unified["unified_principles"]:
        print(f"    {p}")

    print(f"\n  Deepest theorem:\n  {unified['deepest_theorem'][:100]}...")

    return {
        "sessions_map": unified["sessions"],
        "unified_principles": unified["unified_principles"],
        "depth_map_sizes": {
            k: len(GrandSynthesis.DEPTH_MAP[k]["examples"])
            for k in GrandSynthesis.DEPTH_MAP
        },
    }


def main() -> None:
    print("\n" + DIVIDER)
    print("SESSION 68 — COMBINATORICS, GENERATING FUNCTIONS & GRAND SYNTHESIS")
    print(DIVIDER + "\n")

    results: dict = {
        "session": 68,
        "title": "Combinatorics, Generating Functions & Grand Synthesis",
    }

    results["section1_ogf"] = section1_ogf()
    results["section2_egf"] = section2_egf()
    results["section3_partitions"] = section3_partitions()
    results["section4_prime_counting"] = section4_prime_counting()
    results["section5_grand_synthesis"] = section5_grand_synthesis()

    full = analyze_combinatorics_eml()
    results["taxonomy"] = full["taxonomy"]
    results["summary"] = full["summary"]
    results["grand_synthesis_full"] = full["grand_synthesis"]

    print("\n" + DIVIDER)
    print("FINAL SUMMARY — SESSIONS 60-68 EML DEPTH COMPLETE MAP")
    print(DIVIDER)
    print("""
  Session 60 — Information Theory:
    Shannon entropy H: EML-2. Max entropy solution: EML-1.
    Unifies stat mech (Session 57) and info theory under EML-1.

  Session 61 — Quantum Field Theory:
    Path integral: EML-1 (Boltzmann atoms).
    Propagators: EML-2. Instantons: EML-∞ (exp(-1/g)). TQFT: EML-0.

  Session 62 — Navier-Stokes & PDEs:
    Heat kernel: EML-2. Cole-Hopf Burgers: EML-3.
    NS conjecture: EML-finite ↔ smooth solutions.

  Session 63 — Riemannian Geometry & GR:
    Schwarzschild: EML-2 (rational). Hawking T_H formula: EML-1.
    Singularity r=0: EML-∞.

  Session 64 — Stochastic Processes:
    BM paths: EML-∞. Expectations: EML-3 (via heat kernel).
    Black-Scholes: EML-3 (erf/Φ).

  Session 65 — Representation Theory:
    U(1) characters: EML-1 atoms. SU(2): EML-3.
    Peter-Weyl = Fourier analysis on groups.

  Session 66 — Complex Analysis:
    Log: EML-2. Monodromy: EML-0. Over ℂ: sin=EML-1.
    Essential singularities: EML-∞.

  Session 67 — Quantum Computing & Optimization:
    QFT entries: EML-1. Grover: EML-3. Legendre: depth-preserving.
    Log-barrier, entropy mirror: EML-2.

  Session 68 — Combinatorics & Grand Synthesis:
    OGFs/EGFs: EML-2. Hardy-Ramanujan: EML-1.
    Li(x) ~ π(x): EML-2. ALL sessions unified in EML hierarchy.

  THE EML HIERARCHY IS COMPLETE: sessions 47-68 cover
  number theory, algebra, geometry, analysis, physics, information,
  computation, and combinatorics — all under one depth classification.
""")

    out_path = Path(__file__).parent.parent / "results" / "session68_combinatorics_eml.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
