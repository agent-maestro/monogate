# EML IR Lowering Contract v1

Date: 2026-05-25

Status: `INTERNAL_LOWERING_CONTRACT_V1_DRAFT`

First code-backed artifact:

```text
lib/src/ir.js
docs/research/eml_ir_v1_replay_artifact.md
```

## Purpose

This contract defines the next stable boundary for the EML IR prototype:

`expression -> normalized DAG nodes -> guarded replay frames -> lowered sketches -> visual field bridge`

It does not change compiler behavior. It does not change the canonical SuperBEST table. It gives Explorer, SuperBEST DAG experiments, and future Forge lowering work a shared language.

## Primitive Set

The v1 primitive set is:

- `input`
- `constant`
- `neg`
- `add`
- `sub`
- `mul`
- `div`
- `pow`
- `exp`
- `ln`
- `sqrt`
- `sin`
- `cos`
- `tanh`

## Node Identity Rules

Stable node IDs are assigned in topological order:

`n0`, `n1`, `n2`, ...

Structural identity is based on:

`op_kind + normalized_args + normalized_literal`

For commutative operations, `add` and `mul` children should be sorted by structural hash before reuse accounting. Literal normalization remains conservative: preserve the exact source literal until a numeric-literal policy v2 exists.

## Tree Cost vs DAG Cost

Tree SuperBEST cost counts every operation occurrence.

DAG SuperBEST cost counts each structurally identical repeated operation once.

Public-facing headline savings must continue to use Tree SuperBEST until DAG lowering behavior has a dedicated review gate.

## Replay Frame Mapping

An EML IR replay trace uses this lifecycle:

`INIT -> READY -> RUNNING -> END -> PARKED`

Operation nodes emit `RUNNING` frames. Domain-sensitive nodes, especially `div`, must emit guard annotations when the prototype cannot prove the domain condition.

`PARKED` is the explicit terminal replay boundary. It means the packet reached an inspectable stop state; it is not a boot/runtime claim.

## Field Bridge

The complex field view is a visual-intuition bridge, not a correctness validator.

Allowed v1 examples:

- `z`
- `z^2`
- `exp(z)`
- `ln(z)`
- `eml(z, 1)`
- `eml(z, z + 2)`

The field view may explain phase, magnitude, branch behavior, and periodic cues. It must not claim to validate lowering correctness.

## Validity Gates

An IR artifact is reviewable only when:

- schema fields are present;
- replay hash chain is present;
- lifecycle order is valid;
- domain annotations are present where required;
- Tree-vs-DAG savings are labeled correctly.

## Boundaries

This is internal draft infrastructure. It is not a compiler release, public savings claim, formal verification result, production marketplace update, package publish, safety certification, production-control claim, or hardware-backed evidence.
