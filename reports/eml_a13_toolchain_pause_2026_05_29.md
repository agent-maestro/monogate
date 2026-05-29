# EML-A13 Toolchain Pause

Date: 2026-05-29

Status: `EML_A13_TOOLCHAIN_PAUSE_RECORDED`

A13 is a clean pause point for the Forge/eFrog toolchain evidence lane. It
does not finish compiler correctness, but it moves the lane from "can emit
artifacts" to "can emit and sample-check selected target behavior."

## What Now Exists

| Layer | Result | Boundary |
|---|---:|---|
| Source to EML to Forge target roundtrip | 32/32 pass | emission evidence only |
| Forge targets covered | 2 | Python and JavaScript |
| Source/frontends covered | 16 | default plus private holdout slice |
| Semantic comparison cases | 6/6 pass | selected sample grids only |
| Semantic sample frames | 25 | deterministic fixtures |
| Max absolute error | 1.1102230246251565e-16 | floating-point sample evidence |
| Max relative error | 1.5701940187705089e-15 | floating-point sample evidence |

## Stable For Now

- eFrog can decompile selected source frontends into Forge-compatible EML.
- Forge can emit Python and JavaScript targets for the selected roundtrip set.
- Selected Python-source scalar kernels agree with Forge Python and Forge
  JavaScript outputs over deterministic sample grids.
- The private cockpit can review the roundtrip and semantic comparison packets.

## Still Open

- larger semantic sample grids
- non-Python source semantic comparison
- generated target re-ingest
- cross-target semantic equivalence beyond sample grids
- formal compiler correctness proof
- larger holdout source corpus

## Boundary

- No Forge behavior change.
- No eFrog behavior change.
- No compiler correctness claim.
- No formal equivalence claim.
- No broad EML advantage claim.
- No runtime performance claim.
- No production toolchain claim.
- No public product launch.

## Next Research Direction

With A13 paused, the next research exploration can look outward:

- proof-carrying code and foundational PCC
- deterministic replay and record/replay systems
- high-assurance evidence traditions from formal methods groups
- Lean formalization workflows and AI-prover proof digestion
- Pfaffian and holographic-adjacent math only as exploratory inspiration

This is a good stopping point because Monogate now has a concrete internal
toolchain evidence story, while the remaining gaps are explicit rather than
blurred into a larger claim.
