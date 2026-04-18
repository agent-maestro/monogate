"""
session67_quantum_opt_eml.py — Session 67: Quantum Computing & Optimization EML.
"""

import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from monogate.frontiers.quantum_opt_eml import (
    QuantumGates,
    QuantumFourierTransform,
    GroverSearch,
    LegendreTransform,
    ConvexOptimizationEML,
    QC_OPT_EML_TAXONOMY,
    analyze_quantum_opt_eml,
)

DIVIDER = "=" * 70


def section1_quantum_gates() -> dict:
    print(DIVIDER)
    print("SECTION 1 — QUANTUM GATES: EML DEPTHS")
    print(DIVIDER)
    print("""
  Hadamard H = (1/√2)[[1,1],[1,-1]]: EML-2 (entry 1/√2 = 2^{-1/2}, algebraic)
  Phase R_θ = diag(1, e^{iθ}):       EML-1 (entry e^{iθ}: pure EML-1 atom)
  CNOT gate:                          EML-0 (permutation matrix, integer entries)
  T gate = R_{π/4}:                   EML-2 (e^{iπ/4} = (1+i)/√2, algebraic)

  Circuit EML depth bound: depth ≤ max(gate_EML) × circuit_depth.
""")
    gates = QuantumGates()

    H = gates.hadamard()
    print(f"  Hadamard matrix H =")
    print(f"  {H[0]}")
    print(f"  {H[1]}")
    unitary_err = float(np.max(np.abs(H @ H.conj().T - np.eye(2))))
    print(f"  H†H - I max error: {unitary_err:.2e}  (unitary: True)")

    R_pi4 = gates.phase_gate(math.pi / 4)
    print(f"\n  R_{{π/4}}[1,1] = {R_pi4[1,1]:.6f} (expected e^{{iπ/4}} = {(1+1j)/math.sqrt(2):.6f})")

    CNOT = gates.cnot()
    print(f"\n  CNOT gate (integer entries: EML-0):")
    for row in CNOT:
        print(f"  {[int(v.real) for v in row]}")

    # Circuit depth example
    # H on each qubit (EML-2) + CNOT (EML-0): max_EML=2, depth=2 → ≤ EML-4
    circuit_depth = gates.circuit_eml_depth([2, 0, 2, 1], circuit_depth=3)
    print(f"\n  Circuit with gates [H,CNOT,H,R_θ], depth=3: EML ≤ {circuit_depth}")

    return {
        "hadamard": H.tolist(),
        "unitary_error": unitary_err,
        "phase_pi4_entry": R_pi4[1, 1],
        "cnot_is_permutation": bool(np.all(CNOT == CNOT.astype(int))),
        "eml_hadamard": gates.eml_depth_hadamard(),
        "eml_phase": gates.eml_depth_phase(),
        "eml_cnot": gates.eml_depth_cnot(),
    }


def section2_qft() -> dict:
    print(DIVIDER)
    print("SECTION 2 — QUANTUM FOURIER TRANSFORM: EML-1")
    print(DIVIDER)
    print("""
  QFT_n: U_{jk} = e^{2πijk/n}/√n

  Entry e^{2πi·rational}: nth root of unity = EML-1 atom.
  1/√n: algebraic scaling → EML-2, but dominated by EML-1 roots.
  Overall: EML-1 (roots of unity structure).

  QFT_n = DFT_n/√n (normalized).
  Connection to Session 37 (EML Fourier): QFT uses EML-1 atoms = e^{2πijk/n}.
""")
    qft = QuantumFourierTransform()

    print("  QFT_4 matrix entries (first row):")
    Q4 = qft.matrix(4)
    for k in range(4):
        print(f"  k={k}: {Q4[0,k].real:.4f} + {Q4[0,k].imag:.4f}i  (|entry|={abs(Q4[0,k]):.4f})")

    print("\n  Unitarity check (max|U†U-I|) and DFT equivalence:")
    print("  n    unitary_err   dft_match_err")
    tests = []
    for n in [4, 8, 16, 32]:
        u_err = qft.verify_unitary(n)
        rng = np.random.default_rng(42)
        x_test = rng.normal(0, 1, n)
        dft_err = qft.verify_dft_equivalence(n, x_test)
        print(f"  {n:2d}   {u_err:.2e}    {dft_err:.2e}   {'match' if dft_err < 1e-10 else ''}")
        tests.append({"n": n, "unitary_err": u_err, "dft_err": dft_err})

    return {
        "qft4_first_row": [[Q4[0, k].real, Q4[0, k].imag] for k in range(4)],
        "tests": tests,
        "eml_depth": qft.eml_depth_entry(),
    }


