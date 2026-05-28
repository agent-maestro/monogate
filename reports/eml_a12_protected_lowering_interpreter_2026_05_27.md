# EML-A12 Protected Lowering Interpreter

Date: 2026-05-27

Status: `EML_A12_PROTECTED_LOWERING_INTERPRETER_PASS`

A12 runs a tiny deterministic interpreter over protected-lowering
cases selected by the guard/mock-compiler lane.

| Case | Frames | Protected no-worse | Naive non-finite | Protected non-finite |
|---|---:|---:|---:|---:|
| `expm1_near_zero_interpreter_v0` | 9 | 9 | 0 | 0 |
| `logsumexp_edge_grid_interpreter_v0` | 7 | 7 | 3 | 0 |

## Boundary

- Executable fixture interpreter only.
- No compiler behavior change.
- No compiler correctness or formal semantic equivalence claim.
- No runtime performance, hardware measurement, production lowering, or general EML advantage claim.
