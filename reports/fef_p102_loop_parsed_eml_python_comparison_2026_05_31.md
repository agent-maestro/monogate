# FEF-P102 Loop Parsed-EML Python Comparison

Date: 2026-05-31

Status: `FEF_P102_LOOP_PARSED_EML_PYTHON_COMPARISON_PASS`

Decision: `selected_loop_parsed_eml_python_comparison_recorded_installed_support_blocked`

FEF-P102 executes the selected parsed-EML-shaped Python comparison after the P101 parse pass.

## Summary

- Selected fixture: `c_while_accumulate_v0`
- Harness: `selected_loop_parsed_eml_python_comparison_harness_v0`
- Rows compared: `7`
- Pass count: `7`
- Fail count: `0`
- Max absolute error: `0.0`
- P101 parse succeeded: `True`
- Parsed EML/Python comparison performed: `True`
- Forge-recompiled Python target executed: `False`
- Selected adapter installed: `False`
- Loop re-ingest supported: `False`

## Rows

| Sample | n | x | P98 observed | Parsed EML observed | abs error | pass |
|---|---:|---:|---:|---:|---:|---|
| `sample_00` | `0` | `2.0` | `0.0` | `0.0` | `0.0` | `True` |
| `sample_01` | `1` | `2.0` | `2.0` | `2.0` | `0.0` | `True` |
| `sample_02` | `3` | `2.0` | `6.0` | `6.0` | `0.0` | `True` |
| `sample_03` | `4` | `-1.5` | `-6.0` | `-6.0` | `0.0` | `True` |
| `sample_04` | `5` | `0.0` | `0.0` | `0.0` | `0.0` | `True` |
| `sample_05` | `-2` | `3.0` | `0.0` | `0.0` | `0.0` | `True` |
| `sample_06` | `8` | `0.25` | `2.0` | `2.0` | `0.0` | `True` |

## Parsed EML Shape

```text
module c_while_accumulate_v0_helper_adapted;

fn step01(x: Real) -> Real
    where chain_order <= 0
{
    clamp(x * 1e+30, 0.0, 1.0)
}

fn c_while_accumulate_v0_generated_fixture(x: Real, n: Real) -> Real
    where chain_order <= 0
{
    let k = 0.0 + (n - (0.0)) * step01((n) - (0.0));
    x * k
}

```

## Boundary

- Selected parsed-EML-shaped Python comparison only.
- No Forge-recompiled Python target execution.
- No installed eFrog or Forge adapter.
- No loop/back-edge support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
