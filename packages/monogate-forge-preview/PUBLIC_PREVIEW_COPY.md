# monogate-forge-preview Public Preview Copy Review

Status: local scaffold copy draft, not published
Date: 2026-05-30

## Approved Short Copy

`monogate-forge-preview` is a local, evidence-gated scaffold for a selected
Forge/eFrog compiler-preview path. It demonstrates one bounded flow from a
selected source fixture to Python and JavaScript outputs, deterministic sample
checks, and an evidence packet with public-readiness and correctness claims
locked false.

## Approved Capability Copy

The current local scaffold supports:

- `capabilities`
- `emit --target python`
- `emit --target javascript`
- `check --targets python,javascript`
- `packet --targets python,javascript`

The current real bridge evidence also includes JavaScript runtime execution in
the eFrog bridge guard and selected JavaScript-source semantic comparisons.

## Required Boundary Copy

This is not a public package release yet. It is not a general compiler,
compiler-correctness proof, formal semantic-equivalence result, production
toolchain, performance benchmark, Verilog/Lean/zkproof/silicon release, or
checkout-enabled product.

## Blocked Public Phrases

- 36 shipped targets
- Write math. Get silicon.
- bit-equivalent output
- compiler correctness
- formally verified compiler
- Lean proofs emitted
- zkproof target ready
- Verilog target ready
- production toolchain
- checkout enabled
- public package available

## Publication Gate

Publication remains blocked until a separate release action confirms:

- package version and distribution target
- clean-room install from the intended distribution channel
- public copy matches this boundary
- checkout remains disabled unless a separate commerce review passes
- claim flags remain false
