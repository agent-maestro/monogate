# Constructibility Comparison: EML vs Classical Hierarchies

## Summary

This document positions EML constructibility within the known landscape of
mathematical constructibility hierarchies.

## 1. Classical Constructibility Hierarchies

### 1.1 Compass-and-Straightedge (CS)
**Operations**: addition, subtraction, multiplication, division, square root
**Constructible numbers**: `Q(sqrt(a1), sqrt(a2), ...)` — nested quadratic extensions
**Key fact**: `i = sqrt(-1)` IS CS-constructible (draw perpendicular to real line)
**Algebraic characterization**: degree over Q is a power of 2

### 1.2 Origami / Huzita-Hatori (OH)
**Operations**: CS + cube root
**Constructible numbers**: CS + solutions to cubics (e.g., cube root of 2)
**Key fact**: `i` is trivially OH-constructible (subsumes CS)
**Algebraic characterization**: degree over Q is 2^a * 3^b

### 1.3 EL Numbers (Exp-Log Hierarchy)
**Operations**: addition, subtraction, multiplication, division, exp, log (real only)
**Constructible numbers**: e, pi, e^e, ln(2), ...; all "elementary" real numbers
**Key fact**: `i = exp(i*pi/2)` but this is circular (requires i as input to exp)
  Over the REALS: i is not in the EL real closure.
  The extended EL closure over C trivially contains i since exp(i*pi/2) = i.
**Reference**: Liouville (1851), Ritt (1925), Richardson (1968)

### 1.4 Liouville Numbers (Approximation-Theoretic)
**Definition**: real x with very fast rational approximation (|x - p/q| < q^{-n} infinitely often)
**NOT a constructibility hierarchy** — measures approximation speed, not algebraic structure
**Key fact**: All Liouville numbers are transcendental but EML says nothing about this class directly

## 2. The EML Constructibility Hierarchy

**Operator**: `eml(x, y) = exp(x) - Log(y)` (principal branch Log)
**Seed**: {1}
**Closure**: EML_1 = smallest set containing 1 closed under eml

### EML vs CS
- CS produces only algebraic numbers (in Q-bar)
- EML_1 contains transcendentals (e = eml(1,1), pi is conjectured NOT in EML_1)
- EML_1 ⊃ CS-constructibles over R? NO — e.g., sqrt(2) ∉ EML_1 (conjectured)
- CS and EML are INCOMPARABLE hierarchies

### EML vs EL Numbers
- EL uses +,-,*,/,exp,log; EML uses only exp and log combined as eml(x,y)=exp(x)-log(y)
- EML is a STRICT SUBSET of EL (EL can build more values using separate exp and log)
- Every EML value is an EL value (since exp and log are EL operations)
- EL ⊃ EML strictly: EL contains sqrt(2) = exp(0.5 * ln(2)); EML cannot build this directly
- Over C: EL trivially contains i (exp(i*pi/2)); EML's i-constructibility is OPEN

### EML vs Liouville Numbers
- EML is about exact constructibility, not approximation speed
- The density conjecture (S98-S99) says EML_1 APPROXIMATES i arbitrarily well
- If density holds: i is a Liouville-like "accumulation point" of EML_1 but not IN EML_1
- This would be an exact analogue: pi approximated by rationals, i approximated by EML_1

## 3. Position of EML in the Hierarchy

```
CS-constructible (algebraic, degree 2^k)
    ⊂
OH-constructible (algebraic, degree 2^a * 3^b)
    ⊂
Q-bar (all algebraic numbers)
    ...
EL numbers (exp-log hierarchy over R)
    ⊃
EML_1 ∩ R (real part of EML closure)  ← STRICTLY CONTAINED in EL

EML_1 ⊂ C (full complex closure)  ← i-constructibility OPEN
```

**Key**: EML is NOT a sub-hierarchy of CS (EML contains transcendentals).
EML is NOT a super-hierarchy of CS (CS contains sqrt(2), EML may not).
EML is a DIFFERENT kind of hierarchy, organized by iteration depth of a specific operator.

## 4. The i-Constructibility Problem in Context

| System | Is i constructible? | Method |
|--------|---------------------|--------|
| CS | YES | sqrt(-1) directly |
| OH | YES | (subsumes CS) |
| EL (real) | NO | i is not real |
| EL (complex) | YES (trivial) | exp(i*pi/2) uses i |
| EML_1 | OPEN (T_i conjecture) | No depth-finite construction found |

**The point**: i is constructible in every classical system where complex numbers are
admitted. EML_1's i-constructibility is genuinely open because the EML grammar
imposes a specific constraint: you can only apply exp to x and subtract Log(y),
building from {1}. The tan(1) obstruction shows that the specific structure of
pi and tan(1) prevents the known depth-6 route from reaching Im=1 exactly.

## 5. Formal Separation Results

**Proved (T19)**: Under strict grammar (Log restricted to R+), i is NOT constructible.
  This separates EML-strict from EL (which can build non-real values using complex inputs).

**Open (T_i)**: Under extended grammar (Log on C*), i ∉ EML_1?
  - Conditional on Schanuel: TRUE (e and e^i algebraically independent => T_i)
  - Unconditional: OPEN

## 6. References

- Ritt, J.F. (1925). "Elementary functions and their inverses." *Trans. AMS* 27.
- Richardson, D. (1968). "Some undecidable problems involving elementary functions." *JSL* 33.
- Chow, T. (1999). "What is a closed-form number?" *AMM* 106.
- Hermite (1873), Lindemann (1882): Transcendence of e and pi.
- Nesterenko (1996): Algebraic independence of pi, e^pi, Gamma(1/4).
