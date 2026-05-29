# A13 Assurance Case Skeleton

Date: 2026-05-29

Status: private assurance skeleton. This is not certification, proof, or
compiler correctness.

## Scope

A13 covers the Forge/eFrog roundtrip advantage lane:

- source frontends decompile into EML-shaped artifacts
- Forge emits target code
- selected Python-source scalar kernels agree on sample grids
- generated evidence packets and command feeds remain valid

## Top Claim

A13 has enough private evidence to remain an active compiler/decompiler
research lane, but not enough evidence to make a public correctness claim.

## Supported Subclaims

| Subclaim | Status | Evidence |
| --- | --- | --- |
| Roundtrip artifacts can be generated deterministically for the current corpus. | supported | A13 roundtrip packets and feed. |
| Selected Python-source kernels agree across original, Forge Python, and Forge JavaScript on fixed sample grids. | supported | A13.2 semantic comparison packets. |
| The current claim boundary blocks compiler correctness and formal equivalence. | supported | A13 pause packet and cockpit flags. |

## Partial or Unresolved Subclaims

| Subclaim | Status | Missing Evidence |
| --- | --- | --- |
| Cross-language semantic agreement generalizes beyond selected Python sources. | unresolved | Non-Python source semantic comparison. |
| Generated targets can be re-ingested and compared structurally. | unresolved | eFrog/Forge generated-target re-ingest lane. |
| Forge/eFrog are compiler-correct for the represented subset. | blocked | Formal semantics and proof obligations. |
| EML is broadly superior for codegen/runtime. | blocked | Larger holdouts, runtime bakeoffs, negative controls. |

## Assurance Gaps

- Formal source/IR/target semantics.
- Compiler correctness theorem or scoped proof.
- Larger holdout corpus.
- Non-Python source semantic comparison.
- Generated-target re-ingest.
- Runtime performance and numerical stability evidence.

## Non-Claims

- No compiler correctness claim.
- No formal equivalence claim.
- No high-assurance certification claim.
- No broad EML advantage claim.
- No runtime performance claim.
