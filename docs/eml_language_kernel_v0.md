# EML Language Kernel v0

Date: 2026-05-27
Status: internal candidate

## Purpose

EML Language Kernel v0 is a small front door for EML examples. It lets a
program describe an operator tree, declared domains, local guards, and metadata
before lowering into the existing EML Expression Packet v0 pipeline.

This is not a compiler change. It is a parser and normalizer for candidate
research programs.

## Surface Syntax

The line-oriented syntax is intentionally small:

```text
program softplus_pair_v0
family softplus_logsumexp
meaning Small log-sum-exp style expression.
source_repo monogate
input a unit dimensionless range -10 10
input b unit dimensionless range -10 10
guard positive(exp(a) + exp(b))
return ln(exp(a) + exp(b))
```

Supported declarations:

- `program <id>`
- `family <name>`
- `meaning <text>`
- `source_repo <name>`
- `input <name> unit <unit> range <min> <max>`
- `input <name> unit <unit>`
- `let <name> = <expression>`
- `guard positive(<expression>)`
- `guard nonzero(<expression>)`
- `guard range(<input>, <min>, <max>)`
- `return <expression>`

## Operators

Supported expression operators:

- constants
- variables
- `exp(x)`
- `ln(x)`
- `sqrt(x)`
- `sin(x)`
- `cos(x)`
- `tanh(x)`
- `softplus(x)`
- `eml(x, y)`
- `+`
- `-`
- `*`
- `/`
- `**`

The normalizer expands:

- `softplus(x)` to `ln(1 + exp(x))`
- `eml(x, y)` to `exp(x) - ln(y)`
- `let` references into the returned expression

## Output Contract

For each program, the kernel emits:

- a normalized language artifact
- an EML Expression Packet v0 candidate
- a short report

The emitted packet is compatible with the existing EML packet builder, domain
safety lens, proof registry, and Explorer surfaces.

## Boundaries

- No Forge/compiler behavior change.
- No public savings claim.
- No formal verification or theorem claim.
- No complete EML language semantics claim.
- No package publish or deploy.

