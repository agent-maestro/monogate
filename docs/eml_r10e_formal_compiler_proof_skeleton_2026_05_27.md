# EML-R10E Formal Compiler Proof Skeleton

Date: 2026-05-27

R10E is the bridge from scoped semantic certificates to a future compiler
correctness proof. It does not prove compiler correctness. It records the proof
obligations that must be discharged before Monogate can safely claim an EML
lowering compiler is correct.

## What R10E Adds

- Schema: `schemas/eml_formal_compiler_proof_skeleton_v0.json`
- Builder: `python/scripts/eml_r10e_formal_compiler_proof_skeleton.py`
- Result JSON: `python/results/eml_r10e_formal_compiler_proof_skeleton/`
- Report: `reports/eml_r10e_formal_compiler_proof_skeleton_2026_05_27.md`
- Evidence packet: `reports/evidence_packets/eml_r10e_formal_compiler_proof_skeleton.json`
- Command feed: `command_center_feeds/eml_r10e_formal_compiler_proof_skeleton_feed_2026_05_27.json`

## Obligation State

R10E records six compiler-proof obligations:

| Obligation | Status |
|---|---|
| `syntax-preservation` | `open` |
| `domain-guard-preservation` | `open` |
| `per-case-semantic-preservation` | `covered_by_scoped_certificate` |
| `unsupported-case-routing` | `open` |
| `runtime-implementation-correspondence` | `open` |
| `compiler-wide-induction` | `open` |

Current summary:

- Obligations: `6`
- Covered obligations: `1`
- Open obligations: `5`
- Covered cases: `4`
- Compiler correctness proved: `false`
- Formal compiler proof complete: `false`
- Compiler behavior changed: `false`

## Reviewer Routing

RH-A1 now treats compiler claims with R10E evidence as
`formal_proof_skeleton_open`, not as a completed proof. RH-A2 routes those
claims to `R10F proof-assistant AST and guard model`.

This keeps the lane honest: R10E is a map of remaining proof work, not an
approval to make compiler correctness claims.

## Boundary

- No compiler correctness claim.
- No full EML semantics claim.
- No production lowering claim.
- No Forge or compiler behavior change.
- No deployment or package publication.

