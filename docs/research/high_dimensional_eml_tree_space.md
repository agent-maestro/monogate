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
