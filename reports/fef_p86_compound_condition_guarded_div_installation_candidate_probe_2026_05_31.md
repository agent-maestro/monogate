# FEF-P86 Compound-Condition Guarded-Div Installation Candidate Probe

Date: 2026-05-31

Status: `FEF_P86_COMPOUND_CONDITION_GUARDED_DIV_INSTALLATION_CANDIDATE_PROBE_PASS`

Decision: `selected_guarded_div_installation_candidate_probe_pass_not_installed`

FEF-P86 records a selected installation candidate without installing it.

## Summary

- Selected fixture: `c_and_short_circuit_guard_v0`
- Candidate: `selected_guarded_div_local_adapter_installation_candidate_v0`
- Probe: `selected_guarded_div_installation_candidate_probe_v0`
- Executed rows: `7`
- Zero-denominator rows with division skipped: `2`
- Pass count: `7`
- Fail count: `0`
- Max absolute error: `0.0`
- Candidate installed: `False`
- Re-ingest probe performed: `False`

## Intended Hooks

- `rewrite_selected_nonzero_condition`: `nonzero01(y)`
- `rewrite_selected_guarded_division`: `guarded_div(x, y, default=0.0, guard=nonzero01(y))`
- `preserve_short_circuit_non_evaluation`: `skip division when guard is 0.0`

## Rows

- `sample_00` `candidate_probe_executed_not_installed` observed `0.5` pass `True` non-eval `True`
- `sample_01` `candidate_probe_executed_not_installed` observed `0.0` pass `True` non-eval `True`
- `sample_02` `candidate_probe_executed_not_installed` observed `0.0` pass `True` non-eval `True`
- `sample_03` `candidate_probe_executed_not_installed` observed `0.0` pass `True` non-eval `True`
- `sample_04` `candidate_probe_executed_not_installed` observed `-3.0` pass `True` non-eval `True`
- `sample_05` `candidate_probe_executed_not_installed` observed `0.0` pass `True` non-eval `True`
- `sample_06` `candidate_probe_executed_not_installed` observed `2.5` pass `True` non-eval `True`

## Boundary

- Selected installation-candidate probe only.
- No installed eFrog or Forge behavior change.
- No re-ingest execution.
- No compound-condition support claim.
- No compiler-correctness, formal-equivalence, or runtime-performance claim.