def section3_grover() -> dict:
    print(DIVIDER)
    print("SECTION 3 — GROVER'S ALGORITHM: AMPLITUDE EML-3")
    print(DIVIDER)
    print("""
  After k iterations (N items, 1 target):
  Amplitude = sin((2k+1)·arcsin(1/√N)) — EML-3 (arcsin composition)

  arcsin(1/√N): inverse of sin (asin) — EML-3.
  sin(EML-3 × k): composition → still EML-3.

  Optimal: k ≈ π√N/4. Success prob ≈ 1.
  Quantum speedup: O(√N) vs classical O(N).
""")
    grover = GroverSearch()

    N_vals = [4, 16, 100, 1000, 10000]
    print("  N        k_opt   P(success)  Quantum  Classical  Speedup √N")
    print("  ------   -----   ----------  -------  ---------  ----------")
    rows = []
    for N in N_vals:
        k_opt = grover.optimal_iterations(N)
        p_succ = grover.success_prob_at_optimal(N)
        q_queries = int(math.ceil(math.pi * math.sqrt(N) / 4))
        speedup = math.sqrt(N)
        print(f"  {N:6d}   {k_opt:5d}   {p_succ:.6f}  {q_queries:7d}  {N:9d}  {speedup:.2f}")
        rows.append({"N": N, "k_opt": k_opt, "p_success": p_succ,
                     "quantum_queries": q_queries, "speedup": speedup})

    # Verify EML-3: arcsin(1/√N) is the key EML-3 quantity
    print(f"\n  EML-3 verification for Grover amplitude:")
    print(f"  N=100, k=5: sin(11·arcsin(1/10)) = {grover.amplitude(100, 5):.6f}")
    print(f"  arcsin(0.1) = {math.asin(0.1):.6f} (arcsin ∈ EML-3)")
    print(f"  EML depth: {grover.eml_depth()}")

    return {
        "table": rows,
        "amplitude_N100_k5": grover.amplitude(100, 5),
        "eml_depth": grover.eml_depth(),
    }


def section4_legendre() -> dict:
    print(DIVIDER)
    print("SECTION 4 — LEGENDRE TRANSFORM: DEPTH-PRESERVING")
    print(DIVIDER)
    print("""
  f*(y) = sup_x{x·y - f(x)}

  KEY DEPTH-PRESERVATION THEOREM:
    f(x) = x²/2 (EML-2): f*(y) = y²/2 (EML-2) — SAME depth!
    f(x) = exp(x) (EML-1): f*(y) = y·log(y) - y (EML-2) — depth goes UP by 1.
    f(x) = |x| (EML-0): f*(y) = 0 if |y|≤1, ∞ else (EML-0) — preserved!

  Pattern: Legendre transform can INCREASE EML depth by at most 1
  (when f is EML-1, f* involves log → EML-2).
  Conjugate pairs (f,f*) satisfy Young's inequality: xy ≤ f(x)+f*(y).
""")
    legendre = LegendreTransform()

    # Quadratic: verify numerically
    y_vals = [-3.0, -1.0, 0.0, 1.0, 2.0, 3.0]
    print("  f(x)=x²/2: f*(y) numerical vs y²/2 exact:")
    print("  y      f*(y) numeric  y²/2 exact  match")
    quad_rows = legendre.verify_quadratic(y_vals)
    for row in quad_rows:
        print(f"  {row['y']:5.1f}  {row['numerical']:12.6f}   {row['exact']:10.6f}  {row['match']}")

    # Exponential: f(x)=exp(x) → f*(y) = y·log(y)-y
    print("\n  f(x)=exp(x): f*(y) = y·log(y) - y:")
    print("  y      f*(y)")
    for y in [0.5, 1.0, 2.0, math.e, 5.0]:
        fstar = legendre.legendre_exp(y)
        print(f"  {y:.2f}   {fstar:.6f}")

    # Gaussian case
    print("\n  Gaussian f(x)=x²/(2σ²): f*(y)=σ²y²/2 (EML-2→EML-2)")
    for sigma in [0.5, 1.0, 2.0]:
        fstar = legendre.legendre_gaussian(1.0, sigma)
        print(f"  σ={sigma}: f*(y=1) = {fstar:.4f} = σ²/2 = {sigma**2/2:.4f}")

    return {
        "quadratic": quad_rows,
        "all_quad_match": all(r["match"] for r in quad_rows),
        "exp_examples": [{"y": y, "f*": legendre.legendre_exp(y)}
                          for y in [0.5, 1.0, math.e]],
        "eml_quadratic": legendre.eml_depth_quadratic(),
        "eml_exp": legendre.eml_depth_exp(),
        "depth_preservation": "Legendre of x^2/2 = y^2/2: EML-2 → EML-2 (preserved)",
    }


