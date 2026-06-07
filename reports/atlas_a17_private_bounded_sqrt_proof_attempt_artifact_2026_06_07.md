# ATLAS-A17 Private Bounded Sqrt Proof-Attempt Artifact

Status: `ATLAS_A17_PRIVATE_BOUNDED_SQRT_PROOF_ATTEMPT_ARTIFACT_BLOCKED`

## Summary

- source artifact: `atlas-a16-private-sqrt-proof-attempt-open-selector`
- candidate id: `sqrt_square_abs_normalized_nonnegative_boundary_candidate`
- attempt status: `blocked_before_edit_due_allowed_file_missing`
- blocker id: `allowed_file_missing_in_machlib_checkout`
- allowed files exist: `False`
- observed likely witness file: `foundations/MachLib/EMLAtlasWitness.lean`
- proof attempt started: `False`
- MachLib changed: `False`
- Lean typecheck performed: `False`
- next recommended artifact: `ATLAS-A18 private sqrt attempt scope correction selector`

## Allowed-File Preflight

| Allowed file | Exists |
|---|---|
| `MachLib/Real.lean` | `False` |

## Precise Blocker

- status: `blocks_attempt_before_edit`
- description: The A16 attempt scope allows MachLib/Real.lean, but that path is not present in the observed MachLib checkout.

## Why This Aborts Instead Of Correcting Scope

- A17 is bound by the A16 allowed-file list.
- Changing the allowed file would be a scope correction, not the bounded attempt itself.
- A separate selector should decide whether to replace the stale path with the observed witness file.

## Non-Claims

- ATLAS-A17 creates a private bounded attempt artifact and aborts before edit because A16's allowed file path is not present in the MachLib checkout.
- ATLAS-A17 performs allowed-file preflight only; it does not edit MachLib, run Lean, perform theorem lookup, claim exact theorem names, or claim the sqrt candidate is true, valid, checked, Lean-ready, or provable.
- ATLAS-A17 does not silently correct the attempt scope, change runtime lowering, replace sqrt, publish or approve public copy, create SDK/compiler/course copy, consume reviewer responses, touch laptop-owned repositories, or claim catalog completeness, target lower-bound reached, public readiness, runtime performance, compiler correctness, formal equivalence, visualization quality, or broad EML advantage.
