# EML-A9 Compiler Guard Rules

Date: 2026-05-27

A9 turns A8 evidence into conservative compiler/runtime policy. It is a rule
registry only; it does not change compiler behavior.

Rule set:

- Prefer EML for proof/search/teaching structure when domain guards are clear.
- Lower `eml(x,e)` / `exp(x)-1` to protected `expm1` near zero.
- Lower softplus/log-sum-exp shapes to protected `logaddexp` style routines.
- Require positive-domain guards for logarithmic EML arguments.
- Block unstable deep trees until holdout evidence exists.
- Require candidate/trial/control packets before advantage claims.

Result:

- Rules: `6`
- Ready for compiler fixtures: `5`
- Compiler behavior changed: `false`
- Compiler correctness claim: `false`
- Guard rules complete: `false`

Boundary:

A9 does not prove compiler correctness, EML advantage, broad EML superiority,
runtime performance, theorem discovery, public Atlas promotion, or deployment.
