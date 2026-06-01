# FEF-P91 Loop/Back-Edge Expected Samples

Date: 2026-05-31

Status: `FEF_P91_LOOP_BACKEDGE_EXPECTED_SAMPLES_PASS`

Decision: `loop_backedge_expected_samples_recorded_support_blocked`

FEF-P91 records deterministic expected samples for one blocked loop/back-edge fixture.

## Summary

- Selected fixture: `c_while_accumulate_v0`
- Sample count: `7`
- Zero-iteration samples: `2`
- Single-iteration samples: `1`
- Multi-iteration samples: `4`
- Max iteration count: `8`
- Total back-edge taken count: `21`
- Source semantics only: `True`
- Loop runtime execution claim: `False`
- Loop boundedness policy claim: `False`
- Loop/back-edge support claim: `False`

## Samples

| Sample | x | n | Path | Iterations | Expected |
|---|---:|---:|---|---:|---:|
| `sample_00` | 2.0 | 0 | `zero_iterations` | 0 | 0.0 |
| `sample_01` | 2.0 | 1 | `single_iteration` | 1 | 2.0 |
| `sample_02` | 2.0 | 3 | `multi_iteration` | 3 | 6.0 |
| `sample_03` | -1.5 | 4 | `multi_iteration` | 4 | -6.0 |
| `sample_04` | 0.0 | 5 | `multi_iteration` | 5 | 0.0 |
| `sample_05` | 3.0 | -2 | `zero_iterations` | 0 | 0.0 |
| `sample_06` | 0.25 | 8 | `multi_iteration` | 8 | 2.0 |

## Boundary

- Expected samples only; no loop execution.
- No loop boundedness policy, lowering, or support claim.
- No frontend lowering change.
- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.
