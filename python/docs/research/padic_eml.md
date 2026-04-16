# p-adic EML — Research Notes

## Overview

The EML operator `eml(x, y) = exp(x) − ln(y)` extends naturally to p-adic
number fields.  p-adic mathematics provides an alternative notion of "closeness"
based on divisibility by a prime $p$: two numbers are p-adically close if
their difference is divisible by a high power of $p$.

This document records mathematical findings and open questions from the
`monogate.padic` module.

## p-adic Exponential

The p-adic exponential is defined as the formal power series:
$$\exp_p(x) = \sum_{n=0}^{\infty} \frac{x^n}{n!}$$

This series converges for $|x|_p < p^{-1/(p-1)}$:
- For $p=2$: requires $v_2(x) \geq 2$ (i.e., $4 \mid x$)
- For $p=3$: requires $v_3(x) \geq 1$ (i.e., $3 \mid x$)
- For $p=5$: requires $v_5(x) \geq 1$ (i.e., $5 \mid x$)

The key technical challenge: dividing $x^n$ by $n!$ requires extracting the
p-adic valuation of $n!$ (given by Legendre's formula:
$v_p(n!) = \sum_{k=1}^{\infty} \lfloor n/p^k \rfloor$) and right-shifting
the digit representation accordingly.

## p-adic Logarithm

The p-adic logarithm converges for $|x - 1|_p < 1$:
$$\log_p(x) = \sum_{n=1}^{\infty} \frac{(-1)^{n+1} (x-1)^n}{n}$$

This requires $x \equiv 1 \pmod{p}$ (first digit = 1 in base $p$).

## p-adic EML

The EML operator in p-adic arithmetic:
$$\text{eml}_p(x, y) = \exp_p(x) - \log_p(y)$$

**Verified property**: $\text{eml}_p(0, 1) = 1$ for all primes $p$.
- $\exp_p(0) = 1$ (constant term of series)
- $\log_p(1) = 0$ (all terms vanish when $x=1$)

## Fixed Point Structure

For the map $f(x) = \text{eml}_p(x, 1)$, the fixed points satisfy:
$$\exp_p(x) - \log_p(1) = x$$
$$\exp_p(x) = x$$

In real arithmetic, the only fixed point of $e^x = x$ is complex (it doesn't exist
for real $x$). In p-adic arithmetic, the convergence domain is restricted to
$|x|_p < p^{-1/(p-1)}$, and fixed points may exist within this disk.

The `padic_fixed_points` function sweeps integer candidates (multiples of
$p$ for $p$ odd, multiples of $4$ for $p=2$) and tests the fixed-point
condition $|f(x) - x|_p < p^{-\text{precision}/2}$.

## Open Questions

1. **Teichmüller representatives**: The p-adic integers $\mathbb{Z}_p$ have
   $p-1$ distinct $(p-1)$-th roots of unity (Teichmüller lift). Does the
   p-adic EML map preserve these?

2. **p-adic Euler identity**: For primes $p \equiv 1 \pmod{4}$, there exists
   a p-adic square root of $-1$.  Can the Euler identity
   $e^{i\pi} + 1 = 0$ be expressed as a p-adic EML identity?

3. **Universality**: The real EML operator generates all elementary functions.
   Does $\text{eml}_p$ generate all p-adic analytic functions (Mahler's
   theorem characterizes continuous $\mathbb{Z}_p \to \mathbb{Z}_p$ maps)?

4. **Attractor depth-dependence**: The real phantom attractor at
   $\lambda_{\text{crit}} \approx 0.5671$ emerges from the depth-1 EML map.
   Does the p-adic analog of this attractor exist, and if so, does it
   have a closed form in terms of the p-adic Lambert W function?

5. **Kummer's theorem connection**: The valuation of $\binom{m+n}{n}$ is
   the number of carries when adding $m$ and $n$ in base $p$ (Kummer's theorem).
   Is there a combinatorial interpretation of the p-adic EML coefficients
   in terms of carry patterns?

## Implementation Notes

### Finite Precision Arithmetic

The `PAdicNumber` class implements finite-precision p-adic arithmetic as
tuples of digits in $\{0, \ldots, p-1\}$. This truncates the infinite
p-adic expansion at `precision` digits, analogous to floating-point
mantissa truncation.

Operations use **schoolbook multiplication** with carry propagation mod $p^\text{precision}$,
and **Newton's method** for multiplicative inverse:
$$y_{n+1} = y_n (2 - x y_n) \pmod{p^\text{precision}}$$

### Division by non-units

The critical subtlety: dividing a PAdicNumber by an integer $n$ with $p \mid n$
requires:
1. Computing $v = v_p(n)$
2. Right-shifting the numerator by $v$ digit positions
3. Dividing the result by the unit part $n / p^v$

This is essential for the series computation of $\exp_p$ and $\log_p$, where
the denominator $n!$ has p-adic valuation $\sum_k \lfloor n/p^k \rfloor$.

## References

- Koblitz, N. (1984). *p-adic Numbers, p-adic Analysis, and Zeta-Functions*.
  Springer.
- Mahler, K. (1958). An interpolation series for continuous functions of a
  p-adic variable. *Journal für die reine und angewandte Mathematik*, 199, 23–34.
- Robert, A. M. (2000). *A Course in p-adic Analysis*. Springer.
- Odrzywołek, A. (2026). monogate: EML arithmetic. arXiv:2603.21852.
