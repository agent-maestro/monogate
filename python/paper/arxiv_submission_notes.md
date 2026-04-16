# arXiv Submission Notes

## v0.9.0 / arXiv:2603.21852

Initial submission. Covers:
- EML operator definition and completeness results
- Exhaustive N≤8 sin(x) search (862,116 trees, 0 hits)
- Infinite Zeros Barrier proof (Theorem 1)
- EDL complementarity (additive incompleteness, exhaustive N≤6)
- Phantom attractor study: depth-3 EMLTree targeting π, λ_crit = 0.001
- BEST routing table (37 nodes vs 77 all-EML, 52% reduction)
- N=9/10 MCTS search; N=11 exhaustive (208,901,719 trees, 0 hits, best MSE 1.478e-4)

---

## Phase 10 additions (v0.10.0)

The following content was added after the initial submission and should be included
in a revision or companion paper:

**§4.6 Complex-Domain BEST Routing and Special Functions**
- ComplexHybridOperator (CBEST): same routing rules as BEST over ℂ
- Euler path identity: `eml(ix, 1) = exp(ix) = cos x + i·sin x` — sin/cos at 1 complex node (vs 63 real)
- Near-exact complex-MCTS constructions for Bessel J₀, erf, Airy Ai
- Open question: complex EML representation of sin(x) without projection

**§9 Physics-Informed EML Networks (PINN)**
- EMLPINN: EMLNetwork backbone + physics residual loss via autograd
- Equations: harmonic oscillator, steady Burgers, 1D heat
- Learned EML formula is a symbolic approximate solution to the ODE
- Results table: data loss and physics loss for all three equations

New exports: `CBEST`, `complex_best_optimize`, `EMLPINN`, `fit_pinn`,
`complex_mcts_search`, `complex_beam_search`, `gpu_mcts_search`.

---

## Phase 11 additions (v0.11.0-dev)

**THEORY.md** (repo root)
- Canonical expert-level theory reference
- Formal theorem/conjecture statements (Theorem 2.1 Infinite Zeros Barrier,
  Theorem 3.2 Euler Path, Corollary 2.2, Conjectures C1–C7)
- Open problems index with structured research roadmap (T1–T7)
- Intended audience: researchers building on the EML framework

**Formal paper section added to preprint.tex**
- §"Formal Statements of Main Results and Open Problems"
- Precise theorem/conjecture index matching THEORY.md
- Six conjectures C1–C7 with precise mathematical statements
- Insertion point: after §8 (Performance Kernels), before §Conclusion

**Reproducibility infrastructure**
- `Makefile`: `make reproduce-all`, `make reproduce-n11`, `make paper`, `make docker-run`
- `Dockerfile`: Python 3.12 + PyTorch 2.3 (CPU) + TeX Live + Rust — clean-room environment
- `requirements-reproduce.txt`: exact pins for numpy/scipy/matplotlib/pytest
- `scripts/reproduce_n11.py`: verifies all N=11 paper claims (12/12 checks)
  - Loads `results/sin_n11.json`, checks tree counts, zero candidates at 3 tolerances,
    best near-miss MSE ~1.478e-4, search_type field
  - Appends timestamped verification entry to RESULTS.md

**Version:** bumped to `0.11.0-dev` in `__init__.py` and `pyproject.toml`.

---

## Submission checklist

- [ ] All figures regenerated from source (`python experiments/plot_attractor_landscape.py`)
- [ ] Preprint compiled twice (`pdflatex preprint.tex` × 2 for cross-refs)
- [ ] `make reproduce-n11` passes (12/12 claims)
- [ ] `make test` passes (662 passed, 8 skipped)
- [ ] Abstract updated for v0.10.0 + Phase 11 additions
- [ ] All new section labels (`\label{sec:*}`) resolve without warnings
- [ ] Author affiliations and acknowledgements current
- [ ] `paper/README.md` updated with new section list