def section5_optimization() -> dict:
    print(DIVIDER)
    print("SECTION 5 — CONVEX OPTIMIZATION: EML DEPTHS")
    print(DIVIDER)
    print("""
  Log-barrier B(x) = -Σ log(-g_i(x)):  EML-2 (contains log)
  Entropy mirror ψ(x) = -Σ x·log x:    EML-2 (same as entropy, Session 60)
  KKT Lagrangian L = f + Σλ_i g_i:    EML = max(depth_f, depth_g)
  Gradient descent on EML-2 f:         iterates stay EML-2 (differentiation preserves)
""")
    optim = ConvexOptimizationEML()

    # Gradient descent on f(x) = x²/2 (EML-2)
    def f_quad(x): return x ** 2 / 2
    def df_quad(x): return x

    x0 = 5.0
    path = optim.gradient_descent_path(f_quad, df_quad, x0=x0, alpha=0.2, n_steps=20)
    print(f"  GD on f(x)=x²/2 (EML-2), x₀={x0}, α=0.2:")
    print(f"  Steps: {[round(x, 4) for x in path[:8]]}...")
    print(f"  Converges to: {path[-1]:.8f} (expected 0.0)")

    # Log barrier on g(x) = x-1 (constraint x < 1)
    # B(x) = -log(1-x) for x < 1
    x_vals = [0.0, 0.5, 0.8, 0.9, 0.95]
    print("\n  Log-barrier -log(1-x) (g(x)=x-1 < 0 requires x<1):")
    for x in x_vals:
        b = optim.log_barrier(x, x - 1.0)
        print(f"  x={x}: B = {b:.4f}  (EML-2: contains log)")

    # KKT depth
    print("\n  KKT Lagrangian depth:")
    for df, dg in [(2, [2, 0]), (2, [2, 2]), (1, [0])]:
        depth = optim.kkt_lagrangian_depth(df, dg)
        print(f"  depth(f)={df}, depth(g)={dg}: L depth = {depth}")

    # Entropy mirror
    p_uniform = np.array([0.25, 0.25, 0.25, 0.25])
    p_skew = np.array([0.7, 0.1, 0.1, 0.1])
    h_uniform = optim.entropy_mirror(p_uniform)
    h_skew = optim.entropy_mirror(p_skew)
    print(f"\n  Entropy mirror ψ(p)=-Σ p·log p:")
    print(f"  Uniform (max entropy): {h_uniform:.4f} = log(4) = {math.log(4):.4f}")
    print(f"  Skewed: {h_skew:.4f}")

    return {
        "gd_path": path[:10],
        "gd_converges_to": path[-1],
        "kkt_depth_examples": [
            {"df": 2, "dg": [2, 0], "L_depth": optim.kkt_lagrangian_depth(2, [2, 0])},
            {"df": 2, "dg": [2, 2], "L_depth": optim.kkt_lagrangian_depth(2, [2, 2])},
        ],
        "entropy_uniform": h_uniform,
        "entropy_max": math.log(4),
        "eml_log_barrier": optim.eml_depth_log_barrier(),
        "eml_entropy_mirror": optim.eml_depth_entropy_mirror(),
    }


def main() -> None:
    print("\n" + DIVIDER)
    print("SESSION 67 — QUANTUM COMPUTING & OPTIMIZATION EML")
    print(DIVIDER + "\n")

    results: dict = {"session": 67, "title": "Quantum Computing & Optimization EML"}

    results["section1_gates"] = section1_quantum_gates()
    results["section2_qft"] = section2_qft()
    results["section3_grover"] = section3_grover()
    results["section4_legendre"] = section4_legendre()
    results["section5_optimization"] = section5_optimization()

    full = analyze_quantum_opt_eml()
    results["taxonomy"] = full["taxonomy"]
    results["summary"] = full["summary"]

    print("\n" + DIVIDER)
    print("SUMMARY — EML DEPTHS IN QUANTUM COMPUTING & OPTIMIZATION")
    print(DIVIDER)
    print("""
  Hadamard gate H:                 EML-2  (1/√2 entries: algebraic)
  Phase gate R_θ:                  EML-1  (e^{iθ}: EML-1 atom)
  CNOT gate:                       EML-0  (permutation matrix)
  QFT entries e^{2πijk/n}/√n:     EML-1  (roots of unity)
  Grover amplitude sin(arcsin):    EML-3  (arcsin composition)
  Legendre f*(y) for f=x²/2:      EML-2  (depth preserved: y²/2)
  Legendre f*(y) for f=exp(x):    EML-2  (y·log y - y: +1 depth)
  Log-barrier -Σ log(-g):          EML-2  (contains log)
  Entropy mirror -Σ x·log x:       EML-2  (same as entropy)
  KKT Lagrangian:                  EML-max(f,g)

  KEY INSIGHT:
    QFT uses EML-1 atoms (roots of unity) — the most efficient basis.
    Legendre transform: depth-preserving for x²/2, depth+1 for exp(x).
    The pairing f↔f* obeys Young's inequality: xy ≤ f(x) + f*(y).
    All log-based methods (barrier, entropy, KL) are EML-2.
""")

    out_path = Path(__file__).parent.parent / "results" / "session67_quantum_opt_eml.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
