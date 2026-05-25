# EML IR Lowering Contract v0

Date: 2026-05-25

Status: `INTERNAL_LOWERING_CONTRACT_DRAFT`

## Purpose

This contract defines how the current EML IR prototype turns an
expression into a deterministic DAG artifact and replay packet. It is a
bridge between SuperBEST expression costing and future compiler/runtime
work. It is not a Forge compiler integration and does not change
canonical SuperBEST row costs.

## Scope

- Expression-level only.
- Host-runtime only.
- Deterministic local artifact generation.
- No compiler behavior changed.
- No package publish or deploy.

## Primitive Set v0

The v0 prototype recognizes:

`exp`, `ln`, `neg`, `add`, `sub`, `mul`, `div`, `pow`, `sqrt`, `sin`,
`cos`, `tanh`, `recip`, variables, and constants.

Unsupported operations must fail before an IR packet is treated as
valid.

## Determinism Rules

1. Parse expression text into a normalized Python AST fingerprint.
2. Visit child nodes before parent nodes.
3. Assign stable node ids in dependency order: `n0`, `n1`, ...
4. Reuse identical fingerprints as a single DAG node.
5. Emit dependency-ordered temporaries for repeated subexpressions.
6. Preserve the original final expression as a lowered expression over
   stable temporaries.

## Tree vs DAG Semantics

Tree SuperBEST cost counts every operation occurrence in the expression
tree. DAG SuperBEST cost counts each structurally identical repeated
subexpression once.

Current public-safe baseline:

- Tree SuperBEST figures.
- Canonical row table figures.

Current internal prototype evidence:

- DAG savings.
- EML IR replay packet savings.
- Shared denominator, sigmoid, rational, and polynomial-basis reuse
  examples.

Do not turn DAG savings into public headline claims until the lowering
semantics, product copy, and public surfaces are reviewed together.

## Replay Rules

Each EML IR program emits:

1. `INIT`: program accepted by local parser.
2. `READY`: DAG node identifiers assigned.
3. `RUNNING`: operation frames in deterministic node order.
4. `END`: output node reached.
5. `PARKED`: explicit replay terminal boundary.

Every frame carries:

- monotonic tick
- kernel/op id
- guard action and reason
- previous replay hash
- current replay hash

Division frames are annotated because this prototype does not prove
denominator domains.

## Validity Gates

An EML IR packet is valid only if:

- all node edges reference existing nodes;
- output node exists;
- frame ticks are monotonic;
- replay hash predecessor links are intact;
- recomputed frame hashes match;
- final lifecycle state is `PARKED`;
- boundary fields remain false for deploy, package publish, public
  theorem claim, formal verification claim, and production marketplace
  modification.

## Integration Notes

- `python/scripts/eml_ir_pipeline.py` builds the canonical IR examples.
- `python/scripts/eml_ir_inspector.py` builds the local viewer packet
  and Explorer model JSON.
- `explorer/src/components/EMLIRInspectorTab.jsx` displays the prototype
  inside Explorer.
- `demo/eml_ir_inspector_v0_2026_05_25/` remains a standalone local
  artifact.

## Non-Claims

This contract does not claim a compiler, formal verification, public
optimality, package release, production marketplace readiness, or a new
public SuperBEST savings headline.
