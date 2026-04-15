# Operator Cousins of EML: Completeness, Efficiency, and Hybrid Architectures

## Abstract

The EML operator — eml(x,y) = exp(x) − ln(y) — was introduced by Odrzywołek (2026) as a universal primitive for elementary function computation from the single constant 1. We present theoretical and empirical extensions. Among the five natural binary operators of the form f(exp(x), ln(y)), we find that EML and EDL are the only candidates supporting complete elementary arithmetic; EML completeness is established by the original paper, and EDL completeness over the multiplicative group is demonstrated here. We identify EXL (exl(x,y) = exp(x)·ln(y)) as a numerically superior incomplete operator enabling 1-node ln and 3-node pow constructions, and establish that addition and subtraction are structurally irreplaceable in EML — no other complete operator in the family supports them. A HybridOperator framework routing each primitive to its optimal operator achieves 52% fewer nodes overall across all elementary operations, rising to 74% for polynomial evaluation patterns; applied to Taylor sin(x), machine precision (6.5e-15) is reached at 13 terms and 63 nodes. We also report five empirical phenomena from gradient-based symbolic regression and empirical results showing EXL-inner/EML-outer hybrid networks outperform pure-EML on 5/7 regression targets. The open problem of exact closed-form sin(x) from terminal {1} remains open. Code: github.com/almaguer1986/monogate.

---

## 1. Introduction

- placeholder

## 2. Methods

- placeholder

## 3. Results

- placeholder

## 4. Discussion

- placeholder

## 5. Open Problems

- placeholder

## References

- placeholder
