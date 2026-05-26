# EML IR v1 Replay Artifact

Date: 2026-05-26

Status: internal research artifact

## What Changed

`lib/src/ir.js` implements the first code-backed slice of the EML IR Lowering
Contract v1:

```text
expression -> normalized DAG nodes -> guarded replay frames -> evidence packet
```

It exposes:

```js
import {
  buildEvidencePacket,
  certifyLowering,
  checkStructuralLowering,
  checkSampledEquivalence,
  normalizeDag,
  emitReplayPacket,
  lowerDagToJS,
  lowerDagToPython,
  validateEvidencePacket,
  validateReplayPacket,
} from "monogate/ir";
```

## Why It Matters

Before this artifact, the IR contract was prose. Now Monogate has a runnable
boundary object that can be shared by:

- Explorer visualizations;
- SuperBEST tree-vs-DAG experiments;
- future Forge lowering work;
- electronics-style replay evidence;
- future MachLib proof obligations.

This is deliberately not a public savings claim. The packet labels both
`tree_cost` and `dag_cost`, and the boundary flags mark:

```text
public_savings_claim: false
formal_verification_claim: false
compiler_release_claim: false
```

## Current Capabilities

- Parses existing `monogate/cost` expression strings.
- Assigns stable topological node IDs.
- Deduplicates structurally identical subexpressions.
- Canonicalizes `add` and `mul` child order for reuse accounting.
- Emits domain annotations for `ln`, `sqrt`, `div`, and `pow`.
- Emits lifecycle replay frames:

```text
INIT -> READY -> RUNNING -> END -> PARKED
```

- Hash-chains replay frames with stable local hashes.
- Validates replay lifecycle, hash chain, and RUNNING-frame annotations.
- Lowers DAGs to JavaScript and Python sketches.
- Checks per-node structural lowering rule coverage.
- Evaluates DAGs directly on finite sample points.
- Compares lowered JavaScript against the DAG interpreter and emits sampled
  equivalence evidence.
- Builds a top-level evidence packet:

```text
expression -> dag -> replay -> lowering -> replay/structural/sampled checks -> research_status
```

The research status vocabulary is deliberately public-safe:

- `verified`: replay/structural contract gate, not a broad theorem.
- `sampled`: finite numerical evidence only.
- `prototype`: internal artifact with explicit non-claim boundaries.
- `blocked`: a required gate failed or is missing.

## Example

```js
const dag = normalizeDag("exp(x) + exp(x)");

dag.tree_cost; // 4
dag.dag_cost;  // 3
```

The repeated `exp(x)` subtree is one DAG node, but the artifact keeps the
tree-vs-DAG distinction explicit.

Lowering certificate:

```js
const cert = certifyLowering("exp(x) + exp(x)", {
  samples: [{ x: 1 }, { x: 2 }],
});

cert.equivalence.behavioral_equivalence_sampled; // true
cert.structural.structural_lowering_verified;    // true
cert.lowering.javascript.source;                 // function lowered(x) { ... }
cert.lowering.python.source;                     // def lowered(x): ...
```

This is sampled evidence only. It is not a formal equivalence theorem and not a
compiler release.

Evidence packet:

```js
const packet = buildEvidencePacket("exp(x) + exp(x)");

packet.schema_version;                 // monogate.eml_ir.evidence_packet.v1
packet.research_status.labels;         // ["verified", "sampled", "prototype"]
validateEvidencePacket(packet).ok;     // true
```

The packet is suitable for Explorer export and internal review. Its boundary
flags continue to mark:

```text
public_savings_claim: false
formal_verification_claim: false
compiler_release_claim: false
```

## Validation

```bash
cd lib
npm test
```

Current result:

```text
6 test files passed
441 tests passed
```

## Next Research Step

Next ladder:

```text
structural lowering gates + sampled equivalence
-> symbolic equivalence for arithmetic-only expressions
-> MachLib theorem stubs
-> Lean proof obligations
```
