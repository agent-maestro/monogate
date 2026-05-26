# High-Dimensional EML Tree Space

Date: 2026-05-26

Status: sampled research probe

## Why This Exists

The hypersphere/cube collapse is the clean geometric warning sign:

```text
V(ball_d) / V(cube_d) -> 0
```

Full EML trees create a similar pressure. A depth-`k` complete binary tree has
`2^k` terminal coordinates before the first evaluation. Even before Forge sees a
loss landscape, the terminal vector already lives in a high-dimensional cube
where boundary shells dominate.

## What The Probe Measures

`python/monogate/high_dimensional.py` and
`python/scripts/high_dim_corner_concentration.py` measure:

- analytic hypersphere/cube volume ratio;
- sampled cube boundary-shell concentration;
- a crude middle-of-cube proxy;
- raw EML log-domain validity for `[-1, 1]` leaves;
- finite/non-saturated evaluation for positive-domain leaves;
- a conservative `useful_volume_proxy`.

Run:

```bash
make high-d-corner-probe
```

Outputs:

```text
reports/high_dim_corner_concentration_2026_05_26.json
reports/high_dim_corner_concentration_2026_05_26.md
```

## Research Interpretation

This is the correct place to connect the high-dimensional geometry story to
phantom-attractor handling:

```text
depth -> terminal dimension -> boundary concentration -> domain/overflow pressure
```

The probe does not prove a phantom-attractor theorem. It does give Forge a
measurement surface for why naive gradient search becomes brittle: the optimizer
is not walking through a friendly center. It is almost immediately interacting
with faces, corners, log-domain cliffs, and exponential overflow walls.

## Boundaries

This is sampled evidence only:

- no phantom-attractor proof;
- no optimizer release claim;
- no hardware claim;
- no public theorem claim.

The next useful step is to feed Forge optimizer traces through the same packet:

```text
optimizer run -> terminal vector statistics -> replay packet -> attractor/collapse label
```

## Forge Trace Packet

`python/scripts/forge_attractor_trace_packet.py` now compares six regimes:

- `naive_gradient`
- `regularized_gradient`
- `guarded_gradient`
- `boundary_aware_gradient`
- `log_domain_gradient`
- `random_search`

Run:

```bash
make forge-attractor-trace
```

Outputs:

```text
reports/forge_attractor_trace_packet_2026_05_26.json
reports/forge_attractor_trace_packet_2026_05_26.md
```

The packet labels each run as one of:

```text
converged | transient | collapsed | domain_failed | overflowed | saturated
```

This is the bridge from geometry to optimizer behavior. It gives Forge a
replayable measurement surface for boundary-aware heuristics without claiming
those heuristics are production-ready.

## Forge Heuristic Frontier

`python/scripts/forge_heuristic_frontier.py` runs the guarded, boundary-aware,
and random-search regimes across multiple depths and seeds.

Run:

```bash
make forge-heuristic-frontier
```

Outputs:

```text
reports/forge_heuristic_frontier_2026_05_26.json
reports/forge_heuristic_frontier_2026_05_26.md
```

This packet makes the next optimizer question concrete: guarded,
boundary-aware, and log-domain traces preserve finite execution, but
saturation still dominates as depth rises. Log-domain parameterization is now
a first-class Forge baseline candidate; random search stays as a control.

## MachLib / Lean Bridge

The first formalization queue should stay small:

1. Prove `V(unit_ball_d) / V([-1,1]^d) -> 0`.
2. Prove cube boundary-shell probability `1 - (1 - epsilon)^d -> 1`.
3. Prove first-layer raw EML log-domain survival decays exponentially for
   independent symmetric terminal leaves.
4. Connect guarded lowering packets to domain-preservation obligations.

These are theorem obligations, not completed theorem claims.
`make high-d-formalization` also emits draft-only Lean/MachLib stub files under:

```text
reports/formalization_stubs/high_dimensional/
```

## Useful Volume Census

`python/scripts/high_dim_useful_volume_census.py` extends the geometry probe
from finite/non-saturated behavior to target-adjacent behavior.

Run:

```bash
make high-d-useful-volume
```

Outputs:

```text
reports/high_dim_useful_volume_census_2026_05_26.json
reports/high_dim_useful_volume_census_2026_05_26.md
```

The census samples `raw_cube`, `positive_box`, and `guarded_cube`
distributions against small targets such as `0`, `1`, `sqrt2`, `e`, and `pi`.
The key field is `target_adjacent_fraction`: the sampled fraction that is
finite, non-saturated, and within tolerance of the target.

## Evidence Corpus

`make ir-evidence-corpus` writes stable EML IR evidence packets to:

```text
reports/evidence_packets/
```

The current corpus covers shared subexpressions, domain guards, exponent ratios,
trig pairs, and saturation probes. Each packet remains explicitly labeled as
sampled/internal evidence, not a formal verification claim.

## Frontier Suite

Run the full high-D frontier suite with:

```bash
make frontier-high-d
```

This regenerates:

- corner-concentration packet;
- Forge attractor trace packet;
- Forge heuristic frontier packet;
- useful-volume census;
- formalization bridge and Lean/MachLib stubs;
- IR evidence packet corpus.

Public-facing synthesis draft:

```text
docs/research/why_eml_optimization_lives_on_the_boundary.md
```
